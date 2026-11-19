# Extension interface inventory

Baseline: `c340e1b`, version `4.1.0`, generated from AST/source on 2026-11-18.

This index covers the 25 extensions registered in `main.py`, in registration order.
Signatures omit `self`. Lifecycle hooks (`start`, `stop`, `event`) are omitted.
`config_update` is an internal settings callback, although the current dispatcher
does not distinguish it from other handlers. Calls/events list literal names only;
dynamic source routes and dynamically chosen targets require the architecture map.
Defaults are first-install YAML seeds, not the values in an existing database.
The inventory was generated without importing extensions or starting services.

## config

Implementation: [config/config.py](../../config/config.py).

Handlers:

- `config.set(config)`
- `config.get()`

Published events: `config_updated`.

No `config.yaml`; initial configuration is `{}`.

## dsp

Implementation: [dsp/dsp.py](../../dsp/dsp.py).

Handlers:

- `dsp.config_update(config)`
- `dsp.service(state: str)`
- `dsp.set_capture_gain(gain=None)`
- `dsp.get_capture_device()`
- `dsp.set_capture_device(device: str=None, gain: float=None, samplerate: int=None, sampleformat=None, ext: str=None)`
- `dsp.volume_to_db(volume: int)`
- `dsp.db_to_volume(volume_db: float)`
- `dsp.get_volume()`
- `dsp.set_volume(volume_db: float=None)`
- `dsp.get_mute()`
- `dsp.set_mute(mute: bool=False)`
- `dsp.toggle_mute()`
- `dsp.signal_levels()`
- `dsp.status()`
- `dsp.get_config()`
- `dsp.set_config(config)`

Literal core calls: `display.start_cava`, `multiroom.start_snapserver`, `multiroom.stop_snapserver`.

Published events: `dsp_options_changed`, `dsp_options_error`, `dsp_state_changed`, `error`, `system`.

First-install defaults:

```yaml
default_capture_device: hw:CARD=Loopback,DEV=1
default_gain: -15
resample_rate: 48000
```

## system

Implementation: [system/system.py](../../system/system.py).

Handlers:

- `system.config_update(config)`
- `system.datetime()`
- `system.standby()`
- `system.power_state()`
- `system.shutdown()`
- `system.reboot()`
- `system.set_hostname(hostname: str)`
- `system.info()`

Literal core calls: `bluetooth.adapter_set_state`, `source.set`.

Published events: `system`, `system_power_state_changed`, `system_time_updated`.

First-install defaults:

```yaml
hostname: "berryaudio"
timezone: "Europe/Berlin"
hardware: auto
```

## mixer

Implementation: [mixer/mixer.py](../../mixer/mixer.py).

Handlers:

- `mixer.config_update(config)`
- `mixer.set_mute(mute: bool=False)`
- `mixer.get_mute()`
- `mixer.toggle_mute()`
- `mixer.get_volume()`
- `mixer.set_volume(volume: int=0)`
- `mixer.volume_up()`
- `mixer.volume_down()`
- `mixer.alsa_devices(cmd: str, filter_loopback: bool=True)`
- `mixer.alsa_mixer_volume(device: str=None)`
- `mixer.list()`

Literal core calls: `dsp.db_to_volume`, `dsp.get_mute`, `dsp.get_volume`, `dsp.set_mute`, `dsp.set_volume`, `dsp.volume_to_db`.

Published events: `mixer_mute`, `system`, `volume_changed`.

First-install defaults:

```yaml
output_device: hw:CARD=Loopback,DEV=0
hw_device: null
hw_device_id: null
dtoverlay: null
volume_default: 50
volume_device: Software
```

## tracklist

Implementation: [tracklist/tracklist.py](../../tracklist/tracklist.py).

Handlers:

- `tracklist.add_track(uris: list=[], play: bool=False)`
- `tracklist.remove_track(tlid)`
- `tracklist.move_track(start: int, end: int, to_position: int)`
- `tracklist.get_tltracks()`
- `tracklist.clear()`
- `tracklist.get_repeat()`
- `tracklist.set_repeat(value: bool)`
- `tracklist.get_single()`
- `tracklist.set_single(value: bool)`
- `tracklist.get_random()`
- `tracklist.set_random(value: bool)`
- `tracklist.next_track()`
- `tracklist.previous_track()`

Literal core calls: `playback.clear`, `playback.get_current_tl_track`, `playback.play`, `source.set`.

