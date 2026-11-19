# Automatic Berryaudio updates

The updater checks a public Git repository for stable releases tagged
`vMAJOR.MINOR.PATCH`. It accepts tags signed with your release key, keeps the
device's settings, and starts Berryaudio and CamillaDSP after installing. If the
running application fails to report the new version, the updater restores the
previous installation. An update can interrupt playback briefly.

This targets the Bookworm Berryaudio image with `berryaudio.service` running as
`pi` and the application installed in `/home/pi/berryaudio`. The updater uses
the image's existing Python environment and system packages. Releases that change
`requirements.txt` or `setup.py` need a manual upgrade.

## Set up a release key and repository

Use a public fork of Berryaudio that you control. On your computer, generate a
dedicated signing key and keep its private half there.

```bash
ssh-keygen -t ed25519 -f ~/.ssh/berryaudio-release -C berryaudio-release
git remote add my-fork git@github.com:YOUR-USER/berryaudio.git
```

For each release, bump `__version__` in `version.py`, commit your app changes,
then sign and push a matching tag to your fork. Start with a version newer than
the one running on your Pi. Keep downloaded and built SD card images out of the
commit.

```bash
git -c gpg.format=ssh -c user.signingkey="$HOME/.ssh/berryaudio-release" \
  tag -s v4.1.1 -m "Berryaudio 4.1.1"
git push my-fork refs/tags/v4.1.1
```

Git tags for this channel are immutable. If a release fails its startup check,
publish the fix as a new version.

## Install once on the Pi

From your checkout, copy the updater and public key to the running Pi.

```bash
ssh pi@berryaudio.local 'mkdir -p ~/berryaudio-updater'
scp deploy/updates/update.py deploy/updates/berryaudio-update.{service,timer} \
  ~/.ssh/berryaudio-release.pub pi@berryaudio.local:berryaudio-updater/
```

Then SSH into the Pi. Replace `YOUR-USER` with the owner of your public fork.

```bash
cd ~/berryaudio-updater
sudo install -Dm644 update.py /usr/local/lib/berryaudio-update/update.py
sudo install -m644 berryaudio-update.service berryaudio-update.timer /etc/systemd/system/
sudo install -d -m755 /etc/berryaudio-updates
printf '%s\n' 'BERRYAUDIO_UPDATE_REPO=https://github.com/YOUR-USER/berryaudio.git' \
  | sudo tee /etc/berryaudio-updates/config
printf 'berryaudio-release %s\n' "$(cat berryaudio-release.pub)" \
  | sudo tee /etc/berryaudio-updates/allowed_signers
sudo systemctl daemon-reload
sudo systemctl enable --now berryaudio-update.timer
```

The timer checks five minutes after boot and daily at 04:00 in the Pi's local
time. On first activation after five minutes of uptime it may check immediately.
To check manually and see the result, run these commands on the Pi.

```bash
sudo systemctl start berryaudio-update.service
sudo journalctl -u berryaudio-update.service -n 40 --no-pager
```

The last working application tree is kept in
`/home/pi/.berryaudio-update/previous`. The updater carries over the player
database, CamillaDSP state, AirPlay and Snapcast configuration, and artwork
caches. Keep development edits in your source checkout and publish them as a
release. The timer replaces application files on the Pi.
