"""分类类型定义 — ElementLayer 枚举与 ElementDef 数据类"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class ElementLayer(Enum):
    """元素分类层级

    从最基础到最复杂：ATOM → COMPONENT → DISPLAY → DECOR → TEMPLATE
    """
    ATOM = "ATOM"             # L1: 最小不可拆单元
    COMPONENT = "COMPONENT"   # L2: 多原子组合的可复用组件
    DISPLAY = "DISPLAY"       # L3: 完整展示区块
    DECOR = "DECOR"           # L4: 纯装饰性元素
    TEMPLATE = "TEMPLATE"     # L5: 完整幻灯片模板


@dataclass
class ElementDef:
    """元素定义 — catalog 中的单条元素记录

    每个元素归属一个层级 (layer)，可按 category/tags/scenes 检索。
    生成链路：
      - component_name → components/registry.py → generate_component() → IR
      - template_name  → design/slide_templates.py → 完整幻灯片 dict
      - dsl_fragment   → 直接注入 DSL 的元素列表
    """
    id: str                              # 唯一标识，如 "stat_card", "cover_hero"
    layer: ElementLayer                  # 所属层级
    category: str                        # 功能分类，如 "data_display", "slide_cover"
    name: str                            # 人可读名称
    description: str = ""                # 描述
    tags: list[str] = field(default_factory=list)        # 检索标签
    scenes: list[str] = field(default_factory=list)      # 适用场景
    params: dict[str, dict[str, Any]] = field(default_factory=dict)  # 参数定义

    # 生成器引用（三选一，优先级从高到低）
    component_name: str | None = None    # 复用 components/registry.py 中的组件
    template_name: str | None = None     # 复用 design/slide_templates.py 中的模板
    dsl_fragment: list[dict] | None = None  # 直接嵌入 DSL 元素片段（JSON 可序列化）

    @property
    def layer_order(self) -> int:
        """层级排序值，用于搜索结果排序"""
        _ORDER = {
            ElementLayer.TEMPLATE: 0,
            ElementLayer.DISPLAY: 1,
            ElementLayer.COMPONENT: 2,
            ElementLayer.DECOR: 3,
            ElementLayer.ATOM: 4,
        }
        return _ORDER.get(self.layer, 99)
