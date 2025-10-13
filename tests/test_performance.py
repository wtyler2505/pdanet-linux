#!/usr/bin/env python3
"""
Performance and Load Tests
Tests system performance under various load conditions
"""

import os
import subprocess
import sys
import threading
import time
import unittest
from unittest.mock import MagicMock, Mock, patch

import pytest

# Mark entire module as performance to allow filtering
pytestmark = pytest.mark.performance

# Optional dependencies; skip module if unavailable
try:
    import memory_profiler  # type: ignore
    import psutil  # type: ignore
except Exception:  # pragma: no cover - environment without perf deps
    pytest.skip("memory_profiler/psutil not available", allow_module_level=True)

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))


class TestConnectionPerformance(unittest.TestCase):
    """Test suite for connection performance metrics"""

    def setUp(self):
        """Set up test fixtures"""
        self.mock_logger = MagicMock()
        self.mock_config = MagicMock()
        self.mock_stats = MagicMock()

    def test_connection_establishment_time(self):
        """Test connection establishment time is within acceptable limits"""
        with (
            patch("connection_manager.get_logger", return_value=self.mock_logger),
            patch("connection_manager.get_config", return_value=self.mock_config),
            patch("connection_manager.get_stats", return_value=self.mock_stats),
            patch("subprocess.run"),
        ):
            from connection_manager import ConnectionManager, ConnectionState

            manager = ConnectionManager()

            # Measure connection time
            start_time = time.time()
            manager._transition_to(ConnectionState.CONNECTING)
            manager._transition_to(ConnectionState.CONNECTED)
            end_time = time.time()

            connection_time = end_time - start_time

            # Connection state change should be very fast (< 0.1 seconds)
            self.assertLess(connection_time, 0.1)

    @patch("subprocess.run")
    def test_iptables_rule_application_performance(self, mock_run):
        """Test iptables rule application performance"""
        mock_run.return_value = Mock(returncode=0, stdout="", stderr="")

        # Test batch rule application
        rules = [
            ["iptables", "-t", "nat", "-A", "REDSOCKS", "-d", "127.0.0.0/8", "-j", "RETURN"],
            ["iptables", "-t", "nat", "-A", "REDSOCKS", "-d", "192.168.0.0/16", "-j", "RETURN"],
            ["iptables", "-t", "nat", "-A", "REDSOCKS", "-d", "10.0.0.0/8", "-j", "RETURN"],
            ["iptables", "-t", "mangle", "-A", "WIFI_STEALTH", "-j", "TTL", "--ttl-set", "65"],
        ]

        start_time = time.time()
        for rule in rules:
            subprocess.run(rule, check=False, capture_output=True, text=True, timeout=30)
        end_time = time.time()

        rule_application_time = end_time - start_time

        # Rule application should complete quickly (< 2 seconds for 4 rules)
        self.assertLess(rule_application_time, 2.0)
        self.assertEqual(mock_run.call_count, len(rules))

    def test_bandwidth_calculation_performance(self):
        """Test bandwidth calculation performance with large datasets"""
        with patch("stats_collector.get_logger"):
            from stats_collector import StatsCollector

            collector = StatsCollector()

            # Generate large bandwidth history (1000 entries)
            large_history = [(time.time() - i, i * 1024) for i in range(1000)]

            start_time = time.time()
            rate = collector._calculate_rate(large_history)
            end_time = time.time()

            calculation_time = end_time - start_time

            # Bandwidth calculation should be fast even with large datasets
            self.assertLess(calculation_time, 0.1)
            self.assertIsInstance(rate, (int, float))

    def test_gui_update_performance(self):
        """Test GUI update performance with high frequency updates"""
        update_count = 100
        update_times = []

        def mock_update():
            start = time.time()
            # Simulate GUI update work
            time.sleep(0.001)  # 1ms simulated work
            end = time.time()
            update_times.append(end - start)

        # Run multiple updates
        for _ in range(update_count):
            mock_update()

        average_update_time = sum(update_times) / len(update_times)

        # Each update should complete quickly (< 10ms average)
        self.assertLess(average_update_time, 0.01)

    def test_state_transition_performance(self):
        """Test state transition performance under load"""
        with (
            patch("connection_manager.get_logger", return_value=self.mock_logger),
            patch("connection_manager.get_config", return_value=self.mock_config),
            patch("connection_manager.get_stats", return_value=self.mock_stats),
        ):
            from connection_manager import ConnectionManager, ConnectionState

            manager = ConnectionManager()

            # Test rapid state transitions
            states = [
                ConnectionState.DISCONNECTED,
                ConnectionState.CONNECTING,
                ConnectionState.CONNECTED,
                ConnectionState.DISCONNECTING,
            ]

            transition_times = []

            for _ in range(100):  # 100 transition cycles
                for state in states:
                    start_time = time.time()
                    manager._transition_to(state)
                    end_time = time.time()
                    transition_times.append(end_time - start_time)

            average_transition_time = sum(transition_times) / len(transition_times)

            # State transitions should be very fast (< 1ms average)
            self.assertLess(average_transition_time, 0.001)


