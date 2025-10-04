#!/usr/bin/env python3
"""
Visual Regression Testing for PdaNet Linux GUI
Professional visual testing with cyberpunk theme validation
"""

import pytest
import os
import sys
import subprocess
import time
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import json
import hashlib
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict
import threading
import signal

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from theme import Colors
from config_manager import get_config
from logger import get_logger

logger = get_logger()

@dataclass
class VisualTestConfig:
    """Visual test configuration"""
    screenshot_dir: str = "tests/visual/screenshots"
    baseline_dir: str = "tests/visual/baseline"
    diff_dir: str = "tests/visual/diff"
    threshold: float = 0.95  # Similarity threshold (0-1)
    window_size: Tuple[int, int] = (1200, 800)
    wait_time: float = 2.0  # Wait time for GUI to stabilize
    max_startup_time: float = 10.0  # Max time to wait for GUI startup

@dataclass
class VisualTestResult:
    """Visual test result data"""
    test_name: str
    baseline_path: str
    screenshot_path: str
    diff_path: str
    similarity: float
    passed: bool
    dimensions: Tuple[int, int]
    timestamp: str
    theme_validation: Dict[str, bool]

class GUIController:
    """Controls GUI application for testing"""

    def __init__(self, config: VisualTestConfig):
        self.config = config
        self.process = None
        self.gui_ready = False

    def start_gui(self) -> bool:
        """Start GUI application"""
        try:
            # Set environment for headless testing
            env = os.environ.copy()
            env['DISPLAY'] = ':99'  # Use virtual display

            # Start GUI in background
            cmd = [sys.executable, 'src/pdanet_gui_v2.py', '--test-mode']
            self.process = subprocess.Popen(
                cmd,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                preexec_fn=os.setsid
            )

            # Wait for GUI to be ready
            start_time = time.time()
            while time.time() - start_time < self.config.max_startup_time:
                if self.process.poll() is not None:
                    stdout, stderr = self.process.communicate()
                    logger.error(f"GUI failed to start: {stderr.decode()}")
                    return False

                # Check if GUI window is ready (simplified check)
                time.sleep(0.5)
                if self._check_gui_ready():
                    self.gui_ready = True
                    break

            return self.gui_ready

        except Exception as e:
            logger.error(f"Failed to start GUI: {e}")
            return False

    def _check_gui_ready(self) -> bool:
        """Check if GUI is ready for testing"""
        try:
            # Simple check - in real implementation this would check window manager
            result = subprocess.run(['pgrep', '-f', 'pdanet_gui_v2'], capture_output=True)
            return result.returncode == 0
        except:
            return False

    def stop_gui(self):
        """Stop GUI application"""
        if self.process:
            try:
                os.killpg(os.getpgid(self.process.pid), signal.SIGTERM)
                self.process.wait(timeout=5)
            except:
                try:
                    os.killpg(os.getpgid(self.process.pid), signal.SIGKILL)
                except:
                    pass
            self.process = None
            self.gui_ready = False

class ScreenshotCapture:
    """Captures screenshots for visual testing"""

    def __init__(self, config: VisualTestConfig):
        self.config = config

    def capture_window(self, window_name: str, output_path: str) -> bool:
        """Capture window screenshot"""
        try:
            # Use scrot or gnome-screenshot for actual capture
            cmd = [
                'gnome-screenshot',
                '--window',
                '--file', output_path
            ]

            result = subprocess.run(cmd, capture_output=True, timeout=10)

            if result.returncode == 0 and os.path.exists(output_path):
                # Resize to standard size
                self._standardize_screenshot(output_path)
                return True
            else:
                logger.error(f"Screenshot failed: {result.stderr.decode()}")
                return False

        except Exception as e:
            logger.error(f"Screenshot capture failed: {e}")
            return False

    def _standardize_screenshot(self, image_path: str):
        """Standardize screenshot to consistent size"""
        try:
            with Image.open(image_path) as img:
                # Resize to standard window size
                resized = img.resize(self.config.window_size, Image.Resampling.LANCZOS)
                resized.save(image_path)
        except Exception as e:
            logger.error(f"Failed to standardize screenshot: {e}")

