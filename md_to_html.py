#!/usr/bin/env python3
"""
将 news_report_multi_*.md 转换为 Renegade AI 网站风格的 HTML 页面。
用法：python md_to_html.py reports/news_report_multi_2026-05-09_162454.md
"""

import re
import sys
from pathlib import Path
from datetime import datetime

# ── 解析 MD ──────────────────────────────────────────────

def parse_report(md_path: str) -> dict:
    with open(md_path, encoding='utf-8') as f:
        text = f.read()

    # 日期
    date_match = re.search(r'\*\*生成日期\*\*:\s*(\d{4}-\d{2}-\d{2})', text)
    date = date_match.group(1) if date_match else datetime.today().strftime('%Y-%m-%d')

    # 模型阵容
    models_match = re.search(r'\*\*模型阵容\*\*:\s*(.+?)(?:\n|$)', text)
    models = models_match.group(1).strip() if models_match else ''

    # 高相关块
    high_block = re.search(r'## ⭐ 高相关.*?\n(.*?)(?=\n## |\Z)', text, re.DOTALL)
    items = []
    if high_block:
        blocks = high_block.group(1).split('### ')
        for b in blocks[1:]:
            lines = b.strip().split('\n')
            title = lines[0].lstrip('0123456789. ').strip()
            fields = {}
            for l in lines:
                for key in ['最终评分', '核心发现', '与本书关联', '链接', '紧迫度', '目标章节', '更新类型', '建议更新']:
                    pat = rf'-\s*\*\*{key}\*\*:\s*(.*)'
                    m = re.search(pat, l)
                    if m:
                        fields[key] = m.group(1).strip()
            # 草稿
            draft_match = re.search(r'✍️.*?草稿.*?\n>\s*(.+?)(?=\n\n|\n###|\Z)', b, re.DOTALL)
            draft = draft_match.group(1).strip() if draft_match else ''
            items.append({
                'title': title,
                'score': fields.get('最终评分', ''),
                'summary': fields.get('核心发现', ''),
                'implications': fields.get('与本书关联', ''),
                'link': fields.get('链接', ''),
                'chapter': fields.get('目标章节', ''),
                'draft': draft,
            })

    # 总数
    total = re.search(r'\*\*分析条目数\*\*:\s*(\d+)', text)
    total_count = total.group(1) if total else str(len(items))

    # 统计
    high_cnt = re.search(r'高相关.*?\*\*(\d+)\*\*', text)
    med_cnt = re.search(r'中相关.*?\*\*(\d+)\*\*', text)
    high_n = high_cnt.group(1) if high_cnt else '0'
    med_n = med_cnt.group(1) if med_cnt else '0'

    return {
        'date': date,
        'models': models,
        'items': items,
        'total': total_count,
        'high_n': high_n,
        'med_n': med_n,
    }


# ── 生成 HTML ─────────────────────────────────────────────

CSS = """    <style>
      :root {
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
      }
      * { box-sizing: border-box; margin: 0; padding: 0; }
      body {
        font-family: var(--serif);
        background: var(--bg);
        color: var(--text);
        line-height: 1.8;
        -webkit-font-smoothing: antialiased;
        padding: 60px 32px;
        max-width: 860px;
        margin: 0 auto;
      }
      .back-link {
        font-family: var(--mono);
        font-size: 0.65rem;
        letter-spacing: 2px;
        color: var(--text-muted);
        text-decoration: none;
        text-transform: uppercase;
        border: 1px solid var(--border);
        padding: 6px 14px;
        display: inline-block;
        margin-bottom: 40px;
        transition: all .2s;
      }
      .back-link:hover { border-color: var(--accent); color: var(--accent); }
      .page-eyebrow {
        font-family: var(--mono);
        font-size: 0.62rem;
        letter-spacing: 4px;
        color: var(--accent);
        text-transform: uppercase;
        margin-bottom: 8px;
        display: flex; align-items: center; gap: 10px;
      }
      .page-eyebrow::before {
        content: ''; width: 28px; height: 1px; background: var(--accent);
      }
      .page-title {
        font-family: var(--display);
        font-size: 3rem;
        letter-spacing: 2px;
        color: var(--white);
        margin-bottom: 6px;
        line-height: 1;
      }
      .page-sub {
        font-family: var(--mono);
        font-size: 0.65rem;
        color: var(--text-muted);
        letter-spacing: 1.5px;
        margin-bottom: 48px;
      }
      .stats-row {
        display: flex; gap: 24px; margin-bottom: 40px;
        font-family: var(--mono); font-size: 0.65rem; color: var(--text-muted);
        letter-spacing: 1px;
      }
      .stats-row span { color: var(--accent); font-weight: 700; }
      .card {
        background: var(--card);
        border: 1px solid var(--border);
        padding: 32px;
        margin-bottom: 16px;
        transition: border-color .2s;
      }
      .card:hover { border-color: var(--accent); }
      .card-header {
        display: flex; justify-content: space-between; align-items: flex-start;
        margin-bottom: 16px;
      }
      .card-title {
        font-family: var(--display);
        font-size: 1.4rem;
        letter-spacing: 1px;
        color: var(--white);
        line-height: 1.2;
        flex: 1;
        margin-right: 12px;
      }
      .card-score {
        font-family: var(--display);
        font-size: 2.2rem;
        color: var(--accent);
        line-height: 1;
        white-space: nowrap;
      }
      .card-score span {
        font-family: var(--mono);
        font-size: 0.55rem;
        color: var(--text-muted);
        display: block;
        letter-spacing: 1px;
      }
      .card-meta {
        font-family: var(--mono);
        font-size: 0.6rem;
        color: var(--text-faint);
        letter-spacing: 1px;
        margin-bottom: 14px;
        display: flex; gap: 16px; flex-wrap: wrap;
      }
      .card-meta a {
        color: var(--accent2); text-decoration: none;
        border-bottom: 1px solid transparent;
        transition: border-color .2s;
      }
      .card-meta a:hover { border-bottom-color: var(--accent2); }
      .card-body {
        font-size: 0.92rem;
        color: var(--text-muted);
        line-height: 1.8;
        margin-bottom: 12px;
      }
      .card-verdict {
        font-family: var(--mono);
        font-size: 0.68rem;
        color: var(--accent2);
        padding: 10px 14px;
        background: rgba(201,160,64,0.05);
        border-left: 2px solid var(--accent2);
        letter-spacing: 0.5px;
        margin-bottom: 12px;
      }
      .card-draft {
        background: var(--surface);
        border-left: 4px solid var(--accent);
        padding: 20px 24px;
        margin-top: 16px;
        font-size: 0.9rem;
        color: var(--text);
        line-height: 1.85;
        font-style: italic;
      }
      .card-draft::before {
        content: '✍️ 自动生成书稿草稿';
        display: block;
        font-family: var(--mono);
        font-size: 0.58rem;
        letter-spacing: 3px;
        color: var(--accent);
        text-transform: uppercase;
        font-style: normal;
        margin-bottom: 10px;
      }
      footer {
        margin-top: 48px; padding-top: 24px;
        border-top: 1px solid var(--border);
        font-family: var(--mono);
        font-size: 0.6rem;
        color: var(--text-muted);
        letter-spacing: 1px;
        display: flex; justify-content: space-between;
      }
      footer a { color: var(--text-muted); text-decoration: none; }
      footer a:hover { color: var(--accent); }
      @media (max-width: 600px) {
        body { padding: 32px 16px; }
        .page-title { font-size: 2.2rem; }
        .card-header { flex-direction: column; }
        .card-score { margin-top: 8px; }
      }
    </style>"""


