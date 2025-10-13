#!/usr/bin/env python3
"""
PdaNet Linux - Documentation Synchronization Manager
Git-based documentation synchronization and version control integration
"""

import json
import subprocess
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path


@dataclass
class FileChange:
    """Represents a file change in the documentation"""

    file_path: str
    change_type: str  # 'added', 'modified', 'deleted', 'renamed'
    old_path: str | None  # For renamed files
    lines_added: int
    lines_deleted: int
    last_modified: str
    author: str
    commit_hash: str


@dataclass
class SyncStatus:
    """Documentation synchronization status"""

    is_git_repo: bool
    branch: str
    has_uncommitted_changes: bool
    files_to_commit: list[str]
    last_commit: str
    commits_ahead: int
    commits_behind: int
    sync_conflicts: list[str]


@dataclass
class SyncReport:
    """Documentation synchronization report"""

    timestamp: str
    sync_status: SyncStatus
    recent_changes: list[FileChange]
    outdated_files: list[str]
    missing_files: list[str]
    recommendations: list[str]
    auto_sync_enabled: bool
    last_sync: str | None


class DocumentationSyncManager:
    """Manages documentation synchronization with version control"""

    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.git_dir = self.project_root / ".git"

        # Documentation patterns to track
        self.doc_patterns = [
            "*.md",
            "*.txt",
            "*.rst",
            "README*",
            "CHANGELOG*",
            "LICENSE*",
            "docs/**/*",
            "ref/**/*",
        ]

        # Files to ignore in sync operations
        self.ignore_patterns = [
            "**/.git/**",
            "**/node_modules/**",
            "**/__pycache__/**",
            "**/venv/**",
            "**/env/**",
            "**/.claude/**",  # Except for documentation within
            "**/tools/docs-maintenance/reports/**",  # Generated reports
        ]

    def is_git_repository(self) -> bool:
        """Check if project is a git repository"""
        return self.git_dir.exists() and self.git_dir.is_dir()

    def get_git_status(self) -> SyncStatus:
        """Get current git repository status"""
        if not self.is_git_repository():
            return SyncStatus(
                is_git_repo=False,
                branch="",
                has_uncommitted_changes=False,
                files_to_commit=[],
                last_commit="",
                commits_ahead=0,
                commits_behind=0,
                sync_conflicts=[],
            )

        try:
            # Get current branch
            branch_result = subprocess.run(
                ["git", "branch", "--show-current"],
                check=False,
                cwd=self.project_root,
                capture_output=True,
                text=True,
            )
            branch = branch_result.stdout.strip() if branch_result.returncode == 0 else "unknown"

            # Get status
            status_result = subprocess.run(
                ["git", "status", "--porcelain"],
                check=False,
                cwd=self.project_root,
                capture_output=True,
                text=True,
            )

            files_to_commit = []
            if status_result.returncode == 0:
                for line in status_result.stdout.strip().split("\n"):
                    if line.strip():
                        # Parse git status format
                        status_code = line[:2]
                        file_path = line[3:]
                        if any(
                            self._matches_pattern(file_path, pattern)
                            for pattern in self.doc_patterns
                        ):
                            files_to_commit.append(file_path)

            # Get last commit
            last_commit_result = subprocess.run(
                ["git", "log", "-1", "--format=%H %s"],
                check=False,
                cwd=self.project_root,
                capture_output=True,
                text=True,
            )
            last_commit = (
                last_commit_result.stdout.strip() if last_commit_result.returncode == 0 else ""
            )

            # Check remote status
            commits_ahead = 0
            commits_behind = 0
            try:
                # Fetch latest from remote
                subprocess.run(
                    ["git", "fetch"],
                    check=False,
                    cwd=self.project_root,
                    capture_output=True,
                    timeout=30,
                )

                # Count commits ahead/behind
                ahead_result = subprocess.run(
                    ["git", "rev-list", "--count", f"origin/{branch}..HEAD"],
                    check=False,
                    cwd=self.project_root,
                    capture_output=True,
                    text=True,
                )
                if ahead_result.returncode == 0:
                    commits_ahead = int(ahead_result.stdout.strip() or 0)

                behind_result = subprocess.run(
                    ["git", "rev-list", "--count", f"HEAD..origin/{branch}"],
                    check=False,
                    cwd=self.project_root,
                    capture_output=True,
                    text=True,
                )
                if behind_result.returncode == 0:
                    commits_behind = int(behind_result.stdout.strip() or 0)

            except (subprocess.TimeoutExpired, subprocess.CalledProcessError, ValueError):
                pass  # Remote operations failed, continue with local status

            # Check for merge conflicts
            conflict_result = subprocess.run(
                ["git", "diff", "--name-only", "--diff-filter=U"],
                check=False,
                cwd=self.project_root,
                capture_output=True,
                text=True,
            )
            sync_conflicts = []
            if conflict_result.returncode == 0:
                sync_conflicts = [
                    f for f in conflict_result.stdout.strip().split("\n") if f.strip()
                ]

            return SyncStatus(
                is_git_repo=True,
                branch=branch,
                has_uncommitted_changes=len(files_to_commit) > 0,
                files_to_commit=files_to_commit,
                last_commit=last_commit,
                commits_ahead=commits_ahead,
                commits_behind=commits_behind,
                sync_conflicts=sync_conflicts,
            )

        except Exception as e:
            print(f"Error getting git status: {e}")
            return SyncStatus(
                is_git_repo=True,
                branch="error",
                has_uncommitted_changes=False,
                files_to_commit=[],
                last_commit="",
                commits_ahead=0,
                commits_behind=0,
                sync_conflicts=[],
            )

    def get_recent_documentation_changes(self, days: int = 30) -> list[FileChange]:
        """Get recent changes to documentation files"""
        if not self.is_git_repository():
            return []

        changes = []

        try:
            # Get git log for documentation files
            since_date = datetime.now().strftime(f'--since="{days} days ago"')

            for pattern in self.doc_patterns:
                log_result = subprocess.run(
                    ["git", "log", "--oneline", "--name-status", since_date, "--", pattern],
                    check=False,
                    cwd=self.project_root,
                    capture_output=True,
                    text=True,
                )

                if log_result.returncode == 0:
                    changes.extend(self._parse_git_log(log_result.stdout))

        except Exception as e:
            print(f"Error getting recent changes: {e}")

        return changes

    def _parse_git_log(self, git_log_output: str) -> list[FileChange]:
        """Parse git log output to extract file changes"""
        changes = []
        lines = git_log_output.strip().split("\n")

        current_commit = None
        commit_info = {}

        for line in lines:
            if not line.strip():
                continue

            # Parse commit line
            if re.match(r"^[a-f0-9]{7,40}\s", line):
                parts = line.split(" ", 1)
                commit_hash = parts[0]
                commit_message = parts[1] if len(parts) > 1 else ""
                current_commit = commit_hash
                commit_info[commit_hash] = {
                    "message": commit_message,
                    "author": "unknown",  # Would need --format to get author
                    "date": "unknown",
                }
                continue

            # Parse file status line
            if current_commit and line and line[0] in "AMDRT":
                status = line[0]
                file_path = line[1:].strip()

                change_type_map = {
                    "A": "added",
                    "M": "modified",
                    "D": "deleted",
                    "R": "renamed",
                    "T": "modified",  # Type change
                }

                # Skip if not a documentation file
                if not any(
                    self._matches_pattern(file_path, pattern) for pattern in self.doc_patterns
                ):
                    continue

                change = FileChange(
                    file_path=file_path,
                    change_type=change_type_map.get(status, "unknown"),
                    old_path=None,  # Would need more parsing for renames
                    lines_added=0,  # Would need --numstat for line counts
                    lines_deleted=0,
                    last_modified=commit_info[current_commit]["date"],
                    author=commit_info[current_commit]["author"],
                    commit_hash=current_commit,
                )
                changes.append(change)

        return changes

    def _matches_pattern(self, file_path: str, pattern: str) -> bool:
        """Check if file path matches glob pattern"""
        import fnmatch

        return fnmatch.fnmatch(file_path, pattern)

    def find_outdated_files(self, max_age_days: int = 90) -> list[str]:
        """Find documentation files that haven't been updated recently"""
        outdated_files = []

        if not self.is_git_repository():
            # Fall back to filesystem modification time
            for pattern in self.doc_patterns:
                for file_path in self.project_root.rglob(pattern):
                    if self._should_ignore_file(file_path):
                        continue

                    mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
                    age_days = (datetime.now() - mtime).days

                    if age_days > max_age_days:
                        outdated_files.append(str(file_path.relative_to(self.project_root)))

            return outdated_files

        try:
            # Use git to find files not modified recently
            since_date = f'--since="{max_age_days} days ago"'

            # Get all documentation files
            all_doc_files = set()
            for pattern in self.doc_patterns:
                find_result = subprocess.run(
                    ["git", "ls-files", pattern],
                    check=False,
                    cwd=self.project_root,
                    capture_output=True,
                    text=True,
                )

                if find_result.returncode == 0:
                    all_doc_files.update(
                        f for f in find_result.stdout.strip().split("\n") if f.strip()
                    )

            # Get recently modified files
            recent_result = subprocess.run(
                ["git", "log", "--name-only", "--pretty=format:", since_date],
                check=False,
                cwd=self.project_root,
                capture_output=True,
                text=True,
            )

            recent_files = set()
            if recent_result.returncode == 0:
                recent_files = set(f for f in recent_result.stdout.strip().split("\n") if f.strip())

            # Find outdated files
            for file_path in all_doc_files:
                if file_path not in recent_files and not self._should_ignore_file(Path(file_path)):
                    outdated_files.append(file_path)

        except Exception as e:
            print(f"Error finding outdated files: {e}")

        return outdated_files

    def _should_ignore_file(self, file_path: Path) -> bool:
        """Check if file should be ignored based on ignore patterns"""
        file_str = str(file_path)
        return any(self._matches_pattern(file_str, pattern) for pattern in self.ignore_patterns)

    def commit_documentation_changes(self, message: str, files: list[str] | None = None) -> bool:
        """Commit documentation changes"""
        if not self.is_git_repository():
            print("Not a git repository")
            return False

        try:
            # Add files
            if files:
                for file_path in files:
                    subprocess.run(["git", "add", file_path], cwd=self.project_root, check=True)
            else:
                # Add all documentation files
                for pattern in self.doc_patterns:
                    subprocess.run(["git", "add", pattern], check=False, cwd=self.project_root)

            # Check if there are changes to commit
            status_result = subprocess.run(
                ["git", "diff", "--cached", "--quiet"], check=False, cwd=self.project_root
            )

            if status_result.returncode == 0:
                print("No changes to commit")
                return True

            # Commit changes
            commit_result = subprocess.run(
                ["git", "commit", "-m", message],
                check=False,
                cwd=self.project_root,
                capture_output=True,
                text=True,
            )

            if commit_result.returncode == 0:
                print(f"Successfully committed: {message}")
                return True
            else:
                print(f"Commit failed: {commit_result.stderr}")
                return False

        except subprocess.CalledProcessError as e:
            print(f"Git operation failed: {e}")
            return False

    def sync_with_remote(self, push: bool = False) -> bool:
        """Sync with remote repository"""
        if not self.is_git_repository():
            return False

        try:
            # Fetch latest changes
            fetch_result = subprocess.run(
                ["git", "fetch"],
                check=False,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=60,
            )

            if fetch_result.returncode != 0:
                print(f"Fetch failed: {fetch_result.stderr}")
                return False

            # Pull if behind
            status = self.get_git_status()
            if status.commits_behind > 0:
                pull_result = subprocess.run(
                    ["git", "pull"],
                    check=False,
                    cwd=self.project_root,
                    capture_output=True,
                    text=True,
                )

                if pull_result.returncode != 0:
                    print(f"Pull failed: {pull_result.stderr}")
                    return False

            # Push if ahead and requested
            if push and status.commits_ahead > 0:
                push_result = subprocess.run(
                    ["git", "push"],
                    check=False,
                    cwd=self.project_root,
                    capture_output=True,
                    text=True,
                )

                if push_result.returncode != 0:
                    print(f"Push failed: {push_result.stderr}")
                    return False

            return True

        except subprocess.TimeoutExpired:
            print("Git operation timed out")
            return False
        except Exception as e:
            print(f"Sync failed: {e}")
            return False

    def generate_sync_report(self) -> SyncReport:
        """Generate comprehensive synchronization report"""
        print("📊 Generating synchronization report...")

        sync_status = self.get_git_status()
        recent_changes = self.get_recent_documentation_changes(30)
        outdated_files = self.find_outdated_files(90)

        # Find missing files (referenced but don't exist)
        missing_files = self._find_missing_referenced_files()

        # Generate recommendations
        recommendations = self._generate_sync_recommendations(
            sync_status, recent_changes, outdated_files, missing_files
        )

        return SyncReport(
            timestamp=datetime.now().isoformat(),
            sync_status=sync_status,
            recent_changes=recent_changes,
            outdated_files=outdated_files,
            missing_files=missing_files,
            recommendations=recommendations,
            auto_sync_enabled=False,  # Would be configurable
            last_sync=None,  # Would track from config/state
        )

    def _find_missing_referenced_files(self) -> list[str]:
        """Find files that are referenced but don't exist"""
        missing_files = []

        # This would integrate with the link validator
        # For now, return empty list
        return missing_files

    def _generate_sync_recommendations(
        self, status: SyncStatus, changes: list[FileChange], outdated: list[str], missing: list[str]
    ) -> list[str]:
        """Generate synchronization recommendations"""
        recommendations = []

        if not status.is_git_repo:
            recommendations.append("Initialize git repository for version control")
            return recommendations

        if status.has_uncommitted_changes:
            recommendations.append(
                f"Commit {len(status.files_to_commit)} uncommitted documentation changes"
            )

        if status.commits_behind > 0:
            recommendations.append(f"Pull {status.commits_behind} commits from remote repository")

        if status.commits_ahead > 0:
            recommendations.append(f"Push {status.commits_ahead} commits to remote repository")

        if status.sync_conflicts:
            recommendations.append(f"Resolve {len(status.sync_conflicts)} merge conflicts")

        if outdated:
            recommendations.append(
                f"Review and update {len(outdated)} outdated documentation files"
            )

        if missing:
            recommendations.append(f"Fix {len(missing)} broken file references")

        if len(changes) > 50:
            recommendations.append(
                "High documentation activity - consider reviewing recent changes"
            )

        if not recommendations:
            recommendations.append("Documentation is synchronized and up to date")

        return recommendations

    def save_report(self, report: SyncReport, output_path: str) -> None:
        """Save sync report to JSON file"""
        with open(output_path, "w") as f:
            json.dump(asdict(report), f, indent=2, default=str)

    def print_summary(self, report: SyncReport) -> None:
        """Print synchronization summary"""
        print("\n" + "=" * 50)
        print("🔄 DOCUMENTATION SYNC SUMMARY")
        print("=" * 50)

        status = report.sync_status

        if status.is_git_repo:
            print(f"📂 Repository: {status.branch} branch")
            print(f"📝 Uncommitted changes: {len(status.files_to_commit)}")
            print(f"⬆️  Commits ahead: {status.commits_ahead}")
            print(f"⬇️  Commits behind: {status.commits_behind}")

            if status.sync_conflicts:
                print(f"⚠️  Conflicts: {len(status.sync_conflicts)}")
        else:
            print("📂 Not a git repository")

        print("\n📊 Recent Activity (30 days):")
        print(f"  • File changes: {len(report.recent_changes)}")
        print(f"  • Outdated files: {len(report.outdated_files)}")
        print(f"  • Missing references: {len(report.missing_files)}")

        if report.recommendations:
            print("\n💡 Recommendations:")
            for i, rec in enumerate(report.recommendations, 1):
                print(f"  {i}. {rec}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("Usage: python sync_manager.py <project_root>")
        sys.exit(1)

    project_root = sys.argv[1]
    sync_manager = DocumentationSyncManager(project_root)
    report = sync_manager.generate_sync_report()

    # Save detailed report
    output_dir = Path(project_root) / "tools" / "docs-maintenance" / "reports"
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = output_dir / f"sync_report_{timestamp}.json"
    sync_manager.save_report(report, str(report_file))

    # Print summary
    sync_manager.print_summary(report)
    print(f"\n📄 Detailed report saved to: {report_file}")