Published events: `options_changed`, `tracklist_cleared`, `tracklist_track_added`, `tracklist_track_removed`, `tracklist_updated`.

First-install defaults:

```yaml
current_queue: []
```

## radio

Implementation: [radio/radio.py](../../radio/radio.py).

Handlers:

- `radio.stop_service()`
- `radio.start_service()`
- `radio.start_stream()`
- `radio.search(query: str)`
- `radio.lookup_track(path: str)`
- `radio.directory(uri: str | None=None, limit: int | None=None, offset: int | None=None)`
- `radio.playback_uri(path: str)`

Literal core calls: `dsp.set_capture_device`, `playback.clear`, `playback.start_stream`.

No `config.yaml`; initial configuration is `{}`.

## source

Implementation: [source/source.py](../../source/source.py).

Handlers:

- `source.directory()`
- `source.update_source(source: object)`
- `source.set(uri: str | None=None)`
- `source.get()`

Published events: `source_changed`, `source_updated`.

No `config.yaml`; initial configuration is `{}`.

## spotify

Implementation: [spotify/spotify.py](../../spotify/spotify.py).

Handlers:

- `spotify.stop_service()`
- `spotify.start_service()`
- `spotify.start_stream()`
- `spotify.message(event)`

Literal core calls: `dsp.set_capture_device`, `playback.clear`, `playback.playback_stop`, `playback.set_metadata`, `playback.set_state`, `playback.set_time_position`, `playback.stop`, `source.update_source`.

Published events: `error`, `spotify_connected`, `spotify_disconnected`, `track_playback_paused`, `track_playback_resumed`, `track_playback_started`, `track_position_updated`.

First-install defaults:

```yaml
output_device: plughw:CARD=Loopback,DEV=0
bitrate: 320
bit_depth: S32
volume_default: 100
volume_normalization: true
```

## shairportsync

Implementation: [shairportsync/shairportsync.py](../../shairportsync/shairportsync.py).

Handlers:

- `shairportsync.stop_service()`
- `shairportsync.start_service()`
- `shairportsync.start_stream()`

Literal core calls: `dsp.set_capture_device`, `playback.clear`, `playback.set_metadata`, `playback.set_state`, `playback.set_time_position`, `source.update_source`.

Published events: `error`, `shairportsync_connected`, `shairportsync_disconnected`, `track_position_updated`.

No `config.yaml`; initial configuration is `{}`.

## bluetooth

Implementation: [bluetooth/bluetooth.py](../../bluetooth/bluetooth.py).

Handlers:

- `bluetooth.start_stream()`
- `bluetooth.start_service()`
- `bluetooth.stop_service()`
- `bluetooth.adapter_set_state(state: bool)`
- `bluetooth.adapter_get_state()`
- `bluetooth.devices(rescan: bool=False)`
- `bluetooth.device(address: str | None=None)`
- `bluetooth.trust(address: str)`
- `bluetooth.connect(address: str)`
- `bluetooth.disconnect(address: str)`
- `bluetooth.remove(address: str)`
- `bluetooth.device_command(mac_address: str, command: str)`
- `bluetooth.set_volume(address: str, volume: int | None=None, soft_volume: bool=True, mute: bool=False)`

Literal core calls: `dsp.service`, `dsp.set_capture_device`, `playback.clear`, `playback.set_metadata`, `playback.set_state`, `source.get`, `source.set`, `source.update_source`.

Published events: `bluetooth_device_connected`, `bluetooth_device_disconnected`, `bluetooth_device_removed`, `bluetooth_device_updated`, `bluetooth_discoverable`, `bluetooth_pairable`, `bluetooth_powered`.

First-install defaults:

```yaml

```

## local

Implementation: [local/local.py](../../local/local.py).

Handlers:

- `local.search(query: str)`
- `local.directory(uri: str | None=None, limit: int | None=None, offset: int | None=None)`
- `local.playback_uri(path: str)`
- `local.lookup_track(path: str)`
- `local.stop_service()`
- `local.start_service()`
- `local.start_stream()`
- `local.clean()`
- `local.scan_progress()`
- `local.scan()`
- `local.scan_artists()`

Literal core calls: `dsp.set_capture_device`, `playback.clear`, `playback.start_stream`.

Published events: `scan_artist_updated`, `scan_update`.

First-install defaults:

```yaml
library_path: []
```

## search

Implementation: [search/search.py](../../search/search.py).

Handlers:

- `search.search(query)`

Literal core calls: `local.search`, `radio.search`.

