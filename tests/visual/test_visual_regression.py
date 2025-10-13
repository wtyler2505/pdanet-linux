#!/usr/bin/env python3
"""
Visual Regression Testing for PdaNet Linux GUI
Professional visual testing with cyberpunk theme validation
"""

import json
import os
import signal
import subprocess
import sys
import time
from dataclasses import asdict, dataclass

import pytest
from PIL import Image

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from logger import get_logger
from theme import Colors

logger = get_logger()


@dataclass
class VisualTestConfig:
    """Visual test configuration"""

    screenshot_dir: str = "tests/visual/screenshots"
    baseline_dir: str = "tests/visual/baseline"
    diff_dir: str = "tests/visual/diff"
    threshold: float = 0.95  # Similarity threshold (0-1)
    window_size: tuple[int, int] = (1200, 800)
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
    dimensions: tuple[int, int]
    timestamp: str
    theme_validation: dict[str, bool]
    perceptual_hash: str | None = None
    hash_distance: int | None = None
    ssim: float | None = None


class GUIController:
    """Controls GUI application for testing"""

    def __init__(self, config: VisualTestConfig):
        self.config = config
        self.process = None
        self.gui_ready = False

    def start_gui(self) -> bool:
        """Start GUI application"""
        try:
            # Use existing DISPLAY (pytest-xvfb sets this). Do not override.
            env = os.environ.copy()

            # Start GUI in background
            cmd = [sys.executable, "src/pdanet_gui_v2.py", "--test-mode"]
            self.process = subprocess.Popen(
                cmd, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, preexec_fn=os.setsid
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
            result = subprocess.run(
                ["pgrep", "-f", "pdanet_gui_v2"], check=False, capture_output=True
            )
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
            # Try gnome-screenshot first (focused window)
            cmd = ["gnome-screenshot", "--window", "--file", output_path]
            try:
                result = subprocess.run(cmd, check=False, capture_output=True, timeout=8)
                if result.returncode == 0 and os.path.exists(output_path):
                    self._standardize_screenshot(output_path)
                    return True
            except subprocess.TimeoutExpired:
                logger.error("gnome-screenshot timed out; falling back to import/xwininfo")

            # Fallback 1: ImageMagick import targeting the window by name
            if self._capture_with_import(window_name, output_path):
                self._standardize_screenshot(output_path)
                return True

            # Fallback 2: Capture the root window as last resort
            if self._capture_root_with_import(output_path):
                self._standardize_screenshot(output_path)
                return True

            logger.error("All screenshot methods failed")
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

    def _capture_with_import(self, window_name: str, output_path: str) -> bool:
        """Use ImageMagick `import` to capture a specific window by name.
        If direct window capture fails, capture root and crop to window geometry.
        """
        try:
            candidates = [w for w in [window_name, "PdaNet Linux", "PDANET LINUX"] if w]
            for name in candidates:
                try:
                    # Find window id via xwininfo
                    proc = subprocess.run(
                        ["xwininfo", "-name", name],
                        check=False,
                        capture_output=True,
                        text=True,
                        timeout=5,
                    )
                    if proc.returncode != 0:
                        continue
                    wid = None
                    geom = {}
                    for line in proc.stdout.splitlines():
                        if "Window id:" in line:
                            # e.g., "xwininfo: Window id: 0x4a00007 \"PDANET LINUX\""
                            parts = line.split()
                            for p in parts:
                                if p.startswith("0x"):
                                    wid = p
                                    break
                            break
                    # Parse geometry
                    for line in proc.stdout.splitlines():
                        if "Absolute upper-left X" in line:
                            geom["x"] = int(line.split(":")[-1].strip())
                        elif "Absolute upper-left Y" in line:
                            geom["y"] = int(line.split(":")[-1].strip())
                        elif "Width:" in line:
                            geom["w"] = int(line.split(":")[-1].strip())
                        elif "Height:" in line:
                            geom["h"] = int(line.split(":")[-1].strip())

                    if wid:
                        # Attempt direct window capture
                        cap = subprocess.run(
                            ["import", "-window", wid, output_path],
                            check=False,
                            capture_output=True,
                            timeout=8,
                        )
                        if cap.returncode == 0 and os.path.exists(output_path):
                            return True

                    # Fallback: capture root and crop
                    tmp_path = f"{output_path}.root.png"
                    cap2 = subprocess.run(
                        ["import", "-window", "root", tmp_path],
                        check=False,
                        capture_output=True,
                        timeout=8,
                    )
                    if (
                        cap2.returncode == 0
                        and os.path.exists(tmp_path)
                        and all(k in geom for k in ("x", "y", "w", "h"))
                    ):
                        from PIL import Image

                        with Image.open(tmp_path) as img:
                            x, y, w, h = geom["x"], geom["y"], geom["w"], geom["h"]
                            # Ensure bounds
                            w = max(1, min(w, img.width - x))
                            h = max(1, min(h, img.height - y))
                            cropped = img.crop((x, y, x + w, y + h))
                            cropped.save(output_path)
                        os.remove(tmp_path)
                        if os.path.exists(output_path):
                            return True
                except subprocess.TimeoutExpired:
                    continue
        except Exception as e:
            logger.error(f"import/xwininfo capture failed: {e}")
        return False

    def _capture_root_with_import(self, output_path: str) -> bool:
        """Capture the root window using ImageMagick as a last resort."""
        try:
            cap = subprocess.run(
                ["import", "-window", "root", output_path],
                check=False,
                capture_output=True,
                timeout=8,
            )
            return cap.returncode == 0 and os.path.exists(output_path)
        except Exception:
            return False


class ThemeValidator:
    """Validates cyberpunk theme compliance"""

    def __init__(self):
        self.expected_colors = {
            "background": Colors.BG_PRIMARY,  # Pure black
            "success": Colors.SUCCESS,  # Green
            "error": Colors.ERROR,  # Red
            "warning": Colors.WARNING,  # Yellow
        }

    def validate_theme(self, image_path: str) -> dict[str, bool]:
        """Validate theme colors in screenshot (robust against window borders)."""
        try:
            with Image.open(image_path) as img:
                # Convert to RGB if needed
                if img.mode != "RGB":
                    img = img.convert("RGB")

                width, height = img.size

                # Robust background check: sample grid across image and look for near-black prevalence
                black_count = 0
                total_samples = 0
                step_x = max(1, width // 30)
                step_y = max(1, height // 20)
                for x in range(0, width, step_x):
                    for y in range(0, height, step_y):
                        r, g, b = img.getpixel((x, y))
                        total_samples += 1
                        if r <= 30 and g <= 30 and b <= 30:
                            black_count += 1
                has_black_background = (
                    black_count / max(1, total_samples)
                ) >= 0.20  # >=20% near-black

                results = {
                    "has_black_background": has_black_background,
                    "has_green_elements": self._has_green_elements(img),
                    "has_red_elements": self._has_red_elements(img),
                    "no_unwanted_colors": self._check_no_unwanted_colors(img),
                    "proper_contrast": self._check_contrast(img),
                }

                return results

        except Exception as e:
            logger.error(f"Theme validation failed: {e}")
            return {"error": True}

    def _has_color(
        self,
        samples: list[tuple[int, int, int]],
        target_color: tuple[int, int, int],
        tolerance: int = 20,
    ) -> bool:
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

        for i in range(0, width, width // 10):
            for j in range(0, height, height // 10):
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

    def compare_images(
        self, baseline_path: str, screenshot_path: str, diff_path: str
    ) -> tuple[float, bool]:
        """Compare two images and return similarity score"""
        try:
            with Image.open(baseline_path) as baseline, Image.open(screenshot_path) as screenshot:
                # Ensure same size
                if baseline.size != screenshot.size:
                    screenshot = screenshot.resize(baseline.size, Image.Resampling.LANCZOS)

                # Prefer numpy-based metric when available
                try:
                    import numpy as np

                    a = np.asarray(baseline.convert("RGB"), dtype=np.int16)
                    b = np.asarray(screenshot.convert("RGB"), dtype=np.int16)
                    mad = float(np.mean(np.abs(a - b)))  # 0..255
                    similarity = max(0.0, 1.0 - (mad / 255.0))
                except Exception:
                    # Fallback to histogram-based similarity
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
        chi_squared = sum(
            (h1 - h2) ** 2 / (h1 + h2 + 1e-10) for h1, h2 in zip(hist1, hist2, strict=False)
        )

        # Convert to similarity score (0-1)
        similarity = 1.0 / (1.0 + chi_squared / 1000000)

        return similarity

    def _generate_diff_image(self, img1: Image.Image, img2: Image.Image, diff_path: str):
        """Generate difference image using ImageChops for performance."""
        try:
            from PIL import ImageChops

            diff = ImageChops.difference(img1.convert("RGB"), img2.convert("RGB"))
            # Emphasize differences in red channel
            r, g, b = diff.split()
            red = r.point(lambda p: 255 if p > 10 else 0)
            out = Image.merge(
                "RGB", (red, Image.new("L", red.size, 0), Image.new("L", red.size, 0))
            )
            out.save(diff_path)
        except Exception:
            diff = Image.new("RGB", img1.size, (0, 0, 0))
            diff.save(diff_path)


class VisualTestRunner:
    """Main visual test runner"""

    def __init__(self, config: VisualTestConfig = None):
        self.config = config or VisualTestConfig()
        self.gui_controller = GUIController(self.config)
        self.screenshot_capture = ScreenshotCapture(self.config)
        self.theme_validator = ThemeValidator()
        self.comparator = VisualComparator(self.config)
        self.results: list[VisualTestResult] = []

        # Ensure directories exist
        for dir_path in [
            self.config.screenshot_dir,
            self.config.baseline_dir,
            self.config.diff_dir,
        ]:
            os.makedirs(dir_path, exist_ok=True)

    def run_visual_tests(self) -> list[VisualTestResult]:
        """Run all visual tests"""
        try:
            # Start GUI
            if not self.gui_controller.start_gui():
                logger.error("Failed to start GUI for testing")
                return []

            time.sleep(self.config.wait_time)

            # Run test scenarios
            test_scenarios = [
                "main_window_default",
                "connection_dialog",
                "settings_panel",
                "status_indicators",
                "error_states",
                "success_states",
            ]

            for scenario in test_scenarios:
                result = self._run_scenario_test(scenario)
                if result:
                    self.results.append(result)

            return self.results

        finally:
            self.gui_controller.stop_gui()

    def _run_scenario_test(self, scenario: str) -> VisualTestResult | None:
        """Run individual test scenario"""
        try:
            timestamp = time.strftime("%Y%m%d_%H%M%S")

            # Paths
            screenshot_path = os.path.join(
                self.config.screenshot_dir, f"{scenario}_{timestamp}.png"
            )
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

            # Optional perceptual hash & SSIM
            perceptual_hash = None
            hash_distance = None
            ssim_val = None
            try:
                import imagehash  # type: ignore

                with Image.open(baseline_path) as bimg, Image.open(screenshot_path) as simg:
                    h1 = imagehash.phash(bimg.convert("RGB"))
                    h2 = imagehash.phash(simg.convert("RGB"))
                    perceptual_hash = str(h2)
                    hash_distance = int(h1 - h2)
            except Exception:
                pass
            try:
                import numpy as np
                from skimage.metrics import (
                    structural_similarity as ssim,  # type: ignore
                )

                with Image.open(baseline_path) as bimg, Image.open(screenshot_path) as simg:
                    a = np.asarray(bimg.convert("L"))
                    b = np.asarray(simg.convert("L"))
                    if a.shape == b.shape:
                        ssim_val = float(ssim(a, b, data_range=255))
            except Exception:
                pass

            # Compare with baseline if exists
            similarity = 1.0
            passed = True

            if os.path.exists(baseline_path):
                similarity, passed = self.comparator.compare_images(
                    baseline_path, screenshot_path, diff_path
                )
                # If only baseline drifted but critical theme checks pass, refresh baseline only when allowed
                try:
                    import os
                    import shutil

                    critical_ok = (
                        bool(theme_validation.get("has_black_background"))
                        and bool(theme_validation.get("proper_contrast"))
                        and bool(theme_validation.get("no_unwanted_colors", True))
                    )
                    if not passed and critical_ok and os.getenv("PDANET_UPDATE_BASELINES") == "1":
                        shutil.copy2(screenshot_path, baseline_path)
                        logger.info(
                            f"Updated baseline for {scenario} (theme valid, similarity {similarity:.3f})"
                        )
                        similarity, passed = 1.0, True
                except Exception as _e:
                    logger.error(f"Failed to update baseline for {scenario}: {_e}")
            else:
                # First run - create baseline
                import shutil

                shutil.copy2(screenshot_path, baseline_path)
                logger.info(f"Created baseline for {scenario}")

            # Get image dimensions
            with Image.open(screenshot_path) as img:
                dimensions = img.size

            # Determine pass/fail based on similarity and critical theme checks
            critical_ok = (
                bool(theme_validation.get("has_black_background"))
                and bool(theme_validation.get("proper_contrast"))
                and bool(theme_validation.get("no_unwanted_colors", True))
            )

            return VisualTestResult(
                test_name=scenario,
                baseline_path=baseline_path,
                screenshot_path=screenshot_path,
                diff_path=diff_path,
                similarity=similarity,
                passed=passed and critical_ok,
                dimensions=dimensions,
                timestamp=timestamp,
                theme_validation=theme_validation,
                perceptual_hash=perceptual_hash,
                hash_distance=hash_distance,
                ssim=ssim_val,
            )

        except Exception as e:
            logger.error(f"Scenario test failed for {scenario}: {e}")
            return None

    def _setup_scenario(self, scenario: str):
        """Setup specific GUI scenario for testing"""
        # In a real implementation, this would use automation tools
        # to interact with the GUI and set up different states

        scenarios = {
            "main_window_default": lambda: None,  # Default state
            "connection_dialog": lambda: self._simulate_connection_dialog(),
            "settings_panel": lambda: self._simulate_settings_panel(),
            "status_indicators": lambda: self._simulate_status_change(),
            "error_states": lambda: self._simulate_error_state(),
            "success_states": lambda: self._simulate_success_state(),
        }

        if scenario in scenarios:
            scenarios[scenario]()

    def _simulate_connection_dialog(self):
        """Simulate opening connection dialog"""
        # In real implementation, would send key combinations or mouse clicks

    def _simulate_settings_panel(self):
        """Simulate opening settings panel"""

    def _simulate_status_change(self):
        """Simulate status indicator changes"""

    def _simulate_error_state(self):
        """Simulate error state in GUI"""

    def _simulate_success_state(self):
        """Simulate success state in GUI"""

    def generate_report(self, output_path: str = "tests/visual/visual_test_report.json"):
        """Generate test report"""
        report = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "config": asdict(self.config),
            "total_tests": len(self.results),
            "passed_tests": sum(1 for r in self.results if r.passed),
            "failed_tests": sum(1 for r in self.results if not r.passed),
            "results": [asdict(result) for result in self.results],
        }

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w") as f:
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
    main_window_results = [r for r in results if r.test_name == "main_window_default"]

    assert len(main_window_results) > 0, "Main window test should run"
    assert main_window_results[
        0
    ].passed, f"Main window visual test failed: {main_window_results[0].similarity}"


def test_theme_compliance(visual_test_runner):
    """Test cyberpunk theme compliance"""
    results = visual_test_runner.run_visual_tests()

    for result in results:
        assert result.theme_validation.get(
            "has_black_background", False
        ), f"Background should be black in {result.test_name}"
        assert result.theme_validation.get(
            "proper_contrast", False
        ), f"Should have proper contrast in {result.test_name}"


if __name__ == "__main__":
    # Run visual tests directly
    runner = VisualTestRunner()
    results = runner.run_visual_tests()
    report = runner.generate_report()

    print(f"Visual tests completed: {report['passed_tests']}/{report['total_tests']} passed")
    for result in results:
        status = "PASS" if result.passed else "FAIL"
        print(f"  {result.test_name}: {status} (similarity: {result.similarity:.3f})")
