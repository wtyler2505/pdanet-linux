"""
Operations Panel for PdaNet Linux GUI
Connection controls, mode selection, profiles, and action buttons
"""

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk


class OperationsPanel:
    """
    Operations and control panel
    Contains connection buttons, mode selection, profiles, and settings
    """
    
    def __init__(self, parent_window):
        """Initialize operations panel"""
        self.parent = parent_window
        self.panel = None
        
        # Controls (will be created by build_panel)
        self.mode_combo = None
        self.profiles_combo = None
        self.connect_button = None
        self.disconnect_button = None
        self.reconnect_switch = None
        self.autostart_switch = None
        self.stealth_status = None
    
    def build_panel(self):
        """Build controls panel"""
        if self.panel:
            return self.panel
            
        panel = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
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

        # Quick-switch saved profiles
        profiles_label = Gtk.Label(label="SAVED PROFILES")
        profiles_label.get_style_context().add_class("metric-label")
        profiles_label.set_xalign(0)
        panel.pack_start(profiles_label, False, False, 2)

        self.profiles_combo = Gtk.ComboBoxText()
        self.profiles_combo.append("none", "-- Select Profile --")
        self.profiles_combo.set_active(0)
        self.profiles_combo.connect("changed", self.on_profile_selected)
        panel.pack_start(self.profiles_combo, False, False, 0)
        
        # Refresh profiles button
        refresh_profiles_btn = Gtk.Button(label="🔄 Refresh")
        refresh_profiles_btn.connect("clicked", lambda b: self.load_saved_profiles())
        panel.pack_start(refresh_profiles_btn, False, False, 0)

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
        reconnect_box = self.parent.create_switch_row("AUTO-RECONNECT", self.on_auto_reconnect_toggled)
        self.reconnect_switch = reconnect_box.get_children()[1]
        options_box.pack_start(reconnect_box, False, False, 0)

        # Auto-start
        autostart_box = self.parent.create_switch_row("START ON BOOT", self.on_autostart_toggled)
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

        self.panel = panel
        return panel
    
    def on_profile_selected(self, combo):
        """Handle profile selection"""
        # Delegate to parent
        if hasattr(self.parent, 'on_profile_selected'):
            self.parent.on_profile_selected(combo)
    
    def load_saved_profiles(self):
        """Load saved profiles into combo"""
        # Delegate to parent
        if hasattr(self.parent, 'load_saved_profiles'):
            self.parent.load_saved_profiles()
    
    def on_connect_clicked(self, button):
        """Handle connect button"""
        # Delegate to parent
        if hasattr(self.parent, 'on_connect_clicked'):
            self.parent.on_connect_clicked(button)
    
    def on_disconnect_clicked(self, button):
        """Handle disconnect button"""
        # Delegate to parent
        if hasattr(self.parent, 'on_disconnect_clicked'):
            self.parent.on_disconnect_clicked(button)
    
    def on_auto_reconnect_toggled(self, switch, state):
        """Handle auto-reconnect toggle"""
        # Delegate to parent
        if hasattr(self.parent, 'on_auto_reconnect_toggled'):
            self.parent.on_auto_reconnect_toggled(switch, state)
    
    def on_autostart_toggled(self, switch, state):
        """Handle autostart toggle"""
        # Delegate to parent
        if hasattr(self.parent, 'on_autostart_toggled'):
            self.parent.on_autostart_toggled(switch, state)
    
    def on_history_clicked(self, button):
        """Handle history button"""
        # Delegate to parent
        if hasattr(self.parent, 'on_history_clicked'):
            self.parent.on_history_clicked(button)
    
    def on_speedtest_clicked(self, button):
        """Handle speed test button"""
        # Delegate to parent
        if hasattr(self.parent, 'on_speedtest_clicked'):
            self.parent.on_speedtest_clicked(button)
    
    def on_settings_clicked(self, button):
        """Handle settings button"""
        # Delegate to parent
        if hasattr(self.parent, 'on_settings_clicked'):
            self.parent.on_settings_clicked(button)
    
    def update_button_states(self, connected):
        """Update button states based on connection status"""
        if not self.panel:
            return
            
        self.connect_button.set_sensitive(not connected)
        self.disconnect_button.set_sensitive(connected)
    
    def update_stealth_status(self, status_text):
        """Update stealth mode status display"""
        if self.stealth_status:
            self.stealth_status.set_text(status_text)
    
    def get_widget(self):
        """Get the panel widget"""
        if not self.panel:
            self.build_panel()
        return self.panel