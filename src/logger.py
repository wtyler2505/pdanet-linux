"""
PdaNet Linux - Logging System
Rotating log files with multiple severity levels
"""

import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler
from pathlib import Path


class PdaNetLogger:
    def __init__(self, log_dir=None, log_level="INFO"):
        """
        Initialize logger with configurable log level
        
        Args:
            log_dir: Directory for log files (optional)
            log_level: Initial log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        """
        # Allow overriding log directory via env for tests/CI
        # Falls back to XDG-style path in home, then to repo-local .tmp_config if needed
        env_dir = os.environ.get("PDANET_LOG_DIR")
        try:
            if log_dir is not None:
                resolved_dir = Path(log_dir)
            elif env_dir:
                resolved_dir = Path(env_dir)
            else:
                resolved_dir = Path.home() / ".config" / "pdanet-linux"

            resolved_dir.mkdir(parents=True, exist_ok=True)
        except Exception:
            # Sandbox or permissions blocked; use repo-local tmp directory
            resolved_dir = Path.cwd() / ".tmp_config" / "pdanet-linux"
            resolved_dir.mkdir(parents=True, exist_ok=True)

        self.log_file = resolved_dir / "pdanet.log"

        # Setup logger
        self.logger = logging.getLogger("pdanet")
        # Set to DEBUG to capture everything; handlers filter by their own levels
        self.logger.setLevel(logging.DEBUG)

        # Store handlers for level updates
        self.file_handler = None
        self.console_handler = None

        # Rotating file handler (max 5MB, keep 5 backups)
        # Attempt to create rotating file handler; if it fails, fall back to console-only
        try:
            self.file_handler = RotatingFileHandler(
                self.log_file,
                maxBytes=5 * 1024 * 1024,  # 5 MB
                backupCount=5,
            )
            # File handler captures everything (DEBUG+)
            self.file_handler.setLevel(logging.DEBUG)
        except Exception:
            self.file_handler = None

        # Console handler respects configured log level
        self.console_handler = logging.StreamHandler()

        # Format: [2025-10-03 20:34:12] [INFO] :: Message
        formatter = logging.Formatter(
            "[%(asctime)s] [%(levelname)s] :: %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
        )
        if self.file_handler is not None:
            self.file_handler.setFormatter(formatter)
            self.logger.addHandler(self.file_handler)
        self.console_handler.setFormatter(formatter)
        self.logger.addHandler(self.console_handler)

        # Set initial log level (Issue #131)
        self.set_log_level(log_level)

        # Log buffer for GUI (last N entries)
        self.log_buffer = []
        self.max_buffer_size = 1000
        self.buffer_min_level = logging.INFO  # Buffer filter level

    def debug(self, message):
        """Debug level message"""
        self.logger.debug(message)
        self._add_to_buffer("DEBUG", message)

    def info(self, message):
        """Info level message"""
        self.logger.info(message)
        self._add_to_buffer("INFO", message)

    def ok(self, message):
        """Success message (shown as OK in GUI)"""
        self.logger.info(f"OK: {message}")
        self._add_to_buffer("OK", message)

    def warning(self, message):
        """Warning level message"""
        self.logger.warning(message)
        self._add_to_buffer("WARN", message)

    def error(self, message):
        """Error level message"""
        self.logger.error(message)
        self._add_to_buffer("ERROR", message)

    def critical(self, message):
        """Critical level message"""
        self.logger.critical(message)
        self._add_to_buffer("CRITICAL", message)

    def _add_to_buffer(self, level, message):
        """Add entry to circular buffer for GUI display"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
        entry = {"timestamp": timestamp, "level": level, "message": message}
        
        # Filter by buffer min level
        level_map = {
            "DEBUG": logging.DEBUG,
            "INFO": logging.INFO,
            "OK": logging.INFO,
            "WARN": logging.WARNING,
            "ERROR": logging.ERROR,
            "CRITICAL": logging.CRITICAL,
        }
        if level_map.get(level, logging.INFO) < self.buffer_min_level:
            return  # Skip messages below buffer threshold
        
        self.log_buffer.append(entry)

        # Keep buffer size limited
        if len(self.log_buffer) > self.max_buffer_size:
            self.log_buffer.pop(0)

    def set_log_level(self, level_str):
        """
        Set logging level dynamically
        Issue #131: Apply config log level without restart
        
        Args:
            level_str: Log level string (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        """
        level_map = {
            "DEBUG": logging.DEBUG,
            "INFO": logging.INFO,
            "WARNING": logging.WARNING,
            "ERROR": logging.ERROR,
            "CRITICAL": logging.CRITICAL,
        }
        
        level = level_map.get(level_str.upper(), logging.INFO)
        
        # Update console handler
        if self.console_handler:
            self.console_handler.setLevel(level)
        
        # Update buffer filter level
        self.buffer_min_level = level
        
        self.logger.info(f"Log level set to {level_str.upper()}")
    
    def get_log_level(self):
        """Get current console log level as string"""
        if not self.console_handler:
            return "INFO"
        
        level = self.console_handler.level
        level_map = {
            logging.DEBUG: "DEBUG",
            logging.INFO: "INFO",
            logging.WARNING: "WARNING",
            logging.ERROR: "ERROR",
            logging.CRITICAL: "CRITICAL",
        }
        return level_map.get(level, "INFO")

    def get_recent_logs(self, count=100):
        """Get recent log entries for GUI display"""
        return self.log_buffer[-count:]

    def get_all_logs(self):
        """Get all buffered logs"""
        return self.log_buffer

    def clear_buffer(self):
        """Clear the log buffer"""
        self.log_buffer.clear()

    def format_log_entry(self, entry):
        """Format log entry for GUI display"""
        return f"> {entry['timestamp']}\n  [{entry['level']}] :: {entry['message']}"

    def get_log_file_path(self):
        """Get path to log file"""
        return str(self.log_file)

    def read_log_file(self, lines=100):
        """Read last N lines from log file"""
        try:
            with open(self.log_file) as f:
                all_lines = f.readlines()
                return "".join(all_lines[-lines:])
        except FileNotFoundError:
            return ""


# Global logger instance
_logger_instance = None


def get_logger(log_level=None):
    """
    Get or create global logger instance
    
    Args:
        log_level: Optional log level to set (DEBUG, INFO, WARNING, ERROR, CRITICAL)
                  If None and logger exists, keeps current level
                  If None and logger doesn't exist, tries to read from config
    """
    global _logger_instance
    if _logger_instance is None:
        # Use provided log level or safe default (no config dependency)
        if log_level is None:
            log_level = "INFO"  # Safe default, config can override later
        
        _logger_instance = PdaNetLogger(log_level=log_level)
    elif log_level is not None:
        # Update existing logger's level
        _logger_instance.set_log_level(log_level)
    
    return _logger_instance
