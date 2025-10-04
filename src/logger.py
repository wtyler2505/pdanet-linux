"""
PdaNet Linux - Logging System
Rotating log files with multiple severity levels
"""

import logging
import os
from logging.handlers import RotatingFileHandler
from datetime import datetime
from pathlib import Path

class PdaNetLogger:
    def __init__(self, log_dir=None):
        if log_dir is None:
            log_dir = Path.home() / ".config" / "pdanet-linux"
        else:
            log_dir = Path(log_dir)

        log_dir.mkdir(parents=True, exist_ok=True)
        self.log_file = log_dir / "pdanet.log"

        # Setup logger
        self.logger = logging.getLogger("pdanet")
        self.logger.setLevel(logging.DEBUG)

        # Rotating file handler (max 5MB, keep 5 backups)
        file_handler = RotatingFileHandler(
            self.log_file,
            maxBytes=5 * 1024 * 1024,  # 5 MB
            backupCount=5
        )
        file_handler.setLevel(logging.DEBUG)

        # Console handler for development
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)

        # Format: [2025-10-03 20:34:12] [INFO] :: Message
        formatter = logging.Formatter(
            "[%(asctime)s] [%(levelname)s] :: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

        # Log buffer for GUI (last N entries)
        self.log_buffer = []
        self.max_buffer_size = 1000

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
        entry = {
            "timestamp": timestamp,
            "level": level,
            "message": message
        }
        self.log_buffer.append(entry)

        # Keep buffer size limited
        if len(self.log_buffer) > self.max_buffer_size:
            self.log_buffer.pop(0)

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
            with open(self.log_file, 'r') as f:
                all_lines = f.readlines()
                return ''.join(all_lines[-lines:])
        except FileNotFoundError:
            return ""

# Global logger instance
_logger_instance = None

def get_logger():
    """Get or create global logger instance"""
    global _logger_instance
    if _logger_instance is None:
        _logger_instance = PdaNetLogger()
    return _logger_instance
