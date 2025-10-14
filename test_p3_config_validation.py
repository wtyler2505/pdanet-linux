#!/usr/bin/env python3
"""
Test Configuration Validation System
Verifies the P3 config validation functionality
"""

import os
import sys
import json
import tempfile
from pathlib import Path

# Add src to path
sys.path.insert(0, "/app/src")

print("=" * 70)
print("P3 CONFIGURATION VALIDATION SYSTEM TEST")
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

# Test Suite: Configuration Validation
print("[1/5] CONFIGURATION VALIDATION CORE FUNCTIONALITY")
print("-" * 70)

def test_config_validator_import():
    """Test config validator imports correctly"""
    from config_validator import ConfigValidator
    
    validator = ConfigValidator()
    assert validator is not None, "ConfigValidator not created"
    assert hasattr(validator, 'validate_config'), "validate_config method missing"
    assert hasattr(validator, 'SCHEMA'), "Schema not defined"
    assert hasattr(validator, 'DEFAULTS'), "Defaults not defined"

def test_schema_validation():
    """Test schema validation with valid and invalid configs"""
    from config_validator import ConfigValidator
    
    validator = ConfigValidator()
    
    # Test valid config
    valid_config = {
        "proxy_host": "192.168.49.1",
        "proxy_port": 8000,
        "connection_timeout": 30,
        "stealth_level": 3,
        "window_width": 900,
        "theme": "cyberpunk"
    }
    
    is_valid, errors = validator.validate_config(valid_config)
    assert is_valid, f"Valid config rejected: {errors}"
    assert len(errors) == 0, f"Unexpected errors: {errors}"
    
    # Test invalid config
    invalid_config = {
        "proxy_host": "invalid-ip",
        "proxy_port": 99999,  # Out of range
        "connection_timeout": -5,  # Negative
        "stealth_level": 10,  # Out of range
        "theme": "invalid_theme"  # Invalid enum
    }
    
    is_valid, errors = validator.validate_config(invalid_config)
    assert not is_valid, "Invalid config accepted"
    assert len(errors) > 0, "No errors reported for invalid config"

def test_custom_validation_rules():
    """Test custom validation rules"""
    from config_validator import ConfigValidator
    
    validator = ConfigValidator()
    
    # Test data warning/limit relationship
    invalid_data_config = {
        "data_warning_mb": 2000,
        "data_limit_mb": 1000  # Warning higher than limit
    }
    
    is_valid, errors = validator.validate_config(invalid_data_config)
    assert not is_valid, "Data warning > limit should be invalid"
    
    warning_error = any("data_warning_mb should be less than data_limit_mb" in error for error in errors)
    assert warning_error, "Data warning validation rule not triggered"

def test_integrity_verification():
    """Test config integrity verification"""
    from config_validator import ConfigValidator
    
    validator = ConfigValidator()
    
    # Test config with integrity hash
    config_data = {"proxy_port": 8000, "stealth_level": 3}
    config_with_hash = validator.add_integrity_hash(config_data)
    
    assert "_integrity_hash" in config_with_hash, "Integrity hash not added"
    
    # Verify integrity
    integrity_ok = validator.verify_integrity(config_with_hash.copy())
    assert integrity_ok, "Integrity verification failed for valid config"
    
    # Test tampered config
    tampered_config = config_with_hash.copy()
    tampered_config["proxy_port"] = 9000  # Change value
    
    integrity_ok = validator.verify_integrity(tampered_config)
    assert not integrity_ok, "Integrity verification should fail for tampered config"

def test_config_migration():
    """Test configuration migration"""
    from config_validator import ConfigValidator
    
    validator = ConfigValidator()
    
    # Test v1.0 config migration
    old_config = {
        "config_version": "1.0",
        "proxy_port": 8000,
        "log_to_file": True,  # Old field name
        "auto_start": True  # Old field name
    }
    
    migrated_config = validator.migrate_config(old_config)
    
    assert migrated_config["config_version"] == "2.0", "Config not migrated to v2.0"
    assert "enable_file_logging" in migrated_config, "New field name not added"
    assert "start_minimized" in migrated_config, "Renamed field not migrated"
    assert migrated_config["enable_file_logging"] == True, "Old value not preserved"

test("Config Validator Import", test_config_validator_import)
test("Schema Validation", test_schema_validation)
test("Custom Validation Rules", test_custom_validation_rules)
test("Integrity Verification", test_integrity_verification)
test("Config Migration", test_config_migration)

# Test Suite: Config Manager Integration
print("\n[2/5] CONFIG MANAGER INTEGRATION")
print("-" * 70)

def test_config_manager_validation_integration():
    """Test config manager uses validation system"""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        from config_manager import ConfigManager
        
        config = ConfigManager(config_dir=temp_path)
        assert hasattr(config, 'validator'), "Validator not integrated into ConfigManager"
        assert config.validator is not None, "Validator not initialized"

def test_enhanced_save_load():
    """Test enhanced save and load with validation"""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        from config_manager import ConfigManager
        
        # Create config manager
        config = ConfigManager(config_dir=temp_path)
        
        # Set some values
        config.set("proxy_port", 8080)
        config.set("stealth_level", 4)
        
        # Verify config was saved with integrity
        config_file = temp_path / "config.json"
        assert config_file.exists(), "Config file not created"
        
        with open(config_file) as f:
            saved_data = json.load(f)
        
        assert "_integrity_hash" in saved_data, "Integrity hash not saved"
        assert saved_data["proxy_port"] == 8080, "Config value not saved correctly"

