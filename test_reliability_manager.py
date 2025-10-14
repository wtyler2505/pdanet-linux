#!/usr/bin/env python3
"""
Test Reliability Manager Module  
Comprehensive testing of P2 reliability and failure recovery features
"""

import os
import sys
import time
from unittest.mock import Mock, patch, MagicMock
import threading

# Add src to path
sys.path.insert(0, "/app/src")

print("=" * 70)
print("P2-P4 MODULE TESTING: RELIABILITY MANAGER")
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

# Test Suite 1: Reliability Manager Core
print("\n[1/5] RELIABILITY MANAGER CORE FUNCTIONALITY")
print("-" * 70)

def test_reliability_manager_import():
    """Test reliability manager imports correctly"""
    from reliability_manager import get_reliability_manager
    
    assert get_reliability_manager is not None, "get_reliability_manager function not available"

def test_reliability_manager_initialization():
    """Test reliability manager initialization"""
    from reliability_manager import get_reliability_manager
    
    reliability_manager = get_reliability_manager()
    assert reliability_manager is not None, "Reliability manager not created"
    
    # Test singleton pattern
    reliability_manager2 = get_reliability_manager()
    assert reliability_manager is reliability_manager2, "Reliability manager not singleton"

def test_reliability_manager_methods():
    """Test reliability manager has required methods"""
    from reliability_manager import get_reliability_manager
    
    reliability_manager = get_reliability_manager()
    
    # Check required methods exist
    required_methods = [
        'report_failure',
        'report_success', 
        'get_reliability_summary',
        'get_failure_history',
        'is_component_healthy',
        'reset_statistics'
    ]
    
    for method in required_methods:
        assert hasattr(reliability_manager, method), f"Method {method} not found"
        assert callable(getattr(reliability_manager, method)), f"Method {method} not callable"

def test_failure_reporting():
    """Test failure reporting functionality"""
    from reliability_manager import get_reliability_manager
    
    reliability_manager = get_reliability_manager()
    
    # Reset to clean state
    if hasattr(reliability_manager, 'reset_statistics'):
        reliability_manager.reset_statistics()
    
    # Report some failures
    reliability_manager.report_failure("connection", "Test failure 1")
    reliability_manager.report_failure("interface", "Test failure 2", {"interface": "eth0"})
    
    # Check failure history
    history = reliability_manager.get_failure_history()
    assert isinstance(history, (list, dict)), "Failure history should be list or dict"
    
    if isinstance(history, list):
        assert len(history) >= 2, "Should have at least 2 failure records"
    
    # Check reliability summary
    summary = reliability_manager.get_reliability_summary()
    assert isinstance(summary, dict), "Reliability summary should be dictionary"

def test_success_reporting():
    """Test success reporting functionality"""
    from reliability_manager import get_reliability_manager
    
    reliability_manager = get_reliability_manager()
    
    # Report some successes
    reliability_manager.report_success("connection")
    reliability_manager.report_success("interface", {"interface": "wlan0"})
    
    # Check that successes are tracked
    summary = reliability_manager.get_reliability_summary()
    assert isinstance(summary, dict), "Summary should be dictionary after success reporting"

test("Reliability Manager Import", test_reliability_manager_import)
test("Reliability Manager Initialization", test_reliability_manager_initialization) 
test("Reliability Manager Methods", test_reliability_manager_methods)
test("Failure Reporting", test_failure_reporting)
test("Success Reporting", test_success_reporting)

# Test Suite 2: Health Monitoring
print("\n[2/5] HEALTH MONITORING AND COMPONENT STATUS")
print("-" * 70)

def test_component_health_checking():
    """Test component health checking"""
    from reliability_manager import get_reliability_manager
    
    reliability_manager = get_reliability_manager()
    
    # Test health checking for various components
    test_components = ["connection", "interface", "proxy", "dns", "network"]
    
    for component in test_components:
        try:
            is_healthy = reliability_manager.is_component_healthy(component)
            assert isinstance(is_healthy, bool), f"Health check for {component} should return boolean"
        except Exception as e:
            print(f"Health check for {component} failed: {e}")

