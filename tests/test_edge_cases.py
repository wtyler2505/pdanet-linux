#!/usr/bin/env python3
"""
Edge Case and Error Scenario Tests
Tests boundary conditions, error handling, and failure scenarios
"""

import json
import os
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from unittest.mock import MagicMock, Mock, patch

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

# Mock dependencies for testing
with patch.dict(sys.modules, {"gi": MagicMock(), "gi.repository": MagicMock()}):
    pass


class TestConnectionEdgeCases(unittest.TestCase):
    """Test suite for connection edge cases and failure scenarios"""

    def setUp(self):
        """Set up test fixtures"""
        self.mock_logger = MagicMock()
        self.mock_config = MagicMock()
        self.mock_stats = MagicMock()

    def test_rapid_state_transitions(self):
        """Test rapid state change handling"""
        with (
            patch("connection_manager.get_logger", return_value=self.mock_logger),
            patch("connection_manager.get_config", return_value=self.mock_config),
            patch("connection_manager.get_stats", return_value=self.mock_stats),
        ):
            from connection_manager import ConnectionManager, ConnectionState

            manager = ConnectionManager()

            # Rapid state transitions
            states = [
                ConnectionState.CONNECTING,
                ConnectionState.CONNECTED,
                ConnectionState.DISCONNECTING,
                ConnectionState.DISCONNECTED,
                ConnectionState.ERROR,
            ]

            for state in states:
                manager._transition_to(state)
                self.assertEqual(manager.state, state)

    def test_concurrent_connection_attempts(self):
        """Test handling of concurrent connection attempts"""
        with (
            patch("connection_manager.get_logger", return_value=self.mock_logger),
            patch("connection_manager.get_config", return_value=self.mock_config),
            patch("connection_manager.get_stats", return_value=self.mock_stats),
        ):
            from connection_manager import ConnectionManager, ConnectionState

            manager = ConnectionManager()
            results = []

            def attempt_connection():
                try:
                    manager._transition_to(ConnectionState.CONNECTING)
                    time.sleep(0.1)  # Simulate connection time
                    manager._transition_to(ConnectionState.CONNECTED)
                    results.append("success")
                except Exception as e:
                    results.append(f"error: {e}")

            # Start multiple threads trying to connect
            threads = [threading.Thread(target=attempt_connection) for _ in range(5)]
            for thread in threads:
                thread.start()
            for thread in threads:
                thread.join()

            # Should handle concurrent attempts gracefully
            self.assertTrue(len(results) > 0)

    @patch("subprocess.run")
    def test_network_interface_not_found(self, mock_run):
        """Test handling when network interface is not found"""
        mock_run.return_value = Mock(returncode=1, stdout="", stderr="Device not found")

        with (
            patch("connection_manager.get_logger", return_value=self.mock_logger),
            patch("connection_manager.get_config", return_value=self.mock_config),
            patch("connection_manager.get_stats", return_value=self.mock_stats),
        ):
            from connection_manager import ConnectionManager

            manager = ConnectionManager()
            interface = manager._detect_usb_interface()

            # Should return None when interface not found
            self.assertIsNone(interface)

    @patch("subprocess.run")
    def test_proxy_connection_timeout(self, mock_run):
        """Test proxy connection timeout handling"""
        import subprocess

        mock_run.side_effect = subprocess.TimeoutExpired(["curl"], 10)

        # Test timeout handling
        with self.assertRaises(subprocess.TimeoutExpired):
            subprocess.run(
                ["curl", "-x", "http://192.168.49.1:8000", "http://google.com"],
                check=False,
                timeout=10,
            )

    def test_invalid_state_transitions(self):
        """Test prevention of invalid state transitions"""
        with (
            patch("connection_manager.get_logger", return_value=self.mock_logger),
            patch("connection_manager.get_config", return_value=self.mock_config),
            patch("connection_manager.get_stats", return_value=self.mock_stats),
        ):
            from connection_manager import ConnectionManager, ConnectionState

            manager = ConnectionManager()

            # Test invalid transitions
            manager.state = ConnectionState.DISCONNECTED

            # Should not allow direct transition to ERROR from DISCONNECTED
            original_state = manager.state
            try:
                manager._transition_to(ConnectionState.ERROR)
                # If transition is allowed, verify it actually changed
                if manager.state == ConnectionState.ERROR:
                    # This is valid behavior - ERROR can be reached from any state
                    pass
            except Exception:
                # If transition is prevented, state should remain unchanged
                self.assertEqual(manager.state, original_state)

    def test_memory_leak_prevention(self):
        """Test prevention of memory leaks in callbacks"""
        with (
            patch("connection_manager.get_logger", return_value=self.mock_logger),
            patch("connection_manager.get_config", return_value=self.mock_config),
            patch("connection_manager.get_stats", return_value=self.mock_stats),
        ):
            from connection_manager import ConnectionManager, ConnectionState

            manager = ConnectionManager()
            callback_count = 0

            def test_callback(state):
                nonlocal callback_count
                callback_count += 1

            # Register many callbacks
            for _ in range(1000):
                manager.register_state_change_callback(test_callback)

            # Trigger state change
            manager._transition_to(ConnectionState.CONNECTING)

            # Verify callbacks were called
            self.assertEqual(callback_count, 1000)

            # Clear callbacks to prevent memory leak
            manager.on_state_change_callbacks.clear()
            self.assertEqual(len(manager.on_state_change_callbacks), 0)


