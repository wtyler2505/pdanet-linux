"""
Error Database for PdaNet Linux
Maps error codes to user-friendly solutions
"""

from typing import List, Dict, Optional
from dataclasses import dataclass


@dataclass
class ErrorSolution:
    """Represents a solution to an error"""
    title: str
    steps: List[str]
    auto_fix_command: Optional[str] = None  # Command to run for auto-fix
    requires_root: bool = False


@dataclass
class ErrorInfo:
    """Complete information about an error"""
    code: str
    title: str
    description: str
    category: str  # "network", "permission", "config", "system"
    severity: str  # "critical", "high", "medium", "low"
    solutions: List[ErrorSolution]
    documentation_url: Optional[str] = None


# ============================================================================
# ERROR DATABASE
# ============================================================================

ERROR_DATABASE = {
    # Network Errors
    "interface_not_found": ErrorInfo(
        code="interface_not_found",
        title="Network Interface Not Found",
        description="Unable to detect USB or WiFi interface for tethering",
        category="network",
        severity="high",
        solutions=[
            ErrorSolution(
                title="Check USB Connection",
                steps=[
                    "Ensure Android device is connected via USB cable",
                    "Try a different USB port",
                    "Try a different USB cable",
                    "Check if device appears in 'lsusb' output"
                ]
            ),
            ErrorSolution(
                title="Enable USB Debugging",
                steps=[
                    "On Android: Settings → About Phone",
                    "Tap 'Build Number' 7 times to enable Developer Options",
                    "Settings → Developer Options → Enable 'USB Debugging'",
                    "Accept the USB debugging prompt when device is connected"
                ]
            ),
            ErrorSolution(
                title="Restart USB Services",
                steps=[
                    "Run: sudo systemctl restart NetworkManager",
                    "Disconnect and reconnect the device",
                    "Wait 10 seconds for interface to appear"
                ],
                auto_fix_command="systemctl restart NetworkManager",
                requires_root=True
            ),
            ErrorSolution(
                title="Check WiFi Connection",
                steps=[
                    "Verify WiFi hotspot is enabled on Android",
                    "Check that Linux is connected to the hotspot",
                    "Run: nmcli device wifi list",
                    "Verify SSID appears in the list"
                ]
            )
        ]
    ),
    
    "proxy_not_accessible": ErrorInfo(
        code="proxy_not_accessible",
        title="PdaNet Proxy Not Accessible",
        description="Cannot connect to PdaNet proxy at 192.168.49.1:8000",
        category="network",
        severity="critical",
        solutions=[
            ErrorSolution(
                title="Restart PdaNet+ App",
                steps=[
                    "Open PdaNet+ app on Android device",
                    "Toggle 'Activate USB Mode' off",
                    "Wait 3 seconds",
                    "Toggle 'Activate USB Mode' on",
                    "Wait 5 seconds for proxy to start",
                    "Check that app shows 'Connected'"
                ]
            ),
            ErrorSolution(
                title="Verify Proxy Settings",
                steps=[
                    "Open Settings in PdaNet Linux",
                    "Go to Network tab",
                    "Verify Proxy IP is 192.168.49.1",
                    "Verify Proxy Port is 8000",
                    "Try different port if custom configuration used"
                ]
            ),
            ErrorSolution(
                title="Test Proxy Manually",
                steps=[
                    "Run: curl -x http://192.168.49.1:8000 http://ipinfo.io/ip",
                    "If this works, proxy is accessible",
                    "If timeout, PdaNet+ app may not be running",
                    "Check Android device screen is unlocked"
                ]
            ),
            ErrorSolution(
                title="Check Firewall",
                steps=[
                    "Firewall may be blocking proxy access",
                    "Run: sudo ufw status",
                    "If active, add rule: sudo ufw allow from any to 192.168.49.1",
                    "Or temporarily disable: sudo ufw disable"
                ],
                auto_fix_command="ufw allow from any to 192.168.49.1",
                requires_root=True
            )
        ]
    ),
    
    "iptables_failed": ErrorInfo(
        code="iptables_failed",
        title="Failed to Apply iptables Rules",
        description="Could not configure network routing rules",
        category="permission",
        severity="high",
        solutions=[
            ErrorSolution(
                title="Check Root Permissions",
                steps=[
                    "iptables requires root privileges",
                    "Ensure PolicyKit is installed: which pkexec",
                    "Test: pkexec whoami (should return 'root')",
                    "If failed, install policykit: sudo apt install policykit-1"
                ]
            ),
            ErrorSolution(
                title="Check iptables Installation",
                steps=[
                    "Verify iptables is installed: which iptables",
                    "If not found, install: sudo apt install iptables",
                    "Check version: iptables --version"
                ],
                auto_fix_command="apt install -y iptables",
                requires_root=True
            ),
            ErrorSolution(
                title="Clear Existing Rules",
                steps=[
                    "Existing rules may conflict",
                    "Run: sudo iptables -t nat -F",
                    "Run: sudo iptables -t mangle -F",
                    "Try connecting again"
                ],
                auto_fix_command="iptables -t nat -F && iptables -t mangle -F",
                requires_root=True
            )
        ]
    ),
    
    "redsocks_failed": ErrorInfo(
        code="redsocks_failed",
        title="Failed to Start redsocks Service",
        description="Could not start transparent proxy service",
        category="system",
        severity="high",
        solutions=[
            ErrorSolution(
                title="Check redsocks Installation",
                steps=[
                    "Verify redsocks is installed: which redsocks",
                    "If not found, install: sudo apt install redsocks",
                    "Check service status: systemctl status redsocks"
                ],
                auto_fix_command="apt install -y redsocks",
                requires_root=True
            ),
            ErrorSolution(
                title="Check Configuration",
                steps=[
                    "Check redsocks config: cat /tmp/redsocks.conf",
                    "Verify proxy IP and port are correct",
                    "Look for syntax errors in config"
                ]
            ),
            ErrorSolution(
                title="Check Port Availability",
                steps=[
                    "redsocks needs port 12345 available",
                    "Check: sudo netstat -tlnp | grep 12345",
                    "If in use, kill the process or use different port"
                ]
            ),
            ErrorSolution(
                title="Start Manually",
                steps=[
                    "Try starting manually: sudo redsocks -c /tmp/redsocks.conf",
                    "Check output for error messages",
                    "Fix any reported configuration issues"
                ]
            )
        ]
    ),
    
    "permission_denied": ErrorInfo(
        code="permission_denied",
        title="Permission Denied",
        description="Insufficient privileges to perform operation",
        category="permission",
        severity="critical",
        solutions=[
            ErrorSolution(
                title="Run with PolicyKit",
                steps=[
                    "PdaNet Linux uses PolicyKit for privilege escalation",
                    "You should be prompted for password automatically",
                    "If not prompted, PolicyKit may not be configured",
                    "Install: sudo apt install policykit-1"
                ]
            ),
            ErrorSolution(
                title="Check User Permissions",
                steps=[
                    "Your user must be in sudoers",
                    "Check: sudo -l",
                    "If 'command not found', add user to sudo group:",
                    "sudo usermod -aG sudo $USER",
                    "Log out and log back in"
                ]
            ),
            ErrorSolution(
                title="Verify PolicyKit Rules",
                steps=[
                    "Check PolicyKit rules exist",
                    "Look in: /usr/share/polkit-1/actions/",
                    "Should have: com.pdanet.linux.policy",
                    "If missing, reinstall PdaNet Linux"
                ]
            )
        ]
    ),
    
    "config_invalid": ErrorInfo(
        code="config_invalid",
        title="Invalid Configuration",
        description="Configuration file is corrupted or contains invalid values",
        category="config",
        severity="medium",
        solutions=[
            ErrorSolution(
                title="Reset to Defaults",
                steps=[
                    "Open Settings dialog",
                    "Click 'Reset to Defaults'",
                    "Click 'OK' to save",
                    "Try connecting again"
                ]
            ),
            ErrorSolution(
                title="Restore from Backup",
                steps=[
                    "Check for backup: ls ~/.config/pdanet-linux/*.bak",
                    "If backup exists, restore it:",
                    "cp ~/.config/pdanet-linux/config.json.bak ~/.config/pdanet-linux/config.json",
                    "Restart PdaNet Linux"
                ]
            ),
            ErrorSolution(
                title="Delete and Recreate",
                steps=[
                    "Backup first: cp ~/.config/pdanet-linux/config.json ~/config.json.old",
                    "Delete config: rm ~/.config/pdanet-linux/config.json",
                    "Restart PdaNet Linux",
                    "First-run wizard will create new config"
                ]
            )
        ]
    ),
    
    "connection_timeout": ErrorInfo(
        code="connection_timeout",
        title="Connection Timeout",
        description="Connection attempt timed out",
        category="network",
        severity="medium",
        solutions=[
            ErrorSolution(
                title="Increase Timeout",
                steps=[
                    "Open Settings → Network tab",
                    "Increase 'Connection Timeout' to 60 seconds",
                    "Click 'OK' to save",
                    "Try connecting again"
                ]
            ),
            ErrorSolution(
                title="Check Network Quality",
                steps=[
                    "Weak signal may cause timeouts",
                    "Move closer to WiFi hotspot",
                    "Use USB mode instead of WiFi",
                    "Check signal strength in status bar"
                ]
            ),
            ErrorSolution(
                title="Verify Device is Responding",
                steps=[
                    "Ping device: ping 192.168.49.1",
                    "If no response, device may be sleeping",
                    "Unlock device screen",
                    "Ensure PdaNet+ app is in foreground"
                ]
            )
        ]
    ),
    
    "dns_resolution_failed": ErrorInfo(
        code="dns_resolution_failed",
        title="DNS Resolution Failed",
        description="Unable to resolve domain names",
        category="network",
        severity="medium",
        solutions=[
            ErrorSolution(
                title="Check DNS Settings",
                steps=[
                    "Open Settings → Stealth tab",
                    "Verify 'DNS Leak Prevention' is enabled",
                    "Check 'Custom DNS Servers' if specified",
                    "Try: 1.1.1.1, 8.8.8.8"
                ]
            ),
            ErrorSolution(
                title="Test DNS Manually",
                steps=[
                    "Run: nslookup google.com",
                    "If fails, DNS is not working",
                    "Run: nslookup google.com 8.8.8.8",
                    "If works, configure custom DNS in settings"
                ]
            ),
            ErrorSolution(
                title="Restart NetworkManager",
                steps=[
                    "NetworkManager handles DNS",
                    "Run: sudo systemctl restart NetworkManager",
                    "Wait 10 seconds",
                    "Try connecting again"
                ],
                auto_fix_command="systemctl restart NetworkManager",
                requires_root=True
            )
        ]
    ),
    
    "interface_disappeared": ErrorInfo(
        code="interface_disappeared",
        title="Network Interface Disappeared",
        description="Connection lost because interface went offline",
        category="network",
        severity="high",
        solutions=[
            ErrorSolution(
                title="Check Physical Connection",
                steps=[
                    "USB cable may have disconnected",
                    "Check cable is firmly connected",
                    "Try a different USB port",
                    "WiFi: check still connected to hotspot"
                ]
            ),
            ErrorSolution(
                title="Enable Auto-Reconnect",
                steps=[
                    "Open Settings → Network tab",
                    "Enable 'Auto-Reconnect'",
                    "Set 'Max Reconnect Attempts' to 5",
                    "Set 'Reconnect Delay' to 5 seconds",
                    "PdaNet will automatically reconnect on loss"
                ]
            ),
            ErrorSolution(
                title="Check Power Management",
                steps=[
                    "USB power management may disable interface",
                    "Disable USB autosuspend:",
                    "echo 'on' | sudo tee /sys/bus/usb/devices/*/power/control",
                    "Or configure in BIOS/UEFI settings"
                ]
            )
        ]
    ),
}


def get_error_info(error_code: str) -> Optional[ErrorInfo]:
    """
    Get error information by code
    
    Args:
        error_code: Error code string
    
    Returns:
        ErrorInfo object or None if not found
    """
    return ERROR_DATABASE.get(error_code)


def search_errors_by_category(category: str) -> List[ErrorInfo]:
    """
    Get all errors in a category
    
    Args:
        category: Category string (network, permission, config, system)
    
    Returns:
        List of ErrorInfo objects
    """
    return [
        error for error in ERROR_DATABASE.values()
        if error.category == category
    ]


def search_errors_by_severity(severity: str) -> List[ErrorInfo]:
    """
    Get all errors of a severity level
    
    Args:
        severity: Severity string (critical, high, medium, low)
    
    Returns:
        List of ErrorInfo objects
    """
    return [
        error for error in ERROR_DATABASE.values()
        if error.severity == severity
    ]


def get_all_error_codes() -> List[str]:
    """Get list of all error codes"""
    return list(ERROR_DATABASE.keys())
