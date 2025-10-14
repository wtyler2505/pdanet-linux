"""
Reusable setting widgets for PdaNet Linux
"""

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from typing import Optional, List, Tuple


class SettingRow:
    """
    Represents a setting row with label and widget
    Makes it easy to create consistent settings UI
    """
    
    def __init__(self, label: str, widget: Gtk.Widget, tooltip: Optional[str] = None):
        self.label_text = label
        self.widget = widget
        self.tooltip = tooltip
        
        # Create label
        self.label = Gtk.Label(label=label)
        self.label.set_halign(Gtk.Align.START)
        self.label.set_hexpand(False)
        
        if tooltip:
            self.label.set_tooltip_text(tooltip)
            self.widget.set_tooltip_text(tooltip)
    
    def attach_to_grid(self, grid: Gtk.Grid, row: int):
        """Attach this setting row to a grid at specified row"""
        grid.attach(self.label, 0, row, 1, 1)
        grid.attach(self.widget, 1, row, 1, 1)


def create_label_entry(
    label: str,
    placeholder: str = "",
    tooltip: Optional[str] = None,
    default_value: str = ""
) -> Tuple[Gtk.Label, Gtk.Entry]:
    """
    Create a label + entry widget pair
    
    Args:
        label: Label text
        placeholder: Placeholder text for entry
        tooltip: Tooltip text
        default_value: Default entry value
    
    Returns:
        (label_widget, entry_widget)
    """
    label_widget = Gtk.Label(label=label)
    label_widget.set_halign(Gtk.Align.START)
    
    entry = Gtk.Entry()
    entry.set_placeholder_text(placeholder)
    entry.set_text(default_value)
    entry.set_hexpand(True)
    
    if tooltip:
        label_widget.set_tooltip_text(tooltip)
        entry.set_tooltip_text(tooltip)
    
    return label_widget, entry


def create_label_spin(
    label: str,
    min_value: float,
    max_value: float,
    step: float = 1.0,
    default_value: float = 0.0,
    tooltip: Optional[str] = None,
    digits: int = 0
) -> Tuple[Gtk.Label, Gtk.SpinButton]:
    """
    Create a label + spin button widget pair
    
    Args:
        label: Label text
        min_value: Minimum value
        max_value: Maximum value
        step: Step increment
        default_value: Default value
        tooltip: Tooltip text
        digits: Number of decimal places
    
    Returns:
        (label_widget, spin_button_widget)
    """
    label_widget = Gtk.Label(label=label)
    label_widget.set_halign(Gtk.Align.START)
    
    adjustment = Gtk.Adjustment(
        value=default_value,
        lower=min_value,
        upper=max_value,
        step_increment=step,
        page_increment=step * 10
    )
    
    spin = Gtk.SpinButton(adjustment=adjustment)
    spin.set_digits(digits)
    spin.set_hexpand(False)
    spin.set_width_chars(8)
    
    if tooltip:
        label_widget.set_tooltip_text(tooltip)
        spin.set_tooltip_text(tooltip)
    
    return label_widget, spin


def create_label_switch(
    label: str,
    default_state: bool = False,
    tooltip: Optional[str] = None
) -> Tuple[Gtk.Label, Gtk.Switch]:
    """
    Create a label + switch widget pair
    
    Args:
        label: Label text
        default_state: Default switch state
        tooltip: Tooltip text
    
    Returns:
        (label_widget, switch_widget)
    """
    label_widget = Gtk.Label(label=label)
    label_widget.set_halign(Gtk.Align.START)
    
    switch = Gtk.Switch()
    switch.set_active(default_state)
    switch.set_halign(Gtk.Align.START)
    
    if tooltip:
        label_widget.set_tooltip_text(tooltip)
        switch.set_tooltip_text(tooltip)
    
    return label_widget, switch


def create_label_combo(
    label: str,
    options: List[Tuple[str, str]],  # [(id, display_name), ...]
    default_id: Optional[str] = None,
    tooltip: Optional[str] = None
) -> Tuple[Gtk.Label, Gtk.ComboBoxText]:
    """
    Create a label + combo box widget pair
    
    Args:
        label: Label text
        options: List of (id, display_name) tuples
        default_id: Default selected option ID
        tooltip: Tooltip text
    
    Returns:
        (label_widget, combo_widget)
    """
    label_widget = Gtk.Label(label=label)
    label_widget.set_halign(Gtk.Align.START)
    
    combo = Gtk.ComboBoxText()
    combo.set_hexpand(True)
    
    for option_id, display_name in options:
        combo.append(option_id, display_name)
    
    if default_id:
        combo.set_active_id(default_id)
    elif options:
        combo.set_active(0)
    
    if tooltip:
        label_widget.set_tooltip_text(tooltip)
        combo.set_tooltip_text(tooltip)
    
    return label_widget, combo


def create_section_header(text: str) -> Gtk.Label:
    """
    Create a section header label
    
    Args:
        text: Header text
    
    Returns:
        Label widget styled as section header
    """
    label = Gtk.Label()
    label.set_markup(f"<b>{text}</b>")
    label.set_halign(Gtk.Align.START)
    label.set_margin_top(10)
    label.set_margin_bottom(5)
    return label


def create_info_label(text: str) -> Gtk.Label:
    """
    Create an informational label (smaller, gray text)
    
    Args:
        text: Info text
    
    Returns:
        Label widget styled as info
    """
    label = Gtk.Label()
    label.set_markup(f'<span size="small" foreground="#888888">{text}</span>')
    label.set_halign(Gtk.Align.START)
    label.set_line_wrap(True)
    label.set_max_width_chars(60)
    return label
