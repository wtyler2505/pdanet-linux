# CI Environment Setup

The automated test suite includes GUI, networking, and system-integration scenarios that require additional packages and relaxed sandboxing. Configure continuous integration runners with the prerequisites below to avoid false negatives.

## Base Packages

Install the following system dependencies prior to running the test matrix:

```bash
sudo apt-get update
sudo apt-get install -y \
  xvfb \
  dbus-x11 \
  gnome-screenshot \
  imagemagick \
  gir1.2-gtk-3.0 \
  gir1.2-appindicator3-0.1 \
  python3-gi \
  python3-gi-cairo \
  iptables \
  redsocks \
  curl
```

## Python Tooling

Set up the Python environment with the repo requirements and visual-testing extras:

```bash
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt
python3 -m pip install pytest pytest-cov pytest-xvfb pytest-timeout numpy pillow pyvirtualdisplay memory-profiler psutil
```

## Headless Display

GUI and visual regression tests assume an X server. Start Xvfb before invoking the test suite:

```bash
export DISPLAY=:99
Xvfb $DISPLAY -screen 0 1920x1080x24 &
sleep 3
```

## Privilege Requirements

Network integration scenarios create iptables chains and interact with redsocks. Run the test job with sufficient privileges (sudo or an elevated container) and allow access to `/usr/sbin` utilities. Disable restrictive seccomp profiles when running Docker-based CI to permit socket creation and iptables manipulation.

## Recommended Test Invocation

```bash
pytest tests/ --cov=src \
  --cov-report=term-missing \
  --maxfail=1 \
  --timeout=120
```

For environments that cannot provide elevated privileges, skip the network-heavy suites with `-m "not network"` after marking those tests accordingly.
