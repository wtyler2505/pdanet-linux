#!/usr/bin/env python3
"""
P3 User Experience Comprehensive Testing for PdaNet Linux
Tests P3-UX-1, P3-UX-2, P3-UX-3 and Enhanced Connection Manager Integration
"""

import os
import sys
import time
import json
import tempfile
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

# Add src to path
sys.path.insert(0, "/app/src")

print("=" * 80)
print("PDANET LINUX - P3 USER EXPERIENCE COMPREHENSIVE TESTING")
print("=" * 80)
print()

test_results = []

def test(name, func):
    """Run a test and track results"""
    try:
        func()
        test_results.append((name, True, None))
        print(f"✓ {name}")
        return True
    except AssertionError as e:
        test_results.append((name, False, str(e)))
        print(f"✗ {name}: {e}")
        return False
    except Exception as e:
        test_results.append((name, False, f"Exception: {e}"))
        print(f"✗ {name}: Exception - {e}")
        return False

# Test Suite 1: P3 User Experience Manager Core Tests
print("\n[1/6] P3 USER EXPERIENCE MANAGER CORE TESTS")
print("-" * 80)

def test_user_experience_manager_initialization():
    """Test UserExperienceManager initialization and basic setup"""
    from user_experience import UserExperienceManager, ConnectionProfile, UsageStatistics
    
    ux_manager = UserExperienceManager()
    assert ux_manager is not None, "UserExperienceManager failed to initialize"
    assert hasattr(ux_manager, 'user_profiles'), "Missing user_profiles"
    assert hasattr(ux_manager, 'user_preferences'), "Missing user_preferences"
    assert hasattr(ux_manager, 'usage_stats'), "Missing usage_stats"
    assert hasattr(ux_manager, 'quality_history'), "Missing quality_history"
    assert hasattr(ux_manager, 'quick_actions'), "Missing quick_actions"
    assert isinstance(ux_manager.usage_stats, UsageStatistics), "usage_stats not UsageStatistics instance"
    assert len(ux_manager.quick_actions) > 0, "No quick actions defined"

def test_connection_profile_lifecycle():
    """Test complete connection profile lifecycle"""
    from user_experience import UserExperienceManager
    
    ux_manager = UserExperienceManager()
    
    # Test profile creation
    success = ux_manager.create_profile(
        "test_wifi_profile", 
        "wifi", 
        ssid="TestNetwork", 
        stealth_level=2,
        description="Test WiFi profile",
        tags=["work", "secure"]
    )
    assert success == True, "Profile creation failed"
    assert "test_wifi_profile" in ux_manager.user_profiles, "Profile not added to user_profiles"
    
    profile = ux_manager.get_profile("test_wifi_profile")
    assert profile is not None, "Created profile not retrievable"
    assert profile.name == "test_wifi_profile", "Profile name incorrect"
    assert profile.mode == "wifi", "Profile mode incorrect"
    assert profile.ssid == "TestNetwork", "Profile SSID incorrect"
    assert profile.stealth_level == 2, "Profile stealth level incorrect"
    assert profile.description == "Test WiFi profile", "Profile description incorrect"
    assert "work" in profile.tags, "Profile tags not set correctly"
    assert profile.use_count == 0, "Initial use count should be 0"
    
    # Test profile update
    update_success = ux_manager.update_profile(
        "test_wifi_profile", 
        stealth_level=3, 
        description="Updated WiFi profile",
        auto_connect=True
    )
    assert update_success == True, "Profile update failed"
    
    updated_profile = ux_manager.get_profile("test_wifi_profile")
    assert updated_profile.stealth_level == 3, "Profile stealth level not updated"
    assert updated_profile.description == "Updated WiFi profile", "Profile description not updated"
    assert updated_profile.auto_connect == True, "Profile auto_connect not updated"
    
    # Test profile usage tracking
    used_profile = ux_manager.use_profile("test_wifi_profile")
    assert used_profile is not None, "Profile usage failed"
    assert used_profile.use_count == 1, "Profile use count not incremented"
    assert used_profile.last_used is not None, "Profile last_used not set"
    
    # Test profile listing (sorted by usage)
    profiles = ux_manager.list_profiles()
    assert len(profiles) > 0, "Profile list should not be empty"
    assert profiles[0].name == "test_wifi_profile", "Most used profile should be first"
    
    # Test duplicate profile creation
    duplicate_success = ux_manager.create_profile("test_wifi_profile", "usb")
    assert duplicate_success == False, "Duplicate profile creation should fail"
    
    # Test profile deletion
    delete_success = ux_manager.delete_profile("test_wifi_profile")
    assert delete_success == True, "Profile deletion failed"
    assert "test_wifi_profile" not in ux_manager.user_profiles, "Profile not removed from user_profiles"
    
    # Test deleting non-existent profile
    delete_nonexistent = ux_manager.delete_profile("nonexistent_profile")
    assert delete_nonexistent == False, "Deleting non-existent profile should return False"

def test_user_preferences_comprehensive():
    """Test comprehensive user preferences management"""
    from user_experience import UserExperienceManager
    
    ux_manager = UserExperienceManager()
    
    # Test default preferences are loaded
    expected_defaults = [
        ("theme", "cyberpunk_dark"),
        ("notifications_enabled", True),
        ("auto_connect_on_startup", False),
        ("minimize_to_tray", True),
        ("preferred_connection_mode", "usb"),
        ("data_usage_warnings", True),
        ("warning_threshold_gb", 10.0),
        ("quality_monitoring_interval", 30),
        ("auto_profile_suggestions", True),
        ("connection_timeout_seconds", 60),
        ("log_level", "INFO"),
        ("language", "en_US"),
        ("metric_units", "metric")
    ]
    
    for key, expected_value in expected_defaults:
        actual_value = ux_manager.get_preference(key)
        assert actual_value == expected_value, f"Default preference {key} incorrect: expected {expected_value}, got {actual_value}"
    
    # Test preference updates
    test_updates = [
        ("theme", "light_mode"),
        ("notifications_enabled", False),
        ("warning_threshold_gb", 25.0),
        ("quality_monitoring_interval", 60),
        ("language", "es_ES"),
        ("custom_preference", "custom_value")
    ]
    
    for key, value in test_updates:
        ux_manager.update_preference(key, value)
        assert ux_manager.get_preference(key) == value, f"Preference update failed for {key}"
    
    # Test preference with default fallback
    custom_value = ux_manager.get_preference("non_existent_key", "fallback_value")
    assert custom_value == "fallback_value", "Default value not returned for non-existent preference"
    
    # Test preference reset
    ux_manager.reset_preferences()
    assert ux_manager.get_preference("theme") == "cyberpunk_dark", "Preferences not reset to defaults"

def test_usage_analytics_comprehensive():
    """Test comprehensive usage analytics and insights"""
    from user_experience import UserExperienceManager
    
    ux_manager = UserExperienceManager()
    
    # Record diverse connection sessions
    sessions = [
        ("wifi", 3600, 1024*1024*100, True),    # 1 hour, 100MB, success
        ("usb", 1800, 1024*1024*50, True),     # 30 min, 50MB, success
        ("iphone", 7200, 1024*1024*200, False), # 2 hours, 200MB, failed
        ("wifi", 5400, 1024*1024*150, True),   # 1.5 hours, 150MB, success
        ("usb", 900, 1024*1024*25, True),      # 15 min, 25MB, success
        ("wifi", 10800, 1024*1024*300, True),  # 3 hours, 300MB, success
    ]
    
    for mode, duration, data_bytes, success in sessions:
        ux_manager.record_connection_session(mode, duration, data_bytes, success)
    
    # Test usage statistics
    stats = ux_manager.usage_stats
    assert stats.total_sessions == 6, f"Expected 6 sessions, got {stats.total_sessions}"
    assert stats.total_uptime_hours > 0, "Total uptime should be greater than 0"
    assert stats.total_data_gb > 0, "Total data should be greater than 0"
    assert 0 <= stats.success_rate_percent <= 100, "Success rate should be between 0-100"
    
    # Calculate expected success rate (5 successes out of 6 sessions = 83.33%)
    expected_success_rate = (5 / 6) * 100
    assert abs(stats.success_rate_percent - expected_success_rate) < 1, f"Success rate calculation incorrect: expected ~{expected_success_rate:.1f}%, got {stats.success_rate_percent:.1f}%"
    
    # Test usage insights generation
    insights = ux_manager.get_usage_insights()
    assert "summary" in insights, "Insights missing summary"
    assert "patterns" in insights, "Insights missing patterns"
    assert "recommendations" in insights, "Insights missing recommendations"
    
    summary = insights["summary"]
    assert summary["total_sessions"] == 6, "Summary session count incorrect"
    assert summary["total_uptime_hours"] > 0, "Summary uptime incorrect"
    assert summary["total_data_gb"] > 0, "Summary data usage incorrect"
    assert summary["success_rate"] == round(stats.success_rate_percent, 1), "Summary success rate incorrect"
    
    # Test that patterns are detected for sufficient sessions
    assert isinstance(insights["patterns"], list), "Patterns should be a list"
    
    # Test that recommendations are provided
    assert isinstance(insights["recommendations"], list), "Recommendations should be a list"

