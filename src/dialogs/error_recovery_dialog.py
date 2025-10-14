"""
Error Recovery Dialog for PdaNet Linux
Shows user-friendly error messages with actionable solutions
"""

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib
import subprocess
from typing import Optional

from error_database import get_error_info, ErrorInfo, ErrorSolution
from logger import get_logger


class ErrorRecoveryDialog(Gtk.Dialog):
    """Dialog for displaying errors with recovery solutions"""
    
    def __init__(self, parent, error_code: str, error_message: str = "", details: str = ""):
        super().__init__(
            title="Error Recovery",
            parent=parent,
            flags=Gtk.DialogFlags.MODAL
        )
        
        self.logger = get_logger()
        self.error_code = error_code
        self.error_message = error_message
        self.details = details
        
        # Get error info from database
        self.error_info = get_error_info(error_code)
        
        if not self.error_info:
            # Unknown error - create generic info
            self.error_info = self._create_generic_error_info()
        
        self.set_default_size(700, 500)
        self._build_ui()
        
        self.add_button("Close", Gtk.ResponseType.CLOSE)
        self.show_all()
    
    def _create_generic_error_info(self) -> ErrorInfo:
        """Create generic error info for unknown errors"""
        from error_database import ErrorInfo, ErrorSolution
        
        return ErrorInfo(
            code=self.error_code,
            title="Unknown Error",
            description=self.error_message or "An error occurred",
            category="system",
            severity="medium",
            solutions=[
                ErrorSolution(
                    title="Check Logs",
                    steps=[
                        "View application logs for details",
                        "Run: tail -f ~/.config/pdanet-linux/pdanet.log",
                        "Look for error messages before this occurred"
                    ]
                ),
                ErrorSolution(
                    title="Restart Application",
                    steps=[
                        "Close PdaNet Linux",
                        "Wait 5 seconds",
                        "Launch PdaNet Linux again",
                        "Try the operation again"
                    ]
                ),
                ErrorSolution(
                    title="Report Bug",
                    steps=[
                        "This may be a bug",
                        "Copy error details below",
                        "Report at: github.com/yourusername/pdanet-linux/issues",
                        "Include error code and message"
                    ]
                )
            ]
        )
    
    def _build_ui(self):
        """Build the error recovery UI"""
        content = self.get_content_area()
        content.set_spacing(15)
        content.set_border_width(20)
        
        # Error header with icon
        header_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=15)
        
        # Error icon
        icon = Gtk.Image.new_from_icon_name("dialog-error", Gtk.IconSize.DIALOG)
        header_box.pack_start(icon, False, False, 0)
        
        # Error title and description
        text_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        
        title = Gtk.Label()
        title.set_markup(f'<span size="large" weight="bold">{self.error_info.title}</span>')
        title.set_halign(Gtk.Align.START)
        title.set_line_wrap(True)
        text_box.pack_start(title, False, False, 0)
        
        description = Gtk.Label(label=self.error_info.description)
        description.set_halign(Gtk.Align.START)
        description.set_line_wrap(True)
        description.set_max_width_chars(60)
        text_box.pack_start(description, False, False, 0)
        
        # Error metadata
        meta = Gtk.Label()
        meta.set_markup(
            f'<span size="small">Category: {self.error_info.category.title()} | '
            f'Severity: {self.error_info.severity.title()} | '
            f'Code: {self.error_info.code}</span>'
        )
        meta.set_halign(Gtk.Align.START)
        text_box.pack_start(meta, False, False, 0)
        
        header_box.pack_start(text_box, True, True, 0)
        content.pack_start(header_box, False, False, 0)
        
        # Separator
        sep = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        content.pack_start(sep, False, False, 0)
        
        # Solutions notebook
        solutions_label = Gtk.Label()
        solutions_label.set_markup('<b>Possible Solutions:</b>')
        solutions_label.set_halign(Gtk.Align.START)
        content.pack_start(solutions_label, False, False, 0)
        
        notebook = Gtk.Notebook()
        notebook.set_tab_pos(Gtk.PositionType.LEFT)
        
        for i, solution in enumerate(self.error_info.solutions):
            page = self._create_solution_page(solution)
            label = Gtk.Label(label=f"Solution {i+1}")
            notebook.append_page(page, label)
        
        content.pack_start(notebook, True, True, 0)
        
        # Error details expander
        if self.details or self.error_message:
            expander = Gtk.Expander(label="Technical Details")
            details_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
            
            if self.error_message:
                msg_label = Gtk.Label()
                msg_label.set_markup(f'<b>Error Message:</b>\n{self.error_message}')
                msg_label.set_halign(Gtk.Align.START)
                msg_label.set_line_wrap(True)
                msg_label.set_selectable(True)
                details_box.pack_start(msg_label, False, False, 0)
            
            if self.details:
                details_label = Gtk.Label()
                details_label.set_markup(f'<b>Details:</b>\n{self.details}')
                details_label.set_halign(Gtk.Align.START)
                details_label.set_line_wrap(True)
                details_label.set_selectable(True)
                details_box.pack_start(details_label, False, False, 0)
            
            # Copy button
            copy_btn = Gtk.Button(label="Copy Error Details")
            copy_btn.connect("clicked", self._on_copy_details)
            details_box.pack_start(copy_btn, False, False, 5)
            
            expander.add(details_box)
            content.pack_start(expander, False, False, 0)
    
    def _create_solution_page(self, solution: ErrorSolution) -> Gtk.Widget:
        """Create a page for a solution"""
        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        box.set_border_width(15)
        
        # Solution title
        title = Gtk.Label()
        title.set_markup(f'<span size="large" weight="bold">{solution.title}</span>')
        title.set_halign(Gtk.Align.START)
        box.pack_start(title, False, False, 0)
        
        # Steps
        steps_label = Gtk.Label()
        steps_label.set_markup('<b>Steps to resolve:</b>')
        steps_label.set_halign(Gtk.Align.START)
        box.pack_start(steps_label, False, False, 0)
        
        for i, step in enumerate(solution.steps, 1):
            step_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
            
            # Step number
            num_label = Gtk.Label()
            num_label.set_markup(f'<b>{i}.</b>')
            num_label.set_halign(Gtk.Align.START)
            num_label.set_valign(Gtk.Align.START)
            step_box.pack_start(num_label, False, False, 0)
            
            # Step text
            text_label = Gtk.Label(label=step)
            text_label.set_halign(Gtk.Align.START)
            text_label.set_line_wrap(True)
            text_label.set_max_width_chars(50)
            step_box.pack_start(text_label, True, True, 0)
            
            box.pack_start(step_box, False, False, 0)
        
        # Auto-fix button if available
        if solution.auto_fix_command:
            sep = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
            box.pack_start(sep, False, False, 5)
            
            fix_label = Gtk.Label()
            fix_label.set_markup('<b>Automatic Fix Available:</b>')
            fix_label.set_halign(Gtk.Align.START)
            box.pack_start(fix_label, False, False, 0)
            
            fix_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
            
            fix_btn = Gtk.Button(label="🔧 Apply Auto-Fix")
            fix_btn.connect("clicked", self._on_auto_fix, solution)
            fix_box.pack_start(fix_btn, False, False, 0)
            
            if solution.requires_root:
                warning = Gtk.Label()
                warning.set_markup('<span foreground="#FF0000"><i>Requires root privileges</i></span>')
                fix_box.pack_start(warning, False, False, 0)
            
            box.pack_start(fix_box, False, False, 0)
            
            # Command preview
            cmd_label = Gtk.Label()
            cmd_label.set_markup(f'<span font="monospace" size="small">Command: {solution.auto_fix_command}</span>')
            cmd_label.set_halign(Gtk.Align.START)
            cmd_label.set_selectable(True)
            box.pack_start(cmd_label, False, False, 0)
            
            # Status label
            status_label = Gtk.Label()
            status_label.set_halign(Gtk.Align.START)
            status_label.set_no_show_all(True)
            box.pack_start(status_label, False, False, 0)
            
            # Store reference for auto-fix callback
            solution._status_label = status_label
        
        scroll.add(box)
        return scroll
    
    def _on_auto_fix(self, button, solution: ErrorSolution):
        """Handle auto-fix button click"""
        # Disable button during execution
        button.set_sensitive(False)
        button.set_label("⏳ Applying fix...")
        
        def run_fix():
            try:
                if solution.requires_root:
                    # Run with pkexec
                    cmd = ["pkexec"] + solution.auto_fix_command.split()
                else:
                    cmd = solution.auto_fix_command.split()
                
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                def update_ui():
                    if result.returncode == 0:
                        solution._status_label.set_markup(
                            '<span foreground="#00FF00">✓ Fix applied successfully!</span>'
                        )
                        solution._status_label.show()
                        button.set_label("✓ Applied")
                        self.logger.info(f"Auto-fix applied: {solution.auto_fix_command}")
                    else:
                        solution._status_label.set_markup(
                            f'<span foreground="#FF0000">✗ Fix failed: {result.stderr[:100]}</span>'
                        )
                        solution._status_label.show()
                        button.set_label("🔧 Apply Auto-Fix")
                        button.set_sensitive(True)
                        self.logger.error(f"Auto-fix failed: {result.stderr}")
                    return False
                
                GLib.idle_add(update_ui)
                
            except subprocess.TimeoutExpired:
                def timeout_ui():
                    solution._status_label.set_markup(
                        '<span foreground="#FF0000">✗ Fix timed out</span>'
                    )
                    solution._status_label.show()
                    button.set_label("🔧 Apply Auto-Fix")
                    button.set_sensitive(True)
                    return False
                GLib.idle_add(timeout_ui)
                
            except Exception as e:
                def error_ui():
                    solution._status_label.set_markup(
                        f'<span foreground="#FF0000">✗ Error: {str(e)}</span>'
                    )
                    solution._status_label.show()
                    button.set_label("🔧 Apply Auto-Fix")
                    button.set_sensitive(True)
                    return False
                GLib.idle_add(error_ui)
        
        # Run in thread to avoid blocking UI
        import threading
        thread = threading.Thread(target=run_fix)
        thread.daemon = True
        thread.start()
    
    def _on_copy_details(self, button):
        """Copy error details to clipboard"""
        details_text = f"""Error Code: {self.error_info.code}
Title: {self.error_info.title}
Category: {self.error_info.category}
Severity: {self.error_info.severity}

Description:
{self.error_info.description}

Error Message:
{self.error_message}

Details:
{self.details}
"""
        
        clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
        clipboard.set_text(details_text, -1)
        
        button.set_label("✓ Copied!")
        GLib.timeout_add_seconds(2, lambda: button.set_label("Copy Error Details"))


# Convenience function for showing errors
def show_error_dialog(parent, error_code: str, error_message: str = "", details: str = ""):
    """
    Show error recovery dialog
    
    Args:
        parent: Parent window
        error_code: Error code from error_database
        error_message: Optional error message
        details: Optional technical details
    """
    dialog = ErrorRecoveryDialog(parent, error_code, error_message, details)
    dialog.run()
    dialog.destroy()