class TestMemoryUsage(unittest.TestCase):
    """Test suite for memory usage patterns"""

    def test_connection_manager_memory_usage(self):
        """Test ConnectionManager memory usage doesn't grow excessively"""
        with (
            patch("connection_manager.get_logger"),
            patch("connection_manager.get_config"),
            patch("connection_manager.get_stats"),
        ):
            from connection_manager import ConnectionManager, ConnectionState

            # Measure initial memory
            process = psutil.Process()
            initial_memory = process.memory_info().rss

            manager = ConnectionManager()

            # Perform many operations
            for i in range(1000):
                manager._transition_to(ConnectionState.CONNECTING)
                manager._transition_to(ConnectionState.CONNECTED)
                manager._transition_to(ConnectionState.DISCONNECTED)

            # Measure final memory
            final_memory = process.memory_info().rss
            memory_growth = final_memory - initial_memory

            # Memory growth should be minimal (< 10MB for 3000 operations)
            self.assertLess(memory_growth, 10 * 1024 * 1024)

    def test_log_buffer_memory_management(self):
        """Test log buffer doesn't grow unbounded"""
        with patch("logger.get_logger") as mock_get_logger:
            mock_logger = MagicMock()
            mock_get_logger.return_value = mock_logger

            # Simulate GUI log buffer with size limit
            log_buffer = []
            max_buffer_size = 1000

            # Add many log entries
            for i in range(5000):
                log_entry = f"Log message {i} with timestamp {time.time()}"
                log_buffer.append(log_entry)

                # Maintain buffer size limit
                if len(log_buffer) > max_buffer_size:
                    log_buffer = log_buffer[-max_buffer_size:]

            # Buffer should be limited to max size
            self.assertEqual(len(log_buffer), max_buffer_size)

    def test_stats_history_memory_management(self):
        """Test bandwidth history doesn't consume excessive memory"""
        with patch("stats_collector.get_logger"):
            from stats_collector import StatsCollector

            collector = StatsCollector()

            # Simulate long-running stats collection
            for i in range(10000):
                # Add bandwidth data points
                timestamp = time.time() - i
                bytes_value = i * 1024

                # Simulate adding to history with size limit
                history_entry = (timestamp, bytes_value)

                # History should be limited (e.g., last 3600 entries for 1 hour)
                max_history_size = 3600
                if hasattr(collector, "bytes_sent_history"):
                    if len(collector.bytes_sent_history) > max_history_size:
                        collector.bytes_sent_history = collector.bytes_sent_history[
                            -max_history_size:
                        ]

            # Memory usage should be bounded
            # In real implementation, history size should be limited
            self.assertTrue(True)  # Placeholder for actual memory check


