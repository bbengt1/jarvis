"""Text-to-speech synthesis."""

import asyncio
import io
import subprocess
import tempfile
from pathlib import Path
from typing import Any

import numpy as np
import sounddevice as sd

from core.config import TTSSettings


class TextToSpeech:
    """Handles text-to-speech using Piper.

    Piper is a fast, local neural TTS system.
    Falls back to system TTS if Piper is unavailable.
    """

    def __init__(self, settings: TTSSettings) -> None:
        self.settings = settings
        self._piper_available: bool | None = None
        self._sample_rate = 22050

    def _check_piper(self) -> bool:
        """Check if Piper is available."""
        if self._piper_available is None:
            try:
                result = subprocess.run(
                    ["piper", "--version"],
                    capture_output=True,
                    timeout=5,
                )
                self._piper_available = result.returncode == 0
            except (FileNotFoundError, subprocess.TimeoutExpired):
                self._piper_available = False
        return self._piper_available

    async def synthesize(self, text: str) -> bytes:
        """Convert text to audio bytes.

        Args:
            text: Text to synthesize

        Returns:
            Raw audio bytes (22050Hz, mono, int16)
        """
        if self._check_piper():
            return await self._synthesize_piper(text)
        return await self._synthesize_system(text)

    async def _synthesize_piper(self, text: str) -> bytes:
        """Synthesize using Piper TTS."""
        loop = asyncio.get_running_loop()

        def run_piper() -> bytes:
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
                output_path = f.name

            try:
                subprocess.run(
                    [
                        "piper",
                        "--model",
                        self.settings.voice,
                        "--output_file",
                        output_path,
                    ],
                    input=text.encode(),
                    capture_output=True,
                    check=True,
                )

                # Read the wav file
                import wave

                with wave.open(output_path, "rb") as wf:
                    return wf.readframes(wf.getnframes())
            finally:
                Path(output_path).unlink(missing_ok=True)

        return await loop.run_in_executor(None, run_piper)

    async def _synthesize_system(self, text: str) -> bytes:
        """Fallback to system TTS (macOS say, espeak, etc.)."""
        loop = asyncio.get_running_loop()

        def run_system_tts() -> bytes:
            import platform
            import wave

            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
                output_path = f.name

            try:
                system = platform.system()

                if system == "Darwin":  # macOS
                    # Convert to AIFF first, then to WAV
                    aiff_path = output_path.replace(".wav", ".aiff")
                    subprocess.run(
                        ["say", "-o", aiff_path, text],
                        check=True,
                        capture_output=True,
                    )
                    subprocess.run(
                        ["afconvert", "-f", "WAVE", "-d", "LEI16", aiff_path, output_path],
                        check=True,
                        capture_output=True,
                    )
                    Path(aiff_path).unlink(missing_ok=True)
                elif system == "Linux":
                    subprocess.run(
                        ["espeak", "-w", output_path, text],
                        check=True,
                        capture_output=True,
                    )
                else:
                    raise RuntimeError(f"No TTS available for {system}")

                with wave.open(output_path, "rb") as wf:
                    return wf.readframes(wf.getnframes())
            finally:
                Path(output_path).unlink(missing_ok=True)

        return await loop.run_in_executor(None, run_system_tts)

    async def speak(self, text: str) -> None:
        """Synthesize and play text through speakers."""
        audio_data = await self.synthesize(text)

        # Convert to numpy array and play
        audio_array = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768.0

        # Play audio
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(
            None,
            lambda: sd.play(audio_array, self._sample_rate, blocking=True),
        )

    async def close(self) -> None:
        """Cleanup resources."""
        pass
