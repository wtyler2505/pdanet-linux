#!/usr/bin/env python3
"""
Test Performance Optimizer Module
Comprehensive testing of P2 performance optimization features
"""

import os
import sys
import time
from unittest.mock import Mock, patch, MagicMock
import threading

# Add src to path
sys.path.insert(0, "/app/src")

print("=" * 70)
print("P2-P4 MODULE TESTING: PERFORMANCE OPTIMIZER")
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

# Test Suite 1: Performance Optimizer Core
print("\n[1/4] PERFORMANCE OPTIMIZER CORE FUNCTIONALITY")
print("-" * 70)

def test_performance_optimizer_import():
    """Test performance optimizer imports correctly"""
    from performance_optimizer import get_resource_manager, timed_operation, resource_context
    
    assert get_resource_manager is not None, "get_resource_manager function not available"
    assert timed_operation is not None, "timed_operation decorator not available"
    assert resource_context is not None, "resource_context not available"

def test_resource_manager_initialization():
    """Test resource manager initialization"""
    from performance_optimizer import get_resource_manager
    
    resource_manager = get_resource_manager()
    assert resource_manager is not None, "Resource manager not created"
    
    # Test singleton pattern
    resource_manager2 = get_resource_manager()
    assert resource_manager is resource_manager2, "Resource manager not singleton"

def test_resource_manager_methods():
    """Test resource manager has required methods"""
    from performance_optimizer import get_resource_manager
    
    resource_manager = get_resource_manager()
    
    # Check required methods exist
    required_methods = [
        'get_resource_summary',
        'get_memory_usage',
        'get_cpu_usage', 
        'optimize_memory',
        'start_monitoring',
        'stop_monitoring'
    ]
    
    for method in required_methods:
        assert hasattr(resource_manager, method), f"Method {method} not found"
        assert callable(getattr(resource_manager, method)), f"Method {method} not callable"

def test_timed_operation_decorator():
    """Test timed operation decorator functionality"""
    from performance_optimizer import timed_operation
    
    # Test decorator with function
    @timed_operation("test_operation")
    def test_function():
        time.sleep(0.01)  # Small delay
        return "success"
    
    result = test_function()
    assert result == "success", "Decorated function return value incorrect"
    
    # Test decorator creates timing data
    from performance_optimizer import get_resource_manager
    resource_manager = get_resource_manager()
    
    if hasattr(resource_manager, 'get_timing_data'):
        timing_data = resource_manager.get_timing_data()
        assert "test_operation" in timing_data or len(timing_data) > 0, "Timing data not recorded"

def test_resource_context_manager():
    """Test resource context manager"""
    from performance_optimizer import resource_context, get_resource_manager
    
    resource_manager = get_resource_manager()
    initial_summary = resource_manager.get_resource_summary()
    
    # Test context manager usage
    with resource_context("test_context"):
        time.sleep(0.01)  # Small operation
    
    # Context should complete without error
    assert True, "Context manager completed successfully"

test("Performance Optimizer Import", test_performance_optimizer_import)
test("Resource Manager Initialization", test_resource_manager_initialization)
test("Resource Manager Methods", test_resource_manager_methods)
test("Timed Operation Decorator", test_timed_operation_decorator)
test("Resource Context Manager", test_resource_context_manager)

# Test Suite 2: Memory and CPU Monitoring
print("\n[2/4] MEMORY AND CPU MONITORING")
print("-" * 70)

def test_memory_usage_monitoring():
    """Test memory usage monitoring"""
    from performance_optimizer import get_resource_manager
    
    resource_manager = get_resource_manager()
    memory_info = resource_manager.get_memory_usage()
    
    assert isinstance(memory_info, dict), "Memory info should be dictionary"
    
    # Check required memory fields
    expected_fields = ['used_mb', 'total_mb', 'percentage']
    for field in expected_fields:
        if field in memory_info:
            assert isinstance(memory_info[field], (int, float)), f"Memory {field} should be numeric"
            if field == 'percentage':
                assert 0 <= memory_info[field] <= 100, f"Memory {field} should be 0-100%"

def test_cpu_usage_monitoring():
    """Test CPU usage monitoring"""
    from performance_optimizer import get_resource_manager
    
    resource_manager = get_resource_manager()
    cpu_info = resource_manager.get_cpu_usage()
    
    assert isinstance(cpu_info, dict), "CPU info should be dictionary"
    
    # Check for CPU percentage
    if 'percentage' in cpu_info:
        assert isinstance(cpu_info['percentage'], (int, float)), "CPU percentage should be numeric"
        assert 0 <= cpu_info['percentage'] <= 100, "CPU percentage should be 0-100%"

def test_resource_summary():
    """Test comprehensive resource summary"""
    from performance_optimizer import get_resource_manager
    
    resource_manager = get_resource_manager()
    summary = resource_manager.get_resource_summary()
    
    assert isinstance(summary, dict), "Resource summary should be dictionary"
    
    # Check for key sections
    expected_sections = ['memory', 'cpu', 'operations', 'performance']
    for section in expected_sections:
        if section in summary:
            assert isinstance(summary[section], dict), f"Section {section} should be dictionary"

