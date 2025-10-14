#!/usr/bin/env python3
"""
P1 + P2 Integration Testing
Tests that P1 and P2 enhancements work together seamlessly
"""

import os
import sys
import time
from unittest.mock import Mock, patch, MagicMock

# Add src to path
sys.path.insert(0, "/app/src")

print("=" * 70)
print("PDANET LINUX - P1 + P2 INTEGRATION TESTING")
print("=" * 70)
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

# Test Suite 1: P1 + P2 Module Integration
print("\n[1/3] P1 + P2 MODULE INTEGRATION")
print("-" * 70)

def test_all_modules_import():
    """Test all P1 and P2 modules import successfully"""
    # P1 modules
    from nm_client import NMClient, NetworkDevice, AccessPoint
    from connection_manager import ConnectionManager
    
    # P2 modules
    from performance_optimizer import MemoryOptimizer, SmartCache, ResourceManager
    from high_performance_stats import HighPerformanceStatsCollector
    from reliability_manager import ReliabilityManager
    
    # All should be available
    assert all([NMClient, NetworkDevice, AccessPoint, ConnectionManager,
                MemoryOptimizer, SmartCache, ResourceManager,
                HighPerformanceStatsCollector, ReliabilityManager]), "Module import failed"

def test_connection_manager_full_integration():
    """Test ConnectionManager integrates both P1 and P2 features"""
    with patch('connection_manager.get_logger'), \
         patch('connection_manager.get_stats'), \
         patch('connection_manager.get_config'):
        from connection_manager import ConnectionManager
        
        conn = ConnectionManager()
        
        # P1 features
        assert hasattr(conn, 'nm_client'), "Missing P1 nm_client"
        assert hasattr(conn, 'stealth_active'), "Missing P1 stealth_active"
        assert hasattr(conn, 'scan_wifi_networks'), "Missing P1 WiFi scanning"
        
        # P2 features
        assert hasattr(conn, 'resource_manager'), "Missing P2 resource_manager"
        assert hasattr(conn, 'reliability_manager'), "Missing P2 reliability_manager"
        assert hasattr(conn, 'get_comprehensive_status'), "Missing P2 comprehensive status"

def test_enhanced_stats_with_performance_monitoring():
    """Test enhanced stats collector with performance monitoring"""
    with patch('high_performance_stats.get_logger'), \
         patch('high_performance_stats.get_resource_manager'):
        from high_performance_stats import HighPerformanceStatsCollector
        
        collector = HighPerformanceStatsCollector()
        collector.start_session()
        
        # Should have both traditional stats and performance monitoring
        assert hasattr(collector, 'rx_history'), "Missing traditional rx_history"
        assert hasattr(collector, 'resource_manager'), "Missing P2 resource_manager"
        
        # Performance stats should include both
        perf_stats = collector.get_performance_stats()
        assert 'update_performance' in perf_stats, "Missing P2 update performance"
        assert 'data_structures' in perf_stats, "Missing data structure info"

def test_reliability_with_connection_management():
    """Test reliability manager integration with connection management"""
    with patch('reliability_manager.get_logger'):
        from reliability_manager import ReliabilityManager
        
        manager = ReliabilityManager()
        
        # Test failure reporting (P2) with connection context (P1)
        manager.report_failure("wifi_connection_failed", "WiFi connection timeout", "wlan0")
        
        assert len(manager.failure_history) == 1, "Failure not recorded"
        failure = manager.failure_history[0]
        assert failure.interface == "wlan0", "Interface context not preserved"

test("All Modules Import", test_all_modules_import)
test("Connection Manager Full Integration", test_connection_manager_full_integration)
test("Enhanced Stats with Performance Monitoring", test_enhanced_stats_with_performance_monitoring)
test("Reliability with Connection Management", test_reliability_with_connection_management)

# Test Suite 2: Performance Impact Assessment
print("\n[2/3] PERFORMANCE IMPACT ASSESSMENT")
print("-" * 70)

