#!/bin/bash
# ============================================================
#  🤖 Renegade AI 雷达 · 本地一键全流程
#  与 GitHub Actions (daily-radar.yml) 完全对齐
# ============================================================
#  用法: bash full-scan.sh
#  选项: bash full-scan.sh --skip-notify   跳过推送
#        bash full-scan.sh --dry-run       推送预览
# ============================================================

cd "$(dirname "$0")" || exit 1
source venv/bin/activate 2>/dev/null || source .venv/bin/activate 2>/dev/null

# 🧹 清理残留 git 锁文件（安全检查：确认是 git 仓库）
if [ -d ".git" ]; then
  shopt -s nullglob
  for lf in .git/*.lock .git/objects/*.lock; do
    rm -f "$lf" && echo "🧹 清理残留锁文件: $lf"
  done
fi

SKIP_NOTIFY=false
DRY_RUN=""
for arg in "$@"; do
  case "$arg" in
    --skip-notify) SKIP_NOTIFY=true ;;
    --dry-run) DRY_RUN="--dry-run" ;;
  esac
done

echo "========================================"
echo "  📰 News Radar — 资讯扫描"
echo "========================================"
python3 news_radar.py --limit 50 || echo "⚠️ 资讯扫描失败"
echo ""

echo "========================================"
echo "  🌐 新闻报告 → HTML"
echo "========================================"
python3 news_md_to_html.py || echo "⚠️ 无新闻报告"
echo ""

echo "========================================"
echo "  🔬 Academic Radar — 学术论文扫描"
echo "========================================"
python3 academic_radar.py --limit 10 || echo "⚠️ 学术扫描失败"
echo ""

echo "========================================"
echo "  🌐 学术报告 → HTML"
echo "========================================"
python3 academic_md_to_html.py || echo "⚠️ 无学术报告"
echo ""

echo "========================================"
echo "  🏠 生成主页 index.html（含 git 提交 + 推送）"
echo "========================================"
python3 radar_index_generator.py
echo ""

if [ "$SKIP_NOTIFY" = false ]; then
  echo "========================================"
  echo "  🔔 推送通知"
  echo "========================================"
  python3 -m notify --type news $DRY_RUN
  python3 -m notify --type papers $DRY_RUN
  echo ""
fi

echo ""
echo "========================================"
echo "  ✅ 全流程完成"
date '+%Y-%m-%d %H:%M'
echo "========================================"
