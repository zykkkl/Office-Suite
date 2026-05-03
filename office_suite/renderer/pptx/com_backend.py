"""PPTX COM 后端 — Windows 原生 PowerPoint 自动化

设计方案第二章：renderer/pptx/com_backend.py

使用 pywin32 (win32com) 通过 COM 接口控制 PowerPoint，
提供比 python-pptx 更精细的渲染能力：

  - 原生 WordArt 效果（无需 XML 注入）
  - 原生过渡动画
  - 精确的母版/版式管理
  - 实时预览渲染
  - 字体嵌入

使用条件：
  - Windows 操作系统
  - 已安装 Microsoft PowerPoint
  - pywin32 包（pip install pywin32）

降级策略：
  当 COM 不可用时，自动回退到 python-pptx XML 后端。
"""

import sys
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# 平台检测
IS_WINDOWS = sys.platform == "win32"

# COM 可用性
_COM_AVAILABLE = False
if IS_WINDOWS:
    try:
        import win32com.client
        _COM_AVAILABLE = True
    except ImportError:
        logger.debug("pywin32 不可用，COM 后端已禁用")

# PowerPoint COM 常量
PP_ALIGN_LEFT = 1
PP_ALIGN_CENTER = 2
PP_ALIGN_RIGHT = 3
PP_ALIGN_JUSTIFY = 4

MSO_SHAPE_RECTANGLE = 1
MSO_SHAPE_OVAL = 9
MSO_SHAPE_ROUNDED_RECTANGLE = 5


def is_available() -> bool:
    """检查 COM 后端是否可用"""
    return _COM_AVAILABLE


def ensure_available():
    """确保 COM 后端可用，否则抛出异常"""
    if not _COM_AVAILABLE:
        raise RuntimeError(
            "PPTX COM 后端需要 Windows + PowerPoint + pywin32。"
            "请安装: pip install pywin32，或使用 python-pptx 后端。"
        )


class COMPowerPoint:
    """PowerPoint COM 自动化接口

    通过 COM 控制 PowerPoint 应用程序，实现精确渲染。
    支持上下文管理器，自动处理 COM 初始化和清理。

    用法：
        with COMPowerPoint() as ppt:
            deck = ppt.create_deck()
            slide = ppt.add_slide(deck)
            ppt.add_textbox(slide, "Hello", left=100, top=100)
            ppt.save_as(deck, "output.pptx")
    """

    def __init__(self, visible: bool = False):
        """
        Args:
            visible: 是否显示 PowerPoint 窗口（调试用）
        """
        ensure_available()
        self._app = None
        self._visible = visible

    def __enter__(self):
        self._app = win32com.client.Dispatch("PowerPoint.Application")
        self._app.Visible = self._visible
        return self

    def __exit__(self, *args):
        if self._app:
            try:
                self._app.Quit()
            except Exception:
                # COM 应用可能已自行退出
                pass
            self._app = None

    def create_deck(self):
        """创建新演示文稿"""
        return self._app.Presentations.Add()

    def open_deck(self, path: str | Path):
        """打开已有演示文稿"""
        return self._app.Presentations.Open(str(Path(path).resolve()))

    def add_slide(self, deck, layout_index: int = 1):
        """添加幻灯片

        Args:
            deck: 演示文稿对象
            layout_index: 版式索引（1=标题幻灯片, 6=空白等）
        """
        return deck.Slides.Add(deck.Slides.Count + 1, layout_index)

    def add_textbox(self, slide, text: str, left: int, top: int,
                    width: int, height: int, font_size: int = 14,
                    font_name: str = "", bold: bool = False,
                    color: int = 0):
        """添加文本框

        Args:
            text: 文本内容
            left/top/width/height: 位置（磅）
            font_size: 字号
            font_name: 字体名
            bold: 是否加粗
            color: RGB 颜色（int，如 0xFF0000）
        """
        shape = slide.Shapes.AddTextbox(
            1,  # msoTextOrientationHorizontal
            left, top, width, height,
        )
        tf = shape.TextFrame
        tf.TextRange.Text = text
        tf.TextRange.Font.Size = font_size
        if font_name:
            tf.TextRange.Font.Name = font_name
        tf.TextRange.Font.Bold = bold
        if color:
            tf.TextRange.Font.Color.RGB = color
        return shape

    def add_shape(self, slide, shape_type: int, left: int, top: int,
                  width: int, height: int):
        """添加形状"""
        return slide.Shapes.AddShape(shape_type, left, top, width, height)

    def add_picture(self, slide, image_path: str | Path,
                    left: int, top: int, width: int, height: int):
        """添加图片"""
        return slide.Shapes.AddPicture(
            str(Path(image_path).resolve()),
            0,  # LinkToFile: msoFalse
            1,  # SaveWithDocument: msoTrue
            left, top, width, height,
        )

    def set_background(self, slide, color_rgb: int):
        """设置幻灯片背景色"""
        bg = slide.Background
        bg.Fill.Solid()
        bg.Fill.ForeColor.RGB = color_rgb

    def apply_transition(self, slide, effect: str = "fade", duration: float = 1.0):
        """应用幻灯片切换效果

        Args:
            effect: 效果名称（fade, push, wipe, split, reveal 等）
            duration: 持续时间（秒）
        """
        transition_map = {
            "fade": 3844,      # ppEffectFade
            "push": 3845,      # ppEffectPush
            "wipe": 3846,      # ppEffectWipe
            "split": 3847,     # ppEffectSplit
            "reveal": 3852,    # ppEffectReveal
            "none": 0,
        }
        slide.SlideShowTransition.EntryEffect = transition_map.get(effect, 3844)
        slide.SlideShowTransition.Duration = duration

    def save_as(self, deck, path: str | Path):
        """保存演示文稿"""
        deck.SaveAs(str(Path(path).resolve()))

    def export_as_images(self, deck, output_dir: str | Path, fmt: str = "png"):
        """导出为图片序列

        Args:
            output_dir: 输出目录
            fmt: 图片格式（png, jpg, gif）
        """
        out = Path(output_dir)
        out.mkdir(parents=True, exist_ok=True)
        for i, slide in enumerate(deck.Slides, 1):
            slide.Export(str(out / f"slide_{i:03d}.{fmt}"), fmt.upper())
