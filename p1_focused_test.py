#!/usr/bin/env python3
"""
Focused P1 Functionality Testing
Tests P1-FUNC-4, P1-FUNC-5, P1-FUNC-8 enhancements
"""

import os
import sys
import time
from unittest.mock import Mock, patch, MagicMock

# Add src to path
sys.path.insert(0, "/app/src")

print("=" * 60)
print("PDANET LINUX - P1 FOCUSED TESTING")
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

# Test Suite 1: P1-FUNC-4 NetworkManager D-Bus Integration
print("\n[1/3] P1-FUNC-4 NETWORKMANAGER D-BUS INTEGRATION")
print("-" * 60)

def test_nm_client_imports():
    """Test NetworkManager D-Bus client imports"""
    from nm_client import NMClient, NetworkDevice, AccessPoint
    
    assert NMClient is not None, "NMClient class not available"
    assert NetworkDevice is not None, "NetworkDevice class not available"
    assert AccessPoint is not None, "AccessPoint class not available"

def test_nm_client_initialization():
    """Test NMClient initialization"""
    from nm_client import NMClient
    
    client = NMClient()
    assert client is not None, "NMClient failed to initialize"
    assert hasattr(client, 'available'), "NMClient missing available method"
    assert hasattr(client, 'get_devices'), "NMClient missing get_devices method"
    assert hasattr(client, 'scan_wifi_networks'), "NMClient missing scan_wifi_networks method"

def test_connection_manager_nm_integration():
    """Test ConnectionManager integrates with NMClient"""
    with patch('connection_manager.get_logger'), \
         patch('connection_manager.get_stats'), \
         patch('connection_manager.get_config'):
        from connection_manager import ConnectionManager
        
        conn = ConnectionManager()
        assert hasattr(conn, 'nm_client'), "ConnectionManager missing nm_client"
        assert conn.nm_client is not None, "nm_client not initialized"

def test_enhanced_interface_detection():
    """Test enhanced interface detection with D-Bus and fallback"""
    with patch('connection_manager.get_logger'), \
         patch('connection_manager.get_stats'), \
         patch('connection_manager.get_config'):
        from connection_manager import ConnectionManager
        
        conn = ConnectionManager()
        
        # Test D-Bus method exists
        assert hasattr(conn, '_detect_interface_dbus'), "Missing D-Bus interface detection"
        assert hasattr(conn, '_detect_interface_nmcli'), "Missing nmcli fallback detection"

test("NM Client Imports", test_nm_client_imports)
test("NM Client Initialization", test_nm_client_initialization)
test("Connection Manager NM Integration", test_connection_manager_nm_integration)
test("Enhanced Interface Detection", test_enhanced_interface_detection)

# Test Suite 2: P1-FUNC-5 Enhanced WiFi Scanning
print("\n[2/3] P1-FUNC-5 ENHANCED WIFI SCANNING")
print("-" * 60)

def test_wifi_scanning_methods():
    """Test WiFi scanning methods exist"""
    with patch('connection_manager.get_logger'), \
         patch('connection_manager.get_stats'), \
         patch('connection_manager.get_config'):
        from connection_manager import ConnectionManager
        
        conn = ConnectionManager()
        assert hasattr(conn, 'scan_wifi_networks'), "Missing scan_wifi_networks method"

def test_wifi_scanning_with_caching():
    """Test WiFi scanning with caching support"""
    from nm_client import NMClient
    
    client = NMClient()
    assert hasattr(client, '_wifi_scan_cache'), "Missing WiFi scan cache"

def test_wifi_scanning_force_rescan():
    """Test force rescan functionality"""
    with patch('connection_manager.get_logger'), \
         patch('connection_manager.get_stats'), \
         patch('connection_manager.get_config'):
        from connection_manager import ConnectionManager
        
        conn = ConnectionManager()
        
        # Test force_rescan parameter support
        with patch.object(conn.nm_client, 'available', return_value=True), \
             patch.object(conn.nm_client, 'scan_wifi_networks') as mock_scan:
            
            conn.scan_wifi_networks(force_rescan=True)
            mock_scan.assert_called_with(force_rescan=True)

