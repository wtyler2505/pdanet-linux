#!/usr/bin/env python3
"""
Retrospective Tracking System
Automated collection and analysis of development metrics for continuous improvement
"""

import json
import os
import subprocess
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
import argparse


@dataclass
class CodeMetrics:
    """Code quality and structure metrics"""
    total_lines: int
    source_lines: int
    test_lines: int
    doc_lines: int
    total_files: int
    source_files: int
    test_files: int
    doc_files: int
    classes: int
    functions: int
    imports: int
    avg_file_size: float
    test_coverage_ratio: float
    docs_to_code_ratio: float


@dataclass
class QualityMetrics:
    """Quality and technical debt metrics"""
    todo_items: int
    fixme_items: int
    technical_debt_ratio: float
    test_methods: int
    import_statements: int
    code_complexity_score: float
    automation_hooks: int
    documentation_files: int


@dataclass
class ProcessMetrics:
    """Development process effectiveness metrics"""
    automation_coverage: float
    quality_gate_count: int
    ci_integration_score: float
    workflow_efficiency: float
    knowledge_sharing_score: float


@dataclass
class RetrospectiveSnapshot:
    """Complete retrospective snapshot for a point in time"""
    timestamp: str
    sprint_id: str
    code_metrics: CodeMetrics
    quality_metrics: QualityMetrics
    process_metrics: ProcessMetrics
    overall_health_score: float
    key_achievements: List[str]
    improvement_areas: List[str]
    action_items: List[str]


