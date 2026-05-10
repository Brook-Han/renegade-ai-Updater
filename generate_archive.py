#!/usr/bin/env python3
"""
扫描 reports/*.html，生成带每日摘要卡片的 index.html 存档页。
每天的最新报告由文件修改时间决定，保证主页永远指向最后生成的报告。
"""

import re
import os
from pathlib import Path
from string import Template

def extract_cards_from_html(html_path: Path) -> list[dict]:
    with open(html_path, encoding='utf-8') as f:
        content = f.read()
    cards = []
    card_blocks = re.findall(r'<div class="card">(.*?)</div>\s*(?=<div class="card">|</body>|$)', content, re.DOTALL)
    for block in card_blocks:
        card = {}
        title_m = re.search(r'<div class="card-title">(.*?)</div>', block, re.DOTALL)
        if title_m: card['title'] = title_m.group(1).strip()
        score_m = re.search(r'<div class="card-score">([\d.]+)<span>/10</span>', block)
        if score_m: card['score'] = score_m.group(1)
        link_m = re.search(r'<a href="([^"]+)" target="_blank">↗ 原文链接</a>', block)
        if link_m: card['link'] = link_m.group(1)
        summary_m = re.search(r'<div class="card-body">(.*?)</div>', block, re.DOTALL)
        if summary_m: card['summary'] = summary_m.group(1).strip()
        card['has_draft'] = '<div class="card-draft">' in block
        chapter_m = re.search(r'📍\s*(.*?)(?:</span>|$)', block)
        if chapter_m: card['chapter'] = chapter_m.group(1).strip()
        if 'news_report' in html_path.name:
            card['type'] = 'news'
        elif 'papers_report' in html_path.name:
            card['type'] = 'papers'
        else:
            card['type'] = 'unknown'
        if card.get('title'):
            cards.append(card)
    return cards

