"""
Minimal stub for `gi` to support tests without system GTK bindings.
Provides a `repository` namespace with attributes that tests patch.
This avoids hard dependency on PyGObject in CI/sandboxed environments.
"""

from types import SimpleNamespace


def require_version(_lib: str, _ver: str) -> None:
    """No-op version requirement for stubbed gi."""
    return None


# Provide minimal structures expected by tests for patching
class _Indicator:
    @staticmethod
    def new(*_args, **_kwargs):
        return None


class AppIndicator3:  # pragma: no cover - test patch target
    Indicator = _Indicator


# Other commonly patched namespaces
Gtk = SimpleNamespace()
GLib = SimpleNamespace()
Gdk = SimpleNamespace()


# Expose a `repository` namespace akin to gi.repository
repository = SimpleNamespace(
    AppIndicator3=AppIndicator3,
    Gtk=Gtk,
    GLib=GLib,
    Gdk=Gdk,
)