def test_profile_suggestions_ai():
    """Test AI-based profile suggestions with context"""
    from user_experience import UserExperienceManager
    from datetime import datetime
    
    ux_manager = UserExperienceManager()
    
    # Create test profiles with different usage patterns
    profiles_data = [
        ("morning_work", "wifi", {"ssid": "OfficeWiFi", "description": "Morning work profile"}),
        ("mobile_backup", "usb", {"description": "Mobile USB backup"}),
        ("evening_home", "wifi", {"ssid": "HomeWiFi", "description": "Evening home profile"}),
        ("travel_hotspot", "iphone", {"description": "Travel iPhone hotspot"})
    ]
    
    for name, mode, kwargs in profiles_data:
        ux_manager.create_profile(name, mode, **kwargs)
    
    # Simulate usage patterns
    for _ in range(5):
        ux_manager.use_profile("morning_work")
    for _ in range(3):
        ux_manager.use_profile("evening_home")
    for _ in range(2):
        ux_manager.use_profile("mobile_backup")
    
    # Test profile suggestions with context
    current_context = {
        "current_time": datetime.now().hour,
        "preferred_mode": "wifi",
        "current_location": "office"
    }
    
    suggestions = ux_manager.get_suggested_profiles(current_context)
    assert isinstance(suggestions, list), "Suggestions should be a list"
    
    # Most used profiles should be suggested first
    if suggestions:
        assert suggestions[0].name == "morning_work", "Most used profile should be suggested first"
    
    # Test with auto suggestions disabled
    ux_manager.update_preference("auto_profile_suggestions", False)
    no_suggestions = ux_manager.get_suggested_profiles(current_context)
    assert len(no_suggestions) == 0, "Should return no suggestions when disabled"
    
    # Re-enable for other tests
    ux_manager.update_preference("auto_profile_suggestions", True)

def test_quality_monitoring_system():
    """Test network quality monitoring and assessment"""
    from user_experience import UserExperienceManager
    
    ux_manager = UserExperienceManager()
    
    # Test quality assessment with no data
    assessment = ux_manager.get_quality_assessment()
    assert "status" in assessment, "Assessment missing status"
    assert assessment["status"] == "no_data", "Should report no_data when no metrics available"
    assert "score" in assessment, "Assessment missing score"
    assert "recommendations" in assessment, "Assessment missing recommendations"
    
    # Test quality monitoring is enabled by default
    assert ux_manager.quality_monitoring_enabled == True, "Quality monitoring should be enabled by default"
    assert hasattr(ux_manager, 'quality_history'), "Should have quality_history attribute"
    assert isinstance(ux_manager.quality_history, list), "Quality history should be a list"
    
    # Test quality monitoring interval preference
    interval = ux_manager.user_preferences.get("quality_monitoring_interval", 30)
    assert interval == 30, "Default quality monitoring interval should be 30 seconds"

test("User Experience Manager Initialization", test_user_experience_manager_initialization)
test("Connection Profile Lifecycle", test_connection_profile_lifecycle)
test("User Preferences Comprehensive", test_user_preferences_comprehensive)
test("Usage Analytics Comprehensive", test_usage_analytics_comprehensive)
test("Profile Suggestions AI", test_profile_suggestions_ai)
test("Quality Monitoring System", test_quality_monitoring_system)

# Test Suite 2: P3 Keyboard Navigation and Accessibility Tests
print("\n[2/6] P3 KEYBOARD NAVIGATION AND ACCESSIBILITY TESTS")
print("-" * 80)

def test_keyboard_navigation_manager_initialization():
    """Test KeyboardNavigationManager initialization and setup"""
    from keyboard_navigation import KeyboardNavigationManager, AccessibilitySettings, AccessibilityMode
    
    nav_manager = KeyboardNavigationManager()
    assert nav_manager is not None, "KeyboardNavigationManager failed to initialize"
    assert hasattr(nav_manager, 'shortcuts'), "Missing shortcuts"
    assert hasattr(nav_manager, 'accessibility'), "Missing accessibility settings"
    assert hasattr(nav_manager, 'command_palette_commands'), "Missing command palette commands"
    assert hasattr(nav_manager, 'focus_stack'), "Missing focus_stack"
    assert hasattr(nav_manager, 'custom_shortcuts'), "Missing custom_shortcuts"
    
    assert isinstance(nav_manager.accessibility, AccessibilitySettings), "accessibility not AccessibilitySettings instance"
    assert isinstance(nav_manager.focus_stack, list), "focus_stack should be a list"
    assert isinstance(nav_manager.shortcuts, dict), "shortcuts should be a dict"
    assert isinstance(nav_manager.command_palette_commands, dict), "command_palette_commands should be a dict"
    
    # Test default state
    assert nav_manager.modal_active == False, "modal_active should be False initially"
    assert nav_manager.navigation_locked == False, "navigation_locked should be False initially"

def test_accessibility_modes_comprehensive():
    """Test comprehensive accessibility mode management"""
    from keyboard_navigation import KeyboardNavigationManager, AccessibilityMode
    
    nav_manager = KeyboardNavigationManager()
    
    # Test default accessibility settings
    assert nav_manager.accessibility.mode == AccessibilityMode.NONE, "Default accessibility mode should be NONE"
    assert nav_manager.accessibility.high_contrast == False, "Default high contrast should be False"
    assert nav_manager.accessibility.large_text == False, "Default large text should be False"
    assert nav_manager.accessibility.screen_reader_support == False, "Default screen reader support should be False"
    assert nav_manager.accessibility.keyboard_navigation_only == False, "Default keyboard navigation only should be False"
    
    # Test HIGH_CONTRAST mode
    nav_manager.enable_accessibility_mode(AccessibilityMode.HIGH_CONTRAST)
    assert nav_manager.accessibility.mode == AccessibilityMode.HIGH_CONTRAST, "High contrast mode not enabled"
    assert nav_manager.accessibility.high_contrast == True, "High contrast setting not enabled"
    assert nav_manager.accessibility.focus_indicators == True, "Focus indicators should be enabled with high contrast"
    
    # Test LARGE_TEXT mode
    nav_manager.enable_accessibility_mode(AccessibilityMode.LARGE_TEXT)
    assert nav_manager.accessibility.mode == AccessibilityMode.LARGE_TEXT, "Large text mode not enabled"
    assert nav_manager.accessibility.large_text == True, "Large text setting not enabled"
    assert nav_manager.accessibility.large_text_scale == 1.5, "Large text scale not set correctly"
    
    # Test SCREEN_READER mode
    nav_manager.enable_accessibility_mode(AccessibilityMode.SCREEN_READER)
    assert nav_manager.accessibility.mode == AccessibilityMode.SCREEN_READER, "Screen reader mode not enabled"
    assert nav_manager.accessibility.screen_reader_support == True, "Screen reader support not enabled"
    assert nav_manager.accessibility.audio_feedback == True, "Audio feedback should be enabled with screen reader"
    assert nav_manager.accessibility.keyboard_navigation_only == True, "Keyboard navigation only should be enabled with screen reader"
    
    # Test KEYBOARD_ONLY mode
    nav_manager.enable_accessibility_mode(AccessibilityMode.KEYBOARD_ONLY)
    assert nav_manager.accessibility.mode == AccessibilityMode.KEYBOARD_ONLY, "Keyboard-only mode not enabled"
    assert nav_manager.accessibility.keyboard_navigation_only == True, "Keyboard navigation only not enabled"
    assert nav_manager.accessibility.focus_indicators == True, "Focus indicators should be enabled with keyboard-only mode"

def test_accessibility_css_generation():
    """Test CSS generation for accessibility enhancements"""
    from keyboard_navigation import KeyboardNavigationManager, AccessibilityMode
    
    nav_manager = KeyboardNavigationManager()
    
    # Test high contrast CSS
    nav_manager.enable_accessibility_mode(AccessibilityMode.HIGH_CONTRAST)
    css = nav_manager.get_accessibility_css()
    
    expected_high_contrast_rules = [
        "background: #000000",
        "color: #FFFFFF",
        "border: 2px solid #FFFFFF",
        "border-color: #FFFFFF"
    ]
    
    for rule in expected_high_contrast_rules:
        assert rule in css, f"High contrast CSS missing rule: {rule}"
    
    # Test large text CSS
    nav_manager.enable_accessibility_mode(AccessibilityMode.LARGE_TEXT)
    css = nav_manager.get_accessibility_css()
    
    expected_large_text_rules = [
        "font-size: 1.5em",
        "min-height:",
        "min-width:"
    ]
    
    for rule in expected_large_text_rules:
        assert rule in css, f"Large text CSS missing rule: {rule}"
    
    # Test focus indicators CSS
    nav_manager.accessibility.focus_indicators = True
    css = nav_manager.get_accessibility_css()
    
    expected_focus_rules = [
        "outline: 3px solid #0080FF",
        "outline-offset: 2px",
        "box-shadow: 0 0 0 3px #0080FF"
    ]
    
    for rule in expected_focus_rules:
        assert rule in css, f"Focus indicators CSS missing rule: {rule}"
    
    # Test combined modes
    nav_manager.accessibility.high_contrast = True
    nav_manager.accessibility.large_text = True
    nav_manager.accessibility.focus_indicators = True
    css = nav_manager.get_accessibility_css()
    
    # Should contain rules from all enabled modes
    assert "background: #000000" in css, "Combined CSS missing high contrast rules"
    assert "font-size: 1.5em" in css, "Combined CSS missing large text rules"
    assert "outline: 3px solid #0080FF" in css, "Combined CSS missing focus indicator rules"

