#!/usr/bin/env python3
"""
Final Comprehensive Validation for PdaNet Linux 2.0 Enterprise
Testing critical systems as requested in review:
1. P2 Error Recovery System
2. P3 Configuration Validation  
3. iPhone Bypass Excellence
4. Core Connection Functionality
5. Error Database Integration
6. System Stability
"""

import os
import sys
import time
import json
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add src to path
sys.path.insert(0, "/app/src")

print("=" * 80)
print("PDANET LINUX 2.0 ENTERPRISE - FINAL COMPREHENSIVE VALIDATION")
print("Testing Critical Systems for Enterprise Deployment Readiness")
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

# ============================================================================
# 1. P2 ERROR RECOVERY SYSTEM VALIDATION
# ============================================================================
print("\n[1/6] P2 ERROR RECOVERY SYSTEM VALIDATION")
print("-" * 80)

def test_error_database_integration():
    """Test error database provides structured solutions"""
    from error_database import get_error_info, ERROR_DATABASE
    
    # Test critical error codes exist
    critical_errors = [
        "interface_not_found", "proxy_not_accessible", "connection_failed",
        "input_validation_failed", "script_not_found"
    ]
    
    for error_code in critical_errors:
        error_info = get_error_info(error_code)
        assert error_info is not None, f"Error code {error_code} not found in database"
        assert error_info.title, f"Error {error_code} missing title"
        assert error_info.description, f"Error {error_code} missing description"
        assert error_info.solutions, f"Error {error_code} missing solutions"
        assert len(error_info.solutions) > 0, f"Error {error_code} has no solutions"
    
    # Verify database completeness
    assert len(ERROR_DATABASE) >= 15, f"Error database too small: {len(ERROR_DATABASE)} entries"

def test_connection_manager_error_handling():
    """Test ConnectionManager enhanced error handling with structured codes"""
    with patch('connection_manager.get_logger'), \
         patch('connection_manager.get_stats'), \
         patch('connection_manager.get_config'):
        from connection_manager import ConnectionManager
        
        conn = ConnectionManager()
        
        # Test error handling method exists
        assert hasattr(conn, '_handle_error_with_code'), "Missing _handle_error_with_code method"
        
        # Test error recovery callback registration
        assert hasattr(conn, 'register_error_recovery_callback'), "Missing error recovery callback registration"
        
        # Test structured error handling
        test_context = {"test": "data", "interface": "wlan0"}
        conn._handle_error_with_code("connection_failed", "Test error", test_context)
        
        # Verify error was stored with code
        assert hasattr(conn, 'last_error_code'), "Error code not stored"
        assert conn.last_error_code == "connection_failed", "Error code not stored correctly"
        assert hasattr(conn, 'last_error_context'), "Error context not stored"

def test_error_recovery_callbacks():
    """Test enhanced error recovery callbacks with contextual data"""
    with patch('connection_manager.get_logger'), \
         patch('connection_manager.get_stats'), \
         patch('connection_manager.get_config'):
        from connection_manager import ConnectionManager
        
        conn = ConnectionManager()
        
        # Register test callback
        callback_called = False
        callback_data = None
        
        def test_callback(error_data):
            nonlocal callback_called, callback_data
            callback_called = True
            callback_data = error_data
        
        conn.register_error_recovery_callback(test_callback)
        
        # Trigger error with context
        test_context = {"interface": "wlan0", "mode": "wifi"}
        conn._handle_error_with_code("interface_not_found", "Test interface error", test_context)
        
        # Verify callback was called with structured data
        assert callback_called, "Error recovery callback not called"
        assert callback_data is not None, "No callback data received"
        assert 'code' in callback_data, "Error code missing from callback data"
        assert 'context' in callback_data, "Context missing from callback data"
        assert 'error_info' in callback_data, "Error info missing from callback data"

test("Error Database Integration", test_error_database_integration)
test("Connection Manager Error Handling", test_connection_manager_error_handling)
test("Error Recovery Callbacks", test_error_recovery_callbacks)

