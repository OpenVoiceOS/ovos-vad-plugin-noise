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
                "energy_threshold": 1000.0
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

    energy_threshold: Optional[float] = None
        Energy threshold above which audio is considered speech (None for dynamic setting from observed audio)

    silence_method: SilenceMethod = "all"
        Method for deciding if an audio chunk contains silence or speech

Methods

    RATIO
      Only use max/current energy ratio threshold

    THRESHOLD
      Only use current energy threshold

    ALL
      max/current energy ratio, and current energy threshold