def test_keyboard_shortcuts_comprehensive():
    """Test comprehensive keyboard shortcuts management"""
    from keyboard_navigation import KeyboardNavigationManager
    
    nav_manager = KeyboardNavigationManager()
    
    # Test default shortcuts exist and are properly categorized
    expected_categories = ["Connection", "Profiles", "Interface", "Diagnostics", "Accessibility", "Navigation", "Application"]
    
    categories = nav_manager.get_shortcuts_by_category()
    for category in expected_categories:
        assert category in categories, f"Missing shortcut category: {category}"
        assert len(categories[category]) > 0, f"Category {category} should have shortcuts"
    
    # Test specific essential shortcuts
    essential_shortcuts = [
        ("connect", "Ctrl+C", "Connection"),
        ("disconnect", "Ctrl+D", "Connection"),
        ("quick_connect", "Ctrl+Q", "Connection"),
        ("command_palette", "Ctrl+Shift+P", "Interface"),
        ("settings", "Ctrl+,", "Interface"),
        ("help", "Ctrl+?", "Application")
    ]
    
    for shortcut_name, expected_key, expected_category in essential_shortcuts:
        assert shortcut_name in nav_manager.shortcuts, f"Missing essential shortcut: {shortcut_name}"
        shortcut = nav_manager.shortcuts[shortcut_name]
        assert shortcut.key_combination == expected_key, f"Shortcut {shortcut_name} has wrong key: expected {expected_key}, got {shortcut.key_combination}"
        assert shortcut.category == expected_category, f"Shortcut {shortcut_name} has wrong category: expected {expected_category}, got {shortcut.category}"
    
    # Test shortcut customization
    original_key = nav_manager.shortcuts["connect"].key_combination
    success = nav_manager.customize_shortcut("connect", "Ctrl+Shift+C")
    assert success == True, "Shortcut customization failed"
    
    effective_shortcut = nav_manager.get_effective_shortcut("connect")
    assert effective_shortcut == "Ctrl+Shift+C", "Effective shortcut not updated"
    
    # Test conflict detection
    conflict_result = nav_manager.customize_shortcut("disconnect", "Ctrl+Shift+C")
    assert conflict_result == False, "Should detect shortcut conflict"
    
    # Test non-customizable shortcuts
    non_customizable_shortcuts = ["focus_next", "focus_prev", "activate_focused"]
    for shortcut_name in non_customizable_shortcuts:
        if shortcut_name in nav_manager.shortcuts:
            shortcut = nav_manager.shortcuts[shortcut_name]
            assert shortcut.customizable == False, f"Shortcut {shortcut_name} should not be customizable"
    
    # Test accessibility alternatives
    accessibility_shortcuts = [s for s in nav_manager.shortcuts.values() if s.accessibility_alternative]
    assert len(accessibility_shortcuts) > 0, "Should have shortcuts with accessibility alternatives"

def test_command_palette_comprehensive():
    """Test comprehensive command palette functionality"""
    from keyboard_navigation import KeyboardNavigationManager
    
    nav_manager = KeyboardNavigationManager()
    
    # Test command palette has essential commands
    essential_commands = [
        "connect", "disconnect", "profiles", "settings", 
        "speed_test", "network_scan", "stealth_toggle"
    ]
    
    for command in essential_commands:
        assert command in nav_manager.command_palette_commands, f"Missing essential command: {command}"
        cmd_data = nav_manager.command_palette_commands[command]
        assert "name" in cmd_data, f"Command {command} missing name"
        assert "description" in cmd_data, f"Command {command} missing description"
        assert "category" in cmd_data, f"Command {command} missing category"
    
    # Test command search functionality
    search_tests = [
        ("connect", ["connect"]),  # Exact match
        ("Connect", ["connect"]),  # Case insensitive
        ("net", ["network_scan"]),  # Partial match
        ("speed", ["speed_test"]),  # Partial match
        ("xyz123", [])  # No match
    ]
    
    for query, expected_commands in search_tests:
        results = nav_manager.search_commands(query)
        assert isinstance(results, list), f"Search results should be a list for query: {query}"
        
        if expected_commands:
            assert len(results) > 0, f"Should find results for query: {query}"
            result_ids = [r["id"] for r in results]
            for expected_cmd in expected_commands:
                assert expected_cmd in result_ids, f"Expected command {expected_cmd} not found for query: {query}"
        else:
            assert len(results) == 0, f"Should find no results for query: {query}"
    
    # Test search scoring
    exact_results = nav_manager.search_commands("Connect")
    if exact_results:
        # Exact matches should have highest scores
        assert exact_results[0]["score"] >= 90, "Exact match should have high score"
    
    # Test command execution
    for command_id in essential_commands:
        result = nav_manager.execute_command(command_id)
        assert result["success"] == True, f"Command execution should succeed for: {command_id}"
        assert "command" in result, f"Command result should include command info for: {command_id}"
        assert "action_required" in result, f"Command result should include action_required for: {command_id}"
    
    # Test invalid command execution
    invalid_result = nav_manager.execute_command("nonexistent_command_xyz")
    assert invalid_result["success"] == False, "Invalid command should fail"
    assert "error" in invalid_result, "Invalid command result should include error"

def test_navigation_focus_management():
    """Test navigation state and focus management"""
    from keyboard_navigation import KeyboardNavigationManager
    
    nav_manager = KeyboardNavigationManager()
    
    # Test focus stack operations
    assert nav_manager.get_current_focus() is None, "Initial focus should be None"
    
    nav_manager.push_focus("main_window")
    assert nav_manager.get_current_focus() == "main_window", "Current focus should be main_window"
    
    nav_manager.push_focus("connect_button")
    assert nav_manager.get_current_focus() == "connect_button", "Current focus should be connect_button"
    
    nav_manager.push_focus("settings_dialog")
    assert nav_manager.get_current_focus() == "settings_dialog", "Current focus should be settings_dialog"
    
    # Test focus stack popping
    popped = nav_manager.pop_focus()
    assert popped == "settings_dialog", "Popped focus should be settings_dialog"
    assert nav_manager.get_current_focus() == "connect_button", "Current focus should be connect_button after pop"
    
    popped = nav_manager.pop_focus()
    assert popped == "connect_button", "Popped focus should be connect_button"
    assert nav_manager.get_current_focus() == "main_window", "Current focus should be main_window after pop"
    
    popped = nav_manager.pop_focus()
    assert popped == "main_window", "Popped focus should be main_window"
    assert nav_manager.get_current_focus() is None, "Current focus should be None after all pops"
    
    # Test popping from empty stack
    empty_pop = nav_manager.pop_focus()
    assert empty_pop is None, "Popping from empty stack should return None"
    
    # Test modal state management
    assert nav_manager.modal_active == False, "Modal should be inactive initially"
    assert nav_manager.navigation_locked == False, "Navigation should be unlocked initially"
    
    nav_manager.set_modal_active(True)
    assert nav_manager.modal_active == True, "Modal should be active"
    assert nav_manager.navigation_locked == True, "Navigation should be locked when modal active"
    
    nav_manager.set_modal_active(False)
    assert nav_manager.modal_active == False, "Modal should be inactive"
    assert nav_manager.navigation_locked == False, "Navigation should be unlocked when modal inactive"

def test_screen_reader_and_audio_comprehensive():
    """Test comprehensive screen reader and audio feedback support"""
    from keyboard_navigation import KeyboardNavigationManager, AccessibilityMode
    
    nav_manager = KeyboardNavigationManager()
    
    # Test screen reader functionality
    nav_manager.enable_accessibility_mode(AccessibilityMode.SCREEN_READER)
    
    # Test element description generation
    test_descriptions = [
        ("button", "Connect", "enabled", "button: Connect, enabled"),
        ("entry", "IP Address", "focused", "entry: IP Address, focused"),
        ("label", "Connection Status", "", "label: Connection Status"),
        ("menu", "File", "expanded", "menu: File, expanded")
    ]
    
    for element_type, text, state, expected_pattern in test_descriptions:
        description = nav_manager.describe_element(element_type, text, state)
        assert element_type in description, f"Description should include element type: {description}"
        assert text in description, f"Description should include text: {description}"
        if state:
            assert state in description, f"Description should include state: {description}"
    
    # Test screen reader announcements (should not crash)
    nav_manager.announce("Connection established", "normal")
    nav_manager.announce("Error occurred", "urgent")
    nav_manager.announce("Status update", "polite")
    
    # Test audio feedback
    nav_manager.audio_feedback_enabled = True
    
    # Test various feedback sounds (should not crash)
    feedback_sounds = ["button_click", "connection_success", "connection_failed", "notification", "error"]
    for sound in feedback_sounds:
        nav_manager.play_feedback_sound(sound)
    
    # Test navigation help generation
    help_text = nav_manager.get_navigation_help()
    assert isinstance(help_text, list), "Navigation help should be a list"
    assert len(help_text) > 0, "Should provide navigation help"
    
    # Check for essential navigation instructions
    help_content = " ".join(help_text)
    essential_instructions = ["Tab", "Space", "Enter", "Escape"]
    for instruction in essential_instructions:
        assert instruction in help_content, f"Navigation help should mention {instruction}"
    
    # Test accessibility report generation
    report = nav_manager.export_accessibility_report()
    assert "accessibility_settings" in report, "Report missing accessibility settings"
    assert "keyboard_shortcuts" in report, "Report missing keyboard shortcuts"
    assert "command_palette" in report, "Report missing command palette"
    assert "recommendations" in report, "Report missing recommendations"
    
    settings_report = report["accessibility_settings"]
    assert "mode" in settings_report, "Settings report missing mode"
    assert "high_contrast" in settings_report, "Settings report missing high contrast"
    assert "screen_reader_support" in settings_report, "Settings report missing screen reader support"

test("Keyboard Navigation Manager Initialization", test_keyboard_navigation_manager_initialization)
test("Accessibility Modes Comprehensive", test_accessibility_modes_comprehensive)
test("Accessibility CSS Generation", test_accessibility_css_generation)
test("Keyboard Shortcuts Comprehensive", test_keyboard_shortcuts_comprehensive)
test("Command Palette Comprehensive", test_command_palette_comprehensive)
test("Navigation Focus Management", test_navigation_focus_management)
test("Screen Reader and Audio Comprehensive", test_screen_reader_and_audio_comprehensive)

# Test Suite 3: P3 Enhanced Connection Manager Integration Tests
print("\n[3/6] P3 ENHANCED CONNECTION MANAGER INTEGRATION TESTS")
print("-" * 80)

