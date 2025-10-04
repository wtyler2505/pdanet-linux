#!/usr/bin/env python3
"""
Unit tests for ConfigManager
Tests settings persistence, connection profiles, and auto-start management
"""

import unittest
from unittest.mock import Mock, patch, mock_open
import sys
import os
import json
import tempfile

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from config_manager import ConfigManager


class TestConfigManager(unittest.TestCase):
    """Test suite for ConfigManager"""

    def setUp(self):
        """Set up test fixtures with temporary config directory"""
        self.temp_dir = tempfile.mkdtemp()
        with patch('config_manager.get_logger'), \
             patch('config_manager.os.path.expanduser', return_value=self.temp_dir):
            self.config = ConfigManager()

    def test_default_config(self):
        """Test default configuration values"""
        self.assertEqual(self.config.get('auto_reconnect'), True)
        self.assertEqual(self.config.get('stealth_level'), 3)
        self.assertEqual(self.config.get('connection_mode'), 'wifi')

    def test_get_set_config(self):
        """Test getting and setting configuration values"""
        self.config.set('test_key', 'test_value')
        self.assertEqual(self.config.get('test_key'), 'test_value')

    def test_get_nonexistent_key(self):
        """Test getting non-existent key returns None"""
        self.assertIsNone(self.config.get('nonexistent_key'))

    def test_get_with_default(self):
        """Test getting key with default value"""
        value = self.config.get('nonexistent_key', 'default_value')
        self.assertEqual(value, 'default_value')

    @patch('builtins.open', new_callable=mock_open)
    @patch('json.dump')
    def test_save_config(self, mock_json_dump, mock_file):
        """Test configuration persistence"""
        self.config.set('test_key', 'test_value')
        self.config.save()

        mock_file.assert_called()
        mock_json_dump.assert_called_once()

    def test_profile_management(self):
        """Test connection profile creation and retrieval"""
        profile = {
            'name': 'Test Profile',
            'ssid': 'TestSSID',
            'interface': 'wlan0',
            'stealth_level': 3
        }

        self.config.add_profile(profile)
        profiles = self.config.get_profiles()

        self.assertEqual(len(profiles), 1)
        self.assertEqual(profiles[0]['name'], 'Test Profile')

    def test_delete_profile(self):
        """Test profile deletion"""
        profile = {'name': 'Test Profile', 'ssid': 'TestSSID'}
        self.config.add_profile(profile)

        self.config.delete_profile('Test Profile')
        profiles = self.config.get_profiles()

        self.assertEqual(len(profiles), 0)

    def test_auto_start_desktop_file(self):
        """Test .desktop file path for auto-start"""
        desktop_file = self.config.get_autostart_desktop_file()
        self.assertTrue(desktop_file.endswith('.desktop'))
        self.assertIn('autostart', desktop_file)

    @patch('os.path.exists', return_value=True)
    def test_auto_start_enabled(self, mock_exists):
        """Test auto-start detection when enabled"""
        self.assertTrue(self.config.is_autostart_enabled())

    @patch('os.path.exists', return_value=False)
    def test_auto_start_disabled(self, mock_exists):
        """Test auto-start detection when disabled"""
        self.assertFalse(self.config.is_autostart_enabled())


if __name__ == '__main__':
    unittest.main()
