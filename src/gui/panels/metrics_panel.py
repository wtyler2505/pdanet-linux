"""
Metrics Panel for PdaNet Linux GUI
Displays network metrics, bandwidth graphs, and data usage dashboard
"""

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

from widgets.data_dashboard import DataUsageDashboard


class MetricsPanel:
    """
    Network metrics and data usage panel
    Shows download/upload speeds, latency, packet loss, and bandwidth graphs
    """
    
    def __init__(self, parent_window):
        """Initialize metrics panel"""
        self.parent = parent_window
        self.panel = None
        
        # Metric labels (will be created by build_panel)
        self.metric_download_label = None
        self.metric_upload_label = None
        self.metric_latency_label = None
        self.metric_loss_label = None
        self.metric_total_label = None
        self.graph_textview = None
        self.graph_buffer = None
        self.data_dashboard = None
    
    def build_panel(self):
        """Build enhanced metrics panel with integrated Data Usage Dashboard"""
        if self.panel:
            return self.panel
            
        # Create notebook for tabs
        notebook = Gtk.Notebook()
        notebook.set_scrollable(True)
        notebook.get_style_context().add_class("panel")
        
        # Tab 1: Network Metrics (existing)
        metrics_content = self._build_metrics_content()
        metrics_label = Gtk.Label(label="METRICS")
        metrics_label.get_style_context().add_class("tab-label")
        notebook.append_page(metrics_content, metrics_label)
        
        # Tab 2: Data Usage Dashboard (new)
        dashboard_content = self._build_data_dashboard_content()
        dashboard_label = Gtk.Label(label="DATA USAGE")
        dashboard_label.get_style_context().add_class("tab-label")
        notebook.append_page(dashboard_content, dashboard_label)
        
        self.panel = notebook
        return notebook
    
    def _build_metrics_content(self):
        """Build the metrics content"""
        panel = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        
        # Metrics
        self.metric_download_label = self.parent.create_metric_row("↓ DOWN", "0.0 KB/s")
        self.metric_upload_label = self.parent.create_metric_row("↑ UP", "0.0 KB/s")
        self.metric_latency_label = self.parent.create_metric_row("LATENCY", "-- ms")
        self.metric_loss_label = self.parent.create_metric_row("LOSS", "-- %")
        self.metric_total_label = self.parent.create_metric_row("TOTAL", "↓ 0B  ↑ 0B")

        panel.pack_start(self.metric_download_label, False, False, 3)
        panel.pack_start(self.metric_upload_label, False, False, 3)
        panel.pack_start(self.metric_latency_label, False, False, 3)
        panel.pack_start(self.metric_loss_label, False, False, 3)
        panel.pack_start(self.metric_total_label, False, False, 3)

        # Simple bandwidth graph placeholder
        graph_label = Gtk.Label(label="BANDWIDTH GRAPH")
        graph_label.get_style_context().add_class("metric-label")
        graph_label.set_xalign(0)
        panel.pack_start(graph_label, False, False, 5)

        self.graph_textview = Gtk.TextView()
        self.graph_textview.set_editable(False)
        self.graph_textview.set_cursor_visible(False)
        self.graph_textview.set_monospace(True)
        self.graph_buffer = self.graph_textview.get_buffer()

        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.NEVER)
        scroll.add(self.graph_textview)
        panel.pack_start(scroll, False, False, 0)

        return panel
    
    def _build_data_dashboard_content(self):
        """Build the Data Usage Dashboard content"""
        try:
            # Create and configure the dashboard
            self.data_dashboard = DataUsageDashboard(
                config_manager=self.parent.config,
                stats_collector=self.parent.stats
            )
            
            # Wrap in a container to handle any sizing issues
            container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
            container.pack_start(self.data_dashboard, True, True, 0)
            
            return container
            
        except Exception as e:
            self.parent.logger.error(f"Failed to create data dashboard: {e}")
            # Fallback to error message
            error_label = Gtk.Label(label=f"Data Dashboard Error: {e}")
            error_label.get_style_context().add_class("error-text")
            return error_label
    
    def update_metrics(self, download_speed, upload_speed, latency, loss, total_down, total_up):
        """Update network metrics display"""
        if not self.panel:
            return
            
        # Update metric labels (delegate to parent's update methods)
        # The actual update logic will remain in the main window
        pass
    
    def update_graph(self, graph_data):
        """Update bandwidth graph"""
        if not self.graph_buffer:
            return
            
        self.graph_buffer.set_text(graph_data)
    
    def get_widget(self):
        """Get the panel widget"""
        if not self.panel:
            self.build_panel()
        return self.panel