#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════
# Renegade AI · 雷达每日更新脚本 v2
# 功能：新闻(每日) + 学术(每周一) 扫描 → 索引生成 → git 推送
# 用法：bash scripts/daily_update.sh
# ═══════════════════════════════════════════════════════════════
set -uo pipefail  # 故意不加 -e，让单个步骤失败不影响后续

# ── 路径 ──────────────────────────────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
LOG_DIR="$SCRIPT_DIR/logs"
TIMESTAMP="$(date '+%Y-%m-%d_%H-%M-%S')"
LOG_FILE="$LOG_DIR/update_$TIMESTAMP.log"
mkdir -p "$LOG_DIR"

# ── 日志函数：同时输出到屏幕和日志文件 ──────────────────────
log() {
    echo "[$(date '+%H:%M:%S')] $*" | tee -a "$LOG_FILE"
}

# ── 依赖检查（跑之前先看看缺什么） ─────────────────────────
check_deps() {
    log "🔍 检查 Python 依赖..."
    local MISSING=0
    python3 -c "import openai" 2>/dev/null || { log "   ❌ 缺少 openai"; MISSING=1; }
    python3 -c "import feedparser" 2>/dev/null || { log "   ❌ 缺少 feedparser"; MISSING=1; }
    python3 -c "import dotenv" 2>/dev/null || { log "   ❌ 缺少 python-dotenv"; MISSING=1; }
    python3 -c "import requests" 2>/dev/null || { log "   ❌ 缺少 requests"; MISSING=1; }
    python3 -c "import lxml" 2>/dev/null || { log "   ❌ 缺少 lxml"; MISSING=1; }

    if [ "$MISSING" -ne 0 ]; then
        log ""
        log "=============================================="
        log "⚠️  缺少依赖，请先安装："
        log "   pip install openai feedparser python-dotenv requests lxml"
        log "=============================================="
        log ""
        return 1
    fi
    log "   ✅ 所有依赖已就绪"
}

# ── 步骤 1：新闻雷达（每日） ────────────────────────────────
run_news_radar() {
    log ""
    log "═══════════════════════════════════════════"
    log "📰 步骤 1/3：新闻雷达扫描"
    log "═══════════════════════════════════════════"

    cd "$SCRIPT_DIR"
    python3 news_radar.py --force >> "$LOG_FILE" 2>&1
    local RC=$?

    if [ $RC -eq 0 ]; then
        log "   ✅ 新闻雷达扫描完成"
    else
        log "   ⚠️ 新闻雷达出错（exit code: $RC），跳过 → 继续下一步"
        tail -5 "$LOG_FILE" | while read -r line; do log "   ↳ $line"; done
    fi
}

# ── 步骤 2：学术雷达（每周一） ──────────────────────────────
run_academic_radar() {
    local TODAY_DOW
    TODAY_DOW="$(date '+%u')"  # 1=周一, 7=周日

    log ""
    log "═══════════════════════════════════════════"
    if [ "$TODAY_DOW" = "1" ]; then
        log "📄 步骤 2/3：学术雷达扫描（每周一）"
    else
        log "📄 步骤 2/3：学术雷达扫描（跳过——只在每周一执行，今天是周$TODAY_DOW）"
    fi
    log "═══════════════════════════════════════════"

    [ "$TODAY_DOW" != "1" ] && return

    cd "$SCRIPT_DIR"
    python3 academic_radar.py --force >> "$LOG_FILE" 2>&1
    local RC=$?

    if [ $RC -eq 0 ]; then
        log "   ✅ 学术雷达扫描完成"
    else
        log "   ⚠️ 学术雷达出错（exit code: $RC），跳过 → 继续下一步"
        tail -5 "$LOG_FILE" | while read -r line; do log "   ↳ $line"; done
    fi
}

# ── 步骤 3：索引页生成 + git 推送 ──────────────────────────
run_index_generator() {
    log ""
    log "═══════════════════════════════════════════"
    log "🏠 步骤 3/3：生成雷达索引页"
    log "═══════════════════════════════════════════"

    cd "$SCRIPT_DIR"
    python3 radar_index_generator.py 2>&1 | tee -a "$LOG_FILE"
    local RC=${PIPESTATUS[0]}

    if [ $RC -eq 0 ]; then
        log "   ✅ 索引页生成完成"
    else
        log "   ⚠️ 索引页生成出错（exit code: $RC）"
    fi
}

# ── 清理旧日志 ──────────────────────────────────────────────
cleanup_logs() {
    find "$LOG_DIR" -name 'update_*.log' -mtime +30 -delete 2>/dev/null || true
}

# ═══════════════════════════════════════════════════════════════
# 主流程
# ═══════════════════════════════════════════════════════════════
log "═══════════════════════════════════════════════════"
log "🚀 Renegade AI · 雷达每日更新"
log "📂 工作目录: $SCRIPT_DIR"
log "📝 日志: $LOG_FILE"
log "═══════════════════════════════════════════════════"

if check_deps; then
    run_news_radar
    run_academic_radar
else
    log "⏭️  跳过扫描步骤（依赖不全）"
fi

run_index_generator
cleanup_logs

log ""
log "═══════════════════════════════════════════════════"
log "🎉 完成！日志已保存: $LOG_FILE"
log "═══════════════════════════════════════════════════"
