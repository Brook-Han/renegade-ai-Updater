#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎓 Academic Radar MD → HTML 转换器（v2.0 单卡片沉浸式布局）

功能：将 academic_radar.py 生成的 Markdown 报告转换为沉浸式单卡片网页
风格：与 Renegade AI v5.3 完全一致，每篇论文占据完整单卡片版面

📋 用法：
    python academic_md_to_html.py docs/academic/academic_report_2026-05-11.md
    python academic_md_to_html.py   # 自动选最新

作者：Brooks Han · v2.0
"""

import re
import sys
from pathlib import Path
from datetime import datetime


# ═══════════════════════════════════════════════════════════════
# 解析 Markdown
# ═══════════════════════════════════════════════════════════════

def parse_academic_report(md_path: str) -> dict:
    with open(md_path, encoding="utf-8") as f:
        text = f.read()

    date_m  = re.search(r'\*\*生成日期\*\*:\s*(\d{4}-\d{2}-\d{2})', text)
    model_m = re.search(r'\*\*分析模型\*\*:\s*(.+?)(?:\n|$)', text)
    draft_m = re.search(r'\*\*草稿模型\*\*:\s*(.+?)(?:\n|$)', text)
    total_m = re.search(r'\*\*分析条目数\*\*:\s*(\d+)', text)
    high_m  = re.search(r'高相关.*?\*\*(\d+)\*\*', text)
    med_m   = re.search(r'中相关.*?\*\*(\d+)\*\*', text)

    papers = []
    high_sec = re.search(
        r'## ⭐ 高相关论文.*?\n(.*?)(?=\n## |\Z)', text, re.DOTALL
    )
    if high_sec:
        blocks = re.split(r'\n###\s+\d+\.\s*', '\n' + high_sec.group(1).strip())
        for block in blocks[1:]:
            block = block.strip()
            if not block:
                continue
            lines  = block.split('\n')
            title  = lines[0].strip() if lines else 'Untitled'
            fields = {}
            for line in lines[1:]:
                m = re.match(r'-\s*\*\*(.*?)\*\*:\s*(.*)', line)
                if m:
                    fields[m.group(1).strip()] = m.group(2).strip()

            link_raw = fields.get('链接', '')
            link_url = link_raw
            if '[' in link_raw and '](' in link_raw:
                u = re.search(r'\]\(([^)]+)\)', link_raw)
                if u:
                    link_url = u.group(1)

            draft_text = ''
            dm = re.search(r'✍️.*?草稿.*?\n>\s*(.+?)(?=\n\n|\n###|\Z)', block, re.DOTALL)
            if dm:
                draft_text = dm.group(1).strip()

            model_scores = []
            if '🧠 模型评分:' in block:
                for name, score in re.findall(r'\|\s*(.*?)\s*\|\s*(.*?)\s*\|', block):
                    if '模型' not in name and name.strip():
                        model_scores.append((name.strip(), score.strip()))

            papers.append({
                'title':       title,
                'source':      fields.get('来源', ''),
                'authors':     fields.get('作者', ''),
                'published':   fields.get('发表', ''),
                'score':       fields.get('最终评分', '—').replace('/10', '').strip(),
                'urgency':     fields.get('紧迫度', ''),
                'update_type': fields.get('更新类型', ''),
                'chapter':     fields.get('目标章节', ''),
                'link':        link_url,
                'summary':     fields.get('核心发现', ''),
                'implications':fields.get('与本书关联', ''),
                'action':      fields.get('建议更新', ''),
                'draft':       draft_text,
                'model_scores':model_scores,
            })

    urgent = []
    urg_sec = re.search(r'## 🚨 立即更新清单.*?\n(.*?)(?=\n## |\Z)', text, re.DOTALL)
    if urg_sec:
        for line in urg_sec.group(1).strip().split('\n'):
            if line.strip().startswith('- [ ]'):
                cm = re.search(r'\*\*([^*]+)\*\*', line)
                tm = re.search(r'—\s*(.+?)\.\.\.\s*\(', line)
                urgent.append({
                    'chapter': cm.group(1) if cm else '待定',
                    'title':   tm.group(1) if tm else line.strip()[:60],
                })

    return {
        'date':       (date_m.group(1)  if date_m  else datetime.today().strftime('%Y-%m-%d')),
        'model':      (model_m.group(1).strip() if model_m else 'DeepSeek'),
        'draft_model':(draft_m.group(1).strip() if draft_m else 'DeepSeek'),
        'total':      (total_m.group(1) if total_m else '0'),
        'high_n':     (high_m.group(1)  if high_m  else '0'),
        'med_n':      (med_m.group(1)   if med_m   else '0'),
        'papers':     papers,
        'urgent':     urgent,
    }


# ═══════════════════════════════════════════════════════════════
# 生成 HTML
# ═══════════════════════════════════════════════════════════════

def generate_academic_html(data: dict, output_path: str):

    # ── 紧急清单 ──
    urgent_html = ''
    if data['urgent']:
        items = ''.join(
            f'<div class="urgent-item">'
            f'<span class="urgent-ch">{u["chapter"]}</span>'
            f'<span class="urgent-t">{u["title"]}</span>'
            f'</div>'
            for u in data['urgent']
        )
        urgent_html = f'''
<div class="urgent-strip">
  <div class="urgent-label">🚨 IMMEDIATE UPDATE QUEUE</div>
  <div class="urgent-list">{items}</div>
</div>'''

    # ── 论文单卡片 ──
    papers_html = ''
    for idx, p in enumerate(data['papers'], 1):
        try:
            score_num     = float(p['score'])
            score_display = f'{score_num:.1f}'
            # 颜色映射
            if score_num >= 8.5:
                score_cls = 'score-high'
            elif score_num >= 7.0:
                score_cls = 'score-mid'
            else:
                score_cls = 'score-low'
        except (ValueError, TypeError):
            score_display = p['score'] or '—'
            score_cls     = ''

        link_html = ''
        if p['link'] and p['link'] not in ('N/A', '#', ''):
            link_html = (f'<a class="source-btn" href="{p["link"]}" '
                         f'target="_blank" rel="noopener">↗ PDF / SOURCE</a>')

        authors_html = ''
        if p['authors'] and p['authors'] != 'N/A':
            authors_html = f'<span class="meta-authors">👤 {p["authors"]}</span>'

        pub_html = ''
        if p['published'] and p['published'] != 'N/A':
            pub_html = f'<span class="meta-pub">📅 {p["published"][:10]}</span>'

        chapter_html = ''
        if p['chapter'] and p['chapter'] != 'N/A':
            chapter_html = f'<span class="meta-chapter">§ {p["chapter"]}</span>'

        # 核心发现
        summary_html = ''
        if p['summary']:
            summary_html = f'''
      <div class="paper-block">
        <div class="block-label">CORE FINDING</div>
        <p class="block-body">{p["summary"]}</p>
      </div>'''

        # 理论关联
        imp_html = ''
        if p['implications'] and p['implications'] != 'N/A':
            imp_html = f'''
      <div class="paper-block implication-block">
        <div class="block-label">RELEVANCE TO RENEGADE AI</div>
        <p class="block-body imp-text">{p["implications"]}</p>
      </div>'''

        # 建议行动
        action_html = ''
        if p['action'] and p['action'] not in ('N/A', '—', ''):
            action_html = f'''
      <div class="paper-block action-block">
        <div class="block-label">RECOMMENDED UPDATE</div>
        <p class="block-body">{p["action"]}</p>
      </div>'''

        # 模型评分
        scores_html = ''
        if p['model_scores']:
            pills = ''.join(
                f'<span class="score-pill">{n} <strong>{s}</strong></span>'
                for n, s in p['model_scores']
            )
            scores_html = f'''
      <div class="paper-block scores-block">
        <div class="block-label">MODEL SCORES</div>
        <div class="score-pills">{pills}</div>
      </div>'''

        # 草稿
        draft_html = ''
        if p['draft'] and len(p['draft']) > 30:
            draft_html = f'''
      <div class="paper-block draft-block">
        <div class="block-label">✍ AUTO-GENERATED DRAFT</div>
        <div class="draft-body">{p["draft"]}</div>
      </div>'''

        # 底部标签行
        footer_tags = ''
        for val, icon in [(p.get('urgency'), '⏱'), (p.get('update_type'), '🔄')]:
            if val and val not in ('N/A', '—', ''):
                footer_tags += f'<span class="foot-tag">{icon} {val}</span>'

        papers_html += f'''
<section class="paper-card" id="paper-{idx}">
  <!-- LEFT SPINE -->
  <div class="paper-spine">
    <div class="spine-index">{idx:02d}</div>
    <div class="spine-score {score_cls}">
      <span class="score-n">{score_display}</span>
      <span class="score-d">/10</span>
    </div>
    <div class="spine-line"></div>
  </div>

  <!-- RIGHT CONTENT -->
  <div class="paper-body">
    <div class="paper-top">
      <div class="paper-title-wrap">
        <h2 class="paper-title">{p["title"]}</h2>
        <div class="paper-meta">
          {authors_html}{pub_html}{chapter_html}
        </div>
      </div>
      {link_html}
    </div>

    {summary_html}
    {imp_html}
    {action_html}
    {scores_html}
    {draft_html}

    {f'<div class="paper-footer">{footer_tags}</div>' if footer_tags else ''}
  </div>
</section>
'''

    # ── TOC (논문 목록) ──
    toc_html = ''
    if data['papers']:
        toc_items = ''.join(
            f'<a class="toc-item" href="#paper-{i}">'
            f'<span class="toc-n">{i:02d}</span>'
            f'<span class="toc-t">{p["title"][:72]}{"…" if len(p["title"]) > 72 else ""}</span>'
            f'<span class="toc-s">{p["score"]}</span>'
            f'</a>'
            for i, p in enumerate(data['papers'], 1)
        )
        toc_html = f'''
<nav class="toc">
  <div class="toc-label">INDEX · {len(data["papers"])} HIGH-RELEVANCE PAPERS</div>
  {toc_items}
</nav>'''

    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Academic Radar · {data["date"]} | Renegade AI</title>
  <meta name="description" content="学术论文监控报告 {data["date"]} · {data["high_n"]} 高相关论文">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Space+Mono:ital,wght@0,400;0,700;1,400&family=Crimson+Pro:ital,wght@0,300;0,400;0,600;1,300;1,400&family=Bebas+Neue&display=swap" rel="stylesheet">
  <style>
/* ── DESIGN TOKENS ── */
:root {{
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
  --mono:  'Space Mono', monospace;
  --serif: 'Crimson Pro', Georgia, serif;
  --display: 'Bebas Neue', sans-serif;
  --ease: cubic-bezier(0.4,0,0.2,1);
}}
:root.light {{
  --bg:#f8f9fc; --bg2:#fff; --surface:#f0f2f8; --card:#fff;
  --border:#e0e2ec; --border-bright:#c0c2d0;
  --text:#2a2a40; --text-muted:#6a6a80; --text-faint:#a0a0b8;
  --accent-dim:rgba(232,80,58,0.08); --accent3-dim:rgba(74,143,207,0.08);
  --white:#2a2a40;
}}

/* ── RESET ── */
*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
html{{scroll-behavior:smooth}}
body{{font-family:var(--serif);background:var(--bg);color:var(--text);
     line-height:1.8;-webkit-font-smoothing:antialiased;overflow-x:hidden;
     transition:background .3s,color .3s}}
::selection{{background:var(--accent);color:#000}}
::-webkit-scrollbar{{width:4px}}
::-webkit-scrollbar-track{{background:var(--bg)}}
::-webkit-scrollbar-thumb{{background:var(--accent)}}

/* ── NOISE ── */
.noise{{position:fixed;inset:0;z-index:0;pointer-events:none;opacity:.025;
  background-image:url("data:image/svg+xml,%3Csvg viewBox='0 0 512 512' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.65' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='512' height='512' filter='url(%23n)'/%3E%3C/svg%3E")}}
.light .noise{{opacity:.05}}

/* ── NAV ── */
nav{{
  position:fixed;top:0;width:100%;z-index:200;
  background:rgba(8,8,14,.92);backdrop-filter:blur(24px);
  border-bottom:1px solid var(--border);height:56px;
  display:flex;align-items:center;justify-content:space-between;
  padding:0 32px;font-family:var(--mono);
  transition:background .3s,border-color .3s;
}}
.light nav{{background:rgba(248,249,252,.92)}}
.nav-brand{{font-size:.75rem;font-weight:700;color:var(--accent);
           letter-spacing:3px;text-transform:uppercase;text-decoration:none}}
.nav-right{{display:flex;gap:8px;align-items:center}}
.nav-pill{{
  background:none;border:1px solid var(--border);color:var(--text-muted);
  font-family:var(--mono);font-size:.62rem;letter-spacing:2px;
  padding:5px 14px;text-decoration:none;display:inline-flex;align-items:center;
  transition:all .2s;
}}
.nav-pill:hover{{border-color:var(--accent);color:var(--accent);background:var(--accent-dim)}}
.theme-btn{{
  background:none;border:1px solid var(--border);color:var(--text-muted);
  width:36px;height:36px;cursor:pointer;display:flex;align-items:center;
  justify-content:center;font-size:.9rem;transition:all .2s;
}}
.theme-btn:hover{{border-color:var(--accent);color:var(--accent);background:var(--accent-dim)}}

/* ── HERO ── */
.hero{{
  padding-top:56px;border-bottom:1px solid var(--border);
  display:grid;grid-template-columns:1fr auto;
}}
.hero-left{{padding:56px 72px 48px;border-right:1px solid var(--border)}}
.hero-eyebrow{{
  font-family:var(--mono);font-size:.62rem;letter-spacing:4px;
  color:var(--accent);text-transform:uppercase;
  margin-bottom:20px;display:flex;align-items:center;gap:12px;
}}
.hero-eyebrow::before{{content:'';width:36px;height:1px;background:var(--accent)}}
.hero-title{{
  font-family:var(--display);font-size:clamp(3rem,5vw,5.5rem);
  line-height:.92;letter-spacing:3px;color:var(--white);margin-bottom:18px;
}}
.hero-title span{{color:var(--accent)}}
.hero-desc{{
  font-size:1rem;color:var(--text-muted);font-style:italic;
  border-left:3px solid var(--accent);padding-left:16px;
  max-width:500px;line-height:1.9;margin-bottom:28px;transition:color .3s;
}}
.hero-tags{{display:flex;gap:6px;flex-wrap:wrap}}
.hero-tag{{
  font-family:var(--mono);font-size:.6rem;letter-spacing:1.5px;
  color:var(--text-muted);background:var(--surface);
  border:1px solid var(--border);padding:4px 12px;text-transform:uppercase;
}}
.hero-right{{
  display:flex;flex-direction:column;align-items:center;
  justify-content:center;padding:40px 52px;gap:20px;min-width:200px;
}}
.stat-block{{text-align:center}}
.stat-block .n{{font-family:var(--display);font-size:4rem;color:var(--accent);line-height:1;display:block}}
.stat-block .l{{font-family:var(--mono);font-size:.58rem;letter-spacing:2.5px;
               color:var(--text-muted);text-transform:uppercase;display:block;margin-top:4px}}
.stat-divider{{width:1px;height:32px;background:var(--border)}}

/* ── URGENT STRIP ── */
.urgent-strip{{
  border-bottom:1px solid var(--border);
  border-left:4px solid var(--accent);
  background:var(--accent-dim);
  padding:20px 72px;
}}
.urgent-label{{
  font-family:var(--mono);font-size:.6rem;letter-spacing:3px;
  color:var(--accent);text-transform:uppercase;margin-bottom:12px;
}}
.urgent-list{{display:flex;flex-direction:column;gap:6px}}
.urgent-item{{
  display:flex;align-items:baseline;gap:12px;
  font-family:var(--mono);font-size:.65rem;
}}
.urgent-ch{{
  color:var(--accent);letter-spacing:1px;white-space:nowrap;
  border:1px solid rgba(232,80,58,.3);padding:1px 6px;
}}
.urgent-t{{color:var(--text-muted)}}

/* ── TOC ── */
.toc{{border-bottom:1px solid var(--border);padding:0 72px}}
.toc-label{{
  font-family:var(--mono);font-size:.58rem;letter-spacing:3px;
  color:var(--text-faint);text-transform:uppercase;
  padding:14px 0 10px;border-bottom:1px solid var(--border);
}}
.toc-item{{
  display:grid;grid-template-columns:36px 1fr 36px;
  gap:16px;align-items:baseline;
  padding:10px 0;border-bottom:1px solid var(--border);
  text-decoration:none;transition:background .15s;
}}
.toc-item:last-child{{border-bottom:none}}
.toc-item:hover{{background:var(--surface);margin:0 -72px;padding:10px 72px}}
.toc-n{{font-family:var(--display);font-size:1rem;color:var(--text-faint)}}
.toc-t{{font-family:var(--serif);font-size:.92rem;color:var(--text-muted);transition:color .2s}}
.toc-item:hover .toc-t{{color:var(--white)}}
.toc-s{{
  font-family:var(--display);font-size:1rem;color:var(--accent);
  text-align:right;
}}

/* ── PAPER CARD (single-card layout) ── */
.paper-card{{
  display:grid;grid-template-columns:80px 1fr;
  gap:0;border-bottom:1px solid var(--border);
  opacity:0;transform:translateY(20px);
  animation:fadeUp .6s var(--ease) forwards;
  transition:background .2s;
}}
.paper-card:hover{{background:var(--surface)}}

/* LEFT SPINE */
.paper-spine{{
  border-right:1px solid var(--border);
  display:flex;flex-direction:column;
  align-items:center;padding:36px 0;gap:16px;
  position:sticky;top:56px;align-self:start;
  height:auto;
}}
.spine-index{{
  font-family:var(--display);font-size:2.2rem;
  color:var(--text-faint);line-height:1;
}}
.spine-score{{text-align:center}}
.score-n{{
  font-family:var(--display);font-size:2.4rem;line-height:1;display:block;
}}
.score-d{{
  font-family:var(--mono);font-size:.5rem;color:var(--text-faint);
  letter-spacing:1px;display:block;margin-top:2px;
}}
.score-high .score-n{{color:var(--accent)}}
.score-mid  .score-n{{color:var(--accent2)}}
.score-low  .score-n{{color:var(--accent3)}}
.spine-line{{flex:1;width:1px;background:var(--border);min-height:20px}}

/* RIGHT BODY */
.paper-body{{padding:40px 64px 40px 48px;display:flex;flex-direction:column;gap:0}}
.paper-top{{
  display:flex;justify-content:space-between;align-items:flex-start;
  gap:24px;margin-bottom:32px;flex-wrap:wrap;
}}
.paper-title-wrap{{flex:1}}
.paper-title{{
  font-family:var(--display);
  font-size:clamp(1.6rem,3vw,2.4rem);
  letter-spacing:1.5px;color:var(--white);
  line-height:1.1;margin-bottom:12px;
}}
.paper-meta{{
  display:flex;gap:10px;flex-wrap:wrap;align-items:center;
  font-family:var(--mono);font-size:.6rem;letter-spacing:1px;
}}
.meta-authors{{color:var(--text-muted);font-style:italic}}
.meta-pub{{
  background:var(--surface);padding:2px 8px;
  color:var(--text-faint);border:1px solid var(--border);
}}
.meta-chapter{{
  color:var(--accent2);letter-spacing:1.5px;
  border:1px solid rgba(201,160,64,.3);padding:2px 8px;
}}

.source-btn{{
  font-family:var(--mono);font-size:.6rem;letter-spacing:2px;
  text-transform:uppercase;text-decoration:none;
  border:1px solid var(--border-bright);color:var(--text-muted);
  padding:8px 16px;white-space:nowrap;align-self:flex-start;
  transition:all .2s;flex-shrink:0;
}}
.source-btn:hover{{border-color:var(--accent2);color:var(--accent2);background:rgba(201,160,64,.06)}}

/* CONTENT BLOCKS */
.paper-block{{
  padding:24px 0;border-top:1px solid var(--border);
}}
.block-label{{
  font-family:var(--mono);font-size:.55rem;letter-spacing:3px;
  color:var(--text-faint);text-transform:uppercase;margin-bottom:10px;
}}
.block-body{{font-size:.95rem;color:var(--text-muted);line-height:1.85;transition:color .3s}}
.imp-text{{
  color:var(--accent2);
  border-left:3px solid var(--accent2);
  padding-left:16px;font-style:italic;
}}
.action-block .block-body{{
  color:var(--text);
  border-left:3px solid var(--accent3);
  padding-left:16px;
}}
.score-pills{{display:flex;gap:8px;flex-wrap:wrap}}
.score-pill{{
  font-family:var(--mono);font-size:.62rem;
  background:var(--surface);border:1px solid var(--border);
  padding:4px 10px;color:var(--text-muted);
}}
.score-pill strong{{color:var(--accent);font-weight:700}}
.draft-block{{background:var(--surface);margin:0 -48px 0 0;padding:24px 48px 24px 0}}
.draft-block .block-label{{color:var(--accent)}}
.draft-body{{
  font-size:.95rem;color:var(--text);
  line-height:1.9;font-style:italic;
  border-left:3px solid var(--accent);padding-left:16px;
}}

/* PAPER FOOTER */
.paper-footer{{
  padding:16px 0 0;border-top:1px solid var(--border);
  margin-top:8px;display:flex;gap:8px;flex-wrap:wrap;
}}
.foot-tag{{
  font-family:var(--mono);font-size:.58rem;letter-spacing:1px;
  color:var(--text-faint);background:var(--surface);
  border:1px solid var(--border);padding:3px 10px;
}}

/* ── GLOBAL FOOTER ── */
.page-footer{{
  border-top:1px solid var(--border);
  padding:40px 72px;display:flex;justify-content:space-between;
  font-family:var(--mono);font-size:.62rem;color:var(--text-faint);
  flex-wrap:wrap;gap:12px;
}}
.page-footer a{{color:var(--text-faint);text-decoration:none;transition:color .2s}}
.page-footer a:hover{{color:var(--accent)}}

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
@keyframes fadeUp{{to{{opacity:1;transform:translateY(0)}}}}

/* ── RESPONSIVE ── */
@media(max-width:900px){{
  .hero{{grid-template-columns:1fr}}
  .hero-left{{padding:48px 24px 36px;border-right:none;border-bottom:1px solid var(--border)}}
  .hero-right{{flex-direction:row;padding:24px;border-bottom:1px solid var(--border)}}
  .stat-divider{{width:40px;height:1px}}
  .urgent-strip,.toc{{padding-left:24px;padding-right:24px}}
  .toc-item:hover{{margin:0 -24px;padding:10px 24px}}
  .paper-card{{grid-template-columns:56px 1fr}}
  .paper-body{{padding:28px 24px 28px 20px}}
  .draft-block{{margin:0 -24px 0 0;padding:24px 24px 24px 0}}
  .page-footer{{padding:32px 24px}}
}}
  </style>
</head>
<body>
<div class="noise"></div>

<!-- NAV -->
<nav>
  <a href="https://brook-han.github.io/renegade-ai-Updater/" class="nav-brand">RENEGADE RADAR</a>
  <div class="nav-right">
    <a href="index.html" class="nav-pill">← ARCHIVE</a>
    <button class="theme-btn" id="themeBtn" aria-label="Toggle theme">◐</button>
  </div>
</nav>

<!-- HERO -->
<div class="hero">
  <div class="hero-left">
    <div class="hero-eyebrow">§ Academic Radar · {data["date"]}</div>
    <h1 class="hero-title">LITERATURE<br><span>SCAN</span></h1>
    <p class="hero-desc">
      High-relevance papers mapped to the arguments that matter —
      ranked, annotated, and connected to the text of Renegade AI.
    </p>
    <div class="hero-tags">
      <span class="hero-tag">ANALYSIS · {data["model"]}</span>
      <span class="hero-tag">DRAFT · {data["draft_model"]}</span>
      <span class="hero-tag">TOTAL · {data["total"]} PAPERS</span>
      <span class="hero-tag">HIGH · {data["high_n"]} · MED · {data["med_n"]}</span>
    </div>
  </div>
  <div class="hero-right">
    <div class="stat-block">
      <span class="n">{data["high_n"]}</span>
      <span class="l">High</span>
    </div>
    <div class="stat-divider"></div>
    <div class="stat-block">
      <span class="n">{data["med_n"]}</span>
      <span class="l">Medium</span>
    </div>
  </div>
</div>

{urgent_html}
{toc_html}

<!-- PAPERS -->
<div id="papers">
{papers_html}
</div>

<footer class="page-footer">
  <span>Renegade AI v5.3 · Brooks Han · {data["date"]}</span>
  <div style="display:flex;gap:20px">
    <a href="index.html">← Academic Archive</a>
    <a href="https://brook-han.github.io/Renegade-AI/" target="_blank" rel="noopener">GitHub ↗</a>
  </div>
</footer>

<!-- STATUS BAR -->
<div class="status-bar">
  <span><span class="status-dot"></span><span id="statusText">STATUS: [ LITERATURE SCAN · {data["date"]} · {data["high_n"]} HIGH-RELEVANCE ]</span></span>
  <span id="statusTime"></span>
</div>

<script>
/* ── THEME ── */
(function(){{
  const h=document.documentElement,b=document.getElementById('themeBtn');
  const apply=t=>{{h.classList.toggle('light',t==='light');localStorage.setItem('renegade-theme',t)}};
  apply(localStorage.getItem('renegade-theme')||(matchMedia('(prefers-color-scheme:dark)').matches?'dark':'light'));
  b.onclick=()=>apply(h.classList.contains('light')?'dark':'light');
}})();

/* ── STATUS TIME ── */
(function(){{
  const tm=document.getElementById('statusTime');
  function tick(){{tm.textContent=new Date().toISOString().replace('T',' ').slice(0,19)+' UTC'}}
  tick();setInterval(tick,1000);
}})();

/* ── STAGGER ── */
document.querySelectorAll('.paper-card').forEach((c,i)=>{{
  c.style.animationDelay=(i*0.08)+'s';
}});
</script>
</body>
</html>'''

    Path(output_path).write_text(html, encoding='utf-8')
    print(f'✅ HTML 已生成: {output_path}')


# ═══════════════════════════════════════════════════════════════
# 主入口
# ═══════════════════════════════════════════════════════════════

if __name__ == '__main__':
    if len(sys.argv) > 1:
        md_file = sys.argv[1]
        print(f'📄 使用指定文件: {md_file}')
    else:
        for search_dir in [Path('docs/academic'), Path('output/academic'), Path('reports')]:
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

    print('📖 解析中...')
    data = parse_academic_report(md_file)

    if not data['papers']:
        print(f'⚠️ 未解析到高相关论文 (总计 {data["total"]} 篇 | 高相关 {data["high_n"]} 篇)')
        print('💡 请确认 MD 文件包含 "## ⭐ 高相关论文" 区块')

    out_file = str(Path(md_file).with_suffix('.html'))
    generate_academic_html(data, out_file)
    print(f'🎉 完成！预览路径：file://{Path(out_file).resolve()}')