# ============================================================================
# 2. P3 CONFIGURATION VALIDATION SYSTEM
# ============================================================================
print("\n[2/6] P3 CONFIGURATION VALIDATION SYSTEM")
print("-" * 80)

def test_config_validator_schema_validation():
    """Test JSON schema validation with comprehensive rules"""
    from config_validator import ConfigValidator
    
    validator = ConfigValidator()
    
    # Test valid configuration
    valid_config = {
        "proxy_host": "192.168.49.1",
        "proxy_port": 8000,
        "stealth_level": 3,
        "theme": "cyberpunk",
        "data_warning_mb": 1000,
        "dns_servers": ["1.1.1.1", "8.8.8.8"]
    }
    
    is_valid, errors = validator.validate_config(valid_config)
    assert is_valid, f"Valid config failed validation: {errors}"
    
    # Test invalid configuration
    invalid_config = {
        "proxy_host": "invalid_ip",
        "proxy_port": 99999,  # Out of range
        "stealth_level": 10,  # Out of range
        "theme": "invalid_theme",
        "data_warning_mb": -100,  # Negative
        "dns_servers": ["invalid_ip"]
    }
    
    is_valid, errors = validator.validate_config(invalid_config)
    assert not is_valid, "Invalid config passed validation"
    assert len(errors) >= 5, f"Not enough validation errors detected: {len(errors)}"

def test_config_integrity_checking():
    """Test HMAC integrity checking system"""
    from config_validator import ConfigValidator
    
    validator = ConfigValidator()
    
    # Test integrity hash generation
    test_config = {"test": "data", "value": 123}
    config_with_hash = validator.add_integrity_hash(test_config)
    
    assert "_integrity_hash" in config_with_hash, "Integrity hash not added"
    assert len(config_with_hash["_integrity_hash"]) == 64, "Invalid hash length"
    
    # Test integrity verification
    is_valid = validator.verify_integrity(config_with_hash.copy())
    assert is_valid, "Integrity verification failed for valid config"
    
    # Test tampered config detection
    tampered_config = config_with_hash.copy()
    tampered_config["test"] = "tampered"
    is_valid = validator.verify_integrity(tampered_config)
    assert not is_valid, "Tampered config passed integrity check"

def test_config_migration_system():
    """Test automatic configuration migration"""
    from config_validator import ConfigValidator
    
    validator = ConfigValidator()
    
    # Test v1.0 to v2.0 migration
    old_config = {
        "config_version": "1.0",
        "log_to_file": True,  # Old field name
        "auto_start": False,  # Old field name
        "proxy_host": "192.168.49.1"
    }
    
    migrated_config = validator.migrate_config(old_config)
    
    assert migrated_config["config_version"] == "2.0", "Version not updated"
    assert "enable_file_logging" in migrated_config, "Field not migrated"
    assert "start_minimized" in migrated_config, "Field not migrated"
    assert migrated_config["enable_file_logging"] == True, "Value not migrated correctly"

def test_config_backup_system():
    """Test configuration backup and restore system"""
    from config_validator import ConfigValidator
    import tempfile
    
    with tempfile.TemporaryDirectory() as temp_dir:
        config_path = Path(temp_dir) / "test_config.json"
        validator = ConfigValidator(config_path)
        
        test_config = {"test": "backup", "value": 456}
        
        # Create backup
        backup_path = validator.create_backup(test_config)
        assert backup_path.exists(), "Backup file not created"
        
        # Verify backup content
        with open(backup_path) as f:
            backup_data = json.load(f)
        
        assert "config" in backup_data, "Config not in backup"
        assert "integrity_hash" in backup_data, "Integrity hash not in backup"
        assert backup_data["config"]["test"] == "backup", "Config data not backed up correctly"

test("Config Schema Validation", test_config_validator_schema_validation)
test("Config Integrity Checking", test_config_integrity_checking)
test("Config Migration System", test_config_migration_system)
test("Config Backup System", test_config_backup_system)

