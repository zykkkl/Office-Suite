"""Quality gate for Office Suite YAML documents.

This module intentionally composes the existing parser, compiler, validators,
linter, and renderers into one workflow so agents do not skip available checks.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

import yaml

from ..dsl.parser import parse_yaml
from ..dsl.validator import DSLValidationIssue, Severity, validate_dsl
from ..ir.compiler import compile_document
from ..ir.validator import ValidationIssue, validate_ir_v2
from .convert import convert_ir
from .linter import LintIssue, lint_ir


@dataclass
class CheckResult:
    dsl_path: Path
    slide_count: int = 0
    dsl_issues: list[DSLValidationIssue] = field(default_factory=list)
    ir_issues: list[ValidationIssue] = field(default_factory=list)
    lint_issues: list[LintIssue] = field(default_factory=list)
    outputs: dict[str, Path] = field(default_factory=dict)

    @property
    def is_valid(self) -> bool:
        return not self.dsl_errors and not self.ir_errors

    @property
    def dsl_errors(self) -> list[DSLValidationIssue]:
        return [issue for issue in self.dsl_issues if issue.severity.value == "error"]

    @property
    def ir_errors(self) -> list[ValidationIssue]:
        return [issue for issue in self.ir_issues if issue.severity.value == "error"]

    @property
    def warnings(self) -> list[object]:
        dsl_warnings = [issue for issue in self.dsl_issues if issue.severity.value == "warning"]
        ir_warnings = [issue for issue in self.ir_issues if issue.severity.value == "warning"]
        return [*dsl_warnings, *ir_warnings, *self.lint_issues]

    def summary(self) -> str:
        lines = [
            f"File: {self.dsl_path}",
            f"Slides: {self.slide_count}",
            f"DSL issues: {len(self.dsl_issues)}",
            f"IR issues: {len(self.ir_issues)}",
            f"Lint issues: {len(self.lint_issues)}",
            f"Outputs: {', '.join(f'{k}={v}' for k, v in self.outputs.items()) or 'none'}",
            f"Valid: {self.is_valid}",
        ]
        for issue in [*self.dsl_issues, *self.ir_issues, *self.lint_issues]:
            lines.append(f"- {issue}")
        return "\n".join(lines)


def check_dsl_file(
    dsl_path: str | Path,
    *,
    render_formats: Iterable[str] = (),
    output_dir: str | Path | None = None,
    run_lint: bool = True,
) -> CheckResult:
    """Parse, validate, compile, lint, and optionally render a DSL file."""
    dsl_path = Path(dsl_path)
    result = CheckResult(dsl_path=dsl_path)

    with open(dsl_path, "r", encoding="utf-8") as file:
        raw = yaml.safe_load(file) or {}

    dsl_validation = validate_dsl(raw)
    result.dsl_issues = dsl_validation.issues
    result.dsl_issues.extend(_validate_referenced_pages(raw, dsl_path.parent))

    doc = parse_yaml(dsl_path)
    result.slide_count = len(doc.slides)

    ir_doc = compile_document(doc)
    ir_validation = validate_ir_v2(ir_doc)
    result.ir_issues = ir_validation.issues

    if run_lint:
        lint_report = lint_ir(ir_doc)
        result.lint_issues = lint_report.issues

    if render_formats:
        if output_dir is None:
            output_dir = dsl_path.parent
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        for fmt in render_formats:
            fmt = fmt.lower().lstrip(".")
            output_path = output_dir / f"{dsl_path.stem}.{fmt}"
            result.outputs[fmt] = convert_ir(ir_doc, output_path, fmt)

    return result


def _validate_referenced_pages(raw: dict, base_dir: Path) -> list[DSLValidationIssue]:
    """Validate slide YAML referenced from top-level pages.

    Entry files usually contain only `pages: [...]`, so validating the raw
    entry file alone misses slide-level rules such as semantic_icon primitives.
    """
    issues: list[DSLValidationIssue] = []
    page_refs = raw.get("pages") or []
    if not isinstance(page_refs, list):
        return issues

    for index, ref in enumerate(page_refs):
        if isinstance(ref, dict):
            if "path" not in ref:
                slide_raws = [ref]
                page_label = f"pages[{index}]"
            else:
                ref = ref["path"]
                slide_raws = []
                page_label = str(ref)
        else:
            slide_raws = []
            page_label = str(ref)

        if isinstance(ref, str):
            page_path = Path(ref)
            if not page_path.is_absolute():
                page_path = base_dir / page_path
            try:
                page_raw = yaml.safe_load(page_path.read_text(encoding="utf-8")) or {}
            except OSError as exc:
                issues.append(DSLValidationIssue(
                    severity=Severity.ERROR,
                    message=f"Cannot read page file: {exc}",
                    path=f"pages[{index}]",
                    rule="page_file_read",
                ))
                continue

            if "slides" in page_raw and isinstance(page_raw["slides"], list):
                slide_raws = [item for item in page_raw["slides"] if isinstance(item, dict)]
            elif "slide" in page_raw and isinstance(page_raw["slide"], dict):
                slide_raws = [page_raw["slide"]]
            elif isinstance(page_raw, dict):
                slide_raws = [page_raw]

        synthetic = {
            "version": raw.get("version", "4.0"),
            "type": raw.get("type", "presentation"),
            "slides": slide_raws,
        }
        page_validation = validate_dsl(synthetic)
        for issue in page_validation.issues:
            issue.path = f"{page_label}.{issue.path}" if issue.path else page_label
        issues.extend(page_validation.issues)

    return issues


def main(argv: list[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Check an Office Suite YAML DSL file")
    parser.add_argument("dsl_path", help="Path to the YAML DSL entry file")
    parser.add_argument(
        "--render",
        nargs="*",
        default=[],
        help="Optional formats to render, e.g. --render pptx pdf html",
    )
    parser.add_argument("--output-dir", default=None, help="Directory for rendered outputs")
    parser.add_argument("--no-lint", action="store_true", help="Skip design lint checks")
    args = parser.parse_args(argv)

    result = check_dsl_file(
        args.dsl_path,
        render_formats=args.render,
        output_dir=args.output_dir,
        run_lint=not args.no_lint,
    )
    import sys
    if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf8"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    print(result.summary())
    return 0 if result.is_valid else 1


if __name__ == "__main__":
    raise SystemExit(main())
