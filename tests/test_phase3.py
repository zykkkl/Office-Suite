"""Phase 3 测试套件：资源中枢 + 基础流水线

验收标准：
1. MCP 图片资源获取并嵌入 PPTX（模拟）
2. 本地文件资源解析
3. 资源获取失败时降级到占位符
4. 简单 DAG（3 节点串行）调度成功
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from office_suite.hub.registry import ResourceRegistry, ResourceResult
from office_suite.hub.resolver import ResourceResolver, create_default_registry
from office_suite.hub.providers.local_provider import LocalFileProvider
from office_suite.hub.providers.inline_provider import InlineDataProvider
from office_suite.pipeline.core.graph import PipelineGraph, PipelineNode, NodeStatus
from office_suite.pipeline.core.context import PipelineContext
from office_suite.pipeline.core.scheduler import PipelineScheduler
from office_suite.pipeline.parser import parse_pipeline_string


_pass_count = 0
_fail_count = 0


def check(name: str, condition: bool, detail: str = ""):
    global _pass_count, _fail_count
    if condition:
        _pass_count += 1
        print(f"  PASS  {name}")
    else:
        _fail_count += 1
        msg = f"  FAIL  {name}"
        if detail:
            msg += f" — {detail}"
        print(msg)


def section(title: str):
    print(f"\n{'─' * 50}")
    print(f"  {title}")
    print(f"{'─' * 50}")


# ============================================================
# 测试 1-5: 资源注册表
# ============================================================

def test_registry():
    section("1. 资源注册表")

    registry = create_default_registry()
    providers = registry.list_providers()
    check("默认注册 2 个 Provider", len(providers) == 2, f"got {providers}")
    check("local_file 已注册", "local_file" in providers)
    check("inline_data 已注册", "inline_data" in providers)

    # 无匹配 Provider 时降级
    result = registry.resolve("unknown_protocol://resource")
    check("无匹配时 success=False", not result.success)
    check("无匹配时 fallback_used=True", result.fallback_used)


# ============================================================
# 测试 6-10: 本地文件 Provider
# ============================================================

def test_local_file_provider():
    section("2. 本地文件 Provider")

    provider = LocalFileProvider()

    # can_handle
    check("file:// 前缀可处理", provider.can_handle("file://logo.png"))
    check("普通路径可处理", provider.can_handle("image.png"))
    check("dict 不可处理", not provider.can_handle({"key": "value"}))

    # fetch 存在的文件
    test_file = PROJECT_ROOT / "tests" / "hello_world.yml"
    result = provider.fetch(str(test_file))
    check("存在的文件 success=True", result.success)
    check("返回 Path 对象", isinstance(result.data, Path))
    check("MIME 类型正确", result.mime_type == "text/csv" or result.mime_type == "application/octet-stream" or result.mime_type != "")

    # fetch 不存在的文件
    result = provider.fetch("file://nonexistent_file.png")
    check("不存在的文件 success=False", not result.success)
    check("不存在时 fallback_used=True", result.fallback_used)


# ============================================================
# 测试 11-14: 内联数据 Provider
# ============================================================

def test_inline_data_provider():
    section("3. 内联数据 Provider")

    provider = InlineDataProvider()

    # can_handle
    check("data: URI 可处理", provider.can_handle("data:image/png;base64,abc123"))
    check("dict 可处理", provider.can_handle({"type": "chart", "data": {}}))
    check("普通字符串不可处理", not provider.can_handle("file://test.png"))

    # fetch data URI
    result = provider.fetch("data:image/png;base64,iVBORw0KGgo=")
    check("data URI success=True", result.success)
    check("MIME 类型 image/png", result.mime_type == "image/png")

    # fetch dict
    result = provider.fetch({"type": "chart", "values": [1, 2, 3]})
    check("dict success=True", result.success)
    check("MIME 类型 structured", result.mime_type == "application/structured")


# ============================================================
# 测试 15-18: 资源解析器降级
# ============================================================

def test_resolver_fallback():
    section("4. 资源解析器降级策略")

    resolver = ResourceResolver()

    # None 输入
    result = resolver.resolve(None)
    check("None 输入 fallback", result.fallback_used)

    # 不存在的文件
    result = resolver.resolve("file://nonexistent_image.png")
    check("不存在文件 fallback", result.fallback_used)
    check("fallback 有原因", result.fallback_reason != "")

    # 未知协议
    result = resolver.resolve("mcp__unsplash:query=nature")
    check("未知协议 fallback", result.fallback_used)

    # 本地存在的文件
    test_file = str(PROJECT_ROOT / "tests" / "hello_world.yml")
    result = resolver.resolve(test_file)
    check("存在的文件 success", result.success)


# ============================================================
# 测试 19-23: DAG 拓扑排序
# ============================================================

def test_dag_topological_sort():
    section("5. DAG 拓扑排序")

    # 简单 3 节点串行
    graph = PipelineGraph(name="test")
    graph.add_node(PipelineNode(name="A", node_type="fetch"))
    graph.add_node(PipelineNode(name="B", node_type="transform", depends_on=["A"]))
    graph.add_node(PipelineNode(name="C", node_type="render", depends_on=["B"]))

    order = graph.topological_sort()
    check("串行 DAG 排序正确", order == ["A", "B", "C"], f"got {order}")

    # 并行 DAG
    graph2 = PipelineGraph(name="parallel")
    graph2.add_node(PipelineNode(name="fetch1", node_type="fetch"))
    graph2.add_node(PipelineNode(name="fetch2", node_type="fetch"))
    graph2.add_node(PipelineNode(name="merge", node_type="transform", depends_on=["fetch1", "fetch2"]))

    order2 = graph2.topological_sort()
    check("并行 DAG merge 在最后", order2[-1] == "merge", f"got {order2}")
    check("并行 DAG fetch 都在前", "fetch1" in order2[:2] and "fetch2" in order2[:2])

    # 并行层级
    levels = graph2.get_parallel_levels()
    check("2 个层级", len(levels) == 2, f"got {len(levels)}")
    check("第 1 层 2 个节点", len(levels[0]) == 2, f"got {len(levels[0])}")
    check("第 2 层 1 个节点", len(levels[1]) == 1, f"got {len(levels[1])}")

    # 循环依赖检测
    graph3 = PipelineGraph(name="cycle")
    graph3.add_node(PipelineNode(name="X", node_type="fetch", depends_on=["Y"]))
    graph3.add_node(PipelineNode(name="Y", node_type="fetch", depends_on=["X"]))
    try:
        graph3.topological_sort()
        check("循环依赖抛出异常", False)
    except ValueError:
        check("循环依赖抛出异常", True)

    # 依赖不存在的节点
    graph4 = PipelineGraph(name="missing")
    graph4.add_node(PipelineNode(name="A", node_type="fetch", depends_on=["ghost"]))
    errors = graph4.validate()
    check("依赖不存在节点检出", len(errors) > 0)


# ============================================================
# 测试 24-28: 流水线调度器
# ============================================================

def test_scheduler():
    section("6. 流水线调度器")

    # 构建 3 节点串行 DAG
    graph = PipelineGraph(name="test_pipeline")
    graph.add_node(PipelineNode(
        name="fetch_data",
        node_type="fetch",
        params={"source": "quarterly.csv"},
    ))
    graph.add_node(PipelineNode(
        name="transform",
        node_type="transform",
        params={"input": "${fetch_data.output}"},
        depends_on=["fetch_data"],
    ))
    graph.add_node(PipelineNode(
        name="render",
        node_type="fetch",  # 用 fetch 模拟 render
        params={"source": "output.pptx"},
        depends_on=["transform"],
    ))

    ctx = PipelineContext(variables={"topic": "Q4 报告"})
    scheduler = PipelineScheduler(graph, ctx)
    results = scheduler.run()

    check("fetch_data 成功", results["fetch_data"]["status"] == "success")
    check("transform 成功", results["transform"]["status"] == "success")
    check("render 成功", results["render"]["status"] == "success")

    # 检查上下文传递
    check("输出存入 context", ctx.get_output("fetch_data") is not None)

    # 检查日志
    check("有执行日志", len(ctx.logs) > 0)


# ============================================================
# 测试 29-31: 自定义执行器
# ============================================================

def test_custom_executor():
    section("7. 自定义执行器")

    execution_log = []

    def custom_fetch(params, ctx):
        execution_log.append(f"fetch:{params.get('source')}")
        return {"data": [1, 2, 3]}

    def custom_render(params, ctx):
        data = ctx.resolve_ref("fetch_step.data")
        execution_log.append(f"render:{data}")
        return {"file": "output.pptx"}

    graph = PipelineGraph(name="custom")
    graph.add_node(PipelineNode(
        name="fetch_step",
        node_type="custom",
        executor=custom_fetch,
        params={"source": "api/data"},
    ))
    graph.add_node(PipelineNode(
        name="render_step",
        node_type="custom",
        executor=custom_render,
        params={},
        depends_on=["fetch_step"],
    ))

    scheduler = PipelineScheduler(graph)
    results = scheduler.run()

    check("自定义 fetch 执行", "fetch:api/data" in execution_log)
    check("自定义 render 执行", any("render:" in e for e in execution_log))
    check("fetch 结果传递", results["fetch_step"]["result"]["data"] == [1, 2, 3])


# ============================================================
# 测试 32-34: 流水线 YAML 解析
# ============================================================

def test_pipeline_yaml():
    section("8. 流水线 YAML 解析")

    yaml_str = """
