"""Main application module for SpeechSnap PTT transcription."""

import asyncio
import logging

from keyboard import KeyboardTyper, PTTListener
from audio import AudioRecorder
from stt import WhisperSTT
from storage import TextStorage
from config import config
from protocols import (
    AudioRecorderProtocol,
    KeyboardListenerProtocol,
    STTProtocol,
    StorageProtocol,
    TextTyperProtocol,
)

logger = logging.getLogger(__name__)


class App:
    """Push-to-talk speech transcription application.

    Orchestrates keyboard listening, audio recording, speech-to-text
    transcription, and text output via clipboard.

    Components can be injected for testing or alternative implementations.
    """

    def __init__(
        self,
        ptt: KeyboardListenerProtocol | None = None,
        typer: TextTyperProtocol | None = None,
        recorder: AudioRecorderProtocol | None = None,
        stt: STTProtocol | None = None,
        storage: StorageProtocol | None = None,
    ) -> None:
        self.ptt = ptt or PTTListener(ptt_key=config.PTT_KEY)
        self.typer = typer or KeyboardTyper()
        self.recorder = recorder or AudioRecorder(
            samplerate=config.AUDIO_SAMPLERATE,
            channels=config.AUDIO_CHANNELS,
            blocksize=config.AUDIO_BLOCKSIZE,
            gain=config.AUDIO_GAIN,
        )
        self.stt = stt or WhisperSTT()
        self.storage = storage or TextStorage()

    async def on_ptt_press(self) -> None:
        """Handle PTT key press - start recording."""
        try:
            logger.info("Recording...")
            self.recorder.start()
        except Exception:
            logger.exception("Failed to start recording")

    async def on_ptt_release(self) -> None:
        """Handle PTT key release - stop recording and transcribe."""
        try:
            audio = self.recorder.stop()
        except Exception:
            logger.exception("Failed to stop recording")
            return

        duration = len(audio) / self.recorder.samplerate

        if duration < config.MIN_RECORDING_DURATION:
            logger.warning("Recording too short (%.1fs) - rejected", duration)
            return

        logger.info("Recorded %.1fs audio (%d samples)", duration, len(audio))
        logger.info("Transcribing...")

        try:
            text = await asyncio.to_thread(self.stt.transcribe, audio, self.recorder.samplerate)
        except Exception:
            logger.exception("Transcription failed")
            return

        if text:
            logger.info("Text: %s", text)
            try:
                self.typer.type_text(text)
            except Exception:
                logger.exception("Failed to type text")
            try:
                self.storage.save(text)
            except Exception:
                logger.exception("Failed to save text")
        else:
            logger.warning("No text to insert")

    async def run(self) -> None:
        """Run the PTT listener loop."""
        logger.info("PTT active. Hold %s to record.", config.PTT_KEY)
        logger.info("Ctrl+C to exit.")
        await self.ptt.listen(self.on_ptt_press, self.on_ptt_release)
