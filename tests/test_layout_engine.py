"""布局引擎集成测试 — Grid / Flex / Constraint

验证 LayoutResolver 正确桥接 engine/layout 引擎与 IRPosition。
"""

from office_suite.ir.types import IRDocument, IRNode, IRPosition, IRStyle, NodeType
from office_suite.renderer.layout_resolver import LayoutResolver, detect_layout_mode


# ============================================================
# 辅助函数
# ============================================================

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
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")


# ============================================================
# 测试
# ============================================================

def test_detect_layout_mode():
    section("布局模式检测")

    # 默认 absolute
    node = IRNode(node_type=NodeType.SLIDE)
    check("默认模式为 absolute", detect_layout_mode(node) == "absolute")

    # 显式声明
    node = IRNode(node_type=NodeType.SLIDE, extra={"layout_mode": "grid"})
    check("显式声明 grid", detect_layout_mode(node) == "grid")

    node = IRNode(node_type=NodeType.SLIDE, extra={"layout_mode": "flex"})
    check("显式声明 flex", detect_layout_mode(node) == "flex")

    node = IRNode(node_type=NodeType.SLIDE, extra={"layout_mode": "constraint"})
    check("显式声明 constraint", detect_layout_mode(node) == "constraint")

    # 推断模式
    node = IRNode(node_type=NodeType.SLIDE, extra={"grid": {"columns": 12}})
    check("推断 grid 模式", detect_layout_mode(node) == "grid")

    node = IRNode(node_type=NodeType.SLIDE, extra={"flex": {"direction": "row"}})
    check("推断 flex 模式", detect_layout_mode(node) == "flex")

    node = IRNode(node_type=NodeType.SLIDE, extra={"constraints": []})
    check("推断 constraint 模式", detect_layout_mode(node) == "constraint")


def test_absolute_resolve():
    section("绝对布局解析")

    child1 = IRNode(
        node_type=NodeType.TEXT,
        id="title",
        content="Hello",
        position=IRPosition(x_mm=10, y_mm=20, width_mm=100, height_mm=30),
    )
    child2 = IRNode(
        node_type=NodeType.TEXT,
        id="subtitle",
        content="World",
        position=IRPosition(x_mm=10, y_mm=60, width_mm=100, height_mm=20),
    )
    slide = IRNode(
        node_type=NodeType.SLIDE,
        children=[child1, child2],
    )

    resolver = LayoutResolver(254.0, 142.875)
    positions = resolver.resolve_children(slide)

    check("绝对布局解析 2 个元素", len(positions) == 2)
    check("title 位置正确",
          positions["title"].x_mm == 10 and positions["title"].y_mm == 20,
          f"x={positions['title'].x_mm}, y={positions['title'].y_mm}")
    check("subtitle 位置正确",
          positions["subtitle"].x_mm == 10 and positions["subtitle"].y_mm == 60)


def test_relative_resolve():
    section("相对布局解析")

    child = IRNode(
        node_type=NodeType.TEXT,
        id="centered",
        content="Center",
        position=IRPosition(x_mm=20, y_mm=30, width_mm=60, height_mm=50, is_relative=True),
    )
    slide = IRNode(
        node_type=NodeType.SLIDE,
        children=[child],
    )

    resolver = LayoutResolver(254.0, 142.875)
    positions = resolver.resolve_children(slide)

    pos = positions["centered"]
    # 20% of 254 = 50.8, 30% of 142.875 = 42.8625
    check("相对 X 转换正确",
          abs(pos.x_mm - 50.8) < 0.1,
          f"expected ~50.8, got {pos.x_mm}")
    check("相对 Y 转换正确",
          abs(pos.y_mm - 42.8625) < 0.1,
          f"expected ~42.86, got {pos.y_mm}")


def test_grid_resolve():
    section("栅格布局解析")

    # 12 列栅格，2 个元素各占 6 列
    child1 = IRNode(
        node_type=NodeType.TEXT,
        id="left",
        content="Left",
        extra={"grid": {"column": 1, "span": 6, "row": 1}},
    )
    child2 = IRNode(
        node_type=NodeType.TEXT,
        id="right",
        content="Right",
        extra={"grid": {"column": 7, "span": 6, "row": 1}},
    )
    slide = IRNode(
        node_type=NodeType.SLIDE,
        extra={"grid": {"columns": 12, "gutter": 2.0}},
        children=[child1, child2],
    )

    resolver = LayoutResolver(254.0, 142.875)
    positions = resolver.resolve_children(slide)

    left_pos = positions["left"]
    right_pos = positions["right"]

    check("栅格 left.x = 0", left_pos.x_mm == 0.0, f"x={left_pos.x_mm}")
    check("栅格 right.x > 0", right_pos.x_mm > 0, f"x={right_pos.x_mm}")
    check("栅格 left.width > 0", left_pos.width_mm > 0, f"w={left_pos.width_mm}")
    check("栅格 right.width > 0", right_pos.width_mm > 0, f"w={right_pos.width_mm}")
    # 两元素宽度应相等
    check("栅格两列等宽",
          abs(left_pos.width_mm - right_pos.width_mm) < 0.1,
          f"left={left_pos.width_mm}, right={right_pos.width_mm}")


