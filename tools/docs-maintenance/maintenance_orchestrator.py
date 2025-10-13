#!/usr/bin/env python3
"""
PdaNet Linux - Documentation Maintenance Orchestrator
Central system for running all documentation maintenance tasks
"""

import asyncio
import json
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


@dataclass
class MaintenanceTask:
    """A documentation maintenance task"""

    name: str
    description: str
    script: str
    enabled: bool
    frequency: str  # 'daily', 'weekly', 'monthly', 'on_demand'
    dependencies: list[str]
    timeout: int  # seconds
    critical: bool


@dataclass
class TaskResult:
    """Result of a maintenance task execution"""

    task_name: str
    status: str  # 'success', 'failed', 'skipped', 'timeout'
    start_time: str
    end_time: str
    duration: float
    output: str
    error: str | None
    report_file: str | None


@dataclass
class MaintenanceReport:
    """Overall maintenance report"""

    timestamp: str
    total_tasks: int
    successful_tasks: int
    failed_tasks: int
    skipped_tasks: int
    total_duration: float
    task_results: list[TaskResult]
    summary: dict[str, Any]
    recommendations: list[str]


class DocumentationMaintenanceOrchestrator:
    """Orchestrates all documentation maintenance tasks"""

    def __init__(self, project_root: str, config_file: str | None = None):
        self.project_root = Path(project_root)
        self.tools_dir = self.project_root / "tools" / "docs-maintenance"
        self.reports_dir = self.tools_dir / "reports"
        self.config_file = config_file or self.tools_dir / "maintenance_config.json"

        # Ensure directories exist
        self.tools_dir.mkdir(parents=True, exist_ok=True)
        self.reports_dir.mkdir(parents=True, exist_ok=True)

        # Load or create configuration
        self.tasks = self._load_configuration()

    def _load_configuration(self) -> list[MaintenanceTask]:
        """Load maintenance configuration or create default"""
        if self.config_file.exists():
            try:
                with open(self.config_file) as f:
                    config_data = json.load(f)
                return [MaintenanceTask(**task) for task in config_data["tasks"]]
            except Exception as e:
                print(f"Error loading config: {e}, using defaults")

        # Default configuration
        default_tasks = [
            MaintenanceTask(
                name="audit",
                description="Comprehensive documentation audit",
                script="docs_auditor.py",
                enabled=True,
                frequency="weekly",
                dependencies=[],
                timeout=300,
                critical=True,
            ),
            MaintenanceTask(
                name="link_validation",
                description="Validate all internal and external links",
                script="link_validator.py",
                enabled=True,
                frequency="daily",
                dependencies=[],
                timeout=600,
                critical=False,
            ),
            MaintenanceTask(
                name="style_check",
                description="Check documentation style and consistency",
                script="style_checker.py",
                enabled=True,
                frequency="weekly",
                dependencies=[],
                timeout=180,
                critical=False,
            ),
            MaintenanceTask(
                name="content_optimization",
                description="Optimize and enhance documentation content",
                script="content_optimizer.py",
                enabled=True,
                frequency="monthly",
                dependencies=["audit"],
                timeout=240,
                critical=False,
            ),
            MaintenanceTask(
                name="sync_check",
                description="Check documentation synchronization",
                script="sync_checker.py",
                enabled=True,
                frequency="daily",
                dependencies=[],
                timeout=120,
                critical=False,
            ),
        ]

        self._save_configuration(default_tasks)
        return default_tasks

    def _save_configuration(self, tasks: list[MaintenanceTask]) -> None:
        """Save maintenance configuration"""
        config_data = {
            "version": "1.0",
            "last_updated": datetime.now().isoformat(),
            "tasks": [asdict(task) for task in tasks],
        }

        with open(self.config_file, "w") as f:
            json.dump(config_data, f, indent=2)

    async def run_task(self, task: MaintenanceTask) -> TaskResult:
        """Run a single maintenance task"""
        start_time = datetime.now()
        script_path = self.tools_dir / task.script

        print(f"🔧 Running {task.name}: {task.description}")

        if not script_path.exists():
            return TaskResult(
                task_name=task.name,
                status="failed",
                start_time=start_time.isoformat(),
                end_time=datetime.now().isoformat(),
                duration=0.0,
                output="",
                error=f"Script not found: {script_path}",
                report_file=None,
            )

        try:
            # Run the task script
            process = await asyncio.create_subprocess_exec(
                "python3",
                str(script_path),
                str(self.project_root),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=str(self.tools_dir),
            )

            try:
                stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=task.timeout)
            except TimeoutError:
                process.kill()
                await process.wait()

                return TaskResult(
                    task_name=task.name,
                    status="timeout",
                    start_time=start_time.isoformat(),
                    end_time=datetime.now().isoformat(),
                    duration=(datetime.now() - start_time).total_seconds(),
                    output="",
                    error=f"Task timed out after {task.timeout} seconds",
                    report_file=None,
                )

            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()

            output = stdout.decode("utf-8") if stdout else ""
            error = stderr.decode("utf-8") if stderr else None

            # Check for generated report files
            report_file = self._find_latest_report(task.name)

            status = "success" if process.returncode == 0 else "failed"

            return TaskResult(
                task_name=task.name,
                status=status,
                start_time=start_time.isoformat(),
                end_time=end_time.isoformat(),
                duration=duration,
                output=output,
                error=error if process.returncode != 0 else None,
                report_file=str(report_file) if report_file else None,
            )

        except Exception as e:
            return TaskResult(
                task_name=task.name,
                status="failed",
                start_time=start_time.isoformat(),
                end_time=datetime.now().isoformat(),
                duration=(datetime.now() - start_time).total_seconds(),
                output="",
                error=str(e),
                report_file=None,
            )

    def _find_latest_report(self, task_name: str) -> Path | None:
        """Find the latest report file for a task"""
        pattern_map = {
            "audit": "audit_report_*.json",
            "link_validation": "link_validation_*.json",
            "style_check": "style_check_*.json",
            "content_optimization": "content_optimization_*.json",
            "sync_check": "sync_check_*.json",
        }

        pattern = pattern_map.get(task_name, f"{task_name}_*.json")

        matching_files = list(self.reports_dir.glob(pattern))
        if matching_files:
            # Return the most recent file
            return max(matching_files, key=lambda f: f.stat().st_mtime)

        return None

    def check_dependencies(self, task: MaintenanceTask, completed_tasks: Set[str]) -> bool:
        """Check if task dependencies are satisfied"""
        return all(dep in completed_tasks for dep in task.dependencies)

    async def run_maintenance(
        self, task_filter: list[str] | None = None, force_all: bool = False
    ) -> MaintenanceReport:
        """Run documentation maintenance tasks"""
        start_time = datetime.now()

        # Filter tasks based on input
        tasks_to_run = []
        if task_filter:
            tasks_to_run = [task for task in self.tasks if task.name in task_filter]
        else:
            tasks_to_run = [task for task in self.tasks if task.enabled or force_all]

        print(f"🚀 Starting documentation maintenance with {len(tasks_to_run)} tasks")
        print("=" * 60)

        task_results = []
        completed_tasks = set()
        failed_critical_tasks = set()

        # Sort tasks by dependencies (simple topological sort)
        sorted_tasks = self._sort_tasks_by_dependencies(tasks_to_run)

        for task in sorted_tasks:
            # Check if we should skip this task
            if not task.enabled and not force_all:
                task_results.append(
                    TaskResult(
                        task_name=task.name,
                        status="skipped",
                        start_time=datetime.now().isoformat(),
                        end_time=datetime.now().isoformat(),
                        duration=0.0,
                        output="Task disabled",
                        error=None,
                        report_file=None,
                    )
                )
                continue

            # Check dependencies
            if not self.check_dependencies(task, completed_tasks):
                missing_deps = [dep for dep in task.dependencies if dep not in completed_tasks]
                task_results.append(
                    TaskResult(
                        task_name=task.name,
                        status="skipped",
                        start_time=datetime.now().isoformat(),
                        end_time=datetime.now().isoformat(),
                        duration=0.0,
                        output=f'Missing dependencies: {", ".join(missing_deps)}',
                        error=None,
                        report_file=None,
                    )
                )
                continue

            # Skip if critical dependency failed
            critical_deps = [
                dep
                for dep in task.dependencies
                if any(t.critical for t in self.tasks if t.name == dep)
            ]
            if any(dep in failed_critical_tasks for dep in critical_deps):
                task_results.append(
                    TaskResult(
                        task_name=task.name,
                        status="skipped",
                        start_time=datetime.now().isoformat(),
                        end_time=datetime.now().isoformat(),
                        duration=0.0,
                        output="Critical dependency failed",
                        error=None,
                        report_file=None,
                    )
                )
                continue

            # Run the task
            result = await self.run_task(task)
            task_results.append(result)

            if result.status == "success":
                completed_tasks.add(task.name)
                print(f"✅ {task.name} completed successfully ({result.duration:.1f}s)")
            else:
                print(f"❌ {task.name} failed: {result.error or 'Unknown error'}")
                if task.critical:
                    failed_critical_tasks.add(task.name)

        end_time = datetime.now()
        total_duration = (end_time - start_time).total_seconds()

        # Generate summary
        successful_tasks = len([r for r in task_results if r.status == "success"])
        failed_tasks = len([r for r in task_results if r.status == "failed"])
        skipped_tasks = len([r for r in task_results if r.status == "skipped"])

        # Generate recommendations
        recommendations = self._generate_recommendations(task_results)

        # Create summary data
        summary = {
            "execution_time": total_duration,
            "success_rate": successful_tasks / len(task_results) if task_results else 0,
            "critical_failures": len(failed_critical_tasks),
            "task_performance": {
                result.task_name: {"duration": result.duration, "status": result.status}
                for result in task_results
            },
        }

        report = MaintenanceReport(
            timestamp=start_time.isoformat(),
            total_tasks=len(task_results),
            successful_tasks=successful_tasks,
            failed_tasks=failed_tasks,
            skipped_tasks=skipped_tasks,
            total_duration=total_duration,
            task_results=task_results,
            summary=summary,
            recommendations=recommendations,
        )

        return report

    def _sort_tasks_by_dependencies(self, tasks: list[MaintenanceTask]) -> list[MaintenanceTask]:
        """Sort tasks by dependencies (topological sort)"""
        sorted_tasks = []
        remaining_tasks = tasks.copy()
        task_names = {task.name for task in tasks}

        while remaining_tasks:
            # Find tasks with no unresolved dependencies
            ready_tasks = []
            for task in remaining_tasks:
                resolved_deps = [
                    dep
                    for dep in task.dependencies
                    if dep not in task_names or dep in [t.name for t in sorted_tasks]
                ]
                if len(resolved_deps) == len(task.dependencies):
                    ready_tasks.append(task)

            if not ready_tasks:
                # Circular dependency or missing dependency, add remaining tasks anyway
                ready_tasks = remaining_tasks

            # Add ready tasks to sorted list
            for task in ready_tasks:
                sorted_tasks.append(task)
                remaining_tasks.remove(task)

        return sorted_tasks

    def _generate_recommendations(self, task_results: list[TaskResult]) -> list[str]:
        """Generate recommendations based on task results"""
        recommendations = []

        failed_tasks = [r for r in task_results if r.status == "failed"]
        timeout_tasks = [r for r in task_results if r.status == "timeout"]
        slow_tasks = [r for r in task_results if r.duration > 60 and r.status == "success"]

        if failed_tasks:
            recommendations.append(
                f"Fix {len(failed_tasks)} failed tasks before next maintenance run"
            )

        if timeout_tasks:
            recommendations.append(
                f"Increase timeout for {len(timeout_tasks)} tasks that timed out"
            )

        if slow_tasks:
            recommendations.append(
                f"Optimize {len(slow_tasks)} slow-running tasks for better performance"
            )

        # Check for patterns in failures
        error_patterns = {}
        for result in failed_tasks:
            if result.error:
                if "not found" in result.error.lower():
                    error_patterns["missing_files"] = error_patterns.get("missing_files", 0) + 1
                elif "permission" in result.error.lower():
                    error_patterns["permissions"] = error_patterns.get("permissions", 0) + 1
                elif "timeout" in result.error.lower():
                    error_patterns["network"] = error_patterns.get("network", 0) + 1

        for pattern, count in error_patterns.items():
            if pattern == "missing_files":
                recommendations.append(f"Install missing dependencies for {count} tasks")
            elif pattern == "permissions":
                recommendations.append(f"Fix permission issues for {count} tasks")
            elif pattern == "network":
                recommendations.append(f"Check network connectivity for {count} tasks")

        if not recommendations:
            recommendations.append(
                "All tasks completed successfully. Documentation maintenance is up to date."
            )

        return recommendations

    def save_report(self, report: MaintenanceReport, output_path: str) -> None:
        """Save maintenance report to JSON file"""
        with open(output_path, "w") as f:
            json.dump(asdict(report), f, indent=2, default=str)

    def print_summary(self, report: MaintenanceReport) -> None:
        """Print maintenance summary"""
        print("\n" + "=" * 60)
        print("📋 DOCUMENTATION MAINTENANCE SUMMARY")
        print("=" * 60)

        print(f"⏱️  Total duration: {report.total_duration:.1f} seconds")
        print(f"📊 Tasks executed: {report.total_tasks}")
        print(f"✅ Successful: {report.successful_tasks}")
        print(f"❌ Failed: {report.failed_tasks}")
        print(f"⏭️  Skipped: {report.skipped_tasks}")
        print(f"📈 Success rate: {report.summary['success_rate']:.1%}")

        if report.failed_tasks > 0:
            print("\n❌ Failed Tasks:")
            for result in report.task_results:
                if result.status == "failed":
                    print(f"  • {result.task_name}: {result.error}")

        if report.recommendations:
            print("\n💡 Recommendations:")
            for i, rec in enumerate(report.recommendations, 1):
                print(f"  {i}. {rec}")

        print("\n📄 Task Reports:")
        for result in report.task_results:
            if result.report_file and result.status == "success":
                print(f"  • {result.task_name}: {result.report_file}")


async def main():
    """Main function for CLI usage"""
    import argparse

    parser = argparse.ArgumentParser(description="Documentation Maintenance Orchestrator")
    parser.add_argument("project_root", help="Project root directory")
    parser.add_argument("--tasks", nargs="+", help="Specific tasks to run")
    parser.add_argument(
        "--force-all", action="store_true", help="Run all tasks including disabled ones"
    )
    parser.add_argument("--config", help="Custom configuration file")

    args = parser.parse_args()

    orchestrator = DocumentationMaintenanceOrchestrator(args.project_root, args.config)

    report = await orchestrator.run_maintenance(task_filter=args.tasks, force_all=args.force_all)

    # Save detailed report
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = orchestrator.reports_dir / f"maintenance_report_{timestamp}.json"
    orchestrator.save_report(report, str(report_file))

    # Print summary
    orchestrator.print_summary(report)
    print(f"\n📄 Detailed report saved to: {report_file}")


if __name__ == "__main__":
    asyncio.run(main())