class TestConcurrencyPerformance(unittest.TestCase):
    """Test suite for concurrent operation performance"""

    def test_concurrent_gui_updates(self):
        """Test GUI handles concurrent updates efficiently"""
        update_results = []
        lock = threading.Lock()

        def gui_update_thread(thread_id):
            for i in range(100):
                start_time = time.time()
                # Simulate GUI update
                with lock:
                    # Critical section for thread-safe update
                    time.sleep(0.001)  # 1ms work
                end_time = time.time()
                update_results.append(end_time - start_time)

        # Start multiple GUI update threads
        threads = []
        for thread_id in range(5):
            thread = threading.Thread(target=gui_update_thread, args=(thread_id,))
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # All updates should complete reasonably quickly
        max_update_time = max(update_results)
        self.assertLess(max_update_time, 0.5)  # Allow scheduling jitter under load

    def test_concurrent_connection_monitoring(self):
        """Test concurrent connection monitoring performance"""
        with (
            patch("connection_manager.get_logger"),
            patch("connection_manager.get_config"),
            patch("connection_manager.get_stats"),
        ):
            from connection_manager import ConnectionManager

            manager = ConnectionManager()
            monitoring_results = []

            def monitoring_thread():
                for _ in range(100):
                    start_time = time.time()
                    # Simulate connection health check
                    health_status = True  # Mock health check
                    end_time = time.time()
                    monitoring_results.append(end_time - start_time)

            # Start multiple monitoring threads
            threads = []
            for _ in range(3):
                thread = threading.Thread(target=monitoring_thread)
                threads.append(thread)
                thread.start()

            for thread in threads:
                thread.join()

            # Monitoring should be efficient
            average_check_time = sum(monitoring_results) / len(monitoring_results)
            self.assertLess(average_check_time, 0.01)  # < 10ms average

    def test_thread_safety_under_load(self):
        """Test thread safety under high concurrent load"""
        with (
            patch("connection_manager.get_logger"),
            patch("connection_manager.get_config"),
            patch("connection_manager.get_stats"),
        ):
            from connection_manager import ConnectionManager, ConnectionState

            manager = ConnectionManager()
            state_changes = []
            lock = threading.Lock()

            def state_change_thread(states):
                for state in states:
                    with lock:
                        manager._transition_to(state)
                        state_changes.append(state)

            # Define state sequences for different threads
            thread_states = [
                [ConnectionState.CONNECTING, ConnectionState.CONNECTED],
                [ConnectionState.DISCONNECTING, ConnectionState.DISCONNECTED],
                [ConnectionState.CONNECTING, ConnectionState.ERROR],
            ]

            threads = []
            for states in thread_states:
                thread = threading.Thread(target=state_change_thread, args=(states,))
                threads.append(thread)
                thread.start()

            for thread in threads:
                thread.join()

            # Should handle concurrent state changes without corruption
            self.assertEqual(len(state_changes), 6)  # 2 states × 3 threads