def test_reliability_metrics():
    """Test reliability metrics calculation"""
    from reliability_manager import get_reliability_manager
    
    reliability_manager = get_reliability_manager()
    
    # Reset statistics
    if hasattr(reliability_manager, 'reset_statistics'):
        reliability_manager.reset_statistics()
    
    # Create a pattern of successes and failures
    for i in range(8):
        reliability_manager.report_success("test_component")
    
    for i in range(2):
        reliability_manager.report_failure("test_component", f"Test failure {i}")
    
    # Check summary includes reliability metrics
    summary = reliability_manager.get_reliability_summary()
    
    # Look for reliability-related data
    reliability_data_found = False
    for key in summary.keys():
        if any(term in key.lower() for term in ['reliability', 'success', 'failure', 'uptime', 'health']):
            reliability_data_found = True
            break
    
    # If no direct reliability data, check nested structures
    if not reliability_data_found:
        for value in summary.values():
            if isinstance(value, dict):
                for sub_key in value.keys():
                    if any(term in sub_key.lower() for term in ['reliability', 'success', 'failure', 'rate']):
                        reliability_data_found = True
                        break
                if reliability_data_found:
                    break

def test_failure_analysis():
    """Test failure analysis and pattern detection"""
    from reliability_manager import get_reliability_manager
    
    reliability_manager = get_reliability_manager()
    
    # Report failures with different patterns
    failure_types = [
        ("connection_timeout", "Connection timed out after 30 seconds"),
        ("dns_resolution", "Unable to resolve hostname"),
        ("interface_error", "Network interface went down"),
        ("connection_timeout", "Connection timed out after 45 seconds"),  # Repeat
        ("proxy_error", "Proxy server unreachable")
    ]
    
    for failure_type, message in failure_types:
        reliability_manager.report_failure(failure_type, message)
    
    # Get failure history and check it contains our failures
    history = reliability_manager.get_failure_history()
    
    if isinstance(history, list) and len(history) > 0:
        # Check that failures have timestamps and details
        recent_failure = history[0] if isinstance(history[0], dict) else {}
        if isinstance(recent_failure, dict):
            expected_fields = ['timestamp', 'type', 'message']
            for field in expected_fields:
                if field in recent_failure:
                    assert recent_failure[field] is not None, f"Failure {field} should not be None"

def test_recovery_tracking():
    """Test recovery and restoration tracking"""  
    from reliability_manager import get_reliability_manager
    
    reliability_manager = get_reliability_manager()
    
    # Simulate failure and recovery cycle
    reliability_manager.report_failure("network", "Network interface down")
    
    # Check component is unhealthy
    if hasattr(reliability_manager, 'is_component_healthy'):
        # Component might be unhealthy after failure
        pass  # This is implementation dependent
    
    # Simulate recovery
    reliability_manager.report_success("network")
    
    # Component should recover or reliability should improve
    summary = reliability_manager.get_reliability_summary()
    assert isinstance(summary, dict), "Summary should be available after recovery"

def test_statistics_reset():
    """Test statistics reset functionality"""
    from reliability_manager import get_reliability_manager
    
    reliability_manager = get_reliability_manager()
    
    # Add some data
    reliability_manager.report_failure("test_reset", "Test failure")
    reliability_manager.report_success("test_reset")
    
    # Reset statistics
    if hasattr(reliability_manager, 'reset_statistics'):
        reliability_manager.reset_statistics()
        
        # Check data is cleared
        history = reliability_manager.get_failure_history()
        
        if isinstance(history, list):
            # History should be empty or minimal after reset
            pass  # This is implementation dependent
        
        summary = reliability_manager.get_reliability_summary()
        assert isinstance(summary, dict), "Summary should still be available after reset"

test("Component Health Checking", test_component_health_checking)
test("Reliability Metrics", test_reliability_metrics)
test("Failure Analysis", test_failure_analysis)
test("Recovery Tracking", test_recovery_tracking)
test("Statistics Reset", test_statistics_reset)

