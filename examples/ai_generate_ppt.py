"""AI 生成 PPT 示例

使用方式：
    python examples/ai_generate_ppt.py

需要设置环境变量：
    ANTHROPIC_API_KEY=sk-ant-...  (使用 Claude)
    或
    OPENAI_API_KEY=sk-...  (使用 GPT)
"""

import os
import re
from pathlib import Path

# 添加项目根目录到路径
import sys
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from office_suite.ai.dsl_generator_prompt import build_prompt, build_messages, EXAMPLES
from office_suite.dsl.parser import parse_yaml_string
from office_suite.ir.compiler import compile_document
from office_suite.renderer.pptx.deck import PPTXRenderer


def extract_yaml(text: str) -> str | None:
    """从 AI 输出中提取 YAML 代码块"""
    pattern = r"```yaml\s*\n(.*?)```"
    match = re.search(pattern, text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return None


def generate_with_claude(prompt: str) -> str:
    """使用 Claude API 生成"""
    try:
        import anthropic
        client = anthropic.Anthropic()
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4096,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.content[0].text
    except ImportError:
        raise ImportError("需要安装 anthropic: pip install anthropic")
    except Exception as e:
        raise RuntimeError(f"Claude API 调用失败: {e}")


def generate_with_openai(prompt: str) -> str:
    """使用 OpenAI API 生成"""
    try:
        import openai
        client = openai.OpenAI()
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=4096,
        )
        return response.choices[0].message.content
    except ImportError:
        raise ImportError("需要安装 openai: pip install openai")
    except Exception as e:
        raise RuntimeError(f"OpenAI API 调用失败: {e}")


def generate_ppt(
    content: str,
    style: str = "corporate",
    output_path: str | Path = "output.pptx",
    provider: str = "claude",
) -> Path:
    """生成 PPT

    Args:
        content: 内容描述
        style: 风格偏好
        output_path: 输出路径
        provider: AI 提供商 (claude/openai)

    Returns:
        输出文件路径
    """
    # 1. 构建 prompt
    prompt = build_prompt(content, style)

    # 2. 调用 AI 生成
    print(f"正在使用 {provider} 生成 DSL...")
    if provider == "claude":
        ai_output = generate_with_claude(prompt)
    elif provider == "openai":
        ai_output = generate_with_openai(prompt)
    else:
        raise ValueError(f"不支持的 provider: {provider}")

    # 3. 提取 YAML
    yaml_content = extract_yaml(ai_output)
    if yaml_content is None:
        print("AI 输出中未找到 YAML 代码块，尝试直接解析...")
        yaml_content = ai_output

    # 4. 解析并渲染
    print("正在解析 DSL...")
    doc = parse_yaml_string(yaml_content)
    ir = compile_document(doc)

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    print("正在渲染 PPTX...")
    PPTXRenderer().render(ir, output_path)

    print(f"生成完成: {output_path}")
    return output_path


