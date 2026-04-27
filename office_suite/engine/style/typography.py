"""排版引擎 — 字体选择、行距、字距、段落排版

设计方案第七章：样式引擎。

排版引擎处理：
  - 字体族选择 + 回退链
  - 行高（line-height）计算
  - 字距（letter-spacing）和词距（word-spacing）
  - 段落对齐和缩进
  - 中英文混排处理
"""

from dataclasses import dataclass, field
from typing import Any


# ============================================================
# 字体族回退链
# ============================================================

FONT_FALLBACK_CHAINS: dict[str, list[str]] = {
    "sans-serif": [
        "Microsoft YaHei UI", "PingFang SC", "Noto Sans SC",
        "Helvetica Neue", "Arial", "sans-serif",
    ],
    "serif": [
        "SimSun", "Noto Serif SC", "Times New Roman", "serif",
    ],
    "monospace": [
        "Consolas", "Source Code Pro", "Noto Sans Mono", "monospace",
    ],
    "display": [
        "Microsoft YaHei", "PingFang SC", "Noto Sans SC",
        "Segoe UI", "Helvetica Neue", "sans-serif",
    ],
}


def resolve_font_family(family: str | None, fallback_chain: str = "sans-serif") -> str:
    """解析字体族，返回完整的 font-family 字符串

    Args:
        family: 指定字体（可为 None）
        fallback_chain: 回退链名称

    Returns:
        CSS font-family 值
    """
    chain = FONT_FALLBACK_CHAINS.get(fallback_chain, FONT_FALLBACK_CHAINS["sans-serif"])
    if family and family not in chain:
        return f'"{family}", {", ".join(chain)}'
    return ", ".join(f'"{f}"' if " " in f else f for f in chain)


# ============================================================
# 排版规格
# ============================================================

@dataclass
class TypographySpec:
    """排版规格"""
    font_family: str = "sans-serif"
    font_size: float = 14.0        # pt
    font_weight: int = 400
    line_height: float = 1.5       # 倍数（相对于 font-size）
    letter_spacing: float = 0.0    # pt
    word_spacing: float = 0.0      # pt
    text_align: str = "left"       # left / center / right / justify
    text_indent: float = 0.0       # pt（首行缩进）
    text_transform: str = "none"   # none / uppercase / lowercase / capitalize
    white_space: str = "normal"    # normal / nowrap / pre / pre-wrap


@dataclass
class TextMetrics:
    """文本度量结果"""
    width: float = 0.0       # 文本宽度（pt）
    height: float = 0.0      # 文本高度（pt）
    line_count: int = 1      # 行数
    baseline: float = 0.0    # 基线位置（pt）


# ============================================================
# 文本度量（近似计算）
# ============================================================

# 字宽近似系数（相对于 font-size）
CJK_WIDTH_FACTOR = 1.0       # 中文字符宽度 ≈ font-size
LATIN_WIDTH_FACTOR = 0.55    # 拉丁字母平均宽度 ≈ 0.55 * font-size
DIGIT_WIDTH_FACTOR = 0.55    # 数字宽度
SPACE_WIDTH_FACTOR = 0.3     # 空格宽度


def estimate_char_width(char: str, font_size: float) -> float:
    """估算单个字符宽度（pt）

    Args:
        char: 字符
        font_size: 字号（pt）

    Returns:
        估算宽度（pt）
    """
    cp = ord(char)
    # CJK 统一表意文字
    if 0x4E00 <= cp <= 0x9FFF or 0x3400 <= cp <= 0x4DBF:
        return font_size * CJK_WIDTH_FACTOR
    # 日文假名
    if 0x3040 <= cp <= 0x30FF:
        return font_size * CJK_WIDTH_FACTOR
    # 韩文
    if 0xAC00 <= cp <= 0xD7AF:
        return font_size * CJK_WIDTH_FACTOR
    # 数字
    if 0x30 <= cp <= 0x39:
        return font_size * DIGIT_WIDTH_FACTOR
    # 空格
    if char == " ":
        return font_size * SPACE_WIDTH_FACTOR
    # 标点（CJK）
    if 0x3000 <= cp <= 0x303F or 0xFF00 <= cp <= 0xFFEF:
        return font_size * CJK_WIDTH_FACTOR
    # 其他拉丁字符
    return font_size * LATIN_WIDTH_FACTOR