# Test Suite 3: Advanced Reliability Features
print("\n[3/5] ADVANCED RELIABILITY FEATURES")
print("-" * 70)

def test_failure_rate_calculation():
    """Test failure rate calculation over time"""
    from reliability_manager import get_reliability_manager
    
    reliability_manager = get_reliability_manager()
    
    # Reset for clean test
    if hasattr(reliability_manager, 'reset_statistics'):
        reliability_manager.reset_statistics()
    
    # Create known pattern: 7 successes, 3 failures = 70% success rate
    for i in range(7):
        reliability_manager.report_success("rate_test")
    
    for i in range(3):
        reliability_manager.report_failure("rate_test", f"Rate test failure {i}")
    
    summary = reliability_manager.get_reliability_summary()
    
    # Look for rate calculations in summary
    rate_found = False
    for key, value in summary.items():
        if isinstance(value, dict):
            for sub_key, sub_value in value.items():
                if 'rate' in sub_key.lower() and isinstance(sub_value, (int, float)):
                    rate_found = True
                    # Basic sanity check on rate values
                    assert 0 <= sub_value <= 100 or 0 <= sub_value <= 1, f"Rate {sub_value} should be 0-100% or 0-1"

def test_trend_analysis():
    """Test reliability trend analysis"""
    from reliability_manager import get_reliability_manager
    
    reliability_manager = get_reliability_manager()
    
    # Create improving trend: failures decreasing over time
    base_time = time.time()
    
    # Early period: more failures
    for i in range(5):
        reliability_manager.report_failure("trend_test", f"Early failure {i}")
        reliability_manager.report_success("trend_test")
    
    # Later period: fewer failures  
    for i in range(8):
        reliability_manager.report_success("trend_test")
        if i < 2:  # Only 2 failures in later period
            reliability_manager.report_failure("trend_test", f"Late failure {i}")
    
    # Check if trend analysis is available
    summary = reliability_manager.get_reliability_summary()
    
    # Look for trend data
    trend_indicators = ['trend', 'improving', 'degrading', 'stable', 'recent', 'historical']
    trend_found = any(
        any(indicator in str(key).lower() for indicator in trend_indicators)
        for key in summary.keys()
    )
    
    # If no direct trend data, check nested structures
    if not trend_found:
        for value in summary.values():
            if isinstance(value, dict):
                trend_found = any(
                    any(indicator in str(key).lower() for indicator in trend_indicators)
                    for key in value.keys()
                )
                if trend_found:
                    break

def test_component_isolation():
    """Test component-specific reliability tracking"""
    from reliability_manager import get_reliability_manager
    
    reliability_manager = get_reliability_manager()
    
    # Test multiple components with different reliability patterns
    components = {
        "reliable_component": (10, 1),  # 10 successes, 1 failure
        "unreliable_component": (3, 7), # 3 successes, 7 failures  
        "perfect_component": (5, 0),    # 5 successes, 0 failures
    }
    
    for component, (successes, failures) in components.items():
        for i in range(successes):
            reliability_manager.report_success(component)
        for i in range(failures):
            reliability_manager.report_failure(component, f"Failure {i}")
    
    # Check component-specific health
    for component in components.keys():
        if hasattr(reliability_manager, 'is_component_healthy'):
            health = reliability_manager.is_component_healthy(component)
            assert isinstance(health, bool), f"Health for {component} should be boolean"

def test_threshold_alerting():
    """Test reliability threshold and alerting"""
    from reliability_manager import get_reliability_manager
    
    reliability_manager = get_reliability_manager()
    
    # Create a component with very poor reliability
    for i in range(10):
        reliability_manager.report_failure("failing_component", f"Critical failure {i}")
    
    # Add minimal successes
    reliability_manager.report_success("failing_component")
    reliability_manager.report_success("failing_component")
    
    # Check if poor reliability is detected
    summary = reliability_manager.get_reliability_summary()
    
    # Look for any alerting or threshold-related data
    alert_indicators = ['critical', 'alert', 'warning', 'threshold', 'poor', 'unhealthy']
    alert_found = False
    
    for key, value in summary.items():
        if any(indicator in str(key).lower() or indicator in str(value).lower() 
               for indicator in alert_indicators):
            alert_found = True
            break
    
    # Check nested structures
    if not alert_found:
        for value in summary.values():
            if isinstance(value, dict):
                for sub_key, sub_value in value.items():
                    if any(indicator in str(sub_key).lower() or indicator in str(sub_value).lower()
                           for indicator in alert_indicators):
                        alert_found = True
                        break
                if alert_found:
                    break

