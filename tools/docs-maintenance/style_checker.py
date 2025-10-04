#!/usr/bin/env python3
"""
PdaNet Linux - Documentation Style Checker
Comprehensive style and consistency validation for documentation
"""

import re
import json
import spellchecker
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass, asdict
from datetime import datetime
from collections import defaultdict, Counter


@dataclass
class StyleIssue:
    """A style or consistency issue"""
    file_path: str
    line_number: int
    column: int
    issue_type: str
    severity: str  # 'error', 'warning', 'info'
    message: str
    suggestion: Optional[str]
    context: str


@dataclass
class StyleReport:
    """Style checking report"""
    timestamp: str
    total_files: int
    total_issues: int
    issues_by_severity: Dict[str, int]
    issues_by_type: Dict[str, int]
    issues: List[StyleIssue]
    statistics: Dict[str, any]


class DocumentationStyleChecker:
    """Comprehensive documentation style checker"""

    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.spell = spellchecker.SpellChecker()

        # Load project-specific dictionary
        self.project_terms = {
            'pdanet', 'linux', 'wifi', 'usb', 'tethering', 'stealth',
            'cyberpunk', 'gui', 'gtk', 'bluetooth', 'android', 'redsocks',
            'iptables', 'ttl', 'ipv6', 'dns', 'sysctl', 'subprocess',
            'systemctl', 'networkmanager', 'mtu', 'mss', 'dhcp',
            'github', 'api', 'json', 'yaml', 'markdown', 'python',
            'javascript', 'typescript', 'css', 'html', 'sql',
            'cli', 'ide', 'sdk', 'tcp', 'udp', 'http', 'https',
            'oauth', 'jwt', 'ssl', 'tls', 'vpn', 'nat', 'dhcp'
        }
        self.spell.word_frequency.load_words(self.project_terms)

        # Style rules configuration
        self.rules = {
            'max_line_length': 120,
            'require_title': True,
            'heading_style': 'atx',  # # style vs underline style
            'list_style': 'consistent',
            'emphasis_style': 'asterisk',  # * vs _
            'code_fence_style': 'backticks',  # ``` vs ~~~
            'link_style': 'inline',
            'require_alt_text': True,
            'max_heading_level': 4,
            'check_spelling': True,
            'check_grammar_basic': True
        }

        # Common abbreviations and acronyms
        self.acronyms = {
            'api', 'cli', 'gui', 'ui', 'ux', 'cpu', 'gpu', 'ram',
            'ssd', 'hdd', 'usb', 'tcp', 'udp', 'http', 'https',
            'ftp', 'ssh', 'ssl', 'tls', 'vpn', 'dns', 'dhcp',
            'nat', 'wan', 'lan', 'wifi', 'iot', 'ai', 'ml',
            'adr', 'json', 'xml', 'yaml', 'csv', 'pdf', 'png',
            'jpg', 'gif', 'svg', 'css', 'js', 'ts', 'py'
        }

    def check_file(self, file_path: Path) -> List[StyleIssue]:
        """Check a single file for style issues"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except Exception as e:
            return [StyleIssue(
                file_path=str(file_path.relative_to(self.project_root)),
                line_number=0,
                column=0,
                issue_type='file_error',
                severity='error',
                message=f'Could not read file: {e}',
                suggestion=None,
                context=''
            )]

        issues = []
        lines = content.split('\n')
        relative_path = str(file_path.relative_to(self.project_root))

        # Check overall document structure
        issues.extend(self._check_document_structure(relative_path, content, lines))

        # Check each line
        for line_num, line in enumerate(lines, 1):
            issues.extend(self._check_line(relative_path, line_num, line))

        # Check markdown-specific rules
        if file_path.suffix.lower() == '.md':
            issues.extend(self._check_markdown_specific(relative_path, content, lines))

        return issues

    def _check_document_structure(self, file_path: str, content: str, lines: List[str]) -> List[StyleIssue]:
        """Check overall document structure"""
        issues = []

        # Check for title
        if self.rules['require_title']:
            has_title = False
            for line in lines[:10]:  # Check first 10 lines
                if line.startswith('# ') or re.match(r'^[A-Z].*\n=+$', line + '\n' + (lines[lines.index(line) + 1] if lines.index(line) + 1 < len(lines) else '')):
                    has_title = True
                    break

            if not has_title:
                issues.append(StyleIssue(
                    file_path=file_path,
                    line_number=1,
                    column=1,
                    issue_type='missing_title',
                    severity='warning',
                    message='Document should start with a title',
                    suggestion='Add a title using # Title or underline style',
                    context=lines[0][:50] if lines else ''
                ))

        # Check heading hierarchy
        heading_levels = []
        for line_num, line in enumerate(lines, 1):
            if line.startswith('#'):
                level = len(line) - len(line.lstrip('#'))
                if level > self.rules['max_heading_level']:
                    issues.append(StyleIssue(
                        file_path=file_path,
                        line_number=line_num,
                        column=1,
                        issue_type='heading_too_deep',
                        severity='warning',
                        message=f'Heading level {level} exceeds maximum of {self.rules["max_heading_level"]}',
                        suggestion=f'Use heading level {self.rules["max_heading_level"]} or lower',
                        context=line.strip()
                    ))

                heading_levels.append((line_num, level))

        # Check for heading level skips
        for i in range(1, len(heading_levels)):
            prev_level = heading_levels[i-1][1]
            curr_level = heading_levels[i][1]
            curr_line = heading_levels[i][0]

            if curr_level > prev_level + 1:
                issues.append(StyleIssue(
                    file_path=file_path,
                    line_number=curr_line,
                    column=1,
                    issue_type='heading_skip',
                    severity='warning',
                    message=f'Heading level jumps from {prev_level} to {curr_level}',
                    suggestion=f'Use level {prev_level + 1} instead',
                    context=lines[curr_line - 1].strip()
                ))

        return issues

    def _check_line(self, file_path: str, line_num: int, line: str) -> List[StyleIssue]:
        """Check a single line for style issues"""
        issues = []

        # Check line length
        if len(line) > self.rules['max_line_length']:
            issues.append(StyleIssue(
                file_path=file_path,
                line_number=line_num,
                column=self.rules['max_line_length'],
                issue_type='line_too_long',
                severity='warning',
                message=f'Line length {len(line)} exceeds {self.rules["max_line_length"]} characters',
                suggestion='Break line or use shorter sentences',
                context=line[:50] + '...' if len(line) > 50 else line
            ))

        # Check trailing whitespace
        if line.endswith(' ') or line.endswith('\t'):
            issues.append(StyleIssue(
                file_path=file_path,
                line_number=line_num,
                column=len(line.rstrip()) + 1,
                issue_type='trailing_whitespace',
                severity='info',
                message='Line has trailing whitespace',
                suggestion='Remove trailing spaces',
                context=line.rstrip()
            ))

        # Check tab characters
        if '\t' in line:
            tab_pos = line.find('\t')
            issues.append(StyleIssue(
                file_path=file_path,
                line_number=line_num,
                column=tab_pos + 1,
                issue_type='tab_character',
                severity='info',
                message='Use spaces instead of tabs',
                suggestion='Replace tabs with spaces',
                context=line[:tab_pos + 10]
            ))

        # Check spelling in text content
        if self.rules['check_spelling']:
            issues.extend(self._check_spelling(file_path, line_num, line))

        # Check markdown formatting
        issues.extend(self._check_markdown_formatting(file_path, line_num, line))

        return issues

    def _check_spelling(self, file_path: str, line_num: int, line: str) -> List[StyleIssue]:
        """Check spelling in a line"""
        issues = []

        # Skip code blocks and inline code
        if line.strip().startswith('```') or line.strip().startswith('    '):
            return issues

        # Extract words, excluding code spans
        text = re.sub(r'`[^`]+`', '', line)  # Remove inline code
        text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)  # Remove link URLs, keep text
        text = re.sub(r'[*_]{1,2}([^*_]+)[*_]{1,2}', r'\1', text)  # Remove emphasis markers

        words = re.findall(r'\b[a-zA-Z]+\b', text.lower())

        for word in words:
            # Skip acronyms and project terms
            if word in self.acronyms or word in self.project_terms:
                continue

            # Skip short words
            if len(word) < 3:
                continue

            # Check spelling
            if word not in self.spell:
                suggestions = list(self.spell.candidates(word))[:3]
                suggestion_text = f"Did you mean: {', '.join(suggestions)}?" if suggestions else None

                issues.append(StyleIssue(
                    file_path=file_path,
                    line_number=line_num,
                    column=line.lower().find(word) + 1,
                    issue_type='spelling',
                    severity='info',
                    message=f'Possible spelling error: "{word}"',
                    suggestion=suggestion_text,
                    context=line.strip()
                ))

        return issues

    def _check_markdown_formatting(self, file_path: str, line_num: int, line: str) -> List[StyleIssue]:
        """Check markdown formatting consistency"""
        issues = []

        # Check emphasis style consistency
        if self.rules['emphasis_style'] == 'asterisk':
            if re.search(r'_[^_]+_', line) and not re.search(r'__[^_]+__', line):
                issues.append(StyleIssue(
                    file_path=file_path,
                    line_number=line_num,
                    column=line.find('_') + 1,
                    issue_type='emphasis_style',
                    severity='info',
                    message='Use asterisks (*) for emphasis instead of underscores',
                    suggestion='Replace _text_ with *text*',
                    context=line.strip()
                ))

        # Check list style consistency
        if line.strip().startswith(('- ', '* ', '+ ')):
            if self.rules['list_style'] == 'consistent':
                # This would need to be checked at document level for consistency
                pass

        # Check code fence style
        if line.strip().startswith('~~~'):
            if self.rules['code_fence_style'] == 'backticks':
                issues.append(StyleIssue(
                    file_path=file_path,
                    line_number=line_num,
                    column=1,
                    issue_type='code_fence_style',
                    severity='info',
                    message='Use backticks (```) for code fences instead of tildes',
                    suggestion='Replace ~~~ with ```',
                    context=line.strip()
                ))

        # Check for alt text in images
        if self.rules['require_alt_text']:
            img_matches = re.finditer(r'!\[([^\]]*)\]\([^)]+\)', line)
            for match in img_matches:
                alt_text = match.group(1)
                if not alt_text.strip():
                    issues.append(StyleIssue(
                        file_path=file_path,
                        line_number=line_num,
                        column=match.start() + 1,
                        issue_type='missing_alt_text',
                        severity='warning',
                        message='Image is missing alt text',
                        suggestion='Add descriptive alt text for accessibility',
                        context=match.group(0)
                    ))

        return issues

    def _check_markdown_specific(self, file_path: str, content: str, lines: List[str]) -> List[StyleIssue]:
        """Check markdown-specific style rules"""
        issues = []

        # Check for consistent list markers
        list_markers = []
        for line_num, line in enumerate(lines, 1):
            if re.match(r'^\s*[*+-]\s', line):
                marker = re.match(r'^\s*([*+-])\s', line).group(1)
                list_markers.append((line_num, marker))

        if len(set(marker for _, marker in list_markers)) > 1:
            # Mixed list markers found
            most_common = Counter(marker for _, marker in list_markers).most_common(1)[0][0]
            for line_num, marker in list_markers:
                if marker != most_common:
                    issues.append(StyleIssue(
                        file_path=file_path,
                        line_number=line_num,
                        column=lines[line_num - 1].find(marker) + 1,
                        issue_type='inconsistent_list_marker',
                        severity='info',
                        message=f'Inconsistent list marker "{marker}", use "{most_common}" for consistency',
                        suggestion=f'Replace "{marker}" with "{most_common}"',
                        context=lines[line_num - 1].strip()
                    ))

        # Check for proper table formatting
        table_lines = [i for i, line in enumerate(lines) if '|' in line and not line.strip().startswith('```')]
        for line_num in table_lines:
            line = lines[line_num]
            if not re.match(r'^\s*\|.*\|\s*$', line):
                issues.append(StyleIssue(
                    file_path=file_path,
                    line_number=line_num + 1,
                    column=1,
                    issue_type='table_formatting',
                    severity='info',
                    message='Table row should start and end with |',
                    suggestion='Add | at beginning and end of table row',
                    context=line.strip()
                ))

        return issues

    def check_all_files(self) -> StyleReport:
        """Check all documentation files for style issues"""
        print("🔍 Discovering documentation files...")

        # Find all documentation files
        doc_files = []
        for pattern in ['*.md', '*.txt', '*.rst']:
            doc_files.extend(self.project_root.rglob(pattern))

        # Filter out hidden directories except .claude
        filtered_files = []
        for file_path in doc_files:
            if any(part.startswith('.') and part != '.claude' for part in file_path.parts):
                continue
            filtered_files.append(file_path)

        print(f"📝 Checking style in {len(filtered_files)} files...")

        all_issues = []
        for i, file_path in enumerate(filtered_files, 1):
            print(f"  [{i}/{len(filtered_files)}] {file_path.name}")
            file_issues = self.check_file(file_path)
            all_issues.extend(file_issues)

        # Generate statistics
        issues_by_severity = defaultdict(int)
        issues_by_type = defaultdict(int)

        for issue in all_issues:
            issues_by_severity[issue.severity] += 1
            issues_by_type[issue.issue_type] += 1

        statistics = {
            'files_checked': len(filtered_files),
            'total_issues': len(all_issues),
            'files_with_issues': len(set(issue.file_path for issue in all_issues)),
            'avg_issues_per_file': len(all_issues) / len(filtered_files) if filtered_files else 0,
            'most_common_issues': dict(Counter(issue.issue_type for issue in all_issues).most_common(5))
        }

        return StyleReport(
            timestamp=datetime.now().isoformat(),
            total_files=len(filtered_files),
            total_issues=len(all_issues),
            issues_by_severity=dict(issues_by_severity),
            issues_by_type=dict(issues_by_type),
            issues=all_issues,
            statistics=statistics
        )

    def save_report(self, report: StyleReport, output_path: str) -> None:
        """Save style report to JSON file"""
        with open(output_path, 'w') as f:
            json.dump(asdict(report), f, indent=2, default=str)

    def print_summary(self, report: StyleReport) -> None:
        """Print style check summary"""
        print("\n" + "="*50)
        print("📋 STYLE CHECK SUMMARY")
        print("="*50)

        print(f"📁 Files checked: {report.total_files}")
        print(f"📝 Total issues: {report.total_issues}")
        print(f"📊 Files with issues: {report.statistics['files_with_issues']}")
        print(f"📈 Average issues per file: {report.statistics['avg_issues_per_file']:.1f}")

        print(f"\n📊 Issues by Severity:")
        for severity, count in sorted(report.issues_by_severity.items()):
            percentage = count / report.total_issues * 100 if report.total_issues > 0 else 0
            print(f"  • {severity.title()}: {count} ({percentage:.1f}%)")

        print(f"\n🔍 Most Common Issues:")
        for issue_type, count in report.statistics['most_common_issues'].items():
            percentage = count / report.total_issues * 100 if report.total_issues > 0 else 0
            print(f"  • {issue_type.replace('_', ' ').title()}: {count} ({percentage:.1f}%)")

        # Show some example issues
        if report.total_issues > 0:
            print(f"\n⚠️  Example Issues:")
            error_issues = [i for i in report.issues if i.severity == 'error'][:3]
            warning_issues = [i for i in report.issues if i.severity == 'warning'][:3]

            for issue in error_issues + warning_issues:
                print(f"  • {issue.file_path}:{issue.line_number} - {issue.message}")
                if issue.suggestion:
                    print(f"    Suggestion: {issue.suggestion}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("Usage: python style_checker.py <project_root>")
        sys.exit(1)

    project_root = sys.argv[1]
    checker = DocumentationStyleChecker(project_root)
    report = checker.check_all_files()

    # Save detailed report
    output_dir = Path(project_root) / "tools" / "docs-maintenance" / "reports"
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = output_dir / f"style_check_{timestamp}.json"
    checker.save_report(report, str(report_file))

    # Print summary
    checker.print_summary(report)
    print(f"\n📄 Detailed report saved to: {report_file}")