"""Install a signed, application-only release on a Berryaudio image."""

import ast
import ctypes
import fcntl
import json
import os
import re
import shutil
import subprocess
import tarfile
import tempfile
import time
from http.client import HTTPException
from pathlib import Path, PurePosixPath
from urllib.parse import urlsplit
from urllib.request import ProxyHandler, Request, build_opener


APP = Path("/home/pi/berryaudio")
WORK = Path("/home/pi/.berryaudio-update")
SIGNERS = Path("/etc/berryaudio-updates/allowed_signers")
VERSION = r"(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)"
APP_SERVICE = "berryaudio.service"
DSP_SERVICE = "camilladsp.service"
PRESERVE = (
    "berryaudio.egg-info",
    "core/db",
    "dsp/camilladsp/coeffs",
    "dsp/camilladsp/configs",
    "dsp/camilladsp/statefile.yml",
    "shairportsync/shairport-sync.conf",
    "multiroom/snapserver.conf",
    *(f"web/www/images/{name}" for name in (
        "album", "artist", "nowplaying", "shairportsync", "storage"
    )),
)


def version_key(version):
    return tuple(map(int, version.split(".")))


def read_version(directory):
    # Read the version without importing code from either release.
    path = directory / "version.py"
    for node in ast.parse(path.read_text(), filename=str(path)).body:
        if (
            isinstance(node, ast.Assign)
            and any(isinstance(name, ast.Name) and name.id == "__version__"
                    for name in node.targets)
            and isinstance(node.value, ast.Constant)
            and isinstance(node.value.value, str)
            and re.fullmatch(VERSION, node.value.value)
        ):
            return node.value.value
    raise ValueError(f"Expected a numeric __version__ in {path}")


def git(*args):
    env = {
        **os.environ,
        "GIT_TERMINAL_PROMPT": "0",
        "GIT_CONFIG_NOSYSTEM": "1",
        "GIT_CONFIG_GLOBAL": "/dev/null",
    }
    return subprocess.run(
        ["/usr/bin/git", *args],
        env=env, check=True, stdout=subprocess.PIPE, text=True, timeout=120,
    ).stdout


def newer_tag(remote, installed):
    refs = git("ls-remote", "--tags", "--refs", "--", remote, "refs/tags/v*")
    versions = re.findall(rf"\trefs/tags/v({VERSION})$", refs, re.MULTILINE)
    newest = max(versions, key=version_key, default=installed)
    return f"v{newest}" if version_key(newest) > version_key(installed) else None


def stage_release(remote, tag, temp):
    repo = temp / "repo"
    archive = temp / "release.tar"
    tree = temp / "app"
    ref = f"refs/tags/{tag}"

    git("init", "--quiet", "--bare", str(repo))
    git("-C", str(repo), "fetch", "--quiet", "--depth=1", "--no-tags", "--",
        remote, f"{ref}:{ref}")
    git("-C", str(repo), "-c", "gpg.format=ssh",
        "-c", f"gpg.ssh.allowedSignersFile={SIGNERS}",
        "-c", "gpg.minTrustLevel=fully", "verify-tag", ref)
    headers = git("-C", str(repo), "cat-file", "tag", ref).split("\n\n", 1)[0]
    if f"tag {tag}" not in headers.splitlines():
        raise ValueError(f"Signed tag name does not match {tag}")
    git("-C", str(repo), "archive", "--format=tar", f"--output={archive}",
        f"{ref}^{{commit}}")

    tree.mkdir()
    with tarfile.open(archive) as bundle:
        for member in bundle:
            path = PurePosixPath(member.name)
            if path.is_absolute() or ".." in path.parts or ".git" in path.parts:
                raise ValueError(f"Invalid release path: {member.name}")
            destination = tree.joinpath(*path.parts)
            if member.isdir():
                destination.mkdir(parents=True, exist_ok=True)
            elif member.isfile():
                destination.parent.mkdir(parents=True, exist_ok=True)
                with bundle.extractfile(member) as source, destination.open("xb") as target:
                    shutil.copyfileobj(source, target)
                if member.mode & 0o111:
                    destination.chmod(0o755)
            else:
                raise ValueError(f"Unsupported release entry: {member.name}")

    if read_version(tree) != tag[1:]:
        raise ValueError(f"{tag} does not match the release's version.py")
    for name in ("main.py", "web/www/index.html"):
        if not (tree / name).is_file():
            raise ValueError(f"Release is missing {name}")
    for name in ("requirements.txt", "setup.py"):
        if (tree / name).read_bytes() != (APP / name).read_bytes():
            raise ValueError(f"{name} changed. This release needs a manual upgrade.")
    return tree


