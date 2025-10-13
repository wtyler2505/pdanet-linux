#!/usr/bin/env python3
"""
Unit tests for Theme
Tests cyberpunk color system and GTK CSS generation
"""

import os
import sys
import unittest

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from theme import Colors, Format, get_css


class TestColors(unittest.TestCase):
    """Test suite for color constants"""

    def test_base_colors(self):
        """Test base color definitions"""
        self.assertEqual(Colors.BLACK, "#000000")
        self.assertEqual(Colors.DARK_GRAY, "#1A1A1A")
        self.assertEqual(Colors.TEXT_WHITE, "#E0E0E0")

    def test_accent_colors(self):
        """Test accent color definitions"""
        self.assertEqual(Colors.GREEN, "#00FF00")
        self.assertEqual(Colors.RED, "#FF0000")
        self.assertEqual(Colors.YELLOW, "#FFB84D")

    def test_status_colors(self):
        """Test status color mappings"""
        self.assertEqual(Colors.STATUS_ACTIVE, Colors.GREEN)
        self.assertEqual(Colors.STATUS_INACTIVE, Colors.RED)
        self.assertEqual(Colors.STATUS_WARNING, Colors.ORANGE)


class TestFormat(unittest.TestCase):
    """Test suite for text formatting utilities"""

    def test_format_uppercase(self):
        """Test uppercase formatting utility"""
        result = Format.uppercase("test")
        self.assertEqual(result, "TEST")

    def test_format_monospace(self):
        """Test monospace font wrapping"""
        result = Format.monospace("test")
        self.assertIn("test", result)

    def test_format_bold(self):
        """Test bold text formatting"""
        result = Format.bold("test")
        self.assertIn("test", result)

    def test_format_color(self):
        """Test color span formatting"""
        result = Format.color("test", Colors.GREEN)
        self.assertIn(Colors.GREEN, result)
        self.assertIn("test", result)


class TestCSS(unittest.TestCase):
    """Test suite for GTK CSS generation"""

    def test_css_generation(self):
        """Test CSS string is generated"""
        css = get_css()
        self.assertIsInstance(css, str)
        self.assertGreater(len(css), 0)

    def test_css_no_unsupported_properties(self):
        """Test CSS doesn't contain unsupported GTK3 properties"""
        css = get_css()

        # GTK3 doesn't support these properties - they cause runtime errors
        self.assertNotIn("text-transform", css.lower())
        self.assertNotIn("letter-spacing", css.lower())

    def test_css_contains_monospace_fonts(self):
        """Test CSS specifies monospace fonts"""
        css = get_css()
        self.assertIn("monospace", css.lower())

    def test_css_contains_black_background(self):
        """Test CSS uses pure black background"""
        css = get_css()
        self.assertIn("#000000", css)

    def test_css_contains_cyberpunk_colors(self):
        """Test CSS includes cyberpunk color scheme"""
        css = get_css()

        # Should contain green, red, and other accent colors
        self.assertIn("#00FF00", css)  # Green
        self.assertIn("#FF0000", css)  # Red

    def test_no_gradients(self):
        """Test CSS doesn't use gradients (professional style only)"""
        css = get_css()
        self.assertNotIn("gradient", css.lower())

    def test_no_emoji_in_css(self):
        """Test CSS doesn't contain emoji (professional constraint)"""
        css = get_css()

        # Check for common emoji unicode ranges
        emoji_ranges = [
            (0x1F600, 0x1F64F),  # Emoticons
            (0x1F300, 0x1F5FF),  # Misc Symbols and Pictographs
            (0x1F680, 0x1F6FF),  # Transport and Map
        ]

        for char in css:
            code = ord(char)
            for start, end in emoji_ranges:
                self.assertFalse(start <= code <= end, f"Found emoji character in CSS: {char}")


if __name__ == "__main__":
    unittest.main()
