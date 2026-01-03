"""Main J.A.R.V.I.S. coordinator."""

import asyncio
import signal
from typing import Any

from core.config import Settings
from core.context import ConversationContext


class Jarvis:
    """Central orchestrator for J.A.R.V.I.S.

    Coordinates all subsystems: speech recognition, LLM, TTS, vision, and home automation.
    Runs an async event loop handling concurrent inputs from voice, vision sensors, etc.
    """

    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or Settings()
        self.context = ConversationContext(max_messages=self.settings.max_context_messages)
        self._running = False
        self._subsystems: dict[str, Any] = {}

    async def initialize(self) -> None:
        """Initialize all subsystems."""
        self.settings.ensure_data_dir()

        # Import here to avoid circular imports and allow lazy loading
        from brain.llm import LLMClient
        from speech.recognition import SpeechRecognizer
        from speech.synthesis import TextToSpeech
        from speech.wakeword import WakeWordDetector

        # Initialize core subsystems
        print("Initializing LLM client...")
        self._subsystems["llm"] = LLMClient(self.settings.llm)
        print("Initializing speech recognition...")
        self._subsystems["stt"] = SpeechRecognizer(self.settings.whisper)
        print("Initializing text-to-speech...")
        self._subsystems["tts"] = TextToSpeech(self.settings.tts)
        print("Initializing wake word detector...")
        self._subsystems["wakeword"] = WakeWordDetector(self.settings)

        # Initialize optional subsystems
        if self.settings.vision.camera_index >= 0:
            from vision.processor import VisionProcessor

            print("Initializing vision processor...")
            self._subsystems["vision"] = VisionProcessor(self.settings.vision)

        if self.settings.home_assistant.enabled:
            from home.automation import HomeAutomation

            print("Initializing home automation...")
            self._subsystems["home"] = HomeAutomation(
                self.settings.home_assistant,
                self.settings.mqtt,
            )

    async def process_voice_input(self, audio_data: bytes) -> str | None:
        """Process voice input and return response."""
        stt = self._subsystems.get("stt")
        llm = self._subsystems.get("llm")
        tts = self._subsystems.get("tts")

        if not all([stt, llm, tts]):
            return None

        # Speech to text
        text = await stt.transcribe(audio_data)
        if not text:
            return None

        # Check for wake word if not in active conversation
        if not self.context.messages and self.settings.wake_word.lower() not in text.lower():
            return None

        # Add to context and get LLM response
        self.context.add_user_message(text)
        response = await llm.generate(self.context.get_messages_for_llm())
        self.context.add_assistant_message(response)

        # Speak response
        await tts.speak(response)

        return response

    async def process_text_input(self, text: str) -> str:
        """Process text input and return response."""
        llm = self._subsystems.get("llm")
        if not llm:
            return "LLM not initialized"

        self.context.add_user_message(text)
        response = await llm.generate(self.context.get_messages_for_llm())
        self.context.add_assistant_message(response)

        return response

    async def run(self) -> None:
        """Main run loop."""
        self._running = True

        # Set up signal handlers
        loop = asyncio.get_running_loop()
        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(sig, lambda: asyncio.create_task(self.shutdown()))

        print(f"\n{self.settings.name} initialized. Listening for wake word '{self.settings.wake_word}'...")
        print("Say the wake word followed by your command.\n")

        # Main loop - listen for wake word and process commands
        wakeword = self._subsystems.get("wakeword")
        stt = self._subsystems.get("stt")
        llm = self._subsystems.get("llm")
        tts = self._subsystems.get("tts")

        if wakeword and stt and llm and tts:
            async for detection in wakeword.listen():
                if not self._running:
                    break

                print(f"[Wake word detected: {detection.wake_word} ({detection.confidence:.2f})]")

                # Transcribe the audio captured after wake word
                if detection.audio_after is not None:
                    print("Transcribing...")
                    text = await stt.transcribe(detection.audio_after)

                    if text:
                        print(f"You said: {text}")

                        # Get LLM response
                        self.context.add_user_message(text)
                        print("Thinking...")
                        response = await llm.generate(self.context.get_messages_for_llm())
                        self.context.add_assistant_message(response)

                        print(f"{self.settings.name}: {response}")

                        # Speak the response
                        await tts.speak(response)
                    else:
                        print("(No speech detected after wake word)")
                else:
                    print("(No audio captured)")
        else:
            print("Error: Required subsystems not initialized")
            print(f"  wakeword: {wakeword is not None}")
            print(f"  stt: {stt is not None}")
            print(f"  llm: {llm is not None}")
            print(f"  tts: {tts is not None}")

    async def shutdown(self) -> None:
        """Graceful shutdown."""
        print(f"\n{self.settings.name} shutting down...")
        self._running = False

        # Cleanup subsystems
        for name, subsystem in self._subsystems.items():
            if hasattr(subsystem, "close"):
                await subsystem.close()


async def async_main() -> None:
    """Async entry point."""
    jarvis = Jarvis()
    await jarvis.initialize()
    await jarvis.run()


def main() -> None:
    """Entry point."""
    asyncio.run(async_main())


if __name__ == "__main__":
    main()