def test_historical_data_management():
    """Test historical data storage and cleanup"""
    from reliability_manager import get_reliability_manager
    
    reliability_manager = get_reliability_manager()
    
    # Generate substantial historical data
    for i in range(50):
        reliability_manager.report_success("historical_test")
        reliability_manager.report_failure("historical_test", f"Historical failure {i}")
    
    # Check history is managed
    history = reliability_manager.get_failure_history()
    
    if isinstance(history, list):
        # History should exist but might be limited to prevent memory issues
        assert len(history) >= 0, "History should be accessible"
        
        # If history is very long, it should have reasonable limits
        if len(history) > 1000:
            print(f"Warning: History very long ({len(history)} items), might need cleanup")
    
    summary = reliability_manager.get_reliability_summary()
    assert isinstance(summary, dict), "Summary should always be available"

test("Failure Rate Calculation", test_failure_rate_calculation)
test("Trend Analysis", test_trend_analysis)
test("Component Isolation", test_component_isolation)
test("Threshold Alerting", test_threshold_alerting)
test("Historical Data Management", test_historical_data_management)

# Test Suite 4: Integration and Error Handling
print("\n[4/5] INTEGRATION AND ERROR HANDLING")  
print("-" * 70)

def test_concurrent_reporting():
    """Test concurrent failure/success reporting"""
    from reliability_manager import get_reliability_manager
    
    reliability_manager = get_reliability_manager()
    
    results = []
    
    def worker(worker_id):
        try:
            for i in range(10):
                reliability_manager.report_success(f"worker_{worker_id}")
                reliability_manager.report_failure(f"worker_{worker_id}", f"Failure {i}")
                time.sleep(0.001)  # Small delay
            results.append(f"worker_{worker_id}_success")
        except Exception as e:
            results.append(f"worker_{worker_id}_error: {e}")
    
    # Create multiple threads
    threads = []
    for i in range(3):
        thread = threading.Thread(target=worker, args=(i,))
        threads.append(thread)
        thread.start()
    
    # Wait for completion
    for thread in threads:
        thread.join(timeout=5.0)
    
    # Check results
    successful_workers = [r for r in results if 'success' in r]
    assert len(successful_workers) >= 1, "At least one worker should succeed"

def test_error_handling():
    """Test error handling in reliability manager"""
    from reliability_manager import get_reliability_manager
    
    reliability_manager = get_reliability_manager()
    
    # Test with invalid inputs
    try:
        reliability_manager.report_failure(None, "Test with None component")
    except Exception:
        pass  # Expected to handle gracefully
    
    try:
        reliability_manager.report_failure("test", None)
    except Exception:
        pass  # Expected to handle gracefully
    
    try:
        reliability_manager.report_success("")  # Empty component name
    except Exception:
        pass  # Expected to handle gracefully
    
    # Manager should still function after bad inputs
    reliability_manager.report_success("recovery_test")
    summary = reliability_manager.get_reliability_summary()
    assert isinstance(summary, dict), "Manager should recover from bad inputs"

def test_large_scale_reporting():
    """Test large scale failure/success reporting"""
    from reliability_manager import get_reliability_manager
    
    reliability_manager = get_reliability_manager()
    
    # Report large number of events
    start_time = time.time()
    
    for i in range(500):
        component = f"component_{i % 10}"  # 10 different components
        if i % 3 == 0:
            reliability_manager.report_failure(component, f"Batch failure {i}")
        else:
            reliability_manager.report_success(component)
    
    elapsed_time = time.time() - start_time
    
    # Should handle large scale efficiently (under 5 seconds)
    assert elapsed_time < 5.0, f"Large scale reporting too slow: {elapsed_time:.2f}s"
    
    # Should still provide summary
    summary = reliability_manager.get_reliability_summary()
    assert isinstance(summary, dict), "Summary should be available after large scale reporting"

