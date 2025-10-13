#!/usr/bin/env bash
set -Eeuo pipefail

echo "==> PdaNet Linux - Developer Setup"

if ! command -v sudo >/dev/null 2>&1; then
  echo "[!] sudo not found; run this script as root or install sudo." >&2
  exit 1
fi

if ! command -v apt-get >/dev/null 2>&1; then
  echo "[!] This helper targets Debian/Ubuntu/Mint (apt). Install deps manually on your distro." >&2
else
  echo "==> Installing system packages (sudo apt-get)"
  sudo apt-get update -qq
  sudo DEBIAN_FRONTEND=noninteractive apt-get install -y -qq \
    python3-venv python3-pip python3-dev build-essential \
    python3-gi python3-gi-cairo gir1.2-gtk-3.0 gir1.2-appindicator3-0.1 \
    imagemagick x11-utils gnome-screenshot scrot \
    python3-keyring python3-numpy
fi

echo "==> Creating virtual environment (.venv)"
python3 -m venv .venv
source .venv/bin/activate

python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt

echo "==> Installing pre-commit hooks"
if command -v pre-commit >/dev/null 2>&1; then
  pre-commit install || true
else
  echo "[i] pre-commit not on PATH yet; it will be available inside the venv."
  .venv/bin/pre-commit install || true
fi

echo "==> Done. Activate venv with: source .venv/bin/activate"
