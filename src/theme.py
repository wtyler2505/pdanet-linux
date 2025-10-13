"""
PdaNet Linux - Cyberpunk Theme
Color scheme and styling based on tactical/hacker interface design

GTK3 CSS CONSTRAINTS (CRITICAL):
==================================

UNSUPPORTED CSS PROPERTIES (will cause runtime errors):
- text-transform: uppercase/lowercase/capitalize - NOT SUPPORTED in GTK3
- letter-spacing: any value - NOT SUPPORTED in GTK3
- text-shadow: any value - NOT SUPPORTED in GTK3
- box-shadow: limited support, often causes issues

DESIGN PRINCIPLES (NON-NEGOTIABLE):
===================================

1. CYBERPUNK AESTHETIC ONLY:
   - Pure black background (#000000) - NO exceptions
   - Monospaced fonts (JetBrains Mono, Fira Code, Courier)
   - Terminal/hacker style interface
   - Green (#00FF00) for success/active
   - Red (#FF0000) for errors/inactive
   - Yellow/Orange for warnings
   - NO gradients, NO rounded corners beyond minimal

2. NO EMOJI POLICY:
   - Professional interface only
   - No emoji in any UI element
   - No decorative unicode characters
   - Terminal-style symbols only (ASCII)

3. PERFORMANCE CONSIDERATIONS:
   - Minimal CSS rules for fast rendering
   - No complex selectors or animations
   - Direct color values (no opacity layers)
   - Hardware-accelerated properties only

4. WORKAROUNDS FOR LIMITATIONS:
   - Use .upper() in Python for uppercase text (not CSS)
   - Use Pango markup for text styling where CSS fails
   - Test all CSS changes in GTK3 environment before deployment

For text transformations, use Python string methods or Pango markup:
- Python: label.set_text(text.upper())
- Pango: label.set_markup('<span size="large">TEXT</span>')
"""


# Color Palette
class Colors:
    # Base
    BLACK = "#000000"
    DARK_GRAY = "#1A1A1A"
    MEDIUM_GRAY = "#2A2A2A"
    BORDER_GRAY = "#333333"
    TEXT_GRAY = "#CCCCCC"
    TEXT_WHITE = "#E0E0E0"

    # Accents
    GREEN = "#00FF00"
    GREEN_DIM = "#00CC00"
    GREEN_DARK = "#008800"

    RED = "#FF0000"
    RED_DIM = "#CC0000"
    RED_DARK = "#880000"

    YELLOW = "#FFB84D"
    ORANGE = "#FFA500"

    # Status
    STATUS_ACTIVE = GREEN
    STATUS_INACTIVE = RED
    STATUS_WARNING = ORANGE
    STATUS_INFO = TEXT_GRAY

    # Legacy aliases for visual testing suite
    BG_PRIMARY = BLACK
    BG_SECONDARY = DARK_GRAY
    SUCCESS = GREEN
    ERROR = RED
    WARNING = YELLOW
    INFO = TEXT_GRAY


