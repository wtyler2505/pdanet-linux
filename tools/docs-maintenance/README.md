# Documentation Maintenance & Quality Assurance

Comprehensive documentation maintenance framework for PdaNet Linux with automated quality assurance, validation, and synchronization capabilities.

## Overview

This framework provides systematic documentation maintenance through:

- **Content Quality Audit**: File discovery, freshness analysis, and completeness assessment
- **Link Validation**: External and internal link health monitoring with retry logic
- **Style Consistency**: Markdown syntax validation and formatting standards
- **Content Optimization**: TOC generation, metadata updates, and readability improvement
- **Synchronization**: Git-based change tracking and version control integration
- **Automated Reporting**: Comprehensive audit reports with actionable insights

## Tools

### 1. Documentation Auditor (`docs_auditor.py`)

Comprehensive documentation analysis and quality assessment.

**Features:**
- Document discovery and categorization
- Content analysis (word count, headings, structure)
- Link and image reference extraction
- TODO/FIXME tracking
- Quality scoring algorithm
- Detailed audit reports

**Usage:**
```bash
python3 docs_auditor.py /path/to/project
```

**Output:**
- Console summary with key metrics
- JSON report: `reports/audit_report_YYYYMMDD_HHMMSS.json`

### 2. Link Validator (`link_validator.py`)

Advanced link validation with async processing and detailed reporting.

**Features:**
- Internal and external link validation
- Async processing for performance
- Retry logic with timeout handling
- Redirect detection and reporting
- Broken link identification
- Context-aware error reporting

**Usage:**
```bash
python3 link_validator.py /path/to/project
```

**Dependencies:**
```bash
pip install aiohttp
```

**Output:**
- Validation summary with success rates
- JSON report: `reports/link_validation_YYYYMMDD_HHMMSS.json`

### 3. Style Checker (`style_checker.py`)

Documentation style and consistency validation.

**Features:**
- Markdown syntax validation
- Heading hierarchy checking
- Line length enforcement
- Spelling validation with project dictionary
- Emphasis and formatting consistency
- Alt text validation for images
- Table formatting checks

**Usage:**
```bash
python3 style_checker.py /path/to/project
```

**Dependencies:**
```bash
pip install pyspellchecker
```

**Output:**
- Style issues categorized by severity
- JSON report: `reports/style_check_YYYYMMDD_HHMMSS.json`

### 4. Maintenance Orchestrator (`maintenance_orchestrator.py`)

Central system for running all maintenance tasks with dependency management.

**Features:**
- Task dependency resolution
- Async task execution
- Timeout and error handling
- Configurable task scheduling
- Comprehensive reporting
- Performance monitoring

**Usage:**
```bash
# Run all enabled tasks
python3 maintenance_orchestrator.py /path/to/project

# Run specific tasks
python3 maintenance_orchestrator.py /path/to/project --tasks audit link_validation

# Force run all tasks (including disabled)
python3 maintenance_orchestrator.py /path/to/project --force-all
```

**Configuration:**
Tasks are configured in `maintenance_config.json`:
```json
{
  "tasks": [
    {
      "name": "audit",
      "description": "Comprehensive documentation audit",
      "script": "docs_auditor.py",
      "enabled": true,
      "frequency": "weekly",
      "dependencies": [],
      "timeout": 300,
      "critical": true
    }
  ]
}
```

### 5. Synchronization Manager (`sync_manager.py`)

Git-based documentation synchronization and version control integration.

**Features:**
- Git repository status monitoring
- Documentation change tracking
- Outdated file identification
- Commit and sync operations
- Merge conflict detection
- Remote synchronization

**Usage:**
```bash
python3 sync_manager.py /path/to/project
```

**Output:**
- Git status and sync recommendations
- JSON report: `reports/sync_report_YYYYMMDD_HHMMSS.json`

## Installation

### Prerequisites

1. **Python 3.8+** with pip
2. **Git** (for synchronization features)
3. **Required packages:**

```bash
# Core dependencies
pip install aiohttp pyspellchecker

# Optional for enhanced features
pip install markdown beautifulsoup4 requests
```

### Setup

1. **Create tools directory:**
```bash
mkdir -p tools/docs-maintenance/reports
```

2. **Download tools:**
```bash
# Copy all .py files to tools/docs-maintenance/
```

3. **Make scripts executable:**
```bash
chmod +x tools/docs-maintenance/*.py
```

4. **Test installation:**
```bash
cd tools/docs-maintenance
python3 docs_auditor.py ../../
```

## Configuration

### Quality Thresholds

Edit the quality thresholds in each tool:

**`docs_auditor.py`:**
```python
self.quality_thresholds = {
    'min_word_count': 50,
    'max_age_days': 90,
    'min_headings': 1,
    'max_broken_links': 0,
    'readability_score': 0.7
}
```

