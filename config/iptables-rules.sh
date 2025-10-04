#!/bin/bash
#
# iptables-rules.sh - Configure iptables for transparent proxy redirection
#

# Configuration
REDSOCKS_PORT="12345"
PDANET_PROXY_IP="192.168.49.1"

start_rules() {
    echo "Applying iptables rules for PdaNet..."

    # Create REDSOCKS chain if it doesn't exist
    if ! iptables -t nat -L REDSOCKS &>/dev/null; then
        iptables -t nat -N REDSOCKS
    fi

    # Flush existing rules in REDSOCKS chain
    iptables -t nat -F REDSOCKS

    # Don't redirect local traffic
    iptables -t nat -A REDSOCKS -d 0.0.0.0/8 -j RETURN
    iptables -t nat -A REDSOCKS -d 10.0.0.0/8 -j RETURN
    iptables -t nat -A REDSOCKS -d 127.0.0.0/8 -j RETURN
    iptables -t nat -A REDSOCKS -d 169.254.0.0/16 -j RETURN
    iptables -t nat -A REDSOCKS -d 172.16.0.0/12 -j RETURN
    iptables -t nat -A REDSOCKS -d 192.168.0.0/16 -j RETURN
    iptables -t nat -A REDSOCKS -d 224.0.0.0/4 -j RETURN
    iptables -t nat -A REDSOCKS -d 240.0.0.0/4 -j RETURN

    # Don't redirect traffic to the PdaNet proxy itself
    iptables -t nat -A REDSOCKS -d $PDANET_PROXY_IP -j RETURN

    # Redirect all other TCP traffic to redsocks
    iptables -t nat -A REDSOCKS -p tcp -j REDIRECT --to-ports $REDSOCKS_PORT

    # Apply REDSOCKS chain to OUTPUT (for local traffic)
    if ! iptables -t nat -C OUTPUT -p tcp -j REDSOCKS 2>/dev/null; then
        iptables -t nat -A OUTPUT -p tcp -j REDSOCKS
    fi

    # Optional: Apply to PREROUTING (for forwarded traffic)
    # Uncomment if you want to share connection with other devices
    # if ! iptables -t nat -C PREROUTING -p tcp -j REDSOCKS 2>/dev/null; then
    #     iptables -t nat -A PREROUTING -p tcp -j REDSOCKS
    # fi

    echo "✓ Iptables rules applied successfully"
}

stop_rules() {
    echo "Removing iptables rules for PdaNet..."

    # Remove jump rules
    if iptables -t nat -C OUTPUT -p tcp -j REDSOCKS 2>/dev/null; then
        iptables -t nat -D OUTPUT -p tcp -j REDSOCKS
    fi

    # Uncomment if you enabled PREROUTING above
    # if iptables -t nat -C PREROUTING -p tcp -j REDSOCKS 2>/dev/null; then
    #     iptables -t nat -D PREROUTING -p tcp -j REDSOCKS
    # fi

    # Flush and delete REDSOCKS chain
    if iptables -t nat -L REDSOCKS &>/dev/null; then
        iptables -t nat -F REDSOCKS
        iptables -t nat -X REDSOCKS
    fi

    echo "✓ Iptables rules removed successfully"
}

status_rules() {
    echo "Current REDSOCKS iptables rules:"
    echo "================================"
    if iptables -t nat -L REDSOCKS -n -v 2>/dev/null; then
        echo ""
        echo "OUTPUT chain routing:"
        iptables -t nat -L OUTPUT -n -v | grep REDSOCKS
    else
        echo "No REDSOCKS rules active"
    fi
}

case "$1" in
    start)
        start_rules
        ;;
    stop)
        stop_rules
        ;;
    restart)
        stop_rules
        sleep 1
        start_rules
        ;;
    status)
        status_rules
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status}"
        exit 1
        ;;
esac

exit 0
