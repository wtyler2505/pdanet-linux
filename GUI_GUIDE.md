# 🎨 PdaNet Linux - GUI Guide

## Badass GUI Features 🔥

Your PdaNet Linux client now includes a **full-featured GTK graphical interface** with:

✅ **Modern Dark Theme** - Sleek, professional appearance
✅ **System Tray Icon** - Quick access from notification area
✅ **One-Click Connect/Disconnect** - Big, clear buttons
✅ **Real-time Status** - Live connection monitoring
✅ **Stealth Mode Toggle** - Easy carrier bypass control
✅ **Connection Info** - Interface detection & proxy status

---

## Launching the GUI

### Method 1: Application Menu
1. Open your application menu (Menu button)
2. Search for **"PdaNet Linux"**
3. Click to launch

### Method 2: Command Line
```bash
pdanet-gui
```

### Method 3: System Tray
- GUI stays in system tray when running
- Right-click tray icon for quick actions
- Click icon to show/hide window

---

## GUI Interface Tour

### Main Window

```
╔══════════════════════════════════════╗
║       ⚡ PdaNet Linux ⚡              ║
╠══════════════════════════════════════╣
║  ┌─ Connection Status ─────────────┐ ║
║  │  ● DISCONNECTED / CONNECTED     │ ║
║  │                                 │ ║
║  │  Interface: usb0                │ ║
║  │  Proxy: 192.168.49.1:8000       │ ║
║  │  Stealth Mode: Enabled/Disabled │ ║
║  └─────────────────────────────────┘ ║
║                                      ║
║  ┌─────────────────────────────────┐ ║
║  │     🔌 CONNECT / DISCONNECT     │ ║ <- Big Button
║  └─────────────────────────────────┘ ║
║                                      ║
║  🕶️ Stealth Mode:  [  Switch  ]     ║
║                                      ║
║  [ℹ️ About]          [❌ Quit]       ║
╚══════════════════════════════════════╝
```

### Color Coding

- **Green** - Connected status
- **Red** - Disconnected status
- **Cyan** - Headers and emphasis
- **Gray** - Information labels

---

## Using the GUI

### Connecting to PdaNet

1. **Prepare Android Device:**
   - Connect phone via USB
   - Open PdaNet+ app on Android
   - Enable "Activate USB Mode"

2. **In PdaNet Linux GUI:**
   - Click the big **"🔌 CONNECT"** button
   - Wait for connection (5-10 seconds)
   - Status will change to **"● CONNECTED"** in green

3. **Verify:**
   - Check interface shows (e.g., "usb0")
   - System tray icon updates
   - Try browsing the internet

### Disconnecting

1. Click the **"🔌 DISCONNECT"** button
2. Status changes to **"● DISCONNECTED"**
3. Internet reverts to normal connection

### Stealth Mode

**What it does:**
- Hides tethering from carrier detection
- Normalizes TTL values
- Blocks OS update services

**How to use:**
1. Toggle the **Stealth Mode** switch ON
2. Stealth status updates immediately
3. Works while connected or disconnected

### System Tray Features

**Right-click tray icon for:**
- Show Window
- Connect/Disconnect (quick action)
- Quit

**Icon changes:**
- 📶 Connected - Wireless connected icon
- 📡 Disconnected - Wireless disconnected icon

---

## GUI vs CLI Comparison

| Feature | GUI | CLI |
|---------|-----|-----|
| Ease of Use | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| Visual Feedback | ✅ Real-time | ❌ Manual |
| System Tray | ✅ Yes | ❌ No |
| Status Monitoring | ✅ Automatic | ❌ Manual check |
| Stealth Toggle | ✅ One click | Manual command |
| Scripting | ❌ Not designed for it | ✅ Perfect |
| Resource Usage | ~50MB RAM | ~5MB RAM |

**Recommendation:** Use GUI for daily use, CLI for scripts/automation

---

## Keyboard Shortcuts

Currently, the GUI doesn't have custom keyboard shortcuts, but you can use standard GTK shortcuts:

- **Alt+F4** - Close window
- **Tab** - Navigate between controls
- **Space** - Activate buttons/switches

---

## Troubleshooting GUI

