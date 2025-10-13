#!/usr/bin/env bash

set -euo pipefail

echo "PdaNet Linux – Quick Start"
echo "=========================="

# Always log to repo-local tmp to avoid permission issues
export PDANET_LOG_DIR="$(pwd)/.tmp_config/pdanet-linux"

PY=${PYTHON:-python3}
# Prefer system python for GTK (gi) since it's provided by OS packages
SYS_PY=${SYSTEM_PYTHON:-/usr/bin/python3}
if [ ! -x "$SYS_PY" ]; then
  SYS_PY=$(command -v python3 || true)
fi

if ! command -v "$PY" >/dev/null 2>&1; then
  echo "Error: python3 not found. Install Python 3 first." >&2
  exit 1
fi

# Create venv if missing
if [ ! -d .venv ]; then
  echo "Creating virtual environment (.venv)…"
  "$PY" -m venv .venv
fi

echo "Activating virtual environment…"
# shellcheck disable=SC1091
source .venv/bin/activate

PIP_OPTS=${PIP_OPTS:-}

if [ -f requirements.txt ]; then
  echo "Installing Python dependencies…"
  # Prefer system install option if available (Ubuntu/Debian), fallback otherwise
  pip install --upgrade pip >/dev/null
  if pip install --help 2>/dev/null | grep -q -- "break-system-packages"; then
    pip install --break-system-packages -r requirements.txt $PIP_OPTS
  else
    pip install -r requirements.txt $PIP_OPTS
  fi
else
  echo "Warning: requirements.txt not found; skipping dependency install"
fi

echo "Running quick tests (no network, no sudo)…"
pytest tests/ --no-network --no-sudo -q \
  --ignore=tests/visual \
  --ignore=tests/test_gui_components.py || {
  echo "Some tests failed. You can re-run with:"
  echo "  source .venv/bin/activate && pytest tests/ --no-network --no-sudo"
}

echo
echo "GTK check (optional GUI run)…"
if "$SYS_PY" - <<'PY' 2>/dev/null
import gi
gi.require_version('Gtk','3.0')
from gi.repository import Gtk  # noqa: F401
print('GTK: available')
PY
then
  echo "Starting GUI (CTRL+C to exit)…"
  echo "Logs: $PDANET_LOG_DIR/pdanet.log"
  # Use system python so GTK (gi) is available; app loads project modules directly from src/
  "$SYS_PY" src/pdanet_gui_v2.py || true
else
  echo "GTK not available. To enable the GUI, install GTK bindings:"
  echo "  Ubuntu/Debian: sudo apt-get install -y python3-gi gir1.2-gtk-3.0"
  echo "  Fedora: sudo dnf install -y python3-gobject gtk3"
  echo "Then re-run: ./scripts/quickstart.sh"
fi

echo "Done."
