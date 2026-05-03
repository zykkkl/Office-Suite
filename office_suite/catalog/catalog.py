"""元素目录引擎 — 加载、注册、检索、生成 DSL/IR

单例访问：
    catalog = get_catalog()          # 获取全局实例
    catalog.load_yaml("path.yaml")  # 加载预置定义

检索示例：
    results = catalog.search(tags=["cover"])
    results = catalog.search(layer=ElementLayer.TEMPLATE, category="slide_cover")
    results = catalog.search(scenes=["data_display"])

生成链路：
    dsl_fragments = catalog.generate_dsl("stat_card", {"label": "DAU", "value": "1.2M"})
    ir_nodes      = catalog.generate_ir("stat_card", {"label": "DAU", "value": "1.2M"})
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from office_suite.dsl.parser import safe_yaml_load
from .types import ElementDef, ElementLayer


class ElementCatalog:
    """元素目录 — 存储和检索 PPT 画布元素"""

    def __init__(self) -> None:
        self._entries: dict[str, ElementDef] = {}

    # ── 加载 ──────────────────────────────────────────────

    def load_yaml(self, path: str | Path) -> int:
        """从 YAML 文件加载元素定义

        Args:
            path: catalog.yaml 文件路径

        Returns:
            加载的元素数量
        """
        path = Path(path)
        with open(path, "r", encoding="utf-8") as f:
            raw = safe_yaml_load(f.read())

        elements_raw = raw if isinstance(raw, list) else raw.get("elements", [])
        count = 0
        for entry in elements_raw:
            if not isinstance(entry, dict) or "id" not in entry:
                continue
            self.register(self._parse_entry(entry))
            count += 1
        return count

    @staticmethod
    def _parse_entry(raw: dict[str, Any]) -> ElementDef:
        """将 YAML dict 解析为 ElementDef"""
        layer_str = raw.get("layer", "ATOM")
        try:
            layer = ElementLayer(layer_str)
        except ValueError:
            layer = ElementLayer.ATOM

        return ElementDef(
            id=raw["id"],
            layer=layer,
            category=raw.get("category", ""),
            name=raw.get("name", raw["id"]),
            description=raw.get("description", ""),
            tags=raw.get("tags", []),
            scenes=raw.get("scenes", []),
            params=raw.get("params", {}),
            component_name=raw.get("component_name"),
            template_name=raw.get("template_name"),
            dsl_fragment=raw.get("dsl_fragment"),
        )

    # ── 注册 ──────────────────────────────────────────────

    def register(self, entry: ElementDef) -> None:
        """注册或覆盖一条元素定义"""
        self._entries[entry.id] = entry

    # ── 查询 ──────────────────────────────────────────────

    def get(self, element_id: str) -> ElementDef | None:
        """按 ID 精确查找"""
        return self._entries.get(element_id)

    def search(
        self,
        *,
        tags: list[str] | None = None,
        scenes: list[str] | None = None,
        layer: ElementLayer | None = None,
        category: str | None = None,
        limit: int = 50,
    ) -> list[ElementDef]:
        """多维检索，条件取交集

        Args:
            tags:     必须包含全部标签（AND）
            scenes:   命中任一场景即可（OR）
            layer:    层级精确匹配
            category: 分类精确匹配
            limit:    最大返回数

        Returns:
            按层级复杂度排序的匹配结果
        """
        results: list[ElementDef] = []
        for entry in self._entries.values():
            if layer is not None and entry.layer != layer:
                continue
            if category is not None and entry.category != category:
                continue
            if tags and not all(t in entry.tags for t in tags):
                continue
            if scenes and not any(s in entry.scenes for s in scenes):
                continue
            results.append(entry)

        results.sort(key=lambda e: e.layer_order)
        return results[:limit]

    def list_all(self) -> list[ElementDef]:
        """返回所有条目"""
        return sorted(self._entries.values(), key=lambda e: e.layer_order)

    # ── 生成 ──────────────────────────────────────────────

    def generate_dsl(self, element_id: str, params: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        """将 catalog 条目展开为 DSL 元素片段

        生成链路：
          1. 若有 dsl_fragment → 模板替换 params 后返回
          2. 若有 component_name → 返回 type: component 的引用元素
          3. 若有 template_name → 返回 type: template 的引用元素

        Args:
            element_id: catalog 条目 ID
            params:     模板参数

        Returns:
            DSL 元素 dict 列表，可直接注入 slide.elements

        Raises:
            KeyError: 条目不存在
        """
        entry = self._entries.get(element_id)
        if entry is None:
            raise KeyError(f"catalog 中不存在 '{element_id}'")

        params = params or {}

        if entry.dsl_fragment is not None:
            return self._expand_fragment(entry.dsl_fragment, params)

        if entry.component_name is not None:
            return [{
                "type": "component",
                "component": entry.component_name,
                **params,
            }]

        if entry.template_name is not None:
            return [{
                "type": "template_ref",
                "template": entry.template_name,
                **params,
            }]

        return []

    def generate_ir(self, element_id: str, params: dict[str, Any] | None = None) -> list:
        """通过 component_registry 生成 IR 节点

        仅当条目有 component_name 时有效。

        Args:
            element_id: catalog 条目 ID
            params:     组件参数

        Returns:
            IRNode 列表

        Raises:
            KeyError: 条目不存在
            ValueError: 条目无 component_name
        """
        entry = self._entries.get(element_id)
        if entry is None:
            raise KeyError(f"catalog 中不存在 '{element_id}'")
        if entry.component_name is None:
            raise ValueError(f"'{element_id}' 未关联 component（仅 component_name 条目可生成 IR）")

        from ..components.registry import generate_component
        return generate_component(entry.component_name, params or {})

    @staticmethod
    def _expand_fragment(fragments: list[dict], params: dict[str, Any]) -> list[dict[str, Any]]:
        """将 dsl_fragment 中的 {{key}} 占位符替换为 params 值

        浅拷贝，不修改原始 fragment。
        """
        import copy
        result = []
        for frag in fragments:
            frag = copy.deepcopy(frag)
            _replace_placeholders(frag, params)
            result.append(frag)
        return result


def _replace_placeholders(obj: Any, params: dict[str, Any]) -> None:
    """递归替换 dict/list/str 中的 {{key}} 占位符（原地修改）"""
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, str):
                obj[k] = _template_str(v, params)
            elif isinstance(v, (dict, list)):
                _replace_placeholders(v, params)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            if isinstance(v, str):
                obj[i] = _template_str(v, params)
            elif isinstance(v, (dict, list)):
                _replace_placeholders(v, params)


def _template_str(s: str, params: dict[str, Any]) -> str:
    """替换字符串中的 {{key}} 占位符"""
    for key, val in params.items():
        s = s.replace("{{" + key + "}}", str(val))
    return s


# ── 全局单例 ──────────────────────────────────────────────

_GLOBAL_CATALOG: ElementCatalog | None = None


def get_catalog() -> ElementCatalog:
    """获取全局 catalog 单例（首次调用自动加载默认 catalog.yaml）"""
    global _GLOBAL_CATALOG
    if _GLOBAL_CATALOG is None:
        _GLOBAL_CATALOG = ElementCatalog()
        default_path = Path(__file__).parent / "catalog.yaml"
        if default_path.exists():
            _GLOBAL_CATALOG.load_yaml(default_path)
    return _GLOBAL_CATALOG