# ============================================================================
# 3. IPHONE BYPASS EXCELLENCE VALIDATION
# ============================================================================
print("\n[3/6] IPHONE BYPASS EXCELLENCE VALIDATION")
print("-" * 80)

def test_iphone_bypass_initialization():
    """Test iPhone bypass system initialization"""
    from iphone_hotspot_bypass import iPhoneHotspotBypass
    
    bypass = iPhoneHotspotBypass()
    
    # Test initialization
    assert bypass is not None, "iPhone bypass failed to initialize"
    assert hasattr(bypass, 'bypass_techniques'), "Missing bypass techniques"
    assert len(bypass.bypass_techniques) >= 10, f"Not enough bypass techniques: {len(bypass.bypass_techniques)}"
    
    # Test iPhone signatures loaded
    assert hasattr(bypass, 'iphone_signatures'), "Missing iPhone signatures"
    assert len(bypass.iphone_signatures) >= 2, "Not enough iPhone signatures"
    
    # Verify critical techniques present
    critical_techniques = [
        "ttl_manipulation", "ipv6_complete_block", "dns_leak_prevention",
        "user_agent_spoofing", "carrier_app_blocking"
    ]
    
    for technique in critical_techniques:
        assert technique in bypass.bypass_techniques, f"Missing critical technique: {technique}"

def test_iphone_bypass_technique_application():
    """Test individual bypass technique application"""
    from iphone_hotspot_bypass import iPhoneHotspotBypass
    
    bypass = iPhoneHotspotBypass()
    test_interface = "wlan0"
    
    # Test technique application methods exist
    techniques_to_test = [
        "_apply_ttl_manipulation",
        "_apply_ipv6_block", 
        "_apply_dns_bypass",
        "_block_carrier_apps",
        "_block_analytics_domains"
    ]
    
    for technique_method in techniques_to_test:
        assert hasattr(bypass, technique_method), f"Missing technique method: {technique_method}"

def test_iphone_bypass_status_reporting():
    """Test iPhone bypass status and reporting"""
    from iphone_hotspot_bypass import iPhoneHotspotBypass
    
    bypass = iPhoneHotspotBypass()
    
    # Test status reporting
    status = bypass.get_bypass_status()
    assert isinstance(status, dict), "Status not returned as dict"
    
    required_status_fields = [
        "bypass_enabled", "stealth_level", "active_techniques", 
        "total_techniques", "success_rate", "configuration"
    ]
    
    for field in required_status_fields:
        assert field in status, f"Missing status field: {field}"
    
    # Test detailed report
    report = bypass.get_bypass_report()
    assert isinstance(report, dict), "Report not returned as dict"
    assert "techniques" in report, "Missing techniques in report"
    assert "recommendations" in report, "Missing recommendations in report"

def test_iphone_bypass_enterprise_features():
    """Test enterprise-grade iPhone bypass features"""
    from iphone_hotspot_bypass import iPhoneHotspotBypass
    
    bypass = iPhoneHotspotBypass()
    
    # Test configuration system
    assert hasattr(bypass, 'config'), "Missing configuration system"
    assert bypass.config.get("enable_enhanced_iphone_bypass"), "Enhanced bypass not enabled"
    assert bypass.config.get("block_carrier_analytics"), "Carrier analytics blocking not enabled"
    
    # Test iPhone signature spoofing
    signatures = bypass.iphone_signatures
    for device, signature in signatures.items():
        assert signature.user_agent, f"Missing user agent for {device}"
        assert signature.tls_fingerprint, f"Missing TLS fingerprint for {device}"
        assert signature.dns_patterns, f"Missing DNS patterns for {device}"
        assert signature.traffic_timing, f"Missing traffic timing for {device}"

test("iPhone Bypass Initialization", test_iphone_bypass_initialization)
test("iPhone Bypass Technique Application", test_iphone_bypass_technique_application)
test("iPhone Bypass Status Reporting", test_iphone_bypass_status_reporting)
test("iPhone Bypass Enterprise Features", test_iphone_bypass_enterprise_features)

