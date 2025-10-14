#!/usr/bin/env python3
"""
P2 UX Error Recovery System Testing
Tests the newly integrated error recovery system in connection_manager.py
"""

import os
import sys
import time
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

# Add src to path
sys.path.insert(0, "/app/src")

print("=" * 80)
print("P2 UX ERROR RECOVERY SYSTEM TESTING")
print("Testing enhanced error handling with structured error codes and recovery")
print("=" * 80)
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

# Test Suite 1: Error Database Functionality
print("\n[1/5] ERROR DATABASE FUNCTIONALITY TESTS")
print("-" * 80)

def test_error_database_import():
    """Test error_database module imports correctly"""
    from error_database import get_error_info, ErrorInfo, ErrorSolution
    
    assert get_error_info is not None, "get_error_info function not available"
    assert ErrorInfo is not None, "ErrorInfo class not available"
    assert ErrorSolution is not None, "ErrorSolution class not available"

def test_error_info_retrieval():
    """Test error information retrieval by code"""
    from error_database import get_error_info
    
    # Test known error codes
    error_info = get_error_info("interface_not_found")
    assert error_info is not None, "interface_not_found error info not found"
    assert error_info.code == "interface_not_found", "Error code mismatch"
    assert error_info.title == "Network Interface Not Found", "Error title incorrect"
    assert error_info.category == "network", "Error category incorrect"
    assert error_info.severity == "high", "Error severity incorrect"
    assert len(error_info.solutions) > 0, "No solutions provided"
    
    # Test proxy error
    proxy_error = get_error_info("proxy_not_accessible")
    assert proxy_error is not None, "proxy_not_accessible error info not found"
    assert proxy_error.severity == "critical", "Proxy error should be critical"
    
    # Test non-existent error code
    missing_error = get_error_info("non_existent_error")
    assert missing_error is None, "Non-existent error should return None"

def test_error_solution_structure():
    """Test ErrorSolution structure and properties"""
    from error_database import get_error_info
    
    error_info = get_error_info("input_validation_failed")
    assert error_info is not None, "input_validation_failed error not found"
    
    solutions = error_info.solutions
    assert len(solutions) > 0, "No solutions provided for input validation error"
    
    solution = solutions[0]
    assert hasattr(solution, 'title'), "Solution missing title"
    assert hasattr(solution, 'steps'), "Solution missing steps"
    assert hasattr(solution, 'auto_fix_command'), "Solution missing auto_fix_command"
    assert hasattr(solution, 'requires_root'), "Solution missing requires_root"
    
    assert isinstance(solution.steps, list), "Solution steps should be a list"
    assert len(solution.steps) > 0, "Solution should have steps"

def test_error_categories_and_severity():
    """Test error categorization and severity levels"""
    from error_database import search_errors_by_category, search_errors_by_severity
    
    # Test category search
    network_errors = search_errors_by_category("network")
    assert len(network_errors) > 0, "No network errors found"
    
    permission_errors = search_errors_by_category("permission")
    assert len(permission_errors) > 0, "No permission errors found"
    
    # Test severity search
    critical_errors = search_errors_by_severity("critical")
    assert len(critical_errors) > 0, "No critical errors found"
    
    high_errors = search_errors_by_severity("high")
    assert len(high_errors) > 0, "No high severity errors found"

def test_p2_specific_error_codes():
    """Test P2-specific error codes are present"""
    from error_database import get_error_info
    
    # Test P2 error recovery integration codes
    p2_error_codes = [
        "input_validation_failed",
        "missing_ssid", 
        "script_not_found",
        "connection_failed",
        "iphone_script_not_found",
        "disconnect_script_not_found",
        "connection_thread_exception"
    ]
    
    for error_code in p2_error_codes:
        error_info = get_error_info(error_code)
        assert error_info is not None, f"P2 error code '{error_code}' not found in database"
        assert error_info.code == error_code, f"Error code mismatch for {error_code}"
        assert len(error_info.solutions) > 0, f"No solutions for P2 error code {error_code}"

test("Error Database Import", test_error_database_import)
test("Error Info Retrieval", test_error_info_retrieval)
test("Error Solution Structure", test_error_solution_structure)
test("Error Categories and Severity", test_error_categories_and_severity)
test("P2 Specific Error Codes", test_p2_specific_error_codes)

