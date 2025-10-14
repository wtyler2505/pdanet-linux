"""
PdaNet Linux - Configuration Manager
Handles settings, profiles, and persistent state
SECURITY HARDENED VERSION with advanced validation
"""

import ipaddress
import json
import os
from datetime import datetime
from pathlib import Path

# Support both package and direct module execution in tests
try:
    # When src is treated as a package (e.g., `src` on PYTHONPATH)
    from . import secret_store as secrets  # type: ignore
except Exception:  # pragma: no cover - fallback for direct module imports
    # When modules are imported directly from `src/` (tests add `src` to sys.path)
    import secret_store as secrets  # type: ignore

from config_validator import ConfigValidator

CONFIG_DIR = str(Path.home() / ".config" / "pdanet-linux")


def get_logger():
    """Compatibility shim used by legacy tests."""
    try:
        from logger import get_logger as _logger

        return _logger()
    except Exception:
        return None


class ConfigManager:
    # SECURITY FIX: Define allowed configuration keys and their types
    ALLOWED_CONFIG_KEYS = {
        "auto_start": bool,
        "start_minimized": bool,
        "auto_reconnect": bool,
        "reconnect_attempts": int,
        "reconnect_delay": int,
        "stealth_mode": bool,
        "stealth_level": int,
        "proxy_ip": str,
        "proxy_port": int,
        "connection_timeout": int,
        "status_update_interval": int,
        "enable_notifications": bool,
        "enable_logging": bool,
        "log_level": str,
        "theme": str,
        "window_width": int,
        "window_height": int,
        "single_instance": bool,
    }

    # SECURITY FIX: Define value constraints
    VALUE_CONSTRAINTS = {
        "stealth_level": (1, 3),  # min, max
        "proxy_port": (1, 65535),
        "reconnect_attempts": (1, 10),
        "reconnect_delay": (1, 300),
        "connection_timeout": (5, 300),
        "status_update_interval": (100, 10000),
        "window_width": (400, 3840),
        "window_height": (300, 2160),
        "log_level": ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        "theme": ["dark", "light"],
    }

    def __init__(self, config_dir=None):
        if config_dir is None:
            config_dir = Path(CONFIG_DIR)
        else:
            config_dir = Path(config_dir)

        self.config_dir = config_dir
        self.config_dir.mkdir(parents=True, exist_ok=True)

        self.config_file = self.config_dir / "config.json"
        self.profiles_file = self.config_dir / "profiles.json"
        self.state_file = self.config_dir / "state.json"
        self.wifi_networks_file = self.config_dir / "wifi_networks.json"
        
        # Initialize config validator
        self.validator = ConfigValidator(self.config_file)

        # Default configuration
        self.defaults = {
            "auto_start": False,
            "start_minimized": False,
            "auto_reconnect": True,
            "reconnect_attempts": 3,
            "reconnect_delay": 5,
            "stealth_mode": False,
            "stealth_level": 3,
            "proxy_ip": "192.168.49.1",
            "proxy_port": 8000,
            "connection_timeout": 30,
            "status_update_interval": 1000,  # milliseconds
            "enable_notifications": True,
            "enable_logging": True,
            "log_level": "INFO",
            "theme": "dark",
            "window_width": 900,
            "window_height": 600,
            "single_instance": True,
            "connection_mode": "wifi",
        }

        # Load or create config
        self.config = self.load_config()
        self.profiles = self.load_profiles()
        self.state = self.load_state()

    def _validate_proxy_ip(self, ip):
        """Validate IP address"""
        try:
            ipaddress.ip_address(ip)
            return True
        except ValueError:
            return False

    def _validate_config_value(self, key, value):
        """
        Validate configuration key and value
        SECURITY FIX: Prevents configuration injection attacks
        """
        # Check if key is allowed
        if key not in self.ALLOWED_CONFIG_KEYS:
            raise ValueError(f"Invalid configuration key: {key}")

        # Check type
        expected_type = self.ALLOWED_CONFIG_KEYS[key]
        if not isinstance(value, expected_type):
            raise TypeError(
                f"Invalid type for {key}: expected {expected_type.__name__}, got {type(value).__name__}"
            )

        # Check constraints
        if key in self.VALUE_CONSTRAINTS:
            constraint = self.VALUE_CONSTRAINTS[key]

            if isinstance(constraint, tuple):  # Range constraint
                min_val, max_val = constraint
                if not (min_val <= value <= max_val):
                    raise ValueError(f"{key} must be between {min_val} and {max_val}")

            elif isinstance(constraint, list):  # Enum constraint
                if value not in constraint:
                    raise ValueError(f"{key} must be one of {constraint}")

        # Special validation for proxy_ip
        if key == "proxy_ip" and not self._validate_proxy_ip(value):
            raise ValueError(f"Invalid IP address: {value}")

        return True

    def load_config(self):
        """Load configuration from file with enhanced validation"""
        if self.config_file.exists():
            try:
                with open(self.config_file) as f:
                    raw_config = json.load(f)
                
                # Verify integrity if available
                integrity_ok = self.validator.verify_integrity(raw_config.copy())
                if not integrity_ok:
                    logger = get_logger()
                    if logger:
                        logger.warning("Config integrity check failed - possible corruption or tampering")
                
                # Validate and fix configuration
                fixed_config, warnings = self.validator.validate_and_fix_config(raw_config)
                
                # Log any warnings
                logger = get_logger()
                if logger and warnings:
                    for warning in warnings:
                        logger.warning(f"Config validation: {warning}")
                
                # If fixes were applied, save the corrected config
                if warnings:
                    self.config = fixed_config
                    self.save_config()
                    return fixed_config
                
                return fixed_config
                
            except Exception as e:
                logger = get_logger()
                if logger:
                    logger.error(f"Error loading config: {e}")
                
                # Create backup of corrupted config
                try:
                    corrupted_backup = self.config_file.with_suffix('.corrupted.json')
                    self.config_file.rename(corrupted_backup)
                    if logger:
                        logger.info(f"Corrupted config backed up to: {corrupted_backup}")
                except:
                    pass
                
                # Return defaults
                return self.validator.get_default_config()
        else:
            # First run - create default config
            return self.validator.get_default_config()

    def save_config(self):
        """Save configuration to file with validation and backup"""
        try:
            # Validate config before saving
            is_valid, errors = self.validator.validate_config(self.config)
            
            logger = get_logger()
            if not is_valid:
                if logger:
                    logger.warning(f"Attempting to save invalid config. Errors: {errors}")
                
                # Try to fix errors automatically
                fixed_config, warnings = self.validator.validate_and_fix_config(self.config)
                self.config = fixed_config
                
                if logger and warnings:
                    for warning in warnings:
                        logger.warning(f"Config auto-fix: {warning}")
            
            # Create backup before saving
            if self.config_file.exists():
                try:
                    backup_path = self.validator.create_backup(self.config)
                    if logger:
                        logger.debug(f"Config backup created: {backup_path}")
                except Exception as e:
                    if logger:
                        logger.warning(f"Failed to create config backup: {e}")
            
            # Add integrity hash and update metadata
            config_to_save = self.config.copy()
            config_to_save['last_updated'] = datetime.now().isoformat()
            config_with_integrity = self.validator.add_integrity_hash(config_to_save)
            
            # Save with atomic write
            temp_file = self.config_file.with_suffix('.tmp')
            with open(temp_file, "w") as f:
                json.dump(config_with_integrity, f, indent=2)
            
            # Atomic rename
            temp_file.rename(self.config_file)
            
            if logger:
                logger.debug("Configuration saved successfully with integrity protection")
            return True
            
        except Exception as e:
            logger = get_logger()
            if logger:
                logger.error(f"Error saving config: {e}")
            
            # Clean up temp file if it exists
            temp_file = self.config_file.with_suffix('.tmp')
            if temp_file.exists():
                temp_file.unlink()
            
            return False

    # Compatibility alias for older integrations/tests
    def save(self):
        return self.save_config()

    def get(self, key, default=None):
        """Get configuration value"""
        return self.config.get(key, default)

    def set(self, key, value):
        """
        Set configuration value and save
        SECURITY FIX: Validates all inputs before saving
        """
        self._validate_config_value(key, value)
        self.config[key] = value
        self.save_config()

    def reset_to_defaults(self):
        """Reset configuration to defaults"""
        self.config = self.defaults.copy()
        self.save_config()

    # Profile Management
    def load_profiles(self):
        """Load connection profiles"""
        if self.profiles_file.exists():
            try:
                with open(self.profiles_file) as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading profiles: {e}")
                return {}
        return {}

    def save_profiles(self):
        """Save profiles to file"""
        try:
            with open(self.profiles_file, "w") as f:
                json.dump(self.profiles, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving profiles: {e}")
            return False

    def add_profile(self, name, settings=None):
        """Add or update a connection profile (compatibility wrapper)."""
        if isinstance(name, dict):
            profile = name.copy()
            profile_name = profile.pop("name", None)
            if not profile_name:
                raise ValueError("Profile dictionary must include a 'name' key")
            settings = profile
        else:
            profile_name = name
            if settings is None:
                raise ValueError("Profile settings are required")

        # Validate profile settings
        for key, value in settings.items():
            if key in self.ALLOWED_CONFIG_KEYS:
                self._validate_config_value(key, value)

        self.profiles[profile_name] = {"created": datetime.now().isoformat(), "settings": settings}
        self.save_profiles()

    def delete_profile(self, name):
        """Delete a profile"""
        if name in self.profiles:
            del self.profiles[name]
            self.save_profiles()
            return True
        return False

    def get_profile(self, name):
        """Get profile settings"""
        if name in self.profiles:
            return self.profiles[name]["settings"]
        return None

    def list_profiles(self):
        """List all profile names"""
        return list(self.profiles.keys())

    # Compatibility helper for older tests
    def get_profiles(self):
        profiles = []
        for name, payload in self.profiles.items():
            data = {"name": name}
            data.update(payload.get("settings", {}))
            profiles.append(data)
        return profiles

    # State Management (for remembering last connection, etc.)
    def load_state(self):
        """Load application state"""
        if self.state_file.exists():
            try:
                with open(self.state_file) as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading state: {e}")
                return {}
        return {}

    def save_state(self):
        """Save application state"""
        try:
            with open(self.state_file, "w") as f:
                json.dump(self.state, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving state: {e}")
            return False

    def set_state(self, key, value):
        """Set state value"""
        self.state[key] = value
        self.save_state()

    def get_state(self, key, default=None):
        """Get state value"""
        return self.state.get(key, default)

    # Auto-start management
    def get_autostart_file(self):
        """Get path to autostart desktop file"""
        autostart_dir = Path.home() / ".config" / "autostart"
        autostart_dir.mkdir(parents=True, exist_ok=True)
        return autostart_dir / "pdanet-linux.desktop"

    def enable_autostart(self):
        """Enable auto-start on boot"""
        desktop_content = """[Desktop Entry]
Version=1.0
Type=Application
Name=PdaNet Linux
Comment=PdaNet USB Tethering
Exec=/usr/local/bin/pdanet-gui-v2 --start-minimized
Icon=network-wireless
Terminal=false
Categories=Network;
X-GNOME-Autostart-enabled=true
"""
        try:
            autostart_file = self.get_autostart_file()
            with open(autostart_file, "w") as f:
                f.write(desktop_content)
            os.chmod(autostart_file, 0o755)
            self.set("auto_start", True)
            return True
        except Exception as e:
            print(f"Error enabling autostart: {e}")
            return False

    def disable_autostart(self):
        """Disable auto-start on boot"""
        try:
            autostart_file = self.get_autostart_file()
            if autostart_file.exists():
                autostart_file.unlink()
            self.set("auto_start", False)
            return True
        except Exception as e:
            print(f"Error disabling autostart: {e}")
            return False

    def is_autostart_enabled(self):
        """Check if autostart is enabled"""
        return self.get_autostart_file().exists()

    def load_wifi_networks(self):
        """Load saved WiFi networks"""
        try:
            if self.wifi_networks_file.exists():
                with open(self.wifi_networks_file) as f:
                    return json.load(f)
            return {}
        except Exception:
            return {}

    def save_wifi_networks(self, networks):
        """Save WiFi networks with passwords"""
        try:
            with open(self.wifi_networks_file, "w") as f:
                json.dump(networks, f, indent=2)
            # Set restrictive permissions (600 - owner read/write only)
            os.chmod(self.wifi_networks_file, 0o600)
        except Exception as e:
            print(f"Failed to save WiFi networks: {e}")

    def save_wifi_network(self, ssid, password):
        """Save a single WiFi network"""
        # Prefer secure storage when available
        stored_securely = False
        try:
            if secrets.is_available():
                stored_securely = secrets.set_wifi_password(ssid, password)
        except Exception:
            stored_securely = False

        networks = self.load_wifi_networks()
        entry = {"last_used": datetime.now().isoformat()}
        # Only persist plaintext if secure storage unavailable
        if not stored_securely:
            entry["password"] = password
        networks[ssid] = entry
        self.save_wifi_networks(networks)

    def get_wifi_password(self, ssid) -> str | None:
        """Get saved password for SSID (keyring preferred)."""
        try:
            if secrets.is_available():
                secret = secrets.get_wifi_password(ssid)
                if secret:
                    return secret
        except Exception:
            pass
        networks = self.load_wifi_networks()
        if ssid in networks:
            return networks[ssid].get("password")
        return None

    def delete_wifi_network(self, ssid):
        """Delete a saved WiFi network"""
        try:
            if secrets.is_available():
                secrets.delete_wifi_password(ssid)
        except Exception:
            pass
        networks = self.load_wifi_networks()
        if ssid in networks:
            del networks[ssid]
            self.save_wifi_networks(networks)

    def list_saved_wifi_networks(self):
        """Get list of saved WiFi SSIDs"""
        networks = self.load_wifi_networks()
        # Sort by last used, most recent first
        sorted_networks = sorted(
            networks.items(), key=lambda x: x[1].get("last_used", ""), reverse=True
        )
        return [ssid for ssid, _ in sorted_networks]


# Global config instance
_config_instance = None


def get_config():
    """Get or create global config instance"""
    global _config_instance
    if _config_instance is None:
        _config_instance = ConfigManager()
    return _config_instance
