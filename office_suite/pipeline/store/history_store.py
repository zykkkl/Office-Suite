"""执行历史存储 — 记录流水线运行记录

记录每次流水线执行的元信息：时间、各节点状态、耗时、错误。
用于排查问题和性能分析。
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any


class HistoryStore:
    """执行历史存储

    使用示例：
        store = HistoryStore(base_dir="./history")
        store.record_start("Q4报告流水线")
        store.record_node("fetch_data", "success", 0.5)
        store.record_node("render_pptx", "failed", 2.3, error="超时")
        store.record_finish()
    """

    _run_counter: int = 0

    def __init__(self, base_dir: str | Path = "./history"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self._current: dict[str, Any] | None = None

    def record_start(self, pipeline_name: str, config: dict[str, Any] | None = None):
        """记录流水线开始执行"""
        self._current = {
            "pipeline_name": pipeline_name,
            "start_time": datetime.now().isoformat(),
            "config": config or {},
            "nodes": [],
            "status": "running",
        }

    def record_node(
        self,
        node_name: str,
        status: str,
        duration: float,
        error: str | None = None,
        metadata: dict[str, Any] | None = None,
    ):
        """记录单个节点的执行结果"""
        if self._current is None:
            return

        self._current["nodes"].append({
            "node_name": node_name,
            "status": status,
            "duration": duration,
            "error": error,
            "metadata": metadata or {},
        })

    def record_finish(self, status: str = "completed"):
        """记录流水线执行完成"""
        if self._current is None:
            return

        self._current["end_time"] = datetime.now().isoformat()
        self._current["status"] = status

        # 计算总耗时
        nodes = self._current["nodes"]
        self._current["total_duration"] = sum(n["duration"] for n in nodes)

        # 缓存后持久化
        record = self._current
        self._current = None
        self._save_record(record)

    def list_runs(
        self,
        pipeline_name: str | None = None,
        limit: int = 20,
    ) -> list[dict[str, Any]]:
        """查询历史记录"""
        runs = self._load_all()
        if pipeline_name:
            runs = [r for r in runs if r.get("pipeline_name") == pipeline_name]
        return runs[-limit:]

    def get_stats(self, pipeline_name: str) -> dict[str, Any]:
        """获取指定流水线的运行统计"""
        runs = [r for r in self._load_all() if r.get("pipeline_name") == pipeline_name]

        if not runs:
            return {"count": 0}

        durations = [r.get("total_duration", 0) for r in runs]
        successes = sum(1 for r in runs if r.get("status") == "completed")

        return {
            "count": len(runs),
            "success_rate": successes / len(runs),
            "avg_duration": sum(durations) / len(durations),
            "max_duration": max(durations),
            "min_duration": min(durations),
        }

    def _save_record(self, record: dict[str, Any]):
        HistoryStore._run_counter += 1
        timestamp = record["start_time"].replace(":", "-").replace(".", "-")
        filename = f"{record['pipeline_name']}_{timestamp}_{HistoryStore._run_counter}.json"
        filepath = self.base_dir / filename
        filepath.write_text(
            json.dumps(record, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def _load_all(self) -> list[dict[str, Any]]:
        records = []
        for filepath in sorted(self.base_dir.glob("*.json")):
            try:
                records.append(json.loads(filepath.read_text(encoding="utf-8")))
            except (json.JSONDecodeError, OSError):
                continue
        return records
