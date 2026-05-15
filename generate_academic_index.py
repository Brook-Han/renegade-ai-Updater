#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎓 Renegade AI 学术论文列表页生成器
视觉风格与 Renegade AI v5.3 网页完全对齐

用法：
    python generate_academic_index.py
输出：
    docs/academic/index.html

特性：
    - 最新日期显示 Top 3，历史日期显示 Top 1
    - 无圆角网格卡片，与主页 card-grid 同构
    - 暗色优先 + 亮色切换
    - 脉冲状态栏
    - 保留"完整报告"链接
"""

import re
from pathlib import Path
from html import escape

# ═══════════════════════════════════════════════════════════════
# 配置
# ═══════════════════════════════════════════════════════════════
ACADEMIC_DIR = Path("docs/academic")
OUTPUT_FILE  = ACADEMIC_DIR / "index.html"


# ═══════════════════════════════════════════════════════════════
# 提取卡片（复用主页逻辑）
# ═══════════════════════════════════════════════════════════════
def extract_cards_from_html(html_path: Path, report_type: str = "academic") -> list[dict]:
    try:
        content = html_path.read_text(encoding="utf-8")
    except Exception as e:
        print(f"⚠️ 读取失败 {html_path.name}: {e}")
        return []

    cards = []
    card_blocks = re.findall(
        r'<div class="card">(.*?)</div>\s*(?=<div class="card">|</main>|</body>|$)',
        content, re.DOTALL,
    )

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

        chapter_m = re.search(r"📍\s*([^<\s][^<]*?)(?:</span>|<|&nbsp;|$)", block)
        if chapter_m:
            card["chapter"] = chapter_m.group(1).strip()

        card["has_draft"] = '<div class="card-draft">' in block

        if card.get("title"):
            cards.append(card)
    return cards


# ═══════════════════════════════════════════════════════════════
# 收集学术报告
# ═══════════════════════════════════════════════════════════════
def collect_academic_reports() -> dict:
    if not ACADEMIC_DIR.exists():
        print("❌ docs/academic 目录不存在")
        return {"dates": [], "by_date": {}, "stats": {"total": 0, "days": 0}}

    entries = []
    for html_file in sorted(ACADEMIC_DIR.glob("academic_report_*.html")):
        if html_file.name == "index.html":
            continue
        m = re.search(r"(\d{4}-\d{2}-\d{2})(?:_(\d{6}))?", html_file.name)
        if not m:
            continue
        entries.append({
            "date":          m.group(1),
            "time":          m.group(2) if m.group(2) else "000000",
            "path":          html_file,
            "relative_link": html_file.name,
        })

    by_date = {}
    for e in entries:
        by_date.setdefault(e["date"], []).append(e)
    for lst in by_date.values():
        lst.sort(key=lambda x: x["time"], reverse=True)

    sorted_dates = sorted(by_date.keys(), reverse=True)
    return {
        "dates":   sorted_dates,
        "by_date": by_date,
        "stats":   {"total": len(entries), "days": len(sorted_dates)},
    }


# ═══════════════════════════════════════════════════════════════
# 生成日期区块（v5.3 风格）
# ═══════════════════════════════════════════════════════════════
def generate_day_block(date: str, entries: list[dict], top_n: int = None) -> str:
    all_cards = []
    for e in entries:
        cards = extract_cards_from_html(e["path"])
        for c in cards:
            c["_report_link"] = e["relative_link"]
        all_cards.extend(cards)

    # 简单去重
    seen, unique = set(), []
    for c in all_cards:
        key = (c.get("title", ""), c.get("summary", "")[:80])
        if key not in seen:
            seen.add(key)
            unique.append(c)
    all_cards = unique

    all_cards.sort(key=lambda c: float(c.get("score", 0)), reverse=True)
    if not all_cards:
        return ""

    total_cards   = len(all_cards)
    display_cards = all_cards[:top_n] if top_n is not None else all_cards

    latest_time    = entries[0]["time"]
    formatted_time = f"{latest_time[:2]}:{latest_time[2:4]}:{latest_time[4:]}"

    if top_n is not None and total_cards > top_n:
        count_label = f"TOP {len(display_cards)} / {total_cards} PAPERS"
    else:
        count_label = f"{total_cards} PAPERS"

    html = f'''
<div class="day-group" data-date="{date}">
  <div class="day-header-row">
    <div class="day-header-left">
      <div class="day-eyebrow">ACADEMIC · {formatted_time}</div>
      <h2 class="day-date">{date}</h2>
    </div>
    <div class="day-header-right">{count_label}</div>
  </div>
  <div class="card-grid">
'''

    for card in display_cards:
        title      = escape(card.get("title", ""))
        score      = card.get("score", "5.0")
        summary    = escape(card.get("summary", "")[:240])
        chapter    = escape(card.get("chapter", ""))
        link       = card.get("link", "#")
        report_rel = card.get("_report_link", "")

        chapter_html  = f'<span class="card-chapter">§ {chapter}</span>' if chapter else ""
        source_html   = (f'<a class="card-source-link" href="{escape(link)}" '
                         f'target="_blank" rel="noopener">↗ PDF / SOURCE</a>'
                         if link and link != "#" else "")
        draft_dot     = '<span class="draft-dot" title="Has Draft">●</span>' if card.get("has_draft") else ""
        truncated     = "…" if len(card.get("summary", "")) > 240 else ""

        html += f'''    <article class="radar-card" data-type="academic">
      <div class="radar-card-top">
        <div class="radar-card-meta">
          <span class="type-tag">PAPER</span>
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
        {source_html}
        <a class="full-report-link" href="./{report_rel}">FULL REPORT →</a>
      </div>
    </article>
'''

    html += "  </div>\n</div>\n"
    return html


# ═══════════════════════════════════════════════════════════════
# HTML 模板 — v5.3 完整风格
# ═══════════════════════════════════════════════════════════════
def get_html_template() -> str:
    return '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Academic Archive · Renegade AI</title>
  <meta name="description" content="Academic paper archive curated through the lens of Renegade AI — cognitive friction, not cognitive flattery.">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Space+Mono:ital,wght@0,400;0,700;1,400&family=Crimson+Pro:ital,wght@0,300;0,400;0,600;1,300;1,400&family=Bebas+Neue&display=swap" rel="stylesheet">
  <style>
/* ── DESIGN TOKENS ── */
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
body{font-family:var(--serif);background:var(--bg);color:var(--text);
     line-height:1.8;-webkit-font-smoothing:antialiased;overflow-x:hidden;
     transition:background .3s,color .3s}
::selection{background:var(--accent);color:#000}
::-webkit-scrollbar{width:4px}
::-webkit-scrollbar-track{background:var(--bg)}
::-webkit-scrollbar-thumb{background:var(--accent)}

/* ── NOISE ── */
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
.nav-brand{font-size:.75rem;font-weight:700;color:var(--accent);letter-spacing:3px;
           text-transform:uppercase;text-decoration:none}
.nav-right{display:flex;gap:8px;align-items:center}
.nav-pill{
  background:none;border:1px solid var(--border);color:var(--text-muted);
  font-family:var(--mono);font-size:.62rem;letter-spacing:2px;
  padding:5px 14px;cursor:pointer;text-decoration:none;
  display:inline-flex;align-items:center;transition:all .2s;
}
.nav-pill:hover{border-color:var(--accent);color:var(--accent);background:var(--accent-dim)}
.theme-btn{
  background:none;border:1px solid var(--border);color:var(--text-muted);
  width:36px;height:36px;cursor:pointer;display:flex;align-items:center;
  justify-content:center;font-size:.9rem;transition:all .2s;
}
.theme-btn:hover{border-color:var(--accent);color:var(--accent);background:var(--accent-dim)}

/* ── HERO STRIP ── */
.hero-strip{
  padding-top:56px;border-bottom:1px solid var(--border);
  display:grid;grid-template-columns:1fr auto;
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
  font-size:clamp(3rem,6vw,6rem);
  line-height:.92;letter-spacing:3px;color:var(--white);margin-bottom:18px;
}
.hero-title span{color:var(--accent)}
.hero-desc{
  font-size:1.05rem;color:var(--text-muted);font-style:italic;
  border-left:3px solid var(--accent);padding-left:16px;
  max-width:480px;line-height:1.9;margin-bottom:32px;transition:color .3s;
}
.hero-tags{display:flex;gap:6px;flex-wrap:wrap}
.hero-tag{
  font-family:var(--mono);font-size:.6rem;letter-spacing:1.5px;
  color:var(--text-muted);background:var(--surface);
  border:1px solid var(--border);padding:4px 12px;text-transform:uppercase;
}
.hero-right{
  display:flex;flex-direction:column;align-items:center;justify-content:center;
  padding:40px 52px;gap:24px;min-width:200px;
}
.stat-block{text-align:center}
.stat-block .n{font-family:var(--display);font-size:4rem;color:var(--accent);line-height:1;display:block}
.stat-block .l{font-family:var(--mono);font-size:.58rem;letter-spacing:2.5px;
               color:var(--text-muted);text-transform:uppercase;display:block;margin-top:4px}
.stat-divider{width:1px;height:40px;background:var(--border)}

/* ── CONTROLS BAR ── */
.controls-bar{
  display:flex;align-items:center;gap:0;
  border-bottom:1px solid var(--border);
  padding:0 72px;height:52px;font-family:var(--mono);font-size:.62rem;
  overflow-x:auto;
}
.filter-btn{
  height:100%;padding:0 20px;background:none;
  border:none;border-right:1px solid var(--border);
  color:var(--text-muted);cursor:pointer;letter-spacing:2px;
  text-transform:uppercase;font-family:var(--mono);font-size:.62rem;
  transition:all .2s;white-space:nowrap;
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
  font-family:var(--mono);font-size:.65rem;letter-spacing:1px;
  width:100%;outline:none;
}
.search-wrap input::placeholder{color:var(--text-faint)}
.back-link{
  height:100%;padding:0 20px;display:flex;align-items:center;
  color:var(--text-muted);text-decoration:none;letter-spacing:2px;
  text-transform:uppercase;white-space:nowrap;transition:all .2s;
}
.back-link:hover{color:var(--accent);background:var(--accent-dim)}

/* ── MAIN ── */
.main{padding:64px 72px 100px;position:relative;z-index:1}

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
  color:var(--text-faint);text-transform:uppercase;padding-bottom:4px;
}

/* ── CARD GRID ── */
.card-grid{
  display:grid;grid-template-columns:repeat(auto-fill,minmax(720px,1fr));
  gap:1px;background:var(--border);border:1px solid var(--border);
}

/* ── RADAR CARD ── */
.radar-card{
  background:var(--card);padding:28px 24px;
  display:flex;flex-direction:column;gap:12px;
  transition:background .2s;
  opacity:0;transform:translateY(16px);
  animation:fadeUp .55s var(--ease) forwards;
}
.radar-card:hover{background:var(--surface)}
.radar-card.hidden{display:none}

.radar-card-top{display:flex;justify-content:space-between;align-items:flex-start;gap:12px}
.radar-card-meta{display:flex;align-items:center;gap:8px;flex-wrap:wrap}

.type-tag{
  font-family:var(--mono);font-size:.55rem;letter-spacing:2px;padding:3px 8px;
  text-transform:uppercase;
  background:var(--accent-dim);color:var(--accent);border:1px solid rgba(232,80,58,.25);
}
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

.radar-card-body{
  font-size:.88rem;color:var(--text-muted);line-height:1.8;flex:1;transition:color .3s;
}

.radar-card-footer{
  display:flex;justify-content:space-between;align-items:center;
  padding-top:10px;border-top:1px solid var(--border);
  font-family:var(--mono);font-size:.58rem;letter-spacing:1.5px;transition:border-color .3s;
}
.card-source-link{color:var(--accent2);text-decoration:none;text-transform:uppercase;transition:color .2s}
.card-source-link:hover{color:var(--white)}
.full-report-link{color:var(--text-faint);text-decoration:none;text-transform:uppercase;transition:color .2s}
.full-report-link:hover{color:var(--accent)}

/* ── EMPTY ── */
.empty-state{
  display:none;text-align:center;padding:80px 32px;
  font-family:var(--mono);color:var(--text-faint);
  letter-spacing:2px;font-size:.7rem;text-transform:uppercase;
}
.empty-state .glyph{
  font-family:var(--display);font-size:5rem;color:var(--text-faint);
  opacity:.3;display:block;margin-bottom:16px;
}

/* ── FOOTER ── */
footer{margin-top:64px;padding-top:24px;border-top:1px solid var(--border);font-family:var(--mono);font-size:.6rem;color:var(--text-muted);display:flex;justify-content:space-between}
footer a{color:var(--text-muted);text-decoration:none}footer a:hover{color:var(--accent)}

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
  background:var(--accent3);border-radius:50%;margin-right:8px;
  animation:pulse 2s infinite;
}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.2}}
@keyframes fadeUp{to{opacity:1;transform:translateY(0)}}

/* ── RESPONSIVE ── */
@media(max-width:900px){
  .main{padding:48px 24px 100px}
  .controls-bar{padding:0 24px}
  .hero-strip{grid-template-columns:1fr}
  .hero-left{padding:48px 24px 36px;border-right:none;border-bottom:1px solid var(--border)}
  .hero-right{flex-direction:row;padding:24px;border-bottom:1px solid var(--border)}
  .stat-divider{width:40px;height:1px}
  .card-grid{grid-template-columns:1fr}
}
  </style>
</head>
<body>
<div class="noise"></div>

<!-- NAV -->
<nav>
  <a href="https://brook-han.github.io/Renegade-AI/" class="nav-brand">RENEGADE AI v5.3</a>
  <div class="nav-right">
    <a href="../index.html" class="nav-pill">HOME</a>
    <a href="../news/" class="nav-pill">NEWS</a>
    <a href="index.html" class="nav-pill active">PAPERS</a>
    <button class="theme-btn" id="themeBtn" aria-label="Toggle theme">◐</button>
  </div>
</nav>

<!-- HERO -->
<div class="hero-strip">
  <div class="hero-left">
    <div class="hero-eyebrow">§ Academic Archive</div>
    <h1 class="hero-title">ACADEMIC<br><span>ARCHIVE</span></h1>
    <p class="hero-desc">
      Peer-reviewed signal — papers mapped to the arguments that matter,
      ranked by relevance to cognitive friction and civilizational diagnosis.
    </p>
    <div class="hero-tags">
      <span class="hero-tag" id="tagTotal">— REPORTS</span>
      <span class="hero-tag" id="tagDays">— DAYS</span>
      <span class="hero-tag">TOP 3 LATEST · TOP 1 ARCHIVE</span>
      <span class="hero-tag">SCORE / 10</span>
    </div>
  </div>
  <div class="hero-right">
    <div class="stat-block">
      <span class="n" id="statTotal">—</span>
      <span class="l">Reports</span>
    </div>
    <div class="stat-divider"></div>
    <div class="stat-block">
      <span class="n" id="statDays">—</span>
      <span class="l">Days</span>
    </div>
  </div>
</div>

<!-- CONTROLS -->
<div class="controls-bar">
  <button class="filter-btn active" data-filter="all">ALL</button>
  <button class="filter-btn" data-filter="draft">✍ DRAFT</button>
  <div class="search-wrap">
    <input type="text" id="searchInput" placeholder="SEARCH TITLES &amp; ABSTRACTS">
  </div>
  <a href="../index.html" class="back-link">← MAIN DIGEST</a>
</div>

<!-- MAIN -->
<main class="main">
  {{ day_sections }}
  <div class="empty-state" id="emptyState">
    <span class="glyph">∅</span>
    NO RESULTS · ADJUST SEARCH TERMS
  </div>
  <footer>
    <span>Renegade AI v5.3 · Brooks Han</span>
    <a href="https://github.com/Brook-Han/renegade-ai-Updater" target="_blank">GitHub ↗</a>
  </footer>
</main>

<!-- STATUS BAR -->
<div class="status-bar">
  <span><span class="status-dot"></span><span id="statusText">STATUS: [ RENEGADE_SEED_STATUS: GERMINATING ]</span></span>
  <span id="statusTime"></span>
</div>

<script>
/* ── THEME ── */
(function(){
  const h=document.documentElement,b=document.getElementById('themeBtn');
  const apply=t=>{h.classList.toggle('light',t==='light');localStorage.setItem('renegade-theme',t)};
  apply(localStorage.getItem('renegade-theme')||(matchMedia('(prefers-color-scheme:dark)').matches?'dark':'light'));
  b.onclick=()=>apply(h.classList.contains('light')?'dark':'light');
})();

/* ── STATS ── */
(function(){
  const t={{ total_reports }},d={{ days_count }};
  document.getElementById('statTotal').textContent=t;
  document.getElementById('statDays').textContent=d;
  document.getElementById('tagTotal').textContent=t+' REPORTS';
  document.getElementById('tagDays').textContent=d+' DAYS';
})();

/* ── FILTER + SEARCH ── */
(function(){
  const btns  = document.querySelectorAll('.filter-btn');
  const inp   = document.getElementById('searchInput');
  const cards = document.querySelectorAll('.radar-card');
  const groups= document.querySelectorAll('.day-group');
  const empty = document.getElementById('emptyState');
  let filter='all', query='';

  function update(){
    let visible=0;
    cards.forEach(c=>{
      const hasDraft = c.querySelector('.draft-dot') !== null;
      const titleT   = (c.querySelector('.radar-card-title')?.textContent||'').toLowerCase();
      const bodyT    = (c.querySelector('.radar-card-body')?.textContent||'').toLowerCase();
      const filterOk = filter==='all' || (filter==='draft' && hasDraft);
      const searchOk = !query || titleT.includes(query) || bodyT.includes(query);
      const show     = filterOk && searchOk;
      c.classList.toggle('hidden',!show);
      if(show) visible++;
    });
    groups.forEach(g=>{
      const any = g.querySelectorAll('.radar-card:not(.hidden)').length > 0;
      g.classList.toggle('hidden',!any);
    });
    empty.style.display = visible===0 ? 'block' : 'none';
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
    st.textContent=messages[i%messages.length]; i++;
    tm.textContent=new Date().toISOString().replace('T',' ').slice(0,19)+' UTC';
  }
  tick(); setInterval(tick,5000);
})();

/* ── STAGGERED ANIMATION ── */
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
    print("🎓 Renegade AI Academic Index Generator (v5.3 Visual Edition)")
    data = collect_academic_reports()
    if not data["dates"]:
        print("❌ 没有找到学术报告文件")
        return

    latest_date = data["dates"][0]
    print(f"✅ 找到 {data['stats']['total']} 份报告 · {data['stats']['days']} 天")

    day_sections = []
    for date in data["dates"]:
        entries = data["by_date"][date]
        top_n   = 3 if date == latest_date else 1
        block   = generate_day_block(date, entries, top_n=top_n)
        if block:
            day_sections.append(block)

    template = get_html_template()
    html = template.replace("{{ day_sections }}", "\n".join(day_sections))
    html = html.replace("{{ total_reports }}", str(data["stats"]["total"]))
    html = html.replace("{{ days_count }}", str(data["stats"]["days"]))

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text(html, encoding="utf-8")
    print(f"✅ 学术列表页已生成: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()