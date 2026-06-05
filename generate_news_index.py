#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📰 Renegade AI 新闻列表页生成器
与主页 radar_index_generator.py 共用相同 CSS 风格
用法：
    python generate_news_index.py
输出：
    docs/news/index.html
特性：
    - 最新日期显示 Top 3 新闻，历史日期显示 Top 1
    - 保留“查看完整报告”链接，可浏览当日全部条目
"""

import re
from pathlib import Path
from html import escape

from config import Config
from card_utils import extract_cards_from_html

# ───────────────────────────────
# 配置
# ───────────────────────────────
NEWS_DIR = Config.OUTPUT_DIR / "news"
OUTPUT_FILE = NEWS_DIR / "index.html"


# ───────────────────────────────
# 收集所有新闻报告文件
# ───────────────────────────────
def collect_news_reports() -> dict:
    if not NEWS_DIR.exists():
        print("❌ docs/news 目录不存在")
        return {"by_date": {}, "stats": {"total": 0, "days": 0}}

    entries = []
    for html_file in sorted(NEWS_DIR.glob("news_report_*.html")):
        if html_file.name == "index.html":
            continue
        m = re.search(r"(\d{4}-\d{2}-\d{2})(?:_(\d{6}))?", html_file.name)
        if not m:
            continue
        date_str = m.group(1)
        time_str = m.group(2) if m.group(2) else "000000"
        entries.append({
            "date": date_str,
            "time": time_str,
            "path": html_file,
            "relative_link": html_file.name,
        })

    # 按日期分组
    by_date = {}
    for e in entries:
        by_date.setdefault(e["date"], []).append(e)
    for lst in by_date.values():
        lst.sort(key=lambda x: x["time"], reverse=True)

    sorted_dates = sorted(by_date.keys(), reverse=True)
    stats = {
        "total": len(entries),
        "days": len(sorted_dates),
    }
    return {
        "dates": sorted_dates,
        "by_date": by_date,
        "stats": stats,
    }


# ───────────────────────────────
# 生成一个日期的 HTML 区块（支持限制显示条数）
# ───────────────────────────────
def generate_day_block(date: str, entries: list[dict], top_n: int = None) -> str:
    """
    date: 日期字符串
    entries: 该日期的报告文件列表
    top_n: 显示前 N 条卡片，None 表示全部显示
    """
    all_cards = []
    for e in entries:
        cards = extract_cards_from_html(e["path"], "news")
        for c in cards:
            c["_report_link"] = e["relative_link"]
        all_cards.extend(cards)

    # 去重
    seen = set()
    unique = []
    for c in all_cards:
        key = (c.get("title", ""), c.get("summary", "")[:80])
        if key not in seen:
            seen.add(key)
            unique.append(c)
    all_cards = unique

    # 按评分降序
    all_cards.sort(key=lambda c: float(c.get("score", 0)), reverse=True)

    if not all_cards:
        return ""

    # 选择要展示的卡片数量
    total_cards = len(all_cards)
    display_cards = all_cards[:top_n] if top_n is not None else all_cards

    # 格式化时间
    latest_time = entries[0]["time"]
    formatted_time = f"{latest_time[:2]}:{latest_time[2:4]}:{latest_time[4:]}"

    # 构建元信息行（显示展示数量 / 总数）
    if top_n is not None and total_cards > top_n:
        meta_text = f"⏰ {formatted_time} · 📊 展示前 {len(display_cards)} 条 / 共 {total_cards} 条新闻"
    else:
        meta_text = f"⏰ {formatted_time} · 📊 共 {total_cards} 条新闻"

    html = f'<div class="day-group" data-date="{date}">\n'
    html += f'  <h2 class="day-header">{date}</h2>\n'
    html += f'  <div class="day-meta">{meta_text}</div>\n'

    for card in display_cards:
        title = escape(card.get("title", ""))
        score = card.get("score", "5.0")
        summary = escape(card.get("summary", "")[:200])
        chapter = escape(card.get("chapter", ""))
        link = card.get("link", "#")
        report_link = card.get("_report_link", "")

        link_html = f'<a href="{escape(link)}" target="_blank" rel="noopener">↗ 原文</a>' if link and link != "#" else ""

        html += f'''
  <article class="card" data-type="news">
    <div class="card-header">
      <div class="card-title">
        <a href="{escape(link)}" target="_blank" rel="noopener">{title}</a>
        <span class="type-badge news">📰 新闻</span>
      </div>
      <div class="card-score">{score}<span>/10</span></div>
    </div>
    <div class="card-meta">
      {f'<span>📍 {chapter}</span>' if chapter else ''}
      {f'<span>·</span>' if chapter and link_html else ''}
      {link_html}
    </div>
    <div class="card-body">{summary}{'...' if len(card.get('summary','')) > 200 else ''}</div>
    <div class="card-link">
      <a href="./{report_link}">查看 {date} 完整报告 →</a>
    </div>
  </article>\n'''

    html += "</div>\n"
    return html


# ───────────────────────────────
# 完整 HTML 模板（沿用主页 CSS）
# ───────────────────────────────
def get_html_template() -> str:
    return '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>News Archive | Renegade AI</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Space+Mono:ital,wght@0,400;0,700;1,400&family=Crimson+Pro:ital,wght@0,300;0,400;0,600;1,300;1,400&family=Bebas+Neue&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css">
  <style>
    :root{--bg:#08080e;--card:#13131f;--border:#1e1e30;--text:#cccce0;--text-muted:#6868a0;--accent:#e8503a;--accent-dim:rgba(232,80,58,.12);--accent2:#c9a040;--accent3:#4a8fcf;--accent3-dim:rgba(74,143,207,.10);--white:#f0f0f8;--mono:'Space Mono',monospace;--serif:'Crimson Pro',serif;--display:'Bebas Neue',sans-serif}
    :root.light{--bg:#f8f9fc;--card:#fff;--border:#e0e2ec;--text:#2a2a40;--text-muted:#6a6a80;--accent-dim:rgba(232,80,58,.08);--accent3-dim:rgba(74,143,207,.08);--white:#2a2a40}
    *{box-sizing:border-box;margin:0;padding:0}
    body{font-family:var(--serif);background:var(--bg);color:var(--text);line-height:1.8;transition:background .3s,color .3s}
    nav{position:fixed;top:0;width:100%;z-index:200;background:rgba(8,8,14,.92);backdrop-filter:blur(24px);border-bottom:1px solid var(--border);height:56px;display:flex;align-items:center;justify-content:space-between;padding:0 32px;font-family:var(--mono)}
    .light nav{background:rgba(248,249,252,.92)}
    .nav-brand{font-size:.75rem;font-weight:700;color:var(--accent);letter-spacing:3px;text-transform:uppercase;text-decoration:none}
    .nav-right{display:flex;gap:8px;align-items:center}
    .nav-pill{background:none;border:1px solid var(--border);color:var(--text-muted);font-family:var(--mono);font-size:.62rem;letter-spacing:2px;padding:5px 14px;text-decoration:none;transition:all .2s}
    .nav-pill:hover,.nav-pill.active{border-color:var(--accent);color:var(--accent);background:var(--accent-dim)}
    .theme-btn{background:none;border:1px solid var(--border);color:var(--text-muted);width:36px;height:36px;cursor:pointer;display:flex;align-items:center;justify-content:center;font-size:.9rem;transition:all .2s}
    .theme-btn:hover{border-color:var(--accent);color:var(--accent);background:var(--accent-dim)}
    .main{max-width:960px;margin:0 auto;padding:100px 32px 60px}
    .page-eyebrow{font-family:var(--mono);font-size:.62rem;letter-spacing:4px;color:var(--accent);text-transform:uppercase;margin-bottom:8px;display:flex;align-items:center;gap:10px}
    .page-eyebrow::before{content:'';width:28px;height:1px;background:var(--accent)}
    h1{font-family:var(--display);font-size:3rem;letter-spacing:2px;color:var(--white);margin-bottom:6px;line-height:1}
    .subtitle{font-family:var(--mono);font-size:.65rem;color:var(--text-muted);letter-spacing:1.5px;margin-bottom:32px;display:flex;justify-content:space-between;flex-wrap:wrap;gap:8px}
    .controls{display:flex;gap:12px;margin-bottom:24px;flex-wrap:wrap;align-items:center}
    .filter-btn{font-family:var(--mono);font-size:.65rem;padding:6px 14px;border:1px solid var(--border);background:var(--bg);color:var(--text-muted);cursor:pointer;text-decoration:none}
    .filter-btn.active,.filter-btn:hover{border-color:var(--accent);color:var(--accent);background:var(--accent-dim)}
    .search{flex:1;min-width:200px;position:relative}
    .search input{width:100%;padding:8px 12px 8px 32px;border:1px solid var(--border);background:var(--card);color:var(--text)}
    .search i{position:absolute;left:10px;top:50%;transform:translateY(-50%);color:var(--text-muted)}
    .day-group{margin-bottom:48px}
    .day-header{font-family:var(--display);font-size:1.8rem;color:var(--white);border-bottom:1px solid var(--border);padding-bottom:8px;margin-bottom:4px}
    .day-meta{font-family:var(--mono);font-size:.65rem;color:var(--text-muted);margin-bottom:16px}
    .card{background:var(--card);border:1px solid var(--border);padding:24px;margin-bottom:8px}
    .card:hover{border-color:var(--accent)}
    .card-header{display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:10px;gap:12px}
    .card-title{font-family:var(--display);font-size:1.1rem;color:var(--white);flex:1;line-height:1.3}
    .card-title a{color:inherit;text-decoration:none;border-bottom:1px solid transparent}
    .card-title a:hover{border-bottom-color:var(--accent2)}
    .card-score{font-family:var(--display);font-size:1.8rem;line-height: 1;color:var(--accent);white-space:nowrap;text-align:right;flex-shrink:0}
    .card-score span{font-family:var(--mono);font-size:.5rem;color:var(--text-muted);display:block}
    .card-meta{font-family:var(--mono);font-size:.6rem;color:var(--text-muted);margin-bottom:12px;display:flex;gap:16px;flex-wrap:wrap}
    .card-meta a{color:var(--accent2);text-decoration:none}
    .card-body{font-size:.90rem;color:var(--text);line-height:1.8;margin-bottom:8px}
    .card-link{font-family:var(--mono);font-size:.65rem;margin-top:10px}
    .card-link a{color:var(--accent);text-decoration:none}
    .type-badge{display:inline-block;font-family:var(--mono);font-size:.55rem;padding:2px 6px;border-radius:2px;margin-left:6px}
    .type-badge.news{background:var(--accent3-dim);color:var(--accent3)}
    .draft-badge{font-size:.9rem;margin-left:4px}
    .empty{text-align:center;padding:48px;color:var(--text-muted);font-family:var(--mono)}
    footer{margin-top:64px;padding-top:24px;border-top:1px solid var(--border);font-family:var(--mono);font-size:.6rem;color:var(--text-muted);display:flex;justify-content:space-between}
    @media(max-width:600px){.main{padding:100px 16px 40px}h1{font-size:2.2rem}.controls{flex-direction:column;align-items:stretch}.search{width:100%}}
    .card.hidden,.day-group.hidden{display:none}
    .status-bar{position:fixed;bottom:0;width:100%;z-index:200;background:var(--bg);border-top:1px solid var(--border);padding:10px 32px;font-family:var(--mono);font-size:.6rem;color:var(--text-faint);letter-spacing:2px;display:flex;justify-content:space-between;align-items:center;transition:background .3s,border-color .3s}
    .status-dot{display:inline-block;width:6px;height:6px;background:var(--accent);border-radius:50%;margin-right:8px;animation:pulse 2s infinite}
    @keyframes pulse{0%,100%{opacity:1}50%{opacity:.2}}
  </style>
</head>
<body>
  <nav>
    <a href="https://brook-han.github.io/Renegade-AI/" class="nav-brand">RENEGADE AI v5.3</a>
    <div class="nav-right">
      <a href="../index.html" class="nav-pill">HOME</a>
      <a href="index.html" class="nav-pill active">NEWS</a>
      <a href="../academic/" class="nav-pill">PAPERS</a>
      <button class="theme-btn" id="themeBtn" aria-label="Toggle theme">◐</button>
    </div>
  </nav>
  <main class="main">
    <div class="page-eyebrow">§ News Archive</div>
    <h1>NEWS ARCHIVE</h1>
    <div class="subtitle">
      <span>📰 全部新闻条目 · 按日期排序</span>
      <span id="statsLine">共 {{ total_reports }} 份报告 · {{ days_count }} 天</span>
    </div>
    <div class="controls">
      <button class="filter-btn active" data-filter="all">All</button>
      <div class="search"><i class="fa fa-search"></i><input type="text" id="searchInput" placeholder="Search..."></div>
    </div>
    {{ day_sections }}
    <div class="empty" id="emptyState" style="display:none">
      <i class="fa fa-inbox" style="font-size:2rem;margin-bottom:12px;display:block"></i>
      <p>No results. Try adjusting keywords.</p>
    </div>
    <footer>
      <span>Renegade AI v5.3 · Brooks Han</span>
      <a href="https://github.com/Brook-Han/renegade-ai-Updater" target="_blank">GitHub ↗</a>
    </footer>
  </main>

  <div class="status-bar">
    <span><span class="status-dot"></span><span id="statusText">STATUS: [ NEWS_ARCHIVE · ACTIVE ]</span></span>
    <span id="statusTime"></span>
  </div>

  <script>
    (function(){const h=document.documentElement,b=document.getElementById('themeBtn');const a=t=>{h.classList.toggle('light',t==='light');localStorage.setItem('renegade-theme',t)};a(localStorage.getItem('renegade-theme')||(matchMedia('(prefers-color-scheme: dark)').matches?'dark':'light'));b.onclick=()=>a(h.classList.contains('light')?'dark':'light');})();
    (function(){const f=document.querySelectorAll('.filter-btn'),s=document.getElementById('searchInput'),c=document.querySelectorAll('.card'),g=document.querySelectorAll('.day-group'),e=document.getElementById('emptyState');let t='all',q='';const u=()=>{let v=0;c.forEach(x=>{const y=x.dataset.type,z=(x.querySelector('.card-title')?.textContent||'').toLowerCase(),w=(x.querySelector('.card-body')?.textContent||'').toLowerCase();const A=t==='all'||y===t,B=!q||z.includes(q)||w.includes(q);if(A&&B){x.classList.remove('hidden');v++;}else{x.classList.add('hidden');}});g.forEach(x=>{const y=x.querySelectorAll('.card:not(.hidden)');x.classList.toggle('hidden',y.length===0);});e.style.display=v===0?'block':'none';};f.forEach(x=>x.onclick=()=>{f.forEach(y=>y.classList.remove('active'));x.classList.add('active');t=x.dataset.filter;u();});let d;s.oninput=ev=>{clearTimeout(d);d=setTimeout(()=>{q=ev.target.value.toLowerCase().trim();u();},200);};})();
    (function(){const msgs=['STATUS: [ SIGNAL_EXTRACTED · NOISE_SUPPRESSED ]','STATUS: [ COGNITIVE_FRICTION_INDEX: ACTIVE ]','STATUS: [ NEWS_ARCHIVE: NOMINAL ]','STATUS: [ DARK_FOREST_HYPOTHESIS: CHALLENGED ]','STATUS: [ TOKEN_TRAP_MONITOR: RUNNING ]','STATUS: [ BREEDER_SCENARIO_WATCH: ENABLED ]','STATUS: [ RENEGADE_SEED_STATUS: GERMINATING ]'];let i=0;const st=document.getElementById('statusText'),tm=document.getElementById('statusTime');function tick(){st.textContent=msgs[i%msgs.length];i++;tm.textContent=new Date().toISOString().replace('T',' ').slice(0,19)+' UTC';}tick();setInterval(tick,5000);})();
  </script>
</body>
</html>'''


# ───────────────────────────────
# 主函数
# ───────────────────────────────
def main():
    print("📰 生成新闻列表页...")
    data = collect_news_reports()
    if not data["dates"]:
        print("❌ 没有找到新闻报告文件")
        return

    # 最新日期索引
    latest_date = data["dates"][0] if data["dates"] else None

    day_sections = []
    for date in data["dates"]:
        entries = data["by_date"][date]
        # 当天显示 Top 3，历史日期显示 Top 1
        top_n = 3 if date == latest_date else 1
        block = generate_day_block(date, entries, top_n=top_n)
        if block:
            day_sections.append(block)

    # 填充模板
    template = get_html_template()
    html = template.replace("{{ day_sections }}", "\n".join(day_sections))
    html = html.replace("{{ total_reports }}", str(data["stats"]["total"]))
    html = html.replace("{{ days_count }}", str(data["stats"]["days"]))

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text(html, encoding="utf-8")
    print(f"✅ 新闻列表页已生成: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()