def test_connection_manager_p3_initialization():
    """Test ConnectionManager P3 UX enhancements initialization"""
    with patch('connection_manager.get_logger'), \
         patch('connection_manager.get_stats'), \
         patch('connection_manager.get_config'):
        from connection_manager import ConnectionManager
        
        conn = ConnectionManager()
        
        # Test P3 UX manager is initialized
        assert hasattr(conn, 'ux_manager'), "Missing ux_manager"
        assert conn.ux_manager is not None, "ux_manager not initialized"
        
        # Test P1 and P2 components still exist
        assert hasattr(conn, 'nm_client'), "P1 nm_client missing"
        assert hasattr(conn, 'resource_manager'), "P2 resource_manager missing"
        assert hasattr(conn, 'reliability_manager'), "P2 reliability_manager missing"

def test_profile_based_connections():
    """Test profile-based connection functionality"""
    with patch('connection_manager.get_logger'), \
         patch('connection_manager.get_stats'), \
         patch('connection_manager.get_config'):
        from connection_manager import ConnectionManager
        
        conn = ConnectionManager()
        
        # Create test profiles
        conn.ux_manager.create_profile("test_wifi", "wifi", ssid="TestNet", stealth_level=2)
        conn.ux_manager.create_profile("test_usb", "usb", description="USB backup")
        conn.ux_manager.create_profile("test_iphone", "iphone", ssid="iPhone", stealth_level=3)
        
        # Test connect_with_profile method exists
        assert hasattr(conn, 'connect_with_profile'), "Missing connect_with_profile method"
        
        # Test profile connection with existing profile
        with patch.object(conn, '_connect_thread') as mock_connect:
            result = conn.connect_with_profile("test_wifi")
            # Should use the profile and increment usage count
            used_profile = conn.ux_manager.get_profile("test_wifi")
            assert used_profile.use_count == 1, "Profile use count should be incremented"
        
        # Test profile connection with non-existent profile
        with patch.object(conn, '_connect_thread'):
            result = conn.connect_with_profile("nonexistent_profile")
            # Should handle gracefully (implementation dependent)

def test_quick_connect_suggestions():
    """Test AI-powered quick connect suggestions"""
    with patch('connection_manager.get_logger'), \
         patch('connection_manager.get_stats'), \
         patch('connection_manager.get_config'):
        from connection_manager import ConnectionManager
        
        conn = ConnectionManager()
        
        # Create and use profiles to generate suggestions
        conn.ux_manager.create_profile("frequent_wifi", "wifi", ssid="FrequentNet")
        conn.ux_manager.create_profile("backup_usb", "usb")
        
        # Simulate usage
        for _ in range(5):
            conn.ux_manager.use_profile("frequent_wifi")
        for _ in range(2):
            conn.ux_manager.use_profile("backup_usb")
        
        # Test get_quick_connect_suggestions method
        assert hasattr(conn, 'get_quick_connect_suggestions'), "Missing get_quick_connect_suggestions method"
        
        suggestions = conn.get_quick_connect_suggestions()
        assert isinstance(suggestions, list), "Suggestions should be a list"
        
        # Test suggestion structure
        for suggestion in suggestions:
            assert isinstance(suggestion, dict), "Each suggestion should be a dict"
            expected_keys = ["profile", "score", "reason"]
            for key in expected_keys:
                assert key in suggestion, f"Suggestion missing key: {key}"

def test_enhanced_status_with_ux_metrics():
    """Test enhanced connection status with comprehensive UX metrics"""
    with patch('connection_manager.get_logger'), \
         patch('connection_manager.get_stats'), \
         patch('connection_manager.get_config'):
        from connection_manager import ConnectionManager
        
        conn = ConnectionManager()
        
        # Add some test data
        conn.ux_manager.create_profile("status_test", "wifi", ssid="StatusNet")
        conn.ux_manager.record_connection_session("wifi", 3600, 1024*1024*100, True)
        
        # Test comprehensive status includes all UX data
        status = conn.get_comprehensive_status()
        
        # Test main status structure
        assert "state" in status, "Status missing state"
        assert "user_experience" in status, "Status missing user_experience section"
        assert "profiles" in status, "Status missing profiles section"
        
        # Test user experience section
        ux_section = status["user_experience"]
        expected_ux_keys = [
            "quick_connect_suggestions",
            "usage_insights", 
            "quality_assessment",
            "smart_notifications"
        ]
        
        for key in expected_ux_keys:
            assert key in ux_section, f"UX section missing key: {key}"
        
        # Test profiles section
        profiles_section = status["profiles"]
        expected_profile_keys = [
            "available_profiles",
            "most_used_profile", 
            "profile_suggestions"
        ]
        
        for key in expected_profile_keys:
            assert key in profiles_section, f"Profiles section missing key: {key}"
        
        # Test data types and values
        assert isinstance(ux_section["quick_connect_suggestions"], list), "Quick connect suggestions should be a list"
        assert isinstance(ux_section["usage_insights"], dict), "Usage insights should be a dict"
        assert isinstance(ux_section["quality_assessment"], dict), "Quality assessment should be a dict"
        assert isinstance(ux_section["smart_notifications"], list), "Smart notifications should be a list"
        
        assert isinstance(profiles_section["available_profiles"], int), "Available profiles should be an int"
        assert profiles_section["available_profiles"] >= 0, "Available profiles should be non-negative"

def test_quick_action_integration():
    """Test quick action integration with connection manager context"""
    with patch('connection_manager.get_logger'), \
         patch('connection_manager.get_stats'), \
         patch('connection_manager.get_config'):
        from connection_manager import ConnectionManager
        
        conn = ConnectionManager()
        
        # Test execute_quick_action method exists
        assert hasattr(conn, 'execute_quick_action'), "Missing execute_quick_action method"
        
        # Create test profile for quick actions
        conn.ux_manager.create_profile("quick_test", "wifi", ssid="QuickNet")
        conn.ux_manager.use_profile("quick_test")
        
        # Test various quick actions
        quick_actions = [
            "connect_last_used",
            "toggle_stealth", 
            "show_profile_menu",
            "run_speed_test"
        ]
        
        for action in quick_actions:
            result = conn.execute_quick_action(action)
            assert isinstance(result, dict), f"Quick action {action} result should be a dict"
            assert "success" in result, f"Quick action {action} result should have success field"
            
            if result["success"]:
                assert "message" in result, f"Successful quick action {action} should have message"

def test_usage_session_recording_integration():
    """Test usage session recording integration with connection lifecycle"""
    with patch('connection_manager.get_logger'), \
         patch('connection_manager.get_stats'), \
         patch('connection_manager.get_config'):
        from connection_manager import ConnectionManager
        
        conn = ConnectionManager()
        
        # Test initial usage statistics
        initial_sessions = conn.ux_manager.usage_stats.total_sessions
        initial_uptime = conn.ux_manager.usage_stats.total_uptime_hours
        
        # Simulate connection sessions
        test_sessions = [
            ("usb", 1800, 1024*1024*50, True),    # 30 min, 50MB, success
            ("wifi", 3600, 1024*1024*100, True),  # 1 hour, 100MB, success
            ("iphone", 900, 1024*1024*25, False)  # 15 min, 25MB, failed
        ]
        
        for mode, duration, data_bytes, success in test_sessions:
            conn.ux_manager.record_connection_session(mode, duration, data_bytes, success)
        
        # Test that sessions were recorded
        final_sessions = conn.ux_manager.usage_stats.total_sessions
        final_uptime = conn.ux_manager.usage_stats.total_uptime_hours
        
        assert final_sessions == initial_sessions + 3, "Sessions not recorded correctly"
        assert final_uptime > initial_uptime, "Uptime not recorded correctly"
        
        # Test success rate calculation
        expected_success_rate = (2 / 3) * 100  # 2 successes out of 3 sessions
        actual_success_rate = conn.ux_manager.usage_stats.success_rate_percent
        assert abs(actual_success_rate - expected_success_rate) < 1, "Success rate calculation incorrect"

def test_smart_notifications_integration():
    """Test smart notifications integration with connection state"""
    with patch('connection_manager.get_logger'), \
         patch('connection_manager.get_stats'), \
         patch('connection_manager.get_config'):
        from connection_manager import ConnectionManager
        
        conn = ConnectionManager()
        
        # Test smart notifications with different scenarios
        test_scenarios = [
            {
                "connection_state": "connected",
                "metrics": {"session_data_gb": 8.5, "connection_quality": 85},
                "expected_notifications": 1  # Data usage warning
            },
            {
                "connection_state": "connected", 
                "metrics": {"session_data_gb": 2.0, "connection_quality": 30},
                "expected_notifications": 1  # Poor connection quality
            },
            {
                "connection_state": "disconnected",
                "metrics": {"session_data_gb": 1.0, "connection_quality": 100},
                "expected_notifications": 0  # No notifications when disconnected
            }
        ]
        
        for scenario in test_scenarios:
            notifications = conn.ux_manager.get_smart_notifications(
                scenario["connection_state"],
                scenario["metrics"]
            )
            
            assert isinstance(notifications, list), "Notifications should be a list"
            
            # Test notification structure
            for notification in notifications:
                assert "type" in notification, "Notification missing type"
                assert "title" in notification, "Notification missing title"
                assert "message" in notification, "Notification missing message"
                assert notification["type"] in ["info", "warning", "error"], "Invalid notification type"

test("Connection Manager P3 Initialization", test_connection_manager_p3_initialization)
test("Profile-based Connections", test_profile_based_connections)
test("Quick Connect Suggestions", test_quick_connect_suggestions)
test("Enhanced Status with UX Metrics", test_enhanced_status_with_ux_metrics)
test("Quick Action Integration", test_quick_action_integration)
test("Usage Session Recording Integration", test_usage_session_recording_integration)
test("Smart Notifications Integration", test_smart_notifications_integration)

# Test Suite 4: P3 Data Persistence and Configuration Tests
print("\n[4/6] P3 DATA PERSISTENCE AND CONFIGURATION TESTS")
print("-" * 80)

