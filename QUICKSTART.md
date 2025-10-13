# Quick Start Guide

## Zero-Setup (No Dev Tools)

If you just want it to work without fiddling with developer tools:

```bash
cd /home/wtyler/pdanet-linux
./scripts/quickstart.sh
```

What it does:
- Creates a local Python environment
- Installs needed Python packages
- Runs quick self-checks (no network, no sudo)
- Starts the GUI if GTK is available (prints install tips otherwise)

Logs are stored under `.tmp_config/pdanet-linux/pdanet.log` inside this folder.

---

## 1. Install

```bash
cd /home/wtyler/pdanet-linux
sudo ./install.sh
```

## 2. Connect Android

1. Plug in Android device via USB
2. Open PdaNet+ app
3. Enable "Activate USB Mode"

## 3. Connect Linux

```bash
sudo pdanet-connect
```

## 4. (Optional) Enable Stealth

```bash
sudo pdanet-stealth enable
```

## 5. Disconnect

```bash
sudo pdanet-disconnect
```

---

## Troubleshooting One-Liners

**Check if USB tethering interface exists:**
```bash
ip link show | grep -E "usb|rndis"
```

**Test PdaNet proxy directly:**
```bash
curl -x http://192.168.49.1:8000 http://www.google.com
```

**View redsocks status:**
```bash
sudo systemctl status redsocks
```

**Check iptables rules:**
```bash
sudo iptables -t nat -L REDSOCKS -n -v
```

**Full system test:**
```bash
curl -v http://www.google.com
```

---

## Common Commands

| Command | Description |
|---------|-------------|
| `sudo pdanet-connect` | Connect to PdaNet |
| `sudo pdanet-disconnect` | Disconnect from PdaNet |
| `sudo pdanet-stealth enable` | Hide tethering from carrier |
| `sudo pdanet-stealth disable` | Disable stealth mode |
| `sudo pdanet-stealth status` | Check stealth status |
| `sudo ./uninstall.sh` | Remove pdanet-linux |

---

**Need help?** See README.md for detailed documentation
