#!/bin/bash
# Academic Radar — 一键学术扫描 + 生成主页/存档页
# 注意：git 提交 + 推送由 radar_index_generator.py 自动完成
cd "$(dirname "$0")" || exit 1
source venv/bin/activate

python3 academic_radar.py "$@"                  # 抓取 + 分析
python3 academic_md_to_html.py || true          # Markdown → HTML
python3 radar_index_generator.py || true        # 重建主页（含 git 提交 + 推送）
