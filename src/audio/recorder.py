"""Audio recorder for PTT using sounddevice."""

import logging
from typing import Any, Self

import numpy as np
import sounddevice as sd

logger = logging.getLogger(__name__)


class AudioRecorder:
    """Async-compatible audio recorder for PTT."""

    def __init__(self, samplerate: int = 16000, channels: int = 1, blocksize: int = 1024, gain: float = 1.0):
        self.samplerate = samplerate
        self.channels = channels
        self.blocksize = blocksize
        self.gain = gain

        self._stream: sd.InputStream | None = None
        self._chunks: list[np.ndarray] = []
        self._is_recording = False

    def _audio_callback(self, indata: np.ndarray, frames: int, _time: Any, status: Any) -> None:
        """Callback called from audio thread."""
        if status:
            logger.warning("Audio status: %s", status)
        if self._is_recording:
            if self.gain != 1.0:
                amplified = np.clip(indata * self.gain, -32768, 32767).astype(np.int16)
                self._chunks.append(amplified)
            else:
                self._chunks.append(indata.copy())

    def start(self) -> None:
        """Start recording."""
        self._chunks = []
        self._is_recording = True

        self._stream = sd.InputStream(
            samplerate=self.samplerate,
            channels=self.channels,
            dtype=np.int16,
            blocksize=self.blocksize,
            callback=self._audio_callback,
        )
        self._stream.start()

    def stop(self) -> np.ndarray:
        """Stop recording and return audio."""
        self._is_recording = False

        if self._stream:
            try:
                self._stream.stop()
            except Exception:
                logger.exception("Error stopping audio stream")
            try:
                self._stream.close()
            except Exception:
                logger.exception("Error closing audio stream")
            finally:
                self._stream = None

        if self._chunks:
            return np.concatenate(self._chunks)
        return np.array([], dtype=np.int16)

    @property
    def is_recording(self) -> bool:
        return self._is_recording

    async def __aenter__(self) -> Self:
        """Async context manager entry - start recording."""
        self.start()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: Any,
    ) -> bool:
        """Async context manager exit - stop recording and cleanup."""
        self.stop()
        return False
