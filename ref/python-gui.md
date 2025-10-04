# Python GUI Implementation - Technical Reference

**Last Updated:** 2025-10-03
**Framework:** GTK3 (PyGObject)
**Design Pattern:** Model-View-Controller with Observer pattern

## Overview

The PdaNet Linux GUI is a professional cyberpunk-themed GTK3 application written in Python 3. It provides real-time connection management, bandwidth monitoring, and system tray integration with a data-dense, terminal-style interface.

## Module Architecture

```
src/
├── pdanet_gui_v2.py       # Main application (MVC controller)
├── theme.py               # Cyberpunk CSS theme generation
├── logger.py              # Rotating file logger with GUI buffer
├── config_manager.py      # Settings persistence and profiles
├── stats_collector.py     # Bandwidth tracking and ping testing
└── connection_manager.py  # Connection state machine
```

## Core Modules

### 1. theme.py - Visual Design System

**Purpose:** Centralized color palette and GTK CSS generation

**Colors Class:**
```python
class Colors:
    # Base palette
    BLACK = "#000000"           # Pure black background
    TEXT_WHITE = "#E0E0E0"      # Primary text
    BORDER_GRAY = "#333333"     # Panel borders

    # Status accents
    GREEN = "#00FF00"           # Connected, success
    RED = "#FF0000"             # Disconnected, error
    ORANGE = "#FFA500"          # Warning, in-progress
```

