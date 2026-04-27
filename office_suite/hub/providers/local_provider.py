"""本地文件资源提供者 — 处理 file:// 和本地路径引用"""

from pathlib import Path
from typing import Any

from ..registry import ResourceProvider, ResourceResult


class LocalFileProvider:
    """本地文件资源提供者

    支持的 source 格式：
      - "file://path/to/file.png"
      - "path/to/file.png"（相对路径）
      - "/absolute/path/to/file.png"
    """
    name = "local_file"
    prefixes = ["file://", "/", "./", "../"]

    def can_handle(self, source: str | dict) -> bool:
        if isinstance(source, dict):
            return False
        if source.startswith("file://"):
            return True
        # 检查是否是本地文件路径
        path = Path(source)
        return path.exists() or path.suffix != ""

    def fetch(self, source: str | dict, **kwargs) -> ResourceResult:
        path_str = source
        if isinstance(source, str) and source.startswith("file://"):
            path_str = source[7:]

        path = Path(path_str)
        if not path.is_absolute():
            # 相对于当前工作目录或项目根目录
            base = kwargs.get("base_dir", Path.cwd())
            path = base / path

        if not path.exists():
            return ResourceResult(
                success=False,
                source_used=source,
                fallback_used=True,
                fallback_reason=f"文件不存在: {path}",
                error=f"File not found: {path}",
            )

        # 推断 MIME 类型
        mime_map = {
            ".png": "image/png",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".gif": "image/gif",
            ".svg": "image/svg+xml",
            ".bmp": "image/bmp",
            ".csv": "text/csv",
            ".json": "application/json",
            ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        }
        mime_type = mime_map.get(path.suffix.lower(), "application/octet-stream")

        return ResourceResult(
            success=True,
            data=path,
            mime_type=mime_type,
            source_used=source,
        )