No `config.yaml`; initial configuration is `{}`.

## storage

Implementation: [storage/storage.py](../../storage/storage.py).

Handlers:

- `storage.config_update(config)`
- `storage.start_service()`
- `storage.stop_service()`
- `storage.playback_uri(path: str)`
- `storage.lookup_track(path: str)`
- `storage.start_stream()`
- `storage.directory(uri: str=None, limit: int | None=None, offset: int | None=None)`
- `storage.add_to_library(uri: str)`
- `storage.mount(dev: str)`
- `storage.unmount(dev: str)`
- `storage.add_shared(ip: str, username: str=None, password: str=None)`
- `storage.mount_shared(devs: list[str])`
- `storage.unmount_shared(dev: str)`
- `storage.list_smb_shared()`
- `storage.list_shares()`
- `storage.unshare(uri: str)`
- `storage.share(uri: str, name: str=None, read_only: bool=False)`

Literal core calls: `playback.clear`, `playback.start_stream`.

First-install defaults:

```yaml
username: null
password: null
smb_clients: {}
```

## playlist

Implementation: [playlist/playlist.py](../../playlist/playlist.py).

Handlers:

- `playlist.directory(uri: str | None=None, limit: int | None=None, offset: int | None=None)`
- `playlist.edit(uri: str, name: str)`
- `playlist.delete(uri: str)`
- `playlist.create(name: str | None=None, tl_tracks: list[TlTrack] | None=None)`
- `playlist.move_track(uri: str, start: int, end: int, to_position: int)`
- `playlist.remove_track(uri: str, tlid: int)`
- `playlist.add_track(uris: list[str], track_uris: list[str])`

Published events: `playlist_created`, `playlist_removed`, `playlist_renamed`, `playlist_track_added`, `playlist_track_removed`, `playlist_updated`.

No `config.yaml`; initial configuration is `{}`.

## playback

Implementation: [playback/playback.py](../../playback/playback.py).

Handlers:

- `playback.clear()`
- `playback.get_current_tl_track()`
- `playback.get_state()`
- `playback.set_state(state: PlaybackState)`
- `playback.get_time_position()`
- `playback.set_time_position(position_ms: int)`
- `playback.set_metadata(tl_track: TlTrack | None=None)`
- `playback.start_stream()`
- `playback.play(uri: str | None=None, tlid: int | None=0)`
- `playback.seek(time_position: int)`
- `playback.next()`
- `playback.previous()`
- `playback.pause()`
- `playback.playback_stop()`

Literal core calls: `collection.recently_played`, `dsp.set_capture_device`, `source.set`, `tracklist.next_track`, `tracklist.previous_track`.

Published events: `error`, `playback_buffering`, `playback_state_changed`, `track_meta_updated`, `track_playback_ended`, `track_playback_paused`, `track_playback_resumed`, `track_playback_started`, `track_position_updated`.

First-install defaults:

```yaml
background_albumart: true
```

## network

Implementation: [network/network.py](../../network/network.py).

Handlers:

- `network.start_ap_mode()`
- `network.stop_ap_mode()`
- `network.devices()`
- `network.device(ifname)`
- `network.connection(name)`
- `network.disconnect(ifname)`
- `network.connect(ifname)`
- `network.device_down(name)`
- `network.device_up(name)`
- `network.delete(name)`
- `network.modify(ifname, name, ipv4_address, ipv4_gateway, ipv4_dns, method='auto')`
- `network.connect_wlan(ssid, password)`
- `network.wifi(rescan=False)`

Published events: `network_state_changed`.

First-install defaults:

```yaml
apmode_password: 12345678
```

## multiroom

Implementation: [multiroom/multiroom.py](../../multiroom/multiroom.py).

Handlers:

- `multiroom.config_update(config)`
- `multiroom.start_service()`
- `multiroom.stop_service()`
- `multiroom.stop_snapserver()`
- `multiroom.start_snapserver(timeout=10)`
- `multiroom.stop_snapclient()`
- `multiroom.start_snapclient(ip)`
- `multiroom.servers()`
- `multiroom.disconnect(ip=None)`
- `multiroom.connect(ip)`
- `multiroom.add_stream(ip)`
- `multiroom.remove_stream(ip)`
- `multiroom.get_status(ip)`
- `multiroom.set_volume(ip, client_id, volume=None, mute=False)`

Literal core calls: `dsp.get_capture_device`, `playback.clear`, `playback.set_metadata`, `source.set`, `source.update_source`.

