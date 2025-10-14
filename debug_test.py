#!/usr/bin/env python3
"""
Debug specific failing issues
"""

import sys
sys.path.insert(0, "/app/src")

print("=== DEBUGGING SPECIFIC ISSUES ===")

# Issue 1: Default preferences
print("\n1. Testing default preferences:")
try:
    from user_experience import UserExperienceManager
    ux = UserExperienceManager()
    theme = ux.get_preference("theme")
    print(f"Current theme: {theme}")
    print(f"Expected: cyberpunk_dark")
    print(f"Preferences file exists: {ux.preferences_file.exists()}")
    if ux.preferences_file.exists():
        print(f"Preferences file path: {ux.preferences_file}")
except Exception as e:
    print(f"Error: {e}")

# Issue 2: Connection manager status
print("\n2. Testing connection manager status:")
try:
    from unittest.mock import Mock, patch
    
    with patch('connection_manager.get_logger'), \
         patch('connection_manager.get_stats'), \
         patch('connection_manager.get_config'), \
         patch('connection_manager.get_resource_manager'), \
         patch('connection_manager.get_reliability_manager'), \
         patch('connection_manager.get_ux_manager'), \
         patch('connection_manager.get_advanced_network_monitor'), \
         patch('connection_manager.get_intelligent_bandwidth_manager'):
        
        from connection_manager import ConnectionManager
        conn = ConnectionManager()
        
        # Test get_connection_status
        basic_status = conn.get_connection_status()
        print(f"Basic status type: {type(basic_status)}")
        print(f"Basic status: {basic_status}")
        
        # Test get_comprehensive_status
        comp_status = conn.get_comprehensive_status()
        print(f"Comprehensive status type: {type(comp_status)}")
        print(f"Comprehensive status: {comp_status}")
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

print("\n=== DEBUG COMPLETE ===")