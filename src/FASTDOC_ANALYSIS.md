# src - Code Documentation

## Project Summary

- **Total Files**: 18
- **Total Lines**: 1,205
- **Total Classes**: 8
- **Total Functions**: 19
- **Total Methods**: 52

## Dependencies

- `asyncio`
- `collections`
- `concurrent.futures`
- `config_manager`
- `connection_manager`
- `contextlib`
- `dataclasses`
- `datetime`
- `enum`
- `fcntl`
- `functools`
- `gc`
- `gi`
- `gi.repository`
- `input_validators`
- `ipaddress`
- `iptc`
- `json`
- `keyring`
- `logger`
... and 19 more

## Modules


### process_utils.py

Process utilities: centralized subprocess helpers with consistent timeouts and logging.
Migration target: replace scattered subprocess.run calls with run_cmd for uniform behavior.

**Lines**: 23

#### Functions

##### `run_cmd(argv, timeout, text)`

Run a command safely; return (code, stdout, stderr).

- No shell=True usage.
- Enforces timeout.


### secret_store.py

Secret storage abstraction for PdaNet Linux.
Uses system keyring (Secret Service/libsecret) when available, with JSON fallback handled in ConfigManager.

**Lines**: 44

#### Functions

##### `is_available()`

##### `set_wifi_password(ssid, password)`

##### `get_wifi_password(ssid)`

##### `delete_wifi_password(ssid)`


### input_validators.py

Input Validation Module for PdaNet Linux
SECURITY: Prevents command injection and validates user inputs

Addresses Audit Issues:
- #292: Command injection via SSID/password
- #58-59: Inadequate input validation
- #72-75: Unsafe parsing and validation

**Lines**: 328

#### Classes

##### `ValidationError`

Raised when input validation fails

#### Functions

##### `validate_ssid(ssid, allow_empty)`

Validate WiFi SSID for safety

Args:
    ssid: The SSID to validate
    allow_empty: Whether to allow empty SSID
    
Returns:
    The validated SSID (unchanged)
    
Raises:
    ValidationError: If SSID is invalid

##### `validate_password(password, allow_empty, min_length)`

Validate WiFi password for safety

Args:
    password: The password to validate
    allow_empty: Whether to allow empty password
    min_length: Minimum password length (WPA2 requires 8)
    
Returns:
    The validated password (unchanged)
    
Raises:
    ValidationError: If password is invalid

##### `validate_ip_address(ip, allow_private)`

Validate IP address

Args:
    ip: IP address string
    allow_private: Whether to allow private/internal IPs
    
Returns:
    The validated IP (unchanged)
    
Raises:
    ValidationError: If IP is invalid

##### `validate_port(port)`

Validate network port number

Args:
    port: Port number (int or string)
    
Returns:
    The validated port as int
    
Raises:
    ValidationError: If port is invalid

##### `validate_hostname(hostname)`

Validate hostname (RFC 1123)

Args:
    hostname: Hostname to validate
    
Returns:
    The validated hostname (unchanged)
    
Raises:
    ValidationError: If hostname is invalid

##### `validate_interface_name(interface)`

Validate network interface name

Args:
    interface: Interface name (e.g., 'eth0', 'wlan0')
    
Returns:
    The validated interface name
    
Raises:
    ValidationError: If interface name is invalid

##### `validate_path(path, must_be_absolute)`

Validate file path for safety

Args:
    path: File path to validate
    must_be_absolute: Whether path must be absolute
    
Returns:
    The validated path
    
Raises:
    ValidationError: If path is invalid

##### `sanitize_for_shell(value)`

Escape a string for safe shell usage (last resort - prefer list args)

WARNING: This should NOT be used as primary defense.
Always use subprocess with list args instead of shell=True.
This is only for edge cases where shell escaping is unavoidable.

Args:
    value: String to escape
    
Returns:
    Shell-escaped string

##### `validate_subprocess_args(args)`

Validate subprocess arguments for safety

Args:
    args: List of command arguments
    
Returns:
    The validated args list
    
Raises:
    ValidationError: If args are invalid


### iptables_manager.py

Optional iptables management using python-iptables (iptc). Fallback remains shell scripts.

**Lines**: 25

#### Functions

##### `available()`

##### `ensure_chain(table_name, chain_name)`


### nm_client.py

NetworkManager D-Bus client for robust network management.
Replaces fragile nmcli string parsing with proper D-Bus API calls.

**Lines**: 282

