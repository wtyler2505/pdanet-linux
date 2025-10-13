"""
Secret storage abstraction for PdaNet Linux.
Uses system keyring (Secret Service/libsecret) when available, with JSON fallback handled in ConfigManager.
"""

try:
    import keyring  # type: ignore
except Exception:  # keyring may not be installed
    keyring = None  # type: ignore

SERVICE_NAME = "pdanet-linux-wifi"


def is_available() -> bool:
    return keyring is not None


def set_wifi_password(ssid: str, password: str) -> bool:
    if not is_available():
        return False
    try:
        keyring.set_password(SERVICE_NAME, ssid, password)  # type: ignore
        return True
    except Exception:
        return False


def get_wifi_password(ssid: str) -> str | None:
    if not is_available():
        return None
    try:
        return keyring.get_password(SERVICE_NAME, ssid)  # type: ignore
    except Exception:
        return None


def delete_wifi_password(ssid: str) -> bool:
    if not is_available():
        return False
    try:
        keyring.delete_password(SERVICE_NAME, ssid)  # type: ignore
        return True
    except Exception:
        return False
