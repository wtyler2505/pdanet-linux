#!/usr/bin/env python3
"""
PdaNet Linux - Documentation Auditor
Comprehensive documentation maintenance and quality assurance system
"""

import os
import re
import json
import hashlib
import urllib.request
import urllib.parse
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass, asdict
from collections import defaultdict


@dataclass
class DocumentInfo:
    """Document metadata and analysis results"""
    path: str
    size: int
    word_count: int
    line_count: int
    last_modified: str
    file_type: str
    category: str
    title: str
    headings: List[str]
    internal_links: List[str]
    external_links: List[str]
    images: List[str]
    code_blocks: List[str]
    todos: List[str]
    fixmes: List[str]
    issues: List[str]
    quality_score: float


@dataclass
class AuditReport:
    """Complete audit report"""
    timestamp: str
    total_files: int
    total_words: int
    total_size: int
    categories: Dict[str, int]
    broken_links: List[str]
    missing_images: List[str]
    orphaned_files: List[str]
    outdated_files: List[str]
    todos_fixmes: List[str]
    quality_issues: List[str]
    recommendations: List[str]
    documents: List[DocumentInfo]


class DocumentationAuditor:
    """Main documentation auditor class"""

    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.report = AuditReport(
            timestamp=datetime.now().isoformat(),
            total_files=0,
            total_words=0,
            total_size=0,
            categories={},
            broken_links=[],
            missing_images=[],
            orphaned_files=[],
            outdated_files=[],
            todos_fixmes=[],
            quality_issues=[],
            recommendations=[],
            documents=[]
        )

        # File patterns for documentation
        self.doc_patterns = {
            '*.md': 'markdown',
            '*.txt': 'text',
            '*.rst': 'restructured_text',
            'README*': 'readme',
            'CHANGELOG*': 'changelog',
            'LICENSE*': 'license'
        }

        # Quality thresholds
        self.quality_thresholds = {
            'min_word_count': 50,
            'max_age_days': 90,
            'min_headings': 1,
            'max_broken_links': 0,
            'readability_score': 0.7
        }

    def discover_documents(self) -> List[Path]:
        """Discover all documentation files in the project"""
        doc_files = []

        # Find markdown, text, and other doc files
        for pattern in ['*.md', '*.txt', '*.rst']:
            doc_files.extend(self.project_root.rglob(pattern))

        # Filter out hidden directories except .claude
        filtered_files = []
        for file_path in doc_files:
            # Include .claude directory but exclude other hidden dirs
            if any(part.startswith('.') and part != '.claude' for part in file_path.parts):
                continue
            filtered_files.append(file_path)

        return filtered_files

    def categorize_document(self, file_path: Path) -> str:
        """Categorize document based on path and content"""
        path_str = str(file_path).lower()

        # Architecture and technical docs
        if 'architecture' in path_str or 'arc42' in path_str or 'adr' in path_str:
            return 'architecture'

        # Reference documentation
        if '/ref/' in path_str or 'reference' in path_str:
            return 'reference'

        # API documentation
        if 'api' in path_str:
            return 'api'

        # User guides and tutorials
        if any(term in path_str for term in ['guide', 'tutorial', 'how-to', 'quickstart']):
            return 'guide'

        # Installation and setup
        if any(term in path_str for term in ['install', 'setup', 'deployment']):
            return 'setup'

        # Development and internal docs
        if any(term in path_str for term in ['dev', 'development', 'onboarding', 'commands', 'agents']):
            return 'development'

        # Project management
        if any(term in path_str for term in ['feature', 'complete', 'todo', 'decision']):
            return 'project_management'

        # Configuration and templates
        if any(term in path_str for term in ['config', 'template', 'claude']):
            return 'configuration'

        # Main project files
        if file_path.name.upper() in ['README.MD', 'CHANGELOG.MD', 'LICENSE.MD', 'CONTRIBUTING.MD']:
            return 'project_root'

        return 'miscellaneous'

    def analyze_content(self, file_path: Path) -> DocumentInfo:
        """Analyze a single document's content"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except Exception as e:
            return DocumentInfo(
                path=str(file_path),
                size=0,
                word_count=0,
                line_count=0,
                last_modified='unknown',
                file_type='unknown',
                category='error',
                title=f'Error reading file: {e}',
                headings=[],
                internal_links=[],
                external_links=[],
                images=[],
                code_blocks=[],
                todos=[],
                fixmes=[],
                issues=[],
                quality_score=0.0
            )

        stat = file_path.stat()
        lines = content.split('\n')

        # Extract metadata
        title = self.extract_title(content, file_path)
        headings = self.extract_headings(content)
        internal_links, external_links = self.extract_links(content)
        images = self.extract_images(content)
        code_blocks = self.extract_code_blocks(content)
        todos = self.extract_todos_fixmes(content, 'TODO')
        fixmes = self.extract_todos_fixmes(content, 'FIXME')

        # Quality analysis
        issues = self.analyze_quality_issues(content, file_path)
        quality_score = self.calculate_quality_score(content, headings, issues)

        return DocumentInfo(
            path=str(file_path.relative_to(self.project_root)),
            size=stat.st_size,
            word_count=len(content.split()),
            line_count=len(lines),
            last_modified=datetime.fromtimestamp(stat.st_mtime).isoformat(),
            file_type=file_path.suffix.lower(),
            category=self.categorize_document(file_path),
            title=title,
            headings=headings,
            internal_links=internal_links,
            external_links=external_links,
            images=images,
            code_blocks=code_blocks,
            todos=todos,
            fixmes=fixmes,
            issues=issues,
            quality_score=quality_score
        )

    def extract_title(self, content: str, file_path: Path) -> str:
        """Extract document title"""
        lines = content.split('\n')

        # Look for H1 heading
        for line in lines:
            if line.startswith('# '):
                return line[2:].strip()

        # Look for HTML title
        title_match = re.search(r'<title>(.*?)</title>', content, re.IGNORECASE)
        if title_match:
            return title_match.group(1).strip()

        # Use filename as fallback
        return file_path.stem.replace('-', ' ').replace('_', ' ').title()

    def extract_headings(self, content: str) -> List[str]:
        """Extract all headings from markdown content"""
        headings = []
        lines = content.split('\n')

        for line in lines:
            line = line.strip()
            if line.startswith('#'):
                # Remove markdown syntax and clean up
                heading = re.sub(r'^#+\s*', '', line).strip()
                if heading:
                    headings.append(heading)

        return headings

    def extract_links(self, content: str) -> Tuple[List[str], List[str]]:
        """Extract internal and external links"""
        internal_links = []
        external_links = []

        # Markdown links: [text](url)
        md_links = re.findall(r'\[([^\]]*)\]\(([^)]+)\)', content)
        for text, url in md_links:
            if url.startswith(('http://', 'https://')):
                external_links.append(url)
            else:
                internal_links.append(url)

        # HTML links
        html_links = re.findall(r'<a[^>]+href=["\']([^"\']+)["\'][^>]*>', content, re.IGNORECASE)
        for url in html_links:
            if url.startswith(('http://', 'https://')):
                external_links.append(url)
            else:
                internal_links.append(url)

        return list(set(internal_links)), list(set(external_links))

    def extract_images(self, content: str) -> List[str]:
        """Extract image references"""
        images = []

        # Markdown images: ![alt](src)
        md_images = re.findall(r'!\[([^\]]*)\]\(([^)]+)\)', content)
        for alt, src in md_images:
            images.append(src)

        # HTML images
        html_images = re.findall(r'<img[^>]+src=["\']([^"\']+)["\'][^>]*>', content, re.IGNORECASE)
        images.extend(html_images)

        return list(set(images))

    def extract_code_blocks(self, content: str) -> List[str]:
        """Extract code blocks and their languages"""
        code_blocks = []

        # Fenced code blocks
        fenced_blocks = re.findall(r'```(\w*)\n(.*?)\n```', content, re.DOTALL)
        for lang, code in fenced_blocks:
            code_blocks.append(f"{lang or 'unknown'}: {len(code.split())} words")

        # Indented code blocks
        lines = content.split('\n')
        in_code_block = False
        code_lines = 0

        for line in lines:
            if line.startswith('    ') and line.strip():
                if not in_code_block:
                    in_code_block = True
                    code_lines = 1
                else:
                    code_lines += 1
            else:
                if in_code_block:
                    code_blocks.append(f"indented: {code_lines} lines")
                    in_code_block = False

        return code_blocks

    def extract_todos_fixmes(self, content: str, keyword: str) -> List[str]:
        """Extract TODO and FIXME comments"""
        pattern = fr'{keyword}:?\s*(.+?)(?:\n|$)'
        matches = re.findall(pattern, content, re.IGNORECASE | re.MULTILINE)
        return [match.strip() for match in matches if match.strip()]

    def analyze_quality_issues(self, content: str, file_path: Path) -> List[str]:
        """Analyze content for quality issues"""
        issues = []

        # Check word count
        word_count = len(content.split())
        if word_count < self.quality_thresholds['min_word_count']:
            issues.append(f"Low word count: {word_count} words")

        # Check for headings
        headings = self.extract_headings(content)
        if len(headings) < self.quality_thresholds['min_headings']:
            issues.append("Missing or insufficient headings")

        # Check for empty lines (readability)
        lines = content.split('\n')
        non_empty_lines = [line for line in lines if line.strip()]
        if len(lines) > 10 and len(non_empty_lines) / len(lines) > 0.9:
            issues.append("Dense text without paragraph breaks")

        # Check for very long lines
        long_lines = [i for i, line in enumerate(lines) if len(line) > 120]
        if len(long_lines) > len(lines) * 0.1:
            issues.append(f"Many long lines: {len(long_lines)} lines > 120 chars")

        # Check file age
        stat = file_path.stat()
        age_days = (datetime.now() - datetime.fromtimestamp(stat.st_mtime)).days
        if age_days > self.quality_thresholds['max_age_days']:
            issues.append(f"Outdated: {age_days} days old")

        return issues

    def calculate_quality_score(self, content: str, headings: List[str], issues: List[str]) -> float:
        """Calculate overall quality score (0.0 to 1.0)"""
        score = 1.0

        # Deduct for issues
        score -= len(issues) * 0.1

        # Bonus for good structure
        word_count = len(content.split())
        if word_count > 100:
            score += 0.1
        if len(headings) >= 3:
            score += 0.1

        # Bonus for code examples
        if '```' in content or '    ' in content:
            score += 0.05

        return max(0.0, min(1.0, score))

    def validate_links(self) -> None:
        """Validate all external links"""
        all_external_links = set()
        for doc in self.report.documents:
            all_external_links.update(doc.external_links)

        for link in all_external_links:
            try:
                # Simple HEAD request to check if link is accessible
                req = urllib.request.Request(link, method='HEAD')
                req.add_header('User-Agent', 'PdaNet-Docs-Auditor/1.0')
                urllib.request.urlopen(req, timeout=10)
            except Exception:
                self.report.broken_links.append(link)

    def validate_internal_references(self) -> None:
        """Validate internal links and image references"""
        all_files = {str(p.relative_to(self.project_root)) for p in self.discover_documents()}

        for doc in self.report.documents:
            doc_path = Path(doc.path)
            doc_dir = doc_path.parent

            # Check internal links
            for link in doc.internal_links:
                # Skip anchors and external links
                if link.startswith('#') or link.startswith(('http://', 'https://')):
                    continue

                # Resolve relative path
                if link.startswith('/'):
                    target_path = link[1:]
                else:
                    target_path = str(doc_dir / link)

                # Check if file exists
                full_path = self.project_root / target_path
                if not full_path.exists():
                    self.report.broken_links.append(f"{doc.path}: {link}")

            # Check image references
            for image in doc.images:
                if image.startswith(('http://', 'https://')):
                    continue

                if image.startswith('/'):
                    image_path = self.project_root / image[1:]
                else:
                    image_path = self.project_root / doc_dir / image

                if not image_path.exists():
                    self.report.missing_images.append(f"{doc.path}: {image}")

    def generate_recommendations(self) -> None:
        """Generate improvement recommendations"""
        recommendations = []

        # Quality issues
        low_quality_docs = [doc for doc in self.report.documents if doc.quality_score < 0.5]
        if low_quality_docs:
            recommendations.append(f"Improve quality of {len(low_quality_docs)} documents with low scores")

        # Broken links
        if self.report.broken_links:
            recommendations.append(f"Fix {len(self.report.broken_links)} broken links")

        # Missing images
        if self.report.missing_images:
            recommendations.append(f"Fix {len(self.report.missing_images)} missing image references")

        # TODOs and FIXMEs
        total_todos = sum(len(doc.todos) + len(doc.fixmes) for doc in self.report.documents)
        if total_todos > 0:
            recommendations.append(f"Address {total_todos} TODO and FIXME items")

        # Outdated files
        cutoff_date = datetime.now() - timedelta(days=self.quality_thresholds['max_age_days'])
        outdated_docs = []
        for doc in self.report.documents:
            if datetime.fromisoformat(doc.last_modified) < cutoff_date:
                outdated_docs.append(doc.path)
                self.report.outdated_files.append(doc.path)

        if outdated_docs:
            recommendations.append(f"Update {len(outdated_docs)} outdated documents")

        # Missing categories
        categories = defaultdict(int)
        for doc in self.report.documents:
            categories[doc.category] += 1

        essential_categories = ['readme', 'guide', 'api', 'architecture']
        missing_categories = [cat for cat in essential_categories if categories[cat] == 0]
        if missing_categories:
            recommendations.append(f"Add documentation for: {', '.join(missing_categories)}")

        self.report.recommendations = recommendations

    def run_audit(self) -> AuditReport:
        """Run complete documentation audit"""
        print("🔍 Discovering documentation files...")
        doc_files = self.discover_documents()
        self.report.total_files = len(doc_files)

        print(f"📊 Analyzing {len(doc_files)} documents...")
        for i, file_path in enumerate(doc_files, 1):
            print(f"  [{i}/{len(doc_files)}] {file_path.name}")
            doc_info = self.analyze_content(file_path)
            self.report.documents.append(doc_info)

            # Update totals
            self.report.total_words += doc_info.word_count
            self.report.total_size += doc_info.size

            # Collect TODOs and FIXMEs
            for todo in doc_info.todos:
                self.report.todos_fixmes.append(f"{doc_info.path}: TODO: {todo}")
            for fixme in doc_info.fixmes:
                self.report.todos_fixmes.append(f"{doc_info.path}: FIXME: {fixme}")

            # Collect quality issues
            for issue in doc_info.issues:
                self.report.quality_issues.append(f"{doc_info.path}: {issue}")

        # Calculate category statistics
        for doc in self.report.documents:
            self.report.categories[doc.category] = self.report.categories.get(doc.category, 0) + 1

        print("🔗 Validating internal references...")
        self.validate_internal_references()

        print("🌐 Validating external links...")
        self.validate_links()

        print("💡 Generating recommendations...")
        self.generate_recommendations()

        return self.report

    def save_report(self, output_path: str) -> None:
        """Save audit report to JSON file"""
        with open(output_path, 'w') as f:
            json.dump(asdict(self.report), f, indent=2, default=str)

    def print_summary(self) -> None:
        """Print audit summary to console"""
        print("\n" + "="*50)
        print("📋 DOCUMENTATION AUDIT SUMMARY")
        print("="*50)

        print(f"📁 Total files: {self.report.total_files}")
        print(f"📝 Total words: {self.report.total_words:,}")
        print(f"💾 Total size: {self.report.total_size / 1024:.1f} KB")

        print(f"\n📊 Categories:")
        for category, count in sorted(self.report.categories.items()):
            print(f"  • {category}: {count} files")

        print(f"\n⚠️  Issues Found:")
        print(f"  • Broken links: {len(self.report.broken_links)}")
        print(f"  • Missing images: {len(self.report.missing_images)}")
        print(f"  • Outdated files: {len(self.report.outdated_files)}")
        print(f"  • TODOs/FIXMEs: {len(self.report.todos_fixmes)}")
        print(f"  • Quality issues: {len(self.report.quality_issues)}")

        if self.report.recommendations:
            print(f"\n💡 Recommendations:")
            for i, rec in enumerate(self.report.recommendations, 1):
                print(f"  {i}. {rec}")

        avg_quality = sum(doc.quality_score for doc in self.report.documents) / len(self.report.documents)
        print(f"\n⭐ Average Quality Score: {avg_quality:.2f}/1.0")


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("Usage: python docs_auditor.py <project_root>")
        sys.exit(1)

    project_root = sys.argv[1]
    auditor = DocumentationAuditor(project_root)
    report = auditor.run_audit()

    # Save detailed report
    output_dir = Path(project_root) / "tools" / "docs-maintenance" / "reports"
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = output_dir / f"audit_report_{timestamp}.json"
    auditor.save_report(str(report_file))

    # Print summary
    auditor.print_summary()
    print(f"\n📄 Detailed report saved to: {report_file}")