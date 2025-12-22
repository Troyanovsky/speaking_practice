#!/usr/bin/env python3
"""
Comprehensive linting analysis script.
Shows function lengths, file lengths, and other metrics.
"""

import ast
import os
from pathlib import Path
from typing import Any, Dict, List


class FunctionLengthVisitor(ast.NodeVisitor):
    """AST visitor to analyze function lengths."""

    def __init__(self, max_length: int = 50):
        self.max_length = max_length
        self.violations: List[Dict[str, Any]] = []
        self.current_file = ""

    def visit_FunctionDef(self, node):
        start_line = node.lineno
        end_line = (
            node.end_lineno
            if hasattr(node, "end_lineno") and node.end_lineno
            else start_line
        )
        length = end_line - start_line + 1

        if length > self.max_length:
            self.violations.append(
                {
                    "file": self.current_file,
                    "function": node.name,
                    "line": start_line,
                    "length": length,
                    "type": "FunctionDef",
                }
            )

        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node):
        start_line = node.lineno
        end_line = (
            node.end_lineno
            if hasattr(node, "end_lineno") and node.end_lineno
            else start_line
        )
        length = end_line - start_line + 1

        if length > self.max_length:
            self.violations.append(
                {
                    "file": self.current_file,
                    "function": node.name,
                    "line": start_line,
                    "length": length,
                    "type": "AsyncFunctionDef",
                }
            )

        self.generic_visit(node)


def analyze_file_lengths(
    app_dir: Path, max_file_length: int = 300
) -> List[Dict[str, Any]]:
    """Analyze file lengths."""
    violations = []

    for py_file in app_dir.rglob("*.py"):
        if py_file.name.startswith("__") and py_file.stat().st_size < 100:
            continue

        with open(py_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
            line_count = len(lines)

            if line_count > max_file_length:
                violations.append(
                    {
                        "file": str(py_file.relative_to(app_dir)),
                        "length": line_count,
                        "max_allowed": max_file_length,
                    }
                )

    return violations


def analyze_function_lengths(
    app_dir: Path, max_function_length: int = 50
) -> List[Dict[str, Any]]:
    """Analyze function lengths using AST."""
    visitor = FunctionLengthVisitor(max_function_length)
    violations = []

    for py_file in app_dir.rglob("*.py"):
        if py_file.name.startswith("__"):
            continue

        try:
            with open(py_file, "r", encoding="utf-8") as f:
                content = f.read()
                if not content.strip():
                    continue

                tree = ast.parse(content)
                visitor.current_file = str(py_file.relative_to(app_dir))
                visitor.visit(tree)
                violations.extend(visitor.violations)
                visitor.violations.clear()
        except (SyntaxError, UnicodeDecodeError):
            continue

    return violations


def main():
    """Main analysis function."""
    app_dir = Path("app")

    if not app_dir.exists():
        print("Error: app/ directory not found. Run from backend root.")
        return 1

    print("🔍 Linting Analysis Report")
    print("=" * 50)

    # File length analysis
    print("\n📄 File Length Analysis (max: 300 lines)")
    print("-" * 40)
    file_violations = analyze_file_lengths(app_dir)

    if file_violations:
        for violation in file_violations:
            print(
                f"❌ {violation['file']}: {violation['length']} lines (max: {violation['max_allowed']})"
            )
    else:
        print("✅ All files within length limits")

    # Function length analysis
    print("\n🔧 Function Length Analysis (max: 50 lines)")
    print("-" * 40)
    func_violations = analyze_function_lengths(app_dir)

    if func_violations:
        for violation in func_violations:
            func_type = "async" if violation["type"] == "AsyncFunctionDef" else "sync"
            print(
                f"❌ {violation['file']}:{violation['line']} - {violation['function']} ({func_type}): {violation['length']} lines"
            )
    else:
        print("✅ All functions within length limits")

    # Summary
    total_violations = len(file_violations) + len(func_violations)
    print(f"\n📊 Summary: {total_violations} violations found")

    if total_violations > 0:
        print("\n💡 Suggestions:")
        print("  • Break large functions into smaller, focused functions")
        print("  • Extract complex logic into helper methods")
        print("  • Consider splitting large files into modules")

        return 1
    else:
        print("\n🎉 Great job! All length limits are respected!")
        return 0


if __name__ == "__main__":
    exit(main())
