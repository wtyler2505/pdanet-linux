# 🚀 PHASE 1 IMPLEMENTATION PLAN: Critical UX Features

## Overview
**Timeline:** 2 weeks (88 hours)  
**Priority:** CRITICAL  
**Impact:** Transforms app from "power user tool" to "user-friendly application"  

---

## 🎯 DELIVERABLES

### 1. Settings Dialog (40 hours)
### 2. First-Run Wizard (16 hours)
### 3. Error Recovery UI (16 hours)
### 4. Data Usage Dashboard (16 hours)

---

## 📝 DETAILED IMPLEMENTATION GUIDE

## 1. SETTINGS DIALOG (40 hours)

### 1.1 File Structure
```
src/
├── settings_dialog.py          # Main dialog (800 lines)
├── widgets/
│   ├── __init__.py
│   ├── setting_widgets.py      # Reusable setting widgets (400 lines)
│   └── profile_editor.py       # Profile management UI (300 lines)
tests/
└── test_settings_dialog.py     # Unit tests (200 lines)
```

### 1.2 Settings Dialog Architecture

```python
# src/settings_dialog.py

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib
from typing import Dict, Any
from config_manager import get_config
from logger import get_logger

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
        
        # Store original values for cancel
        self.original_values = self._capture_current_settings()
        
        # Set dialog size
        self.set_default_size(800, 600)
        
        # Build UI
        self._build_ui()
        
        # Load current settings
        self._load_settings()
        
    def _build_ui(self):
        """Build the settings dialog UI"""
        content_area = self.get_content_area()
        content_area.set_spacing(10)
        content_area.set_border_width(10)
        
        # Create notebook (tabbed interface)
        self.notebook = Gtk.Notebook()
        self.notebook.set_tab_pos(Gtk.PositionType.LEFT)
        
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
        
        self.show_all()
    
    def _create_general_tab(self) -> Gtk.Widget:
        """Create General settings tab"""
        grid = Gtk.Grid()
        grid.set_row_spacing(10)
        grid.set_column_spacing(10)
        grid.set_border_width(20)
        
        row = 0
        
        # Auto-start on boot
        label = Gtk.Label(label="Start on boot:")
        label.set_halign(Gtk.Align.START)
        self.autostart_switch = Gtk.Switch()
        grid.attach(label, 0, row, 1, 1)
        grid.attach(self.autostart_switch, 1, row, 1, 1)
        row += 1
        
        # Start minimized
        label = Gtk.Label(label="Start minimized to tray:")
        label.set_halign(Gtk.Align.START)
        self.start_minimized_switch = Gtk.Switch()
        grid.attach(label, 0, row, 1, 1)
        grid.attach(self.start_minimized_switch, 1, row, 1, 1)
        row += 1
        
        # Enable notifications
        label = Gtk.Label(label="Show desktop notifications:")
        label.set_halign(Gtk.Align.START)
        self.notifications_switch = Gtk.Switch()
        grid.attach(label, 0, row, 1, 1)
        grid.attach(self.notifications_switch, 1, row, 1, 1)
        row += 1
        
        # Enable data usage warnings
        label = Gtk.Label(label="Enable data usage warnings:")
        label.set_halign(Gtk.Align.START)
        self.data_warnings_switch = Gtk.Switch()
        grid.attach(label, 0, row, 1, 1)
        grid.attach(self.data_warnings_switch, 1, row, 1, 1)
        row += 1
        
        # Data warning threshold
        label = Gtk.Label(label="Warning threshold (GB):")
        label.set_halign(Gtk.Align.START)
        adjustment = Gtk.Adjustment(value=10, lower=1, upper=100, step_increment=1)
        self.data_threshold_spin = Gtk.SpinButton(adjustment=adjustment)
        grid.attach(label, 0, row, 1, 1)
        grid.attach(self.data_threshold_spin, 1, row, 1, 1)
        row += 1
        
        # Update interval
        label = Gtk.Label(label="GUI update interval (ms):")
        label.set_halign(Gtk.Align.START)
        adjustment = Gtk.Adjustment(value=1000, lower=500, upper=5000, step_increment=100)
        self.update_interval_spin = Gtk.SpinButton(adjustment=adjustment)
        grid.attach(label, 0, row, 1, 1)
        grid.attach(self.update_interval_spin, 1, row, 1, 1)
        row += 1
        
        # Theme selection
        label = Gtk.Label(label="Theme:")
        label.set_halign(Gtk.Align.START)
        self.theme_combo = Gtk.ComboBoxText()
        self.theme_combo.append("cyberpunk_dark", "Cyberpunk Dark (Default)")
        self.theme_combo.append("cyberpunk_green", "Cyberpunk Green")
        self.theme_combo.append("cyberpunk_blue", "Cyberpunk Blue")
        grid.attach(label, 0, row, 1, 1)
        grid.attach(self.theme_combo, 1, row, 1, 1)
        row += 1
        
        return grid
    
    def _create_network_tab(self) -> Gtk.Widget:
        """Create Network settings tab"""
        grid = Gtk.Grid()
        grid.set_row_spacing(10)
        grid.set_column_spacing(10)
        grid.set_border_width(20)
        
        row = 0
        
        # Proxy IP
        label = Gtk.Label(label="Proxy IP address:")
        label.set_halign(Gtk.Align.START)
        self.proxy_ip_entry = Gtk.Entry()
        self.proxy_ip_entry.set_placeholder_text("192.168.49.1")
        grid.attach(label, 0, row, 1, 1)
        grid.attach(self.proxy_ip_entry, 1, row, 1, 1)
        row += 1
        
        # Proxy Port
        label = Gtk.Label(label="Proxy port:")
        label.set_halign(Gtk.Align.START)
        adjustment = Gtk.Adjustment(value=8000, lower=1, upper=65535, step_increment=1)
        self.proxy_port_spin = Gtk.SpinButton(adjustment=adjustment)
        grid.attach(label, 0, row, 1, 1)
        grid.attach(self.proxy_port_spin, 1, row, 1, 1)
        row += 1
        
        # Connection timeout
        label = Gtk.Label(label="Connection timeout (seconds):")
        label.set_halign(Gtk.Align.START)
        adjustment = Gtk.Adjustment(value=30, lower=5, upper=300, step_increment=5)
        self.timeout_spin = Gtk.SpinButton(adjustment=adjustment)
        grid.attach(label, 0, row, 1, 1)
        grid.attach(self.timeout_spin, 1, row, 1, 1)
        row += 1
        
        # Auto-reconnect
        label = Gtk.Label(label="Enable auto-reconnect:")
        label.set_halign(Gtk.Align.START)
        self.auto_reconnect_switch = Gtk.Switch()
        grid.attach(label, 0, row, 1, 1)
        grid.attach(self.auto_reconnect_switch, 1, row, 1, 1)
        row += 1
        
        # Reconnect attempts
        label = Gtk.Label(label="Max reconnect attempts:")
        label.set_halign(Gtk.Align.START)
        adjustment = Gtk.Adjustment(value=3, lower=1, upper=10, step_increment=1)
        self.reconnect_attempts_spin = Gtk.SpinButton(adjustment=adjustment)
        grid.attach(label, 0, row, 1, 1)
        grid.attach(self.reconnect_attempts_spin, 1, row, 1, 1)
        row += 1
        
        # Reconnect delay
        label = Gtk.Label(label="Reconnect delay (seconds):")
        label.set_halign(Gtk.Align.START)
        adjustment = Gtk.Adjustment(value=5, lower=1, upper=60, step_increment=1)
        self.reconnect_delay_spin = Gtk.SpinButton(adjustment=adjustment)
        grid.attach(label, 0, row, 1, 1)
        grid.attach(self.reconnect_delay_spin, 1, row, 1, 1)
        row += 1
        
        return grid
    
    def _create_stealth_tab(self) -> Gtk.Widget:
        """Create Stealth settings tab"""
        grid = Gtk.Grid()
        grid.set_row_spacing(10)
        grid.set_column_spacing(10)
        grid.set_border_width(20)
        
        row = 0
        
        # Stealth level
        label = Gtk.Label(label="Stealth level:")
        label.set_halign(Gtk.Align.START)
        self.stealth_level_combo = Gtk.ComboBoxText()
        self.stealth_level_combo.append("1", "Level 1 - Basic (TTL only)")
        self.stealth_level_combo.append("2", "Level 2 - Standard (TTL + IPv6 + DNS)")
        self.stealth_level_combo.append("3", "Level 3 - Aggressive (All 6 layers)")
        grid.attach(label, 0, row, 1, 1)
        grid.attach(self.stealth_level_combo, 1, row, 1, 1)
        row += 1
        
        # Custom TTL value
        label = Gtk.Label(label="Custom TTL value:")
        label.set_halign(Gtk.Align.START)
        adjustment = Gtk.Adjustment(value=65, lower=1, upper=255, step_increment=1)
        self.ttl_spin = Gtk.SpinButton(adjustment=adjustment)
        grid.attach(label, 0, row, 1, 1)
        grid.attach(self.ttl_spin, 1, row, 1, 1)
        row += 1
        
        # Enable IPv6 blocking
        label = Gtk.Label(label="Block IPv6 completely:")
        label.set_halign(Gtk.Align.START)
        self.block_ipv6_switch = Gtk.Switch()
        grid.attach(label, 0, row, 1, 1)
        grid.attach(self.block_ipv6_switch, 1, row, 1, 1)
        row += 1
        
        # DNS leak prevention
        label = Gtk.Label(label="Enable DNS leak prevention:")
        label.set_halign(Gtk.Align.START)
        self.dns_leak_prevention_switch = Gtk.Switch()
        grid.attach(label, 0, row, 1, 1)
        grid.attach(self.dns_leak_prevention_switch, 1, row, 1, 1)
        row += 1
        
        # Custom DNS servers
        label = Gtk.Label(label="Custom DNS servers:")
        label.set_halign(Gtk.Align.START)
        self.custom_dns_entry = Gtk.Entry()
        self.custom_dns_entry.set_placeholder_text("1.1.1.1, 8.8.8.8")
        grid.attach(label, 0, row, 1, 1)
        grid.attach(self.custom_dns_entry, 1, row, 1, 1)
        row += 1
        
        # Traffic shaping
        label = Gtk.Label(label="Enable traffic shaping:")
        label.set_halign(Gtk.Align.START)
        self.traffic_shaping_switch = Gtk.Switch()
        grid.attach(label, 0, row, 1, 1)
        grid.attach(self.traffic_shaping_switch, 1, row, 1, 1)
        row += 1
        
        return grid
    
    def _create_advanced_tab(self) -> Gtk.Widget:
        """Create Advanced settings tab"""
        grid = Gtk.Grid()
        grid.set_row_spacing(10)
        grid.set_column_spacing(10)
        grid.set_border_width(20)
        
        row = 0
        
        # Log level
        label = Gtk.Label(label="Log level:")
        label.set_halign(Gtk.Align.START)
        self.log_level_combo = Gtk.ComboBoxText()
        self.log_level_combo.append("DEBUG", "DEBUG - Verbose logging")
        self.log_level_combo.append("INFO", "INFO - Normal logging")
        self.log_level_combo.append("WARNING", "WARNING - Warnings and errors only")
        self.log_level_combo.append("ERROR", "ERROR - Errors only")
        grid.attach(label, 0, row, 1, 1)
        grid.attach(self.log_level_combo, 1, row, 1, 1)
        row += 1
        
        # Enable debug mode
        label = Gtk.Label(label="Enable debug mode:")
        label.set_halign(Gtk.Align.START)
        self.debug_mode_switch = Gtk.Switch()
        grid.attach(label, 0, row, 1, 1)
        grid.attach(self.debug_mode_switch, 1, row, 1, 1)
        row += 1
        
        # Performance monitoring
        label = Gtk.Label(label="Enable performance monitoring:")
        label.set_halign(Gtk.Align.START)
        self.perf_monitoring_switch = Gtk.Switch()
        grid.attach(label, 0, row, 1, 1)
        grid.attach(self.perf_monitoring_switch, 1, row, 1, 1)
        row += 1
        
        # Advanced network monitoring
        label = Gtk.Label(label="Enable advanced network monitoring:")
        label.set_halign(Gtk.Align.START)
        self.adv_monitoring_switch = Gtk.Switch()
        grid.attach(label, 0, row, 1, 1)
        grid.attach(self.adv_monitoring_switch, 1, row, 1, 1)
        row += 1
        
        # Intelligent QoS
        label = Gtk.Label(label="Enable intelligent QoS:")
        label.set_halign(Gtk.Align.START)
        self.qos_switch = Gtk.Switch()
        grid.attach(label, 0, row, 1, 1)
        grid.attach(self.qos_switch, 1, row, 1, 1)
        row += 1
        
        return grid
    
    def _create_profiles_tab(self) -> Gtk.Widget:
        """Create Profiles management tab"""
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        box.set_border_width(20)
        
        # Profile list
        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        
        self.profile_store = Gtk.ListStore(str, str, str)  # name, mode, ssid
        self.profile_treeview = Gtk.TreeView(model=self.profile_store)
        
        # Add columns
        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("Profile Name", renderer, text=0)
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
        new_btn.connect("clicked", self._on_new_profile)
        button_box.pack_start(new_btn, True, True, 0)
        
        edit_btn = Gtk.Button(label="Edit")
        edit_btn.connect("clicked", self._on_edit_profile)
        button_box.pack_start(edit_btn, True, True, 0)
        
        delete_btn = Gtk.Button(label="Delete")
        delete_btn.connect("clicked", self._on_delete_profile)
        button_box.pack_start(delete_btn, True, True, 0)
        
        import_btn = Gtk.Button(label="Import")
        import_btn.connect("clicked", self._on_import_profiles)
        button_box.pack_start(import_btn, True, True, 0)
        
        export_btn = Gtk.Button(label="Export")
        export_btn.connect("clicked", self._on_export_profiles)
        button_box.pack_start(export_btn, True, True, 0)
        
        box.pack_start(button_box, False, False, 0)
        
        return box
    
    def _load_settings(self):
        """Load current settings into widgets"""
        # General tab
        self.autostart_switch.set_active(self.config.is_autostart_enabled())
        self.start_minimized_switch.set_active(self.config.get("start_minimized", False))
        self.notifications_switch.set_active(self.config.get("enable_notifications", True))
        self.data_warnings_switch.set_active(self.config.get("enable_data_warnings", True))
        self.data_threshold_spin.set_value(self.config.get("data_warning_threshold_mb", 10))
        self.update_interval_spin.set_value(self.config.get("update_interval_ms", 1000))
        self.theme_combo.set_active_id(self.config.get("theme", "cyberpunk_dark"))
        
        # Network tab
        self.proxy_ip_entry.set_text(self.config.get("proxy_ip", "192.168.49.1"))
        self.proxy_port_spin.set_value(self.config.get("proxy_port", 8000))
        self.timeout_spin.set_value(self.config.get("connection_timeout", 30))
        self.auto_reconnect_switch.set_active(self.config.get("auto_reconnect", True))
        self.reconnect_attempts_spin.set_value(self.config.get("reconnect_attempts", 3))
        self.reconnect_delay_spin.set_value(self.config.get("reconnect_delay", 5))
        
        # Stealth tab
        self.stealth_level_combo.set_active_id(str(self.config.get("stealth_level", 3)))
        self.ttl_spin.set_value(self.config.get("ttl_value", 65))
        self.block_ipv6_switch.set_active(self.config.get("block_ipv6", True))
        self.dns_leak_prevention_switch.set_active(self.config.get("dns_leak_prevention", True))
        # ... more settings
        
        # Load profiles
        self._load_profiles()
    
    def _save_settings(self):
        """Save settings from widgets to config"""
        # General tab
        if self.autostart_switch.get_active():
            self.config.enable_autostart()
        else:
            self.config.disable_autostart()
        
        self.config.set("start_minimized", self.start_minimized_switch.get_active())
        self.config.set("enable_notifications", self.notifications_switch.get_active())
        self.config.set("enable_data_warnings", self.data_warnings_switch.get_active())
        self.config.set("data_warning_threshold_mb", self.data_threshold_spin.get_value_as_int())
        self.config.set("update_interval_ms", self.update_interval_spin.get_value_as_int())
        self.config.set("theme", self.theme_combo.get_active_id())
        
        # Network tab
        self.config.set("proxy_ip", self.proxy_ip_entry.get_text())
        self.config.set("proxy_port", self.proxy_port_spin.get_value_as_int())
        self.config.set("connection_timeout", self.timeout_spin.get_value_as_int())
        self.config.set("auto_reconnect", self.auto_reconnect_switch.get_active())
        self.config.set("reconnect_attempts", self.reconnect_attempts_spin.get_value_as_int())
        self.config.set("reconnect_delay", self.reconnect_delay_spin.get_value_as_int())
        
        # Stealth tab
        self.config.set("stealth_level", int(self.stealth_level_combo.get_active_id()))
        self.config.set("ttl_value", self.ttl_spin.get_value_as_int())
        # ... more settings
        
        self.logger.info("Settings saved successfully")
    
    def _on_response(self, dialog, response_id):
        """Handle dialog button responses"""
        if response_id == Gtk.ResponseType.OK:
            self._save_settings()
            self._apply_settings()
            dialog.destroy()
        elif response_id == Gtk.ResponseType.APPLY:
            self._save_settings()
            self._apply_settings()
        elif response_id == Gtk.ResponseType.CANCEL:
            self._restore_original_settings()
            dialog.destroy()
        elif response_id == Gtk.ResponseType.HELP:
            self._reset_to_defaults()
    
    def _apply_settings(self):
        """Apply settings that take effect immediately"""
        # Notify parent window to reload settings
        if hasattr(self.parent_window, 'reload_settings'):
            self.parent_window.reload_settings()
    
    # ... more helper methods ...
```

