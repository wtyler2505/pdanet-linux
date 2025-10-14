"""
Tests for Settings Dialog
"""

import pytest
import sys
import os

# Mock GTK if not available
try:
    import gi
    gi.require_version("Gtk", "3.0")
    from gi.repository import Gtk
    GTK_AVAILABLE = True
except:
    GTK_AVAILABLE = False
    pytest.skip("GTK not available", allow_module_level=True)

from config_manager import ConfigManager
from dialogs.settings_dialog import SettingsDialog
from constants import *


class TestSettingsDialog:
    """Test Settings Dialog functionality"""
    
    @pytest.fixture
    def temp_config_dir(self, tmp_path):
        """Create temporary config directory"""
        config_dir = tmp_path / "config"
        config_dir.mkdir()
        return config_dir
    
    @pytest.fixture
    def config(self, temp_config_dir):
        """Create test config manager"""
        return ConfigManager(config_dir=str(temp_config_dir))
    
    def test_constants_imported(self):
        """Test that constants are properly defined"""
        assert PROXY_DEFAULT_IP == "192.168.49.1"
        assert PROXY_DEFAULT_PORT == 8000
        assert TTL_VALUE_PHONE_TRAFFIC == 65
        assert GUI_UPDATE_INTERVAL_MS == 1000
        assert STEALTH_LEVEL_AGGRESSIVE == 3
    
    def test_constants_validation_limits(self):
        """Test validation limit constants"""
        assert SSID_MIN_LENGTH == 1
        assert SSID_MAX_LENGTH == 32
        assert PORT_MIN == 1
        assert PORT_MAX == 65535
    
    def test_constants_modes(self):
        """Test connection mode constants"""
        assert MODE_USB == "usb"
        assert MODE_WIFI == "wifi"
        assert MODE_IPHONE == "iphone"
    
    def test_constants_quality_thresholds(self):
        """Test quality threshold constants"""
        assert QUALITY_SCORE_EXCELLENT == 90
        assert QUALITY_SCORE_GOOD == 70
        assert LATENCY_EXCELLENT_MS == 50
        assert LATENCY_GOOD_MS == 100
    
    def test_dialog_class_exists(self):
        """Test that SettingsDialog class is defined"""
        assert SettingsDialog is not None
    
    # Note: Full GUI testing requires display server
    # These tests verify the code structure is sound


class TestConstantsModule:
    """Test constants module completeness"""
    
    def test_all_connection_constants(self):
        """Test connection-related constants"""
        assert CONNECTION_TIMEOUT_SECONDS > 0
        assert RECONNECT_DELAY_SECONDS > 0
        assert RETRY_MAX_ATTEMPTS > 0
    
    def test_all_gui_constants(self):
        """Test GUI-related constants"""
        assert MAIN_WINDOW_WIDTH > 0
        assert MAIN_WINDOW_HEIGHT > 0
        assert PANEL_SPACING >= 0
    
    def test_all_data_usage_constants(self):
        """Test data usage constants"""
        assert DATA_WARNING_THRESHOLD_BYTES > 0
        assert BYTES_PER_KB == 1024
        assert BYTES_PER_MB == 1024 * 1024
        assert BYTES_PER_GB == 1024 * 1024 * 1024
    
    def test_all_stealth_constants(self):
        """Test stealth mode constants"""
        assert STEALTH_LEVEL_BASIC == 1
        assert STEALTH_LEVEL_MODERATE == 2
        assert STEALTH_LEVEL_AGGRESSIVE == 3
        assert DEFAULT_STEALTH_LEVEL in [1, 2, 3]
    
    def test_all_log_constants(self):
        """Test logging constants"""
        assert LOG_LEVEL_DEBUG == "DEBUG"
        assert LOG_LEVEL_INFO == "INFO"
        assert LOG_LEVEL_WARNING == "WARNING"
        assert LOG_LEVEL_ERROR == "ERROR"
    
    def test_all_keyboard_shortcuts(self):
        """Test keyboard shortcut constants"""
        assert SHORTCUT_CONNECT == "<Control>c"
        assert SHORTCUT_DISCONNECT == "<Control>d"
        assert SHORTCUT_QUIT == "<Control>q"
        assert SHORTCUT_SETTINGS == "<Control>s"
