"""Skill 资源提供者 — 通过其他 Skill 获取资源

设计方案第五章：资源中枢。

Skill 提供者通过 Claude Code 的 Skill 系统获取：
  - matplotlib / seaborn → 图表图片
  - architecture-design → 流程图
  - deep-research → 研究报告
  - scientific-writing → 学术内容

source 格式：
  skill__matplotlib    — 调用 matplotlib 生成图表
  skill__chart         — 调用通用图表 Skill

注意：Skill 调用需要 Claude Code 环境。
本模块提供 Skill 注册和调用适配。
"""

from dataclasses import dataclass
from typing import Any, Callable

from ..registry import ResourceProvider, ResourceResult


@dataclass
class SkillDef:
    """Skill 定义"""
    name: str
    description: str = ""
    capabilities: list[str] | None = None
    output_format: str = "auto"  # auto, image, text, data


class SkillProvider:
    """Skill 资源提供者

    通过 Skill 系统获取资源。

    使用方式：
        provider = SkillProvider()
        provider.register_skill(SkillDef(name="matplotlib", ...))
        provider.set_executor("matplotlib", my_executor)
        result = provider.fetch({"skill": "matplotlib", "data": {...}})
    """

    name = "skill"
    prefixes = ["skill__", "skill:"]

    def __init__(self):
        self._skills: dict[str, SkillDef] = {}
        self._executors: dict[str, Callable] = {}

    def register_skill(self, skill: SkillDef) -> None:
        """注册 Skill"""
        self._skills[skill.name] = skill

    def set_executor(self, skill_name: str, executor: Callable) -> None:
        """设置 Skill 执行函数

        Args:
            skill_name: Skill 名称
            executor: 执行函数，签名 (params: dict) -> ResourceResult
        """
        self._executors[skill_name] = executor

    def can_handle(self, source: str | dict) -> bool:
        if isinstance(source, dict):
            return "skill" in source or "skill_name" in source
        if isinstance(source, str):
            return source.startswith("skill__") or source.startswith("skill:")
        return False

    def fetch(self, source: str | dict, **kwargs) -> ResourceResult:
        """获取 Skill 资源

        Args:
            source: 资源引用
                - "skill__matplotlib" 或 {"skill": "matplotlib", "data": {...}}

        Returns:
            ResourceResult
        """
        skill_name, params = self._parse_source(source, kwargs)

        if not skill_name:
            return ResourceResult(
                success=False,
                fallback_used=True,
                fallback_reason="无法解析 Skill 名称",
                error=f"Invalid skill source: {source}",
            )

        # 检查 Skill 是否注册
        if skill_name not in self._skills:
            return ResourceResult(
                success=False,
                fallback_used=True,
                fallback_reason=f"Skill {skill_name} 未注册",
                error=f"Skill not registered: {skill_name}",
            )

        # 检查是否有执行器
        executor = self._executors.get(skill_name)
        if not executor:
            return ResourceResult(
                success=False,
                fallback_used=True,
                fallback_reason=f"Skill {skill_name} 未配置执行器",
                error=f"No executor for skill: {skill_name}",
            )

        # 执行 Skill
        try:
            result = executor(params)
            if isinstance(result, ResourceResult):
                return result
            return ResourceResult(
                success=True,
                data=result,
                source_used=f"skill__{skill_name}",
            )
        except Exception as e:
            return ResourceResult(
                success=False,
                fallback_used=True,
                fallback_reason=f"Skill 执行异常: {e}",
                error=str(e),
            )

    def _parse_source(self, source: str | dict, kwargs: dict) -> tuple[str, dict]:
        """解析 source"""
        if isinstance(source, dict):
            name = source.get("skill", source.get("skill_name", ""))
            params = {k: v for k, v in source.items() if k not in ("skill", "skill_name")}
            params.update(kwargs)
            return name, params

        if isinstance(source, str):
            if source.startswith("skill__"):
                name = source[7:]
            elif source.startswith("skill:"):
                name = source[6:]
            else:
                return "", {}
            return name, dict(kwargs)

        return "", {}

    def list_skills(self) -> list[SkillDef]:
        """列出已注册的 Skill"""
        return list(self._skills.values())

    def get_skill(self, name: str) -> SkillDef | None:
        """获取 Skill 定义"""
        return self._skills.get(name)