class ThemeValidator:
    """Validates cyberpunk theme compliance"""

    def __init__(self):
        self.expected_colors = {
            'background': Colors.BG_PRIMARY,  # Pure black
            'success': Colors.SUCCESS,        # Green
            'error': Colors.ERROR,           # Red
            'warning': Colors.WARNING,       # Yellow
        }

    def validate_theme(self, image_path: str) -> Dict[str, bool]:
        """Validate theme colors in screenshot"""
        try:
            with Image.open(image_path) as img:
                # Convert to RGB if needed
                if img.mode != 'RGB':
                    img = img.convert('RGB')

                # Sample key areas for color validation
                width, height = img.size
                samples = [
                    img.getpixel((0, 0)),           # Top-left (likely background)
                    img.getpixel((width//2, 0)),    # Top-center
                    img.getpixel((0, height//2)),   # Left-center
                    img.getpixel((width//2, height//2)),  # Center
                ]

                # Check for expected theme colors
                results = {
                    'has_black_background': self._has_color(samples, (0, 0, 0)),
                    'has_green_elements': self._has_green_elements(img),
                    'has_red_elements': self._has_red_elements(img),
                    'no_unwanted_colors': self._check_no_unwanted_colors(img),
                    'proper_contrast': self._check_contrast(img),
                }

                return results

        except Exception as e:
            logger.error(f"Theme validation failed: {e}")
            return {'error': True}

    def _has_color(self, samples: List[Tuple[int, int, int]], target_color: Tuple[int, int, int], tolerance: int = 10) -> bool:
        """Check if samples contain target color within tolerance"""
        for sample in samples:
            if all(abs(sample[i] - target_color[i]) <= tolerance for i in range(3)):
                return True
        return False

    def _has_green_elements(self, img: Image.Image) -> bool:
        """Check for green UI elements (success states)"""
        # Sample green pixels - look for high green values
        width, height = img.size
        green_count = 0
        sample_size = min(1000, width * height // 100)

        for _ in range(sample_size):
            x = width // 4 + (_ % (width // 2))
            y = height // 4 + (_ // (width // 2)) % (height // 2)
            r, g, b = img.getpixel((x, y))
            if g > 200 and r < 100 and b < 100:  # Bright green
                green_count += 1

        return green_count > 0

    def _has_red_elements(self, img: Image.Image) -> bool:
        """Check for red UI elements (error states)"""
        # Similar to green check but for red
        width, height = img.size
        red_count = 0
        sample_size = min(1000, width * height // 100)

        for _ in range(sample_size):
            x = width // 4 + (_ % (width // 2))
            y = height // 4 + (_ // (width // 2)) % (height // 2)
            r, g, b = img.getpixel((x, y))
            if r > 200 and g < 100 and b < 100:  # Bright red
                red_count += 1

        return red_count > 0

    def _check_no_unwanted_colors(self, img: Image.Image) -> bool:
        """Check that no unwanted colors are present (like pastels)"""
        width, height = img.size
        sample_size = min(1000, width * height // 50)

        for _ in range(sample_size):
            x = _ % width
            y = (_ // width) % height
            r, g, b = img.getpixel((x, y))

            # Check for pastel colors (high saturation, medium brightness)
            if 100 < r < 200 and 100 < g < 200 and 100 < b < 200:
                return False

        return True

    def _check_contrast(self, img: Image.Image) -> bool:
        """Check for proper contrast ratios"""
        # Sample different areas and check contrast
        width, height = img.size
        contrasts = []

        for i in range(0, width, width//10):
            for j in range(0, height, height//10):
                if i < width and j < height:
                    pixel = img.getpixel((i, j))
                    luminance = 0.299 * pixel[0] + 0.587 * pixel[1] + 0.114 * pixel[2]
                    contrasts.append(luminance)

        # Check for sufficient contrast range
        return max(contrasts) - min(contrasts) > 100

class VisualComparator:
    """Compares screenshots for visual regression"""

    def __init__(self, config: VisualTestConfig):
        self.config = config

    def compare_images(self, baseline_path: str, screenshot_path: str, diff_path: str) -> Tuple[float, bool]:
        """Compare two images and return similarity score"""
        try:
            with Image.open(baseline_path) as baseline, Image.open(screenshot_path) as screenshot:
                # Ensure same size
                if baseline.size != screenshot.size:
                    screenshot = screenshot.resize(baseline.size, Image.Resampling.LANCZOS)

                # Calculate pixel-by-pixel difference
                similarity = self._calculate_similarity(baseline, screenshot)

                # Generate diff image
                self._generate_diff_image(baseline, screenshot, diff_path)

                passed = similarity >= self.config.threshold
                return similarity, passed

        except Exception as e:
            logger.error(f"Image comparison failed: {e}")
            return 0.0, False

    def _calculate_similarity(self, img1: Image.Image, img2: Image.Image) -> float:
        """Calculate similarity between two images"""
        # Convert to same mode if needed
        if img1.mode != img2.mode:
            img2 = img2.convert(img1.mode)

        # Calculate histogram difference
        hist1 = img1.histogram()
        hist2 = img2.histogram()

        # Calculate chi-squared distance
        chi_squared = sum((h1 - h2) ** 2 / (h1 + h2 + 1e-10) for h1, h2 in zip(hist1, hist2))

        # Convert to similarity score (0-1)
        similarity = 1.0 / (1.0 + chi_squared / 1000000)

        return similarity

    def _generate_diff_image(self, img1: Image.Image, img2: Image.Image, diff_path: str):
        """Generate difference image highlighting changes"""
        # Create diff image
        diff = Image.new('RGB', img1.size, (0, 0, 0))

        width, height = img1.size
        for y in range(height):
            for x in range(width):
                p1 = img1.getpixel((x, y))
                p2 = img2.getpixel((x, y))

                # Calculate difference
                if isinstance(p1, int):  # Grayscale
                    diff_val = abs(p1 - p2)
                    diff.putpixel((x, y), (diff_val, 0, 0) if diff_val > 10 else (0, 0, 0))
                else:  # RGB
                    diff_r = abs(p1[0] - p2[0])
                    diff_g = abs(p1[1] - p2[1])
                    diff_b = abs(p1[2] - p2[2])
                    total_diff = (diff_r + diff_g + diff_b) // 3

                    if total_diff > 10:
                        diff.putpixel((x, y), (255, 0, 0))  # Red for differences
                    else:
                        diff.putpixel((x, y), (0, 0, 0))    # Black for same

        diff.save(diff_path)

class VisualTestRunner:
    """Main visual test runner"""

    def __init__(self, config: VisualTestConfig = None):
        self.config = config or VisualTestConfig()
        self.gui_controller = GUIController(self.config)
        self.screenshot_capture = ScreenshotCapture(self.config)
        self.theme_validator = ThemeValidator()
        self.comparator = VisualComparator(self.config)
        self.results: List[VisualTestResult] = []

        # Ensure directories exist
        for dir_path in [self.config.screenshot_dir, self.config.baseline_dir, self.config.diff_dir]:
            os.makedirs(dir_path, exist_ok=True)

    def run_visual_tests(self) -> List[VisualTestResult]:
        """Run all visual tests"""
        try:
            # Start GUI
            if not self.gui_controller.start_gui():
                logger.error("Failed to start GUI for testing")
                return []

            time.sleep(self.config.wait_time)

            # Run test scenarios
            test_scenarios = [
                'main_window_default',
                'connection_dialog',
                'settings_panel',
                'status_indicators',
                'error_states',
                'success_states'
            ]

            for scenario in test_scenarios:
                result = self._run_scenario_test(scenario)
                if result:
                    self.results.append(result)

            return self.results

        finally:
            self.gui_controller.stop_gui()

    def _run_scenario_test(self, scenario: str) -> Optional[VisualTestResult]:
        """Run individual test scenario"""
        try:
            timestamp = time.strftime('%Y%m%d_%H%M%S')

            # Paths
            screenshot_path = os.path.join(self.config.screenshot_dir, f"{scenario}_{timestamp}.png")
            baseline_path = os.path.join(self.config.baseline_dir, f"{scenario}.png")
            diff_path = os.path.join(self.config.diff_dir, f"{scenario}_{timestamp}_diff.png")

            # Setup scenario (trigger different GUI states)
            self._setup_scenario(scenario)
            time.sleep(1.0)  # Let GUI stabilize

            # Capture screenshot
            if not self.screenshot_capture.capture_window("PdaNet Linux", screenshot_path):
                logger.error(f"Failed to capture screenshot for {scenario}")
                return None

            # Validate theme
            theme_validation = self.theme_validator.validate_theme(screenshot_path)

            # Compare with baseline if exists
            similarity = 1.0
            passed = True

            if os.path.exists(baseline_path):
                similarity, passed = self.comparator.compare_images(
                    baseline_path, screenshot_path, diff_path
                )
            else:
                # First run - create baseline
                import shutil
                shutil.copy2(screenshot_path, baseline_path)
                logger.info(f"Created baseline for {scenario}")

            # Get image dimensions
            with Image.open(screenshot_path) as img:
                dimensions = img.size

            return VisualTestResult(
                test_name=scenario,
                baseline_path=baseline_path,
                screenshot_path=screenshot_path,
                diff_path=diff_path,
                similarity=similarity,
                passed=passed and all(theme_validation.values()),
                dimensions=dimensions,
                timestamp=timestamp,
                theme_validation=theme_validation
            )

        except Exception as e:
            logger.error(f"Scenario test failed for {scenario}: {e}")
            return None

    def _setup_scenario(self, scenario: str):
        """Setup specific GUI scenario for testing"""
        # In a real implementation, this would use automation tools
        # to interact with the GUI and set up different states

        scenarios = {
            'main_window_default': lambda: None,  # Default state
            'connection_dialog': lambda: self._simulate_connection_dialog(),
            'settings_panel': lambda: self._simulate_settings_panel(),
            'status_indicators': lambda: self._simulate_status_change(),
            'error_states': lambda: self._simulate_error_state(),
            'success_states': lambda: self._simulate_success_state(),
        }

        if scenario in scenarios:
            scenarios[scenario]()

    def _simulate_connection_dialog(self):
        """Simulate opening connection dialog"""
        # In real implementation, would send key combinations or mouse clicks
        pass

    def _simulate_settings_panel(self):
        """Simulate opening settings panel"""
        pass

    def _simulate_status_change(self):
        """Simulate status indicator changes"""
        pass

    def _simulate_error_state(self):
        """Simulate error state in GUI"""
        pass

    def _simulate_success_state(self):
        """Simulate success state in GUI"""
        pass

    def generate_report(self, output_path: str = "tests/visual/visual_test_report.json"):
        """Generate test report"""
        report = {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'config': asdict(self.config),
            'total_tests': len(self.results),
            'passed_tests': sum(1 for r in self.results if r.passed),
            'failed_tests': sum(1 for r in self.results if not r.passed),
            'results': [asdict(result) for result in self.results]
        }

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)

        logger.info(f"Visual test report generated: {output_path}")
        return report

# Pytest integration
@pytest.fixture
def visual_test_runner():
    """Pytest fixture for visual test runner"""
    return VisualTestRunner()

def test_main_window_visual(visual_test_runner):
    """Test main window visual appearance"""
    results = visual_test_runner.run_visual_tests()
    main_window_results = [r for r in results if r.test_name == 'main_window_default']

    assert len(main_window_results) > 0, "Main window test should run"
    assert main_window_results[0].passed, f"Main window visual test failed: {main_window_results[0].similarity}"

def test_theme_compliance(visual_test_runner):
    """Test cyberpunk theme compliance"""
    results = visual_test_runner.run_visual_tests()

    for result in results:
        assert result.theme_validation.get('has_black_background', False), f"Background should be black in {result.test_name}"
        assert result.theme_validation.get('proper_contrast', False), f"Should have proper contrast in {result.test_name}"

if __name__ == "__main__":
    # Run visual tests directly
    runner = VisualTestRunner()
    results = runner.run_visual_tests()
    report = runner.generate_report()

    print(f"Visual tests completed: {report['passed_tests']}/{report['total_tests']} passed")
    for result in results:
        status = "PASS" if result.passed else "FAIL"
        print(f"  {result.test_name}: {status} (similarity: {result.similarity:.3f})")