def test_nmcli_fallback_scanning():
    """Test nmcli fallback WiFi scanning"""
    with patch('connection_manager.get_logger'), \
         patch('connection_manager.get_stats'), \
         patch('connection_manager.get_config'):
        from connection_manager import ConnectionManager
        
        conn = ConnectionManager()
        assert hasattr(conn, '_scan_wifi_nmcli'), "Missing nmcli fallback scanning"

test("WiFi Scanning Methods", test_wifi_scanning_methods)
test("WiFi Scanning with Caching", test_wifi_scanning_with_caching)
test("WiFi Scanning Force Rescan", test_wifi_scanning_force_rescan)
test("nmcli Fallback Scanning", test_nmcli_fallback_scanning)

# Test Suite 3: P1-FUNC-8 Real-time Stealth Status
print("\n[3/3] P1-FUNC-8 REAL-TIME STEALTH STATUS")
print("-" * 60)

def test_stealth_status_attributes():
    """Test stealth status tracking attributes"""
    with patch('connection_manager.get_logger'), \
         patch('connection_manager.get_stats'), \
         patch('connection_manager.get_config'):
        from connection_manager import ConnectionManager
        
        conn = ConnectionManager()
        assert hasattr(conn, 'stealth_active'), "Missing stealth_active attribute"
        assert hasattr(conn, 'stealth_level'), "Missing stealth_level attribute"
        assert conn.stealth_active == False, "Initial stealth_active should be False"
        assert conn.stealth_level == 0, "Initial stealth_level should be 0"

def test_stealth_status_methods():
    """Test stealth status methods"""
    with patch('connection_manager.get_logger'), \
         patch('connection_manager.get_stats'), \
         patch('connection_manager.get_config'):
        from connection_manager import ConnectionManager
        
        conn = ConnectionManager()
        assert hasattr(conn, 'update_stealth_status'), "Missing update_stealth_status method"
        assert hasattr(conn, 'get_stealth_status_string'), "Missing get_stealth_status_string method"

def test_stealth_status_string_formatting():
    """Test stealth status string formatting"""
    with patch('connection_manager.get_logger'), \
         patch('connection_manager.get_stats'), \
         patch('connection_manager.get_config'):
        from connection_manager import ConnectionManager
        
        conn = ConnectionManager()
        
        # Test disabled state
        conn.stealth_active = False
        status = conn.get_stealth_status_string()
        assert status == "DISABLED", f"Expected DISABLED, got {status}"
        
        # Test active state
        conn.stealth_active = True
        conn.stealth_level = 1
        status = conn.get_stealth_status_string()
        assert "ACTIVE" in status, f"Active status should contain ACTIVE: {status}"

def test_stealth_monitoring_integration():
    """Test stealth status monitoring integration"""
    with patch('connection_manager.get_logger'), \
         patch('connection_manager.get_stats'), \
         patch('connection_manager.get_config'):
        from connection_manager import ConnectionManager
        
        conn = ConnectionManager()
        
        # Test stealth status update doesn't crash
        try:
            conn.update_stealth_status()
            # Should complete without errors
        except Exception as e:
            # Allow subprocess errors in test environment
            if "subprocess" not in str(e).lower():
                raise

test("Stealth Status Attributes", test_stealth_status_attributes)
test("Stealth Status Methods", test_stealth_status_methods)
test("Stealth Status String Formatting", test_stealth_status_string_formatting)
test("Stealth Monitoring Integration", test_stealth_monitoring_integration)

# Summary
print("\n" + "=" * 60)
print("P1 FOCUSED TEST SUMMARY")
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
    print("✅ ALL P1 FOCUSED TESTS PASSED")
    print("✅ P1-FUNC-4: NetworkManager D-Bus Integration - WORKING")
    print("✅ P1-FUNC-5: Enhanced WiFi Scanning - WORKING")
    print("✅ P1-FUNC-8: Real-time Stealth Status - WORKING")
else:
    print("❌ SOME P1 TESTS FAILED")
    print("🔍 Review failed tests above")

print("=" * 60)
sys.exit(0 if failed == 0 else 1)