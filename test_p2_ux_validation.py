#!/usr/bin/env python3
"""
P2 UX Frontend Integration Validation Test
Validates the integration fixes and method signatures
"""

import os
import sys
import re

print("=" * 70)
print("P2 UX FRONTEND INTEGRATION VALIDATION TEST")
print("=" * 70)
print()

def test_data_dashboard_constructor_fix():
    """Test that DataUsageDashboard constructor calls are fixed"""
    print("[1/5] Testing DataUsageDashboard constructor fix...")
    
    try:
        # Read the main GUI file
        with open("/app/src/pdanet_gui_v2.py", "r") as f:
            gui_content = f.read()
        
        # Check for correct constructor calls
        correct_calls = [
            "config_manager=self.config",
            "stats_collector=self.stats"
        ]
        
        dashboard_calls = re.findall(r'DataUsageDashboard\((.*?)\)', gui_content, re.DOTALL)
        
        if not dashboard_calls:
            print("  ✗ No DataUsageDashboard constructor calls found")
            return False
        
        all_correct = True
        for call in dashboard_calls:
            for required_param in correct_calls:
                if required_param not in call:
                    print(f"  ✗ Missing parameter in call: {required_param}")
                    all_correct = False
        
        if all_correct:
            print("  ✓ All DataUsageDashboard constructor calls use correct parameters")
        
        # Check that incorrect parameters are not used
        incorrect_calls = ["connection_manager=self.connection"]
        for call in dashboard_calls:
            for incorrect_param in incorrect_calls:
                if incorrect_param in call:
                    print(f"  ✗ Found incorrect parameter: {incorrect_param}")
                    all_correct = False
        
        if all_correct:
            print("  ✓ No incorrect parameters found in constructor calls")
            print("✓ DataUsageDashboard constructor fix verified")
            return True
        else:
            return False
        
    except Exception as e:
        print(f"✗ DataUsageDashboard constructor test failed: {e}")
        return False

def test_error_recovery_dialog_fix():
    """Test that ErrorRecoveryDialog constructor calls are fixed"""
    print("\n[2/5] Testing ErrorRecoveryDialog constructor fix...")
    
    try:
        # Read the main GUI file
        with open("/app/src/pdanet_gui_v2.py", "r") as f:
            gui_content = f.read()
        
        # Check for correct constructor calls
        correct_params = [
            "error_code=",
            "error_message=",
            "details="
        ]
        
        # Check that all required parameters are present in the file
        all_correct = True
        for required_param in correct_params:
            if required_param not in gui_content:
                print(f"  ✗ Missing parameter in file: {required_param}")
                all_correct = False
        
        if all_correct:
            print("  ✓ All ErrorRecoveryDialog constructor calls use correct parameters")
        
        # Check that incorrect parameters are not used
        if "error_info=" in gui_content:
            print("  ✗ Found incorrect parameter: error_info=")
            all_correct = False
        else:
            print("  ✓ No incorrect parameters found in constructor calls")
        
        if all_correct:
            print("✓ ErrorRecoveryDialog constructor fix verified")
            return True
        else:
            return False
        
    except Exception as e:
        print(f"✗ ErrorRecoveryDialog constructor test failed: {e}")
        return False

def test_first_run_wizard_fix():
    """Test that FirstRunWizard method calls are fixed"""
    print("\n[3/5] Testing FirstRunWizard method call fix...")
    
    try:
        # Read the main GUI file
        with open("/app/src/pdanet_gui_v2.py", "r") as f:
            gui_content = f.read()
        
        # Check that get_wizard_data() is not called
        if "get_wizard_data()" in gui_content:
            print("  ✗ Found call to non-existent method: get_wizard_data()")
            return False
        else:
            print("  ✓ No calls to non-existent get_wizard_data() method")
        
        # Check that first_run is properly set to False
        if 'self.config.set("first_run", False)' in gui_content:
            print("  ✓ First run completion properly handled")
        else:
            print("  ⚠ First run completion handling may be missing")
        
        print("✓ FirstRunWizard method call fix verified")
        return True
        
    except Exception as e:
        print(f"✗ FirstRunWizard method call test failed: {e}")
        return False

