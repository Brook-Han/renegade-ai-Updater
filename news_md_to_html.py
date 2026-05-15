#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📰 News Radar MD → HTML 转换器（完整注释版）

功能：将 news_radar.py 生成的 Markdown 报告转换为漂亮的网页
风格：与 Renegade AI 官网一致，支持浅色/深色主题切换

📋 用法：
    # 方式1：转换指定文件
    python news_md_to_html.py docs/news/news_report_2026-05-11.md
    
    # 方式2：自动找最新报告（推荐）
    python news_md_to_html.py

🔧 输出：同目录下生成 .html 文件，可直接用浏览器打开

作者：Brooks Han
版本：v1.1 (2026-05-11)
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
    
    参数:
        md_path: Markdown 文件路径，如 "docs/news/news_report_2026-05-11.md"
    
    返回:
        dict: 包含报告元数据和高价值案例的字典
    """
    
    # 📂 读取 MD 文件内容
    with open(md_path, encoding='utf-8') as f:
        text = f.read()
    
    # ── 1️⃣ 提取报告元数据 ──
    
    # 提取生成日期：匹配 "**生成日期**: 2026-05-11" 格式
    date_match = re.search(r'\*\*生成日期\*\*:\s*(\d{4}-\d{2}-\d{2})', text)
    date = date_match.group(1) if date_match else datetime.today().strftime('%Y-%m-%d')
    
    # 提取分析模型名称
    model_match = re.search(r'\*\*分析模型\*\*:\s*(.+?)(?:\n|$)', text)
    model = model_match.group(1).strip() if model_match else 'DeepSeek'
    
    # 提取统计数字（总条目数、高/中相关数量）
    total_match = re.search(r'\*\*分析条目\*\*:\s*(\d+)', text)
    total_count = total_match.group(1) if total_match else '0'
    
    high_match = re.search(r'高价值.*?\*\*(\d+)\*\*', text)
    med_match = re.search(r'中相关.*?\*\*(\d+)\*\*', text)
    high_n = high_match.group(1) if high_match else '0'
    med_n = med_match.group(1) if med_match else '0'
    
    # ── 2️⃣ 提取"高价值案例"区块 ──
    
    items = []  # 存储所有解析出的案例
    
    # 正则说明：
    # ## ⭐ 高价值案例.*?\n   → 匹配标题行
    # (.*?)                   → 捕获标题后的内容（非贪婪）
    # (?=\n## |<details|---|\Z) → 向前看：遇到下一个##标题、<details、分割线或文件结尾就停止
    high_section = re.search(
        r'## ⭐ 高价值案例.*?\n(.*?)(?=\n## |<details|---|\Z)', 
        text, 
        re.DOTALL  # 让 . 也能匹配换行符
    )
    
    if high_section:
        content = high_section.group(1).strip()
        
        # 按 "### 数字. " 分割每个案例（如 "### 1. 标题"）
        # 第一个元素是空字符串，所以从 [1:] 开始
        blocks = re.split(r'\n###\s+\d+\.\s*', '\n' + content)
        
        for block in blocks[1:]:  # 跳过第一个空块
            block = block.strip()
            if not block:  # 跳过空块
                continue
            
            lines = block.split('\n')  # 按行分割
            
            # 📌 第一行是案例标题
            title = lines[0].strip() if lines else 'Untitled'
            
            # 📌 解析标题下方的字段（格式：- **字段名**: 值）
            fields = {}
            for line in lines[1:]:
                line = line.strip()
                
                # 定义 MD 中的字段名 → 内部使用的键名 映射表
                for md_key, field_key in [
                    ('来源', 'source'),
                    ('相关度', 'score'),
                    ('案例价值', 'case_value'),
                    ('紧迫度', 'urgency'),
                    ('更新类型', 'update_type'),  # ✅ 修复：确保包含此字段
                    ('目标章节', 'chapter'),
                    ('事件摘要', 'summary'),
                    ('理论关联', 'implications'),
                    ('建议操作', 'action'),
                    ('链接', 'link')
                ]:
                    # 构建正则：匹配 "- **字段名**: 值"
                    pattern = rf'-\s*\*\*{md_key}\*\*:\s*(.*)'
                    match = re.search(pattern, line)
                    if match:
                        fields[field_key] = match.group(1).strip()
                        break  # 找到就跳出，避免重复匹配
            
            # 🔗 特殊处理：链接可能是 [文本](url) 格式，需要提取 url
            if 'link' in fields and fields['link'].startswith('['):
                url_match = re.search(r'\]\(([^)]+)\)', fields['link'])
                if url_match:
                    fields['link'] = url_match.group(1)  # 只保留 URL 部分
            
            # 📊 特殊处理：相关度 "8/10" → 只取数字 "8"
            if 'score' in fields:
                score_match = re.search(r'(\d+(?:\.\d+)?)/10', fields['score'])
                if score_match:
                    fields['score'] = score_match.group(1)
            
            # ✅ 构建案例字典（所有字段都用 .get() 提供默认值，避免 KeyError）
            items.append({
                'title': title,
                'source': fields.get('source', ''),
                'score': fields.get('score', '—'),
                'case_value': fields.get('case_value', '').upper(),
                'urgency': fields.get('urgency', ''),
                'update_type': fields.get('update_type', ''),  # ✅ 关键修复：添加此字段
                'chapter': fields.get('chapter', ''),
                'summary': fields.get('summary', ''),
                'implications': fields.get('implications', ''),
                'action': fields.get('action', ''),
                'link': fields.get('link', ''),
            })
    
    # ── 3️⃣ 提取"紧急关注清单"（可选）─
    # 格式：每组以 `- [ ]` 开头，紧跟 `📌` 标题行
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
                # 保存上一个，开始新的紧急条目
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
    
    # ── 4️⃣ 返回解析结果 ──
    return {
        'date': date,              # 报告日期
        'model': model,            # 分析模型名称
        'total': total_count,      # 总分析条目数
        'high_n': high_n,          # 高价值案例数
        'med_n': med_n,            # 中相关案例数
        'items': items,            # 高价值案例列表
        'urgent': urgent_items,    # 紧急清单
    }


# ──────────────────────────────────────────────────────────────
# 🎨 函数2：CSS 样式模板（浅色 + 深色双主题）
# ──────────────────────────────────────────────────────────────

CSS_TEMPLATE = """
    <style>
      /* ========== 颜色变量定义（浅色模式默认）========== */
      :root {
        --bg: #08080e;
        --bg2: #0d0d18;
        --surface: #111120;
        --card: #13131f;
        --border: #1e1e30;
        --border-bright: #2e2e50;
        --text: #cccce0;
        --text-muted: #6868a0;
        --text-faint: #3a3a5a;
        --accent: #e8503a;
        --accent-dim: rgba(232,80,58,0.12);
        --accent2: #c9a040;
        --accent3: #4a8fcf;
        --accent3-dim: rgba(74,143,207,0.10);
        --white: #f0f0f8;
        --mono: 'Space Mono', 'Courier New', monospace;
        --serif: 'Crimson Pro', Georgia, serif;
        --display: 'Bebas Neue', 'Arial Narrow', sans-serif;
      }
      :root.light {
        --bg: #f8f9fc; --bg2: #fff; --surface: #f0f2f8; --card: #fff;
        --border: #e0e2ec; --border-bright: #c0c2d0;
        --text: #2a2a40; --text-muted: #6a6a80; --text-faint: #a0a0b8;
        --accent-dim: rgba(232,80,58,0.08); --accent3-dim: rgba(74,143,207,0.08);
        --white: #2a2a40;
      }

      /* ========== 全局重置 ========== */
      * { box-sizing: border-box; margin: 0; padding: 0; }

      body {
        font-family: var(--serif);
        background: var(--bg);
        color: var(--text);
        line-height: 1.8;
        -webkit-font-smoothing: antialiased;  /* 字体平滑 */
        transition: background-color 0.3s ease, color 0.3s ease;  /* 主题切换动画 */
      }

      /* ========== 顶部导航栏（固定定位）========== */
      nav {
        position: fixed; top: 0; width: 100%; z-index: 200;
        background: rgba(8,8,14,.92); backdrop-filter: blur(24px);
        border-bottom: 1px solid var(--border);
        height: 56px;
        display: flex; align-items: center; justify-content: space-between;
        padding: 0 32px;
        font-family: var(--mono);
        transition: background-color 0.3s ease, border-color 0.3s ease;
      }
      .light nav { background: rgba(248,249,252,.92); }
      
      .nav-brand {
        font-size: 0.75rem; font-weight: 700;
        color: var(--accent); letter-spacing: 3px;
        text-transform: uppercase; text-decoration: none;
        transition: color 0.2s;
      }
      .nav-brand:hover { color: var(--accent2); }
      
      .nav-right { display: flex; gap: 8px; align-items: center; }

      .nav-pill {
        background: none; border: 1px solid var(--border); color: var(--text-muted);
        font-family: var(--mono); font-size: .62rem; letter-spacing: 2px;
        padding: 5px 14px; cursor: pointer; text-decoration: none;
        display: inline-flex; align-items: center; transition: all .2s;
      }
      .nav-pill:hover { border-color: var(--accent); color: var(--accent); background: var(--accent-dim); }

      .theme-btn {
        background: none; border: 1px solid var(--border); color: var(--text-muted);
        width: 36px; height: 36px; cursor: pointer; display: flex; align-items: center; justify-content: center;
        font-size: .9rem; transition: all .2s;
      }
      .theme-btn:hover { border-color: var(--accent); color: var(--accent); background: var(--accent-dim); }

      /* ========== 主内容区 ========== */
      .main {
        max-width: 860px; margin: 0 auto;
        padding: 70px 32px 60px;  /* 顶部留白避开固定导航栏 */
      }

      /* 返回链接 */
      .back-link {
        font-family: var(--mono); font-size: 0.65rem;
        letter-spacing: 2px; color: var(--text-muted);
        text-decoration: none; text-transform: uppercase;
        border: 1px solid var(--border); padding: 6px 14px;
        display: inline-block; margin-bottom: 10px;
        transition: all .2s;
      }
      .back-link:hover { border-color: var(--accent); color: var(--accent); }

      /* 页面标题区域 */
      .page-eyebrow {
        font-family: var(--mono); font-size: 0.62rem;
        letter-spacing: 4px; color: var(--accent);
        text-transform: uppercase; margin-bottom: 8px;
        display: flex; align-items: center; gap: 10px;
      }
      .page-eyebrow::before {
        content: ''; width: 28px; height: 1px; background: var(--accent);
      }
      .page-title {
        font-family: var(--display); font-size: 3rem;
        letter-spacing: 2px; color: var(--white);
        margin-bottom: 6px; line-height: 1;
      }
      .page-sub {
        font-family: var(--mono); font-size: 0.65rem;
        color: var(--text-muted); letter-spacing: 1.5px;
        margin-bottom: 16px;
      }

      /* 统计行 */
      .stats-row {
        display: flex; gap: 24px; margin-bottom: 10px;
        font-family: var(--mono); font-size: 0.6rem;
        color: var(--text-muted); letter-spacing: 0px;
        flex-wrap: wrap;
      }
      .stats-row span { color: var(--accent); font-weight: 700; }
      
      /* ========== 紧急清单盒子 ========== */
      .urgent-box {
        background: var(--accent-dim); border: 1px solid var(--accent);
        padding: 20px 24px; margin-bottom: 32px;
        border-left: 4px solid var(--accent);
      }
      .urgent-title {
        font-family: var(--mono); font-size: 0.6rem;
        letter-spacing: 2px; color: var(--accent);
        text-transform: uppercase; margin-bottom: 12px;
        display: flex; align-items: center; gap: 8px;
      }
      .urgent-item {
        font-size: 0.55rem; margin-bottom: 8px;
        padding-left: 16px; border-left: 2px solid var(--border);
      }
      .urgent-item strong { color: var(--white); }
      .urgent-item a { color: var(--accent2); text-decoration: none; }
      .urgent-item a:hover { text-decoration: underline; }
      .urgent-type-tag {
        font-family: var(--mono); font-size: 0.5rem; letter-spacing: 1px;
        color: var(--accent); background: var(--accent-dim);
        padding: 1px 5px; margin-left: 6px; text-transform: uppercase;
      }
      
      /* ========== 案例卡片 ========== */
      .card {
        background: var(--card); border: 1px solid var(--border);
        padding: 28px; margin-bottom: 16px;
        transition: border-color .2s, background 0.2s;
      }
      .card:hover { border-color: var(--accent); }  /* 悬停高亮 */
      
      .card-header {
        display: flex; justify-content: space-between;
        align-items: flex-start; margin-bottom: 14px; gap: 16px;
      }
      .card-title {
        font-family: var(--display); font-size: 1.3rem;
        letter-spacing: 0.5px; color: var(--white);
        line-height: 1.3; flex: 1;
      }
      .card-score {
        font-family: var(--display); font-size: 2rem;
        color: var(--accent); line-height: 1;
        white-space: nowrap; text-align: right;
      }
      .card-score span {
        font-family: var(--mono); font-size: 0.5rem;
        color: var(--text-muted); display: block;
        letter-spacing: 1px; margin-top: 4px;
      }
      
      /* 案例价值徽章 */
      .card-badge {
        display: inline-block; padding: 2px 8px;
        font-family: var(--mono); font-size: 0.55rem;
        letter-spacing: 1px; text-transform: uppercase;
        background: var(--accent3-dim); color: var(--accent3);
        border: 1px solid var(--accent3); margin-left: 8px;
      }
      .card-badge.high {
        background: var(--accent-dim); color: var(--accent);
        border-color: var(--accent);
      }
      
      /* 卡片元信息行 */
      .card-meta {
        font-family: var(--mono); font-size: 0.6rem;
        color: var(--text-faint); letter-spacing: 0.5px;
        margin-bottom: 12px; display: flex;
        gap: 16px; flex-wrap: wrap; align-items: center;
      }
      .card-meta a { color: var(--accent2); text-decoration: none; }
      .card-meta a:hover { text-decoration: underline; }
      
      .card-body {
        font-size: 0.70rem; color: var(--text-muted);
        line-height: 1.8; margin-bottom: 12px;
      }
      
      /* 理论关联引用块 */
      .card-implications {
        font-family: var(--mono); font-size: 0.68rem;
        color: var(--accent2); padding: 10px 14px;
        background: rgba(201,160,64,0.05);
        border-left: 2px solid var(--accent2);
        letter-spacing: 0.3px; margin-bottom: 12px;
      }
      
      /* 卡片底部标签 */
      .card-footer {
        display: flex; gap: 12px; flex-wrap: wrap;
        font-family: var(--mono); font-size: 0.58rem;
        color: var(--text-faint); letter-spacing: 0.5px;
        padding-top: 12px; border-top: 1px dashed var(--border);
      }
      .card-footer .tag {
        padding: 2px 6px; background: var(--surface);
        border-radius: 2px; color: var(--text-muted);
      }
      
      /* ========== 折叠区域（中相关资讯）========== */
      details {
        margin: 32px 0; border: 1px solid var(--border);
        background: var(--card); border-radius: 0;
      }
      summary {
        padding: 14px 20px; cursor: pointer;
        font-family: var(--mono); font-size: 0.65rem;
        letter-spacing: 1px; color: var(--text-muted);
        background: var(--surface); user-select: none;
        display: flex; align-items: center; gap: 8px;
      }
      summary:hover { color: var(--accent); }
      details[open] summary { border-bottom: 1px solid var(--border); }
      .collapsed-list { padding: 16px 20px; }
      .collapsed-list li {
        margin-bottom: 10px; font-size: 0.9rem;
        color: var(--text-muted);
      }
      .collapsed-list a { color: var(--text); text-decoration: none; }
      .collapsed-list a:hover { color: var(--accent); text-decoration: underline; }
      
      /* ========== 页脚 ========== */
      footer {
        margin-top: 48px; padding-top: 24px;
        border-top: 1px solid var(--border);
        font-family: var(--mono); font-size: 0.6rem;
        color: var(--text-muted); letter-spacing: 1px;
        display: flex; justify-content: space-between;
      }
      footer a { color: var(--text-muted); text-decoration: none; }
      footer a:hover { color: var(--accent); }
      
      /* ========== 移动端适配 ========== */
      @media (max-width: 600px) {
        .main { padding: 70px 16px 40px; } /* 修正顶部内边距过大问题 */
        .page-title { font-size: 2.2rem; }
        .card-header { flex-direction: column; }
        .card-score { text-align: left; }
        
        /* 移除stats-row的垂直排列，改为水平滚动 */
        .stats-row { 
          flex-direction: row; 
          gap: 16px; 
          overflow-x: auto; /* 允许水平滚动 */
          padding-bottom: 4px;
          -webkit-overflow-scrolling: touch; /* 平滑滚动 */
          scrollbar-width: none; /* 隐藏滚动条 */
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
    </style>"""


# ──────────────────────────────────────────────────────────────
# 🏗️ 函数3：生成 HTML 页面
# ──────────────────────────────────────────────────────────────

def generate_news_html(data: dict, output_path: str):
    """
    根据解析的数据生成完整的 HTML 页面
    
    参数:
        data: parse_news_report() 返回的字典
        output_path: 输出 HTML 文件路径
    """
    
    # ── 1️⃣ 生成紧急清单 HTML ──
    urgent_html = ''
    if data['urgent']:  # 如果有紧急项
        parts = []
        for u in data['urgent']:
            chapter = escape(u.get('chapter', ''))
            title = escape(u.get('title', ''))
            update_type = escape(u.get('update_type', ''))
            type_tag = f' <span class="urgent-type-tag">{update_type}</span>' if update_type else ''
            title_part = f' — {title}' if title else ''
            parts.append(
                f'<div class="urgent-item">• <strong>{chapter}</strong>{title_part}{type_tag}</div>'
            )
        urgent_items = ''.join(parts)
        urgent_html = f'''
    <div class="urgent-box">
      <div class="urgent-title">🚨 紧急关注</div>
      {urgent_items}
    </div>'''
    
    # ── 2️⃣ 生成高价值案例卡片 ──
    items_html = ''
    for it in data['items']:
        # 📊 分数格式化：确保显示为 "8.0" 格式
        try:
            score_num = float(it['score'])
            score_display = f'{score_num:.1f}'
        except (ValueError, TypeError):
            score_display = it['score'] if it['score'] else '—'
        
        # 🏷️ 案例价值徽章（HIGH 用红色，其他用蓝色）
        case_badge = ''
        case_val = it.get('case_value', '')  # ✅ 安全访问
        if case_val and case_val != 'N/A':
            badge_class = 'high' if case_val.lower() == 'high' else ''
            case_badge = f'<span class="card-badge {badge_class}">{case_val}</span>'
        
        # 🔗 链接处理：只在实际有链接时显示
        link_html = ''
        link_val = it.get('link', '')
        if link_val and link_val not in ('N/A', '#', ''):
            link_html = f'<a href="{link_val}" target="_blank" rel="noopener">↗ 原文</a>'
        
        # 📍 章节标记
        chapter_html = ''
        chapter_val = it.get('chapter', '')
        if chapter_val and chapter_val != 'N/A':
            chapter_html = f'📍 {chapter_val}'
        
        # 💡 理论关联引用块
        implications_html = ''
        imp_val = it.get('implications', '')
        if imp_val and imp_val != 'N/A':
            implications_html = f'\n      <div class="card-implications">{imp_val}</div>'
        
        # 🏷️ 底部标签（紧迫度/更新类型/建议操作）
        tags = []
        urgency = it.get('urgency', '')      # ✅ 安全访问，避免 KeyError
        update_type = it.get('update_type', '')  # ✅ 关键修复
        action = it.get('action', '')
        
        if urgency and urgency not in ('N/A', '—', ''):
            tags.append(f'<span class="tag">⏱ {urgency}</span>')
        if update_type and update_type not in ('N/A', '—', ''):
            tags.append(f'<span class="tag">🔄 {update_type}</span>')
        if action and action not in ('N/A', '—', ''):
            tags.append(f'<span class="tag">✅ {action}</span>')
        tags_html = ''.join(tags) if tags else ''
        
        # 🧱 拼接单个案例卡片 HTML
        items_html += f'''
    <div class="card">
      <div class="card-header">
        <div class="card-title">{it["title"]}{case_badge}</div>
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
    </div>'''
    
    # ── 3️⃣ 拼接完整 HTML 文档 ──
    html = f'''<!DOCTYPE html>
<html lang="zh-CN" class="no-js">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>News Radar · {data['date']} | Renegade AI</title>
  <meta name="description" content="AI 资讯监控报告 · {data['high_n']} 高价值案例">
  
  <!-- 加载字体（谷歌字体）-->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Space+Mono:ital,wght@0,400;0,700;1,400&family=Crimson+Pro:ital,wght@0,300;0,400;0,600;1,300;1,400&family=Bebas+Neue&display=swap" rel="stylesheet">
  
  <!-- Font Awesome 图标 -->
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css">
  
  <!-- 嵌入 CSS 样式 -->
{CSS_TEMPLATE}
</head>
<body>
  <!-- 顶部导航栏 -->
  <nav>
    <a href="https://brook-han.github.io/Renegade-AI/" class="nav-brand">RENEGADE AI v5.3</a>
    <div class="nav-right">
      <a href="../index.html" class="nav-pill">HOME</a>
      <a href="index.html" class="nav-pill">NEWS</a>
      <a href="../academic/" class="nav-pill">PAPERS</a>
      <button class="theme-btn" id="themeBtn" aria-label="Toggle theme">◐</button>
    </div>
  </nav>

  <!-- 主内容区 -->
  <main class="main">
    <div class="page-eyebrow">§ News Radar</div>
    <h1 class="page-title">DAILY INTELLIGENCE</h1>
    <p class="page-sub">{data['date']} · Model: {data['model']}</p>
    
    <!-- 统计行 -->
    <div class="stats-row">
      <div>📊 总条目: <span>{data['total']}</span></div>
      <div>🔴 高价值: <span>{data['high_n']}</span></div>
      <div>🟡 中相关: <span>{data['med_n']}</span></div>
    </div>
    
    <!-- 紧急清单 + 案例卡片 -->
    {urgent_html}
    {items_html}
    
    <!-- 页脚 -->
    <footer>
      <span>Renegade AI v5.3 · Brooks Han</span>
      <a href="https://brook-han.github.io/Renegade-AI/" target="_blank" rel="noopener">GitHub ↗</a>
    </footer>
  </main>

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
    
    # ── 4️⃣ 写入文件 ──
    Path(output_path).write_text(html, encoding='utf-8')
    print(f'✅ HTML 已生成: {output_path}')


# ──────────────────────────────────────────────────────────────
# 🚀 主入口：程序从这里开始执行
# ──────────────────────────────────────────────────────────────

if __name__ == '__main__':
    """
    命令行入口点
    支持两种调用方式：
      1. python news_md_to_html.py 路径/到/报告.md
      2. python news_md_to_html.py  （自动找最新报告）
    """
    
    # ── 1️⃣ 确定要处理的 MD 文件 ──
    if len(sys.argv) > 1:
        # 用户指定了文件路径
        md_file = sys.argv[1]
        print(f'📄 使用指定文件: {md_file}')
    else:
        # 自动查找：优先 docs/，备选 output/news/
        reports_dir = Path('docs/news')
        if not reports_dir.exists():
            reports_dir = Path('output/news')
        
        # 查找所有 news_report_*.md 文件，按时间排序取最新
        reports = sorted(reports_dir.glob('news_report_*.md'))
        if not reports:
            print('❌ 未找到 news_report_*.md 文件')
            print('💡 用法: python news_md_to_html.py path/to/report.md')
            sys.exit(1)  # 退出程序，返回错误码
        
        md_file = str(reports[-1])
        print(f'🔍 自动选择最新报告: {md_file}')
    
    # ── 2️⃣ 解析 MD 文件 ──
    print(f'📖 解析中...')
    data = parse_news_report(md_file)
    
    # 调试提示：如果没解析到案例，可能是 MD 格式不匹配
    if not data['items']:
        print('⚠️ 警告: 未解析到高价值案例')
        print(f'   统计: 总计 {data["total"]} 条 | 高 {data["high_n"]} | 中 {data["med_n"]}')
        print('💡 请检查 MD 文件是否由 news_radar.py 生成，且包含 "## ⭐ 高价值案例" 区块')
    
    # ── 3️⃣ 确定输出路径并生成 HTML ──
    # 将 .md 后缀替换为 .html
    out_file = str(Path(md_file).with_suffix('.html'))
    generate_news_html(data, out_file)
    
    # ── 4️⃣ 完成 ──
    print('🎉 转换完成！用浏览器打开即可预览：')
    print(f'   file://{Path(out_file).resolve()}')