def generate_index():
    reports_dir = Path("reports")
    reports_dir.mkdir(exist_ok=True)

    # 收集所有报告文件
    all_files = list(reports_dir.glob("news_report_multi_*.html")) + \
                list(reports_dir.glob("papers_report_multi_*.html"))

    # 按日期分组，并记录每个文件的全路径和修改时间
    date_groups = {}
    for f in all_files:
        m = re.search(r'(\d{4}-\d{2}-\d{2})_(\d{6})', f.name)
        if not m:
            continue
        date_str = m.group(1)
        time_str = m.group(2)
        if date_str not in date_groups:
            date_groups[date_str] = []
        date_groups[date_str].append({
            'file': f.name,
            'time': time_str,
            'full': str(f),
            'mtime': os.path.getmtime(str(f)),
        })

    sorted_dates = sorted(date_groups.keys(), reverse=True)
    day_sections = []

    for date in sorted_dates:
        all_cards = []
        for entry in date_groups[date]:
            cards = extract_cards_from_html(Path(entry['full']))
            all_cards.extend(cards)

        all_cards.sort(key=lambda x: float(x.get('score', 0)) if x.get('score', '').replace('.','',1).isdigit() else -1, reverse=True)
        top3 = all_cards[:3]

        # 用文件修改时间确定当天最新报告
        latest_entry = max(date_groups[date], key=lambda x: x['mtime'])
        link_target = latest_entry['file']          # 文件名，作为相对链接
        time_str = latest_entry['time']
        formatted_time = f"{time_str[:2]}:{time_str[2:4]}:{time_str[4:]}"
        total_count = len(all_cards)

        day_html = f'<div class="day-group">\n'
        day_html += f'  <div class="day-header">{date}</div>\n'
        day_html += f'  <div class="day-meta">{formatted_time} · 共 {total_count} 条分析（含新闻/论文）</div>\n'

        for card in top3:
            score = card.get('score', '—')
            title = card.get('title', 'No title')
            link = card.get('link', '#')
            summary = card.get('summary', '')
            chapter = card.get('chapter', '')
            draft_badge = ' ✍️' if card.get('has_draft') else ''
            type_badge = ''
            if card.get('type') == 'papers':
                type_badge = ' <span style="font-size:0.55rem; background:var(--accent-dim); padding:2px 6px; border-radius:2px;">📄 论文</span>'
            elif card.get('type') == 'news':
                type_badge = ' <span style="font-size:0.55rem; background:var(--accent3-dim); padding:2px 6px; border-radius:2px;">📰 新闻</span>'

            day_html += f'''
  <div class="card">
    <div class="card-header">
      <div class="card-title">{title}{draft_badge}{type_badge}</div>
      <div class="card-score">{score}<span>/10</span></div>
    </div>
    <div class="card-meta">
      {f'<span>📍 {chapter}</span>' if chapter else ''}
      {'<a href="' + link + '" target="_blank">↗ 原文</a>' if link else ''}
    </div>
    <div class="card-body">{summary[:200]}</div>
    <div class="card-link"><a href="{link_target}">查看完整报告 →</a></div>
  </div>\n'''
        day_html += '</div>\n'
        day_sections.append(day_html)

    total_reports = len(all_files)
    first_date = sorted_dates[0] if sorted_dates else '—'

    # 模板（与你之前使用的风格一致）
    template_str = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Renegade AI 每日雷达 · 报告存档</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Space+Mono:ital,wght@0,400;0,700;1,400&family=Crimson+Pro:ital,wght@0,300;0,400;0,600;1,300;1,400&family=Bebas+Neue&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css">
  <style>
    :root {
      --bg: #f8f9fc; --bg2: #ffffff; --surface: #f0f2f8;
      --card: #ffffff; --border: #e0e2ec; --border-bright: #c0c2d0;
      --text: #2a2a40; --text-muted: #6a6a80; --text-faint: #a0a0b8;
      --accent: #e8503a; --accent-dim: rgba(232,80,58,0.08);
      --accent2: #b88c2a; --accent3: #3a7fbf; --accent3-dim: rgba(74,143,207,0.08);
      --white: #2a2a40; --mono: 'Space Mono', monospace;
      --serif: 'Crimson Pro', serif; --display: 'Bebas Neue', sans-serif;
    }
    :root.dark-theme {
      --bg: #08080e; --bg2: #0d0d18; --surface: #111120;
      --card: #13131f; --border: #1e1e30; --border-bright: #2e2e50;
      --text: #cccce0; --text-muted: #6868a0; --text-faint: #3a3a5a;
      --accent: #e8503a; --accent-dim: rgba(232,80,58,0.12);
      --accent2: #c9a040; --accent3: #4a8fcf; --accent3-dim: rgba(74,143,207,0.1);
      --white: #f0f0f8;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { font-family: var(--serif); background: var(--bg); color: var(--text); line-height: 1.8; transition: background-color 0.3s ease, color 0.3s ease; }
    nav { position: fixed; top: 0; width: 100%; z-index: 200; background: rgba(248,249,252,0.92); backdrop-filter: blur(24px); border-bottom: 1px solid var(--border); height: 56px; display: flex; align-items: center; justify-content: space-between; padding: 0 32px; font-family: var(--mono); }
    .nav-brand { font-size: 0.75rem; font-weight: 700; color: var(--accent); letter-spacing: 3px; text-decoration: none; }
    .nav-right { display: flex; gap: 12px; align-items: center; }
    .theme-toggle { background: none; border: 1px solid var(--border); color: var(--text-muted); width: 36px; height: 36px; cursor: pointer; }
    .main { max-width: 860px; margin: 0 auto; padding: 100px 32px 60px; }
    .page-eyebrow { font-family: var(--mono); font-size: 0.62rem; letter-spacing: 4px; color: var(--accent); text-transform: uppercase; margin-bottom: 8px; display: flex; align-items: center; gap: 10px; }
    .page-eyebrow::before { content: ''; width: 28px; height: 1px; background: var(--accent); }
    h1 { font-family: var(--display); font-size: 3rem; letter-spacing: 2px; color: var(--white); margin-bottom: 6px; line-height: 1; }
    .subtitle { font-family: var(--mono); font-size: 0.65rem; color: var(--text-muted); letter-spacing: 1.5px; margin-bottom: 48px; display: flex; justify-content: space-between; }
    .day-group { margin-bottom: 48px; }
    .day-header { font-family: var(--display); font-size: 1.8rem; color: var(--white); border-bottom: 1px solid var(--border); padding-bottom: 8px; margin-bottom: 4px; }
    .day-meta { font-family: var(--mono); font-size: 0.65rem; color: var(--text-muted); margin-bottom: 16px; }
    .card { background: var(--card); border: 1px solid var(--border); padding: 24px; margin-bottom: 8px; }
    .card:hover { border-color: var(--accent); }
    .card-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 10px; }
    .card-title { font-family: var(--display); font-size: 1.2rem; color: var(--white); flex: 1; margin-right: 12px; }
    .card-score { font-family: var(--display); font-size: 1.8rem; color: var(--accent); line-height: 1; white-space: nowrap; }
    .card-score span { font-family: var(--mono); font-size: 0.5rem; color: var(--text-muted); display: block; }
    .card-meta { font-family: var(--mono); font-size: 0.6rem; color: var(--text-muted); margin-bottom: 12px; display: flex; gap: 16px; }
    .card-body { font-size: 0.92rem; color: var(--text); line-height: 1.8; margin-bottom: 8px; }
    .card-link { font-family: var(--mono); font-size: 0.65rem; margin-top: 10px; }
    .card-link a { color: var(--accent); text-decoration: none; border-bottom: 1px solid transparent; }
    .card-link a:hover { border-bottom-color: var(--accent); }
    footer { margin-top: 64px; padding-top: 24px; border-top: 1px solid var(--border); font-family: var(--mono); font-size: 0.6rem; color: var(--text-muted); display: flex; justify-content: space-between; }
    @media (max-width: 600px) { .main { padding: 100px 16px 40px; } h1 { font-size: 2.2rem; } }
  </style>
