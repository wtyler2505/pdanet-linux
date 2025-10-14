"""
PdaNet Linux - Advanced Keyboard Navigation and Accessibility
P3-UX-2: Enhanced keyboard shortcuts, accessibility features, and power user tools
"""

import json
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

from logger import get_logger


class AccessibilityMode(Enum):
    """Accessibility mode settings"""
    NONE = "none"
    HIGH_CONTRAST = "high_contrast"
    LARGE_TEXT = "large_text"
    SCREEN_READER = "screen_reader"
    KEYBOARD_ONLY = "keyboard_only"


@dataclass
class KeyboardShortcut:
    """Keyboard shortcut definition"""
    name: str
    description: str
    key_combination: str
    action: str
    category: str
    customizable: bool = True
    enabled: bool = True
    accessibility_alternative: Optional[str] = None


@dataclass
class AccessibilitySettings:
    """Comprehensive accessibility settings"""
    mode: AccessibilityMode = AccessibilityMode.NONE
    high_contrast: bool = False
    large_text: bool = False
    large_text_scale: float = 1.2
    reduced_motion: bool = False
    screen_reader_support: bool = False
    keyboard_navigation_only: bool = False
    focus_indicators: bool = True
    audio_feedback: bool = False
    tooltip_delays_ms: int = 500
    animation_speed: float = 1.0  # 1.0 = normal, 0.5 = half speed, 2.0 = double speed
    color_blind_support: bool = False
    color_blind_type: str = "none"  # "deuteranopia", "protanopia", "tritanopia"


