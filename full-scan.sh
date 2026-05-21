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

# 🧹 清理残留 git 锁文件（上次中断留下的）
# VS Code、radar_index_generator 等都可能留下死锁
# 清掉 .git/ 下所有 .lock 文件，不限具体文件名
shopt -s nullglob
for lf in .git/*.lock .git/objects/*.lock; do
  rm -f "$lf" && echo "🧹 清理残留锁文件: $lf"
done

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
python news_radar.py --limit 50 || echo "⚠️ 资讯扫描失败"
echo ""

echo "========================================"
echo "  🌐 新闻报告 → HTML"
echo "========================================"
python news_md_to_html.py || echo "⚠️ 无新闻报告"
echo ""

echo "========================================"
echo "  🔬 Academic Radar — 学术论文扫描"
echo "========================================"
python academic_radar.py --limit 10 || echo "⚠️ 学术扫描失败"
echo ""

echo "========================================"
echo "  🌐 学术报告 → HTML"
echo "========================================"
python academic_md_to_html.py || echo "⚠️ 无学术报告"
echo ""

echo "========================================"
echo "  🏠 生成主页 index.html"
echo "========================================"
python radar_index_generator.py
echo ""

echo "========================================"
echo "  📰 新闻列表页"
echo "========================================"
python generate_news_index.py || echo "⚠️ 无新闻文件"
echo ""

echo "========================================"
echo "  🎓 学术列表页"
echo "========================================"
python generate_academic_index.py || echo "⚠️ 无学术文件"
echo ""

if [ "$SKIP_NOTIFY" = false ]; then
  echo "========================================"
  echo "  🔔 推送通知"
  echo "========================================"
  python dingtalk.py --type news $DRY_RUN
  python dingtalk.py --type papers $DRY_RUN
  echo ""
fi

echo "========================================"
echo "  ✅ 全流程完成"
date '+%Y-%m-%d %H:%M'
echo "========================================"