# Test Suite 2: Connection Manager Error Recovery Integration
print("\n[2/5] CONNECTION MANAGER ERROR RECOVERY INTEGRATION")
print("-" * 80)

def test_handle_error_with_code_method():
    """Test _handle_error_with_code method exists and functions"""
    with patch('connection_manager.get_logger'), \
         patch('connection_manager.get_stats'), \
         patch('connection_manager.get_config'):
        from connection_manager import ConnectionManager, ConnectionState
        
        conn = ConnectionManager()
        
        # Test method exists
        assert hasattr(conn, '_handle_error_with_code'), "_handle_error_with_code method missing"
        
        # Test method execution
        conn._handle_error_with_code(
            "test_error_code",
            "Test error message",
            {"test_context": "test_value"}
        )
        
        # Verify error state was set
        assert conn.state == ConnectionState.ERROR, "Error state not set"
        assert conn.last_error == "Test error message", "Error message not stored"
        assert hasattr(conn, 'last_error_code'), "last_error_code attribute missing"
        assert conn.last_error_code == "test_error_code", "Error code not stored"

def test_error_recovery_callback_registration():
    """Test error recovery callback registration and triggering"""
    with patch('connection_manager.get_logger'), \
         patch('connection_manager.get_stats'), \
         patch('connection_manager.get_config'):
        from connection_manager import ConnectionManager
        
        conn = ConnectionManager()
        
        # Test callback registration method exists
        assert hasattr(conn, 'register_error_recovery_callback'), "register_error_recovery_callback method missing"
        
        # Register test callback
        callback_called = False
        callback_data = None
        
        def test_callback(error_data):
            nonlocal callback_called, callback_data
            callback_called = True
            callback_data = error_data
        
        conn.register_error_recovery_callback(test_callback)
        
        # Trigger error to test callback
        conn._handle_error_with_code(
            "test_callback_error",
            "Test callback message",
            {"callback_test": True}
        )
        
        # Verify callback was called
        assert callback_called, "Error recovery callback not called"
        assert callback_data is not None, "Callback data not provided"
        assert callback_data['code'] == "test_callback_error", "Error code not passed to callback"
        assert callback_data['message'] == "Test callback message", "Error message not passed to callback"
        assert 'error_info' in callback_data, "Error info not included in callback data"
        assert 'context' in callback_data, "Context not included in callback data"
        assert 'timestamp' in callback_data, "Timestamp not included in callback data"

def test_legacy_error_callback_compatibility():
    """Test backward compatibility with legacy error callbacks"""
    with patch('connection_manager.get_logger'), \
         patch('connection_manager.get_stats'), \
         patch('connection_manager.get_config'):
        from connection_manager import ConnectionManager
        
        conn = ConnectionManager()
        
        # Register legacy callback
        legacy_callback_called = False
        legacy_error_message = None
        
        def legacy_callback(error_message):
            nonlocal legacy_callback_called, legacy_error_message
            legacy_callback_called = True
            legacy_error_message = error_message
        
        conn.register_error_callback(legacy_callback)
        
        # Trigger error
        conn._handle_error_with_code(
            "legacy_test_error",
            "Legacy test message",
            {"legacy": True}
        )
        
        # Verify legacy callback still works
        assert legacy_callback_called, "Legacy error callback not called"
        assert legacy_error_message == "Legacy test message", "Legacy callback message incorrect"

def test_get_last_error_info_method():
    """Test get_last_error_info method for structured error retrieval"""
    with patch('connection_manager.get_logger'), \
         patch('connection_manager.get_stats'), \
         patch('connection_manager.get_config'):
        from connection_manager import ConnectionManager
        
        conn = ConnectionManager()
        
        # Test method exists
        assert hasattr(conn, 'get_last_error_info'), "get_last_error_info method missing"
        
        # Test with no error
        error_info = conn.get_last_error_info()
        assert error_info is None, "Should return None when no error"
        
        # Trigger error
        conn._handle_error_with_code(
            "interface_not_found",
            "Test interface error",
            {"interface": "test0"}
        )
        
        # Test error info retrieval
        error_info = conn.get_last_error_info()
        assert error_info is not None, "Error info should be available"
        assert error_info['code'] == "interface_not_found", "Error code incorrect"
        assert error_info['message'] == "Test interface error", "Error message incorrect"
        assert 'error_info' in error_info, "Structured error info missing"
        assert 'context' in error_info, "Error context missing"

