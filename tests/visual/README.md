# Visual Testing Suite for PdaNet Linux

Comprehensive visual regression testing system for the PdaNet Linux GTK GUI application.

## Overview

This testing suite provides automated visual validation for the PdaNet Linux cyberpunk-themed GUI, ensuring consistent visual appearance across different configurations and preventing visual regressions.

## Test Categories

### 1. Visual Regression Tests (`test_visual_regression.py`)
- **Purpose**: Detect unintended visual changes between versions
- **Coverage**: Main window, dialogs, panels, and key UI states
- **Method**: Pixel-perfect screenshot comparison with baseline images
- **Threshold**: 95% similarity required for pass

### 2. Responsive Design Tests (`test_responsive.py`)
- **Purpose**: Validate UI behavior across different screen sizes
- **Coverage**: Multiple breakpoints from 800x600 to 2560x1440
- **Method**: Layout analysis and element positioning validation
- **Focus**: Mobile usability, touch targets, content overflow

### 3. Accessibility Tests (`test_accessibility.py`)
- **Purpose**: Ensure WCAG AA compliance and inclusive design
- **Coverage**: Color contrast, color blindness safety, low vision support
- **Method**: Automated accessibility analysis and visual simulation
- **Standards**: WCAG 2.1 AA guidelines

### 4. Component Tests (`test_components.py`)
- **Purpose**: Validate individual UI components in isolation
- **Coverage**: Connection panel, status indicators, stealth controls, statistics
- **Method**: State-based testing with theme compliance validation
- **Focus**: Cyberpunk theme adherence, component-specific functionality

## Directory Structure

```
tests/visual/
├── test_visual_regression.py    # Main visual regression tests
├── test_responsive.py           # Responsive design validation
├── test_accessibility.py        # Accessibility compliance tests
├── test_components.py           # Component-level testing
├── conftest.py                  # Pytest configuration and fixtures
├── visual_test_runner.py        # Main test orchestrator
├── README.md                    # This file
│
├── baseline/                    # Reference screenshots
│   ├── main_window_default.png
│   ├── connection_dialog.png
│   └── ...
│
├── screenshots/                 # Current test screenshots
├── diff/                       # Visual difference images
├── responsive/                 # Responsive test outputs
├── components/                 # Component test screenshots
└── reports/                    # Test reports and summaries
```

## Quick Start

### Prerequisites

```bash
# Install system dependencies (Ubuntu/Debian)
sudo apt-get install xvfb gnome-screenshot imagemagick x11-utils python3-gi gir1.2-gtk-3.0

# Install Python dependencies
pip install -r requirements.txt
pip install pytest pillow numpy
```

### Running Tests

#### All Tests
```bash
cd tests/visual
python visual_test_runner.py --all
```

#### Specific Test Suites
```bash
# Visual regression only
python visual_test_runner.py --regression

# Responsive design only
python visual_test_runner.py --responsive

# Accessibility only
python visual_test_runner.py --accessibility

# Component tests only
python visual_test_runner.py --components
```

#### Using Pytest
```bash
# Run all visual tests
pytest tests/visual/ -v

# Run specific test categories
pytest tests/visual/test_visual_regression.py -v
pytest tests/visual/test_responsive.py -v -m responsive
pytest tests/visual/test_accessibility.py -v -m accessibility
pytest tests/visual/test_components.py -v -m visual
```

### Creating/Updating Baselines

```bash
# Create initial baselines (first run)
PDANET_UPDATE_BASELINES=1 python visual_test_runner.py --all --create-baselines

# Update baselines after approved changes
PDANET_UPDATE_BASELINES=1 python visual_test_runner.py --all --update-baselines
```

## Configuration

### Test Configuration

Each test suite has its own configuration class:

```python
# Visual regression config
VisualTestConfig(
    threshold=0.95,           # Similarity threshold (0-1)
    window_size=(1200, 800),  # Standard window size
    wait_time=2.0             # GUI stabilization time
)

# Responsive config
ResponsiveTestConfig(
    breakpoints=[             # Test breakpoints
        (800, 600),
        (1024, 768),
        (1920, 1080)
    ]
)

# Accessibility config
AccessibilityConfig(
    min_contrast_ratio=4.5,   # WCAG AA standard
    min_touch_target_size=44, # iOS/Android guidelines
    test_color_blindness=True
)
```

### Environment Variables

```bash
export DISPLAY=:99                    # Virtual display for headless testing
export VISUAL_TEST_MODE=ci           # CI optimization mode
export PDANET_TEST_TIMEOUT=30       # Test timeout in seconds
```

## Cyberpunk Theme Validation

The test suite enforces PdaNet Linux's cyberpunk aesthetic:

