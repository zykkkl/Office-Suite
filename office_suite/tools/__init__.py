"""工具层 — 设计检查、格式转换、批量生成

注意：本模块使用延迟导入，避免 CLI --help 因缺少可选后端依赖而崩溃。
直接 import 子模块（如 from office_suite.tools.convert import ...）不受影响。
"""

__all__ = [
    "lint_ir", "LintReport", "LintIssue",
    "convert_ir", "convert_dsl_file", "convert_dsl_string", "batch_convert",
    "batch_from_template", "batch_from_dsl_files",
]


def __getattr__(name: str):
    if name in ("lint_ir", "LintReport", "LintIssue"):
        from .linter import lint_ir, LintReport, LintIssue
        return {"lint_ir": lint_ir, "LintReport": LintReport, "LintIssue": LintIssue}[name]
    if name in ("convert_ir", "convert_dsl_file", "convert_dsl_string", "batch_convert"):
        from .convert import convert_ir, convert_dsl_file, convert_dsl_string, batch_convert
        return {"convert_ir": convert_ir, "convert_dsl_file": convert_dsl_file,
                "convert_dsl_string": convert_dsl_string, "batch_convert": batch_convert}[name]
    if name in ("batch_from_template", "batch_from_dsl_files"):
        from .batch import batch_from_template, batch_from_dsl_files
        return {"batch_from_template": batch_from_template, "batch_from_dsl_files": batch_from_dsl_files}[name]
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
