#!/usr/bin/env python3
"""
Visual Test Runner - Orchestrates all visual testing
Main entry point for running comprehensive visual tests
"""

import os
import sys
import time
import json
import argparse
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from test_visual_regression import VisualTestRunner, VisualTestConfig
from test_responsive import ResponsiveTestRunner, ResponsiveTestConfig
from test_accessibility import AccessibilityTestRunner, AccessibilityConfig
from test_components import ComponentTester, ComponentTestConfig
from logger import get_logger

logger = get_logger()

@dataclass
class VisualTestSuite:
    """Complete visual test suite configuration"""
    run_regression: bool = True
    run_responsive: bool = True
    run_accessibility: bool = True
    run_components: bool = True
    create_baselines: bool = False
    update_baselines: bool = False
    output_dir: str = "tests/visual/reports"
    parallel_execution: bool = False

class ComprehensiveVisualTestRunner:
    """Orchestrates all visual testing suites"""

    def __init__(self, suite_config: VisualTestSuite = None):
        self.suite_config = suite_config or VisualTestSuite()
        self.test_results = {}
        self.start_time = None
        self.end_time = None

    def run_all_tests(self) -> Dict:
        """Run complete visual test suite"""
        self.start_time = time.time()
        logger.info("Starting comprehensive visual test suite")

        try:
            # Ensure output directory exists
            os.makedirs(self.suite_config.output_dir, exist_ok=True)

            # Run visual regression tests
            if self.suite_config.run_regression:
                logger.info("Running visual regression tests...")
                self.test_results['regression'] = self._run_regression_tests()

            # Run responsive tests
            if self.suite_config.run_responsive:
                logger.info("Running responsive design tests...")
                self.test_results['responsive'] = self._run_responsive_tests()

            # Run accessibility tests
            if self.suite_config.run_accessibility:
                logger.info("Running accessibility tests...")
                self.test_results['accessibility'] = self._run_accessibility_tests()

            # Run component tests
            if self.suite_config.run_components:
                logger.info("Running component tests...")
                self.test_results['components'] = self._run_component_tests()

            self.end_time = time.time()

            # Generate comprehensive report
            comprehensive_report = self._generate_comprehensive_report()

            logger.info(f"Visual test suite completed in {self.end_time - self.start_time:.2f} seconds")
            return comprehensive_report

        except Exception as e:
            logger.error(f"Visual test suite failed: {e}")
            self.end_time = time.time()
            return {'error': str(e), 'completed': False}

    def _run_regression_tests(self) -> Dict:
        """Run visual regression tests"""
        try:
            config = VisualTestConfig(
                screenshot_dir=os.path.join(self.suite_config.output_dir, "regression/screenshots"),
                baseline_dir=os.path.join(self.suite_config.output_dir, "regression/baseline"),
                diff_dir=os.path.join(self.suite_config.output_dir, "regression/diff"),
            )

            runner = VisualTestRunner(config)
            visual_results = runner.run_visual_tests()

            # Generate report
            report_path = os.path.join(self.suite_config.output_dir, "regression_report.json")
            report = runner.generate_report(report_path)

            return {
                'completed': True,
                'passed': report['passed_tests'],
                'total': report['total_tests'],
                'report_path': report_path,
                'results': visual_results
            }

        except Exception as e:
            logger.error(f"Regression tests failed: {e}")
            return {'completed': False, 'error': str(e)}

    def _run_responsive_tests(self) -> Dict:
        """Run responsive design tests"""
        try:
            config = ResponsiveTestConfig()
            runner = ResponsiveTestRunner(config)
            responsive_results = runner.run_responsive_tests()

            # Generate report
            report_path = os.path.join(self.suite_config.output_dir, "responsive_report.json")
            report = runner.generate_responsive_report(report_path)

            return {
                'completed': True,
                'passed': report['summary']['passed_tests'],
                'total': report['summary']['total_tests'],
                'report_path': report_path,
                'results': responsive_results
            }

        except Exception as e:
            logger.error(f"Responsive tests failed: {e}")
            return {'completed': False, 'error': str(e)}

    def _run_accessibility_tests(self) -> Dict:
        """Run accessibility tests"""
        try:
            config = AccessibilityConfig()
            runner = AccessibilityTestRunner(config)

            # Get screenshots from previous tests or capture new ones
            screenshot_paths = self._get_available_screenshots()

            if not screenshot_paths:
                logger.warning("No screenshots available for accessibility testing")
                return {'completed': False, 'error': 'No screenshots available'}

            accessibility_results = runner.run_accessibility_tests(screenshot_paths)

            # Generate report
            report_path = os.path.join(self.suite_config.output_dir, "accessibility_report.json")
            report = runner.generate_accessibility_report(report_path)

            return {
                'completed': True,
                'passed': report['summary']['passed_tests'],
                'total': report['summary']['total_tests'],
                'report_path': report_path,
                'results': accessibility_results
            }

        except Exception as e:
            logger.error(f"Accessibility tests failed: {e}")
            return {'completed': False, 'error': str(e)}

    def _run_component_tests(self) -> Dict:
        """Run component-level tests"""
        try:
            config = ComponentTestConfig()
            tester = ComponentTester(config)
            component_results = tester.test_all_components()

            # Generate report
            report_path = os.path.join(self.suite_config.output_dir, "component_report.json")
            report = tester.generate_component_report(report_path)

            return {
                'completed': True,
                'passed': report['summary']['passed_components'],
                'total': report['summary']['total_components'],
                'report_path': report_path,
                'results': component_results
            }

        except Exception as e:
            logger.error(f"Component tests failed: {e}")
            return {'completed': False, 'error': str(e)}

    def _get_available_screenshots(self) -> List[str]:
        """Get list of available screenshots for testing"""
        screenshot_paths = []

        # Check regression test screenshots
        regression_dir = os.path.join(self.suite_config.output_dir, "regression/screenshots")
        if os.path.exists(regression_dir):
            for file in os.listdir(regression_dir):
                if file.endswith('.png'):
                    screenshot_paths.append(os.path.join(regression_dir, file))

        # Check component screenshots
        component_dir = "tests/visual/components"
        if os.path.exists(component_dir):
            for file in os.listdir(component_dir):
                if file.endswith('.png'):
                    screenshot_paths.append(os.path.join(component_dir, file))

        return screenshot_paths

    def _generate_comprehensive_report(self) -> Dict:
        """Generate comprehensive test report"""
        report = {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'execution_time': self.end_time - self.start_time if self.end_time else 0,
            'suite_config': asdict(self.suite_config),
            'summary': {
                'total_test_suites': len([k for k, v in self.test_results.items() if v.get('completed', False)]),
                'passed_test_suites': len([k for k, v in self.test_results.items() if v.get('completed', False) and v.get('passed', 0) == v.get('total', 1)]),
                'total_tests': sum(v.get('total', 0) for v in self.test_results.values()),
                'total_passed': sum(v.get('passed', 0) for v in self.test_results.values()),
                'overall_pass_rate': 0,
            },
            'test_results': self.test_results,
            'recommendations': [],
            'next_steps': []
        }

        # Calculate overall pass rate
        if report['summary']['total_tests'] > 0:
            report['summary']['overall_pass_rate'] = (
                report['summary']['total_passed'] / report['summary']['total_tests'] * 100
            )

        # Generate recommendations based on results
        report['recommendations'] = self._generate_recommendations()
        report['next_steps'] = self._generate_next_steps()

        # Save comprehensive report
        report_path = os.path.join(self.suite_config.output_dir, "comprehensive_visual_test_report.json")
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)

        # Generate HTML report
        html_report_path = os.path.join(self.suite_config.output_dir, "visual_test_report.html")
        self._generate_html_report(report, html_report_path)

        logger.info(f"Comprehensive report generated: {report_path}")
        return report

    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on test results"""
        recommendations = []

        # Analyze regression test results
        if 'regression' in self.test_results:
            regression = self.test_results['regression']
            if regression.get('completed') and regression.get('passed', 0) < regression.get('total', 1):
                recommendations.append("Review and update visual baselines for failing regression tests")

        # Analyze responsive test results
        if 'responsive' in self.test_results:
            responsive = self.test_results['responsive']
            if responsive.get('completed') and responsive.get('passed', 0) < responsive.get('total', 1):
                recommendations.append("Improve responsive design for failed breakpoints")

        # Analyze accessibility results
        if 'accessibility' in self.test_results:
            accessibility = self.test_results['accessibility']
            if accessibility.get('completed') and accessibility.get('passed', 0) < accessibility.get('total', 1):
                recommendations.append("Address accessibility issues to meet WCAG AA standards")

        # Analyze component results
        if 'components' in self.test_results:
            components = self.test_results['components']
            if components.get('completed') and components.get('passed', 0) < components.get('total', 1):
                recommendations.append("Fix component-level visual inconsistencies")

        # General recommendations
        if not recommendations:
            recommendations.append("All visual tests passed - consider implementing automated visual testing in CI/CD")
        else:
            recommendations.append("Integrate visual testing into development workflow")
            recommendations.append("Set up baseline management process")

        return recommendations

    def _generate_next_steps(self) -> List[str]:
        """Generate next steps based on results"""
        next_steps = []

        # Check if any tests failed
        failed_suites = [k for k, v in self.test_results.items() if not v.get('completed', True) or v.get('passed', 0) < v.get('total', 1)]

        if failed_suites:
            next_steps.append(f"Address failing test suites: {', '.join(failed_suites)}")
            next_steps.append("Review detailed test reports for specific issues")
            next_steps.append("Update visual baselines after fixing issues")

        # CI/CD integration
        next_steps.append("Integrate visual tests into CI/CD pipeline")
        next_steps.append("Set up automatic baseline updates for approved changes")
        next_steps.append("Configure visual test notifications for team")

        # Monitoring and maintenance
        next_steps.append("Schedule regular visual test reviews")
        next_steps.append("Train team on visual testing best practices")

        return next_steps

    def _generate_html_report(self, report_data: Dict, output_path: str):
        """Generate HTML report for better visualization"""
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>PdaNet Linux Visual Test Report</title>
    <style>
        body {{ font-family: 'Courier New', monospace; background: #000; color: #00FF00; margin: 20px; }}
        .header {{ border-bottom: 2px solid #00FF00; padding-bottom: 10px; }}
        .summary {{ background: #111; padding: 15px; margin: 10px 0; border: 1px solid #00FF00; }}
        .test-suite {{ background: #111; margin: 10px 0; padding: 10px; border-left: 4px solid #00FF00; }}
        .pass {{ color: #00FF00; }}
        .fail {{ color: #FF0000; }}
        .warning {{ color: #FFFF00; }}
        .recommendations {{ background: #111; padding: 15px; margin: 10px 0; border: 1px solid #FFFF00; }}
        table {{ width: 100%; border-collapse: collapse; }}
        th, td {{ padding: 8px; text-align: left; border-bottom: 1px solid #333; }}
        th {{ background: #222; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>PdaNet Linux Visual Test Report</h1>
        <p>Generated: {report_data['timestamp']}</p>
        <p>Execution Time: {report_data['execution_time']:.2f} seconds</p>
    </div>

    <div class="summary">
        <h2>Summary</h2>
        <table>
            <tr><th>Metric</th><th>Value</th></tr>
            <tr><td>Total Test Suites</td><td>{report_data['summary']['total_test_suites']}</td></tr>
            <tr><td>Passed Test Suites</td><td class="{'pass' if report_data['summary']['passed_test_suites'] == report_data['summary']['total_test_suites'] else 'fail'}">{report_data['summary']['passed_test_suites']}</td></tr>
            <tr><td>Total Tests</td><td>{report_data['summary']['total_tests']}</td></tr>
            <tr><td>Total Passed</td><td class="{'pass' if report_data['summary']['total_passed'] == report_data['summary']['total_tests'] else 'fail'}">{report_data['summary']['total_passed']}</td></tr>
            <tr><td>Overall Pass Rate</td><td class="{'pass' if report_data['summary']['overall_pass_rate'] >= 95 else 'warning' if report_data['summary']['overall_pass_rate'] >= 80 else 'fail'}">{report_data['summary']['overall_pass_rate']:.1f}%</td></tr>
        </table>
    </div>
"""

        # Add test suite details
        for suite_name, suite_result in report_data['test_results'].items():
            status = "PASS" if suite_result.get('completed') and suite_result.get('passed', 0) == suite_result.get('total', 1) else "FAIL"
            status_class = "pass" if status == "PASS" else "fail"

            html_content += f"""
    <div class="test-suite">
        <h3>{suite_name.title()} Tests <span class="{status_class}">[{status}]</span></h3>
        <p>Passed: {suite_result.get('passed', 0)} / {suite_result.get('total', 0)}</p>
        <p>Report: <a href="{os.path.basename(suite_result.get('report_path', ''))}" style="color: #00FFFF;">{os.path.basename(suite_result.get('report_path', 'N/A'))}</a></p>
    </div>
"""

        # Add recommendations
        html_content += """
    <div class="recommendations">
        <h2>Recommendations</h2>
        <ul>
"""
        for rec in report_data['recommendations']:
            html_content += f"            <li>{rec}</li>\n"

        html_content += """
        </ul>
    </div>

    <div class="recommendations">
        <h2>Next Steps</h2>
        <ul>
"""
        for step in report_data['next_steps']:
            html_content += f"            <li>{step}</li>\n"

        html_content += """
        </ul>
    </div>
</body>
</html>"""

        with open(output_path, 'w') as f:
            f.write(html_content)

        logger.info(f"HTML report generated: {output_path}")

