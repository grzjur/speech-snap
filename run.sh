#!/bin/bash

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Check system dependencies
check_dependencies() {
    local missing=()

    command -v ydotool &>/dev/null || missing+=("ydotool")
    command -v wl-copy &>/dev/null || missing+=("wl-clipboard")

    if [ ${#missing[@]} -ne 0 ]; then
        log_error "Missing dependencies: ${missing[*]}"
        log_info "Install with: sudo pacman -S ${missing[*]}"
        exit 1
    fi
}

# Ensure ydotoold is running
start_ydotoold() {
    if ! pgrep -x "ydotoold" > /dev/null; then
        log_info "Starting ydotoold..."
        ydotoold &
        sleep 0.5
    fi
}

# Setup virtual environment if needed
setup_venv() {
    if [ ! -d ".venv" ]; then
        log_info "Creating virtual environment..."
        uv venv
        log_info "Installing dependencies..."
        uv sync
    fi
}

# Main
check_dependencies
start_ydotoold
setup_venv

log_info "Starting SpeechSnap..."
source .venv/bin/activate
exec python src/main.py "$@"
