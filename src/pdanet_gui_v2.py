#!/usr/bin/env python3
"""
PdaNet Linux - Professional GUI v2
Cyberpunk-themed interface with full feature set
"""

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GLib

# Try to import AppIndicator3, but make it optional
try:
    gi.require_version('AppIndicator3', '0.1')
    from gi.repository import AppIndicator3
    HAS_APPINDICATOR = True
except (ValueError, ImportError):
    HAS_APPINDICATOR = False
    AppIndicator3 = None

import sys
import os
from datetime import datetime
import fcntl

# Add src directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from theme import Colors, Format, ASCII, get_css
from logger import get_logger
from config_manager import get_config
from stats_collector import get_stats
from connection_manager import get_connection_manager, ConnectionState

class SingleInstance:
    """Ensure only one instance of GUI runs"""
    def __init__(self, lockfile='/tmp/pdanet-linux-gui.lock'):
        self.lockfile = lockfile
        self.fp = None

    def acquire(self):
        """Acquire lock"""
        try:
            self.fp = open(self.lockfile, 'w')
            fcntl.lockf(self.fp, fcntl.LOCK_EX | fcntl.LOCK_NB)
            return True
        except IOError:
            return False

    def release(self):
        """Release lock"""
        if self.fp:
            fcntl.lockf(self.fp, fcntl.LOCK_UN)
            self.fp.close()
            try:
                os.unlink(self.lockfile)
            except:
                pass

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

        # Apply theme
        self.load_theme()

        # Build UI
        self.build_ui()

        # Setup system tray
        self.setup_indicator()

        # Register callbacks
        self.connection.register_state_change_callback(self.on_connection_state_changed)
        self.connection.register_error_callback(self.on_connection_error)

        # Start update loop
        GLib.timeout_add(1000, self.update_display)

        # Load settings
        self.load_settings()

        # Start minimized if requested
        if start_minimized:
            self.hide()
            self.logger.info("Started minimized to system tray")
        else:
            self.logger.info("GUI initialized")

    def load_theme(self):
        """Load cyberpunk theme"""
        css_provider = Gtk.CssProvider()
        css_provider.load_from_data(get_css().encode())
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(),
            css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

    def build_ui(self):
        """Build main interface"""
        main_vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.add(main_vbox)

        # Header
        header = self.build_header()
        main_vbox.pack_start(header, False, False, 0)

        # Main content (4-panel grid)
        content = self.build_content()
        main_vbox.pack_start(content, True, True, 0)

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

        # Right: Status indicators
        status_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=15)

        self.header_status_label = Gtk.Label(label="[DISCONNECTED]")
        self.header_time_label = Gtk.Label(label="")
        self.update_header_time()

        status_box.pack_end(self.header_time_label, False, False, 10)
        status_box.pack_end(self.header_status_label, False, False, 0)

        header.pack_start(title_box, False, False, 0)
        header.pack_end(status_box, False, False, 0)

        return header

    def build_content(self):
        """Build main content grid"""
        grid = Gtk.Grid()
        grid.set_column_homogeneous(False)
        grid.set_row_homogeneous(True)
        grid.set_column_spacing(2)
        grid.set_row_spacing(2)
        grid.set_margin_top(2)
        grid.set_margin_bottom(2)
        grid.set_margin_start(2)
        grid.set_margin_end(2)

        # Top left: Status panel
        status_panel = self.build_status_panel()
        grid.attach(status_panel, 0, 0, 1, 1)

        # Top right: Metrics panel
        metrics_panel = self.build_metrics_panel()
        grid.attach(metrics_panel, 1, 0, 1, 1)

        # Bottom left: Log panel
        log_panel = self.build_log_panel()
        grid.attach(log_panel, 0, 1, 1, 1)

        # Bottom right: Controls panel
        controls_panel = self.build_controls_panel()
        grid.attach(controls_panel, 1, 1, 1, 1)

        return grid

    def build_status_panel(self):
        """Build connection status panel"""
        panel = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
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

        panel.pack_start(self.status_state_label, False, False, 5)
        panel.pack_start(self.status_interface_label, False, False, 5)
        panel.pack_start(self.status_endpoint_label, False, False, 5)
        panel.pack_start(self.status_uptime_label, False, False, 5)
        panel.pack_start(self.status_stealth_label, False, False, 5)

        # Quality bar
        quality_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        quality_label = Gtk.Label(label="CONNECTION QUALITY")
        quality_label.get_style_context().add_class("metric-label")
        quality_label.set_xalign(0)

        self.quality_progress = Gtk.ProgressBar()
        self.quality_progress.set_fraction(0.75)
        self.quality_progress.set_text("75%")
        self.quality_progress.set_show_text(True)

        quality_box.pack_start(quality_label, False, False, 0)
        quality_box.pack_start(self.quality_progress, False, False, 0)
        panel.pack_start(quality_box, False, False, 10)

        return panel

    def build_metrics_panel(self):
        """Build network metrics panel"""
        panel = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
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

        panel.pack_start(self.metric_download_label, False, False, 5)
        panel.pack_start(self.metric_upload_label, False, False, 5)
        panel.pack_start(self.metric_latency_label, False, False, 5)
        panel.pack_start(self.metric_loss_label, False, False, 5)
        panel.pack_start(self.metric_total_label, False, False, 5)

        # Simple bandwidth graph placeholder
        graph_label = Gtk.Label(label="BANDWIDTH GRAPH")
        graph_label.get_style_context().add_class("metric-label")
        graph_label.set_xalign(0)
        panel.pack_start(graph_label, False, False, 10)

        self.graph_textview = Gtk.TextView()
        self.graph_textview.set_editable(False)
        self.graph_textview.set_cursor_visible(False)
        self.graph_textview.set_size_request(-1, 100)
        self.graph_textview.set_monospace(True)
        self.graph_buffer = self.graph_textview.get_buffer()

        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scroll.add(self.graph_textview)
        panel.pack_start(scroll, True, True, 0)

        return panel

    def build_log_panel(self):
        """Build system log panel"""
        panel = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        panel.get_style_context().add_class("panel")

        # Header
        header = Gtk.Label(label="SYSTEM LOG")
        header.get_style_context().add_class("panel-header")
        header.set_xalign(0)
        panel.pack_start(header, False, False, 0)

        # Log viewer
        self.log_textview = Gtk.TextView()
        self.log_textview.set_editable(False)
        self.log_textview.set_cursor_visible(False)
        self.log_textview.set_monospace(True)
        self.log_textview.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
        self.log_buffer = self.log_textview.get_buffer()

        # Create tags for different log levels
        self.log_buffer.create_tag("info", foreground=Colors.TEXT_GRAY)
        self.log_buffer.create_tag("ok", foreground=Colors.GREEN_DIM)
        self.log_buffer.create_tag("warn", foreground=Colors.ORANGE)
        self.log_buffer.create_tag("error", foreground=Colors.RED_DIM)

        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scroll.add(self.log_textview)
        panel.pack_start(scroll, True, True, 0)

        return panel

    def build_controls_panel(self):
        """Build controls panel"""
        panel = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
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
        panel.pack_start(mode_label, False, False, 5)

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
        panel.pack_start(self.connect_button, False, False, 5)

        self.disconnect_button = Gtk.Button(label="■ DISCONNECT")
        self.disconnect_button.get_style_context().add_class("button-disconnect")
        self.disconnect_button.connect("clicked", self.on_disconnect_clicked)
        self.disconnect_button.set_sensitive(False)
        panel.pack_start(self.disconnect_button, False, False, 0)

        # Separator
        sep = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        panel.pack_start(sep, False, False, 5)

        # Options
        options_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)

        # Stealth mode
        stealth_box = self.create_switch_row("STEALTH MODE", self.on_stealth_toggled)
        self.stealth_switch = stealth_box.get_children()[1]
        options_box.pack_start(stealth_box, False, False, 0)

        # Auto-reconnect
        reconnect_box = self.create_switch_row("AUTO-RECONNECT", self.on_auto_reconnect_toggled)
        self.reconnect_switch = reconnect_box.get_children()[1]
        options_box.pack_start(reconnect_box, False, False, 0)

        # Auto-start
        autostart_box = self.create_switch_row("START ON BOOT", self.on_autostart_toggled)
        self.autostart_switch = autostart_box.get_children()[1]
        options_box.pack_start(autostart_box, False, False, 0)

        panel.pack_start(options_box, False, False, 10)

        # Settings button
        settings_button = Gtk.Button(label="⚙ SETTINGS")
        settings_button.connect("clicked", self.on_settings_clicked)
        panel.pack_end(settings_button, False, False, 0)

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
        self.indicator = AppIndicator3.Indicator.new(
            "pdanet-linux",
            "network-wireless-disconnected",
            AppIndicator3.IndicatorCategory.APPLICATION_STATUS
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

        # Get current state
        state = self.connection.get_state()
        is_connected = (state == ConnectionState.CONNECTED)

        # Update status panel
        if state == ConnectionState.CONNECTED:
            self.status_state_label.get_children()[1].set_markup(
                f"<span foreground='{Colors.GREEN}'>● ACTIVE</span>"
            )
            self.header_status_label.set_markup(f"<span foreground='{Colors.GREEN}'>[CONNECTED]</span>")
        elif state == ConnectionState.CONNECTING:
            self.status_state_label.get_children()[1].set_markup(
                f"<span foreground='{Colors.ORANGE}'>◐ CONNECTING</span>"
            )
            self.header_status_label.set_markup(f"<span foreground='{Colors.ORANGE}'>[CONNECTING]</span>")
        else:
            self.status_state_label.get_children()[1].set_markup(
                f"<span foreground='{Colors.RED}'>● INACTIVE</span>"
            )
            self.header_status_label.set_markup(f"<span foreground='{Colors.TEXT_GRAY}'>[DISCONNECTED]</span>")

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

        return True

    def update_log_display(self):
        """Update log text view"""
        logs = self.logger.get_recent_logs(50)

        self.log_buffer.set_text("")
        for entry in logs:
            level = entry["level"]
            text = f"> {entry['timestamp']}\n  [{level}] :: {entry['message']}\n\n"

            tag = "info"
            if level == "OK":
                tag = "ok"
            elif level == "WARN":
                tag = "warn"
            elif level in ["ERROR", "CRITICAL"]:
                tag = "error"

            end_iter = self.log_buffer.get_end_iter()
            self.log_buffer.insert_with_tags_by_name(end_iter, text, tag)

        # Auto-scroll to bottom
        mark = self.log_buffer.get_insert()
        self.log_textview.scroll_to_mark(mark, 0.0, True, 0.0, 1.0)

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
            ssid, password = self.show_wifi_credentials_dialog(mode)
            if not ssid:
                return  # User cancelled
            
            self.connect_button.set_sensitive(False)
            self.disconnect_button.set_sensitive(False)
            self.connection.connect(mode=mode, ssid=ssid, password=password)
            GLib.timeout_add(2000, self.update_button_states)
        else:
            # USB mode - no credentials needed
            self.connect_button.set_sensitive(False)
            self.disconnect_button.set_sensitive(False)
            self.connection.connect(mode=mode)
            GLib.timeout_add(2000, self.update_button_states)

    def show_wifi_credentials_dialog(self, mode):
        """Show dialog to get WiFi/iPhone credentials"""
        dialog = Gtk.Dialog(title=f"{mode.upper()} Connection",
                           transient_for=self,
                           flags=0)
        dialog.add_buttons(
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
            Gtk.STOCK_OK, Gtk.ResponseType.OK
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

        # SSID entry
        ssid_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        ssid_label = Gtk.Label(label="Network Name (SSID):")
        ssid_label.set_width_chars(20)
        ssid_label.set_xalign(0)
        ssid_entry = Gtk.Entry()
        ssid_entry.set_placeholder_text("iPhone" if mode == "iphone" else "AndroidAP")
        ssid_box.pack_start(ssid_label, False, False, 0)
        ssid_box.pack_start(ssid_entry, True, True, 0)
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

        # Stealth mode notice for iPhone
        if mode == "iphone":
            notice = Gtk.Label()
            notice.set_markup("<i>Note: Aggressive stealth mode will be automatically enabled\nto bypass carrier throttling detection.</i>")
            notice.set_line_wrap(True)
            box.pack_start(notice, False, False, 5)

        dialog.show_all()
        response = dialog.run()
        
        ssid = ssid_entry.get_text() if response == Gtk.ResponseType.OK else None
        password = pass_entry.get_text() if response == Gtk.ResponseType.OK else None
        
        dialog.destroy()
        
        return ssid, password

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
            self.tray_connect_item.set_label("Disconnect")
            self.indicator.set_icon("network-wireless-connected")
        else:
            self.connect_button.set_sensitive(True)
            self.disconnect_button.set_sensitive(False)
            self.tray_connect_item.set_label("Connect")
            self.indicator.set_icon("network-wireless-disconnected")

        return False

    def on_stealth_toggled(self, switch, gparam):
        """Handle stealth mode toggle"""
        enabled = switch.get_active()
        # TODO: Implement stealth mode control
        self.logger.info(f"Stealth mode: {'enabled' if enabled else 'disabled'}")

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
        # TODO: Implement settings dialog
        self.logger.info("Settings clicked")

    def on_connection_state_changed(self, new_state):
        """Callback for connection state changes"""
        GLib.idle_add(self.update_button_states)

    def on_connection_error(self, error_message):
        """Callback for connection errors"""
        def show_error():
            dialog = Gtk.MessageDialog(
                transient_for=self,
                flags=0,
                message_type=Gtk.MessageType.ERROR,
                buttons=Gtk.ButtonsType.OK,
                text="Connection Error"
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