def test_flex_resolve():
    section("弹性布局解析")

    # 3 个等宽元素水平排列
    children = []
    for i in range(3):
        children.append(IRNode(
            node_type=NodeType.TEXT,
            id=f"item_{i}",
            content=f"Item {i}",
            extra={"flex": {"grow": 1}},
        ))

    slide = IRNode(
        node_type=NodeType.SLIDE,
        extra={"flex": {"direction": "row", "gap": 5}},
        children=children,
    )

    resolver = LayoutResolver(254.0, 142.875)
    positions = resolver.resolve_children(slide)

    check("弹性布局解析 3 个元素", len(positions) == 3)

    # 所有元素宽度应相等
    widths = [positions[f"item_{i}"].width_mm for i in range(3)]
    check("弹性布局等宽分配",
          all(abs(w - widths[0]) < 0.1 for w in widths),
          f"widths={widths}")

    # 间隔检查：第二个元素的 x 应大于第一个元素的 x + width
    pos0 = positions["item_0"]
    pos1 = positions["item_1"]
    check("弹性布局间隔正确",
          pos1.x_mm > pos0.x_mm + pos0.width_mm,
          f"item_0 right={pos0.x_mm + pos0.width_mm}, item_1 x={pos1.x_mm}")


def test_flex_column():
    section("弹性布局 — 列方向")

    children = []
    for i in range(3):
        children.append(IRNode(
            node_type=NodeType.TEXT,
            id=f"row_{i}",
            content=f"Row {i}",
            extra={"flex": {"grow": 1}},
        ))

    slide = IRNode(
        node_type=NodeType.SLIDE,
        extra={"flex": {"direction": "column", "gap": 3}},
        children=children,
    )

    resolver = LayoutResolver(254.0, 142.875)
    positions = resolver.resolve_children(slide)

    # Y 坐标应递增
    ys = [positions[f"row_{i}"].y_mm for i in range(3)]
    check("列方向 Y 递增",
          ys[0] < ys[1] < ys[2],
          f"y values: {ys}")


def test_constraint_resolve():
    section("约束布局解析")

    # 元素约束：width=100, height=30, x=居中
    child = IRNode(
        node_type=NodeType.TEXT,
        id="centered_box",
        content="Centered",
        position=IRPosition(width_mm=100, height_mm=30),
        extra={"constraints": [
            {"type": "eq", "lhs": {"var": "self.width"}, "rhs": {"value": 100}},
            {"type": "eq", "lhs": {"var": "self.height"}, "rhs": {"value": 30}},
            # center_x = parent.width / 2 → x = (parent.width - width) / 2
            # 这里用等式约束 x = 77 (254-100)/2
            {"type": "eq", "lhs": {"var": "self.x"}, "rhs": {"value": 77}},
            {"type": "eq", "lhs": {"var": "self.y"}, "rhs": {"value": 56}},
        ]},
    )
    slide = IRNode(
        node_type=NodeType.SLIDE,
        extra={"layout_mode": "constraint"},
        children=[child],
    )

    resolver = LayoutResolver(254.0, 142.875)
    positions = resolver.resolve_children(slide)

    pos = positions["centered_box"]
    check("约束布局 width=100", pos.width_mm == 100, f"w={pos.width_mm}")
    check("约束布局 height=30", pos.height_mm == 30, f"h={pos.height_mm}")
    check("约束布局 x=77", pos.x_mm == 77, f"x={pos.x_mm}")
    check("约束布局 y=56", pos.y_mm == 56, f"y={pos.y_mm}")