# GTK CSS Theme
def get_css():
    return f"""
    * {{
        font-family: "JetBrains Mono", "Fira Code", "Courier New", monospace;
        font-size: 11px;
    }}

    window {{
        background-color: {Colors.BLACK};
        color: {Colors.TEXT_WHITE};
    }}

    .main-container {{
        background-color: {Colors.BLACK};
        border: 1px solid {Colors.BORDER_GRAY};
    }}

    .panel {{
        background-color: {Colors.BLACK};
        border: 1px solid {Colors.MEDIUM_GRAY};
        padding: 10px;
        margin: 5px;
    }}

    .panel-header {{
        color: {Colors.TEXT_WHITE};
        font-weight: bold;
        font-size: 10px;
        padding: 5px;
        border-bottom: 1px solid {Colors.MEDIUM_GRAY};
    }}

    .status-connected {{
        color: {Colors.GREEN};
        font-weight: bold;
    }}

    .status-disconnected {{
        color: {Colors.RED};
        font-weight: bold;
    }}

    .status-warning {{
        color: {Colors.ORANGE};
        font-weight: bold;
    }}

    .metric-label {{
        color: {Colors.TEXT_GRAY};
        font-size: 9px;
    }}

    .metric-value {{
        color: {Colors.TEXT_WHITE};
        font-weight: bold;
        font-size: 12px;
    }}

    .log-entry {{
        font-family: monospace;
        font-size: 10px;
        color: {Colors.TEXT_GRAY};
        padding: 2px 5px;
    }}

    .log-info {{
        color: {Colors.TEXT_GRAY};
    }}

    .log-ok {{
        color: {Colors.GREEN_DIM};
    }}

    .log-warning {{
        color: {Colors.ORANGE};
    }}

    .log-error {{
        color: {Colors.RED_DIM};
    }}

    button {{
        background-color: {Colors.DARK_GRAY};
        color: {Colors.TEXT_WHITE};
        border: 1px solid {Colors.BORDER_GRAY};
        padding: 8px 16px;
        font-size: 10px;
    }}

    button:hover {{
        background-color: {Colors.MEDIUM_GRAY};
        border-color: {Colors.GREEN_DARK};
    }}

    button:active {{
        background-color: {Colors.BLACK};
    }}

    button:disabled {{
        opacity: 0.5;
    }}

    .button-connect {{
        border-color: {Colors.GREEN_DARK};
    }}

    .button-connect:hover {{
        background-color: {Colors.GREEN_DARK};
        color: {Colors.BLACK};
    }}

    .button-disconnect {{
        border-color: {Colors.RED_DARK};
    }}

    .button-disconnect:hover {{
        background-color: {Colors.RED_DARK};
        color: {Colors.BLACK};
    }}

    switch {{
        background-color: {Colors.DARK_GRAY};
        border: 1px solid {Colors.BORDER_GRAY};
    }}

    switch:checked {{
        background-color: {Colors.GREEN_DARK};
        border-color: {Colors.GREEN};
    }}

    switch slider {{
        background-color: {Colors.MEDIUM_GRAY};
    }}

    switch:checked slider {{
        background-color: {Colors.GREEN};
    }}

    entry {{
        background-color: {Colors.DARK_GRAY};
        color: {Colors.TEXT_WHITE};
        border: 1px solid {Colors.BORDER_GRAY};
        padding: 5px;
    }}

    entry:focus {{
        border-color: {Colors.GREEN_DARK};
    }}

    textview {{
        background-color: {Colors.BLACK};
        color: {Colors.TEXT_GRAY};
        font-family: monospace;
        font-size: 10px;
    }}

    textview text {{
        background-color: {Colors.BLACK};
        color: {Colors.TEXT_GRAY};
    }}

    scrollbar {{
        background-color: {Colors.DARK_GRAY};
    }}

    scrollbar slider {{
        background-color: {Colors.MEDIUM_GRAY};
        border: 1px solid {Colors.BORDER_GRAY};
    }}

    scrollbar slider:hover {{
        background-color: {Colors.BORDER_GRAY};
    }}

    .statusbar {{
        background-color: {Colors.DARK_GRAY};
        border-top: 1px solid {Colors.BORDER_GRAY};
        padding: 5px;
        font-size: 9px;
    }}

    .titlebar {{
        background-color: {Colors.BLACK};
        border-bottom: 1px solid {Colors.BORDER_GRAY};
        padding: 8px;
        font-size: 10px;
    }}

    separator {{
        background-color: {Colors.BORDER_GRAY};
        min-width: 1px;
        min-height: 1px;
    }}

    progressbar {{
        background-color: {Colors.DARK_GRAY};
        border: 1px solid {Colors.BORDER_GRAY};
    }}

    progressbar progress {{
        background-color: {Colors.GREEN_DARK};
    }}

    .corner-bracket {{
        color: {Colors.BORDER_GRAY};
        font-size: 14px;
    }}
    """


# UI Text Formatting
class Format:
    @staticmethod
    def bold(text):
        return f"<b>{text}</b>"

    @staticmethod
    def color(text, color_code):
        return f"<span foreground='{color_code}'>{text}</span>"

    @staticmethod
    def monospace(text):
        return f"<span font_family='monospace'>{text}</span>"

    @staticmethod
    def uppercase(text):
        return text.upper() if isinstance(text, str) else text

    @staticmethod
    def status_active():
        return "● ACTIVE"

    @staticmethod
    def status_inactive():
        return "● INACTIVE"

    @staticmethod
    def status_connecting():
        return "◐ CONNECTING"

    @staticmethod
    def format_bandwidth(bytes_per_sec):
        """Format bandwidth in KB/s or MB/s"""
        if bytes_per_sec < 1024:
            return f"{bytes_per_sec:.0f} B/s"
        elif bytes_per_sec < 1024 * 1024:
            return f"{bytes_per_sec / 1024:.1f} KB/s"
        else:
            return f"{bytes_per_sec / (1024 * 1024):.2f} MB/s"

    @staticmethod
    def format_bytes(bytes_val):
        """Format total bytes in KB/MB/GB"""
        if bytes_val < 1024:
            return f"{bytes_val} B"
        elif bytes_val < 1024 * 1024:
            return f"{bytes_val / 1024:.1f} KB"
        elif bytes_val < 1024 * 1024 * 1024:
            return f"{bytes_val / (1024 * 1024):.1f} MB"
        else:
            return f"{bytes_val / (1024 * 1024 * 1024):.2f} GB"

    @staticmethod
    def format_uptime(seconds):
        """Format uptime as HH:MM:SS"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"

    @staticmethod
    def format_timestamp():
        """Format current timestamp for logs"""
        from datetime import datetime

        return datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")


# ASCII Art / Decorative Elements
class ASCII:
    CORNER_TL = "┌"
    CORNER_TR = "┐"
    CORNER_BL = "└"
    CORNER_BR = "┘"
    LINE_H = "─"
    LINE_V = "│"

    @staticmethod
    def box_top(width, title=""):
        if title:
            title_text = f" {title} "
            dashes = "─" * ((width - len(title_text) - 2) // 2)
            return f"┌{dashes}{title_text}{dashes}┐"
        return f"┌{'─' * (width - 2)}┐"

    @staticmethod
    def box_bottom(width):
        return f"└{'─' * (width - 2)}┘"

    @staticmethod
    def progress_bar(percent, width=20):
        """Create ASCII progress bar"""
        filled = int((percent / 100) * width)
        empty = width - filled
        return f"[{'█' * filled}{'░' * empty}] {percent}%"
