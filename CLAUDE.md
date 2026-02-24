# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Build and Run Commands

```bash
# Setup virtual environment
uv venv
source .venv/bin/activate.fish
uv sync

# Run the application
python src/main.py
```

## Architecture

SpeechSnap is a Push-to-Talk (PTT) speech-to-text application for Linux (Wayland). Hold a key to record audio, release to transcribe and paste text.

### Key Components

- **Entry point**: `src/main.py` - async main function that instantiates and runs the App
- **Application**: `src/app.py` - main App class orchestrating PTT workflow; supports dependency injection for all components
- **Protocols**: `src/protocols.py` - Protocol interfaces (`STTProtocol`, `StorageProtocol`, `AudioRecorderProtocol`, `KeyboardListenerProtocol`, `TextTyperProtocol`) enabling dependency injection and testing
- **Configuration**: `src/config/` - pydantic-settings based config
  - `Config.py` - singleton config accessed via `config = get_config()`, auto-loads `.env`; `setup_logging()` is a separate function
  - `Paths.py` - centralized path management relative to project root
- **Keyboard**: `src/keyboard/` - PTT listener (`listener.py`, evdev) and text pasting (`typer.py`, wl-copy + ydotool)
- **Audio**: `src/audio/` - audio recording via sounddevice
- **STT**: `src/stt/` - speech-to-text using faster-whisper (GPU/CPU)
- **Storage**: `src/storage/` - daily transcription logs

### Configuration Pattern

Import the singleton config anywhere via:
```python
from config import config
```

Config provides settings for:
- Whisper model (language, model name for GPU/CPU, beam_size, VAD filter)
- Audio recording (samplerate, channels, blocksize, gain, min duration)
- PTT key binding and paste delays

To initialize logging separately:
```python
from config import setup_logging
setup_logging(config.LOG_LEVEL)
```

### Text Pasting

`KeyboardTyper` pastes text via clipboard (`wl-copy`) + Ctrl+V (`ydotool`). Features:
- Saves and restores previous clipboard content
- Sanitizes text before pasting (strips control characters)
- Auto-detects active RDP sessions (Remmina) and applies `RDP_PASTE_DELAY`
- Auto-starts `ydotoold` daemon via `start_ydotoold.sh` if not running

### Dependencies

- **faster-whisper**: Local speech-to-text transcription
- **torch**: Deep learning framework (Whisper backend)
- **sounddevice**: Audio recording
- **evdev**: Kernel-level keyboard input
- **pydantic-settings**: Environment-based configuration

### System Requirements

- Linux with Wayland
- User must be in `input` group (for evdev)
- `wl-clipboard` and `ydotool` installed
- `start_ydotoold.sh` script present in project root (auto-starts ydotoold daemon)
- CUDA (optional, for GPU acceleration)

### Environment Variables

Copy `.env.example` to `.env` and configure:
- `WHISPER_LANGUAGE` - transcription language (default: `"pl"`)
- `WHISPER_MODEL` - model for GPU (default: `"large-v3"`)
- `WHISPER_MODEL_CPU` - model for CPU (default: `"base"`)
- `WHISPER_BEAM_SIZE` - beam search size (default: `5`)
- `WHISPER_VAD_FILTER` - voice activity detection filter (default: `true`)
- `AUDIO_SAMPLERATE` - sample rate in Hz (default: `16000`)
- `AUDIO_CHANNELS` - number of channels (default: `1`)
- `AUDIO_BLOCKSIZE` - recording block size (default: `1024`)
- `AUDIO_GAIN` - microphone gain multiplier (default: `2.0`)
- `MIN_RECORDING_DURATION` - minimum recording length in seconds (default: `1.5`)
- `PTT_KEY` - push-to-talk key (default: `"KEY_RIGHTCTRL"`)
- `PASTE_DELAY` - fixed delay before paste in seconds (default: `0.0`, auto-detects RDP)
- `RDP_PASTE_DELAY` - delay used when RDP session detected (default: `0.2`)
- `LOG_LEVEL` - logging level (default: `"INFO"`)
