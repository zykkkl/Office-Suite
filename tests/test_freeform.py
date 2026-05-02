"""自由贝塞尔形状测试 — 路径解析 + 预设生成"""

from office_suite.engine.text.path_text import parse_svg_path_struct
from office_suite.design.freeform_shapes import (
    blob_shape,
    wave_edge,
    ink_splash,
    ribbon_shape,
    cloud_shape,
    leaf_shape,
)


class TestParseSvgPathStruct:
    def test_move_and_line(self):
        nodes = parse_svg_path_struct("M 10,20 L 30,40 L 50,60")
        assert len(nodes) == 3
        assert nodes[0]["type"] == "move"
        assert nodes[0]["points"] == [(10.0, 20.0)]
        assert nodes[1]["type"] == "line"
        assert nodes[1]["points"] == [(30.0, 40.0)]
        assert nodes[2]["type"] == "line"
        assert nodes[2]["points"] == [(50.0, 60.0)]

    def test_cubic_bezier(self):
        nodes = parse_svg_path_struct("M 0,0 C 10,20 30,40 50,50")
        assert len(nodes) == 2
        assert nodes[1]["type"] == "cubic"
        assert nodes[1]["points"] == [(10.0, 20.0), (30.0, 40.0), (50.0, 50.0)]

    def test_quad_bezier(self):
        nodes = parse_svg_path_struct("M 0,0 Q 20,40 40,0")
        assert len(nodes) == 2
        assert nodes[1]["type"] == "quad"
        assert nodes[1]["points"] == [(20.0, 40.0), (40.0, 0.0)]

    def test_close_command(self):
        nodes = parse_svg_path_struct("M 0,0 L 10,0 L 10,10 Z")
        assert len(nodes) == 4
        assert nodes[3] == {"type": "close"}

    def test_close_lowercase(self):
        nodes = parse_svg_path_struct("M 0,0 L 10,0 z")
        assert nodes[-1] == {"type": "close"}

    def test_empty_path(self):
        nodes = parse_svg_path_struct("")
        assert nodes == []

    def test_complex_path(self):
        path = "M 20,30 C 20,60 80,60 80,30 C 80,10 50,5 20,30 Z"
        nodes = parse_svg_path_struct(path)
        assert len(nodes) == 4
        assert nodes[0]["type"] == "move"
        assert nodes[1]["type"] == "cubic"
        assert nodes[2]["type"] == "cubic"
        assert nodes[3] == {"type": "close"}

    def test_comma_separated(self):
        nodes = parse_svg_path_struct("M 5,10 L 20,30")
        assert nodes[0]["points"] == [(5.0, 10.0)]
        assert nodes[1]["points"] == [(20.0, 30.0)]


class TestFreeformShapes:
    def test_blob_shape_returns_string(self):
        path = blob_shape(seed=42)
        assert isinstance(path, str)
        assert path.startswith("M ")
        assert "Z" in path

    def test_blob_shape_different_seeds(self):
        p1 = blob_shape(seed=1)
        p2 = blob_shape(seed=2)
        assert p1 != p2

    def test_blob_shape_parseable(self):
        nodes = parse_svg_path_struct(blob_shape(seed=0))
        assert nodes[0]["type"] == "move"
        assert nodes[-1]["type"] == "close"

    def test_wave_edge_bottom(self):
        path = wave_edge(direction="bottom", waves=2)
        assert isinstance(path, str)
        nodes = parse_svg_path_struct(path)
        assert any(n["type"] == "quad" for n in nodes)
        assert nodes[-1]["type"] == "close"

    def test_wave_edge_top(self):
        path = wave_edge(direction="top", waves=3)
        nodes = parse_svg_path_struct(path)
        assert nodes[0]["type"] == "move"
        assert nodes[-1]["type"] == "close"

    def test_ink_splash(self):
        path = ink_splash(seed=5)
        assert isinstance(path, str)
        nodes = parse_svg_path_struct(path)
        assert nodes[0]["type"] == "move"
        assert nodes[-1]["type"] == "close"
        assert all(n["type"] in ("move", "cubic", "close") for n in nodes)

    def test_ribbon_shape(self):
        path = ribbon_shape()
        assert isinstance(path, str)
        nodes = parse_svg_path_struct(path)
        assert nodes[-1]["type"] == "close"

    def test_cloud_shape(self):
        path = cloud_shape()
        assert isinstance(path, str)
        nodes = parse_svg_path_struct(path)
        assert nodes[0]["type"] == "move"
        assert nodes[-1]["type"] == "close"

    def test_leaf_shape(self):
        path = leaf_shape()
        assert isinstance(path, str)
        nodes = parse_svg_path_struct(path)
        assert nodes[0]["type"] == "move"
        assert nodes[-1]["type"] == "close"

    def test_all_presets_parseable(self):
        """所有预设均能被解析且为闭合路径"""
        presets = [
            blob_shape(seed=0),
            blob_shape(seed=99),
            wave_edge("bottom"),
            wave_edge("top"),
            ink_splash(seed=0),
            ink_splash(seed=7),
            ribbon_shape(),
            cloud_shape(),
            leaf_shape(),
            leaf_shape(angle_deg=45),
        ]
        for path in presets:
            nodes = parse_svg_path_struct(path)
            assert len(nodes) >= 2, f"Path too short: {path[:50]}"
            assert nodes[0]["type"] == "move", f"First node not move: {path[:50]}"
            assert nodes[-1]["type"] == "close", f"Not closed: {path[:50]}"
