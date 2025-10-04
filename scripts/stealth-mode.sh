#!/bin/bash
#
# stealth-mode.sh - Hide tethering usage from carrier detection
# Implements similar functionality to PdaNet's "Hide Tether Usage" feature
#

# Configuration
IPTABLES_MANGLE_CHAIN="PDANET_STEALTH"

enable_stealth() {
    echo "Enabling stealth mode (hide tethering usage)..."

    # Create mangle chain for TTL/HL modification
    if ! iptables -t mangle -L $IPTABLES_MANGLE_CHAIN &>/dev/null; then
        iptables -t mangle -N $IPTABLES_MANGLE_CHAIN
    fi

    # Flush existing rules
    iptables -t mangle -F $IPTABLES_MANGLE_CHAIN

    # =====================================================
    # TTL (Time-To-Live) Modification
    # =====================================================
    # Carriers detect tethering by checking if TTL is decremented
    # (desktop/laptop traffic goes through phone, decreasing TTL)
    # Set all outgoing packets to TTL 65 (common mobile value)

    iptables -t mangle -A $IPTABLES_MANGLE_CHAIN -j TTL --ttl-set 65

    # Apply to POSTROUTING
    if ! iptables -t mangle -C POSTROUTING -j $IPTABLES_MANGLE_CHAIN 2>/dev/null; then
        iptables -t mangle -A POSTROUTING -j $IPTABLES_MANGLE_CHAIN
    fi

    # =====================================================
    # Block OS-Specific Update Ports
    # =====================================================
    # Many carriers detect tethering by seeing Windows/Mac update traffic
    # Block these ports to prevent detection

    # Windows Update (port 80, 443 with specific IPs would be better, but we'll use a simple approach)
    # Block common Windows Update domains by blocking specific port combinations

    # Drop Windows Update traffic (helps avoid detection)
    iptables -A OUTPUT -p tcp --dport 80 -m string --string "windowsupdate.com" --algo bm -j DROP 2>/dev/null || true
    iptables -A OUTPUT -p tcp --dport 443 -m string --string "windowsupdate.com" --algo bm -j DROP 2>/dev/null || true

    # Block Microsoft telemetry
    iptables -A OUTPUT -p tcp --dport 443 -m string --string "telemetry.microsoft.com" --algo bm -j DROP 2>/dev/null || true

    # Block Mac App Store updates (port 80/443)
    iptables -A OUTPUT -p tcp --dport 80 -m string --string "apple.com" --algo bm -j DROP 2>/dev/null || true

    # Note: The above string matching rules may not work in all cases due to HTTPS encryption
    # A more robust solution would use a transparent proxy with SSL inspection (complex)

    echo "✓ Stealth mode enabled"
    echo ""
    echo "Active stealth features:"
    echo "  - TTL normalization (set to 65)"
    echo "  - OS update blocking (Windows/Mac)"
    echo ""
    echo "Note: This reduces carrier detection but is not 100% foolproof."
    echo "For maximum stealth, use a VPN over the tethered connection."
}

disable_stealth() {
    echo "Disabling stealth mode..."

    # Remove mangle chain from POSTROUTING
    if iptables -t mangle -C POSTROUTING -j $IPTABLES_MANGLE_CHAIN 2>/dev/null; then
        iptables -t mangle -D POSTROUTING -j $IPTABLES_MANGLE_CHAIN
    fi

    # Flush and delete mangle chain
    if iptables -t mangle -L $IPTABLES_MANGLE_CHAIN &>/dev/null; then
        iptables -t mangle -F $IPTABLES_MANGLE_CHAIN
        iptables -t mangle -X $IPTABLES_MANGLE_CHAIN
    fi

    # Remove string matching rules (if they exist)
    iptables -D OUTPUT -p tcp --dport 80 -m string --string "windowsupdate.com" --algo bm -j DROP 2>/dev/null || true
    iptables -D OUTPUT -p tcp --dport 443 -m string --string "windowsupdate.com" --algo bm -j DROP 2>/dev/null || true
    iptables -D OUTPUT -p tcp --dport 443 -m string --string "telemetry.microsoft.com" --algo bm -j DROP 2>/dev/null || true
    iptables -D OUTPUT -p tcp --dport 80 -m string --string "apple.com" --algo bm -j DROP 2>/dev/null || true

    echo "✓ Stealth mode disabled"
}

status_stealth() {
    echo "Stealth mode status:"
    echo "===================="

    if iptables -t mangle -L $IPTABLES_MANGLE_CHAIN &>/dev/null; then
        echo "✓ Stealth mode is ENABLED"
        echo ""
        echo "Active TTL rules:"
        iptables -t mangle -L $IPTABLES_MANGLE_CHAIN -n -v
    else
        echo "✗ Stealth mode is DISABLED"
    fi
}

case "$1" in
    enable|start|on)
        if [[ $EUID -ne 0 ]]; then
            echo "Error: This script must be run as root (use sudo)"
            exit 1
        fi
        enable_stealth
        ;;
    disable|stop|off)
        if [[ $EUID -ne 0 ]]; then
            echo "Error: This script must be run as root (use sudo)"
            exit 1
        fi
        disable_stealth
        ;;
    status)
        status_stealth
        ;;
    *)
        echo "Usage: $0 {enable|disable|status}"
        echo ""
        echo "Commands:"
        echo "  enable  - Enable stealth mode (hide tethering from carrier)"
        echo "  disable - Disable stealth mode"
        echo "  status  - Show current stealth mode status"
        exit 1
        ;;
esac

exit 0
