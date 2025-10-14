"""
First-Run Wizard for PdaNet Linux
Guides users through initial setup
"""

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib
import subprocess
import shutil
from pathlib import Path
from typing import Optional

from config_manager import get_config
from logger import get_logger
from constants import *


class FirstRunWizard(Gtk.Assistant):
    """
    First-run wizard to guide users through initial setup
    Pages: Welcome, Requirements, Permissions, Android Setup, Test Connection, Profile, Complete
    """
    
    def __init__(self, parent_window=None):
        super().__init__()
        
        self.config = get_config()
        self.logger = get_logger()
        self.parent_window = parent_window
        
        # Setup wizard
        self.set_title("PdaNet Linux - Setup Wizard")
        self.set_default_size(700, 500)
        self.set_modal(True)
        
        if parent_window:
            self.set_transient_for(parent_window)
        
        # Track setup state
        self.requirements_met = {}
        self.test_connection_success = False
        
        # Build pages
        self._add_welcome_page()
        self._add_requirements_page()
        self._add_permissions_page()
        self._add_android_setup_page()
        self._add_test_connection_page()
        self._add_profile_page()
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
        box.set_halign(Gtk.Align.CENTER)
        box.set_valign(Gtk.Align.CENTER)
        
        # Title
        title = Gtk.Label()
        title.set_markup('<span size="xx-large" weight="bold">Welcome to PdaNet Linux!</span>')
        box.pack_start(title, False, False, 0)
        
        # Description
        description = Gtk.Label()
        description.set_markup(
            '<span size="large">Share your Android device\'s internet connection\n'
            'with advanced carrier detection bypass</span>'
        )
        description.set_justify(Gtk.Justification.CENTER)
        box.pack_start(description, False, False, 10)
        
        # Features list
        features = Gtk.Label()
        features.set_markup(
            '<b>Features:</b>\n'
            '• USB, WiFi, and iPhone hotspot modes\n'
            '• Hide tethering usage from carrier detection\n'
            '• Monitor bandwidth and connection quality\n'
            '• Connection profiles for quick switching\n'
            '• Advanced network monitoring and QoS\n\n'
            '<i>This wizard will guide you through the setup process.</i>'
        )
        features.set_line_wrap(True)
        features.set_max_width_chars(60)
        box.pack_start(features, False, False, 0)
        
        self.append_page(box)
        self.set_page_type(box, Gtk.AssistantPageType.INTRO)
        self.set_page_title(box, "Welcome")
        self.set_page_complete(box, True)
    
    def _add_requirements_page(self):
        """System requirements check page"""
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        box.set_border_width(20)
        
        # Title
        title = Gtk.Label()
        title.set_markup('<span size="large" weight="bold">System Requirements Check</span>')
        title.set_halign(Gtk.Align.START)
        box.pack_start(title, False, False, 0)
        
        info = Gtk.Label()
        info.set_markup('<span size="small">Checking system for required dependencies...</span>')
        info.set_halign(Gtk.Align.START)
        box.pack_start(info, False, False, 10)
        
        # Checks grid
        grid = Gtk.Grid()
        grid.set_row_spacing(8)
        grid.set_column_spacing(20)
        
        self.requirement_checks = {}
        checks = [
            ("python", "Python 3.8+", self._check_python),
            ("gtk", "GTK 3.0+", self._check_gtk),
            ("networkmanager", "NetworkManager", self._check_networkmanager),
            ("policykit", "PolicyKit", self._check_policykit),
            ("redsocks", "redsocks", self._check_redsocks),
            ("iptables", "iptables", self._check_iptables),
        ]
        
        for i, (key, name, check_func) in enumerate(checks):
            # Label
            label = Gtk.Label(label=name)
            label.set_halign(Gtk.Align.START)
            label.set_width_chars(25)
            grid.attach(label, 0, i, 1, 1)
            
            # Status
            status_label = Gtk.Label()
            status_label.set_halign(Gtk.Align.START)
            grid.attach(status_label, 1, i, 1, 1)
            
            # Store reference
            self.requirement_checks[key] = (check_func, status_label)
        
        box.pack_start(grid, False, False, 10)
        
        # Check button
        check_button = Gtk.Button(label="Run Check")
        check_button.connect("clicked", self._on_run_requirements_check)
        box.pack_start(check_button, False, False, 10)
        
        # Warning label
        self.requirements_warning = Gtk.Label()
        self.requirements_warning.set_line_wrap(True)
        box.pack_start(self.requirements_warning, False, False, 0)
        
        self.requirements_page = box
        self.append_page(box)
        self.set_page_type(box, Gtk.AssistantPageType.CONTENT)
        self.set_page_title(box, "Requirements Check")
        self.set_page_complete(box, False)
    
    def _add_permissions_page(self):
        """Permissions setup page"""
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        box.set_border_width(20)
        
        title = Gtk.Label()
        title.set_markup('<span size="large" weight="bold">Permission Setup</span>')
        title.set_halign(Gtk.Align.START)
        box.pack_start(title, False, False, 0)
        
        info = Gtk.Label()
        info.set_markup(
            'PdaNet Linux requires root privileges for network configuration.\n'
            'We use PolicyKit (pkexec) for secure privilege escalation.\n\n'
            '<b>Why root access is needed:</b>\n'
            '• Configure iptables rules for traffic routing\n'
            '• Modify TTL values for carrier bypass\n'
            '• Start/stop redsocks service\n'
            '• Configure DNS settings\n\n'
            '<i>You will be prompted for your password when needed.</i>'
        )
        info.set_line_wrap(True)
        info.set_halign(Gtk.Align.START)
        box.pack_start(info, False, False, 10)
        
        # Test permissions button
        test_button = Gtk.Button(label="Test Permissions")
        test_button.connect("clicked", self._on_test_permissions)
        box.pack_start(test_button, False, False, 10)
        
        self.permissions_status = Gtk.Label()
        self.permissions_status.set_line_wrap(True)
        box.pack_start(self.permissions_status, False, False, 0)
        
        self.permissions_page = box
        self.append_page(box)
        self.set_page_type(box, Gtk.AssistantPageType.CONTENT)
        self.set_page_title(box, "Permissions")
        self.set_page_complete(box, True)  # Optional step
    
    def _add_android_setup_page(self):
        """Android device setup instructions"""
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        box.set_border_width(20)
        
        title = Gtk.Label()
        title.set_markup('<span size="large" weight="bold">Android Device Setup</span>')
        title.set_halign(Gtk.Align.START)
        box.pack_start(title, False, False, 0)
        
        instructions = Gtk.Label()
        instructions.set_markup(
            '<b>On your Android device:</b>\n\n'
            '<b>1. Install PdaNet+ app</b>\n'
            '   • Download from Google Play Store\n'
            '   • Or get APK from pdanet.com\n\n'
            '<b>2. Enable USB debugging</b>\n'
            '   • Settings → About Phone\n'
            '   • Tap "Build Number" 7 times\n'
            '   • Settings → Developer Options\n'
            '   • Enable "USB Debugging"\n\n'
            '<b>3. Connect device</b>\n'
            '   • Connect via USB cable\n'
            '   • Accept USB debugging prompt on device\n'
            '   • Open PdaNet+ app\n'
            '   • Enable "USB Tether"\n\n'
            '<b>For WiFi/iPhone mode:</b>\n'
            '   • Enable WiFi hotspot on device\n'
            '   • Connect your Linux computer to the hotspot\n'
            '   • Note the hotspot SSID and password'
        )
        instructions.set_line_wrap(True)
        instructions.set_halign(Gtk.Align.START)
        box.pack_start(instructions, True, True, 10)
        
        self.append_page(box)
        self.set_page_type(box, Gtk.AssistantPageType.CONTENT)
        self.set_page_title(box, "Android Setup")
        self.set_page_complete(box, True)
    
    def _add_test_connection_page(self):
        """Test connection page"""
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        box.set_border_width(20)
        
        title = Gtk.Label()
        title.set_markup('<span size="large" weight="bold">Test Connection</span>')
        title.set_halign(Gtk.Align.START)
        box.pack_start(title, False, False, 0)
        
        info = Gtk.Label()
        info.set_markup(
            'Let\'s verify your setup is working.\n\n'
            '<b>Make sure:</b>\n'
            '• Android device is connected\n'
            '• PdaNet+ app is running on device\n'
            '• USB tethering is enabled in PdaNet+ app'
        )
        info.set_line_wrap(True)
        info.set_halign(Gtk.Align.START)
        box.pack_start(info, False, False, 10)
        
        # Test button
        test_button = Gtk.Button(label="Test Connection")
        test_button.connect("clicked", self._on_test_connection)
        box.pack_start(test_button, False, False, 10)
        
        # Status
        self.test_status = Gtk.Label()
        self.test_status.set_line_wrap(True)
        box.pack_start(self.test_status, False, False, 0)
        
        # Progress
        self.test_progress = Gtk.ProgressBar()
        self.test_progress.set_no_show_all(True)
        box.pack_start(self.test_progress, False, False, 0)
        
        self.test_page = box
        self.append_page(box)
        self.set_page_type(box, Gtk.AssistantPageType.CONTENT)
        self.set_page_title(box, "Test Connection")
        self.set_page_complete(box, False)
    
    def _add_profile_page(self):
        """Profile creation page"""
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        box.set_border_width(20)
        
        title = Gtk.Label()
        title.set_markup('<span size="large" weight="bold">Create Your First Profile</span>')
        title.set_halign(Gtk.Align.START)
        box.pack_start(title, False, False, 0)
        
        info = Gtk.Label()
        info.set_markup(
            'Profiles allow you to save and quickly switch between\n'
            'different network configurations.'
        )
        info.set_halign(Gtk.Align.START)
        box.pack_start(info, False, False, 10)
        
        # Profile name
        grid = Gtk.Grid()
        grid.set_row_spacing(10)
        grid.set_column_spacing(10)
        
        label = Gtk.Label(label="Profile Name:")
        label.set_halign(Gtk.Align.START)
        self.profile_name_entry = Gtk.Entry()
        self.profile_name_entry.set_text("Default")
        self.profile_name_entry.set_hexpand(True)
        grid.attach(label, 0, 0, 1, 1)
        grid.attach(self.profile_name_entry, 1, 0, 1, 1)
        
        # Connection mode
        label = Gtk.Label(label="Connection Mode:")
        label.set_halign(Gtk.Align.START)
        self.profile_mode_combo = Gtk.ComboBoxText()
        self.profile_mode_combo.append("usb", "USB Tethering")
        self.profile_mode_combo.append("wifi", "WiFi Hotspot")
        self.profile_mode_combo.append("iphone", "iPhone Hotspot")
        self.profile_mode_combo.set_active(0)
        grid.attach(label, 0, 1, 1, 1)
        grid.attach(self.profile_mode_combo, 1, 1, 1, 1)
        
        box.pack_start(grid, False, False, 10)
        
        # Skip option
        skip_check = Gtk.CheckButton(label="Skip profile creation (can create later)")
        skip_check.connect("toggled", lambda cb: self.set_page_complete(box, True))
        box.pack_start(skip_check, False, False, 10)
        
        self.append_page(box)
        self.set_page_type(box, Gtk.AssistantPageType.CONTENT)
        self.set_page_title(box, "Create Profile")
        self.set_page_complete(box, True)
    
    def _add_completion_page(self):
        """Completion page"""
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20)
        box.set_border_width(40)
        box.set_halign(Gtk.Align.CENTER)
        box.set_valign(Gtk.Align.CENTER)
        
        # Success icon
        title = Gtk.Label()
        title.set_markup('<span size="xx-large">✓</span>')
        box.pack_start(title, False, False, 0)
        
        # Title
        title = Gtk.Label()
        title.set_markup('<span size="x-large" weight="bold">Setup Complete!</span>')
        box.pack_start(title, False, False, 0)
        
        # Message
        message = Gtk.Label()
        message.set_markup(
            'PdaNet Linux is ready to use.\n\n'
            '<b>Quick Tips:</b>\n'
            '• Click CONNECT to start tethering\n'
            '• Use ⚙ SETTINGS to customize\n'
            '• Press Ctrl+H to view connection history\n'
            '• Check system tray for quick access\n\n'
            '<i>For help, check the documentation or logs.</i>'
        )
        message.set_justify(Gtk.Justification.CENTER)
        message.set_line_wrap(True)
        box.pack_start(message, False, False, 0)
        
        self.append_page(box)
        self.set_page_type(box, Gtk.AssistantPageType.SUMMARY)
        self.set_page_title(box, "Complete")
        self.set_page_complete(box, True)
    
    # Requirement checks
    def _check_python(self) -> bool:
        """Check if Python 3.8+ is available"""
        import sys
        return sys.version_info >= (3, 8)
    
    def _check_gtk(self) -> bool:
        """Check if GTK 3.0+ is available"""
        return True  # We're running so GTK is available
    
    def _check_networkmanager(self) -> bool:
        """Check if NetworkManager is installed and running"""
        try:
            result = subprocess.run(
                ["systemctl", "is-active", "NetworkManager"],
                capture_output=True,
                text=True
            )
            return result.returncode == 0
        except:
            return False
    
    def _check_policykit(self) -> bool:
        """Check if PolicyKit is available"""
        return shutil.which("pkexec") is not None
    
    def _check_redsocks(self) -> bool:
        """Check if redsocks is installed"""
        return shutil.which("redsocks") is not None
    
    def _check_iptables(self) -> bool:
        """Check if iptables is installed"""
        return shutil.which("iptables") is not None
    
    def _on_run_requirements_check(self, button):
        """Run requirements check"""
        all_met = True
        
        for key, (check_func, status_label) in self.requirement_checks.items():
            passed = check_func()
            self.requirements_met[key] = passed
            
            if passed:
                status_label.set_markup('<span foreground="#00FF00">✓ Installed</span>')
            else:
                status_label.set_markup('<span foreground="#FF0000">✗ Missing</span>')
                all_met = False
        
        if all_met:
            self.requirements_warning.set_markup(
                '<span foreground="#00FF00"><b>✓ All requirements met!</b></span>'
            )
            self.set_page_complete(self.requirements_page, True)
        else:
            missing = [k for k, v in self.requirements_met.items() if not v]
            self.requirements_warning.set_markup(
                f'<span foreground="#FF0000"><b>Missing requirements: {", ".join(missing)}</b>\n'
                f'Please install missing packages and run check again.</span>'
            )
            self.set_page_complete(self.requirements_page, False)
    
    def _on_test_permissions(self, button):
        """Test if permissions work"""
        try:
            # Try to run a simple privileged command
            result = subprocess.run(
                ["pkexec", "whoami"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                self.permissions_status.set_markup(
                    '<span foreground="#00FF00"><b>✓ Permissions working!</b>\n'
                    'PolicyKit authentication successful.</span>'
                )
            else:
                self.permissions_status.set_markup(
                    '<span foreground="#FF0000"><b>✗ Permission denied</b>\n'
                    'PolicyKit authentication failed.</span>'
                )
        except Exception as e:
            self.permissions_status.set_markup(
                f'<span foreground="#FF0000"><b>✗ Error testing permissions</b>\n'
                f'{str(e)}</span>'
            )
    
    def _on_test_connection(self, button):
        """Test USB connection"""
        self.test_progress.show()
        self.test_progress.pulse()
        self.test_status.set_text("Testing connection...")
        
        # Simulate test (in real implementation, would actually test)
        def finish_test():
            # Check for USB interface
            try:
                result = subprocess.run(
                    ["ip", "link", "show"],
                    capture_output=True,
                    text=True
                )
                
                # Look for common Android USB interface names
                if any(name in result.stdout for name in ["usb0", "rndis", "enp"]):
                    self.test_status.set_markup(
                        '<span foreground="#00FF00"><b>✓ Connection test passed!</b>\n'
                        'USB interface detected.</span>'
                    )
                    self.test_connection_success = True
                    self.set_page_complete(self.test_page, True)
                else:
                    self.test_status.set_markup(
                        '<span foreground="#FFFF00"><b>⚠ No USB interface detected</b>\n'
                        'Make sure device is connected and PdaNet+ is running.\n'
                        'You can skip this test and try connecting later.</span>'
                    )
                    self.set_page_complete(self.test_page, True)  # Allow skip
            except Exception as e:
                self.test_status.set_markup(
                    f'<span foreground="#FF0000"><b>✗ Test failed</b>\n{str(e)}</span>'
                )
                self.set_page_complete(self.test_page, True)  # Allow skip
            
            self.test_progress.hide()
            return False
        
        GLib.timeout_add(1000, finish_test)
    
    def _on_prepare(self, assistant, page):
        """Called when moving to a new page"""
        # Run checks automatically on requirements page
        if page == self.requirements_page and not self.requirements_met:
            GLib.timeout_add(500, lambda: self._on_run_requirements_check(None))
    
    def _on_cancel(self, assistant):
        """Handle cancel"""
        self.logger.info("First-run wizard cancelled")
        assistant.destroy()
    
    def _on_close(self, assistant):
        """Handle close after completion"""
        self._mark_first_run_complete()
        self.logger.info("First-run wizard completed")
        assistant.destroy()
    
    def _on_apply(self, assistant):
        """Handle apply (final page)"""
        self._mark_first_run_complete()
        self._create_profile_if_requested()
    
    def _mark_first_run_complete(self):
        """Mark first-run as complete"""
        self.config.set('first_run_complete', True)
        self.logger.info("Marked first-run as complete")
    
    def _create_profile_if_requested(self):
        """Create profile if user entered details"""
        profile_name = self.profile_name_entry.get_text()
        if profile_name and profile_name != "Default":
            mode = self.profile_mode_combo.get_active_id()
            
            profile = {
                'name': profile_name,
                'mode': mode,
                'auto_connect': False,
                'stealth_enabled': True,
                'stealth_level': STEALTH_LEVEL_AGGRESSIVE
            }
            
            try:
                profile_id = self.config.add_profile(profile)
                self.logger.info(f"Created first profile: {profile_name} ({mode})")
            except Exception as e:
                self.logger.error(f"Failed to create profile: {e}")
