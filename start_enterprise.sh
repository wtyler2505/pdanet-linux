#!/bin/bash
# PdaNet Linux 2.0 Enterprise Startup Script
# Optimized for production deployment

set -e

echo "🚀 PdaNet Linux 2.0 Enterprise Starting..."

# Set optimal environment
export PYTHONOPTIMIZE=1
export PYTHONDONTWRITEBYTECODE=1

# Pre-load critical modules for faster startup  
cd /app/src

# Verify critical components
echo "✓ Verifying core components..."
python3 -c "from connection_manager import get_connection_manager; print('Connection Manager: OK')"
python3 -c "from config_manager import get_config; print('Config Manager: OK')"
python3 -c "from error_database import get_error_info; print('Error Database: OK')"

echo "✓ Verifying P2 UX components..."
python3 -c "from dialogs.settings_dialog import SettingsDialog; print('Settings Dialog: OK')"
python3 -c "from dialogs.first_run_wizard import FirstRunWizard; print('First-Run Wizard: OK')"

echo "✓ Verifying P4 advanced features..."  
python3 -c "from iphone_hotspot_bypass import get_iphone_hotspot_bypass; print('iPhone Bypass: OK')"

echo "🎯 All components verified - ready for launch"
echo "🏆 PdaNet Linux 2.0 Enterprise: READY"

# Launch main application
python3 pdanet_gui_v2.py "$@"