class RetrospectiveTracker:
    """Automated retrospective data collection and analysis"""

    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.data_dir = self.project_root / ".retrospective"
        self.data_dir.mkdir(exist_ok=True)

    def collect_code_metrics(self) -> CodeMetrics:
        """Collect comprehensive code metrics"""

        # Count lines in different categories
        source_lines = self._count_lines("src", "*.py")
        test_lines = self._count_lines("tests", "*.py")
        tool_lines = self._count_lines("tools", "*.py")
        doc_lines = self._count_lines(".", "*.md")

        total_lines = source_lines + test_lines + tool_lines + doc_lines

        # Count files
        source_files = len(list(self.project_root.glob("src/*.py")))
        test_files = len(list(self.project_root.glob("tests/*.py")))
        doc_files = len(list(self.project_root.glob("**/*.md")))
        total_files = source_files + test_files + doc_files

        # Count code structures
        classes = self._count_patterns("src", "class ")
        functions = self._count_patterns("src", "def ")
        imports = self._count_patterns("src", "import ")

        # Calculate ratios
        avg_file_size = source_lines / source_files if source_files > 0 else 0
        test_coverage_ratio = test_lines / source_lines if source_lines > 0 else 0
        docs_to_code_ratio = doc_lines / source_lines if source_lines > 0 else 0

        return CodeMetrics(
            total_lines=total_lines,
            source_lines=source_lines,
            test_lines=test_lines,
            doc_lines=doc_lines,
            total_files=total_files,
            source_files=source_files,
            test_files=test_files,
            doc_files=doc_files,
            classes=classes,
            functions=functions,
            imports=imports,
            avg_file_size=avg_file_size,
            test_coverage_ratio=test_coverage_ratio,
            docs_to_code_ratio=docs_to_code_ratio
        )

    def collect_quality_metrics(self) -> QualityMetrics:
        """Collect quality and technical debt metrics"""

        # Count technical debt markers
        todo_items = self._count_patterns("src", "TODO")
        fixme_items = self._count_patterns("src", "FIXME")

        # Count test methods
        test_methods = self._count_patterns("tests", "def test_")

        # Count import statements
        import_statements = self._count_patterns("src", "import ")

        # Count automation and documentation
        automation_hooks = self._count_claude_hooks()
        documentation_files = len(list(self.project_root.glob("**/*.md")))

        # Calculate derived metrics
        source_lines = self._count_lines("src", "*.py")
        technical_debt_ratio = (todo_items + fixme_items) / source_lines if source_lines > 0 else 0
        code_complexity_score = self._calculate_complexity_score()

        return QualityMetrics(
            todo_items=todo_items,
            fixme_items=fixme_items,
            technical_debt_ratio=technical_debt_ratio,
            test_methods=test_methods,
            import_statements=import_statements,
            code_complexity_score=code_complexity_score,
            automation_hooks=automation_hooks,
            documentation_files=documentation_files
        )

    def collect_process_metrics(self) -> ProcessMetrics:
        """Collect development process effectiveness metrics"""

        # Automation coverage
        automation_coverage = self._calculate_automation_coverage()

        # Quality gates
        quality_gate_count = self._count_claude_hooks()

        # CI integration (based on hooks and automation)
        ci_integration_score = min(automation_coverage * 100, 100)

        # Workflow efficiency (based on structure and automation)
        workflow_efficiency = self._calculate_workflow_efficiency()

        # Knowledge sharing (based on documentation ratio)
        docs_ratio = self._count_lines(".", "*.md") / self._count_lines("src", "*.py")
        knowledge_sharing_score = min(docs_ratio * 10, 100)

        return ProcessMetrics(
            automation_coverage=automation_coverage,
            quality_gate_count=quality_gate_count,
            ci_integration_score=ci_integration_score,
            workflow_efficiency=workflow_efficiency,
            knowledge_sharing_score=knowledge_sharing_score
        )

    def calculate_health_score(self, code: CodeMetrics, quality: QualityMetrics,
                             process: ProcessMetrics) -> float:
        """Calculate overall project health score"""

        # Code quality score (0-30 points)
        code_score = min(30, (
            min(20, code.test_coverage_ratio * 20) +  # Test coverage
            min(10, code.docs_to_code_ratio * 2)      # Documentation ratio
        ))

        # Quality score (0-35 points)
        quality_score = min(35, (
            max(0, 15 - quality.technical_debt_ratio * 1000) +  # Low technical debt
            min(10, quality.test_methods / 10) +                # Test methods
            min(10, quality.automation_hooks * 2)               # Automation
        ))

        # Process score (0-35 points)
        process_score = min(35, (
            process.automation_coverage * 15 +      # Automation coverage
            process.workflow_efficiency * 10 +      # Workflow efficiency
            min(10, process.knowledge_sharing_score / 10)  # Knowledge sharing
        ))

        return min(100, code_score + quality_score + process_score)

    def create_snapshot(self, sprint_id: Optional[str] = None) -> RetrospectiveSnapshot:
        """Create a complete retrospective snapshot"""

        if not sprint_id:
            sprint_id = f"snapshot_{int(time.time())}"

        code_metrics = self.collect_code_metrics()
        quality_metrics = self.collect_quality_metrics()
        process_metrics = self.collect_process_metrics()

        health_score = self.calculate_health_score(code_metrics, quality_metrics, process_metrics)

        # Generate insights based on metrics
        achievements = self._identify_achievements(code_metrics, quality_metrics, process_metrics)
        improvements = self._identify_improvements(code_metrics, quality_metrics, process_metrics)
        actions = self._generate_action_items(code_metrics, quality_metrics, process_metrics)

        return RetrospectiveSnapshot(
            timestamp=datetime.now().isoformat(),
            sprint_id=sprint_id,
            code_metrics=code_metrics,
            quality_metrics=quality_metrics,
            process_metrics=process_metrics,
            overall_health_score=health_score,
            key_achievements=achievements,
            improvement_areas=improvements,
            action_items=actions
        )

    def save_snapshot(self, snapshot: RetrospectiveSnapshot) -> str:
        """Save snapshot to disk"""
        filename = f"retrospective_{snapshot.sprint_id}_{int(time.time())}.json"
        filepath = self.data_dir / filename

        with open(filepath, 'w') as f:
            json.dump(asdict(snapshot), f, indent=2)

        return str(filepath)

    def load_snapshots(self, limit: Optional[int] = None) -> List[RetrospectiveSnapshot]:
        """Load historical snapshots"""
        snapshots = []

        for filepath in sorted(self.data_dir.glob("retrospective_*.json")):
            try:
                with open(filepath, 'r') as f:
                    data = json.load(f)
                    # Reconstruct dataclasses
                    snapshot = RetrospectiveSnapshot(
                        timestamp=data['timestamp'],
                        sprint_id=data['sprint_id'],
                        code_metrics=CodeMetrics(**data['code_metrics']),
                        quality_metrics=QualityMetrics(**data['quality_metrics']),
                        process_metrics=ProcessMetrics(**data['process_metrics']),
                        overall_health_score=data['overall_health_score'],
                        key_achievements=data['key_achievements'],
                        improvement_areas=data['improvement_areas'],
                        action_items=data['action_items']
                    )
                    snapshots.append(snapshot)
            except Exception as e:
                print(f"Error loading {filepath}: {e}")

        if limit:
            snapshots = snapshots[-limit:]

        return snapshots

    def generate_trend_analysis(self, days: int = 30) -> Dict:
        """Generate trend analysis for recent snapshots"""
        snapshots = self.load_snapshots()

        if len(snapshots) < 2:
            return {"error": "Need at least 2 snapshots for trend analysis"}

        cutoff_date = datetime.now() - timedelta(days=days)
        recent_snapshots = [
            s for s in snapshots
            if datetime.fromisoformat(s.timestamp) >= cutoff_date
        ]

        if len(recent_snapshots) < 2:
            recent_snapshots = snapshots[-2:]  # At least compare last 2

        first = recent_snapshots[0]
        latest = recent_snapshots[-1]

        return {
            "period": f"{len(recent_snapshots)} snapshots over {days} days",
            "health_score_trend": latest.overall_health_score - first.overall_health_score,
            "test_coverage_trend": latest.code_metrics.test_coverage_ratio - first.code_metrics.test_coverage_ratio,
            "technical_debt_trend": latest.quality_metrics.technical_debt_ratio - first.quality_metrics.technical_debt_ratio,
            "documentation_trend": latest.code_metrics.docs_to_code_ratio - first.code_metrics.docs_to_code_ratio,
            "automation_trend": latest.process_metrics.automation_coverage - first.process_metrics.automation_coverage
        }

    # Helper methods

    def _count_lines(self, directory: str, pattern: str) -> int:
        """Count lines in files matching pattern"""
        total = 0
        search_path = self.project_root / directory

        if not search_path.exists():
            return 0

        for file_path in search_path.rglob(pattern):
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    total += len(f.readlines())
            except Exception:
                continue

        return total

    def _count_patterns(self, directory: str, pattern: str) -> int:
        """Count occurrences of pattern in directory"""
        count = 0
        search_path = self.project_root / directory

        if not search_path.exists():
            return 0

        try:
            result = subprocess.run(
                ['grep', '-r', pattern, str(search_path)],
                capture_output=True, text=True, timeout=30
            )
            if result.returncode == 0:
                count = len(result.stdout.strip().split('\n'))
        except Exception:
            pass

        return count

    def _count_claude_hooks(self) -> int:
        """Count Claude Code automation hooks"""
        settings_file = self.project_root / ".claude" / "settings.json"

        if not settings_file.exists():
            return 0

        try:
            with open(settings_file, 'r') as f:
                settings = json.load(f)
                hooks = 0
                for hook_type in ['PreToolUse', 'PostToolUse', 'Stop']:
                    if hook_type in settings:
                        hooks += len(settings[hook_type])
                return hooks
        except Exception:
            return 0

    def _calculate_complexity_score(self) -> float:
        """Calculate code complexity score (0-100)"""
        source_lines = self._count_lines("src", "*.py")
        functions = self._count_patterns("src", "def ")
        classes = self._count_patterns("src", "class ")

        if source_lines == 0:
            return 0

        # Lower complexity is better
        avg_function_size = source_lines / functions if functions > 0 else 0

        # Score based on maintainable function sizes (20-50 lines ideal)
        if 20 <= avg_function_size <= 50:
            return 100
        elif avg_function_size < 20:
            return 80 + (avg_function_size / 20) * 20
        else:
            return max(0, 100 - (avg_function_size - 50) * 2)

    def _calculate_automation_coverage(self) -> float:
        """Calculate automation coverage (0-1)"""
        hooks = self._count_claude_hooks()
        max_useful_hooks = 15  # Reasonable maximum

        return min(1.0, hooks / max_useful_hooks)

    def _calculate_workflow_efficiency(self) -> float:
        """Calculate workflow efficiency score (0-1)"""
        # Based on organization, automation, and structure
        factors = []

        # Directory organization
        has_src = (self.project_root / "src").exists()
        has_tests = (self.project_root / "tests").exists()
        has_docs = (self.project_root / "docs").exists()
        has_tools = (self.project_root / "tools").exists()

        organization_score = sum([has_src, has_tests, has_docs, has_tools]) / 4
        factors.append(organization_score)

        # Automation presence
        automation_score = min(1.0, self._count_claude_hooks() / 10)
        factors.append(automation_score)

        # Documentation completeness
        doc_ratio = self._count_lines(".", "*.md") / max(1, self._count_lines("src", "*.py"))
        doc_score = min(1.0, doc_ratio / 5)  # 5:1 ratio = full score
        factors.append(doc_score)

        return sum(factors) / len(factors)

    def _identify_achievements(self, code: CodeMetrics, quality: QualityMetrics,
                            process: ProcessMetrics) -> List[str]:
        """Identify key achievements based on metrics"""
        achievements = []

        if code.test_coverage_ratio > 1.0:
            achievements.append(f"Outstanding test coverage: {code.test_coverage_ratio:.1%}")

        if code.docs_to_code_ratio > 5:
            achievements.append(f"Exceptional documentation: {code.docs_to_code_ratio:.1f}:1 ratio")

        if quality.technical_debt_ratio < 0.01:
            achievements.append("Minimal technical debt maintained")

        if quality.automation_hooks > 8:
            achievements.append("Comprehensive automation framework")

        if process.knowledge_sharing_score > 80:
            achievements.append("Excellent knowledge sharing practices")

        return achievements

    def _identify_improvements(self, code: CodeMetrics, quality: QualityMetrics,
                            process: ProcessMetrics) -> List[str]:
        """Identify improvement areas based on metrics"""
        improvements = []

        if code.test_coverage_ratio < 0.8:
            improvements.append("Increase test coverage")

        if quality.technical_debt_ratio > 0.05:
            improvements.append("Reduce technical debt")

        if process.automation_coverage < 0.7:
            improvements.append("Enhance process automation")

        if code.docs_to_code_ratio < 2:
            improvements.append("Improve documentation coverage")

        if quality.automation_hooks < 5:
            improvements.append("Implement more quality gates")

        return improvements

    def _generate_action_items(self, code: CodeMetrics, quality: QualityMetrics,
                             process: ProcessMetrics) -> List[str]:
        """Generate specific action items"""
        actions = []

        if quality.todo_items > 5:
            actions.append(f"Address {quality.todo_items} TODO items")

        if code.test_coverage_ratio < 0.9:
            actions.append("Add tests for uncovered code paths")

        if process.automation_coverage < 0.8:
            actions.append("Implement additional automation hooks")

        if not (self.project_root / ".git").exists():
            actions.append("Initialize git repository for version control")

        return actions