def test_error_context_data_capture():
    """Test that contextual information is properly captured"""
    with patch('connection_manager.get_logger'), \
         patch('connection_manager.get_stats'), \
         patch('connection_manager.get_config'):
        from connection_manager import ConnectionManager
        
        conn = ConnectionManager()
        
        # Test context data capture
        test_context = {
            "mode": "wifi",
            "interface": "wlan0", 
            "script": "/usr/local/bin/pdanet-wifi-connect",
            "ssid": "TestNetwork",
            "validation_error": "Invalid SSID format"
        }
        
        conn._handle_error_with_code(
            "input_validation_failed",
            "Invalid input provided",
            test_context
        )
        
        # Verify context is stored and retrievable
        error_info = conn.get_last_error_info()
        assert error_info is not None, "Error info not available"
        assert 'context' in error_info, "Context not stored"
        
        stored_context = error_info['context']
        for key, value in test_context.items():
            assert key in stored_context, f"Context key '{key}' missing"
            assert stored_context[key] == value, f"Context value for '{key}' incorrect"

test("Handle Error With Code Method", test_handle_error_with_code_method)
test("Error Recovery Callback Registration", test_error_recovery_callback_registration)
test("Legacy Error Callback Compatibility", test_legacy_error_callback_compatibility)
test("Get Last Error Info Method", test_get_last_error_info_method)
test("Error Context Data Capture", test_error_context_data_capture)

# Test Suite 3: Error Recovery in Connection Scenarios
print("\n[3/5] ERROR RECOVERY IN CONNECTION SCENARIOS")
print("-" * 80)

def test_input_validation_error_recovery():
    """Test error recovery for input validation failures"""
    with patch('connection_manager.get_logger'), \
         patch('connection_manager.get_stats'), \
         patch('connection_manager.get_config'):
        from connection_manager import ConnectionManager
        from input_validators import ValidationError
        
        conn = ConnectionManager()
        
        # Mock validation error
        with patch('connection_manager.validate_ssid', side_effect=ValidationError("Invalid SSID")):
            # This should trigger input_validation_failed error
            conn._connect_thread("wifi", "invalid_ssid", "password")
            
            # Verify error was handled with correct code
            error_info = conn.get_last_error_info()
            assert error_info is not None, "Error info not captured"
            assert error_info['code'] == "input_validation_failed", "Wrong error code for validation failure"
            assert "Invalid input" in error_info['message'], "Error message doesn't indicate validation failure"

def test_interface_detection_error_recovery():
    """Test error recovery for interface detection failures"""
    with patch('connection_manager.get_logger'), \
         patch('connection_manager.get_stats'), \
         patch('connection_manager.get_config'):
        from connection_manager import ConnectionManager
        
        conn = ConnectionManager()
        
        # Mock interface detection failure
        with patch.object(conn, 'detect_interface', return_value=None):
            conn._connect_thread("usb")
            
            # Verify error was handled with correct code
            error_info = conn.get_last_error_info()
            assert error_info is not None, "Error info not captured"
            assert error_info['code'] == "interface_not_found", "Wrong error code for interface failure"
            assert "No USB interface detected" in error_info['message'], "Error message incorrect"

def test_script_not_found_error_recovery():
    """Test error recovery for missing connection scripts"""
    with patch('connection_manager.get_logger'), \
         patch('connection_manager.get_stats'), \
         patch('connection_manager.get_config'):
        from connection_manager import ConnectionManager
        
        conn = ConnectionManager()
        
        # Mock script not found
        conn.connect_script = None  # Simulate script not found
        
        # Mock interface detection and proxy validation to succeed so we get to script check
        with patch.object(conn, 'detect_interface', return_value="usb0"):
            with patch.object(conn, 'validate_proxy', return_value=True):
                conn._connect_thread("usb")
        
        # Verify error was handled with correct code
        error_info = conn.get_last_error_info()
        assert error_info is not None, "Error info not captured"
        assert error_info['code'] == "script_not_found", "Wrong error code for script not found"
        assert "Connection script not found" in error_info['message'], "Error message incorrect"