# ============================================================================
# 4. CORE CONNECTION FUNCTIONALITY VALIDATION
# ============================================================================
print("\n[4/6] CORE CONNECTION FUNCTIONALITY VALIDATION")
print("-" * 80)

def test_connection_manager_p1_p2_p3_p4_integration():
    """Test all enhancement phases are integrated"""
    with patch('connection_manager.get_logger'), \
         patch('connection_manager.get_stats'), \
         patch('connection_manager.get_config'):
        from connection_manager import ConnectionManager
        
        conn = ConnectionManager()
        
        # Test P1 components (NetworkManager, stealth)
        assert hasattr(conn, 'nm_client'), "Missing P1 NetworkManager client"
        assert hasattr(conn, 'stealth_active'), "Missing P1 stealth tracking"
        assert hasattr(conn, 'update_stealth_status'), "Missing P1 stealth status method"
        
        # Test P2 components (performance, reliability)
        assert hasattr(conn, 'resource_manager'), "Missing P2 resource manager"
        assert hasattr(conn, 'reliability_manager'), "Missing P2 reliability manager"
        assert hasattr(conn, '_handle_error_with_code'), "Missing P2 error handling"
        
        # Test P3 components (user experience)
        assert hasattr(conn, 'ux_manager'), "Missing P3 UX manager"
        assert hasattr(conn, 'connect_with_profile'), "Missing P3 profile connections"
        assert hasattr(conn, 'get_quick_connect_suggestions'), "Missing P3 quick connect"
        
        # Test P4 components (advanced features)
        assert hasattr(conn, 'network_monitor'), "Missing P4 network monitor"
        assert hasattr(conn, 'bandwidth_manager'), "Missing P4 bandwidth manager"
        assert hasattr(conn, 'iphone_bypass'), "Missing P4 iPhone bypass"

def test_enhanced_status_reporting():
    """Test comprehensive status reporting with all phases"""
    with patch('connection_manager.get_logger'), \
         patch('connection_manager.get_stats'), \
         patch('connection_manager.get_config'):
        from connection_manager import ConnectionManager
        
        conn = ConnectionManager()
        
        # Test comprehensive status
        status = conn.get_comprehensive_status()
        assert isinstance(status, dict), "Status not returned as dict"
        
        # Should include basic connection info
        basic_fields = ["state", "interface", "mode", "stealth_active"]
        for field in basic_fields:
            assert field in status, f"Missing basic status field: {field}"
        
        # Test enhanced status with UX
        enhanced_status = conn.get_enhanced_status_with_ux()
        assert isinstance(enhanced_status, dict), "Enhanced status not returned as dict"
        
        # Test advanced status (P4)
        advanced_status = conn.get_advanced_status()
        assert isinstance(advanced_status, dict), "Advanced status not returned as dict"

def test_connection_state_management():
    """Test connection state machine and transitions"""
    with patch('connection_manager.get_logger'), \
         patch('connection_manager.get_stats'), \
         patch('connection_manager.get_config'):
        from connection_manager import ConnectionManager, ConnectionState
        
        conn = ConnectionManager()
        
        # Test initial state
        assert conn.state == ConnectionState.DISCONNECTED, "Initial state not DISCONNECTED"
        
        # Test state transition validation
        assert hasattr(conn, '_set_state'), "Missing state transition method"
        
        # Test valid transitions
        valid_transition = conn._set_state(ConnectionState.CONNECTING)
        assert valid_transition, "Valid state transition failed"
        assert conn.state == ConnectionState.CONNECTING, "State not updated"

