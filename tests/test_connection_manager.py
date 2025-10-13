#!/usr/bin/env python3
"""
Unit tests for ConnectionManager
Tests state machine, auto-reconnect, and connection orchestration
"""

import os
import sys
import unittest
from unittest.mock import Mock, patch

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from connection_manager import ConnectionManager, ConnectionState


class TestConnectionManager(unittest.TestCase):
    """Test suite for ConnectionManager"""

    def setUp(self):
        """Set up test fixtures"""
        with (
            patch("connection_manager.get_logger"),
            patch("connection_manager.get_stats"),
            patch("connection_manager.get_config"),
        ):
            self.manager = ConnectionManager()

    def test_initial_state(self):
        """Test initial state is DISCONNECTED"""
        self.assertEqual(self.manager.state, ConnectionState.DISCONNECTED)
        self.assertIsNone(self.manager.current_interface)
        self.assertFalse(self.manager.proxy_available)

    def test_state_transitions(self):
        """Test valid state transitions"""
        # DISCONNECTED -> CONNECTING
        self.manager.state = ConnectionState.DISCONNECTED
        self.manager._transition_to(ConnectionState.CONNECTING)
        self.assertEqual(self.manager.state, ConnectionState.CONNECTING)

        # CONNECTING -> CONNECTED
        self.manager._transition_to(ConnectionState.CONNECTED)
        self.assertEqual(self.manager.state, ConnectionState.CONNECTED)

        # CONNECTED -> DISCONNECTING
        self.manager._transition_to(ConnectionState.DISCONNECTING)
        self.assertEqual(self.manager.state, ConnectionState.DISCONNECTING)

        # DISCONNECTING -> DISCONNECTED
        self.manager._transition_to(ConnectionState.DISCONNECTED)
        self.assertEqual(self.manager.state, ConnectionState.DISCONNECTED)

    def test_auto_reconnect_disabled_by_default(self):
        """Test auto-reconnect is disabled by default"""
        self.assertFalse(self.manager.auto_reconnect_enabled)
        self.assertEqual(self.manager.reconnect_attempts, 0)

    def test_max_reconnect_attempts(self):
        """Test max reconnect attempts configuration"""
        self.assertEqual(self.manager.max_reconnect_attempts, 3)
        self.assertEqual(self.manager.reconnect_delay, 5)

    @patch("connection_manager.subprocess.run")
    def test_detect_usb_interface(self, mock_run):
        """Test USB interface detection"""
        # Mock successful USB interface detection
        mock_run.return_value = Mock(returncode=0, stdout="usb0\n")

        interface = self.manager._detect_usb_interface()
        self.assertEqual(interface, "usb0")

    @patch("connection_manager.subprocess.run")
    def test_detect_wifi_interface(self, mock_run):
        """Test WiFi interface detection"""
        # Mock successful WiFi interface detection
        mock_run.return_value = Mock(returncode=0, stdout="wlan0\n")

        interface = self.manager._detect_wifi_interface()
        self.assertEqual(interface, "wlan0")

    def test_observer_pattern_callbacks(self):
        """Test observer pattern for state change notifications"""
        callback_called = []

        def callback(state):
            callback_called.append(state)

        self.manager.add_state_callback(callback)
        self.manager._transition_to(ConnectionState.CONNECTING)

        self.assertEqual(len(callback_called), 1)
        self.assertEqual(callback_called[0], ConnectionState.CONNECTING)


if __name__ == "__main__":
    unittest.main()
