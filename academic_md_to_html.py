#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎓 Academic Radar MD → HTML 转换器（头部页脚完全对齐 Renegade AI 主页）
======================================================================
📌 功能：把学术雷达生成的 Markdown 报告变成漂亮的网页
✨ 特色：和主页一模一样的导航栏、页脚、颜色、字体和主题切换
🎯 目标用户：小白也能看懂（每一行关键代码都有中文注释）

用法（二选一）：
  1. 自动转换最新报告：
     python academic_md_to_html.py

  2. 手动指定文件：
     python academic_md_to_html.py docs/academic/academic_report_2026-05-11_143022.md

输出：同目录下生成 .html 文件，双击就能在浏览器里看
"""

import re
import sys
from pathlib import Path
from datetime import datetime


# ═══════════════════════════════════════════════════════════════
# 🔍 第一部分：解析 Markdown 报告
# ═══════════════════════════════════════════════════════════════
def parse_academic_report(md_path: str) -> dict:
    """
    从 academic_radar.py 生成的 Markdown 里提取所有论文信息。
    返回一个大字典，包含：
      - date: 报告日期
      - model / draft_model: 使用的AI模型
      - total / high_n / med_n: 总条目数 / 高相关数 / 中相关数
      - papers: 论文列表，每篇又是一个字典（标题、评分、链接等）
      - urgent: 立即更新清单
    """
    with open(md_path, encoding='utf-8') as f:
        text = f.read()

    # ── 1. 提取报告元信息 ──
    date_match = re.search(r'\*\*生成日期\*\*:\s*(\d{4}-\d{2}-\d{2})', text)
    date = date_match.group(1) if date_match else datetime.today().strftime('%Y-%m-%d')

    model_match = re.search(r'\*\*分析模型\*\*:\s*(.+?)(?:\n|$)', text)
    model = model_match.group(1).strip() if model_match else 'DeepSeek'

    draft_model_match = re.search(r'\*\*草稿模型\*\*:\s*(.+?)(?:\n|$)', text)
    draft_model = draft_model_match.group(1).strip() if draft_model_match else 'DeepSeek'

    total_match = re.search(r'\*\*分析条目数\*\*:\s*(\d+)', text)
    total_count = total_match.group(1) if total_match else '0'

    high_match = re.search(r'高相关.*?\*\*(\d+)\*\*', text)
    med_match = re.search(r'中相关.*?\*\*(\d+)\*\*', text)
    high_n = high_match.group(1) if high_match else '0'
    med_n = med_match.group(1) if med_match else '0'

    # ── 2. 提取“高相关论文”区块 ──
    papers = []
    high_section = re.search(
        r'## ⭐ 高相关论文.*?\n(.*?)(?=\n## |\Z)',
        text,
        re.DOTALL
    )
    if high_section:
        content = high_section.group(1).strip()
        # 用 "### 数字. " 分割每篇论文
        blocks = re.split(r'\n###\s+\d+\.\s*', '\n' + content)
        for block in blocks[1:]:          # 第一个是空的，跳过
            block = block.strip()
            if not block:
                continue
            lines = block.split('\n')
            title = lines[0].strip() if lines else 'Untitled'

            # 解析所有 "- **字段名**: 值" 格式的行
            fields = {}
            for line in lines[1:]:
                m = re.match(r'-\s*\*\*(.*?)\*\*:\s*(.*)', line)
                if m:
                    key = m.group(1).strip()
                    val = m.group(2).strip()
                    fields[key] = val

            # 处理链接（可能是 Markdown 格式 [text](url)）
            link_raw = fields.get('链接', '')
            link_url = link_raw
            if link_raw.startswith('[') and '](' in link_raw:
                url_match = re.search(r'\]\(([^)]+)\)', link_raw)
                if url_match:
                    link_url = url_match.group(1)

            # 提取书稿草稿（以 > 开头的引用块）
            draft_text = ''
            draft_match = re.search(r'✍️.*?草稿.*?\n>\s*(.+?)(?=\n\n|\n###|\Z)', block, re.DOTALL)
            if draft_match:
                draft_text = draft_match.group(1).strip()

            # 提取模型评分表格（如果有）
            model_scores_html = ''
            if '🧠 模型评分:' in block:
                score_lines = re.findall(r'\|\s*(.*?)\s*\|\s*(.*?)\s*\|', block)
                if score_lines:
                    scores_html = ''.join(
                        f'<span class="model-tag">{name.strip()}: {score.strip()}/10</span>'
                        for name, score in score_lines if '模型' not in name
                    )
                    model_scores_html = f'<div class="card-model-scores">🧠 {scores_html}</div>'

            papers.append({
                'title': title,
                'source': fields.get('来源', ''),
                'authors': fields.get('作者', ''),
                'published': fields.get('发表', ''),
                'score': fields.get('最终评分', '—').replace('/10', ''),
                'urgency': fields.get('紧迫度', ''),
                'update_type': fields.get('更新类型', ''),
                'chapter': fields.get('目标章节', ''),
                'link': link_url,
                'summary': fields.get('核心发现', ''),
                'implications': fields.get('与本书关联', ''),
                'action': fields.get('建议更新', ''),
                'draft': draft_text,
                'model_scores': model_scores_html,
            })

    # ── 3. 提取“立即更新清单” ──
    urgent_items = []
    urgent_section = re.search(
        r'## 🚨 立即更新清单.*?\n(.*?)(?=\n## |\Z)',
        text,
        re.DOTALL
    )
    if urgent_section:
        for line in urgent_section.group(1).strip().split('\n'):
            if line.strip().startswith('- [ ]'):
                chap_match = re.search(r'\*\*([^*]+)\*\*', line)
                title_match = re.search(r'—\s*(.+?)\.\.\.\s*\(', line)
                urgent_items.append({
                    'chapter': chap_match.group(1) if chap_match else '待定',
                    'title': title_match.group(1) if title_match else line.strip()[:60]
                })

    return {
        'date': date,
        'model': model,
        'draft_model': draft_model,
        'total': total_count,
        'high_n': high_n,
        'med_n': med_n,
        'papers': papers,
        'urgent': urgent_items,
    }


# ═══════════════════════════════════════════════════════════════
# 🎨 第二部分：CSS 样式（和主页一模一样的视觉）
# ═══════════════════════════════════════════════════════════════
CSS_TEMPLATE = """
    <style>
      /* ══════════════ 全局颜色变量（Design Tokens） ══════════════
         这些变量控制整个页面的颜色，和主页共用同一套。
         暗色主题是默认，当 <html> 加上 class="light" 时切换到亮色。
      */
      :root {
        --bg:           #08080e;      /* 页面背景 */
        --bg2:          #0d0d18;      /* 次级背景 */
        --surface:      #111120;      /* 卡片悬浮时的背景 */
        --card:         #13131f;      /* 卡片默认背景 */
        --border:       #1e1e30;      /* 边框线 */
        --border-bright:#2e2e50;      /* 亮一点的边框（悬浮时用） */
        --text:         #cccce0;      /* 正文文字 */
        --text-muted:   #6868a0;      /* 次要文字 */
        --text-faint:   #3a3a5a;      /* 更淡的文字 */
        --accent:       #e8503a;      /* 强调色（橙红） */
        --accent-dim:   rgba(232,80,58,0.12);
        --accent2:      #c9a040;      /* 第二种强调色（金） */
        --accent3:      #4a8fcf;      /* 第三种强调色（蓝） */
        --accent3-dim:  rgba(74,143,207,0.10);
        --white:        #f0f0f8;      /* 最亮的文字（标题） */
        --mono:         'Space Mono', 'Courier New', monospace;
        --serif:        'Crimson Pro', Georgia, serif;
        --display:      'Bebas Neue', 'Arial Narrow', sans-serif;
        --ease:         cubic-bezier(0.4,0,0.2,1);  /* 平滑动画曲线 */
      }
      :root.light {
        --bg:           #f8f9fc;
        --bg2:          #ffffff;
        --surface:      #f0f2f8;
        --card:         #ffffff;
        --border:       #e0e2ec;
        --border-bright:#c0c2d0;
        --text:         #2a2a40;
        --text-muted:   #6a6a80;
        --text-faint:   #a0a0b8;
        --accent-dim:   rgba(232,80,58,0.08);
        --accent3-dim:  rgba(74,143,207,0.08);
        --white:        #2a2a40;
      }

      * { box-sizing: border-box; margin: 0; padding: 0; }
      html { scroll-behavior: smooth; }
      body {
        font-family: var(--serif);
        background: var(--bg);
        color: var(--text);
        line-height: 1.8;
        -webkit-font-smoothing: antialiased;  /* 让字体更清晰 */
        transition: background-color 0.3s, color 0.3s;
      }
      /* 选中文字的颜色 */
      ::selection { background: var(--accent); color: #000; }

      /* ══════════════ 固定导航栏（和主页一模一样） ══════════════ */
      nav {
        position: fixed; top: 0; width: 100%; z-index: 200;
        /* 毛玻璃效果：背景半透明 + 模糊 */
        background: rgba(8,8,14,0.92); backdrop-filter: blur(24px);
        border-bottom: 1px solid var(--border);
        height: 56px;
        display: flex; align-items: center; justify-content: space-between;
        padding: 0 32px;
        font-family: var(--mono);
        transition: background 0.3s, border-color 0.3s;
      }
      .light nav { background: rgba(248,249,252,0.92); }
      /* 左侧品牌文字 */
      .nav-brand {
        font-size: 0.75rem; font-weight: 700;
        color: var(--accent); letter-spacing: 3px;
        text-transform: uppercase; text-decoration: none;
      }
      .nav-brand:hover { color: var(--accent2); }
      /* 右侧按钮组 */
      .nav-right { display: flex; gap: 8px; align-items: center; }
      /* 返回 Radar 主页的按钮（也用在主页的导航中，这里样式完全一致） */
      .nav-pill {
        background: none; border: 1px solid var(--border);
        color: var(--text-muted); font-family: var(--mono);
        font-size: 0.62rem; letter-spacing: 2px; padding: 5px 14px;
        cursor: pointer; text-decoration: none; text-transform: uppercase;
        transition: all 0.2s;
      }
      .nav-pill:hover {
        border-color: var(--accent); color: var(--accent);
        background: var(--accent-dim);
      }
      /* 主题切换按钮 ◐ */
      .theme-btn {
        background: none; border: 1px solid var(--border);
        color: var(--text-muted); width: 36px; height: 36px;
        cursor: pointer; display: flex; align-items: center; justify-content: center;
        font-size: 0.9rem; transition: all 0.2s;
      }
      .theme-btn:hover {
        border-color: var(--accent); color: var(--accent);
        background: var(--accent-dim);
      }

      /* ══════════════ 页面主体 ══════════════ */
      .main {
        max-width: 900px; margin: 0 auto;
        padding: 80px 32px 80px;  /* 上面留出导航栏的空间 */
      }

      /* 顶部装饰线 */
      .page-eyebrow {
        font-family: var(--mono); font-size: 0.62rem; letter-spacing: 4px;
        color: var(--accent); text-transform: uppercase; margin-bottom: 12px;
        display: flex; align-items: center; gap: 10px;
      }
      .page-eyebrow::before {
        content: ''; width: 28px; height: 1px; background: var(--accent);
      }
      .page-title {
        font-family: var(--display);
        font-size: clamp(2.5rem, 6vw, 4rem);
        letter-spacing: 2px; color: var(--white); margin-bottom: 8px;
        line-height: 1;
      }
      .page-sub {
        font-family: var(--mono); font-size: 0.65rem; color: var(--text-muted);
        letter-spacing: 1.5px; margin-bottom: 28px;
      }
      .stats-row {
        display: flex; gap: 20px; margin-bottom: 24px;
        font-family: var(--mono); font-size: 0.6rem; color: var(--text-muted);
        flex-wrap: wrap;
      }
      .stats-row span { color: var(--accent); font-weight: 700; }

      /* ══════════════ 紧急清单区块 ══════════════ */
      .urgent-box {
        background: var(--accent-dim); border: 1px solid var(--accent);
        padding: 20px 24px; margin-bottom: 32px; border-left: 4px solid var(--accent);
      }
      .urgent-title {
        font-family: var(--mono); font-size: 0.6rem; letter-spacing: 2px;
        color: var(--accent); text-transform: uppercase; margin-bottom: 12px;
      }
      .urgent-item {
        font-size: 0.75rem; margin-bottom: 6px; padding-left: 16px;
        border-left: 2px solid var(--border-bright); color: var(--text);
      }
      .urgent-item strong { color: var(--white); }

      /* ══════════════ 论文卡片（和主页的 radar-card 风格统一） ══════════════ */
      .card {
        background: var(--card); border: 1px solid var(--border);
        padding: 28px 24px; margin-bottom: 16px;
        transition: background 0.2s, border-color 0.2s;
        opacity: 0; transform: translateY(12px);
        animation: fadeUp 0.45s var(--ease) forwards;  /* 淡入上移动画 */
      }
      .card:hover { background: var(--surface); border-color: var(--border-bright); }
      .card-header {
        display: flex; justify-content: space-between; align-items: flex-start;
        margin-bottom: 12px; gap: 16px; flex-wrap: wrap;
      }
      .card-title {
        font-family: var(--display); font-size: 1.35rem; letter-spacing: 0.5px;
        color: var(--white); line-height: 1.25; flex: 1;
      }
      .card-score {
        font-family: var(--display); font-size: 2rem; color: var(--accent);
        line-height: 1; white-space: nowrap; text-align: right;
        flex-shrink: 0;
      }
      .card-score span {
        font-family: var(--mono); font-size: 0.5rem; color: var(--text-faint);
        display: block; letter-spacing: 1px; margin-top: 4px;
      }
      .card-meta {
        font-family: var(--mono); font-size: 0.6rem; color: var(--text-faint);
        letter-spacing: 0.5px; margin-bottom: 14px;
        display: flex; gap: 12px; flex-wrap: wrap; align-items: center;
      }
      .card-meta a { color: var(--accent2); text-decoration: none; }
      .card-meta a:hover { text-decoration: underline; }
      .card-authors { color: var(--text-muted); font-style: italic; }
      .card-pub { background: var(--surface); padding: 2px 6px; border-radius: 2px; }
      .card-body {
        font-size: 0.88rem; color: var(--text-muted); line-height: 1.8; margin-bottom: 12px;
      }
      .card-implications {
        font-family: var(--mono); font-size: 0.7rem; color: var(--accent2);
        background: rgba(201,160,64,0.05); border-left: 2px solid var(--accent2);
        padding: 10px 14px; margin-bottom: 12px;
      }
      .card-model-scores {
        font-family: var(--mono); font-size: 0.58rem; color: var(--text-faint);
        margin-bottom: 12px; display: flex; gap: 8px; flex-wrap: wrap;
      }
      .model-tag { background: var(--surface); padding: 2px 6px; border-radius: 2px; }
      /* 自动生成的草稿样式 */
      .card-draft {
        background: var(--surface); border-left: 4px solid var(--accent);
        padding: 18px 22px; margin-top: 12px; font-size: 0.9rem;
        color: var(--text); line-height: 1.8; font-style: italic;
      }
      .card-draft::before {
        content: '✍️ 自动生成书稿草稿';
        display: block; font-family: var(--mono); font-size: 0.55rem;
        letter-spacing: 2px; color: var(--accent); text-transform: uppercase;
        font-style: normal; margin-bottom: 8px;
      }
      .card-footer {
        display: flex; gap: 10px; flex-wrap: wrap;
        font-family: var(--mono); font-size: 0.58rem; color: var(--text-faint);
        padding-top: 12px; border-top: 1px dashed var(--border); margin-top: 12px;
      }
      .card-footer .tag {
        padding: 2px 6px; background: var(--surface); border-radius: 2px;
      }

      /* ══════════════ 页脚（和主页底部的状态栏风格一致） ══════════════ */
      footer {
        margin-top: 48px; padding-top: 24px;
        border-top: 1px solid var(--border);
        font-family: var(--mono); font-size: 0.6rem; color: var(--text-muted);
        letter-spacing: 1px;
        display: flex; justify-content: space-between;
        flex-wrap: wrap; gap: 8px;
      }
      footer a { color: var(--text-muted); text-decoration: none; }
      footer a:hover { color: var(--accent); }

      /* ══════════════ 动画 ══════════════ */
      @keyframes fadeUp { to { opacity: 1; transform: translateY(0); } }

      /* ══════════════ 手机适配 ══════════════ */
      @media (max-width: 600px) {
        .main { padding: 80px 16px 60px; }
        .page-title { font-size: 2.2rem; }
        .card-header { flex-direction: column; }
        .card-score { text-align: left; }
        .stats-row { overflow-x: auto; padding-bottom: 4px; }
      }

      /* ── STATUS BAR ── */
      .status-bar{{
        position:fixed;bottom:0;width:100%;z-index:200;
        background:var(--bg);border-top:1px solid var(--border);
        padding:10px 32px;font-family:var(--mono);font-size:.6rem;
        color:var(--text-faint);letter-spacing:2px;
        display:flex;justify-content:space-between;align-items:center;
        transition:background .3s,border-color .3s;
      }}
      .status-dot{{
        display:inline-block;width:6px;height:6px;
        background:var(--accent);border-radius:50%;margin-right:8px;
        animation:pulse 2s infinite;
      }}
      @keyframes pulse{{0%,100%{{opacity:1}}50%{{opacity:.2}}}}
    </style>
"""


# ═══════════════════════════════════════════════════════════════
# 🏗️ 第三部分：生成完整 HTML 页面
# ═══════════════════════════════════════════════════════════════
def generate_academic_html(data: dict, output_path: str):
    """
    根据解析出的数据，拼接出和主页风格完全统一的 HTML。
    """
    # ── 1. 生成紧急清单的 HTML ──
    urgent_html = ''
    if data['urgent']:
        urgent_list = ''.join(
            f'<div class="urgent-item">• <strong>{u["chapter"]}</strong> — {u["title"]}</div>'
            for u in data['urgent']
        )
        urgent_html = f'''
    <div class="urgent-box">
      <div class="urgent-title">🚨 立即更新清单</div>
      {urgent_list}
    </div>'''

    # ── 2. 生成论文卡片 ──
    papers_html = ''
    for p in data['papers']:
        # 确保分数可以显示
        try:
            score_num = float(p['score'])
            score_display = f'{score_num:.1f}'
        except (ValueError, TypeError):
            score_display = p['score'] if p['score'] else '—'

        # 原文链接
        link_html = ''
        if p['link'] and p['link'] not in ('N/A', '#', ''):
            link_html = f'<a href="{p["link"]}" target="_blank" rel="noopener">↗ PDF/原文</a>'

        # 作者和发表日期
        meta_tags = []
        if p['authors'] and p['authors'] != 'N/A':
            meta_tags.append(f'<span class="card-authors">👤 {p["authors"]}</span>')
        if p['published'] and p['published'] != 'N/A':
            meta_tags.append(f'<span class="card-pub">📅 {p["published"][:10]}</span>')

        # 底部标签（紧迫度、更新类型等）
        tags = []
        for key, icon in [('urgency', '⏱'), ('update_type', '🔄'), ('action', '✅')]:
            val = p.get(key, '')
            if val and val not in ('N/A', '—', ''):
                tags.append(f'<span class="tag">{icon} {val}</span>')
        tags_html = ''.join(tags) if tags else ''

        # 草稿内容
        draft_html = ''
        if p['draft'] and len(p['draft']) > 30:
            draft_html = f'\n      <div class="card-draft">{p["draft"]}</div>'

        # 模型评分
        model_html = p.get('model_scores', '')

        # 理论关联
        imp_html = ''
        if p['implications'] and p['implications'] != 'N/A':
            imp_html = f'\n      <div class="card-implications">{p["implications"]}</div>'

        # 拼接一张卡片
        papers_html += f'''
    <div class="card">
      <div class="card-header">
        <div class="card-title">{p["title"]}</div>
        <div class="card-score">{score_display}<span>/10</span></div>
      </div>
      <div class="card-meta">
        {' '.join(meta_tags)}
        {f'<span>·</span>' if meta_tags and link_html else ''}
        {link_html}
        {f'<span>·</span>' if p.get("chapter") and p["chapter"] != "N/A" else ''}
        {f'📍 {p["chapter"]}' if p.get("chapter") and p["chapter"] != "N/A" else ''}
      </div>
      <div class="card-body">{p["summary"]}</div>
      {imp_html}
      {model_html}
      {draft_html}
      {f'<div class="card-footer">{tags_html}</div>' if tags_html else ''}
    </div>'''

    # ── 3. 拼装完整 HTML 结构 ──
    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Academic Radar · {data['date']} | Renegade AI</title>
  <meta name="description" content="学术论文监控报告 · {data['high_n']} 高相关论文">
  <!-- 加载 Google 字体（和主页完全一样） -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Space+Mono:ital,wght@0,400;0,700;1,400&family=Crimson+Pro:ital,wght@0,300;0,400;0,600;1,300;1,400&family=Bebas+Neue&display=swap" rel="stylesheet">
{CSS_TEMPLATE}
</head>
<body>
  <!-- ══════════════ 头部导航栏（和主页一模一样） ══════════════ -->
  <nav>
    <a href="https://brook-han.github.io/Renegade-AI/" class="nav-brand">RENEGADE AI v5.3</a>
    <div class="nav-right">
      <a href="../index.html" class="nav-pill">HOME</a>
      <a href="../news/index.html" class="nav-pill">NEWS</a>
      <a href="index.html" class="nav-pill active">PAPERS</a>
      <button class="theme-btn" id="themeBtn" aria-label="Toggle theme">◐</button>
    </div>
  </nav>

  <main class="main">
    <div class="page-eyebrow">§ Academic Radar</div>
    <h1 class="page-title">LITERATURE SCAN</h1>
    <p class="page-sub">{data['date']} · 分析: {data['model']} · 草稿: {data['draft_model']}</p>

    <div class="stats-row">
      <div>📊 总条目: <span>{data['total']}</span></div>
      <div>⭐ 高相关: <span>{data['high_n']}</span></div>
      <div>🔶 中相关: <span>{data['med_n']}</span></div>
    </div>

    {urgent_html}
    {papers_html}
  </main>

  <!-- ══════════════ 页脚（和主页底部栏视觉统一） ══════════════ -->
  <footer style="max-width:900px;margin:0 auto;padding:24px 32px 60px;border-top:1px solid var(--border);font-family:var(--mono);font-size:0.6rem;color:var(--text-muted);letter-spacing:1px;display:flex;justify-content:space-between;flex-wrap:wrap;gap:8px;">
    <span>Renegade AI v5.3 · Academic Radar</span>
    <a href="https://brook-han.github.io/Renegade-AI/" target="_blank" rel="noopener" style="color:var(--text-muted);text-decoration:none;">GitHub ↗</a>
  </footer>

  <div class="status-bar">
    <span><span class="status-dot"></span><span id="statusText">STATUS: [ ACADEMIC_PIPELINE · NOMINAL ]</span></span>
    <span id="statusTime"></span>
  </div>

  <script>
    /* ══════════════ 主题切换（使用和主页同一个 localStorage 键） ══════════════ */
    (function() {{
      const html = document.documentElement;
      const btn = document.getElementById('themeBtn');
      const KEY = 'renegade-theme';   // 和主页保持一致，切换一次全局生效

      // 应用主题：light 或 dark
      function apply(theme) {{
        html.classList.toggle('light', theme === 'light');
        localStorage.setItem(KEY, theme);
      }}

      // 优先读取本地存储，否则跟随系统偏好
      const systemDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
      const saved = localStorage.getItem(KEY) || (systemDark ? 'dark' : 'light');
      apply(saved);

      // 点击按钮切换
      btn.onclick = function() {{
        const current = html.classList.contains('light') ? 'dark' : 'light';
        apply(current);
      }};
    }})();

    /* ══════════════ 卡片逐个淡入 ══════════════ */
    document.querySelectorAll('.card').forEach(function(card, index) {{
      card.style.animationDelay = (index * 0.05) + 's';
    }});

    /* ══════════════ 状态栏轮播 ══════════════ */
    (function(){{
      const msgs=[
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
      function tick(){{
        st.textContent=msgs[i%msgs.length];i++;
        tm.textContent=new Date().toISOString().replace('T',' ').slice(0,19)+' UTC';
      }}
      tick();setInterval(tick,5000);
    }})();
  </script>
</body>
</html>'''

    # 写入文件
    Path(output_path).write_text(html, encoding='utf-8')
    print(f'✅ HTML 已生成: {output_path}')


# ═══════════════════════════════════════════════════════════════
# 🚀 第四部分：程序入口
# ═══════════════════════════════════════════════════════════════
if __name__ == '__main__':
    # 1. 确定要转换哪个 Markdown 文件
    if len(sys.argv) > 1:
        md_file = sys.argv[1]
        print(f'📄 使用指定文件: {md_file}')
    else:
        # 自动寻找最新的学术报告（在几个常见目录里找）
        for search_dir in [Path('docs/academic'), Path('output/academic'), Path('reports')]:
            if search_dir.exists():
                reports = sorted(search_dir.glob('academic_report_*.md'))
                if reports:
                    md_file = str(reports[-1])
                    break
        else:
            print('❌ 没找到 academic_report_*.md 文件')
            print('💡 用法: python academic_md_to_html.py 报告文件路径')
            sys.exit(1)
        print(f'🔍 自动选择最新报告: {md_file}')

    # 2. 解析 Markdown
    print('📖 解析中...')
    data = parse_academic_report(md_file)

    if not data['papers']:
        print('⚠️ 警告: 没解析到论文，请检查 Markdown 格式')

    # 3. 输出 HTML（放在和 md 相同的目录下）
    out_file = str(Path(md_file).with_suffix('.html'))
    generate_academic_html(data, out_file)

    print('🎉 完成！可以在浏览器里打开：')
    print(f'   file://{Path(out_file).resolve()}')