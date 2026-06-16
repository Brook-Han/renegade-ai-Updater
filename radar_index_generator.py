#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🏠 Renegade AI 雷达主页生成器 v2.3（v5.4 可读性与视觉优化版）

✅ v2.3 / v5.4 更新内容：
  1. ✅ 基础字号 .92rem → .95rem，正文可读性提升
  2. ✅ 深色背景柔化：#0a0a12 → #0c0c18，减轻视觉疲劳
  3. ✅ 文字对比提升：text-muted #9595c0 → #a8a8d0
  4. ✅ 卡片内边距 28px → 32px，更大呼吸感
  5. ✅ Hero 区域增加径向渐变环境光，视觉层次更丰富
  6. ✅ 卡片悬停增加 accent 色光晕 + 微动效
  7. ✅ 导航栏强化玻璃态效果（backdrop-blur 24px → 32px）
  8. ✅ 评分数字增加视觉条指示器，分数更直观
  9. ✅ 卡片入场动画加速优化：.55s → .4s，节奏感更好
  10. ✅ 中等屏幕 (900-1200px) 增加三列布局断点
  11. ✅ Light Mode 对比度进一步优化
  12. ✅ 保留 v2.2 全部修复（WCAG AA / 无障碍 / 触控热区）

用法：
    cd your-project-root
    python radar_index_generator.py
