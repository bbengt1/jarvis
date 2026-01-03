"""Speech recognition using faster-whisper."""

import asyncio
from collections.abc import AsyncIterator
from typing import Any

import numpy as np
import sounddevice as sd

from core.config import WhisperSettings


class SpeechRecognizer:
    """Handles speech-to-text using faster-whisper.

    Supports both file-based transcription and real-time streaming.
    """

    def __init__(self, settings: WhisperSettings) -> None:
        self.settings = settings
        self._model: Any = None
        self._sample_rate = 16000  # Whisper expects 16kHz
        self._chunk_duration = 2.0  # seconds per chunk

    def _load_model(self) -> Any:
        """Lazy load the Whisper model."""
        if self._model is None:
            from faster_whisper import WhisperModel

            device = self.settings.device
            if device == "auto":
                # faster-whisper uses 'cuda' or 'cpu'
                try:
                    import torch
                    device = "cuda" if torch.cuda.is_available() else "cpu"
                except ImportError:
                    device = "cpu"

            # faster-whisper compute type
            compute_type = "float16" if device == "cuda" else "int8"

            self._model = WhisperModel(
                self.settings.model,
                device=device,
                compute_type=compute_type,
            )
        return self._model

    async def transcribe(self, audio_data: bytes | np.ndarray) -> str:
        """Transcribe audio data to text.

        Args:
            audio_data: Raw audio bytes or numpy array (16kHz, mono, float32)

        Returns:
            Transcribed text
        """
        model = self._load_model()

        # Convert bytes to numpy if needed
        if isinstance(audio_data, bytes):
            audio_array = np.frombuffer(audio_data, dtype=np.float32)
        else:
            audio_array = audio_data.astype(np.float32)

        # Run transcription in thread pool to avoid blocking
        loop = asyncio.get_running_loop()

        def _transcribe() -> str:
            segments, _ = model.transcribe(
                audio_array,
                language=self.settings.language,
                beam_size=5,
                vad_filter=True,
            )
            return " ".join(segment.text for segment in segments).strip()

        result = await loop.run_in_executor(None, _transcribe)
        return result

    async def stream_audio(self) -> AsyncIterator[bytes]:
        """Stream audio from microphone.

        Yields audio chunks suitable for transcription.
        """
        chunk_samples = int(self._sample_rate * self._chunk_duration)
        audio_queue: asyncio.Queue[bytes] = asyncio.Queue()

        # Capture the event loop in the main thread
        loop = asyncio.get_running_loop()

        def audio_callback(
            indata: np.ndarray, frames: int, time_info: Any, status: Any
        ) -> None:
            """Callback for sounddevice stream."""
            if status:
                print(f"Audio status: {status}")
            # Put audio data in queue using the captured loop
            loop.call_soon_threadsafe(
                audio_queue.put_nowait, indata.copy().astype(np.float32).tobytes()
            )

        # Start audio stream
        with sd.InputStream(
            samplerate=self._sample_rate,
            channels=1,
            dtype=np.float32,
            blocksize=chunk_samples,
            callback=audio_callback,
        ):
            while True:
                chunk = await audio_queue.get()
                yield chunk

    async def transcribe_stream(self) -> AsyncIterator[str]:
        """Continuously transcribe from microphone.

        Yields transcribed text segments.
        """
        async for chunk in self.stream_audio():
            text = await self.transcribe(chunk)
            if text:
                yield text

    async def close(self) -> None:
        """Cleanup resources."""
        self._model = None