#### Classes

##### `NetworkDevice`

Represents a network device with its properties

**Methods**:
- `__init__(self, path, device_type, interface, state)`
- `type_name(self)`
- `state_name(self)`
- `is_connected(self)`

##### `AccessPoint`

Represents a WiFi access point

**Methods**:
- `__init__(self, ssid, signal_strength, security, frequency)`
- `is_secured(self)`
- `security_string(self)`

##### `NMClient`

Robust NetworkManager D-Bus client

**Methods**:
- `__init__(self)`
- `available(self)`: Check if NetworkManager D-Bus is available.
- `get_devices(self)`: Get all network devices.
- `get_wifi_devices(self)`: Get all WiFi devices.
- `get_connected_wifi_device(self)`: Get the currently connected WiFi device.
- `get_active_interface(self, device_type)`: Get active interface name by device type.
- `scan_wifi_networks(self, device_interface, force_rescan)`: Scan for available WiFi networks with caching.
- `get_connection_status(self)`: Get comprehensive connection status.


### config_manager_old.py

PdaNet Linux - Configuration Manager
Handles settings, profiles, and persistent state

**Lines**: 227

#### Classes

##### `ConfigManager`

**Methods**:
- `__init__(self, config_dir)`
- `load_config(self)`: Load configuration from file or create defaults.
- `save_config(self)`: Save configuration to file.
- `get(self, key, default)`: Get configuration value.
- `set(self, key, value)`: Set configuration value and save.
- `reset_to_defaults(self)`: Reset configuration to defaults.
- `load_profiles(self)`: Load connection profiles.
- `save_profiles(self)`: Save profiles to file.
- `add_profile(self, name, settings)`: Add or update a connection profile.
- `delete_profile(self, name)`: Delete a profile.
- `get_profile(self, name)`: Get profile settings.
- `list_profiles(self)`: List all profile names.
- `load_state(self)`: Load application state.
- `save_state(self)`: Save application state.
- `set_state(self, key, value)`: Set state value.
- `get_state(self, key, default)`: Get state value.
- `get_autostart_file(self)`: Get path to autostart desktop file.
- `enable_autostart(self)`: Enable auto-start on boot.
- `disable_autostart(self)`: Disable auto-start on boot.
- `is_autostart_enabled(self)`: Check if autostart is enabled.

#### Functions

##### `get_config()`

Get or create global config instance


### logger.py

PdaNet Linux - Logging System
Rotating log files with multiple severity levels

**Lines**: 238

#### Classes

##### `PdaNetLogger`

**Methods**:
- `__init__(self, log_dir, log_level)`: Initialize logger with configurable log level

Args:
    log_dir: Directory for log files (optional)
    log_level: Initial log level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
- `debug(self, message)`: Debug level message.
- `info(self, message)`: Info level message.
- `ok(self, message)`: Success message (shown as OK in GUI).
- `warning(self, message)`: Warning level message.
- `error(self, message)`: Error level message.
- `critical(self, message)`: Critical level message.
- `_add_to_buffer(self, level, message)`: Add entry to circular buffer for GUI display.
- `set_log_level(self, level_str)`: Set logging level dynamically
Issue #131: Apply config log level without restart

Args:
    level_str: Log level string (DEBUG, INFO, WARNING, ERROR, CRITICAL).
- `get_log_level(self)`: Get current console log level as string.
- `get_recent_logs(self, count)`: Get recent log entries for GUI display.
- `get_all_logs(self)`: Get all buffered logs.
- `clear_buffer(self)`: Clear the log buffer.
- `format_log_entry(self, entry)`: Format log entry for GUI display.
- `get_log_file_path(self)`: Get path to log file.
- `read_log_file(self, lines)`: Read last N lines from log file.

#### Functions

##### `get_logger(log_level)`

Get or create global logger instance

Args:
    log_level: Optional log level to set (DEBUG, INFO, WARNING, ERROR, CRITICAL)
              If None and logger exists, keeps current level
              If None and logger doesn't exist, tries to read from config


### gi/__init__.py

Minimal stub for `gi` to support tests without system GTK bindings.
Provides a `repository` namespace with attributes that tests patch.
This avoids hard dependency on PyGObject in CI/sandboxed environments.

**Lines**: 38

#### Classes

##### `_Indicator`

**Methods**:
- `new()`

##### `AppIndicator3`

#### Functions

##### `require_version(_lib, _ver)`

No-op version requirement for stubbed gi.

