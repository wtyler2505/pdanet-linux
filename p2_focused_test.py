#!/usr/bin/env python3
"""
Focused P2 Performance & Reliability Testing
Tests key P2 enhancements without overwhelming memory usage
"""

import os
import sys
import time
from unittest.mock import Mock, patch, MagicMock

# Add src to path
sys.path.insert(0, "/app/src")

print("=" * 60)
print("PDANET LINUX - P2 FOCUSED TESTING")
print("=" * 60)
print()

test_results = []

def test(name, func):
    """Run a test and track results"""
    try:
        func()
        test_results.append((name, True, None))
        print(f"✓ {name}")
        return True
    except AssertionError as e:
        test_results.append((name, False, str(e)))
        print(f"✗ {name}: {e}")
        return False
    except Exception as e:
        test_results.append((name, False, f"Exception: {e}"))
        print(f"✗ {name}: Exception - {e}")
        return False

# Test Suite 1: P2 Performance Optimizer
print("\n[1/4] P2 PERFORMANCE OPTIMIZER TESTS")
print("-" * 60)

def test_performance_optimizer_imports():
    """Test performance optimizer module imports"""
    from performance_optimizer import (
        MemoryOptimizer, SmartCache, ResourceManager,
        timed_operation, cached_method, resource_context,
        get_resource_manager
    )
    
    assert MemoryOptimizer is not None, "MemoryOptimizer not available"
    assert SmartCache is not None, "SmartCache not available"
    assert ResourceManager is not None, "ResourceManager not available"
    assert get_resource_manager is not None, "get_resource_manager not available"

def test_memory_optimizer_basic():
    """Test MemoryOptimizer basic functionality"""
    from performance_optimizer import MemoryOptimizer
    
    optimizer = MemoryOptimizer()
    
    # Test memory tracking
    memory_info = optimizer.track_memory_usage()
    assert 'rss' in memory_info, "Memory info missing RSS"
    assert 'timestamp' in memory_info, "Memory info missing timestamp"
    
    # Test memory optimization
    result = optimizer.optimize_memory()
    assert 'freed_bytes' in result, "Optimization result missing freed_bytes"

def test_smart_cache_basic():
    """Test SmartCache basic operations"""
    from performance_optimizer import SmartCache
    
    cache = SmartCache(default_ttl=60, max_size=10)
    
    # Test set/get
    cache.set('test_key', 'test_value')
    assert cache.get('test_key') == 'test_value', "Cache get/set failed"
    
    # Test stats
    stats = cache.get_stats()
    assert 'hit_count' in stats, "Cache stats missing hit_count"
    assert stats['hit_count'] == 1, "Hit count incorrect"

def test_resource_manager_basic():
    """Test ResourceManager basic functionality"""
    from performance_optimizer import ResourceManager
    
    manager = ResourceManager()
    
    # Test resource summary
    summary = manager.get_resource_summary()
    assert 'cache' in summary, "Resource summary missing cache"
    assert 'gc' in summary, "Resource summary missing gc"

def test_performance_decorators():
    """Test performance decorators"""
    from performance_optimizer import timed_operation, cached_method
    
    # Test timed operation
    @timed_operation("test_op")
    def test_func():
        return "result"
    
    result = test_func()
    assert result == "result", "Timed operation failed"
    
    # Test cached method
    class TestClass:
        @cached_method(ttl=60)
        def cached_func(self, x):
            return x * 2
    
    obj = TestClass()
    assert obj.cached_func(5) == 10, "Cached method failed"

test("Performance Optimizer Imports", test_performance_optimizer_imports)
test("Memory Optimizer Basic", test_memory_optimizer_basic)
test("Smart Cache Basic", test_smart_cache_basic)
test("Resource Manager Basic", test_resource_manager_basic)
test("Performance Decorators", test_performance_decorators)

# Test Suite 2: P2 High-Performance Stats
print("\n[2/4] P2 HIGH-PERFORMANCE STATS TESTS")
print("-" * 60)

def test_high_performance_stats_imports():
    """Test high-performance stats imports"""
    with patch('high_performance_stats.get_logger'), \
         patch('high_performance_stats.get_resource_manager'):
        from high_performance_stats import HighPerformanceStatsCollector, get_stats
        
        assert HighPerformanceStatsCollector is not None, "HighPerformanceStatsCollector not available"
        assert get_stats is not None, "get_stats function not available"

def test_high_performance_stats_basic():
    """Test high-performance stats basic functionality"""
    with patch('high_performance_stats.get_logger'), \
         patch('high_performance_stats.get_resource_manager'):
        from high_performance_stats import HighPerformanceStatsCollector
        
        collector = HighPerformanceStatsCollector()
        
        # Test session management
        collector.start_session()
        assert collector.start_time is not None, "Session start failed"
        
        collector.stop_session()
        # Should complete without errors

def test_performance_stats_collection():
    """Test performance stats collection"""
    with patch('high_performance_stats.get_logger'), \
         patch('high_performance_stats.get_resource_manager'):
        from high_performance_stats import HighPerformanceStatsCollector
        
        collector = HighPerformanceStatsCollector()
        collector.start_session()
        
        # Test performance stats
        perf_stats = collector.get_performance_stats()
        assert 'update_performance' in perf_stats, "Missing update performance"
        assert 'cache_stats' in perf_stats, "Missing cache stats"

