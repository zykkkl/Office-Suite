"""我爱我家 — 主题 PPT 生成脚本"""
import sys
from pathlib import Path

# 向上两级到项目根目录
PROJECT_ROOT = Path(__file__).parent.parent.parent

from ..dsl.parser import parse_yaml_string
from ..ir.compiler import compile_document
from ..renderer.pptx.deck import PPTXRenderer

# 输出到 demo_output/my_home/
OUTPUT_DIR = PROJECT_ROOT / "demo_output" / "my_home"


def main():
    OUTPUT_DIR.mkdir(exist_ok=True)

    yaml_dsl = """
version: "4.0"
type: presentation
styles:
  title:
    font: { size: 40, weight: 700, color: "#FFFFFF" }
  subtitle:
    font: { size: 20, color: "#FFFFFF" }
  heading:
    font: { size: 28, weight: 700, color: "#92400E" }
  body:
    font: { size: 14, color: "#44403C" }
  accent:
    font: { size: 48, weight: 700, color: "#DC2626" }
  card_title:
    font: { size: 18, weight: 700, color: "#92400E" }
  card_body:
    font: { size: 13, color: "#57534E" }

slides:
  # -- Slide 1: 封面 --
  - layout: blank
    background:
      gradient:
        type: linear
        angle: 135
        stops: ["#FEF3C7", "#F59E0B"]
    elements:
      - type: text
        content: "我爱我家"
        style: { font: { size: 52, weight: 700, color: "#92400E" } }
        position: { x: 30mm, y: 45mm, width: 194mm, height: 25mm }
        animation: { effect: fade_in, duration: 0.8 }
      - type: text
        content: "家是最温暖的港湾"
        style: { font: { size: 22, color: "#78350F" } }
        position: { x: 30mm, y: 75mm, width: 194mm, height: 15mm }
        animation: { effect: slide_up, duration: 0.6, trigger: after_previous }
      - type: shape
        shape_type: rectangle
        position: { x: 30mm, y: 93mm, width: 60mm, height: 0.5mm }
        style: { fill: { color: "#D97706" } }
      - type: text
        content: "Family Is Where Love Is"
        style: { font: { size: 16, color: "#A16207", italic: true } }
        position: { x: 30mm, y: 100mm, width: 194mm, height: 10mm }
        animation: { effect: fade_in, duration: 0.5, trigger: after_previous, delay: 0.3 }

  # -- Slide 2: 家的意义 --
  - layout: blank
    background: { color: "#FFFBEB" }
    elements:
      - type: text
        content: "家的意义"
        style: heading
        position: { x: 20mm, y: 10mm, width: 214mm, height: 12mm }
      - type: shape
        shape_type: rounded_rectangle
        style: { fill: { color: "#FEF3C7" } }
        position: { x: 20mm, y: 30mm, width: 65mm, height: 60mm }
      - type: text
        content: "陪伴"
        style: card_title
        position: { x: 25mm, y: 38mm, width: 55mm, height: 10mm }
      - type: text
        content: "每一顿家常饭\n每一次深夜谈心\n都是最珍贵的时光"
        style: card_body
        position: { x: 25mm, y: 52mm, width: 55mm, height: 32mm }
      - type: shape
        shape_type: rounded_rectangle
        style: { fill: { color: "#ECFDF5" } }
        position: { x: 95mm, y: 30mm, width: 65mm, height: 60mm }
      - type: text
        content: "包容"
        style: card_title
        position: { x: 100mm, y: 38mm, width: 55mm, height: 10mm }
      - type: text
        content: "接纳彼此的不完美\n在争吵后依然选择\n站在一起"
        style: card_body
        position: { x: 100mm, y: 52mm, width: 55mm, height: 32mm }
      - type: shape
        shape_type: rounded_rectangle
        style: { fill: { color: "#FFF1F2" } }
        position: { x: 170mm, y: 30mm, width: 65mm, height: 60mm }
      - type: text
        content: "成长"
        style: card_title
        position: { x: 175mm, y: 38mm, width: 55mm, height: 10mm }
      - type: text
        content: "一起经历风雨\n一起收获欢笑\n共同变得更好"
        style: card_body
        position: { x: 175mm, y: 52mm, width: 55mm, height: 32mm }
      - type: text
        content: "家不在于大小，而在于里面充满了爱。"
        style: { font: { size: 15, color: "#92400E", italic: true } }
        position: { x: 20mm, y: 105mm, width: 214mm, height: 10mm }

  # -- Slide 3: 家庭时光 --
  - layout: blank
    background: { color: "#FFFBEB" }
    elements:
      - type: text
        content: "家庭时光"
        style: heading
        position: { x: 20mm, y: 10mm, width: 214mm, height: 12mm }
      - type: table
        rows: 6
        cols: 3
        data:
          - ["时间", "活动", "心情"]
          - ["早晨", "一起做早餐", "温馨"]
          - ["午后", "阳台晒太阳聊天", "惬意"]
          - ["傍晚", "散步逛公园", "快乐"]
          - ["晚上", "围坐看电视", "放松"]
          - ["周末", "全家出游/做饭", "幸福"]
        position: { x: 20mm, y: 30mm, width: 214mm, height: 100mm }

  # -- Slide 4: 家庭成员 --
  - layout: blank
    background: { color: "#FFFBEB" }
    elements:
      - type: text
        content: "我们的家庭"
        style: heading
        position: { x: 20mm, y: 10mm, width: 214mm, height: 12mm }
      - type: shape
        shape_type: rounded_rectangle
        style: { fill: { color: "#DBEAFE" } }
        position: { x: 20mm, y: 30mm, width: 100mm, height: 40mm }
      - type: text
        content: "爸爸"
        style: { font: { size: 20, weight: 700, color: "#1E40AF" } }
        position: { x: 30mm, y: 35mm, width: 80mm, height: 12mm }
      - type: text
        content: "家里的顶梁柱，默默承担一切"
        style: { font: { size: 13, color: "#1E3A8A" } }
        position: { x: 30mm, y: 50mm, width: 80mm, height: 8mm }
      - type: shape
        shape_type: rounded_rectangle
        style: { fill: { color: "#FCE7F3" } }
        position: { x: 130mm, y: 30mm, width: 100mm, height: 40mm }
      - type: text
        content: "妈妈"
        style: { font: { size: 20, weight: 700, color: "#BE185D" } }
        position: { x: 140mm, y: 35mm, width: 80mm, height: 12mm }
      - type: text
        content: "温暖的港湾，用爱守护每个人"
        style: { font: { size: 13, color: "#9D174D" } }
        position: { x: 140mm, y: 50mm, width: 80mm, height: 8mm }
      - type: shape
        shape_type: rounded_rectangle
        style: { fill: { color: "#D1FAE5" } }
        position: { x: 20mm, y: 80mm, width: 100mm, height: 40mm }
      - type: text
        content: "孩子"
        style: { font: { size: 20, weight: 700, color: "#065F46" } }
        position: { x: 30mm, y: 85mm, width: 80mm, height: 12mm }
      - type: text
        content: "家的希望，未来的光"
        style: { font: { size: 13, color: "#064E3B" } }
        position: { x: 30mm, y: 100mm, width: 80mm, height: 8mm }
      - type: shape
        shape_type: rounded_rectangle
        style: { fill: { color: "#FEF3C7" } }
        position: { x: 130mm, y: 80mm, width: 100mm, height: 40mm }
      - type: text
        content: "宠物"
        style: { font: { size: 20, weight: 700, color: "#92400E" } }
        position: { x: 140mm, y: 85mm, width: 80mm, height: 12mm }
      - type: text
        content: "毛茸茸的家人，治愈一切"
        style: { font: { size: 13, color: "#78350F" } }
        position: { x: 140mm, y: 100mm, width: 80mm, height: 8mm }

  # -- Slide 5: 家庭数据 --
  - layout: blank
    background: { color: "#FFFBEB" }
    elements:
      - type: text
        content: "我们的记录"
        style: heading
        position: { x: 20mm, y: 10mm, width: 214mm, height: 12mm }
      - type: text
        content: "365"
        style: accent
        position: { x: 20mm, y: 35mm, width: 70mm, height: 20mm }
        animation: { effect: zoom_in, duration: 0.5 }
      - type: text
        content: "天的陪伴"
        style: body
        position: { x: 20mm, y: 55mm, width: 70mm, height: 8mm }
      - type: text
        content: "1,095"
        style: { font: { size: 48, weight: 700, color: "#2563EB" } }
        position: { x: 95mm, y: 35mm, width: 70mm, height: 20mm }
        animation: { effect: zoom_in, duration: 0.5, delay: 0.2 }
      - type: text
        content: "顿家常饭"
        style: body
        position: { x: 95mm, y: 55mm, width: 70mm, height: 8mm }
      - type: text
        content: "∞"
        style: { font: { size: 48, weight: 700, color: "#059669" } }
        position: { x: 170mm, y: 35mm, width: 60mm, height: 20mm }
        animation: { effect: zoom_in, duration: 0.5, delay: 0.4 }
      - type: text
        content: "份爱"
        style: body
        position: { x: 170mm, y: 55mm, width: 60mm, height: 8mm }
      - type: chart
        chart_type: column
        position: { x: 20mm, y: 75mm, width: 214mm, height: 100mm }
        extra:
          title: "每月家庭活动次数"
          categories: ["1月", "2月", "3月", "4月", "5月", "6月"]
          series:
            - name: "出游"
              values: [2, 3, 4, 5, 6, 8]
            - name: "聚餐"
              values: [8, 10, 12, 15, 14, 18]

  # -- Slide 6: 结束页 --
  - layout: blank
    background:
      gradient:
        type: linear
        angle: 135
        stops: ["#FEF3C7", "#F59E0B"]
    elements:
      - type: text
        content: "有家就有爱"
        style: { font: { size: 44, weight: 700, color: "#92400E" } }
        position: { x: 30mm, y: 50mm, width: 194mm, height: 20mm }
        animation: { effect: fade_in, duration: 0.8 }
      - type: text
        content: "珍惜在一起的每一天"
        style: { font: { size: 20, color: "#78350F" } }
        position: { x: 30mm, y: 78mm, width: 194mm, height: 12mm }
        animation: { effect: slide_up, duration: 0.6, trigger: after_previous }
      - type: text
        content: "Home is where the heart is"
        style: { font: { size: 16, color: "#A16207", italic: true } }
        position: { x: 30mm, y: 100mm, width: 194mm, height: 10mm }
        animation: { effect: fade_in, duration: 0.5, trigger: after_previous, delay: 0.3 }
"""

    print("Generating...")
    doc = parse_yaml_string(yaml_dsl)
    ir = compile_document(doc)
    output = PPTXRenderer().render(ir, OUTPUT_DIR / "my_home.pptx")
    print(f"Done: {output} ({output.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
