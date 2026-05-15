#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🏠 Renegade AI 雷达主页生成器 v2.1（新闻/论文分开展示版 · 优化版）
视觉风格与 Renegade AI v5.3 网页对齐

✅ 修复与改进：
  1. ✅ 新闻卡片分数提取失败时给默认值 5.0
  2. ✅ 链接路径正确（./news/xxx.html 形式）
  3. ✅ 每日区块：新闻 Top 10 + 学术 Top 5（不再混合 Top 5）
  4. ✅ 调试输出显示实际展示的卡片类型
  5. ✅ 新闻/论文按钮改为直接跳转独立列表页
  6. ✅ 视觉风格与 v5.3 主页完全对齐
  7. ✅ [v2.1] 用 lxml 替代正则解析 HTML，更稳健
  8. ✅ [v2.1] HTML 模板提取为模块级常量，避免重复创建
  9. ✅ [v2.1] 动态 import 增加异常处理
 10. ✅ [v2.1] 摘要截断尊重词边界
 11. ✅ [v2.1] 文件名正则合并为单次匹配

用法：
    cd your-project-root
    python radar_index_generator.py
"""

import re
import subprocess
from pathlib import Path
from html import escape

# lxml 是可选的加速依赖；不可用时自动降级为正则解析
try:
    from lxml import html as lxml_html
    _HAS_LXML = True
except ImportError:
    _HAS_LXML = False

# ═══════════════════════════════════════════════════════════════
# 配置
# ═══════════════════════════════════════════════════════════════
REPORTS_ROOT = Path("docs")

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

TOP_NEWS = 10
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
    if len(text) <= max_chars:
        return text, ""
    truncated = text[:max_chars]
    # 在空格或中文标点处断开
    for sep in (" ", "，", "。", "、", "；", ".", ",", "!", "?"):
        idx = truncated.rfind(sep)
        if idx > max_chars * 0.7:
            return text[:idx], "…"
    return truncated, "…"


# ═══════════════════════════════════════════════════════════════
# 从 HTML 报告中提取卡片信息
# ═══════════════════════════════════════════════════════════════
if _HAS_LXML:

    def extract_cards_from_html(html_path: Path, report_type: str) -> list[dict]:
        """用 lxml + XPath 解析 HTML 报告，提取卡片信息。"""
        try:
            content = html_path.read_text(encoding="utf-8")
        except Exception as e:
            print(f"   ⚠️ 读取失败 {html_path.name}: {e}")
            return []

        try:
            tree = lxml_html.fromstring(content)
        except Exception as e:
            print(f"   ⚠️ 解析失败 {html_path.name}: {e}")
            return []

        card_elements = tree.xpath("//div[@class='card']")
        if card_elements:
            print(f"   🔍 {html_path.name}: 找到 {len(card_elements)} 个卡片区块")

        cards = []
        for card_el in card_elements:
            card = {"type": report_type}

            # --- 标题 ---
            title_els = card_el.xpath(".//div[@class='card-title']")
            if not title_els:
                continue
            card["title"] = title_els[0].text_content().strip()

            # --- 评分 ---
            score_els = card_el.xpath(".//div[@class='card-score']")
            if score_els:
                score_text = score_els[0].text_content().strip()
                score_m = re.search(r"([\d.]+)", score_text)
                card["score"] = score_m.group(1) if score_m else "5.0"
            else:
                card["score"] = "5.0"

            # --- 原文链接 ---
            card["link"] = ""
            for a in card_el.xpath(".//a[@target='_blank']"):
                link_text = a.text_content().strip() if a.text_content() else ""
                if "原文" in link_text or "PDF" in link_text:
                    href = a.get("href", "")
                    if href:
                        card["link"] = href
                    break

            # --- 摘要 ---
            body_els = card_el.xpath(".//div[@class='card-body']")
            if body_els:
                card["summary"] = body_els[0].text_content().strip()
            else:
                card["summary"] = ""

            # --- 是否有草稿 ---
            card["has_draft"] = bool(card_el.xpath(".//div[@class='card-draft']"))

            # --- 章节标记 ---
            meta_els = card_el.xpath(".//div[@class='card-meta']")
            if meta_els:
                meta_text = meta_els[0].text_content()
                chapter_m = re.search(r"📍\s*(.+?)(?:\n|$)", meta_text)
                if chapter_m:
                    card["chapter"] = chapter_m.group(1).strip()

            cards.append(card)

        return cards

else:
    # lxml 不可用时的正则降级方案

    def extract_cards_from_html(html_path: Path, report_type: str) -> list[dict]:
        """用正则解析 HTML 报告（降级方案）。"""
        try:
            content = html_path.read_text(encoding="utf-8")
        except Exception as e:
            print(f"   ⚠️ 读取失败 {html_path.name}: {e}")
            return []

        cards = []
        card_blocks = re.findall(
            r'<div class="card">(.*?)</div>\s*(?=<div class="card">|</main>|</body>|$)',
            content,
            re.DOTALL,
        )
        if card_blocks:
            print(f"   🔍 {html_path.name}: 找到 {len(card_blocks)} 个卡片区块")

        for block in card_blocks:
            card = {"type": report_type}

            title_m = re.search(r'<div class="card-title">(.*?)</div>', block, re.DOTALL)
            if title_m:
                card["title"] = re.sub(r"<[^>]+>", "", title_m.group(1)).strip()

            score_m = re.search(r'<div class="card-score">([\d.]+)\s*<span>/10</span>', block)
            card["score"] = score_m.group(1) if score_m else "5.0"

            link_m = re.search(r'<a href="([^"]+)" target="_blank"[^>]*>↗\s*(?:原文|PDF/原文)</a>', block)
            if link_m:
                card["link"] = link_m.group(1)

            summary_m = re.search(r'<div class="card-body">(.*?)</div>', block, re.DOTALL)
            if summary_m:
                card["summary"] = re.sub(r"<[^>]+>", "", summary_m.group(1)).strip()

            card["has_draft"] = '<div class="card-draft">' in block

            chapter_m = re.search(r"📍\s*([^<\s][^<]*?)(?:</span>|<|&nbsp;|$)", block)
            if chapter_m:
                card["chapter"] = chapter_m.group(1).strip()

            if card.get("title"):
                cards.append(card)

        return cards


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
# 生成每日区块（v5.3 风格）
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

        html += f'''    <article class="radar-card" data-type="{card_type}">
      <div class="radar-card-top">
        <div class="radar-card-meta">
          <span class="type-tag {card_type}">{type_label}</span>
          {chapter_html}
          {draft_dot}
        </div>
        <div class="radar-score">{score}<span>/10</span></div>
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
# HTML 模板 — 与 Renegade AI v5.3 视觉风格对齐（模块级常量）
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
  <link href="https://fonts.googleapis.com/css2?family=Space+Mono:ital,wght@0,400;0,700;1,400&family=Crimson+Pro:ital,wght@0,300;0,400;0,600;1,300;1,400&family=Bebas+Neue&display=swap" rel="stylesheet">
  <style>
/* ── DESIGN TOKENS (mirrors v5.3) ── */
:root {
  --bg:           #08080e;
  --bg2:          #0d0d18;
  --surface:      #111120;
  --card:         #13131f;
  --border:       #1e1e30;
  --border-bright:#2e2e50;
  --text:         #cccce0;
  --text-muted:   #6868a0;
  --text-faint:   #3a3a5a;
  --accent:       #e8503a;
  --accent-dim:   rgba(232,80,58,0.12);
  --accent2:      #c9a040;
  --accent3:      #4a8fcf;
  --accent3-dim:  rgba(74,143,207,0.10);
  --white:        #f0f0f8;
  --mono:         'Space Mono', monospace;
  --serif:        'Crimson Pro', Georgia, serif;
  --display:      'Bebas Neue', sans-serif;
  --ease:         cubic-bezier(0.4,0,0.2,1);
}
:root.light {
  --bg:#f8f9fc; --bg2:#fff; --surface:#f0f2f8; --card:#fff;
  --border:#e0e2ec; --border-bright:#c0c2d0;
  --text:#2a2a40; --text-muted:#6a6a80; --text-faint:#a0a0b8;
  --accent-dim:rgba(232,80,58,0.08); --accent3-dim:rgba(74,143,207,0.08);
  --white:#2a2a40;
}

/* ── RESET ── */
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
html{scroll-behavior:smooth}
body{font-family:var(--serif);background:var(--bg);color:var(--text);line-height:1.8;-webkit-font-smoothing:antialiased;overflow-x:hidden;transition:background .3s,color .3s}
::selection{background:var(--accent);color:#000}
::-webkit-scrollbar{width:4px}
::-webkit-scrollbar-track{background:var(--bg)}
::-webkit-scrollbar-thumb{background:var(--accent)}

/* ── NOISE OVERLAY ── */
.noise{position:fixed;inset:0;z-index:0;pointer-events:none;opacity:.025;
  background-image:url("data:image/svg+xml,%3Csvg viewBox='0 0 512 512' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.65' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='512' height='512' filter='url(%23n)'/%3E%3C/svg%3E")}
.light .noise{opacity:.05}

/* ── NAV ── */
nav{
  position:fixed;top:0;width:100%;z-index:200;
  background:rgba(8,8,14,.92);backdrop-filter:blur(24px);
  border-bottom:1px solid var(--border);
  height:56px;display:flex;align-items:center;justify-content:space-between;
  padding:0 32px;font-family:var(--mono);transition:background .3s,border-color .3s;
}
.light nav{background:rgba(248,249,252,.92)}
.nav-brand{font-size:.75rem;font-weight:700;color:var(--accent);letter-spacing:3px;text-transform:uppercase;text-decoration:none}
.nav-right{display:flex;gap:8px;align-items:center}
.nav-pill{
  background:none;border:1px solid var(--border);color:var(--text-muted);
  font-family:var(--mono);font-size:.62rem;letter-spacing:2px;
  padding:5px 14px;cursor:pointer;text-decoration:none;
  display:inline-flex;align-items:center;transition:all .2s;
}
.nav-pill:hover,.nav-pill.active{border-color:var(--accent);color:var(--accent);background:var(--accent-dim)}
.theme-btn{
  background:none;border:1px solid var(--border);color:var(--text-muted);
  width:36px;height:36px;cursor:pointer;display:flex;align-items:center;justify-content:center;
  font-size:.9rem;transition:all .2s;
}
.theme-btn:hover{border-color:var(--accent);color:var(--accent);background:var(--accent-dim)}

/* ── HERO STRIP ── */
.hero-strip{
  padding-top:56px;
  border-bottom:1px solid var(--border);
  display:grid;grid-template-columns:1fr auto;
  gap:0;
}
.hero-left{padding:60px 72px 52px;border-right:1px solid var(--border)}
.hero-eyebrow{
  font-family:var(--mono);font-size:.62rem;letter-spacing:4px;
  color:var(--accent);text-transform:uppercase;
  margin-bottom:20px;display:flex;align-items:center;gap:12px;
}
.hero-eyebrow::before{content:'';width:36px;height:1px;background:var(--accent)}
.hero-title{
  font-family:var(--display);
  font-size:clamp(3.5rem,7vw,7rem);
  line-height:.92;letter-spacing:3px;
  color:var(--white);margin-bottom:18px;
}
.hero-title span{color:var(--accent)}
.hero-desc{
  font-size:1.05rem;color:var(--text-muted);font-style:italic;
  border-left:3px solid var(--accent);padding-left:16px;
  max-width:480px;line-height:1.9;margin-bottom:32px;
  transition:color .3s;
}
.hero-tags{display:flex;gap:6px;flex-wrap:wrap}
.hero-tag{
  font-family:var(--mono);font-size:.6rem;letter-spacing:1.5px;
  color:var(--text-muted);background:var(--surface);
  border:1px solid var(--border);padding:4px 12px;text-transform:uppercase;
}
.hero-right{
  display:flex;flex-direction:column;align-items:center;justify-content:center;
  padding:40px 48px;gap:24px;min-width:220px;
}
.stat-block{text-align:center}
.stat-block .n{
  font-family:var(--display);font-size:4rem;color:var(--accent);
  line-height:1;display:block;
}
.stat-block .l{
  font-family:var(--mono);font-size:.58rem;letter-spacing:2.5px;
  color:var(--text-muted);text-transform:uppercase;display:block;margin-top:4px;
}
.stat-divider{width:1px;height:40px;background:var(--border)}

/* ── CONTROLS BAR ── */
.controls-bar{
  display:flex;align-items:center;gap:0;
  border-bottom:1px solid var(--border);
  padding:0 72px;height:52px;
  font-family:var(--mono);font-size:.62rem;
  overflow-x:auto;
}
.filter-btn{
  height:100%;padding:0 20px;
  background:none;border:none;border-right:1px solid var(--border);
  color:var(--text-muted);cursor:pointer;letter-spacing:2px;
  text-transform:uppercase;font-family:var(--mono);font-size:.62rem;
  transition:all .2s;white-space:nowrap;
}
.filter-btn:first-child{border-left:1px solid var(--border)}
.filter-btn.active,.filter-btn:hover{color:var(--accent);background:var(--accent-dim)}
.search-wrap{
  flex:1;display:flex;align-items:center;gap:10px;
  padding:0 20px;border-right:1px solid var(--border);
  min-width:180px;
}
.search-wrap::before{content:'§';color:var(--text-faint);font-size:.8rem}
.search-wrap input{
  background:none;border:none;color:var(--text);
  font-family:var(--mono);font-size:.65rem;letter-spacing:1px;
  width:100%;outline:none;
}
.search-wrap input::placeholder{color:var(--text-faint)}
.controls-bar .list-link{
  height:100%;padding:0 20px;display:flex;align-items:center;
  color:var(--text-muted);text-decoration:none;letter-spacing:2px;
  text-transform:uppercase;white-space:nowrap;
  border-right:1px solid var(--border);transition:all .2s;
}
.controls-bar .list-link:hover{color:var(--accent);background:var(--accent-dim)}

/* ── MAIN CONTENT ── */
.main{max-width:100%;padding:64px 72px 80px}

/* ── DAY GROUP ── */
.day-group{margin-bottom:56px}
.day-group.hidden{display:none}
.day-header-row{
  display:flex;align-items:flex-end;justify-content:space-between;
  border-bottom:1px solid var(--border);padding-bottom:14px;margin-bottom:24px;
}
.day-eyebrow{
  font-family:var(--mono);font-size:.58rem;letter-spacing:3px;
  color:var(--accent);text-transform:uppercase;margin-bottom:4px;
}
.day-date{
  font-family:var(--display);font-size:clamp(2rem,4vw,3.2rem);
  letter-spacing:2px;color:var(--white);line-height:1;
}
.day-header-right{
  font-family:var(--mono);font-size:.58rem;letter-spacing:2px;
  color:var(--text-faint);text-transform:uppercase;
  padding-bottom:4px;
}

/* ── CARD GRID ── */
.card-grid{
  display:grid;
  grid-template-columns:repeat(auto-fill,minmax(450px,1fr));
  gap:1px;background:var(--border);
  border:1px solid var(--border);
}

/* ── RADAR CARD ── */
.radar-card{
  background:var(--card);padding:28px 24px;
  display:flex;flex-direction:column;gap:12px;
  transition:background .2s;position:relative;
  opacity:0;transform:translateY(16px);
  animation:fadeUp .55s var(--ease) forwards;
}
.radar-card:hover{background:var(--surface)}
.radar-card.hidden{display:none}

.radar-card-top{display:flex;justify-content:space-between;align-items:flex-start;gap:12px}
.radar-card-meta{display:flex;align-items:center;gap:8px;flex-wrap:wrap}

.type-tag{
  font-family:var(--mono);font-size:.55rem;letter-spacing:2px;
  padding:3px 8px;text-transform:uppercase;
}
.type-tag.news{background:var(--accent3-dim);color:var(--accent3);border:1px solid rgba(74,143,207,.25)}
.type-tag.academic{background:var(--accent-dim);color:var(--accent);border:1px solid rgba(232,80,58,.25)}

.card-chapter{
  font-family:var(--mono);font-size:.55rem;letter-spacing:1px;
  color:var(--text-faint);text-transform:uppercase;
}
.draft-dot{color:var(--accent2);font-size:.65rem;line-height:1}

.radar-score{
  font-family:var(--display);font-size:2rem;color:var(--accent);
  line-height:1;text-align:right;white-space:nowrap;flex-shrink:0;
}
.radar-score span{
  display:block;font-family:var(--mono);font-size:.48rem;
  color:var(--text-faint);letter-spacing:1px;text-align:right;margin-top:2px;
}

.radar-card-title{
  font-family:var(--display);font-size:1.25rem;letter-spacing:1px;
  color:var(--white);line-height:1.2;
}
.radar-card-title a{color:inherit;text-decoration:none;border-bottom:1px solid transparent;transition:border-color .2s}
.radar-card-title a:hover{border-bottom-color:var(--accent2)}

.radar-card-body{font-size:.88rem;color:var(--text-muted);line-height:1.8;flex:1;transition:color .3s}

.radar-card-footer{
  display:flex;justify-content:space-between;align-items:center;
  padding-top:10px;border-top:1px solid var(--border);
  font-family:var(--mono);font-size:.58rem;letter-spacing:1.5px;
  transition:border-color .3s;
}
.card-source-link{color:var(--accent2);text-decoration:none;text-transform:uppercase;transition:color .2s}
.card-source-link:hover{color:var(--white)}
.full-report-link{color:var(--text-faint);text-decoration:none;text-transform:uppercase;transition:color .2s}
.full-report-link:hover{color:var(--accent)}

/* ── EMPTY STATE ── */
.empty-state{
  display:none;text-align:center;padding:80px 32px;
  font-family:var(--mono);color:var(--text-faint);letter-spacing:2px;
  font-size:.7rem;text-transform:uppercase;
}
.empty-state .glyph{font-family:var(--display);font-size:5rem;color:var(--text-faint);opacity:.3;display:block;margin-bottom:16px}

/* ── STATUS BAR ── */
.status-bar{
  position:fixed;bottom:0;width:100%;z-index:200;
  background:var(--bg);border-top:1px solid var(--border);
  padding:10px 32px;font-family:var(--mono);font-size:.6rem;
  color:var(--text-faint);letter-spacing:2px;
  display:flex;justify-content:space-between;align-items:center;
  transition:background .3s,border-color .3s;
}
.status-dot{
  display:inline-block;width:6px;height:6px;
  background:var(--accent);border-radius:50%;margin-right:8px;
  animation:pulse 2s infinite;
}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.2}}
@keyframes fadeUp{to{opacity:1;transform:translateY(0)}}

/* ── RESPONSIVE ── */
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
  <a href="https://brook-han.github.io/Renegade-AI/" class="nav-brand">RENEGADE AI v5.3</a>
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
      <span class="hero-tag">NEWS TOP 10 + PAPERS TOP 5</span>
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
  <button class="filter-btn active" data-filter="all">ALL</button>
  <button class="filter-btn" data-filter="news">📰 NEWS</button>
  <button class="filter-btn" data-filter="academic">📄 PAPERS</button>
  <div class="search-wrap">
    <input type="text" id="searchInput" placeholder="SEARCH TITLES &amp; SUMMARIES">
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
    btns.forEach(x=>x.classList.remove('active'));
    b.classList.add('active');
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
  c.style.animationDelay=(i*0.06)+'s';
});
</script>
</body>
</html>'''


# ═══════════════════════════════════════════════════════════════
# 主函数
# ═══════════════════════════════════════════════════════════════
def main():
    print("🚀 Renegade AI Radar Index Generator v2.1 (Optimized Edition)")
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
    latest = data["dates"][0] if data["dates"] else "unknown"

    files_to_add = [
        "docs/index.html",
        "docs/news/index.html",
        "docs/academic/index.html",
    ]

    try:
        subprocess.run(
            ["git", "add"] + files_to_add,
            cwd=repo_root, check=True, capture_output=True,
        )
    except subprocess.CalledProcessError as e:
        print(f"⚠️ git add 失败: {e.stderr.decode()}")
        return

    commit_msg = f"chore: auto-update radar index [{latest}]"
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

    try:
        subprocess.run(
            ["git", "pull", "--rebase", "--quiet"],
            cwd=repo_root, check=True, capture_output=True,
        )
    except subprocess.CalledProcessError:
        pass  # pull 失败不阻塞 push（比如还没设置 upstream）

    try:
        result = subprocess.run(
            ["git", "push", "origin", "HEAD"],
            cwd=repo_root, capture_output=True,
        )
        if result.returncode == 0:
            print("✅ Git push 成功")
        elif b"Everything up-to-date" in result.stderr or b"up to date" in result.stderr:
            print("✅ Already up-to-date")
        else:
            print(f"⚠️ git push 失败: {result.stderr.decode()}")
    except subprocess.CalledProcessError as e:
        print(f"⚠️ git push 失败: {e.stderr.decode()}")


if __name__ == "__main__":
    main()