def demo_offline():
    """离线演示：使用示例 DSL 直接渲染"""
    from office_suite.ai.dsl_generator_prompt import EXAMPLES

    # 使用一个预设的 DSL 示例
    example_dsl = '''
version: "4.0"
type: presentation
style_preset: corporate

data:
  revenue:
    categories: ["Q1", "Q2", "Q3", "Q4"]
    series:
      - name: "营收(万)"
        values: [8000, 9500, 10500, 12000]

slides:
  - layout: blank
    background_board:
      background:
        type: linear_gradient
        angle: 135
        stops: ["#1E40AF", "#3B82F6"]
      ornament:
        - type: shape
          shape_type: circle
          style: { fill: { color: "#FFFFFF", opacity: 0.05 } }
          position: { x: 160mm, y: -30mm, width: 200mm, height: 200mm }
    elements:
      - type: text
        content: "2026 Q2 季度经营报告"
        position: { x: 30mm, y: 45mm, width: 194mm, height: 25mm }
        style:
          font: { size: 40, weight: 700, color: "#FFFFFF" }
      - type: text
        content: "总营收 1.2 亿 | 同比增长 23%"
        position: { x: 30mm, y: 75mm, width: 194mm, height: 10mm }
        style:
          font: { size: 18, color: "#DBEAFE" }
      - type: shape
        shape_type: rectangle
        style: { fill: { color: "#FFFFFF", opacity: 0.3 } }
        position: { x: 30mm, y: 95mm, width: 40mm, height: 1mm }
      - type: text
        content: "财务部  |  2026年4月"
        position: { x: 30mm, y: 105mm, width: 194mm, height: 8mm }
        style:
          font: { size: 14, color: "#BFDBFE" }

  - layout: blank
    elements:
      - type: text
        content: "目录"
        position: { x: 30mm, y: 15mm, width: 194mm, height: 15mm }
        style:
          font: { size: 28, weight: 700, color: "#0F172A" }
      - type: shape
        shape_type: rectangle
        style: { fill: { color: "#1E40AF" } }
        position: { x: 30mm, y: 35mm, width: 16mm, height: 2mm }
      - type: text
        content: "01  核心指标\\n02  营收趋势\\n03  市场构成\\n04  下期展望"
        position: { x: 30mm, y: 50mm, width: 194mm, height: 80mm }
        style:
          font: { size: 18, color: "#334155" }

  - layout: blank
    background_board:
      background:
        type: color
        color: "#F8FAFC"
    elements:
      - type: text
        content: "核心指标"
        position: { x: 20mm, y: 10mm, width: 214mm, height: 12mm }
        style:
          font: { size: 24, weight: 700, color: "#0F172A" }
      - type: shape
        shape_type: rectangle
        style: { fill: { color: "#FFFFFF" }, shadow: { color: "#000", opacity: 0.05, blur: 4, offset: [0, 2] } }
        position: { x: 20mm, y: 30mm, width: 68mm, height: 50mm }
      - type: text
        content: "1.2亿"
        position: { x: 20mm, y: 35mm, width: 68mm, height: 20mm }
        style:
          font: { size: 36, weight: 700, color: "#1E40AF", align: center }
      - type: text
        content: "总营收"
        position: { x: 20mm, y: 55mm, width: 68mm, height: 8mm }
        style:
          font: { size: 14, color: "#64748B", align: center }
      - type: text
        content: "同比 +23%"
        position: { x: 20mm, y: 65mm, width: 68mm, height: 8mm }
        style:
          font: { size: 12, color: "#16A34A", align: center }
      - type: shape
        shape_type: rectangle
        style: { fill: { color: "#FFFFFF" }, shadow: { color: "#000", opacity: 0.05, blur: 4, offset: [0, 2] } }
        position: { x: 93mm, y: 30mm, width: 68mm, height: 50mm }
      - type: text
        content: "60%"
        position: { x: 93mm, y: 35mm, width: 68mm, height: 20mm }
        style:
          font: { size: 36, weight: 700, color: "#1E40AF", align: center }
      - type: text
        content: "海外占比"
        position: { x: 93mm, y: 55mm, width: 68mm, height: 8mm }
        style:
          font: { size: 14, color: "#64748B", align: center }
      - type: text
        content: "主要增长引擎"
        position: { x: 93mm, y: 65mm, width: 68mm, height: 8mm }
        style:
          font: { size: 12, color: "#16A34A", align: center }
      - type: shape
        shape_type: rectangle
        style: { fill: { color: "#FFFFFF" }, shadow: { color: "#000", opacity: 0.05, blur: 4, offset: [0, 2] } }
        position: { x: 166mm, y: 30mm, width: 68mm, height: 50mm }
      - type: text
        content: "18%"
        position: { x: 166mm, y: 35mm, width: 68mm, height: 20mm }
        style:
          font: { size: 36, weight: 700, color: "#1E40AF", align: center }
      - type: text
        content: "利润率"
        position: { x: 166mm, y: 55mm, width: 68mm, height: 8mm }
        style:
          font: { size: 14, color: "#64748B", align: center }
      - type: text
        content: "成本控制显著"
        position: { x: 166mm, y: 65mm, width: 68mm, height: 8mm }
        style:
          font: { size: 12, color: "#16A34A", align: center }

  - layout: blank
    elements:
      - type: text
        content: "营收趋势"
        position: { x: 20mm, y: 10mm, width: 214mm, height: 12mm }
        style:
          font: { size: 24, weight: 700, color: "#0F172A" }
      - type: chart
        chart_type: bar
        data_ref: revenue
        position: { x: 20mm, y: 30mm, width: 214mm, height: 100mm }
        extra:
          title: "季度营收趋势"
          legend: true
          colors: ["#1E40AF", "#3B82F6", "#60A5FA", "#93C5FD"]

  - layout: blank
    elements:
      - type: text
        content: "市场构成"
        position: { x: 20mm, y: 10mm, width: 214mm, height: 12mm }
        style:
          font: { size: 24, weight: 700, color: "#0F172A" }
      - type: chart
        chart_type: pie
        position: { x: 20mm, y: 30mm, width: 100mm, height: 100mm }
        extra:
          categories: ["国内", "海外"]
          series:
            - name: "占比"
              values: [40, 60]
          colors: ["#3B82F6", "#1E40AF"]
      - type: text
        content: "海外市场成为主要增长引擎，占比达 60%。新客户增长 35%，客户留存率保持在 92% 的高水平。"
        position: { x: 130mm, y: 40mm, width: 104mm, height: 80mm }
        style:
          font: { size: 14, color: "#334155" }

  - layout: blank
    background_board:
      background:
        type: color
        color: "#0F172A"
      ornament:
        type: color
        color: "#1E40AF"
        position: { x: 0mm, y: 0mm, width: 8mm, height: 142.875mm }
    elements:
      - type: text
        content: "下期展望"
        position: { x: 30mm, y: 15mm, width: 194mm, height: 15mm }
        style:
          font: { size: 28, weight: 700, color: "#FFFFFF" }
      - type: text
        content: "1. 持续深耕海外市场，目标占比提升至 70%\\n2. 加大研发投入，推出 3 款新产品\\n3. 优化供应链，目标利润率提升至 20%\\n4. 拓展东南亚市场，建立本地化团队"
        position: { x: 30mm, y: 40mm, width: 194mm, height: 90mm }
        style:
          font: { size: 16, color: "#E2E8F0" }

  - layout: blank
    background_board:
      background:
        type: color
        color: "#0F172A"
      ornament:
        type: color
        color: "#1E40AF"
        position: { x: 0mm, y: 120mm, width: 254mm, height: 4mm }
    elements:
      - type: text
        content: "感谢聆听"
        position: { x: 30mm, y: 45mm, width: 194mm, height: 25mm }
        style:
          font: { size: 40, weight: 700, color: "#FFFFFF", align: center }
      - type: text
        content: "Q&A"
        position: { x: 30mm, y: 75mm, width: 194mm, height: 15mm }
        style:
          font: { size: 20, color: "#94A3B8", align: center }
      - type: text
        content: "财务部 | finance@company.com"
        position: { x: 30mm, y: 128mm, width: 194mm, height: 8mm }
        style:
          font: { size: 12, color: "#64748B", align: center }
'''

    print("使用预设 DSL 示例渲染...")
    doc = parse_yaml_string(example_dsl)
    ir = compile_document(doc)

    output_dir = PROJECT_ROOT / "examples" / "output"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "quarterly_report.pptx"

    PPTXRenderer().render(ir, output_path)
    print(f"生成完成: {output_path}")
    return output_path


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="AI 生成 PPT")
    parser.add_argument("--demo", action="store_true", help="离线演示模式")
    parser.add_argument("--content", type=str, help="内容描述")
    parser.add_argument("--style", default="corporate", help="风格偏好")
    parser.add_argument("--output", default="output.pptx", help="输出路径")
    parser.add_argument("--provider", default="claude", choices=["claude", "openai"], help="AI 提供商")

    args = parser.parse_args()

    if args.demo:
        demo_offline()
    elif args.content:
        generate_ppt(args.content, args.style, args.output, args.provider)
    else:
        print("示例用法:")
        print("  python examples/ai_generate_ppt.py --demo")
        print('  python examples/ai_generate_ppt.py --content "Q2 营收报告" --style corporate')
