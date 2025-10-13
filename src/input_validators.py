"""
Input Validation Module for PdaNet Linux
SECURITY: Prevents command injection and validates user inputs

Addresses Audit Issues:
- #292: Command injection via SSID/password
- #58-59: Inadequate input validation
- #72-75: Unsafe parsing and validation
"""

import re
import ipaddress
from typing import Optional


class ValidationError(Exception):
    """Raised when input validation fails"""
    pass


# RFC 1123 hostname validation
HOSTNAME_PATTERN = re.compile(
    r'^(?!-)[A-Za-z0-9-]{1,63}(?<!-)$'  # Each label
)

# SSID validation (IEEE 802.11 spec: 0-32 bytes UTF-8)
# We're being conservative and blocking control characters and shells pecial chars
SSID_SAFE_PATTERN = re.compile(
    r'^[A-Za-z0-9 _\-\.@#\(\)\[\]]+$'  # Alphanumeric + safe symbols
)

# Portable unsafe characters that could cause shell issues
# Note: () and [] are allowed in SSID pattern, so excluded from this set
SHELL_UNSAFE_CHARS = set(';&|<>`${}*?!\\"\'\n\r\t')


def validate_ssid(ssid: str, allow_empty: bool = False) -> str:
    """
    Validate WiFi SSID for safety
    
    Args:
        ssid: The SSID to validate
        allow_empty: Whether to allow empty SSID
        
    Returns:
        The validated SSID (unchanged)
        
    Raises:
        ValidationError: If SSID is invalid
    """
    if not ssid:
        if allow_empty:
            return ssid
        raise ValidationError("SSID cannot be empty")
    
    # Check length (IEEE 802.11: max 32 bytes)
    if len(ssid.encode('utf-8')) > 32:
        raise ValidationError(f"SSID too long: {len(ssid.encode('utf-8'))} bytes (max 32)")
    
    # Check for shell-unsafe characters
    unsafe = set(ssid) & SHELL_UNSAFE_CHARS
    if unsafe:
        unsafe_str = ''.join(sorted(unsafe))
        raise ValidationError(
            f"SSID contains unsafe characters: {repr(unsafe_str)}"
        )
    
    # Verify it matches our safe pattern
    if not SSID_SAFE_PATTERN.match(ssid):
        raise ValidationError(
            f"SSID contains invalid characters. Allowed: A-Z, a-z, 0-9, space, _ - . @ # ( ) [ ]"
        )
    
    return ssid


def validate_password(password: str, allow_empty: bool = False, min_length: int = 0) -> str:
    """
    Validate WiFi password for safety
    
    Args:
        password: The password to validate
        allow_empty: Whether to allow empty password
        min_length: Minimum password length (WPA2 requires 8)
        
    Returns:
        The validated password (unchanged)
        
    Raises:
        ValidationError: If password is invalid
    """
    if not password:
        if allow_empty:
            return password
        raise ValidationError("Password cannot be empty")
    
    # Check minimum length
    if len(password) < min_length:
        raise ValidationError(f"Password too short: {len(password)} chars (min {min_length})")
    
    # Check maximum length (WPA2: max 63)
    if len(password) > 63:
        raise ValidationError(f"Password too long: {len(password)} chars (max 63)")
    
    # Check for shell-unsafe characters (these need escaping)
    unsafe = set(password) & SHELL_UNSAFE_CHARS
    if unsafe:
        unsafe_str = ''.join(sorted(unsafe))
        raise ValidationError(
            f"Password contains unsafe characters: {repr(unsafe_str)}. "
            f"Please avoid: ; & | < > ` $ {{ }} ( ) * ? [ ] ! \\ \" ' and control characters"
        )
    
    return password


def validate_ip_address(ip: str, allow_private: bool = True) -> str:
    """
    Validate IP address
    
    Args:
        ip: IP address string
        allow_private: Whether to allow private/internal IPs
        
    Returns:
        The validated IP (unchanged)
        
    Raises:
        ValidationError: If IP is invalid
    """
    if not ip:
        raise ValidationError("IP address cannot be empty")
    
    try:
        addr = ipaddress.ip_address(ip)
    except ValueError as e:
        raise ValidationError(f"Invalid IP address: {e}")
    
    # Check if private IP is allowed
    if not allow_private and addr.is_private:
        raise ValidationError(f"Private IP address not allowed: {ip}")
    
    # Block special addresses
    if addr.is_loopback:
        raise ValidationError(f"Loopback address not allowed: {ip}")
    if addr.is_multicast:
        raise ValidationError(f"Multicast address not allowed: {ip}")
    if addr.is_reserved:
        raise ValidationError(f"Reserved address not allowed: {ip}")
    
    return ip


