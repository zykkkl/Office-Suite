"""数据节点 — 数据转换

支持常见的转换操作：
  - 字段映射/重命名
  - 类型转换
  - 过滤/筛选
  - 聚合（sum/avg/count/max/min）
"""

from typing import Any

from ..base import NodeExecutor
from office_suite.pipeline.core.context import PipelineContext


class TransformNode(NodeExecutor):
    node_type = "transform"

    def execute(self, params: dict[str, Any], ctx: PipelineContext) -> Any:
        input_data = params.get("input") or params.get("data")

        # 解析变量引用
        if isinstance(input_data, str) and input_data.startswith("${"):
            ref = input_data[2:-1]
            input_data = ctx.resolve_ref(ref)

        if input_data is None:
            raise ValueError("transform: 缺少 input/data 参数")

        transform_type = params.get("transform", "passthrough")

        handlers = {
            "passthrough": self._passthrough,
            "map": self._map_fields,
            "filter": self._filter,
            "aggregate": self._aggregate,
        }

        handler = handlers.get(transform_type)
        if handler is None:
            raise ValueError(f"transform: 未知转换类型 '{transform_type}'")

        return handler(input_data, params)

    @staticmethod
    def _passthrough(data: Any, params: dict) -> Any:
        return data

    @staticmethod
    def _map_fields(data: Any, params: dict) -> Any:
        """字段映射 — 按映射表重命名字段"""
        mapping = params.get("mapping", {})
        if isinstance(data, dict):
            return {mapping.get(k, k): v for k, v in data.items()}
        if isinstance(data, list):
            return [
                {mapping.get(k, k): v for k, v in item.items()}
                for item in data
                if isinstance(item, dict)
            ]
        return data

    @staticmethod
    def _filter(data: Any, params: dict) -> Any:
        """过滤 — 按字段条件筛选列表项"""
        if not isinstance(data, list):
            return data
        field = params.get("field", "")
        op = params.get("op", "eq")
        value = params.get("value")

        # 支持的比较操作符
        operators = {
            "eq":  lambda a, b: a == b,
            "ne":  lambda a, b: a != b,
            "gt":  lambda a, b: a > b,
            "lt":  lambda a, b: a < b,
            "gte": lambda a, b: a >= b,
            "lte": lambda a, b: a <= b,
        }

        if op not in operators:
            raise ValueError(f"transform: 不支持的过滤操作符 '{op}'，合法值: {list(operators)}")

        compare = operators[op]

        result = []
        for item in data:
            if not isinstance(item, dict) or field not in item:
                continue
            item_val = item[field]
            try:
                if compare(item_val, value):
                    result.append(item)
            except TypeError:
                # 跳过无法比较的值，不中断整个过滤
                continue
        return result

    @staticmethod
    def _aggregate(data: Any, params: dict) -> Any:
        """聚合 — 对数值字段做统计"""
        if not isinstance(data, list):
            return data
        field = params.get("field", "")
        op = params.get("agg", "sum")

        values = [
            item[field] for item in data
            if isinstance(item, dict) and field in item
            and isinstance(item[field], (int, float))
        ]

        if not values:
            return {"result": None, "count": 0}

        if op == "sum":
            result = sum(values)
        elif op == "avg":
            result = sum(values) / len(values)
        elif op == "count":
            result = len(values)
        elif op == "max":
            result = max(values)
        elif op == "min":
            result = min(values)
        else:
            raise ValueError(f"transform: 未知聚合操作 '{op}'")

        return {"result": result, "count": len(values)}