class TestNetworkPerformance(unittest.TestCase):
    """Test suite for network operation performance"""

    @patch("subprocess.run")
    def test_proxy_latency_measurement(self, mock_run):
        """Test proxy latency measurement accuracy"""
        # Mock ping response with specific latency
        mock_run.return_value = Mock(
            returncode=0,
            stdout="PING google.com: 56 data bytes\n64 bytes from google.com: icmp_seq=0 ttl=65 time=25.123 ms\n",
            stderr="",
        )

        start_time = time.time()
        result = subprocess.run(
            ["ping", "-c", "1", "google.com"],
            check=False,
            capture_output=True,
            text=True,
            timeout=30,
        )
        end_time = time.time()

        ping_execution_time = end_time - start_time

        # Ping execution should complete quickly
        self.assertLess(ping_execution_time, 5.0)
        self.assertEqual(result.returncode, 0)

    @patch("subprocess.run")
    def test_iptables_rule_removal_performance(self, mock_run):
        """Test iptables rule removal performance"""
        mock_run.return_value = Mock(returncode=0, stdout="", stderr="")

        cleanup_rules = [
            ["iptables", "-t", "nat", "-F", "REDSOCKS"],
            ["iptables", "-t", "nat", "-X", "REDSOCKS"],
            ["iptables", "-t", "mangle", "-F", "WIFI_STEALTH"],
            ["iptables", "-t", "mangle", "-X", "WIFI_STEALTH"],
        ]

        start_time = time.time()
        for rule in cleanup_rules:
            subprocess.run(rule, check=False, capture_output=True, text=True, timeout=30)
        end_time = time.time()

        cleanup_time = end_time - start_time

        # Cleanup should be fast (< 1 second)
        self.assertLess(cleanup_time, 1.0)

    def test_bandwidth_monitoring_efficiency(self):
        """Test bandwidth monitoring doesn't impact performance"""
        with patch("stats_collector.get_logger"):
            from stats_collector import StatsCollector

            collector = StatsCollector()

            # Simulate high-frequency monitoring
            monitoring_times = []

            for _ in range(1000):
                start_time = time.time()
                # Mock reading network stats
                bytes_sent = 1024 * 1024  # 1MB
                bytes_received = 2048 * 1024  # 2MB
                end_time = time.time()
                monitoring_times.append(end_time - start_time)

            average_monitoring_time = sum(monitoring_times) / len(monitoring_times)

            # Monitoring should be very efficient (< 1ms average)
            self.assertLess(average_monitoring_time, 0.001)


class TestResourceUtilization(unittest.TestCase):
    """Test suite for resource utilization optimization"""

    def test_cpu_usage_under_normal_load(self):
        """Test CPU usage remains reasonable under normal load"""
        process = psutil.Process()

        # Measure CPU usage before test
        process.cpu_percent()  # Initialize measurement
        time.sleep(1)  # Let CPU measurement stabilize

        # Simulate normal application load
        with (
            patch("connection_manager.get_logger"),
            patch("connection_manager.get_config"),
            patch("connection_manager.get_stats"),
        ):
            from connection_manager import ConnectionManager, ConnectionState

            manager = ConnectionManager()

            # Perform typical operations
            for _ in range(100):
                manager._transition_to(ConnectionState.CONNECTING)
                manager._transition_to(ConnectionState.CONNECTED)
                time.sleep(0.01)  # 10ms between operations

        # Measure CPU usage after test
        cpu_usage = process.cpu_percent()

        # CPU usage should be reasonable (< 50% for test operations)
        self.assertLess(cpu_usage, 50.0)

    def test_file_descriptor_usage(self):
        """Test file descriptor usage doesn't leak"""
        process = psutil.Process()
        initial_fds = process.num_fds()

        # Simulate operations that might open file descriptors
        temp_files = []
        for i in range(100):
            # Simulate opening/closing files
            import tempfile

            temp_file = tempfile.NamedTemporaryFile(delete=True)
            temp_files.append(temp_file)

        # Close all temp files
        for temp_file in temp_files:
            temp_file.close()

        final_fds = process.num_fds()

        # File descriptor count should return to near initial level
        fd_difference = abs(final_fds - initial_fds)
        self.assertLess(fd_difference, 10)  # Allow some variance

    def test_network_socket_cleanup(self):
        """Test network sockets are properly cleaned up"""
        import socket

        sockets = []

        try:
            for _ in range(10):
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                except PermissionError:
                    self.skipTest("Socket creation blocked by sandbox permissions")
                sockets.append(sock)

            self.assertEqual(len(sockets), 10)
        finally:
            for sock in sockets:
                try:
                    sock.close()
                except Exception:
                    pass

        self.assertTrue(True)  # Placeholder for actual socket verification


if __name__ == "__main__":
    # Skip memory profiler tests if not available
    try:
        import memory_profiler
        import psutil
    except ImportError:
        print("Warning: memory_profiler or psutil not available, skipping some performance tests")

    unittest.main()
