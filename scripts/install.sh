
#!/bin/bash

# AI-Enhanced PDanet-Linux Installation Script

echo "📦 Installing AI-Enhanced PDanet-Linux..."

# Update system packages
echo "🔄 Updating system packages..."
apt-get update

# Install system dependencies
echo "📥 Installing system dependencies..."
apt-get install -y     python3     python3-pip     python3-venv     iproute2     iptables     tcpdump     net-tools     iputils-ping     curl     wget     git

# Create virtual environment
echo "🐍 Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Create directories
echo "📁 Creating directories..."
mkdir -p logs data/models ml_models config

# Set permissions
echo "🔒 Setting permissions..."
chmod +x scripts/*.sh

echo "✅ Installation complete!"
echo "📖 Next steps:"
echo "   1. Edit config/config.yaml with your settings"
echo "   2. Run: sudo ./scripts/start.sh"
echo "   3. Access the API at http://localhost:8000"
