# Noise VAD

simple VAD plugin extracted from the old [ovos-listener](https://github.com/OpenVoiceOS/ovos-listener/blob/dev/ovos_listener/silence.py)

should only be used as fallback, works in all platforms including 32bit systems

## Configuration


```javascript
{
    "listener": {
        "VAD": {
            "module": "ovos-vad-plugin-noise",
            "ovos-vad-plugin-noise": {
                "method": "all",
                "max_current_ratio_threshold": 2.0,
                "initial_energy_threshold": 1000.0
            }
        }
    }
}
```

Arguments

    max_energy: Optional[float] = None
        Maximum denoise energy value (None for dynamic setting from observed audio)

    max_current_ratio_threshold: Optional[float] = 2.0
        Ratio of max/current energy below which audio is considered speech

    current_energy_threshold: Optional[float] = 1000.0
        Energy threshold above which audio is considered speech

    silence_method: SilenceMethod = "all"
        Method for deciding if an audio chunk contains silence or speech

Methods

    RATIO_ONLY
      Only use max/current energy ratio threshold

    CURRENT_ONLY
      Only use current energy threshold

    ALL
      max/current energy ratio, and current energy threshold