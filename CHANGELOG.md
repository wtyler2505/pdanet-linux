# PdaNet Linux - Changelog

All notable changes to this project will be documented in this file.

## [2.1.0] - 2025-10-13

### Added
- **Desktop Notifications**: Real-time notifications for connection state changes
  - Connected/Disconnected notifications (low urgency)
  - Error notifications (critical urgency)
  - Configurable via settings (can be disabled)
  
- **Connection History Tracking**: Automatic session history logging
  - Tracks timestamp, duration, downloaded/uploaded bytes, interface, and average latency
  - Stores last 100 sessions in `~/.config/pdanet-linux/connection_history.json`
  - Automatically saved when connection is terminated
  
- **Configurable Update Interval**: GUI update frequency is now configurable
  - Default: 1000ms (1 second)
  - Range: 500-5000ms
  - Reduces CPU usage for users who don't need real-time updates
  - Configurable in settings dialog

### Improved
- Code quality improvements
  - Fixed unused variable in network scanner
  - Enhanced error handling for notifications
  - Better fallback handling when Notify library is unavailable
  
- Performance optimizations
  - Reduced memory overhead for log buffers
  - Optimized GUI update cycles

### Fixed
- Minor linting issues (unused variable in SSID combo)
- Import handling for optional dependencies (Notify)

### Security
- All security audits passed
- Input validation maintained for all user inputs
- Subprocess calls remain properly sanitized

### Testing
- All 105 unit tests passing
- No regressions introduced
- Security audit: 0 critical, 0 high issues
- Code coverage maintained

---

## [2.0.0] - 2025-10-04

### Initial Release
- USB tethering support
- WiFi tethering with 6-layer carrier bypass
- iPhone Personal Hotspot support
- Professional cyberpunk GUI
- Auto-reconnect functionality
- Bandwidth monitoring
- Connection quality metrics
- System tray integration
- Configuration profiles
- Comprehensive test suite (105 tests)
- Full documentation

---

## Features Summary (Current Version)

### Core Features
✅ USB Tethering  
✅ WiFi Hotspot Tethering (Primary Mode)  
✅ iPhone Personal Hotspot Support  
✅ 6-Layer Aggressive Carrier Bypass  
✅ Professional Cyberpunk GUI  
✅ Desktop Notifications (NEW)  
✅ Connection History Tracking (NEW)  
✅ Configurable Update Intervals (NEW)  

### Advanced Features
✅ Auto-reconnect with exponential backoff  
✅ Real-time bandwidth monitoring  
✅ Connection quality metrics (latency, packet loss)  
✅ System tray integration  
✅ Configuration profiles  
✅ Saved WiFi networks with encrypted passwords  
✅ Network scanning  
✅ Speed testing  

### Quality Assurance
✅ 105 unit tests (100% passing)  
✅ Security audits (bandit)  
✅ Code quality checks (flake8, mypy)  
✅ Dependency vulnerability scanning (pip-audit)  
✅ Visual regression testing  

---

## Upgrade Instructions

### From 2.0.0 to 2.1.0

No breaking changes. Simply pull latest code and restart application:

```bash
cd ~/pdanet-linux
git pull
sudo systemctl restart pdanet-linux  # if running as service
# OR
pkill -f pdanet_gui_v2.py  # kill GUI
pdanet-gui-v2  # restart GUI
```

### New Configuration Options

Add to `~/.config/pdanet-linux/config.json` (optional):

```json
{
  "show_notifications": true,
  "update_interval_ms": 1000
}
```

---

## Known Issues

### Minor Issues
- GTK3 must be installed via system packages (cannot use pip)
- Notify library (libnotify) required for desktop notifications
- Some carriers may still detect tethering despite 6-layer bypass

### Planned Improvements (v2.2.0)
- Connection history viewer in GUI
- Data usage alerts
- Bandwidth limiting GUI controls
- Multi-language support
- Theme variants (light/dark while keeping cyberpunk aesthetic)
- VPN detection and recommendations

---

## Contributing

See [AGENTS.md](AGENTS.md) for contributor guidelines.

---

## Support

- **Issues**: GitHub Issues
- **Documentation**: README.md, docs/
- **Testing**: Run `pytest tests/` for full test suite

---

**Version 2.1.0 Release Date**: October 13, 2025  
**Tested On**: Linux Mint 22.2, Ubuntu 24.04  
**License**: MIT
