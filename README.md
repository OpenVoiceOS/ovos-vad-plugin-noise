# Noise VAD

Noise VAD is a voice activity detection (VAD) plugin for [OpenVoiceOS](https://github.com/OpenVoiceOS). It decides if an audio chunk contains speech by looking at its energy level, not its content.

The plugin comes from the old [ovos-listener](https://github.com/OpenVoiceOS/ovos-listener/blob/dev/ovos_listener/silence.py) project. Use it as a fallback VAD. It runs on all platforms, including 32-bit systems, because it needs no machine learning model.

## Install

```bash
pip install ovos-vad-plugin-noise
```

## Usage

Set `ovos-vad-plugin-noise` as the VAD module in your listener configuration.

```javascript
{
    "listener": {
        "VAD": {
            "module": "ovos-vad-plugin-noise",
            "ovos-vad-plugin-noise": {
                "method": "all",
                "max_current_ratio_threshold": 2.0,
                "energy_threshold": 1000.0
            }
        }
    }
}
```

### Arguments

- `max_energy` (float, optional): maximum denoise energy value. If not set, the plugin sets it dynamically from the observed audio.
- `max_current_ratio_threshold` (float, default `2.0`): ratio of max energy to current energy below which the plugin treats the audio as speech.
- `energy_threshold` (float, optional): energy threshold above which the plugin treats the audio as speech. If not set, the plugin sets it dynamically from the observed audio.
- `silence_method` (string, default `"all"`): method the plugin uses to decide if a chunk contains silence or speech. See Methods below.

### Methods

- `RATIO`: use only the max/current energy ratio threshold.
- `THRESHOLD`: use only the current energy threshold.
- `ALL`: use both the max/current energy ratio and the current energy threshold.

## Related projects

- [ovos-plugin-manager](https://github.com/OpenVoiceOS/ovos-plugin-manager) loads and manages this plugin.
- [ovos-dinkum-listener](https://github.com/OpenVoiceOS/ovos-dinkum-listener) is the OVOS listener that uses VAD plugins like this one.
- [ovos-listener](https://github.com/OpenVoiceOS/ovos-listener) is the original project this plugin's code came from.

## License

Apache-2.0
