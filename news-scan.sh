#!/bin/bash
# News Radar — 一键资讯扫描 + 生成主页/存档页
cd "$(dirname "$0")" || exit 1
source venv/bin/activate

python news_radar.py "$@"                  # 抓取 + 分析
python news_md_to_html.py || true          # Markdown → HTML
python radar_index_generator.py || true    # 重建主页 docs/index.html
python generate_news_index.py || true      # 重建新闻列表 docs/news/index.html
