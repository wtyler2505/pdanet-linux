"""
Circular Progress Widget for Data Usage Display
"""

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk
import cairo
import math


class CircularProgress(Gtk.DrawingArea):
    """
    Circular progress meter widget
    Shows percentage with colored arc
    """
    
    def __init__(self, size=150):
        super().__init__()
        
        self.percentage = 0.0  # 0.0 to 1.0
        self.size = size
        self.text = "0%"
        self.subtitle = ""
        
        # Colors
        self.bg_color = (0.1, 0.1, 0.1)      # Dark background
        self.track_color = (0.2, 0.2, 0.2)   # Track (unfilled)
        self.progress_color = (0.0, 1.0, 0.0) # Progress (green)
        self.warning_color = (1.0, 1.0, 0.0)  # Warning (yellow)
        self.critical_color = (1.0, 0.0, 0.0) # Critical (red)
        self.text_color = (1.0, 1.0, 1.0)    # White text
        
        # Thresholds
        self.warning_threshold = 0.7   # 70%
        self.critical_threshold = 0.9  # 90%
        
        self.set_size_request(size, size)
        self.connect("draw", self._on_draw)
    
    def set_percentage(self, percentage: float):
        """Set progress percentage (0.0 to 1.0)"""
        self.percentage = max(0.0, min(1.0, percentage))
        self.text = f"{int(self.percentage * 100)}%"
        self.queue_draw()
    
    def set_text(self, text: str):
        """Set center text"""
        self.text = text
        self.queue_draw()
    
    def set_subtitle(self, subtitle: str):
        """Set subtitle below main text"""
        self.subtitle = subtitle
        self.queue_draw()
    
    def set_colors(self, progress=None, warning=None, critical=None):
        """Set custom colors"""
        if progress:
            self.progress_color = progress
        if warning:
            self.warning_color = warning
        if critical:
            self.critical_color = critical
        self.queue_draw()
    
    def _on_draw(self, widget, cr):
        """Draw the circular progress"""
        # Get widget dimensions
        width = widget.get_allocated_width()
        height = widget.get_allocated_height()
        
        # Center point
        cx = width / 2
        cy = height / 2
        
        # Radius
        radius = min(width, height) / 2 - 10
        
        # Line width
        line_width = 12
        
        # Background
        cr.set_source_rgb(*self.bg_color)
        cr.paint()
        
        # Track (full circle, unfilled)
        cr.set_line_width(line_width)
        cr.set_source_rgb(*self.track_color)
        cr.arc(cx, cy, radius, 0, 2 * math.pi)
        cr.stroke()
        
        # Progress arc
        if self.percentage > 0:
            # Choose color based on percentage
            if self.percentage >= self.critical_threshold:
                color = self.critical_color
            elif self.percentage >= self.warning_threshold:
                color = self.warning_color
            else:
                color = self.progress_color
            
            cr.set_source_rgb(*color)
            cr.set_line_width(line_width)
            cr.set_line_cap(cairo.LINE_CAP_ROUND)
            
            # Draw arc from top (-90 degrees) clockwise
            start_angle = -math.pi / 2
            end_angle = start_angle + (2 * math.pi * self.percentage)
            
            cr.arc(cx, cy, radius, start_angle, end_angle)
            cr.stroke()
        
        # Center text
        cr.set_source_rgb(*self.text_color)
        cr.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        
        # Main text
        cr.set_font_size(32)
        extents = cr.text_extents(self.text)
        text_x = cx - extents.width / 2
        text_y = cy + extents.height / 2
        
        if self.subtitle:
            text_y -= 10  # Move up if subtitle present
        
        cr.move_to(text_x, text_y)
        cr.show_text(self.text)
        
        # Subtitle
        if self.subtitle:
            cr.set_font_size(14)
            cr.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
            extents = cr.text_extents(self.subtitle)
            subtitle_x = cx - extents.width / 2
            subtitle_y = cy + extents.height / 2 + 15
            cr.move_to(subtitle_x, subtitle_y)
            cr.show_text(self.subtitle)
        
        return False