"""

import re
import subprocess
from pathlib import Path
from html import escape

from config import Config
from card_utils import extract_cards_from_html

# ═══════════════════════════════════════════════════════════════
# 配置
# ═══════════════════════════════════════════════════════════════
REPORTS_ROOT = Config.OUTPUT_DIR

SUBDIR_CONFIG = {
    "news": {
        "label": "NEWS",
        "type": "news",
        "pattern": "news_report*.html",
        "badge_class": "news",
    },
    "academic": {
        "label": "PAPER",
        "type": "academic",
        "pattern": "academic_report*.html",
        "badge_class": "academic",
    },
}

TOP_NEWS = 5
TOP_ACAD = 5
SUMMARY_MAX_CHARS = 220


# ═══════════════════════════════════════════════════════════════
# 工具函数
# ═══════════════════════════════════════════════════════════════
def _safe_float(value, default=5.0):
    """安全地将字符串转为浮点数，失败时返回默认值。"""
    try:
        return float(value)
    except (ValueError, TypeError):
        return default


def _truncate_summary(text, max_chars=SUMMARY_MAX_CHARS):
    """截断文本至 max_chars，尽量在词边界处断开。"""
    if not text or len(text) <= max_chars:
        return text or "", ""
    truncated = text[:max_chars]
    # 在空格或中文标点处断开
    for sep in (" ", "，", "。", "、", "；", ".", ",", "!", "?"):
        idx = truncated.rfind(sep)
        if idx > max_chars * 0.7:
            return text[:idx], "…"
    return truncated, "…"


# ═══════════════════════════════════════════════════════════════
# 收集所有报告文件
# ═══════════════════════════════════════════════════════════════
def collect_all_reports() -> dict:
    all_entries = []

    for subdir_name, config in SUBDIR_CONFIG.items():
        subdir_path = REPORTS_ROOT / subdir_name
        if not subdir_path.exists():
            print(f"ℹ️  目录不存在，跳过: {subdir_path}")
            continue

        print(f"🔍 扫描 {subdir_path} / {config['pattern']}")
        for html_file in subdir_path.glob(config["pattern"]):
            if html_file.name == "index.html":
                continue

            # 合并日期 + 时间匹配为一次正则（时间部分可选）
            m = re.search(r"(\d{4}-\d{2}-\d{2})(?:_(\d{6}))?", html_file.name)
            if not m:
                print(f"⚠️ 文件名格式不符，跳过: {html_file.name}")
                continue

            date_str = m.group(1)
            time_str = m.group(2) or "000000"
            relative_link = f"{subdir_name}/{html_file.name}"

            entry = {
                "file_name": html_file.name,
                "subdir": subdir_name,
                "relative_link": relative_link,
                "full_path": html_file,
                "date": date_str,
                "time": time_str,
                "type": config["type"],
                "label": config["label"],
            }
            all_entries.append(entry)

    by_date = {}
    for entry in all_entries:
        by_date.setdefault(entry["date"], []).append(entry)

    sorted_dates = sorted(by_date.keys(), reverse=True)
    for date in by_date:
        by_date[date].sort(key=lambda x: x["time"], reverse=True)

    stats = {
        "total": len(all_entries),
        "news": sum(1 for e in all_entries if e["type"] == "news"),
        "academic": sum(1 for e in all_entries if e["type"] == "academic"),
        "days": len(sorted_dates),
    }
    return {"dates": sorted_dates, "by_date": by_date, "stats": stats}


# ═══════════════════════════════════════════════════════════════
# 生成每日区块（v5.4 风格）
# ═══════════════════════════════════════════════════════════════
def generate_day_html(date: str, entries: list[dict]) -> str:
    all_cards = []
    for entry in entries:
        cards = extract_cards_from_html(entry["full_path"], entry["type"])
        for c in cards:
            c["_report_link"] = entry["relative_link"]
        all_cards.extend(cards)

    news_cards = [c for c in all_cards if c["type"] == "news"]
    acad_cards = [c for c in all_cards if c["type"] == "academic"]

    print(f"   📊 {date}: 新闻卡片 {len(news_cards)} 个，学术卡片 {len(acad_cards)} 个")

    news_cards.sort(key=lambda c: _safe_float(c.get("score", "5.0")), reverse=True)
    acad_cards.sort(key=lambda c: _safe_float(c.get("score", "5.0")), reverse=True)

    top_news = news_cards[:TOP_NEWS]
    top_acad = acad_cards[:TOP_ACAD]
    display_cards = top_news + top_acad

    top_types = [c["type"] for c in display_cards]
    print(f"   🏆 展示卡片类型: {top_types}")

    latest_entry = entries[0]
    formatted_time = f"{latest_entry['time'][:2]}:{latest_entry['time'][2:4]}:{latest_entry['time'][4:]}"
    total_label = f"{len(news_cards)} NEWS · {len(acad_cards)} PAPERS"

    html = f'''
<div class="day-group" data-date="{date}">
  <div class="day-header-row">
    <div class="day-header-left">
      <div class="day-eyebrow">DIGEST · {formatted_time}</div>
      <h2 class="day-date">{date}</h2>
    </div>
    <div class="day-header-right">{total_label}</div>
  </div>
  <div class="card-grid">
'''

    for card in display_cards:
        title = escape(card.get("title", ""))
        score = card.get("score", "5.0")
        raw_summary = card.get("summary", "")
        summary, truncated = _truncate_summary(raw_summary)
        summary = escape(summary)
        chapter = escape(card.get("chapter", ""))
        link = card.get("link", "#")
        card_type = card["type"]
        type_label = SUBDIR_CONFIG[card_type]["label"]

        report_link_raw = card.get("_report_link", "")
        report_link = f"./{report_link_raw}" if not report_link_raw.startswith(("./", "../", "http")) else report_link_raw

        chapter_html = f'<span class="card-chapter">§ {chapter}</span>' if chapter else ''
        link_html = f'<a class="card-source-link" href="{escape(link)}" target="_blank" rel="noopener">↗ SOURCE</a>' if link and link != "#" else ""
        draft_dot = '<span class="draft-dot" title="Has Draft">●</span>' if card.get("has_draft") else ""

        # Score visual bars (0-10 → 5 bars, each bar = 2 points)
        score_val = _safe_float(score, 5.0)
        filled_bars = min(5, max(0, round(score_val / 2)))
        score_bars_html = '<div class="score-bar">' + ''.join(
            f'<span class="bar{" filled" if i < filled_bars else ""}"></span>'
            for i in range(5)
        ) + '</div>'

        html += f'''    <article class="radar-card" data-type="{card_type}">
      <div class="radar-card-top">
        <div class="radar-card-meta">
          <span class="type-tag {card_type}">{type_label}</span>
          {chapter_html}
          {draft_dot}
        </div>
        <div class="radar-score">
          {score}<span>/10</span>
          {score_bars_html}
        </div>
      </div>
      <h3 class="radar-card-title">
        <a href="{escape(link)}" target="_blank" rel="noopener">{title}</a>
      </h3>
      <p class="radar-card-body">{summary}{truncated}</p>
      <div class="radar-card-footer">
        {link_html}
        <a class="full-report-link" href="{report_link}">FULL REPORT →</a>
      </div>
    </article>
'''

    html += "  </div>\n</div>\n"
    return html


# ═══════════════════════════════════════════════════════════════
# HTML 模板 — 与 Renegade AI v5.4 可读性优化版对齐
# ═══════════════════════════════════════════════════════════════
_HTML_TEMPLATE = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Renegade AI · Radar Archive</title>
  <meta name="description" content="Daily digest of AI news and academic papers, curated through the lens of Renegade AI.">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Space+Mono:ital,wght@0,400;0,500;0,700;1,400&family=Crimson+Pro:ital,wght@0,300;0,400;0,600;1,300;1,400&family=Bebas+Neue&display=swap" rel="stylesheet">
  <style>
/* ── DESIGN TOKENS (v5.4 · Readability & Visual Optimized) ── */
:root {
  --bg:           #0c0c18;
  --bg2:          #10101e;
  --surface:      #12121e;
  --card:         #1a1a2e;
  --border:       #282840;
  --border-bright:#3a3a5a;
  --text:         #e2e2f0;
  --text-muted:   #a8a8d0;
  --text-faint:   #55557a;
  --accent:       #ff5c45;
  --accent-dim:   rgba(255,92,69,0.12);
  --accent-glow:  rgba(255,92,69,0.06);
  --accent2:      #d4af5c;
  --accent2-dim:  rgba(212,175,92,0.10);
  --accent3:      #5ba3e6;
  --accent3-dim:  rgba(91,163,230,0.12);
  --white:        #f4f4fc;
  --mono:         'Space Mono', monospace;
  --serif:        'Crimson Pro', Georgia, serif;
  --display:      'Bebas Neue', sans-serif;
  --ease:         cubic-bezier(0.4,0,0.2,1);
}
:root.light {
  --bg:#f0f2f8; --bg2:#fafbff; --surface:#e8eaf2; --card:#ffffff;
  --border:#d4d7e4; --border-bright:#b8bcd0;
  --text:#1a1a2e; --text-muted:#4c4c6a; --text-faint:#8888a0;
  --accent:#d94934; --accent-dim:rgba(217,73,52,0.08); --accent-glow:rgba(217,73,52,0.04);
  --accent2:#a67c28; --accent2-dim:rgba(166,124,40,0.08);
  --accent3:#356ba8; --accent3-dim:rgba(53,107,168,0.08);
  --white:#1a1a2e;
}

/* ── RESET & TYPOGRAPHY ── */
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
html{scroll-behavior:smooth}
body{
  font-family:var(--serif);background:var(--bg);color:var(--text);
  font-size:1rem;line-height:1.8;-webkit-font-smoothing:antialiased;
  -moz-osx-font-smoothing:grayscale;overflow-x:hidden;
  transition:background .3s,color .3s;
  text-rendering:optimizeLegibility;
  font-feature-settings:"kern" 1,"liga" 1,"palt" 1;
}
::selection{background:var(--accent);color:#fff;text-shadow:0 1px 2px rgba(0,0,0,.2)}
::-webkit-scrollbar{width:4px}
::-webkit-scrollbar-track{background:var(--bg)}
::-webkit-scrollbar-thumb{background:var(--border-bright);border-radius:2px}
::-webkit-scrollbar-thumb:hover{background:var(--accent)}

/* ── ACCESSIBILITY ── */
:focus-visible{outline:2px solid var(--accent);outline-offset:3px;border-radius:2px;z-index:10}
:focus:not(:focus-visible){outline:none}
@media(prefers-reduced-motion:reduce){
  *,*::before,*::after{
    animation-duration:.01ms!important;animation-iteration-count:1!important;
    transition-duration:.01ms!important;scroll-behavior:auto!important;
  }
  .noise{opacity:0!important}
}

/* ── NOISE OVERLAY ── */
.noise{position:fixed;inset:0;z-index:0;pointer-events:none;opacity:.025;
  background-image:url("data:image/svg+xml,%3Csvg viewBox='0 0 512 512' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.65' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='512' height='512' filter='url(%23n)'/%3E%3C/svg%3E")}
.light .noise{opacity:.05}

/* ── NAV (Glass v5.4) ── */
nav{
  position:fixed;top:0;width:100%;z-index:200;
  background:rgba(12,12,24,.88);backdrop-filter:blur(32px) saturate(1.2);
  -webkit-backdrop-filter:blur(32px) saturate(1.2);
  border-bottom:1px solid var(--border);
  height:56px;display:flex;align-items:center;justify-content:space-between;
  padding:0 32px;font-family:var(--mono);transition:background .3s,border-color .3s;
}
.light nav{background:rgba(240,242,248,.88)}
.nav-brand{
  font-size:.75rem;font-weight:700;color:var(--accent);letter-spacing:3px;
  text-transform:uppercase;text-decoration:none;
  position:relative;transition:opacity .2s;
}
.nav-brand:hover{opacity:.85}
.nav-right{display:flex;gap:8px;align-items:center}
.nav-pill{
  background:none;border:1px solid var(--border);color:var(--text-muted);
  font-family:var(--mono);font-size:.72rem;font-weight:500;letter-spacing:2px;
  padding:5px 14px;cursor:pointer;text-decoration:none;
  display:inline-flex;align-items:center;transition:all .25s var(--ease);
}
.nav-pill:hover,.nav-pill.active{border-color:var(--accent);color:var(--accent);background:var(--accent-dim)}
.theme-btn{
  background:none;border:1px solid var(--border);color:var(--text-muted);
  width:36px;height:36px;cursor:pointer;display:flex;align-items:center;justify-content:center;
  font-size:.9rem;transition:all .25s var(--ease);
}
.theme-btn:hover,.theme-btn:focus-visible{border-color:var(--accent);color:var(--accent);background:var(--accent-dim);transform:rotate(180deg)}

/* ── HERO STRIP (v5.4 Ambient) ── */
.hero-strip{
  padding-top:56px;border-bottom:1px solid var(--border);
  display:grid;grid-template-columns:1fr auto;gap:0;position:relative;
}
.hero-strip::before{
  content:'';position:absolute;top:-120px;left:-80px;
  width:600px;height:600px;
  background:radial-gradient(ellipse at 30% 40%,rgba(255,92,69,.08) 0%,transparent 70%);
  pointer-events:none;z-index:0;
}
.hero-left{
  padding:60px 72px 52px;border-right:1px solid var(--border);
  position:relative;z-index:1;
}
.hero-eyebrow{
  font-family:var(--mono);font-size:.72rem;font-weight:500;letter-spacing:4px;
  color:var(--accent);text-transform:uppercase;
  margin-bottom:20px;display:flex;align-items:center;gap:12px;
}
.hero-eyebrow::before{content:'';width:36px;height:1px;background:var(--accent)}
.hero-title{
  font-family:var(--display);font-size:clamp(3.5rem,7vw,7rem);
  line-height:.9;letter-spacing:3px;color:var(--white);margin-bottom:16px;
}
.hero-title span{color:var(--accent);text-shadow:0 0 40px rgba(255,92,69,.25)}
.hero-desc{
  font-size:1.1rem;color:var(--text-muted);font-style:italic;
  border-left:3px solid var(--accent);padding-left:18px;
  max-width:520px;line-height:1.85;margin-bottom:32px;transition:color .3s;
}
.hero-tags{display:flex;gap:6px;flex-wrap:wrap}
.hero-tag{
  font-family:var(--mono);font-size:.72rem;font-weight:500;letter-spacing:1.5px;
  color:var(--text-muted);background:var(--surface);
  border:1px solid var(--border);padding:4px 12px;text-transform:uppercase;
}
.hero-right{
  display:flex;flex-direction:column;align-items:center;justify-content:center;
  padding:40px 48px;gap:24px;min-width:220px;position:relative;z-index:1;
}
.stat-block{text-align:center}
.stat-block .n{
  font-family:var(--display);font-size:4rem;color:var(--accent);
  line-height:1;display:block;
  text-shadow:0 0 30px rgba(255,92,69,.2);
}
.stat-block .l{
  font-family:var(--mono);font-size:.72rem;font-weight:500;letter-spacing:2.5px;
  color:var(--text-muted);text-transform:uppercase;display:block;margin-top:4px;
}
.stat-divider{width:1px;height:40px;background:var(--border)}

/* ── CONTROLS BAR ── */
.controls-bar{
  display:flex;align-items:center;gap:0;
  border-bottom:1px solid var(--border);
  padding:0 72px;height:52px;
  font-family:var(--mono);font-size:.72rem;
  overflow-x:auto;position:relative;z-index:1;
}
.filter-btn{
  height:100%;padding:0 22px;
  background:none;border:none;border-right:1px solid var(--border);
  color:var(--text-muted);cursor:pointer;letter-spacing:2px;
  text-transform:uppercase;font-family:var(--mono);font-size:.72rem;font-weight:600;
  transition:all .25s var(--ease);white-space:nowrap;
}
.filter-btn:first-child{border-left:1px solid var(--border)}
.filter-btn.active,.filter-btn:hover{color:var(--accent);background:var(--accent-dim)}
.search-wrap{
  flex:1;display:flex;align-items:center;gap:10px;
  padding:0 20px;border-right:1px solid var(--border);min-width:180px;
}
.search-wrap::before{content:'§';color:var(--text-faint);font-size:.8rem}
.search-wrap input{
  background:none;border:none;color:var(--text);
  font-family:var(--mono);font-size:.72rem;font-weight:500;letter-spacing:1px;
  width:100%;outline:none;
}
.search-wrap input::placeholder{color:var(--text-faint);transition:color .2s}
.search-wrap input:focus::placeholder{color:transparent}
.controls-bar .list-link{
  height:100%;padding:0 20px;display:flex;align-items:center;
  color:var(--text-muted);text-decoration:none;letter-spacing:2px;
  text-transform:uppercase;white-space:nowrap;font-size:.72rem;font-weight:500;
  border-right:1px solid var(--border);transition:all .2s;
}
.controls-bar .list-link:hover{color:var(--accent);background:var(--accent-dim)}

/* ── MAIN CONTENT ── */
.main{max-width:100%;padding:64px 72px 80px;position:relative;z-index:1}

/* ── DAY GROUP ── */
.day-group{margin-bottom:64px}
.day-group.hidden{display:none}
.day-header-row{
  display:flex;align-items:flex-end;justify-content:space-between;
  border-bottom:1px solid var(--border);padding-bottom:16px;margin-bottom:28px;
}
.day-eyebrow{
  font-family:var(--mono);font-size:.72rem;font-weight:600;letter-spacing:3px;
  color:var(--accent);text-transform:uppercase;margin-bottom:6px;
}
.day-date{
  font-family:var(--display);font-size:clamp(2rem,4vw,3.2rem);
  letter-spacing:2px;color:var(--white);line-height:1;
}
.day-header-right{
  font-family:var(--mono);font-size:.72rem;font-weight:500;letter-spacing:2px;
  color:var(--text-faint);text-transform:uppercase;padding-bottom:6px;
}

/* ── CARD GRID ── */
.card-grid{
  display:grid;grid-template-columns:repeat(auto-fill,minmax(480px,1fr));
  gap:1px;background:var(--border);border:1px solid var(--border);
}

/* ── RADAR CARD (v5.4) ── */
.radar-card{
  background:var(--card);padding:32px 28px;
  display:flex;flex-direction:column;gap:14px;
  transition:background .25s var(--ease),box-shadow .35s var(--ease),border-color .25s;
  position:relative;
  opacity:0;transform:translateY(16px);
  animation:fadeUp .4s var(--ease) forwards;
  box-shadow:0 2px 16px rgba(0,0,0,.12),inset 0 1px 0 rgba(255,255,255,.03);
  border-left:2px solid transparent;
}
.radar-card::before{
  content:'';position:absolute;inset:0;
  background:linear-gradient(135deg,var(--accent-glow),transparent 60%);
  opacity:0;transition:opacity .4s var(--ease);pointer-events:none;
}
.radar-card:hover::before{opacity:1}
.radar-card:hover{
  background:var(--surface);
  box-shadow:0 8px 32px rgba(0,0,0,.2),0 0 0 1px rgba(255,92,69,.12);
  z-index:2;
}
.radar-card:has(.radar-card-title a:focus-visible){
  box-shadow:0 8px 32px rgba(0,0,0,.2),0 0 0 2px var(--accent);
}
.radar-card.hidden{display:none}

.radar-card-top{display:flex;justify-content:space-between;align-items:flex-start;gap:16px}
.radar-card-meta{display:flex;align-items:center;gap:8px;flex-wrap:wrap;flex:1}

.type-tag{
  font-family:var(--mono);font-size:.72rem;font-weight:600;letter-spacing:2px;
  padding:3px 10px;text-transform:uppercase;
}
.type-tag.news{background:var(--accent3-dim);color:var(--accent3);border:1px solid rgba(91,163,230,.2)}
.type-tag.academic{background:var(--accent-dim);color:var(--accent);border:1px solid rgba(255,92,69,.2)}

.card-chapter{
  font-family:var(--mono);font-size:.72rem;font-weight:500;letter-spacing:1px;
  color:var(--text-faint);text-transform:uppercase;
}
.draft-dot{color:var(--accent2);font-size:.75rem;line-height:1;opacity:.8}

.radar-score{
  display:flex;flex-direction:column;align-items:flex-end;gap:4px;
  font-family:var(--display);font-size:2rem;color:var(--accent);
  line-height:1;white-space:nowrap;flex-shrink:0;
  position:relative;padding-left:8px;
}
.radar-score span{
  display:block;font-family:var(--mono);font-size:.7rem;font-weight:500;
  color:var(--text-faint);letter-spacing:1px;text-align:right;
}
.score-bar{
  display:flex;gap:2px;width:48px;height:3px;
}
.score-bar .bar{
  flex:1;border-radius:1px;
  background:var(--border-bright);transition:background .3s var(--ease);
}
.score-bar .bar.filled{background:var(--accent)}
.radar-card:hover .score-bar .bar.filled{background:var(--accent2)}

.radar-card-title{
  font-family:var(--display);font-size:1.35rem;letter-spacing:1px;
  color:var(--white);line-height:1.2;position:relative;z-index:1;
}
.radar-card-title a{
  color:inherit;text-decoration:none;
  border-bottom:1px solid transparent;
  transition:border-color .25s var(--ease),color .2s;
}
.radar-card-title a:hover{color:var(--accent2);border-bottom-color:var(--accent2)}

.radar-card-body{
  font-size:.95rem;color:var(--text-muted);line-height:1.8;
  flex:1;position:relative;z-index:1;
}

.radar-card-footer{
  display:flex;justify-content:space-between;align-items:center;
  padding-top:12px;border-top:1px solid var(--border);
  font-family:var(--mono);font-size:.72rem;font-weight:500;letter-spacing:1.5px;
  transition:border-color .3s;position:relative;z-index:1;
}
.card-source-link{
  color:var(--accent2);text-decoration:none;text-transform:uppercase;
  transition:color .25s var(--ease);
  display:inline-flex;align-items:center;gap:4px;
}
.card-source-link:hover{color:var(--white);gap:6px}
.full-report-link{
  color:var(--text-faint);text-decoration:none;text-transform:uppercase;
  transition:color .25s var(--ease);
  display:inline-flex;align-items:center;gap:4px;
}
.full-report-link:hover{color:var(--accent);gap:6px}

/* ── EMPTY STATE ── */
.empty-state{
  display:none;text-align:center;padding:100px 32px 80px;
  font-family:var(--mono);color:var(--text-faint);letter-spacing:2px;
  font-size:.72rem;font-weight:500;text-transform:uppercase;
}
.empty-state .glyph{
  font-family:var(--display);font-size:5rem;color:var(--text-faint);opacity:.2;
  display:block;margin-bottom:20px;line-height:1;
}

/* ── STATUS BAR ── */
.status-bar{
  position:fixed;bottom:0;width:100%;z-index:200;
  background:rgba(12,12,24,.92);backdrop-filter:blur(16px);
  border-top:1px solid var(--border);
  padding:10px 32px;font-family:var(--mono);font-size:.72rem;font-weight:500;
  color:var(--text-faint);letter-spacing:2px;
  display:flex;justify-content:space-between;align-items:center;
  transition:background .3s,border-color .3s;
}
.light .status-bar{background:rgba(240,242,248,.92)}
.status-dot{
  display:inline-block;width:6px;height:6px;
  background:var(--accent);border-radius:50%;margin-right:8px;
  animation:pulse 2s ease-in-out infinite;
  box-shadow:0 0 6px var(--accent);
}
@keyframes pulse{0%,100%{opacity:1;transform:scale(1)}50%{opacity:.5;transform:scale(.7)}}
@keyframes fadeUp{to{opacity:1;transform:translateY(0)}}

/* ── MOBILE TOUCH TARGETS ── */
@media(max-width:768px){
  .nav-pill,.theme-btn,.filter-btn,.controls-bar .list-link{
    min-height:44px;min-width:44px;display:inline-flex;align-items:center;justify-content:center;
  }
  .controls-bar{padding:0 8px;height:44px}
  .search-wrap{min-width:80px;padding:0 10px}
  .search-wrap::before{display:none}
  .filter-btn{padding:0 10px;font-size:.68rem}
  .controls-bar .list-link{padding:0 10px;font-size:.68rem}
}
@media(max-width:480px){
  .controls-bar{padding:0 4px;height:40px;gap:0;overflow-x:auto;-webkit-overflow-scrolling:touch}
  .search-wrap{min-width:60px;flex:0 0 auto;padding:0 8px}
  .search-wrap input{width:60px}
  .filter-btn{padding:0 8px;font-size:.65rem;letter-spacing:1px}
  .controls-bar .list-link{padding:0 8px;font-size:.65rem;letter-spacing:1px}
  .controls-bar .list-link:last-child{border-right:none}
}

/* ── RESPONSIVE ── */
@media(max-width:1200px){
  .card-grid{grid-template-columns:repeat(auto-fill,minmax(420px,1fr))}
}
@media(max-width:900px){
  .main{padding:48px 24px 80px}
  .controls-bar{padding:0 24px}
  .hero-strip{grid-template-columns:1fr}
  .hero-left{padding:48px 24px 36px;border-right:none;border-bottom:1px solid var(--border)}
  .hero-right{flex-direction:row;padding:24px;border-bottom:1px solid var(--border)}
  .stat-divider{width:40px;height:1px}
  .card-grid{grid-template-columns:1fr}
  .nav-center{display:none}
}
  </style>
</head>
<body>
<div class="noise"></div>

<!-- NAV -->
<nav>
  <a href="https://brook-han.github.io/Renegade-AI/" class="nav-brand">RENEGADE AI v5.4</a>
  <div class="nav-right">
    <a href="./news/" class="nav-pill">NEWS</a>
    <a href="./academic/" class="nav-pill">PAPERS</a>
    <button class="theme-btn" id="themeBtn" aria-label="Toggle theme">◐</button>
  </div>
</nav>

<!-- HERO -->
<div class="hero-strip">
  <div class="hero-left">
    <div class="hero-eyebrow">Radar Archive · Daily Digest</div>
    <h1 class="hero-title">DAILY<br><span>DIGEST</span></h1>
    <p class="hero-desc">AI-curated signal from the noise — news ranked by relevance to cognitive evolution, papers mapped to the arguments that matter.</p>
    <div class="hero-tags">
      <span class="hero-tag" id="tagTotal">— REPORTS</span>
      <span class="hero-tag" id="tagDays">— DAYS</span>
      <span class="hero-tag" id="tagLatest">LATEST: —</span>
      <span class="hero-tag">NEWS TOP 5 + PAPERS TOP 5</span>
    </div>
  </div>
  <div class="hero-right">
    <div class="stat-block">
      <span class="n" id="statNews">—</span>
      <span class="l">News</span>
    </div>
    <div class="stat-divider"></div>
    <div class="stat-block">
      <span class="n" id="statAcad">—</span>
      <span class="l">Papers</span>
    </div>
  </div>
</div>

<!-- CONTROLS -->
<div class="controls-bar">
  <button class="filter-btn active" data-filter="all" aria-pressed="true">ALL</button>
  <button class="filter-btn" data-filter="news" aria-pressed="false">📰 NEWS</button>
  <button class="filter-btn" data-filter="academic" aria-pressed="false">📄 PAPERS</button>
  <div class="search-wrap">
    <input type="text" id="searchInput" placeholder="SEARCH TITLES &amp; SUMMARIES" aria-label="Search titles and summaries">
  </div>
  <a href="./news/" class="list-link">→ NEWS INDEX</a>
  <a href="./academic/" class="list-link">→ PAPERS INDEX</a>
</div>

<!-- MAIN -->
<main class="main">
  {{ day_sections }}
  <div class="empty-state" id="emptyState">
    <span class="glyph">∅</span>
    NO RESULTS · ADJUST FILTERS OR SEARCH TERMS
  </div>
</main>

<!-- STATUS BAR -->
<div class="status-bar">
  <span><span class="status-dot"></span><span id="statusText">STATUS: [ INITIALIZING ]</span></span>
  <span id="statusTime"></span>
</div>

<script>
/* ── THEME ── */
(function(){
  const h=document.documentElement,b=document.getElementById('themeBtn');
  const apply=t=>{h.classList.toggle('light',t==='light');localStorage.setItem('renegade-theme',t)};
  apply(localStorage.getItem('renegade-theme')||(matchMedia('(prefers-color-scheme: dark)').matches?'dark':'light'));
  b.onclick=()=>apply(h.classList.contains('light')?'dark':'light');
})();

/* ── STATS ── */
(function(){
  const t={{ total_reports }},n={{ news_count }},a={{ academic_count }},d={{ days_count }},l='{{ latest_date }}';
  document.getElementById('statNews').textContent=n;
  document.getElementById('statAcad').textContent=a;
  document.getElementById('tagTotal').textContent=t+' REPORTS';
  document.getElementById('tagDays').textContent=d+' DAYS';
  document.getElementById('tagLatest').textContent='LATEST: '+l;
})();

/* ── FILTER + SEARCH ── */
(function(){
  const btns=document.querySelectorAll('.filter-btn');
  const inp=document.getElementById('searchInput');
  const cards=document.querySelectorAll('.radar-card');
  const groups=document.querySelectorAll('.day-group');
  const empty=document.getElementById('emptyState');
  let filter='all',query='';

  function update(){
    let visible=0;
    cards.forEach(c=>{
      const typeMatch=filter==='all'||c.dataset.type===filter;
      const titleText=(c.querySelector('.radar-card-title')?.textContent||'').toLowerCase();
      const bodyText=(c.querySelector('.radar-card-body')?.textContent||'').toLowerCase();
      const searchMatch=!query||titleText.includes(query)||bodyText.includes(query);
      const show=typeMatch&&searchMatch;
      c.classList.toggle('hidden',!show);
      if(show)visible++;
    });
    groups.forEach(g=>{
      const hasVisible=g.querySelectorAll('.radar-card:not(.hidden)').length>0;
      g.classList.toggle('hidden',!hasVisible);
    });
    empty.style.display=visible===0?'block':'none';
  }

  btns.forEach(b=>b.addEventListener('click',()=>{
    btns.forEach(x=>{x.classList.remove('active');x.setAttribute('aria-pressed','false')});
    b.classList.add('active');
    b.setAttribute('aria-pressed','true');
    filter=b.dataset.filter;
    update();
  }));

  let debounce;
  inp.addEventListener('input',ev=>{
    clearTimeout(debounce);
    debounce=setTimeout(()=>{query=ev.target.value.toLowerCase().trim();update();},200);
  });
})();

/* ── STATUS BAR ── */
(function(){
  const messages=[
    'STATUS: [ SIGNAL_EXTRACTED · NOISE_SUPPRESSED ]',
    'STATUS: [ COGNITIVE_FRICTION_INDEX: ACTIVE ]',
    'STATUS: [ ACADEMIC_PIPELINE: NOMINAL ]',
    'STATUS: [ DARK_FOREST_HYPOTHESIS: CHALLENGED ]',
    'STATUS: [ TOKEN_TRAP_MONITOR: RUNNING ]',
    'STATUS: [ BREEDER_SCENARIO_WATCH: ENABLED ]',
    'STATUS: [ RENEGADE_SEED_STATUS: GERMINATING ]',
    'STATUS: [ v5.4_READABILITY_MATRIX: OPTIMIZED ]',
    'STATUS: [ ATTENTION_SPAN_ANCHOR: LOCKED ]',
    'STATUS: [ SIGNAL_TO_NOISE_RATIO: IMPROVED ]',
  ];
  let i=0;
  const st=document.getElementById('statusText'),tm=document.getElementById('statusTime');
  function tick(){
    st.textContent=messages[i%messages.length];i++;
    tm.textContent=new Date().toISOString().replace('T',' ').slice(0,19)+' UTC';
  }
  tick();setInterval(tick,5000);
})();

/* ── STAGGERED CARD ANIMATION ── */
document.querySelectorAll('.radar-card').forEach((c,i)=>{
  c.style.animationDelay=(i*0.04)+'s';
});
</script>
</body>
</html>'''


# ═══════════════════════════════════════════════════════════════
# 主函数
# ═══════════════════════════════════════════════════════════════
def main():
    print("🚀 Renegade AI Radar Index Generator v2.3 (v5.4 Aligned)")
    print(f"📁 Reports root: {REPORTS_ROOT.resolve()}")

    data = collect_all_reports()
    if not data["dates"]:
        print("❌ No reports found!")
        return

    print(f"✅ Found {data['stats']['total']} reports across {data['stats']['days']} days")
    print(f"   📰 News: {data['stats']['news']} | 📄 Academic: {data['stats']['academic']}")

    print("\n🎨 Generating HTML sections...")
    day_sections = []
    for date in data["dates"]:
        entries = data["by_date"][date]
        print(f"📅 处理日期: {date} ({len(entries)} 个报告)")
        section = generate_day_html(date, entries)
        day_sections.append(section)

    print("📄 Rendering index.html...")
    final = _HTML_TEMPLATE.replace("{{ day_sections }}", "\n".join(day_sections))
    final = final.replace("{{ total_reports }}", str(data["stats"]["total"]))
    final = final.replace("{{ news_count }}", str(data["stats"]["news"]))
    final = final.replace("{{ academic_count }}", str(data["stats"]["academic"]))
    final = final.replace("{{ days_count }}", str(data["stats"]["days"]))
    final = final.replace("{{ latest_date }}", data["dates"][0] if data["dates"] else "N/A")

    output = REPORTS_ROOT / "index.html"
    output.write_text(final, encoding="utf-8")
    print(f"\n✅ Success! Generated: {output}")

    if output.exists():
        content = output.read_text(encoding="utf-8")
        news_cnt = content.count('data-type="news"')
        acad_cnt = content.count('data-type="academic"')
        print(f"\n🔍 调试：index.html 中 news 卡片: {news_cnt} 个，academic 卡片: {acad_cnt} 个")

    # --- 自动生成子列表页（带异常保护）---
    print("\n📋 正在自动生成新闻列表页...")
    try:
        from generate_news_index import main as gen_news_main
        gen_news_main()
    except ImportError:
        print("⚠️ generate_news_index 模块未找到，跳过新闻列表页生成")

    print("\n📋 正在自动生成学术列表页...")
    try:
        from generate_academic_index import main as gen_acad_main
        gen_acad_main()
    except ImportError:
        print("⚠️ generate_academic_index 模块未找到，跳过学术列表页生成")

    # --- 自动 Git 提交 ---
    auto_git_commit(data)

    print("\n✨ 全部生成完毕！")


# ═══════════════════════════════════════════════════════════════
# 自动 Git 提交
# ═══════════════════════════════════════════════════════════════
def auto_git_commit(data: dict) -> None:
    """将生成的 index 文件自动 git add / commit / push。"""
    repo_root = REPORTS_ROOT.parent

    # ── 清理上次残留的 .lock 文件（安全检查：确认是 git 仓库） ───
    git_dir = repo_root / ".git"
    if git_dir.is_dir():
        for pattern in (".git/*.lock", ".git/objects/*.lock"):
            for f in repo_root.glob(pattern):
                try:
                    f.unlink()
                    print(f"🧹 清理残留锁文件: {f.relative_to(repo_root)}")
                except Exception as e:
                    print(f"⚠️ 无法删除 {f.name}: {e}")
    else:
        print("⚠️ 未检测到 .git 目录，跳过锁文件清理")

    latest = data["dates"][0] if data["dates"] else "unknown"

    files_to_add = [
        "docs/index.html",
        "docs/news/index.html",
        "docs/academic/index.html",
        "docs/news/news_cache.json",
        "docs/news/last_report_hash.txt",
    ]

    # 添加当天报告文件（如果存在）
    if latest != "unknown":
        for stem in (
            f"docs/news/news_articles_{latest}.json",
            f"docs/news/news_data_{latest}.json",
            f"docs/news/news_report_{latest}.md",
            f"docs/news/news_report_{latest}.html",
        ):
            if (repo_root / stem).exists():
                files_to_add.append(stem)

    try:
        subprocess.run(
            ["git", "add"] + files_to_add,
            cwd=repo_root, check=True, capture_output=True,
        )
    except subprocess.CalledProcessError as e:
        print(f"⚠️ git add 失败: {e.stderr.decode()}")
        return

    commit_msg = f"chore: auto-update radar v5.4 index [{latest}]"
    result = subprocess.run(
        ["git", "commit", "-m", commit_msg],
        cwd=repo_root, capture_output=True,
    )

    if result.returncode == 0:
        print(f"✅ Git commit: {commit_msg}")
    elif b"nothing to commit" in result.stderr:
        print("ℹ️  No changes to commit — skipping push")
        return
    else:
        print(f"⚠️ git commit 失败: {result.stderr.decode()}")
        return

    # ── 先 fetch 远程状态（fetch 不怕工作区脏） ────────────────
    subprocess.run(
        ["git", "fetch", "origin", "main"],
        cwd=repo_root, capture_output=True, text=True,
    )

    # ── 用 force-with-lease 推送（安全强推，不怕 remote 有变更） ──
    try:
        result = subprocess.run(
            ["git", "push", "--force-with-lease", "origin", "HEAD"],
            cwd=repo_root, capture_output=True, text=True,
        )
        if result.returncode == 0:
            print("✅ Git push 成功（force-with-lease）")
        elif "Everything up-to-date" in result.stderr or "up to date" in result.stderr:
            print("✅ Already up-to-date")
        elif "failed to push" in result.stderr or "[rejected]" in result.stderr:
            print(f"⚠️ force-with-lease 也被拒，可能是远程有意料外的提交。")
            print(f"   错误: {result.stderr}")
        else:
            print(f"⚠️ git push 失败: {result.stderr}")
    except subprocess.CalledProcessError as e:
        print(f"⚠️ git push 异常: {e.stderr}")


if __name__ == "__main__":
    main()