**`style_checker.py`:**
```python
self.rules = {
    'max_line_length': 120,
    'require_title': True,
    'heading_style': 'atx',
    'list_style': 'consistent',
    'emphasis_style': 'asterisk',
    'code_fence_style': 'backticks',
    'require_alt_text': True,
    'max_heading_level': 4,
    'check_spelling': True
}
```

### Project Dictionary

Add project-specific terms to avoid false spelling errors:

**`style_checker.py`:**
```python
self.project_terms = {
    'pdanet', 'linux', 'wifi', 'usb', 'tethering',
    'cyberpunk', 'gui', 'gtk', 'android', 'redsocks',
    # Add your project terms here
}
```

## Automation

### Scheduled Maintenance

Create a cron job for regular maintenance:

```bash
# Run daily at 2 AM
0 2 * * * cd /path/to/project/tools/docs-maintenance && python3 maintenance_orchestrator.py /path/to/project

# Run weekly comprehensive audit
0 3 * * 0 cd /path/to/project/tools/docs-maintenance && python3 maintenance_orchestrator.py /path/to/project --force-all
```

### Git Hooks

Integrate with git hooks for automatic validation:

**`.git/hooks/pre-commit`:**
```bash
#!/bin/bash
# Run style check on documentation files
cd tools/docs-maintenance
python3 style_checker.py ../../ --exit-code
```

### CI/CD Integration

Add to your CI pipeline:

```yaml
# .github/workflows/docs-maintenance.yml
name: Documentation Maintenance
on: [push, pull_request]

jobs:
  docs-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: pip install aiohttp pyspellchecker
      - name: Run documentation maintenance
        run: |
          cd tools/docs-maintenance
          python3 maintenance_orchestrator.py ../../ --tasks audit style_check link_validation
```

## Reports

All tools generate detailed JSON reports in the `reports/` directory:

### Report Structure

```json
{
  "timestamp": "2025-01-15T10:30:00",
  "total_files": 85,
  "summary": {
    "success_rate": 0.95,
    "critical_issues": 2
  },
  "recommendations": [
    "Fix 3 broken links",
    "Update 5 outdated files"
  ],
  "details": {
    // Tool-specific detailed results
  }
}
```

### Report Analysis

Use the reports for:

1. **Quality Tracking**: Monitor documentation health over time
2. **Issue Prioritization**: Focus on critical and high-impact issues
3. **Team Metrics**: Track improvement and maintenance velocity
4. **Compliance**: Ensure documentation standards are met

## Best Practices

### 1. Regular Maintenance Schedule

- **Daily**: Link validation, sync check
- **Weekly**: Style check, content audit
- **Monthly**: Comprehensive review, optimization

### 2. Quality Gates

Set quality thresholds as gates for:
- Pull request approval
- Release preparation
- Documentation publication

### 3. Team Integration

- Include documentation maintenance in sprint planning
- Assign ownership for different documentation categories
- Review maintenance reports in team meetings

### 4. Continuous Improvement

- Adjust quality thresholds based on project needs
- Add project-specific validation rules
- Extend tools for custom requirements

## Troubleshooting

### Common Issues

**1. Permission Errors**
```bash
# Ensure proper file permissions
chmod +x tools/docs-maintenance/*.py
```

**2. Missing Dependencies**
```bash
# Install required packages
pip install aiohttp pyspellchecker
```

**3. Git Repository Not Found**
```bash
# Initialize git repository
git init
```

**4. Network Timeouts**
```bash
# Increase timeout in link_validator.py
timeout = 30.0  # seconds
```

### Performance Optimization

**For Large Documentation Sets:**

1. **Increase async limits:**
```python
# In link_validator.py
max_concurrent = 20
```

2. **Use report caching:**
```python
# Cache results between runs
enable_caching = True
```

3. **Filter file patterns:**
```python
# Focus on specific file types
doc_patterns = ['*.md']  # Only markdown
```

## Contributing

To extend the documentation maintenance framework:

1. **Add new validation rules** to existing tools
2. **Create new specialized tools** following the same patterns
3. **Enhance reporting** with additional metrics
4. **Improve automation** with better scheduling

### Tool Development Template

```python
#!/usr/bin/env python3
"""
New Documentation Tool
Description of functionality
"""

from pathlib import Path
from datetime import datetime
from dataclasses import dataclass
import json

@dataclass
class ToolReport:
    timestamp: str
    # Add tool-specific fields

class NewDocumentationTool:
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)

    def run_analysis(self) -> ToolReport:
        # Implement tool logic
        pass

    def save_report(self, report: ToolReport, output_path: str):
        with open(output_path, 'w') as f:
            json.dump(asdict(report), f, indent=2)

if __name__ == "__main__":
    # CLI interface
    pass
```

## License

This documentation maintenance framework is part of the PdaNet Linux project and follows the same license terms.