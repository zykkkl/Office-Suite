"""Pipeline 节点 + Store + 并行调度 测试"""

import os
import tempfile
from pathlib import Path

from office_suite.pipeline.nodes import list_registered, get_handler
from office_suite.pipeline.nodes.base import NodeExecutor
from office_suite.pipeline.core.graph import PipelineGraph, PipelineNode
from office_suite.pipeline.core.context import PipelineContext
from office_suite.pipeline.core.scheduler import PipelineScheduler
from office_suite.pipeline.store.artifact_store import ArtifactStore
from office_suite.pipeline.store.history_store import HistoryStore
from office_suite.pipeline.parser import parse_pipeline_string


# ── 注册机制 ──────────────────────────────────────────────

def test_all_nodes_registered():
    """15 个节点全部注册"""
    registered = list_registered()
    expected = [
        "ai_generate", "condition", "fetch", "layout", "mcp_call",
        "parallel", "render_docx", "render_html", "render_pdf",
        "render_pptx", "render_xlsx", "retry", "skill_invoke",
        "style", "transform",
    ]
    for name in expected:
        assert name in registered, f"节点 '{name}' 未注册"


def test_get_handler_returns_instance():
    """get_handler 返回正确类型的实例"""
    handler = get_handler("fetch")
    assert handler is not None
    assert hasattr(handler, "execute")


def test_get_handler_unknown_returns_none():
    """未知节点类型返回 None"""
    assert get_handler("nonexistent") is None


# ── Data 节点 ─────────────────────────────────────────────

def test_fetch_node_local_file():
    """fetch 节点获取本地文件"""
    with tempfile.NamedTemporaryFile(suffix=".txt", delete=False, mode="w") as f:
        f.write("hello pipeline")
        f.flush()
        path = f.name

    try:
        handler = get_handler("fetch")
        ctx = PipelineContext()
        result = handler.execute({"source": f"file://{path}"}, ctx)
        assert result["fallback_used"] is False or result["data"] is not None
    finally:
        os.unlink(path)


def test_fetch_node_missing_source():
    """fetch 节点缺少 source 参数抛异常"""
    handler = get_handler("fetch")
    ctx = PipelineContext()
    try:
        handler.execute({}, ctx)
        assert False, "应抛异常"
    except ValueError as e:
        assert "source" in str(e)


def test_transform_passthrough():
    """transform 的 passthrough 模式"""
    handler = get_handler("transform")
    ctx = PipelineContext()
    result = handler.execute({"input": {"a": 1}, "transform": "passthrough"}, ctx)
    assert result == {"a": 1}


def test_transform_map_fields():
    """transform 的字段映射"""
    handler = get_handler("transform")
    ctx = PipelineContext()
    result = handler.execute({
        "input": [{"name": "Alice", "age": 30}],
        "transform": "map",
        "mapping": {"name": "姓名", "age": "年龄"},
    }, ctx)
    assert result[0]["姓名"] == "Alice"
    assert result[0]["年龄"] == 30


def test_transform_filter():
    """transform 的过滤"""
    handler = get_handler("transform")
    ctx = PipelineContext()
    result = handler.execute({
        "input": [
            {"name": "A", "score": 90},
            {"name": "B", "score": 60},
            {"name": "C", "score": 75},
        ],
        "transform": "filter",
        "field": "score",
        "op": "gte",
        "value": 75,
    }, ctx)
    assert len(result) == 2
    assert result[0]["name"] == "A"


def test_transform_aggregate():
    """transform 的聚合"""
    handler = get_handler("transform")
    ctx = PipelineContext()
    result = handler.execute({
        "input": [
            {"revenue": 100},
            {"revenue": 200},
            {"revenue": 300},
        ],
        "transform": "aggregate",
        "field": "revenue",
        "agg": "sum",
    }, ctx)
    assert result["result"] == 600
    assert result["count"] == 3


def test_transform_variable_ref():
    """transform 从上下文解析变量引用"""
    handler = get_handler("transform")
    ctx = PipelineContext(variables={"mydata": [1, 2, 3]})
    # 设置输出让 resolve_ref 能找到
    ctx.set_output("upstream", [{"x": 10}, {"x": 20}])
    result = handler.execute({
        "input": "${upstream}",
        "transform": "passthrough",
    }, ctx)
    assert len(result) == 2
    assert result[0]["x"] == 10


