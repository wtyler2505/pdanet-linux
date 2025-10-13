#!/usr/bin/env python3
"""
Demonstration of pytest-regressions image_regression for main window.
"""

import os

import pytest
from PIL import Image

from .test_visual_regression import VisualTestRunner


@pytest.mark.visual
def test_main_window_image_regression(image_regression):
    runner = VisualTestRunner()
    results = runner.run_visual_tests()
    # Find main_window_default result
    result = next((r for r in results if r.test_name == "main_window_default"), None)
    assert result is not None, "main_window_default scenario should run"
    assert os.path.exists(result.screenshot_path), "Screenshot should exist"
    with Image.open(result.screenshot_path) as img:
        image_regression.check(img)
