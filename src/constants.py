#!/usr/bin/env python3
"""
PdaNet Linux - Application Constants
All magic numbers and configuration defaults in one place
"""

# ============================================================================
# CONNECTION CONFIGURATION
# ============================================================================

# Timeouts (seconds)
CONNECTION_TIMEOUT_SECONDS = 30
PROXY_CHECK_TIMEOUT_SECONDS = 5
RECONNECT_DELAY_SECONDS = 5
RETRY_MAX_ATTEMPTS = 3
INTERFACE_DETECTION_TIMEOUT = 10

# Network Configuration
TTL_VALUE_PHONE_TRAFFIC = 65  # Standard mobile device TTL
TTL_VALUE_DESKTOP = 64         # Standard desktop/laptop TTL
PROXY_DEFAULT_IP = "192.168.49.1"
PROXY_DEFAULT_PORT = 8000
REDSOCKS_PORT = 12345

# ============================================================================
# PERFORMANCE TUNING
# ============================================================================

# Threading
THREAD_POOL_MAX_WORKERS = 3
THREAD_POOL_MIN_WORKERS = 1

# Caching
CACHE_TTL_SECONDS = 30
CACHE_MAX_SIZE = 10
CACHE_CLEANUP_INTERVAL_SECONDS = 300  # 5 minutes

# History/Buffers
NETWORK_FLOW_HISTORY_SIZE = 10000
SECURITY_EVENTS_HISTORY_SIZE = 1000
LOG_BUFFER_MAX_SIZE = 1000
QUALITY_HISTORY_SIZE = 100

# ============================================================================
# GUI CONFIGURATION
# ============================================================================

# Update Intervals (milliseconds)
GUI_UPDATE_INTERVAL_MS = 1000
STATS_COLLECTION_INTERVAL_MS = 1000
QUALITY_MONITORING_INTERVAL_MS = 30000  # 30 seconds
TRAY_ICON_UPDATE_INTERVAL_MS = 2000

# Window Dimensions
MAIN_WINDOW_WIDTH = 800
MAIN_WINDOW_HEIGHT = 600
MAIN_WINDOW_MIN_WIDTH = 700
MAIN_WINDOW_MIN_HEIGHT = 500

# Panel Spacing
PANEL_SPACING = 10
PANEL_BORDER_WIDTH = 10
BUTTON_SPACING = 5

# ============================================================================
# DATA USAGE TRACKING
# ============================================================================

# Thresholds (bytes)
DATA_WARNING_THRESHOLD_BYTES = 10 * 1024 * 1024 * 1024  # 10GB
DATA_CRITICAL_THRESHOLD_BYTES = 20 * 1024 * 1024 * 1024  # 20GB
BANDWIDTH_SUSPICIOUS_THRESHOLD_BYTES = 1024 * 1024  # 1MB/s

# Display Units
BYTES_PER_KB = 1024
BYTES_PER_MB = 1024 * 1024
BYTES_PER_GB = 1024 * 1024 * 1024

# ============================================================================
# STEALTH MODE CONFIGURATION
# ============================================================================

# Stealth Levels
STEALTH_LEVEL_BASIC = 1       # TTL only
STEALTH_LEVEL_MODERATE = 2    # TTL + IPv6 + DNS
STEALTH_LEVEL_AGGRESSIVE = 3  # All 6 layers

# Default Stealth Settings
DEFAULT_STEALTH_LEVEL = STEALTH_LEVEL_AGGRESSIVE
DEFAULT_STEALTH_ENABLED = True

# ============================================================================
# NETWORK QUALITY ASSESSMENT
# ============================================================================

# Quality Thresholds (0-100 scale)
QUALITY_SCORE_EXCELLENT = 90
QUALITY_SCORE_GOOD = 70
QUALITY_SCORE_FAIR = 50
QUALITY_SCORE_POOR = 30

# Latency Thresholds (milliseconds)
LATENCY_EXCELLENT_MS = 50
LATENCY_GOOD_MS = 100
LATENCY_FAIR_MS = 200
LATENCY_POOR_MS = 500

# Packet Loss Thresholds (percentage)
PACKET_LOSS_ACCEPTABLE_PERCENT = 1.0
PACKET_LOSS_POOR_PERCENT = 5.0

