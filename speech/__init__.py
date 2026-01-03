"""Speech recognition, synthesis, and wake word detection."""

from speech.recognition import SpeechRecognizer
from speech.synthesis import TextToSpeech
from speech.wakeword import WakeWordDetector

__all__ = ["SpeechRecognizer", "TextToSpeech", "WakeWordDetector"]
