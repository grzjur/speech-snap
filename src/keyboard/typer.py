"""
Module for typing text into active window.
Uses clipboard (wl-copy) + Ctrl+V via ydotool.
"""

import logging
import subprocess
import shutil
import time
from dataclasses import dataclass, field
from pathlib import Path

from config import config

logger = logging.getLogger(__name__)

# ydotool key codes (Linux input event codes)
KEY_LEFTCTRL = 29
KEY_V = 47


def sanitize_text(text: str) -> str:
    """
    Sanitize text before pasting to prevent potential injection.

    Removes or escapes characters that could be dangerous when pasted
    into terminals or other input fields.

    Args:
        text: Raw text from transcription

    Returns:
        Sanitized text safe for pasting
    """
    if not text:
        return text

    # Remove control characters except newline and tab
    sanitized = "".join(
        char for char in text
        if char in ("\n", "\t") or (ord(char) >= 32 and ord(char) != 127)
    )
    return sanitized.strip()


@dataclass
class KeyboardTyper:
    """Pastes text to active window via clipboard."""

    _old_clipboard: str | None = field(default=None, init=False)
    _project_root: Path = field(default_factory=lambda: Path(__file__).parent.parent.parent)

    def __post_init__(self):
        self._check_tools()

    def _check_tools(self) -> None:
        """Checks if required tools are available."""
        if not shutil.which("wl-copy"):
            raise RuntimeError(
                "wl-copy not found. "
                "Install: sudo pacman -S wl-clipboard"
            )
        if not shutil.which("ydotool"):
            raise RuntimeError(
                "ydotool not found. "
                "Install: sudo pacman -S ydotool"
            )

        self._ensure_ydotoold_running()

    def _ensure_ydotoold_running(self) -> None:
        """Starts ydotoold if not running."""
        result = subprocess.run(["pgrep", "-x", "ydotoold"], capture_output=True)
        if result.returncode == 0:
            return  # already running

        script_path = self._project_root / "start_ydotoold.sh"
        if not script_path.exists():
            raise RuntimeError(
                f"Script {script_path} does not exist. "
                "Run manually: ydotoold &"
            )

        subprocess.run(["bash", str(script_path)], check=True)
        time.sleep(0.5)  # allow time to start

        result = subprocess.run(["pgrep", "-x", "ydotoold"], capture_output=True)
        if result.returncode != 0:
            raise RuntimeError(
                "Failed to start ydotoold. "
                "Run manually: ydotoold &"
            )

    def _save_clipboard(self) -> None:
        """Saves current clipboard content."""
        try:
            result = subprocess.run(
                ["wl-paste", "--no-newline"],
                capture_output=True,
                timeout=1
            )
            self._old_clipboard = result.stdout.decode() if result.returncode == 0 else None
        except UnicodeDecodeError:
            self._old_clipboard = None  # binary content (e.g. image), skip restore
        except subprocess.TimeoutExpired:
            self._old_clipboard = None

    def _has_active_rdp_connection(self) -> bool:
        """Returns True if Remmina has an active RDP TCP connection."""
        try:
            result = subprocess.run(
                ["ss", "-tnp"], capture_output=True, text=True, timeout=1
            )
            return "remmina" in result.stdout.lower() and ":3389" in result.stdout
        except (subprocess.TimeoutExpired, OSError):
            return False

    def _restore_clipboard(self) -> None:
        """Restores previous clipboard content."""
        if self._old_clipboard is not None:
            subprocess.run(
                ["wl-copy", self._old_clipboard],
                check=False
            )

    def type_text(self, text: str, restore_clipboard: bool = True) -> None:
        """
        Pastes text to active window (immediately via Ctrl+V).

        Args:
            text: Text to paste
            restore_clipboard: Whether to restore previous clipboard content
        """
        if not text:
            return

        # Sanitize text to prevent injection attacks
        text = sanitize_text(text)
        if not text:
            return

        if restore_clipboard:
            self._save_clipboard()

        # Copy to clipboard
        subprocess.run(["wl-copy", text], check=True)

        # Allow clipboard to sync (important for RDP sessions, e.g., Remmina)
        delay = config.PASTE_DELAY
        if delay == 0.0 and self._has_active_rdp_connection():
            delay = config.RDP_PASTE_DELAY
        if delay > 0:
            logger.info("Paste delay: %.2fs (RDP active)", delay)
            time.sleep(delay)

        # Ctrl+V using ydotool key codes
        # Format: keycode:state (1=press, 0=release)
        ctrl_v_sequence = [
            f"{KEY_LEFTCTRL}:1",  # Press Ctrl
            f"{KEY_V}:1",         # Press V
            f"{KEY_V}:0",         # Release V
            f"{KEY_LEFTCTRL}:0",  # Release Ctrl
        ]
        subprocess.run(["ydotool", "key", *ctrl_v_sequence], check=True)

        if restore_clipboard:
            self._restore_clipboard()

    def press_key(self, key: str) -> None:
        """Presses a single key."""
        subprocess.run(["ydotool", "key", key], check=True)

    def hotkey(self, *keys: str) -> None:
        """Presses a key combination."""
        combo = "+".join(keys)
        subprocess.run(["ydotool", "key", combo], check=True)
