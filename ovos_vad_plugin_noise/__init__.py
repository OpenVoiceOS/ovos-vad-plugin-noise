from ovos_plugin_manager.templates.vad import VADEngine

from ovos_vad_plugin_noise.silence import SilenceDetector, SilenceMethod


class NoiseVAD(VADEngine):
    def __init__(self, config=None, sample_rate=None):
        super().__init__(config, sample_rate)
        method = self.config.get("method") or SilenceMethod.ALL
        max_energy = self.config.get("max_energy")
        max_current_ratio_threshold = self.config.get("max_current_ratio_threshold", 2.0)
        current_energy_threshold = self.config.get("energy_threshold")
        self.vad = SilenceDetector(silence_method=method,
                                   max_current_ratio_threshold=max_current_ratio_threshold,
                                   current_energy_threshold=current_energy_threshold,
                                   max_energy=max_energy)

    def reset(self):
        self.vad.reset()

    def is_silence(self, chunk):
        return self.vad.is_silence(chunk)
