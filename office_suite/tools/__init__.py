"""工具层 — 设计检查、格式转换、批量生成"""

from .linter import lint_ir, LintReport, LintIssue
from .convert import convert_ir, convert_dsl_file, convert_dsl_string, batch_convert
from .batch import batch_from_template, batch_from_dsl_files

__all__ = [
    "lint_ir", "LintReport", "LintIssue",
    "convert_ir", "convert_dsl_file", "convert_dsl_string", "batch_convert",
    "batch_from_template", "batch_from_dsl_files",
]
