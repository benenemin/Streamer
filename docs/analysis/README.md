# Repository analysis notes

Reviewed 2026-11-18 at commit `c340e1b`, application version `4.1.0`.

Start here for future feature work. These notes capture the repository's structure,
audio/control paths, extension interfaces, dependencies, verified findings and an
I²S integration proposal. Only documentation was changed.

| Document | Use it for |
| --- | --- |
| [Architecture and feature map](architecture.md) | Runtime, data flow, persistence, module ownership and deployment boundaries |
| [Pi 4 to LSWEQ DSP-AMP 4](rpi4-lsweq-dsp-amp4.md) | Current user hardware, proposed profile, signal connections and remaining board checks |
| [I²S external DSP proposal](i2s-external-dsp.md) | Recommended approach, hardware decisions, configuration, implementation phases and acceptance checks |
| [Findings and verification](findings.md) | Confirmed issues, reproductions, limitations and outstanding questions |
| [Extension interface inventory](interfaces.md) | Handler signatures, literal cross-extension calls, published events and first-install settings |

## Most important conclusions

- Treat the external DSP's I²S input as a physical ALSA output. Generic I²S profiles
  already exist; DSP programming/control is a separate feature.
- Keep the current CamillaDSP/Loopback route for the first version so volume,
  source switching, multiroom, visualization and browser streaming remain available.
- The eight-channel CamillaDSP output represents four stereo destinations, not
  an eight-channel I²S bus.
- The actual `audio_out` ALSA graph and appliance provisioning are absent from
  this checkout. Obtain them from the installed image before editing routing.
- Replace the broad `.asoundrc` PCM replacement and add settings migration and
  application-status handling before making configurable hardware support robust.
- The user confirmed Pi 4 to an ADAU1701-based LSWEQ DSP-AMP 4, send-only.
  The target-specific note recommends Pi-generated clocks for its advertised
  ASRC input, subject to board revision/header verification. Hardware is untested.
- Frontend source is absent; this repository contains the compiled web UI.

## Scope and confidence

Startup/core/config and the audio path were inspected in detail. Other feature
areas were mapped by their interfaces, persistence and integration points rather
than audited line by line. The compiled UI was inspected selectively for mixer,
DSP settings, RPC and reboot behavior.

Temporary database/ALSA fixtures reproduced two configuration defects. Python
syntax and literal routes were checked statically. No application services were
started and no hardware was exercised. See the verification record before using
these notes as evidence of runtime compatibility.

## Keeping the notes useful

For subsequent changes, compare the current commit with this baseline and inspect
the changed modules plus their callers/consumers. Update the affected notes and
record the new baseline; a full repository reread should usually be unnecessary.
Line references are for this baseline, and external kernel/library documentation
must be checked against the target's installed versions.

Useful starting commands, run from the repository root:

```bash
git diff c340e1b -- main.py core config mixer dsp playback bluetooth multiroom
rg -n 'on_config_update|set_capture_device|write_asoundrc|write_dtoverlay' --glob '*.py'
rg -n 'audio_out|Loopback|resample_rate' --glob '*.py' --glob '*.yaml' --glob '*.yml' --glob '*.conf'
```

Avoid running `main.py` merely to inspect APIs: startup integrates with appliance
services and can write system configuration. Use source/AST inspection or isolated
fixtures until a representative runtime environment is available.