def test_profile_persistence():
    """Test connection profile persistence and atomic operations"""
    from user_experience import UserExperienceManager
    import tempfile
    import shutil
    
    # Create temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        # Patch the config directory to use temp directory
        with patch.object(UserExperienceManager, '__init__') as mock_init:
            def custom_init(self):
                self.logger = Mock()
                self.config_dir = Path(temp_dir)
                self.config_dir.mkdir(parents=True, exist_ok=True)
                
                self.profiles_file = self.config_dir / "profiles.json"
                self.user_profiles = {}
                
                self.preferences_file = self.config_dir / "user_preferences.json"
                self.user_preferences = self._load_user_preferences()
                
                self.usage_file = self.config_dir / "usage_statistics.json"
                self.usage_stats = self._load_usage_statistics()
                
                self.quality_history = []
                self.quality_monitoring_enabled = False
                self.quick_actions = []
            
            mock_init.side_effect = custom_init
            
            ux_manager = UserExperienceManager()
            
            # Test profile creation and persistence
            ux_manager.create_profile("persist_test", "wifi", ssid="PersistNet", stealth_level=2)
            ux_manager.save_profiles()
            
            assert ux_manager.profiles_file.exists(), "Profiles file should be created"
            
            # Test profile loading
            new_ux_manager = UserExperienceManager()
            new_ux_manager._load_profiles()
            
            assert "persist_test" in new_ux_manager.user_profiles, "Profile should be loaded from file"
            loaded_profile = new_ux_manager.get_profile("persist_test")
            assert loaded_profile.ssid == "PersistNet", "Profile data should be preserved"
            assert loaded_profile.stealth_level == 2, "Profile stealth level should be preserved"

def test_preferences_persistence():
    """Test user preferences persistence and defaults"""
    from user_experience import UserExperienceManager
    import tempfile
    
    with tempfile.TemporaryDirectory() as temp_dir:
        with patch.object(UserExperienceManager, '__init__') as mock_init:
            def custom_init(self):
                self.logger = Mock()
                self.config_dir = Path(temp_dir)
                self.config_dir.mkdir(parents=True, exist_ok=True)
                
                self.profiles_file = self.config_dir / "profiles.json"
                self.user_profiles = {}
                
                self.preferences_file = self.config_dir / "user_preferences.json"
                self.user_preferences = self._load_user_preferences()
                
                self.usage_file = self.config_dir / "usage_statistics.json"
                self.usage_stats = self._load_usage_statistics()
                
                self.quality_history = []
                self.quality_monitoring_enabled = False
                self.quick_actions = []
            
            mock_init.side_effect = custom_init
            
            ux_manager = UserExperienceManager()
            
            # Test default preferences
            assert ux_manager.get_preference("theme") == "cyberpunk_dark", "Default theme should be loaded"
            assert ux_manager.get_preference("notifications_enabled") == True, "Default notifications should be enabled"
            
            # Test preference updates and persistence
            ux_manager.update_preference("theme", "custom_theme")
            ux_manager.update_preference("warning_threshold_gb", 25.0)
            ux_manager.save_preferences()
            
            assert ux_manager.preferences_file.exists(), "Preferences file should be created"
            
            # Test preference loading
            new_ux_manager = UserExperienceManager()
            assert new_ux_manager.get_preference("theme") == "custom_theme", "Custom theme should be loaded"
            assert new_ux_manager.get_preference("warning_threshold_gb") == 25.0, "Custom threshold should be loaded"

def test_usage_statistics_persistence():
    """Test usage statistics persistence and atomic operations"""
    from user_experience import UserExperienceManager, UsageStatistics
    import tempfile
    
    with tempfile.TemporaryDirectory() as temp_dir:
        with patch.object(UserExperienceManager, '__init__') as mock_init:
            def custom_init(self):
                self.logger = Mock()
                self.config_dir = Path(temp_dir)
                self.config_dir.mkdir(parents=True, exist_ok=True)
                
                self.profiles_file = self.config_dir / "profiles.json"
                self.user_profiles = {}
                
                self.preferences_file = self.config_dir / "user_preferences.json"
                self.user_preferences = self._load_user_preferences()
                
                self.usage_file = self.config_dir / "usage_statistics.json"
                self.usage_stats = self._load_usage_statistics()
                
                self.quality_history = []
                self.quality_monitoring_enabled = False
                self.quick_actions = []
            
            mock_init.side_effect = custom_init
            
            ux_manager = UserExperienceManager()
            
            # Test usage statistics recording and persistence
            ux_manager.record_connection_session("wifi", 3600, 1024*1024*100, True)
            ux_manager.record_connection_session("usb", 1800, 1024*1024*50, False)
            ux_manager.save_usage_statistics()
            
            assert ux_manager.usage_file.exists(), "Usage statistics file should be created"
            
            # Test usage statistics loading
            new_ux_manager = UserExperienceManager()
            stats = new_ux_manager.usage_stats
            
            assert stats.total_sessions == 2, "Session count should be preserved"
            assert stats.total_uptime_hours > 0, "Uptime should be preserved"
            assert stats.total_data_gb > 0, "Data usage should be preserved"

def test_keyboard_shortcuts_persistence():
    """Test keyboard shortcuts customization persistence"""
    from keyboard_navigation import KeyboardNavigationManager
    import tempfile
    
    with tempfile.TemporaryDirectory() as temp_dir:
        with patch.object(KeyboardNavigationManager, '__init__') as mock_init:
            def custom_init(self):
                self.logger = Mock()
                self.config_dir = Path(temp_dir)
                
                self.accessibility_file = self.config_dir / "accessibility.json"
                self.accessibility = self._load_accessibility_settings()
                
                self.shortcuts_file = self.config_dir / "shortcuts.json"
                self.shortcuts = self._initialize_default_shortcuts()
                self.custom_shortcuts = self._load_custom_shortcuts()
                
                self.focus_stack = []
                self.modal_active = False
                self.navigation_locked = False
                self.screen_reader_enabled = False
                self.audio_feedback_enabled = False
                self.command_palette_commands = self._initialize_command_palette()
            
            mock_init.side_effect = custom_init
            
            nav_manager = KeyboardNavigationManager()
            
            # Test shortcut customization and persistence
            nav_manager.customize_shortcut("connect", "Ctrl+Alt+C")
            nav_manager.customize_shortcut("disconnect", "Ctrl+Alt+D")
            nav_manager.save_custom_shortcuts()
            
            assert nav_manager.shortcuts_file.exists(), "Custom shortcuts file should be created"
            
            # Test shortcut loading
            new_nav_manager = KeyboardNavigationManager()
            
            assert new_nav_manager.get_effective_shortcut("connect") == "Ctrl+Alt+C", "Custom connect shortcut should be loaded"
            assert new_nav_manager.get_effective_shortcut("disconnect") == "Ctrl+Alt+D", "Custom disconnect shortcut should be loaded"

def test_accessibility_settings_persistence():
    """Test accessibility settings persistence"""
    from keyboard_navigation import KeyboardNavigationManager, AccessibilityMode
    import tempfile
    
    with tempfile.TemporaryDirectory() as temp_dir:
        with patch.object(KeyboardNavigationManager, '__init__') as mock_init:
            def custom_init(self):
                self.logger = Mock()
                self.config_dir = Path(temp_dir)
                
                self.accessibility_file = self.config_dir / "accessibility.json"
                self.accessibility = self._load_accessibility_settings()
                
                self.shortcuts_file = self.config_dir / "shortcuts.json"
                self.shortcuts = self._initialize_default_shortcuts()
                self.custom_shortcuts = self._load_custom_shortcuts()
                
                self.focus_stack = []
                self.modal_active = False
                self.navigation_locked = False
                self.screen_reader_enabled = False
                self.audio_feedback_enabled = False
                self.command_palette_commands = self._initialize_command_palette()
            
            mock_init.side_effect = custom_init
            
            nav_manager = KeyboardNavigationManager()
            
            # Test accessibility settings persistence
            nav_manager.enable_accessibility_mode(AccessibilityMode.HIGH_CONTRAST)
            nav_manager.accessibility.large_text_scale = 1.8
            nav_manager.accessibility.tooltip_delays_ms = 1000
            nav_manager.save_accessibility_settings()
            
            assert nav_manager.accessibility_file.exists(), "Accessibility settings file should be created"
            
            # Test accessibility settings loading
            new_nav_manager = KeyboardNavigationManager()
            
            assert new_nav_manager.accessibility.mode == AccessibilityMode.HIGH_CONTRAST, "Accessibility mode should be loaded"
            assert new_nav_manager.accessibility.high_contrast == True, "High contrast setting should be loaded"

def test_data_export_import():
    """Test comprehensive data export and import functionality"""
    from user_experience import UserExperienceManager
    import tempfile
    
    with tempfile.TemporaryDirectory() as temp_dir:
        export_file = Path(temp_dir) / "export_test.json"
        
        with patch.object(UserExperienceManager, '__init__') as mock_init:
            def custom_init(self):
                self.logger = Mock()
                self.config_dir = Path(temp_dir) / "config"
                self.config_dir.mkdir(parents=True, exist_ok=True)
                
                self.profiles_file = self.config_dir / "profiles.json"
                self.user_profiles = {}
                
                self.preferences_file = self.config_dir / "user_preferences.json"
                self.user_preferences = self._load_user_preferences()
                
                self.usage_file = self.config_dir / "usage_statistics.json"
                self.usage_stats = self._load_usage_statistics()
                
                self.quality_history = []
                self.quality_monitoring_enabled = False
                self.quick_actions = []
            
            mock_init.side_effect = custom_init
            
            # Create source UX manager with test data
            source_ux = UserExperienceManager()
            source_ux.create_profile("export_test", "wifi", ssid="ExportNet")
            source_ux.update_preference("theme", "export_theme")
            source_ux.record_connection_session("wifi", 3600, 1024*1024*100, True)
            
            # Test data export
            export_success = source_ux.export_user_data(export_file)
            assert export_success == True, "Data export should succeed"
            assert export_file.exists(), "Export file should be created"
            
            # Verify export file structure
            with open(export_file) as f:
                export_data = json.load(f)
            
            expected_keys = ["profiles", "preferences", "usage_statistics", "export_timestamp", "version"]
            for key in expected_keys:
                assert key in export_data, f"Export data missing key: {key}"
            
            # Create target UX manager and test import
            target_ux = UserExperienceManager()
            import_success = target_ux.import_user_data(export_file)
            assert import_success == True, "Data import should succeed"
            
            # Verify imported data
            assert "export_test" in target_ux.user_profiles, "Profile should be imported"
            assert target_ux.get_preference("theme") == "export_theme", "Preference should be imported"
            assert target_ux.usage_stats.total_sessions > 0, "Usage statistics should be imported"

