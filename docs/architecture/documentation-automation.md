# Architecture Documentation Automation

**Version:** 1.0
**Date:** 2025-10-04
**Purpose:** Automate generation, validation, and maintenance of architecture documentation

## Overview

This document describes the automation setup for maintaining PdaNet Linux architecture documentation, including diagram generation, validation pipelines, and documentation-as-code workflows.

## Table of Contents

1. [Automation Architecture](#automation-architecture)
2. [Diagram Generation](#diagram-generation)
3. [Documentation Pipeline](#documentation-pipeline)
4. [Validation and Quality Assurance](#validation-and-quality-assurance)
5. [Integration with Development Workflow](#integration-with-development-workflow)
6. [Maintenance and Updates](#maintenance-and-updates)

---

## Automation Architecture

### Components

```
┌─────────────────────────────────────────────────────────────┐
│                Documentation Automation                     │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐ │
│  │   PlantUML      │  │   Arc42 Gen     │  │  ADR Tools  │ │
│  │   Generator     │  │                 │  │             │ │
│  └─────────────────┘  └─────────────────┘  └─────────────┘ │
│                                                             │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐ │
│  │   Validation    │  │   Publishing    │  │  Metrics    │ │
│  │   Pipeline      │  │   Pipeline      │  │  Tracking   │ │
│  └─────────────────┘  └─────────────────┘  └─────────────┘ │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Tools and Technologies

| Tool | Purpose | Configuration |
|------|---------|---------------|
| **PlantUML** | Diagram generation from text | Local JAR + online server |
| **pandoc** | Document format conversion | Markdown to HTML/PDF |
| **git hooks** | Automatic validation on commit | Pre-commit and pre-push |
| **Make** | Build orchestration | Makefile for common tasks |
| **Python scripts** | Custom automation logic | Validation and metrics |

---

## Diagram Generation

### PlantUML Setup

Create automated diagram generation pipeline:

```bash
#!/bin/bash
# scripts/generate-diagrams.sh

set -euo pipefail

DOCS_DIR="docs/architecture"
PUML_FILES="$DOCS_DIR/*.puml"
OUTPUT_DIR="$DOCS_DIR/generated"

# Create output directory
mkdir -p "$OUTPUT_DIR"

echo "Generating architecture diagrams..."

# Download PlantUML if not present
if [[ ! -f "tools/plantuml.jar" ]]; then
    echo "Downloading PlantUML..."
    mkdir -p tools
    wget -O tools/plantuml.jar "https://github.com/plantuml/plantuml/releases/latest/download/plantuml.jar"
fi

# Generate diagrams
for puml_file in $PUML_FILES; do
    if [[ -f "$puml_file" ]]; then
        filename=$(basename "$puml_file" .puml)
        echo "  Generating $filename..."

        # Generate PNG for web display
        java -jar tools/plantuml.jar -tpng -o "$(realpath $OUTPUT_DIR)" "$puml_file"

        # Generate SVG for high-quality print
        java -jar tools/plantuml.jar -tsvg -o "$(realpath $OUTPUT_DIR)" "$puml_file"

        # Generate text for accessibility
        java -jar tools/plantuml.jar -ttxt -o "$(realpath $OUTPUT_DIR)" "$puml_file"
    fi
done

echo "Diagram generation complete. Output in: $OUTPUT_DIR"
```

### Makefile Integration

```make
# Makefile
.PHONY: docs diagrams validate-docs publish-docs clean-docs

# Generate all documentation
docs: diagrams
	@echo "Building complete documentation..."
	@./scripts/generate-diagrams.sh
	@./scripts/build-docs.sh

# Generate diagrams only
diagrams:
	@echo "Generating architecture diagrams..."
	@./scripts/generate-diagrams.sh

# Validate documentation
validate-docs:
	@echo "Validating documentation..."
	@./scripts/validate-docs.py
	@./scripts/check-links.py

# Publish documentation
publish-docs: docs validate-docs
	@echo "Publishing documentation..."
	@./scripts/publish-docs.sh

# Clean generated files
clean-docs:
	@echo "Cleaning generated documentation..."
	@rm -rf docs/architecture/generated/
	@rm -rf docs/build/
```

### Automated Diagram Updates

```python
#!/usr/bin/env python3
# scripts/update-diagrams.py

import os
import subprocess
import hashlib
from pathlib import Path

class DiagramUpdater:
    def __init__(self, docs_dir="docs/architecture"):
        self.docs_dir = Path(docs_dir)
        self.cache_file = self.docs_dir / ".diagram_cache"

    def get_file_hash(self, filepath):
        """Calculate SHA256 hash of file content"""
        with open(filepath, 'rb') as f:
            return hashlib.sha256(f.read()).hexdigest()

    def load_cache(self):
        """Load previous diagram hashes"""
        if self.cache_file.exists():
            cache = {}
            with open(self.cache_file, 'r') as f:
                for line in f:
                    filename, hash_value = line.strip().split(':')
                    cache[filename] = hash_value
            return cache
        return {}

    def save_cache(self, cache):
        """Save current diagram hashes"""
        with open(self.cache_file, 'w') as f:
            for filename, hash_value in cache.items():
                f.write(f"{filename}:{hash_value}\n")

    def update_changed_diagrams(self):
        """Update only diagrams that have changed"""
        cache = self.load_cache()
        current_hashes = {}
        changed_files = []

        # Check all .puml files
        for puml_file in self.docs_dir.glob("*.puml"):
            current_hash = self.get_file_hash(puml_file)
            current_hashes[puml_file.name] = current_hash

            if puml_file.name not in cache or cache[puml_file.name] != current_hash:
                changed_files.append(puml_file)

        if changed_files:
            print(f"Updating {len(changed_files)} changed diagrams...")
            for puml_file in changed_files:
                self.generate_diagram(puml_file)
        else:
            print("No diagram changes detected.")

        self.save_cache(current_hashes)

    def generate_diagram(self, puml_file):
        """Generate diagram for a single file"""
        print(f"  Generating {puml_file.name}...")
        output_dir = self.docs_dir / "generated"
        output_dir.mkdir(exist_ok=True)

        subprocess.run([
            "java", "-jar", "tools/plantuml.jar",
            "-tpng", "-tsvg",
            "-o", str(output_dir.absolute()),
            str(puml_file)
        ], check=True)

if __name__ == "__main__":
    updater = DiagramUpdater()
    updater.update_changed_diagrams()
```

---

## Documentation Pipeline

### Build Pipeline

```bash
#!/bin/bash
# scripts/build-docs.sh

set -euo pipefail

DOCS_DIR="docs"
BUILD_DIR="$DOCS_DIR/build"
ARCHITECTURE_DIR="$DOCS_DIR/architecture"

echo "Building PdaNet Linux documentation..."

# Clean and create build directory
rm -rf "$BUILD_DIR"
mkdir -p "$BUILD_DIR"

# Copy static assets
cp -r "$ARCHITECTURE_DIR/generated" "$BUILD_DIR/diagrams" 2>/dev/null || true

# Build main architecture document
echo "Building Arc42 architecture document..."
pandoc \
    --from markdown \
    --to html \
    --standalone \
    --toc \
    --toc-depth=3 \
    --css=styles/architecture.css \
    --metadata title="PdaNet Linux Architecture" \
    --output "$BUILD_DIR/architecture.html" \
    "$ARCHITECTURE_DIR/arc42-architecture.md"

# Build security documentation
echo "Building security architecture..."
pandoc \
    --from markdown \
    --to html \
    --standalone \
    --toc \
    --css=styles/security.css \
    --metadata title="PdaNet Linux Security Architecture" \
    --output "$BUILD_DIR/security.html" \
    "$ARCHITECTURE_DIR/security-architecture.md"

# Build ADR index
echo "Building ADR index..."
python3 scripts/build-adr-index.py "$ARCHITECTURE_DIR/adrs" "$BUILD_DIR"

# Generate documentation metrics
echo "Generating documentation metrics..."
python3 scripts/doc-metrics.py "$DOCS_DIR" "$BUILD_DIR/metrics.json"

echo "Documentation build complete. Output in: $BUILD_DIR"
```

### ADR Index Generation

```python
#!/usr/bin/env python3
# scripts/build-adr-index.py

import os
import re
import json
from pathlib import Path
from datetime import datetime

def parse_adr(adr_file):
    """Parse ADR file and extract metadata"""
    with open(adr_file, 'r') as f:
        content = f.read()

    # Extract title
    title_match = re.search(r'^# (.+)', content, re.MULTILINE)
    title = title_match.group(1) if title_match else adr_file.name

    # Extract metadata
    status_match = re.search(r'\*\*Status:\*\* (.+)', content)
    status = status_match.group(1) if status_match else "Unknown"

    date_match = re.search(r'\*\*Date:\*\* (.+)', content)
    date = date_match.group(1) if date_match else "Unknown"

    # Extract summary (first paragraph after metadata)
    summary_match = re.search(r'## Context\n\n(.+?)\n\n', content, re.DOTALL)
    summary = summary_match.group(1).strip() if summary_match else ""

    return {
        'title': title,
        'status': status,
        'date': date,
        'summary': summary,
        'filename': adr_file.name
    }

def build_adr_index(adrs_dir, output_dir):
    """Build HTML index of all ADRs"""
    adrs_path = Path(adrs_dir)
    output_path = Path(output_dir)

    adrs = []
    for adr_file in adrs_path.glob("ADR-*.md"):
        adrs.append(parse_adr(adr_file))

    # Sort by filename (ADR number)
    adrs.sort(key=lambda x: x['filename'])

    # Generate HTML
    html_template = """
<!DOCTYPE html>
<html>
<head>
    <title>Architecture Decision Records</title>
    <link rel="stylesheet" href="styles/adr.css">
</head>
<body>
    <h1>Architecture Decision Records</h1>
    <p>This page lists all architectural decisions made for PdaNet Linux.</p>

    <table class="adr-table">
        <thead>
            <tr>
                <th>ADR</th>
                <th>Title</th>
                <th>Status</th>
                <th>Date</th>
                <th>Summary</th>
            </tr>
        </thead>
        <tbody>
            {adr_rows}
        </tbody>
    </table>

    <footer>
        <p>Generated on {timestamp}</p>
    </footer>
</body>
</html>
    """

    adr_rows = []
    for adr in adrs:
        row = f"""
            <tr class="status-{adr['status'].lower()}">
                <td><a href="adrs/{adr['filename']}">{adr['filename']}</a></td>
                <td>{adr['title']}</td>
                <td>{adr['status']}</td>
                <td>{adr['date']}</td>
                <td>{adr['summary']}</td>
            </tr>
        """
        adr_rows.append(row)

    html_content = html_template.format(
        adr_rows='\n'.join(adr_rows),
        timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    )

    # Write HTML file
    with open(output_path / "adrs.html", 'w') as f:
        f.write(html_content)

    # Copy ADR files
    adr_output_dir = output_path / "adrs"
    adr_output_dir.mkdir(exist_ok=True)

    for adr_file in adrs_path.glob("ADR-*.md"):
        # Convert to HTML
        os.system(f"pandoc --from markdown --to html --standalone "
                 f"--output '{adr_output_dir / adr_file.stem}.html' '{adr_file}'")

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print("Usage: build-adr-index.py <adrs_dir> <output_dir>")
        sys.exit(1)

    build_adr_index(sys.argv[1], sys.argv[2])
```

---

## Validation and Quality Assurance

### Documentation Validation Script

```python
#!/usr/bin/env python3
# scripts/validate-docs.py

import os
import re
import sys
from pathlib import Path

class DocumentationValidator:
    def __init__(self, docs_dir="docs"):
        self.docs_dir = Path(docs_dir)
        self.errors = []
        self.warnings = []

    def validate_all(self):
        """Run all validation checks"""
        print("Validating PdaNet Linux documentation...")

        self.check_file_structure()
        self.check_markdown_syntax()
        self.check_internal_links()
        self.check_diagram_references()
        self.check_adr_format()
        self.check_arc42_completeness()

        self.report_results()
        return len(self.errors) == 0

    def check_file_structure(self):
        """Validate expected file structure exists"""
        required_files = [
            "architecture/arc42-architecture.md",
            "architecture/security-architecture.md",
            "architecture/c4-context.puml",
            "architecture/c4-container.puml",
            "architecture/c4-component.puml",
            "architecture/c4-deployment.puml",
            "architecture/adrs/ADR-001-python-gtk3-gui.md",
            "architecture/adrs/ADR-002-carrier-bypass-strategy.md"
        ]

        for required_file in required_files:
            file_path = self.docs_dir / required_file
            if not file_path.exists():
                self.errors.append(f"Missing required file: {required_file}")

    def check_markdown_syntax(self):
        """Check markdown files for syntax issues"""
        for md_file in self.docs_dir.rglob("*.md"):
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Check for common markdown issues
            lines = content.split('\n')
            for i, line in enumerate(lines, 1):
                # Check for unmatched brackets
                if line.count('[') != line.count(']'):
                    self.warnings.append(f"{md_file}:{i} - Unmatched brackets")

                # Check for empty headers
                if re.match(r'^#+\s*$', line):
                    self.errors.append(f"{md_file}:{i} - Empty header")

                # Check for inconsistent header levels
                header_match = re.match(r'^(#+)', line)
                if header_match and len(header_match.group(1)) > 6:
                    self.warnings.append(f"{md_file}:{i} - Header level too deep")

    def check_internal_links(self):
        """Validate internal links point to existing files"""
        for md_file in self.docs_dir.rglob("*.md"):
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Find internal links
            internal_links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', content)
            for link_text, link_target in internal_links:
                if not link_target.startswith('http'):
                    # Resolve relative path
                    target_path = (md_file.parent / link_target).resolve()
                    if not target_path.exists():
                        self.errors.append(f"{md_file} - Broken internal link: {link_target}")

    def check_diagram_references(self):
        """Check that referenced diagrams exist"""
        for md_file in self.docs_dir.rglob("*.md"):
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Find diagram references
            diagram_refs = re.findall(r'!\[.*?\]\((.+\.puml)\)', content)
            for diagram_ref in diagram_refs:
                diagram_path = (md_file.parent / diagram_ref).resolve()
                if not diagram_path.exists():
                    self.errors.append(f"{md_file} - Missing diagram: {diagram_ref}")

    def check_adr_format(self):
        """Validate ADR files follow template"""
        adr_dir = self.docs_dir / "architecture" / "adrs"
        if not adr_dir.exists():
            return

        required_sections = [
            "## Context",
            "## Decision",
            "## Rationale",
            "## Alternatives Considered",
            "## Consequences"
        ]

        for adr_file in adr_dir.glob("ADR-*.md"):
            with open(adr_file, 'r', encoding='utf-8') as f:
                content = f.read()

            for section in required_sections:
                if section not in content:
                    self.warnings.append(f"{adr_file.name} - Missing section: {section}")

            # Check for metadata
            if "**Status:**" not in content:
                self.errors.append(f"{adr_file.name} - Missing status metadata")

            if "**Date:**" not in content:
                self.errors.append(f"{adr_file.name} - Missing date metadata")

    def check_arc42_completeness(self):
        """Check Arc42 document has all required sections"""
        arc42_file = self.docs_dir / "architecture" / "arc42-architecture.md"
        if not arc42_file.exists():
            return

        required_sections = [
            "1. Introduction and Goals",
            "2. Architecture Constraints",
            "3. System Context and Scope",
            "4. Solution Strategy",
            "5. Building Block View",
            "6. Runtime View",
            "7. Deployment View",
            "8. Cross-cutting Concepts",
            "9. Architecture Decisions",
            "10. Quality Requirements",
            "11. Risks and Technical Debt",
            "12. Glossary"
        ]

        with open(arc42_file, 'r', encoding='utf-8') as f:
            content = f.read()

        for section in required_sections:
            if f"## {section}" not in content:
                self.warnings.append(f"Arc42 document missing section: {section}")

    def report_results(self):
        """Report validation results"""
        print(f"\nValidation Results:")
        print(f"  Errors: {len(self.errors)}")
        print(f"  Warnings: {len(self.warnings)}")

        if self.errors:
            print("\nERRORS:")
            for error in self.errors:
                print(f"  ❌ {error}")

        if self.warnings:
            print("\nWARNINGS:")
            for warning in self.warnings:
                print(f"  ⚠️  {warning}")

        if not self.errors and not self.warnings:
            print("  ✅ All validations passed!")

if __name__ == "__main__":
    validator = DocumentationValidator()
    success = validator.validate_all()
    sys.exit(0 if success else 1)
```

### Git Hooks Integration

```bash
#!/bin/bash
# .git/hooks/pre-commit

echo "Running documentation validation..."

# Check if any documentation files changed
if git diff --cached --name-only | grep -E '\.(md|puml)$' > /dev/null; then
    echo "Documentation changes detected, running validation..."

    # Run diagram generation for changed PlantUML files
    if git diff --cached --name-only | grep '\.puml$' > /dev/null; then
        python3 scripts/update-diagrams.py
        git add docs/architecture/generated/
    fi

    # Run documentation validation
    if ! python3 scripts/validate-docs.py; then
        echo "Documentation validation failed. Commit aborted."
        exit 1
    fi

    echo "Documentation validation passed."
fi

# Continue with normal pre-commit checks
```

---

## Integration with Development Workflow

### CI/CD Integration

```yaml
# .github/workflows/documentation.yml
name: Documentation

on:
  push:
    paths:
      - 'docs/**'
      - 'scripts/**'
  pull_request:
    paths:
      - 'docs/**'

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'

      - name: Install dependencies
        run: |
          sudo apt-get update
          sudo apt-get install -y pandoc default-jre
          pip install -r scripts/requirements.txt

      - name: Validate documentation
        run: |
          make validate-docs

      - name: Build documentation
        run: |
          make docs

      - name: Upload documentation artifacts
        uses: actions/upload-artifact@v3
        with:
          name: documentation
          path: docs/build/

  publish:
    needs: validate
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v3

      - name: Build and publish docs
        run: |
          make publish-docs
```

### Development Scripts

```bash
#!/bin/bash
# scripts/dev-docs.sh
# Development helper for documentation workflow

set -euo pipefail

case "${1:-help}" in
    "watch")
        echo "Watching for documentation changes..."
        find docs/ -name "*.md" -o -name "*.puml" | entr make diagrams
        ;;

    "serve")
        echo "Starting documentation server..."
        make docs
        cd docs/build
        python3 -m http.server 8080
        ;;

    "new-adr")
        if [[ -z "${2:-}" ]]; then
            echo "Usage: $0 new-adr <title>"
            exit 1
        fi
        ./scripts/new-adr.sh "$2"
        ;;

    "metrics")
        echo "Generating documentation metrics..."
        python3 scripts/doc-metrics.py docs docs/build/metrics.json
        cat docs/build/metrics.json | jq '.'
        ;;

    "help")
        echo "Documentation development commands:"
        echo "  watch    - Watch for changes and regenerate diagrams"
        echo "  serve    - Build docs and serve on localhost:8080"
        echo "  new-adr  - Create new ADR from template"
        echo "  metrics  - Show documentation metrics"
        ;;

    *)
        echo "Unknown command: $1"
        echo "Run '$0 help' for available commands"
        exit 1
        ;;
