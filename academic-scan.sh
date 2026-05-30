#!/bin/bash
# Academic Radar — 一键学术扫描 + 生成主页/存档页 + 自动推送
cd "$(dirname "$0")" || exit 1
source venv/bin/activate

python academic_radar.py "$@"                  # 抓取 + 分析
python academic_md_to_html.py || true          # Markdown → HTML
python radar_index_generator.py || true        # 重建主页 docs/index.html
python generate_academic_index.py || true      # 重建学术列表 docs/academic/index.html

# 自动 git 提交 + 推送
git add docs/ cache/
if ! git diff --staged --quiet; then
  git commit -m "🎓 本地学术扫描: $(date '+%Y-%m-%d %H:%M')"
  git fetch origin main 2>/dev/null || true
  git rebase origin/main 2>/dev/null || true
  git push origin main || echo "⚠️ 推送失败，请手动执行: git push origin main"
else
  echo "✨ 无新变更，跳过提交"
fi
