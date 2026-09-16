"""E2E listener tests for ovos-vad-plugin-noise.

Uses ovoscope's MiniListener and MiniVoiceLoop harnesses to exercise the
NoiseVAD plugin against real audio from test/fixtures/command.wav.

The fixture is a 16-bit PCM mono WAV at 16 kHz containing a spoken command
(debiased energy peaks ~9800).  The VAD is configured with:

    method=threshold, energy_threshold=200

so that zero-byte silence → is_silence=True and speech chunks → is_silence=False.
"""
import os
import wave
import struct
import pytest

FIXTURE = os.path.join(os.path.dirname(__file__), "fixtures", "command.wav")
CHUNK_SIZE = 960  # 30 ms @ 16 kHz 16-bit mono


def _speech_chunk_from_fixture() -> bytes:
    """Return a 960-byte PCM chunk with measurable energy from the fixture."""
    with wave.open(FIXTURE, "rb") as wf:
        frames = wf.readframes(wf.getnframes())
    # Chunk at offset 18*960 has peak energy (~9800 debiased)
    return frames[18 * CHUNK_SIZE: 19 * CHUNK_SIZE]


def _make_vad():
    """Instantiate NoiseVAD with a fixed threshold tuned for the fixture."""
    from ovos_vad_plugin_noise import NoiseVAD
    return NoiseVAD(config={
        "method": "threshold",
        "energy_threshold": 200,
    })


# ---------------------------------------------------------------------------
# Part 1 — direct VAD assertions
# ---------------------------------------------------------------------------

def test_vad_silence_on_zero_chunk():
    """All-zero bytes must be classified as silence."""
    vad = _make_vad()
    silent = b"\x00" * CHUNK_SIZE
    assert vad.is_silence(silent) is True


def test_vad_speech_on_fixture_chunk():
    """A speech chunk from the fixture must NOT be classified as silence."""
    vad = _make_vad()
    speech = _speech_chunk_from_fixture()
    assert vad.is_silence(speech) is False


# ---------------------------------------------------------------------------
# Part 2 — MiniListener VAD integration
# ---------------------------------------------------------------------------

def test_mini_listener_vad_silence():
    """MiniListener.is_silence proxies to the real NoiseVAD correctly."""
    from ovoscope.listener import get_mini_listener

    vad = _make_vad()
    listener = get_mini_listener(vad_instance=vad)
    try:
        silent = b"\x00" * CHUNK_SIZE
        assert listener.is_silence(silent) is True
    finally:
        listener.shutdown()


def test_mini_listener_vad_speech():
    """MiniListener.is_silence returns False on a speech chunk."""
    from ovoscope.listener import get_mini_listener

    vad = _make_vad()
    listener = get_mini_listener(vad_instance=vad)
    try:
        speech = _speech_chunk_from_fixture()
        assert listener.is_silence(speech) is False
    finally:
        listener.shutdown()


# ---------------------------------------------------------------------------
# Part 3 — MiniVoiceLoop full-pipeline (best-effort)
# ---------------------------------------------------------------------------

def test_voice_loop_utterance_from_fixture():
    """Drive fixture through MiniVoiceLoop and assert recognizer_loop:utterance.

    Uses:
    - NoiseVAD (real) as VAD
    - MockHotWordEngine triggering immediately as wake word
    - MockStreamingSTT returning a fixed transcript
    - MockFileMicrophone streaming command.wav

    The loop should emit recognizer_loop:wakeword, record_begin, record_end,
    and recognizer_loop:utterance.
    """
    from ovoscope.voice_loop import (
        MiniVoiceLoop,
        MockHotWordEngine,
        MockStreamingSTT,
    )

    vad = _make_vad()
    ww = MockHotWordEngine(key_phrase="hey_mycroft", trigger_after=1)
    stt = MockStreamingSTT(transcript="turn on the lights")

    with MiniVoiceLoop(
        ww_instances={"hey_mycroft": ww},
        vad_instance=vad,
        stt_instance=stt,
    ) as vl:
        msgs = vl.feed_file(FIXTURE, silence_tail_chunks=30)

    types = [m.msg_type for m in msgs]
    assert "recognizer_loop:utterance" in types, (
        f"Expected recognizer_loop:utterance in captured messages: {types}"
    )