def test_connection_script_failure_recovery():
    """Test error recovery for connection script execution failures"""
    with patch('connection_manager.get_logger'), \
         patch('connection_manager.get_stats'), \
         patch('connection_manager.get_config'):
        from connection_manager import ConnectionManager
        
        conn = ConnectionManager()
        
        # Mock script execution failure
        with patch.object(conn, '_execute_connection_script', return_value=False):
            with patch.object(conn, 'detect_interface', return_value="usb0"):
                with patch.object(conn, 'validate_proxy', return_value=True):
                    conn._connect_thread("usb")
                    
                    # Verify error was handled with correct code
                    error_info = conn.get_last_error_info()
                    assert error_info is not None, "Error info not captured"
                    assert error_info['code'] == "connection_failed", "Wrong error code for connection failure"
                    assert "connection failed" in error_info['message'].lower(), "Error message incorrect"

def test_disconnect_error_recovery():
    """Test error recovery for disconnection failures"""
    with patch('connection_manager.get_logger'), \
         patch('connection_manager.get_stats'), \
         patch('connection_manager.get_config'):
        from connection_manager import ConnectionManager
        
        conn = ConnectionManager()
        
        # Mock disconnect script not found
        conn.disconnect_script = None
        
        conn._disconnect_thread()
        
        # Verify error was handled with correct code
        error_info = conn.get_last_error_info()
        assert error_info is not None, "Error info not captured"
        assert error_info['code'] == "disconnect_script_not_found", "Wrong error code for disconnect script failure"

def test_iphone_connection_error_recovery():
    """Test error recovery for iPhone-specific connection errors"""
    with patch('connection_manager.get_logger'), \
         patch('connection_manager.get_stats'), \
         patch('connection_manager.get_config'):
        from connection_manager import ConnectionManager
        
        conn = ConnectionManager()
        
        # Mock iPhone script not found
        conn.iphone_connect_script = None
        
        conn._connect_thread("iphone", "iPhone", "password")
        
        # Verify error was handled with correct code
        error_info = conn.get_last_error_info()
        assert error_info is not None, "Error info not captured"
        assert error_info['code'] == "script_not_found", "Wrong error code for iPhone script failure"

test("Input Validation Error Recovery", test_input_validation_error_recovery)
test("Interface Detection Error Recovery", test_interface_detection_error_recovery)
test("Script Not Found Error Recovery", test_script_not_found_error_recovery)
test("Connection Script Failure Recovery", test_connection_script_failure_recovery)
test("Disconnect Error Recovery", test_disconnect_error_recovery)
test("iPhone Connection Error Recovery", test_iphone_connection_error_recovery)

# Test Suite 4: Reliability Manager Integration
print("\n[4/5] RELIABILITY MANAGER INTEGRATION")
print("-" * 80)

def test_reliability_manager_error_reporting():
    """Test that errors are reported to reliability manager"""
    with patch('connection_manager.get_logger'), \
         patch('connection_manager.get_stats'), \
         patch('connection_manager.get_config'):
        from connection_manager import ConnectionManager
        
        conn = ConnectionManager()
        
        # Mock reliability manager
        mock_reliability = Mock()
        conn.reliability_manager = mock_reliability
        
        # Trigger error
        conn._handle_error_with_code(
            "test_reliability_error",
            "Test reliability message",
            {"test": "data"}
        )
        
        # Verify reliability manager was called
        mock_reliability.report_failure.assert_called_once()
        call_args = mock_reliability.report_failure.call_args
        assert call_args[0][0] == "test_reliability_error", "Error code not reported to reliability manager"
        assert call_args[0][1] == "Test reliability message", "Error message not reported to reliability manager"