# Bandwidth Thresholds (bytes per second)
BANDWIDTH_EXCELLENT_BPS = 10 * 1024 * 1024   # 10 MB/s
BANDWIDTH_GOOD_BPS = 5 * 1024 * 1024         # 5 MB/s
BANDWIDTH_FAIR_BPS = 1 * 1024 * 1024         # 1 MB/s
BANDWIDTH_POOR_BPS = 500 * 1024              # 500 KB/s

# ============================================================================
# IPHONE HOTSPOT BYPASS
# ============================================================================

# Bypass Technique Identifiers
BYPASS_TTL_MODIFICATION = "ttl_modification"
BYPASS_TCP_FINGERPRINT = "tcp_fingerprint_masking"
BYPASS_USER_AGENT = "user_agent_rotation"
BYPASS_DNS_LEAK = "dns_leak_prevention"
BYPASS_IPV6_DISABLE = "ipv6_complete_disable"
BYPASS_PACKET_SIZE = "packet_size_randomization"
BYPASS_TIMING_OBFUSCATION = "timing_pattern_obfuscation"
BYPASS_TRAFFIC_SHAPING = "traffic_shaping"
BYPASS_PROTOCOL_TUNNELING = "protocol_tunneling"
BYPASS_ENTROPY_INJECTION = "entropy_injection"

# ============================================================================
# FILE PATHS
# ============================================================================

# Configuration Directory (use XDG Base Directory Specification)
CONFIG_DIR_NAME = "pdanet-linux"
CONFIG_FILE_NAME = "config.json"
PROFILES_FILE_NAME = "profiles.json"
STATISTICS_FILE_NAME = "statistics.json"
LOG_FILE_NAME = "pdanet.log"

# ============================================================================
# LOGGING
# ============================================================================

# Log Levels
LOG_LEVEL_DEBUG = "DEBUG"
LOG_LEVEL_INFO = "INFO"
LOG_LEVEL_WARNING = "WARNING"
LOG_LEVEL_ERROR = "ERROR"
LOG_LEVEL_CRITICAL = "CRITICAL"

DEFAULT_LOG_LEVEL = LOG_LEVEL_INFO
LOG_MAX_BYTES = 10 * 1024 * 1024  # 10MB
LOG_BACKUP_COUNT = 5

# ============================================================================
# COLORS (Cyberpunk Theme)
# ============================================================================

# GTK CSS colors
COLOR_BG_PRIMARY = "#000000"        # Pure black
COLOR_BG_SECONDARY = "#0a0a0a"      # Slightly lighter black
COLOR_BG_PANEL = "#111111"          # Panel background

COLOR_FG_PRIMARY = "#00FF00"        # Neon green (success/active)
COLOR_FG_SECONDARY = "#888888"      # Gray (inactive)
COLOR_FG_ERROR = "#FF0000"          # Red (errors)
COLOR_FG_WARNING = "#FFFF00"        # Yellow (warnings)
COLOR_FG_INFO = "#00FFFF"           # Cyan (info)

COLOR_BORDER = "#00FF00"            # Green borders
COLOR_HIGHLIGHT = "#00FF00"         # Green highlights

# ============================================================================
# FONTS
# ============================================================================

FONT_FAMILY_MONO = "JetBrains Mono, Courier New, monospace"
FONT_SIZE_NORMAL = 10
FONT_SIZE_LARGE = 12
FONT_SIZE_XLARGE = 14
FONT_SIZE_SMALL = 9

# ============================================================================
# CONNECTION MODES
# ============================================================================

MODE_USB = "usb"
MODE_WIFI = "wifi"
MODE_IPHONE = "iphone"

# ============================================================================
# VALIDATION LIMITS
# ============================================================================

# SSID Validation
SSID_MIN_LENGTH = 1
SSID_MAX_LENGTH = 32

# Password Validation
PASSWORD_MIN_LENGTH = 8
PASSWORD_MAX_LENGTH = 63

# Port Validation
PORT_MIN = 1
PORT_MAX = 65535

# IP Address Validation
IP_LOOPBACK = "127.0.0.1"
IP_PRIVATE_RANGES = [
    "10.0.0.0/8",
    "172.16.0.0/12",
    "192.168.0.0/16"
]

# ============================================================================
# ERROR MESSAGES
# ============================================================================

