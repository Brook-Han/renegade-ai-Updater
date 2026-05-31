#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📰 News Radar MD → HTML 转换器（v5.3 视觉/无障碍完全对齐版）

功能：将 news_radar.py 生成的 Markdown 报告转换为漂亮的网页
风格：与 Renegade AI v5.3 优化版完全对齐（WCAG AA 合规）

📋 用法：
    # 方式1：转换指定文件
    python news_md_to_html.py docs/news/news_report_2026-05-11.md
    
    # 方式2：自动找最新报告（推荐）
    python news_md_to_html.py

🔧 输出：同目录下生成 .html 文件，可直接用浏览器打开

作者：Brooks Han
版本：v1.2 (2026-05-30)
"""

# ──────────────────────────────────────────────────────────────
# 🔧 导入必要的模块
# ──────────────────────────────────────────────────────────────

import re          # 正则表达式，用于解析 Markdown 文本
import sys         # 系统模块，处理命令行参数
from html import escape  # HTML 转义
from pathlib import Path  # 路径处理，比 os.path 更现代
from datetime import datetime  # 日期时间处理

# ──────────────────────────────────────────────────────────────
# 📖 函数1：解析 Markdown 报告
# ──────────────────────────────────────────────────────────────

def parse_news_report(md_path: str) -> dict:
    """
    解析 news_radar.py 生成的 Markdown 文件，提取关键数据
    """
    with open(md_path, encoding='utf-8') as f:
        text = f.read()
    
    # ── 1️⃣ 提取报告元数据 ──
    date_match = re.search(r'\*\*生成日期\*\*:\s*(\d{4}-\d{2}-\d{2})', text)
    date = date_match.group(1) if date_match else datetime.today().strftime('%Y-%m-%d')
    
    model_match = re.search(r'\*\*分析模型\*\*:\s*(.+?)(?:\n|$)', text)
    model = model_match.group(1).strip() if model_match else 'DeepSeek'
    
    total_match = re.search(r'\*\*分析条目\*\*:\s*(\d+)', text)
    total_count = total_match.group(1) if total_match else '0'
    
    high_match = re.search(r'高价值.*?\*\*(\d+)\*\*', text)
    med_match = re.search(r'中相关.*?\*\*(\d+)\*\*', text)
    high_n = high_match.group(1) if high_match else '0'
    med_n = med_match.group(1) if med_match else '0'
    
    # ── 2️⃣ 提取"高价值案例"区块 ──
    items = []
    high_section = re.search(
        r'## ⭐ 高价值案例.*?\n(.*?)(?=\n## |<details|---|\Z)', 
        text, 
        re.DOTALL
    )
    
    if high_section:
        content = high_section.group(1).strip()
        blocks = re.split(r'\n###\s+\d+\.\s*', '\n' + content)
        
        for block in blocks[1:]:
            block = block.strip()
            if not block:
                continue
            
            lines = block.split('\n')
            title = lines[0].strip() if lines else 'Untitled'
            
            fields = {}
            for line in lines[1:]:
                line = line.strip()
                for md_key, field_key in [
                    ('来源', 'source'), ('相关度', 'score'), ('案例价值', 'case_value'),
                    ('紧迫度', 'urgency'), ('更新类型', 'update_type'), ('目标章节', 'chapter'),
                    ('事件摘要', 'summary'), ('理论关联', 'implications'),
                    ('建议操作', 'action'), ('链接', 'link')
                ]:
                    pattern = rf'-\s*\*\*{md_key}\*\*:\s*(.*)'
                    match = re.search(pattern, line)
                    if match:
                        fields[field_key] = match.group(1).strip()
                        break
            
            if 'link' in fields and fields['link'].startswith('['):
                url_match = re.search(r'\]\(([^)]+)\)', fields['link'])
                if url_match:
                    fields['link'] = url_match.group(1)
            
            if 'score' in fields:
                score_match = re.search(r'(\d+(?:\.\d+)?)/10', fields['score'])
                if score_match:
                    fields['score'] = score_match.group(1)
            
            items.append({
                'title': title,
                'source': fields.get('source', ''),
                'score': fields.get('score', '—'),
                'case_value': fields.get('case_value', '').upper(),
                'urgency': fields.get('urgency', ''),
                'update_type': fields.get('update_type', ''),
                'chapter': fields.get('chapter', ''),
                'summary': fields.get('summary', ''),
                'implications': fields.get('implications', ''),
                'action': fields.get('action', ''),
                'link': fields.get('link', ''),
            })
    
    # ── 3️⃣ 提取"紧急关注清单" ──
    urgent_items = []
    urgent_section = re.search(
        r'## 🚨 紧急关注清单.*?\n(.*?)(?=\n## |\Z)',
        text,
        re.DOTALL
    )
    if urgent_section:
        urgent_lines = urgent_section.group(1).strip().split('\n')
        current = None
        for line in urgent_lines:
            stripped = line.strip()
            if stripped.startswith('- [ ]'):
                chapter_m = re.search(r'\*\*([^*]+)\*\*', stripped)
                update_m = re.search(r'\|\s*(\S+)', stripped)
                current = {
                    'chapter': chapter_m.group(1) if chapter_m else '',
                    'title': '',
                    'update_type': update_m.group(1) if update_m else '',
                }
                urgent_items.append(current)
            elif stripped.startswith('- 📌') and current:
                title_m = re.search(r'📌\s*(.+?)(?:\.{3}|$)', stripped)
                current['title'] = title_m.group(1).strip() if title_m else ''
    
    return {
        'date': date, 'model': model, 'total': total_count,
        'high_n': high_n, 'med_n': med_n, 'items': items, 'urgent': urgent_items,
    }


# ──────────────────────────────────────────────────────────────
# 🎨 函数2：CSS 样式模板（v5.3 优化版 · WCAG AA 对齐）
# ──────────────────────────────────────────────────────────────

CSS_TEMPLATE = """
    <style>
      /* ========== DESIGN TOKENS (v5.3 Optimized) ========== */
      :root {
        --bg: #0a0a12; --bg2: #0f0f1a; --surface: #141422; --card: #181828;
        --border: #25253a; --border-bright: #363655;
        --text: #e2e2f0; --text-muted: #9595c0; --text-faint: #4a4a6a;
        --accent: #ff5c45; --accent-dim: rgba(255,92,69,0.12);
        --accent2: #d4af5c; --accent3: #5ba3e6; --accent3-dim: rgba(91,163,230,0.10);
        --white: #f4f4fc;
        --mono: 'Space Mono', 'Courier New', monospace;
        --serif: 'Crimson Pro', Georgia, serif;
        --display: 'Bebas Neue', 'Arial Narrow', sans-serif;
      }
      :root.light {
        --bg: #f5f6fa; --bg2: #fff; --surface: #eceef5; --card: #fff;
        --border: #d8dbe6; --border-bright: #c0c4d6;
        --text: #222233; --text-muted: #5c5c75; --text-faint: #9a9ab0;
        --accent: #e8503a; --accent-dim: rgba(232,80,58,0.08);
        --accent2: #b88c2a; --accent3: #3a7fbf; --accent3-dim: rgba(74,143,207,0.08);
        --white: #222233;
      }

      /* ========== RESET & TYPOGRAPHY ========== */
      * { box-sizing: border-box; margin: 0; padding: 0; }
      html { scroll-behavior: smooth; }
      body {
        font-family: var(--serif); background: var(--bg); color: var(--text);
        line-height: 1.8; -webkit-font-smoothing: antialiased; -moz-osx-font-smoothing: grayscale;
        transition: background-color 0.3s ease, color 0.3s ease;
        text-rendering: optimizeLegibility; font-feature-settings: "kern" 1, "liga" 1;
      }
      ::selection { background: var(--accent); color: #fff; text-shadow: 0 1px 2px rgba(0,0,0,.2); }
      
      /* ========== ACCESSIBILITY ========== */
      :focus-visible { outline: 2px solid var(--accent); outline-offset: 3px; border-radius: 2px; z-index: 10; }
      :focus:not(:focus-visible) { outline: none; }
      @media (prefers-reduced-motion: reduce) {
        *, *::before, *::after { animation-duration: 0.01ms !important; transition-duration: 0.01ms !important; }
      }

      /* ========== NAV ========== */
      nav {
        position: fixed; top: 0; width: 100%; z-index: 200;
        background: rgba(10,10,18,.92); backdrop-filter: blur(24px);
        border-bottom: 1px solid var(--border); height: 56px;
        display: flex; align-items: center; justify-content: space-between;
        padding: 0 32px; font-family: var(--mono);
      }
      .light nav { background: rgba(245,246,250,.92); }
      .nav-brand {
        font-size: 0.75rem; font-weight: 700; color: var(--accent); letter-spacing: 3px;
        text-transform: uppercase; text-decoration: none;
      }
      .nav-right { display: flex; gap: 8px; align-items: center; }
      .nav-pill {
        background: none; border: 1px solid var(--border); color: var(--text-muted);
        font-family: var(--mono); font-size: .72rem; font-weight: 500; letter-spacing: 2px;
        padding: 5px 14px; cursor: pointer; text-decoration: none; display: inline-flex; align-items: center;
      }
      .nav-pill:hover, .nav-pill:focus-visible { border-color: var(--accent); color: var(--accent); background: var(--accent-dim); }
      .theme-btn {
        background: none; border: 1px solid var(--border); color: var(--text-muted);
        width: 36px; height: 36px; cursor: pointer; display: flex; align-items: center; justify-content: center; font-size: .9rem;
      }
      .theme-btn:hover, .theme-btn:focus-visible { border-color: var(--accent); color: var(--accent); background: var(--accent-dim); }

      /* ========== MAIN ========== */
      .main { max-width: 960px; margin: 0 auto; padding: 80px 32px 60px; }
      .back-link {
        font-family: var(--mono); font-size: 0.72rem; font-weight: 500; letter-spacing: 2px; 
        color: var(--text-muted); text-decoration: none; text-transform: uppercase;
        border: 1px solid var(--border); padding: 6px 14px; display: inline-block; margin-bottom: 16px;
      }
      .back-link:hover { border-color: var(--accent); color: var(--accent); }
      .page-eyebrow {
        font-family: var(--mono); font-size: 0.72rem; font-weight: 500; letter-spacing: 4px; 
        color: var(--accent); text-transform: uppercase; margin-bottom: 12px;
        display: flex; align-items: center; gap: 10px;
      }
      .page-eyebrow::before { content: ''; width: 28px; height: 1px; background: var(--accent); }
      .page-title {
        font-family: var(--display); font-size: clamp(2.5rem, 5vw, 3.5rem);
        letter-spacing: 2px; color: var(--white); margin-bottom: 8px; line-height: 1;
      }
      .page-sub {
        font-family: var(--mono); font-size: 0.72rem; font-weight: 500;
        color: var(--text-muted); letter-spacing: 1.5px; margin-bottom: 24px;
      }
      .stats-row {
        display: flex; gap: 24px; margin-bottom: 24px;
        font-family: var(--mono); font-size: 0.72rem; font-weight: 500;
        color: var(--text-muted); flex-wrap: wrap;
      }
      .stats-row span { color: var(--accent); font-weight: 700; }
      
      /* ========== URGENT BOX ========== */
      .urgent-box {
        background: var(--accent-dim); border: 1px solid var(--accent);
        padding: 20px 24px; margin-bottom: 32px; border-left: 4px solid var(--accent);
      }
      .urgent-title {
        font-family: var(--mono); font-size: 0.72rem; font-weight: 700;
        letter-spacing: 2px; color: var(--accent); text-transform: uppercase; margin-bottom: 12px;
      }
      .urgent-item {
        font-family: var(--mono); font-size: 0.72rem; font-weight: 500; margin-bottom: 8px;
        padding-left: 16px; border-left: 2px solid var(--border); color: var(--text-muted);
      }
      .urgent-item strong { color: var(--white); }
      .urgent-type-tag {
        font-family: var(--mono); font-size: 0.65rem; font-weight: 700; letter-spacing: 1px;
        color: var(--accent); background: var(--bg); padding: 2px 6px; margin-left: 6px; text-transform: uppercase;
      }
      
      /* ========== CARDS ========== */
      .card {
        background: var(--card); border: 1px solid var(--border); padding: 28px; margin-bottom: 16px;
        transition: border-color .2s, background 0.2s, box-shadow .2s;
        box-shadow: 0 4px 24px rgba(0,0,0,.15), inset 0 1px 0 rgba(255,255,255,.02);
      }
      .card:hover { border-color: var(--accent); }
      .card-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 14px; gap: 16px; }
      .card-title {
        font-family: var(--display); font-size: 1.4rem; letter-spacing: 0.5px; 
        color: var(--white); line-height: 1.3; flex: 1;
      }
      .card-score {
        font-family: var(--display); font-size: 2.2rem; color: var(--accent); 
        line-height: 1; white-space: nowrap; text-align: right;
      }
      .card-score span {
        font-family: var(--mono); font-size: 0.72rem; font-weight: 500;
        color: var(--text-faint); display: block; letter-spacing: 1px; margin-top: 4px;
      }
      .card-badge {
        display: inline-block; padding: 3px 8px; font-family: var(--mono); 
        font-size: 0.65rem; font-weight: 700; letter-spacing: 1px; text-transform: uppercase;
        background: var(--accent3-dim); color: var(--accent3); border: 1px solid var(--accent3); margin-left: 8px;
      }
      .card-badge.high { background: var(--accent-dim); color: var(--accent); border-color: var(--accent); }
      .card-meta {
        font-family: var(--mono); font-size: 0.72rem; font-weight: 500;
        color: var(--text-faint); letter-spacing: 0.5px; margin-bottom: 16px; 
        display: flex; gap: 16px; flex-wrap: wrap; align-items: center;
      }
      .card-meta a { color: var(--accent2); text-decoration: none; }
      .card-meta a:hover { text-decoration: underline; }
      .card-body { font-size: 0.95rem; color: var(--text-muted); line-height: 1.8; margin-bottom: 16px; }
      .card-implications {
        font-family: var(--mono); font-size: 0.75rem; font-weight: 500;
        color: var(--accent2); padding: 12px 16px; background: rgba(212,175,92,0.05);
        border-left: 3px solid var(--accent2); letter-spacing: 0.3px; margin-bottom: 16px; line-height: 1.7;
      }
      .card-footer {
        display: flex; gap: 12px; flex-wrap: wrap; font-family: var(--mono); 
        font-size: 0.72rem; font-weight: 500; color: var(--text-faint); letter-spacing: 0.5px;
        padding-top: 12px; border-top: 1px dashed var(--border);
      }
      .card-footer .tag { padding: 3px 8px; background: var(--surface); border-radius: 2px; color: var(--text-muted); }
      
      /* ========== COLLAPSED LIST ========== */
      details { margin: 32px 0; border: 1px solid var(--border); background: var(--card); }
      summary {
        padding: 14px 20px; cursor: pointer; font-family: var(--mono); 
        font-size: 0.72rem; font-weight: 700; letter-spacing: 1px; color: var(--text-muted);
        background: var(--surface); user-select: none; display: flex; align-items: center; gap: 8px;
      }
      summary:hover { color: var(--accent); }
      details[open] summary { border-bottom: 1px solid var(--border); }
      .collapsed-list { padding: 16px 20px; }
      .collapsed-list li { margin-bottom: 10px; font-size: 0.95rem; color: var(--text-muted); }
      .collapsed-list a { color: var(--text); text-decoration: none; }
      .collapsed-list a:hover { color: var(--accent); text-decoration: underline; }
      
      /* ========== FOOTER ========== */
      footer {
        margin-top: 48px; padding-top: 24px; border-top: 1px solid var(--border);
        font-family: var(--mono); font-size: 0.72rem; font-weight: 500;
        color: var(--text-muted); letter-spacing: 1px; display: flex; justify-content: space-between;
      }
      footer a { color: var(--text-muted); text-decoration: none; }
      footer a:hover { color: var(--accent); }
      
      /* ========== STATUS BAR ========== */
      .status-bar {
        position: fixed; bottom: 0; width: 100%; z-index: 200;
        background: var(--bg); border-top: 1px solid var(--border);
        padding: 10px 32px; font-family: var(--mono); font-size: 0.72rem; font-weight: 500;
        color: var(--text-faint); letter-spacing: 2px;
        display: flex; justify-content: space-between; align-items: center;
      }
      .status-dot {
        display: inline-block; width: 6px; height: 6px; background: var(--accent);
        border-radius: 50%; margin-right: 8px; animation: pulse 2s infinite;
      }
      @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: .2; } }

      /* ========== MOBILE & TOUCH TARGETS ========== */
      @media (max-width: 768px) {
        .nav-pill, .theme-btn, .back-link { min-height: 44px; min-width: 44px; display: inline-flex; align-items: center; justify-content: center; }
      }
      @media (max-width: 600px) {
        .main { padding: 70px 16px 60px; }
        .page-title { font-size: 2.2rem; }
        .card-header { flex-direction: column; }
        .card-score { text-align: left; }
        .stats-row { flex-direction: row; gap: 16px; overflow-x: auto; padding-bottom: 4px; scrollbar-width: none; }
      }
    </style>"""


# ──────────────────────────────────────────────────────────────
# 🏗️ 函数3：生成 HTML 页面
# ──────────────────────────────────────────────────────────────

def generate_news_html(data: dict, output_path: str):
    """根据解析的数据生成完整的 HTML 页面"""
    
    # ── 1️⃣ 生成紧急清单 HTML ──
    urgent_html = ''
    if data['urgent']:
        parts = []
        for u in data['urgent']:
            chapter = escape(u.get('chapter', ''))
            title = escape(u.get('title', ''))
            update_type = escape(u.get('update_type', ''))
            type_tag = f' <span class="urgent-type-tag">{update_type}</span>' if update_type else ''
            title_part = f' — {title}' if title else ''
            parts.append(f'<div class="urgent-item">• <strong>{chapter}</strong>{title_part}{type_tag}</div>')
        urgent_items = ''.join(parts)
        urgent_html = f'''
    <div class="urgent-box">
      <div class="urgent-title">🚨 紧急关注</div>
      {urgent_items}
    </div>'''
    
    # ── 2️⃣ 生成高价值案例卡片 ──
    items_html = ''
    for it in data['items']:
        try:
            score_num = float(it['score'])
            score_display = f'{score_num:.1f}'
        except (ValueError, TypeError):
            score_display = it['score'] if it['score'] else '—'
        
        case_badge = ''
        case_val = it.get('case_value', '')
        if case_val and case_val != 'N/A':
            badge_class = 'high' if case_val.lower() == 'high' else ''
            case_badge = f'<span class="card-badge {badge_class}">{case_val}</span>'
        
        link_html = ''
        link_val = it.get('link', '')
        if link_val and link_val not in ('N/A', '#', ''):
            link_html = f'<a href="{link_val}" target="_blank" rel="noopener">↗ 原文</a>'
        
        chapter_html = ''
        chapter_val = it.get('chapter', '')
        if chapter_val and chapter_val != 'N/A':
            chapter_html = f'📍 {chapter_val}'
        
        implications_html = ''
        imp_val = it.get('implications', '')
        if imp_val and imp_val != 'N/A':
            implications_html = f'\n      <div class="card-implications">{imp_val}</div>'
        
        tags = []
        urgency = it.get('urgency', '')
        update_type = it.get('update_type', '')
        action = it.get('action', '')
        
        if urgency and urgency not in ('N/A', '—', ''): tags.append(f'<span class="tag">⏱ {urgency}</span>')
        if update_type and update_type not in ('N/A', '—', ''): tags.append(f'<span class="tag">🔄 {update_type}</span>')
        if action and action not in ('N/A', '—', ''): tags.append(f'<span class="tag">✅ {action}</span>')
        tags_html = ''.join(tags) if tags else ''
        
        items_html += f'''
    <article class="card">
      <div class="card-header">
        <h2 class="card-title">{it["title"]}{case_badge}</h2>
        <div class="card-score">{score_display}<span>/10</span></div>
      </div>
      <div class="card-meta">
        {f'<span>{it["source"]}</span>' if it.get('source') and it['source'] != 'N/A' else ''}
        {f'<span>·</span>' if it.get('source') and link_html else ''}
        {link_html}
        {f'<span>·</span>' if chapter_html and (it.get('source') or link_html) else ''}
        {chapter_html}
      </div>
      <div class="card-body">{it["summary"]}</div>{implications_html}
      {f'<div class="card-footer">{tags_html}</div>' if tags_html else ''}
    </article>'''
    
    # ── 3️⃣ 拼接完整 HTML 文档 ──
    # 注意：JS 代码中的花括号必须使用 {{ 和 }} 进行转义，因为它们位于 f-string 内部
    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>News Radar · {data['date']} | Renegade AI</title>
  <meta name="description" content="AI 资讯监控报告 · {data['high_n']} 高价值案例">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Space+Mono:ital,wght@0,400;0,500;0,700;1,400&family=Crimson+Pro:ital,wght@0,300;0,400;0,600;1,300;1,400&family=Bebas+Neue&display=swap" rel="stylesheet">
  {CSS_TEMPLATE}
</head>
<body>
  <nav>
    <a href="https://brook-han.github.io/Renegade-AI/" class="nav-brand">RENEGADE AI v5.3</a>
    <div class="nav-right">
      <a href="../index.html" class="nav-pill">HOME</a>
      <a href="index.html" class="nav-pill">NEWS</a>
      <a href="../academic/" class="nav-pill">PAPERS</a>
      <button class="theme-btn" id="themeBtn" aria-label="Toggle theme">◐</button>
    </div>
  </nav>

  <main class="main">
    <a href="index.html" class="back-link">← BACK TO INDEX</a>
    <div class="page-eyebrow">§ News Radar</div>
    <h1 class="page-title">DAILY INTELLIGENCE</h1>
    <p class="page-sub">{data['date']} · Model: {data['model']}</p>
    
    <div class="stats-row">
      <div>📊 总条目: <span>{data['total']}</span></div>
      <div>🔴 高价值: <span>{data['high_n']}</span></div>
      <div>🟡 中相关: <span>{data['med_n']}</span></div>
    </div>
    
    {urgent_html}
    {items_html}
  </main>

  <footer style="max-width:900px;margin:0 auto;padding:24px 32px 60px;border-top:1px solid var(--border);font-family:var(--mono);font-size:0.6rem;color:var(--text-muted);letter-spacing:1px;display:flex;justify-content:space-between;flex-wrap:wrap;gap:8px;">
    <span>Renegade AI v5.3 · Brooks Han</span>
    <a href="https://brook-han.github.io/Renegade-AI/" target="_blank" rel="noopener" style="color:var(--text-muted);text-decoration:none;">GitHub ↗</a>
  </footer>

  <div class="status-bar">
    <span><span class="status-dot"></span><span id="statusText">STATUS: [ RADAR_ACTIVE ]</span></span>
    <span id="statusTime"></span>
  </div>

  <script>
(function(){{
  const h=document.documentElement,b=document.getElementById('themeBtn');
  const apply=t=>{{h.classList.toggle('light',t==='light');localStorage.setItem('renegade-theme',t)}};
  apply(localStorage.getItem('renegade-theme')||(matchMedia('(prefers-color-scheme: dark)').matches?'dark':'light'));
  b.onclick=()=>apply(h.classList.contains('light')?'dark':'light');
}})();
(function(){{
  const msgs=[
    'STATUS: [ SIGNAL_EXTRACTED · NOISE_SUPPRESSED ]',
    'STATUS: [ COGNITIVE_FRICTION_INDEX: ACTIVE ]',
    'STATUS: [ NEWS_PIPELINE: NOMINAL ]',
    'STATUS: [ DARK_FOREST_HYPOTHESIS: CHALLENGED ]',
    'STATUS: [ TOKEN_TRAP_MONITOR: RUNNING ]',
    'STATUS: [ BREEDER_SCENARIO_WATCH: ENABLED ]',
    'STATUS: [ RENEGADE_SEED_STATUS: GERMINATING ]',
  ];
  let i=0;
  const st=document.getElementById('statusText'),tm=document.getElementById('statusTime');
  function tick(){{
    st.textContent=msgs[i%msgs.length];i++;
    tm.textContent=new Date().toISOString().replace('T',' ').slice(0,19)+' UTC';
  }}
  tick();setInterval(tick,5000);
}})();
  </script>
</body>
</html>'''
    
    Path(output_path).write_text(html, encoding='utf-8')
    print(f'✅ HTML 已生成: {output_path}')


# ──────────────────────────────────────────────────────────────
# 🚀 主入口
# ──────────────────────────────────────────────────────────────

if __name__ == '__main__':
    if len(sys.argv) > 1:
        md_file = sys.argv[1]
        print(f'📄 使用指定文件: {md_file}')
    else:
        reports_dir = Path('docs/news')
        if not reports_dir.exists():
            reports_dir = Path('output/news')
        
        reports = sorted(reports_dir.glob('news_report_*.md'))
        if not reports:
            print('❌ 未找到 news_report_*.md 文件')
            print('💡 用法: python news_md_to_html.py path/to/report.md')
            sys.exit(1)
        
        md_file = str(reports[-1])
        print(f'🔍 自动选择最新报告: {md_file}')
    
    print(f'📖 解析中...')
    data = parse_news_report(md_file)
    
    if not data['items']:
        print('⚠️ 警告: 未解析到高价值案例')
        print(f'   统计: 总计 {data["total"]} 条 | 高 {data["high_n"]} | 中 {data["med_n"]}')
        print('💡 请检查 MD 文件是否由 news_radar.py 生成，且包含 "## ⭐ 高价值案例" 区块')
    
    out_file = str(Path(md_file).with_suffix('.html'))
    generate_news_html(data, out_file)
    
    print('🎉 转换完成！用浏览器打开即可预览：')
    print(f'   file://{Path(out_file).resolve()}')