### "Command not found: pdanet-gui"
**Solution:**
```bash
# Reinstall
cd /home/wtyler/pdanet-linux
sudo ./install.sh
```

### GUI Won't Start
**Check dependencies:**
```bash
python3 -c "import gi; gi.require_version('Gtk', '3.0'); from gi.repository import Gtk; print('GTK OK')"
```

**Expected output:** `GTK OK`

If error, reinstall dependencies:
```bash
sudo apt install python3-gi python3-gi-cairo gir1.2-gtk-3.0 gir1.2-appindicator3-0.1
```

### Connection Button Doesn't Work
**Check sudo permissions:**
```bash
sudo -n /home/wtyler/pdanet-linux/pdanet-connect
```

If it asks for password, reinstall to fix sudoers:
```bash
cd /home/wtyler/pdanet-linux
sudo ./install.sh
```

### Status Not Updating
- Click the main button to refresh
- GUI auto-updates every 1 second
- Check system logs: `sudo journalctl -u redsocks -f`

### System Tray Icon Missing
**Cinnamon desktop:**
```bash
# Install system tray extension if needed
```

**Check AppIndicator:**
```bash
dpkg -l | grep appindicator
```

---

## Advanced GUI Features

### Background Operation
- GUI can run minimized to system tray
- Close window (X button) = minimize to tray
- Use "Quit" button to fully exit

### Auto-Start (Optional)
To launch GUI on login:

1. Open "Startup Applications"
2. Add new startup program:
   - **Name:** PdaNet Linux
   - **Command:** `pdanet-gui`
   - **Comment:** PdaNet tethering manager

---

## GUI Technical Details

**Technology Stack:**
- **Language:** Python 3
- **GUI Framework:** GTK 3 (PyGObject)
- **System Tray:** AppIndicator3
- **Theme:** GTK Dark Theme
- **Custom CSS:** Gradient buttons, color-coded status

**Resource Usage:**
- Memory: ~40-60 MB
- CPU: <1% when idle
- Disk: ~50 KB (Python script)

**Compatibility:**
- Linux Mint 22.2 Cinnamon ✅
- Ubuntu 24.04 ✅
- Other GTK-based desktops ✅
- GNOME (may need gnome-shell-extension-appindicator)
- KDE Plasma (may need additional packages)

---

## Screenshots Reference

### Connected State
```
Status: ● CONNECTED (green)
Button: 🔌 DISCONNECT (red)
Interface: usb0
Stealth: Enabled
```

### Disconnected State
```
Status: ● DISCONNECTED (red)
Button: 🔌 CONNECT (green)
Interface: Not detected
Stealth: Disabled
```

---

## Future GUI Features (Planned)

Potential improvements:
- [ ] Connection history/logs viewer
- [ ] Data usage statistics
- [ ] Auto-reconnect on disconnect
- [ ] Multiple device support
- [ ] Bandwidth monitoring
- [ ] Notifications on connection change
- [ ] Custom keyboard shortcuts
- [ ] Light theme option

---

## Comparison with Windows PdaNet GUI

| Feature | Windows PdaNet | PdaNet Linux GUI |
|---------|----------------|------------------|
| Connect Button | ✅ | ✅ |
| Status Display | ✅ | ✅ |
| Stealth Mode | ✅ | ✅ |
| System Tray | ✅ | ✅ |
| Auto-start | ✅ | ⚠️ Manual setup |
| WiFi Direct | ✅ | ❌ (USB only) |
| Bluetooth | ✅ | ❌ (USB only) |
| Dark Theme | ❌ | ✅ |
| Open Source | ❌ | ✅ |

---

## Getting Help

**GUI not working?**
1. Check `GUI_GUIDE.md` troubleshooting section (this file)
2. Try CLI instead: `sudo pdanet-connect`
3. Check logs: `sudo journalctl -u redsocks -f`

**Want to customize?**
- GUI source: `/home/wtyler/pdanet-linux/src/pdanet-gui.py`
- Desktop file: `/usr/share/applications/pdanet-linux.desktop`
- CSS styling is in the Python file (modify `load_custom_css()`)

---

**Enjoy your badass GUI! 🚀**
