#!/bin/bash
#
# uninstall.sh - Uninstall PdaNet Linux Client
# Removes all configurations and restores system to original state
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
echo "║   PdaNet Linux Client - Uninstaller   ║"
echo "╚════════════════════════════════════════╝"
echo -e "${NC}"

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   echo -e "${RED}Error: This script must be run as root (use sudo)${NC}"
   exit 1
fi

echo ""
read -p "This will remove PdaNet Linux client. Continue? (y/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Uninstall cancelled."
    exit 0
fi

echo ""
echo -e "${YELLOW}[1/6]${NC} Disconnecting active PdaNet connection..."

# Stop any active connection
if [ -f "$PROJECT_DIR/pdanet-disconnect" ]; then
    bash "$PROJECT_DIR/pdanet-disconnect" 2>/dev/null || true
fi

# Disable stealth mode if active
if [ -f "$PROJECT_DIR/scripts/stealth-mode.sh" ]; then
    bash "$PROJECT_DIR/scripts/stealth-mode.sh" disable 2>/dev/null || true
fi

echo -e "${GREEN}✓${NC} Connection terminated"

echo -e "${YELLOW}[2/6]${NC} Stopping and disabling services..."

# Stop and disable redsocks
systemctl stop redsocks 2>/dev/null || true
systemctl disable redsocks 2>/dev/null || true

echo -e "${GREEN}✓${NC} Services stopped"

echo -e "${YELLOW}[3/6]${NC} Removing configuration files..."

# Restore original redsocks config if backup exists
if ls /etc/redsocks.conf.backup.* 1> /dev/null 2>&1; then
    LATEST_BACKUP=$(ls -t /etc/redsocks.conf.backup.* | head -1)
    mv "$LATEST_BACKUP" /etc/redsocks.conf
    echo "  Restored original redsocks.conf from backup"
else
    rm -f /etc/redsocks.conf
    echo "  Removed redsocks.conf"
fi

# Remove sudoers file
rm -f /etc/sudoers.d/pdanet-linux

echo -e "${GREEN}✓${NC} Configuration files removed"

echo -e "${YELLOW}[4/6]${NC} Removing convenience commands..."

# Remove symlinks
rm -f /usr/local/bin/pdanet-connect
rm -f /usr/local/bin/pdanet-disconnect
rm -f /usr/local/bin/pdanet-stealth

echo -e "${GREEN}✓${NC} Commands removed"

echo -e "${YELLOW}[5/6]${NC} Cleaning up iptables rules..."

# Make sure all our iptables rules are gone
bash "$PROJECT_DIR/config/iptables-rules.sh" stop 2>/dev/null || true

echo -e "${GREEN}✓${NC} Iptables rules cleaned"

echo -e "${YELLOW}[6/6]${NC} Removing dependencies (optional)..."

echo ""
echo "The following packages were installed:"
echo "  - redsocks"
echo "  - iptables-persistent"
echo ""
read -p "Remove these packages? (y/N) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    apt-get remove -y redsocks iptables-persistent
    apt-get autoremove -y
    echo -e "${GREEN}✓${NC} Packages removed"
else
    echo "  Keeping packages installed"
fi

echo ""
echo -e "${GREEN}╔════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║    Uninstallation Complete! ✓          ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════╝${NC}"
echo ""
echo "The PdaNet Linux client has been removed."
echo ""
echo "To completely remove the project directory, run:"
echo "  ${YELLOW}rm -rf $PROJECT_DIR${NC}"
echo ""

exit 0
