"""AI 意图解析 — 自然语言 → DesignBrief

设计方案第九章：将用户自然语言描述解析为结构化设计意图。

解析策略（P0 规则引擎，P1 接入 LLM）：
  1. 关键词匹配：提取文档类型、风格、强调点
  2. 情绪分析：从描述词推断设计情绪
  3. 约束提取：颜色、格式等显式约束

数据流：
  "做一个科技感的季度汇报 PPT" → DesignBrief(type=presentation, style=tech_dark, ...)

DesignBrief 可直接传入 suggest.py 获取布局/配色建议，
也可作为 DSL 生成的前置输入。
"""

import re
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class DesignBrief:
    """结构化设计意图"""
    # 文档类型: presentation / document / spreadsheet
    doc_type: str = "presentation"
    # 设计风格: tech_dark / business_light / minimal / creative / academic
    style: str = "business_light"
    # 强调点: charts / data_visualization / images / text / tables
    emphasis: list[str] = field(default_factory=list)
    # 设计情绪: professional / modern / warm / playful / serious
    mood: list[str] = field(default_factory=list)
    # 主色调 (HEX, 可选)
    primary_color: Optional[str] = None
    # 背景偏好: dark / light / auto
    background: str = "auto"
    # 页面数量提示 (可选)
    page_count: Optional[int] = None
    # 原始输入
    raw_input: str = ""
    # 额外约束
    constraints: dict = field(default_factory=dict)


# ============================================================
# 关键词词典
# ============================================================

# 文档类型关键词
DOC_TYPE_KEYWORDS: dict[str, list[str]] = {
    "presentation": [
        "PPT", "PPTX", "演示", "幻灯片", "汇报", "报告", "演讲", "展示",
        "presentation", "slide", "deck", "pitch",
    ],
    "document": [
        "文档", "Word", "DOCX", "文章", "论文", "报告书", "方案", "说明书",
        "document", "word", "article", "paper", "report",
    ],
    "spreadsheet": [
        "表格", "Excel", "XLSX", "数据表", "统计表", "财务表", "预算",
        "spreadsheet", "excel", "table", "budget", "data",
    ],
}

# 风格关键词
STYLE_KEYWORDS: dict[str, list[str]] = {
    "tech_dark": [
        "科技", "技术", "深色", "暗色", "赛博", "未来感", "科技感",
        "tech", "dark", "cyber", "futuristic", "modern tech",
    ],
    "business_light": [
        "商务", "正式", "专业", "简洁", "白色", "浅色", "企业",
        "business", "professional", "formal", "clean", "light",
    ],
    "minimal": [
        "极简", "简约", "留白", "简单", "清爽",
        "minimal", "simple", "clean", "whitespace",
    ],
    "creative": [
        "创意", "活泼", "有趣", "彩色", "多彩", "动感",
        "creative", "colorful", "playful", "vibrant", "fun",
    ],
    "academic": [
        "学术", "论文", "研究", "教育", "严谨",
        "academic", "research", "scholarly", "education",
    ],
}

# 强调点关键词
EMPHASIS_KEYWORDS: dict[str, list[str]] = {
    "charts": ["图表", "数据图", "柱状图", "折线图", "饼图", "chart", "graph"],
    "data_visualization": ["数据", "可视化", "统计", "数据驱动", "data", "visualization"],
    "images": ["图片", "照片", "图像", "视觉", "image", "photo", "visual"],
    "tables": ["表格", "数据表", "对比表", "table", "comparison"],
    "text": ["文字", "内容", "排版", "文本", "text", "content", "typography"],
    "timeline": ["时间线", "时间轴", "里程碑", "timeline", "milestone"],
}

# 情绪关键词
MOOD_KEYWORDS: dict[str, list[str]] = {
    "professional": ["专业", "正式", "商务", "professional", "formal", "business"],
    "modern": ["现代", "时尚", "潮流", "modern", "trendy", "contemporary"],
    "warm": ["温暖", "柔和", "亲切", "warm", "soft", "friendly"],
    "playful": ["活泼", "有趣", "动感", "playful", "fun", "dynamic"],
    "serious": ["严肃", "严谨", "稳重", "serious", "rigorous", "stable"],
    "data_driven": ["数据驱动", "数据导向", "分析", "data-driven", "analytical"],
}

# 背景关键词
BACKGROUND_KEYWORDS: dict[str, str] = {
    "深色": "dark", "暗色": "dark", "黑色": "dark", "深色背景": "dark",
    "dark": "dark", "black": "dark",
    "浅色": "light", "白色": "light", "亮色": "light", "浅色背景": "light",
    "light": "light", "white": "light", "bright": "light",
}

# 颜色提取模式
COLOR_PATTERN = re.compile(r"#[0-9A-Fa-f]{6}")


def parse_intent(text: str) -> DesignBrief:
    """解析自然语言为 DesignBrief

    Args:
        text: 用户自然语言描述

    Returns:
        DesignBrief 结构化设计意图
    """
    brief = DesignBrief(raw_input=text)

    # 1. 文档类型
    brief.doc_type = _match_keyword(text, DOC_TYPE_KEYWORDS, "presentation")

    # 2. 风格
    brief.style = _match_keyword(text, STYLE_KEYWORDS, "business_light")

    # 3. 强调点
    brief.emphasis = _match_all_keywords(text, EMPHASIS_KEYWORDS)

    # 4. 情绪
    brief.mood = _match_all_keywords(text, MOOD_KEYWORDS)

    # 5. 背景偏好
    for kw, bg in BACKGROUND_KEYWORDS.items():
        if kw in text.lower():
            brief.background = bg
            break

    # 6. 主色调提取
    color_match = COLOR_PATTERN.search(text)
    if color_match:
        brief.primary_color = color_match.group()

    # 7. 页面数量
    page_match = re.search(r"(\d+)\s*[页张slides]", text, re.IGNORECASE)
    if page_match:
        brief.page_count = int(page_match.group(1))

    # 8. 默认情绪
    if not brief.mood:
        brief.mood = _infer_default_mood(brief.style)

    return brief


def _match_keyword(text: str, keyword_map: dict[str, list[str]], default: str) -> str:
    """匹配第一个命中的关键词类别"""
    text_lower = text.lower()
    for category, keywords in keyword_map.items():
        for kw in keywords:
            if kw.lower() in text_lower:
                return category
    return default


def _match_all_keywords(text: str, keyword_map: dict[str, list[str]]) -> list[str]:
    """匹配所有命中的关键词类别（去重）"""
    text_lower = text.lower()
    matched = []
    for category, keywords in keyword_map.items():
        for kw in keywords:
            if kw.lower() in text_lower:
                if category not in matched:
                    matched.append(category)
                break
    return matched


def _infer_default_mood(style: str) -> list[str]:
    """从风格推断默认情绪"""
    style_mood_map = {
        "tech_dark": ["modern", "professional"],
        "business_light": ["professional", "serious"],
        "minimal": ["modern", "professional"],
        "creative": ["playful", "modern"],
        "academic": ["serious", "professional"],
    }
    return style_mood_map.get(style, ["professional"])
