#!/usr/bin/env python3
"""
Pytest configuration and shared fixtures
Provides common test utilities and setup for all test modules
"""

import pytest
import sys
import os
import tempfile
import shutil
from unittest.mock import MagicMock, patch
import json

# Add src to path for all tests
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


@pytest.fixture
def mock_gi_imports():
    """Mock GTK/GI imports for testing without GUI dependencies"""
    gi_mock = MagicMock()
    gi_mock.require_version = MagicMock()
    gi_mock.repository = MagicMock()
    gi_mock.repository.Gtk = MagicMock()
    gi_mock.repository.Gdk = MagicMock()
    gi_mock.repository.GLib = MagicMock()
    gi_mock.repository.AppIndicator3 = MagicMock()
    gi_mock.repository.Pango = MagicMock()

    with patch.dict(sys.modules, {
        'gi': gi_mock,
        'gi.repository': gi_mock.repository
    }):
        yield gi_mock


@pytest.fixture
def mock_logger():
    """Mock logger for testing without file I/O"""
    return MagicMock()


@pytest.fixture
def mock_config():
    """Mock configuration manager"""
    config_mock = MagicMock()
    config_mock.get.return_value = "default_value"
    config_mock.set = MagicMock()
    config_mock.save = MagicMock()
    return config_mock


@pytest.fixture
def mock_stats():
    """Mock statistics collector"""
    stats_mock = MagicMock()
    stats_mock.get_bytes_sent.return_value = 1024 * 1024
    stats_mock.get_bytes_received.return_value = 2048 * 1024
    stats_mock.get_ping_latency.return_value = 25.5
    stats_mock.get_interface.return_value = "wlan0"
    return stats_mock


@pytest.fixture
def temp_config_dir():
    """Temporary configuration directory for testing"""
    temp_dir = tempfile.mkdtemp(prefix="pdanet_test_")
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def sample_config_data():
    """Sample configuration data for testing"""
    return {
        "version": "2.0",
        "auto_reconnect": False,
        "reconnect_attempts": 3,
        "window_width": 900,
        "window_height": 600,
        "theme": "cyberpunk",
        "log_level": "INFO",
        "profiles": [
            {
                "name": "Default",
                "mode": "wifi",
                "stealth_level": 3,
                "auto_connect": False
            }
        ]
    }


@pytest.fixture
def mock_connection_manager(mock_logger, mock_config, mock_stats):
    """Mock connection manager with dependencies"""
    with patch('connection_manager.get_logger', return_value=mock_logger), \
         patch('connection_manager.get_config', return_value=mock_config), \
         patch('connection_manager.get_stats', return_value=mock_stats):

        from connection_manager import ConnectionManager
        return ConnectionManager()


@pytest.fixture
def mock_subprocess():
    """Mock subprocess for testing system commands"""
    with patch('subprocess.run') as mock_run:
        # Default successful response
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="",
            stderr=""
        )
        yield mock_run


@pytest.fixture
def network_interfaces():
    """Sample network interface data"""
    return {
        "usb0": {
            "type": "usb",
            "status": "up",
            "ip": "192.168.49.15",
            "gateway": "192.168.49.1"
        },
        "wlan0": {
            "type": "wifi",
            "status": "up",
            "ip": "192.168.43.100",
            "gateway": "192.168.43.1",
            "ssid": "AndroidAP"
        },
        "eth0": {
            "type": "ethernet",
            "status": "down",
            "ip": None,
            "gateway": None
        }
    }


@pytest.fixture
def iptables_rules():
    """Sample iptables rules for testing"""
    return {
        "nat_rules": [
            "iptables -t nat -N REDSOCKS",
            "iptables -t nat -A OUTPUT -p tcp -j REDSOCKS",
            "iptables -t nat -A REDSOCKS -d 127.0.0.0/8 -j RETURN",
            "iptables -t nat -A REDSOCKS -d 192.168.0.0/16 -j RETURN",
            "iptables -t nat -A REDSOCKS -p tcp -j REDIRECT --to-ports 12345"
        ],
        "mangle_rules": [
            "iptables -t mangle -N WIFI_STEALTH",
            "iptables -t mangle -A WIFI_STEALTH -j TTL --ttl-set 65",
            "iptables -t mangle -A OUTPUT -o wlan0 -j WIFI_STEALTH"
        ],
        "ipv6_rules": [
            "ip6tables -A OUTPUT -o wlan0 -j DROP"
        ]
    }


@pytest.fixture
def redsocks_config():
    """Sample redsocks configuration"""
    return """
base {
    log_debug = off;
    log_info = on;
    log = "syslog:daemon";
    daemon = on;
    user = redsocks;
    group = redsocks;
    redirector = iptables;
}

redsocks {
    local_ip = 127.0.0.1;
    local_port = 12345;
    ip = 192.168.49.1;
    port = 8000;
    type = http-connect;
}
"""


@pytest.fixture
def bandwidth_history():
    """Sample bandwidth history data"""
    import time
    current_time = time.time()

    return {
        "bytes_sent": [
            (current_time - 60, 1024 * 100),    # 1 minute ago: 100KB
            (current_time - 30, 1024 * 500),    # 30 seconds ago: 500KB
            (current_time, 1024 * 1024)         # Now: 1MB
        ],
        "bytes_received": [
            (current_time - 60, 1024 * 200),    # 1 minute ago: 200KB
            (current_time - 30, 1024 * 1000),   # 30 seconds ago: 1000KB
            (current_time, 1024 * 2048)         # Now: 2MB
        ]
    }


