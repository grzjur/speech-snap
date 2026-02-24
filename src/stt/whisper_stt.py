"""Local audio transcription using faster-whisper."""

import logging

import numpy as np
import torch
from faster_whisper import WhisperModel

from config import config

logger = logging.getLogger(__name__)


class WhisperSTT:
    """Local audio transcription using faster-whisper."""

    def __init__(self) -> None:
        self._model: WhisperModel | None = None

    def _load_model(self) -> WhisperModel:
        """Lazy loading of Whisper model with CPU fallback."""
        if self._model is not None:
            return self._model

        # Try CUDA
        if torch.cuda.is_available():
            logger.info("Loading Whisper model: %s (cuda)", config.WHISPER_MODEL)
            try:
                self._model = WhisperModel(
                    config.WHISPER_MODEL,
                    device="cuda",
                    compute_type="float16",
                )
                return self._model
            except Exception as e:
                logger.warning("CUDA unavailable (%s), falling back to CPU", e)

        # Fallback to CPU
        logger.info("Loading Whisper model: %s (cpu)", config.WHISPER_MODEL_CPU)
        self._model = WhisperModel(
            config.WHISPER_MODEL_CPU,
            device="cpu",
            compute_type="int8",
        )
        return self._model

    def transcribe(self, audio: np.ndarray, samplerate: int = 16000) -> str:
        """Transcribe audio to text.

        Args:
            audio: Numpy array with audio data (int16 or float32)
            samplerate: Sample rate (default 16000 Hz)

        Returns:
            Transcribed text
        """
        model = self._load_model()

        # Flatten to 1D (sounddevice returns 2D even for mono)
        if audio.ndim > 1:
            audio = audio.flatten()

        # Convert int16 -> float32 if needed
        if audio.dtype == np.int16:
            audio = audio.astype(np.float32) / 32768.0

        segments, info = model.transcribe(
            audio,
            language=config.WHISPER_LANGUAGE,
            beam_size=config.WHISPER_BEAM_SIZE,
            vad_filter=config.WHISPER_VAD_FILTER,
        )

        text = " ".join(segment.text.strip() for segment in segments)
        return text.strip()
