"""PDF 字体管理 — 从 canvas.py 提取的字体映射逻辑

本模块集中管理 PDF 渲染器的字体映射和注册。

使用方式：
    from office_suite.renderer.pdf.font import resolve_font, FONT_MAP, BUILTIN_FONTS
"""

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont

# 注册 CID 中文字体（reportlab 内置，无需外部文件）
pdfmetrics.registerFont(UnicodeCIDFont('STSong-Light'))

# reportlab 内置字体
BUILTIN_FONTS = {
    "Helvetica", "Helvetica-Bold", "Helvetica-Oblique", "Helvetica-BoldOblique",
    "Courier", "Courier-Bold", "Courier-Oblique", "Courier-BoldOblique",
    "Times-Roman", "Times-Bold", "Times-Italic", "Times-BoldItalic",
}

# 外部字体名 → reportlab 字体映射
FONT_MAP = {
    "microsoft yahei ui": "STSong-Light",
    "microsoft yahei": "STSong-Light",
    "simhei": "STSong-Light",
    "simsun": "STSong-Light",
    "nsimsun": "STSong-Light",
    "fangsong": "STSong-Light",
    "kaiti": "STSong-Light",
    "segoe ui": "Helvetica",
    "arial": "Helvetica",
    "helvetica neue": "Helvetica",
    "impact": "Helvetica-Bold",
    "times new roman": "Times-Roman",
    "consolas": "Courier",
    "cascadia code": "Courier",
}


def resolve_font(font_name: str | None, bold: bool = False) -> str:
    """将字体名映射到 reportlab 可用的字体

    Args:
        font_name: 外部字体名（如 "Microsoft YaHei UI"）
        bold: 是否粗体

    Returns:
        reportlab 字体名
    """
    if font_name is None:
        return "Helvetica-Bold" if bold else "Helvetica"

    # 直接可用
    if font_name in BUILTIN_FONTS:
        return font_name

    # 映射
    mapped = FONT_MAP.get(font_name.lower(), "Helvetica")

    # CID 中文字体没有 Bold 变体，直接返回
    if mapped == "STSong-Light":
        return mapped

    # 西文字体添加 Bold 后缀
    if bold and not mapped.endswith("-Bold"):
        if mapped == "Helvetica":
            return "Helvetica-Bold"
        elif mapped == "Times-Roman":
            return "Times-Bold"
        elif mapped == "Courier":
            return "Courier-Bold"

    return mapped
