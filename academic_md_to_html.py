#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎓 Academic Radar MD → HTML 转换器（完整注释版）

功能：将 academic_radar.py 生成的 Markdown 报告转换为漂亮的网页
风格：与 Renegade AI 官网一致，支持浅色/深色主题切换

📋 用法：
    # 方式1：转换指定文件
    python academic_md_to_html.py reports/academic/academic_report_2026-05-11_143022.md
    
    # 方式2：自动找最新报告（推荐✨）
    python academic_md_to_html.py

🔧 输出：同目录下生成 .html 文件，双击即可在浏览器预览

作者：Brooks Han
版本：v1.0 (2026-05-11)
"""

# ──────────────────────────────────────────────────────────────
# 🔧 导入必要的模块
# ──────────────────────────────────────────────────────────────

import re          # 正则表达式：用于从 Markdown 文本中提取结构化数据
import sys         # 系统模块：处理命令行参数和程序退出
from pathlib import Path  # 现代路径处理库：比 os.path 更安全易用
from datetime import datetime  # 日期时间工具：用于默认日期回退

# ──────────────────────────────────────────────────────────────
# 📖 函数1：解析学术 Markdown 报告
# ──────────────────────────────────────────────────────────────

def parse_academic_report(md_path: str) -> dict:
    """
    解析 academic_radar.py 生成的 Markdown 文件，提取关键数据
    
    参数:
        md_path: Markdown 文件路径，如 "reports/academic/academic_report_2026-05-11.md"
    
    返回:
        dict: 包含报告元数据、统计信息和论文列表的字典
    """
    
    # 📂 读取 MD 文件内容
    with open(md_path, encoding='utf-8') as f:
        text = f.read()
    
    # ── 1️⃣ 提取报告元数据 ──
    date_match = re.search(r'\*\*生成日期\*\*:\s*(\d{4}-\d{2}-\d{2})', text)
    date = date_match.group(1) if date_match else datetime.today().strftime('%Y-%m-%d')
    
    model_match = re.search(r'\*\*分析模型\*\*:\s*(.+?)(?:\n|$)', text)
    model = model_match.group(1).strip() if model_match else 'DeepSeek'
    
    draft_model_match = re.search(r'\*\*草稿模型\*\*:\s*(.+?)(?:\n|$)', text)
    draft_model = draft_model_match.group(1).strip() if draft_model_match else 'DeepSeek'
    
    total_match = re.search(r'\*\*分析条目数\*\*:\s*(\d+)', text)
    total_count = total_match.group(1) if total_match else '0'
    
    # 提取统计数字
    high_match = re.search(r'高相关.*?\*\*(\d+)\*\*', text)
    med_match = re.search(r'中相关.*?\*\*(\d+)\*\*', text)
    high_n = high_match.group(1) if high_match else '0'
    med_n = med_match.group(1) if med_match else '0'
    
    # ── 2️⃣ 提取"高相关论文"区块 ──
    papers = []
    
    # 正则说明：匹配 "## ⭐ 高相关论文" 标题后的内容，直到遇到下一个 ## 或文件结尾
    high_section = re.search(
        r'## ⭐ 高相关论文.*?\n(.*?)(?=\n## |\Z)', 
        text, 
        re.DOTALL  # 让 . 也能匹配换行符，跨行捕获
    )
    
    if high_section:
        content = high_section.group(1).strip()
        # 按 "### 数字. " 分割每篇论文
        blocks = re.split(r'\n###\s+\d+\.\s*', '\n' + content)
        
        for block in blocks[1:]:  # 跳过第一个空元素
            block = block.strip()
            if not block:
                continue
                
            lines = block.split('\n')
            title = lines[0].strip() if lines else 'Untitled'
            
            # 📌 通用字段解析器：匹配所有 "- **字段名**: 值" 格式
            fields = {}
            for line in lines[1:]:
                # 匹配：- **任意文字**: 任意内容
                m = re.match(r'-\s*\*\*(.*?)\*\*:\s*(.*)', line)
                if m:
                    key = m.group(1).strip()
                    val = m.group(2).strip()
                    fields[key] = val
            
            # 🔗 特殊处理：链接可能是 Markdown 格式 [text](url)
            link_raw = fields.get('链接', '')
            link_url = link_raw
            if link_raw.startswith('[') and '](' in link_raw:
                url_match = re.search(r'\]\(([^)]+)\)', link_raw)
                if url_match:
                    link_url = url_match.group(1)
            
            # 📝 特殊处理：提取书稿草稿（> 开头的引用块）
            draft_text = ''
            draft_match = re.search(r'✍️.*?草稿.*?\n>\s*(.+?)(?=\n\n|\n###|\Z)', block, re.DOTALL)
            if draft_match:
                draft_text = draft_match.group(1).strip()
            
            # 📊 提取模型评分（如果有表格）
            model_scores_html = ''
            if '🧠 模型评分:' in block:
                # 简化处理：提取表格内容转为纯文本列表
                score_lines = re.findall(r'\|\s*(.*?)\s*\|\s*(.*?)\s*\|', block)
                if score_lines:
                    scores_html = ''.join(
                        f'<span class="model-tag">{name.strip()}: {score.strip()}/10</span>' 
                        for name, score in score_lines if '模型' not in name
                    )
                    model_scores_html = f'<div class="card-model-scores">🧠 {scores_html}</div>'
            
            # ✅ 构建论文字典（所有字段提供默认值，防止 KeyError）
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
    
    # ── 3️⃣ 提取"立即更新清单" ──
    urgent_items = []
    urgent_section = re.search(
        r'## 🚨 立即更新清单.*?\n(.*?)(?=\n## |\Z)', 
        text, 
        re.DOTALL
    )
    if urgent_section:
        for line in urgent_section.group(1).strip().split('\n'):
            if line.strip().startswith('- [ ]'):
                # 提取章节和标题
                chap_match = re.search(r'\*\*([^*]+)\*\*', line)
                title_match = re.search(r'—\s*(.+?)\.\.\.\s*\(', line)
                urgent_items.append({
                    'chapter': chap_match.group(1) if chap_match else '待定',
                    'title': title_match.group(1) if title_match else line.strip()[:60]
                })
    
    # ── 4️⃣ 返回结构化数据 ──
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


# ──────────────────────────────────────────────────────────────
# 🎨 函数2：CSS 样式模板（学术版微调）
# ──────────────────────────────────────────────────────────────

CSS_TEMPLATE = """
    <style>
      :root {
        --bg: #f8f9fc; --bg2: #ffffff; --surface: #f0f2f8;
        --card: #ffffff; --border: #e0e2ec; --border-bright: #c0c2d0;
        --text: #2a2a40; --text-muted: #6a6a80; --text-faint: #a0a0b8;
        --accent: #e8503a; --accent-dim: rgba(232,80,58,0.08);
        --accent2: #b88c2a; --accent3: #3a7fbf; --accent3-dim: rgba(74,143,207,0.08);
        --white: #2a2a40;
        --mono: 'Space Mono', 'Courier New', monospace;
        --serif: 'Crimson Pro', Georgia, serif;
        --display: 'Bebas Neue', 'Arial Narrow', sans-serif;
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
      body {
        font-family: var(--serif); background: var(--bg); color: var(--text);
        line-height: 1.8; -webkit-font-smoothing: antialiased;
        transition: background-color 0.3s ease, color 0.3s ease;
      }
      nav {
        position: fixed; top: 0; width: 100%; z-index: 200;
        background: rgba(248,249,252,0.92); backdrop-filter: blur(24px);
        border-bottom: 1px solid var(--border); height: 56px;
        display: flex; align-items: center; justify-content: space-between;
        padding: 0 32px; font-family: var(--mono);
        transition: background-color 0.3s ease, border-color 0.3s ease;
      }
      .dark-theme nav { background: rgba(8,8,14,0.92); }
      .nav-brand {
        font-size: 0.75rem; font-weight: 700; color: var(--accent);
        letter-spacing: 3px; text-transform: uppercase;
        text-decoration: none; transition: color 0.2s;
      }
      .nav-brand:hover { color: var(--accent2); }
      .nav-right { display: flex; gap: 12px; align-items: center; }
      .theme-toggle {
        background: none; border: 1px solid var(--border);
        color: var(--text-muted); width: 36px; height: 36px;
        border-radius: 0; cursor: pointer; display: flex;
        align-items: center; justify-content: center; transition: all 0.2s;
      }
      .theme-toggle:hover { border-color: var(--accent); color: var(--accent); background: var(--accent-dim); }
      .theme-toggle i { font-size: 0.8rem; }
      .main { max-width: 860px; margin: 0 auto; padding: 70px 32px 60px; }
      .back-link {
        font-family: var(--mono); font-size: 0.65rem; letter-spacing: 2px;
        color: var(--text-muted); text-decoration: none; text-transform: uppercase;
        border: 1px solid var(--border); padding: 6px 14px; display: inline-block;
        margin-bottom: 10px; transition: all .2s;
      }
      .back-link:hover { border-color: var(--accent); color: var(--accent); }
      .page-eyebrow {
        font-family: var(--mono); font-size: 0.62rem; letter-spacing: 4px;
        color: var(--accent); text-transform: uppercase; margin-bottom: 8px;
        display: flex; align-items: center; gap: 10px;
      }
      .page-eyebrow::before { content: ''; width: 28px; height: 1px; background: var(--accent); }
      .page-title {
        font-family: var(--display); font-size: 3rem; letter-spacing: 2px;
        color: var(--white); margin-bottom: 6px; line-height: 1;
      }
      .page-sub {
        font-family: var(--mono); font-size: 0.65rem; color: var(--text-muted);
        letter-spacing: 1.5px; margin-bottom: 16px;
      }
      .stats-row {
        display: flex; gap: 24px; margin-bottom: 10px;
        font-family: var(--mono); font-size: 0.65rem; color: var(--text-muted);
        letter-spacing: 1px; flex-wrap: wrap;
      }
      .stats-row span { color: var(--accent); font-weight: 700; }
      .urgent-box {
        background: var(--accent-dim); border: 1px solid var(--accent);
        padding: 20px 24px; margin-bottom: 32px; border-left: 4px solid var(--accent);
      }
      .urgent-title {
        font-family: var(--mono); font-size: 0.6rem; letter-spacing: 2px;
        color: var(--accent); text-transform: uppercase; margin-bottom: 12px;
      }
      .urgent-item {
        font-size: 0.55rem; margin-bottom: 8px; padding-left: 16px;
        border-left: 2px solid var(--border);
      }
      .urgent-item strong { color: var(--white); }
      .card {
        background: var(--card); border: 1px solid var(--border);
        padding: 28px; margin-bottom: 16px; transition: border-color .2s, background 0.2s;
      }
      .card:hover { border-color: var(--accent); }
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
      }
      .card-score span {
        font-family: var(--mono); font-size: 0.5rem; color: var(--text-muted);
        display: block; letter-spacing: 1px; margin-top: 4px;
      }
      .card-meta {
        font-family: var(--mono); font-size: 0.6rem; color: var(--text-faint);
        letter-spacing: 0.5px; margin-bottom: 14px; display: flex;
        gap: 12px; flex-wrap: wrap; align-items: center;
      }
      .card-meta a { color: var(--accent2); text-decoration: none; }
      .card-meta a:hover { text-decoration: underline; }
      .card-authors { color: var(--text-muted); font-style: italic; }
      .card-pub { background: var(--surface); padding: 2px 6px; border-radius: 2px; }
      .card-body {
        font-size: 0.70rem; color: var(--text-muted); line-height: 1.8; margin-bottom: 12px;
      }
      .card-implications {
        font-family: var(--mono); font-size: 0.68rem; color: var(--accent2);
        padding: 10px 14px; background: rgba(201,160,64,0.05);
        border-left: 2px solid var(--accent2); margin-bottom: 12px;
      }
      .card-model-scores {
        font-family: var(--mono); font-size: 0.58rem; color: var(--text-faint);
        margin-bottom: 12px; display: flex; gap: 8px; flex-wrap: wrap;
      }
      .model-tag { background: var(--surface); padding: 2px 6px; border-radius: 2px; }
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
      .card-footer .tag { padding: 2px 6px; background: var(--surface); border-radius: 2px; }
      footer {
        margin-top: 48px; padding-top: 24px; border-top: 1px solid var(--border);
        font-family: var(--mono); font-size: 0.6rem; color: var(--text-muted);
        letter-spacing: 1px; display: flex; justify-content: space-between; flex-wrap: wrap; gap: 8px;
      }
      footer a { color: var(--text-muted); text-decoration: none; }
      footer a:hover { color: var(--accent); }
      @media (max-width: 600px) {
        .main { padding: 100px 16px 40px; }
        .page-title { font-size: 2.2rem; }
        .card-header { flex-direction: column; }
        .card-score { text-align: left; margin-top: 8px; }
      }
    </style>"""


# ──────────────────────────────────────────────────────────────
# 🏗️ 函数3：生成学术版 HTML 页面
# ──────────────────────────────────────────────────────────────

def generate_academic_html(data: dict, output_path: str):
    """
    根据解析的学术数据生成完整 HTML
    
    参数:
        data: parse_academic_report() 返回的字典
        output_path: 输出 HTML 文件路径
    """
    
    # ── 1️⃣ 生成紧急清单 ──
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
    
    # ── 2️⃣ 生成论文卡片 ──
    papers_html = ''
    for p in data['papers']:
        # 📊 分数处理
        try:
            score_num = float(p['score'])
            score_display = f'{score_num:.1f}'
        except (ValueError, TypeError):
            score_display = p['score'] if p['score'] else '—'
        
        # 🔗 链接处理
        link_html = ''
        if p['link'] and p['link'] not in ('N/A', '#', ''):
            link_html = f'<a href="{p["link"]}" target="_blank" rel="noopener">↗ PDF/原文</a>'
        
        # 📝 作者与日期标签
        meta_tags = []
        if p['authors'] and p['authors'] != 'N/A':
            meta_tags.append(f'<span class="card-authors">👤 {p["authors"]}</span>')
        if p['published'] and p['published'] != 'N/A':
            meta_tags.append(f'<span class="card-pub">📅 {p["published"][:10]}</span>')
        
        # 🏷️ 底部状态标签
        tags = []
        for key, icon in [('urgency', '⏱'), ('update_type', '🔄'), ('action', '✅')]:
            val = p.get(key, '')
            if val and val not in ('N/A', '—', ''):
                tags.append(f'<span class="tag">{icon} {val}</span>')
        tags_html = ''.join(tags) if tags else ''
        
        # 📜 草稿区块
        draft_html = ''
        if p['draft'] and len(p['draft']) > 30:
            draft_html = f'\n      <div class="card-draft">{p["draft"]}</div>'
        
        # 🧠 模型评分
        model_html = p.get('model_scores', '')
        
        # 💡 理论关联
        imp_html = ''
        if p['implications'] and p['implications'] != 'N/A':
            imp_html = f'\n      <div class="card-implications">{p["implications"]}</div>'
        
        # 🧱 拼接卡片
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
    
    # ── 3️⃣ 拼接完整 HTML ──
    html = f'''<!DOCTYPE html>
<html lang="zh-CN" class="no-js">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Academic Radar · {data['date']} | Renegade AI</title>
  <meta name="description" content="学术论文监控报告 · {data['high_n']} 高相关论文">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Space+Mono:ital,wght@0,400;0,700;1,400&family=Crimson+Pro:ital,wght@0,300;0,400;0,600;1,300;1,400&family=Bebas+Neue&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css">
{CSS_TEMPLATE}
</head>
<body>
  <nav>
    <a href="https://github.com/Brook-Han/renegade-ai-Updater" class="nav-brand">RENEGADE RADAR</a>
    <div class="nav-right">
      <button class="theme-toggle" id="themeToggle" aria-label="切换主题">
        <i class="fa fa-sun-o" id="themeIcon"></i>
      </button>
    </div>
  </nav>

  <main class="main">
    <a href="index.html" class="back-link">← 返回主页</a>
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
    
    <footer>
      <span>Renegade AI v5.3 · Brooks Han</span>
      <a href="https://brook-han.github.io/Renegade-AI/" target="_blank" rel="noopener">GitHub ↗</a>
    </footer>
  </main>

  <script>
    (function() {{
      const html = document.documentElement;
      const toggle = document.getElementById('themeToggle');
      const icon = document.getElementById('themeIcon');
      const KEY = 'renegade-theme';
      const apply = (theme) => {{
        html.classList.toggle('dark-theme', theme === 'dark');
        icon.className = theme === 'dark' ? 'fa fa-moon-o' : 'fa fa-sun-o';
        localStorage.setItem(KEY, theme);
      }};
      const pref = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
      apply(localStorage.getItem(KEY) || pref);
      toggle?.addEventListener('click', () => apply(html.classList.contains('dark-theme') ? 'light' : 'dark'));
    }})();
  </script>
</body>
</html>'''
    
    # ── 4️⃣ 写入文件 ──
    Path(output_path).write_text(html, encoding='utf-8')
    print(f'✅ HTML 已生成: {output_path}')


# ──────────────────────────────────────────────────────────────
# 🚀 主入口
# ──────────────────────────────────────────────────────────────

if __name__ == '__main__':
    # ── 1️⃣ 确定输入文件 ──
    if len(sys.argv) > 1:
        md_file = sys.argv[1]
        print(f'📄 使用指定文件: {md_file}')
    else:
        # 自动查找最新学术报告
        for search_dir in [Path('reports/academic'), Path('output/academic'), Path('reports')]:
            if search_dir.exists():
                reports = sorted(search_dir.glob('academic_report_*.md'))
                if reports:
                    md_file = str(reports[-1])
                    break
        else:
            print('❌ 未找到 academic_report_*.md 文件')
            print('💡 用法: python academic_md_to_html.py path/to/report.md')
            sys.exit(1)
        print(f'🔍 自动选择最新报告: {md_file}')
    
    # ── 2️⃣ 解析与生成 ──
    print(f'📖 解析中...')
    data = parse_academic_report(md_file)
    
    if not data['papers']:
        print('⚠️ 警告: 未解析到高相关论文')
        print(f'   统计: 总计 {data["total"]} 篇 | 高相关 {data["high_n"]} 篇')
        print('💡 请检查 MD 文件是否由 academic_radar.py 生成，且包含 "## ⭐ 高相关论文" 区块')
    
    out_file = str(Path(md_file).with_suffix('.html'))
    generate_academic_html(data, out_file)
    
    print('🎉 转换完成！双击打开预览：')
    print(f'   file://{Path(out_file).resolve()}')