def estimate_text_width(text: str, font_size: float, letter_spacing: float = 0.0) -> float:
    """估算文本宽度（pt）

    Args:
        text: 文本内容
        font_size: 字号（pt）
        letter_spacing: 字距（pt）

    Returns:
        估算宽度（pt）
    """
    width = sum(estimate_char_width(c, font_size) for c in text)
    if letter_spacing and len(text) > 1:
        width += letter_spacing * (len(text) - 1)
    return width


def estimate_text_metrics(
    text: str,
    spec: TypographySpec,
    container_width: float = 0.0,  # pt
) -> TextMetrics:
    """估算文本度量

    Args:
        text: 文本内容
        spec: 排版规格
        container_width: 容器宽度（pt），用于计算换行

    Returns:
        TextMetrics 实例
    """
    line_height = spec.font_size * spec.line_height

    if container_width <= 0:
        # 无容器约束，单行
        width = estimate_text_width(text, spec.font_size, spec.letter_spacing)
        return TextMetrics(
            width=width,
            height=line_height,
            line_count=1,
            baseline=spec.font_size * 0.85,
        )

    # 计算换行
    lines = _wrap_text(text, spec.font_size, spec.letter_spacing, container_width)
    line_count = len(lines)
    max_width = max(
        estimate_text_width(line, spec.font_size, spec.letter_spacing)
        for line in lines
    ) if lines else 0.0

    return TextMetrics(
        width=max_width,
        height=line_count * line_height,
        line_count=line_count,
        baseline=spec.font_size * 0.85,
    )


def _wrap_text(
    text: str, font_size: float, letter_spacing: float, container_width: float,
) -> list[str]:
    """文本自动换行

    Args:
        text: 文本内容
        font_size: 字号
        letter_spacing: 字距
        container_width: 容器宽度（pt）

    Returns:
        换行后的文本列表
    """
    lines = []
    current_line = ""
    current_width = 0.0

    for char in text:
        if char == "\n":
            lines.append(current_line)
            current_line = ""
            current_width = 0.0
            continue

        char_w = estimate_char_width(char, font_size)
        sp = letter_spacing if current_line else 0.0

        if current_width + char_w + sp > container_width and current_line:
            lines.append(current_line)
            current_line = char
            current_width = char_w
        else:
            current_line += char
            current_width += char_w + sp

    if current_line:
        lines.append(current_line)

    return lines if lines else [""]


# ============================================================
# 渲染器适配
# ============================================================

def to_css(spec: TypographySpec) -> dict[str, str]:
    """转换为 CSS 属性字典"""
    css = {
        "font-family": resolve_font_family(spec.font_family),
        "font-size": f"{spec.font_size}pt",
        "font-weight": str(spec.font_weight),
        "line-height": str(spec.line_height),
        "text-align": spec.text_align,
        "white-space": spec.white_space,
    }
    if spec.letter_spacing:
        css["letter-spacing"] = f"{spec.letter_spacing}pt"
    if spec.word_spacing:
        css["word-spacing"] = f"{spec.word_spacing}pt"
    if spec.text_indent:
        css["text-indent"] = f"{spec.text_indent}pt"
    if spec.text_transform != "none":
        css["text-transform"] = spec.text_transform
    return css


def to_pptx_params(spec: TypographySpec) -> dict[str, Any]:
    """转换为 PPTX 渲染参数"""
    return {
        "font_size": spec.font_size,
        "font_weight": spec.font_weight,
        "line_spacing": spec.line_height,
        "alignment": {
            "left": 1,   # PP_ALIGN.LEFT
            "center": 2, # PP_ALIGN.CENTER
            "right": 3,  # PP_ALIGN.RIGHT
            "justify": 4,
        }.get(spec.text_align, 1),
    }