def test_error_recovery_with_structured_solutions():
    """Test that structured error solutions are provided"""
    with patch('connection_manager.get_logger'), \
         patch('connection_manager.get_stats'), \
         patch('connection_manager.get_config'):
        from connection_manager import ConnectionManager
        
        conn = ConnectionManager()
        
        # Trigger error with known solutions
        conn._handle_error_with_code(
            "proxy_not_accessible",
            "Proxy connection failed",
            {"proxy_ip": "192.168.49.1", "proxy_port": 8000}
        )
        
        # Get error info and verify solutions are available
        error_info = conn.get_last_error_info()
        assert error_info is not None, "Error info not available"
        assert 'error_info' in error_info, "Structured error info missing"
        
        structured_info = error_info['error_info']
        assert structured_info is not None, "Structured error info is None"
        assert hasattr(structured_info, 'solutions'), "Solutions not available"
        assert len(structured_info.solutions) > 0, "No solutions provided"
        
        # Verify solution structure
        solution = structured_info.solutions[0]
        assert hasattr(solution, 'title'), "Solution missing title"
        assert hasattr(solution, 'steps'), "Solution missing steps"
        assert len(solution.steps) > 0, "Solution has no steps"

def test_error_callback_enhanced_data():
    """Test that error callbacks receive enhanced error data"""
    with patch('connection_manager.get_logger'), \
         patch('connection_manager.get_stats'), \
         patch('connection_manager.get_config'):
        from connection_manager import ConnectionManager
        
        conn = ConnectionManager()
        
        # Register callback to capture enhanced data
        callback_data = None
        
        def enhanced_callback(error_data):
            nonlocal callback_data
            callback_data = error_data
        
        conn.register_error_recovery_callback(enhanced_callback)
        
        # Trigger error
        conn._handle_error_with_code(
            "interface_not_found",
            "Interface detection failed",
            {"mode": "usb", "expected_interface": "usb0"}
        )
        
        # Verify enhanced data structure
        assert callback_data is not None, "Callback not called"
        
        required_fields = ['code', 'message', 'context', 'error_info', 'timestamp']
        for field in required_fields:
            assert field in callback_data, f"Enhanced callback missing field: {field}"
        
        # Verify error_info contains structured data
        error_info = callback_data['error_info']
        assert error_info is not None, "Error info not provided to callback"
        assert hasattr(error_info, 'title'), "Error info missing title"
        assert hasattr(error_info, 'category'), "Error info missing category"
        assert hasattr(error_info, 'severity'), "Error info missing severity"
        assert hasattr(error_info, 'solutions'), "Error info missing solutions"

def test_fallback_error_handling():
    """Test fallback error handling when error database fails"""
    with patch('connection_manager.get_logger'), \
         patch('connection_manager.get_stats'), \
         patch('connection_manager.get_config'):
        from connection_manager import ConnectionManager
        
        conn = ConnectionManager()
        
        # Mock get_error_info to raise exception
        with patch('connection_manager.get_error_info', side_effect=Exception("Database error")):
            # Should not crash, should fall back to basic error handling
            conn._handle_error_with_code(
                "test_fallback_error",
                "Test fallback message",
                {"fallback": True}
            )
            
            # Verify basic error handling still works
            assert conn.last_error == "Test fallback message", "Fallback error message not stored"
            assert conn.state.value == "error", "Error state not set in fallback"

def test_error_context_preservation():
    """Test that error context is preserved through the recovery system"""
    with patch('connection_manager.get_logger'), \
         patch('connection_manager.get_stats'), \
         patch('connection_manager.get_config'):
        from connection_manager import ConnectionManager
        
        conn = ConnectionManager()
        
        # Complex context data
        context = {
            "mode": "wifi",
            "interface": "wlan0",
            "script": "/usr/local/bin/pdanet-wifi-connect",
            "ssid": "TestNetwork",
            "password_provided": True,
            "stealth_level": 2,
            "retry_count": 3,
            "timestamp": time.time()
        }
        
        conn._handle_error_with_code(
            "connection_failed",
            "WiFi connection attempt failed",
            context
        )
        
        # Verify all context is preserved
        error_info = conn.get_last_error_info()
        stored_context = error_info['context']
        
        for key, value in context.items():
            assert key in stored_context, f"Context key '{key}' not preserved"
            assert stored_context[key] == value, f"Context value for '{key}' not preserved correctly"

