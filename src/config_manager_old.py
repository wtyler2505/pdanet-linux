"""
PdaNet Linux - Configuration Manager
Handles settings, profiles, and persistent state
"""

import json
import os
from datetime import datetime
from pathlib import Path


class ConfigManager:
    def __init__(self, config_dir=None):
        if config_dir is None:
            config_dir = Path.home() / ".config" / "pdanet-linux"
        else:
            config_dir = Path(config_dir)

        self.config_dir = config_dir
        self.config_dir.mkdir(parents=True, exist_ok=True)

        self.config_file = self.config_dir / "config.json"
        self.profiles_file = self.config_dir / "profiles.json"
        self.state_file = self.config_dir / "state.json"

        # Default configuration
        self.defaults = {
            "auto_start": False,
            "start_minimized": False,
            "auto_reconnect": False,
            "reconnect_attempts": 3,
            "reconnect_delay": 5,
            "stealth_mode": False,
            "stealth_level": 2,
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
        }

        # Load or create config
        self.config = self.load_config()
        self.profiles = self.load_profiles()
        self.state = self.load_state()

    def load_config(self):
        """Load configuration from file or create defaults"""
        if self.config_file.exists():
            try:
                with open(self.config_file) as f:
                    config = json.load(f)
                    # Merge with defaults (add any new keys)
                    for key, value in self.defaults.items():
                        if key not in config:
                            config[key] = value
                    return config
            except Exception as e:
                print(f"Error loading config: {e}")
                return self.defaults.copy()
        else:
            return self.defaults.copy()

    def save_config(self):
        """Save configuration to file"""
        try:
            with open(self.config_file, "w") as f:
                json.dump(self.config, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving config: {e}")
            return False

    def get(self, key, default=None):
        """Get configuration value"""
        return self.config.get(key, default)

    def set(self, key, value):
        """Set configuration value and save"""
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

    def add_profile(self, name, settings):
        """Add or update a connection profile"""
        self.profiles[name] = {"created": datetime.now().isoformat(), "settings": settings}
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
Exec=/usr/local/bin/pdanet-gui --start-minimized
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


# Global config instance
_config_instance = None


def get_config():
    """Get or create global config instance"""
    global _config_instance
    if _config_instance is None:
        _config_instance = ConfigManager()
    return _config_instance
