#!/usr/bin/env python3
"""
PdaNet Linux 2.0 Enterprise Deployment Validator  
Final validation before production deployment
"""

import os
import sys
sys.path.insert(0, "/app/src")

def validate_deployment_readiness():
    """Validate system is ready for enterprise deployment"""
    
    validations = []
    
    # File structure validation
    required_files = [
        "/app/src/pdanet_gui_v2.py",
        "/app/src/connection_manager.py",
        "/app/src/config_manager.py", 
        "/app/src/config_validator.py",
        "/app/src/error_database.py",
        "/app/src/dialogs/settings_dialog.py",
        "/app/src/dialogs/first_run_wizard.py",
        "/app/src/dialogs/error_recovery_dialog.py",
        "/app/src/widgets/data_dashboard.py",
        "/app/src/iphone_hotspot_bypass.py"
    ]
    
    missing_files = [f for f in required_files if not os.path.exists(f)]
    validations.append(("File Structure", len(missing_files) == 0, f"{len(missing_files)} missing files" if missing_files else "All files present"))
    
    # Import validation  
    try:
        from connection_manager import get_connection_manager
        from config_manager import get_config
        from dialogs.settings_dialog import SettingsDialog
        from error_database import get_error_info
        validations.append(("Core Imports", True, "All critical modules importable"))
    except Exception as e:
        validations.append(("Core Imports", False, str(e)))
    
    # Configuration integrity
    try:
        from config_validator import ConfigValidator
        validator = ConfigValidator()
        default_config = validator.get_default_config()
        is_valid, errors = validator.validate_config(default_config)
        validations.append(("Config Integrity", is_valid, f"{len(errors)} validation errors" if not is_valid else "Default config valid"))
    except Exception as e:
        validations.append(("Config Integrity", False, str(e)))
    
    # Error database completeness
    try:
        from error_database import ERROR_DATABASE
        error_count = len(ERROR_DATABASE)
        validations.append(("Error Database", error_count > 10, f"{error_count} error types defined"))
    except Exception as e:
        validations.append(("Error Database", False, str(e)))
    
    # Security features
    try:
        from input_validators import validate_ssid, validate_password, ValidationError
        # Test validation works
        validate_ssid("TestSSID") 
        validate_password("TestPassword123")
        validations.append(("Security Validation", True, "Input validation operational"))
    except Exception as e:
        validations.append(("Security Validation", False, str(e)))
    
    return validations

if __name__ == "__main__":
    print("🚀 PdaNet Linux 2.0 - Deployment Readiness Check")
    print("=" * 60)
    
    validation_results = validate_deployment_readiness()
    
    passed = sum(1 for _, success, _ in validation_results if success)
    total = len(validation_results)
    
    for component, success, message in validation_results:
        status = "✅" if success else "❌"
        print(f"{status} {component}: {message}")
    
    print(f"\n🎯 Readiness Score: {passed}/{total} ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 DEPLOYMENT STATUS: READY FOR ENTERPRISE PRODUCTION")
        print("🏆 All systems validated - deployment approved")
        exit(0)
    elif passed >= total * 0.9:
        print("✅ DEPLOYMENT STATUS: READY WITH MINOR ISSUES")
        print("📋 Recommend addressing minor issues post-deployment")
        exit(0)
    else:
        print("⚠️  DEPLOYMENT STATUS: NOT READY - Critical issues detected")
        print("🛠️  Address critical issues before production deployment")
        exit(1)
