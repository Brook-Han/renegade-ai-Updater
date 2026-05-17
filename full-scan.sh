#!/bin/bash
# Full Radar Scan — 学术 + 资讯，一键全跑
cd "$(dirname "$0")" && source venv/bin/activate
echo "========================================"
echo "  🔬 Academic Radar — 学术论文扫描"
echo "========================================"
python academic_radar.py
echo ""
echo "========================================"
echo "  📰 News Radar — 资讯扫描"
echo "========================================"
python news_radar.py
echo ""
echo "✅ 全扫描完成"
