"""
Optional iptables management using python-iptables (iptc). Fallback remains shell scripts.
"""

try:
    import iptc  # type: ignore
except Exception:
    iptc = None  # type: ignore


def available() -> bool:
    return iptc is not None


def ensure_chain(table_name: str, chain_name: str) -> bool:
    if not available():
        return False
    try:
        table = iptc.Table(table_name)
        table.refresh()
        if not any(c.name == chain_name for c in table.chains):
            table.create_chain(chain_name)
        return True
    except Exception:
        return False