Published events: `error`, `multiroom_client_connected`, `multiroom_client_disconnected`, `multiroom_server_connected`, `multiroom_server_disconnected`, `multiroom_server_updated`, `multiroom_stream_update`.

First-install defaults:

```yaml
client_device: plughw:CARD=Loopback,DEV=0
server_device: hw:Loopback,1,1
server: false
codec: opus
chunk: 50
buffer: 1024
```

## display

Implementation: [display/display.py](../../display/display.py).

Handlers:

- `display.config_update(config)`
- `display.get_displays()`

Literal core calls: `bluetooth.connect`, `bluetooth.devices`, `bluetooth.disconnect`, `gpio.set_encoder_mode`, `local.directory`, `playback.play`, `radio.directory`, `snapcast.servers`, `source.directory`, `source.set`, `storage.directory`, `system.standby`.

Published events: `command`.

First-install defaults:

```yaml
output_display: null
visualizer_layout: 7
```

## collection

Implementation: [collection/collection.py](../../collection/collection.py).

Handlers:

- `collection.favourite(item)`
- `collection.recently_played(track: Track)`
- `collection.directory(uri: str | None=None, limit: int | None=None, offset: int | None=None)`

Published events: `favourite_added`, `favourite_removed`.

First-install defaults:

```yaml
library_path: []
```

## tuner

Implementation: [tuner/tuner.py](../../tuner/tuner.py).

Handlers:

- `tuner.config_update(config)`
- `tuner.start_service()`
- `tuner.start_stream()`
- `tuner.stop_service()`
- `tuner.directory(uri: str | None=None, limit: int | None=None, offset: int | None=None)`
- `tuner.preset_add(channel, name=None)`
- `tuner.preset_edit(id)`
- `tuner.preset_delete(id)`
- `tuner.get_channel()`
- `tuner.set_channel(channel)`
- `tuner.seek_up(auto=False)`
- `tuner.seek_down(auto=False)`
- `tuner.playback_uri(path: str)`
- `tuner.lookup_track(path: str)`
- `tuner.devices(device=None)`

Literal core calls: `dsp.set_capture_device`, `dsp.set_capture_gain`, `playback.clear`, `playback.set_metadata`, `source.get`, `source.set`.

Published events: `channel_updated`, `preset_saved`, `system`.

First-install defaults:

```yaml
hw_device: null
input_device: null
sample_rate: 44100
bit_depth: S16_LE
gain: 0
```

## webrtc

Implementation: [webrtc/webrtc.py](../../webrtc/webrtc.py).

No `config.yaml`; initial configuration is `{}`.

## linein

Implementation: [linein/linein.py](../../linein/linein.py).

Handlers:

- `linein.config_update(config)`
- `linein.start_service()`
- `linein.start_stream()`
- `linein.stop_service()`

Literal core calls: `dsp.set_capture_device`, `dsp.set_capture_gain`, `playback.clear`, `playback.set_metadata`, `source.get`.

Published events: `system`.

First-install defaults:

```yaml
input_device: null
sample_rate: 44100
bit_depth: S16_LE
gain: 0
```

## command

Implementation: [command/command.py](../../command/command.py).

Handlers:

- `command.config_update(config)`

Literal core calls: `mixer.toggle_mute`, `mixer.volume_down`, `mixer.volume_up`, `playback.next`, `playback.play`, `playback.previous`, `playback.stop`, `system.standby`.

No `config.yaml`; initial configuration is `{}`.

## usbdac

Implementation: [usbdac/usbdac.py](../../usbdac/usbdac.py).

Handlers:

- `usbdac.init(enable=False)`
- `usbdac.config_update(config)`
- `usbdac.start_service()`
- `usbdac.start_stream()`
- `usbdac.stop_service()`

Literal core calls: `dsp.set_capture_device`, `dsp.set_capture_gain`, `playback.set_metadata`, `source.get`.

Published events: `system`.

First-install defaults:

```yaml
enable: false
input_device: hw:CARD=UAC2Gadget,DEV=0
sample_rate: 44100
bit_depth: S16_LE
gain: -10
```

## web

Implementation: [web/web.py](../../web/web.py).

No `config.yaml`; initial configuration is `{}`.

## Other hardware code

`gpio` and `infrared` are not registered in the baseline `main.py`.
`mixer/local/` is not the active library extension. Drivers, widgets and utilities
do not automatically create independently routed extensions. See
[architecture](architecture.md) for their ownership and deployment dependencies.