# ── Control 节点 ──────────────────────────────────────────

def test_condition_true():
    """condition 节点 — 条件为真"""
    handler = get_handler("condition")
    ctx = PipelineContext()
    result = handler.execute({"condition": True}, ctx)
    assert result["condition"] is True
    assert result["branch"] == "then"


def test_condition_false():
    """condition 节点 — 条件为假"""
    handler = get_handler("condition")
    ctx = PipelineContext()
    result = handler.execute({"condition": False}, ctx)
    assert result["condition"] is False
    assert result["branch"] == "else"


def test_condition_expression():
    """condition 节点 — 比较表达式"""
    handler = get_handler("condition")
    ctx = PipelineContext()
    ctx.set_output("fetch_data", {"count": 5})
    result = handler.execute({"condition": "5 > 0"}, ctx)
    assert result["condition"] is True


def test_retry_success_first_try():
    """retry 节点 — 首次成功"""
    handler = get_handler("retry")
    ctx = PipelineContext()
    result = handler.execute({
        "executor": lambda params, ctx: {"ok": True},
        "max_retries": 3,
    }, ctx)
    assert result["success"] is True
    assert result["attempts"] == 1


def test_retry_all_fail():
    """retry 节点 — 全部失败"""
    call_count = 0

    def failing_executor(params, ctx):
        nonlocal call_count
        call_count += 1
        raise RuntimeError(f"fail #{call_count}")

    handler = get_handler("retry")
    ctx = PipelineContext()
    result = handler.execute({
        "executor": failing_executor,
        "max_retries": 2,
        "initial_delay": 0.01,
        "backoff": "fixed",
    }, ctx)
    assert result["success"] is False
    assert result["attempts"] == 3  # 1 初始 + 2 重试


def test_parallel_node():
    """parallel 节点 — 声明并行分支"""
    handler = get_handler("parallel")
    ctx = PipelineContext()
    result = handler.execute({"branches": ["task_a", "task_b", "task_c"]}, ctx)
    assert len(result["branches"]) == 3


# ── Compute 节点（骨架） ──────────────────────────────────

def test_skill_invoke_node():
    """skill_invoke 节点 — 骨架返回 pending_provider"""
    handler = get_handler("skill_invoke")
    ctx = PipelineContext()
    result = handler.execute({"skill": "deep-research", "params": {"query": "AI"}}, ctx)
    assert result["skill"] == "deep-research"
    assert result["status"] == "pending_provider"


def test_mcp_call_node():
    """mcp_call 节点 — 骨架返回 pending_provider"""
    handler = get_handler("mcp_call")
    ctx = PipelineContext()
    result = handler.execute({"server": "unsplash", "method": "search"}, ctx)
    assert result["server"] == "unsplash"
    assert result["status"] == "pending_provider"


def test_ai_generate_node():
    """ai_generate 节点 — 骨架返回 pending_provider"""
    handler = get_handler("ai_generate")
    ctx = PipelineContext()
    result = handler.execute({"prompt": "生成封面图", "output_type": "image"}, ctx)
    assert result["output_type"] == "image"
    assert result["status"] == "pending_provider"


# ── Scheduler 注册表集成 ───────────────────────────────────

def test_scheduler_uses_registry():
    """scheduler 通过注册表执行节点"""
    graph = PipelineGraph(name="test_registry")
    graph.add_node(PipelineNode(
        name="transform_data",
        node_type="transform",
        params={"input": {"x": 1}, "transform": "passthrough"},
    ))
    scheduler = PipelineScheduler(graph)
    results = scheduler.run()
    assert results["transform_data"]["status"] == "success"
    assert results["transform_data"]["result"] == {"x": 1}


def test_scheduler_unknown_type_with_no_executor():
    """scheduler 遇到未知类型且无 executor 报错"""
    graph = PipelineGraph(name="test_unknown")
    graph.add_node(PipelineNode(
        name="bad_node",
        node_type="nonexistent_type",
    ))
    scheduler = PipelineScheduler(graph)
    results = scheduler.run()
    assert results["bad_node"]["status"] == "failed"


