"""元素分类目录 — PPT 画布元素的分层分类、收集与检索系统

5 层分类体系：
  L1 ATOM       — 最小不可拆单元（text, rectangle, circle, image）
  L2 COMPONENT  — 多原子组合的可复用组件（stat_card, icon_badge）
  L3 DISPLAY    — 完整展示区块（hero_banner, timeline, feature_grid）
  L4 DECOR      — 纯装饰性元素（underline, separator）
  L5 TEMPLATE   — 完整幻灯片模板（cover, section, closing）
"""

from .types import ElementLayer, ElementDef
from .catalog import ElementCatalog, get_catalog

__all__ = [
    "ElementLayer",
    "ElementDef",
    "ElementCatalog",
    "get_catalog",
]
