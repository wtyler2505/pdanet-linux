#!/usr/bin/env python3
"""
Configuration Management System for AI-Enhanced PDanet-Linux

Provides centralized configuration management with environment-specific settings,
validation, and dynamic updates. Supports multiple configuration sources including
environment variables, configuration files, and runtime overrides.
"""

import os
import json
import yaml
from pathlib import Path
from typing import Dict, Any, Optional, Union, List
from dataclasses import dataclass, field
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

@dataclass
class DatabaseConfig:
    """Database configuration settings"""
    host: str = "localhost"
    port: int = 5432
    database: str = "pdanet_ai"
    username: str = "pdanet_user"
    password: str = ""
    pool_size: int = 10
    max_overflow: int = 20
    pool_timeout: int = 30

@dataclass
class RedisConfig:
    """Redis configuration settings"""
    host: str = "localhost"
    port: int = 6379
    database: int = 0
    password: Optional[str] = None
    max_connections: int = 100
    socket_timeout: int = 5

@dataclass
class MLConfig:
    """Machine Learning model configuration"""
    models_dir: str = "ml_models"
    data_dir: str = "data"
    batch_size: int = 32
    learning_rate: float = 0.001
    max_epochs: int = 100
    early_stopping_patience: int = 10
    model_checkpoint_interval: int = 10
    enable_gpu: bool = True
    device: str = "auto"  # auto, cpu, cuda

@dataclass
class NetworkConfig:
    """Network monitoring and optimization configuration"""
    default_interface: str = "tun0"
    monitoring_interval: int = 5  # seconds
    optimization_interval: int = 30  # seconds
    max_connections: int = 1000
    connection_timeout: int = 30
    read_timeout: int = 60
    write_timeout: int = 30
    enable_ipv6: bool = False
    buffer_size: int = 8192

@dataclass
class SecurityConfig:
    """Security monitoring configuration"""
    enable_monitoring: bool = True
    threat_detection_threshold: float = 0.7
    auto_response_enabled: bool = True
    max_threat_response_actions: int = 5
    security_log_retention_days: int = 30
    enable_forensic_capture: bool = True
    whitelist_ips: List[str] = field(default_factory=list)
    blacklist_ips: List[str] = field(default_factory=list)

@dataclass
class APIConfig:
    """API server configuration"""
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 4
    max_request_size: int = 16 * 1024 * 1024  # 16MB
    request_timeout: int = 300  # 5 minutes
    enable_cors: bool = True
    cors_origins: List[str] = field(default_factory=lambda: ["*"])
    api_key_required: bool = True
    rate_limit_requests: int = 1000
    rate_limit_window: int = 3600  # 1 hour

@dataclass
class LoggingConfig:
    """Logging configuration"""
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file_path: Optional[str] = None
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    backup_count: int = 5
    enable_json_logging: bool = False
    log_to_console: bool = True
    log_sql_queries: bool = False

@dataclass
class MonitoringConfig:
    """Monitoring and metrics configuration"""
    enable_prometheus: bool = True
    prometheus_port: int = 9090
    metrics_retention_days: int = 7
    health_check_interval: int = 30
    alert_webhook_url: Optional[str] = None
    enable_detailed_metrics: bool = True
    custom_metrics: Dict[str, Any] = field(default_factory=dict)