test("Reliability Manager Error Reporting", test_reliability_manager_error_reporting)
test("Error Recovery with Structured Solutions", test_error_recovery_with_structured_solutions)
test("Error Callback Enhanced Data", test_error_callback_enhanced_data)
test("Fallback Error Handling", test_fallback_error_handling)
test("Error Context Preservation", test_error_context_preservation)

# Test Suite 5: Integration and Edge Cases
print("\n[5/5] INTEGRATION AND EDGE CASES")
print("-" * 80)

def test_multiple_error_callbacks():
    """Test multiple error recovery callbacks work correctly"""
    with patch('connection_manager.get_logger'), \
         patch('connection_manager.get_stats'), \
         patch('connection_manager.get_config'):
        from connection_manager import ConnectionManager
        
        conn = ConnectionManager()
        
        # Register multiple callbacks
        callback1_called = False
        callback2_called = False
        
        def callback1(error_data):
            nonlocal callback1_called
            callback1_called = True
        
        def callback2(error_data):
            nonlocal callback2_called
            callback2_called = True
        
        conn.register_error_recovery_callback(callback1)
        conn.register_error_recovery_callback(callback2)
        
        # Trigger error
        conn._handle_error_with_code("test_multi_callback", "Multi callback test", {})
        
        # Verify both callbacks were called
        assert callback1_called, "First callback not called"
        assert callback2_called, "Second callback not called"

def test_error_callback_exception_handling():
    """Test that callback exceptions don't break error handling"""
    with patch('connection_manager.get_logger'), \
         patch('connection_manager.get_stats'), \
         patch('connection_manager.get_config'):
        from connection_manager import ConnectionManager
        
        conn = ConnectionManager()
        
        # Register callback that raises exception
        def failing_callback(error_data):
            raise Exception("Callback failed")
        
        def working_callback(error_data):
            working_callback.called = True
        
        working_callback.called = False
        
        conn.register_error_recovery_callback(failing_callback)
        conn.register_error_recovery_callback(working_callback)
        
        # Trigger error - should not crash
        conn._handle_error_with_code("test_callback_exception", "Callback exception test", {})
        
        # Verify error handling still worked
        assert conn.last_error == "Callback exception test", "Error handling failed due to callback exception"
        assert working_callback.called, "Working callback not called due to failing callback"

def test_concurrent_error_handling():
    """Test error handling works correctly with concurrent operations"""
    with patch('connection_manager.get_logger'), \
         patch('connection_manager.get_stats'), \
         patch('connection_manager.get_config'):
        from connection_manager import ConnectionManager
        import threading
        
        conn = ConnectionManager()
        
        # Track errors from multiple threads
        errors_handled = []
        
        def error_callback(error_data):
            errors_handled.append(error_data['code'])
        
        conn.register_error_recovery_callback(error_callback)
        
        # Trigger errors from multiple threads
        def trigger_error(error_code):
            conn._handle_error_with_code(error_code, f"Error from {error_code}", {"thread": threading.current_thread().name})
        
        threads = []
        for i in range(3):
            thread = threading.Thread(target=trigger_error, args=(f"concurrent_error_{i}",))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads
        for thread in threads:
            thread.join()
        
        # Verify all errors were handled
        assert len(errors_handled) == 3, f"Expected 3 errors, got {len(errors_handled)}"
        for i in range(3):
            assert f"concurrent_error_{i}" in errors_handled, f"Error concurrent_error_{i} not handled"

def test_error_recovery_system_performance():
    """Test error recovery system performance with many errors"""
    with patch('connection_manager.get_logger'), \
         patch('connection_manager.get_stats'), \
         patch('connection_manager.get_config'):
        from connection_manager import ConnectionManager
        
        conn = ConnectionManager()
        
        # Measure time for handling many errors
        start_time = time.time()
        
        for i in range(100):
            conn._handle_error_with_code(
                "performance_test_error",
                f"Performance test error {i}",
                {"iteration": i}
            )
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Should handle 100 errors in reasonable time (< 1 second)
        assert total_time < 1.0, f"Error handling too slow: {total_time:.3f}s for 100 errors"
        
        # Verify last error is correct
        error_info = conn.get_last_error_info()
        assert error_info['code'] == "performance_test_error", "Last error code incorrect"
        assert "Performance test error 99" in error_info['message'], "Last error message incorrect"

