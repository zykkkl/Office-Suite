"""Command line entry point for Office Suite.

Provides the documented command:
    python -m office_suite build input.yml -o output.pptx
    python -m office_suite --help
"""

from __future__ import annotations

import argparse
from pathlib import Path

SUPPORTED_FORMATS = {"pptx", "docx", "xlsx", "pdf", "html"}


def _infer_format(output_path: Path, explicit_format: str | None) -> str:
    if explicit_format:
        fmt = explicit_format.lower().lstrip(".")
    else:
        fmt = output_path.suffix.lower().lstrip(".")

    if fmt not in SUPPORTED_FORMATS:
        supported = ", ".join(sorted(SUPPORTED_FORMATS))
        raise ValueError(
            f"Cannot infer output format. Use an output suffix or --format. "
            f"Supported formats: {supported}"
        )
    return fmt


def build_command(args: argparse.Namespace) -> int:
    # 延迟导入：仅在实际渲染时才加载渲染器依赖
    from .tools.convert import convert_dsl_file

    input_path = Path(args.input)
    output_path = Path(args.output)
    target_format = _infer_format(output_path, args.format)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    rendered_path = convert_dsl_file(input_path, output_path, target_format)
    print(f"Rendered {target_format}: {rendered_path}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="office-suite",
        description="Office Suite 4.0 — Omni-media fusion document engine",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    build_parser = subparsers.add_parser("build", help="Render a YAML DSL file")
    build_parser.add_argument("input", help="Path to the YAML DSL entry file")
    build_parser.add_argument(
        "-o",
        "--output",
        required=True,
        help="Output file path, e.g. output/deck.pptx",
    )
    build_parser.add_argument(
        "-f",
        "--format",
        choices=sorted(SUPPORTED_FORMATS),
        help="Output format. Defaults to the output file extension.",
    )
    build_parser.set_defaults(func=build_command)

    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except Exception as exc:
        parser.exit(1, f"error: {exc}\n")


if __name__ == "__main__":
    raise SystemExit(main())
