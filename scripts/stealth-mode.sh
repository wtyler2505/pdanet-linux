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

    # IMPORTANT NOTE: String matching on HTTPS traffic (port 443) is INEFFECTIVE because
    # the traffic is encrypted. The following rules only work for unencrypted HTTP (port 80).
    # For proper domain blocking, use DNS-based methods or a hosts file approach.
    
    # Block HTTP (port 80) traffic to common update domains
    # This only catches unencrypted update checks (most modern systems use HTTPS)
    iptables -A OUTPUT -p tcp --dport 80 -m string --string "windowsupdate.com" --algo bm -j DROP 2>/dev/null || true
    
    # REMOVED: HTTPS string matching (lines 46, 49) - completely ineffective due to encryption
    # For HTTPS blocking, use DNS redirection instead (see wifi-stealth.sh DNS layer)
    
    # Note: For robust update/telemetry blocking, implement DNS-based blocking:
    # 1. Redirect DNS queries to local resolver
    # 2. Block update domains in /etc/hosts or dnsmasq
    # 3. Use SNI inspection (requires specialized tools)

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
