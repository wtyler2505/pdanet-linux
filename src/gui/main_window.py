#!/usr/bin/env python3
"""
PdaNet Linux - Main Window (Refactored)
Professional GUI with modular panel architecture
"""

import os
import sys

# Ensure system GTK bindings are used
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_removed_src = False
if sys.path and sys.path[0] == _SCRIPT_DIR:
    sys.path.pop(0)
    _removed_src = True

try:
    import gi  # type: ignore
except Exception:
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
import shutil
import subprocess
import threading
import time
from pathlib import Path

# Add parent directory to path for relative imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from config_manager import get_config
from connection_manager import ConnectionState, get_connection_manager
from logger import get_logger
from stats_collector import get_stats
from theme import Colors, Format, get_css

# Import new dialog components
from dialogs.settings_dialog import SettingsDialog
from dialogs.first_run_wizard import FirstRunWizard
from dialogs.error_recovery_dialog import ErrorRecoveryDialog
from widgets.data_dashboard import DataUsageDashboard

# Import new panel components
from panels.connection_panel import ConnectionPanel
from panels.metrics_panel import MetricsPanel
from panels.log_panel import LogPanel
from panels.operations_panel import OperationsPanel


class PdaNetMainWindow(Gtk.Window):
    """
    Main application window with modular panel architecture
    Refactored from the original 3000+ line monolithic GUI
    """
    
    def __init__(self, start_minimized=False):
        super().__init__(title="PDANET LINUX")

        # Initialize core components
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

        # Set minimum window size
        geometry = Gdk.Geometry()
        geometry.min_width = 700
        geometry.min_height = 400
        self.set_geometry_hints(None, geometry, Gdk.WindowHints.MIN_SIZE)

        # Apply theme
        self.load_theme()

        # Initialize panels
        self.connection_panel = ConnectionPanel(self)
        self.metrics_panel = MetricsPanel(self)
        self.log_panel = LogPanel(self)
        self.operations_panel = OperationsPanel(self)

        # Build UI
        self.build_ui()

        # Setup system tray and notifications
        self.setup_indicator()
        self.setup_notifications()

        # Register callbacks
        self.connection.register_state_change_callback(self.on_connection_state_changed)
        self.connection.register_error_callback(self.on_connection_error)
        self.connection.register_error_recovery_callback(self.on_error_recovery_needed)

        # Test-mode state override
        self._test_state_file = None
        if "--test-mode" in sys.argv:
            self._test_state_file = os.environ.get("PDANET_TEST_STATE_FILE")

        # Start update loop
        update_interval = self.config.get("update_interval_ms", 1000)
        GLib.timeout_add(update_interval, self.update_display)

        # Setup keyboard shortcuts
        self.setup_keyboard_shortcuts()

        # Initialize data usage tracking
        self.last_warning_time = 0
        self.warning_thresholds_hit = set()

        # Load settings
        self.load_settings()
        
        # Check for first run and show wizard if needed
        self.check_first_run()

        # Start minimized if requested
        if start_minimized:
            self.hide()
            self.logger.info("Started minimized to system tray")
        else:
            self.logger.info("Main window initialized (refactored architecture)")

    def build_ui(self):
        """Build main interface using modular panels"""
        main_vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.add(main_vbox)

        # Header
        header = self.build_header()
        main_vbox.pack_start(header, False, False, 0)

        # Main content with panels in grid layout
        content_grid = self.build_content_grid()
        scroller = Gtk.ScrolledWindow()
        scroller.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scroller.add(content_grid)
        main_vbox.pack_start(scroller, True, True, 0)

        # Status bar
        statusbar = self.build_statusbar()
        main_vbox.pack_start(statusbar, False, False, 0)

    def build_content_grid(self):
        """Build main content grid with panels"""
        grid = Gtk.Grid()
        grid.set_hexpand(True)
        grid.set_vexpand(True)
        grid.set_column_homogeneous(True)
        grid.set_row_homogeneous(False)
        grid.set_column_spacing(2)
        grid.set_row_spacing(2)
        grid.set_margin_top(2)
        grid.set_margin_bottom(2)
        grid.set_margin_start(2)
        grid.set_margin_end(2)

        # Top left: Connection status panel
        connection_widget = self.connection_panel.get_widget()
        connection_widget.set_hexpand(True)
        connection_widget.set_vexpand(False)
        grid.attach(connection_widget, 0, 0, 1, 1)

        # Top right: Metrics panel with enhanced dashboard
        metrics_widget = self.metrics_panel.get_widget()
        metrics_widget.set_hexpand(True)
        metrics_widget.set_vexpand(False)
        grid.attach(metrics_widget, 1, 0, 1, 1)

        # Bottom left: Log panel
        log_widget = self.log_panel.get_widget()
        log_widget.set_hexpand(True)
        log_widget.set_vexpand(True)
        grid.attach(log_widget, 0, 1, 1, 1)

        # Bottom right: Operations/controls panel
        operations_widget = self.operations_panel.get_widget()
        operations_widget.set_hexpand(True)
        operations_widget.set_vexpand(True)
        grid.attach(operations_widget, 1, 1, 1, 1)

        return grid

    def build_header(self):
        """Build header bar (preserved from original)"""
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
        self.header_status_label.get_style_context().add_class("status-indicator")
        status_box.pack_start(self.header_status_label, False, False, 0)

        # Corner bracket
        corner_r = Gtk.Label(label="◈")
        corner_r.get_style_context().add_class("corner-bracket")
        status_box.pack_start(corner_r, False, False, 5)

        header.pack_start(title_box, False, False, 0)
        header.pack_end(status_box, False, False, 0)

        return header

    def build_statusbar(self):
        """Build bottom status bar (preserved from original)"""
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

    # ==================================================================
    # Helper Methods (preserved from original)
    # ==================================================================
    
    def create_metric_row(self, label, value):
        """Create a metric row with label and value"""
        row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        
        label_widget = Gtk.Label(label=label)
        label_widget.set_xalign(0)
        label_widget.get_style_context().add_class("metric-label")
        
        value_widget = Gtk.Label(label=value)
        value_widget.set_xalign(1)
        value_widget.get_style_context().add_class("metric-value")
        
        row.pack_start(label_widget, True, True, 0)
        row.pack_start(value_widget, False, False, 0)
        
        return row
    
    def create_switch_row(self, label, callback):
        """Create a switch row with label and toggle"""
        row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        
        label_widget = Gtk.Label(label=label)
        label_widget.set_xalign(0)
        label_widget.get_style_context().add_class("setting-label")
        
        switch = Gtk.Switch()
        switch.connect("notify::active", callback)
        
        row.pack_start(label_widget, True, True, 0)
        row.pack_start(switch, False, False, 0)
        
        return row

    # ==================================================================
    # Core Methods - Import these from original when needed
    # ==================================================================
    
    def load_theme(self):
        """Load and apply CSS theme (to be imported from original)"""
        # Placeholder - will delegate to original implementation
        pass
        
    def setup_indicator(self):
        """Setup system tray indicator (to be imported from original)"""
        # Placeholder - will delegate to original implementation
        pass
        
    def setup_notifications(self):
        """Setup desktop notifications (to be imported from original)"""
        # Placeholder - will delegate to original implementation
        pass
        
    def setup_keyboard_shortcuts(self):
        """Setup keyboard shortcuts (to be imported from original)"""
        # Placeholder - will delegate to original implementation
        pass
        
    def load_settings(self):
        """Load settings from config (to be imported from original)"""
        # Placeholder - will delegate to original implementation
        pass
        
    def check_first_run(self):
        """Check for first run and show wizard if needed (already implemented)"""
        # Placeholder - will delegate to P2 implementation
        pass

    # ==================================================================
    # Event Handlers - Import these from original when needed
    # ==================================================================
    
    def update_display(self):
        """Update display loop (to be imported from original)"""
        # Placeholder - will delegate to original implementation
        return True  # Keep the timer running
        
    def on_connection_state_changed(self, state):
        """Handle connection state changes (to be imported from original)"""
        # Placeholder - will delegate to original implementation
        pass
        
    def on_connection_error(self, error_message):
        """Handle connection errors (to be imported from original)"""
        # Placeholder - will delegate to original implementation  
        pass
        
    def on_error_recovery_needed(self, error_info):
        """Handle enhanced error recovery (already implemented)"""
        # Placeholder - will delegate to P2 implementation
        pass

    # ==================================================================
    # Panel Delegate Methods - Import these from original as needed
    # ==================================================================
    
    def on_connect_clicked(self, button):
        """Handle connect button (to be imported from original)"""
        # Placeholder - will delegate to original implementation
        pass
        
    def on_disconnect_clicked(self, button):
        """Handle disconnect button (to be imported from original)"""
        # Placeholder - will delegate to original implementation
        pass
        
    def on_settings_clicked(self, button):
        """Handle settings button (already implemented)"""
        # Placeholder - will delegate to P2 implementation
        pass

    # Additional delegate methods as needed...

# ==================================================================
# Compatibility Alias
# ==================================================================

# Keep the old class name for backward compatibility
PdaNetGUI = PdaNetMainWindow