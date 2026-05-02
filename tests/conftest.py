"""pytest 全局配置与共享 fixtures

pythonpath = ["."] (在 pyproject.toml 中) 已将项目根目录加入 sys.path，
各测试文件无需手动 sys.path.insert。
"""

from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).parent.parent


@pytest.fixture
def project_root() -> Path:
    """项目根目录路径"""
    return PROJECT_ROOT


@pytest.fixture
def pptx_renderer():
    """共享的 PPTX 渲染器实例"""
    from office_suite.renderer.pptx.deck import PPTXRenderer
    return PPTXRenderer()


@pytest.fixture
def compile_ir():
    """DSL YAML 字符串 → IR 编译器的便捷 wrapper"""
    from office_suite.dsl.parser import parse_yaml_string
    from office_suite.ir.compiler import compile_document

    def _compile(yaml_str: str):
        doc = parse_yaml_string(yaml_str)
        return compile_document(doc)

    return _compile