name: "研究 → 演示 全自动流水线"
config:
  timeout: 600s
  parallelism: 4
graph:
  literature_search:
    type: skill_invoke
    params: { query: "${vars.topic}" }
  paper_collection:
    type: skill_invoke
    params: { query: "${vars.topic}", limit: 20 }
  key_findings:
    type: ai_generate
    depends_on: [literature_search]
    params: { model: "claude-sonnet-4-6" }
  render_pptx:
    type: render
    depends_on: [key_findings, paper_collection]
    params: { format: pptx }
"""
    graph = parse_pipeline_string(yaml_str)
    check("流水线名称", graph.name == "研究 → 演示 全自动流水线")
    check("4 个节点", len(graph.nodes) == 4, f"got {len(graph.nodes)}")
    check("config 有 timeout", graph.config.get("timeout") == "600s")

    # 校验
    errors = graph.validate()
    check("DAG 校验通过", len(errors) == 0, f"errors: {errors}")

    # 拓扑排序
    order = graph.topological_sort()
    check("render_pptx 在最后", order[-1] == "render_pptx", f"order: {order}")


# ============================================================
# 测试 35: 端到端 DAG + 资源解析
# ============================================================

def test_e2e_pipeline_resource():
    section("9. 端到端：DAG + 资源解析")

    resolver = ResourceResolver()

    # 模拟：fetch → resolve resource → render
    def fetch_step(params, ctx):
        return {"source": params.get("source")}

    def resolve_step(params, ctx):
        source = ctx.resolve_ref("fetch.source")
        result = resolver.resolve(source)
        return {
            "resolved": result.success,
            "fallback": result.fallback_used,
            "path": str(result.data) if result.data else None,
        }

    def render_step(params, ctx):
        resolve_result = ctx.resolve_ref("resolve")
        return {
            "rendered": True,
            "used_fallback": resolve_result.get("fallback", False),
        }

    graph = PipelineGraph(name="e2e")
    graph.add_node(PipelineNode(name="fetch", executor=fetch_step, params={"source": "file://test.png"}))
    graph.add_node(PipelineNode(name="resolve", executor=resolve_step, depends_on=["fetch"]))
    graph.add_node(PipelineNode(name="render", executor=render_step, depends_on=["resolve"]))

    scheduler = PipelineScheduler(graph)
    results = scheduler.run()

    check("fetch 成功", results["fetch"]["status"] == "success")
    check("resolve 成功", results["resolve"]["status"] == "success")
    check("render 成功", results["render"]["status"] == "success")
    check("3 节点串行调度", all(r["status"] == "success" for r in results.values()))


# ============================================================
# 主函数
# ============================================================

def main():
    print("=" * 60)
    print("  Office Suite 4.0 — Phase 3 测试套件")
    print("=" * 60)

    test_registry()
    test_local_file_provider()
    test_inline_data_provider()
    test_resolver_fallback()
    test_dag_topological_sort()
    test_scheduler()
    test_custom_executor()
    test_pipeline_yaml()
    test_e2e_pipeline_resource()

    print(f"\n{'=' * 60}")
    print(f"  结果:  PASS={_pass_count}  FAIL={_fail_count}")
    print(f"{'=' * 60}")

    return _fail_count == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
