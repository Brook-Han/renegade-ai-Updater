#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🏠 Renegade AI 雷达主页生成器（重构精准版）

✅ 修复重点：
  1. 明确指定子目录：只扫描 reports/news/ 和 reports/academic/
  2. 类型判断：通过父目录名判断（非文件名），100% 准确
  3. 链接路径：生成相对于 index.html 的正确相对路径
  4. 分类统计：新闻/论文数量精确计算

📁 期望的文件结构：
    reports/
    ├── news/
    │   └── news_report_2026-05-11_143022.html
    ├── academic/
    │   └── academic_report_2026-05-11_143500.html
    └── index.html  ← 本脚本生成于此（与子目录同级）

📋 用法：
    cd your-project-root
    python radar_index_generator.py

作者：Brooks Han
版本：v3.0 (2026-05-11) · 重构精准版
"""

# ──────────────────────────────────────────────────────────────
# 🔧 导入模块
# ──────────────────────────────────────────────────────────────

import re
from pathlib import Path
from html import escape

# ──────────────────────────────────────────────────────────────
# ⚙️ 配置常量（集中管理，方便修改）
# ──────────────────────────────────────────────────────────────

# 报告根目录（相对于脚本运行位置）
REPORTS_ROOT = Path("reports")

# 子目录配置：目录名 → 显示名称 → 类型标识
SUBDIR_CONFIG = {
    "news": {
        "label": "📰 新闻",
        "type": "news",
        "pattern": "news_report*.html",
        "badge_class": "news",
    },
    "academic": {
        "label": "📄 论文", 
        "type": "academic",
        "pattern": "academic_report*.html",
        "badge_class": "academic",
    },
}

# ──────────────────────────────────────────────────────────────
# 📖 函数1：从单个 HTML 提取卡片数据
# ──────────────────────────────────────────────────────────────

def extract_cards_from_html(html_path: Path, report_type: str) -> list[dict]:
    """
    解析报告 HTML，提取卡片关键信息
    
    参数:
        html_path: HTML 文件完整路径
        report_type: 'news' 或 'academic'（由调用方传入，确保准确）
    
    返回:
        list[dict]: 卡片数据列表
    """
    try:
        with open(html_path, encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"⚠️ 读取失败 {html_path.name}: {e}")
        return []
    
    cards = []
    
    # 🔍 匹配所有 <div class="card">...</div>
    card_blocks = re.findall(
        r'<div class="card">(.*?)</div>\s*(?=<div class="card">|</main>|</body>|$)', 
        content, 
        re.DOTALL
    )
    
    for block in card_blocks:
        card = {'type': report_type}  # ✅ 类型由参数传入，100% 准确
        
        # 📌 提取标题（清理内部标签）
        title_m = re.search(r'<div class="card-title">(.*?)</div>', block, re.DOTALL)
        if title_m:
            card['title'] = re.sub(r'<[^>]+>', '', title_m.group(1)).strip()
        
        # 📊 提取分数
        score_m = re.search(r'<div class="card-score">([\d.]+)<span>/10</span>', block)
        if score_m:
            card['score'] = score_m.group(1)
        
        # 🔗 提取原文链接（保持原样，通常是绝对 URL）
        link_m = re.search(r'<a href="([^"]+)" target="_blank"[^>]*>↗\s*(?:原文|PDF/原文)</a>', block)
        if link_m:
            card['link'] = link_m.group(1)
        
        # 📝 提取摘要
        summary_m = re.search(r'<div class="card-body">(.*?)</div>', block, re.DOTALL)
        if summary_m:
            card['summary'] = re.sub(r'<[^>]+>', '', summary_m.group(1)).strip()
        
        # ✍️ 检测草稿（仅学术报告有）
        card['has_draft'] = '<div class="card-draft">' in block
        
        # 📍 提取章节
        chapter_m = re.search(r'📍\s*([^<\s][^<]*?)(?:</span>|<|&nbsp;|$)', block)
        if chapter_m:
            card['chapter'] = chapter_m.group(1).strip()
        
        # ✅ 只保留有标题的有效卡片
        if card.get('title'):
            cards.append(card)
    
    return cards


# ──────────────────────────────────────────────────────────────
# 📁 函数2：收集所有报告文件（✅ 精准版：指定子目录）
# ──────────────────────────────────────────────────────────────

def collect_all_reports() -> dict:
    """
    扫描指定子目录，收集所有报告文件
    
    返回:
        {
            'dates': ['2026-05-11', ...],  # 倒序
            'by_date': {
                '2026-05-11': [
                    {
                        'file_name': 'news_report_2026-05-11_143022.html',
                        'subdir': 'news',
                        'relative_link': 'news/news_report_2026-05-11_143022.html',
                        'full_path': Path('reports/news/news_report_...'),
                        'mtime': 1234567890.0,
                        'type': 'news',
                        'cards': [...]  # 提取的卡片列表
                    },
                    ...
                ]
            },
            'stats': {'total': 10, 'news': 6, 'academic': 4, 'days': 3}
        }
    """
    from datetime import datetime
    
    all_entries = []
    
    # 🔍 遍历配置的每个子目录
    for subdir_name, config in SUBDIR_CONFIG.items():
        subdir_path = REPORTS_ROOT / subdir_name
        
        if not subdir_path.exists():
            print(f"ℹ️  目录不存在，跳过: {subdir_path}")
            continue
        
        print(f"🔍 扫描 {subdir_path} / {config['pattern']}")
        
        # 匹配文件
        for html_file in subdir_path.glob(config['pattern']):
            # 跳过 index.html 自身
            if html_file.name == 'index.html':
                continue
            
            # 解析文件名中的日期时间
            m = re.search(r'(\d{4}-\d{2}-\d{2})_(\d{6})', html_file.name)
            if not m:
                print(f"⚠️ 文件名格式不符，跳过: {html_file.name}")
                continue
            
            date_str = m.group(1)  # '2026-05-11'
            time_str = m.group(2)  # '143022'
            
            # ✅ 关键：生成相对于 reports/index.html 的链接
            # index.html 在 reports/，报告在 reports/news/，所以链接是 "news/xxx.html"
            relative_link = f"{subdir_name}/{html_file.name}"
            
            entry = {
                'file_name': html_file.name,
                'subdir': subdir_name,
                'relative_link': relative_link,  # ✅ 用于"查看完整报告"链接
                'full_path': html_file,
                'date': date_str,
                'time': time_str,
                'mtime': html_file.stat().st_mtime,
                'type': config['type'],  # ✅ 类型由目录决定，准确无误
                'label': config['label'],
                'cards': [],  # 稍后填充
            }
            all_entries.append(entry)
    
    # 📅 按日期分组
    by_date = {}
    for entry in all_entries:
        date = entry['date']
        if date not in by_date:
            by_date[date] = []
        by_date[date].append(entry)
    
    # 🔄 日期倒序 + 每组内按时间倒序（最新的报告在前）
    sorted_dates = sorted(by_date.keys(), reverse=True)
    for date in by_date:
        by_date[date].sort(key=lambda x: x['time'], reverse=True)
    
    # 📊 计算统计
    stats = {
        'total': len(all_entries),
        'news': sum(1 for e in all_entries if e['type'] == 'news'),
        'academic': sum(1 for e in all_entries if e['type'] == 'academic'),
        'days': len(sorted_dates),
    }
    
    return {
        'dates': sorted_dates,
        'by_date': by_date,
        'stats': stats,
    }


# ──────────────────────────────────────────────────────────────
# 🎨 函数3：生成每日区块 HTML
# ──────────────────────────────────────────────────────────────

def generate_day_html(date: str, entries: list[dict]) -> str:
    """
    为指定日期生成摘要区块
    
    逻辑：
      1. 提取每个报告的所有卡片
      2. 合并 + 按分数排序，取 Top 3
      3. 以"时间最新"的报告作为该日期的详情入口
    """
    # 📦 收集并提取所有卡片
    all_cards = []
    for entry in entries:
        # ✅ 传入准确的 report_type
        cards = extract_cards_from_html(entry['full_path'], entry['type'])
        for c in cards:
            c['_report_link'] = entry['relative_link']  # 标记来源报告链接
        all_cards.extend(cards)
    
    # 🏆 按分数排序（高→低）
    def score_key(c):
        try:
            return float(c.get('score', 0))
        except (ValueError, TypeError):
            return -1
    
    all_cards.sort(key=score_key, reverse=True)
    top3 = all_cards[:3]
    
    # 🎯 确定该日期的主报告（时间最新的）
    latest_entry = entries[0]  # 已按 time 倒序，第一个就是最新
    main_report_link = latest_entry['relative_link']  # ✅ 正确的相对路径
    formatted_time = f"{latest_entry['time'][:2]}:{latest_entry['time'][2:4]}:{latest_entry['time'][4:]}"
    
    # 🧱 构建 HTML
    html = f'<div class="day-group" data-date="{date}">\n'
    html += f'  <h2 class="day-header">{date}</h2>\n'
    
    # 元信息行
    news_cnt = sum(1 for c in all_cards if c['type'] == 'news')
    acad_cnt = sum(1 for c in all_cards if c['type'] == 'academic')
    type_info = f' · 📰{news_cnt} 📄{acad_cnt}' if news_cnt or acad_cnt else ''
    html += f'  <div class="day-meta">⏰ {formatted_time} · 📊 共 {len(all_cards)} 条{type_info}</div>\n'
    
    # 🃏 渲染 Top 3 卡片
    for card in top3:
        title = escape(card['title'])
        score = card.get('score', '—')
        summary = escape(card.get('summary', '')[:200])
        chapter = escape(card.get('chapter', ''))
        link = card.get('link', '#')
        
        # 🏷️ 类型徽章（使用配置的 badge_class）
        badge_class = SUBDIR_CONFIG.get(card['type'], {}).get('badge_class', '')
        type_label = SUBDIR_CONFIG.get(card['type'], {}).get('label', '')
        type_badge = f'<span class="type-badge {badge_class}">{type_label}</span>' if badge_class else ''
        
        # ✍️ 草稿徽章
        draft_badge = '<span class="draft-badge">✍️</span>' if card.get('has_draft') else ''
        
        # 🔗 链接处理
        link_html = f'<a href="{escape(link)}" target="_blank" rel="noopener">↗ 原文</a>' if link and link != '#' else ''
        
        # ✅ 关键修复：报告链接使用相对路径
        report_link = card.get('_report_link', main_report_link)
        
        html += f'''
  <article class="card" data-type="{card['type']}">
    <div class="card-header">
      <div class="card-title">
        <a href="{escape(link)}" target="_blank" rel="noopener">{title}</a>
        {draft_badge}{type_badge}
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
      <a href="{report_link}">查看 {date} 完整报告 →</a>
    </div>
  </article>\n'''
    
    html += '</div>\n'
    return html


# ──────────────────────────────────────────────────────────────
# 🎨 函数4：HTML 模板（精简版，保留核心交互）
# ──────────────────────────────────────────────────────────────

def get_html_template() -> str:
    return '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Renegade AI · Radar Archive</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Space+Mono:ital,wght@0,400;0,700;1,400&family=Crimson+Pro:ital,wght@0,300;0,400;0,600;1,300;1,400&family=Bebas+Neue&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css">
  <style>
    :root{--bg:#f8f9fc;--card:#fff;--border:#e0e2ec;--text:#2a2a40;--text-muted:#6a6a80;--accent:#e8503a;--accent-dim:rgba(232,80,58,.08);--accent2:#b88c2a;--accent3:#3a7fbf;--accent3-dim:rgba(74,143,207,.08);--white:#2a2a40;--mono:'Space Mono',monospace;--serif:'Crimson Pro',serif;--display:'Bebas Neue',sans-serif}
    :root.dark-theme{--bg:#08080e;--card:#13131f;--border:#1e1e30;--text:#cccce0;--text-muted:#6868a0;--accent-dim:rgba(232,80,58,.12);--accent3-dim:rgba(74,143,207,.1);--white:#f0f0f8}
    *{box-sizing:border-box;margin:0;padding:0}
    body{font-family:var(--serif);background:var(--bg);color:var(--text);line-height:1.8;transition:background .3s,color .3s}
    nav{position:fixed;top:0;width:100%;z-index:200;background:rgba(248,249,252,.92);backdrop-filter:blur(24px);border-bottom:1px solid var(--border);height:56px;display:flex;align-items:center;justify-content:space-between;padding:0 32px;font-family:var(--mono)}
    .dark-theme nav{background:rgba(8,8,14,.92)}
    .nav-brand{font-size:.75rem;font-weight:700;color:var(--accent);letter-spacing:3px;text-transform:uppercase;text-decoration:none}
    .theme-toggle{background:none;border:1px solid var(--border);color:var(--text-muted);width:36px;height:36px;cursor:pointer;display:flex;align-items:center;justify-content:center}
    .theme-toggle:hover{border-color:var(--accent);color:var(--accent);background:var(--accent-dim)}
    .main{max-width:860px;margin:0 auto;padding:100px 32px 60px}
    .page-eyebrow{font-family:var(--mono);font-size:.62rem;letter-spacing:4px;color:var(--accent);text-transform:uppercase;margin-bottom:8px;display:flex;align-items:center;gap:10px}
    .page-eyebrow::before{content:'';width:28px;height:1px;background:var(--accent)}
    h1{font-family:var(--display);font-size:3rem;letter-spacing:2px;color:var(--white);margin-bottom:6px;line-height:1}
    .subtitle{font-family:var(--mono);font-size:.65rem;color:var(--text-muted);letter-spacing:1.5px;margin-bottom:32px;display:flex;justify-content:space-between;flex-wrap:wrap;gap:8px}
    .stats-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(100px,1fr));gap:12px;margin-bottom:32px}
    .stat{background:var(--card);border:1px solid var(--border);padding:16px;text-align:center}
    .stat-val{font-family:var(--display);font-size:1.5rem;color:var(--accent)}
    .stat-lbl{font-family:var(--mono);font-size:.6rem;color:var(--text-muted)}
    .controls{display:flex;gap:12px;margin-bottom:24px;flex-wrap:wrap;align-items:center}
    .filter-btn{font-family:var(--mono);font-size:.65rem;padding:6px 14px;border:1px solid var(--border);background:var(--bg);color:var(--text-muted);cursor:pointer}
    .filter-btn.active,.filter-btn:hover{border-color:var(--accent);color:var(--accent);background:var(--accent-dim)}
    .search{flex:1;min-width:200px;position:relative}
    .search input{width:100%;padding:8px 12px 8px 32px;border:1px solid var(--border);background:var(--card);color:var(--text)}
    .search i{position:absolute;left:10px;top:50%;transform:translateY(-50%);color:var(--text-muted)}
    .day-group{margin-bottom:48px}
    .day-header{font-family:var(--display);font-size:1.8rem;color:var(--white);border-bottom:1px solid var(--border);padding-bottom:8px;margin-bottom:4px}
    .day-meta{font-family:var(--mono);font-size:.65rem;color:var(--text-muted);margin-bottom:16px}
    .card{background:var(--card);border:1px solid var(--border);padding:24px;margin-bottom:8px}
    .card:hover{border-color:var(--accent)}
    .card-header{display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:10px;gap:12px;flex-wrap:wrap}
    .card-title{font-family:var(--display);font-size:1.2rem;color:var(--white);flex:1;line-height:1.3}
    .card-title a{color:inherit;text-decoration:none;border-bottom:1px solid transparent}
    .card-title a:hover{border-bottom-color:var(--accent2)}
    .card-score{font-family:var(--display);font-size:1.8rem;color:var(--accent);white-space:nowrap;text-align:right}
    .card-score span{font-family:var(--mono);font-size:.5rem;color:var(--text-muted);display:block}
    .card-meta{font-family:var(--mono);font-size:.6rem;color:var(--text-muted);margin-bottom:12px;display:flex;gap:16px;flex-wrap:wrap}
    .card-meta a{color:var(--accent2);text-decoration:none}
    .card-body{font-size:.92rem;color:var(--text);line-height:1.8;margin-bottom:8px}
    .card-link{font-family:var(--mono);font-size:.65rem;margin-top:10px}
    .card-link a{color:var(--accent);text-decoration:none}
    .type-badge{display:inline-block;font-family:var(--mono);font-size:.55rem;padding:2px 6px;border-radius:2px;margin-left:6px}
    .type-badge.news{background:var(--accent3-dim);color:var(--accent3)}
    .type-badge.academic{background:var(--accent-dim);color:var(--accent)}
    .draft-badge{font-size:.9rem;margin-left:4px}
    .empty{text-align:center;padding:48px;color:var(--text-muted);font-family:var(--mono)}
    footer{margin-top:64px;padding-top:24px;border-top:1px solid var(--border);font-family:var(--mono);font-size:.6rem;color:var(--text-muted);display:flex;justify-content:space-between}
    @media(max-width:600px){.main{padding:100px 16px 40px}h1{font-size:2.2rem}.card-header{flex-direction:column}.card-score{text-align:left;margin-top:8px}.controls{flex-direction:column;align-items:stretch}.search{width:100%}}
    .card.hidden,.day-group.hidden{display:none}
  </style>
</head>
<body>
  <nav>
    <a href="https://brook-han.github.io/Renegade-AI/" class="nav-brand">RENEGADE AI v5.3</a>
    <div style="display:flex;gap:12px;align-items:center">
      <button class="theme-toggle" id="themeToggle"><i class="fa fa-sun-o" id="themeIcon"></i></button>
    </div>
  </nav>
  <main class="main">
    <div class="page-eyebrow">§ Radar Archive</div>
    <h1>DAILY DIGEST</h1>
    <div class="subtitle">
      <span>📰 News + 🎓 Academic · AI-Powered</span>
      <span id="statsLine">Loading...</span>
    </div>
    <div class="stats-grid">
      <div class="stat"><div class="stat-val" id="statTotal">—</div><div class="stat-lbl">Reports</div></div>
      <div class="stat"><div class="stat-val" id="statNews">—</div><div class="stat-lbl">📰 News</div></div>
      <div class="stat"><div class="stat-val" id="statAcademic">—</div><div class="stat-lbl">📄 Papers</div></div>
      <div class="stat"><div class="stat-val" id="statDays">—</div><div class="stat-lbl">Days</div></div>
    </div>
    <div class="controls">
      <button class="filter-btn active" data-filter="all">All</button>
      <button class="filter-btn" data-filter="news">📰 News</button>
      <button class="filter-btn" data-filter="academic">📄 Papers</button>
      <div class="search"><i class="fa fa-search"></i><input type="text" id="searchInput" placeholder="Search..."></div>
    </div>
    {{ day_sections }}
    <div class="empty" id="emptyState" style="display:none">
      <i class="fa fa-inbox" style="font-size:2rem;margin-bottom:12px;display:block"></i>
      <p>No results. Try adjusting filters or keywords.</p>
    </div>
    <footer>
      <span>Renegade AI v5.3 · Brooks Han</span>
      <a href="https://github.com/Brook-Han/renegade-ai-Updater" target="_blank">GitHub ↗</a>
    </footer>
  </main>
  <script>
    // Theme toggle
    (function(){const h=document.documentElement,b=document.getElementById('themeToggle'),i=document.getElementById('themeIcon'),k='renegade-theme',a=t=>{h.classList.toggle('dark-theme',t==='dark');i.className=t==='dark'?'fa fa-moon-o':'fa fa-sun-o';localStorage.setItem(k,t);};a(localStorage.getItem(k)||(matchMedia('(prefers-color-scheme:dark)').matches?'dark':'light'));b.onclick=()=>a(h.classList.contains('dark-theme')?'light':'dark');})();
    // Filter + Search
    (function(){const f=document.querySelectorAll('.filter-btn'),s=document.getElementById('searchInput'),c=document.querySelectorAll('.card'),g=document.querySelectorAll('.day-group'),e=document.getElementById('emptyState');let t='all',q='';const u=()=>{let v=0;c.forEach(x=>{const y=x.dataset.type,z=(x.querySelector('.card-title')?.textContent||'').toLowerCase(),w=(x.querySelector('.card-body')?.textContent||'').toLowerCase();const A=t==='all'||y===t,B=!q||z.includes(q)||w.includes(q);if(A&&B){x.classList.remove('hidden');v++;}else{x.classList.add('hidden');}});g.forEach(x=>{const y=x.querySelectorAll('.card:not(.hidden)');x.classList.toggle('hidden',y.length===0);});e.style.display=v===0?'block':'none';};f.forEach(x=>x.onclick=()=>{f.forEach(y=>y.classList.remove('active'));x.classList.add('active');t=x.dataset.filter;u();});let d;s.oninput=ev=>{clearTimeout(d);d=setTimeout(()=>{q=ev.target.value.toLowerCase().trim();u();},200);};})();
    // Stats
    (function(){const t={{ total_reports }},n={{ news_count }},a={{ academic_count }},d={{ days_count }},l='{{ latest_date }}';document.getElementById('statTotal').textContent=t;document.getElementById('statNews').textContent=n;document.getElementById('statAcademic').textContent=a;document.getElementById('statDays').textContent=d;document.getElementById('statsLine').textContent='📅 Latest: '+l;})();
  </script>
</body>
</html>'''


# ──────────────────────────────────────────────────────────────
# 🚀 主函数
# ──────────────────────────────────────────────────────────────

def main():
    print("🚀 Renegade AI Radar Index Generator v3.0")
    print(f"📁 Reports root: {REPORTS_ROOT.resolve()}")
    
    # 1️⃣ 收集报告
    print("\n🔍 Collecting reports...")
    data = collect_all_reports()
    
    if not data['dates']:
        print("❌ No reports found!")
        print(f"💡 Expected structure:\n  {REPORTS_ROOT}/news/news_report_*.html\n  {REPORTS_ROOT}/academic/academic_report_*.html")
        return
    
    print(f"✅ Found {data['stats']['total']} reports across {data['stats']['days']} days")
    print(f"   📰 News: {data['stats']['news']} | 📄 Academic: {data['stats']['academic']}")
    
    # 2️⃣ 生成每日区块
    print("\n🎨 Generating HTML sections...")
    day_sections = []
    for date in data['dates']:
        entries = data['by_date'][date]
        section = generate_day_html(date, entries)
        day_sections.append(section)
    
    # 3️⃣ 渲染完整页面
    print("📄 Rendering index.html...")
    template = get_html_template()
    
    # 安全替换变量
    final = template.replace('{{ day_sections }}', ''.join(day_sections))
    final = final.replace('{{ total_reports }}', str(data['stats']['total']))
    final = final.replace('{{ news_count }}', str(data['stats']['news']))
    final = final.replace('{{ academic_count }}', str(data['stats']['academic']))
    final = final.replace('{{ days_count }}', str(data['stats']['days']))
    final = final.replace('{{ latest_date }}', data['dates'][0] if data['dates'] else 'N/A')
    
    # 4️⃣ 写入文件
    output = REPORTS_ROOT / "index.html"
    output.write_text(final, encoding='utf-8')
    
    print(f"\n✅ Success! Generated: {output}")
    print(f"🌐 Preview: file://{output.resolve()}")
    print("\n✨ Done. Run `python radar_index_generator.py` anytime to refresh.")


# ──────────────────────────────────────────────────────────────
# 🔑 入口
# ──────────────────────────────────────────────────────────────

if __name__ == '__main__':
    main()