**Design Constraints:**
- **NO gradients** - Flat colors only
- **NO emoji** - Professional text only
- **Monospaced fonts** - JetBrains Mono, Fira Code, Courier New
- **Pure black (#000000)** - Not dark gray
- **High contrast** - Green/red on black for readability

**CSS Generation:**
```python
def get_css():
    return f"""
    * {{
        font-family: "JetBrains Mono", monospace;
        font-size: 11px;
    }}

    window {{
        background-color: {Colors.BLACK};
        color: {Colors.TEXT_WHITE};
    }}

    .status-connected {{
        color: {Colors.GREEN};
        font-weight: bold;
    }}
    """
```

**GTK CSS Limitations:**
- ❌ `text-transform` (not supported in GTK 3)
- ❌ `letter-spacing` (not supported in GTK 3)
- ✅ `font-weight`, `color`, `background-color`, `border`, `padding`, `margin`

**Formatting Utilities:**
```python
class Format:
    @staticmethod
    def header(text):
        return f"[{text.upper()}]"

    @staticmethod
    def data_rate(bytes_per_sec):
        if bytes_per_sec >= 1024 * 1024:
            return f"{bytes_per_sec / (1024 * 1024):.2f} MB/s"
        elif bytes_per_sec >= 1024:
            return f"{bytes_per_sec / 1024:.2f} KB/s"
        return f"{bytes_per_sec:.0f} B/s"
```

---

### 2. logger.py - Logging System

**Purpose:** Dual-output logging (file + GUI buffer)

**Architecture:**
```
Log Event → Logger
              ├──> Rotating File Handler (~/.config/pdanet-linux/app.log)
              └──> GUI Buffer (deque, max 1000 entries)
```

**Configuration:**
```python
class LoggerConfig:
    LOG_DIR = Path.home() / ".config" / "pdanet-linux"
    LOG_FILE = LOG_DIR / "app.log"
    MAX_BYTES = 10 * 1024 * 1024  # 10MB
    BACKUP_COUNT = 5
    GUI_BUFFER_SIZE = 1000
```

**Singleton Pattern:**
```python
_logger = None

def get_logger():
    global _logger
    if _logger is None:
        _logger = Logger()
    return _logger
```

**Log Levels:**
```python
logger.ok("Connection established")      # Green, success
logger.info("Detecting interface...")    # Gray, informational
logger.warning("Proxy slow to respond")  # Orange, warning
logger.error("Connection failed")        # Red, error
```

**GUI Integration:**
```python
# GUI reads from buffer for display
logs = logger.get_gui_logs()  # Returns list of (timestamp, level, message)
```

---

### 3. config_manager.py - Settings Persistence

**Purpose:** Save/load user settings and connection profiles

**Storage Location:** `~/.config/pdanet-linux/settings.json`

**Configuration Schema:**
```json
{
  "auto_connect": false,
  "auto_reconnect": true,
  "reconnect_attempts": 3,
  "connection_mode": "wifi",
  "stealth_level": 3,
  "wifi_ssid": "AndroidAP",
  "usb_interface": "usb0",
  "show_notifications": true,
  "start_minimized": false,
  "theme": "cyberpunk"
}
```

**API:**
```python
config = get_config()

# Read settings
auto_connect = config.get("auto_connect", False)

# Write settings
config.set("stealth_level", 3)
config.save()

# Auto-start management
config.enable_auto_start()   # Creates .desktop file in autostart
config.disable_auto_start()
```

**Desktop Integration:**
- Creates `.desktop` file for autostart
- Manages system tray integration
- Persists window size/position

---

### 4. stats_collector.py - Bandwidth Monitoring

**Purpose:** Real-time network statistics collection

**Data Sources:**
```bash
/sys/class/net/{interface}/statistics/
├── rx_bytes       # Total received bytes
├── tx_bytes       # Total transmitted bytes
├── rx_packets     # Total received packets
└── tx_packets     # Total transmitted packets
```

**Architecture:**
```python
class StatsCollector:
    def __init__(self):
        self.interface = None
        self.last_rx_bytes = 0
        self.last_tx_bytes = 0
        self.last_sample_time = time.time()

        # Rolling window for rate calculation
        self.rx_samples = deque(maxlen=10)  # 10-second window
        self.tx_samples = deque(maxlen=10)
```

**Rate Calculation:**
```python
def get_current_rates(self):
    """Returns (download_rate, upload_rate) in bytes/sec"""
    current_rx = self._read_bytes("rx_bytes")
    current_tx = self._read_bytes("tx_bytes")
    current_time = time.time()

    time_delta = current_time - self.last_sample_time
    rx_rate = (current_rx - self.last_rx_bytes) / time_delta
    tx_rate = (current_tx - self.last_tx_bytes) / time_delta

    self.last_rx_bytes = current_rx
    self.last_tx_bytes = current_tx
    self.last_sample_time = current_time

    return (rx_rate, tx_rate)
```

**Ping Testing:**
```python
def ping_test(self, host="8.8.8.8"):
    """Returns latency in milliseconds or None if failed"""
    result = subprocess.run(
        ["ping", "-c", "1", "-W", "2", host],
        capture_output=True
    )
    if result.returncode == 0:
        # Parse: time=42.3 ms
        match = re.search(r'time=([\d.]+)', result.stdout.decode())
        if match:
            return float(match.group(1))
    return None
```

**Update Frequency:** 1 second (configurable)

---

### 5. connection_manager.py - State Machine

**Purpose:** Connection orchestration and state management

**State Enum:**
```python
class ConnectionState(Enum):
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    DISCONNECTING = "disconnecting"
    ERROR = "error"
```

**State Diagram:**
```
      ┌──────────────┐
      │ DISCONNECTED │
      └──────┬───────┘
             │ connect()
             ▼
      ┌──────────────┐
      │  CONNECTING  │───────────┐
      └──────┬───────┘           │
             │                   │ validate_fail()
        validate_ok()            │
             │                   ▼
             ▼              ┌─────────┐
      ┌──────────────┐     │  ERROR  │
      │  CONNECTED   │     └────┬────┘
      └──────┬───────┘          │
             │                  │ auto_reconnect()
      disconnect()              │
             │                  │
             ▼                  │
      ┌──────────────┐          │
      │DISCONNECTING │          │
      └──────┬───────┘          │
             │                  │
             └──────────────────┘
```

**Observer Pattern (Callbacks):**
```python
manager = get_connection_manager()

# Register callbacks
manager.register_state_change_callback(on_state_changed)
manager.register_error_callback(on_error)

# Callbacks are invoked automatically
def on_state_changed(new_state):
    if new_state == ConnectionState.CONNECTED:
        update_ui_connected()
```

**Connection Flow (USB):**
```python
def connect_usb(self):
    self._set_state(ConnectionState.CONNECTING)

    # 1. Detect interface
    interface = self.detect_interface()
    if not interface:
        self._set_state(ConnectionState.ERROR)
        return False

    # 2. Validate proxy
    if not self.validate_proxy():
        self._set_state(ConnectionState.ERROR)
        return False

    # 3. Start services
    subprocess.run(["sudo", "pdanet-connect"])

    # 4. Mark connected
    self._set_state(ConnectionState.CONNECTED)

    # 5. Start monitoring
    self._start_health_monitor()

    return True
```

**Auto-Reconnect:**
```python
def _start_auto_reconnect(self):
    if self.reconnect_attempts >= self.max_reconnect_attempts:
        return

    self.reconnect_attempts += 1
    delay = self.reconnect_delay * (2 ** self.reconnect_attempts)  # Exponential backoff

    time.sleep(delay)
    self.connect()
```

**Health Monitoring:**
```python
def _health_monitor_loop(self):
    """Background thread that checks connection health"""
    while self.monitoring_active:
        if self.state == ConnectionState.CONNECTED:
            if not self.validate_proxy():
                self.logger.error("Connection lost")
                self._set_state(ConnectionState.ERROR)
                self._start_auto_reconnect()

        time.sleep(5)  # Check every 5 seconds
```

---

### 6. pdanet_gui_v2.py - Main Application

**Purpose:** GTK3 GUI with 4-panel dashboard layout

**Class Hierarchy:**
```
GtkApplication
    └── PdaNetGUI (Gtk.Window)
        ├── HeaderBar
        ├── StatusPanel
        ├── ControlPanel
        ├── StatsPanel
        └── LogPanel
```

**Single Instance Enforcement:**
```python
class SingleInstance:
    def __init__(self, lockfile='/tmp/pdanet-linux-gui.lock'):
        self.lockfile = lockfile
        self.fp = None

    def acquire(self):
        try:
            self.fp = open(self.lockfile, 'w')
            fcntl.lockf(self.fp, fcntl.LOCK_EX | fcntl.LOCK_NB)
            return True
        except IOError:
            return False
```

**System Tray Integration:**
```python
# Using AppIndicator3
self.indicator = AppIndicator3.Indicator.new(
    "pdanet-linux",
    "network-wired",
    AppIndicator3.IndicatorCategory.APPLICATION_STATUS
)
self.indicator.set_status(AppIndicator3.IndicatorStatus.ACTIVE)
```

**Real-Time Updates:**
```python
def start_update_loop(self):
    """Called every 1 second via GLib.timeout_add"""
    # Update stats
    rx_rate, tx_rate = self.stats.get_current_rates()
    self.stats_label.set_text(f"↓ {Format.data_rate(rx_rate)}")

    # Update ping
    latency = self.stats.ping_test()
    self.ping_label.set_text(f"Ping: {latency}ms" if latency else "N/A")

    # Update logs
    logs = self.logger.get_gui_logs()
    self.log_buffer.clear()
    for timestamp, level, message in logs:
        self.log_buffer.insert(f"[{timestamp}] {message}\n")

    return True  # Continue loop
```

**4-Panel Layout:**
```
┌───────────────────────────────────────┐
│          STATUS PANEL                 │
│  State: CONNECTED | Mode: WiFi        │
│  Interface: wlan0 | Stealth: Level 3  │
└───────────────────────────────────────┘
┌───────────────────────────────────────┐
│         CONTROL PANEL                 │
│  [CONNECT]  [DISCONNECT]  [STEALTH]   │
└───────────────────────────────────────┘
┌───────────────────────────────────────┐
│          STATS PANEL                  │
│  ↓ 2.5 MB/s  ↑ 512 KB/s  Ping: 42ms   │
│  Total: 1.2 GB | Session: 45 min      │
└───────────────────────────────────────┘
┌───────────────────────────────────────┐
│           LOG PANEL                   │
│  [12:34:56] Connection established    │
│  [12:35:12] Stealth enabled (Level 3) │
│  [12:35:45] Bandwidth: 2.5 MB/s       │
└───────────────────────────────────────┘
```

---

## Threading Model

**Main Thread (GTK):**
- UI updates
- Event handling
- User interactions

**Background Threads:**
- Health monitoring (ConnectionManager)
- Stats collection (StatsCollector)
- Auto-reconnect (ConnectionManager)

**Thread Safety:**
- Use `GLib.idle_add()` to update UI from background threads
- Never call GTK methods directly from non-main threads
- Use threading.Lock() for shared state

**Example:**
```python
def background_task():
    result = long_running_operation()

    # Update UI safely
    GLib.idle_add(update_ui, result)

def update_ui(result):
    label.set_text(result)
    return False  # Don't repeat
```

---

## Error Handling

**Connection Errors:**
```python
try:
    self.connection_manager.connect()
except InterfaceNotFoundError:
    self.show_error_dialog("No USB tethering interface found")
except ProxyUnreachableError:
    self.show_error_dialog("Cannot reach PdaNet proxy at 192.168.49.1:8000")
except PermissionError:
    self.show_error_dialog("Root permission required")
```

**Graceful Degradation:**
- GUI continues running even if connection fails
- Stats collector handles missing interface gracefully
- Logger always works (even if file write fails)

---

## Performance Optimization

**Update Frequency:**
- Stats collection: 1 second
- Health monitoring: 5 seconds
- Log GUI refresh: 1 second
- Ping test: 10 seconds

**Memory Management:**
- Log buffer: Limited to 1000 entries (deque)
- Stats samples: Rolling 10-second window
- Connection tracking: Cleanup old state on disconnect

**CPU Usage:**
- Idle: <1%
- Active monitoring: 2-3%
- During connection: 5-10%

---

## Testing and Debugging

**Run GUI in debug mode:**
```bash
python3 src/pdanet_gui_v2.py --debug
```

**Check logs:**
```bash
tail -f ~/.config/pdanet-linux/app.log
```

**GTK Inspector:**
```bash
GTK_DEBUG=interactive python3 src/pdanet_gui_v2.py
```

**Test without root:**
```bash
# Some features require sudo, but GUI launches without it
python3 src/pdanet_gui_v2.py
```

---

## Future Enhancements

1. **Bandwidth Graphs** - Real-time charts using matplotlib
2. **Connection Profiles** - Save/load different configurations
3. **VPN Integration** - Built-in OpenVPN/WireGuard client
4. **Traffic Analysis** - Show top applications by bandwidth
5. **Dark/Light Themes** - User-selectable color schemes (keeping cyberpunk default)

---

## References

- [System Architecture](architecture.md)
- [Connection Manager Flow](architecture.md#connection-management-layer)
- [GTK3 Documentation](https://docs.gtk.org/gtk3/)
- [PyGObject Reference](https://pygobject.readthedocs.io/)