class Config:
    """Main configuration manager for AI-Enhanced PDanet-Linux"""
    
    def __init__(self, config_file: Optional[str] = None, environment: Optional[str] = None):
        self.environment = environment or os.getenv('PDANET_ENV', 'development')
        self.config_file = config_file or self._find_config_file()
        
        # Configuration sections
        self.database = DatabaseConfig()
        self.redis = RedisConfig()
        self.ml = MLConfig()
        self.network = NetworkConfig()
        self.security = SecurityConfig()
        self.api = APIConfig()
        self.logging = LoggingConfig()
        self.monitoring = MonitoringConfig()
        
        # Additional settings
        self._custom_settings: Dict[str, Any] = {}
        self._loaded_from: List[str] = []
        
        # Load configuration
        self._load_configuration()
        self._apply_environment_overrides()
        self._validate_configuration()
        
        logger.info(f"Configuration loaded for environment: {self.environment}")
    
    def _find_config_file(self) -> Optional[str]:
        """Find configuration file in standard locations"""
        search_paths = [
            "config.yaml",
            "config.yml",
            "config.json",
            f"config_{self.environment}.yaml",
            f"config_{self.environment}.yml",
            f"config_{self.environment}.json",
            "conf/config.yaml",
            "etc/pdanet/config.yaml",
            "/etc/pdanet/config.yaml",
        ]
        
        for path in search_paths:
            if os.path.exists(path):
                logger.info(f"Found configuration file: {path}")
                return path
        
        logger.warning("No configuration file found, using defaults")
        return None
    
    def _load_configuration(self):
        """Load configuration from file"""
        if not self.config_file or not os.path.exists(self.config_file):
            logger.info("Using default configuration")
            return
        
        try:
            with open(self.config_file, 'r') as f:
                if self.config_file.endswith(('.yaml', '.yml')):
                    config_data = yaml.safe_load(f)
                else:
                    config_data = json.load(f)
            
            self._apply_config_data(config_data)
            self._loaded_from.append(self.config_file)
            
            logger.info(f"Loaded configuration from {self.config_file}")
            
        except Exception as e:
            logger.error(f"Failed to load configuration file {self.config_file}: {e}")
    
    def _apply_config_data(self, config_data: Dict[str, Any]):
        """Apply configuration data to settings"""
        # Database configuration
        if 'database' in config_data:
            db_config = config_data['database']
            for key, value in db_config.items():
                if hasattr(self.database, key):
                    setattr(self.database, key, value)
        
        # Redis configuration
        if 'redis' in config_data:
            redis_config = config_data['redis']
            for key, value in redis_config.items():
                if hasattr(self.redis, key):
                    setattr(self.redis, key, value)
        
        # ML configuration
        if 'ml' in config_data:
            ml_config = config_data['ml']
            for key, value in ml_config.items():
                if hasattr(self.ml, key):
                    setattr(self.ml, key, value)
        
        # Network configuration
        if 'network' in config_data:
            network_config = config_data['network']
            for key, value in network_config.items():
                if hasattr(self.network, key):
                    setattr(self.network, key, value)
        
        # Security configuration
        if 'security' in config_data:
            security_config = config_data['security']
            for key, value in security_config.items():
                if hasattr(self.security, key):
                    setattr(self.security, key, value)
        
        # API configuration
        if 'api' in config_data:
            api_config = config_data['api']
            for key, value in api_config.items():
                if hasattr(self.api, key):
                    setattr(self.api, key, value)
        
        # Logging configuration
        if 'logging' in config_data:
            logging_config = config_data['logging']
            for key, value in logging_config.items():
                if hasattr(self.logging, key):
                    setattr(self.logging, key, value)
        
        # Monitoring configuration
        if 'monitoring' in config_data:
            monitoring_config = config_data['monitoring']
            for key, value in monitoring_config.items():
                if hasattr(self.monitoring, key):
                    setattr(self.monitoring, key, value)
        
        # Custom settings
        for key, value in config_data.items():
            if key not in ['database', 'redis', 'ml', 'network', 'security', 'api', 'logging', 'monitoring']:
                self._custom_settings[key] = value
    
    def _apply_environment_overrides(self):
        """Apply environment variable overrides"""
        env_mappings = {
            # Database
            'PDANET_DB_HOST': ('database', 'host'),
            'PDANET_DB_PORT': ('database', 'port', int),
            'PDANET_DB_NAME': ('database', 'database'),
            'PDANET_DB_USER': ('database', 'username'),
            'PDANET_DB_PASSWORD': ('database', 'password'),
            
            # Redis
            'PDANET_REDIS_HOST': ('redis', 'host'),
            'PDANET_REDIS_PORT': ('redis', 'port', int),
            'PDANET_REDIS_DB': ('redis', 'database', int),
            'PDANET_REDIS_PASSWORD': ('redis', 'password'),
            
            # API
            'PDANET_API_HOST': ('api', 'host'),
            'PDANET_API_PORT': ('api', 'port', int),
            'PDANET_API_WORKERS': ('api', 'workers', int),
            
            # Security
            'PDANET_SECURITY_ENABLED': ('security', 'enable_monitoring', lambda x: x.lower() == 'true'),
            'PDANET_AUTO_RESPONSE': ('security', 'auto_response_enabled', lambda x: x.lower() == 'true'),
            
            # ML
            'PDANET_ML_MODELS_DIR': ('ml', 'models_dir'),
            'PDANET_ML_BATCH_SIZE': ('ml', 'batch_size', int),
            'PDANET_ML_LEARNING_RATE': ('ml', 'learning_rate', float),
            'PDANET_ML_DEVICE': ('ml', 'device'),
            
            # Logging
            'PDANET_LOG_LEVEL': ('logging', 'level'),
            'PDANET_LOG_FILE': ('logging', 'file_path'),
        }
        
        for env_var, config_path in env_mappings.items():
            value = os.getenv(env_var)
            if value is not None:
                section_name, attr_name = config_path[0], config_path[1]
                converter = config_path[2] if len(config_path) > 2 else str
                
                section = getattr(self, section_name)
                try:
                    converted_value = converter(value)
                    setattr(section, attr_name, converted_value)
                    self._loaded_from.append(f"ENV:{env_var}")
                except (ValueError, TypeError) as e:
                    logger.warning(f"Invalid value for {env_var}: {value} ({e})")
    
    def _validate_configuration(self):
        """Validate configuration settings"""
        errors = []
        
        # Validate database configuration
        if not self.database.host:
            errors.append("Database host is required")
        if not 1 <= self.database.port <= 65535:
            errors.append("Database port must be between 1 and 65535")
        if not self.database.database:
            errors.append("Database name is required")
        
        # Validate Redis configuration
        if not 1 <= self.redis.port <= 65535:
            errors.append("Redis port must be between 1 and 65535")
        
        # Validate API configuration
        if not 1 <= self.api.port <= 65535:
            errors.append("API port must be between 1 and 65535")
        if self.api.workers < 1:
            errors.append("API workers must be at least 1")
        
        # Validate ML configuration
        if not os.path.exists(self.ml.models_dir):
            try:
                os.makedirs(self.ml.models_dir, exist_ok=True)
            except OSError:
                errors.append(f"Cannot create models directory: {self.ml.models_dir}")
        
        if self.ml.batch_size < 1:
            errors.append("ML batch size must be at least 1")
        if not 0 < self.ml.learning_rate < 1:
            errors.append("ML learning rate must be between 0 and 1")
        
        # Validate network configuration
        if self.network.monitoring_interval < 1:
            errors.append("Network monitoring interval must be at least 1 second")
        if self.network.optimization_interval < 5:
            errors.append("Network optimization interval must be at least 5 seconds")
        
        # Validate security configuration
        if not 0 <= self.security.threat_detection_threshold <= 1:
            errors.append("Threat detection threshold must be between 0 and 1")
        
        if errors:
            error_msg = "Configuration validation failed:\n" + "\n".join(f"  - {error}" for error in errors)
            raise ValueError(error_msg)
        
        logger.info("Configuration validation passed")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key"""
        # Check custom settings first
        if key in self._custom_settings:
            return self._custom_settings[key]
        
        # Check section attributes
        parts = key.split('.', 1)
        if len(parts) == 2:
            section_name, attr_name = parts
            if hasattr(self, section_name):
                section = getattr(self, section_name)
                if hasattr(section, attr_name):
                    return getattr(section, attr_name)
        
        # Check direct attributes
        if hasattr(self, key):
            return getattr(self, key)
        
        return default
    
    def set(self, key: str, value: Any):
        """Set configuration value"""
        parts = key.split('.', 1)
        if len(parts) == 2:
            section_name, attr_name = parts
            if hasattr(self, section_name):
                section = getattr(self, section_name)
                if hasattr(section, attr_name):
                    setattr(section, attr_name, value)
                    return
        
        self._custom_settings[key] = value
    
    def update(self, updates: Dict[str, Any]):
        """Update multiple configuration values"""
        for key, value in updates.items():
            self.set(key, value)
    
    def get_database_url(self) -> str:
        """Get database connection URL"""
        password_part = f":{self.database.password}" if self.database.password else ""
        return (
            f"postgresql://{self.database.username}{password_part}@"
            f"{self.database.host}:{self.database.port}/{self.database.database}"
        )
    
    def get_redis_url(self) -> str:
        """Get Redis connection URL"""
        password_part = f":{self.redis.password}@" if self.redis.password else ""
        return f"redis://{password_part}{self.redis.host}:{self.redis.port}/{self.redis.database}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        return {
            'environment': self.environment,
            'database': self.database.__dict__,
            'redis': self.redis.__dict__,
            'ml': self.ml.__dict__,
            'network': self.network.__dict__,
            'security': self.security.__dict__,
            'api': self.api.__dict__,
            'logging': self.logging.__dict__,
            'monitoring': self.monitoring.__dict__,
            'custom': self._custom_settings,
            'loaded_from': self._loaded_from,
        }
    
    def save_to_file(self, file_path: str, format: str = 'yaml'):
        """Save current configuration to file"""
        config_dict = self.to_dict()
        
        # Remove runtime-only data
        config_dict.pop('loaded_from', None)
        
        try:
            with open(file_path, 'w') as f:
                if format.lower() in ('yaml', 'yml'):
                    yaml.dump(config_dict, f, default_flow_style=False, indent=2)
                else:
                    json.dump(config_dict, f, indent=2, default=str)
            
            logger.info(f"Configuration saved to {file_path}")
            
        except Exception as e:
            logger.error(f"Failed to save configuration to {file_path}: {e}")
            raise
    
    def reload(self):
        """Reload configuration from sources"""
        logger.info("Reloading configuration...")
        
        # Reset to defaults
        self.__init__(self.config_file, self.environment)
    
    def get_environment_info(self) -> Dict[str, Any]:
        """Get environment information"""
        return {
            'environment': self.environment,
            'config_file': self.config_file,
            'loaded_from': self._loaded_from,
            'python_version': os.sys.version,
            'working_directory': os.getcwd(),
            'user': os.getenv('USER', 'unknown'),
            'hostname': os.getenv('HOSTNAME', 'unknown'),
        }
    
    def validate_directories(self):
        """Ensure required directories exist"""
        directories = [
            self.ml.models_dir,
            self.ml.data_dir,
            'logs',
            'temp',
            'cache',
        ]
        
        for directory in directories:
            try:
                os.makedirs(directory, exist_ok=True)
                logger.debug(f"Ensured directory exists: {directory}")
            except OSError as e:
                logger.error(f"Failed to create directory {directory}: {e}")
                raise
    
    def setup_logging(self):
        """Configure logging based on settings"""
        import logging.handlers
        
        # Create formatter
        if self.logging.enable_json_logging:
            import json
            
            class JSONFormatter(logging.Formatter):
                def format(self, record):
                    log_entry = {
                        'timestamp': datetime.fromtimestamp(record.created).isoformat(),
                        'level': record.levelname,
                        'logger': record.name,
                        'message': record.getMessage(),
                        'module': record.module,
                        'function': record.funcName,
                        'line': record.lineno,
                    }
                    if record.exc_info:
                        log_entry['exception'] = self.formatException(record.exc_info)
                    return json.dumps(log_entry)
            
            formatter = JSONFormatter()
        else:
            formatter = logging.Formatter(self.logging.format)
        
        # Configure root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(getattr(logging, self.logging.level.upper()))
        
        # Clear existing handlers
        root_logger.handlers.clear()
        
        # Console handler
        if self.logging.log_to_console:
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            root_logger.addHandler(console_handler)
        
        # File handler
        if self.logging.file_path:
            file_handler = logging.handlers.RotatingFileHandler(
                self.logging.file_path,
                maxBytes=self.logging.max_file_size,
                backupCount=self.logging.backup_count
            )
            file_handler.setFormatter(formatter)
            root_logger.addHandler(file_handler)
        
        logger.info("Logging configured")
    
    def __str__(self) -> str:
        return f"Config(environment={self.environment}, sources={len(self._loaded_from)})"
    
    def __repr__(self) -> str:
        return self.__str__()

# Global configuration instance
_config_instance: Optional[Config] = None

def get_config() -> Config:
    """Get global configuration instance"""
    global _config_instance
    if _config_instance is None:
        _config_instance = Config()
    return _config_instance

def set_config(config: Config):
    """Set global configuration instance"""
    global _config_instance
    _config_instance = config

def reload_config():
    """Reload global configuration"""
    global _config_instance
    if _config_instance is not None:
        _config_instance.reload()

# Configuration validation utilities
def validate_ip_address(ip: str) -> bool:
    """Validate IP address format"""
    import ipaddress
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False

def validate_port(port: Union[int, str]) -> bool:
    """Validate port number"""
    try:
        port_num = int(port)
        return 1 <= port_num <= 65535
    except (ValueError, TypeError):
        return False

def validate_url(url: str) -> bool:
    """Validate URL format"""
    import re
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+'  # domain...
        r'(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # host...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return url_pattern.match(url) is not None

# Example configuration files
EXAMPLE_CONFIG_YAML = """
# AI-Enhanced PDanet-Linux Configuration

