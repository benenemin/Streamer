# Findings and verification record

Baseline: `c340e1b`, reviewed 2026-11-18. No runtime code changes were made.
Priority is relative to implementing configurable I²S output, not a general
assessment of the project's severity or production reliability.

## Address before configurable output ships

| Finding | Evidence | Implication / suggested action |
| --- | --- | --- |
| ALSA routing definition absent | `audio_out` is used by CamillaDSP but never defined in tracked files; `/home/pi/.asoundrc` is read externally | Capture the installed graph and includes; add a maintained template before changing routing |
| Global replacement of PCM targets | `core/util/system.py:60`, `write_asoundrc()` replaces every `pcm "..."` occurrence | Replace a single owned physical-output node; preserve auxiliary routes and BlueALSA configuration |
| New configuration keys cannot be added by YAML alone | `core/db.py:95`, `init_extension()`; `core/db.py:113`, `set_config()` | Add versioned migration/default merging with user-value preservation |
| Saved settings can precede failed application | `config/config.py:34` schedules asynchronous updates after persistence; overlay writer logs errors without raising | Validate and report requested/applied state; await operations that determine success and support rollback |
| Boot helper assumes image-specific layout | `core/util/system.py:196`, `apply_dtoverlay()` requires exact marker and deletes adjacent overlay lines; supplied `path` is ignored | Own an explicit block/file, preserve unrelated settings, use supplied paths, atomic replacement and backup |
| Clock drift policy is missing | `dsp/dsp.py:201` forces synchronous conversion with fixed rate; example YAML leaves rate adjustment unset | Determine clock relationship per source; validate appropriate drift correction, not just nominal rate conversion |
| Output format and channel count are not modeled as hardware settings | `mixer/config.yaml` stores output identifiers, not endpoint capabilities; DSP YAML plays eight channels to `audio_out` | Keep physical stereo capabilities separate from the logical fan-out and verify negotiated parameters |
| Concurrent hardware changes are possible | `core.request()` directly invokes handlers, and `config.set` schedules multiple tasks | Serialize output/capture graph changes and coordinate service stop/start/reload |

The PCM replacement risk is conditional on file contents. The installed graph may
avoid multiple quoted targets by using other syntax; it has not been inspected.
The helper's broad behavior was reproduced independently of that unknown graph.

## Fix when touching related input/format code

| Finding | Evidence | Implication |
| --- | --- | --- |
| Undefined metadata object on rate updates | `linein/linein.py:43`, `usbdac/usbdac.py:50` write `self._track`, which those classes never initialize | Existing settings callbacks can raise; USB DAC callback may already have changed module settings |
| Configured capture bit depth does not set actual capture format | `linein`, `tuner`, `usbdac` read `bit_depth` but do not pass `sampleformat` to `dsp.set_capture_device`; their config-update handlers do not update `_bit_depth` | Displayed bit depth and hardware negotiation can differ; propagate and validate explicit format |
| Reported DSP format is assumed | `dsp/dsp.py:249` uses requested capture format or `S32_LE`; playback YAML `format` is null | Snapcast format selection is based on an assumption; report actual playback/tap format separately |
| Some low-level settings do not update caches | DSP config callback handles gain/rate but not `default_capture_device`; playback caches `mixer.output_device` with no config callback | Explicitly define live/restart application for every new field |
| Readiness failure continues into client access | `dsp/dsp.py:234` exhausts RUNNING retries, disconnects client, then reaches `self._client.volume` | Return/raise on failed readiness and preserve meaningful failure state |
| Missing RPC target for visualizer restart | `dsp/dsp.py:286` calls `display.start_cava`, but no `on_start_cava` exists on `DisplayExtension` | Determine intended controller restart behavior when changing tap rate |
| Physical channel order needs confirmation | CamillaDSP `Distributer` maps source 1 to destination 0 and source 0 to destination 1 for each stereo pair | Use separate L/R tones before changing mapping; downstream ALSA bindings are unavailable |

## Broader maintenance observations

- Actor startup is concurrent; declared extension order does not provide readiness.
  Stop hooks may run twice. These matter for future service coordination work.
- Several async methods invoke synchronous subprocess/client/database operations.
  A large hardware refactor should isolate blocking work, but this is not needed
  as an unrelated cleanup before proving a stereo I²S link.
- Frontend source and appliance provisioning are missing, so a backend feature
  can be developed here while a polished UI/reproducible image needs those sources.
- The shipped CamillaDSP YAML contains active gain/EQ and a saved USB capture
  setup. Disabling resampling alone does not establish bit-perfect output.
- Generic I²S, DAC+ DSP and Beocreate catalog entries contain no DSP management
  protocol or capability validation. Catalog presence does not prove a tested board.
- `mixer/local/` is an inactive duplicate library implementation.
- `system/._system.py` is tracked AppleDouble metadata (header `00051607`), not
  Python source. Exclude it from compilation/source indexing; remove in a separate
  cleanup if desired.
- Existing server authentication/network boundaries and plaintext persisted
  network/storage settings need consideration if new remote admin endpoints are
  added. This analysis did not perform a security audit.

## Checks performed

All checks were read-only or used temporary fixtures. The application and hardware
services were not started; boot files and installed ALSA files were not changed.

1. Inspected startup/core/config, all active extension interfaces/defaults, audio
   producers and consumers, output catalog, boot/ALSA helpers, persistence, native
   integrations and selected compiled UI settings/RPC code.
2. Parsed all 90 tracked `*.py` paths using Python's encoding-aware source reader:
   89 source files parsed; one binary AppleDouble file was excluded as above.
   This is syntax verification, not import/runtime compatibility testing.
3. Loaded `core/db.py` against a temporary directory/database. A selected hardware
   value survived re-initialization, but a newly introduced default was absent;
   setting it raised `Unknown config for extension mixer: ['new_i2s_setting']`.
4. Called `SystemUtil.write_asoundrc()` against a temporary ALSA fixture containing
   one physical and one auxiliary quoted PCM target. Both targets became the new
   physical device; the auxiliary Loopback target was lost.
5. Compared literal core request routes against active extension handlers using
   AST inspection. Found the unresolved `display.start_cava` call. Dynamic routes,
   arguments, type compatibility and external services were not proven by this.
6. Checked Raspberry Pi, ALSA and CamillaDSP primary documentation for the I²S
   proposal. Links and version caveats are recorded in that document.
7. Verified local documentation links, code-fence balance and whitespace. The
   root README links to the analysis index for future discovery.

## Still unknown

The user has since confirmed Raspberry Pi 4, ADAU1701-based LSWEQ DSP-AMP 4, and
Pi-to-DSP audio only. The [target-specific note](rpi4-lsweq-dsp-amp4.md) records the
proposed profile based on the published module interface.

- Pi kernel/OS image and exact DSP module revision.
- Module connector pinout, accepted slot layout, logic levels, power/reset
  sequencing, source selection and installed DSP boot/control setup.
- Installed `.asoundrc`/includes, Loopback module settings, boot anchors/filters,
  systemd units, service user, sudo permissions and actual CamillaDSP version.
- Actual I²S pinmux, advertised ALSA capabilities and behavior on missing clocks.
- Real audio quality, XRUNs, long-duration drift, end-to-end latency, source
  switching, reboot behavior and multiroom synchronization on the target hardware.

Keep those items as explicit unknowns until measured; do not replace them with
assumptions based on the board names in `mixers.json`.
