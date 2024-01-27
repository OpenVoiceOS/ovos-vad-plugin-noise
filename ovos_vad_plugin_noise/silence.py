# Copyright 2022 Mycroft AI Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import audioop
import typing
from enum import Enum


class SilenceMethod(str, Enum):
    """Method used to determine if an audio frame contains silence.

    Values
    ------
    RATIO
      Only use max/current energy ratio threshold

    THRESHOLD
      Only use current energy threshold

    ALL
      max/current energy ratio, and current energy threshold
    """
    RATIO = "ratio"
    THRESHOLD = "threshold"
    ALL = "all"


class SilenceDetector:
    """Detect speech/silence using noise threshold

    Attributes
    ----------
    max_energy: Optional[float] = None
        Maximum denoise energy value (None for dynamic setting from observed audio)

    max_current_ratio_threshold: Optional[float] = None
        Ratio of max/current energy below which audio is considered speech

    current_energy_threshold: Optional[float] = None
        Energy threshold above which audio is considered speech

    silence_method: SilenceMethod = "all"
        Method for deciding if an audio chunk contains silence or speech
    """

    def __init__(
            self,
            max_energy: typing.Optional[float] = None,
            max_current_ratio_threshold: typing.Optional[float] = None,
            current_energy_threshold: typing.Optional[float] = None,
            silence_method: SilenceMethod = SilenceMethod.ALL
    ):
        self.energy = 0

        self.max_energy = max_energy
        self.dynamic_max_energy = max_energy is None
        self.dynamic_thresh = current_energy_threshold is None
        self.max_current_ratio_threshold = max_current_ratio_threshold
        self.current_energy_threshold = current_energy_threshold
        self.silence_method = silence_method

        if self.silence_method in [
            SilenceMethod.RATIO,
            SilenceMethod.ALL,
        ]:
            self.use_ratio = True
            assert (
                    self.max_current_ratio_threshold is not None
            ), "Max/current ratio threshold is required"
        else:
            self.use_ratio = False

        if self.silence_method in [
            SilenceMethod.THRESHOLD,
            SilenceMethod.ALL,
        ]:
            self.use_current = True
        else:
            self.use_current = False

        if not self.use_current and not self.use_ratio:
            self.use_ratio = True

    def reset(self):
        self.energy = 0
        if self.dynamic_thresh and self.max_energy:
            self.current_energy_threshold = self.max_energy * 0.3
        if self.dynamic_max_energy:
            self.max_energy = None

    def is_silence(self, chunk: bytes, energy: typing.Optional[float] = None) -> bool:
        """True if audio chunk contains silence."""
        all_silence = True

        if self.use_ratio or self.use_current:
            # Compute debiased energy of audio chunk
            energy = SilenceDetector.get_debiased_energy(chunk)

            if self.use_ratio:
                # Ratio of max/current energy compared to threshold
                if self.dynamic_max_energy:
                    # Overwrite max energy
                    if self.max_energy is None:
                        self.max_energy = energy
                    else:
                        self.max_energy = max(energy, self.max_energy)

                assert self.max_energy is not None
                if energy > 0:
                    ratio = self.max_energy / energy
                else:
                    # Not sure what to do here
                    ratio = 0

                assert self.max_current_ratio_threshold is not None
                all_silence = all_silence and (ratio > self.max_current_ratio_threshold)
            elif self.use_current and self.current_energy_threshold is not None:
                # Current energy compared to threshold
                all_silence = all_silence and (energy < self.current_energy_threshold)

        if all_silence or not self.energy:
            self.energy = energy
        return all_silence

    @staticmethod
    def get_debiased_energy(audio_data: bytes) -> float:
        """Compute RMS of debiased audio."""
        # Thanks to the speech_recognition library!
        # https://github.com/Uberi/speech_recognition/blob/master/speech_recognition/__init__.py
        energy = -audioop.rms(audio_data, 2)
        energy_bytes = bytes([energy & 0xFF, (energy >> 8) & 0xFF])
        debiased_energy = audioop.rms(
            audioop.add(audio_data, energy_bytes * (len(audio_data) // 2), 2), 2
        )

        # Probably actually audio if > 30
        return debiased_energy