environment: development

database:
  host: localhost
  port: 5432
  database: pdanet_ai
  username: pdanet_user
  password: secure_password
  pool_size: 10

redis:
  host: localhost
  port: 6379
  database: 0
  password: null

ml:
  models_dir: ml_models
  data_dir: data
  batch_size: 32
  learning_rate: 0.001
  device: auto
  enable_gpu: true

network:
  default_interface: tun0
  monitoring_interval: 5
  optimization_interval: 30
  max_connections: 1000

security:
  enable_monitoring: true
  threat_detection_threshold: 0.7
  auto_response_enabled: true
  whitelist_ips: []

api:
  host: 0.0.0.0
  port: 8000
  workers: 4
  enable_cors: true
  api_key_required: true

logging:
  level: INFO
  log_to_console: true
  file_path: logs/pdanet_ai.log
  enable_json_logging: false

monitoring:
  enable_prometheus: true
  prometheus_port: 9090
  metrics_retention_days: 7
"""

if __name__ == "__main__":
    # Example usage
    config = Config()
    print("Configuration loaded successfully!")
    print(f"Environment: {config.environment}")
    print(f"Database URL: {config.get_database_url()}")
    print(f"API will run on {config.api.host}:{config.api.port}")
    
    # Save example configuration
    with open('example_config.yaml', 'w') as f:
        f.write(EXAMPLE_CONFIG_YAML)
    
    print("Example configuration saved to example_config.yaml")