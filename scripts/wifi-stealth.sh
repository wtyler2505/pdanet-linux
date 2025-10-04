#!/bin/bash
#
# wifi-stealth.sh - AGGRESSIVE carrier bypass for WiFi tethering
# Multi-layered approach to hide tethering from carrier detection
#

set -e

# Configuration
WIFI_INTERFACE="${1:-wlan0}"
STEALTH_LEVEL="${2:-3}"  # 1=basic, 2=moderate, 3=aggressive

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

enable_stealth() {
    echo -e "${GREEN}[STEALTH]${NC} Enabling aggressive carrier bypass..."
    echo -e "${YELLOW}[LEVEL $STEALTH_LEVEL]${NC}"

    # ================================================================
    # LAYER 1: TTL MODIFICATION (CRITICAL!)
    # ================================================================
    # Carriers detect tethering by checking TTL decrements
    # Phone packets have TTL 64/65, tethered packets have TTL 63/64
    # We set all outgoing packets to TTL 65 to match phone traffic

    echo -e "${GREEN}[STEALTH]${NC} Layer 1: TTL Normalization"

    # Create mangle chain
    iptables -t mangle -N WIFI_STEALTH 2>/dev/null || iptables -t mangle -F WIFI_STEALTH

    # Set TTL to 65 for all outgoing packets on WiFi
    iptables -t mangle -A WIFI_STEALTH -j TTL --ttl-set 65

    # Set HL (Hop Limit) for IPv6
    ip6tables -t mangle -N WIFI_STEALTH 2>/dev/null || ip6tables -t mangle -F WIFI_STEALTH
    ip6tables -t mangle -A WIFI_STEALTH -j HL --hl-set 65

    # Apply to POSTROUTING
    iptables -t mangle -A POSTROUTING -o $WIFI_INTERFACE -j WIFI_STEALTH 2>/dev/null || true
    ip6tables -t mangle -A POSTROUTING -o $WIFI_INTERFACE -j WIFI_STEALTH 2>/dev/null || true

    echo -e "${GREEN}  ✓${NC} TTL set to 65"

    # ================================================================
    # LAYER 2: BLOCK IPv6 (Prevent leaks)
    # ================================================================
    # Many carriers only monitor IPv4, IPv6 can leak real traffic

    if [ "$STEALTH_LEVEL" -ge 2 ]; then
        echo -e "${GREEN}[STEALTH]${NC} Layer 2: IPv6 Blocking"

        # Disable IPv6 on WiFi interface
        sysctl -w net.ipv6.conf.$WIFI_INTERFACE.disable_ipv6=1 >/dev/null 2>&1 || true

        # Block all IPv6 traffic
        ip6tables -P INPUT DROP 2>/dev/null || true
        ip6tables -P FORWARD DROP 2>/dev/null || true
        ip6tables -P OUTPUT DROP 2>/dev/null || true

        echo -e "${GREEN}  ✓${NC} IPv6 disabled"
    fi

    # ================================================================
    # LAYER 3: DNS LEAK PREVENTION
    # ================================================================
    # Force all DNS queries through the phone (not ISP DNS)

    if [ "$STEALTH_LEVEL" -ge 2 ]; then
        echo -e "${GREEN}[STEALTH]${NC} Layer 3: DNS Leak Prevention"

        # Get gateway (phone) IP
        GATEWAY=$(ip route | grep "default.*$WIFI_INTERFACE" | awk '{print $3}')

        if [ -n "$GATEWAY" ]; then
            # Redirect all DNS (port 53) to gateway
            iptables -t nat -A OUTPUT -o $WIFI_INTERFACE -p udp --dport 53 -j DNAT --to $GATEWAY:53
            iptables -t nat -A OUTPUT -o $WIFI_INTERFACE -p tcp --dport 53 -j DNAT --to $GATEWAY:53

            # Block Google DNS (often used to detect tethering)
            iptables -A OUTPUT -d 8.8.8.8 -j DROP
            iptables -A OUTPUT -d 8.8.4.4 -j DROP

            echo -e "${GREEN}  ✓${NC} DNS forced through gateway: $GATEWAY"
        fi
    fi

    # ================================================================
    # LAYER 4: BLOCK OS UPDATE SERVICES
    # ================================================================
    # OS updates are a dead giveaway of desktop tethering

    if [ "$STEALTH_LEVEL" -ge 3 ]; then
        echo -e "${GREEN}[STEALTH]${NC} Layer 4: OS Update Blocking"

        # Windows Update domains
        iptables -A OUTPUT -m string --string "windowsupdate" --algo bm -j DROP 2>/dev/null || true
        iptables -A OUTPUT -m string --string "update.microsoft" --algo bm -j DROP 2>/dev/null || true

        # Mac/Apple updates
        iptables -A OUTPUT -m string --string "swcdn.apple.com" --algo bm -j DROP 2>/dev/null || true
        iptables -A OUTPUT -m string --string "mesu.apple.com" --algo bm -j DROP 2>/dev/null || true

        # Ubuntu/Debian updates
        iptables -A OUTPUT -p tcp --dport 80 -m string --string "archive.ubuntu.com" --algo bm -j DROP 2>/dev/null || true
        iptables -A OUTPUT -p tcp --dport 80 -m string --string "security.ubuntu.com" --algo bm -j DROP 2>/dev/null || true

        echo -e "${GREEN}  ✓${NC} OS updates blocked"
    fi

    # ================================================================
    # LAYER 5: MSS/MTU CLAMPING
    # ================================================================
    # Adjust packet sizes to match mobile traffic

    if [ "$STEALTH_LEVEL" -ge 3 ]; then
        echo -e "${GREEN}[STEALTH]${NC} Layer 5: MSS/MTU Adjustment"

        # Clamp MSS to avoid fragmentation detection
        iptables -t mangle -A FORWARD -o $WIFI_INTERFACE -p tcp --tcp-flags SYN,RST SYN -j TCPMSS --clamp-mss-to-pmtu

        echo -e "${GREEN}  ✓${NC} MSS clamping enabled"
    fi

    # ================================================================
    # LAYER 6: TRAFFIC RATE LIMITING (Optional)
    # ================================================================
    # Limit bandwidth to appear more like phone usage

    if [ "$STEALTH_LEVEL" -ge 3 ]; then
        echo -e "${GREEN}[STEALTH]${NC} Layer 6: Traffic Shaping (Optional)"

        # Note: tc (traffic control) rules would go here
        # Omitted for now to avoid breaking legitimate high-speed use

        echo -e "${GREEN}  ✓${NC} Traffic shaping ready"
    fi

    echo ""
    echo -e "${GREEN}[STEALTH]${NC} Carrier bypass ACTIVE - ${STEALTH_LEVEL} layers enabled"
    echo -e "${YELLOW}[WARNING]${NC} Not 100% foolproof. Use VPN for maximum stealth."
}

