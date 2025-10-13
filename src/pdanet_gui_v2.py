#!/usr/bin/env python3
"""
PdaNet Linux - Professional GUI v2
Cyberpunk-themed interface with full feature set
"""

import os
import sys

# Ensure system GTK bindings are used instead of the test stub in src/gi
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_removed_src = False
if sys.path and sys.path[0] == _SCRIPT_DIR:
    sys.path.pop(0)
    _removed_src = True

try:
    import gi  # type: ignore
except Exception:
    # Fallback to local stub (used in tests without GTK)
    if _removed_src:
        sys.path.insert(0, _SCRIPT_DIR)
    import gi  # type: ignore

gi.require_version("Gtk", "3.0")
from gi.repository import Gdk, GLib, Gtk

# Try to import AppIndicator3, but make it optional
try:
    gi.require_version("AppIndicator3", "0.1")
    from gi.repository import AppIndicator3

    HAS_APPINDICATOR = True
except (ValueError, ImportError):
    HAS_APPINDICATOR = False
    AppIndicator3 = None

# Try to import Notify for desktop notifications
try:
    gi.require_version("Notify", "0.7")
    from gi.repository import Notify

    HAS_NOTIFY = True
except (ValueError, ImportError):
    HAS_NOTIFY = False
    Notify = None

import fcntl
import json
import subprocess
from datetime import datetime

# Add src directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config_manager import CONFIG_DIR, get_config
from connection_manager import ConnectionState, get_connection_manager
from logger import get_logger
from stats_collector import get_stats
from theme import Colors, Format, get_css


class SingleInstance:
    """Ensure only one instance of GUI runs"""

    def __init__(self, lockfile="/tmp/pdanet-linux-gui.lock"):
        self.lockfile = lockfile
        self.fp = None

    def acquire(self):
        """Acquire lock"""
        try:
            self.fp = open(self.lockfile, "w")
            fcntl.lockf(self.fp, fcntl.LOCK_EX | fcntl.LOCK_NB)
            return True
        except OSError:
            return False

    def release(self):
        """Release lock"""
        if not self.fp:
            return
        try:
            if not self.fp.closed:
                try:
                    fcntl.lockf(self.fp, fcntl.LOCK_UN)
                except (OSError, ValueError):
                    pass
            self.fp.close()
        except Exception:
            pass
        finally:
            try:
                if os.path.exists(self.lockfile):
                    os.unlink(self.lockfile)
            except OSError:
                pass
            self.fp = None