def test_error_recovery_memory_usage():
    """Test that error recovery doesn't cause memory leaks"""
    with patch('connection_manager.get_logger'), \
         patch('connection_manager.get_stats'), \
         patch('connection_manager.get_config'):
        from connection_manager import ConnectionManager
        import gc
        
        conn = ConnectionManager()
        
        # Force garbage collection before test
        gc.collect()
        initial_objects = len(gc.get_objects())
        
        # Generate many errors
        for i in range(50):
            conn._handle_error_with_code(
                "memory_test_error",
                f"Memory test error {i}",
                {"large_context": "x" * 1000}  # Large context data
            )
        
        # Force garbage collection after test
        gc.collect()
        final_objects = len(gc.get_objects())
        
        # Object count shouldn't grow excessively
        object_growth = final_objects - initial_objects
        assert object_growth < 1000, f"Excessive object growth: {object_growth} objects"

test("Multiple Error Callbacks", test_multiple_error_callbacks)
test("Error Callback Exception Handling", test_error_callback_exception_handling)
test("Concurrent Error Handling", test_concurrent_error_handling)
test("Error Recovery System Performance", test_error_recovery_system_performance)
test("Error Recovery Memory Usage", test_error_recovery_memory_usage)

# Summary
print("\n" + "=" * 80)
print("P2 UX ERROR RECOVERY SYSTEM TEST SUMMARY")
print("=" * 80)

passed = sum(1 for _, success, _ in test_results if success)
failed = sum(1 for _, success, _ in test_results if not success)
total = len(test_results)

print(f"\nTotal Tests: {total}")
print(f"Passed: {passed} ✓")
print(f"Failed: {failed} ✗")
print(f"Success Rate: {(passed/total)*100:.1f}%")

# Group results by test suite
test_suites = {
    "Error Database Functionality": test_results[0:5],
    "Connection Manager Error Recovery Integration": test_results[5:10],
    "Error Recovery in Connection Scenarios": test_results[10:16],
    "Reliability Manager Integration": test_results[16:21],
    "Integration and Edge Cases": test_results[21:26]
}

print("\nRESULTS BY TEST SUITE:")
for suite_name, suite_tests in test_suites.items():
    suite_passed = sum(1 for _, success, _ in suite_tests if success)
    suite_total = len(suite_tests)
    print(f"\n{suite_name}: {suite_passed}/{suite_total} passed")
    
    for name, success, error in suite_tests:
        status = "✓" if success else "✗"
        print(f"  {status} {name}")
        if not success and error:
            print(f"    Error: {error}")

# Critical Issues Summary
critical_failures = []
for name, success, error in test_results:
    if not success:
        critical_failures.append((name, error))

if critical_failures:
    print(f"\n⚠️  CRITICAL ISSUES FOUND ({len(critical_failures)}):")
    for name, error in critical_failures:
        print(f"  • {name}: {error}")

print("\n" + "=" * 80)
if failed == 0:
    print("✅ P2 UX ERROR RECOVERY SYSTEM FULLY FUNCTIONAL")
    print("✅ Error Database: Structured error codes and solutions - WORKING")
    print("✅ Error Recovery Integration: Enhanced error handling in connection manager - WORKING")
    print("✅ Error Recovery Callbacks: Enhanced callbacks with structured data - WORKING")
    print("✅ Backward Compatibility: Legacy error callbacks still functional - WORKING")
    print("✅ Error Context Data: Contextual information properly captured - WORKING")
    print("✅ ENTERPRISE-GRADE ERROR RECOVERY SYSTEM - OPERATIONAL")
else:
    print("❌ P2 UX ERROR RECOVERY SYSTEM HAS ISSUES")
    print("🔍 Review failed tests above for specific error recovery problems")

print("\n" + "=" * 80)
print("P2 UX ERROR RECOVERY TESTING COMPLETE")
print("Enhanced error handling with structured solutions and recovery callbacks")
print("=" * 80)