### 1.3 Testing Strategy

```python
# tests/test_settings_dialog.py

import pytest
from src.settings_dialog import SettingsDialog
from src.config_manager import ConfigManager
import tempfile
import os

class TestSettingsDialog:
    
    @pytest.fixture
    def temp_config_dir(self):
        """Create temporary config directory"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        # Cleanup
        import shutil
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def config(self, temp_config_dir):
        """Create test config manager"""
        return ConfigManager(config_dir=temp_config_dir)
    
    def test_dialog_creation(self, config):
        """Test settings dialog can be created"""
        # This test would need GTK testing setup
        pass
    
    def test_load_settings(self, config):
        """Test loading settings into widgets"""
        pass
    
    def test_save_settings(self, config):
        """Test saving settings from widgets"""
        pass
    
    def test_reset_to_defaults(self, config):
        """Test reset to defaults functionality"""
        pass
    
    def test_validation(self, config):
        """Test input validation"""
        pass
```

---

## 2. FIRST-RUN WIZARD (16 hours)

### 2.1 Implementation

```python
# src/first_run_wizard.py

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib
from config_manager import get_config
from logger import get_logger

class FirstRunWizard(Gtk.Assistant):
    """
    First-run wizard to guide users through initial setup
    """
    
    def __init__(self):
        super().__init__()
        
        self.config = get_config()
        self.logger = get_logger()
        
        self.set_title("PdaNet Linux - Setup Wizard")
        self.set_default_size(800, 600)
        
        # Add pages
        self._add_welcome_page()
        self._add_requirements_page()
        self._add_permissions_page()
        self._add_android_setup_page()
        self._add_test_connection_page()
        self._add_profile_creation_page()
        self._add_completion_page()
        
        # Connect signals
        self.connect("cancel", self._on_cancel)
        self.connect("close", self._on_close)
        self.connect("apply", self._on_apply)
        self.connect("prepare", self._on_prepare)
        
        self.show_all()
    
    def _add_welcome_page(self):
        """Welcome page with introduction"""
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20)
        box.set_border_width(40)
        
        title = Gtk.Label()
        title.set_markup("<span size='x-large' weight='bold'>Welcome to PdaNet Linux!</span>")
        box.pack_start(title, False, False, 0)
        
        description = Gtk.Label()
        description.set_markup(
            "This wizard will help you set up PdaNet Linux for the first time.\n\n"
            "PdaNet Linux allows you to:\n"
            "• Share your Android device's internet connection\n"
            "• Use USB, WiFi, or iPhone hotspot modes\n"
            "• Hide tethering usage from carrier detection\n"
            "• Monitor bandwidth and connection quality\n\n"
            "Click 'Forward' to begin setup."
        )
        description.set_line_wrap(True)
        box.pack_start(description, False, False, 0)
        
        self.append_page(box)
        self.set_page_type(box, Gtk.AssistantPageType.INTRO)
        self.set_page_title(box, "Welcome")
        self.set_page_complete(box, True)
    
    def _add_requirements_page(self):
        """System requirements check page"""
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        box.set_border_width(20)
        
        title = Gtk.Label()
        title.set_markup("<span weight='bold'>System Requirements Check</span>")
        box.pack_start(title, False, False, 0)
        
        # Check requirements
        checks = [
            ("Python 3.8+", self._check_python()),
            ("GTK 3.0+", self._check_gtk()),
            ("NetworkManager", self._check_networkmanager()),
            ("PolicyKit", self._check_policykit()),
            ("redsocks", self._check_redsocks()),
            ("iptables", self._check_iptables()),
        ]
        
        for check_name, passed in checks:
            row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
            label = Gtk.Label(label=check_name)
            label.set_halign(Gtk.Align.START)
            label.set_width_chars(30)
            
            status = Gtk.Label()
            if passed:
                status.set_markup("<span foreground='#00FF00'>✓ Installed</span>")
            else:
                status.set_markup("<span foreground='#FF0000'>✗ Missing</span>")
            
            row.pack_start(label, False, False, 0)
            row.pack_start(status, False, False, 0)
            box.pack_start(row, False, False, 0)
        
        all_passed = all(check[1] for check in checks)
        
        self.append_page(box)
        self.set_page_type(box, Gtk.AssistantPageType.CONTENT)
        self.set_page_title(box, "Requirements Check")
        self.set_page_complete(box, all_passed)
    
    # ... more pages ...
    
    def _check_python(self) -> bool:
        """Check if Python 3.8+ is available"""
        import sys
        return sys.version_info >= (3, 8)
    
    def _check_gtk(self) -> bool:
        """Check if GTK 3.0+ is available"""
        return True  # We're running so GTK is available
    
    # ... more checks ...
```