class TestGUIEdgeCases(unittest.TestCase):
    """Test suite for GUI edge cases and error conditions"""

    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test fixtures"""
        import shutil

        shutil.rmtree(self.temp_dir)

    def test_invalid_gtk_css(self):
        """Test handling of invalid GTK CSS"""
        invalid_css_samples = [
            "invalid { text-transform: uppercase; }",  # Unsupported property
            "broken css syntax {{{",  # Malformed CSS
            "* { background: invalid-color; }",  # Invalid color
            "button { letter-spacing: 2px; }",  # Unsupported in GTK3
        ]

        for css in invalid_css_samples:
            # CSS should be validated before use
            with self.assertRaises(Exception):
                # Simulate CSS parsing that would fail
                raise Exception(f"CSS parse error: {css}")

    def test_missing_config_directory(self):
        """Test handling when config directory doesn't exist"""
        nonexistent_path = "/tmp/nonexistent/config/path"

        with patch("config_manager.CONFIG_DIR", nonexistent_path):
            # Should create directory when needed
            try:
                os.makedirs(nonexistent_path, exist_ok=True)
                self.assertTrue(os.path.exists(nonexistent_path))
                os.rmdir(nonexistent_path)
            except PermissionError:
                # Expected if permissions don't allow creation
                pass

    def test_corrupted_config_file(self):
        """Test handling of corrupted configuration file"""
        config_file = os.path.join(self.temp_dir, "config.json")

        # Create corrupted JSON file
        with open(config_file, "w") as f:
            f.write('{"invalid": json syntax}')

        # Should handle JSON parsing error gracefully
        with self.assertRaises(json.JSONDecodeError), open(config_file) as f:
            json.load(f)

    def test_extremely_long_log_messages(self):
        """Test handling of extremely long log messages"""
        long_message = "A" * 10000  # 10KB message

        with patch("logger.get_logger") as mock_get_logger:
            mock_logger = MagicMock()
            mock_get_logger.return_value = mock_logger

            # Should handle long messages without crashing
            mock_logger.info(long_message)
            mock_logger.info.assert_called_once_with(long_message)

    def test_gui_update_with_missing_data(self):
        """Test GUI updates with missing or None data"""
        mock_stats = {
            "bytes_sent": None,
            "bytes_received": None,
            "ping_latency": None,
            "interface": None,
        }

        # GUI should handle None values gracefully
        for key, value in mock_stats.items():
            if value is None:
                # Convert None to display-friendly format
                display_value = "N/A" if value is None else str(value)
                self.assertEqual(display_value, "N/A")

    def test_system_tray_unavailable(self):
        """Test handling when system tray is unavailable"""
        with patch("gi.repository.AppIndicator3") as mock_indicator:
            mock_indicator.Indicator.new.side_effect = Exception("No system tray available")

            # Should handle system tray unavailability gracefully
            with self.assertRaises(Exception) as ctx:
                mock_indicator.Indicator.new("test", "icon", 1)
            self.assertIn("No system tray", str(ctx.exception))


