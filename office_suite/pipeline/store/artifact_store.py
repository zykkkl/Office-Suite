"""产物存储 — 持久化节点产出

将流水线节点的产出物保存到磁盘，并维护索引以便后续查询。
"""

import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any


class ArtifactStore:
    """产物存储

    使用示例：
        store = ArtifactStore(base_dir="./artifacts")
        store.save("render_pptx", {"path": "output.pptx"}, Path("output.pptx"))
        artifacts = store.list_artifacts(node_name="render_pptx")
    """

    def __init__(self, base_dir: str | Path = "./artifacts"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self._index_file = self.base_dir / "_index.json"
        self._index: list[dict[str, Any]] = self._load_index()

    def save(
        self,
        node_name: str,
        result: Any,
        file_path: Path | str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """保存产物

        Args:
            node_name: 产出节点名称
            result: 节点执行结果
            file_path: 产物文件路径（如有）
            metadata: 额外元数据

        Returns:
            产物记录
        """
        artifact = {
            "node_name": node_name,
            "timestamp": datetime.now().isoformat(),
            "result": result if not isinstance(result, Path) else str(result),
            "metadata": metadata or {},
        }

        # 复制文件到产物目录
        if file_path is not None:
            file_path = Path(file_path)
            if file_path.exists():
                dest = self.base_dir / node_name / file_path.name
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(file_path, dest)
                artifact["stored_path"] = str(dest)
                artifact["original_path"] = str(file_path)

        self._index.append(artifact)
        self._save_index()
        return artifact

    def list_artifacts(
        self,
        node_name: str | None = None,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        """查询产物列表"""
        results = self._index
        if node_name:
            results = [a for a in results if a["node_name"] == node_name]
        return results[-limit:]

    def get_latest(self, node_name: str) -> dict[str, Any] | None:
        """获取指定节点的最新产物"""
        matching = [a for a in self._index if a["node_name"] == node_name]
        return matching[-1] if matching else None

    def _load_index(self) -> list[dict[str, Any]]:
        if self._index_file.exists():
            try:
                return json.loads(self._index_file.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                return []
        return []

    def _save_index(self):
        self._index_file.write_text(
            json.dumps(self._index, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
