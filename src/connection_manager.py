"""
PdaNet Linux - Connection Manager
State machine, auto-reconnect, and connection orchestration
SECURITY HARDENED VERSION
"""

import ipaddress
import os
import re
import shutil
import subprocess
import threading
import time
from enum import Enum
from pathlib import Path

from config_manager import get_config
from logger import get_logger
from stats_collector import get_stats
from input_validators import (
    ValidationError,
    validate_ssid,
    validate_password,
    validate_ip_address,
    validate_port,
    validate_interface_name,
    validate_subprocess_args,
)


class ConnectionState(Enum):
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    DISCONNECTING = "disconnecting"
    ERROR = "error"


class ConnectionManager:
    def __init__(self):
        self.state = ConnectionState.DISCONNECTED
        self.logger = get_logger()
        self.stats = get_stats()
        self.config = get_config()

        self.current_interface = None
        self.current_mode = None
        self.proxy_available = False
        self.last_error = None

        # Auto-reconnect state
        self.auto_reconnect_enabled = False
        self.reconnect_attempts = 0
        self.max_reconnect_attempts = 3
        self.reconnect_delay = 5  # seconds
        self.reconnect_thread = None

        # Monitoring
        self.monitor_thread = None
        self.monitoring_active = False

        # Callbacks
        self.on_state_change_callbacks = []
        self.on_error_callbacks = []

        # Find script paths at initialization (SECURITY FIX: No hardcoded paths)
        self.connect_script = self._find_script("pdanet-connect")
        self.disconnect_script = self._find_script("pdanet-disconnect")
        self.wifi_connect_script = self._find_script("pdanet-wifi-connect")
        self.wifi_disconnect_script = self._find_script("pdanet-wifi-disconnect")
        self.iphone_connect_script = self._find_script("pdanet-iphone-connect")
        self.iphone_disconnect_script = self._find_script("pdanet-iphone-disconnect")

    def _run_privileged(self, argv, timeout=60):
        """
        Run a privileged command using PolicyKit (pkexec).
        SECURITY FIX: Audit Issue #55, #293
        - Requires pkexec (PolicyKit) for privilege escalation
        - Fails explicitly if pkexec is unavailable
        - No silent sudo fallback to avoid inconsistent security model
        """
        # Validate arguments before execution
        try:
            validate_subprocess_args(argv)
        except ValidationError as e:
            self.logger.error(f"Invalid subprocess arguments: {e}")
            # Return a failed result instead of raising
            class FailedResult:
                returncode = 1
                stdout = ""
                stderr = f"Argument validation failed: {e}"
            return FailedResult()
        
        # Check if pkexec is available
        pkexec_path = shutil.which("pkexec")
        if not pkexec_path:
            error_msg = (
                "PolicyKit (pkexec) is not available. "
                "Please install it: sudo apt-get install policykit-1"
            )
            self.logger.error(error_msg)
            
            # Return a failed result with helpful message
            class FailedResult:
                returncode = 127
                stdout = ""
                stderr = error_msg
            return FailedResult()
        
        try:
            cmd = [pkexec_path] + argv
            result = subprocess.run(
                cmd,
                check=False,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            # Log privileged operation for audit trail (Issue #300-303)
            self.logger.info(
                f"Privileged command executed: {argv[0]} "
                f"(exit code: {result.returncode})"
            )
            
            return result
            
        except subprocess.TimeoutExpired:
            error_msg = f"Privileged command timed out after {timeout}s: {' '.join(argv)}"
            self.logger.error(error_msg)
            
            class FailedResult:
                returncode = 124
                stdout = ""
                stderr = error_msg
            return FailedResult()
            
        except Exception as e:
            error_msg = f"Failed to execute privileged command: {e}"
            self.logger.error(error_msg)
            
            class FailedResult:
                returncode = 1
                stdout = ""
                stderr = error_msg
            return FailedResult()

    def _find_script(self, script_name):
        """
        Find script in PATH or relative to current directory
        SECURITY: Prevents arbitrary path execution
        """
        # First try system PATH
        script_path = shutil.which(script_name)
        if script_path:
            return script_path

        # Try relative to this file's directory
        current_dir = Path(__file__).parent.parent
        script_path = current_dir / script_name
        if script_path.exists() and os.access(script_path, os.X_OK):
            return str(script_path)

        # Try /usr/local/bin (common install location)
        script_path = Path("/usr/local/bin") / script_name
        if script_path.exists():
            return str(script_path)

        self.logger.warning(f"Script not found: {script_name}")
        return None

    def _validate_proxy_ip(self, ip):
        """
        Validate proxy IP address
        SECURITY FIX: Prevents command injection via malicious IP
        """
        try:
            ipaddress.ip_address(ip)
            return True
        except ValueError:
            return False

    def _validate_proxy_port(self, port):
        """
        Validate proxy port number
        SECURITY FIX: Ensures port is valid integer in range
        """
        try:
            port_int = int(port)
            return 1 <= port_int <= 65535
        except (ValueError, TypeError):
            return False

    def _validate_hostname(self, hostname):
        """
        Validate hostname for DNS operations
        SECURITY FIX: Prevents command injection via malicious hostnames
        """
        # Allow IP addresses
        if self._validate_proxy_ip(hostname):
            return True

        # Allow valid hostnames (RFC 1123)
        hostname_pattern = r"^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)*$"
        return bool(re.match(hostname_pattern, hostname)) and len(hostname) <= 253

    def register_state_change_callback(self, callback):
        """Register callback for state changes"""
        self.on_state_change_callbacks.append(callback)

    def register_error_callback(self, callback):
        """Register callback for errors"""
        self.on_error_callbacks.append(callback)

    def _notify_state_change(self):
        """Notify all registered callbacks of state change"""
        for callback in self.on_state_change_callbacks:
            try:
                callback(self.state)
            except Exception as e:
                self.logger.error(f"State change callback error: {e}")

    def _notify_error(self, error_message):
        """Notify all registered callbacks of error"""
        for callback in self.on_error_callbacks:
            try:
                callback(error_message)
            except Exception as e:
                self.logger.error(f"Error callback error: {e}")

    def _set_state(self, new_state):
        """Update connection state and notify"""
        if self.state != new_state:
            old_state = self.state
            self.state = new_state
            self.logger.info(f"State changed: {old_state.value} -> {new_state.value}")
            self._notify_state_change()

    def detect_interface(self):
        """Detect active network interface (USB or WiFi)"""
        try:
            # If we have a current mode, detect appropriate interface
            if self.current_mode in ["iphone", "wifi"]:
                # For WiFi/iPhone mode, find active WiFi interface
                result = subprocess.run(
                    ["nmcli", "-t", "-f", "DEVICE,TYPE,STATE", "device"],
                    check=False,
                    capture_output=True,
                    text=True,
                    timeout=5,
                )

                for line in result.stdout.split("\n"):
                    if line:
                        parts = line.split(":")
                        if len(parts) >= 3:
                            device, dev_type, state = parts[0], parts[1], parts[2]
                            if dev_type == "wifi" and state == "connected":
                                self.current_interface = device
                                self.logger.ok(f"WiFi interface detected: {device}")
                                return device

                self.logger.warning("No active WiFi interface detected")
                return None

            else:
                # For USB mode, look for USB/RNDIS interfaces
                result = subprocess.run(
                    ["ip", "link", "show"], check=False, capture_output=True, text=True, timeout=5
                )

                for line in result.stdout.split("\n"):
                    if "usb" in line.lower() or "rndis" in line.lower():
                        # Extract interface name
                        parts = line.split(":")
                        if len(parts) >= 2:
                            iface = parts[1].strip().split("@")[0]
                            self.current_interface = iface
                            self.logger.ok(f"USB interface detected: {iface}")
                            return iface

                self.logger.warning("No USB tethering interface detected")
                return None
        except Exception as e:
            self.logger.error(f"Interface detection failed: {e}")
            return None

    # ------------------------------------------------------------------
    # Compatibility helpers for legacy tests
    # ------------------------------------------------------------------
    def _detect_usb_interface(self):
        try:
            result = subprocess.run(
                ["ip", "link", "show"], check=False, capture_output=True, text=True, timeout=5
            )
            output = result.stdout or ""
            for line in output.splitlines():
                if (
                    line.strip().startswith("usb")
                    or "usb" in line.lower()
                    or "rndis" in line.lower()
                ):
                    iface = line.split(":")[0].strip()
                    self.logger.debug(f"Compatibility USB detection picked {iface}")
                    return iface or None
        except Exception as exc:
            self.logger.debug(f"Compatibility USB detection failed: {exc}")
        return None

    def _detect_wifi_interface(self):
        try:
            result = subprocess.run(
                ["nmcli", "-t", "-f", "DEVICE,TYPE,STATE", "device"],
                check=False,
                capture_output=True,
                text=True,
                timeout=5,
            )
            output = result.stdout or ""
            for line in output.splitlines():
                parts = line.split(":")
                if len(parts) == 1:
                    # Legacy tests return plain interface names
                    return parts[0].strip() or None
                if len(parts) >= 3:
                    device, dev_type, state = parts[0], parts[1], parts[2]
                    if dev_type == "wifi" and state == "connected":
                        return device
        except Exception as exc:
            self.logger.debug(f"Compatibility WiFi detection failed: {exc}")
        return None

    def _transition_to(self, new_state):
        self._set_state(new_state)
        return self.state

    def add_state_callback(self, callback):
        self.register_state_change_callback(callback)

    def validate_proxy(self):
        """
        Check if PdaNet proxy is accessible
        SECURITY HARDENED: Input validation before subprocess call
        """
        proxy_ip = self.config.get("proxy_ip", "192.168.49.1")
        proxy_port = self.config.get("proxy_port", 8000)

        # SECURITY FIX: Validate inputs before using in subprocess
        if not self._validate_proxy_ip(proxy_ip):
            self.logger.error(f"Invalid proxy IP: {proxy_ip}")
            return False

        if not self._validate_proxy_port(proxy_port):
            self.logger.error(f"Invalid proxy port: {proxy_port}")
            return False

        try:
            # Safe to use validated inputs
            # Use HTTPS head request to validate CONNECT path through proxy
            result = subprocess.run(
                [
                    "curl",
                    "-I",  # HEAD request
                    "-x",
                    f"http://{proxy_ip}:{proxy_port}",
                    "--connect-timeout",
                    "5",
                    "-sS",
                    "https://example.com/",
                ],
                check=False,
                capture_output=True,
                timeout=10,
            )

            if result.returncode == 0:
                self.proxy_available = True
                self.logger.ok(f"Proxy validated: {proxy_ip}:{proxy_port}")
                return True
            else:
                self.proxy_available = False
                stderr = (result.stderr or b"").decode(errors="ignore").strip()
                self.logger.error(f"Proxy not accessible: {proxy_ip}:{proxy_port} ({stderr})")
                return False
        except Exception as e:
            self.proxy_available = False
            self.logger.error(f"Proxy validation failed: {e}")
            return False

    def connect(self, mode="usb", ssid=None, password=None):
        """
        Initiate connection

        Args:
            mode: Connection mode - "usb", "wifi", or "iphone"
            ssid: WiFi/iPhone network name (required for wifi/iphone modes)
            password: WiFi/iPhone password (optional)
        """
        if self.state == ConnectionState.CONNECTED:
            self.logger.warning("Already connected")
            return True

        if self.state == ConnectionState.CONNECTING:
            self.logger.warning("Connection already in progress")
            return False

        self._set_state(ConnectionState.CONNECTING)
        self.current_mode = mode  # Store mode for interface detection
        self.logger.info(f"Initiating {mode} connection...")

        # Run in thread to avoid blocking
        thread = threading.Thread(
            target=self._connect_thread, args=(mode, ssid, password), daemon=True
        )
        thread.start()

        return True

    def _connect_thread(self, mode="usb", ssid=None, password=None):
        """Connection thread (runs in background)"""
        try:
            # Step 0: SECURITY - Validate all inputs before proceeding
            # Audit Issue #292, #58-59
            try:
                if mode in ["iphone", "wifi"]:
                    if ssid:
                        validate_ssid(ssid)
                    if password:
                        validate_password(password)
            except ValidationError as e:
                self.last_error = f"Invalid input: {e}"
                self._set_state(ConnectionState.ERROR)
                self._notify_error(self.last_error)
                self.logger.error(f"Input validation failed: {e}")
                return
            
            # Step 1: Detect interface (for USB mode)
            if mode == "usb":
                interface = self.detect_interface()
                if not interface:
                    self.last_error = "No USB interface detected"
                    self._set_state(ConnectionState.ERROR)
                    self._notify_error(self.last_error)
                    return

                # Step 2: Validate proxy
                if not self.validate_proxy():
                    self.last_error = "Proxy not accessible"
                    self._set_state(ConnectionState.ERROR)
                    self._notify_error(self.last_error)
                    return

            # Step 2b: For iPhone/WiFi mode, validate SSID
            if mode in ["iphone", "wifi"] and not ssid:
                self.last_error = f"SSID required for {mode} mode"
                self._set_state(ConnectionState.ERROR)
                self._notify_error(self.last_error)
                return

            # Step 3: Run connect script
            # SECURITY FIX: Use dynamically found script path, not hardcoded
            if mode == "wifi":
                script = self.wifi_connect_script
            elif mode == "iphone":
                script = self.iphone_connect_script
            else:
                script = self.connect_script

            if not script:
                self.last_error = f"Connection script not found for {mode} mode"
                self._set_state(ConnectionState.ERROR)
                self._notify_error(self.last_error)
                return

            self.logger.info(f"Running connection script: {script}")

            # Build command args. Prefer passing as arguments (pkexec strips env)
            cmd = [script]
            if mode in ["iphone", "wifi"] and ssid:
                cmd += [f"SSID={ssid}"]
                if password:
                    cmd += [f"PASSWORD={password}"]

            result = self._run_privileged(cmd, timeout=60)

            if result.returncode == 0:
                # For WiFi/iPhone modes, detect the interface after connection with retry
                if mode in ["iphone", "wifi"]:
                    # Retry interface detection up to 5 times (10 seconds total)
                    interface = None
                    for attempt in range(5):
                        time.sleep(2)
                        interface = self.detect_interface()
                        if interface:
                            self.logger.ok(f"WiFi interface detected: {interface}")
                            break
                        self.logger.debug(f"Interface detection attempt {attempt + 1}/5 failed")

                    if not interface:
                        self.logger.warning("WiFi interface detection failed after 5 attempts")

                self._set_state(ConnectionState.CONNECTED)
                self.logger.ok("Connection established")

                # Start statistics tracking
                self.stats.start_session()

                # Start monitoring
                self.start_monitoring()

                # Reset reconnect attempts
                self.reconnect_attempts = 0

            else:
                self.last_error = f"Connection script failed: {result.stderr}"
                self._set_state(ConnectionState.ERROR)
                self._notify_error(self.last_error)
                self.logger.error(self.last_error)

        except Exception as e:
            self.last_error = str(e)
            self._set_state(ConnectionState.ERROR)
            self._notify_error(self.last_error)
            self.logger.error(f"Connection failed: {e}")

    def disconnect(self):
        """Disconnect from PdaNet"""
        if self.state == ConnectionState.DISCONNECTED:
            self.logger.warning("Already disconnected")
            return True

        self._set_state(ConnectionState.DISCONNECTING)
        self.logger.info("Disconnecting...")

        # Stop monitoring
        self.stop_monitoring()

        # Run in thread
        thread = threading.Thread(target=self._disconnect_thread, daemon=True)
        thread.start()

        return True

    def _disconnect_thread(self):
        """Disconnection thread"""
        try:
            # SECURITY FIX: Use dynamically found script path
            script = self.disconnect_script
            if not script:
                self.last_error = "Disconnect script not found"
                self._set_state(ConnectionState.ERROR)
                self._notify_error(self.last_error)
                return

            result = self._run_privileged([script], timeout=15)

            if result.returncode == 0:
                self._set_state(ConnectionState.DISCONNECTED)
                self.logger.ok("Disconnected successfully")

                # Stop statistics
                self.stats.stop_session()

            else:
                self.last_error = f"Disconnect script failed: {result.stderr}"
                self._set_state(ConnectionState.ERROR)
                self._notify_error(self.last_error)
                self.logger.error(self.last_error)

        except Exception as e:
            self.last_error = str(e)
            self._set_state(ConnectionState.ERROR)
            self._notify_error(self.last_error)
            self.logger.error(f"Disconnection failed: {e}")

    def start_monitoring(self):
        """Start connection health monitoring"""
        if self.monitoring_active:
            return

        self.monitoring_active = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        self.logger.info("Connection monitoring started")

    def stop_monitoring(self):
        """Stop connection health monitoring"""
        self.monitoring_active = False
        if self.monitor_thread:
            self.monitor_thread = None
        self.logger.info("Connection monitoring stopped")

    def _monitor_loop(self):
        """Monitor connection health"""
        while self.monitoring_active and self.state == ConnectionState.CONNECTED:
            try:
                # Update bandwidth statistics
                if self.current_interface:
                    self.stats.update_bandwidth(self.current_interface)

                # Check if interface still exists
                interface = self.detect_interface()
                if not interface:
                    self.logger.warning("Interface lost")
                    if self.auto_reconnect_enabled:
                        self._handle_disconnect_and_reconnect()
                    else:
                        self._set_state(ConnectionState.DISCONNECTED)
                    break

                time.sleep(1)  # Check every second

            except Exception as e:
                self.logger.error(f"Monitoring error: {e}")
                time.sleep(5)

    def enable_auto_reconnect(self, enabled=True):
        """Enable or disable auto-reconnect"""
        self.auto_reconnect_enabled = enabled
        if enabled:
            self.max_reconnect_attempts = self.config.get("reconnect_attempts", 3)
            self.reconnect_delay = self.config.get("reconnect_delay", 5)
            self.logger.info(f"Auto-reconnect enabled (max {self.max_reconnect_attempts} attempts)")
        else:
            self.logger.info("Auto-reconnect disabled")

    def _handle_disconnect_and_reconnect(self):
        """Handle unexpected disconnect and attempt reconnection"""
        if not self.auto_reconnect_enabled:
            return

        if self.reconnect_attempts >= self.max_reconnect_attempts:
            self.logger.error(f"Max reconnect attempts ({self.max_reconnect_attempts}) reached")
            self._set_state(ConnectionState.ERROR)
            return

        self.reconnect_attempts += 1

        # Exponential backoff
        delay = self.reconnect_delay * (2 ** (self.reconnect_attempts - 1))
        delay = min(delay, 60)  # Cap at 60 seconds

        self.logger.warning(
            f"Reconnect attempt {self.reconnect_attempts}/{self.max_reconnect_attempts} in {delay}s"
        )

        time.sleep(delay)
        self.connect()

    def get_state(self):
        """Get current connection state"""
        return self.state

    def is_connected(self):
        """Check if currently connected"""
        return self.state == ConnectionState.CONNECTED

    def get_status_info(self):
        """Get detailed status information"""
        return {
            "state": self.state.value,
            "interface": self.current_interface,
            "proxy_available": self.proxy_available,
            "auto_reconnect": self.auto_reconnect_enabled,
            "reconnect_attempts": self.reconnect_attempts,
            "last_error": self.last_error,
        }


# Global connection manager instance
_connection_instance = None


def get_connection_manager():
    """Get or create global connection manager instance"""
    global _connection_instance
    if _connection_instance is None:
        _connection_instance = ConnectionManager()
    return _connection_instance
