#!/usr/bin/env python3
"""
Accessibility Visual Testing for PdaNet Linux GUI
Tests accessibility compliance including color contrast, readability, and WCAG guidelines
"""

import pytest
import os
import sys
import subprocess
import time
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter
import numpy as np
from typing import Dict, List, Tuple, Optional, Union
from dataclasses import dataclass, asdict
import colorsys
import math

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from theme import Colors
from test_visual_regression import VisualTestRunner, VisualTestConfig
from logger import get_logger

logger = get_logger()

@dataclass
class AccessibilityConfig:
    """Accessibility test configuration"""
    min_contrast_ratio: float = 4.5  # WCAG AA standard
    min_large_text_contrast: float = 3.0  # WCAG AA for large text
    min_touch_target_size: int = 44  # pixels (iOS/Android guidelines)
    max_color_difference_threshold: float = 0.1  # For color blindness testing
    test_color_blindness: bool = True
    test_low_vision: bool = True
    test_high_contrast: bool = True

@dataclass
class AccessibilityTestResult:
    """Accessibility test result"""
    test_name: str
    passed: bool
    contrast_ratio: float
    color_blind_safe: bool
    low_vision_compliant: bool
    touch_targets_adequate: bool
    issues: List[str]
    recommendations: List[str]
    wcag_level: str  # A, AA, or AAA

class ColorAnalyzer:
    """Analyzes colors for accessibility compliance"""

    @staticmethod
    def rgb_to_luminance(rgb: Tuple[int, int, int]) -> float:
        """Calculate relative luminance of RGB color"""
        def channel_luminance(channel: int) -> float:
            c = channel / 255.0
            if c <= 0.03928:
                return c / 12.92
            else:
                return pow((c + 0.055) / 1.055, 2.4)

        r, g, b = rgb
        return 0.2126 * channel_luminance(r) + 0.7152 * channel_luminance(g) + 0.0722 * channel_luminance(b)

    @staticmethod
    def contrast_ratio(color1: Tuple[int, int, int], color2: Tuple[int, int, int]) -> float:
        """Calculate contrast ratio between two colors"""
        lum1 = ColorAnalyzer.rgb_to_luminance(color1)
        lum2 = ColorAnalyzer.rgb_to_luminance(color2)

        # Ensure lighter color is in numerator
        if lum1 > lum2:
            return (lum1 + 0.05) / (lum2 + 0.05)
        else:
            return (lum2 + 0.05) / (lum1 + 0.05)

    @staticmethod
    def simulate_color_blindness(rgb: Tuple[int, int, int], blindness_type: str) -> Tuple[int, int, int]:
        """Simulate color blindness on RGB color"""
        r, g, b = [c / 255.0 for c in rgb]

        # Transformation matrices for different types of color blindness
        if blindness_type == 'protanopia':  # Red-blind
            matrix = [
                [0.567, 0.433, 0],
                [0.558, 0.442, 0],
                [0, 0.242, 0.758]
            ]
        elif blindness_type == 'deuteranopia':  # Green-blind
            matrix = [
                [0.625, 0.375, 0],
                [0.7, 0.3, 0],
                [0, 0.3, 0.7]
            ]
        elif blindness_type == 'tritanopia':  # Blue-blind
            matrix = [
                [0.95, 0.05, 0],
                [0, 0.433, 0.567],
                [0, 0.475, 0.525]
            ]
        else:
            return rgb

        # Apply transformation
        new_r = matrix[0][0] * r + matrix[0][1] * g + matrix[0][2] * b
        new_g = matrix[1][0] * r + matrix[1][1] * g + matrix[1][2] * b
        new_b = matrix[2][0] * r + matrix[2][1] * g + matrix[2][2] * b

        # Clamp and convert back to 0-255 range
        return (
            max(0, min(255, int(new_r * 255))),
            max(0, min(255, int(new_g * 255))),
            max(0, min(255, int(new_b * 255)))
        )

    @staticmethod
    def is_color_distinguishable(color1: Tuple[int, int, int], color2: Tuple[int, int, int],
                               threshold: float = 0.1) -> bool:
        """Check if two colors are distinguishable for color blind users"""
        blindness_types = ['protanopia', 'deuteranopia', 'tritanopia']

        for blindness_type in blindness_types:
            cb_color1 = ColorAnalyzer.simulate_color_blindness(color1, blindness_type)
            cb_color2 = ColorAnalyzer.simulate_color_blindness(color2, blindness_type)

            # Calculate color difference in HSV space
            hsv1 = colorsys.rgb_to_hsv(cb_color1[0]/255, cb_color1[1]/255, cb_color1[2]/255)
            hsv2 = colorsys.rgb_to_hsv(cb_color2[0]/255, cb_color2[1]/255, cb_color2[2]/255)

            # Calculate difference
            h_diff = min(abs(hsv1[0] - hsv2[0]), 1 - abs(hsv1[0] - hsv2[0]))
            s_diff = abs(hsv1[1] - hsv2[1])
            v_diff = abs(hsv1[2] - hsv2[2])

            total_diff = math.sqrt(h_diff**2 + s_diff**2 + v_diff**2)

            if total_diff < threshold:
                return False

        return True

