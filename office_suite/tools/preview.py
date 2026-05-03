"""实时预览工具 — DSL 修改 → 文件刷新

设计方案第十一章：前端实时预览（P2 特性）。

预览工具提供：
  - 监听 DSL 文件变化
  - 自动重新编译和渲染
  - 生成 HTML 预览页面
  - WebSocket 推送更新（可选）

当前实现为"生成 → 打开"模式（P0），
WebSocket 实时刷新留待 P2 完整实现。
"""

import html as html_mod
from dataclasses import dataclass
from pathlib import Path
from typing import Any
import hashlib
import time

from ..dsl.parser import parse_yaml, parse_yaml_string
from ..ir.compiler import compile_document
from ..renderer.pptx.deck import PPTXRenderer
from ..renderer.docx.document import DOCXRenderer
from ..renderer.xlsx.workbook import XLSXRenderer
from ..renderer.pdf.canvas import PDFRenderer
from ..renderer.html.dom import HTMLRenderer


@dataclass
class PreviewResult:
    """预览结果"""
    success: bool
    output_path: Path | None = None
    format: str = "html"
    compile_time: float = 0.0
    render_time: float = 0.0
    error: str = ""


RENDERERS = {
    "pptx": PPTXRenderer,
    "docx": DOCXRenderer,
    "xlsx": XLSXRenderer,
    "pdf": PDFRenderer,
    "html": HTMLRenderer,
}


def generate_preview(
    dsl_source: str | Path,
    output_dir: Path | None = None,
    formats: list[str] | None = None,
) -> dict[str, PreviewResult]:
    """生成预览文件

    Args:
        dsl_source: DSL 文件路径或 YAML 字符串
        output_dir: 输出目录
        formats: 输出格式列表，默认 ["html"]

    Returns:
        格式 → PreviewResult 映射
    """
    if formats is None:
        formats = ["html"]

    if output_dir is None:
        output_dir = Path.cwd() / "preview_output"
    output_dir.mkdir(parents=True, exist_ok=True)

    results: dict[str, PreviewResult] = {}

    # 解析 DSL
    try:
        t0 = time.time()
        if isinstance(dsl_source, Path):
            doc = parse_yaml(dsl_source)
        else:
            doc = parse_yaml_string(dsl_source)
        compile_time = time.time() - t0
    except Exception as e:
        for fmt in formats:
            results[fmt] = PreviewResult(success=False, error=f"DSL 解析失败: {e}")
        return results

    # 编译 IR
    try:
        t0 = time.time()
        ir = compile_document(doc)
        compile_time += time.time() - t0
    except Exception as e:
        for fmt in formats:
            results[fmt] = PreviewResult(success=False, error=f"IR 编译失败: {e}")
        return results

    # 渲染各格式
    for fmt in formats:
        renderer_cls = RENDERERS.get(fmt)
        if not renderer_cls:
            results[fmt] = PreviewResult(success=False, error=f"不支持的格式: {fmt}")
            continue

        try:
            t0 = time.time()
            renderer = renderer_cls()
            output_path = output_dir / f"preview.{fmt}"
            renderer.render(ir, output_path)
            render_time = time.time() - t0

            results[fmt] = PreviewResult(
                success=True,
                output_path=output_path,
                format=fmt,
                compile_time=compile_time,
                render_time=render_time,
            )
        except Exception as e:
            results[fmt] = PreviewResult(
                success=False,
                format=fmt,
                compile_time=compile_time,
                error=f"渲染失败: {e}",
            )

    return results


def generate_html_preview_page(
    dsl_source: str | Path,
    output_path: Path | None = None,
) -> Path:
    """生成 HTML 预览页面

    创建一个独立的 HTML 页面，包含：
    - DSL 源码展示
    - 渲染结果预览
    - 刷新按钮

    Args:
        dsl_source: DSL 文件路径或 YAML 字符串
        output_path: 输出 HTML 路径

    Returns:
        HTML 文件路径
    """
    if output_path is None:
        output_path = Path.cwd() / "preview.html"

    # 读取 DSL 源码
    if isinstance(dsl_source, Path):
        dsl_content = dsl_source.read_text(encoding="utf-8")
    else:
        dsl_content = dsl_source

    # 生成预览
    results = generate_preview(dsl_source, formats=["html"])

    html_result = results.get("html")
    preview_html = ""
    if html_result and html_result.success and html_result.output_path:
        preview_html = html_result.output_path.read_text(encoding="utf-8")

    # 生成完整页面
    safe_dsl = html_mod.escape(dsl_content)
    safe_preview = preview_html  # preview_html 来自渲染器输出，已在渲染器内部转义
    compile_t = f"{html_result.compile_time:.3f}" if html_result else "N/A"
    render_t = f"{html_result.render_time:.3f}" if html_result else "N/A"

    page_html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Office Suite 预览</title>
    <style>
        body {{ font-family: 'Segoe UI', sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }}
        .container {{ display: flex; gap: 20px; max-width: 1400px; margin: 0 auto; }}
        .panel {{ flex: 1; background: white; border-radius: 8px; padding: 16px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }}
        .panel h2 {{ margin-top: 0; color: #1E40AF; }}
        pre {{ background: #1E293B; color: #E2E8F0; padding: 12px; border-radius: 4px;
               overflow: auto; max-height: 600px; font-size: 13px; }}
        .preview-frame {{ border: 1px solid #E2E8F0; border-radius: 4px; min-height: 400px; }}
        .toolbar {{ margin-bottom: 12px; }}
        .toolbar button {{ padding: 8px 16px; background: #2563EB; color: white;
                          border: none; border-radius: 4px; cursor: pointer; }}
        .toolbar button:hover {{ background: #1D4ED8; }}
        .status {{ margin-top: 8px; color: #64748B; font-size: 13px; }}
    </style>
</head>
<body>
    <div class="toolbar">
        <button onclick="location.reload()">刷新预览</button>
        <span class="status">
            编译: {compile_t}s |
            渲染: {render_t}s
        </span>
    </div>
    <div class="container">
        <div class="panel">
            <h2>DSL 源码</h2>
            <pre>{safe_dsl}</pre>
        </div>
        <div class="panel">
            <h2>渲染预览</h2>
            <div class="preview-frame">
                {safe_preview}
            </div>
        </div>
    </div>
</body>
</html>"""

    output_path.write_text(page_html, encoding="utf-8")
    return output_path


def file_hash(path: Path) -> str:
    """计算文件哈希（用于变化检测）"""
    return hashlib.md5(path.read_bytes()).hexdigest()[:12]


class FileWatcher:
    """文件变化监听器（简化版）

    定期检查文件是否变化，用于触发重新渲染。
    完整版应使用 watchdog 库实现文件系统监听。
    """

    def __init__(self, file_path: Path, callback: Any = None):
        self.file_path = file_path
        self.callback = callback
        self._last_hash: str = ""

    def check(self) -> bool:
        """检查文件是否变化

        Returns:
            True 如果文件已变化
        """
        if not self.file_path.exists():
            return False

        current_hash = file_hash(self.file_path)
        if current_hash != self._last_hash:
            self._last_hash = current_hash
            if self.callback:
                self.callback(self.file_path)
            return True
        return False