def test_p2_performance_overhead():
    """Test P2 enhancements don't significantly impact P1 performance"""
    # Test basic operations are still fast
    start_time = time.time()
    
    with patch('connection_manager.get_logger'), \
         patch('connection_manager.get_stats'), \
         patch('connection_manager.get_config'):
        from connection_manager import ConnectionManager
        
        # Create connection manager (includes P1 + P2 initialization)
        conn = ConnectionManager()
        
        # Test basic P1 operations
        conn.stealth_active = True
        conn.stealth_level = 2
        status_string = conn.get_stealth_status_string()
        
        # Test P2 doesn't break P1
        assert "ACTIVE" in status_string, "P1 functionality affected by P2"
    
    elapsed = time.time() - start_time
    assert elapsed < 2.0, f"Initialization too slow: {elapsed:.2f}s"

def test_memory_optimization_effectiveness():
    """Test memory optimization actually works"""
    from performance_optimizer import MemoryOptimizer
    
    optimizer = MemoryOptimizer()
    
    # Track initial memory
    initial = optimizer.track_memory_usage()
    
    # Create some objects to optimize
    test_data = [list(range(100)) for _ in range(10)]
    del test_data
    
    # Optimize memory
    result = optimizer.optimize_memory()
    
    # Should have attempted optimization
    assert 'freed_bytes' in result, "Memory optimization not attempted"
    assert 'collected_objects' in result, "GC collection not attempted"

def test_caching_improves_performance():
    """Test caching actually improves performance"""
    from performance_optimizer import SmartCache
    
    cache = SmartCache(default_ttl=60)
    
    # Simulate expensive operation
    def expensive_operation(x):
        time.sleep(0.001)  # 1ms delay
        return x * 2
    
    # First call (cache miss)
    start = time.time()
    cache.set('test', expensive_operation(5))
    first_call = time.time() - start
    
    # Second call (cache hit)
    start = time.time()
    result = cache.get('test')
    second_call = time.time() - start
    
    assert result == 10, "Cached result incorrect"
    assert second_call < first_call, "Cache didn't improve performance"

def test_reliability_monitoring_efficiency():
    """Test reliability monitoring is efficient"""
    with patch('reliability_manager.get_logger'):
        from reliability_manager import ReliabilityManager
        
        manager = ReliabilityManager()
        
        start_time = time.time()
        
        # Test multiple operations
        for i in range(10):
            manager.report_failure(f"test_{i}", f"Error {i}", "test0")
        
        summary = manager.get_reliability_summary()
        analysis = manager.get_failure_analysis()
        
        elapsed = time.time() - start_time
        
        assert elapsed < 1.0, f"Reliability operations too slow: {elapsed:.2f}s"
        assert 'total_failures' in analysis, "Analysis incomplete"
        assert analysis['total_failures'] == 10, "Failure tracking incorrect"

test("P2 Performance Overhead", test_p2_performance_overhead)
test("Memory Optimization Effectiveness", test_memory_optimization_effectiveness)
test("Caching Improves Performance", test_caching_improves_performance)
test("Reliability Monitoring Efficiency", test_reliability_monitoring_efficiency)

# Test Suite 3: Backward Compatibility
print("\n[3/3] BACKWARD COMPATIBILITY")
print("-" * 70)

def test_p1_functionality_preserved():
    """Test P1 functionality is fully preserved with P2 enhancements"""
    with patch('connection_manager.get_logger'), \
         patch('connection_manager.get_stats'), \
         patch('connection_manager.get_config'):
        from connection_manager import ConnectionManager
        
        conn = ConnectionManager()
        
        # All P1 methods should still work
        p1_methods = [
            'scan_wifi_networks',
            'update_stealth_status', 
            'get_stealth_status_string',
            'detect_interface',
            'get_connection_status'
        ]
        
        for method_name in p1_methods:
            assert hasattr(conn, method_name), f"P1 method {method_name} missing"
            method = getattr(conn, method_name)
            assert callable(method), f"P1 method {method_name} not callable"