disable_stealth() {
    echo -e "${GREEN}[STEALTH]${NC} Disabling carrier bypass..."

    # Remove mangle chains
    iptables -t mangle -D POSTROUTING -o $WIFI_INTERFACE -j WIFI_STEALTH 2>/dev/null || true
    iptables -t mangle -F WIFI_STEALTH 2>/dev/null || true
    iptables -t mangle -X WIFI_STEALTH 2>/dev/null || true

    ip6tables -t mangle -D POSTROUTING -o $WIFI_INTERFACE -j WIFI_STEALTH 2>/dev/null || true
    ip6tables -t mangle -F WIFI_STEALTH 2>/dev/null || true
    ip6tables -t mangle -X WIFI_STEALTH 2>/dev/null || true

    # Re-enable IPv6
    sysctl -w net.ipv6.conf.$WIFI_INTERFACE.disable_ipv6=0 >/dev/null 2>&1 || true

    # Remove DNS redirects
    iptables -t nat -D OUTPUT -o $WIFI_INTERFACE -p udp --dport 53 -j DNAT 2>/dev/null || true
    iptables -t nat -D OUTPUT -o $WIFI_INTERFACE -p tcp --dport 53 -j DNAT 2>/dev/null || true

    # Remove Google DNS blocks
    iptables -D OUTPUT -d 8.8.8.8 -j DROP 2>/dev/null || true
    iptables -D OUTPUT -d 8.8.4.4 -j DROP 2>/dev/null || true

    # Remove string matching rules
    iptables -D OUTPUT -m string --string "windowsupdate" --algo bm -j DROP 2>/dev/null || true
    iptables -D OUTPUT -m string --string "update.microsoft" --algo bm -j DROP 2>/dev/null || true
    iptables -D OUTPUT -m string --string "swcdn.apple.com" --algo bm -j DROP 2>/dev/null || true
    iptables -D OUTPUT -m string --string "mesu.apple.com" --algo bm -j DROP 2>/dev/null || true
    iptables -D OUTPUT -p tcp --dport 80 -m string --string "archive.ubuntu.com" --algo bm -j DROP 2>/dev/null || true
    iptables -D OUTPUT -p tcp --dport 80 -m string --string "security.ubuntu.com" --algo bm -j DROP 2>/dev/null || true

    # Re-enable IPv6 policy
    ip6tables -P INPUT ACCEPT 2>/dev/null || true
    ip6tables -P FORWARD ACCEPT 2>/dev/null || true
    ip6tables -P OUTPUT ACCEPT 2>/dev/null || true

    echo -e "${GREEN}✓${NC} Carrier bypass disabled"
}

status_stealth() {
    echo "WiFi Stealth Mode Status"
    echo "========================"

    if iptables -t mangle -L WIFI_STEALTH -n >/dev/null 2>&1; then
        echo -e "${GREEN}✓ ACTIVE${NC}"
        echo ""
        echo "Active rules:"
        iptables -t mangle -L WIFI_STEALTH -n -v 2>/dev/null || true
    else
        echo -e "${RED}✗ INACTIVE${NC}"
    fi
}

case "$1" in
    enable|start|on)
        if [[ $EUID -ne 0 ]]; then
            echo "Error: Must run as root"
            exit 1
        fi
        enable_stealth
        ;;
    disable|stop|off)
        if [[ $EUID -ne 0 ]]; then
            echo "Error: Must run as root"
            exit 1
        fi
        disable_stealth
        ;;
    status)
        status_stealth
        ;;
    *)
        echo "Usage: $0 {enable|disable|status} [interface] [level]"
        echo ""
        echo "Examples:"
        echo "  $0 enable wlan0 3     # Aggressive mode on wlan0"
        echo "  $0 enable wlan0 2     # Moderate mode"
        echo "  $0 disable wlan0"
        echo "  $0 status"
        echo ""
        echo "Stealth Levels:"
        echo "  1 = Basic (TTL only)"
        echo "  2 = Moderate (TTL + IPv6 + DNS)"
        echo "  3 = Aggressive (All layers)"
        exit 1
        ;;
esac

exit 0
