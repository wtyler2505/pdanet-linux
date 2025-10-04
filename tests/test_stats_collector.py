#!/usr/bin/env python3
"""
Unit tests for StatsCollector
Tests bandwidth tracking, ping testing, and rate calculations
"""

import unittest
from unittest.mock import Mock, patch, mock_open
import sys
import os
import time

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from stats_collector import StatsCollector


class TestStatsCollector(unittest.TestCase):
    """Test suite for StatsCollector"""

    def setUp(self):
        """Set up test fixtures"""
        with patch('stats_collector.get_logger'):
            self.collector = StatsCollector()

    def test_initial_stats(self):
        """Test initial statistics are zero"""
        stats = self.collector.get_stats()
        self.assertEqual(stats['bytes_sent'], 0)
        self.assertEqual(stats['bytes_received'], 0)
        self.assertEqual(stats['upload_rate'], 0)
        self.assertEqual(stats['download_rate'], 0)

    @patch('builtins.open', new_callable=mock_open, read_data='1024')
    def test_read_interface_bytes(self, mock_file):
        """Test reading interface bytes from /sys/class/net"""
        bytes_val = self.collector._read_interface_bytes('eth0', 'tx_bytes')
        self.assertEqual(bytes_val, 1024)

    @patch('builtins.open', side_effect=FileNotFoundError)
    def test_read_interface_bytes_error(self, mock_file):
        """Test error handling when interface doesn't exist"""
        bytes_val = self.collector._read_interface_bytes('nonexistent0', 'tx_bytes')
        self.assertEqual(bytes_val, 0)

    def test_calculate_rate(self):
        """Test rate calculation from rolling window"""
        # Simulate bytes transferred over time
        self.collector.bytes_sent_history = [(time.time() - 2, 0), (time.time(), 2048)]
        rate = self.collector._calculate_rate(self.collector.bytes_sent_history)

        # Rate should be approximately 1024 bytes/sec
        self.assertGreater(rate, 900)
        self.assertLess(rate, 1100)

    def test_rolling_window_size(self):
        """Test rolling window maintains max size"""
        # Add more entries than window size
        for i in range(15):
            self.collector.bytes_sent_history.append((time.time(), i * 1024))

        self.collector._trim_history(self.collector.bytes_sent_history)
        self.assertLessEqual(len(self.collector.bytes_sent_history), 10)

    @patch('stats_collector.subprocess.run')
    def test_ping_success(self, mock_run):
        """Test successful ping measurement"""
        mock_run.return_value = Mock(
            returncode=0,
            stdout="rtt min/avg/max/mdev = 10.1/15.5/20.2/3.1 ms"
        )

        latency = self.collector.test_ping('8.8.8.8')
        self.assertIsNotNone(latency)
        self.assertGreater(latency, 0)

    @patch('stats_collector.subprocess.run')
    def test_ping_failure(self, mock_run):
        """Test ping failure handling"""
        mock_run.return_value = Mock(returncode=1, stdout="")

        latency = self.collector.test_ping('192.168.1.1')
        self.assertIsNone(latency)

    def test_format_bytes(self):
        """Test human-readable byte formatting"""
        self.assertEqual(self.collector.format_bytes(512), "512 B")
        self.assertEqual(self.collector.format_bytes(1024), "1.00 KB")
        self.assertEqual(self.collector.format_bytes(1048576), "1.00 MB")
        self.assertEqual(self.collector.format_bytes(1073741824), "1.00 GB")

    def test_format_rate(self):
        """Test rate formatting with /s suffix"""
        self.assertEqual(self.collector.format_rate(512), "512 B/s")
        self.assertEqual(self.collector.format_rate(2048), "2.00 KB/s")


if __name__ == '__main__':
    unittest.main()
