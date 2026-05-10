#!/usr/bin/env python3
"""
扫描 reports/*.html，生成带每日摘要卡片的 index.html 存档页。
"""

import os
import re
from pathlib import Path
from datetime import datetime
import json

def extract_cards_from_html(html_path: str) -> list[dict]:
    """从单个报告 HTML 中提取所有卡片的标题、评分、摘要、链接、草稿状况"""
    with open(html_path, encoding='utf-8') as f:
        content = f.read()

    cards = []
    # 简单正则匹配每一个 .card 区块
    card_blocks = re.findall(r'<div class="card">(.*?)</div>\s*(?=<div class="card">|</body>|$)', content, re.DOTALL)
    for block in card_blocks:
        card = {}
        # 标题
        title_match = re.search(r'<div class="card-title">(.*?)</div>', block, re.DOTALL)
        if title_match:
            card['title'] = title_match.group(1).strip()
        # 评分
        score_match = re.search(r'<div class="card-score">([\d.]+)<span>/10</span>', block)
        if score_match:
            card['score'] = score_match.group(1)
        # 链接（摘自 card-meta 中的第一个 a）
        link_match = re.search(r'<a href="([^"]+)" target="_blank">↗ 原文链接</a>', block)
        if link_match:
            card['link'] = link_match.group(1)
        # 摘要（card-body）
        summary_match = re.search(r'<div class="card-body">(.*?)</div>', block, re.DOTALL)
        if summary_match:
            card['summary'] = summary_match.group(1).strip()
        # 是否有草稿 (card-draft)
        draft_match = re.search(r'<div class="card-draft">', block)
        card['has_draft'] = bool(draft_match)
        # 章节信息
        chapter_match = re.search(r'📍\s*(.*?)(?:</span>|$)', block)
        if chapter_match:
            card['chapter'] = chapter_match.group(1).strip()

        if card.get('title'):
            cards.append(card)
    return cards