def test_pptx_renderer_integration():
    section("PPTX 渲染器集成 — Grid 布局渲染")

    from office_suite.renderer.pptx.deck import PPTXRenderer
    import tempfile, os

    child1 = IRNode(
        node_type=NodeType.TEXT,
        id="left",
        content="Left Column",
        extra={"grid": {"column": 1, "span": 6, "row": 1}},
    )
    child2 = IRNode(
        node_type=NodeType.TEXT,
        id="right",
        content="Right Column",
        extra={"grid": {"column": 7, "span": 6, "row": 1}},
    )
    slide = IRNode(
        node_type=NodeType.SLIDE,
        extra={"layout": "blank", "grid": {"columns": 12, "gutter": 2}},
        children=[child1, child2],
    )
    doc = IRDocument(children=[slide])

    renderer = PPTXRenderer()
    with tempfile.NamedTemporaryFile(suffix=".pptx", delete=False) as f:
        out_path = f.name

    try:
        result = renderer.render(doc, out_path)
        check("Grid 布局 PPTX 渲染成功", result.exists(), f"path={result}")
        check("输出文件有内容", result.stat().st_size > 0, f"size={result.stat().st_size}")
    finally:
        os.unlink(out_path)


def test_mixed_layout():
    section("混合布局 — Grid + 绝对坐标")

    # Grid 布局的子元素 + 一个绝对坐标元素
    grid_child = IRNode(
        node_type=NodeType.TEXT,
        id="gridded",
        content="Grid",
        extra={"grid": {"column": 1, "span": 6, "row": 1}},
    )
    abs_child = IRNode(
        node_type=NodeType.TEXT,
        id="absolute",
        content="Absolute",
        position=IRPosition(x_mm=10, y_mm=100, width_mm=50, height_mm=20),
    )
    slide = IRNode(
        node_type=NodeType.SLIDE,
        extra={"grid": {"columns": 12}},
        children=[grid_child, abs_child],
    )

    resolver = LayoutResolver(254.0, 142.875)
    positions = resolver.resolve_children(slide)

    check("Grid 元素有位置", "gridded" in positions)
    check("绝对坐标元素有位置", "absolute" in positions)
    check("绝对坐标元素保持原位",
          positions["absolute"].x_mm == 10,
          f"x={positions['absolute'].x_mm}")


# ============================================================
# Cassowary Simplex 求解器测试
# ============================================================

def test_simplex_multi_variable():
    """多变量等式约束 — simple求解器联动"""
    section("Simplex 多变量联动")

    from office_suite.engine.layout.constraint import Solver, eq, le, ge, Priority

    solver = Solver()
    x = solver.add_variable("x", 0.0)
    y = solver.add_variable("y", 0.0)
    w = solver.add_variable("w", 50.0)
    h = solver.add_variable("h", 30.0)

    # right = x + w
    solver.add_constraint(eq(
        solver.get_variable("right") or solver.add_variable("right"),
        x + w,
    ))
    # bottom = y + h
    solver.add_constraint(eq(
        solver.get_variable("bottom") or solver.add_variable("bottom"),
        y + h,
    ))
    # right == 150 (x + 50 == 150 → x == 100)
    solver.add_constraint(eq(
        solver.get_variable("right"),
        150.0,
    ))
    # bottom == 80 (y + 30 == 80 → y == 50)
    solver.add_constraint(eq(
        solver.get_variable("bottom"),
        80.0,
    ))

    solver.solve()
    check("x = 100", x.value == 100, f"x={x.value}")
    check("y = 50", y.value == 50, f"y={y.value}")
    check("right = 150", solver.get_variable("right").value == 150)


def test_simplex_inequality():
    """不等式约束求解"""
    section("Simplex 不等式约束")

    from office_suite.engine.layout.constraint import Solver, eq, le, ge, Priority

    solver = Solver()
    x = solver.add_variable("x", 0.0)
    w = solver.add_variable("w", 100.0)

    # x >= 10
    solver.add_constraint(ge(x, 10.0))
    # x + w <= 200
    solver.add_constraint(le(x + w, 200.0))
    # w == 100
    solver.add_constraint(eq(w, 100.0))

    solver.solve()
    check("x >= 10", x.value >= 10, f"x={x.value}")
    check("x + w <= 200", x.value + w.value <= 200.01, f"x+w={x.value + w.value}")
    check("w == 100", w.value == 100, f"w={w.value}")


def test_stay_constraint():
    """Stay 约束 — 变量倾向保持当前值"""
    section("Stay 约束")

    from office_suite.engine.layout.constraint import Solver, eq, Priority

    solver = Solver()
    x = solver.add_variable("x", 50.0)
    y = solver.add_variable("y", 80.0)

    # 添加 stay（WEAK 优先级，x 倾向保持 50）
    solver.add_stay(x, Priority.WEAK)
    solver.add_stay(y, Priority.WEAK)

    # 只添加一条 REQUIRED 约束：x + y == 200
    solver.add_constraint(eq(x + y, 200.0, Priority.REQUIRED))

    solver.solve()
    check("x + y == 200", abs(x.value + y.value - 200) < 0.01,
          f"x+y={x.value + y.value}")
    # stay 使两个变量被均匀推动（从 50+80=130 均分 70 的差距）
    check("x 被推动到合理值", 80 < x.value < 130, f"x={x.value}")
    check("y 被推动到合理值", 70 < y.value < 120, f"y={y.value}")