def validate_port(port: int | str) -> int:
    """
    Validate network port number
    
    Args:
        port: Port number (int or string)
        
    Returns:
        The validated port as int
        
    Raises:
        ValidationError: If port is invalid
    """
    try:
        port_int = int(port)
    except (ValueError, TypeError):
        raise ValidationError(f"Invalid port: {port}")
    
    if port_int < 1 or port_int > 65535:
        raise ValidationError(f"Port out of range: {port_int} (must be 1-65535)")
    
    # Warn about privileged ports
    if port_int < 1024:
        # Not an error, but worth noting
        pass
    
    return port_int


def validate_hostname(hostname: str) -> str:
    """
    Validate hostname (RFC 1123)
    
    Args:
        hostname: Hostname to validate
        
    Returns:
        The validated hostname (unchanged)
        
    Raises:
        ValidationError: If hostname is invalid
    """
    if not hostname:
        raise ValidationError("Hostname cannot be empty")
    
    if len(hostname) > 253:
        raise ValidationError(f"Hostname too long: {len(hostname)} chars (max 253)")
    
    # Split into labels
    labels = hostname.split('.')
    if not labels:
        raise ValidationError("Invalid hostname format")
    
    for label in labels:
        if not label:
            raise ValidationError("Empty label in hostname")
        if len(label) > 63:
            raise ValidationError(f"Label too long: {len(label)} chars (max 63)")
        if not HOSTNAME_PATTERN.match(label):
            raise ValidationError(
                f"Invalid hostname label: {label}. "
                f"Must contain only A-Z, a-z, 0-9, and hyphen (not at start/end)"
            )
    
    return hostname


def validate_interface_name(interface: str) -> str:
    """
    Validate network interface name
    
    Args:
        interface: Interface name (e.g., 'eth0', 'wlan0')
        
    Returns:
        The validated interface name
        
    Raises:
        ValidationError: If interface name is invalid
    """
    if not interface:
        raise ValidationError("Interface name cannot be empty")
    
    # Linux interface names: max 15 chars, alphanumeric + underscore/hyphen
    if len(interface) > 15:
        raise ValidationError(f"Interface name too long: {len(interface)} chars (max 15)")
    
    # Allow alphanumeric, underscore, hyphen, colon (for VLANs), dot (for bridges)
    if not re.match(r'^[a-zA-Z0-9_\-:\.]+$', interface):
        raise ValidationError(
            f"Invalid interface name: {interface}. "
            f"Must contain only A-Z, a-z, 0-9, _, -, :, ."
        )
    
    return interface


def validate_path(path: str, must_be_absolute: bool = False) -> str:
    """
    Validate file path for safety
    
    Args:
        path: File path to validate
        must_be_absolute: Whether path must be absolute
        
    Returns:
        The validated path
        
    Raises:
        ValidationError: If path is invalid
    """
    if not path:
        raise ValidationError("Path cannot be empty")
    
    # Check for path traversal attempts
    if '..' in path:
        raise ValidationError("Path traversal not allowed (..)")
    
    # Check for null bytes
    if '\x00' in path:
        raise ValidationError("Null bytes not allowed in path")
    
    # Check absolute requirement
    if must_be_absolute and not path.startswith('/'):
        raise ValidationError(f"Path must be absolute: {path}")
    
    return path


def sanitize_for_shell(value: str) -> str:
    """
    Escape a string for safe shell usage (last resort - prefer list args)
    
    WARNING: This should NOT be used as primary defense.
    Always use subprocess with list args instead of shell=True.
    This is only for edge cases where shell escaping is unavoidable.
    
    Args:
        value: String to escape
        
    Returns:
        Shell-escaped string
    """
    # Replace single quotes with '\''
    return value.replace("'", "'\\''")


def validate_subprocess_args(args: list[str]) -> list[str]:
    """
    Validate subprocess arguments for safety
    
    Args:
        args: List of command arguments
        
    Returns:
        The validated args list
        
    Raises:
        ValidationError: If args are invalid
    """
    if not args:
        raise ValidationError("Command arguments cannot be empty")
    
    if not isinstance(args, list):
        raise ValidationError(f"Arguments must be a list, not {type(args).__name__}")
    
    for i, arg in enumerate(args):
        if not isinstance(arg, str):
            raise ValidationError(f"Argument {i} must be string, not {type(arg).__name__}")
        
        # Check for null bytes
        if '\x00' in arg:
            raise ValidationError(f"Argument {i} contains null byte")
    
    return args