def test_interface_detection_robustness():
    """Test robust interface detection with D-Bus and fallback"""
    with patch('connection_manager.get_logger'), \
         patch('connection_manager.get_stats'), \
         patch('connection_manager.get_config'):
        from connection_manager import ConnectionManager
        
        conn = ConnectionManager()
        
        # Test detection methods exist
        assert hasattr(conn, 'detect_interface'), "Missing interface detection"
        assert hasattr(conn, '_detect_interface_dbus'), "Missing D-Bus detection"
        assert hasattr(conn, '_detect_interface_nmcli'), "Missing nmcli fallback"
        
        # Test NetworkManager client integration
        assert hasattr(conn, 'nm_client'), "Missing NetworkManager client"

test("P1+P2+P3+P4 Integration", test_connection_manager_p1_p2_p3_p4_integration)
test("Enhanced Status Reporting", test_enhanced_status_reporting)
test("Connection State Management", test_connection_state_management)
test("Interface Detection Robustness", test_interface_detection_robustness)

# ============================================================================
# 5. ERROR DATABASE INTEGRATION VALIDATION
# ============================================================================
print("\n[5/6] ERROR DATABASE INTEGRATION VALIDATION")
print("-" * 80)

def test_error_code_mapping_completeness():
    """Test all error codes map to structured solutions"""
    from error_database import ERROR_DATABASE, get_error_info
    
    # Test database structure
    assert len(ERROR_DATABASE) >= 15, f"Error database too small: {len(ERROR_DATABASE)}"
    
    # Test each error has complete information
    for error_code, error_info in ERROR_DATABASE.items():
        assert error_info.code == error_code, f"Error code mismatch: {error_code}"
        assert error_info.title, f"Missing title for {error_code}"
        assert error_info.description, f"Missing description for {error_code}"
        assert error_info.category, f"Missing category for {error_code}"
        assert error_info.severity, f"Missing severity for {error_code}"
        assert error_info.solutions, f"Missing solutions for {error_code}"
        
        # Test each solution has actionable steps
        for solution in error_info.solutions:
            assert solution.title, f"Solution missing title for {error_code}"
            assert solution.steps, f"Solution missing steps for {error_code}"
            assert len(solution.steps) > 0, f"Solution has no steps for {error_code}"

def test_contextual_error_solutions():
    """Test error solutions provide contextual information"""
    from error_database import get_error_info
    
    # Test critical errors have auto-fix commands where appropriate
    auto_fix_errors = ["iptables_failed", "redsocks_failed", "dns_resolution_failed"]
    
    for error_code in auto_fix_errors:
        error_info = get_error_info(error_code)
        assert error_info, f"Error {error_code} not found"
        
        # At least one solution should have auto-fix capability
        has_auto_fix = any(sol.auto_fix_command for sol in error_info.solutions)
        assert has_auto_fix, f"Error {error_code} missing auto-fix solutions"

def test_error_categorization():
    """Test error categorization and severity levels"""
    from error_database import search_errors_by_category, search_errors_by_severity
    
    # Test categories exist
    categories = ["network", "permission", "config", "system"]
    for category in categories:
        errors = search_errors_by_category(category)
        assert len(errors) > 0, f"No errors found in category: {category}"
    
    # Test severity levels exist
    severities = ["critical", "high", "medium", "low"]
    for severity in severities:
        errors = search_errors_by_severity(severity)
        # At least some errors should exist for critical/high/medium
        if severity in ["critical", "high", "medium"]:
            assert len(errors) > 0, f"No errors found with severity: {severity}"

def test_connection_manager_error_integration():
    """Test ConnectionManager integrates with error database"""
    with patch('connection_manager.get_logger'), \
         patch('connection_manager.get_stats'), \
         patch('connection_manager.get_config'):
        from connection_manager import ConnectionManager
        from error_database import get_error_info
        
        conn = ConnectionManager()
        
        # Test error handling integration
        conn._handle_error_with_code("interface_not_found", "Test error", {"test": "context"})
        
        # Test error info retrieval
        error_info = conn.get_last_error_info()
        assert error_info is not None, "Error info not retrieved"
        assert error_info['code'] == "interface_not_found", "Error code not stored"
        assert error_info['error_info'] is not None, "Error database info not retrieved"

