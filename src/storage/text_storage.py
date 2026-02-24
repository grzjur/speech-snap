"""
Text storage module for saving transcriptions to daily JSON log files.

Transcriptions are saved as JSON arrays to daily files in the data directory.
"""

import json
import logging
from datetime import datetime
from pathlib import Path

from config import config

logger = logging.getLogger(__name__)


class TextStorage:
    """
    Stores transcribed text in daily JSON log files.

    Each day gets a separate file (YYYY-MM-DD.json) with entries as JSON array.
    Files are created automatically in the configured data directory.
    """

    def __init__(self) -> None:
        """Initialize storage with data directory from config."""
        self.data_dir = config.paths.path_to_data
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def _get_daily_file(self) -> Path:
        """
        Get the path to today's log file.

        Returns:
            Path to the daily log file (YYYY-MM-DD.json)
        """
        today = datetime.now().strftime("%Y-%m-%d")
        return self.data_dir / f"{today}.json"

    def save(self, text: str, role: str = "user") -> None:
        """
        Save transcribed text to the daily JSON log file.

        Each entry contains role, content, and ISO 8601 timestamp.
        Empty text is silently ignored.

        Args:
            text: Transcribed text to save
            role: Role identifier (default: "user")

        Raises:
            OSError: If file cannot be written
        """
        if not text:
            return

        file_path = self._get_daily_file()

        entries: list[dict] = []
        if file_path.exists():
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    entries = json.load(f)
            except (json.JSONDecodeError, OSError):
                logger.warning("Cannot read %s, creating new file", file_path)
                entries = []

        entry = {
            "role": role,
            "content": text,
            "timestamp": datetime.now().astimezone().isoformat(),
        }
        entries.append(entry)

        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(entries, f, ensure_ascii=False, indent=2)
        except OSError:
            logger.exception("Failed to save text to %s", file_path)
            raise