---

## 3. ERROR RECOVERY UI (16 hours)

### 3.1 Error Database

```python
# src/error_recovery.py

ERROR_SOLUTIONS = {
    "interface_not_found": {
        "title": "Network Interface Not Found",
        "description": "Unable to detect USB or WiFi interface",
        "solutions": [
            {
                "title": "Check USB connection",
                "steps": [
                    "Ensure Android device is connected via USB",
                    "Enable USB debugging on Android",
                    "Try a different USB cable or port"
                ],
                "auto_fix": None
            },
            {
                "title": "Check WiFi connection",
                "steps": [
                    "Verify WiFi hotspot is enabled on Android",
                    "Check that Linux is connected to the hotspot",
                    "Run: nmcli device wifi list"
                ],
                "auto_fix": None
            }
        ]
    },
    "proxy_not_accessible": {
        "title": "PdaNet Proxy Not Accessible",
        "description": "Cannot connect to proxy at 192.168.49.1:8000",
        "solutions": [
            {
                "title": "Restart PdaNet+ app",
                "steps": [
                    "Open PdaNet+ app on Android",
                    "Toggle 'Activate USB Mode' off and on",
                    "Wait 5 seconds for proxy to start"
                ],
                "auto_fix": None
            },
            {
                "title": "Check firewall",
                "steps": [
                    "Ensure firewall allows connections to proxy",
                    "Try: sudo ufw allow from any to 192.168.49.1 port 8000"
                ],
                "auto_fix": "allow_proxy_firewall"
            }
        ]
    },
    # ... more error definitions ...
}

class ErrorRecoveryDialog(Gtk.Dialog):
    """Dialog for error recovery with solutions"""
    
    def __init__(self, parent, error_code, error_message):
        super().__init__(
            title="Error Recovery Assistant",
            parent=parent,
            flags=Gtk.DialogFlags.MODAL
        )
        
        self.error_code = error_code
        self.error_message = error_message
        self.error_info = ERROR_SOLUTIONS.get(error_code, {})
        
        self._build_ui()
    
    def _build_ui(self):
        """Build error recovery UI"""
        # ... implementation ...
```