class PdaNetGUI(Gtk.Window):
    def __init__(self, start_minimized=False):
        super().__init__(title="PDANET LINUX")

        # Initialize components
        self.logger = get_logger()
        self.config = get_config()
        self.stats = get_stats()
        self.connection = get_connection_manager()

        # Window setup
        width = self.config.get("window_width", 900)
        height = self.config.get("window_height", 600)
        self.set_default_size(width, height)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_resizable(True)
        self.set_decorated(True)

        # Set minimum window size to allow proper resizing
        geometry = Gdk.Geometry()
        geometry.min_width = 700
        geometry.min_height = 400

        self.set_geometry_hints(None, geometry, Gdk.WindowHints.MIN_SIZE)

        # Apply theme
        self.load_theme()

        # Build UI
        self.build_ui()

        # Setup system tray
        self.setup_indicator()

        # Initialize desktop notifications
        self.setup_notifications()

        # Register callbacks
        self.connection.register_state_change_callback(self.on_connection_state_changed)
        self.connection.register_error_callback(self.on_connection_error)

        # Test-mode state override (for deterministic visual tests)
        self._test_state_file = None
        if "--test-mode" in sys.argv:
            self._test_state_file = os.environ.get("PDANET_TEST_STATE_FILE")

        # Start update loop with configurable interval
        update_interval = self.config.get("update_interval_ms", 1000)
        GLib.timeout_add(update_interval, self.update_display)

        # Setup keyboard shortcuts
        self.setup_keyboard_shortcuts()

        # Initialize data usage warning tracking
        self.last_warning_time = 0
        self.warning_thresholds_hit = set()

        # Load settings
        self.load_settings()

        # Start minimized if requested
        if start_minimized:
            self.hide()
            self.logger.info("Started minimized to system tray")
        else:
            self.logger.info("GUI initialized")

    def setup_keyboard_shortcuts(self):
        """Setup keyboard shortcuts for common actions"""
        accel_group = Gtk.AccelGroup()
        self.add_accel_group(accel_group)
        
        # Ctrl+C: Connect
        key, mod = Gtk.accelerator_parse("<Control>C")
        accel_group.connect(key, mod, Gtk.AccelFlags.VISIBLE, 
                          lambda *args: self.on_connect_clicked(None))
        
        # Ctrl+D: Disconnect
        key, mod = Gtk.accelerator_parse("<Control>D")
        accel_group.connect(key, mod, Gtk.AccelFlags.VISIBLE,
                          lambda *args: self.on_disconnect_clicked(None))
        
        # Ctrl+H: History
        key, mod = Gtk.accelerator_parse("<Control>H")
        accel_group.connect(key, mod, Gtk.AccelFlags.VISIBLE,
                          lambda *args: self.on_history_clicked(None))
        
        # Ctrl+S: Settings
        key, mod = Gtk.accelerator_parse("<Control>S")
        accel_group.connect(key, mod, Gtk.AccelFlags.VISIBLE,
                          lambda *args: self.on_settings_clicked(None))
        
        # Ctrl+T: Speed Test
        key, mod = Gtk.accelerator_parse("<Control>T")
        accel_group.connect(key, mod, Gtk.AccelFlags.VISIBLE,
                          lambda *args: self.on_speedtest_clicked(None))
        
        # Ctrl+Q: Quit
        key, mod = Gtk.accelerator_parse("<Control>Q")
        accel_group.connect(key, mod, Gtk.AccelFlags.VISIBLE,
                          lambda *args: self.on_quit(None))
        
        # F5: Refresh/Update display
        key, mod = Gtk.accelerator_parse("F5")
        accel_group.connect(key, mod, Gtk.AccelFlags.VISIBLE,
                          lambda *args: self.update_display())
        
        self.logger.info("Keyboard shortcuts enabled: Ctrl+C/D/H/S/T/Q, F5")

    def setup_notifications(self):
        """Initialize desktop notifications"""
        if HAS_NOTIFY:
            try:
                Notify.init("PDANET LINUX")
                self.notifications_enabled = True
                self.logger.info("Desktop notifications enabled")
            except Exception as e:
                self.notifications_enabled = False
                self.logger.warning(f"Failed to initialize notifications: {e}")
        else:
            self.notifications_enabled = False
            self.logger.info("Notify library not available - notifications disabled")

    def show_notification(self, title, message, urgency="normal"):
        """
        Show desktop notification
        
        Args:
            title: Notification title
            message: Notification message
            urgency: "low", "normal", or "critical"
        """
        if not self.notifications_enabled or not self.config.get("show_notifications", True):
            return
        
        try:
            urgency_map = {
                "low": Notify.Urgency.LOW,
                "normal": Notify.Urgency.NORMAL,
                "critical": Notify.Urgency.CRITICAL
            }
            
            notification = Notify.Notification.new(title, message, "network-wireless")
            notification.set_urgency(urgency_map.get(urgency, Notify.Urgency.NORMAL))
            notification.show()
        except Exception as e:
            self.logger.warning(f"Failed to show notification: {e}")

    def load_theme(self):
        """Load cyberpunk theme"""
        css_provider = Gtk.CssProvider()
        css_provider.load_from_data(get_css().encode())
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(), css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

    def build_ui(self):
        """Build main interface"""
        main_vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.add(main_vbox)

        # Header
        header = self.build_header()
        main_vbox.pack_start(header, False, False, 0)

        # Main content (wrapped in ScrolledWindow so small screens don't clip)
        content = self.build_content()
        scroller = Gtk.ScrolledWindow()
        scroller.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scroller.add(content)
        main_vbox.pack_start(scroller, True, True, 0)

        # Status bar
        statusbar = self.build_statusbar()
        main_vbox.pack_start(statusbar, False, False, 0)

    def build_header(self):
        """Build header bar"""
        header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        header.get_style_context().add_class("titlebar")

        # Left: Title with corner bracket
        title_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        corner_l = Gtk.Label(label="◈")
        corner_l.get_style_context().add_class("corner-bracket")
        title = Gtk.Label(label="  PDANET LINUX")
        title.set_markup("<b>  PDANET LINUX</b>")

        title_box.pack_start(corner_l, False, False, 5)
        title_box.pack_start(title, False, False, 0)

        # Right: Status indicators + window controls
        status_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)

        self.header_status_label = Gtk.Label(label="[DISCONNECTED]")
        self.header_time_label = Gtk.Label(label="")
        self.update_header_time()

        # Window control buttons (ensure usability even if WM hides them)
        btn_min = Gtk.Button(label="_")
        btn_min.set_relief(Gtk.ReliefStyle.NONE)
        btn_min.set_tooltip_text("Minimize")
        btn_min.connect("clicked", lambda b: self.iconify())

        btn_max = Gtk.Button(label="□")
        btn_max.set_relief(Gtk.ReliefStyle.NONE)
        btn_max.set_tooltip_text("Maximize/Restore")
        btn_max.connect("clicked", self.on_toggle_maximize)

        btn_close = Gtk.Button(label="✕")
        btn_close.set_relief(Gtk.ReliefStyle.NONE)
        btn_close.set_tooltip_text("Close")
        btn_close.connect("clicked", self.on_quit)

        status_box.pack_end(btn_close, False, False, 0)
        status_box.pack_end(btn_max, False, False, 0)
        status_box.pack_end(btn_min, False, False, 0)
        status_box.pack_end(self.header_time_label, False, False, 8)
        status_box.pack_end(self.header_status_label, False, False, 6)

        header.pack_start(title_box, False, False, 0)
        header.pack_end(status_box, False, False, 0)

        return header

    def build_content(self):
        """Build main content grid"""
        grid = Gtk.Grid()
        grid.set_hexpand(True)
        grid.set_vexpand(True)
        # Responsive: columns share width, rows size to content
        grid.set_column_homogeneous(True)
        grid.set_row_homogeneous(False)
        grid.set_column_spacing(2)
        grid.set_row_spacing(2)
        grid.set_margin_top(2)
        grid.set_margin_bottom(2)
        grid.set_margin_start(2)
        grid.set_margin_end(2)

        # Top left: Status panel
        status_panel = self.build_status_panel()
        status_panel.set_hexpand(True)
        status_panel.set_vexpand(False)
        grid.attach(status_panel, 0, 0, 1, 1)

        # Top right: Metrics panel
        metrics_panel = self.build_metrics_panel()
        metrics_panel.set_hexpand(True)
        metrics_panel.set_vexpand(False)
        grid.attach(metrics_panel, 1, 0, 1, 1)

        # Bottom left: Log panel
        log_panel = self.build_log_panel()
        log_panel.set_hexpand(True)
        log_panel.set_vexpand(True)
        grid.attach(log_panel, 0, 1, 1, 1)

        # Bottom right: Controls panel
        controls_panel = self.build_controls_panel()
        controls_panel.set_hexpand(True)
        controls_panel.set_vexpand(True)
        grid.attach(controls_panel, 1, 1, 1, 1)

        return grid

    def on_toggle_maximize(self, *_args):
        try:
            if self.is_maximized():
                self.unmaximize()
            else:
                self.maximize()
        except Exception:
            pass

    def build_status_panel(self):
        """Build connection status panel"""
        panel = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)  # Compact
        panel.get_style_context().add_class("panel")

        # Header
        header = Gtk.Label(label="CONNECTION STATUS")
        header.get_style_context().add_class("panel-header")
        header.set_xalign(0)
        panel.pack_start(header, False, False, 0)

        # Status items
        self.status_state_label = self.create_metric_row("STATUS", "● INACTIVE")
        self.status_interface_label = self.create_metric_row("INTERFACE", "NOT DETECTED")
        self.status_endpoint_label = self.create_metric_row("ENDPOINT", "192.168.49.1:8000")
        self.status_uptime_label = self.create_metric_row("UPTIME", "00:00:00")
        self.status_stealth_label = self.create_metric_row("STEALTH", "DISABLED")

        panel.pack_start(self.status_state_label, False, False, 3)
        panel.pack_start(self.status_interface_label, False, False, 3)
        panel.pack_start(self.status_endpoint_label, False, False, 3)
        panel.pack_start(self.status_uptime_label, False, False, 3)
        panel.pack_start(self.status_stealth_label, False, False, 3)

        # Quality bar with status indicator
        quality_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        
        quality_header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        quality_label = Gtk.Label(label="CONNECTION QUALITY")
        quality_label.get_style_context().add_class("metric-label")
        quality_label.set_xalign(0)
        
        self.quality_status_label = Gtk.Label(label="● UNKNOWN")
        self.quality_status_label.set_xalign(1)
        
        quality_header.pack_start(quality_label, True, True, 0)
        quality_header.pack_start(self.quality_status_label, False, False, 0)

        self.quality_progress = Gtk.ProgressBar()
        self.quality_progress.set_fraction(0.0)
        self.quality_progress.set_text("Not Connected")
        self.quality_progress.set_show_text(True)

        quality_box.pack_start(quality_header, False, False, 0)
        quality_box.pack_start(self.quality_progress, False, False, 0)
        panel.pack_start(quality_box, False, False, 5)

        return panel

    def build_metrics_panel(self):
        """Build network metrics panel"""
        panel = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)  # Compact
        panel.get_style_context().add_class("panel")

        # Header
        header = Gtk.Label(label="NETWORK METRICS")
        header.get_style_context().add_class("panel-header")
        header.set_xalign(0)
        panel.pack_start(header, False, False, 0)

        # Metrics
        self.metric_download_label = self.create_metric_row("↓ DOWN", "0.0 KB/s")
        self.metric_upload_label = self.create_metric_row("↑ UP", "0.0 KB/s")
        self.metric_latency_label = self.create_metric_row("LATENCY", "-- ms")
        self.metric_loss_label = self.create_metric_row("LOSS", "-- %")
        self.metric_total_label = self.create_metric_row("TOTAL", "↓ 0B  ↑ 0B")

        panel.pack_start(self.metric_download_label, False, False, 3)
        panel.pack_start(self.metric_upload_label, False, False, 3)
        panel.pack_start(self.metric_latency_label, False, False, 3)
        panel.pack_start(self.metric_loss_label, False, False, 3)
        panel.pack_start(self.metric_total_label, False, False, 3)

        # Simple bandwidth graph placeholder (compact)
        graph_label = Gtk.Label(label="BANDWIDTH GRAPH")
        graph_label.get_style_context().add_class("metric-label")
        graph_label.set_xalign(0)
        panel.pack_start(graph_label, False, False, 5)

        self.graph_textview = Gtk.TextView()
        self.graph_textview.set_editable(False)
        self.graph_textview.set_cursor_visible(False)
        # Natural height; avoid fixed sizing so panels can autosize
        # self.graph_textview.set_size_request(-1, 60)
        self.graph_textview.set_monospace(True)
        self.graph_buffer = self.graph_textview.get_buffer()

        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.NEVER)  # No scrollbars for graph
        scroll.add(self.graph_textview)
        panel.pack_start(scroll, False, False, 0)  # Don't expand

        return panel

    def build_log_panel(self):
        """Build enhanced system log panel with filtering and controls"""
        panel = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=1)  # Compact spacing
        panel.get_style_context().add_class("panel")

        # Header with controls
        header_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)

        header = Gtk.Label(label="SYSTEM LOG")
        header.get_style_context().add_class("panel-header")
        header.set_xalign(0)
        header_box.pack_start(header, True, True, 0)

        # Log level filters
        self.log_filters = {"DEBUG": False, "INFO": True, "OK": True, "WARN": True, "ERROR": True}

        filter_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=3)
        for level in ["DEBUG", "INFO", "OK", "WARN", "ERROR"]:
            btn = Gtk.ToggleButton(label=level[:1])  # Single letter
            btn.set_active(self.log_filters[level])
            btn.set_tooltip_text(f"Show {level} logs")
            btn.connect("toggled", self.on_log_filter_toggled, level)
            filter_box.pack_start(btn, False, False, 0)

        header_box.pack_start(filter_box, False, False, 5)
        panel.pack_start(header_box, False, False, 0)

        # Search bar
        search_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        self.log_search_entry = Gtk.Entry()
        self.log_search_entry.set_placeholder_text("Search logs...")
        self.log_search_entry.connect("changed", self.on_log_search_changed)
        search_box.pack_start(self.log_search_entry, True, True, 0)

        clear_search_btn = Gtk.Button(label="×")
        clear_search_btn.set_tooltip_text("Clear search")
        clear_search_btn.connect("clicked", lambda b: self.log_search_entry.set_text(""))
        search_box.pack_start(clear_search_btn, False, False, 0)

        panel.pack_start(search_box, False, False, 0)

        # Log viewer with line numbers
        log_view_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)

        # Line numbers TextView
        self.log_line_numbers = Gtk.TextView()
        self.log_line_numbers.set_editable(False)
        self.log_line_numbers.set_cursor_visible(False)
        self.log_line_numbers.set_size_request(40, -1)
        self.log_line_numbers.set_monospace(True)
        self.log_line_numbers_buffer = self.log_line_numbers.get_buffer()
        self.log_line_numbers_buffer.create_tag("line_num", foreground=Colors.TEXT_GRAY)

        # Main log TextView
        self.log_textview = Gtk.TextView()
        self.log_textview.set_editable(False)
        self.log_textview.set_cursor_visible(False)
        # Allow the log viewer to grow with the window
        # self.log_textview.set_size_request(-1, 60)
        self.log_textview.set_vexpand(True)
        self.log_textview.set_monospace(True)
        self.log_textview.set_wrap_mode(Gtk.WrapMode.NONE)
        self.log_buffer = self.log_textview.get_buffer()

        # Create tags for different log levels with symbols
        self.log_buffer.create_tag("debug", foreground=Colors.TEXT_GRAY)
        self.log_buffer.create_tag("info", foreground=Colors.TEXT_GRAY)
        self.log_buffer.create_tag("ok", foreground=Colors.GREEN_DIM)
        self.log_buffer.create_tag("warn", foreground=Colors.ORANGE)
        self.log_buffer.create_tag("error", foreground=Colors.RED_DIM)
        self.log_buffer.create_tag("timestamp", foreground=Colors.TEXT_GRAY)

        # Synchronized scrolling
        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scroll.set_hexpand(True)
        scroll.set_vexpand(True)

        scroll_lines = Gtk.ScrolledWindow()
        scroll_lines.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scroll_lines.set_hexpand(False)
        scroll_lines.set_vexpand(True)
        scroll_lines.add(self.log_line_numbers)

        # Sync scrolling
        vadj = scroll.get_vadjustment()
        scroll_lines.set_vadjustment(vadj)

        log_view_box.pack_start(scroll_lines, False, False, 0)
        scroll.add(self.log_textview)
        log_view_box.pack_start(scroll, True, True, 0)

        panel.pack_start(log_view_box, True, True, 0)

        # Control buttons
        btn_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=3)

        copy_btn = Gtk.Button(label="Copy")
        copy_btn.set_tooltip_text("Copy visible logs to clipboard")
        copy_btn.connect("clicked", self.on_copy_logs)
        btn_box.pack_start(copy_btn, True, True, 0)

        export_btn = Gtk.Button(label="Export")
        export_btn.set_tooltip_text("Export logs to file")
        export_btn.connect("clicked", self.on_export_logs)
        btn_box.pack_start(export_btn, True, True, 0)

        clear_btn = Gtk.Button(label="Clear")
        clear_btn.set_tooltip_text("Clear log buffer")
        clear_btn.connect("clicked", self.on_clear_logs)
        btn_box.pack_start(clear_btn, True, True, 0)

        panel.pack_start(btn_box, False, False, 0)

        # Store last log count for efficient updates
        self.last_log_count = 0

        return panel

    def build_controls_panel(self):
        """Build controls panel"""
        panel = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)  # Compact
        panel.get_style_context().add_class("panel")

        # Header
        header = Gtk.Label(label="OPERATIONS")
        header.get_style_context().add_class("panel-header")
        header.set_xalign(0)
        panel.pack_start(header, False, False, 0)

        # Mode selector
        mode_label = Gtk.Label(label="CONNECTION MODE")
        mode_label.get_style_context().add_class("metric-label")
        mode_label.set_xalign(0)
        panel.pack_start(mode_label, False, False, 2)

        self.mode_combo = Gtk.ComboBoxText()
        self.mode_combo.append("usb", "USB Tethering (Android)")
        self.mode_combo.append("wifi", "WiFi Hotspot (Android)")
        self.mode_combo.append("iphone", "iPhone Personal Hotspot")
        self.mode_combo.set_active(0)
        panel.pack_start(self.mode_combo, False, False, 0)

        # Connect/Disconnect buttons
        self.connect_button = Gtk.Button(label="▶ CONNECT")
        self.connect_button.get_style_context().add_class("button-connect")
        self.connect_button.connect("clicked", self.on_connect_clicked)
        panel.pack_start(self.connect_button, False, False, 2)

        self.disconnect_button = Gtk.Button(label="■ DISCONNECT")
        self.disconnect_button.get_style_context().add_class("button-disconnect")
        self.disconnect_button.connect("clicked", self.on_disconnect_clicked)
        self.disconnect_button.set_sensitive(False)
        panel.pack_start(self.disconnect_button, False, False, 2)

        # Separator
        sep = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        panel.pack_start(sep, False, False, 2)

        # Options
        options_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)

        # Stealth mode status (auto-enabled on WiFi/iPhone connections)
        stealth_status_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        stealth_label = Gtk.Label(label="STEALTH MODE")
        stealth_label.set_xalign(0)
        self.stealth_status = Gtk.Label(label="[AUTO]")
        self.stealth_status.get_style_context().add_class("metric-value")
        stealth_status_box.pack_start(stealth_label, True, True, 0)
        stealth_status_box.pack_start(self.stealth_status, False, False, 0)
        options_box.pack_start(stealth_status_box, False, False, 0)

        # Auto-reconnect
        reconnect_box = self.create_switch_row("AUTO-RECONNECT", self.on_auto_reconnect_toggled)
        self.reconnect_switch = reconnect_box.get_children()[1]
        options_box.pack_start(reconnect_box, False, False, 0)

        # Auto-start
        autostart_box = self.create_switch_row("START ON BOOT", self.on_autostart_toggled)
        self.autostart_switch = autostart_box.get_children()[1]
        options_box.pack_start(autostart_box, False, False, 0)

        panel.pack_start(options_box, False, False, 2)

        # History button
        history_button = Gtk.Button(label="📊 HISTORY")
        history_button.connect("clicked", self.on_history_clicked)
        panel.pack_end(history_button, False, False, 2)

        # Speed test button
        speedtest_button = Gtk.Button(label="⚡ SPEED TEST")
        speedtest_button.connect("clicked", self.on_speedtest_clicked)
        panel.pack_end(speedtest_button, False, False, 2)

        # Settings button
        settings_button = Gtk.Button(label="⚙ SETTINGS")
        settings_button.connect("clicked", self.on_settings_clicked)
        panel.pack_end(settings_button, False, False, 2)

        return panel

    def build_statusbar(self):
        """Build bottom status bar"""
        statusbar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        statusbar.get_style_context().add_class("statusbar")

        self.sb_status = Gtk.Label(label="SYS: INACTIVE")
        self.sb_network = Gtk.Label(label="NET: 0.0 MB/s")
        self.sb_stealth = Gtk.Label(label="STEALTH: OFF")
        self.sb_uptime = Gtk.Label(label="UPTIME: 00:00:00")

        statusbar.pack_start(self.sb_status, False, False, 5)
        statusbar.pack_start(Gtk.Separator(orientation=Gtk.Orientation.VERTICAL), False, False, 0)
        statusbar.pack_start(self.sb_network, False, False, 5)
        statusbar.pack_start(Gtk.Separator(orientation=Gtk.Orientation.VERTICAL), False, False, 0)
        statusbar.pack_start(self.sb_stealth, False, False, 5)
        statusbar.pack_start(Gtk.Separator(orientation=Gtk.Orientation.VERTICAL), False, False, 0)
        statusbar.pack_start(self.sb_uptime, False, False, 5)

        return statusbar

    def create_metric_row(self, label_text, value_text):
        """Create a metric label/value row"""
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)

        label = Gtk.Label(label=label_text)
        label.set_width_chars(12)
        label.set_xalign(0)
        label.get_style_context().add_class("metric-label")

        value = Gtk.Label(label=value_text)
        value.set_xalign(0)
        value.get_style_context().add_class("metric-value")

        box.pack_start(label, False, False, 0)
        box.pack_start(value, True, True, 0)

        return box

    def create_switch_row(self, label_text, callback):
        """Create a label/switch row"""
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)

        label = Gtk.Label(label=label_text)
        label.set_xalign(0)

        switch = Gtk.Switch()
        switch.connect("notify::active", callback)

        box.pack_start(label, True, True, 0)
        box.pack_start(switch, False, False, 0)

        return box

    def setup_indicator(self):
        """Setup system tray indicator"""
        if not HAS_APPINDICATOR:
            self.logger.warning("AppIndicator3 not available - system tray disabled")
            self.indicator = None
            return

        self.indicator = AppIndicator3.Indicator.new(
            "pdanet-linux",
            "network-wireless-disconnected",
            AppIndicator3.IndicatorCategory.APPLICATION_STATUS,
        )
        self.indicator.set_status(AppIndicator3.IndicatorStatus.ACTIVE)
        self.indicator.set_title("PDANET LINUX")

        # Menu
        menu = Gtk.Menu()

        show_item = Gtk.MenuItem(label="Show Window")
        show_item.connect("activate", lambda x: self.present())
        menu.append(show_item)

        menu.append(Gtk.SeparatorMenuItem())

        self.tray_connect_item = Gtk.MenuItem(label="Connect")
        self.tray_connect_item.connect("activate", lambda x: self.on_connect_clicked(None))
        menu.append(self.tray_connect_item)

        menu.append(Gtk.SeparatorMenuItem())

        quit_item = Gtk.MenuItem(label="Quit")
        quit_item.connect("activate", self.on_quit)
        menu.append(quit_item)

        menu.show_all()
        self.indicator.set_menu(menu)

    def update_header_time(self):
        """Update header timestamp"""
        now = datetime.now().strftime("%H:%M UTC")
        self.header_time_label.set_text(now)
        return True

    def update_display(self):
        """Update all display elements"""
        # Update time
        self.update_header_time()

        # Get current state (allow test override)
        state = self.connection.get_state()
        if self._test_state_file and os.path.exists(self._test_state_file):
            try:
                with open(self._test_state_file) as f:
                    data = json.load(f)
                override = data.get("connection_state")
                if override:
                    from connection_manager import ConnectionState

                    mapping = {
                        "DISCONNECTED": ConnectionState.DISCONNECTED,
                        "CONNECTING": ConnectionState.CONNECTING,
                        "CONNECTED": ConnectionState.CONNECTED,
                        "ERROR": ConnectionState.ERROR,
                    }
                    state = mapping.get(override.upper(), state)
            except Exception:
                pass
        is_connected = state == ConnectionState.CONNECTED

        # Update status panel
        if state == ConnectionState.CONNECTED:
            self.status_state_label.get_children()[1].set_markup(
                f"<span foreground='{Colors.GREEN}'>● ACTIVE</span>"
            )
            self.header_status_label.set_markup(
                f"<span foreground='{Colors.GREEN}'>[CONNECTED]</span>"
            )
        elif state == ConnectionState.CONNECTING:
            self.status_state_label.get_children()[1].set_markup(
                f"<span foreground='{Colors.ORANGE}'>◐ CONNECTING</span>"
            )
            self.header_status_label.set_markup(
                f"<span foreground='{Colors.ORANGE}'>[CONNECTING]</span>"
            )
        else:
            self.status_state_label.get_children()[1].set_markup(
                f"<span foreground='{Colors.RED}'>● INACTIVE</span>"
            )
            self.header_status_label.set_markup(
                f"<span foreground='{Colors.TEXT_GRAY}'>[DISCONNECTED]</span>"
            )

        # Update interface
        interface = self.connection.current_interface or "NOT DETECTED"
        self.status_interface_label.get_children()[1].set_text(interface)

        # Update uptime
        if is_connected:
            uptime = self.stats.get_uptime()
            self.status_uptime_label.get_children()[1].set_text(Format.format_uptime(uptime))
            self.sb_uptime.set_text(f"UPTIME: {Format.format_uptime(uptime)}")
        else:
            self.status_uptime_label.get_children()[1].set_text("00:00:00")
            self.sb_uptime.set_text("UPTIME: 00:00:00")

        # Update metrics
        if is_connected:
            dl_rate = self.stats.get_current_download_rate()
            ul_rate = self.stats.get_current_upload_rate()

            self.metric_download_label.get_children()[1].set_text(Format.format_bandwidth(dl_rate))
            self.metric_upload_label.get_children()[1].set_text(Format.format_bandwidth(ul_rate))

            total_dl = self.stats.get_total_downloaded()
            total_ul = self.stats.get_total_uploaded()
            self.metric_total_label.get_children()[1].set_text(
                f"↓ {Format.format_bytes(total_dl)}  ↑ {Format.format_bytes(total_ul)}"
            )

            # Check data usage warnings
            self.check_data_usage_warnings(total_dl, total_ul)

            # Network rate for statusbar
            self.sb_network.set_text(f"NET: {Format.format_bandwidth(dl_rate + ul_rate)}")
        else:
            self.metric_download_label.get_children()[1].set_text("0.0 KB/s")
            self.metric_upload_label.get_children()[1].set_text("0.0 KB/s")
            self.metric_total_label.get_children()[1].set_text("↓ 0B  ↑ 0B")
            self.sb_network.set_text("NET: 0.0 MB/s")

        # Update log
        self.update_log_display()

        # Statusbar
        state_text = "ACTIVE" if is_connected else "INACTIVE"
        self.sb_status.set_text(f"SYS: {state_text}")

        # Update network quality indicator
        if is_connected:
            self.update_network_quality()

        return True

    def update_network_quality(self):
        """Calculate and update network quality indicator with color coding"""
        # Get metrics
        latency = self.stats.get_average_latency()
        packet_loss = self.stats.get_packet_loss()
        uptime = self.stats.get_uptime()
        
        # Calculate quality score (0-100)
        quality_score = 100
        
        # Latency penalty
        if latency > 0:
            if latency < 50:
                latency_penalty = 0
            elif latency < 100:
                latency_penalty = 10
            elif latency < 200:
                latency_penalty = 25
            elif latency < 500:
                latency_penalty = 40
            else:
                latency_penalty = 60
            quality_score -= latency_penalty
        
        # Packet loss penalty
        if packet_loss > 0:
            quality_score -= min(packet_loss * 2, 40)
        
        # Connection stability bonus (longer uptime = bonus, capped at 10)
        if uptime > 300:  # 5 minutes
            stability_bonus = min(10, uptime // 300)
            quality_score = min(100, quality_score + stability_bonus)
        
        # Ensure score is in range
        quality_score = max(0, min(100, quality_score))
        
        # Update progress bar
        self.quality_progress.set_fraction(quality_score / 100.0)
        self.quality_progress.set_text(f"{int(quality_score)}%")
        
        # Color-coded status with emoji-free indicators
        if quality_score >= 90:
            status_text = "● EXCELLENT"
            status_color = Colors.GREEN
        elif quality_score >= 75:
            status_text = "● GOOD"
            status_color = Colors.GREEN_DIM
        elif quality_score >= 50:
            status_text = "● FAIR"
            status_color = Colors.ORANGE
        elif quality_score >= 25:
            status_text = "● POOR"
            status_color = "#FF6B00"  # Dark orange
        else:
            status_text = "● CRITICAL"
            status_color = Colors.RED
        
        self.quality_status_label.set_markup(f"<span foreground='{status_color}'>{status_text}</span>")
    def check_data_usage_warnings(self, downloaded, uploaded):
        """Check and alert for data usage thresholds"""
        # Only check if warnings are enabled
        if not self.config.get("enable_data_warnings", True):
            return
        
        total_usage = downloaded + uploaded
        warning_threshold = self.config.get("data_warning_threshold_mb", 1000) * 1024 * 1024  # MB to bytes
        critical_threshold = self.config.get("data_critical_threshold_mb", 5000) * 1024 * 1024
        
        current_time = time.time()
        
        # Avoid spamming warnings (minimum 5 minutes between same warning)
        if current_time - self.last_warning_time < 300:
            return
        
        # Critical threshold (5GB default)
        if total_usage >= critical_threshold and 'critical' not in self.warning_thresholds_hit:
            self.warning_thresholds_hit.add('critical')
            self.last_warning_time = current_time
            
            msg = (f"CRITICAL: {Format.format_bytes(total_usage)} data used this session! "
                   f"You've exceeded {Format.format_bytes(critical_threshold)}. "
                   "Consider disconnecting to avoid carrier detection.")
            
            self.show_notification("Data Usage Critical", msg, "critical")
            self.logger.warning(msg)
        
        # Warning threshold (1GB default)
        elif total_usage >= warning_threshold and 'warning' not in self.warning_thresholds_hit:
            self.warning_thresholds_hit.add('warning')
            self.last_warning_time = current_time
            
            msg = (f"Data usage: {Format.format_bytes(total_usage)} this session. "
                   f"Approaching threshold of {Format.format_bytes(warning_threshold)}.")
            
            self.show_notification("Data Usage Warning", msg, "normal")
            self.logger.info(msg)

    def update_log_display(self):
        """Update log text view with efficient incremental updates"""
        logs = self.logger.get_all_logs()

        # Only update if new logs added
        if len(logs) <= self.last_log_count:
            return

        # Get only new logs
        new_logs = logs[self.last_log_count :]
        search_text = self.log_search_entry.get_text().lower()

        # Filter and append new logs
        for i, entry in enumerate(new_logs):
            level = entry["level"]

            # Apply level filter
            if level not in self.log_filters or not self.log_filters[level]:
                continue

            # Apply search filter
            if search_text and search_text not in entry["message"].lower():
                continue

            # Format: [HH:MM:SS] [OK] Message (compact single line)
            timestamp = entry["timestamp"].split()[1]  # Get time only

            # Level symbols (ASCII)
            symbols = {
                "DEBUG": "[D]",
                "INFO": "[i]",
                "OK": "[OK]",
                "WARN": "[!]",
                "ERROR": "[X]",
                "CRITICAL": "[!!]",
            }
            symbol = symbols.get(level, "-")

            # Line number
            line_num = self.last_log_count + i + 1
            line_text = f"{line_num}\n"
            end_iter = self.log_line_numbers_buffer.get_end_iter()
            self.log_line_numbers_buffer.insert_with_tags_by_name(end_iter, line_text, "line_num")

            # Compact log line
            text = f"[{timestamp}] {symbol} {entry['message']}\n"

            tag = level.lower()
            if level == "CRITICAL":
                tag = "error"

            end_iter = self.log_buffer.get_end_iter()
            self.log_buffer.insert_with_tags_by_name(end_iter, text, tag)

        self.last_log_count = len(logs)

        # Auto-scroll to bottom
        mark = self.log_buffer.get_insert()
        self.log_textview.scroll_to_mark(mark, 0.0, True, 0.0, 1.0)

    def on_log_filter_toggled(self, button, level):
        """Handle log level filter toggle"""
        self.log_filters[level] = button.get_active()
        self.refresh_log_display()

    def on_log_search_changed(self, entry):
        """Handle log search text change"""
        self.refresh_log_display()

    def refresh_log_display(self):
        """Refresh entire log display with current filters"""
        self.log_buffer.set_text("")
        self.log_line_numbers_buffer.set_text("")
        self.last_log_count = 0
        self.update_log_display()

    def on_copy_logs(self, button):
        """Copy visible logs to clipboard"""
        clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)

        start = self.log_buffer.get_start_iter()
        end = self.log_buffer.get_end_iter()
        text = self.log_buffer.get_text(start, end, True)

        clipboard.set_text(text, -1)
        self.logger.ok("Logs copied to clipboard")

    def on_export_logs(self, button):
        """Export logs to file"""
        dialog = Gtk.FileChooserDialog(
            title="Export Logs", parent=self, action=Gtk.FileChooserAction.SAVE
        )
        dialog.add_buttons(
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_SAVE, Gtk.ResponseType.OK
        )
        dialog.set_current_name(f"pdanet-logs-{datetime.now().strftime('%Y%m%d-%H%M%S')}.txt")

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            filepath = dialog.get_filename()
            try:
                start = self.log_buffer.get_start_iter()
                end = self.log_buffer.get_end_iter()
                text = self.log_buffer.get_text(start, end, True)

                with open(filepath, "w") as f:
                    f.write(text)

                self.logger.ok(f"Logs exported to {filepath}")
            except Exception as e:
                self.logger.error(f"Export failed: {e}")

        dialog.destroy()

    def on_clear_logs(self, button):
        """Clear log buffer"""
        self.logger.clear_buffer()
        self.log_buffer.set_text("")
        self.log_line_numbers_buffer.set_text("")
        self.last_log_count = 0
        self.logger.ok("Log buffer cleared")

    def load_settings(self):
        """Load settings from config"""
        # Auto-reconnect
        auto_reconnect = self.config.get("auto_reconnect", False)
        self.reconnect_switch.set_active(auto_reconnect)
        if auto_reconnect:
            self.connection.enable_auto_reconnect(True)

        # Auto-start
        autostart = self.config.is_autostart_enabled()
        self.autostart_switch.set_active(autostart)

    def on_connect_clicked(self, button):
        """Handle connect button"""
        mode = self.mode_combo.get_active_id()

        # For iPhone and WiFi modes, show dialog to get SSID/password
        if mode in ["iphone", "wifi"]:
            result = self.show_wifi_credentials_dialog(mode)
            if not result or not result[0]:
                return  # User cancelled

            ssid, password, save_password = result

            self.connect_button.set_sensitive(False)
            self.disconnect_button.set_sensitive(False)
            self.connection.connect(mode=mode, ssid=ssid, password=password)

            # Save password after successful connection
            if save_password and password:
                # Wait for connection to be established
                def check_and_save():
                    if self.connection.is_connected():
                        self.config.save_wifi_network(ssid, password)
                        self.logger.ok(f"Saved password for network: {ssid}")
                        return False  # Stop checking
                    return True  # Keep checking

                GLib.timeout_add(3000, check_and_save)  # Check after 3 seconds

            GLib.timeout_add(2000, self.update_button_states)
        else:
            # USB mode - no credentials needed
            self.connect_button.set_sensitive(False)
            self.disconnect_button.set_sensitive(False)
            self.connection.connect(mode=mode)
            GLib.timeout_add(2000, self.update_button_states)

    def show_wifi_credentials_dialog(self, mode):
        """Show dialog to get WiFi/iPhone credentials with network scanning"""
        dialog = Gtk.Dialog(title=f"{mode.upper()} Connection", transient_for=self, flags=0)
        dialog.add_buttons(
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OK, Gtk.ResponseType.OK
        )

        box = dialog.get_content_area()
        box.set_spacing(10)
        box.set_margin_top(10)
        box.set_margin_bottom(10)
        box.set_margin_start(10)
        box.set_margin_end(10)

        # Info label
        if mode == "iphone":
            info_text = "Enter your iPhone Personal Hotspot details:"
        else:
            info_text = "Enter Android WiFi Hotspot details:"

        info_label = Gtk.Label(label=info_text)
        box.pack_start(info_label, False, False, 0)

        # Scan button
        scan_button = Gtk.Button(label="Scan Networks")
        scan_button.get_style_context().add_class("button-connect")
        box.pack_start(scan_button, False, False, 5)

        # SSID ComboBox with entry (allows both selection and manual entry)
        ssid_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        ssid_label = Gtk.Label(label="Network Name (SSID):")
        ssid_label.set_width_chars(20)
        ssid_label.set_xalign(0)

        ssid_combo = Gtk.ComboBoxText.new_with_entry()
        ssid_combo.set_entry_text_column(0)
        ssid_entry = ssid_combo.get_child()
        ssid_entry.set_placeholder_text("iPhone" if mode == "iphone" else "AndroidAP")

        # Load saved networks and populate combo
        saved_networks = self.config.list_saved_wifi_networks()
        for saved_ssid in saved_networks:
            ssid_combo.append_text(saved_ssid)

        ssid_box.pack_start(ssid_label, False, False, 0)
        ssid_box.pack_start(ssid_combo, True, True, 0)
        box.pack_start(ssid_box, False, False, 0)

        # Password entry
        pass_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        pass_label = Gtk.Label(label="Password:")
        pass_label.set_width_chars(20)
        pass_label.set_xalign(0)
        pass_entry = Gtk.Entry()
        pass_entry.set_visibility(False)
        pass_entry.set_placeholder_text("Optional if open network")
        pass_box.pack_start(pass_label, False, False, 0)
        pass_box.pack_start(pass_entry, True, True, 0)
        box.pack_start(pass_box, False, False, 0)

        # Save password checkbox
        save_password_check = Gtk.CheckButton(label="Save password for this network")
        save_password_check.set_active(False)
        box.pack_start(save_password_check, False, False, 0)

        # Auto-fill password when saved network is selected
        def on_ssid_changed(combo):
            text = ssid_entry.get_text()

            # Check if we have a saved password
            saved_password = self.config.get_wifi_password(text)
            if saved_password:
                pass_entry.set_text(saved_password)
                save_password_check.set_active(True)
            else:
                pass_entry.set_text("")
                save_password_check.set_active(False)

        ssid_combo.connect("changed", on_ssid_changed)

        # Scan status label
        scan_status = Gtk.Label(label="")
        scan_status.get_style_context().add_class("metric-label")
        box.pack_start(scan_status, False, False, 0)

        # Scan button callback
        def on_scan_clicked(btn):
            btn.set_sensitive(False)
            scan_status.set_text("Scanning...")

            # Scan networks
            networks = self.scan_networks(mode)

            # Clear and populate combo
            ssid_combo.remove_all()
            if networks:
                for ssid, signal, security in networks:
                    # Add SSID to combo (signal and security shown during scan but not stored)
                    ssid_combo.append_text(ssid)

                ssid_combo.set_active(0)
                scan_status.set_text(f"Found {len(networks)} networks")
            else:
                scan_status.set_text("No networks found. Enter manually.")

            btn.set_sensitive(True)

        scan_button.connect("clicked", on_scan_clicked)

        # Stealth mode notice for iPhone
        if mode == "iphone":
            notice = Gtk.Label()
            notice.set_markup(
                "<i>Note: Aggressive stealth mode will be automatically enabled\nto bypass carrier throttling detection.</i>"
            )
            notice.set_line_wrap(True)
            box.pack_start(notice, False, False, 5)

        dialog.show_all()
        response = dialog.run()

        ssid = ssid_entry.get_text() if response == Gtk.ResponseType.OK else None
        password = pass_entry.get_text() if response == Gtk.ResponseType.OK else None
        save_password = (
            save_password_check.get_active() if response == Gtk.ResponseType.OK else False
        )

        dialog.destroy()

        return ssid, password, save_password

    def scan_networks(self, mode):
        """Scan for available WiFi networks using nmcli"""
        try:
            # Rescan for fresh results
            subprocess.run(
                ["nmcli", "device", "wifi", "rescan"], check=False, capture_output=True, timeout=5
            )

            # Get network list
            result = subprocess.run(
                ["nmcli", "-t", "-f", "SSID,SIGNAL,SECURITY", "device", "wifi", "list"],
                check=False,
                capture_output=True,
                text=True,
                timeout=10,
            )

            if result.returncode == 0:
                networks = []
                for line in result.stdout.strip().split("\n"):
                    if line:
                        parts = line.split(":")
                        if len(parts) >= 1 and parts[0]:
                            ssid = parts[0]
                            # Filter out duplicates and hidden networks
                            if ssid and ssid not in [n[0] for n in networks]:
                                signal = parts[1] if len(parts) > 1 else "?"
                                security = parts[2] if len(parts) > 2 else "None"
                                networks.append((ssid, signal, security))

                # Sort by signal strength (descending)
                networks.sort(key=lambda x: int(x[1]) if x[1].isdigit() else 0, reverse=True)
                return networks

            return []

        except subprocess.TimeoutExpired:
            self.logger.error("Network scan timed out")
            return []
        except Exception as e:
            self.logger.error(f"Network scan failed: {e}")
            return []

    def on_disconnect_clicked(self, button):
        """Handle disconnect button"""
        self.connect_button.set_sensitive(False)
        self.disconnect_button.set_sensitive(False)
        self.connection.disconnect()
        GLib.timeout_add(2000, self.update_button_states)

    def update_button_states(self):
        """Update button sensitivity based on state"""
        state = self.connection.get_state()

        if state == ConnectionState.CONNECTED:
            self.connect_button.set_sensitive(False)
            self.disconnect_button.set_sensitive(True)
            if self.indicator:
                self.tray_connect_item.set_label("Disconnect")
                self.indicator.set_icon("network-wireless-connected")
        else:
            self.connect_button.set_sensitive(True)
            self.disconnect_button.set_sensitive(False)
            if self.indicator:
                self.tray_connect_item.set_label("Connect")
                self.indicator.set_icon("network-wireless-disconnected")

        return False

    # NOTE: Stealth mode is now AUTOMATIC for WiFi/iPhone connections
    # The pdanet-iphone-connect and pdanet-wifi-connect scripts apply it automatically
    # No manual toggle needed - it's always active for carrier bypass

    def on_auto_reconnect_toggled(self, switch, gparam):
        """Handle auto-reconnect toggle"""
        enabled = switch.get_active()
        self.connection.enable_auto_reconnect(enabled)
        self.config.set("auto_reconnect", enabled)

    def on_autostart_toggled(self, switch, gparam):
        """Handle auto-start toggle"""
        enabled = switch.get_active()
        if enabled:
            self.config.enable_autostart()
        else:
            self.config.disable_autostart()

    def on_settings_clicked(self, button):
        """Open settings dialog"""
        dialog = Gtk.Dialog(title="Settings", parent=self, flags=Gtk.DialogFlags.MODAL)
        dialog.add_buttons(
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_SAVE, Gtk.ResponseType.OK
        )
        dialog.set_default_size(500, 600)

        content = dialog.get_content_area()
        content.set_spacing(10)
        content.set_margin_top(10)
        content.set_margin_bottom(10)
        content.set_margin_start(10)
        content.set_margin_end(10)

        # Create notebook for tabbed settings
        notebook = Gtk.Notebook()
        content.pack_start(notebook, True, True, 0)

        # === CONNECTION TAB ===
        conn_page = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        conn_page.set_margin_top(10)
        conn_page.set_margin_bottom(10)
        conn_page.set_margin_start(10)
        conn_page.set_margin_end(10)

        # Proxy settings
        proxy_frame = Gtk.Frame(label="Proxy Configuration")
        proxy_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        proxy_box.set_margin_top(10)
        proxy_box.set_margin_bottom(10)
        proxy_box.set_margin_start(10)
        proxy_box.set_margin_end(10)

        proxy_ip_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        proxy_ip_label = Gtk.Label(label="Proxy IP:")
        proxy_ip_label.set_width_chars(15)
        proxy_ip_label.set_xalign(0)
        proxy_ip_entry = Gtk.Entry()
        proxy_ip_entry.set_text(self.config.get("proxy_ip", "192.168.49.1"))
        proxy_ip_box.pack_start(proxy_ip_label, False, False, 0)
        proxy_ip_box.pack_start(proxy_ip_entry, True, True, 0)
        proxy_box.pack_start(proxy_ip_box, False, False, 0)

        proxy_port_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        proxy_port_label = Gtk.Label(label="Proxy Port:")
        proxy_port_label.set_width_chars(15)
        proxy_port_label.set_xalign(0)
        proxy_port_spin = Gtk.SpinButton()
        proxy_port_spin.set_range(1, 65535)
        proxy_port_spin.set_increments(1, 100)
        proxy_port_spin.set_value(self.config.get("proxy_port", 8000))
        proxy_port_box.pack_start(proxy_port_label, False, False, 0)
        proxy_port_box.pack_start(proxy_port_spin, True, True, 0)
        proxy_box.pack_start(proxy_port_box, False, False, 0)

        proxy_frame.add(proxy_box)
        conn_page.pack_start(proxy_frame, False, False, 0)

        # Auto-reconnect settings
        reconnect_frame = Gtk.Frame(label="Auto-Reconnect")
        reconnect_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        reconnect_box.set_margin_top(10)
        reconnect_box.set_margin_bottom(10)
        reconnect_box.set_margin_start(10)
        reconnect_box.set_margin_end(10)

        attempts_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        attempts_label = Gtk.Label(label="Max Attempts:")
        attempts_label.set_width_chars(15)
        attempts_label.set_xalign(0)
        attempts_spin = Gtk.SpinButton()
        attempts_spin.set_range(1, 10)
        attempts_spin.set_increments(1, 1)
        attempts_spin.set_value(self.config.get("reconnect_attempts", 3))
        attempts_box.pack_start(attempts_label, False, False, 0)
        attempts_box.pack_start(attempts_spin, True, True, 0)
        reconnect_box.pack_start(attempts_box, False, False, 0)

        delay_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        delay_label = Gtk.Label(label="Initial Delay (s):")
        delay_label.set_width_chars(15)
        delay_label.set_xalign(0)
        delay_spin = Gtk.SpinButton()
        delay_spin.set_range(1, 60)
        delay_spin.set_increments(1, 5)
        delay_spin.set_value(self.config.get("reconnect_delay", 5))
        delay_box.pack_start(delay_label, False, False, 0)
        delay_box.pack_start(delay_spin, True, True, 0)
        reconnect_box.pack_start(delay_box, False, False, 0)

        reconnect_frame.add(reconnect_box)
        conn_page.pack_start(reconnect_frame, False, False, 0)

        # Stealth mode settings
        stealth_frame = Gtk.Frame(label="Stealth Mode")
        stealth_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        stealth_box.set_margin_top(10)
        stealth_box.set_margin_bottom(10)
        stealth_box.set_margin_start(10)
        stealth_box.set_margin_end(10)

        level_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        level_label = Gtk.Label(label="Default Level:")
        level_label.set_width_chars(15)
        level_label.set_xalign(0)
        level_combo = Gtk.ComboBoxText()
        level_combo.append("1", "Level 1 - Basic")
        level_combo.append("2", "Level 2 - Standard")
        level_combo.append("3", "Level 3 - Aggressive")
        level_combo.set_active(self.config.get("stealth_level", 3) - 1)
        level_box.pack_start(level_label, False, False, 0)
        level_box.pack_start(level_combo, True, True, 0)
        stealth_box.pack_start(level_box, False, False, 0)

        stealth_frame.add(stealth_box)
        conn_page.pack_start(stealth_frame, False, False, 0)

        # Saved Networks management
        saved_networks_frame = Gtk.Frame(label="Saved WiFi Networks")
        saved_networks_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        saved_networks_box.set_margin_top(10)
        saved_networks_box.set_margin_bottom(10)
        saved_networks_box.set_margin_start(10)
        saved_networks_box.set_margin_end(10)

        manage_networks_btn = Gtk.Button(label="Manage Saved Networks")
        manage_networks_btn.connect("clicked", lambda b: self.show_manage_networks_dialog())
        saved_networks_box.pack_start(manage_networks_btn, False, False, 0)

        saved_count_label = Gtk.Label(
            label=f"Saved networks: {len(self.config.list_saved_wifi_networks())}"
        )
        saved_count_label.get_style_context().add_class("metric-label")
        saved_networks_box.pack_start(saved_count_label, False, False, 0)

        saved_networks_frame.add(saved_networks_box)
        conn_page.pack_start(saved_networks_frame, False, False, 0)

        notebook.append_page(conn_page, Gtk.Label(label="Connection"))

        # === INTERFACE TAB ===
        ui_page = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        ui_page.set_margin_top(10)
        ui_page.set_margin_bottom(10)
        ui_page.set_margin_start(10)
        ui_page.set_margin_end(10)

        # Auto-start
        autostart_frame = Gtk.Frame(label="Startup")
        autostart_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        autostart_box.set_margin_top(10)
        autostart_box.set_margin_bottom(10)
        autostart_box.set_margin_start(10)
        autostart_box.set_margin_end(10)

        autostart_check = Gtk.CheckButton(label="Start GUI on system boot")
        autostart_check.set_active(self.config.get("autostart", False))
        autostart_box.pack_start(autostart_check, False, False, 0)

        minimize_check = Gtk.CheckButton(label="Start minimized to tray")
        minimize_check.set_active(self.config.get("start_minimized", False))
        autostart_box.pack_start(minimize_check, False, False, 0)

        autostart_frame.add(autostart_box)
        ui_page.pack_start(autostart_frame, False, False, 0)

        # Logging
        log_frame = Gtk.Frame(label="Logging")
        log_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        log_box.set_margin_top(10)
        log_box.set_margin_bottom(10)
        log_box.set_margin_start(10)
        log_box.set_margin_end(10)

        verbosity_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        verbosity_label = Gtk.Label(label="Log Verbosity:")
        verbosity_label.set_width_chars(15)
        verbosity_label.set_xalign(0)
        verbosity_combo = Gtk.ComboBoxText()
        verbosity_combo.append("DEBUG", "DEBUG")
        verbosity_combo.append("INFO", "INFO")
        verbosity_combo.append("WARNING", "WARNING")
        verbosity_combo.append("ERROR", "ERROR")
        verbosity_combo.set_active_id(self.config.get("log_level", "INFO"))
        verbosity_box.pack_start(verbosity_label, False, False, 0)
        verbosity_box.pack_start(verbosity_combo, True, True, 0)
        log_box.pack_start(verbosity_box, False, False, 0)

        log_frame.add(log_box)
        ui_page.pack_start(log_frame, False, False, 0)

        # Data Usage Warnings
        data_frame = Gtk.Frame(label="Data Usage Warnings")
        data_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        data_box.set_margin_top(10)
        data_box.set_margin_bottom(10)
        data_box.set_margin_start(10)
        data_box.set_margin_end(10)

        enable_warnings_check = Gtk.CheckButton(label="Enable data usage warnings")
        enable_warnings_check.set_active(self.config.get("enable_data_warnings", True))
        data_box.pack_start(enable_warnings_check, False, False, 0)

        warning_threshold_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        warning_threshold_label = Gtk.Label(label="Warning at (MB):")
        warning_threshold_label.set_width_chars(15)
        warning_threshold_label.set_xalign(0)
        warning_threshold_spin = Gtk.SpinButton()
        warning_threshold_spin.set_range(100, 50000)
        warning_threshold_spin.set_increments(100, 1000)
        warning_threshold_spin.set_value(self.config.get("data_warning_threshold_mb", 1000))
        warning_threshold_box.pack_start(warning_threshold_label, False, False, 0)
        warning_threshold_box.pack_start(warning_threshold_spin, True, True, 0)
        data_box.pack_start(warning_threshold_box, False, False, 0)

        critical_threshold_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        critical_threshold_label = Gtk.Label(label="Critical at (MB):")
        critical_threshold_label.set_width_chars(15)
        critical_threshold_label.set_xalign(0)
        critical_threshold_spin = Gtk.SpinButton()
        critical_threshold_spin.set_range(500, 100000)
        critical_threshold_spin.set_increments(500, 1000)
        critical_threshold_spin.set_value(self.config.get("data_critical_threshold_mb", 5000))
        critical_threshold_box.pack_start(critical_threshold_label, False, False, 0)
        critical_threshold_box.pack_start(critical_threshold_spin, True, True, 0)
        data_box.pack_start(critical_threshold_box, False, False, 0)

        data_frame.add(data_box)
        ui_page.pack_start(data_frame, False, False, 0)

        notebook.append_page(ui_page, Gtk.Label(label="Interface"))

        # Show dialog
        dialog.show_all()
        response = dialog.run()

        if response == Gtk.ResponseType.OK:
            # Save settings
            self.config.set("proxy_ip", proxy_ip_entry.get_text())
            self.config.set("proxy_port", int(proxy_port_spin.get_value()))
            self.config.set("reconnect_attempts", int(attempts_spin.get_value()))
            self.config.set("reconnect_delay", int(delay_spin.get_value()))
            self.config.set("stealth_level", int(level_combo.get_active_id()))
            self.config.set("autostart", autostart_check.get_active())
            self.config.set("start_minimized", minimize_check.get_active())
            self.config.set("log_level", verbosity_combo.get_active_id())
            self.config.set("enable_data_warnings", enable_warnings_check.get_active())
            self.config.set("data_warning_threshold_mb", int(warning_threshold_spin.get_value()))
            self.config.set("data_critical_threshold_mb", int(critical_threshold_spin.get_value()))
            self.config.save()

            # Apply auto-reconnect settings
            self.connection.max_reconnect_attempts = int(attempts_spin.get_value())
            self.connection.reconnect_delay = int(delay_spin.get_value())

            self.logger.ok("Settings saved successfully")

        dialog.destroy()

    def show_manage_networks_dialog(self):
        """Show dialog to manage saved WiFi networks"""
        dialog = Gtk.Dialog(title="Manage Saved Networks", parent=self, flags=Gtk.DialogFlags.MODAL)
        dialog.add_button(Gtk.STOCK_CLOSE, Gtk.ResponseType.CLOSE)
        dialog.set_default_size(500, 400)

        content = dialog.get_content_area()
        content.set_spacing(10)
        content.set_margin_top(10)
        content.set_margin_bottom(10)
        content.set_margin_start(10)
        content.set_margin_end(10)

        # Header
        header = Gtk.Label(label="Saved WiFi Networks")
        header.get_style_context().add_class("panel-header")
        content.pack_start(header, False, False, 0)

        # List of saved networks
        listbox = Gtk.ListBox()
        listbox.set_selection_mode(Gtk.SelectionMode.SINGLE)

        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scroll.add(listbox)
        content.pack_start(scroll, True, True, 0)

        def refresh_list():
            # Clear list
            for child in listbox.get_children():
                listbox.remove(child)

            # Add saved networks
            saved_networks = self.config.list_saved_wifi_networks()
            if not saved_networks:
                no_networks_label = Gtk.Label(label="No saved networks")
                no_networks_label.get_style_context().add_class("metric-label")
                listbox.add(no_networks_label)
            else:
                for ssid in saved_networks:
                    row_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
                    row_box.set_margin_top(5)
                    row_box.set_margin_bottom(5)
                    row_box.set_margin_start(10)
                    row_box.set_margin_end(10)

                    # SSID label
                    ssid_label = Gtk.Label(label=ssid)
                    ssid_label.set_xalign(0)
                    row_box.pack_start(ssid_label, True, True, 0)

                    # Delete button
                    delete_btn = Gtk.Button(label="Del")
                    delete_btn.set_tooltip_text(f"Delete {ssid}")
                    delete_btn.connect("clicked", lambda b, s=ssid: delete_network(s))
                    row_box.pack_start(delete_btn, False, False, 0)

                    row_box.show_all()
                    listbox.add(row_box)

            listbox.show_all()

        def delete_network(ssid):
            self.config.delete_wifi_network(ssid)
            self.logger.ok(f"Deleted saved network: {ssid}")
            refresh_list()

        refresh_list()
        dialog.show_all()
        dialog.run()
        dialog.destroy()

    def on_history_clicked(self, button):
        """Show connection history dialog"""
        dialog = Gtk.Dialog(title="Connection History", parent=self, flags=Gtk.DialogFlags.MODAL)
        dialog.add_buttons(
            "Clear History", Gtk.ResponseType.REJECT,
            Gtk.STOCK_CLOSE, Gtk.ResponseType.CLOSE
        )
        dialog.set_default_size(700, 500)

        content = dialog.get_content_area()
        content.set_spacing(10)
        content.set_margin_top(10)
        content.set_margin_bottom(10)
        content.set_margin_start(10)
        content.set_margin_end(10)

        # Header with stats
        header_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        
        title_label = Gtk.Label(label="CONNECTION HISTORY")
        title_label.get_style_context().add_class("panel-header")
        header_box.pack_start(title_label, False, False, 0)

        # Load history
        history = self.load_connection_history()
        
        if not history:
            no_history_label = Gtk.Label(label="No connection history available")
            no_history_label.get_style_context().add_class("metric-label")
            content.pack_start(no_history_label, True, True, 0)
        else:
            # Summary stats
            total_sessions = len(history)
            total_downloaded = sum(s.get('downloaded', 0) for s in history)
            total_uploaded = sum(s.get('uploaded', 0) for s in history)
            total_duration = sum(s.get('duration', 0) for s in history)
            
            stats_label = Gtk.Label()
            stats_text = (
                f"Total Sessions: {total_sessions}  |  "
                f"Downloaded: {Format.format_bytes(total_downloaded)}  |  "
                f"Uploaded: {Format.format_bytes(total_uploaded)}  |  "
                f"Total Time: {Format.format_uptime(int(total_duration))}"
            )
            stats_label.set_markup(f"<span foreground='{Colors.GREEN}'>{stats_text}</span>")
            header_box.pack_start(stats_label, False, False, 5)

        content.pack_start(header_box, False, False, 0)

        # History list with TreeView
        if history:
            # Create ListStore
            # Columns: Timestamp, Duration, Downloaded, Uploaded, Interface, Latency
            liststore = Gtk.ListStore(str, str, str, str, str, str)
            
            for session in reversed(history):  # Most recent first
                timestamp = session.get('timestamp', 'Unknown')
                try:
                    # Format timestamp nicely
                    from datetime import datetime
                    dt = datetime.fromisoformat(timestamp)
                    timestamp_str = dt.strftime("%Y-%m-%d %H:%M:%S")
                except:
                    timestamp_str = timestamp[:19] if len(timestamp) > 19 else timestamp
                
                duration = Format.format_uptime(int(session.get('duration', 0)))
                downloaded = Format.format_bytes(session.get('downloaded', 0))
                uploaded = Format.format_bytes(session.get('uploaded', 0))
                interface = session.get('interface', 'Unknown')
                latency = f"{session.get('avg_latency', 0):.1f} ms"
                
                liststore.append([timestamp_str, duration, downloaded, uploaded, interface, latency])

            # Create TreeView
            treeview = Gtk.TreeView(model=liststore)
            treeview.set_grid_lines(Gtk.TreeViewGridLines.BOTH)
            
            # Add columns
            columns = [
                ("Timestamp", 0, 180),
                ("Duration", 1, 100),
                ("Downloaded", 2, 100),
                ("Uploaded", 3, 100),
                ("Interface", 4, 80),
                ("Avg Latency", 5, 90)
            ]
            
            for col_title, col_id, width in columns:
                renderer = Gtk.CellRendererText()
                column = Gtk.TreeViewColumn(col_title, renderer, text=col_id)
                column.set_min_width(width)
                column.set_resizable(True)
                column.set_sort_column_id(col_id)
                treeview.append_column(column)

            # Scroll window
            scroll = Gtk.ScrolledWindow()
            scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
            scroll.add(treeview)
            content.pack_start(scroll, True, True, 0)

        dialog.show_all()
        response = dialog.run()
        
        # Handle clear history
        if response == Gtk.ResponseType.REJECT:
            confirm = Gtk.MessageDialog(
                transient_for=dialog,
                flags=0,
                message_type=Gtk.MessageType.WARNING,
                buttons=Gtk.ButtonsType.YES_NO,
                text="Clear Connection History?"
            )
            confirm.format_secondary_text(
                "This will permanently delete all connection history. This action cannot be undone."
            )
            
            if confirm.run() == Gtk.ResponseType.YES:
                self.clear_connection_history()
                self.logger.ok("Connection history cleared")
                confirm.destroy()
                dialog.destroy()
                # Reopen dialog to show empty state
                self.on_history_clicked(button)
                return
            
            confirm.destroy()
        
        dialog.destroy()

    def load_connection_history(self):
        """Load connection history from file"""
        try:
            history_file = Path(CONFIG_DIR) / "connection_history.json"
            if history_file.exists():
                with open(history_file) as f:
                    return json.load(f)
        except Exception as e:
            self.logger.warning(f"Failed to load connection history: {e}")
        return []

    def clear_connection_history(self):
        """Clear all connection history"""
        try:
            history_file = Path(CONFIG_DIR) / "connection_history.json"
            if history_file.exists():
                history_file.unlink()
            self.show_notification("History Cleared", "Connection history has been deleted", "low")
        except Exception as e:
            self.logger.error(f"Failed to clear history: {e}")

    def on_speedtest_clicked(self, button):
        """Run speed test and show results"""
        # Create dialog
        dialog = Gtk.Dialog(title="Speed Test", parent=self, flags=Gtk.DialogFlags.MODAL)
        dialog.add_button(Gtk.STOCK_CLOSE, Gtk.ResponseType.CLOSE)
        dialog.set_default_size(500, 400)

        content = dialog.get_content_area()
        content.set_spacing(10)
        content.set_margin_top(10)
        content.set_margin_bottom(10)
        content.set_margin_start(10)
        content.set_margin_end(10)

        # Status label
        status_label = Gtk.Label(label="Running speed test...")
        status_label.get_style_context().add_class("panel-header")
        content.pack_start(status_label, False, False, 0)

        # Progress bar
        progress = Gtk.ProgressBar()
        progress.set_pulse_step(0.1)
        content.pack_start(progress, False, False, 0)

        # Results area
        results_view = Gtk.TextView()
        results_view.set_editable(False)
        results_view.set_monospace(True)
        results_view.set_wrap_mode(Gtk.WrapMode.WORD)
        results_buffer = results_view.get_buffer()

        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scroll.add(results_view)
        content.pack_start(scroll, True, True, 0)

        dialog.show_all()

        def run_speedtest():
            """Run speed test in background"""
            try:
                # Pulse progress bar
                def pulse():
                    progress.pulse()
                    return True

                pulse_id = GLib.timeout_add(100, pulse)

                # Try speedtest-cli first
                result = subprocess.run(
                    ["speedtest-cli", "--simple"],
                    check=False,
                    capture_output=True,
                    text=True,
                    timeout=60,
                )

                GLib.source_remove(pulse_id)

                if result.returncode == 0:
                    # Parse results
                    lines = result.stdout.strip().split("\n")
                    output = "╔══════════════════════════════════════╗\n"
                    output += "║         SPEED TEST RESULTS           ║\n"
                    output += "╚══════════════════════════════════════╝\n\n"

                    for line in lines:
                        if "Ping:" in line:
                            output += f"  PING:     {line.split('Ping:')[1].strip()}\n"
                        elif "Download:" in line:
                            output += f"  DOWNLOAD: {line.split('Download:')[1].strip()}\n"
                        elif "Upload:" in line:
                            output += f"  UPLOAD:   {line.split('Upload:')[1].strip()}\n"

                    GLib.idle_add(status_label.set_text, "Speed test complete!")
                    GLib.idle_add(results_buffer.set_text, output)
                    GLib.idle_add(progress.set_fraction, 1.0)
                    self.logger.ok("Speed test completed")
                else:
                    # Fallback: Use curl to test download speed
                    GLib.idle_add(status_label.set_text, "Using fallback speed test...")

                    # Test ping
                    ping_result = subprocess.run(
                        ["ping", "-c", "3", "8.8.8.8"],
                        check=False,
                        capture_output=True,
                        text=True,
                        timeout=10,
                    )

                    ping_time = "N/A"
                    for line in ping_result.stdout.split("\n"):
                        if "avg" in line:
                            parts = line.split("/")
                            if len(parts) >= 5:
                                ping_time = f"{parts[4]} ms"

                    # Test download speed with curl
                    import time

                    start = time.time()
                    dl_result = subprocess.run(
                        [
                            "curl",
                            "-sS",
                            "-L",
                            "-o",
                            "/dev/null",
                            "-w",
                            "%{speed_download}",
                            "--range",
                            "0-1048575",
                            "https://speed.hetzner.de/100MB.bin",
                        ],
                        check=False,
                        capture_output=True,
                        text=True,
                        timeout=30,
                    )
                    elapsed = time.time() - start

                    if dl_result.returncode == 0:
                        speed_bps = float(dl_result.stdout)
                        speed_mbps = (speed_bps * 8) / 1_000_000

                        output = "╔══════════════════════════════════════╗\n"
                        output += "║    SPEED TEST RESULTS (Fallback)     ║\n"
                        output += "╚══════════════════════════════════════╝\n\n"
                        output += f"  PING:     {ping_time}\n"
                        output += f"  DOWNLOAD: {speed_mbps:.2f} Mbit/s\n"
                        output += "  UPLOAD:   (not tested)\n\n"
                        output += "Note: Install speedtest-cli for full test:\n"
                        output += "  sudo apt install speedtest-cli\n"

                        GLib.idle_add(status_label.set_text, "Speed test complete!")
                        GLib.idle_add(results_buffer.set_text, output)
                        GLib.idle_add(progress.set_fraction, 1.0)
                        self.logger.ok("Speed test completed (fallback)")
                    else:
                        raise Exception("Fallback test failed")

            except subprocess.TimeoutExpired:
                GLib.source_remove(pulse_id)
                GLib.idle_add(status_label.set_text, "Speed test timed out")
                GLib.idle_add(
                    results_buffer.set_text,
                    "Speed test timed out after 60 seconds.\nCheck your internet connection.",
                )
                GLib.idle_add(progress.set_fraction, 0)
                self.logger.error("Speed test timed out")

            except Exception as e:
                if "pulse_id" in locals():
                    GLib.source_remove(pulse_id)
                GLib.idle_add(status_label.set_text, "Speed test failed")
                GLib.idle_add(
                    results_buffer.set_text,
                    f"Error: {e!s}\n\nMake sure you're connected to the internet.",
                )
                GLib.idle_add(progress.set_fraction, 0)
                self.logger.error(f"Speed test failed: {e}")

        # Run in background thread
        import threading

        thread = threading.Thread(target=run_speedtest, daemon=True)
        thread.start()

        dialog.run()
        dialog.destroy()

    def on_connection_state_changed(self, new_state):
        """Callback for connection state changes"""
        # Send desktop notification
        if new_state == ConnectionState.CONNECTED:
            self.show_notification("Connected", "PdaNet connection established", "low")
        elif new_state == ConnectionState.DISCONNECTED:
            self.show_notification("Disconnected", "PdaNet connection closed", "low")
        elif new_state == ConnectionState.ERROR:
            error_msg = self.connection.last_error or "Unknown error"
            self.show_notification("Connection Error", error_msg, "critical")
        
        GLib.idle_add(self.update_button_states)

    def on_connection_error(self, error_message):
        """Callback for connection errors"""
        # Send notification
        self.show_notification("Connection Error", error_message, "critical")

        def show_error():
            dialog = Gtk.MessageDialog(
                transient_for=self,
                flags=0,
                message_type=Gtk.MessageType.ERROR,
                buttons=Gtk.ButtonsType.OK,
                text="Connection Error",
            )
            dialog.format_secondary_text(error_message)
            dialog.run()
            dialog.destroy()

        GLib.idle_add(show_error)

    def on_quit(self, widget):
        """Quit application"""
        self.logger.info("Shutting down...")
        Gtk.main_quit()


def main():
    # Check for single instance
    if "--allow-multiple" not in sys.argv:
        instance = SingleInstance()
        if not instance.acquire():
            print("PdaNet Linux GUI is already running")
            sys.exit(1)

    # Check for start minimized
    start_minimized = "--start-minimized" in sys.argv

    # Create and run GUI
    app = PdaNetGUI(start_minimized=start_minimized)
    app.connect("destroy", Gtk.main_quit)
    app.show_all()
    Gtk.main()


if __name__ == "__main__":
    main()
