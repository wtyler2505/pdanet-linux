# Repository Guidelines

## Project Structure & Module Organization
Core application logic lives in `src/`, with `pdanet_gui_v2.py`, `connection_manager.py`, and `stats_collector.py` orchestrating the GTK interface, connection state machine, and telemetry. Shell automation resides in `scripts/` (for carrier bypass, NetworkManager helpers, and docs tooling). Systemd-ready launchers and desktop entries live under `config/`. Automated tests, including GUI baselines, are grouped in `tests/` with visual assets in `tests/visual/`. Generated reference material and ADRs belong in `docs/`, while executable wrappers (`pdanet-wifi-connect`, `pdanet-connect`, etc.) sit at the repo root for packaging.

## Build, Test, and Development Commands
Set up dependencies, run checks, and regenerate docs with the canonical commands:
```bash
pip install --break-system-packages -r requirements.txt  # local dev setup
pytest tests/ --cov=src --cov-report=html                # full suite + coverage
pytest tests/ --no-network --no-sudo                     # fast offline smoke
make docs                                                # rebuild architecture docs
sudo ./install.sh                                        # system install + symlinks
```
Each script is idempotent—rerun after significant changes to validate tooling and packaging.

## Coding Style & Naming Conventions
Python code follows PEP 8 with 4-space indentation and `snake_case` functions; GTK classes stay `CamelCase`. Run `black`, `isort`, `flake8`, and `mypy` before pushing (the `.claude` hooks expect clean output). Keep modules ASCII-only unless interacting with GTK resources, and favor explicit type hints for new APIs.

## Testing Guidelines
Pytest drives coverage; target ≥90% on touched modules to align with existing metrics. Name test files `test_<component>.py` and pytest classes `Test<Component>`. Mark slow scenarios with `@pytest.mark.performance` or `@pytest.mark.integration` so contributors can toggle them via `-m` filters. Visual regressions live in `tests/visual/`; regenerate baselines with `make baselines` only after UI changes are approved.

## Commit & Pull Request Guidelines
Current history includes automated checkpoints, so human commits should restore clarity: use an imperative subject like `gui: tighten bandwidth graph refresh`. Reference relevant scripts/modules in the body, note test coverage (`pytest ...`), and attach screenshots when GUI surfaces change. PRs should include a succinct summary, linked issue or ticket, and a checklist confirming install/test commands were executed.

## Security & Configuration Tips
Network tooling modifies iptables and sudoers; restrict experiments to disposable interfaces and avoid committing host-specific files from `~/.config/pdanet-linux/`. When editing stealth scripts, keep TTL defaults and blocked-domain lists conservative, and document any carrier-facing change in the PR description for traceability.
