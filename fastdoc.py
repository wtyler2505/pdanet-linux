#!/usr/bin/env python3
"""
FastDoc - Fast Documentation Generator
A simple tool to analyze and document Python codebases
"""

import os
import sys
import ast
import re
from pathlib import Path
from typing import Dict, List, Tuple, Any
import json

class FastDoc:
    """Fast documentation generator for Python projects"""
    
    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.modules = {}
        self.classes = {}
        self.functions = {}
        self.dependencies = set()
        
    def analyze_file(self, file_path: Path) -> Dict[str, Any]:
        """Analyze a Python file and extract documentation info"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            file_info = {
                'path': str(file_path),
                'docstring': ast.get_docstring(tree),
                'classes': [],
                'functions': [],
                'imports': [],
                'lines': len(content.splitlines())
            }
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    class_info = {
                        'name': node.name,
                        'docstring': ast.get_docstring(node),
                        'methods': [],
                        'line': node.lineno
                    }
                    
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef):
                            class_info['methods'].append({
                                'name': item.name,
                                'docstring': ast.get_docstring(item),
                                'line': item.lineno,
                                'args': [arg.arg for arg in item.args.args]
                            })
                    
                    file_info['classes'].append(class_info)
                
                elif isinstance(node, ast.FunctionDef) and not any(
                    isinstance(parent, ast.ClassDef) for parent in ast.walk(tree)
                    if hasattr(parent, 'body') and node in getattr(parent, 'body', [])
                ):
                    file_info['functions'].append({
                        'name': node.name,
                        'docstring': ast.get_docstring(node),
                        'line': node.lineno,
                        'args': [arg.arg for arg in node.args.args]
                    })
                
                elif isinstance(node, (ast.Import, ast.ImportFrom)):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            file_info['imports'].append(alias.name)
                            self.dependencies.add(alias.name)
                    else:
                        module = node.module or ''
                        for alias in node.names:
                            import_name = f"{module}.{alias.name}" if module else alias.name
                            file_info['imports'].append(import_name)
                            self.dependencies.add(module if module else alias.name)
            
            return file_info
            
        except Exception as e:
            return {
                'path': str(file_path),
                'error': str(e),
                'lines': 0
            }
    
    def scan_project(self) -> None:
        """Scan the entire project for Python files"""
        print(f"🔍 Scanning project: {self.project_path}")
        
        python_files = list(self.project_path.rglob("*.py"))
        print(f"📁 Found {len(python_files)} Python files")
        
        for file_path in python_files:
            if file_path.name.startswith('.') or 'test' in file_path.name.lower():
                continue
                
            relative_path = file_path.relative_to(self.project_path)
            print(f"📄 Analyzing: {relative_path}")
            
            file_info = self.analyze_file(file_path)
            self.modules[str(relative_path)] = file_info
    
    def generate_summary(self) -> Dict[str, Any]:
        """Generate project summary"""
        total_lines = sum(module.get('lines', 0) for module in self.modules.values())
        total_classes = sum(len(module.get('classes', [])) for module in self.modules.values())
        total_functions = sum(len(module.get('functions', [])) for module in self.modules.values())
        total_methods = sum(
            sum(len(cls.get('methods', [])) for cls in module.get('classes', []))
            for module in self.modules.values()
        )
        
        return {
            'project_path': str(self.project_path),
            'total_files': len(self.modules),
            'total_lines': total_lines,
            'total_classes': total_classes,
            'total_functions': total_functions,
            'total_methods': total_methods,
            'dependencies': sorted(list(self.dependencies))
        }
    
    def generate_markdown_docs(self) -> str:
        """Generate markdown documentation"""
        summary = self.generate_summary()
        
        md = f"""# {self.project_path.name} - Code Documentation

## Project Summary

- **Total Files**: {summary['total_files']}
- **Total Lines**: {summary['total_lines']:,}
- **Total Classes**: {summary['total_classes']}
- **Total Functions**: {summary['total_functions']}
- **Total Methods**: {summary['total_methods']}

## Dependencies

{chr(10).join(f"- `{dep}`" for dep in summary['dependencies'][:20])}
{f"... and {len(summary['dependencies']) - 20} more" if len(summary['dependencies']) > 20 else ""}