def test_priority_conflict():
    """优先级冲突 — REQUIRED 优先于 STRONG"""
    section("优先级冲突解决")

    from office_suite.engine.layout.constraint import Solver, eq, Priority

    solver = Solver()
    x = solver.add_variable("x", 0.0)

    # REQUIRED: x == 100
    solver.add_constraint(eq(x, 100.0, Priority.REQUIRED))
    # STRONG: x == 200（与 REQUIRED 冲突，应被违反）
    solver.add_constraint(eq(x, 200.0, Priority.STRONG))

    solver.solve()
    check("REQUIRED x=100 优先", x.value == 100, f"x={x.value}")


def test_priority_cascade():
    """多级优先级级联 — REQUIRED → STRONG → WEAK"""
    section("优先级级联求解")

    from office_suite.engine.layout.constraint import Solver, eq, ge, le, Priority

    solver = Solver()
    x = solver.add_variable("x", 0.0)
    y = solver.add_variable("y", 0.0)

    # REQUIRED: x + y == 200
    solver.add_constraint(eq(x + y, 200.0, Priority.REQUIRED))

    # STRONG: x >= 80
    solver.add_constraint(ge(x, 80.0, Priority.STRONG))

    # WEAK: stay x at initial 0（但被 REQUIRED + STRONG 推动）
    solver.add_stay(x, Priority.WEAK)
    solver.add_stay(y, Priority.WEAK)

    solver.solve()
    check("x + y == 200", abs(x.value + y.value - 200) < 0.01,
          f"x+y={x.value + y.value}")
    check("x >= 80 (STRONG)", x.value >= 80, f"x={x.value}")


def test_edit_variable():
    """Edit 变量 — suggest_value 增量重解"""
    section("Edit 变量")

    from office_suite.engine.layout.constraint import Solver, eq, Priority

    solver = Solver()
    x = solver.add_variable("x", 50.0)
    y = solver.add_variable("y", 50.0)

    solver.add_edit_variable(x)
    solver.add_constraint(eq(x + y, 200.0, Priority.REQUIRED))

    # 第一次求解
    solver.solve()
    check("初始 x+y=200", abs(x.value + y.value - 200) < 0.01)

    # suggest x=120 → y 应变为 80
    solver.suggest_value(x, 120.0)
    solver.solve()
    check("suggest 后 x=120", x.value == 120, f"x={x.value}")
    check("联动 y=80", abs(y.value - 80) < 0.01, f"y={y.value}")


def test_centering_constraint():
    """居中约束 — center_x = parent.width / 2"""
    section("居中约束求解")

    from office_suite.engine.layout.constraint import Solver, eq, make_expression, Priority

    solver = Solver()
    pw = solver.add_variable("parent.width", 254.0)

    x = solver.add_variable("x", 0.0)
    w = solver.add_variable("w", 100.0)
    cx = solver.add_variable("center_x", 0.0)

    # center_x = x + w/2
    solver.add_constraint(eq(make_expression(cx), make_expression(x) + make_expression(w, 0.5)))
    # center_x = parent.width / 2
    solver.add_constraint(eq(make_expression(cx), make_expression(pw, 0.5)))
    # w == 100
    solver.add_constraint(eq(make_expression(w), 100.0))

    solver.solve()
    expected_x = (254.0 - 100.0) / 2
    check(f"x = 居中 ({expected_x})", abs(x.value - expected_x) < 0.01, f"x={x.value}")
    check("center_x = 127", abs(cx.value - 127.0) < 0.01, f"cx={cx.value}")


# ============================================================
# 运行
# ============================================================

if __name__ == "__main__":
    print("布局引擎集成测试")
    print("=" * 60)

    test_detect_layout_mode()
    test_absolute_resolve()
    test_relative_resolve()
    test_grid_resolve()
    test_flex_resolve()
    test_flex_column()
    test_constraint_resolve()
    test_pptx_renderer_integration()
    test_mixed_layout()
    test_simplex_multi_variable()
    test_simplex_inequality()
    test_stay_constraint()
    test_priority_conflict()
    test_priority_cascade()
    test_edit_variable()
    test_centering_constraint()

    print(f"\n{'='*60}")
    print(f"  结果: {_pass_count} 通过, {_fail_count} 失败")
    print(f"{'='*60}")

    sys.exit(0 if _fail_count == 0 else 1)
