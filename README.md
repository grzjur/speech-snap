# SpeechSnap

A Speech-to-Text application with Push-to-Talk functionality for Linux. Press a key, speak, and the text automatically appears in the active window.

## Features

- **Push-to-Talk** - right Ctrl key starts recording
- **Local transcription** - Whisper AI without sending data to the cloud
- **Auto-paste** - text is inserted into the active window
- **History** - daily transcription logs in `data/` directory
- **GPU/CPU** - automatic acceleration selection

## System Requirements

- Linux (Wayland/X11)
- Python 3.11+
- `wl-clipboard` and `ydotool`
- User in `input` group

## Installation

```bash
uv venv
source .venv/bin/activate.fish
uv sync
```

## Usage

```bash
# Quick start (recommended)
./run.sh

# Or manually:
./start_ydotoold.sh
python src/main.py
```

## Configuration

Copy `.env.example` to `.env` and adjust settings:

- `WHISPER_MODEL` - Whisper model (default: `large-v3` on GPU, `base` on CPU)
- `WHISPER_LANGUAGE` - transcription language (default: `en`)