class KeyboardNavigationManager:
    """Advanced keyboard navigation and accessibility manager"""
    
    def __init__(self):
        self.logger = get_logger()
        self.config_dir = Path.home() / ".config" / "pdanet-linux"
        
        # Accessibility settings
        self.accessibility_file = self.config_dir / "accessibility.json"
        self.accessibility = self._load_accessibility_settings()
        
        # Keyboard shortcuts
        self.shortcuts_file = self.config_dir / "shortcuts.json"
        self.shortcuts = self._initialize_default_shortcuts()
        self.custom_shortcuts = self._load_custom_shortcuts()
        
        # Navigation state
        self.focus_stack: List[str] = []
        self.modal_active = False
        self.navigation_locked = False
        
        # Accessibility features
        self.screen_reader_enabled = False
        self.audio_feedback_enabled = self.accessibility.audio_feedback
        
        # Command palette
        self.command_palette_commands = self._initialize_command_palette()
    
    def _load_accessibility_settings(self) -> AccessibilitySettings:
        """Load accessibility settings"""
        if self.accessibility_file.exists():
            try:
                with open(self.accessibility_file) as f:
                    data = json.load(f)
                    return AccessibilitySettings(**data)
            except Exception as e:
                self.logger.warning(f"Failed to load accessibility settings: {e}")
        
        return AccessibilitySettings()
    
    def save_accessibility_settings(self):
        """Save accessibility settings"""
        try:
            import dataclasses
            data = dataclasses.asdict(self.accessibility)
            data['mode'] = self.accessibility.mode.value  # Convert enum
            
            with open(self.accessibility_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to save accessibility settings: {e}")
    
    def _initialize_default_shortcuts(self) -> Dict[str, KeyboardShortcut]:
        """Initialize default keyboard shortcuts"""
        shortcuts = {}
        
        # Connection shortcuts
        connection_shortcuts = [
            KeyboardShortcut("connect", "Connect to network", "Ctrl+C", "connect", "Connection"),
            KeyboardShortcut("disconnect", "Disconnect from network", "Ctrl+D", "disconnect", "Connection"),
            KeyboardShortcut("quick_connect", "Quick connect with last profile", "Ctrl+Q", "quick_connect", "Connection"),
            KeyboardShortcut("toggle_stealth", "Toggle stealth mode", "Ctrl+S", "toggle_stealth", "Connection"),
        ]
        
        # Profile shortcuts
        profile_shortcuts = [
            KeyboardShortcut("profile_menu", "Open profile menu", "Ctrl+P", "show_profile_menu", "Profiles"),
            KeyboardShortcut("new_profile", "Create new profile", "Ctrl+N", "new_profile", "Profiles"),
            KeyboardShortcut("edit_profile", "Edit current profile", "Ctrl+E", "edit_profile", "Profiles"),
            KeyboardShortcut("next_profile", "Switch to next profile", "Ctrl+Tab", "next_profile", "Profiles"),
            KeyboardShortcut("prev_profile", "Switch to previous profile", "Ctrl+Shift+Tab", "prev_profile", "Profiles"),
        ]
        
        # Interface shortcuts
        interface_shortcuts = [
            KeyboardShortcut("refresh", "Refresh status/scan networks", "F5", "refresh", "Interface"),
            KeyboardShortcut("settings", "Open settings", "Ctrl+,", "show_settings", "Interface"),
            KeyboardShortcut("command_palette", "Open command palette", "Ctrl+Shift+P", "command_palette", "Interface"),
            KeyboardShortcut("minimize_tray", "Minimize to tray", "Ctrl+M", "minimize_tray", "Interface"),
            KeyboardShortcut("show_hide", "Show/Hide window", "Ctrl+H", "toggle_window", "Interface"),
        ]
        
        # Diagnostics shortcuts
        diagnostic_shortcuts = [
            KeyboardShortcut("speed_test", "Run speed test", "Ctrl+T", "speed_test", "Diagnostics"),
            KeyboardShortcut("network_info", "Show network information", "Ctrl+I", "network_info", "Diagnostics"),
            KeyboardShortcut("connection_log", "Show connection log", "Ctrl+L", "show_log", "Diagnostics"),
            KeyboardShortcut("export_logs", "Export diagnostic logs", "Ctrl+Shift+E", "export_logs", "Diagnostics"),
        ]
        
        # Accessibility shortcuts
        accessibility_shortcuts = [
            KeyboardShortcut("toggle_high_contrast", "Toggle high contrast", "Alt+Ctrl+H", "toggle_high_contrast", "Accessibility", accessibility_alternative="High contrast mode"),
            KeyboardShortcut("increase_text_size", "Increase text size", "Ctrl+=", "increase_text_size", "Accessibility"),
            KeyboardShortcut("decrease_text_size", "Decrease text size", "Ctrl+-", "decrease_text_size", "Accessibility"),
            KeyboardShortcut("focus_next", "Focus next element", "Tab", "focus_next", "Navigation", customizable=False),
            KeyboardShortcut("focus_prev", "Focus previous element", "Shift+Tab", "focus_prev", "Navigation", customizable=False),
            KeyboardShortcut("activate_focused", "Activate focused element", "Space", "activate_focused", "Navigation", customizable=False),
        ]
        
        # Application shortcuts
        app_shortcuts = [
            KeyboardShortcut("quit", "Quit application", "Ctrl+Q", "quit", "Application"),
            KeyboardShortcut("about", "About PdaNet Linux", "F1", "show_about", "Application"),
            KeyboardShortcut("help", "Show help", "Ctrl+?", "show_help", "Application"),
            KeyboardShortcut("shortcuts_help", "Show keyboard shortcuts", "Ctrl+Shift+?", "shortcuts_help", "Application"),
        ]
        
        # Combine all shortcuts
        all_shortcuts = (connection_shortcuts + profile_shortcuts + interface_shortcuts + 
                        diagnostic_shortcuts + accessibility_shortcuts + app_shortcuts)
        
        for shortcut in all_shortcuts:
            shortcuts[shortcut.name] = shortcut
        
        return shortcuts
    
    def _load_custom_shortcuts(self) -> Dict[str, str]:
        """Load custom keyboard shortcuts"""
        if self.shortcuts_file.exists():
            try:
                with open(self.shortcuts_file) as f:
                    return json.load(f)
            except Exception as e:
                self.logger.warning(f"Failed to load custom shortcuts: {e}")
        
        return {}
    
    def save_custom_shortcuts(self):
        """Save custom keyboard shortcuts"""
        try:
            with open(self.shortcuts_file, 'w') as f:
                json.dump(self.custom_shortcuts, f, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to save custom shortcuts: {e}")
    
    def _initialize_command_palette(self) -> Dict[str, Dict[str, Any]]:
        """Initialize command palette commands"""
        return {
            "connect": {"name": "Connect", "description": "Establish network connection", "category": "Connection"},
            "disconnect": {"name": "Disconnect", "description": "Terminate network connection", "category": "Connection"},
            "profiles": {"name": "Manage Profiles", "description": "Create and manage connection profiles", "category": "Profiles"},
            "settings": {"name": "Settings", "description": "Open application settings", "category": "Configuration"},
            "speed_test": {"name": "Speed Test", "description": "Test connection speed", "category": "Diagnostics"},
            "network_scan": {"name": "Scan Networks", "description": "Scan for available WiFi networks", "category": "Connection"},
            "stealth_toggle": {"name": "Toggle Stealth", "description": "Enable/disable stealth mode", "category": "Security"},
            "export_config": {"name": "Export Configuration", "description": "Export settings and profiles", "category": "Data"},
            "import_config": {"name": "Import Configuration", "description": "Import settings and profiles", "category": "Data"},
            "clear_logs": {"name": "Clear Logs", "description": "Clear connection logs", "category": "Maintenance"},
            "reset_stats": {"name": "Reset Statistics", "description": "Reset usage statistics", "category": "Maintenance"},
            "check_updates": {"name": "Check Updates", "description": "Check for application updates", "category": "System"},
        }
    
    # Accessibility Management
    def enable_accessibility_mode(self, mode: AccessibilityMode):
        """Enable specific accessibility mode"""
        self.accessibility.mode = mode
        
        if mode == AccessibilityMode.HIGH_CONTRAST:
            self.accessibility.high_contrast = True
            self.accessibility.focus_indicators = True
        elif mode == AccessibilityMode.LARGE_TEXT:
            self.accessibility.large_text = True
            self.accessibility.large_text_scale = 1.5
        elif mode == AccessibilityMode.SCREEN_READER:
            self.accessibility.screen_reader_support = True
            self.accessibility.audio_feedback = True
            self.accessibility.keyboard_navigation_only = True
        elif mode == AccessibilityMode.KEYBOARD_ONLY:
            self.accessibility.keyboard_navigation_only = True
            self.accessibility.focus_indicators = True
        
        self.save_accessibility_settings()
        self.logger.info(f"Enabled accessibility mode: {mode.value}")
    
    def get_accessibility_css(self) -> str:
        """Generate CSS for accessibility enhancements"""
        css_rules = []
        
        if self.accessibility.high_contrast:
            css_rules.extend([
                "* { border-color: #FFFFFF !important; }",
                ".button { background: #000000 !important; color: #FFFFFF !important; border: 2px solid #FFFFFF !important; }",
                ".entry { background: #000000 !important; color: #FFFFFF !important; border: 2px solid #FFFFFF !important; }",
                ".label { color: #FFFFFF !important; }",
                ".window { background: #000000 !important; }"
            ])
        
        if self.accessibility.large_text:
            scale = self.accessibility.large_text_scale
            css_rules.extend([
                f"* {{ font-size: {scale}em !important; }}",
                f".button {{ min-height: {48 * scale}px !important; min-width: {120 * scale}px !important; }}",
                f".entry {{ min-height: {36 * scale}px !important; }}"
            ])
        
        if self.accessibility.focus_indicators:
            css_rules.extend([
                "*:focus { outline: 3px solid #0080FF !important; outline-offset: 2px !important; }",
                ".button:focus { box-shadow: 0 0 0 3px #0080FF !important; }"
            ])
        
        return "\n".join(css_rules)
    
    # Keyboard Shortcut Management
    def customize_shortcut(self, action_name: str, new_key_combination: str) -> bool:
        """Customize a keyboard shortcut"""
        if action_name in self.shortcuts and self.shortcuts[action_name].customizable:
            # Check for conflicts
            if self._has_shortcut_conflict(new_key_combination, action_name):
                return False
            
            self.custom_shortcuts[action_name] = new_key_combination
            self.save_custom_shortcuts()
            self.logger.info(f"Customized shortcut {action_name}: {new_key_combination}")
            return True
        
        return False
    
    def _has_shortcut_conflict(self, key_combination: str, exclude_action: str = "") -> bool:
        """Check if key combination conflicts with existing shortcuts"""
        for action, shortcut in self.shortcuts.items():
            if action == exclude_action:
                continue
            
            effective_key = self.custom_shortcuts.get(action, shortcut.key_combination)
            if effective_key == key_combination:
                return True
        
        return False
    
    def get_effective_shortcut(self, action_name: str) -> Optional[str]:
        """Get the effective shortcut for an action (custom or default)"""
        if action_name in self.custom_shortcuts:
            return self.custom_shortcuts[action_name]
        elif action_name in self.shortcuts:
            return self.shortcuts[action_name].key_combination
        
        return None
    
    def get_shortcuts_by_category(self) -> Dict[str, List[KeyboardShortcut]]:
        """Get shortcuts organized by category"""
        categories = {}
        
        for shortcut in self.shortcuts.values():
            category = shortcut.category
            if category not in categories:
                categories[category] = []
            
            # Apply custom key combination if available
            effective_shortcut = KeyboardShortcut(
                name=shortcut.name,
                description=shortcut.description,
                key_combination=self.custom_shortcuts.get(shortcut.name, shortcut.key_combination),
                action=shortcut.action,
                category=shortcut.category,
                customizable=shortcut.customizable,
                enabled=shortcut.enabled,
                accessibility_alternative=shortcut.accessibility_alternative
            )
            
            categories[category].append(effective_shortcut)
        
        return categories
    
    # Command Palette
    def search_commands(self, query: str) -> List[Dict[str, Any]]:
        """Search command palette commands"""
        query = query.lower()
        matches = []
        
        for command_id, command in self.command_palette_commands.items():
            score = 0
            name_lower = command["name"].lower()
            desc_lower = command["description"].lower()
            
            # Exact name match
            if query == name_lower:
                score = 100
            # Name starts with query
            elif name_lower.startswith(query):
                score = 90
            # Name contains query
            elif query in name_lower:
                score = 70
            # Description contains query
            elif query in desc_lower:
                score = 50
            
            if score > 0:
                result = command.copy()
                result["id"] = command_id
                result["score"] = score
                matches.append(result)
        
        # Sort by score (descending) and name (ascending)
        matches.sort(key=lambda x: (-x["score"], x["name"]))
        return matches[:10]  # Return top 10 matches
    
    def execute_command(self, command_id: str) -> Dict[str, Any]:
        """Execute a command palette command"""
        if command_id not in self.command_palette_commands:
            return {"success": False, "error": "Command not found"}
        
        command = self.command_palette_commands[command_id]
        
        # This would integrate with the main application to execute the command
        # For now, return a success response with the command info
        return {
            "success": True,
            "command": command,
            "action_required": command_id
        }
    
    # Navigation Management
    def push_focus(self, widget_id: str):
        """Push widget to focus stack"""
        self.focus_stack.append(widget_id)
    
    def pop_focus(self) -> Optional[str]:
        """Pop widget from focus stack"""
        return self.focus_stack.pop() if self.focus_stack else None
    
    def get_current_focus(self) -> Optional[str]:
        """Get currently focused widget"""
        return self.focus_stack[-1] if self.focus_stack else None
    
    def set_modal_active(self, active: bool):
        """Set modal dialog active state"""
        self.modal_active = active
        if active:
            self.navigation_locked = True
        else:
            self.navigation_locked = False
    
    # Screen Reader Support
    def announce(self, text: str, priority: str = "normal"):
        """Announce text to screen reader"""
        if not self.accessibility.screen_reader_support:
            return
        
        # This would integrate with screen reader APIs
        # For now, log the announcement
        self.logger.info(f"Screen reader announcement ({priority}): {text}")
    
    def describe_element(self, element_type: str, text: str, state: str = "") -> str:
        """Generate screen reader description for element"""
        if not self.accessibility.screen_reader_support:
            return text
        
        description = f"{element_type}: {text}"
        if state:
            description += f", {state}"
        
        return description
    
    # Audio Feedback
    def play_feedback_sound(self, sound_type: str):
        """Play audio feedback sound"""
        if not self.audio_feedback_enabled:
            return
        
        # This would integrate with audio system
        # For now, log the sound event
        self.logger.debug(f"Audio feedback: {sound_type}")
    
    # Keyboard Navigation Helpers
    def get_navigation_help(self) -> List[str]:
        """Get keyboard navigation help text"""
        help_text = []
        
        if self.accessibility.keyboard_navigation_only:
            help_text.extend([
                "Navigation: Use Tab/Shift+Tab to move between elements",
                "Activation: Press Space or Enter to activate buttons",
                "Menus: Use arrow keys to navigate menu items",
                "Dialogs: Press Escape to close dialogs"
            ])
        
        essential_shortcuts = [
            f"Connect: {self.get_effective_shortcut('connect')}",
            f"Disconnect: {self.get_effective_shortcut('disconnect')}",
            f"Settings: {self.get_effective_shortcut('settings')}",
            f"Help: {self.get_effective_shortcut('help')}"
        ]
        
        help_text.extend(essential_shortcuts)
        return help_text
    
    def export_accessibility_report(self) -> Dict[str, Any]:
        """Export comprehensive accessibility report"""
        return {
            "accessibility_settings": {
                "mode": self.accessibility.mode.value,
                "high_contrast": self.accessibility.high_contrast,
                "large_text": self.accessibility.large_text,
                "screen_reader_support": self.accessibility.screen_reader_support,
                "keyboard_navigation_only": self.accessibility.keyboard_navigation_only,
            },
            "keyboard_shortcuts": {
                "total_shortcuts": len(self.shortcuts),
                "customized_shortcuts": len(self.custom_shortcuts),
                "categories": list(set(s.category for s in self.shortcuts.values()))
            },
            "command_palette": {
                "total_commands": len(self.command_palette_commands),
                "categories": list(set(c["category"] for c in self.command_palette_commands.values()))
            },
            "recommendations": self._get_accessibility_recommendations()
        }
    
    def _get_accessibility_recommendations(self) -> List[str]:
        """Get accessibility improvement recommendations"""
        recommendations = []
        
        if not self.accessibility.focus_indicators:
            recommendations.append("Enable focus indicators for better keyboard navigation")
        
        if not self.accessibility.screen_reader_support and self.accessibility.keyboard_navigation_only:
            recommendations.append("Consider enabling screen reader support")
        
        if len(self.custom_shortcuts) == 0:
            recommendations.append("Customize keyboard shortcuts to match your preferences")
        
        return recommendations


# Global instance
_keyboard_nav = None

def get_keyboard_navigation_manager() -> KeyboardNavigationManager:
    """Get global keyboard navigation manager instance"""
    global _keyboard_nav
    if _keyboard_nav is None:
        _keyboard_nav = KeyboardNavigationManager()
    return _keyboard_nav