def generate_index(reports_pattern: str = "reports/news_report_multi_*.html"):
    """生成带每日摘要的 index.html"""
    report_files = sorted(Path('.').glob(reports_pattern), reverse=True)
    if not report_files:
        report_files = sorted(Path('.').glob("reports/papers_report_multi_*.html"), reverse=True)

    # 按日期分组，每个日期取第一个（最新）报告，也可以保留多个时间点
    date_groups = {}
    for f in report_files:
        # 文件名样例 news_report_multi_2026-05-09_162454.html
        name = f.name
        match = re.search(r'(\d{4}-\d{2}-\d{2})_(\d{6})', name)
        if match:
            date_str = match.group(1)
            time_str = match.group(2)
            if date_str not in date_groups:
                date_groups[date_str] = []
            date_groups[date_str].append({
                'file': name,
                'time': time_str,
                'full': str(f),
            })

    # 按日期倒序
    sorted_dates = sorted(date_groups.keys(), reverse=True)

    # 构建 HTML 主体内容
    day_sections = []

    for date in sorted_dates:
        # 取该日期最近的一份报告（列表已按文件名排序，直接取第一个）
        entry = date_groups[date][0]  # 可根据需要调整
        html_path = entry['full']
        cards = extract_cards_from_html(html_path)
        top3 = cards[:3]  # 每天前三条

        # 生成该日的 HTML 块
        day_html = f'<div class="day-group">\n'
        day_html += f'  <div class="day-header">{date}</div>\n'
        day_html += f'  <div class="day-meta">{entry["time"][:2]}:{entry["time"][2:4]}:{entry["time"][4:]} · {len(cards)} 条分析</div>\n'

        for card in top3:
            score = card.get('score', '—')
            title = card.get('title', 'No title')
            link = card.get('link', '#')
            summary = card.get('summary', '')
            chapter = card.get('chapter', '')
            draft_badge = ' ✍️' if card.get('has_draft') else ''

            day_html += f'''
  <div class="card">
    <div class="card-header">
      <div class="card-title">{title}{draft_badge}</div>
      <div class="card-score">{score}<span>/10</span></div>
    </div>
    <div class="card-meta">
      {f'<span>📍 {chapter}</span>' if chapter else ''}
      {'<a href="' + link + '" target="_blank">↗ 原文</a>' if link else ''}
    </div>
    <div class="card-body">{summary[:200]}</div>
    <div class="card-link"><a href="{entry['file']}">查看完整报告 →</a></div>
  </div>\n'''

        day_html += '</div>\n'
        day_sections.append(day_html)

    # 总报告数
    total_reports = sum(len(v) for v in date_groups.values())

    # 读取模板（直接在脚本内定义，或从外部文件读取）
    index_template = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Renegade AI 每日雷达 · 报告存档</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Space+Mono:ital,wght@0,400;0,700;1,400&family=Crimson+Pro:ital,wght@0,300;0,400;0,600;1,300;1,400&family=Bebas+Neue&display=swap" rel="stylesheet">
  <style>
    :root {{
      --bg: #08080e;
      --surface: #111120;
      --card: #13131f;
      --border: #1e1e30;
      --text: #cccce0;
      --text-muted: #6868a0;
      --accent: #e8503a;
      --accent2: #c9a040;
      --white: #f0f0f8;
      --mono: 'Space Mono', 'Courier New', monospace;
      --serif: 'Crimson Pro', Georgia, serif;
      --display: 'Bebas Neue', 'Arial Narrow', sans-serif;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: var(--serif);
      background: var(--bg);
      color: var(--text);
      line-height: 1.8;
      -webkit-font-smoothing: antialiased;
      padding: 60px 32px;
      max-width: 860px;
      margin: 0 auto;
    }}
    .back-link {{
      font-family: var(--mono);
      font-size: 0.65rem; letter-spacing: 2px;
      color: var(--text-muted); text-decoration: none;
      text-transform: uppercase;
      border: 1px solid var(--border); padding: 6px 14px;
      display: inline-block; margin-bottom: 40px;
      transition: all .2s;
    }}
    .back-link:hover {{ border-color: var(--accent); color: var(--accent); }}
    .page-eyebrow {{
      font-family: var(--mono); font-size: 0.62rem;
      letter-spacing: 4px; color: var(--accent);
      text-transform: uppercase; margin-bottom: 8px;
      display: flex; align-items: center; gap: 10px;
    }}
    .page-eyebrow::before {{
      content: ''; width: 28px; height: 1px; background: var(--accent);
    }}
    h1 {{
      font-family: var(--display); font-size: 3rem;
      letter-spacing: 2px; color: var(--white);
      margin-bottom: 6px; line-height: 1;
    }}
    .subtitle {{
      font-family: var(--mono); font-size: 0.65rem;
      color: var(--text-muted); letter-spacing: 1.5px;
      margin-bottom: 48px;
    }}
    .stats-row {{
      display: flex; gap: 24px; margin-bottom: 40px;
      font-family: var(--mono); font-size: 0.65rem;
      color: var(--text-muted); letter-spacing: 1px;
    }}
    .stats-row span {{ color: var(--accent); font-weight: 700; }}

    .day-group {{ margin-bottom: 48px; }}
    .day-header {{
      font-family: var(--display); font-size: 1.8rem;
      letter-spacing: 1px; color: var(--white);
      border-bottom: 1px solid var(--border);
      padding-bottom: 8px; margin-bottom: 4px;
    }}
    .day-meta {{
      font-family: var(--mono); font-size: 0.65rem;
      color: var(--text-muted); margin-bottom: 16px;
    }}

    .card {{
      background: var(--card); border: 1px solid var(--border);
      padding: 24px; margin-bottom: 8px;
      transition: border-color .2s;
    }}
    .card:hover {{ border-color: var(--accent); }}
    .card-header {{
      display: flex; justify-content: space-between; align-items: flex-start;
      margin-bottom: 10px;
    }}
    .card-title {{
      font-family: var(--display); font-size: 1.2rem;
      letter-spacing: 1px; color: var(--white); line-height: 1.2;
      flex: 1; margin-right: 12px;
    }}
    .card-score {{
      font-family: var(--display); font-size: 1.8rem;
      color: var(--accent); line-height: 1;
      white-space: nowrap;
    }}
    .card-score span {{
      font-family: var(--mono); font-size: 0.5rem;
      color: var(--text-muted); display: block;
    }}
    .card-meta {{
      font-family: var(--mono); font-size: 0.6rem;
      color: var(--text-muted); margin-bottom: 12px;
      display: flex; gap: 16px; flex-wrap: wrap;
    }}
    .card-meta a {{ color: var(--accent2); text-decoration: none; }}
    .card-body {{
      font-size: 0.92rem; color: var(--text);
      line-height: 1.8; margin-bottom: 8px;
    }}
    .card-link {{
      font-family: var(--mono); font-size: 0.65rem; margin-top: 10px;
    }}
    .card-link a {{
      color: var(--accent); text-decoration: none;
      border-bottom: 1px solid transparent;
    }}
    .card-link a:hover {{ border-bottom-color: var(--accent); }}

    footer {{
      margin-top: 64px; padding-top: 24px;
      border-top: 1px solid var(--border);
      font-family: var(--mono); font-size: 0.6rem;
      color: var(--text-muted); letter-spacing: 1px;
      display: flex; justify-content: space-between;
    }}
    footer a {{ color: var(--text-muted); text-decoration: none; }}
    footer a:hover {{ color: var(--accent); }}

    @media (max-width: 600px) {{
      body {{ padding: 40px 16px; }}
      h1 {{ font-size: 2.2rem; }}
      .card-header {{ flex-direction: column; }}
    }}
  </style>
</head>
<body>
  <a href="https://brook-han.github.io/Renegade-AI/" class="back-link">← Renegade AI v5.3</a>
  <div class="page-eyebrow">§ 每日雷达 · Daily Radar</div>
  <h1>REPORT ARCHIVE</h1>
  <p class="subtitle">自动抓取 · AI 分析 · 书稿草稿生成 · GitHub Pages 部署</p>
  <div class="stats-row">
    <span>▲</span> 报告总数: <span>{total_reports}</span>
    <span>◆</span> 最新: <span>{sorted_dates[0] if sorted_dates else '—'}</span>
  </div>
  {"".join(day_sections)}
  <footer>
    <span>Renegade AI v5.3 · Brooks Han</span>
    <a href="https://github.com/Brook-Han/renegade-ai-Updater" target="_blank">GitHub ↗</a>
  </footer>
</body>
</html>'''

    with open('reports/index.html', 'w', encoding='utf-8') as f:
        f.write(index_template)
    print(f'✅ Archive index generated with {total_reports} reports')

if __name__ == '__main__':
    generate_index()