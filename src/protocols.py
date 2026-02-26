"""Protocol interfaces for SpeechSnap components.

These protocols define the contracts that components must follow,
enabling dependency injection, testing, and alternative implementations.
"""

from collections.abc import Awaitable, Callable
from typing import Protocol

import numpy as np


class STTProtocol(Protocol):
    """Protocol for speech-to-text engines."""

    def transcribe(self, audio: np.ndarray, samplerate: int = 16000) -> str:
        """Transcribe audio to text.

        Args:
            audio: Numpy array with audio data (int16 or float32)
            samplerate: Sample rate (default 16000 Hz)

        Returns:
            Transcribed text
        """
        ...


class StorageProtocol(Protocol):
    """Protocol for text storage backends."""

    def save(self, text: str, role: str = "user") -> None:
        """Save transcribed text.

        Args:
            text: Transcribed text to save
            role: Role identifier (default: "user")
        """
        ...


class AudioRecorderProtocol(Protocol):
    """Protocol for audio recording."""

    samplerate: int

    def start(self) -> None:
        """Start recording."""
        ...

    def stop(self) -> np.ndarray:
        """Stop recording and return audio.

        Returns:
            Numpy array with recorded audio data
        """
        ...


class KeyboardListenerProtocol(Protocol):
    """Protocol for keyboard/PTT listeners."""

    async def listen(
        self,
        on_press: Callable[[], Awaitable[None]],
        on_release: Callable[[], Awaitable[None]],
        on_cancel: Callable[[], Awaitable[None]] | None = None,
    ) -> None:
        """Listen for key events.

        Args:
            on_press: async callback called when key is pressed
            on_release: async callback called when key is released (no combo)
            on_cancel: async callback called when key is released after a combo key
                       was pressed; if None, on_release is used as fallback
        """
        ...


class TextTyperProtocol(Protocol):
    """Protocol for text input/typing."""

    def type_text(self, text: str, restore_clipboard: bool = True) -> None:
        """Type/paste text to active window.

        Args:
            text: Text to type/paste
            restore_clipboard: Whether to restore previous clipboard content
        """
        ...