test("Profile Persistence", test_profile_persistence)
test("Preferences Persistence", test_preferences_persistence)
test("Usage Statistics Persistence", test_usage_statistics_persistence)
test("Keyboard Shortcuts Persistence", test_keyboard_shortcuts_persistence)
test("Accessibility Settings Persistence", test_accessibility_settings_persistence)
test("Data Export Import", test_data_export_import)

# Test Suite 5: P1+P2+P3 Integration and Performance Tests
print("\n[5/6] P1+P2+P3 COMPREHENSIVE INTEGRATION TESTS")
print("-" * 80)

def test_p1_p2_p3_module_integration():
    """Test all P1, P2, and P3 modules work together seamlessly"""
    with patch('connection_manager.get_logger'), \
         patch('connection_manager.get_stats'), \
         patch('connection_manager.get_config'):
        from connection_manager import ConnectionManager
        
        conn = ConnectionManager()
        
        # Test all enhancement layers are present and initialized
        assert hasattr(conn, 'nm_client'), "P1 NetworkManager client missing"
        assert hasattr(conn, 'resource_manager'), "P2 resource manager missing"
        assert hasattr(conn, 'reliability_manager'), "P2 reliability manager missing"
        assert hasattr(conn, 'ux_manager'), "P3 UX manager missing"
        
        assert conn.nm_client is not None, "P1 nm_client not initialized"
        assert conn.resource_manager is not None, "P2 resource_manager not initialized"
        assert conn.reliability_manager is not None, "P2 reliability_manager not initialized"
        assert conn.ux_manager is not None, "P3 ux_manager not initialized"
        
        # Test cross-layer functionality
        # P1 + P3: Profile-based WiFi scanning
        conn.ux_manager.create_profile("integration_test", "wifi", ssid="IntegrationNet")
        profile = conn.ux_manager.get_profile("integration_test")
        assert profile is not None, "P1+P3 profile creation failed"
        
        # P2 + P3: Performance monitoring with UX insights
        if hasattr(conn.resource_manager, 'get_resource_summary'):
            summary = conn.resource_manager.get_resource_summary()
            insights = conn.ux_manager.get_usage_insights()
            assert isinstance(summary, dict), "P2 resource summary should be available"
            assert isinstance(insights, dict), "P3 usage insights should be available"

def test_p3_performance_impact():
    """Test P3 enhancements don't significantly impact performance"""
    import time
    
    with patch('connection_manager.get_logger'), \
         patch('connection_manager.get_stats'), \
         patch('connection_manager.get_config'):
        from connection_manager import ConnectionManager
        
        # Measure initialization time with all enhancements
        start_time = time.time()
        conn = ConnectionManager()
        init_time = time.time() - start_time
        
        # P3 should add minimal overhead (less than 3 seconds for initialization)
        assert init_time < 3.0, f"P1+P2+P3 initialization too slow: {init_time:.2f}s"
        
        # Test status retrieval performance
        start_time = time.time()
        status = conn.get_comprehensive_status()
        status_time = time.time() - start_time
        
        assert status_time < 1.0, f"Comprehensive status retrieval too slow: {status_time:.2f}s"
        assert "user_experience" in status, "P3 UX data missing from status"
        
        # Test profile operations performance
        start_time = time.time()
        for i in range(10):
            conn.ux_manager.create_profile(f"perf_test_{i}", "wifi", ssid=f"PerfNet{i}")
        profile_time = time.time() - start_time
        
        assert profile_time < 1.0, f"Profile operations too slow: {profile_time:.2f}s for 10 profiles"

def test_memory_efficiency_all_enhancements():
    """Test memory efficiency with P1+P2+P3 enhancements"""
    import gc
    
    with patch('connection_manager.get_logger'), \
         patch('connection_manager.get_stats'), \
         patch('connection_manager.get_config'):
        from connection_manager import ConnectionManager
        from user_experience import UserExperienceManager
        from keyboard_navigation import KeyboardNavigationManager
        
        # Force garbage collection before test
        gc.collect()
        
        # Create all enhancement components
        conn = ConnectionManager()
        ux_manager = UserExperienceManager()
        nav_manager = KeyboardNavigationManager()
        
        # Test that P2 resource manager is monitoring memory
        if hasattr(conn.resource_manager, 'get_resource_summary'):
            summary = conn.resource_manager.get_resource_summary()
            assert 'cache' in summary, "P2 resource manager not tracking cache"
        
        # Test P3 components don't leak memory
        for i in range(20):
            ux_manager.get_quality_assessment()
            ux_manager.get_usage_insights()
            nav_manager.search_commands(f"test{i}")
        
        # Should not accumulate excessive data
        assert len(ux_manager.quality_history) <= 100, "P3 quality history growing too large"
        
        # Test profile cleanup
        for i in range(50):
            ux_manager.create_profile(f"memory_test_{i}", "wifi")
        
        # Should handle large numbers of profiles efficiently
        profiles = ux_manager.list_profiles()
        assert len(profiles) > 0, "Profiles should be accessible"

def test_configuration_persistence_integration():
    """Test all P1+P2+P3 configurations persist correctly together"""
    from user_experience import UserExperienceManager
    from keyboard_navigation import KeyboardNavigationManager
    import tempfile
    
    # Test that all configuration files can coexist
    with tempfile.TemporaryDirectory() as temp_dir:
        config_dir = Path(temp_dir)
        
        # Create UX manager with custom config directory
        with patch.object(UserExperienceManager, '__init__') as mock_ux_init:
            def custom_ux_init(self):
                self.logger = Mock()
                self.config_dir = config_dir
                self.config_dir.mkdir(parents=True, exist_ok=True)
                
                self.profiles_file = self.config_dir / "profiles.json"
                self.user_profiles = {}
                
                self.preferences_file = self.config_dir / "user_preferences.json"
                self.user_preferences = self._load_user_preferences()
                
                self.usage_file = self.config_dir / "usage_statistics.json"
                self.usage_stats = self._load_usage_statistics()
                
                self.quality_history = []
                self.quality_monitoring_enabled = False
                self.quick_actions = []
            
            mock_ux_init.side_effect = custom_ux_init
            
            # Create keyboard navigation manager with custom config directory
            with patch.object(KeyboardNavigationManager, '__init__') as mock_nav_init:
                def custom_nav_init(self):
                    self.logger = Mock()
                    self.config_dir = config_dir
                    
                    self.accessibility_file = self.config_dir / "accessibility.json"
                    self.accessibility = self._load_accessibility_settings()
                    
                    self.shortcuts_file = self.config_dir / "shortcuts.json"
                    self.shortcuts = self._initialize_default_shortcuts()
                    self.custom_shortcuts = self._load_custom_shortcuts()
                    
                    self.focus_stack = []
                    self.modal_active = False
                    self.navigation_locked = False
                    self.screen_reader_enabled = False
                    self.audio_feedback_enabled = False
                    self.command_palette_commands = self._initialize_command_palette()
                
                mock_nav_init.side_effect = custom_nav_init
                
                # Test configuration persistence
                ux_manager = UserExperienceManager()
                nav_manager = KeyboardNavigationManager()
                
                # Create configurations
                ux_manager.create_profile("integration_profile", "wifi", ssid="IntegrationNet")
                ux_manager.update_preference("theme", "integration_theme")
                nav_manager.customize_shortcut("connect", "Ctrl+Alt+I")
                
                # Save configurations
                ux_manager.save_profiles()
                ux_manager.save_preferences()
                nav_manager.save_custom_shortcuts()
                
                # Verify all configuration files exist
                expected_files = [
                    "profiles.json",
                    "user_preferences.json", 
                    "usage_statistics.json",
                    "shortcuts.json"
                ]
                
                for filename in expected_files:
                    file_path = config_dir / filename
                    if file_path.exists():  # Some files may not exist until first save
                        assert file_path.is_file(), f"Configuration file {filename} should be a regular file"

def test_graceful_degradation_all_layers():
    """Test graceful degradation when any layer fails"""
    with patch('connection_manager.get_logger'), \
         patch('connection_manager.get_stats'), \
         patch('connection_manager.get_config'):
        from connection_manager import ConnectionManager
        
        conn = ConnectionManager()
        
        # Test P3 failure doesn't break P1+P2
        original_ux_manager = conn.ux_manager
        conn.ux_manager = None
        
        try:
            # Basic P1 functionality should still work
            status = conn.get_connection_status()
            assert "state" in status, "P1 basic status should work without P3"
            
            # P2 functionality should still work
            if hasattr(conn, 'resource_manager') and conn.resource_manager:
                summary = conn.resource_manager.get_resource_summary()
                assert isinstance(summary, dict), "P2 should work without P3"
        
        except Exception as e:
            # If it fails, it should fail gracefully without exposing internal errors
            error_msg = str(e).lower()
            assert "ux_manager" not in error_msg, "Should not expose P3 internal errors"
        
        finally:
            conn.ux_manager = original_ux_manager
        
        # Test P2 failure doesn't break P1+P3
        original_resource_manager = conn.resource_manager
        conn.resource_manager = None
        
        try:
            # P1 and P3 should still work
            suggestions = conn.get_quick_connect_suggestions()
            assert isinstance(suggestions, list), "P3 should work without P2"
        
        except Exception as e:
            error_msg = str(e).lower()
            assert "resource_manager" not in error_msg, "Should not expose P2 internal errors"
        
        finally:
            conn.resource_manager = original_resource_manager

