import logging
from functools import lru_cache

from pydantic_settings import BaseSettings
from dotenv import load_dotenv
from pydantic import Field
from .Paths import Paths

load_dotenv()


class Config(BaseSettings):
    """Application configuration loaded from environment variables."""

    VERSION: str = "0.0.1"
    paths: Paths = Field(default_factory=Paths)

    # STT configuration
    WHISPER_LANGUAGE: str = Field(default="en")
    WHISPER_MODEL: str = Field(default="large-v3")
    WHISPER_MODEL_CPU: str = Field(default="base")
    WHISPER_BEAM_SIZE: int = Field(default=5)
    WHISPER_VAD_FILTER: bool = Field(default=True)

    # Audio configuration
    AUDIO_SAMPLERATE: int = Field(default=16000)
    AUDIO_CHANNELS: int = Field(default=1)
    AUDIO_BLOCKSIZE: int = Field(default=1024)
    AUDIO_GAIN: float = Field(default=2.0)
    MIN_RECORDING_DURATION: float = Field(default=1.5)

    # PTT configuration
    PTT_KEY: str = Field(default="KEY_RIGHTCTRL")
    PASTE_DELAY: float = Field(default=0.0)
    RDP_PASTE_DELAY: float = Field(default=0.2)

    # Logging
    LOG_LEVEL: str = Field(default="INFO")


@lru_cache()
def get_config() -> Config:
    return Config()


def setup_logging(level: str = "INFO") -> None:
    """Configure logging for the application."""
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )


config = get_config()
