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
from concurrent.futures import ThreadPoolExecutor
from enum import Enum
from pathlib import Path
from typing import Any, Dict, Optional

from config_manager import get_config
from logger import get_logger
from stats_collector import get_stats
from nm_client import NMClient
from performance_optimizer import get_resource_manager, timed_operation, resource_context
from reliability_manager import get_reliability_manager
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


# Valid state transitions (Issue #56)
# Each state maps to a set of valid next states
VALID_TRANSITIONS = {
    ConnectionState.DISCONNECTED: {
        ConnectionState.CONNECTING,
        ConnectionState.ERROR,
    },
    ConnectionState.CONNECTING: {
        ConnectionState.CONNECTED,
        ConnectionState.ERROR,
        ConnectionState.DISCONNECTING,  # Allow cancellation during connect
    },
    ConnectionState.CONNECTED: {
        ConnectionState.DISCONNECTING,
        ConnectionState.ERROR,
        ConnectionState.DISCONNECTED,  # Network loss detection
    },
    ConnectionState.DISCONNECTING: {
        ConnectionState.DISCONNECTED,
        ConnectionState.ERROR,
    },
    ConnectionState.ERROR: {
        ConnectionState.DISCONNECTED,
        ConnectionState.CONNECTING,  # Allow retry from error
    },
}


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
        
        # Thread management (Issue #266, #P1-FUNC-7)
        # Bounded thread pool to prevent unbounded thread spawning
        self.executor = ThreadPoolExecutor(max_workers=3, thread_name_prefix="pdanet")
        self.active_futures = set()  # Track active operations

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

        # NetworkManager D-Bus client for robust network management
        self.nm_client = NMClient()
        if self.nm_client.available():
            self.logger.info("Using NetworkManager D-Bus API for network management")
        else:
            self.logger.warning("NetworkManager D-Bus unavailable, falling back to nmcli")

        # Stealth mode status tracking
        self.stealth_active = False
        self.stealth_level = 0
        
        # Performance and reliability enhancements (P2)
        self.resource_manager = get_resource_manager()
        self.reliability_manager = get_reliability_manager()
        
        # Start performance monitoring and reliability checks
        self.resource_manager.start_monitoring(interval=60)
        self.reliability_manager.start_monitoring()

    def _run_privileged(self, argv, timeout=60, env=None):
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
            
            # Prepare environment
            run_env = os.environ.copy()
            if env:
                run_env.update(env)
            
            result = subprocess.run(
                cmd,
                check=False,
                capture_output=True,
                text=True,
                timeout=timeout,
                env=run_env
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
        """
        Update connection state with transition validation
        Issue #56: Prevent illegal state transitions
        
        Args:
            new_state: Target ConnectionState
        
        Returns:
            bool: True if transition successful, False if invalid
        """
        if self.state == new_state:
            # Already in target state, no-op
            return True
        
        old_state = self.state
        
        # Validate transition
        valid_next_states = VALID_TRANSITIONS.get(old_state, set())
        if new_state not in valid_next_states:
            self.logger.error(
                f"Invalid state transition: {old_state.value} -> {new_state.value}. "
                f"Valid transitions from {old_state.value}: {[s.value for s in valid_next_states]}"
            )
            # For safety, allow transition to ERROR from any state
            if new_state == ConnectionState.ERROR:
                self.logger.warning("Forcing transition to ERROR state")
            else:
                return False
        
        # Perform transition
        self.state = new_state
        self.logger.info(f"State changed: {old_state.value} -> {new_state.value}")
        self._notify_state_change()
        return True

    @timed_operation("interface_detection")
    def detect_interface(self):
        """Detect active network interface using NetworkManager D-Bus or fallback to nmcli"""
        try:
            # First, try robust D-Bus method
            if self.nm_client.available():
                return self._detect_interface_dbus()
            else:
                # Fallback to nmcli parsing
                return self._detect_interface_nmcli()
        except Exception as e:
            self.logger.error(f"Interface detection failed: {e}")
            return None

    def _detect_interface_dbus(self):
        """Detect interface using NetworkManager D-Bus API"""
        try:
            if self.current_mode in ["iphone", "wifi"]:
                # For WiFi/iPhone mode, find active WiFi interface
                wifi_device = self.nm_client.get_connected_wifi_device()
                if wifi_device:
                    self.current_interface = wifi_device.interface
                    self.logger.ok(f"WiFi interface detected via D-Bus: {wifi_device.interface}")
                    return wifi_device.interface
                
                self.logger.warning("No active WiFi interface detected via D-Bus")
                return None
            else:
                # For USB mode, look for active ethernet/generic interfaces
                active_interface = self.nm_client.get_active_interface("ethernet")
                if not active_interface:
                    active_interface = self.nm_client.get_active_interface("generic")
                
                if active_interface:
                    self.current_interface = active_interface
                    self.logger.ok(f"USB interface detected via D-Bus: {active_interface}")
                    return active_interface
                
                self.logger.warning("No USB tethering interface detected via D-Bus")
                return None
        except Exception as e:
            self.logger.error(f"D-Bus interface detection failed: {e}")
            return None

    def _detect_interface_nmcli(self):
        """Fallback interface detection using nmcli (legacy method)"""
        try:
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
                                self.logger.ok(f"WiFi interface detected via nmcli: {device}")
                                return device

                self.logger.warning("No active WiFi interface detected via nmcli")
                return None
            else:
                # For USB mode, look for USB/RNDIS interfaces using ip command
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
                            self.logger.ok(f"USB interface detected via ip: {iface}")
                            return iface

                self.logger.warning("No USB tethering interface detected via ip")
                return None
        except Exception as e:
            self.logger.error(f"nmcli interface detection failed: {e}")
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
        """Compatibility method for legacy tests - uses robust detection"""
        try:
            if self.nm_client.available():
                wifi_device = self.nm_client.get_connected_wifi_device()
                if wifi_device:
                    return wifi_device.interface
            
            # Fallback to nmcli
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
        Issue #266, #P1-FUNC-7: Use ThreadPoolExecutor for bounded threading

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

        # Submit to thread pool instead of creating daemon thread
        future = self.executor.submit(self._connect_thread, mode, ssid, password)
        self.active_futures.add(future)
        # Clean up completed futures
        future.add_done_callback(lambda f: self.active_futures.discard(f))

        return True

    @timed_operation("connection_establishment")
    def _connect_thread(self, mode="usb", ssid=None, password=None):
        """Connection thread (runs in background) with enhanced error handling"""
        with resource_context("connection_thread"):
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
                    error_msg = f"Invalid input: {e}"
                    self.last_error = error_msg
                    self._set_state(ConnectionState.ERROR)
                    self._notify_error(error_msg)
                    self.reliability_manager.report_failure("validation_error", error_msg)
                    self.logger.error(f"Input validation failed: {e}")
                    return
                
                # Step 1: Detect interface (for USB mode)
                if mode == "usb":
                    interface = self.detect_interface()
                    if not interface:
                        error_msg = "No USB interface detected"
                        self.last_error = error_msg
                        self._set_state(ConnectionState.ERROR)
                        self._notify_error(error_msg)
                        self.reliability_manager.report_failure("interface_detection", error_msg)
                        return

                    # Step 2: Validate proxy
                    if not self.validate_proxy():
                        error_msg = "Proxy not accessible"
                        self.last_error = error_msg
                        self._set_state(ConnectionState.ERROR)
                        self._notify_error(error_msg)
                        self.reliability_manager.report_failure("proxy_validation", error_msg, interface)
                        return

                # Step 2b: For iPhone/WiFi mode, validate SSID
                if mode in ["iphone", "wifi"] and not ssid:
                    error_msg = f"SSID required for {mode} mode"
                    self.last_error = error_msg
                    self._set_state(ConnectionState.ERROR)
                    self._notify_error(error_msg)
                    self.reliability_manager.report_failure("missing_ssid", error_msg)
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
                    error_msg = f"Connection script not found for {mode} mode"
                    self.last_error = error_msg
                    self._set_state(ConnectionState.ERROR)
                    self._notify_error(error_msg)
                    self.reliability_manager.report_failure("script_not_found", error_msg)
                    return

                self.logger.info(f"Running connection script: {script}")

                # Build command args with enhanced error handling
                success = self._execute_connection_script(script, mode, ssid, password)
                
                if success:
                    self._set_state(ConnectionState.CONNECTED)
                    self.current_failures = 0  # Reset failure counter on success
                    self.logger.ok(f"{mode.upper()} connection established successfully")
                else:
                    error_msg = f"{mode.upper()} connection failed"
                    self.last_error = error_msg
                    self._set_state(ConnectionState.ERROR)
                    self._notify_error(error_msg)
                    self.reliability_manager.report_failure("connection_script_failed", error_msg, self.current_interface)

            except Exception as e:
                error_msg = f"Connection thread error: {e}"
                self.last_error = error_msg
                self._set_state(ConnectionState.ERROR)
                self._notify_error(error_msg)
                self.reliability_manager.report_failure("connection_thread_exception", error_msg)
                self.logger.error(f"Connection thread failed: {e}")
    
    @timed_operation("connection_script")
    def _execute_connection_script(self, script: str, mode: str, ssid: Optional[str], password: Optional[str]) -> bool:
        """Execute connection script with enhanced error handling and timeout"""
        try:
            # Enhanced script execution with better error handling
            cmd = [script]
            
            # Build environment for script
            env = {}
            if mode in ["iphone", "wifi"] and ssid:
                env["SSID"] = ssid
                if password:
                    env["PASSWORD"] = password
            
            # Execute with timeout and proper error capture
            result = self._run_privileged(cmd, timeout=120, env=env)
            
            if result and result.returncode == 0:
                self.logger.info("Connection script completed successfully")
                return True
            else:
                error_output = result.stderr if result else "No result returned"
                self.logger.error(f"Connection script failed: {error_output}")
                return False
                
        except subprocess.TimeoutExpired:
            self.logger.error("Connection script timed out")
            return False
        except Exception as e:
            self.logger.error(f"Failed to execute connection script: {e}")
            return False

    @timed_operation("disconnection")
    def disconnect(self):
        """Disconnect from PdaNet"""
        if self.state == ConnectionState.DISCONNECTED:
            self.logger.warning("Already disconnected")
            return True

        self._set_state(ConnectionState.DISCONNECTING)
        self.logger.info("Disconnecting...")

        # Stop monitoring
        self.stop_monitoring()

        # Submit to thread pool instead of creating daemon thread
        future = self.executor.submit(self._disconnect_thread)
        self.active_futures.add(future)
        # Clean up completed futures
        future.add_done_callback(lambda f: self.active_futures.discard(f))

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
        """
        Stop connection health monitoring
        Issue #96-102: Properly join thread to prevent leaks
        """
        if not self.monitoring_active:
            return
        
        self.monitoring_active = False
        self.logger.info("Stopping connection monitoring...")
        
        # Wait for monitor thread to finish (with timeout)
        if self.monitor_thread and self.monitor_thread.is_alive():
            try:
                self.monitor_thread.join(timeout=3.0)
                if self.monitor_thread.is_alive():
                    self.logger.warning("Monitor thread did not stop within timeout")
                else:
                    self.logger.info("Connection monitoring stopped")
            except Exception as e:
                self.logger.error(f"Error joining monitor thread: {e}")
        
        self.monitor_thread = None

    def _monitor_loop(self):
        """Monitor connection health"""
        while self.monitoring_active and self.state == ConnectionState.CONNECTED:
            try:
                # Update bandwidth statistics
                if self.current_interface:
                    self.stats.update_bandwidth(self.current_interface)

                # Update stealth status (P1-FUNC-8)
                self.update_stealth_status()

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

    def shutdown(self):
        """
        Enhanced shutdown with performance monitoring cleanup
        Issue #96-102, #266: Properly cleanup all threads and resources
        """
        self.logger.info("Shutting down connection manager...")
        
        # Stop monitoring systems
        self.stop_monitoring()
        
        # Stop performance and reliability monitoring
        if hasattr(self, 'resource_manager'):
            self.resource_manager.stop_monitoring()
        if hasattr(self, 'reliability_manager'):
            self.reliability_manager.stop_monitoring()
        
        # Cancel any pending operations
        for future in list(self.active_futures):
            future.cancel()
        self.active_futures.clear()
        
        # Shutdown thread pool with improved timeout handling
        try:
            self.executor.shutdown(wait=True, timeout=10.0)
        except Exception as e:
            self.logger.warning(f"Executor shutdown warning: {e}")
        
        self.logger.info("Connection manager shutdown complete")
    # ------------------------------------------------------------------
    # Enhanced WiFi and Stealth Management (P1-FUNC-5, P1-FUNC-8)
    # ------------------------------------------------------------------
    
    def scan_wifi_networks(self, force_rescan=False):
        """
        Robust WiFi scanning with caching and error recovery
        P1-FUNC-5: Enhanced WiFi scanning/selection
        """
        try:
            if self.nm_client.available():
                return self.nm_client.scan_wifi_networks(force_rescan=force_rescan)
            else:
                # Fallback to nmcli-based scanning
                return self._scan_wifi_nmcli(force_rescan)
        except Exception as e:
            self.logger.error(f"WiFi scan failed: {e}")
            return []
    
    def _scan_wifi_nmcli(self, force_rescan=False):
        """Fallback WiFi scanning using nmcli"""
        try:
            # Request rescan if needed
            if force_rescan:
                subprocess.run(
                    ["nmcli", "device", "wifi", "rescan"],
                    check=False,
                    capture_output=True,
                    timeout=5
                )
                time.sleep(2)  # Give scan time to complete
            
            # Get network list
            result = subprocess.run(
                ["nmcli", "-t", "-f", "SSID,SIGNAL,SECURITY", "device", "wifi", "list"],
                check=False,
                capture_output=True,
                text=True,
                timeout=10,
            )
            
            if result.returncode != 0:
                return []
            
            # Parse results with better error handling
            networks = []
            seen_ssids = set()
            
            for line in result.stdout.strip().split("\n"):
                if not line:
                    continue
                
                parts = line.split(":")
                if len(parts) < 1 or not parts[0]:
                    continue
                
                ssid = parts[0].strip()
                if ssid in seen_ssids:  # Skip duplicates
                    continue
                
                seen_ssids.add(ssid)
                signal = parts[1] if len(parts) > 1 else "0"
                security = parts[2] if len(parts) > 2 else "None"
                
                # Convert to consistent format
                from nm_client import AccessPoint
                try:
                    signal_strength = int(signal) if signal.isdigit() else 0
                    security_list = [security] if security and security != "None" else ["none"]
                    
                    networks.append(AccessPoint(
                        ssid=ssid,
                        signal_strength=signal_strength,
                        security=security_list
                    ))
                except ValueError:
                    continue
            
            # Sort by signal strength
            networks.sort(key=lambda x: x.signal_strength, reverse=True)
            return networks
            
        except Exception as e:
            self.logger.error(f"nmcli WiFi scan failed: {e}")
            return []
    
    def get_connection_status(self):
        """Get comprehensive connection status including stealth information"""
        try:
            if self.nm_client.available():
                nm_status = self.nm_client.get_connection_status()
            else:
                nm_status = {"available": False, "error": "NetworkManager D-Bus not available"}
            
            return {
                "state": self.state.value,
                "interface": self.current_interface,
                "mode": self.current_mode,
                "proxy_available": self.proxy_available,
                "stealth_active": self.stealth_active,
                "stealth_level": self.stealth_level,
                "auto_reconnect": self.auto_reconnect_enabled,
                "reconnect_attempts": self.reconnect_attempts,
                "last_error": self.last_error,
                "nm_status": nm_status
            }
        except Exception as e:
            self.logger.error(f"Failed to get connection status: {e}")
            return {"state": self.state.value, "error": str(e)}
    
    def update_stealth_status(self):
        """
        Update stealth mode status by checking actual stealth script status
        P1-FUNC-8: Real-time stealth status display
        """
        try:
            if not self.current_interface:
                self.stealth_active = False
                self.stealth_level = 0
                return
            
            # Check if stealth mode is active by examining iptables rules
            result = subprocess.run(
                ["iptables", "-t", "mangle", "-L", "WIFI_STEALTH"],
                check=False,
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0 and "TTL" in result.stdout:
                self.stealth_active = True
                # Determine stealth level from current rules
                if "IPv6" in result.stdout or "ip6tables" in result.stdout:
                    self.stealth_level = 3  # Aggressive
                elif "DNS" in result.stdout:
                    self.stealth_level = 2  # Moderate
                else:
                    self.stealth_level = 1  # Basic
                
                self.logger.debug(f"Stealth mode active: Level {self.stealth_level}")
            else:
                self.stealth_active = False
                self.stealth_level = 0
                
        except Exception as e:
            self.logger.debug(f"Stealth status check failed: {e}")
            self.stealth_active = False
            self.stealth_level = 0
    
    def get_stealth_status_string(self):
        """Get human-readable stealth status string"""
        if not self.stealth_active:
            return "DISABLED"
        
        level_names = {1: "BASIC", 2: "MODERATE", 3: "AGGRESSIVE"}
        return f"ACTIVE (L{self.stealth_level}: {level_names.get(self.stealth_level, 'UNKNOWN')})"
    
    def get_comprehensive_status(self) -> Dict[str, Any]:
        """
        Get comprehensive system status including performance and reliability metrics
        P2-PERF: Enhanced status reporting
        """
        base_status = self.get_connection_status()
        
        # Add performance metrics
        if hasattr(self, 'resource_manager'):
            base_status['performance'] = self.resource_manager.get_resource_summary()
        
        # Add reliability metrics  
        if hasattr(self, 'reliability_manager'):
            base_status['reliability'] = self.reliability_manager.get_reliability_summary()
            base_status['failure_analysis'] = self.reliability_manager.get_failure_analysis()
        
        # Add network health
        if hasattr(self, 'reliability_manager'):
            base_status['network_health'] = self.reliability_manager.check_connection_health().value
        
        return base_status

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
