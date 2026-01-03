"""Audio utilities."""

import numpy as np


class AudioBuffer:
    """Ring buffer for audio data with voice activity detection."""

    def __init__(
        self,
        sample_rate: int = 16000,
        buffer_seconds: float = 30.0,
        silence_threshold: float = 0.01,
    ) -> None:
        self.sample_rate = sample_rate
        self.buffer_size = int(sample_rate * buffer_seconds)
        self.silence_threshold = silence_threshold
        self._buffer = np.zeros(self.buffer_size, dtype=np.float32)
        self._write_pos = 0
        self._speech_start: int | None = None

    def write(self, audio: np.ndarray) -> None:
        """Write audio data to buffer."""
        audio = audio.flatten()
        n = len(audio)

        if n >= self.buffer_size:
            # Audio larger than buffer, keep last buffer_size samples
            self._buffer[:] = audio[-self.buffer_size :]
            self._write_pos = 0
        elif self._write_pos + n <= self.buffer_size:
            # Fits without wrap
            self._buffer[self._write_pos : self._write_pos + n] = audio
            self._write_pos += n
        else:
            # Wrap around
            first_part = self.buffer_size - self._write_pos
            self._buffer[self._write_pos :] = audio[:first_part]
            self._buffer[: n - first_part] = audio[first_part:]
            self._write_pos = n - first_part

    def is_speech(self, audio: np.ndarray) -> bool:
        """Detect if audio contains speech based on energy."""
        energy = np.sqrt(np.mean(audio**2))
        return energy > self.silence_threshold

    def get_speech_segment(self, min_duration: float = 0.5) -> np.ndarray | None:
        """Get the current speech segment if one is complete.

        Returns audio from speech start to current position if silence detected.
        """
        min_samples = int(min_duration * self.sample_rate)

        if self._speech_start is not None:
            segment_len = (self._write_pos - self._speech_start) % self.buffer_size
            if segment_len >= min_samples:
                # Check if recent audio is silence (speech ended)
                recent = self._buffer[max(0, self._write_pos - 1600) : self._write_pos]
                if not self.is_speech(recent):
                    # Extract segment
                    if self._speech_start < self._write_pos:
                        segment = self._buffer[self._speech_start : self._write_pos].copy()
                    else:
                        segment = np.concatenate(
                            [
                                self._buffer[self._speech_start :],
                                self._buffer[: self._write_pos],
                            ]
                        )
                    self._speech_start = None
                    return segment

        return None

    def clear(self) -> None:
        """Clear the buffer."""
        self._buffer.fill(0)
        self._write_pos = 0
        self._speech_start = None
