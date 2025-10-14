#!/usr/bin/env python3
"""
P2 UX Frontend Integration Test
Tests the integration of P2 UX components in the GTK desktop application
"""

import os
import sys
import traceback

# Add src to path
sys.path.insert(0, "/app/src")

print("=" * 70)
print("P2 UX FRONTEND INTEGRATION TEST")
print("=" * 70)
print()

def test_component_imports():
    """Test that all P2 UX components can be imported"""
    print("[1/6] Testing P2 UX component imports...")
    
    try:
        # Test dialog imports
        from dialogs.settings_dialog import SettingsDialog
        print("  ✓ SettingsDialog imported")
        
        from dialogs.first_run_wizard import FirstRunWizard
        print("  ✓ FirstRunWizard imported")
        
        from dialogs.error_recovery_dialog import ErrorRecoveryDialog
        print("  ✓ ErrorRecoveryDialog imported")
        
        # Test widget imports
        from widgets.data_dashboard import DataUsageDashboard
        print("  ✓ DataUsageDashboard imported")
        
        print("✓ All P2 UX components imported successfully")
        return True
        
    except Exception as e:
        print(f"✗ Component import failed: {e}")
        traceback.print_exc()
        return False

def test_main_gui_integration():
    """Test that main GUI integrates P2 UX components"""
    print("\n[2/6] Testing main GUI P2 UX integration...")
    
    try:
        # Read the main GUI file to check for integration
        with open("/app/src/pdanet_gui_v2.py", "r") as f:
            gui_content = f.read()
        
        # Check for required imports
        required_imports = [
            "from dialogs.settings_dialog import SettingsDialog",
            "from dialogs.first_run_wizard import FirstRunWizard", 
            "from dialogs.error_recovery_dialog import ErrorRecoveryDialog",
            "from widgets.data_dashboard import DataUsageDashboard"
        ]
        
        missing_imports = []
        for import_line in required_imports:
            if import_line not in gui_content:
                missing_imports.append(import_line)
        
        if missing_imports:
            print(f"✗ Missing imports: {missing_imports}")
            return False
        
        print("  ✓ All required P2 UX imports found in main GUI")
        
        # Check for integration methods
        integration_methods = [
            "build_enhanced_metrics_panel",
            "check_first_run", 
            "on_error_recovery_needed",
            "show_data_dashboard_window"
        ]
        
        missing_methods = []
        for method in integration_methods:
            if f"def {method}" not in gui_content:
                missing_methods.append(method)
        
        if missing_methods:
            print(f"✗ Missing integration methods: {missing_methods}")
            return False
            
        print("  ✓ All integration methods found in main GUI")
        
        # Check for error recovery callback registration
        if "register_error_recovery_callback" not in gui_content:
            print("✗ Error recovery callback registration not found")
            return False
            
        print("  ✓ Error recovery callback registration found")
        
        print("✓ Main GUI P2 UX integration verified")
        return True
        
    except Exception as e:
        print(f"✗ Main GUI integration test failed: {e}")
        traceback.print_exc()
        return False

def test_settings_dialog_structure():
    """Test Settings Dialog structure and functionality"""
    print("\n[3/6] Testing Settings Dialog structure...")
    
    try:
        # Read settings dialog file
        with open("/app/src/dialogs/settings_dialog.py", "r") as f:
            settings_content = f.read()
        
        # Check for required tabs
        required_tabs = [
            "_create_general_tab",
            "_create_network_tab", 
            "_create_stealth_tab",
            "_create_advanced_tab",
            "_create_profiles_tab"
        ]
        
        missing_tabs = []
        for tab in required_tabs:
            if f"def {tab}" not in settings_content:
                missing_tabs.append(tab)
        
        if missing_tabs:
            print(f"✗ Missing settings tabs: {missing_tabs}")
            return False
            
        print("  ✓ All required settings tabs found")
        
        # Check for settings persistence methods
        persistence_methods = ["_save_settings", "_load_settings", "_capture_current_settings"]
        
        missing_persistence = []
        for method in persistence_methods:
            if f"def {method}" not in settings_content:
                missing_persistence.append(method)
        
        if missing_persistence:
            print(f"✗ Missing persistence methods: {missing_persistence}")
            return False
            
        print("  ✓ Settings persistence methods found")
        
        print("✓ Settings Dialog structure verified")
        return True
        
    except Exception as e:
        print(f"✗ Settings Dialog test failed: {e}")
        traceback.print_exc()
        return False