# ── Store ──────────────────────────────────────────────────

def test_artifact_store_save_and_list():
    """ArtifactStore 保存和查询"""
    with tempfile.TemporaryDirectory() as tmpdir:
        store = ArtifactStore(base_dir=tmpdir)
        store.save("render_pptx", {"path": "output.pptx"})
        store.save("render_pdf", {"path": "output.pdf"})
        store.save("render_pptx", {"path": "output2.pptx"})

        all_artifacts = store.list_artifacts()
        assert len(all_artifacts) == 3

        pptx_artifacts = store.list_artifacts(node_name="render_pptx")
        assert len(pptx_artifacts) == 2

        latest = store.get_latest("render_pptx")
        assert latest["result"]["path"] == "output2.pptx"


def test_artifact_store_with_file():
    """ArtifactStore 保存文件"""
    with tempfile.TemporaryDirectory() as tmpdir:
        # 创建临时文件
        src = Path(tmpdir) / "source.pptx"
        src.write_text("fake pptx")

        store = ArtifactStore(base_dir=Path(tmpdir) / "store")
        record = store.save("render_pptx", {"path": "output.pptx"}, file_path=src)
        assert "stored_path" in record

        latest = store.get_latest("render_pptx")
        assert latest["stored_path"]


def test_history_store_record():
    """HistoryStore 记录执行历史"""
    with tempfile.TemporaryDirectory() as tmpdir:
        store = HistoryStore(base_dir=tmpdir)
        store.record_start("测试流水线")
        store.record_node("fetch", "success", 0.5)
        store.record_node("render", "success", 1.2)
        store.record_finish()

        runs = store.list_runs()
        assert len(runs) == 1
        assert runs[0]["pipeline_name"] == "测试流水线"
        assert runs[0]["total_duration"] == 1.7


def test_history_store_stats():
    """HistoryStore 统计"""
    with tempfile.TemporaryDirectory() as tmpdir:
        store = HistoryStore(base_dir=tmpdir)
        for i in range(3):
            store.record_start("Q4流水线")
            store.record_node("fetch", "success", 0.5 + i * 0.1)
            store.record_finish()

        stats = store.get_stats("Q4流水线")
        assert stats["count"] == 3
        assert stats["success_rate"] == 1.0


# ── 并行调度 ────────────────────────────────────────────────

def test_parallel_scheduler():
    """并行调度器 — 同层节点并发执行"""
    import time

    graph = PipelineGraph(name="parallel_test", config={"parallelism": 4})
    graph.add_node(PipelineNode(
        name="step_a",
        node_type="transform",
        params={"input": "a", "transform": "passthrough"},
    ))
    graph.add_node(PipelineNode(
        name="step_b",
        node_type="transform",
        params={"input": "b", "transform": "passthrough"},
    ))
    graph.add_node(PipelineNode(
        name="merge",
        node_type="transform",
        depends_on=["step_a", "step_b"],
        params={"input": "merged", "transform": "passthrough"},
    ))

    scheduler = PipelineScheduler(graph)
    results = scheduler.run_parallel()
    assert results["step_a"]["status"] == "success"
    assert results["step_b"]["status"] == "success"
    assert results["merge"]["status"] == "success"


# ── Pipeline YAML + 注册表 ─────────────────────────────────

def test_pipeline_yaml_with_registered_nodes():
    """从 YAML 解析并使用注册表执行"""
    yaml_str = """
name: "数据转换流水线"
graph:
  step1:
    type: transform
    params:
      input: {"values": [1, 2, 3]}
      transform: passthrough
  step2:
    type: condition
    depends_on: [step1]
    params:
      condition: true
"""
    graph = parse_pipeline_string(yaml_str)
    assert graph.name == "数据转换流水线"
    assert len(graph.nodes) == 2

    scheduler = PipelineScheduler(graph)
    results = scheduler.run()
    assert results["step1"]["status"] == "success"
    assert results["step2"]["status"] == "success"
    assert results["step2"]["result"]["condition"] is True
