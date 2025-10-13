#!/usr/bin/env python3
"""
P2 Performance Optimization Tests
Tests for enhanced performance monitoring, reliability management, and resource optimization
"""

import os
import sys
import threading
import time
import unittest
from unittest.mock import MagicMock, Mock, patch

import pytest

# Mark as performance test
pytestmark = pytest.mark.performance

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))


class TestP2PerformanceEnhancements(unittest.TestCase):
    """Test suite for P2 performance optimization features"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.mock_logger = MagicMock()
    
    def test_memory_optimizer_initialization(self):
        """Test memory optimizer initialization and basic functionality"""
        from performance_optimizer import MemoryOptimizer
        
        optimizer = MemoryOptimizer()
        self.assertIsNotNone(optimizer)
        
        # Test memory tracking
        memory_info = optimizer.track_memory_usage()
        self.assertIn('rss', memory_info)
        self.assertIn('timestamp', memory_info)
        self.assertIn('gc_counts', memory_info)
        
    def test_smart_cache_operations(self):
        """Test smart cache with TTL and memory-aware eviction"""
        from performance_optimizer import SmartCache
        
        cache = SmartCache(default_ttl=1, max_size=3)
        
        # Test basic operations
        cache.set('key1', 'value1')
        self.assertEqual(cache.get('key1'), 'value1')
        
        # Test cache stats
        stats = cache.get_stats()
        self.assertIn('size', stats)
        self.assertIn('hit_count', stats)
        self.assertIn('miss_count', stats)
        self.assertEqual(stats['hit_count'], 1)
        
        # Test eviction
        cache.set('key2', 'value2')
        cache.set('key3', 'value3')
        cache.set('key4', 'value4')  # Should evict oldest
        
        self.assertEqual(cache.get_stats()['size'], 3)
        
    def test_resource_manager_functionality(self):
        """Test resource manager monitoring and optimization"""
        from performance_optimizer import ResourceManager
        
        manager = ResourceManager()
        self.assertIsNotNone(manager)
        
        # Test resource summary
        summary = manager.get_resource_summary()
        self.assertIn('cache', summary)
        self.assertIn('gc', summary)
        
        # Test monitoring start/stop
        manager.start_monitoring(interval=1)
        time.sleep(0.1)  # Brief pause
        self.assertTrue(manager._monitoring)
        
        manager.stop_monitoring()
        time.sleep(0.1)  # Brief pause
        self.assertFalse(manager._monitoring)
    
    def test_performance_decorators(self):
        """Test performance monitoring decorators"""
        from performance_optimizer import timed_operation, cached_method
        
        # Test timed operation decorator
        @timed_operation("test_operation")
        def slow_function():
            time.sleep(0.001)  # 1ms delay
            return "result"
        
        result = slow_function()
        self.assertEqual(result, "result")
        
        # Test cached method decorator (mock class)
        class TestClass:
            @cached_method(ttl=5, max_size=10)
            def expensive_computation(self, x):
                return x * 2
        
        obj = TestClass()
        result1 = obj.expensive_computation(5)
        result2 = obj.expensive_computation(5)  # Should be cached
        
        self.assertEqual(result1, 10)
        self.assertEqual(result2, 10)
        
        # Check cache stats
        stats = obj.expensive_computation.cache_stats()
        self.assertIn('hit_count', stats)
    
    def test_high_performance_stats_collector(self):
        """Test high-performance statistics collector"""
        with patch('high_performance_stats.get_logger', return_value=self.mock_logger):
            from high_performance_stats import HighPerformanceStatsCollector
            
            collector = HighPerformanceStatsCollector()
            self.assertIsNotNone(collector)
            
            # Test session management
            collector.start_session()
            self.assertIsNotNone(collector.start_time)
            
            # Test bandwidth update (with mock interface)
            with patch('pathlib.Path.exists', return_value=True):
                with patch('builtins.open', side_effect=[
                    Mock(read=lambda: "1024\n"),  # rx_bytes
                    Mock(read=lambda: "512\n")   # tx_bytes
                ]):
                    collector.update_bandwidth("test0")
            
            # Test performance stats
            perf_stats = collector.get_performance_stats()
            self.assertIn('update_performance', perf_stats)
            self.assertIn('cache_stats', perf_stats)
            self.assertIn('data_structures', perf_stats)
            
            collector.stop_session()
    
    def test_reliability_manager_functionality(self):
        """Test reliability manager and fault tolerance"""
        with patch('reliability_manager.get_logger', return_value=self.mock_logger):
            from reliability_manager import ReliabilityManager, ConnectionHealth
            
            manager = ReliabilityManager()
            self.assertIsNotNone(manager)
            
            # Test failure reporting
            manager.report_failure("test_failure", "Test error message", "test0")
            self.assertEqual(len(manager.failure_history), 1)
            self.assertEqual(manager.failure_history[0].failure_type, "test_failure")
            
            # Test reliability summary
            summary = manager.get_reliability_summary()
            self.assertIn('current_health', summary)
            self.assertIn('reliability_stats', summary)
            
            # Test failure analysis
            analysis = manager.get_failure_analysis()
            self.assertIn('total_failures', analysis)
            self.assertIn('failure_types', analysis)
            
    def test_connection_manager_p2_integration(self):
        """Test connection manager integration with P2 enhancements"""
        with (
            patch("connection_manager.get_logger", return_value=self.mock_logger),
            patch("connection_manager.get_config", return_value=MagicMock()),
            patch("connection_manager.get_stats", return_value=MagicMock()),
        ):
            from connection_manager import ConnectionManager
            
            manager = ConnectionManager()
            
            # Test enhanced status reporting
            status = manager.get_comprehensive_status()
            self.assertIn('state', status)
            
            # Test enhanced interface detection with timing
            with patch('subprocess.run', return_value=Mock(returncode=0, stdout="")):
                interface = manager.detect_interface()
                # Should not raise any exceptions
    
    def test_resource_context_manager(self):
        """Test resource tracking context manager"""
        from performance_optimizer import resource_context
        
        with resource_context("test_operation"):
            # Simulate some work
            time.sleep(0.001)
            data = [i for i in range(100)]
            
        # Should complete without errors
        self.assertEqual(len(data), 100)
    
    def test_memory_optimization_trigger(self):
        """Test memory optimization triggers"""
        from performance_optimizer import MemoryOptimizer
        
        optimizer = MemoryOptimizer()
        
        # Force memory tracking
        optimizer.track_memory_usage()
        time.sleep(0.1)
        optimizer.track_memory_usage()
        
        # Test memory trend calculation
        trend = optimizer.get_memory_trend(minutes=1)
        self.assertIn('growth_rate', trend)
        self.assertIn('avg_usage', trend)
        
        # Test memory optimization
        result = optimizer.optimize_memory()
        self.assertIn('freed_bytes', result)
        self.assertIn('collected_objects', result)
    
    def test_concurrent_performance_monitoring(self):
        """Test performance monitoring under concurrent load"""
        from performance_optimizer import ResourceManager
        
        manager = ResourceManager()
        results = []
        
        def worker_thread(thread_id):
            for i in range(10):
                summary = manager.get_resource_summary()
                results.append(len(summary))
                time.sleep(0.001)
        
        # Start multiple threads
        threads = []
        for i in range(3):
            thread = threading.Thread(target=worker_thread, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for completion
        for thread in threads:
            thread.join()
        
        # Verify all operations completed
        self.assertEqual(len(results), 30)  # 3 threads × 10 operations
        self.assertTrue(all(r > 0 for r in results))  # All summaries non-empty
    
    def test_network_diagnostic_functionality(self):
        """Test network diagnostic capabilities"""
        with patch('reliability_manager.get_logger', return_value=self.mock_logger):
            from reliability_manager import ReliabilityManager
            
            manager = ReliabilityManager()
            
            # Mock ping subprocess call
            mock_result = Mock()
            mock_result.returncode = 0
            mock_result.stdout = "PING 8.8.8.8: 56 data bytes\n64 bytes from 8.8.8.8: icmp_seq=0 ttl=64 time=25.123 ms\n--- 8.8.8.8 ping statistics ---\n1 packets transmitted, 1 received, 0% packet loss"
            mock_result.stderr = ""
            
            with patch('subprocess.run', return_value=mock_result):
                diagnostic = manager._run_ping_diagnostic("8.8.8.8")
            
            self.assertIsNotNone(diagnostic)
            self.assertTrue(diagnostic.success)
            self.assertGreater(diagnostic.latency_ms, 0)
    
    def test_enhanced_connection_error_handling(self):
        """Test enhanced connection error handling and recovery"""
        with (
            patch("connection_manager.get_logger", return_value=self.mock_logger),
            patch("connection_manager.get_config", return_value=MagicMock()),
            patch("connection_manager.get_stats", return_value=MagicMock()),
        ):
            from connection_manager import ConnectionManager, ConnectionState
            
            manager = ConnectionManager()
            
            # Test connection with invalid mode
            manager._connect_thread("invalid_mode")
            
            # Should handle gracefully and set error state
            self.assertEqual(manager.get_state(), ConnectionState.ERROR)
            self.assertIsNotNone(manager.last_error)
            
    def test_performance_baseline_comparison(self):
        """Test performance improvements vs baseline"""
        from performance_optimizer import ResourceManager
        from high_performance_stats import HighPerformanceStatsCollector
        
        # Baseline: Regular operations
        start_time = time.time()
        for i in range(100):
            data = {'test': i, 'timestamp': time.time()}
        baseline_time = time.time() - start_time
        
        # Enhanced: With performance monitoring
        manager = ResourceManager()
        collector = HighPerformanceStatsCollector()
        
        start_time = time.time()
        for i in range(100):
            collector.track_memory_usage()
            summary = manager.get_resource_summary()
        enhanced_time = time.time() - start_time
        
        # Performance should be reasonable (not more than 10x slower)
        # This allows for monitoring overhead
        self.assertLess(enhanced_time, baseline_time * 10)


if __name__ == "__main__":
    unittest.main()