ERROR_NO_INTERFACE = "No suitable network interface found"
ERROR_PROXY_UNREACHABLE = "PdaNet proxy not accessible"
ERROR_IPTABLES_FAILED = "Failed to apply iptables rules"
ERROR_REDSOCKS_FAILED = "Failed to start redsocks service"
ERROR_INVALID_CONFIG = "Invalid configuration"
ERROR_PERMISSION_DENIED = "Permission denied - requires root privileges"

# ============================================================================
# SUCCESS MESSAGES
# ============================================================================

SUCCESS_CONNECTED = "Successfully connected"
SUCCESS_DISCONNECTED = "Successfully disconnected"
SUCCESS_CONFIG_SAVED = "Configuration saved"
SUCCESS_PROFILE_CREATED = "Profile created"

# ============================================================================
# KEYBOARD SHORTCUTS
# ============================================================================

# Main actions
SHORTCUT_CONNECT = "<Control>c"
SHORTCUT_DISCONNECT = "<Control>d"
SHORTCUT_QUIT = "<Control>q"
SHORTCUT_SETTINGS = "<Control>s"
SHORTCUT_REFRESH = "F5"

# Views
SHORTCUT_HISTORY = "<Control>h"
SHORTCUT_LOGS = "<Control>l"
SHORTCUT_STATS = "<Control>t"

# Special
SHORTCUT_HELP = "F1"
SHORTCUT_ABOUT = "<Control>a"

# ============================================================================
# BUFFER SIZES
# ============================================================================

PACKET_BUFFER_SIZE = 8192
READ_BUFFER_SIZE = 4096
SOCKET_BUFFER_SIZE = 65536

# ============================================================================
# RETRY CONFIGURATION
# ============================================================================

RETRY_INITIAL_DELAY = 1.0         # seconds
RETRY_MAX_DELAY = 60.0            # seconds
RETRY_EXPONENTIAL_BASE = 2.0      # for exponential backoff
RETRY_JITTER_MAX = 0.1            # 10% jitter

# ============================================================================
# NOTIFICATIONS
# ============================================================================

NOTIFICATION_TIMEOUT_MS = 5000    # 5 seconds
NOTIFICATION_ICON_SIZE = 48       # pixels

# ============================================================================
# TESTING CONSTANTS
# ============================================================================

TEST_TIMEOUT_SECONDS = 10
TEST_RETRY_COUNT = 3
TEST_MOCK_DELAY_MS = 100

# ============================================================================
# VERSION INFORMATION
# ============================================================================

APP_NAME = "PdaNet Linux"
APP_VERSION = "1.0.0"
APP_DESCRIPTION = "Network tethering with carrier detection bypass"
APP_AUTHOR = "PdaNet Linux Team"
APP_LICENSE = "MIT"
APP_URL = "https://github.com/yourusername/pdanet-linux"

# ============================================================================
# FEATURE FLAGS (for gradual rollout)
# ============================================================================

FEATURE_ADVANCED_NETWORK_MONITOR = True
FEATURE_INTELLIGENT_BANDWIDTH_MANAGER = True
FEATURE_IPHONE_HOTSPOT_BYPASS = True
FEATURE_CONNECTION_PROFILES = True
FEATURE_USAGE_ANALYTICS = True
FEATURE_COMMAND_PALETTE = True

# ============================================================================
# EXPORT (for easy imports)
# ============================================================================

__all__ = [
    # Connection
    'CONNECTION_TIMEOUT_SECONDS',
    'PROXY_DEFAULT_IP',
    'PROXY_DEFAULT_PORT',
    'TTL_VALUE_PHONE_TRAFFIC',
    
    # GUI
    'GUI_UPDATE_INTERVAL_MS',
    'MAIN_WINDOW_WIDTH',
    'MAIN_WINDOW_HEIGHT',
    
    # Colors
    'COLOR_BG_PRIMARY',
    'COLOR_FG_PRIMARY',
    'COLOR_FG_ERROR',
    
    # Modes
    'MODE_USB',
    'MODE_WIFI',
    'MODE_IPHONE',
    
    # Quality
    'QUALITY_SCORE_EXCELLENT',
    'LATENCY_EXCELLENT_MS',
    
    # Stealth
    'STEALTH_LEVEL_AGGRESSIVE',
    'DEFAULT_STEALTH_ENABLED',
]
