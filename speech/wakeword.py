"""Wake word detection using OpenWakeWord."""

import asyncio
from collections.abc import AsyncIterator
from dataclasses import dataclass
from typing import Any

import numpy as np
import sounddevice as sd

from core.config import Settings


@dataclass
class WakeWordDetection:
    """Result of wake word detection."""

    detected: bool
    confidence: float
    wake_word: str
    audio_after: np.ndarray | None = None  # Audio captured after wake word


class WakeWordDetector:
    """Detects wake words using OpenWakeWord.

    OpenWakeWord is an open-source wake word detection library that
    supports custom wake words without requiring API keys.
    """

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self._model: Any = None
        self._sample_rate = 16000
        self._chunk_size = 1280  # 80ms at 16kHz - required by OpenWakeWord
        self._threshold = 0.5
        self._running = False

    def _load_model(self) -> Any:
        """Lazy load the OpenWakeWord model."""
        if self._model is None:
            from openwakeword.model import Model

            # Load pre-trained models - we'll use "hey_jarvis" as base
            # and add custom "argus" model if available
            self._model = Model(
                wakeword_models=[],  # Use default models
                inference_framework="onnx",
            )
        return self._model

    async def detect_once(self, audio: np.ndarray) -> WakeWordDetection:
        """Check if wake word is present in audio chunk.

        Args:
            audio: Audio data as float32 numpy array (16kHz, mono)

        Returns:
            WakeWordDetection with results
        """
        model = self._load_model()

        loop = asyncio.get_running_loop()

        def run_detection() -> dict[str, float]:
            # OpenWakeWord expects int16 audio
            audio_int16 = (audio * 32767).astype(np.int16)
            prediction = model.predict(audio_int16)
            return prediction

        predictions = await loop.run_in_executor(None, run_detection)

        # Check for any wake word above threshold
        # Also check for variations of our configured wake word
        wake_word = self.settings.wake_word.lower()
        best_match = ""
        best_score = 0.0

        for word, score in predictions.items():
            # Check if this matches our wake word (fuzzy match)
            word_lower = word.lower().replace("_", " ")
            if wake_word in word_lower or word_lower in wake_word:
                if score > best_score:
                    best_score = score
                    best_match = word
            # Also accept any high-confidence detection
            elif score > best_score and score > self._threshold:
                best_score = score
                best_match = word

        return WakeWordDetection(
            detected=best_score >= self._threshold,
            confidence=best_score,
            wake_word=best_match,
        )

    async def listen(self) -> AsyncIterator[WakeWordDetection]:
        """Continuously listen for wake word.

        Yields WakeWordDetection when wake word is detected.
        Buffers audio after detection for immediate transcription.
        """
        self._running = True
        audio_queue: asyncio.Queue[np.ndarray] = asyncio.Queue()
        post_detection_buffer: list[np.ndarray] = []
        detection_cooldown = 0

        # Capture event loop in main thread
        loop = asyncio.get_running_loop()

        def audio_callback(
            indata: np.ndarray, frames: int, time_info: Any, status: Any
        ) -> None:
            if status:
                print(f"Audio status: {status}")
            loop.call_soon_threadsafe(
                audio_queue.put_nowait,
                indata.copy().astype(np.float32).flatten(),
            )

        with sd.InputStream(
            samplerate=self._sample_rate,
            channels=1,
            dtype=np.float32,
            blocksize=self._chunk_size,
            callback=audio_callback,
        ):
            while self._running:
                chunk = await audio_queue.get()

                # Cooldown after detection to prevent rapid re-triggers
                if detection_cooldown > 0:
                    post_detection_buffer.append(chunk)
                    detection_cooldown -= 1
                    if detection_cooldown == 0:
                        # Yield with buffered audio
                        pass
                    continue

                detection = await self.detect_once(chunk)

                if detection.detected:
                    # Start collecting post-detection audio
                    detection_cooldown = 20  # ~1.6 seconds of audio
                    post_detection_buffer = [chunk]

                    # Wait for buffer to fill
                    for _ in range(detection_cooldown):
                        if not self._running:
                            break
                        post_chunk = await audio_queue.get()
                        post_detection_buffer.append(post_chunk)

                    # Combine buffered audio
                    detection.audio_after = np.concatenate(post_detection_buffer)
                    post_detection_buffer = []
                    detection_cooldown = 0

                    yield detection

    async def listen_simple(self) -> AsyncIterator[bool]:
        """Simple wake word listener that just yields True when detected."""
        async for detection in self.listen():
            yield True

    def stop(self) -> None:
        """Stop listening."""
        self._running = False

    async def close(self) -> None:
        """Cleanup resources."""
        self.stop()
        self._model = None
