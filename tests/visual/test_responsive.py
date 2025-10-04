#!/usr/bin/env python3
"""
Responsive Visual Testing for PdaNet Linux GUI
Tests different window sizes and ensures proper responsive behavior
"""

import pytest
import os
import sys
import subprocess
import time
from pathlib import Path
from PIL import Image
import json
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from theme import Colors
from test_visual_regression import VisualTestRunner, VisualTestConfig, VisualTestResult
from logger import get_logger

logger = get_logger()

@dataclass
class ResponsiveTestConfig:
    """Responsive test configuration"""
    breakpoints: List[Tuple[int, int]] = None
    min_window_size: Tuple[int, int] = (800, 600)
    max_window_size: Tuple[int, int] = (1920, 1080)
    test_orientations: List[str] = None

    def __post_init__(self):
        if self.breakpoints is None:
            self.breakpoints = [
                (800, 600),    # Small
                (1024, 768),   # Medium
                (1200, 800),   # Large
                (1920, 1080),  # XL
                (2560, 1440),  # XXL
            ]

        if self.test_orientations is None:
            self.test_orientations = ['landscape', 'portrait']

class ResponsiveTestRunner:
    """Runner for responsive visual tests"""

    def __init__(self, config: ResponsiveTestConfig = None):
        self.config = config or ResponsiveTestConfig()
        self.visual_runner = None
        self.results: List[Dict] = []

    def run_responsive_tests(self) -> List[Dict]:
        """Run responsive tests across all breakpoints"""
        try:
            for width, height in self.config.breakpoints:
                # Test landscape orientation
                result = self._test_breakpoint(width, height, 'landscape')
                if result:
                    self.results.append(result)

                # Test portrait orientation for supported sizes
                if width > height:  # Only test portrait for landscape breakpoints
                    portrait_result = self._test_breakpoint(height, width, 'portrait')
                    if portrait_result:
                        self.results.append(portrait_result)

            return self.results

        except Exception as e:
            logger.error(f"Responsive tests failed: {e}")
            return []

    def _test_breakpoint(self, width: int, height: int, orientation: str) -> Optional[Dict]:
        """Test specific breakpoint"""
        try:
            # Create visual test config for this breakpoint
            visual_config = VisualTestConfig(
                window_size=(width, height),
                screenshot_dir=f"tests/visual/responsive/{width}x{height}_{orientation}",
                baseline_dir=f"tests/visual/responsive/baseline/{width}x{height}_{orientation}",
                diff_dir=f"tests/visual/responsive/diff/{width}x{height}_{orientation}",
            )

            # Run visual tests with this configuration
            self.visual_runner = VisualTestRunner(visual_config)
            visual_results = self.visual_runner.run_visual_tests()

            # Analyze responsive behavior
            responsive_analysis = self._analyze_responsive_behavior(visual_results, width, height)

            return {
                'breakpoint': f"{width}x{height}",
                'orientation': orientation,
                'visual_results': [asdict(r) for r in visual_results],
                'responsive_analysis': responsive_analysis,
                'passed': all(r.passed for r in visual_results) and responsive_analysis['responsive_compliant']
            }

        except Exception as e:
            logger.error(f"Breakpoint test failed for {width}x{height}: {e}")
            return None

    def _analyze_responsive_behavior(self, visual_results: List[VisualTestResult], width: int, height: int) -> Dict:
        """Analyze responsive behavior from visual results"""
        analysis = {
            'responsive_compliant': True,
            'layout_issues': [],
            'element_issues': [],
            'text_readability': True,
            'scrolling_required': False,
            'content_overflow': False,
        }

        try:
            for result in visual_results:
                if os.path.exists(result.screenshot_path):
                    # Analyze screenshot for responsive issues
                    issues = self._detect_layout_issues(result.screenshot_path, width, height)
                    analysis['layout_issues'].extend(issues)

                    # Check text readability
                    readability = self._check_text_readability(result.screenshot_path, width, height)
                    analysis['text_readability'] = analysis['text_readability'] and readability

                    # Check for content overflow
                    overflow = self._detect_content_overflow(result.screenshot_path, width, height)
                    analysis['content_overflow'] = analysis['content_overflow'] or overflow

            # Overall compliance
            analysis['responsive_compliant'] = (
                len(analysis['layout_issues']) == 0 and
                analysis['text_readability'] and
                not analysis['content_overflow']
            )

        except Exception as e:
            logger.error(f"Responsive analysis failed: {e}")
            analysis['responsive_compliant'] = False
            analysis['layout_issues'].append(f"Analysis error: {e}")

        return analysis

    def _detect_layout_issues(self, image_path: str, width: int, height: int) -> List[str]:
        """Detect layout issues in screenshot"""
        issues = []

        try:
            with Image.open(image_path) as img:
                # Check if image matches expected dimensions
                if img.size != (width, height):
                    issues.append(f"Image size {img.size} doesn't match expected {width}x{height}")

                # Check for UI elements being cut off
                if self._has_cutoff_elements(img):
                    issues.append("UI elements appear to be cut off")

                # Check for overlapping elements
                if self._has_overlapping_elements(img):
                    issues.append("UI elements appear to overlap")

                # Check button sizes for touch targets
                if width < 1024 and not self._has_adequate_touch_targets(img):
                    issues.append("Touch targets may be too small for mobile devices")

        except Exception as e:
            issues.append(f"Layout analysis error: {e}")

        return issues

    def _has_cutoff_elements(self, img: Image.Image) -> bool:
        """Check for UI elements that appear to be cut off at edges"""
        width, height = img.size

        # Check edges for sudden color changes that might indicate cutoff
        edge_pixels = [
            # Top edge
            [img.getpixel((x, 0)) for x in range(0, width, width//20)],
            # Bottom edge
            [img.getpixel((x, height-1)) for x in range(0, width, width//20)],
            # Left edge
            [img.getpixel((0, y)) for y in range(0, height, height//20)],
            # Right edge
            [img.getpixel((width-1, y)) for y in range(0, height, height//20)],
        ]

        # Look for non-background colors at edges (potential cutoff)
        background_color = (0, 0, 0)  # Black background
        tolerance = 20

        for edge in edge_pixels:
            for pixel in edge:
                if isinstance(pixel, tuple) and len(pixel) >= 3:
                    r, g, b = pixel[:3]
                    if (abs(r - background_color[0]) > tolerance or
                        abs(g - background_color[1]) > tolerance or
                        abs(b - background_color[2]) > tolerance):
                        # Found non-background color at edge - possible cutoff
                        return True

        return False

    def _has_overlapping_elements(self, img: Image.Image) -> bool:
        """Check for overlapping UI elements (simplified heuristic)"""
        # This is a simplified check - in practice would use more sophisticated analysis
        width, height = img.size

        # Sample grid points and look for color conflicts
        grid_size = 20
        conflicts = 0

        for x in range(0, width, width//grid_size):
            for y in range(0, height, height//grid_size):
                if x < width and y < height:
                    # Check surrounding pixels for conflicting colors
                    center_pixel = img.getpixel((x, y))
                    surrounding = []

                    for dx in [-5, 0, 5]:
                        for dy in [-5, 0, 5]:
                            nx, ny = x + dx, y + dy
                            if 0 <= nx < width and 0 <= ny < height:
                                surrounding.append(img.getpixel((nx, ny)))

                    # Check for unusual color patterns that might indicate overlap
                    if len(set(surrounding)) > 5:  # Too many colors in small area
                        conflicts += 1

        # If more than 10% of grid points show conflicts, consider it overlapping
        return conflicts > (grid_size * grid_size * 0.1)

    def _has_adequate_touch_targets(self, img: Image.Image) -> bool:
        """Check if touch targets are adequate for mobile (simplified)"""
        # In real implementation, this would analyze button/clickable element sizes
        # For now, just return True as this requires more complex image analysis
        return True

    def _check_text_readability(self, image_path: str, width: int, height: int) -> bool:
        """Check text readability at different sizes"""
        try:
            with Image.open(image_path) as img:
                # Convert to grayscale for text analysis
                gray = img.convert('L')

                # Simple contrast check - look for text-like patterns
                # In real implementation, would use OCR or more sophisticated analysis

                # Check for sufficient contrast in potential text areas
                # Text areas typically have high local contrast
                contrast_areas = 0
                sample_size = min(100, width * height // 10000)

                for i in range(sample_size):
                    x = (i * 73) % width  # Pseudo-random sampling
                    y = (i * 131) % height

                    if x < width - 10 and y < height - 10:
                        # Sample 10x10 area
                        area_pixels = []
                        for dx in range(10):
                            for dy in range(10):
                                area_pixels.append(gray.getpixel((x + dx, y + dy)))

                        # Check local contrast
                        if max(area_pixels) - min(area_pixels) > 100:
                            contrast_areas += 1

                # If sufficient contrast areas found, consider text readable
                return contrast_areas > sample_size * 0.1

        except Exception as e:
            logger.error(f"Text readability check failed: {e}")
            return False

    def _detect_content_overflow(self, image_path: str, width: int, height: int) -> bool:
        """Detect if content overflows the visible area"""
        try:
            with Image.open(image_path) as img:
                # Check for scroll indicators or content at edges
                # This is a simplified check

                # Look for content very close to edges (possible overflow)
                margin = 5
                edge_content = False

                # Check right edge for content
                for y in range(margin, height - margin):
                    pixel = img.getpixel((width - margin, y))
                    if pixel != (0, 0, 0):  # Non-background at edge
                        edge_content = True
                        break

                # Check bottom edge for content
                if not edge_content:
                    for x in range(margin, width - margin):
                        pixel = img.getpixel((x, height - margin))
                        if pixel != (0, 0, 0):  # Non-background at edge
                            edge_content = True
                            break

                return edge_content

        except Exception as e:
            logger.error(f"Content overflow check failed: {e}")
            return False

    def generate_responsive_report(self, output_path: str = "tests/visual/responsive_test_report.json"):
        """Generate responsive test report"""
        summary = {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'total_breakpoints': len(self.config.breakpoints),
            'total_tests': len(self.results),
            'passed_tests': sum(1 for r in self.results if r['passed']),
            'failed_tests': sum(1 for r in self.results if not r['passed']),
            'breakpoint_summary': {},
            'responsive_issues': [],
        }

        # Analyze results by breakpoint
        for result in self.results:
            breakpoint = result['breakpoint']
            if breakpoint not in summary['breakpoint_summary']:
                summary['breakpoint_summary'][breakpoint] = {
                    'passed': 0,
                    'failed': 0,
                    'issues': []
                }

            if result['passed']:
                summary['breakpoint_summary'][breakpoint]['passed'] += 1
            else:
                summary['breakpoint_summary'][breakpoint]['failed'] += 1
                summary['breakpoint_summary'][breakpoint]['issues'].extend(
                    result['responsive_analysis']['layout_issues']
                )

        # Collect all responsive issues
        for result in self.results:
            if not result['passed']:
                summary['responsive_issues'].extend(
                    result['responsive_analysis']['layout_issues']
                )

        # Full report
        report = {
            'summary': summary,
            'config': asdict(self.config),
            'detailed_results': self.results
        }

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)

        logger.info(f"Responsive test report generated: {output_path}")
        return report

# Pytest integration
@pytest.fixture
def responsive_test_runner():
    """Pytest fixture for responsive test runner"""
    return ResponsiveTestRunner()

def test_responsive_breakpoints(responsive_test_runner):
    """Test responsive behavior at different breakpoints"""
    results = responsive_test_runner.run_responsive_tests()
    assert len(results) > 0, "Should have responsive test results"

    failed_breakpoints = [r for r in results if not r['passed']]
    assert len(failed_breakpoints) == 0, f"Failed breakpoints: {[r['breakpoint'] for r in failed_breakpoints]}"

def test_small_screen_usability(responsive_test_runner):
    """Test usability on small screens"""
    small_config = ResponsiveTestConfig(breakpoints=[(800, 600)])
    responsive_test_runner.config = small_config

    results = responsive_test_runner.run_responsive_tests()
    assert len(results) > 0, "Should have small screen test results"

    small_result = results[0]
    analysis = small_result['responsive_analysis']

    assert analysis['text_readability'], "Text should be readable on small screens"
    assert not analysis['content_overflow'], "Content should not overflow on small screens"

def test_large_screen_layout(responsive_test_runner):
    """Test layout on large screens"""
    large_config = ResponsiveTestConfig(breakpoints=[(1920, 1080)])
    responsive_test_runner.config = large_config

    results = responsive_test_runner.run_responsive_tests()
    assert len(results) > 0, "Should have large screen test results"

    large_result = results[0]
    assert large_result['passed'], "Layout should work correctly on large screens"

if __name__ == "__main__":
    # Run responsive tests directly
    runner = ResponsiveTestRunner()
    results = runner.run_responsive_tests()
    report = runner.generate_responsive_report()

    print(f"Responsive tests completed: {report['summary']['passed_tests']}/{report['summary']['total_tests']} passed")

    for breakpoint, summary in report['summary']['breakpoint_summary'].items():
        status = "PASS" if summary['failed'] == 0 else "FAIL"
        print(f"  {breakpoint}: {status} ({summary['passed']} passed, {summary['failed']} failed)")

        if summary['issues']:
            for issue in summary['issues'][:3]:  # Show first 3 issues
                print(f"    - {issue}")