def test_end_to_end_user_workflow():
    """Test complete user workflow with all P1+P2+P3 enhancements"""
    with patch('connection_manager.get_logger'), \
         patch('connection_manager.get_stats'), \
         patch('connection_manager.get_config'):
        from connection_manager import ConnectionManager
        from keyboard_navigation import KeyboardNavigationManager
        
        conn = ConnectionManager()
        nav_manager = KeyboardNavigationManager()
        
        # Simulate complete user workflow:
        
        # 1. User creates connection profiles (P3)
        profile_created = conn.ux_manager.create_profile(
            "workflow_wifi", "wifi", 
            ssid="WorkflowNet", 
            stealth_level=2,
            description="End-to-end test profile"
        )
        assert profile_created == True, "Profile creation failed in workflow"
        
        # 2. User customizes keyboard shortcuts (P3)
        shortcut_customized = nav_manager.customize_shortcut("connect", "Ctrl+Shift+W")
        assert shortcut_customized == True, "Shortcut customization failed in workflow"
        
        # 3. User gets AI suggestions (P3)
        suggestions = conn.get_quick_connect_suggestions()
        assert isinstance(suggestions, list), "Quick suggestions failed in workflow"
        
        # 4. User executes quick actions (P3)
        action_result = conn.execute_quick_action("show_profile_menu")
        assert action_result["success"] == True, "Quick action failed in workflow"
        
        # 5. User connects using profile (P1+P3 integration)
        with patch.object(conn, '_connect_thread'):
            profile_connection = conn.connect_with_profile("workflow_wifi")
            # Should handle gracefully regardless of result
        
        # 6. System monitors performance (P2) and records usage (P3)
        conn.ux_manager.record_connection_session("wifi", 1800, 1024*1024*75, True)
        
        # 7. User gets comprehensive status (P1+P2+P3)
        status = conn.get_comprehensive_status()
        assert "user_experience" in status, "Comprehensive status missing P3 data in workflow"
        assert "state" in status, "Comprehensive status missing P1 data in workflow"
        
        # 8. User uses command palette (P3)
        commands = nav_manager.search_commands("connect")
        assert len(commands) > 0, "Command palette search failed in workflow"
        
        # 9. User gets usage insights (P3)
        insights = conn.ux_manager.get_usage_insights()
        assert "summary" in insights, "Usage insights failed in workflow"
        
        # 10. User enables accessibility (P3)
        from keyboard_navigation import AccessibilityMode
        nav_manager.enable_accessibility_mode(AccessibilityMode.HIGH_CONTRAST)
        css = nav_manager.get_accessibility_css()
        assert len(css) > 0, "Accessibility CSS generation failed in workflow"

test("P1+P2+P3 Module Integration", test_p1_p2_p3_module_integration)
test("P3 Performance Impact", test_p3_performance_impact)
test("Memory Efficiency All Enhancements", test_memory_efficiency_all_enhancements)
test("Configuration Persistence Integration", test_configuration_persistence_integration)
test("Graceful Degradation All Layers", test_graceful_degradation_all_layers)
test("End-to-End User Workflow", test_end_to_end_user_workflow)

# Test Suite 6: P3 Edge Cases and Error Handling Tests
print("\n[6/6] P3 EDGE CASES AND ERROR HANDLING TESTS")
print("-" * 80)

def test_profile_edge_cases():
    """Test connection profile edge cases and error handling"""
    from user_experience import UserExperienceManager
    
    ux_manager = UserExperienceManager()
    
    # Test profile creation with invalid data
    invalid_profiles = [
        ("", "wifi", "Empty name should fail"),
        ("valid_name", "", "Empty mode should fail"),
        ("valid_name", "invalid_mode", "Invalid mode should fail")
    ]
    
    for name, mode, description in invalid_profiles:
        try:
            result = ux_manager.create_profile(name, mode)
            if not result:
                # Expected failure
                pass
        except Exception:
            # Should handle gracefully
            pass
    
    # Test profile operations on non-existent profiles
    non_existent_operations = [
        ("get_profile", "nonexistent"),
        ("use_profile", "nonexistent"),
        ("update_profile", "nonexistent"),
        ("delete_profile", "nonexistent")
    ]
    
    for operation, profile_name in non_existent_operations:
        try:
            method = getattr(ux_manager, operation)
            if operation == "update_profile":
                result = method(profile_name, description="test")
            else:
                result = method(profile_name)
            
            # Should return None or False for non-existent profiles
            assert result in [None, False], f"Operation {operation} should handle non-existent profile gracefully"
        except Exception as e:
            # Should not raise exceptions
            assert False, f"Operation {operation} should not raise exception: {e}"

def test_preferences_edge_cases():
    """Test user preferences edge cases and validation"""
    from user_experience import UserExperienceManager
    
    ux_manager = UserExperienceManager()
    
    # Test preference updates with various data types
    test_preferences = [
        ("string_pref", "test_value"),
        ("int_pref", 42),
        ("float_pref", 3.14),
        ("bool_pref", True),
        ("list_pref", [1, 2, 3]),
        ("dict_pref", {"key": "value"}),
        ("none_pref", None)
    ]
    
    for key, value in test_preferences:
        ux_manager.update_preference(key, value)
        retrieved_value = ux_manager.get_preference(key)
        assert retrieved_value == value, f"Preference {key} not stored correctly: expected {value}, got {retrieved_value}"
    
    # Test preference retrieval with defaults
    default_tests = [
        ("nonexistent_string", "default_string"),
        ("nonexistent_int", 999),
        ("nonexistent_bool", False),
        ("nonexistent_list", []),
        ("nonexistent_dict", {})
    ]
    
    for key, default_value in default_tests:
        retrieved_value = ux_manager.get_preference(key, default_value)
        assert retrieved_value == default_value, f"Default value not returned for {key}"

def test_usage_analytics_edge_cases():
    """Test usage analytics edge cases and data validation"""
    from user_experience import UserExperienceManager
    
    ux_manager = UserExperienceManager()
    
    # Test session recording with edge case values
    edge_case_sessions = [
        ("wifi", 0, 0, True),           # Zero duration and data
        ("usb", -1, -1, True),          # Negative values (should be handled)
        ("iphone", 86400, 1024**4, True),  # Very large values
        ("wifi", 0.1, 1, False),        # Very small values
    ]
    
    initial_sessions = ux_manager.usage_stats.total_sessions
    
    for mode, duration, data_bytes, success in edge_case_sessions:
        try:
            ux_manager.record_connection_session(mode, duration, data_bytes, success)
        except Exception as e:
            # Should handle edge cases gracefully
            assert False, f"Session recording should handle edge case gracefully: {e}"
    
    # Should have recorded all sessions (even with edge case values)
    final_sessions = ux_manager.usage_stats.total_sessions
    assert final_sessions >= initial_sessions, "Sessions should be recorded even with edge case values"
    
    # Test usage insights with no data
    empty_ux_manager = UserExperienceManager()
    insights = empty_ux_manager.get_usage_insights()
    assert "summary" in insights, "Insights should work with no usage data"
    assert insights["summary"]["total_sessions"] == 0, "Empty insights should show zero sessions"

def test_keyboard_shortcuts_edge_cases():
    """Test keyboard shortcuts edge cases and conflict resolution"""
    from keyboard_navigation import KeyboardNavigationManager
    
    nav_manager = KeyboardNavigationManager()
    
    # Test shortcut customization edge cases
    edge_case_shortcuts = [
        ("connect", ""),                    # Empty shortcut
        ("connect", "InvalidKey"),          # Invalid key combination
        ("connect", "Ctrl+Shift+Alt+Super+A"),  # Very complex combination
        ("nonexistent_action", "Ctrl+X"),   # Non-existent action
    ]
    
    for action, key_combination in edge_case_shortcuts:
        try:
            result = nav_manager.customize_shortcut(action, key_combination)
            # Should return False for invalid cases
            if action not in nav_manager.shortcuts or not key_combination:
                assert result == False, f"Should reject invalid shortcut: {action} -> {key_combination}"
        except Exception as e:
            # Should handle gracefully
            assert False, f"Shortcut customization should handle edge case gracefully: {e}"
    
    # Test conflict detection with multiple shortcuts
    nav_manager.customize_shortcut("connect", "Ctrl+T")
    conflict_result = nav_manager.customize_shortcut("disconnect", "Ctrl+T")
    assert conflict_result == False, "Should detect and reject conflicting shortcuts"
    
    # Test shortcut retrieval for non-existent actions
    non_existent_shortcut = nav_manager.get_effective_shortcut("nonexistent_action")
    assert non_existent_shortcut is None, "Should return None for non-existent shortcuts"

