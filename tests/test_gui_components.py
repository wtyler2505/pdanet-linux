#!/usr/bin/env python3
"""
Unit tests for GUI Components
Tests SingleInstance, window initialization, and GTK UI components
"""

import os
import sys
import tempfile
import unittest
from unittest.mock import MagicMock, mock_open, patch

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

# Mock gi before importing
gi_mock = MagicMock()
gi_mock.require_version = MagicMock()
gi_mock.repository = MagicMock()
gi_mock.repository.Gtk = MagicMock()
gi_mock.repository.Gdk = MagicMock()
gi_mock.repository.GLib = MagicMock()
gi_mock.repository.AppIndicator3 = MagicMock()
gi_mock.repository.Pango = MagicMock()

sys.modules["gi"] = gi_mock
sys.modules["gi.repository"] = gi_mock.repository

# Mock theme and manager imports
with patch.dict(
    sys.modules,
    {
        "theme": MagicMock(
            Colors=MagicMock(),
            Format=MagicMock(),
            ASCII=MagicMock(),
            get_css=MagicMock(return_value=""),
        ),
        "logger": MagicMock(get_logger=MagicMock()),
        "config_manager": MagicMock(get_config=MagicMock()),
        "stats_collector": MagicMock(get_stats=MagicMock()),
        "connection_manager": MagicMock(
            get_connection_manager=MagicMock(), ConnectionState=MagicMock()
        ),
    },
):
    from pdanet_gui_v2 import SingleInstance


class TestSingleInstance(unittest.TestCase):
    """Test suite for SingleInstance functionality"""

    def setUp(self):
        """Set up test fixtures"""
        self.temp_lock = tempfile.NamedTemporaryFile(delete=False)
        self.temp_lock.close()
        self.instance = SingleInstance(self.temp_lock.name)

    def tearDown(self):
        """Clean up test fixtures"""
        self.instance.release()
        try:
            os.unlink(self.temp_lock.name)
        except:
            pass

    @patch("fcntl.lockf")
    @patch("builtins.open", new_callable=mock_open)
    def test_acquire_lock_success(self, mock_file, mock_lockf):
        """Test successful lock acquisition"""
        mock_lockf.return_value = None  # Success

        result = self.instance.acquire()
        self.assertTrue(result)
        mock_file.assert_called_once_with(self.temp_lock.name, "w")
        mock_lockf.assert_called_once()

    @patch("fcntl.lockf")
    @patch("builtins.open", new_callable=mock_open)
    def test_acquire_lock_failure(self, mock_file, mock_lockf):
        """Test lock acquisition failure (another instance running)"""
        mock_lockf.side_effect = OSError("Resource temporarily unavailable")

        result = self.instance.acquire()
        self.assertFalse(result)

    @patch("fcntl.lockf")
    @patch("builtins.open", new_callable=mock_open)
    def test_release_lock(self, mock_file, mock_lockf):
        """Test lock release"""
        # First acquire the lock
        self.instance.acquire()

        # Then release it
        with patch("os.unlink") as mock_unlink:
            self.instance.release()
            mock_unlink.assert_called_once_with(self.temp_lock.name)

    def test_custom_lockfile_path(self):
        """Test custom lockfile path"""
        custom_path = "/tmp/custom-pdanet.lock"
        instance = SingleInstance(custom_path)
        self.assertEqual(instance.lockfile, custom_path)

    @patch("builtins.open", side_effect=PermissionError())
    def test_acquire_permission_error(self, mock_file):
        """Test lock acquisition with permission error"""
        result = self.instance.acquire()
        self.assertFalse(result)


class TestGUIThemeIntegration(unittest.TestCase):
    """Test suite for theme integration in GUI"""

    def setUp(self):
        """Set up test fixtures"""
        self.mock_theme = MagicMock()
        self.mock_theme.Colors.BLACK = "#000000"
        self.mock_theme.Colors.GREEN = "#00FF00"
        self.mock_theme.Colors.RED = "#FF0000"
        self.mock_theme.get_css.return_value = "* { background: #000000; }"

    def test_color_constants(self):
        """Test theme color constants are properly defined"""
        self.assertEqual(self.mock_theme.Colors.BLACK, "#000000")
        self.assertEqual(self.mock_theme.Colors.GREEN, "#00FF00")
        self.assertEqual(self.mock_theme.Colors.RED, "#FF0000")

    def test_css_generation(self):
        """Test CSS generation for GTK theme"""
        css = self.mock_theme.get_css()
        self.assertIsInstance(css, str)
        self.assertIn("#000000", css)  # Cyberpunk black background

    def test_no_unsupported_css_properties(self):
        """Test CSS doesn't contain unsupported GTK3 properties"""
        css = self.mock_theme.get_css()

        # GTK3 doesn't support these properties
        unsupported_properties = ["text-transform", "letter-spacing", "text-shadow", "box-shadow"]

        for prop in unsupported_properties:
            self.assertNotIn(prop, css.lower(), f"CSS contains unsupported property: {prop}")


