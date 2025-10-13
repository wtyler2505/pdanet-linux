"""
NetworkManager D-Bus client for robust network management.
Replaces fragile nmcli string parsing with proper D-Bus API calls.
"""

import time
from typing import Dict, List, Optional, Tuple

try:
    from pydbus import SystemBus
    HAS_DBUS = True
except ImportError:
    SystemBus = None
    HAS_DBUS = False

from logger import get_logger


class NetworkDevice:
    """Represents a network device with its properties"""
    def __init__(self, path: str, device_type: int, interface: str, state: int):
        self.path = path
        self.device_type = device_type  # 1=Ethernet, 2=WiFi, etc.
        self.interface = interface
        self.state = state  # 10=unmanaged, 20=unavailable, 30=disconnected, 100=connected, etc.
    
    @property
    def type_name(self) -> str:
        type_map = {1: "ethernet", 2: "wifi", 14: "generic"}
        return type_map.get(self.device_type, "unknown")
    
    @property
    def state_name(self) -> str:
        state_map = {
            10: "unmanaged", 20: "unavailable", 30: "disconnected", 
            40: "prepare", 50: "config", 60: "need-auth",
            70: "ip-config", 80: "ip-check", 90: "secondaries", 100: "connected"
        }
        return state_map.get(self.state, "unknown")
    
    @property
    def is_connected(self) -> bool:
        return self.state == 100


class AccessPoint:
    """Represents a WiFi access point"""
    def __init__(self, ssid: str, signal_strength: int, security: List[str], frequency: int = 0):
        self.ssid = ssid
        self.signal_strength = signal_strength  # 0-100
        self.security = security  # List of security types
        self.frequency = frequency
    
    @property
    def is_secured(self) -> bool:
        return len(self.security) > 0 and self.security != ["none"]
    
    @property
    def security_string(self) -> str:
        if not self.is_secured:
            return "None"
        return "/".join(self.security)