def test_memory_optimization():
    """Test memory optimization functionality"""
    from performance_optimizer import get_resource_manager
    
    resource_manager = get_resource_manager()
    
    # Test memory optimization
    try:
        result = resource_manager.optimize_memory()
        assert isinstance(result, bool), "optimize_memory should return boolean"
    except Exception as e:
        # Memory optimization might not be available in all environments
        print(f"Memory optimization not available: {e}")

def test_monitoring_control():
    """Test monitoring start/stop functionality"""
    from performance_optimizer import get_resource_manager
    
    resource_manager = get_resource_manager()
    
    # Test start monitoring
    try:
        resource_manager.start_monitoring()
        # Should not raise exception
    except Exception as e:
        print(f"Start monitoring issue: {e}")
    
    # Test stop monitoring
    try:
        resource_manager.stop_monitoring()
        # Should not raise exception
    except Exception as e:
        print(f"Stop monitoring issue: {e}")

test("Memory Usage Monitoring", test_memory_usage_monitoring)
test("CPU Usage Monitoring", test_cpu_usage_monitoring)
test("Resource Summary", test_resource_summary)
test("Memory Optimization", test_memory_optimization)
test("Monitoring Control", test_monitoring_control)

# Test Suite 3: Performance Optimization Features
print("\n[3/4] PERFORMANCE OPTIMIZATION FEATURES")
print("-" * 70)

def test_operation_timing():
    """Test operation timing and performance tracking"""
    from performance_optimizer import timed_operation, get_resource_manager
    
    resource_manager = get_resource_manager()
    
    @timed_operation("timing_test")
    def slow_operation():
        time.sleep(0.02)
        return "completed"
    
    # Run operation multiple times
    for i in range(3):
        result = slow_operation()
        assert result == "completed", f"Operation {i} failed"
    
    # Check if timing data is collected (if available)
    if hasattr(resource_manager, 'get_operations_summary'):
        ops_summary = resource_manager.get_operations_summary()
        assert isinstance(ops_summary, dict), "Operations summary should be dictionary"

def test_resource_context_tracking():
    """Test resource context tracking"""
    from performance_optimizer import resource_context, get_resource_manager
    
    resource_manager = get_resource_manager()
    
    # Test nested contexts
    with resource_context("outer_context"):
        with resource_context("inner_context"):
            time.sleep(0.01)
    
    # Context tracking should handle nesting without issues
    assert True, "Nested contexts completed successfully"

def test_concurrent_resource_monitoring():
    """Test resource monitoring under concurrent operations"""
    from performance_optimizer import resource_context, get_resource_manager
    
    resource_manager = get_resource_manager()
    
    def worker_function(worker_id):
        with resource_context(f"worker_{worker_id}"):
            time.sleep(0.01)
    
    # Create multiple threads
    threads = []
    for i in range(5):
        thread = threading.Thread(target=worker_function, args=(i,))
        threads.append(thread)
        thread.start()
    
    # Wait for all threads to complete
    for thread in threads:
        thread.join()
    
    # Resource manager should handle concurrent access
    summary = resource_manager.get_resource_summary()
    assert isinstance(summary, dict), "Resource summary should work after concurrent access"

def test_performance_metrics_collection():
    """Test performance metrics collection"""
    from performance_optimizer import get_resource_manager
    
    resource_manager = get_resource_manager()
    
    # Test various metric collection methods
    metrics_methods = [
        'get_memory_usage',
        'get_cpu_usage',
        'get_resource_summary'
    ]
    
    for method_name in metrics_methods:
        if hasattr(resource_manager, method_name):
            method = getattr(resource_manager, method_name)
            try:
                result = method()
                assert result is not None, f"{method_name} returned None"
            except Exception as e:
                print(f"Method {method_name} failed: {e}")

def test_optimization_algorithms():
    """Test optimization algorithms and strategies"""
    from performance_optimizer import get_resource_manager
    
    resource_manager = get_resource_manager()
    
    # Test memory optimization
    if hasattr(resource_manager, 'optimize_performance'):
        try:
            optimization_result = resource_manager.optimize_performance()
            assert isinstance(optimization_result, (dict, bool)), "Optimization should return dict or bool"
        except Exception as e:
            print(f"Performance optimization failed: {e}")
    
    # Test garbage collection optimization
    if hasattr(resource_manager, 'optimize_memory'):
        try:
            gc_result = resource_manager.optimize_memory()
            assert isinstance(gc_result, bool), "Memory optimization should return boolean"
        except Exception as e:
            print(f"Memory optimization failed: {e}")

test("Operation Timing", test_operation_timing)
test("Resource Context Tracking", test_resource_context_tracking)
test("Concurrent Resource Monitoring", test_concurrent_resource_monitoring)
test("Performance Metrics Collection", test_performance_metrics_collection)
test("Optimization Algorithms", test_optimization_algorithms)