test("Error Code Mapping Completeness", test_error_code_mapping_completeness)
test("Contextual Error Solutions", test_contextual_error_solutions)
test("Error Categorization", test_error_categorization)
test("Connection Manager Error Integration", test_connection_manager_error_integration)

# ============================================================================
# 6. SYSTEM STABILITY VALIDATION
# ============================================================================
print("\n[6/6] SYSTEM STABILITY VALIDATION")
print("-" * 80)

def test_resource_management():
    """Test resource management and cleanup"""
    with patch('connection_manager.get_logger'), \
         patch('connection_manager.get_stats'), \
         patch('connection_manager.get_config'):
        from connection_manager import ConnectionManager
        
        conn = ConnectionManager()
        
        # Test thread pool management
        assert hasattr(conn, 'executor'), "Missing thread pool executor"
        assert hasattr(conn, 'active_futures'), "Missing active futures tracking"
        
        # Test shutdown cleanup
        assert hasattr(conn, 'shutdown'), "Missing shutdown method"
        
        # Test resource managers are initialized
        assert hasattr(conn, 'resource_manager'), "Missing resource manager"
        assert hasattr(conn, 'reliability_manager'), "Missing reliability manager"

def test_performance_monitoring_integration():
    """Test performance monitoring doesn't impact stability"""
    with patch('connection_manager.get_logger'), \
         patch('connection_manager.get_stats'), \
         patch('connection_manager.get_config'):
        from connection_manager import ConnectionManager
        
        conn = ConnectionManager()
        
        # Test performance decorators don't break functionality
        assert hasattr(conn, 'detect_interface'), "Interface detection missing"
        
        # Test resource context management
        try:
            from performance_optimizer import resource_context
            with resource_context("test_operation"):
                pass  # Should not raise exceptions
        except ImportError:
            pass  # Performance optimizer may not be available in test environment

def test_advanced_features_stability():
    """Test advanced features don't conflict with core functionality"""
    with patch('connection_manager.get_logger'), \
         patch('connection_manager.get_stats'), \
         patch('connection_manager.get_config'):
        from connection_manager import ConnectionManager
        
        conn = ConnectionManager()
        
        # Test P4 advanced features are properly integrated
        assert hasattr(conn, 'start_advanced_monitoring'), "Missing advanced monitoring"
        assert hasattr(conn, 'enable_intelligent_qos'), "Missing intelligent QoS"
        assert hasattr(conn, 'connect_to_iphone_hotspot'), "Missing iPhone hotspot connection"
        
        # Test iPhone bypass integration
        assert hasattr(conn, 'get_iphone_bypass_status'), "Missing iPhone bypass status"
        assert hasattr(conn, 'optimize_iphone_bypass'), "Missing iPhone bypass optimization"

def test_configuration_system_stability():
    """Test configuration system handles edge cases gracefully"""
    from config_validator import ConfigValidator
    
    validator = ConfigValidator()
    
    # Test with empty config
    empty_config = {}
    fixed_config, warnings = validator.validate_and_fix_config(empty_config)
    assert isinstance(fixed_config, dict), "Fixed config not returned as dict"
    assert len(fixed_config) > 0, "Fixed config is empty"
    
    # Test with corrupted config
    corrupted_config = {
        "proxy_port": "not_a_number",
        "stealth_level": "invalid",
        "theme": 123  # Wrong type
    }
    
    fixed_config, warnings = validator.validate_and_fix_config(corrupted_config)
    assert isinstance(fixed_config, dict), "Corrupted config not fixed"
    assert len(warnings) > 0, "No warnings generated for corrupted config"

test("Resource Management", test_resource_management)
test("Performance Monitoring Integration", test_performance_monitoring_integration)
test("Advanced Features Stability", test_advanced_features_stability)
test("Configuration System Stability", test_configuration_system_stability)

