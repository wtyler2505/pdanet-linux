#!/bin/bash
#
# install.sh - Install PdaNet Linux Client
# Installs dependencies and configures system for PdaNet USB tethering
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;36m'
NC='\033[0m' # No Color

PROJECT_DIR="/home/wtyler/pdanet-linux"

echo -e "${BLUE}"
echo "╔════════════════════════════════════════╗"
echo "║   PdaNet Linux Client - Installer     ║"
echo "║   USB Tethering for Linux Mint 22.2   ║"
echo "╚════════════════════════════════════════╝"
echo -e "${NC}"

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   echo -e "${RED}Error: This script must be run as root (use sudo)${NC}"
   exit 1
fi

# Detect distribution
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$ID
    VER=$VERSION_ID
    echo -e "Detected OS: ${GREEN}$PRETTY_NAME${NC}"
else
    echo -e "${RED}Error: Cannot detect OS${NC}"
    exit 1
fi

# Verify Linux Mint or Ubuntu
if [[ "$OS" != "linuxmint" ]] && [[ "$OS" != "ubuntu" ]]; then
    echo -e "${YELLOW}Warning: This installer is designed for Linux Mint/Ubuntu${NC}"
    echo -e "${YELLOW}Your OS: $OS - Installation may not work correctly${NC}"
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo ""
echo -e "${YELLOW}[1/7]${NC} Updating package lists..."
apt-get update -qq

echo -e "${YELLOW}[2/7]${NC} Installing dependencies..."

# Install required packages
PACKAGES=(
    "redsocks"
    "iptables"
    "iptables-persistent"
    "curl"
    "net-tools"
    "python3-gi"
    "python3-gi-cairo"
    "gir1.2-gtk-3.0"
    "gir1.2-appindicator3-0.1"
    "python3-pil"
)

for pkg in "${PACKAGES[@]}"; do
    if ! dpkg -l | grep -q "^ii  $pkg "; then
        echo "  Installing $pkg..."
        DEBIAN_FRONTEND=noninteractive apt-get install -y -qq "$pkg"
    else
        echo "  ✓ $pkg already installed"
    fi
done

echo -e "${GREEN}✓${NC} All dependencies installed"

echo -e "${YELLOW}[3/7]${NC} Configuring redsocks..."

# Backup existing redsocks config if it exists
if [ -f /etc/redsocks.conf ]; then
    cp /etc/redsocks.conf /etc/redsocks.conf.backup.$(date +%Y%m%d-%H%M%S)
    echo "  Existing config backed up"
fi

# Install our redsocks config
cp "$PROJECT_DIR/config/redsocks.conf" /etc/redsocks.conf
chown root:root /etc/redsocks.conf
chmod 644 /etc/redsocks.conf

echo -e "${GREEN}✓${NC} Redsocks configured"

echo -e "${YELLOW}[4/7]${NC} Configuring systemd service..."

# Make sure redsocks service is enabled but not started (we'll start it when connecting)
systemctl enable redsocks
systemctl stop redsocks 2>/dev/null || true

echo -e "${GREEN}✓${NC} Service configured"

echo -e "${YELLOW}[5/7]${NC} Setting up user permissions..."

# Allow current user to run connect/disconnect scripts without password
REAL_USER="${SUDO_USER:-$USER}"
if [ -z "$REAL_USER" ]; then
    REAL_USER="wtyler"  # Fallback to current user
fi
SUDOERS_FILE="/etc/sudoers.d/pdanet-linux"

cat > "$SUDOERS_FILE" << EOF
# Allow user to run pdanet scripts without password
$REAL_USER ALL=(ALL) NOPASSWD: $PROJECT_DIR/pdanet-connect
$REAL_USER ALL=(ALL) NOPASSWD: $PROJECT_DIR/pdanet-disconnect
$REAL_USER ALL=(ALL) NOPASSWD: $PROJECT_DIR/scripts/stealth-mode.sh
$REAL_USER ALL=(ALL) NOPASSWD: /usr/bin/systemctl is-active redsocks
$REAL_USER ALL=(ALL) NOPASSWD: /usr/sbin/iptables -t mangle -L PDANET_STEALTH
EOF

chmod 440 "$SUDOERS_FILE"
echo -e "${GREEN}✓${NC} Sudo permissions configured for $REAL_USER"

echo -e "${YELLOW}[6/7]${NC} Creating convenience commands..."

# Create symlinks in /usr/local/bin for easy access
ln -sf "$PROJECT_DIR/pdanet-connect" /usr/local/bin/pdanet-connect
ln -sf "$PROJECT_DIR/pdanet-disconnect" /usr/local/bin/pdanet-disconnect
ln -sf "$PROJECT_DIR/pdanet-wifi-connect" /usr/local/bin/pdanet-wifi-connect
ln -sf "$PROJECT_DIR/pdanet-wifi-disconnect" /usr/local/bin/pdanet-wifi-disconnect
ln -sf "$PROJECT_DIR/pdanet-iphone-connect" /usr/local/bin/pdanet-iphone-connect
ln -sf "$PROJECT_DIR/pdanet-iphone-disconnect" /usr/local/bin/pdanet-iphone-disconnect
ln -sf "$PROJECT_DIR/scripts/stealth-mode.sh" /usr/local/bin/pdanet-stealth
ln -sf "$PROJECT_DIR/src/pdanet_gui_v2.py" /usr/local/bin/pdanet-gui-v2

# Make scripts executable
chmod +x "$PROJECT_DIR/src/pdanet_gui_v2.py"
chmod +x "$PROJECT_DIR/pdanet-wifi-connect"
chmod +x "$PROJECT_DIR/pdanet-wifi-disconnect"
chmod +x "$PROJECT_DIR/pdanet-iphone-connect"
chmod +x "$PROJECT_DIR/pdanet-iphone-disconnect"

echo -e "${GREEN}✓${NC} Commands installed to /usr/local/bin"

echo -e "${YELLOW}[7/7]${NC} Installing GUI desktop launcher..."

# Install desktop file
cp "$PROJECT_DIR/config/pdanet-linux.desktop" /usr/share/applications/pdanet-linux.desktop
chmod 644 /usr/share/applications/pdanet-linux.desktop

# Update desktop database
if command -v update-desktop-database &> /dev/null; then
    update-desktop-database /usr/share/applications 2>/dev/null || true
fi

echo -e "${GREEN}✓${NC} GUI installed to application menu"

echo ""
echo -e "${GREEN}╔════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║     Installation Complete! ✓           ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}Next steps:${NC}"
echo ""
echo "1. Connect your Android device via USB"
echo "2. Open PdaNet+ app on Android"
echo "3. Enable 'Activate USB Mode' in PdaNet+"
echo ""
echo -e "${BLUE}Launch the GUI:${NC}"
echo "   ${GREEN}pdanet-gui${NC}  (or search for 'PdaNet Linux' in your app menu)"
echo ""
echo -e "${BLUE}Or use CLI:${NC}"
echo "   ${GREEN}sudo pdanet-connect${NC}"
echo ""
echo -e "${BLUE}Optional - Enable stealth mode:${NC}"
echo "   ${GREEN}sudo pdanet-stealth enable${NC}"
echo "   (Hides tethering usage from carrier detection)"
echo ""
echo -e "${BLUE}To disconnect:${NC}"
echo "   ${GREEN}sudo pdanet-disconnect${NC}"
echo ""
echo -e "${YELLOW}Note:${NC} Make sure your Android device has PdaNet+ installed"
echo "Download from: https://pdanet.co/"
echo ""

exit 0