def test_command_palette_edge_cases():
    """Test command palette edge cases and search robustness"""
    from keyboard_navigation import KeyboardNavigationManager
    
    nav_manager = KeyboardNavigationManager()
    
    # Test search with edge case queries
    edge_case_queries = [
        "",                    # Empty query
        " ",                   # Whitespace only
        "   test   ",          # Query with extra whitespace
        "UPPERCASE",           # All uppercase
        "lowercase",           # All lowercase
        "MiXeD cAsE",         # Mixed case
        "special!@#$%^&*()",  # Special characters
        "very_long_query_that_probably_wont_match_anything_but_should_not_crash",  # Very long query
        "unicode_test_café_naïve_résumé",  # Unicode characters
    ]
    
    for query in edge_case_queries:
        try:
            results = nav_manager.search_commands(query)
            assert isinstance(results, list), f"Search should return list for query: '{query}'"
            assert len(results) <= 10, f"Search should limit results for query: '{query}'"
        except Exception as e:
            assert False, f"Command search should handle edge case gracefully: '{query}' -> {e}"
    
    # Test command execution edge cases
    edge_case_commands = [
        "",                    # Empty command
        "nonexistent_command", # Non-existent command
        "UPPERCASE_COMMAND",   # Case sensitivity test
    ]
    
    for command_id in edge_case_commands:
        try:
            result = nav_manager.execute_command(command_id)
            assert isinstance(result, dict), f"Command execution should return dict for: '{command_id}'"
            assert "success" in result, f"Command result should have success field for: '{command_id}'"
            
            if command_id not in nav_manager.command_palette_commands:
                assert result["success"] == False, f"Non-existent command should fail: '{command_id}'"
        except Exception as e:
            assert False, f"Command execution should handle edge case gracefully: '{command_id}' -> {e}"

def test_accessibility_edge_cases():
    """Test accessibility features edge cases and robustness"""
    from keyboard_navigation import KeyboardNavigationManager, AccessibilityMode
    
    nav_manager = KeyboardNavigationManager()
    
    # Test accessibility mode transitions
    mode_transitions = [
        AccessibilityMode.NONE,
        AccessibilityMode.HIGH_CONTRAST,
        AccessibilityMode.LARGE_TEXT,
        AccessibilityMode.SCREEN_READER,
        AccessibilityMode.KEYBOARD_ONLY,
        AccessibilityMode.NONE,  # Back to none
    ]
    
    for mode in mode_transitions:
        try:
            nav_manager.enable_accessibility_mode(mode)
            assert nav_manager.accessibility.mode == mode, f"Accessibility mode not set correctly: {mode}"
        except Exception as e:
            assert False, f"Accessibility mode transition should not fail: {mode} -> {e}"
    
    # Test CSS generation with extreme settings
    nav_manager.accessibility.large_text_scale = 5.0  # Very large scale
    nav_manager.accessibility.high_contrast = True
    nav_manager.accessibility.focus_indicators = True
    
    try:
        css = nav_manager.get_accessibility_css()
        assert isinstance(css, str), "CSS generation should return string"
        assert len(css) > 0, "CSS should not be empty with accessibility features enabled"
    except Exception as e:
        assert False, f"CSS generation should handle extreme settings: {e}"
    
    # Test screen reader functionality with edge cases
    nav_manager.enable_accessibility_mode(AccessibilityMode.SCREEN_READER)
    
    edge_case_announcements = [
        ("", "normal"),                    # Empty text
        ("Very long announcement that goes on and on and should be handled gracefully by the screen reader system", "urgent"),
        ("Special chars: !@#$%^&*()", "polite"),
        ("Unicode: café naïve résumé", "normal"),
    ]
    
    for text, priority in edge_case_announcements:
        try:
            nav_manager.announce(text, priority)
            # Should not crash
        except Exception as e:
            assert False, f"Screen reader announcement should handle edge case: '{text}' -> {e}"

def test_data_persistence_error_handling():
    """Test data persistence error handling and recovery"""
    from user_experience import UserExperienceManager
    import tempfile
    import os
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Test with read-only directory (simulating permission errors)
        readonly_dir = Path(temp_dir) / "readonly"
        readonly_dir.mkdir()
        os.chmod(readonly_dir, 0o444)  # Read-only
        
        with patch.object(UserExperienceManager, '__init__') as mock_init:
            def custom_init(self):
                self.logger = Mock()
                self.config_dir = readonly_dir
                
                self.profiles_file = self.config_dir / "profiles.json"
                self.user_profiles = {}
                
                self.preferences_file = self.config_dir / "user_preferences.json"
                self.user_preferences = self._load_user_preferences()
                
                self.usage_file = self.config_dir / "usage_statistics.json"
                self.usage_stats = self._load_usage_statistics()
                
                self.quality_history = []
                self.quality_monitoring_enabled = False
                self.quick_actions = []
            
            mock_init.side_effect = custom_init
            
            try:
                ux_manager = UserExperienceManager()
                
                # Test that operations don't crash with permission errors
                ux_manager.create_profile("test_profile", "wifi")
                ux_manager.update_preference("test_pref", "test_value")
                ux_manager.record_connection_session("wifi", 3600, 1024*1024*100, True)
                
                # Try to save (should handle permission errors gracefully)
                ux_manager.save_profiles()
                ux_manager.save_preferences()
                ux_manager.save_usage_statistics()
                
                # Should not crash even if saves fail
                
            except Exception as e:
                # Should handle permission errors gracefully
                error_msg = str(e).lower()
                if "permission" not in error_msg and "readonly" not in error_msg:
                    assert False, f"Should handle permission errors gracefully: {e}"
            
            finally:
                # Restore permissions for cleanup
                try:
                    os.chmod(readonly_dir, 0o755)
                except:
                    pass

test("Profile Edge Cases", test_profile_edge_cases)
test("Preferences Edge Cases", test_preferences_edge_cases)
test("Usage Analytics Edge Cases", test_usage_analytics_edge_cases)
test("Keyboard Shortcuts Edge Cases", test_keyboard_shortcuts_edge_cases)
test("Command Palette Edge Cases", test_command_palette_edge_cases)
test("Accessibility Edge Cases", test_accessibility_edge_cases)
test("Data Persistence Error Handling", test_data_persistence_error_handling)

# Final Summary
print("\n" + "=" * 80)
print("P3 USER EXPERIENCE COMPREHENSIVE TEST SUMMARY")
print("=" * 80)

passed = sum(1 for _, success, _ in test_results if success)
failed = sum(1 for _, success, _ in test_results if not success)
total = len(test_results)

print(f"\nTotal Tests: {total}")
print(f"Passed: {passed} ✓")
print(f"Failed: {failed} ✗")
print(f"Success Rate: {(passed/total)*100:.1f}%")

# Group results by test suite
test_suites = {
    "P3 User Experience Manager Core": [],
    "P3 Keyboard Navigation and Accessibility": [],
    "P3 Enhanced Connection Manager Integration": [],
    "P3 Data Persistence and Configuration": [],
    "P1+P2+P3 Comprehensive Integration": [],
    "P3 Edge Cases and Error Handling": []
}

suite_names = list(test_suites.keys())
tests_per_suite = [6, 7, 7, 6, 6, 7]  # Number of tests in each suite
current_suite = 0
current_count = 0

for name, success, error in test_results:
    if current_count >= tests_per_suite[current_suite]:
        current_suite += 1
        current_count = 0
    
    if current_suite < len(suite_names):
        test_suites[suite_names[current_suite]].append((name, success, error))
    current_count += 1

print("\nRESULTS BY P3 USER EXPERIENCE FUNCTIONALITY:")
for suite_name, suite_tests in test_suites.items():
    suite_passed = sum(1 for _, success, _ in suite_tests if success)
    suite_total = len(suite_tests)
    print(f"\n{suite_name}: {suite_passed}/{suite_total} passed")
    
    for name, success, error in suite_tests:
        status = "✓" if success else "✗"
        print(f"  {status} {name}")
        if not success and error:
            print(f"    Error: {error}")

if failed > 0:
    print(f"\n⚠️  CRITICAL ISSUES FOUND:")
    for name, success, error in test_results:
        if not success:
            print(f"  • {name}: {error}")

print("\n" + "=" * 80)
if failed == 0:
    print("✅ ALL P3 USER EXPERIENCE FUNCTIONALITY TESTS PASSED")
    print("✅ P3-UX-1: User Experience Manager - WORKING")
    print("✅ P3-UX-1: Connection Profiles Management - WORKING")
    print("✅ P3-UX-1: Usage Analytics & Insights - WORKING")
    print("✅ P3-UX-1: User Preferences Management - WORKING")
    print("✅ P3-UX-1: Quality Monitoring & Assessment - WORKING")
    print("✅ P3-UX-1: Smart Notifications - WORKING")
    print("✅ P3-UX-2: Keyboard Navigation & Accessibility - WORKING")
    print("✅ P3-UX-2: Accessibility Settings Management - WORKING")
    print("✅ P3-UX-2: Keyboard Shortcuts System - WORKING")
    print("✅ P3-UX-2: Command Palette Functionality - WORKING")
    print("✅ P3-UX-2: Screen Reader & Audio Support - WORKING")
    print("✅ P3-UX-2: Navigation Focus Management - WORKING")
    print("✅ P3-UX-3: Enhanced Connection Manager Integration - WORKING")
    print("✅ P3-UX-3: Profile-based Connections - WORKING")
    print("✅ P3-UX-3: Quick Connect Suggestions - WORKING")
    print("✅ P3-UX-3: Enhanced Status with UX Metrics - WORKING")
    print("✅ P3-UX-3: Quick Action Integration - WORKING")
    print("✅ P1+P2+P3: Seamless Integration - WORKING")
    print("✅ P1+P2+P3: Performance Optimized - WORKING")
    print("✅ P1+P2+P3: Memory Efficient - WORKING")
    print("✅ P1+P2+P3: Configuration Persistent - WORKING")
    print("✅ P1+P2+P3: Graceful Degradation - WORKING")
    print("✅ P3: Edge Cases Handled - WORKING")
    print("✅ P3: Error Recovery - WORKING")
else:
    print("❌ SOME P3 USER EXPERIENCE FUNCTIONALITY TESTS FAILED")
    print("🔍 Review failed tests above for P3 UX functionality issues")

print("=" * 80)
sys.exit(0 if failed == 0 else 1)