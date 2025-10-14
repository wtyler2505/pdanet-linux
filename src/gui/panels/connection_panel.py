"""
Connection Panel for PdaNet Linux GUI
Displays connection status, interface information, and quality metrics
"""

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk


class ConnectionPanel:
    """
    Connection status and information panel
    Displays current connection state, interface, uptime, and quality
    """
    
    def __init__(self, parent_window):
        """Initialize connection panel"""
        self.parent = parent_window
        self.panel = None
        
        # Status labels (will be created by build_panel)
        self.status_state_label = None
        self.status_interface_label = None
        self.status_endpoint_label = None
        self.status_uptime_label = None
        self.status_stealth_label = None
        self.quality_progress = None
        self.quality_status_label = None
    
    def build_panel(self):
        """Build connection status panel"""
        if self.panel:
            return self.panel
            
        panel = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        panel.get_style_context().add_class("panel")

        # Header
        header = Gtk.Label(label="CONNECTION STATUS")
        header.get_style_context().add_class("panel-header")
        header.set_xalign(0)
        panel.pack_start(header, False, False, 0)

        # Status items
        self.status_state_label = self.parent.create_metric_row("STATUS", "● INACTIVE")
        self.status_interface_label = self.parent.create_metric_row("INTERFACE", "NOT DETECTED")
        self.status_endpoint_label = self.parent.create_metric_row("ENDPOINT", "192.168.49.1:8000")
        self.status_uptime_label = self.parent.create_metric_row("UPTIME", "00:00:00")
        self.status_stealth_label = self.parent.create_metric_row("STEALTH", "DISABLED")

        panel.pack_start(self.status_state_label, False, False, 3)
        panel.pack_start(self.status_interface_label, False, False, 3)
        panel.pack_start(self.status_endpoint_label, False, False, 3)
        panel.pack_start(self.status_uptime_label, False, False, 3)
        panel.pack_start(self.status_stealth_label, False, False, 3)

        # Quality bar with status indicator
        quality_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        
        quality_header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        quality_label = Gtk.Label(label="CONNECTION QUALITY")
        quality_label.get_style_context().add_class("metric-label")
        quality_label.set_xalign(0)
        
        self.quality_status_label = Gtk.Label(label="● UNKNOWN")
        self.quality_status_label.set_xalign(1)
        
        quality_header.pack_start(quality_label, True, True, 0)
        quality_header.pack_start(self.quality_status_label, False, False, 0)

        self.quality_progress = Gtk.ProgressBar()
        self.quality_progress.set_fraction(0.0)
        self.quality_progress.set_text("Not Connected")
        self.quality_progress.set_show_text(True)

        quality_box.pack_start(quality_header, False, False, 0)
        quality_box.pack_start(self.quality_progress, False, False, 0)
        panel.pack_start(quality_box, False, False, 5)

        self.panel = panel
        return panel
    
    def update_status(self, connection_state, interface, uptime, stealth_active):
        """Update connection status display"""
        if not self.panel:
            return
            
        # Update status labels (delegate to parent's update methods)
        # The actual update logic will remain in the main window
        # This method serves as a clean interface for updates
        pass
    
    def update_quality(self, quality_score, quality_text, quality_color):
        """Update connection quality display"""
        if not self.quality_progress:
            return
            
        self.quality_progress.set_fraction(quality_score)
        self.quality_progress.set_text(quality_text)
        
        if self.quality_status_label:
            self.quality_status_label.set_markup(f"● <span color='{quality_color}'>{quality_text}</span>")
    
    def get_widget(self):
        """Get the panel widget"""
        if not self.panel:
            self.build_panel()
        return self.panel