def test_invalid_value_rejection():
    """Test that invalid values are rejected"""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        from config_manager import ConfigManager
        
        config = ConfigManager(config_dir=temp_path)
        
        # Try to set invalid values
        try:
            config.set("proxy_port", 99999)  # Out of range
            assert False, "Invalid port value should be rejected"
        except ValueError:
            pass  # Expected
        
        try:
            config.set("theme", "invalid_theme")  # Invalid enum
            assert False, "Invalid theme should be rejected"
        except ValueError:
            pass  # Expected

def test_config_backup_system():
    """Test automatic backup creation"""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        from config_manager import ConfigManager
        
        config = ConfigManager(config_dir=temp_path)
        
        # Set initial value and save
        config.set("proxy_port", 8000)
        
        # Change value (should create backup)
        config.set("proxy_port", 8080)
        
        # Check backup directory exists and has backups
        backup_dir = temp_path / "backups"
        assert backup_dir.exists(), "Backup directory not created"
        
        backup_files = list(backup_dir.glob("config_backup_*.json"))
        assert len(backup_files) >= 1, "No backup files created"

def test_config_fix_functionality():
    """Test automatic config fixing"""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        from config_manager import ConfigManager
        
        config = ConfigManager(config_dir=temp_path)
        
        # Test fix_config_issues method
        fixes = config.fix_config_issues()
        assert isinstance(fixes, list), "fix_config_issues should return list"
        
        # Test validate_current_config method  
        is_valid, errors, warnings = config.validate_current_config()
        assert isinstance(is_valid, bool), "validate_current_config should return boolean"
        assert isinstance(errors, list), "validate_current_config should return error list"
        assert isinstance(warnings, list), "validate_current_config should return warning list"

test("Config Manager Validation Integration", test_config_manager_validation_integration)
test("Enhanced Save/Load", test_enhanced_save_load)
test("Invalid Value Rejection", test_invalid_value_rejection)
test("Config Backup System", test_config_backup_system)
test("Config Fix Functionality", test_config_fix_functionality)

# Test Suite: Error Recovery and Edge Cases
print("\n[3/5] ERROR RECOVERY AND EDGE CASES")
print("-" * 70)

def test_corrupted_config_recovery():
    """Test recovery from corrupted config files"""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        from config_manager import ConfigManager
        
        # Create corrupted config file
        config_file = temp_path / "config.json"
        config_file.write_text("{ invalid json")
        
        # Should recover with defaults
        config = ConfigManager(config_dir=temp_path)
        config.load_config()
        
        # Should have moved corrupted file and created new one
        corrupted_files = list(temp_path.glob("*.corrupted.json"))
        assert len(corrupted_files) > 0, "Corrupted config not backed up"

def test_missing_config_fields():
    """Test handling of missing config fields"""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        from config_manager import ConfigManager
        
        # Create minimal config file
        config_file = temp_path / "config.json"
        minimal_config = {"proxy_port": 8000}
        config_file.write_text(json.dumps(minimal_config))
        
        config = ConfigManager(config_dir=temp_path)
        loaded_config = config.load_config()
        
        # Should have all default fields filled in
        from config_validator import ConfigValidator
        validator = ConfigValidator()
        defaults = validator.get_default_config()
        
        for key in defaults:
            assert key in loaded_config or key.startswith('_'), f"Missing default field: {key}"

def test_schema_evolution():
    """Test handling of schema evolution"""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        from config_validator import ConfigValidator
        
        validator = ConfigValidator()
        
        # Test that new fields can be added without breaking old configs
        old_config = {"proxy_port": 8000, "config_version": "2.0"}
        
        fixed_config, warnings = validator.validate_and_fix_config(old_config)
        
        # Should have added missing fields
        assert len(fixed_config) > len(old_config), "Missing fields not added"
        assert any("Added missing field" in warning for warning in warnings), "No missing field warnings"

def test_security_validation():
    """Test security-related validation"""
    from config_validator import ConfigValidator
    
    validator = ConfigValidator()
    
    # Test dangerous port validation
    dangerous_config = {"proxy_port": 22}  # SSH port
    
    is_valid, errors = validator.validate_config(dangerous_config)
    # Should warn about dangerous ports (this might be in custom validation)
    
    # Test DNS server validation
    bad_dns_config = {"dns_servers": ["invalid-ip", "300.300.300.300"]}
    
    is_valid, errors = validator.validate_config(bad_dns_config)
    assert not is_valid, "Invalid DNS servers should be rejected"

def test_atomic_save_operations():
    """Test atomic save operations"""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        from config_manager import ConfigManager
        
        config = ConfigManager(config_dir=temp_path)
        
        # Set a value to trigger save
        config.set("proxy_port", 8080)
        
        config_file = temp_path / "config.json"
        temp_file = temp_path / "config.json.tmp"
        
        # Temp file should not exist after successful save
        assert not temp_file.exists(), "Temporary file not cleaned up"
        assert config_file.exists(), "Config file not created"

test("Corrupted Config Recovery", test_corrupted_config_recovery)
test("Missing Config Fields", test_missing_config_fields)
test("Schema Evolution", test_schema_evolution)
test("Security Validation", test_security_validation)
test("Atomic Save Operations", test_atomic_save_operations)

# Test Results Summary
print("\n" + "=" * 70)
print("TEST RESULTS SUMMARY")
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

# Overall assessment
if failed_tests == 0:
    print(f"\n🎉 ALL TESTS PASSED! P3 Configuration Validation system is fully functional.")
    exit(0)
else:
    print(f"\n⚠️ {failed_tests} test(s) failed. System needs fixes before production.")
    exit(1)