"""
Data Usage Dashboard Widget
"""

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib
from datetime import datetime
import json
from pathlib import Path

from widgets.circular_progress import CircularProgress
from constants import *
from logger import get_logger


class DataUsageDashboard(Gtk.Box):
    """
    Data usage dashboard with visual meter and statistics
    """
    
    def __init__(self, config_manager, stats_collector):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        
        self.config = config_manager
        self.stats = stats_collector
        self.logger = get_logger()
        
        # Data tracking
        self.session_bytes = 0
        self.daily_bytes = 0
        self.monthly_bytes = 0
        
        # Load saved usage data
        self._load_usage_data()
        
        # Build UI
        self._build_ui()
        
        # Start update timer
        GLib.timeout_add_seconds(5, self._update_display)
    
    def _build_ui(self):
        """Build dashboard UI"""
        self.set_border_width(10)
        
        # Header
        header = Gtk.Label()
        header.set_markup('<span size="large" weight="bold">DATA USAGE</span>')
        header.set_halign(Gtk.Align.START)
        self.pack_start(header, False, False, 0)
        
        # Circular progress meter
        self.progress_meter = CircularProgress(size=180)
        meter_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        meter_box.set_center_widget(self.progress_meter)
        self.pack_start(meter_box, False, False, 10)
        
        # Stats grid
        grid = Gtk.Grid()
        grid.set_row_spacing(8)
        grid.set_column_spacing(20)
        grid.set_halign(Gtk.Align.CENTER)
        
        row = 0
        
        # Session data
        self._add_stat_row(grid, row, "Session:", "0 MB")
        self.session_label = grid.get_child_at(1, row)
        row += 1
        
        # Today
        self._add_stat_row(grid, row, "Today:", "0 MB")
        self.daily_label = grid.get_child_at(1, row)
        row += 1
        
        # This month
        self._add_stat_row(grid, row, "This Month:", "0 MB")
        self.monthly_label = grid.get_child_at(1, row)
        row += 1
        
        # Threshold
        threshold_gb = self.config.get("data_warning_threshold_gb", 10)
        self._add_stat_row(grid, row, "Warning at:", f"{threshold_gb} GB")
        self.threshold_label = grid.get_child_at(1, row)
        row += 1
        
        self.pack_start(grid, False, False, 10)
        
        # Buttons
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        button_box.set_halign(Gtk.Align.CENTER)
        
        reset_btn = Gtk.Button(label="Reset Session")
        reset_btn.connect("clicked", self._on_reset_session)
        button_box.pack_start(reset_btn, False, False, 0)
        
        reset_monthly_btn = Gtk.Button(label="Reset Monthly")
        reset_monthly_btn.connect("clicked", self._on_reset_monthly)
        button_box.pack_start(reset_monthly_btn, False, False, 0)
        
        export_btn = Gtk.Button(label="Export History")
        export_btn.connect("clicked", self._on_export)
        button_box.pack_start(export_btn, False, False, 0)
        
        self.pack_start(button_box, False, False, 0)
    
    def _add_stat_row(self, grid, row, label_text, value_text):
        """Add a statistics row to grid"""
        label = Gtk.Label()
        label.set_markup(f'<b>{label_text}</b>')
        label.set_halign(Gtk.Align.END)
        grid.attach(label, 0, row, 1, 1)
        
        value = Gtk.Label(label=value_text)
        value.set_halign(Gtk.Align.START)
        grid.attach(value, 1, row, 1, 1)
    
    def _update_display(self):
        """Update display with current statistics"""
        try:
            # Get current session data
            current_bytes = self.stats.total_bytes_received + self.stats.total_bytes_sent
            self.session_bytes = current_bytes
            
            # Update labels
            self.session_label.set_text(self._format_bytes(self.session_bytes))
            self.daily_label.set_text(self._format_bytes(self.daily_bytes))
            self.monthly_label.set_text(self._format_bytes(self.monthly_bytes))
            
            # Update progress meter
            threshold_bytes = self.config.get("data_warning_threshold_gb", 10) * BYTES_PER_GB
            percentage = min(1.0, self.monthly_bytes / threshold_bytes) if threshold_bytes > 0 else 0
            
            self.progress_meter.set_percentage(percentage)
            self.progress_meter.set_subtitle(self._format_bytes(self.monthly_bytes))
            
            # Check for warnings
            if percentage >= 0.9:
                self._show_warning("Critical", "90% of data limit reached!")
            elif percentage >= 0.7:
                self._show_warning("Warning", "70% of data limit reached")
            
            # Save data periodically
            self._save_usage_data()
            
        except Exception as e:
            self.logger.error(f"Error updating data dashboard: {e}")
        
        return True  # Continue timer
    
    def _format_bytes(self, bytes_val):
        """Format bytes to human-readable string"""
        if bytes_val >= BYTES_PER_GB:
            return f"{bytes_val / BYTES_PER_GB:.2f} GB"
        elif bytes_val >= BYTES_PER_MB:
            return f"{bytes_val / BYTES_PER_MB:.2f} MB"
        elif bytes_val >= BYTES_PER_KB:
            return f"{bytes_val / BYTES_PER_KB:.2f} KB"
        else:
            return f"{bytes_val} B"
    
    def _load_usage_data(self):
        """Load saved usage data"""
        try:
            usage_file = Path.home() / ".config" / "pdanet-linux" / "data_usage.json"
            if usage_file.exists():
                with open(usage_file) as f:
                    data = json.load(f)
                    
                    # Check if data is from today
                    today = datetime.now().strftime("%Y-%m-%d")
                    if data.get("date") == today:
                        self.daily_bytes = data.get("daily_bytes", 0)
                    
                    # Check if data is from this month
                    this_month = datetime.now().strftime("%Y-%m")
                    if data.get("month") == this_month:
                        self.monthly_bytes = data.get("monthly_bytes", 0)
                        
        except Exception as e:
            self.logger.error(f"Failed to load usage data: {e}")
    
    def _save_usage_data(self):
        """Save usage data to file"""
        try:
            usage_file = Path.home() / ".config" / "pdanet-linux" / "data_usage.json"
            usage_file.parent.mkdir(parents=True, exist_ok=True)
            
            data = {
                "date": datetime.now().strftime("%Y-%m-%d"),
                "month": datetime.now().strftime("%Y-%m"),
                "daily_bytes": self.daily_bytes + self.session_bytes,
                "monthly_bytes": self.monthly_bytes + self.session_bytes,
                "last_updated": datetime.now().isoformat()
            }
            
            with open(usage_file, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            self.logger.error(f"Failed to save usage data: {e}")
    
    def _show_warning(self, title, message):
        """Show data usage warning"""
        # Only show if warnings enabled
        if not self.config.get("enable_data_warnings", True):
            return
        
        # TODO: Show desktop notification
        self.logger.warning(f"Data usage warning: {message}")
    
    def _on_reset_session(self, button):
        """Reset session counter"""
        self.session_bytes = 0
        self.stats.reset()
        self._update_display()
        self.logger.info("Session data usage reset")
    
    def _on_reset_monthly(self, button):
        """Reset monthly counter"""
        dialog = Gtk.MessageDialog(
            transient_for=self.get_toplevel(),
            flags=0,
            message_type=Gtk.MessageType.QUESTION,
            buttons=Gtk.ButtonsType.YES_NO,
            text="Reset Monthly Usage?"
        )
        dialog.format_secondary_text(
            "This will reset the monthly data usage counter to zero. "
            "Are you sure?"
        )
        
        response = dialog.run()
        dialog.destroy()
        
        if response == Gtk.ResponseType.YES:
            self.monthly_bytes = 0
            self.daily_bytes = 0
            self._save_usage_data()
            self._update_display()
            self.logger.info("Monthly data usage reset")
    
    def _on_export(self, button):
        """Export usage history"""
        dialog = Gtk.FileChooserDialog(
            title="Export Data Usage",
            parent=self.get_toplevel(),
            action=Gtk.FileChooserAction.SAVE
        )
        dialog.add_buttons(
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
            Gtk.STOCK_SAVE, Gtk.ResponseType.OK
        )
        dialog.set_current_name("pdanet_data_usage.json")
        
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            filename = dialog.get_filename()
            try:
                export_data = {
                    "export_date": datetime.now().isoformat(),
                    "session_bytes": self.session_bytes,
                    "daily_bytes": self.daily_bytes,
                    "monthly_bytes": self.monthly_bytes,
                    "session_formatted": self._format_bytes(self.session_bytes),
                    "daily_formatted": self._format_bytes(self.daily_bytes),
                    "monthly_formatted": self._format_bytes(self.monthly_bytes)
                }
                
                with open(filename, 'w') as f:
                    json.dump(export_data, f, indent=2)
                
                self.logger.info(f"Data usage exported to {filename}")
                
            except Exception as e:
                self.logger.error(f"Failed to export data usage: {e}")
        
        dialog.destroy()
