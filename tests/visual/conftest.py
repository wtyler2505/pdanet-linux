#!/usr/bin/env python3
"""
Pytest configuration for visual testing
Shared fixtures and setup for visual regression tests
"""

import pytest
import os
import sys
import subprocess
import time
import tempfile
import shutil
from pathlib import Path
from typing import Generator, Optional

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from logger import get_logger

logger = get_logger()

@pytest.fixture(scope="session")
def visual_test_environment():
    """Set up visual testing environment"""
    # Check if running in headless environment
    display = os.environ.get('DISPLAY')
    if not display:
        # Set up virtual display for CI/headless testing
        try:
            # Start Xvfb virtual display
            xvfb_process = subprocess.Popen([
                'Xvfb', ':99', '-screen', '0', '1920x1080x24', '-ac'
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            os.environ['DISPLAY'] = ':99'
            time.sleep(2)  # Give Xvfb time to start

            yield {'xvfb_process': xvfb_process, 'display': ':99'}

            # Cleanup
            xvfb_process.terminate()
            xvfb_process.wait()

        except FileNotFoundError:
            pytest.skip("Xvfb not available for headless testing")
    else:
        yield {'xvfb_process': None, 'display': display}

@pytest.fixture(scope="session")
def visual_test_directories():
    """Set up visual test directories"""
    base_dir = Path("tests/visual")
    directories = {
        'screenshots': base_dir / "screenshots",
        'baseline': base_dir / "baseline",
        'diff': base_dir / "diff",
        'responsive': base_dir / "responsive",
        'accessibility': base_dir / "accessibility",
        'reports': base_dir / "reports"
    }

    # Create directories
    for dir_path in directories.values():
        dir_path.mkdir(parents=True, exist_ok=True)

    yield directories

    # Cleanup if in CI environment
    if os.environ.get('CI'):
        # Keep only essential files in CI
        for dir_name, dir_path in directories.items():
            if dir_name in ['screenshots', 'diff']:
                # Clean up temporary test files
                for file in dir_path.glob("*_test_*.png"):
                    file.unlink(missing_ok=True)

@pytest.fixture
def temp_screenshot_dir():
    """Create temporary directory for test screenshots"""
    with tempfile.TemporaryDirectory(prefix="visual_test_") as temp_dir:
        yield Path(temp_dir)

@pytest.fixture(scope="function")
def gui_test_instance():
    """Fixture for GUI testing - ensures single instance"""
    # Check if GUI is already running
    result = subprocess.run(['pgrep', '-f', 'pdanet_gui_v2'], capture_output=True)

    gui_was_running = result.returncode == 0
    gui_process = None

    if not gui_was_running:
        # Start GUI for testing
        try:
            env = os.environ.copy()
            gui_process = subprocess.Popen([
                sys.executable, 'src/pdanet_gui_v2.py', '--test-mode'
            ], env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            # Wait for GUI to start
            time.sleep(3)

            # Verify it started
            result = subprocess.run(['pgrep', '-f', 'pdanet_gui_v2'], capture_output=True)
            if result.returncode != 0:
                pytest.skip("Could not start GUI for testing")

        except Exception as e:
            pytest.skip(f"Failed to start GUI: {e}")

    yield {
        'was_running': gui_was_running,
        'process': gui_process
    }

    # Cleanup
    if gui_process and not gui_was_running:
        try:
            gui_process.terminate()
            gui_process.wait(timeout=5)
        except:
            try:
                gui_process.kill()
            except:
                pass

@pytest.fixture
def screenshot_tools():
    """Fixture providing screenshot capture tools"""
    tools = {}

    # Check available screenshot tools
    for tool in ['gnome-screenshot', 'scrot', 'import']:  # import is from ImageMagick
        try:
            subprocess.run([tool, '--version'], capture_output=True, timeout=5)
            tools[tool] = True
        except (FileNotFoundError, subprocess.TimeoutExpired):
            tools[tool] = False

    if not any(tools.values()):
        pytest.skip("No screenshot tools available")

    yield tools

@pytest.fixture
def test_images():
    """Fixture providing test images for comparison"""
    test_dir = Path("tests/visual/test_images")
    test_dir.mkdir(exist_ok=True)

    # Create simple test images if they don't exist
    test_images = {}

    try:
        from PIL import Image, ImageDraw

        # Create test pattern images
        patterns = {
            'solid_black': (100, 100, (0, 0, 0)),
            'solid_white': (100, 100, (255, 255, 255)),
            'checkerboard': None,  # Will create programmatically
            'gradient': None,
        }

        for name, config in patterns.items():
            image_path = test_dir / f"{name}.png"

            if not image_path.exists():
                if config:
                    width, height, color = config
                    img = Image.new('RGB', (width, height), color)
                else:
                    # Create special patterns
                    if name == 'checkerboard':
                        img = Image.new('RGB', (100, 100), (255, 255, 255))
                        draw = ImageDraw.Draw(img)
                        for x in range(0, 100, 10):
                            for y in range(0, 100, 10):
                                if (x // 10 + y // 10) % 2:
                                    draw.rectangle([x, y, x+10, y+10], fill=(0, 0, 0))
                    elif name == 'gradient':
                        img = Image.new('RGB', (100, 100))
                        for x in range(100):
                            for y in range(100):
                                img.putpixel((x, y), (x * 255 // 100, y * 255 // 100, 128))

                img.save(image_path)

            test_images[name] = str(image_path)

    except ImportError:
        pytest.skip("PIL not available for test image creation")

    yield test_images

@pytest.fixture
def mock_gui_states():
    """Mock different GUI states for testing"""
    states = {
        'disconnected': {
            'connection_status': 'disconnected',
            'stealth_enabled': False,
            'last_error': None
        },
        'connected': {
            'connection_status': 'connected',
            'stealth_enabled': True,
            'last_error': None
        },
        'error': {
            'connection_status': 'error',
            'stealth_enabled': False,
            'last_error': 'Connection failed'
        },
        'connecting': {
            'connection_status': 'connecting',
            'stealth_enabled': False,
            'last_error': None
        }
    }

    yield states

@pytest.fixture(autouse=True)
def cleanup_test_files():
    """Automatically cleanup test files after each test"""
    yield

    # Clean up any test files created during the test
    test_patterns = [
        "tests/visual/**/*_test_*.png",
        "tests/visual/**/*_temp_*.png",
        "/tmp/pdanet_visual_test_*"
    ]

    import glob
    for pattern in test_patterns:
        for file_path in glob.glob(pattern, recursive=True):
            try:
                os.unlink(file_path)
            except:
                pass

# Pytest marks for categorizing tests
def pytest_configure(config):
    """Configure pytest with custom marks"""
    config.addinivalue_line(
        "markers", "visual: mark test as visual regression test"
    )
    config.addinivalue_line(
        "markers", "responsive: mark test as responsive design test"
    )
    config.addinivalue_line(
        "markers", "accessibility: mark test as accessibility test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
    config.addinivalue_line(
        "markers", "gui: mark test as requiring GUI"
    )

def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers"""
    for item in items:
        # Mark GUI tests
        if "gui" in item.nodeid or "visual" in item.nodeid:
            item.add_marker(pytest.mark.gui)

        # Mark slow tests
        if "accessibility" in item.nodeid or "responsive" in item.nodeid:
            item.add_marker(pytest.mark.slow)

# Helper functions for tests
def ensure_gui_ready(timeout: int = 10) -> bool:
    """Ensure GUI is ready for testing"""
    start_time = time.time()

    while time.time() - start_time < timeout:
        result = subprocess.run(['pgrep', '-f', 'pdanet_gui_v2'], capture_output=True)
        if result.returncode == 0:
            time.sleep(1)  # Additional settling time
            return True
        time.sleep(0.5)

    return False

def capture_test_screenshot(output_path: str, window_title: str = None) -> bool:
    """Capture screenshot for testing"""
    try:
        if window_title:
            cmd = ['gnome-screenshot', '--window', '--file', output_path]
        else:
            cmd = ['gnome-screenshot', '--file', output_path]

        result = subprocess.run(cmd, capture_output=True, timeout=10)
        return result.returncode == 0 and os.path.exists(output_path)

    except (FileNotFoundError, subprocess.TimeoutExpired):
        # Fallback to scrot
        try:
            cmd = ['scrot', output_path]
            result = subprocess.run(cmd, capture_output=True, timeout=10)
            return result.returncode == 0 and os.path.exists(output_path)
        except:
            return False