---

## 4. DATA USAGE DASHBOARD (16 hours)

### 4.1 Implementation

```python
# Add to pdanet_gui_v2.py

def build_data_usage_panel(self):
    """Build data usage dashboard panel"""
    panel = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
    panel.get_style_context().add_class("panel")
    
    # Header
    header = Gtk.Label(label="DATA USAGE")
    header.get_style_context().add_class("panel-header")
    panel.pack_start(header, False, False, 0)
    
    # Circular progress meter
    self.data_usage_meter = CircularProgressMeter()
    panel.pack_start(self.data_usage_meter, False, False, 0)
    
    # Current session data
    self.session_data_label = Gtk.Label()
    self.session_data_label.set_markup("<b>Session:</b> 0 GB")
    panel.pack_start(self.session_data_label, False, False, 0)
    
    # Monthly data
    self.monthly_data_label = Gtk.Label()
    self.monthly_data_label.set_markup("<b>This Month:</b> 0 GB")
    panel.pack_start(self.monthly_data_label, False, False, 0)
    
    # Warning threshold
    self.threshold_label = Gtk.Label()
    self.threshold_label.set_markup("<b>Warning at:</b> 10 GB")
    panel.pack_start(self.threshold_label, False, False, 0)
    
    # Reset button
    reset_btn = Gtk.Button(label="Reset Counters")
    reset_btn.connect("clicked", self._on_reset_usage)
    panel.pack_start(reset_btn, False, False, 0)
    
    return panel
```

---

## 🎯 ACCEPTANCE CRITERIA

### Settings Dialog
✅ All settings accessible via GUI  
✅ Changes apply immediately or on restart  
✅ Input validation for all fields  
✅ Reset to defaults option  
✅ Import/export profiles  

### First-Run Wizard
✅ Guides user through complete setup  
✅ Validates system requirements  
✅ Creates first profile  
✅ Tests connection before completion  

### Error Recovery
✅ User-friendly error messages  
✅ Step-by-step solutions  
✅ One-click fixes where possible  
✅ Copy error details to clipboard  

### Data Usage Dashboard
✅ Visual usage meter  
✅ Session and monthly tracking  
✅ Configurable warning thresholds  
✅ Export usage history  

---

## 📅 TIMELINE

### Week 1
- Day 1-2: Settings Dialog structure & General tab
- Day 3: Network & Stealth tabs
- Day 4: Advanced & Profiles tabs
- Day 5: Testing & refinement

### Week 2
- Day 1: First-Run Wizard (all pages)
- Day 2: Error Recovery system
- Day 3: Data Usage Dashboard
- Day 4-5: Integration testing, bug fixes, documentation

---

**Total: 88 hours across 2 weeks**