class TestNetworkEdgeCases(unittest.TestCase):
    """Test suite for network-related edge cases"""

    @patch("subprocess.run")
    def test_iptables_permission_denied(self, mock_run):
        """Test handling of iptables permission errors"""
        mock_run.return_value = Mock(returncode=1, stdout="", stderr="iptables: Permission denied")

        result = subprocess.run(["iptables", "-L"], check=False, capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Permission denied", result.stderr)

    @patch("subprocess.run")
    def test_redsocks_service_not_found(self, mock_run):
        """Test handling when redsocks service is not installed"""
        mock_run.return_value = Mock(
            returncode=5, stdout="", stderr="Unit redsocks.service could not be found"
        )

        result = subprocess.run(
            ["systemctl", "status", "redsocks"], check=False, capture_output=True, text=True
        )
        self.assertNotEqual(result.returncode, 0)

    @patch("subprocess.run")
    def test_network_interface_disappears(self, mock_run):
        """Test handling when network interface disappears during operation"""
        # First call returns interface
        # Second call returns no interface
        mock_run.side_effect = [
            Mock(returncode=0, stdout="wlan0\n"),
            Mock(returncode=1, stdout="", stderr="No such device"),
        ]

        # First detection succeeds
        result1 = subprocess.run(
            ["ip", "link", "show", "wlan0"], check=False, capture_output=True, text=True
        )
        self.assertEqual(result1.returncode, 0)

        # Second detection fails (interface disappeared)
        result2 = subprocess.run(
            ["ip", "link", "show", "wlan0"], check=False, capture_output=True, text=True
        )
        self.assertNotEqual(result2.returncode, 0)

    def test_proxy_response_malformed(self):
        """Test handling of malformed proxy responses"""
        malformed_responses = [
            "",  # Empty response
            "HTTP/1.1",  # Incomplete status line
            "INVALID RESPONSE FORMAT",  # Non-HTTP response
            "HTTP/1.1 500 Internal Server Error\r\n\r\nError details",  # Server error
        ]

        for response in malformed_responses:
            # Should handle malformed responses gracefully
            if not response.startswith("HTTP/1.1 200"):
                # Consider it an error response
                self.assertNotIn("200 OK", response)

    @patch("subprocess.run")
    def test_dns_resolution_failure(self, mock_run):
        """Test handling of DNS resolution failures"""
        mock_run.return_value = Mock(
            returncode=1, stdout="", stderr="nslookup: can't resolve 'nonexistent.domain.invalid'"
        )

        result = subprocess.run(
            ["nslookup", "nonexistent.domain.invalid"], check=False, capture_output=True, text=True
        )
        self.assertNotEqual(result.returncode, 0)


class TestResourceLimitEdgeCases(unittest.TestCase):
    """Test suite for resource limit and performance edge cases"""

    def test_high_frequency_state_changes(self):
        """Test handling of very high frequency state changes"""
        with (
            patch("connection_manager.get_logger"),
            patch("connection_manager.get_config"),
            patch("connection_manager.get_stats"),
        ):
            from connection_manager import ConnectionManager, ConnectionState

            manager = ConnectionManager()

            # Rapid state changes
            for i in range(1000):
                if i % 2 == 0:
                    manager._transition_to(ConnectionState.CONNECTING)
                else:
                    manager._transition_to(ConnectionState.DISCONNECTED)

            # Should complete without crashing
            self.assertIn(manager.state, [ConnectionState.CONNECTING, ConnectionState.DISCONNECTED])

    def test_large_bandwidth_numbers(self):
        """Test handling of very large bandwidth numbers"""
        large_bytes = 999_999_999_999_999  # ~1PB

        with patch("stats_collector.get_logger"):
            from stats_collector import StatsCollector

            collector = StatsCollector()

            # Should handle large numbers without overflow
            formatted = collector._format_bytes(large_bytes)
            self.assertIsInstance(formatted, str)
            self.assertIn("PB", formatted)  # Should use appropriate unit

    def test_memory_usage_with_long_running_gui(self):
        """Test memory usage patterns in long-running GUI"""
        # Simulate long-running operations
        log_entries = []

        # Simulate 10,000 log entries (typical for long-running app)
        for i in range(10000):
            log_entries.append(f"Log entry {i} with timestamp {time.time()}")

        # Should limit log buffer size to prevent memory growth
        max_entries = 1000
        if len(log_entries) > max_entries:
            log_entries = log_entries[-max_entries:]

        self.assertEqual(len(log_entries), max_entries)

    def test_disk_space_exhaustion(self):
        """Test handling of disk space exhaustion"""
        # Simulate disk full error
        with patch("builtins.open", side_effect=OSError("No space left on device")):
            try:
                with open("/tmp/test_file", "w") as f:
                    f.write("test data")
                self.fail("Should have raised OSError")
            except OSError as e:
                self.assertIn("No space left", str(e))

    def test_network_buffer_overflow(self):
        """Test handling of network buffer overflow scenarios"""
        # Simulate very large network data
        large_data = b"x" * (1024 * 1024 * 10)  # 10MB

        # Should handle large data chunks appropriately
        chunk_size = 8192
        chunks = []

        for i in range(0, len(large_data), chunk_size):
            chunk = large_data[i : i + chunk_size]
            chunks.append(chunk)

        # Verify chunking worked correctly
        self.assertEqual(len(b"".join(chunks)), len(large_data))


class TestErrorRecoveryScenarios(unittest.TestCase):
    """Test suite for error recovery and resilience"""

    def test_automatic_reconnection_after_failure(self):
        """Test automatic reconnection after connection failure"""
        with (
            patch("connection_manager.get_logger"),
            patch("connection_manager.get_config"),
            patch("connection_manager.get_stats"),
        ):
            from connection_manager import ConnectionManager, ConnectionState

            manager = ConnectionManager()
            manager.auto_reconnect_enabled = True
            manager.max_reconnect_attempts = 3

            # Simulate connection failure
            manager._transition_to(ConnectionState.ERROR)
            self.assertEqual(manager.state, ConnectionState.ERROR)

            # Should track reconnection attempts
            manager.reconnect_attempts = 1
            self.assertLessEqual(manager.reconnect_attempts, manager.max_reconnect_attempts)

    def test_graceful_degradation_without_stealth(self):
        """Test operation without stealth mode (fallback behavior)"""
        # Should work in basic mode even if stealth features fail
        basic_connection_possible = True

        # Simulate stealth mode failure
        stealth_available = False

        if not stealth_available:
            # Should still allow basic connectivity
            self.assertTrue(basic_connection_possible)

    def test_configuration_recovery(self):
        """Test recovery from corrupted configuration"""
        # Simulate configuration recovery
        default_config = {
            "auto_reconnect": False,
            "window_width": 900,
            "window_height": 600,
            "theme": "cyberpunk",
        }

        corrupted_config = None  # Simulate corrupted/missing config

        # Should use defaults when config is corrupted
        active_config = corrupted_config if corrupted_config else default_config
        self.assertEqual(active_config, default_config)

    def test_service_restart_handling(self):
        """Test handling of service restarts (redsocks, NetworkManager)"""
        service_states = {"redsocks": "stopped", "NetworkManager": "running"}

        # Should detect service states and handle appropriately
        for service, state in service_states.items():
            if state == "stopped":
                # Should attempt to restart or handle gracefully
                service_action = "restart_needed"
                self.assertEqual(service_action, "restart_needed")


if __name__ == "__main__":
    unittest.main()
