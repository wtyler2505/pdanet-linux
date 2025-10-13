#!/usr/bin/env bash
set -Eeuo pipefail

echo "[+] Running ruff lint..." && ruff .
echo "[+] Running bandit on src/..." && bandit -q -r src
echo "[+] Running pip-audit..." && pip-audit || true
echo "[+] Security checks completed"