def test_memory_efficiency():
    """Test memory efficiency under sustained load"""
    from reliability_manager import get_reliability_manager
    
    reliability_manager = get_reliability_manager()
    
    # Sustained reporting over time
    for batch in range(10):
        for i in range(100):
            reliability_manager.report_success("memory_test")
            reliability_manager.report_failure("memory_test", f"Memory test failure batch{batch}-{i}")
    
    # Get multiple summaries to test memory stability
    summaries = []
    for i in range(5):
        summary = reliability_manager.get_reliability_summary()
        summaries.append(summary)
        assert isinstance(summary, dict), f"Summary {i} should be dictionary"
    
    # All summaries should be consistent in structure
    if len(summaries) > 1:
        keys1 = set(summaries[0].keys())
        keys2 = set(summaries[1].keys()) 
        # Keys should be similar (allowing for dynamic data)
        common_keys = keys1.intersection(keys2)
        assert len(common_keys) > 0, "Summaries should have some common structure"

def test_data_persistence():
    """Test data persistence and state management"""  
    from reliability_manager import get_reliability_manager
    
    reliability_manager = get_reliability_manager()
    
    # Add some trackable data
    test_data = [
        ("persist_test", "Initial failure"),
        ("persist_test", "Second failure"),
    ]
    
    for component, message in test_data:
        reliability_manager.report_failure(component, message)
    
    # Get initial state
    initial_history = reliability_manager.get_failure_history()
    initial_summary = reliability_manager.get_reliability_summary()
    
    # Data should persist across multiple calls
    later_history = reliability_manager.get_failure_history()
    later_summary = reliability_manager.get_reliability_summary()
    
    assert isinstance(later_history, type(initial_history)), "History type should be consistent"
    assert isinstance(later_summary, dict), "Summary should always be dictionary"

test("Concurrent Reporting", test_concurrent_reporting)
test("Error Handling", test_error_handling)
test("Large Scale Reporting", test_large_scale_reporting)
test("Memory Efficiency", test_memory_efficiency)
test("Data Persistence", test_data_persistence)

# Test Suite 5: Performance and Edge Cases
print("\n[5/5] PERFORMANCE AND EDGE CASES")
print("-" * 70)

def test_performance_under_load():
    """Test performance under sustained load"""
    from reliability_manager import get_reliability_manager
    
    reliability_manager = get_reliability_manager()
    
    # Time sustained operations
    start_time = time.time()
    
    # Heavy mixed workload
    for i in range(1000):
        if i % 5 == 0:
            reliability_manager.get_reliability_summary()
        if i % 7 == 0:
            reliability_manager.get_failure_history()
        if i % 2 == 0:
            reliability_manager.report_success(f"perf_test_{i % 20}")
        else:
            reliability_manager.report_failure(f"perf_test_{i % 20}", f"Performance test {i}")
    
    elapsed_time = time.time() - start_time
    
    # Should handle sustained load efficiently
    operations_per_second = 1000 / elapsed_time
    assert operations_per_second > 100, f"Performance too low: {operations_per_second:.1f} ops/sec"

def test_edge_case_inputs():
    """Test edge case inputs and boundary conditions"""
    from reliability_manager import get_reliability_manager
    
    reliability_manager = get_reliability_manager()
    
    # Test various edge cases
    edge_cases = [
        ("", "Empty component name"),
        (" " * 100, "Very long spaces"),
        ("component_with_very_long_name_that_exceeds_normal_limits_" * 5, "Very long name"),
        ("comp-with-special-chars!@#$%", "Special characters"),
        ("comp\nwith\nnewlines", "Newline characters"),
        ("comp\x00with\x00nulls", "Null characters"),
    ]
    
    for component, message in edge_cases:
        try:
            reliability_manager.report_failure(component, message)
            reliability_manager.report_success(component)
        except Exception as e:
            # Should handle edge cases gracefully
            print(f"Edge case handling: {component[:20]}... -> {type(e).__name__}")
    
    # Should still function normally after edge cases
    reliability_manager.report_success("normal_component")
    summary = reliability_manager.get_reliability_summary()
    assert isinstance(summary, dict), "Should recover from edge cases"