esac
```

---

## Maintenance and Updates

### Automated Updates

```python
#!/usr/bin/env python3
# scripts/update-architecture.py

import subprocess
import json
from datetime import datetime
from pathlib import Path

class ArchitectureUpdater:
    def __init__(self):
        self.docs_dir = Path("docs/architecture")
        self.metrics_file = Path("docs/build/metrics.json")

    def check_for_updates(self):
        """Check if architecture documentation needs updates"""
        updates_needed = []

        # Check if code changes require documentation updates
        if self.code_changed_since_last_doc_update():
            updates_needed.append("Code changes detected")

        # Check if ADRs need review
        outdated_adrs = self.find_outdated_adrs()
        if outdated_adrs:
            updates_needed.append(f"{len(outdated_adrs)} ADRs need review")

        # Check if diagrams are outdated
        if self.diagrams_outdated():
            updates_needed.append("Diagrams may be outdated")

        return updates_needed

    def code_changed_since_last_doc_update(self):
        """Check if source code changed since last doc update"""
        try:
            # Get last commit that touched documentation
            doc_commit = subprocess.check_output([
                "git", "log", "-1", "--format=%H", "--", "docs/"
            ]).decode().strip()

            # Get last commit that touched source code
            code_commit = subprocess.check_output([
                "git", "log", "-1", "--format=%H", "--", "src/"
            ]).decode().strip()

            # Check if code is newer than docs
            doc_time = subprocess.check_output([
                "git", "show", "-s", "--format=%ct", doc_commit
            ]).decode().strip()

            code_time = subprocess.check_output([
                "git", "show", "-s", "--format=%ct", code_commit
            ]).decode().strip()

            return int(code_time) > int(doc_time)

        except subprocess.CalledProcessError:
            return False

    def find_outdated_adrs(self):
        """Find ADRs that haven't been reviewed recently"""
        outdated = []
        adr_dir = self.docs_dir / "adrs"

        for adr_file in adr_dir.glob("ADR-*.md"):
            # Get last modification time
            mtime = adr_file.stat().st_mtime
            age_days = (datetime.now().timestamp() - mtime) / 86400

            # ADRs should be reviewed every 6 months
            if age_days > 180:
                outdated.append(adr_file)

        return outdated

    def diagrams_outdated(self):
        """Check if diagrams might be outdated based on metrics"""
        if not self.metrics_file.exists():
            return True

        with open(self.metrics_file) as f:
            metrics = json.load(f)

        # Check if there are new components not in diagrams
        return metrics.get('components_without_diagrams', 0) > 0

    def generate_update_report(self):
        """Generate report of needed updates"""
        updates = self.check_for_updates()

        report = {
            'timestamp': datetime.now().isoformat(),
            'updates_needed': updates,
            'status': 'needs_attention' if updates else 'up_to_date'
        }

        # Save report
        with open('docs/build/update_report.json', 'w') as f:
            json.dump(report, f, indent=2)

        return report

