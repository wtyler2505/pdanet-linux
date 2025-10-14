"""
Settings Dialog for PdaNet Linux
Provides GUI configuration for all application settings
"""

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib
from typing import Dict, Any, Optional
import json
from pathlib import Path

from config_manager import get_config
from logger import get_logger
from constants import *
from widgets.setting_widgets import (
    create_label_entry,
    create_label_spin,
    create_label_switch,
    create_label_combo,
    create_section_header,
    create_info_label
)


class SettingsDialog(Gtk.Dialog):
    """
    Professional settings dialog with tabbed interface
    Tabs: General, Network, Stealth, Advanced, Profiles
    """
    
    def __init__(self, parent_window):
        super().__init__(
            title="PdaNet Linux - Settings",
            parent=parent_window,
            flags=Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT
        )
        
        self.config = get_config()
        self.logger = get_logger()
        self.parent_window = parent_window
        
        # Store original values for cancel functionality
        self.original_values = self._capture_current_settings()
        
        # Track if any changes were made
        self.changes_made = False
        
        # Set dialog size
        self.set_default_size(700, 550)
        self.set_resizable(True)
        
        # Build UI
        self._build_ui()
        
        # Load current settings into widgets
        self._load_settings()
        
    def _capture_current_settings(self) -> Dict[str, Any]:
        """Capture current settings for cancel/restore"""
        return {
            # General
            'autostart': self.config.is_autostart_enabled(),
            'start_minimized': self.config.get('start_minimized', False),
            'enable_notifications': self.config.get('enable_notifications', True),
            'enable_data_warnings': self.config.get('enable_data_warnings', True),
            'data_warning_threshold_gb': self.config.get('data_warning_threshold_gb', 10),
            'update_interval_ms': self.config.get('update_interval_ms', GUI_UPDATE_INTERVAL_MS),
            'theme': self.config.get('theme', 'cyberpunk_dark'),
            
            # Network
            'proxy_ip': self.config.get('proxy_ip', PROXY_DEFAULT_IP),
            'proxy_port': self.config.get('proxy_port', PROXY_DEFAULT_PORT),
            'connection_timeout': self.config.get('connection_timeout', CONNECTION_TIMEOUT_SECONDS),
            'auto_reconnect': self.config.get('auto_reconnect', True),
            'reconnect_attempts': self.config.get('reconnect_attempts', RETRY_MAX_ATTEMPTS),
            'reconnect_delay': self.config.get('reconnect_delay', RECONNECT_DELAY_SECONDS),
            
            # Stealth
            'stealth_level': self.config.get('stealth_level', DEFAULT_STEALTH_LEVEL),
            'ttl_value': self.config.get('ttl_value', TTL_VALUE_PHONE_TRAFFIC),
            'block_ipv6': self.config.get('block_ipv6', True),
            'dns_leak_prevention': self.config.get('dns_leak_prevention', True),
            'custom_dns': self.config.get('custom_dns', ''),
            'traffic_shaping': self.config.get('traffic_shaping', True),
            
            # Advanced
            'log_level': self.config.get('log_level', LOG_LEVEL_INFO),
            'debug_mode': self.config.get('debug_mode', False),
            'performance_monitoring': self.config.get('performance_monitoring', False),
            'advanced_network_monitor': self.config.get('advanced_network_monitor', True),
            'intelligent_qos': self.config.get('intelligent_qos', True),
        }
    
    def _build_ui(self):
        """Build the settings dialog UI"""
        content_area = self.get_content_area()
        content_area.set_spacing(10)
        content_area.set_border_width(10)
        
        # Create notebook (tabbed interface)
        self.notebook = Gtk.Notebook()
        self.notebook.set_tab_pos(Gtk.PositionType.TOP)
        
        # Add tabs
        self.notebook.append_page(
            self._create_general_tab(),
            Gtk.Label(label="General")
        )
        self.notebook.append_page(
            self._create_network_tab(),
            Gtk.Label(label="Network")
        )
        self.notebook.append_page(
            self._create_stealth_tab(),
            Gtk.Label(label="Stealth")
        )
        self.notebook.append_page(
            self._create_advanced_tab(),
            Gtk.Label(label="Advanced")
        )
        self.notebook.append_page(
            self._create_profiles_tab(),
            Gtk.Label(label="Profiles")
        )
        
        content_area.pack_start(self.notebook, True, True, 0)
        
        # Add action buttons
        self.add_button("Reset to Defaults", Gtk.ResponseType.HELP)
        self.add_button("Cancel", Gtk.ResponseType.CANCEL)
        self.add_button("Apply", Gtk.ResponseType.APPLY)
        self.add_button("OK", Gtk.ResponseType.OK)
        
        # Connect button signals
        self.connect("response", self._on_response)
        
        # Connect change signals to track modifications
        self._connect_change_signals()
        
        self.show_all()
    
    def _create_general_tab(self) -> Gtk.Widget:
        """Create General settings tab"""
        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        box.set_border_width(20)
        
        # Startup section
        box.pack_start(create_section_header("Startup"), False, False, 0)
        
        grid = Gtk.Grid()
        grid.set_row_spacing(10)
        grid.set_column_spacing(10)
        row = 0
        
        # Auto-start on boot
        label, self.autostart_switch = create_label_switch(
            "Start on boot:",
            tooltip="Automatically start PdaNet Linux when you log in"
        )
        grid.attach(label, 0, row, 1, 1)
        grid.attach(self.autostart_switch, 1, row, 1, 1)
        row += 1
        
        # Start minimized
        label, self.start_minimized_switch = create_label_switch(
            "Start minimized to tray:",
            tooltip="Start in system tray without showing main window"
        )
        grid.attach(label, 0, row, 1, 1)
        grid.attach(self.start_minimized_switch, 1, row, 1, 1)
        row += 1
        
        box.pack_start(grid, False, False, 0)
        
        # Notifications section
        box.pack_start(create_section_header("Notifications"), False, False, 0)
        
        grid2 = Gtk.Grid()
        grid2.set_row_spacing(10)
        grid2.set_column_spacing(10)
        row = 0
        
        # Enable notifications
        label, self.notifications_switch = create_label_switch(
            "Show desktop notifications:",
            default_state=True,
            tooltip="Display notifications for connection events"
        )
        grid2.attach(label, 0, row, 1, 1)
        grid2.attach(self.notifications_switch, 1, row, 1, 1)
        row += 1
        
        box.pack_start(grid2, False, False, 0)
        
        # Data Usage section
        box.pack_start(create_section_header("Data Usage"), False, False, 0)
        
        grid3 = Gtk.Grid()
        grid3.set_row_spacing(10)
        grid3.set_column_spacing(10)
        row = 0
        
        # Enable data warnings
        label, self.data_warnings_switch = create_label_switch(
            "Enable data usage warnings:",
            default_state=True,
            tooltip="Alert when approaching data limits"
        )
        grid3.attach(label, 0, row, 1, 1)
        grid3.attach(self.data_warnings_switch, 1, row, 1, 1)
        row += 1
        
        # Warning threshold
        label, self.data_threshold_spin = create_label_spin(
            "Warning threshold (GB):",
            min_value=1,
            max_value=100,
            step=1,
            default_value=10,
            tooltip="Show warning when data usage exceeds this amount"
        )
        grid3.attach(label, 0, row, 1, 1)
        grid3.attach(self.data_threshold_spin, 1, row, 1, 1)
        row += 1
        
        box.pack_start(grid3, False, False, 0)
        
        # Interface section
        box.pack_start(create_section_header("Interface"), False, False, 0)
        
        grid4 = Gtk.Grid()
        grid4.set_row_spacing(10)
        grid4.set_column_spacing(10)
        row = 0
        
        # Update interval
        label, self.update_interval_spin = create_label_spin(
            "GUI update interval (ms):",
            min_value=500,
            max_value=5000,
            step=100,
            default_value=GUI_UPDATE_INTERVAL_MS,
            tooltip="How often to update statistics display (lower = more CPU usage)"
        )
        grid4.attach(label, 0, row, 1, 1)
        grid4.attach(self.update_interval_spin, 1, row, 1, 1)
        row += 1
        
        # Theme selection
        label, self.theme_combo = create_label_combo(
            "Theme:",
            options=[
                ("cyberpunk_dark", "Cyberpunk Dark (Default)"),
                ("cyberpunk_green", "Cyberpunk Green"),
                ("cyberpunk_blue", "Cyberpunk Blue"),
            ],
            default_id="cyberpunk_dark",
            tooltip="Visual theme (requires restart)"
        )
        grid4.attach(label, 0, row, 1, 1)
        grid4.attach(self.theme_combo, 1, row, 1, 1)
        row += 1
        
        box.pack_start(grid4, False, False, 0)
        
        scroll.add(box)
        return scroll
    
    def _create_network_tab(self) -> Gtk.Widget:
        """Create Network settings tab"""
        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        box.set_border_width(20)
        
        # Proxy section
        box.pack_start(create_section_header("Proxy Configuration"), False, False, 0)
        box.pack_start(
            create_info_label("PdaNet proxy running on your Android device"),
            False, False, 0
        )
        
        grid = Gtk.Grid()
        grid.set_row_spacing(10)
        grid.set_column_spacing(10)
        row = 0
        
        # Proxy IP
        label, self.proxy_ip_entry = create_label_entry(
            "Proxy IP address:",
            placeholder="192.168.49.1",
            default_value=PROXY_DEFAULT_IP,
            tooltip="IP address of PdaNet proxy on Android device"
        )
        grid.attach(label, 0, row, 1, 1)
        grid.attach(self.proxy_ip_entry, 1, row, 1, 1)
        row += 1
        
        # Proxy Port
        label, self.proxy_port_spin = create_label_spin(
            "Proxy port:",
            min_value=PORT_MIN,
            max_value=PORT_MAX,
            step=1,
            default_value=PROXY_DEFAULT_PORT,
            tooltip="Port number of PdaNet proxy"
        )
        grid.attach(label, 0, row, 1, 1)
        grid.attach(self.proxy_port_spin, 1, row, 1, 1)
        row += 1
        
        box.pack_start(grid, False, False, 0)
        
        # Connection section
        box.pack_start(create_section_header("Connection Behavior"), False, False, 0)
        
        grid2 = Gtk.Grid()
        grid2.set_row_spacing(10)
        grid2.set_column_spacing(10)
        row = 0
        
        # Connection timeout
        label, self.timeout_spin = create_label_spin(
            "Connection timeout (seconds):",
            min_value=5,
            max_value=300,
            step=5,
            default_value=CONNECTION_TIMEOUT_SECONDS,
            tooltip="How long to wait before declaring connection failed"
        )
        grid2.attach(label, 0, row, 1, 1)
        grid2.attach(self.timeout_spin, 1, row, 1, 1)
        row += 1
        
        # Auto-reconnect
        label, self.auto_reconnect_switch = create_label_switch(
            "Enable auto-reconnect:",
            default_state=True,
            tooltip="Automatically reconnect if connection is lost"
        )
        grid2.attach(label, 0, row, 1, 1)
        grid2.attach(self.auto_reconnect_switch, 1, row, 1, 1)
        row += 1
        
        # Reconnect attempts
        label, self.reconnect_attempts_spin = create_label_spin(
            "Max reconnect attempts:",
            min_value=1,
            max_value=10,
            step=1,
            default_value=RETRY_MAX_ATTEMPTS,
            tooltip="Number of times to retry connection before giving up"
        )
        grid2.attach(label, 0, row, 1, 1)
        grid2.attach(self.reconnect_attempts_spin, 1, row, 1, 1)
        row += 1
        
        # Reconnect delay
        label, self.reconnect_delay_spin = create_label_spin(
            "Reconnect delay (seconds):",
            min_value=1,
            max_value=60,
            step=1,
            default_value=RECONNECT_DELAY_SECONDS,
            tooltip="Wait time between reconnection attempts"
        )
        grid2.attach(label, 0, row, 1, 1)
        grid2.attach(self.reconnect_delay_spin, 1, row, 1, 1)
        row += 1
        
        box.pack_start(grid2, False, False, 0)
        
        scroll.add(box)
        return scroll
    
    def _create_stealth_tab(self) -> Gtk.Widget:
        """Create Stealth settings tab"""
        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        box.set_border_width(20)
        
        # Stealth level section
        box.pack_start(create_section_header("Carrier Detection Bypass"), False, False, 0)
        box.pack_start(
            create_info_label(
                "Configure how aggressively to hide tethering from carrier detection. "
                "Higher levels provide better protection but may affect performance."
            ),
            False, False, 0
        )
        
        grid = Gtk.Grid()
        grid.set_row_spacing(10)
        grid.set_column_spacing(10)
        row = 0
        
        # Stealth level
        label, self.stealth_level_combo = create_label_combo(
            "Stealth level:",
            options=[
                ("1", "Level 1 - Basic (TTL modification only)"),
                ("2", "Level 2 - Standard (TTL + IPv6 + DNS)"),
                ("3", "Level 3 - Aggressive (All 6 bypass layers)"),
            ],
            default_id="3",
            tooltip="Choose bypass intensity"
        )
        grid.attach(label, 0, row, 1, 1)
        grid.attach(self.stealth_level_combo, 1, row, 1, 1)
        row += 1
        
        box.pack_start(grid, False, False, 0)
        
        # TTL section
        box.pack_start(create_section_header("TTL Configuration"), False, False, 0)
        
        grid2 = Gtk.Grid()
        grid2.set_row_spacing(10)
        grid2.set_column_spacing(10)
        row = 0
        
        # Custom TTL value
        label, self.ttl_spin = create_label_spin(
            "Custom TTL value:",
            min_value=1,
            max_value=255,
            step=1,
            default_value=TTL_VALUE_PHONE_TRAFFIC,
            tooltip=f"TTL value to use (default {TTL_VALUE_PHONE_TRAFFIC} mimics mobile device)"
        )
        grid2.attach(label, 0, row, 1, 1)
        grid2.attach(self.ttl_spin, 1, row, 1, 1)
        row += 1
        
        box.pack_start(grid2, False, False, 0)
        
        # IPv6 section
        box.pack_start(create_section_header("IPv6 Leak Prevention"), False, False, 0)
        
        grid3 = Gtk.Grid()
        grid3.set_row_spacing(10)
        grid3.set_column_spacing(10)
        row = 0
        
        # Block IPv6
        label, self.block_ipv6_switch = create_label_switch(
            "Block IPv6 completely:",
            default_state=True,
            tooltip="Prevent IPv6 leaks that could bypass tethering detection"
        )
        grid3.attach(label, 0, row, 1, 1)
        grid3.attach(self.block_ipv6_switch, 1, row, 1, 1)
        row += 1
        
        box.pack_start(grid3, False, False, 0)
        
        # DNS section
        box.pack_start(create_section_header("DNS Configuration"), False, False, 0)
        
        grid4 = Gtk.Grid()
        grid4.set_row_spacing(10)
        grid4.set_column_spacing(10)
        row = 0
        
        # DNS leak prevention
        label, self.dns_leak_prevention_switch = create_label_switch(
            "Enable DNS leak prevention:",
            default_state=True,
            tooltip="Route all DNS queries through proxy"
        )
        grid4.attach(label, 0, row, 1, 1)
        grid4.attach(self.dns_leak_prevention_switch, 1, row, 1, 1)
        row += 1
        
        # Custom DNS servers
        label, self.custom_dns_entry = create_label_entry(
            "Custom DNS servers:",
            placeholder="1.1.1.1, 8.8.8.8",
            tooltip="Comma-separated list of DNS servers (optional)"
        )
        grid4.attach(label, 0, row, 1, 1)
        grid4.attach(self.custom_dns_entry, 1, row, 1, 1)
        row += 1
        
        box.pack_start(grid4, False, False, 0)
        
        # Traffic shaping section
        box.pack_start(create_section_header("Traffic Shaping"), False, False, 0)
        
        grid5 = Gtk.Grid()
        grid5.set_row_spacing(10)
        grid5.set_column_spacing(10)
        row = 0
        
        # Traffic shaping
        label, self.traffic_shaping_switch = create_label_switch(
            "Enable traffic shaping:",
            default_state=True,
            tooltip="Make traffic patterns look more like mobile device"
        )
        grid5.attach(label, 0, row, 1, 1)
        grid5.attach(self.traffic_shaping_switch, 1, row, 1, 1)
        row += 1
        
        box.pack_start(grid5, False, False, 0)
        
        scroll.add(box)
        return scroll
    
    def _create_advanced_tab(self) -> Gtk.Widget:
        """Create Advanced settings tab"""
        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        box.set_border_width(20)
        
        # Logging section
        box.pack_start(create_section_header("Logging"), False, False, 0)
        
        grid = Gtk.Grid()
        grid.set_row_spacing(10)
        grid.set_column_spacing(10)
        row = 0
        
        # Log level
        label, self.log_level_combo = create_label_combo(
            "Log level:",
            options=[
                (LOG_LEVEL_DEBUG, "DEBUG - Verbose logging"),
                (LOG_LEVEL_INFO, "INFO - Normal logging"),
                (LOG_LEVEL_WARNING, "WARNING - Warnings and errors only"),
                (LOG_LEVEL_ERROR, "ERROR - Errors only"),
            ],
            default_id=LOG_LEVEL_INFO,
            tooltip="Amount of detail in log messages"
        )
        grid.attach(label, 0, row, 1, 1)
        grid.attach(self.log_level_combo, 1, row, 1, 1)
        row += 1
        
        # Debug mode
        label, self.debug_mode_switch = create_label_switch(
            "Enable debug mode:",
            tooltip="Enable additional debugging features (may affect performance)"
        )
        grid.attach(label, 0, row, 1, 1)
        grid.attach(self.debug_mode_switch, 1, row, 1, 1)
        row += 1
        
        box.pack_start(grid, False, False, 0)
        
        # Monitoring section
        box.pack_start(create_section_header("Monitoring"), False, False, 0)
        
        grid2 = Gtk.Grid()
        grid2.set_row_spacing(10)
        grid2.set_column_spacing(10)
        row = 0
        
        # Performance monitoring
        label, self.perf_monitoring_switch = create_label_switch(
            "Enable performance monitoring:",
            tooltip="Track memory usage and performance metrics"
        )
        grid2.attach(label, 0, row, 1, 1)
        grid2.attach(self.perf_monitoring_switch, 1, row, 1, 1)
        row += 1
        
        # Advanced network monitoring
        label, self.adv_monitoring_switch = create_label_switch(
            "Enable advanced network monitoring:",
            default_state=True,
            tooltip="Real-time traffic analysis and security event detection"
        )
        grid2.attach(label, 0, row, 1, 1)
        grid2.attach(self.adv_monitoring_switch, 1, row, 1, 1)
        row += 1
        
        # Intelligent QoS
        label, self.qos_switch = create_label_switch(
            "Enable intelligent QoS:",
            default_state=True,
            tooltip="Automatic bandwidth management and traffic prioritization"
        )
        grid2.attach(label, 0, row, 1, 1)
        grid2.attach(self.qos_switch, 1, row, 1, 1)
        row += 1
        
        box.pack_start(grid2, False, False, 0)
        
        scroll.add(box)
        return scroll
    
    def _create_profiles_tab(self) -> Gtk.Widget:
        """Create Profiles management tab"""
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        box.set_border_width(20)
        
        # Info label
        info = create_info_label(
            "Connection profiles allow you to save and quickly switch between "
            "different network configurations. Coming in next update!"
        )
        box.pack_start(info, False, False, 0)
        
        # Profile list
        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        
        self.profile_store = Gtk.ListStore(str, str, str)  # name, mode, ssid
        self.profile_treeview = Gtk.TreeView(model=self.profile_store)
        
        # Add columns
        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("Profile Name", renderer, text=0)
        column.set_expand(True)
        self.profile_treeview.append_column(column)
        
        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("Mode", renderer, text=1)
        self.profile_treeview.append_column(column)
        
        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("SSID", renderer, text=2)
        self.profile_treeview.append_column(column)
        
        scroll.add(self.profile_treeview)
        box.pack_start(scroll, True, True, 0)
        
        # Buttons
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        
        new_btn = Gtk.Button(label="New Profile")
        new_btn.set_sensitive(False)  # TODO: Implement
        button_box.pack_start(new_btn, True, True, 0)
        
        edit_btn = Gtk.Button(label="Edit")
        edit_btn.set_sensitive(False)  # TODO: Implement
        button_box.pack_start(edit_btn, True, True, 0)
        
        delete_btn = Gtk.Button(label="Delete")
        delete_btn.set_sensitive(False)  # TODO: Implement
        button_box.pack_start(delete_btn, True, True, 0)
        
        import_btn = Gtk.Button(label="Import")
        import_btn.set_sensitive(False)  # TODO: Implement
        button_box.pack_start(import_btn, True, True, 0)
        
        export_btn = Gtk.Button(label="Export")
        export_btn.set_sensitive(False)  # TODO: Implement
        button_box.pack_start(export_btn, True, True, 0)
        
        box.pack_start(button_box, False, False, 0)
        
        return box
    
    def _load_settings(self):
        """Load current settings into widgets"""
        # General tab
        self.autostart_switch.set_active(self.original_values['autostart'])
        self.start_minimized_switch.set_active(self.original_values['start_minimized'])
        self.notifications_switch.set_active(self.original_values['enable_notifications'])
        self.data_warnings_switch.set_active(self.original_values['enable_data_warnings'])
        self.data_threshold_spin.set_value(self.original_values['data_warning_threshold_gb'])
        self.update_interval_spin.set_value(self.original_values['update_interval_ms'])
        self.theme_combo.set_active_id(self.original_values['theme'])
        
        # Network tab
        self.proxy_ip_entry.set_text(self.original_values['proxy_ip'])
        self.proxy_port_spin.set_value(self.original_values['proxy_port'])
        self.timeout_spin.set_value(self.original_values['connection_timeout'])
        self.auto_reconnect_switch.set_active(self.original_values['auto_reconnect'])
        self.reconnect_attempts_spin.set_value(self.original_values['reconnect_attempts'])
        self.reconnect_delay_spin.set_value(self.original_values['reconnect_delay'])
        
        # Stealth tab
        self.stealth_level_combo.set_active_id(str(self.original_values['stealth_level']))
        self.ttl_spin.set_value(self.original_values['ttl_value'])
        self.block_ipv6_switch.set_active(self.original_values['block_ipv6'])
        self.dns_leak_prevention_switch.set_active(self.original_values['dns_leak_prevention'])
        self.custom_dns_entry.set_text(self.original_values['custom_dns'])
        self.traffic_shaping_switch.set_active(self.original_values['traffic_shaping'])
        
        # Advanced tab
        self.log_level_combo.set_active_id(self.original_values['log_level'])
        self.debug_mode_switch.set_active(self.original_values['debug_mode'])
        self.perf_monitoring_switch.set_active(self.original_values['performance_monitoring'])
        self.adv_monitoring_switch.set_active(self.original_values['advanced_network_monitor'])
        self.qos_switch.set_active(self.original_values['intelligent_qos'])
        
        # Load profiles
        self._load_profiles()
    
    def _save_settings(self):
        """Save settings from widgets to config"""
        try:
            # General tab
            if self.autostart_switch.get_active():
                self.config.enable_autostart()
            else:
                self.config.disable_autostart()
            
            self.config.set('start_minimized', self.start_minimized_switch.get_active())
            self.config.set('enable_notifications', self.notifications_switch.get_active())
            self.config.set('enable_data_warnings', self.data_warnings_switch.get_active())
            self.config.set('data_warning_threshold_gb', self.data_threshold_spin.get_value_as_int())
            self.config.set('update_interval_ms', self.update_interval_spin.get_value_as_int())
            self.config.set('theme', self.theme_combo.get_active_id())
            
            # Network tab
            self.config.set('proxy_ip', self.proxy_ip_entry.get_text())
            self.config.set('proxy_port', self.proxy_port_spin.get_value_as_int())
            self.config.set('connection_timeout', self.timeout_spin.get_value_as_int())
            self.config.set('auto_reconnect', self.auto_reconnect_switch.get_active())
            self.config.set('reconnect_attempts', self.reconnect_attempts_spin.get_value_as_int())
            self.config.set('reconnect_delay', self.reconnect_delay_spin.get_value_as_int())
            
            # Stealth tab
            self.config.set('stealth_level', int(self.stealth_level_combo.get_active_id()))
            self.config.set('ttl_value', self.ttl_spin.get_value_as_int())
            self.config.set('block_ipv6', self.block_ipv6_switch.get_active())
            self.config.set('dns_leak_prevention', self.dns_leak_prevention_switch.get_active())
            self.config.set('custom_dns', self.custom_dns_entry.get_text())
            self.config.set('traffic_shaping', self.traffic_shaping_switch.get_active())
            
            # Advanced tab
            self.config.set('log_level', self.log_level_combo.get_active_id())
            self.config.set('debug_mode', self.debug_mode_switch.get_active())
            self.config.set('performance_monitoring', self.perf_monitoring_switch.get_active())
            self.config.set('advanced_network_monitor', self.adv_monitoring_switch.get_active())
            self.config.set('intelligent_qos', self.qos_switch.get_active())
            
            self.logger.info("Settings saved successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to save settings: {e}")
            self._show_error_dialog("Failed to save settings", str(e))
            return False
    
    def _apply_settings(self):
        """Apply settings that take effect immediately"""
        # Notify parent window to reload settings
        if hasattr(self.parent_window, 'reload_settings'):
            self.parent_window.reload_settings()
    
    def _restore_original_settings(self):
        """Restore settings to original values (for cancel)"""
        self._load_settings()
    
    def _reset_to_defaults(self):
        """Reset all settings to application defaults"""
        dialog = Gtk.MessageDialog(
            transient_for=self,
            flags=0,
            message_type=Gtk.MessageType.QUESTION,
            buttons=Gtk.ButtonsType.YES_NO,
            text="Reset to Defaults?"
        )
        dialog.format_secondary_text(
            "This will reset all settings to their default values. "
            "Are you sure you want to continue?"
        )
        
        response = dialog.run()
        dialog.destroy()
        
        if response == Gtk.ResponseType.YES:
            # Reset widgets to defaults
            self._load_default_settings()
            self.changes_made = True
    
    def _load_default_settings(self):
        """Load default settings into widgets"""
        # General
        self.autostart_switch.set_active(False)
        self.start_minimized_switch.set_active(False)
        self.notifications_switch.set_active(True)
        self.data_warnings_switch.set_active(True)
        self.data_threshold_spin.set_value(10)
        self.update_interval_spin.set_value(GUI_UPDATE_INTERVAL_MS)
        self.theme_combo.set_active_id("cyberpunk_dark")
        
        # Network
        self.proxy_ip_entry.set_text(PROXY_DEFAULT_IP)
        self.proxy_port_spin.set_value(PROXY_DEFAULT_PORT)
        self.timeout_spin.set_value(CONNECTION_TIMEOUT_SECONDS)
        self.auto_reconnect_switch.set_active(True)
        self.reconnect_attempts_spin.set_value(RETRY_MAX_ATTEMPTS)
        self.reconnect_delay_spin.set_value(RECONNECT_DELAY_SECONDS)
        
        # Stealth
        self.stealth_level_combo.set_active_id(str(DEFAULT_STEALTH_LEVEL))
        self.ttl_spin.set_value(TTL_VALUE_PHONE_TRAFFIC)
        self.block_ipv6_switch.set_active(True)
        self.dns_leak_prevention_switch.set_active(True)
        self.custom_dns_entry.set_text("")
        self.traffic_shaping_switch.set_active(True)
        
        # Advanced
        self.log_level_combo.set_active_id(LOG_LEVEL_INFO)
        self.debug_mode_switch.set_active(False)
        self.perf_monitoring_switch.set_active(False)
        self.adv_monitoring_switch.set_active(True)
        self.qos_switch.set_active(True)
    
    def _load_profiles(self):
        """Load connection profiles into tree view"""
        self.profile_store.clear()
        
        profiles = self.config.get_all_profiles()
        for profile_id, profile in profiles.items():
            self.profile_store.append([
                profile.get('name', 'Unnamed'),
                profile.get('mode', 'Unknown'),
                profile.get('ssid', '-')
            ])
    
    def _connect_change_signals(self):
        """Connect change signals to track if user made modifications"""
        # This is a simplified version - in production, connect all widgets
        pass
    
    def _on_response(self, dialog, response_id):
        """Handle dialog button responses"""
        if response_id == Gtk.ResponseType.OK:
            if self._save_settings():
                self._apply_settings()
                dialog.destroy()
        elif response_id == Gtk.ResponseType.APPLY:
            if self._save_settings():
                self._apply_settings()
        elif response_id == Gtk.ResponseType.CANCEL:
            dialog.destroy()
        elif response_id == Gtk.ResponseType.HELP:
            self._reset_to_defaults()
    
    def _show_error_dialog(self, title: str, message: str):
        """Show error dialog"""
        dialog = Gtk.MessageDialog(
            transient_for=self,
            flags=0,
            message_type=Gtk.MessageType.ERROR,
            buttons=Gtk.ButtonsType.OK,
            text=title
        )
        dialog.format_secondary_text(message)
        dialog.run()
        dialog.destroy()