@pytest.fixture
def theme_colors():
    """Cyberpunk theme color definitions"""
    return {
        "BLACK": "#000000",
        "WHITE": "#FFFFFF",
        "GREEN": "#00FF00",
        "RED": "#FF0000",
        "YELLOW": "#FFFF00",
        "BLUE": "#0080FF",
        "CYAN": "#00FFFF",
        "GRAY": "#808080",
        "DARK_GRAY": "#404040"
    }


@pytest.fixture
def carrier_bypass_tests():
    """Test data for carrier bypass validation"""
    return {
        "ttl_test": {
            "command": "ping -c 1 google.com",
            "expected_ttl": 65,
            "success_pattern": r"ttl=65"
        },
        "ipv6_test": {
            "command": "curl -6 https://ipv6.google.com",
            "expected_result": "failure",
            "failure_patterns": ["Couldn't connect", "Network unreachable"]
        },
        "dns_test": {
            "command": "nslookup google.com",
            "expected_server": "192.168.43.1",
            "success_pattern": r"Server:\s+192\.168\.43\.1"
        }
    }


@pytest.fixture
def error_scenarios():
    """Common error scenarios for testing"""
    return {
        "permission_denied": {
            "returncode": 1,
            "stderr": "Permission denied"
        },
        "command_not_found": {
            "returncode": 127,
            "stderr": "command not found"
        },
        "network_unreachable": {
            "returncode": 1,
            "stderr": "Network is unreachable"
        },
        "timeout": {
            "exception": "TimeoutExpired",
            "timeout": 30
        },
        "service_not_found": {
            "returncode": 5,
            "stderr": "Unit redsocks.service could not be found"
        }
    }


@pytest.fixture(scope="session")
def test_performance_data():
    """Performance benchmarks for testing"""
    return {
        "max_connection_time": 0.1,      # 100ms
        "max_state_transition_time": 0.001,  # 1ms
        "max_gui_update_time": 0.01,     # 10ms
        "max_bandwidth_calc_time": 0.1,  # 100ms
        "max_iptables_rule_time": 2.0,   # 2 seconds
        "max_memory_growth_mb": 10,      # 10MB
        "max_cpu_usage_percent": 50,     # 50%
        "max_fd_variance": 10            # 10 file descriptors
    }


# pytest hooks for custom test behavior
def pytest_configure(config):
    """Configure pytest with custom markers"""
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers", "performance: mark test as performance test"
    )
    config.addinivalue_line(
        "markers", "network: mark test as requiring network access"
    )
    config.addinivalue_line(
        "markers", "sudo: mark test as requiring sudo privileges"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection to skip certain tests based on environment"""
    skip_network = pytest.mark.skip(reason="Network tests disabled in CI")
    skip_sudo = pytest.mark.skip(reason="Sudo tests disabled in CI")

    # Skip network tests if running in CI or no network available
    if config.getoption("--no-network", default=False):
        for item in items:
            if "network" in item.keywords:
                item.add_marker(skip_network)

    # Skip sudo tests if not running as root or in CI
    if config.getoption("--no-sudo", default=False):
        for item in items:
            if "sudo" in item.keywords:
                item.add_marker(skip_sudo)


def pytest_addoption(parser):
    """Add custom command line options"""
    parser.addoption(
        "--no-network",
        action="store_true",
        default=False,
        help="Skip tests that require network access"
    )
    parser.addoption(
        "--no-sudo",
        action="store_true",
        default=False,
        help="Skip tests that require sudo privileges"
    )
    parser.addoption(
        "--performance",
        action="store_true",
        default=False,
        help="Run performance tests (may take longer)"
    )


# Custom assertion helpers
class PdaNetTestHelpers:
    """Helper methods for PdaNet-specific testing"""

    @staticmethod
    def assert_valid_connection_state(state):
        """Assert that state is a valid ConnectionState"""
        from connection_manager import ConnectionState
        assert state in ConnectionState, f"Invalid connection state: {state}"

    @staticmethod
    def assert_valid_interface_name(interface):
        """Assert that interface name follows expected patterns"""
        valid_patterns = ['usb0', 'wlan0', 'eth0', 'enp', 'wlp']
        assert any(interface.startswith(pattern) for pattern in valid_patterns), \
               f"Invalid interface name: {interface}"

    @staticmethod
    def assert_cyberpunk_color(color):
        """Assert that color follows cyberpunk theme"""
        cyberpunk_colors = ['#000000', '#00FF00', '#FF0000', '#FFFF00', '#FFFFFF']
        assert color.upper() in cyberpunk_colors, \
               f"Color {color} not in cyberpunk theme"

    @staticmethod
    def assert_no_emoji_in_text(text):
        """Assert that text contains no emoji characters"""
        import re
        emoji_pattern = re.compile(
            "["
            "\U0001F600-\U0001F64F"  # emoticons
            "\U0001F300-\U0001F5FF"  # symbols & pictographs
            "\U0001F680-\U0001F6FF"  # transport & map symbols
            "\U0001F1E0-\U0001F1FF"  # flags (iOS)
            "]+", flags=re.UNICODE)

        assert not emoji_pattern.search(text), \
               f"Text contains emoji (not allowed): {text}"


@pytest.fixture
def pdanet_helpers():
    """Fixture providing PdaNet test helpers"""
    return PdaNetTestHelpers()