### Color Requirements
- **Background**: Pure black (#000000)
- **Success/Active**: Green (#00FF00)
- **Error/Inactive**: Red (#FF0000)
- **Warning**: Yellow (#FFFF00)
- **NO pastels or gradients**

### Font Requirements
- **Primary**: Monospaced fonts (JetBrains Mono, Fira Code)
- **NO emoji or decorative unicode**
- **Professional terminal aesthetic**

### Validation Checks
- ✅ Black background verification
- ✅ Cyberpunk color palette compliance
- ✅ Contrast ratio validation (4.5:1 minimum)
- ✅ No unwanted colors detection
- ✅ Monospace font usage

## CI/CD Integration

### GitHub Actions Workflow

The included workflow (`.github/workflows/visual-tests.yml`) provides:

- **Multi-environment testing**: Python 3.9-3.11, multiple resolutions
- **Automated baseline management**: Updates baselines on main branch
- **PR integration**: Comments with test results
- **Artifact management**: Screenshots, diffs, and reports
- **Scheduled testing**: Daily runs to catch environmental changes

### Workflow Triggers
- Push to main/develop branches
- Pull requests with UI changes
- Daily scheduled runs (2 AM UTC)
- Manual dispatch with configuration options

## Test Reports

### Generated Reports

1. **comprehensive_visual_test_report.json**: Complete test results
2. **visual_test_report.html**: Human-readable HTML report
3. **regression_report.json**: Detailed regression test results
4. **responsive_report.json**: Responsive design analysis
5. **accessibility_report.json**: WCAG compliance report
6. **component_report.json**: Component-level test results

### Report Structure

```json
{
  "timestamp": "2025-01-01 12:00:00",
  "execution_time": 45.2,
  "summary": {
    "total_tests": 24,
    "total_passed": 22,
    "overall_pass_rate": 91.7
  },
  "recommendations": [
    "Address accessibility issues",
    "Update baselines for changed components"
  ]
}
```

## Troubleshooting

### Common Issues

#### 1. GUI Won't Start in Headless Environment
```bash
# Ensure Xvfb is running
Xvfb :99 -screen 0 1920x1080x24 -ac &
export DISPLAY=:99

# Verify display
xdpyinfo
```

#### 2. Screenshot Capture Fails
```bash
# Install screenshot tools
sudo apt-get install gnome-screenshot scrot imagemagick

# Test screenshot capability
gnome-screenshot --file=test.png
```

#### 3. Permission Errors
```bash
# Ensure proper permissions
chmod +x tests/visual/visual_test_runner.py
sudo chmod +r /tmp/pdanet-linux-gui.lock
```

#### 4. High False Positive Rate
```python
# Adjust sensitivity in config
VisualTestConfig(threshold=0.90)  # Lower threshold = more tolerant
```

### Debug Mode

```bash
# Enable debug logging
PDANET_LOG_LEVEL=DEBUG python visual_test_runner.py --all

# Keep temporary files
PDANET_KEEP_TEMP=1 python visual_test_runner.py --regression
```

## Best Practices

### Development Workflow

1. **Before UI Changes**: Run baseline tests to ensure starting point
2. **During Development**: Use component tests for rapid feedback
3. **Before Commit**: Run full visual test suite
4. **After Merge**: Update baselines if changes are approved

### Baseline Management

- **Create baselines**: Only on stable, approved UI states
- **Update baselines**: When visual changes are intentional and approved
- **Review diffs**: Always examine difference images before updating
- **Version control**: Keep baselines in git for change tracking

### Performance Optimization

- **Parallel execution**: Use `--parallel` flag for faster runs
- **Selective testing**: Run only relevant test suites during development
- **CI optimization**: Use caching and artifacts effectively
- **Resolution targeting**: Test only relevant resolutions for your use case

## Contributing

### Adding New Tests

1. **Component Tests**: Add new component validation in `test_components.py`
2. **Regression Tests**: Add new scenarios in `test_visual_regression.py`
3. **Responsive Tests**: Add new breakpoints in `test_responsive.py`
4. **Accessibility Tests**: Add new WCAG checks in `test_accessibility.py`

### Test Development Guidelines

- **Descriptive names**: Use clear, specific test function names
- **Proper isolation**: Ensure tests don't interfere with each other
- **Error handling**: Handle GUI startup failures gracefully
- **Documentation**: Document test purpose and expected behavior
- **Theme compliance**: Validate cyberpunk theme requirements

### Pull Request Requirements

- [ ] All visual tests pass
- [ ] New features include visual tests
- [ ] Baselines updated for intentional changes
- [ ] CI workflow validates changes
- [ ] Documentation updated

## Advanced Usage

### Custom Test Scenarios

```python
# Create custom test scenario
def test_custom_scenario():
    runner = VisualTestRunner()
    runner._setup_scenario('custom_state')
    result = runner._run_scenario_test('custom_scenario')
    assert result.passed
```

### Integration with Other Tools

```bash
# Combine with performance testing
python visual_test_runner.py --all && pytest tests/performance/

# Generate accessibility report
python -m accessibility_test --generate-report

# Export baselines for manual review
python visual_test_runner.py --export-baselines ./review/
```

### Monitoring and Alerting

```yaml
# Monitor test trends
name: Visual Test Monitoring
on:
  schedule:
    - cron: '0 */6 * * *'  # Every 6 hours

jobs:
  monitor:
    runs-on: ubuntu-latest
    steps:
      - name: Run visual tests
        run: python visual_test_runner.py --all
      - name: Alert on failures
        if: failure()
        run: |
          # Send alert to team (Slack, email, etc.)
          echo "Visual tests failing - investigate immediately"
```

## Support

For issues, questions, or contributions:

1. **Check logs**: Review test output and error messages
2. **Verify environment**: Ensure all dependencies are installed
3. **Test isolation**: Run individual test suites to isolate issues
4. **Check baselines**: Verify baseline images are valid
5. **GitHub Issues**: Report bugs with reproduction steps

---

**PdaNet Linux Visual Testing Suite** - Ensuring consistent cyberpunk aesthetics and professional UI quality.