class TouchTargetAnalyzer:
    """Analyzes touch target sizes for accessibility"""

    def __init__(self, min_size: int = 44):
        self.min_size = min_size

    def find_interactive_elements(self, img: Image.Image) -> List[Tuple[int, int, int, int]]:
        """Find potential interactive elements (buttons, links) in image"""
        # This is a simplified version - real implementation would use ML or template matching
        interactive_areas = []

        width, height = img.size

        # Look for rectangular areas with consistent colors (potential buttons)
        # Sample the image in a grid and look for grouped similar colors
        grid_size = 20
        sample_points = []

        for x in range(0, width, width // grid_size):
            for y in range(0, height, height // grid_size):
                if x < width and y < height:
                    color = img.getpixel((x, y))
                    sample_points.append((x, y, color))

        # Group similar colors that might represent buttons
        color_groups = self._group_similar_colors(sample_points)

        # Convert color groups to bounding rectangles
        for group in color_groups:
            if len(group) >= 4:  # Minimum size for a button
                x_coords = [point[0] for point in group]
                y_coords = [point[1] for point in group]

                min_x, max_x = min(x_coords), max(x_coords)
                min_y, max_y = min(y_coords), max(y_coords)

                # Only consider reasonably sized rectangles
                if (max_x - min_x) > 20 and (max_y - min_y) > 20:
                    interactive_areas.append((min_x, min_y, max_x, max_y))

        return interactive_areas

    def _group_similar_colors(self, sample_points: List[Tuple[int, int, Tuple]],
                            color_threshold: int = 30) -> List[List[Tuple]]:
        """Group sample points with similar colors"""
        groups = []

        for point in sample_points:
            x, y, color = point
            placed = False

            # Try to add to existing group
            for group in groups:
                if len(group) > 0:
                    group_color = group[0][2]  # Color of first point in group
                    if self._colors_similar(color, group_color, color_threshold):
                        group.append(point)
                        placed = True
                        break

            # Create new group if not placed
            if not placed:
                groups.append([point])

        return groups

    def _colors_similar(self, color1: Union[int, Tuple], color2: Union[int, Tuple],
                       threshold: int = 30) -> bool:
        """Check if two colors are similar"""
        # Handle grayscale
        if isinstance(color1, int):
            color1 = (color1, color1, color1)
        if isinstance(color2, int):
            color2 = (color2, color2, color2)

        # Calculate Euclidean distance in RGB space
        distance = math.sqrt(sum((a - b) ** 2 for a, b in zip(color1[:3], color2[:3])))
        return distance < threshold

    def analyze_touch_targets(self, img: Image.Image) -> Dict[str, Union[bool, List[str], int]]:
        """Analyze touch target adequacy"""
        interactive_areas = self.find_interactive_elements(img)

        adequate_targets = 0
        inadequate_targets = 0
        issues = []

        for area in interactive_areas:
            min_x, min_y, max_x, max_y = area
            width = max_x - min_x
            height = max_y - min_y

            # Check if target meets minimum size requirements
            if width >= self.min_size and height >= self.min_size:
                adequate_targets += 1
            else:
                inadequate_targets += 1
                issues.append(f"Touch target at ({min_x}, {min_y}) is {width}x{height}px (minimum: {self.min_size}x{self.min_size}px)")

        return {
            'adequate_targets': adequate_targets,
            'inadequate_targets': inadequate_targets,
            'all_targets_adequate': inadequate_targets == 0,
            'issues': issues,
            'total_targets': len(interactive_areas)
        }

class AccessibilityTestRunner:
    """Main accessibility test runner"""

    def __init__(self, config: AccessibilityConfig = None):
        self.config = config or AccessibilityConfig()
        self.color_analyzer = ColorAnalyzer()
        self.touch_analyzer = TouchTargetAnalyzer(self.config.min_touch_target_size)
        self.results: List[AccessibilityTestResult] = []

    def run_accessibility_tests(self, screenshot_paths: List[str]) -> List[AccessibilityTestResult]:
        """Run accessibility tests on screenshots"""
        self.results = []

        for screenshot_path in screenshot_paths:
            if os.path.exists(screenshot_path):
                result = self._test_screenshot_accessibility(screenshot_path)
                if result:
                    self.results.append(result)

        return self.results

    def _test_screenshot_accessibility(self, screenshot_path: str) -> Optional[AccessibilityTestResult]:
        """Test accessibility of a single screenshot"""
        try:
            test_name = os.path.basename(screenshot_path).replace('.png', '')
            issues = []
            recommendations = []

            with Image.open(screenshot_path) as img:
                # Test 1: Color contrast
                contrast_result = self._test_color_contrast(img)
                contrast_ratio = contrast_result['min_contrast_ratio']
                contrast_passed = contrast_ratio >= self.config.min_contrast_ratio

                if not contrast_passed:
                    issues.extend(contrast_result['issues'])
                    recommendations.extend(contrast_result['recommendations'])

                # Test 2: Color blindness safety
                colorblind_result = self._test_color_blindness_safety(img)
                colorblind_passed = colorblind_result['safe']

                if not colorblind_passed:
                    issues.extend(colorblind_result['issues'])
                    recommendations.extend(colorblind_result['recommendations'])

                # Test 3: Low vision compliance
                low_vision_result = self._test_low_vision_compliance(img)
                low_vision_passed = low_vision_result['compliant']

                if not low_vision_passed:
                    issues.extend(low_vision_result['issues'])
                    recommendations.extend(low_vision_result['recommendations'])

                # Test 4: Touch targets
                touch_result = self.touch_analyzer.analyze_touch_targets(img)
                touch_passed = touch_result['all_targets_adequate']

                if not touch_passed:
                    issues.extend(touch_result['issues'])
                    recommendations.append("Increase size of small touch targets to at least 44x44px")

                # Determine WCAG compliance level
                wcag_level = self._determine_wcag_level(contrast_ratio, contrast_passed,
                                                      colorblind_passed, low_vision_passed, touch_passed)

                # Overall pass/fail
                overall_passed = contrast_passed and colorblind_passed and low_vision_passed and touch_passed

                return AccessibilityTestResult(
                    test_name=test_name,
                    passed=overall_passed,
                    contrast_ratio=contrast_ratio,
                    color_blind_safe=colorblind_passed,
                    low_vision_compliant=low_vision_passed,
                    touch_targets_adequate=touch_passed,
                    issues=issues,
                    recommendations=recommendations,
                    wcag_level=wcag_level
                )

        except Exception as e:
            logger.error(f"Accessibility test failed for {screenshot_path}: {e}")
            return None

    def _test_color_contrast(self, img: Image.Image) -> Dict:
        """Test color contrast ratios"""
        # Sample the image to find text/background combinations
        width, height = img.size
        contrasts = []
        issues = []
        recommendations = []

        # Sample grid points to find potential text areas
        grid_size = 20
        for x in range(0, width, width // grid_size):
            for y in range(0, height, height // grid_size):
                if x < width - 10 and y < height - 10:
                    # Sample a small area to find foreground/background pairs
                    area_colors = []
                    for dx in range(10):
                        for dy in range(10):
                            if x + dx < width and y + dy < height:
                                color = img.getpixel((x + dx, y + dy))
                                if isinstance(color, int):
                                    color = (color, color, color)
                                area_colors.append(color[:3])

                    # Find min/max colors in area (likely text and background)
                    if area_colors:
                        min_luminance_color = min(area_colors, key=self.color_analyzer.rgb_to_luminance)
                        max_luminance_color = max(area_colors, key=self.color_analyzer.rgb_to_luminance)

                        if min_luminance_color != max_luminance_color:
                            ratio = self.color_analyzer.contrast_ratio(min_luminance_color, max_luminance_color)
                            contrasts.append(ratio)

        min_contrast = min(contrasts) if contrasts else 1.0
        avg_contrast = sum(contrasts) / len(contrasts) if contrasts else 1.0

        if min_contrast < self.config.min_contrast_ratio:
            issues.append(f"Insufficient color contrast: {min_contrast:.2f} (minimum: {self.config.min_contrast_ratio})")
            recommendations.append("Increase contrast between text and background colors")

        return {
            'min_contrast_ratio': min_contrast,
            'avg_contrast_ratio': avg_contrast,
            'all_contrasts': contrasts,
            'issues': issues,
            'recommendations': recommendations
        }

    def _test_color_blindness_safety(self, img: Image.Image) -> Dict:
        """Test color blindness safety"""
        issues = []
        recommendations = []

        if not self.config.test_color_blindness:
            return {'safe': True, 'issues': [], 'recommendations': []}

        # Sample colors from the image
        width, height = img.size
        sample_colors = set()

        # Get a representative sample of colors
        for x in range(0, width, width // 20):
            for y in range(0, height, height // 20):
                if x < width and y < height:
                    color = img.getpixel((x, y))
                    if isinstance(color, int):
                        color = (color, color, color)
                    sample_colors.add(color[:3])

        # Test color pairs for distinguishability
        colors_list = list(sample_colors)
        problematic_pairs = []

        for i, color1 in enumerate(colors_list):
            for color2 in colors_list[i+1:]:
                if not self.color_analyzer.is_color_distinguishable(
                    color1, color2, self.config.max_color_difference_threshold):
                    problematic_pairs.append((color1, color2))

        safe = len(problematic_pairs) == 0

        if not safe:
            issues.append(f"Found {len(problematic_pairs)} color pairs that may be indistinguishable to color blind users")
            recommendations.append("Use patterns, textures, or additional visual cues beyond color alone")
            recommendations.append("Test interface with color blindness simulators")

        return {
            'safe': safe,
            'problematic_pairs': problematic_pairs,
            'issues': issues,
            'recommendations': recommendations
        }

    def _test_low_vision_compliance(self, img: Image.Image) -> Dict:
        """Test compliance for low vision users"""
        issues = []
        recommendations = []

        if not self.config.test_low_vision:
            return {'compliant': True, 'issues': [], 'recommendations': []}

        # Test 1: High contrast mode simulation
        high_contrast_img = self._simulate_high_contrast(img)
        hc_readable = self._is_content_readable(high_contrast_img)

        # Test 2: Magnification simulation
        magnified_img = img.resize((img.width * 2, img.height * 2), Image.Resampling.NEAREST)
        mag_readable = self._is_content_readable(magnified_img)

        # Test 3: Blur simulation (simulate vision impairment)
        blurred_img = img.filter(ImageFilter.GaussianBlur(radius=2))
        blur_readable = self._is_content_readable(blurred_img)

        compliant = hc_readable and mag_readable and blur_readable

        if not hc_readable:
            issues.append("Interface may not be readable in high contrast mode")
            recommendations.append("Ensure sufficient contrast in high contrast themes")

        if not mag_readable:
            issues.append("Interface may not scale well when magnified")
            recommendations.append("Use scalable fonts and layout designs")

        if not blur_readable:
            issues.append("Interface may not be readable with visual impairments")
            recommendations.append("Increase font sizes and improve contrast")

        return {
            'compliant': compliant,
            'high_contrast_readable': hc_readable,
            'magnification_readable': mag_readable,
            'blur_readable': blur_readable,
            'issues': issues,
            'recommendations': recommendations
        }

    def _simulate_high_contrast(self, img: Image.Image) -> Image.Image:
        """Simulate high contrast mode"""
        # Convert to grayscale and enhance contrast
        gray = img.convert('L')
        enhancer = ImageEnhance.Contrast(gray)
        high_contrast = enhancer.enhance(3.0)  # Increase contrast significantly

        # Convert back to RGB
        return high_contrast.convert('RGB')

    def _is_content_readable(self, img: Image.Image) -> bool:
        """Check if content is readable (simplified heuristic)"""
        # Convert to grayscale for analysis
        gray = img.convert('L')
        width, height = gray.size

        # Sample the image and check for text-like patterns
        text_indicators = 0
        sample_size = min(100, width * height // 1000)

        for i in range(sample_size):
            x = (i * 73) % width  # Pseudo-random sampling
            y = (i * 97) % height

            if x < width - 5 and y < height - 5:
                # Sample 5x5 area and check local contrast
                area_pixels = []
                for dx in range(5):
                    for dy in range(5):
                        area_pixels.append(gray.getpixel((x + dx, y + dy)))

                local_contrast = max(area_pixels) - min(area_pixels)
                if local_contrast > 50:  # Significant local contrast suggests text
                    text_indicators += 1

        # If sufficient text-like areas found, consider readable
        return text_indicators > sample_size * 0.05

    def _determine_wcag_level(self, contrast_ratio: float, contrast_passed: bool,
                            colorblind_passed: bool, low_vision_passed: bool,
                            touch_passed: bool) -> str:
        """Determine WCAG compliance level"""
        if contrast_ratio >= 7.0 and contrast_passed and colorblind_passed and low_vision_passed and touch_passed:
            return "AAA"
        elif contrast_ratio >= 4.5 and contrast_passed and colorblind_passed:
            return "AA"
        elif contrast_ratio >= 3.0:
            return "A"
        else:
            return "Non-compliant"

    def generate_accessibility_report(self, output_path: str = "tests/visual/accessibility_report.json") -> Dict:
        """Generate accessibility test report"""
        summary = {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'total_tests': len(self.results),
            'passed_tests': sum(1 for r in self.results if r.passed),
            'failed_tests': sum(1 for r in self.results if not r.passed),
            'wcag_levels': {},
            'common_issues': {},
            'recommendations': []
        }

        # Analyze WCAG levels
        for result in self.results:
            level = result.wcag_level
            if level not in summary['wcag_levels']:
                summary['wcag_levels'][level] = 0
            summary['wcag_levels'][level] += 1

        # Collect common issues
        all_issues = []
        all_recommendations = []

        for result in self.results:
            all_issues.extend(result.issues)
            all_recommendations.extend(result.recommendations)

        # Count issue frequency
        for issue in all_issues:
            if issue not in summary['common_issues']:
                summary['common_issues'][issue] = 0
            summary['common_issues'][issue] += 1

        # Get unique recommendations
        summary['recommendations'] = list(set(all_recommendations))

        # Full report
        report = {
            'summary': summary,
            'config': asdict(self.config),
            'detailed_results': [asdict(result) for result in self.results]
        }

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)

        logger.info(f"Accessibility report generated: {output_path}")
        return report

# Pytest integration
@pytest.fixture
def accessibility_test_runner():
    """Pytest fixture for accessibility test runner"""
    return AccessibilityTestRunner()

def test_color_contrast_compliance(accessibility_test_runner):
    """Test color contrast compliance"""
    # This would run on actual screenshots
    sample_screenshots = ["tests/visual/screenshots/main_window_default.png"]
    results = accessibility_test_runner.run_accessibility_tests(sample_screenshots)

    for result in results:
        assert result.contrast_ratio >= 4.5, f"Insufficient contrast in {result.test_name}: {result.contrast_ratio}"

def test_color_blindness_safety(accessibility_test_runner):
    """Test color blindness safety"""
    sample_screenshots = ["tests/visual/screenshots/main_window_default.png"]
    results = accessibility_test_runner.run_accessibility_tests(sample_screenshots)

    for result in results:
        assert result.color_blind_safe, f"Not color blind safe: {result.test_name}"

def test_wcag_aa_compliance(accessibility_test_runner):
    """Test WCAG AA compliance"""
    sample_screenshots = ["tests/visual/screenshots/main_window_default.png"]
    results = accessibility_test_runner.run_accessibility_tests(sample_screenshots)

    for result in results:
        assert result.wcag_level in ["AA", "AAA"], f"Does not meet WCAG AA: {result.test_name} ({result.wcag_level})"

if __name__ == "__main__":
    # Run accessibility tests directly
    runner = AccessibilityTestRunner()

    # Test with sample screenshots (would be actual screenshots in real use)
    sample_screenshots = [
        "tests/visual/screenshots/main_window_default.png",
        "tests/visual/screenshots/connection_dialog.png"
    ]

    results = runner.run_accessibility_tests(sample_screenshots)
    report = runner.generate_accessibility_report()

    print(f"Accessibility tests completed: {report['summary']['passed_tests']}/{report['summary']['total_tests']} passed")
    print(f"WCAG levels: {report['summary']['wcag_levels']}")

    if report['summary']['common_issues']:
        print("\nCommon issues:")
        for issue, count in sorted(report['summary']['common_issues'].items(), key=lambda x: x[1], reverse=True):
            print(f"  {issue} ({count} occurrences)")

    if report['summary']['recommendations']:
        print(f"\nRecommendations:")
        for rec in report['summary']['recommendations'][:5]:
            print(f"  - {rec}")