#!/bin/bash
# Academic Radar — 一键学术扫描 + 生成主页/存档页
# 注意：git 提交 + 推送由 radar_index_generator.py 自动完成
cd "$(dirname "$0")" || exit 1
source venv/bin/activate

# 自动安装缺失依赖（静默，已装则跳过）
pip install --break-system-packages -r requirements.txt -q 2>/dev/null

python3 academic_radar.py "$@"                  # 抓取 + 分析
python3 academic_md_to_html.py || true          # Markdown → HTML
python3 radar_index_generator.py || true        # 重建主页（含 git 提交 + 推送）