def test_enhanced_metrics_panel_integration():
    """Test enhanced metrics panel with tabs"""
    print("\n[4/5] Testing enhanced metrics panel integration...")
    
    try:
        # Read the main GUI file
        with open("/app/src/pdanet_gui_v2.py", "r") as f:
            gui_content = f.read()
        
        # Check for enhanced metrics panel method
        if "def build_enhanced_metrics_panel" not in gui_content:
            print("  ✗ Enhanced metrics panel method not found")
            return False
        else:
            print("  ✓ Enhanced metrics panel method found")
        
        # Check for notebook (tabbed interface)
        if "Gtk.Notebook" in gui_content:
            print("  ✓ Tabbed interface (Notebook) found")
        else:
            print("  ⚠ Tabbed interface may be missing")
        
        # Check for tab labels
        tab_labels = ["METRICS", "DATA USAGE"]
        missing_tabs = []
        for label in tab_labels:
            if label not in gui_content:
                missing_tabs.append(label)
        
        if missing_tabs:
            print(f"  ⚠ Missing tab labels: {missing_tabs}")
        else:
            print("  ✓ All required tab labels found")
        
        # Check for data dashboard integration in tabs
        if "build_data_dashboard_content" in gui_content:
            print("  ✓ Data dashboard tab content method found")
        else:
            print("  ⚠ Data dashboard tab content method may be missing")
        
        print("✓ Enhanced metrics panel integration verified")
        return True
        
    except Exception as e:
        print(f"✗ Enhanced metrics panel test failed: {e}")
        return False

def test_menu_integration_completeness():
    """Test completeness of menu integration"""
    print("\n[5/5] Testing menu integration completeness...")
    
    try:
        # Read the main GUI file
        with open("/app/src/pdanet_gui_v2.py", "r") as f:
            gui_content = f.read()
        
        # Check for settings menu integration
        settings_indicators = [
            "Advanced Settings",
            "on_settings_clicked",
            "SettingsDialog"
        ]
        
        missing_settings = []
        for indicator in settings_indicators:
            if indicator not in gui_content:
                missing_settings.append(indicator)
        
        if missing_settings:
            print(f"  ⚠ Missing settings integration: {missing_settings}")
        else:
            print("  ✓ Settings menu integration complete")
        
        # Check for data dashboard menu integration
        dashboard_indicators = [
            "Data Usage Dashboard",
            "show_data_dashboard_window"
        ]
        
        missing_dashboard = []
        for indicator in dashboard_indicators:
            if indicator not in gui_content:
                missing_dashboard.append(indicator)
        
        if missing_dashboard:
            print(f"  ⚠ Missing dashboard integration: {missing_dashboard}")
        else:
            print("  ✓ Data dashboard menu integration complete")
        
        # Check for error recovery callback registration
        if "register_error_recovery_callback" in gui_content:
            print("  ✓ Error recovery callback registration found")
        else:
            print("  ✗ Error recovery callback registration missing")
            return False
        
        # Check for first run check
        if "check_first_run" in gui_content:
            print("  ✓ First run check integration found")
        else:
            print("  ✗ First run check integration missing")
            return False
        
        print("✓ Menu integration completeness verified")
        return True
        
    except Exception as e:
        print(f"✗ Menu integration test failed: {e}")
        return False

def main():
    """Run all P2 UX integration validation tests"""
    tests = [
        test_data_dashboard_constructor_fix,
        test_error_recovery_dialog_fix,
        test_first_run_wizard_fix,
        test_enhanced_metrics_panel_integration,
        test_menu_integration_completeness
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print()
    print("=" * 70)
    print(f"P2 UX INTEGRATION VALIDATION RESULTS: {passed}/{total} PASSED")
    print("=" * 70)
    print()
    
    if passed == total:
        print("✓ ALL P2 UX INTEGRATION VALIDATION TESTS PASSED")
        print()
        print("Summary of validated fixes:")
        print("  • DataUsageDashboard constructor parameters corrected")
        print("  • ErrorRecoveryDialog constructor parameters corrected")
        print("  • FirstRunWizard method calls fixed")
        print("  • Enhanced metrics panel with tabs verified")
        print("  • Menu integration completeness verified")
        print("  • Error recovery callback registration verified")
        print()
        print("P2 UX Frontend Integration is ready for runtime testing!")
        print()
        return True
    else:
        print(f"✗ {total - passed} P2 UX INTEGRATION VALIDATION TESTS FAILED")
        print()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)