## Modules

"""
        
        for module_path, module_info in self.modules.items():
            if module_info.get('error'):
                continue
                
            md += f"\n### {module_path}\n\n"
            
            if module_info.get('docstring'):
                md += f"{module_info['docstring']}\n\n"
            
            md += f"**Lines**: {module_info.get('lines', 0)}\n\n"
            
            # Classes
            if module_info.get('classes'):
                md += "#### Classes\n\n"
                for cls in module_info['classes']:
                    md += f"##### `{cls['name']}`\n\n"
                    if cls.get('docstring'):
                        md += f"{cls['docstring']}\n\n"
                    
                    if cls.get('methods'):
                        md += "**Methods**:\n"
                        for method in cls['methods']:
                            args_str = ', '.join(method.get('args', []))
                            md += f"- `{method['name']}({args_str})`"
                            if method.get('docstring'):
                                md += f": {method['docstring'].split('.')[0]}."
                            md += "\n"
                        md += "\n"
            
            # Functions
            if module_info.get('functions'):
                md += "#### Functions\n\n"
                for func in module_info['functions']:
                    args_str = ', '.join(func.get('args', []))
                    md += f"##### `{func['name']}({args_str})`\n\n"
                    if func.get('docstring'):
                        md += f"{func['docstring']}\n\n"
        
        return md
    
    def search_code(self, pattern: str, case_sensitive: bool = False) -> List[Dict[str, Any]]:
        """Search for patterns in the codebase"""
        results = []
        flags = 0 if case_sensitive else re.IGNORECASE
        
        for module_path, module_info in self.modules.items():
            if module_info.get('error'):
                continue
                
            try:
                with open(self.project_path / module_path, 'r') as f:
                    lines = f.readlines()
                
                for i, line in enumerate(lines, 1):
                    if re.search(pattern, line, flags):
                        results.append({
                            'file': module_path,
                            'line': i,
                            'content': line.strip(),
                            'context': lines[max(0, i-2):i+1] if i > 1 else [line]
                        })
            except Exception:
                continue
        
        return results

def main():
    if len(sys.argv) < 2:
        print("Usage: fastdoc <project_path> [command] [args]")
        print("Commands:")
        print("  analyze    - Analyze project and generate summary")
        print("  docs       - Generate markdown documentation")
        print("  search <pattern> - Search for pattern in code")
        sys.exit(1)
    
    project_path = sys.argv[1]
    command = sys.argv[2] if len(sys.argv) > 2 else "analyze"
    
    if not os.path.exists(project_path):
        print(f"❌ Project path does not exist: {project_path}")
        sys.exit(1)
    
    fastdoc = FastDoc(project_path)
    fastdoc.scan_project()
    
    if command == "analyze":
        summary = fastdoc.generate_summary()
        print("\n" + "="*60)
        print("📊 PROJECT ANALYSIS SUMMARY")
        print("="*60)
        print(f"Project: {summary['project_path']}")
        print(f"Files: {summary['total_files']}")
        print(f"Lines: {summary['total_lines']:,}")
        print(f"Classes: {summary['total_classes']}")
        print(f"Functions: {summary['total_functions']}")
        print(f"Methods: {summary['total_methods']}")
        print(f"Dependencies: {len(summary['dependencies'])}")
        print("="*60)
        
    elif command == "docs":
        docs = fastdoc.generate_markdown_docs()
        output_file = Path(project_path) / "FASTDOC_ANALYSIS.md"
        with open(output_file, 'w') as f:
            f.write(docs)
        print(f"📝 Documentation generated: {output_file}")
        
    elif command == "search":
        if len(sys.argv) < 4:
            print("Usage: fastdoc <project_path> search <pattern>")
            sys.exit(1)
        
        pattern = sys.argv[3]
        results = fastdoc.search_code(pattern)
        
        print(f"\n🔍 Search results for '{pattern}':")
        print("="*60)
        
        for result in results[:20]:  # Limit to first 20 results
            print(f"📁 {result['file']}:{result['line']}")
            print(f"   {result['content']}")
            print()
        
        if len(results) > 20:
            print(f"... and {len(results) - 20} more results")
        
        print(f"Total matches: {len(results)}")

if __name__ == "__main__":
    main()