def control(action, unit):
    subprocess.run(
        ["/usr/bin/sudo", "-n", "/usr/bin/systemctl", action, unit],
        check=True, timeout=120,
    )


def stop_services():
    control("stop", APP_SERVICE)
    control("stop", DSP_SERVICE)


def start_services():
    control("start", DSP_SERVICE)
    control("start", APP_SERVICE)


def service_active():
    return subprocess.run(
        ["/usr/bin/systemctl", "is-active", "--quiet", APP_SERVICE],
        timeout=10,
    ).returncode == 0


def wait_for_app(expected):
    # Query the running app itself. A live systemd unit alone can be restarting.
    request = Request(
        "http://127.0.0.1:8080/rpc",
        data=b'{"jsonrpc":"2.0","id":1,"method":"system.info"}',
        headers={"Content-Type": "application/json"},
    )
    http = build_opener(ProxyHandler({}))
    deadline = time.monotonic() + 60
    while time.monotonic() < deadline:
        try:
            with http.open(request, timeout=15) as response:
                reply = json.load(response)
            if isinstance(reply, dict):
                result = reply.get("result")
                if isinstance(result, dict) and result.get("version") == expected:
                    return
        except (OSError, ValueError, HTTPException):
            pass
        time.sleep(2)
    raise RuntimeError(f"Berryaudio {expected} did not pass its startup check")


def exchange(candidate):
    # The editably installed launcher and DSP service use APP by absolute path.
    # Exchange two directories atomically so that path is always present.
    renameat2 = ctypes.CDLL(None, use_errno=True).renameat2
    at_fdcwd, rename_exchange = -100, 2
    if renameat2(at_fdcwd, os.fsencode(APP), at_fdcwd,
                 os.fsencode(candidate), rename_exchange) != 0:
        error = ctypes.get_errno()
        raise OSError(error, os.strerror(error))


def finish_activation(pending, expected, old_version):
    try:
        start_services()
        wait_for_app(expected)
    except (OSError, RuntimeError, subprocess.SubprocessError):
        stop_services()
        exchange(pending)
        os.sync()
        start_services()
        wait_for_app(old_version)
        (WORK / "failed-version").write_text(expected + "\n")
        shutil.rmtree(pending)
        print(f"Restored {old_version} after {expected} failed to start.", flush=True)
        raise

    previous = WORK / "previous"
    if previous.exists():
        shutil.rmtree(previous)
    pending.rename(previous)
    os.sync()
    print(f"Updated Berryaudio to {expected}. Previous version: {old_version}.", flush=True)


def update(remote):
    pending = WORK / "pending"
    installed = read_version(APP)
    if pending.exists():
        pending_version = read_version(pending)
        if version_key(pending_version) < version_key(installed):
            finish_activation(pending, installed, pending_version)
            return
        shutil.rmtree(pending)

    if not service_active():
        print("Berryaudio is stopped. Skipping this update check.", flush=True)
        return
    tag = newer_tag(remote, installed)
    if tag is None:
        print(f"Berryaudio {installed} is up to date.", flush=True)
        return
    failed = WORK / "failed-version"
    if failed.exists() and failed.read_text().strip() == tag[1:]:
        print(f"{tag} failed its startup check before. Waiting for a newer tag.", flush=True)
        return

    with tempfile.TemporaryDirectory(dir=WORK, prefix="download-") as temp:
        tree = stage_release(remote, tag, Path(temp))
        print(f"Installing {tag}. Restarting Berryaudio and CamillaDSP.", flush=True)
        try:
            stop_services()
            subprocess.run(
                ["/usr/bin/rsync", "-aR", "--ignore-missing-args", "--",
                 *PRESERVE, str(tree) + "/"],
                cwd=APP, check=True, timeout=120,
            )
            tree.rename(pending)
            os.sync()
            exchange(pending)
        except (OSError, subprocess.SubprocessError):
            start_services()
            raise
        finish_activation(pending, tag[1:], installed)


def main():
    remote = os.environ["BERRYAUDIO_UPDATE_REPO"]
    url = urlsplit(remote)
    if url.scheme != "https" or not url.hostname or url.username is not None:
        raise ValueError("BERRYAUDIO_UPDATE_REPO must be an HTTPS Git URL without credentials")
    if not SIGNERS.is_file():
        raise ValueError(f"Install the release signing public key in {SIGNERS}")
    if not APP.is_dir() or APP.is_symlink():
        raise ValueError(f"{APP} must be the installed application directory")
    WORK.mkdir(mode=0o700, exist_ok=True)
    with (WORK / "lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        update(remote)


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, KeyError, RuntimeError, subprocess.SubprocessError) as error:
        raise SystemExit(f"Berryaudio update failed: {error}") from error