if __name__ == "__main__":
    updater = ArchitectureUpdater()
    report = updater.generate_update_report()

    print(f"Architecture Update Status: {report['status']}")
    if report['updates_needed']:
        print("Updates needed:")
        for update in report['updates_needed']:
            print(f"  - {update}")
    else:
        print("Documentation is up to date.")
```

### Scheduled Maintenance

```bash
#!/bin/bash
# scripts/weekly-maintenance.sh
# Run weekly documentation maintenance tasks

echo "Running weekly documentation maintenance..."

# Update diagrams
echo "Updating diagrams..."
python3 scripts/update-diagrams.py

# Check for outdated content
echo "Checking for outdated content..."
python3 scripts/update-architecture.py

# Validate all documentation
echo "Validating documentation..."
python3 scripts/validate-docs.py

# Generate fresh metrics
echo "Generating metrics..."
python3 scripts/doc-metrics.py docs docs/build/metrics.json

# Commit any automated updates
if git diff --quiet; then
    echo "No changes to commit."
else
    echo "Committing automated updates..."
    git add docs/
    git commit -m "Automated documentation maintenance $(date +%Y-%m-%d)"
fi

echo "Weekly maintenance complete."
```

---

This completes the comprehensive architecture documentation automation setup for PdaNet Linux, providing:

1. **Automated diagram generation** from PlantUML source files
2. **Documentation validation** pipeline with quality checks
3. **Build and publishing** automation for multiple output formats
4. **Integration with development workflow** through git hooks and CI/CD
5. **Maintenance automation** for keeping documentation current
6. **Metrics and reporting** for documentation health monitoring

The system ensures that architecture documentation stays synchronized with code changes and maintains high quality standards through automated validation and review processes.