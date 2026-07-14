"""
sound_manager.py
Generates small synthesized WAV tones for UI sound effects (button click,
correct answer, wrong answer, quiz completion) the first time the app
runs -- no external audio assets or internet connection required -- and
plays them cross-platform in a background thread so the UI never blocks.
"""

import math
import os
import struct
import threading
import wave

from src import config

SAMPLE_RATE = 44100

# (filename, list of (frequency_hz, duration_seconds) tones played in sequence)
_TONE_DEFINITIONS = {
    "click.wav": [(880, 0.05)],
    "correct.wav": [(660, 0.09), (990, 0.12)],
    "wrong.wav": [(300, 0.08), (200, 0.16)],
    "complete.wav": [(523, 0.12), (659, 0.12), (784, 0.12), (1046, 0.2)],
}


def _synthesize_wav(path, tones, volume=0.35):
    frames = bytearray()
    for freq, duration in tones:
        n_samples = int(SAMPLE_RATE * duration)
        for i in range(n_samples):
            t = i / SAMPLE_RATE
            # simple sine wave with a short fade-out to avoid clicks
            fade = 1.0 - (i / n_samples)
            sample = math.sin(2 * math.pi * freq * t) * volume * fade
            value = int(sample * 32767)
            frames += struct.pack("<h", value)
    with wave.open(path, "w") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(SAMPLE_RATE)
        wav_file.writeframes(bytes(frames))


def ensure_sound_assets():
    """Generate the WAV tone files into assets/sounds if they don't already
    exist. Safe to call every startup."""
    os.makedirs(config.SOUNDS_DIR, exist_ok=True)
    for filename, tones in _TONE_DEFINITIONS.items():
        path = os.path.join(config.SOUNDS_DIR, filename)
        if not os.path.exists(path):
            try:
                _synthesize_wav(path, tones)
            except Exception:
                pass  # non-fatal: app should still run without sound


class SoundManager:
    """Cross-platform, non-blocking sound effect player."""

    def __init__(self, enabled=True):
        self.enabled = enabled
        ensure_sound_assets()
        self._winsound = None
        try:
            import winsound  # type: ignore
            self._winsound = winsound
        except ImportError:
            self._winsound = None

    def set_enabled(self, enabled):
        self.enabled = enabled

    def _play_path(self, path):
        if not self.enabled or not os.path.exists(path):
            return

        def _worker():
            try:
                if self._winsound:
                    self._winsound.PlaySound(path, self._winsound.SND_FILENAME)
                else:
                    import subprocess
                    import sys
                    if sys.platform == "darwin":
                        subprocess.run(["afplay", path], check=False,
                                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    else:
                        subprocess.run(["aplay", "-q", path], check=False,
                                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except Exception:
                pass  # sound is a nice-to-have, never crash the app

        threading.Thread(target=_worker, daemon=True).start()

    def play_click(self):
        self._play_path(os.path.join(config.SOUNDS_DIR, "click.wav"))

    def play_correct(self):
        self._play_path(os.path.join(config.SOUNDS_DIR, "correct.wav"))

    def play_wrong(self):
        self._play_path(os.path.join(config.SOUNDS_DIR, "wrong.wav"))

    def play_complete(self):
        self._play_path(os.path.join(config.SOUNDS_DIR, "complete.wav"))