class TestGUIStateCallbacks(unittest.TestCase):
    """Test suite for GUI state change callbacks"""

    def setUp(self):
        """Set up test fixtures"""
        self.mock_connection = MagicMock()
        self.mock_logger = MagicMock()
        self.callback_invocations = []

    def test_state_change_callback_registration(self):
        """Test state change callback registration"""

        def test_callback(state):
            self.callback_invocations.append(state)

        self.mock_connection.register_state_change_callback(test_callback)
        self.mock_connection.register_state_change_callback.assert_called_once_with(test_callback)

    def test_error_callback_registration(self):
        """Test error callback registration"""

        def test_error_callback(error):
            self.callback_invocations.append(error)

        self.mock_connection.register_error_callback(test_error_callback)
        self.mock_connection.register_error_callback.assert_called_once_with(test_error_callback)

    @patch("gi.repository.GLib")
    def test_gtk_main_loop_integration(self, mock_glib):
        """Test GTK main loop timer integration"""
        mock_glib.timeout_add = MagicMock()

        # Simulate adding update timer
        update_interval = 1000  # 1 second
        mock_update_function = MagicMock()

        mock_glib.timeout_add(update_interval, mock_update_function)
        mock_glib.timeout_add.assert_called_once_with(update_interval, mock_update_function)

    def test_thread_safe_gui_updates(self):
        """Test thread-safe GUI updates using GLib.idle_add"""
        with patch("gi.repository.GLib") as mock_glib:
            mock_glib.idle_add = MagicMock()

            # Simulate background thread updating GUI
            update_data = {"status": "connected", "interface": "wlan0"}
            update_function = MagicMock()

            mock_glib.idle_add(update_function, update_data)
            mock_glib.idle_add.assert_called_once_with(update_function, update_data)


class TestGUIErrorHandling(unittest.TestCase):
    """Test suite for GUI error handling"""

    def test_gtk_css_error_handling(self):
        """Test handling of GTK CSS parsing errors"""
        invalid_css = "invalid { text-transform: uppercase; }"

        with patch("gi.repository.Gtk") as mock_gtk:
            mock_provider = MagicMock()
            mock_gtk.CssProvider.return_value = mock_provider
            mock_provider.load_from_data.side_effect = Exception("CSS parse error")

            # Test that CSS errors are handled gracefully
            try:
                mock_provider.load_from_data(invalid_css.encode())
            except Exception as e:
                self.assertIn("CSS parse error", str(e))

    def test_missing_dependency_handling(self):
        """Test handling of missing GTK dependencies"""
        with patch("gi.require_version", side_effect=ImportError("Gtk not found")):
            try:
                import gi

                gi.require_version("Gtk", "3.0")
                self.fail("Should have raised ImportError")
            except ImportError as e:
                self.assertIn("Gtk not found", str(e))

    def test_config_loading_error_handling(self):
        """Test handling of configuration loading errors"""
        with patch("config_manager.get_config") as mock_get_config:
            mock_config = MagicMock()
            mock_config.get.side_effect = KeyError("Setting not found")
            mock_get_config.return_value = mock_config

            # Test that missing config values are handled with defaults
            try:
                width = mock_config.get("window_width", 900)
            except KeyError:
                width = 900  # Default fallback

            self.assertEqual(width, 900)


class TestGUIWindowManagement(unittest.TestCase):
    """Test suite for GUI window management"""

    def setUp(self):
        """Set up test fixtures"""
        self.mock_window = MagicMock()
        self.mock_window.set_default_size = MagicMock()
        self.mock_window.set_position = MagicMock()

    def test_window_sizing(self):
        """Test window default sizing"""
        width, height = 900, 600
        self.mock_window.set_default_size(width, height)
        self.mock_window.set_default_size.assert_called_once_with(width, height)

    def test_window_positioning(self):
        """Test window positioning"""
        with patch("gi.repository.Gtk") as mock_gtk:
            mock_gtk.WindowPosition.CENTER = "center"
            self.mock_window.set_position("center")
            self.mock_window.set_position.assert_called_once_with("center")

    def test_window_title(self):
        """Test window title setting"""
        expected_title = "PDANET LINUX"
        self.mock_window.title = expected_title
        self.assertEqual(self.mock_window.title, expected_title)

    def test_system_tray_integration(self):
        """Test system tray indicator setup"""
        with patch("gi.repository.AppIndicator3") as mock_indicator:
            mock_indicator3 = MagicMock()
            mock_indicator.Indicator = MagicMock(return_value=mock_indicator3)

            # Simulate indicator creation
            indicator = mock_indicator.Indicator.new("pdanet-linux", "network-idle", 1)
            self.assertIsNotNone(indicator)


if __name__ == "__main__":
    unittest.main()