def test_first_run_wizard_structure():
    """Test First-Run Wizard structure"""
    print("\n[4/6] Testing First-Run Wizard structure...")
    
    try:
        # Read first run wizard file
        with open("/app/src/dialogs/first_run_wizard.py", "r") as f:
            wizard_content = f.read()
        
        # Check for required pages
        required_pages = [
            "_add_welcome_page",
            "_add_requirements_page",
            "_add_permissions_page", 
            "_add_android_setup_page",
            "_add_test_connection_page",
            "_add_profile_page",
            "_add_completion_page"
        ]
        
        missing_pages = []
        for page in required_pages:
            if f"def {page}" not in wizard_content:
                missing_pages.append(page)
        
        if missing_pages:
            print(f"✗ Missing wizard pages: {missing_pages}")
            return False
            
        print("  ✓ All required wizard pages found")
        
        # Check for requirement checks
        requirement_checks = [
            "_check_python",
            "_check_gtk",
            "_check_networkmanager",
            "_check_policykit", 
            "_check_redsocks",
            "_check_iptables"
        ]
        
        missing_checks = []
        for check in requirement_checks:
            if f"def {check}" not in wizard_content:
                missing_checks.append(check)
        
        if missing_checks:
            print(f"✗ Missing requirement checks: {missing_checks}")
            return False
            
        print("  ✓ All requirement checks found")
        
        print("✓ First-Run Wizard structure verified")
        return True
        
    except Exception as e:
        print(f"✗ First-Run Wizard test failed: {e}")
        traceback.print_exc()
        return False

def test_error_recovery_dialog_structure():
    """Test Error Recovery Dialog structure"""
    print("\n[5/6] Testing Error Recovery Dialog structure...")
    
    try:
        # Read error recovery dialog file
        with open("/app/src/dialogs/error_recovery_dialog.py", "r") as f:
            dialog_content = f.read()
        
        # Check for required methods
        required_methods = [
            "_build_ui",
            "_create_solution_page",
            "_on_auto_fix",
            "_on_copy_details"
        ]
        
        missing_methods = []
        for method in required_methods:
            if f"def {method}" not in dialog_content:
                missing_methods.append(method)
        
        if missing_methods:
            print(f"✗ Missing dialog methods: {missing_methods}")
            return False
            
        print("  ✓ All required dialog methods found")
        
        # Check for error database integration
        if "from error_database import get_error_info" not in dialog_content:
            print("✗ Error database integration not found")
            return False
            
        print("  ✓ Error database integration found")
        
        # Check for convenience function
        if "def show_error_dialog" not in dialog_content:
            print("✗ Convenience function not found")
            return False
            
        print("  ✓ Convenience function found")
        
        print("✓ Error Recovery Dialog structure verified")
        return True
        
    except Exception as e:
        print(f"✗ Error Recovery Dialog test failed: {e}")
        traceback.print_exc()
        return False

def test_data_dashboard_structure():
    """Test Data Usage Dashboard structure"""
    print("\n[6/6] Testing Data Usage Dashboard structure...")
    
    try:
        # Read data dashboard file
        with open("/app/src/widgets/data_dashboard.py", "r") as f:
            dashboard_content = f.read()
        
        # Check for required methods
        required_methods = [
            "_build_ui",
            "_update_display",
            "_format_bytes",
            "_load_usage_data",
            "_save_usage_data"
        ]
        
        missing_methods = []
        for method in required_methods:
            if f"def {method}" not in dashboard_content:
                missing_methods.append(method)
        
        if missing_methods:
            print(f"✗ Missing dashboard methods: {missing_methods}")
            return False
            
        print("  ✓ All required dashboard methods found")
        
        # Check for circular progress widget import
        if "from widgets.circular_progress import CircularProgress" not in dashboard_content:
            print("✗ Circular progress widget import not found")
            return False
            
        print("  ✓ Circular progress widget import found")
        
        # Check for data persistence
        if "data_usage.json" not in dashboard_content:
            print("✗ Data persistence configuration not found")
            return False
            
        print("  ✓ Data persistence configuration found")
        
        print("✓ Data Usage Dashboard structure verified")
        return True
        
    except Exception as e:
        print(f"✗ Data Usage Dashboard test failed: {e}")
        traceback.print_exc()
        return False

def main():
    """Run all P2 UX integration tests"""
    tests = [
        test_component_imports,
        test_main_gui_integration,
        test_settings_dialog_structure,
        test_first_run_wizard_structure,
        test_error_recovery_dialog_structure,
        test_data_dashboard_structure
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print()
    print("=" * 70)
    print(f"P2 UX INTEGRATION TEST RESULTS: {passed}/{total} PASSED")
    print("=" * 70)
    print()
    
    if passed == total:
        print("✓ ALL P2 UX INTEGRATION TESTS PASSED")
        print()
        print("Summary of verified P2 UX components:")
        print("  • Settings Dialog with tabbed interface")
        print("  • First-Run Wizard with 7 setup pages")
        print("  • Error Recovery Dialog with structured solutions")
        print("  • Data Usage Dashboard with visual meter")
        print("  • Enhanced metrics panel with tabs")
        print("  • Error recovery callback integration")
        print("  • Main GUI integration of all components")
        print()
        return True
    else:
        print(f"✗ {total - passed} P2 UX INTEGRATION TESTS FAILED")
        print()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)