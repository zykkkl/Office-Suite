"""内联数据资源提供者 — 处理 data: URI 和内联 dict"""

from typing import Any

from ..registry import ResourceProvider, ResourceResult


class InlineDataProvider:
    """内联数据资源提供者

    支持的 source 格式：
      - "data:image/png;base64,..." — data URI
      - dict: { type: "chart", data: {...} } — 结构化数据
    """
    name = "inline_data"
    prefixes = ["data:"]

    def can_handle(self, source: str | dict) -> bool:
        if isinstance(source, str) and source.startswith("data:"):
            return True
        if isinstance(source, dict):
            return True
        return False

    def fetch(self, source: str | dict, **kwargs) -> ResourceResult:
        if isinstance(source, str) and source.startswith("data:"):
            # data URI 解析
            parts = source.split(",", 1)
            if len(parts) == 2:
                header = parts[0]  # data:image/png;base64
                data = parts[1]
                mime = header.split(";")[0].replace("data:", "")
                return ResourceResult(
                    success=True,
                    data=data,
                    mime_type=mime,
                    source_used="data_uri",
                )
            return ResourceResult(
                success=False,
                source_used=source,
                error="Invalid data URI format",
            )

        if isinstance(source, dict):
            return ResourceResult(
                success=True,
                data=source,
                mime_type="application/structured",
                source_used="inline_dict",
            )

        return ResourceResult(
            success=False,
            source_used=str(source),
            error="Unsupported inline format",
        )