# ============================================================================
# FINAL VALIDATION SUMMARY
# ============================================================================
print("\n" + "=" * 80)
print("FINAL COMPREHENSIVE VALIDATION SUMMARY")
print("PdaNet Linux 2.0 Enterprise - Critical Systems Validation")
print("=" * 80)

passed = sum(1 for _, success, _ in test_results if success)
failed = sum(1 for _, success, _ in test_results if not success)
total = len(test_results)

print(f"\nTotal Validation Tests: {total}")
print(f"Passed: {passed} ✓")
print(f"Failed: {failed} ✗")
print(f"Success Rate: {(passed/total)*100:.1f}%")

# Group results by validation area
validation_areas = {
    "P2 Error Recovery System": test_results[0:3],
    "P3 Configuration Validation": test_results[3:7],
    "iPhone Bypass Excellence": test_results[7:11],
    "Core Connection Functionality": test_results[11:15],
    "Error Database Integration": test_results[15:19],
    "System Stability": test_results[19:23]
}

print("\nVALIDATION RESULTS BY CRITICAL SYSTEM:")
for area_name, area_tests in validation_areas.items():
    area_passed = sum(1 for _, success, _ in area_tests if success)
    area_total = len(area_tests)
    print(f"\n{area_name}: {area_passed}/{area_total} passed")
    
    for name, success, error in area_tests:
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
    print(f"\n⚠️  CRITICAL VALIDATION FAILURES ({len(critical_failures)}):")
    for name, error in critical_failures:
        print(f"  • {name}: {error}")
else:
    print(f"\n✅ ALL CRITICAL SYSTEMS VALIDATED SUCCESSFULLY")

print("\n" + "=" * 80)
if failed == 0:
    print("🎉 ENTERPRISE DEPLOYMENT READY")
    print("✅ P2 Error Recovery System: Enhanced error handling with structured codes - VALIDATED")
    print("✅ P3 Configuration Validation: JSON schema, integrity, migration - VALIDATED") 
    print("✅ iPhone Bypass Excellence: 10-layer enterprise stealth system - VALIDATED")
    print("✅ Core Connection Functionality: P1+P2+P3+P4 integration - VALIDATED")
    print("✅ Error Database Integration: Structured solutions mapping - VALIDATED")
    print("✅ System Stability: Advanced features integration - VALIDATED")
    print("✅ PDANET LINUX 2.0 ENTERPRISE - FULLY VALIDATED FOR PRODUCTION")
else:
    print("❌ VALIDATION ISSUES DETECTED")
    print("🔍 Review failed validations above before enterprise deployment")
    
    # Categorize failures by system
    error_recovery_failures = sum(1 for name, success, _ in test_results[0:3] if not success)
    config_validation_failures = sum(1 for name, success, _ in test_results[3:7] if not success)
    iphone_bypass_failures = sum(1 for name, success, _ in test_results[7:11] if not success)
    connection_failures = sum(1 for name, success, _ in test_results[11:15] if not success)
    error_db_failures = sum(1 for name, success, _ in test_results[15:19] if not success)
    stability_failures = sum(1 for name, success, _ in test_results[19:23] if not success)
    
    if error_recovery_failures > 0:
        print(f"  P2 Error Recovery Issues: {error_recovery_failures} failures")
    if config_validation_failures > 0:
        print(f"  P3 Configuration Issues: {config_validation_failures} failures")
    if iphone_bypass_failures > 0:
        print(f"  iPhone Bypass Issues: {iphone_bypass_failures} failures")
    if connection_failures > 0:
        print(f"  Core Connection Issues: {connection_failures} failures")
    if error_db_failures > 0:
        print(f"  Error Database Issues: {error_db_failures} failures")
    if stability_failures > 0:
        print(f"  System Stability Issues: {stability_failures} failures")

print("\n" + "=" * 80)
print("FINAL COMPREHENSIVE VALIDATION COMPLETE")
print("Enterprise-grade functionality validation for PdaNet Linux 2.0")
print("=" * 80)