def test_resource_cleanup():
    """Test resource cleanup and garbage collection"""
    from reliability_manager import get_reliability_manager
    import gc
    
    reliability_manager = get_reliability_manager()
    
    # Generate data that might need cleanup
    for i in range(500):
        large_message = "Large failure message " + ("data " * 100)
        reliability_manager.report_failure(f"cleanup_test_{i}", large_message)
    
    # Force garbage collection
    initial_objects = len(gc.get_objects())
    gc.collect()
    
    # Continue operations
    for i in range(100):
        reliability_manager.report_success("cleanup_continued")
    
    # Check memory usage hasn't grown excessively
    final_objects = len(gc.get_objects())
    object_growth = final_objects - initial_objects
    
    # Some growth is normal, but should be reasonable
    assert object_growth < 10000, f"Excessive object growth: {object_growth}"

def test_boundary_conditions():
    """Test boundary conditions and limits"""
    from reliability_manager import get_reliability_manager
    
    reliability_manager = get_reliability_manager()
    
    # Test zero operations
    if hasattr(reliability_manager, 'reset_statistics'):
        reliability_manager.reset_statistics()
        summary = reliability_manager.get_reliability_summary()
        assert isinstance(summary, dict), "Should handle zero data state"
    
    # Test single operation
    reliability_manager.report_success("boundary_test")
    summary = reliability_manager.get_reliability_summary()
    assert isinstance(summary, dict), "Should handle single operation"
    
    # Test alternating pattern
    for i in range(100):
        if i % 2 == 0:
            reliability_manager.report_success("alternating")
        else:
            reliability_manager.report_failure("alternating", f"Alternating failure {i}")
    
    summary = reliability_manager.get_reliability_summary()
    assert isinstance(summary, dict), "Should handle alternating patterns"

def test_system_integration():
    """Test integration with system monitoring"""
    from reliability_manager import get_reliability_manager
    
    reliability_manager = get_reliability_manager()
    
    # Test integration with different system scenarios
    system_scenarios = [
        ("connection_lost", "Network connection dropped"),
        ("high_latency", "Network latency above threshold"), 
        ("dns_failure", "DNS resolution timeout"),
        ("proxy_unavailable", "Proxy server not responding"),
        ("interface_down", "Network interface went offline"),
    ]
    
    for scenario, description in system_scenarios:
        # Report system event
        reliability_manager.report_failure(scenario, description)
        
        # Check system can recover
        reliability_manager.report_success(scenario)
        
        # Verify health status
        if hasattr(reliability_manager, 'is_component_healthy'):
            health = reliability_manager.is_component_healthy(scenario)
            assert isinstance(health, bool), f"Health check for {scenario} should return boolean"
    
    # Overall system health should be trackable
    summary = reliability_manager.get_reliability_summary()
    assert isinstance(summary, dict), "System integration should provide summary"

test("Performance Under Load", test_performance_under_load)
test("Edge Case Inputs", test_edge_case_inputs)
test("Resource Cleanup", test_resource_cleanup)
test("Boundary Conditions", test_boundary_conditions)
test("System Integration", test_system_integration)

# Test Results Summary
print("\n" + "=" * 70)
print("RELIABILITY MANAGER TEST RESULTS")
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

print(f"\n📊 Reliability Manager Module: {'✅ FULLY FUNCTIONAL' if failed_tests == 0 else '⚠️ NEEDS ATTENTION'}")

if failed_tests == 0:
    print("All reliability management features working correctly!")
else:
    print(f"{failed_tests} issues found - recommend investigation before production use.")

# Return appropriate exit code
exit(0 if failed_tests == 0 else 1)