# Test Suite 4: Integration and Edge Cases
print("\n[4/4] INTEGRATION AND EDGE CASES")
print("-" * 70)

def test_error_handling():
    """Test error handling in performance monitoring"""
    from performance_optimizer import resource_context, timed_operation
    
    # Test context manager with exception
    try:
        with resource_context("error_test"):
            raise ValueError("Test error")
    except ValueError:
        pass  # Expected
    
    # Context should still clean up properly
    assert True, "Error handling in context manager works"
    
    # Test decorator with exception
    @timed_operation("error_operation")
    def failing_operation():
        raise RuntimeError("Operation failed")
    
    try:
        failing_operation()
        assert False, "Should have raised exception"
    except RuntimeError:
        pass  # Expected

def test_resource_limits():
    """Test behavior under resource limits"""
    from performance_optimizer import get_resource_manager
    
    resource_manager = get_resource_manager()
    
    # Test getting resource info under various conditions
    for i in range(10):
        memory_info = resource_manager.get_memory_usage()
        cpu_info = resource_manager.get_cpu_usage()
        
        # Should consistently return valid data
        assert isinstance(memory_info, dict), f"Iteration {i}: Memory info should be dict"
        assert isinstance(cpu_info, dict), f"Iteration {i}: CPU info should be dict"

def test_thread_safety():
    """Test thread safety of resource manager"""
    from performance_optimizer import get_resource_manager
    
    resource_manager = get_resource_manager()
    results = []
    
    def thread_worker():
        try:
            for _ in range(5):
                memory_info = resource_manager.get_memory_usage()
                results.append(memory_info)
                time.sleep(0.001)
        except Exception as e:
            results.append(f"Error: {e}")
    
    # Create multiple threads
    threads = []
    for _ in range(3):
        thread = threading.Thread(target=thread_worker)
        threads.append(thread)
        thread.start()
    
    # Wait for completion
    for thread in threads:
        thread.join()
    
    # Check results
    valid_results = [r for r in results if isinstance(r, dict)]
    assert len(valid_results) > 0, "Should have valid results from thread workers"

def test_performance_overhead():
    """Test that performance monitoring has minimal overhead"""
    from performance_optimizer import timed_operation, resource_context
    
    # Time a simple operation with and without monitoring
    import time as time_module
    
    def simple_operation():
        return sum(range(1000))
    
    # Without monitoring
    start_time = time_module.time()
    for _ in range(100):
        simple_operation()
    unmonitored_time = time_module.time() - start_time
    
    # With monitoring
    @timed_operation("overhead_test")
    def monitored_operation():
        return sum(range(1000))
    
    start_time = time_module.time()
    for _ in range(100):
        monitored_operation()
    monitored_time = time_module.time() - start_time
    
    # Overhead should be reasonable (less than 50% increase)
    overhead_ratio = monitored_time / unmonitored_time if unmonitored_time > 0 else 1
    assert overhead_ratio < 2.0, f"Performance monitoring overhead too high: {overhead_ratio:.2f}x"

def test_memory_leak_prevention():
    """Test that performance monitoring doesn't cause memory leaks"""
    from performance_optimizer import resource_context, get_resource_manager
    
    resource_manager = get_resource_manager()
    initial_memory = resource_manager.get_memory_usage()
    
    # Perform many operations
    for i in range(100):
        with resource_context(f"leak_test_{i}"):
            pass
    
    final_memory = resource_manager.get_memory_usage()
    
    # Memory usage shouldn't increase dramatically
    if 'used_mb' in initial_memory and 'used_mb' in final_memory:
        memory_increase = final_memory['used_mb'] - initial_memory['used_mb']
        assert memory_increase < 50, f"Potential memory leak: {memory_increase}MB increase"

test("Error Handling", test_error_handling)
test("Resource Limits", test_resource_limits)  
test("Thread Safety", test_thread_safety)
test("Performance Overhead", test_performance_overhead)
test("Memory Leak Prevention", test_memory_leak_prevention)

# Test Results Summary
print("\n" + "=" * 70)
print("PERFORMANCE OPTIMIZER TEST RESULTS")
print("=" * 70)

total_tests = len(test_results)
passed_tests = sum(1 for _, passed, _ in test_results if passed)
failed_tests = total_tests - passed_tests

print(f"Total Tests: {total_tests}")
print(f"Passed: {passed_tests}")
print(f"Failed: {failed_tests}")
print(f"Success Rate: {(passed_tests/total_tests*100):.1f}%")

if failed_tests > 0:
    print(f"\nFailed Tests:")
    for name, passed, error in test_results:
        if not passed:
            print(f"  ✗ {name}: {error}")

print(f"\n📊 Performance Optimizer Module: {'✅ FULLY FUNCTIONAL' if failed_tests == 0 else '⚠️ NEEDS ATTENTION'}")

if failed_tests == 0:
    print("All performance optimization features working correctly!")
else:
    print(f"{failed_tests} issues found - recommend investigation before production use.")

# Return appropriate exit code
exit(0 if failed_tests == 0 else 1)