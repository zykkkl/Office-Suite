"""IR 差异比较 — 两个文档之间的结构差异

设计方案第四章：中间表示。

差异比较用于：
  - 版本对比（显示两个版本之间的变化）
  - 增量渲染（只重新渲染变化的部分）
  - 变更追踪（记录谁改了什么）

差异类型：
  - ADD: 新增节点
  - REMOVE: 移除节点
  - MODIFY: 修改属性（样式/内容/位置）
  - MOVE: 节点位置变化（父子关系改变）
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from .types import IRNode, IRDocument, NodeType


class DiffType(Enum):
    ADD = "add"
    REMOVE = "remove"
    MODIFY = "modify"
    MOVE = "move"


@dataclass
class DiffEntry:
    """单条差异记录"""
    diff_type: DiffType
    node_path: str           # 节点路径（如 /document/slide[1]/text[2]）
    old_value: Any = None    # 旧值（REMOVE/MODIFY）
    new_value: Any = None    # 新值（ADD/MODIFY）
    field: str = ""          # 变化的字段名
    details: str = ""        # 人类可读描述


@dataclass
class DiffResult:
    """差异结果"""
    entries: list[DiffEntry] = field(default_factory=list)
    has_changes: bool = False

    @property
    def added(self) -> list[DiffEntry]:
        return [e for e in self.entries if e.diff_type == DiffType.ADD]

    @property
    def removed(self) -> list[DiffEntry]:
        return [e for e in self.entries if e.diff_type == DiffType.REMOVE]

    @property
    def modified(self) -> list[DiffEntry]:
        return [e for e in self.entries if e.diff_type == DiffType.MODIFY]

    @property
    def moved(self) -> list[DiffEntry]:
        return [e for e in self.entries if e.diff_type == DiffType.MOVE]

    def summary(self) -> str:
        """生成差异摘要"""
        parts = []
        if self.added:
            parts.append(f"+{len(self.added)} 新增")
        if self.removed:
            parts.append(f"-{len(self.removed)} 移除")
        if self.modified:
            parts.append(f"~{len(self.modified)} 修改")
        if self.moved:
            parts.append(f"↕{len(self.moved)} 移动")
        return ", ".join(parts) if parts else "无变化"


class IRDiff:
    """IR 文档差异比较器

    用法：
        diff = IRDiff()
        result = diff.compare(old_doc, new_doc)
        print(result.summary())
    """

    def compare(self, old_doc: IRDocument, new_doc: IRDocument) -> DiffResult:
        """比较两个文档

        Args:
            old_doc: 旧文档
            new_doc: 新文档

        Returns:
            DiffResult 实例
        """
        result = DiffResult()
        self._compare_nodes(old_doc.root, new_doc.root, "/document", result)
        result.has_changes = len(result.entries) > 0
        return result

    def _compare_nodes(
        self, old: IRNode, new: IRNode, path: str, result: DiffResult,
    ) -> None:
        """递归比较节点"""
        # 类型变化
        if old.node_type != new.node_type:
            result.entries.append(DiffEntry(
                diff_type=DiffType.MODIFY,
                node_path=path,
                old_value=old.node_type.value,
                new_value=new.node_type.value,
                field="node_type",
                details=f"节点类型从 {old.node_type.value} 变为 {new.node_type.value}",
            ))

        # 内容变化
        if old.content != new.content:
            result.entries.append(DiffEntry(
                diff_type=DiffType.MODIFY,
                node_path=path,
                old_value=old.content,
                new_value=new.content,
                field="content",
                details="内容变化",
            ))

        # 样式变化
        old_style = self._style_to_dict(old.style)
        new_style = self._style_to_dict(new.style)
        if old_style != new_style:
            changed_fields = []
            all_keys = set(list(old_style.keys()) + list(new_style.keys()))
            for key in all_keys:
                if old_style.get(key) != new_style.get(key):
                    changed_fields.append(key)
            result.entries.append(DiffEntry(
                diff_type=DiffType.MODIFY,
                node_path=path,
                old_value=old_style,
                new_value=new_style,
                field="style",
                details=f"样式变化: {', '.join(changed_fields)}",
            ))

        # 位置变化
        old_pos = self._pos_to_dict(old.position)
        new_pos = self._pos_to_dict(new.position)
        if old_pos != new_pos:
            result.entries.append(DiffEntry(
                diff_type=DiffType.MODIFY,
                node_path=path,
                old_value=old_pos,
                new_value=new_pos,
                field="position",
                details="位置变化",
            ))

        # 子节点比较
        old_children = old.children
        new_children = new.children
        max_len = max(len(old_children), len(new_children))

        for i in range(max_len):
            child_path = f"{path}/{old.node_type.value}[{i}]"
            if i >= len(old_children):
                result.entries.append(DiffEntry(
                    diff_type=DiffType.ADD,
                    node_path=child_path,
                    new_value=new_children[i].node_type.value,
                    details=f"新增子节点: {new_children[i].node_type.value}",
                ))
            elif i >= len(new_children):
                result.entries.append(DiffEntry(
                    diff_type=DiffType.REMOVE,
                    node_path=child_path,
                    old_value=old_children[i].node_type.value,
                    details=f"移除子节点: {old_children[i].node_type.value}",
                ))
            else:
                self._compare_nodes(old_children[i], new_children[i], child_path, result)

    def _style_to_dict(self, style: Any) -> dict:
        """将样式转换为可比较的字典"""
        if style is None:
            return {}
        if isinstance(style, dict):
            return style
        if hasattr(style, "__dict__"):
            return {k: v for k, v in style.__dict__.items() if v is not None}
        return {}

    def _pos_to_dict(self, pos: Any) -> dict:
        """将位置转换为可比较的字典"""
        if pos is None:
            return {}
        if isinstance(pos, dict):
            return pos
        if hasattr(pos, "__dict__"):
            return {k: v for k, v in pos.__dict__.items() if v is not None}
        return {}