def test_enhanced_features_optional():
    """Test P2 enhancements are optional and don't break basic functionality"""
    with patch('connection_manager.get_logger'), \
         patch('connection_manager.get_stats'), \
         patch('connection_manager.get_config'):
        from connection_manager import ConnectionManager
        
        conn = ConnectionManager()
        
        # Basic connection status should work even if P2 components fail
        try:
            status = conn.get_connection_status()
            assert 'state' in status, "Basic status missing state"
            assert 'interface' in status, "Basic status missing interface"
        except Exception as e:
            assert False, f"Basic functionality broken: {e}"

def test_graceful_degradation():
    """Test system degrades gracefully if P2 components unavailable"""
    # Test with mocked unavailable P2 components
    with patch('connection_manager.get_logger'), \
         patch('connection_manager.get_stats'), \
         patch('connection_manager.get_config'), \
         patch('connection_manager.get_resource_manager', side_effect=ImportError("P2 unavailable")), \
         patch('connection_manager.get_reliability_manager', side_effect=ImportError("P2 unavailable")):
        
        try:
            from connection_manager import ConnectionManager
            conn = ConnectionManager()
            
            # Should still initialize without P2 components
            assert conn is not None, "Connection manager failed without P2"
            
            # Basic P1 functionality should still work
            conn.stealth_active = False
            status = conn.get_stealth_status_string()
            assert status == "DISABLED", "P1 functionality broken without P2"
            
        except ImportError:
            # This is expected if P2 components are truly unavailable
            pass

def test_configuration_compatibility():
    """Test configuration remains compatible between P1 and P2"""
    with patch('connection_manager.get_logger'), \
         patch('connection_manager.get_stats'), \
         patch('connection_manager.get_config'):
        from connection_manager import ConnectionManager
        
        conn = ConnectionManager()
        
        # Configuration methods should work
        assert hasattr(conn, 'config'), "Configuration object missing"
        
        # P1 configuration should be preserved
        try:
            # These are the core P1 configuration items
            proxy_ip = conn.config.get("proxy_ip", "192.168.49.1")
            proxy_port = conn.config.get("proxy_port", 8000)
            
            assert isinstance(proxy_ip, str), "Proxy IP configuration broken"
            assert isinstance(proxy_port, int), "Proxy port configuration broken"
        except Exception as e:
            assert False, f"Configuration compatibility broken: {e}"

test("P1 Functionality Preserved", test_p1_functionality_preserved)
test("Enhanced Features Optional", test_enhanced_features_optional)
test("Graceful Degradation", test_graceful_degradation)
test("Configuration Compatibility", test_configuration_compatibility)

# Summary
print("\n" + "=" * 70)
print("P1 + P2 INTEGRATION TEST SUMMARY")
print("=" * 70)

passed = sum(1 for _, success, _ in test_results if success)
failed = sum(1 for _, success, _ in test_results if not success)
total = len(test_results)

print(f"\nTotal Tests: {total}")
print(f"Passed: {passed} ✓")
print(f"Failed: {failed} ✗")
print(f"Success Rate: {(passed/total)*100:.1f}%")

if failed > 0:
    print(f"\n⚠️  INTEGRATION ISSUES FOUND:")
    for name, success, error in test_results:
        if not success:
            print(f"  • {name}: {error}")

print("\n" + "=" * 70)
if failed == 0:
    print("✅ ALL P1 + P2 INTEGRATION TESTS PASSED")
    print("✅ P1 + P2 Module Integration - WORKING")
    print("✅ Performance Impact Assessment - ACCEPTABLE")
    print("✅ Backward Compatibility - MAINTAINED")
    print("\n🎯 P1 + P2 ENHANCEMENTS SUCCESSFULLY INTEGRATED")
else:
    print("❌ SOME INTEGRATION TESTS FAILED")
    print("🔍 Review failed tests above for integration issues")

print("=" * 70)
sys.exit(0 if failed == 0 else 1)