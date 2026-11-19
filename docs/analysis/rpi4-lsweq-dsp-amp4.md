# Raspberry Pi 4 to LSWEQ DSP-AMP 4

Updated 2026-11-18. Repository baseline: `c340e1b`, Berryaudio `4.1.0`.

## Confirmed scope

The user specified Raspberry Pi 4, ADAU1701 and audio only from Pi to DSP, then
identified [LSWEQ DSP-AMP 4](https://www.hs-sound.de/LSWEQ-DSP-AMP-4) as the module.
Use this note for the current hardware; the general I²S proposal covers other
possible devices and directions.

## Published interface and confidence

HS-Sound specifies 24-bit/48 kHz processing and an I²S input with ASRC that needs
no separate MCLK. It offers SigmaStudio/PC software configuration and specifies
an ICP5 programmer for custom SigmaStudio programming. The retrieved product
page does not document connector pin numbering, logic levels, accepted slot
widths, or the I²S source-selection procedure. These are published claims, not
measurements of the user's board. Source: [module product page](https://www.hs-sound.de/LSWEQ-DSP-AMP-4).

This differs from a bare ADAU1701: its serial clocks must be synchronous with its
master clock, and its input clock pins are consumers. The module's advertised
ASRC interface is therefore the relevant connection boundary. Do not bypass it
using raw DSP pin wiring. Source: [ADAU1701 Rev. C datasheet, page 46](https://www.analog.com/media/en/technical-documentation/data-sheets/ADAU1701.pdf#page=46).

## Recommended first profile

Based on the advertised ASRC input, the proposed arrangement is:

```mermaid
flowchart LR
    BA[Berryaudio sources] --> Camilla[Existing CamillaDSP route]
    Camilla --> ALSA[Managed physical ALSA output]
    ALSA --> Pi[Pi 4: data and clock producer]
    Pi -->|BCLK, LRCLK, stereo data| Input[Module I²S input / ASRC]
    Input --> DSP[ADAU1701 processing]
    DSP --> Amp[Amplifier channels]
```

This is an engineering proposal inferred from the published input description.
Verify the particular board revision and header requirements before wiring.

| Setting | Proposed value |
| --- | --- |
| Transport | Pi-to-module stereo I²S; no return audio |
| Clock role | Pi produces BCLK and LRCLK; module receives them |
| Nominal output rate | Fixed 48000 Hz |
| Sample precision target | 24 valid bits |
| Slot layout to validate | Two 32-bit slots; expected BCLK 3.072 MHz |
| ALSA format to validate | `S32_LE` container, with appropriate precision/framing at the receiver |
| Candidate overlay | `i2s-dac` |
| Physical device name | Discover with ALSA after overlay activation; do not guess card index |
| Initial volume backend | Existing CamillaDSP software volume |
| Local software filters | Prefer neutral EQ/effects for initial integration; retain deliberate gain/volume policy |
| DSP control | Separate from audio transport; no automatic program changes in this feature |

The [Pi kernel's i2s-dac overlay](https://github.com/raspberrypi/linux/blob/rpi-6.12.y/arch/arm/boot/dts/overlays/i2s-dac-overlay.dts)
enables the Pi clock producer. It is a candidate to validate against the installed
kernel, not proof that the module accepts the proposed slot/format combination.
The general proposal's `i2s-master-dac` alternative is not the initial choice for
this module's advertised input.

Keep physical sample precision, ALSA memory container and serial slot width
separate. Do not expose 32 valid bits or native 44.1/96/192 kHz as supported
features of this profile without additional documentation and verification.

## Signal-level wiring plan

This table describes functions only. It deliberately does not assign unverified
connector positions on the amplifier board.

| Pi 4 signal | GPIO | Physical header pin | Module destination |
| --- | --- | --- | --- |
| BCLK output | 18 | 12 | I²S input bit clock |
| LRCLK output | 19 | 35 | I²S input word/left-right clock |
| Serial data output | 21 | 40 | I²S input data |
| Ground | — | 6, or another ground | Signal ground |

Pi GPIO20/physical pin 38 is unused for this send-only profile. No Pi MCLK signal
is part of the proposed connection. Verify module input logic compatibility and
connector orientation from its manual/schematic; do not use its I²S output header
as the Pi's destination. Pi pin assignments are documented in the
[Raspberry Pi I²S white paper](https://pip-assets.raspberrypi.com/categories/1259-audio-camera-and-display/documents/RP-009699-WP-1-Using%20the%20I2S%20peripherals%20on%20Raspberry%20Pi%20SBCs.pdf).

## Berryaudio implementation scope

1. Add a profile labeled `LSWEQ DSP-AMP 4 (I²S)` with a stable identifier and
   explicit Pi clock-producer metadata. Mark compatibility unverified until tested.
2. Retain `mixer.output_device` as Loopback ingestion. Select the discovered
   physical I²S PCM through `mixer.hw_device` and the managed ALSA output node.
3. Keep `dsp.resample_rate` at 48000, including when source material is 44.1 kHz.
   Preserve the existing logical eight-channel fan-out and all auxiliary taps.
4. Set and validate physical output format independently of the logical graph's
   channel count. The module's amplifier output count does not require four I²S
   input channels for this stereo-source design.
5. Keep mixer software volume and neutralize unwanted software EQ/effects while
   the external DSP handles the user's speaker processing. Preserve the module's
   intended crossover/routing program.
6. Implement the documented settings migration, scoped ALSA writes and explicit
   application/reboot status from [findings](findings.md). Existing generic-I²S
   support may be enough for the first hardware proof before those improvements.

The ASRC at the module input and the Pi's own source/capture/playback clock
relationships are separate boundaries. Verify CamillaDSP buffer behavior for
each source; the module's input conversion does not establish that the Pi's
Loopback/ADC/gadget paths have suitable pacing or drift management.

An ADAU1701-specific Linux codec driver is not the first requirement for sending
audio to an already configured module input. Its upstream integration includes
firmware loading and device control, which is a larger scope. See
[Analog Devices Linux driver documentation](https://developer.analog.com/docs/linux/drivers/sound/adau1701/)
if host-side DSP programming becomes a future requirement.

## Remaining checks

- Exact board revision and its I²S input connector pinout/electrical specification.
- Whether the proposed 32-bit slots are accepted and how input selection, mute
  and Bluetooth/line-in priority work in the installed module firmware.
- Whether its present DSP program uses the digital input and persists after power
  cycling; do not assume the product page specifies a self-boot setup.
- Pi kernel/overlay availability, actual ALSA device/capabilities, installed
  `.asoundrc` and includes, CamillaDSP service configuration and version.
- Separate left/right playback, volume, startup/standby, all required sources,
  taps and long-running buffer/XRUN behavior.

No target hardware was accessed. This note records the next concrete design,
not a verified wiring instruction or implemented feature.
