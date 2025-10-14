
#!/bin/bash

# AI-Enhanced PDanet-Linux Startup Script

echo "🚀 Starting AI-Enhanced PDanet-Linux..."

# Check if running as root (required for network operations)
if [ "$EUID" -ne 0 ]; then
  echo "❌ This script must be run as root for network operations"
  echo "   Please run: sudo $0"
  exit 1
fi

# Check dependencies
echo "🔍 Checking system dependencies..."

command -v python3 >/dev/null 2>&1 || { echo "❌ Python 3 is required but not installed."; exit 1; }
command -v pip3 >/dev/null 2>&1 || { echo "❌ pip3 is required but not installed."; exit 1; }
command -v ip >/dev/null 2>&1 || { echo "❌ iproute2 (ip command) is required but not installed."; exit 1; }
command -v iptables >/dev/null 2>&1 || { echo "❌ iptables is required but not installed."; exit 1; }

echo "✅ All dependencies found"

# Install Python dependencies if needed
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
else
    echo "📦 Using existing virtual environment..."
    source venv/bin/activate
fi

# Create necessary directories
mkdir -p logs data/models ml_models config

# Set appropriate permissions
chmod +x scripts/*.sh

# Start the application
echo "🎯 Starting AI-Enhanced PDanet-Linux API..."
exec python -m uvicorn pdanet_ai.api.fastapi_server:app --host 0.0.0.0 --port 8000 --reload