def main():
    """Main CLI interface"""
    parser = argparse.ArgumentParser(description="Retrospective Tracking System")
    parser.add_argument("project_root", help="Project root directory")
    parser.add_argument("--sprint-id", help="Sprint identifier")
    parser.add_argument("--action", choices=["snapshot", "trends", "report"],
                       default="snapshot", help="Action to perform")
    parser.add_argument("--days", type=int, default=30, help="Days for trend analysis")

    args = parser.parse_args()

    tracker = RetrospectiveTracker(args.project_root)

    if args.action == "snapshot":
        snapshot = tracker.create_snapshot(args.sprint_id)
        filepath = tracker.save_snapshot(snapshot)

        print(f"Retrospective snapshot created: {filepath}")
        print(f"Overall health score: {snapshot.overall_health_score:.1f}/100")
        print(f"Key achievements: {len(snapshot.key_achievements)}")
        print(f"Action items: {len(snapshot.action_items)}")

    elif args.action == "trends":
        trends = tracker.generate_trend_analysis(args.days)
        print("Trend Analysis:")
        for key, value in trends.items():
            if isinstance(value, float):
                print(f"  {key}: {value:+.3f}")
            else:
                print(f"  {key}: {value}")

    elif args.action == "report":
        snapshot = tracker.create_snapshot()

        print("=== Retrospective Report ===")
        print(f"Health Score: {snapshot.overall_health_score:.1f}/100")
        print(f"Test Coverage: {snapshot.code_metrics.test_coverage_ratio:.1%}")
        print(f"Documentation Ratio: {snapshot.code_metrics.docs_to_code_ratio:.1f}:1")
        print(f"Technical Debt: {snapshot.quality_metrics.technical_debt_ratio:.3%}")
        print(f"Automation Hooks: {snapshot.quality_metrics.automation_hooks}")

        print("\nKey Achievements:")
        for achievement in snapshot.key_achievements:
            print(f"  ✅ {achievement}")

        print("\nImprovement Areas:")
        for improvement in snapshot.improvement_areas:
            print(f"  ⚠️ {improvement}")

        print("\nAction Items:")
        for action in snapshot.action_items:
            print(f"  🎯 {action}")


if __name__ == "__main__":
    main()