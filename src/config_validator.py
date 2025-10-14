"""
Configuration Validation for PdaNet Linux
JSON schema validation, integrity checking, and migration system
"""

import json
import hashlib
import hmac
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

from logger import get_logger


class ConfigValidator:
    """
    Configuration validation and integrity system
    Implements JSON schema validation, backup system, and migration
    """
    
    # Configuration schema definition
    SCHEMA = {
        "type": "object",
        "properties": {
            # Connection settings
            "proxy_host": {"type": "string", "pattern": r"^(\d{1,3}\.){3}\d{1,3}$"},
            "proxy_port": {"type": "integer", "minimum": 1, "maximum": 65535},
            "connection_timeout": {"type": "integer", "minimum": 5, "maximum": 300},
            "auto_reconnect": {"type": "boolean"},
            "max_reconnect_attempts": {"type": "integer", "minimum": 1, "maximum": 20},
            "reconnect_delay": {"type": "integer", "minimum": 1, "maximum": 60},
            
            # Stealth settings
            "stealth_level": {"type": "integer", "minimum": 1, "maximum": 5},
            "bypass_dns_blocking": {"type": "boolean"},
            "bypass_throttling": {"type": "boolean"},
            "traffic_obfuscation": {"type": "boolean"},
            "ttl_modification": {"type": "boolean"},
            "ipv6_blocking": {"type": "boolean"},
            "custom_ttl": {"type": "integer", "minimum": 1, "maximum": 255},
            "dns_servers": {"type": "array", "items": {"type": "string"}},
            
            # Interface settings
            "window_width": {"type": "integer", "minimum": 700, "maximum": 3000},
            "window_height": {"type": "integer", "minimum": 400, "maximum": 2000},
            "theme": {"type": "string", "enum": ["dark", "light", "cyberpunk"]},
            "update_interval_ms": {"type": "integer", "minimum": 100, "maximum": 10000},
            "notifications_enabled": {"type": "boolean"},
            "minimize_to_tray": {"type": "boolean"},
            "start_minimized": {"type": "boolean"},
            
            # Data usage
            "data_warning_mb": {"type": "integer", "minimum": 0, "maximum": 1000000},
            "data_limit_mb": {"type": "integer", "minimum": 0, "maximum": 1000000},
            "reset_data_monthly": {"type": "boolean"},
            
            # Logging
            "log_level": {"type": "string", "enum": ["DEBUG", "INFO", "WARNING", "ERROR"]},
            "max_log_files": {"type": "integer", "minimum": 1, "maximum": 100},
            "max_log_size_mb": {"type": "integer", "minimum": 1, "maximum": 1000},
            "enable_file_logging": {"type": "boolean"},
            
            # Advanced features  
            "enable_advanced_monitoring": {"type": "boolean"},
            "enable_qos": {"type": "boolean"},
            "performance_optimization": {"type": "boolean"},
            "intelligent_bandwidth_management": {"type": "boolean"},
            
            # Meta information
            "config_version": {"type": "string"},
            "first_run": {"type": "boolean"},
            "last_updated": {"type": "string"},
            "created": {"type": "string"}
        },
        "additionalProperties": True  # Allow custom user settings
    }
    
    # Default configuration values
    DEFAULTS = {
        "proxy_host": "192.168.49.1",
        "proxy_port": 8000,
        "connection_timeout": 30,
        "auto_reconnect": False,
        "max_reconnect_attempts": 3,
        "reconnect_delay": 5,
        
        "stealth_level": 3,
        "bypass_dns_blocking": True,
        "bypass_throttling": True,
        "traffic_obfuscation": True,
        "ttl_modification": True,
        "ipv6_blocking": True,
        "custom_ttl": 64,
        "dns_servers": ["1.1.1.1", "8.8.8.8"],
        
        "window_width": 900,
        "window_height": 600,
        "theme": "cyberpunk",
        "update_interval_ms": 1000,
        "notifications_enabled": True,
        "minimize_to_tray": True,
        "start_minimized": False,
        
        "data_warning_mb": 1000,
        "data_limit_mb": 2000,
        "reset_data_monthly": True,
        
        "log_level": "INFO",
        "max_log_files": 10,
        "max_log_size_mb": 10,
        "enable_file_logging": True,
        
        "enable_advanced_monitoring": True,
        "enable_qos": False,
        "performance_optimization": True,
        "intelligent_bandwidth_management": True,
        
        "config_version": "2.0",
        "first_run": True,
        "last_updated": datetime.now().isoformat(),
        "created": datetime.now().isoformat()
    }
    
    def __init__(self, config_path: Path = None):
        """Initialize config validator"""
        self.logger = get_logger()
        
        if config_path is None:
            # Default config path
            config_dir = Path.home() / ".config" / "pdanet"
            config_dir.mkdir(parents=True, exist_ok=True)
            config_path = config_dir / "config.json"
        
        self.config_path = Path(config_path)
        self.backup_dir = self.config_path.parent / "backups"
        self.backup_dir.mkdir(exist_ok=True)
        
        # HMAC secret for integrity checking (stored separately)
        self.secret_path = self.config_path.parent / ".integrity"
        self._ensure_secret()
    
    def _ensure_secret(self):
        """Ensure integrity secret exists"""
        if not self.secret_path.exists():
            # Generate random secret
            secret = os.urandom(32)
            with open(self.secret_path, 'wb') as f:
                f.write(secret)
            os.chmod(self.secret_path, 0o600)  # Secure permissions
    
    def _get_secret(self) -> bytes:
        """Get integrity secret"""
        with open(self.secret_path, 'rb') as f:
            return f.read()
    
    def _calculate_integrity_hash(self, config_data: Dict[str, Any]) -> str:
        """Calculate HMAC integrity hash for config"""
        secret = self._get_secret()
        config_json = json.dumps(config_data, sort_keys=True, separators=(',', ':'))
        return hmac.new(secret, config_json.encode(), hashlib.sha256).hexdigest()
    
    def validate_config(self, config_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate configuration against schema
        
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        try:
            # Check required properties and types
            for key, schema_def in self.SCHEMA["properties"].items():
                if key in config_data:
                    value = config_data[key]
                    
                    # Type validation
                    expected_type = schema_def.get("type")
                    if expected_type:
                        if not self._validate_type(value, expected_type):
                            errors.append(f"'{key}': expected {expected_type}, got {type(value).__name__}")
                            continue
                    
                    # Range validation for integers
                    if expected_type == "integer":
                        minimum = schema_def.get("minimum")
                        maximum = schema_def.get("maximum")
                        if minimum is not None and value < minimum:
                            errors.append(f"'{key}': {value} is below minimum {minimum}")
                        if maximum is not None and value > maximum:
                            errors.append(f"'{key}': {value} is above maximum {maximum}")
                    
                    # Pattern validation for strings
                    if expected_type == "string" and "pattern" in schema_def:
                        import re
                        pattern = schema_def["pattern"]
                        if not re.match(pattern, value):
                            errors.append(f"'{key}': '{value}' does not match pattern {pattern}")
                    
                    # Enum validation
                    if "enum" in schema_def:
                        if value not in schema_def["enum"]:
                            errors.append(f"'{key}': '{value}' not in allowed values {schema_def['enum']}")
                    
                    # Array item validation
                    if expected_type == "array" and "items" in schema_def:
                        item_type = schema_def["items"].get("type")
                        if item_type:
                            for i, item in enumerate(value):
                                if not self._validate_type(item, item_type):
                                    errors.append(f"'{key}[{i}]': expected {item_type}, got {type(item).__name__}")
            
            # Custom validation rules
            custom_errors = self._custom_validation(config_data)
            errors.extend(custom_errors)
            
        except Exception as e:
            errors.append(f"Validation error: {e}")
        
        return len(errors) == 0, errors
    
    def _validate_type(self, value: Any, expected_type: str) -> bool:
        """Validate value type against expected type"""
        if expected_type == "string":
            return isinstance(value, str)
        elif expected_type == "integer":
            return isinstance(value, int) and not isinstance(value, bool)
        elif expected_type == "boolean":
            return isinstance(value, bool)
        elif expected_type == "array":
            return isinstance(value, list)
        elif expected_type == "object":
            return isinstance(value, dict)
        return True
    
    def _custom_validation(self, config_data: Dict[str, Any]) -> List[str]:
        """Custom validation rules"""
        errors = []
        
        # Data limit should be higher than warning
        warning = config_data.get("data_warning_mb", 0)
        limit = config_data.get("data_limit_mb", 0)
        if warning > 0 and limit > 0 and warning >= limit:
            errors.append("data_warning_mb should be less than data_limit_mb")
        
        # Port validation
        proxy_port = config_data.get("proxy_port")
        if proxy_port and proxy_port in [22, 80, 443, 53, 25]:
            errors.append("proxy_port should not use common system ports (22, 80, 443, 53, 25)")
        
        # DNS servers validation
        dns_servers = config_data.get("dns_servers", [])
        for dns in dns_servers:
            if not self._is_valid_ip(dns):
                errors.append(f"Invalid DNS server IP: {dns}")
        
        return errors
    
    def _is_valid_ip(self, ip: str) -> bool:
        """Validate IP address format"""
        import ipaddress
        try:
            ipaddress.ip_address(ip)
            return True
        except ValueError:
            return False
    
    def create_backup(self, config_data: Dict[str, Any]) -> Path:
        """Create backup of configuration"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"config_backup_{timestamp}.json"
        backup_path = self.backup_dir / backup_name
        
        # Add integrity hash to backup
        backup_data = {
            "config": config_data,
            "integrity_hash": self._calculate_integrity_hash(config_data),
            "backup_timestamp": timestamp,
            "original_path": str(self.config_path)
        }
        
        with open(backup_path, 'w') as f:
            json.dump(backup_data, f, indent=2)
        
        self.logger.info(f"Config backup created: {backup_path}")
        
        # Clean up old backups (keep last 10)
        self._cleanup_old_backups()
        
        return backup_path
    
    def _cleanup_old_backups(self):
        """Clean up old backup files, keeping the last 10"""
        try:
            backups = sorted(
                self.backup_dir.glob("config_backup_*.json"),
                key=lambda p: p.stat().st_mtime,
                reverse=True
            )
            
            # Keep only the 10 most recent backups
            for old_backup in backups[10:]:
                old_backup.unlink()
                self.logger.debug(f"Removed old backup: {old_backup}")
                
        except Exception as e:
            self.logger.warning(f"Failed to cleanup old backups: {e}")
    
    def verify_integrity(self, config_data: Dict[str, Any]) -> bool:
        """Verify configuration integrity using HMAC"""
        try:
            # Check if config has stored integrity hash
            if "_integrity_hash" in config_data:
                stored_hash = config_data.pop("_integrity_hash")
                calculated_hash = self._calculate_integrity_hash(config_data)
                return hmac.compare_digest(stored_hash, calculated_hash)
            
            # No integrity hash found (first time or old config)
            return True
            
        except Exception as e:
            self.logger.warning(f"Integrity verification failed: {e}")
            return False
    
    def add_integrity_hash(self, config_data: Dict[str, Any]) -> Dict[str, Any]:
        """Add integrity hash to configuration"""
        config_copy = config_data.copy()
        integrity_hash = self._calculate_integrity_hash(config_copy)
        config_copy["_integrity_hash"] = integrity_hash
        return config_copy
    
    def migrate_config(self, config_data: Dict[str, Any]) -> Dict[str, Any]:
        """Migrate old configuration to current version"""
        current_version = config_data.get("config_version", "1.0")
        migrated_data = config_data.copy()
        
        if current_version == "1.0":
            # Migrate from v1.0 to v2.0
            self.logger.info("Migrating config from v1.0 to v2.0")
            
            # Add new fields with defaults
            for key, default_value in self.DEFAULTS.items():
                if key not in migrated_data:
                    migrated_data[key] = default_value
            
            # Migrate renamed fields
            if "log_to_file" in migrated_data:
                migrated_data["enable_file_logging"] = migrated_data.pop("log_to_file")
            
            if "auto_start" in migrated_data:
                migrated_data["start_minimized"] = migrated_data.pop("auto_start")
            
            migrated_data["config_version"] = "2.0"
            migrated_data["last_updated"] = datetime.now().isoformat()
        
        return migrated_data
    
    def get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""
        return self.DEFAULTS.copy()
    
    def validate_and_fix_config(self, config_data: Dict[str, Any]) -> Tuple[Dict[str, Any], List[str]]:
        """
        Validate configuration and fix issues where possible
        
        Returns:
            Tuple of (fixed_config, list_of_warnings)
        """
        warnings = []
        fixed_config = config_data.copy()
        
        # First, migrate if needed
        if fixed_config.get("config_version", "1.0") != self.DEFAULTS["config_version"]:
            fixed_config = self.migrate_config(fixed_config)
            warnings.append("Configuration migrated to current version")
        
        # Add missing required fields with defaults
        for key, default_value in self.DEFAULTS.items():
            if key not in fixed_config:
                fixed_config[key] = default_value
                warnings.append(f"Added missing field '{key}' with default value")
        
        # Validate and fix values
        is_valid, errors = self.validate_config(fixed_config)
        
        if not is_valid:
            # Try to fix validation errors
            for error in errors:
                if "expected integer, got" in error:
                    key = error.split("'")[1]
                    try:
                        fixed_config[key] = int(fixed_config[key])
                        warnings.append(f"Converted '{key}' to integer")
                    except (ValueError, TypeError):
                        fixed_config[key] = self.DEFAULTS.get(key, 0)
                        warnings.append(f"Reset '{key}' to default due to invalid value")
                
                elif "expected boolean, got" in error:
                    key = error.split("'")[1]
                    try:
                        if isinstance(fixed_config[key], str):
                            fixed_config[key] = fixed_config[key].lower() in ('true', '1', 'yes')
                        else:
                            fixed_config[key] = bool(fixed_config[key])
                        warnings.append(f"Converted '{key}' to boolean")
                    except:
                        fixed_config[key] = self.DEFAULTS.get(key, False)
                        warnings.append(f"Reset '{key}' to default due to invalid value")
                
                elif "is below minimum" in error or "is above maximum" in error:
                    key = error.split("'")[1]
                    fixed_config[key] = self.DEFAULTS.get(key, 0)
                    warnings.append(f"Reset '{key}' to default due to out-of-range value")
                
                elif "not in allowed values" in error:
                    key = error.split("'")[1]
                    fixed_config[key] = self.DEFAULTS.get(key, "")
                    warnings.append(f"Reset '{key}' to default due to invalid enum value")
        
        return fixed_config, warnings


def get_config_validator(config_path: Path = None) -> ConfigValidator:
    """Get or create global config validator instance"""
    global _validator_instance
    if '_validator_instance' not in globals():
        _validator_instance = ConfigValidator(config_path)
    return _validator_instance