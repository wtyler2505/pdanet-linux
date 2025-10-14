"""
Log Panel for PdaNet Linux GUI
Enhanced system log panel with filtering, search, and export functionality
"""

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

from theme import Colors


class LogPanel:
    """
    System log display and management panel
    Shows filtered, searchable system logs with export capabilities
    """
    
    def __init__(self, parent_window):
        """Initialize log panel"""
        self.parent = parent_window
        self.panel = None
        
        # Log components (will be created by build_panel)
        self.log_textview = None
        self.log_buffer = None
        self.log_line_numbers = None
        self.log_line_numbers_buffer = None
        self.log_search_entry = None
        self.log_filters = {"DEBUG": False, "INFO": True, "OK": True, "WARN": True, "ERROR": True}
        self.last_log_count = 0
    
    def build_panel(self):
        """Build enhanced system log panel with filtering and controls"""
        if self.panel:
            return self.panel
            
        panel = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=1)
        panel.get_style_context().add_class("panel")

        # Header with controls
        header_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)

        header = Gtk.Label(label="SYSTEM LOG")
        header.get_style_context().add_class("panel-header")
        header.set_xalign(0)
        header_box.pack_start(header, True, True, 0)

        # Log level filters
        filter_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=3)
        for level in ["DEBUG", "INFO", "OK", "WARN", "ERROR"]:
            btn = Gtk.ToggleButton(label=level[:1])  # Single letter
            btn.set_active(self.log_filters[level])
            btn.set_tooltip_text(f"Show {level} logs")
            btn.connect("toggled", self.on_log_filter_toggled, level)
            filter_box.pack_start(btn, False, False, 0)

        header_box.pack_start(filter_box, False, False, 5)
        panel.pack_start(header_box, False, False, 0)

        # Search bar
        search_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        self.log_search_entry = Gtk.Entry()
        self.log_search_entry.set_placeholder_text("Search logs...")
        self.log_search_entry.connect("changed", self.on_log_search_changed)
        search_box.pack_start(self.log_search_entry, True, True, 0)

        clear_search_btn = Gtk.Button(label="×")
        clear_search_btn.set_tooltip_text("Clear search")
        clear_search_btn.connect("clicked", lambda b: self.log_search_entry.set_text(""))
        search_box.pack_start(clear_search_btn, False, False, 0)

        panel.pack_start(search_box, False, False, 0)

        # Log viewer with line numbers
        log_view_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)

        # Line numbers TextView
        self.log_line_numbers = Gtk.TextView()
        self.log_line_numbers.set_editable(False)
        self.log_line_numbers.set_cursor_visible(False)
        self.log_line_numbers.set_size_request(40, -1)
        self.log_line_numbers.set_monospace(True)
        self.log_line_numbers_buffer = self.log_line_numbers.get_buffer()
        self.log_line_numbers_buffer.create_tag("line_num", foreground=Colors.TEXT_GRAY)

        # Main log TextView
        self.log_textview = Gtk.TextView()
        self.log_textview.set_editable(False)
        self.log_textview.set_cursor_visible(False)
        self.log_textview.set_vexpand(True)
        self.log_textview.set_monospace(True)
        self.log_textview.set_wrap_mode(Gtk.WrapMode.NONE)
        self.log_buffer = self.log_textview.get_buffer()

        # Create tags for different log levels with symbols
        self.log_buffer.create_tag("debug", foreground=Colors.TEXT_GRAY)
        self.log_buffer.create_tag("info", foreground=Colors.TEXT_GRAY)
        self.log_buffer.create_tag("ok", foreground=Colors.GREEN_DIM)
        self.log_buffer.create_tag("warn", foreground=Colors.ORANGE)
        self.log_buffer.create_tag("error", foreground=Colors.RED_DIM)
        self.log_buffer.create_tag("timestamp", foreground=Colors.TEXT_GRAY)

        # Synchronized scrolling
        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scroll.set_hexpand(True)
        scroll.set_vexpand(True)

        scroll_lines = Gtk.ScrolledWindow()
        scroll_lines.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scroll_lines.set_hexpand(False)
        scroll_lines.set_vexpand(True)
        scroll_lines.add(self.log_line_numbers)

        # Sync scrolling
        vadj = scroll.get_vadjustment()
        scroll_lines.set_vadjustment(vadj)

        log_view_box.pack_start(scroll_lines, False, False, 0)
        scroll.add(self.log_textview)
        log_view_box.pack_start(scroll, True, True, 0)

        panel.pack_start(log_view_box, True, True, 0)

        # Control buttons
        btn_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=3)

        copy_btn = Gtk.Button(label="Copy")
        copy_btn.set_tooltip_text("Copy visible logs to clipboard")
        copy_btn.connect("clicked", self.on_copy_logs)
        btn_box.pack_start(copy_btn, True, True, 0)

        export_btn = Gtk.Button(label="Export")
        export_btn.set_tooltip_text("Export logs to file")
        export_btn.connect("clicked", self.on_export_logs)
        btn_box.pack_start(export_btn, True, True, 0)

        clear_btn = Gtk.Button(label="Clear")
        clear_btn.set_tooltip_text("Clear log buffer")
        clear_btn.connect("clicked", self.on_clear_logs)
        btn_box.pack_start(clear_btn, True, True, 0)

        panel.pack_start(btn_box, False, False, 0)

        self.panel = panel
        return panel
    
    def on_log_filter_toggled(self, button, level):
        """Handle log filter toggle"""
        self.log_filters[level] = button.get_active()
        # Delegate to parent for actual filtering logic
        if hasattr(self.parent, 'on_log_filter_toggled'):
            self.parent.on_log_filter_toggled(button, level)
    
    def on_log_search_changed(self, entry):
        """Handle log search change"""
        # Delegate to parent for actual search logic
        if hasattr(self.parent, 'on_log_search_changed'):
            self.parent.on_log_search_changed(entry)
    
    def on_copy_logs(self, button):
        """Handle copy logs button"""
        # Delegate to parent
        if hasattr(self.parent, 'on_copy_logs'):
            self.parent.on_copy_logs(button)
    
    def on_export_logs(self, button):
        """Handle export logs button"""
        # Delegate to parent
        if hasattr(self.parent, 'on_export_logs'):
            self.parent.on_export_logs(button)
    
    def on_clear_logs(self, button):
        """Handle clear logs button"""
        # Delegate to parent
        if hasattr(self.parent, 'on_clear_logs'):
            self.parent.on_clear_logs(button)
    
    def update_logs(self, log_data):
        """Update log display"""
        # The actual log update logic will remain in the main window
        # This method serves as a clean interface for updates
        pass
    
    def get_widget(self):
        """Get the panel widget"""
        if not self.panel:
            self.build_panel()
        return self.panel