test("High-Performance Stats Imports", test_high_performance_stats_imports)
test("High-Performance Stats Basic", test_high_performance_stats_basic)
test("Performance Stats Collection", test_performance_stats_collection)

# Test Suite 3: P2 Reliability Manager
print("\n[3/4] P2 RELIABILITY MANAGER TESTS")
print("-" * 60)

def test_reliability_manager_imports():
    """Test reliability manager imports"""
    with patch('reliability_manager.get_logger'):
        from reliability_manager import (
            ReliabilityManager, ConnectionHealth, ConnectionFailure,
            NetworkDiagnostic, get_reliability_manager
        )
        
        assert ReliabilityManager is not None, "ReliabilityManager not available"
        assert ConnectionHealth is not None, "ConnectionHealth not available"
        assert get_reliability_manager is not None, "get_reliability_manager not available"

def test_reliability_manager_basic():
    """Test reliability manager basic functionality"""
    with patch('reliability_manager.get_logger'):
        from reliability_manager import ReliabilityManager
        
        manager = ReliabilityManager()
        
        # Test failure reporting
        manager.report_failure("test_failure", "Test error", "test0")
        assert len(manager.failure_history) == 1, "Failure not recorded"
        
        # Test reliability summary
        summary = manager.get_reliability_summary()
        assert 'current_health' in summary, "Missing current health"
        assert 'reliability_stats' in summary, "Missing reliability stats"

def test_network_diagnostics():
    """Test network diagnostic functionality"""
    with patch('reliability_manager.get_logger'):
        from reliability_manager import ReliabilityManager
        
        manager = ReliabilityManager()
        
        # Mock successful ping
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "time=25.123 ms\n0% packet loss"
        mock_result.stderr = ""
        
        with patch('subprocess.run', return_value=mock_result):
            diagnostic = manager._run_ping_diagnostic("8.8.8.8")
            assert diagnostic is not None, "Diagnostic failed"
            assert diagnostic.success == True, "Diagnostic should succeed"

test("Reliability Manager Imports", test_reliability_manager_imports)
test("Reliability Manager Basic", test_reliability_manager_basic)
test("Network Diagnostics", test_network_diagnostics)

# Test Suite 4: P2 Connection Manager Integration
print("\n[4/4] P2 CONNECTION MANAGER INTEGRATION TESTS")
print("-" * 60)

def test_connection_manager_p2_integration():
    """Test connection manager P2 integration"""
    with patch('connection_manager.get_logger'), \
         patch('connection_manager.get_stats'), \
         patch('connection_manager.get_config'):
        from connection_manager import ConnectionManager
        
        conn = ConnectionManager()
        
        # Test P2 components are present
        assert hasattr(conn, 'resource_manager'), "Missing resource_manager"
        assert hasattr(conn, 'reliability_manager'), "Missing reliability_manager"

def test_enhanced_status_reporting():
    """Test enhanced status reporting"""
    with patch('connection_manager.get_logger'), \
         patch('connection_manager.get_stats'), \
         patch('connection_manager.get_config'):
        from connection_manager import ConnectionManager
        
        conn = ConnectionManager()
        
        # Test comprehensive status
        status = conn.get_comprehensive_status()
        assert 'state' in status, "Missing connection state"

def test_performance_monitoring_integration():
    """Test performance monitoring integration"""
    with patch('connection_manager.get_logger'), \
         patch('connection_manager.get_stats'), \
         patch('connection_manager.get_config'):
        from connection_manager import ConnectionManager
        
        conn = ConnectionManager()
        
        # Test timed interface detection
        with patch('subprocess.run', return_value=Mock(returncode=0, stdout="")):
            interface = conn.detect_interface()
            # Should complete without errors

test("Connection Manager P2 Integration", test_connection_manager_p2_integration)
test("Enhanced Status Reporting", test_enhanced_status_reporting)
test("Performance Monitoring Integration", test_performance_monitoring_integration)

# Summary
print("\n" + "=" * 60)
print("P2 FOCUSED TEST SUMMARY")
print("=" * 60)

passed = sum(1 for _, success, _ in test_results if success)
failed = sum(1 for _, success, _ in test_results if not success)
total = len(test_results)

print(f"\nTotal Tests: {total}")
print(f"Passed: {passed} ✓")
print(f"Failed: {failed} ✗")
print(f"Success Rate: {(passed/total)*100:.1f}%")

if failed > 0:
    print(f"\n⚠️  ISSUES FOUND:")
    for name, success, error in test_results:
        if not success:
            print(f"  • {name}: {error}")

print("\n" + "=" * 60)
if failed == 0:
    print("✅ ALL P2 FOCUSED TESTS PASSED")
    print("✅ P2 Performance Optimization - WORKING")
    print("✅ P2 High-Performance Stats - WORKING")
    print("✅ P2 Reliability Manager - WORKING")
    print("✅ P2 Connection Manager Integration - WORKING")
else:
    print("❌ SOME P2 TESTS FAILED")
    print("🔍 Review failed tests above")

print("=" * 60)
sys.exit(0 if failed == 0 else 1)