</head>
<body>
  <nav>
    <a href="https://brook-han.github.io/Renegade-AI/" class="nav-brand">RENEGADE AI v5.3</a>
    <div class="nav-right">
      <button class="theme-toggle" id="themeToggle" aria-label="切换主题"><i class="fa fa-sun-o" id="themeIcon"></i></button>
    </div>
  </nav>
  <div class="main">
    <div class="page-eyebrow">§ 每日雷达 · Daily Radar</div>
    <h1>REPORT ARCHIVE</h1>
    <div class="subtitle">
      <span>全网抓取 · AI 分析 · GitHub Pages 部署</span>
      <span class="stats">▲ 报告总数: $total_reports &nbsp;◆ 最新: $first_date</span>
    </div>
    $day_sections
    <footer>
      <span>Renegade AI v5.3 · Brooks Han</span>
      <a href="https://github.com/Brook-Han/renegade-ai-Updater" target="_blank">GitHub ↗</a>
    </footer>
  </div>
  <script>
    (function() {
      const html = document.documentElement;
      const btn = document.getElementById('themeToggle');
      const icon = document.getElementById('themeIcon');
      const get = () => localStorage.getItem('renegade-theme') || 'light';
      const set = (t) => {
        if (t === 'dark') { html.classList.add('dark-theme'); icon.className = 'fa fa-moon-o'; }
        else { html.classList.remove('dark-theme'); icon.className = 'fa fa-sun-o'; }
        localStorage.setItem('renegade-theme', t);
      };
      set(get());
      btn.onclick = () => set(html.classList.contains('dark-theme') ? 'light' : 'dark');
    })();
  </script>
</body>
</html>'''

    template = Template(template_str)
    final_html = template.substitute(
        total_reports=total_reports,
        first_date=first_date,
        day_sections="".join(day_sections)
    )
    output_path = reports_dir / "index.html"
    output_path.write_text(final_html, encoding='utf-8')
    print(f'✅ Archive index generated with {total_reports} reports (news + papers merged)')

if __name__ == '__main__':
    generate_index()