def generate_html(data: dict, output_path: str):
    items_html = ''
    for it in data['items']:
        score = it['score'] or '—'
        try:
            score_num = float(score)
            score_display = f'{score_num:.1f}'
        except:
            score_display = score

        draft_html = ''
        if it['draft'] and len(it['draft']) > 30:
            draft_html = f'\n      <div class="card-draft">{it["draft"]}</div>'

        link_html = ''
        if it['link'] and it['link'] != 'N/A':
            link_html = f'<a href="{it["link"]}" target="_blank">↗ 原文链接</a>'

        chapter_html = ''
        if it['chapter'] and it['chapter'] != 'N/A':
            chapter_html = f'<span>📍 {it["chapter"]}</span>'

        verdict_html = ''
        if it['implications'] and it['implications'] != 'N/A':
            verdict_html = f'\n      <div class="card-verdict">{it["implications"]}</div>'

        items_html += f'''    <div class="card">
      <div class="card-header">
        <div class="card-title">{it["title"]}</div>
        <div class="card-score">{score_display}<span>/10</span></div>
      </div>
      <div class="card-meta">
        {chapter_html}
        {link_html}
      </div>
      <div class="card-body">{it["summary"]}</div>{verdict_html}{draft_html}
    </div>
'''

    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Renegade AI 资讯监控 · {data['date']}</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Space+Mono:ital,wght@0,400;0,700;1,400&family=Crimson+Pro:ital,wght@0,300;0,400;0,600;1,300;1,400&family=Bebas+Neue&display=swap" rel="stylesheet">
{CSS}
</head>
<body>
  <a href="/" class="back-link">← Renegade AI v5.3</a>
  <div class="page-eyebrow">§ 资讯监控</div>
  <h1 class="page-title">DAILY RADAR</h1>
  <p class="page-sub">{data['date']} · 模型: {data['models']} · 共分析 {data['total']} 条 · 高相关 {data['high_n']} 条 · 中相关 {data['med_n']} 条</p>
  <div class="stats-row">
    <span>▲</span> 高相关 ≥6.5: <span>{data['high_n']}</span> 条
    <span>◆</span> 中相关 3-6.4: <span>{data['med_n']}</span> 条
    <span>▼</span> 总计分析: <span>{data['total']}</span> 条
  </div>
{items_html}
  <footer>
    <span>Renegade AI v5.3 · Brooks Han</span>
    <a href="https://github.com/Brook-Han/renegade-ai-Updater" target="_blank">GitHub ↗</a>
  </footer>
</body>
</html>'''

    Path(output_path).write_text(html, encoding='utf-8')
    print(f'✅ HTML 已保存: {output_path}')


# ── 入口 ──────────────────────────────────────────────────

if __name__ == '__main__':
    if len(sys.argv) > 1:
        md_file = sys.argv[1]
    else:
        # 自动找当日最新的 news_report
        reports = sorted(Path('reports').glob('news_report_multi_*.md'))
        if not reports:
            print('未找到任何 MD 报告')
            sys.exit(1)
        md_file = str(reports[-1])

    print(f'📄 解析: {md_file}')
    data = parse_report(md_file)
    out_file = md_file.replace('.md', '.html')
    generate_html(data, out_file)