def main():
    """Main entry point for visual test runner"""
    parser = argparse.ArgumentParser(description="PdaNet Linux Visual Test Runner")

    parser.add_argument('--regression', action='store_true', help='Run only regression tests')
    parser.add_argument('--responsive', action='store_true', help='Run only responsive tests')
    parser.add_argument('--accessibility', action='store_true', help='Run only accessibility tests')
    parser.add_argument('--components', action='store_true', help='Run only component tests')
    parser.add_argument('--all', action='store_true', default=True, help='Run all test suites (default)')
    parser.add_argument('--create-baselines', action='store_true', help='Create new baselines')
    parser.add_argument('--update-baselines', action='store_true', help='Update existing baselines')
    parser.add_argument('--output-dir', default='tests/visual/reports', help='Output directory for reports')
    parser.add_argument('--parallel', action='store_true', help='Run tests in parallel')

    args = parser.parse_args()

    # Configure test suite
    suite_config = VisualTestSuite(
        run_regression=args.regression or args.all,
        run_responsive=args.responsive or args.all,
        run_accessibility=args.accessibility or args.all,
        run_components=args.components or args.all,
        create_baselines=args.create_baselines,
        update_baselines=args.update_baselines,
        output_dir=args.output_dir,
        parallel_execution=args.parallel
    )

    # Run tests
    runner = ComprehensiveVisualTestRunner(suite_config)
    report = runner.run_all_tests()

    # Print summary
    if 'error' in report:
        print(f"Visual tests failed: {report['error']}")
        sys.exit(1)
    else:
        summary = report['summary']
        print(f"Visual tests completed:")
        print(f"  Test Suites: {summary['passed_test_suites']}/{summary['total_test_suites']} passed")
        print(f"  Total Tests: {summary['total_passed']}/{summary['total_tests']} passed")
        print(f"  Pass Rate: {summary['overall_pass_rate']:.1f}%")

        if summary['overall_pass_rate'] < 100:
            print(f"  See reports in: {args.output_dir}")
            sys.exit(1)

if __name__ == "__main__":
    main()