class NMClient:
    """Robust NetworkManager D-Bus client"""
    
    def __init__(self):
        self.bus = None
        self.nm = None
        self.logger = get_logger()
        self._wifi_scan_cache = {}
        self._scan_cache_timeout = 30  # seconds
        
        if HAS_DBUS:
            try:
                self.bus = SystemBus()
                self.nm = self.bus.get("org.freedesktop.NetworkManager")
                self.logger.info("NetworkManager D-Bus client initialized")
            except Exception as e:
                self.logger.warning(f"Failed to initialize NetworkManager D-Bus: {e}")
                self.bus = None
                self.nm = None
        else:
            self.logger.warning("pydbus not available, falling back to nmcli")

    def available(self) -> bool:
        """Check if NetworkManager D-Bus is available"""
        return self.nm is not None

    def get_devices(self) -> List[NetworkDevice]:
        """Get all network devices"""
        if not self.available():
            return []
        
        try:
            device_paths = self.nm.GetDevices()
            devices = []
            
            for path in device_paths:
                try:
                    device = self.bus.get("org.freedesktop.NetworkManager", path)
                    devices.append(NetworkDevice(
                        path=path,
                        device_type=device.DeviceType,
                        interface=device.Interface,
                        state=device.State
                    ))
                except Exception as e:
                    self.logger.debug(f"Failed to get device info for {path}: {e}")
                    continue
                    
            return devices
        except Exception as e:
            self.logger.error(f"Failed to get devices: {e}")
            return []

    def get_wifi_devices(self) -> List[NetworkDevice]:
        """Get all WiFi devices"""
        devices = self.get_devices()
        return [d for d in devices if d.device_type == 2]  # NM_DEVICE_TYPE_WIFI = 2

    def get_connected_wifi_device(self) -> Optional[NetworkDevice]:
        """Get the currently connected WiFi device"""
        wifi_devices = self.get_wifi_devices()
        for device in wifi_devices:
            if device.is_connected:
                return device
        return None

    def get_active_interface(self, device_type: Optional[str] = None) -> Optional[str]:
        """Get active interface name by device type"""
        devices = self.get_devices()
        
        for device in devices:
            if device.is_connected:
                if device_type is None or device.type_name == device_type:
                    return device.interface
        
        return None

    def scan_wifi_networks(self, device_interface: Optional[str] = None, force_rescan: bool = False) -> List[AccessPoint]:
        """Scan for available WiFi networks with caching"""
        cache_key = device_interface or "default"
        current_time = time.time()
        
        # Check cache first unless force_rescan
        if not force_rescan and cache_key in self._wifi_scan_cache:
            cached_data, cache_time = self._wifi_scan_cache[cache_key]
            if current_time - cache_time < self._scan_cache_timeout:
                self.logger.debug("Using cached WiFi scan results")
                return cached_data
        
        if not self.available():
            return []
        
        try:
            # Find WiFi device
            wifi_devices = self.get_wifi_devices()
            if not wifi_devices:
                self.logger.warning("No WiFi devices found")
                return []
            
            # Use specified device or first available
            target_device = None
            if device_interface:
                target_device = next((d for d in wifi_devices if d.interface == device_interface), None)
            if not target_device:
                target_device = wifi_devices[0]
            
            # Get the device D-Bus object
            device_obj = self.bus.get("org.freedesktop.NetworkManager", target_device.path)
            
            # Request scan if needed
            if force_rescan:
                try:
                    device_obj.RequestScan({})
                    self.logger.debug("Requested WiFi rescan")
                    time.sleep(2)  # Give scan time to complete
                except Exception as e:
                    self.logger.warning(f"Failed to request WiFi scan: {e}")
            
            # Get access points
            ap_paths = device_obj.AccessPoints
            access_points = []
            
            for ap_path in ap_paths:
                try:
                    ap = self.bus.get("org.freedesktop.NetworkManager", ap_path)
                    
                    # Get SSID (bytes to string)
                    ssid_bytes = ap.Ssid
                    ssid = bytes(ssid_bytes).decode('utf-8', errors='ignore').strip()
                    
                    if not ssid:  # Skip hidden networks
                        continue
                    
                    # Get signal strength (0-100)
                    signal = min(100, max(0, int(ap.Strength)))
                    
                    # Get security info
                    flags = getattr(ap, 'Flags', 0)
                    wpa_flags = getattr(ap, 'WpaFlags', 0)
                    rsn_flags = getattr(ap, 'RsnFlags', 0)
                    
                    security = []
                    if wpa_flags & 0x2:  # WPA-PSK
                        security.append("WPA")
                    if rsn_flags & 0x2:  # WPA2-PSK
                        security.append("WPA2")
                    if rsn_flags & 0x8:  # WPA3-PSK
                        security.append("WPA3")
                    if flags & 0x1:  # Privacy (WEP)
                        if not security:  # Only add WEP if no WPA
                            security.append("WEP")
                    
                    if not security:
                        security = ["none"]
                    
                    # Get frequency
                    frequency = getattr(ap, 'Frequency', 0)
                    
                    access_points.append(AccessPoint(
                        ssid=ssid,
                        signal_strength=signal,
                        security=security,
                        frequency=frequency
                    ))
                    
                except Exception as e:
                    self.logger.debug(f"Failed to process access point {ap_path}: {e}")
                    continue
            
            # Remove duplicates (same SSID) and keep the strongest signal
            unique_aps = {}
            for ap in access_points:
                if ap.ssid not in unique_aps or ap.signal_strength > unique_aps[ap.ssid].signal_strength:
                    unique_aps[ap.ssid] = ap
            
            result = list(unique_aps.values())
            
            # Sort by signal strength (descending)
            result.sort(key=lambda x: x.signal_strength, reverse=True)
            
            # Cache results
            self._wifi_scan_cache[cache_key] = (result, current_time)
            
            self.logger.info(f"Found {len(result)} unique WiFi networks")
            return result
            
        except Exception as e:
            self.logger.error(f"WiFi scan failed: {e}")
            return []

    def get_connection_status(self) -> Dict[str, any]:
        """Get comprehensive connection status"""
        if not self.available():
            return {"available": False, "error": "NetworkManager D-Bus not available"}
        
        try:
            # Get NetworkManager state
            nm_state = self.nm.State
            state_names = {
                10: "ASLEEP", 20: "DISCONNECTED", 30: "DISCONNECTING", 
                40: "CONNECTING", 50: "CONNECTED_LOCAL", 60: "CONNECTED_SITE", 70: "CONNECTED_GLOBAL"
            }
            
            devices = self.get_devices()
            active_devices = [d for d in devices if d.is_connected]
            
            return {
                "available": True,
                "nm_state": nm_state,
                "nm_state_name": state_names.get(nm_state, "UNKNOWN"),
                "total_devices": len(devices),
                "active_devices": len(active_devices),
                "wifi_devices": len([d for d in devices if d.device_type == 2]),
                "ethernet_devices": len([d for d in devices if d.device_type == 1]),
                "active_connections": [{"interface": d.interface, "type": d.type_name} for d in active_devices]
            }
        except Exception as e:
            return {"available": False, "error": str(e)}
