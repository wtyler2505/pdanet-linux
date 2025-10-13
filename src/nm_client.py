"""
NetworkManager client (experimental): DBus access via pydbus/dbus-next.
This module is optional and not yet wired into ConnectionManager.
"""

try:
    from pydbus import SystemBus  # type: ignore
except Exception:
    SystemBus = None  # type: ignore


class NMClient:
    def __init__(self):
        self.bus = None
        self.nm = None
        if SystemBus is not None:
            try:
                self.bus = SystemBus()
                self.nm = self.bus.get("org.freedesktop.NetworkManager")
            except Exception:
                self.bus = None
                self.nm = None

    def available(self) -> bool:
        return self.nm is not None

    def get_wifi_devices(self) -> list[str]:
        if not self.available():
            return []
        try:
            devices = self.nm.GetDevices()
            wifi_paths = []
            for path in devices:
                dev = self.bus.get(".NetworkManager", path)
                if getattr(dev, "DeviceType", 0) == 2:  # NM_DEVICE_TYPE_WIFI = 2
                    wifi_paths.append(path)
            return wifi_paths
        except Exception:
            return []
