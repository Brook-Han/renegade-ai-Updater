#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📰 News Radar MD → HTML 转换器（v5.4 与主页完全对齐版）

功能：将 news_radar.py 生成的 Markdown 报告转换为漂亮的网页
风格：与 Renegade AI v5.4 主页完全对齐（高级 CSS 布局与动效）

📋 用法：
    # 方式1：转换指定文件
    python news_md_to_html.py docs/news/news_report_2026-05-11.md
    
    # 方式2：自动找最新报告（推荐）
    python news_md_to_html.py

🔧 输出：同目录下生成 .html 文件，可直接用浏览器打开

作者：Brooks Han
版本：v1.3 (2026-06-09) v5.4
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

/* ── DESIGN TOKENS (v5.4 · Readability & Visual Optimized) ── */
:root {
  --bg:           #0c0c18;
  --bg2:          #10101e;
  --surface:      #12121e;
  --card:         #1a1a2e;
  --border:       #282840;
  --border-bright:#3a3a5a;
  --text:         #e2e2f0;
  --text-muted:   #a8a8d0;
  --text-faint:   #55557a;
  --accent:       #ff5c45;
  --accent-dim:   rgba(255,92,69,0.12);
  --accent-glow:  rgba(255,92,69,0.06);
  --accent2:      #d4af5c;
  --accent2-dim:  rgba(212,175,92,0.10);
  --accent3:      #5ba3e6;
  --accent3-dim:  rgba(91,163,230,0.12);
  --white:        #f4f4fc;
  --mono:         'Space Mono', monospace;
  --serif:        'Crimson Pro', Georgia, serif;
  --display:      'Bebas Neue', sans-serif;
  --ease:         cubic-bezier(0.4,0,0.2,1);
}
:root.light {
  --bg:#f0f2f8; --bg2:#fafbff; --surface:#e8eaf2; --card:#ffffff;
  --border:#d4d7e4; --border-bright:#b8bcd0;
  --text:#1a1a2e; --text-muted:#4c4c6a; --text-faint:#8888a0;
  --accent:#d94934; --accent-dim:rgba(217,73,52,0.08); --accent-glow:rgba(217,73,52,0.04);
  --accent2:#a67c28; --accent2-dim:rgba(166,124,40,0.08);
  --accent3:#356ba8; --accent3-dim:rgba(53,107,168,0.08);
  --white:#1a1a2e;
}

/* ── RESET & TYPOGRAPHY ── */
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
html{scroll-behavior:smooth}
body{
  font-family:var(--serif);background:var(--bg);color:var(--text);
  font-size:1rem;line-height:1.8;-webkit-font-smoothing:antialiased;
  -moz-osx-font-smoothing:grayscale;overflow-x:hidden;
  transition:background .3s,color .3s;
  text-rendering:optimizeLegibility;
  font-feature-settings:"kern" 1,"liga" 1,"palt" 1;
}
::selection{background:var(--accent);color:#fff;text-shadow:0 1px 2px rgba(0,0,0,.2)}
::-webkit-scrollbar{width:4px}
::-webkit-scrollbar-track{background:var(--bg)}
::-webkit-scrollbar-thumb{background:var(--border-bright);border-radius:2px}
::-webkit-scrollbar-thumb:hover{background:var(--accent)}

/* ── ACCESSIBILITY ── */
:focus-visible{outline:2px solid var(--accent);outline-offset:3px;border-radius:2px;z-index:10}
:focus:not(:focus-visible){outline:none}
@media(prefers-reduced-motion:reduce){
  *,*::before,*::after{
    animation-duration:.01ms!important;animation-iteration-count:1!important;
    transition-duration:.01ms!important;scroll-behavior:auto!important;
  }
  .noise{opacity:0!important}
}

/* ── NOISE OVERLAY ── */
.noise{position:fixed;inset:0;z-index:0;pointer-events:none;opacity:.025;
  background-image:url("data:image/svg+xml,%3Csvg viewBox='0 0 512 512' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.65' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='512' height='512' filter='url(%23n)'/%3E%3C/svg%3E")}
.light .noise{opacity:.05}

/* ── NAV (Glass v5.4) ── */
nav{
  position:fixed;top:0;width:100%;z-index:200;
  background:rgba(12,12,24,.88);backdrop-filter:blur(32px) saturate(1.2);
  -webkit-backdrop-filter:blur(32px) saturate(1.2);
  border-bottom:1px solid var(--border);
  height:56px;display:flex;align-items:center;justify-content:space-between;
  padding:0 32px;font-family:var(--mono);transition:background .3s,border-color .3s;
}
.light nav{background:rgba(240,242,248,.88)}
.nav-brand{
  font-size:.75rem;font-weight:700;color:var(--accent);letter-spacing:3px;
  text-transform:uppercase;text-decoration:none;
  position:relative;transition:opacity .2s;
}
.nav-brand:hover{opacity:.85}
.nav-right{display:flex;gap:8px;align-items:center}
.nav-pill{
  background:none;border:1px solid var(--border);color:var(--text-muted);
  font-family:var(--mono);font-size:.72rem;font-weight:500;letter-spacing:2px;
  padding:5px 14px;cursor:pointer;text-decoration:none;
  display:inline-flex;align-items:center;transition:all .25s var(--ease);
}
.nav-pill:hover,.nav-pill.active{border-color:var(--accent);color:var(--accent);background:var(--accent-dim)}
.theme-btn{
  background:none;border:1px solid var(--border);color:var(--text-muted);
  width:36px;height:36px;cursor:pointer;display:flex;align-items:center;justify-content:center;
  font-size:.9rem;transition:all .25s var(--ease);
}
.theme-btn:hover,.theme-btn:focus-visible{border-color:var(--accent);color:var(--accent);background:var(--accent-dim);transform:rotate(180deg)}

/* ── HERO STRIP (v5.4 Ambient) ── */
.hero-strip{
  padding-top:56px;border-bottom:1px solid var(--border);
  display:grid;grid-template-columns:1fr auto;gap:0;position:relative;
}
.hero-strip::before{
  content:'';position:absolute;top:-120px;left:-80px;
  width:600px;height:600px;
  background:radial-gradient(ellipse at 30% 40%,rgba(255,92,69,.08) 0%,transparent 70%);
  pointer-events:none;z-index:0;
}
.hero-left{
  padding:60px 72px 52px;border-right:1px solid var(--border);
  position:relative;z-index:1;
}
.hero-eyebrow{
  font-family:var(--mono);font-size:.72rem;font-weight:500;letter-spacing:4px;
  color:var(--accent);text-transform:uppercase;
  margin-bottom:20px;display:flex;align-items:center;gap:12px;
}
.hero-eyebrow::before{content:'';width:36px;height:1px;background:var(--accent)}
.hero-title{
  font-family:var(--display);font-size:clamp(3.5rem,7vw,7rem);
  line-height:.9;letter-spacing:3px;color:var(--white);margin-bottom:16px;
}
.hero-title span{color:var(--accent);text-shadow:0 0 40px rgba(255,92,69,.25)}
.hero-desc{
  font-size:1.1rem;color:var(--text-muted);font-style:italic;
  border-left:3px solid var(--accent);padding-left:18px;
  max-width:520px;line-height:1.85;margin-bottom:32px;transition:color .3s;
}
.hero-tags{display:flex;gap:6px;flex-wrap:wrap}
.hero-tag{
  font-family:var(--mono);font-size:.72rem;font-weight:500;letter-spacing:1.5px;
  color:var(--text-muted);background:var(--surface);
  border:1px solid var(--border);padding:4px 12px;text-transform:uppercase;
}
.hero-right{
  display:flex;flex-direction:column;align-items:center;justify-content:center;
  padding:40px 48px;gap:24px;min-width:220px;position:relative;z-index:1;
}
.stat-block{text-align:center}
.stat-block .n{
  font-family:var(--display);font-size:4rem;color:var(--accent);
  line-height:1;display:block;
  text-shadow:0 0 30px rgba(255,92,69,.2);
}
.stat-block .l{
  font-family:var(--mono);font-size:.72rem;font-weight:500;letter-spacing:2.5px;
  color:var(--text-muted);text-transform:uppercase;display:block;margin-top:4px;
}
.stat-divider{width:1px;height:40px;background:var(--border)}

/* ── CONTROLS BAR ── */
.controls-bar{
  display:flex;align-items:center;gap:0;
  border-bottom:1px solid var(--border);
  padding:0 72px;height:52px;
  font-family:var(--mono);font-size:.72rem;
  overflow-x:auto;position:relative;z-index:1;
}
.filter-btn{
  height:100%;padding:0 22px;
  background:none;border:none;border-right:1px solid var(--border);
  color:var(--text-muted);cursor:pointer;letter-spacing:2px;
  text-transform:uppercase;font-family:var(--mono);font-size:.72rem;font-weight:600;
  transition:all .25s var(--ease);white-space:nowrap;
}
.filter-btn:first-child{border-left:1px solid var(--border)}
.filter-btn.active,.filter-btn:hover{color:var(--accent);background:var(--accent-dim)}
.search-wrap{
  flex:1;display:flex;align-items:center;gap:10px;
  padding:0 20px;border-right:1px solid var(--border);min-width:180px;
}
.search-wrap::before{content:'§';color:var(--text-faint);font-size:.8rem}
.search-wrap input{
  background:none;border:none;color:var(--text);
  font-family:var(--mono);font-size:.72rem;font-weight:500;letter-spacing:1px;
  width:100%;outline:none;
}
.search-wrap input::placeholder{color:var(--text-faint);transition:color .2s}
.search-wrap input:focus::placeholder{color:transparent}
.controls-bar .list-link{
  height:100%;padding:0 20px;display:flex;align-items:center;
  color:var(--text-muted);text-decoration:none;letter-spacing:2px;
  text-transform:uppercase;white-space:nowrap;font-size:.72rem;font-weight:500;
  border-right:1px solid var(--border);transition:all .2s;
}
.controls-bar .list-link:hover{color:var(--accent);background:var(--accent-dim)}

/* ── MAIN CONTENT ── */
.main{max-width:100%;padding:64px 72px 80px;position:relative;z-index:1}

/* ── DAY GROUP ── */
.day-group{margin-bottom:64px}
.day-group.hidden{display:none}
.day-header-row{
  display:flex;align-items:flex-end;justify-content:space-between;
  border-bottom:1px solid var(--border);padding-bottom:16px;margin-bottom:28px;
}
.day-eyebrow{
  font-family:var(--mono);font-size:.72rem;font-weight:600;letter-spacing:3px;
  color:var(--accent);text-transform:uppercase;margin-bottom:6px;
}
.day-date{
  font-family:var(--display);font-size:clamp(2rem,4vw,3.2rem);
  letter-spacing:2px;color:var(--white);line-height:1;
}
.day-header-right{
  font-family:var(--mono);font-size:.72rem;font-weight:500;letter-spacing:2px;
  color:var(--text-faint);text-transform:uppercase;padding-bottom:6px;
}

/* ── CARD GRID ── */
.card-grid{
  display:grid;grid-template-columns:repeat(auto-fill,minmax(480px,1fr));
  gap:1px;background:var(--border);border:1px solid var(--border);
}

/* ── RADAR CARD (v5.4) ── */
.radar-card{
  background:var(--card);padding:32px 28px;
  display:flex;flex-direction:column;gap:14px;
  transition:background .25s var(--ease),box-shadow .35s var(--ease),border-color .25s;
  position:relative;
  opacity:0;transform:translateY(16px);
  animation:fadeUp .4s var(--ease) forwards;
  box-shadow:0 2px 16px rgba(0,0,0,.12),inset 0 1px 0 rgba(255,255,255,.03);
  border-left:2px solid transparent;
}
.radar-card::before{
  content:'';position:absolute;inset:0;
  background:linear-gradient(135deg,var(--accent-glow),transparent 60%);
  opacity:0;transition:opacity .4s var(--ease);pointer-events:none;
}
.radar-card:hover::before{opacity:1}
.radar-card:hover{
  background:var(--surface);
  box-shadow:0 8px 32px rgba(0,0,0,.2),0 0 0 1px rgba(255,92,69,.12);
  z-index:2;
}
.radar-card:has(.radar-card-title a:focus-visible){
  box-shadow:0 8px 32px rgba(0,0,0,.2),0 0 0 2px var(--accent);
}
.radar-card.hidden{display:none}

.radar-card-top{display:flex;justify-content:space-between;align-items:flex-start;gap:16px}
.radar-card-meta{display:flex;align-items:center;gap:8px;flex-wrap:wrap;flex:1}

.type-tag{
  font-family:var(--mono);font-size:.72rem;font-weight:600;letter-spacing:2px;
  padding:3px 10px;text-transform:uppercase;
}
.type-tag.news{background:var(--accent3-dim);color:var(--accent3);border:1px solid rgba(91,163,230,.2)}
.type-tag.academic{background:var(--accent-dim);color:var(--accent);border:1px solid rgba(255,92,69,.2)}

.card-chapter{
  font-family:var(--mono);font-size:.72rem;font-weight:500;letter-spacing:1px;
  color:var(--text-faint);text-transform:uppercase;
}
.draft-dot{color:var(--accent2);font-size:.75rem;line-height:1;opacity:.8}

.radar-score{
  display:flex;flex-direction:column;align-items:flex-end;gap:4px;
  font-family:var(--display);font-size:2rem;color:var(--accent);
  line-height:1;white-space:nowrap;flex-shrink:0;
  position:relative;padding-left:8px;
}
.radar-score span{
  display:block;font-family:var(--mono);font-size:.7rem;font-weight:500;
  color:var(--text-faint);letter-spacing:1px;text-align:right;
}
.score-bar{
  display:flex;gap:2px;width:48px;height:3px;
}
.score-bar .bar{
  flex:1;border-radius:1px;
  background:var(--border-bright);transition:background .3s var(--ease);
}
.score-bar .bar.filled{background:var(--accent)}
.radar-card:hover .score-bar .bar.filled{background:var(--accent2)}

.radar-card-title{
  font-family:var(--display);font-size:1.35rem;letter-spacing:1px;
  color:var(--white);line-height:1.2;position:relative;z-index:1;
}
.radar-card-title a{
  color:inherit;text-decoration:none;
  border-bottom:1px solid transparent;
  transition:border-color .25s var(--ease),color .2s;
}
.radar-card-title a:hover{color:var(--accent2);border-bottom-color:var(--accent2)}

.radar-card-body{
  font-size:.95rem;color:var(--text-muted);line-height:1.8;
  flex:1;position:relative;z-index:1;
}

.radar-card-footer{
  display:flex;justify-content:space-between;align-items:center;
  padding-top:12px;border-top:1px solid var(--border);
  font-family:var(--mono);font-size:.72rem;font-weight:500;letter-spacing:1.5px;
  transition:border-color .3s;position:relative;z-index:1;
}
.card-source-link{
  color:var(--accent2);text-decoration:none;text-transform:uppercase;
  transition:color .25s var(--ease);
  display:inline-flex;align-items:center;gap:4px;
}
.card-source-link:hover{color:var(--white);gap:6px}
.full-report-link{
  color:var(--text-faint);text-decoration:none;text-transform:uppercase;
  transition:color .25s var(--ease);
  display:inline-flex;align-items:center;gap:4px;
}
.full-report-link:hover{color:var(--accent);gap:6px}

/* ── EMPTY STATE ── */
.empty-state{
  display:none;text-align:center;padding:100px 32px 80px;
  font-family:var(--mono);color:var(--text-faint);letter-spacing:2px;
  font-size:.72rem;font-weight:500;text-transform:uppercase;
}
.empty-state .glyph{
  font-family:var(--display);font-size:5rem;color:var(--text-faint);opacity:.2;
  display:block;margin-bottom:20px;line-height:1;
}

/* ── STATUS BAR ── */
.status-bar{
  position:fixed;bottom:0;width:100%;z-index:200;
  background:rgba(12,12,24,.92);backdrop-filter:blur(16px);
  border-top:1px solid var(--border);
  padding:10px 32px;font-family:var(--mono);font-size:.72rem;font-weight:500;
  color:var(--text-faint);letter-spacing:2px;
  display:flex;justify-content:space-between;align-items:center;
  transition:background .3s,border-color .3s;
}
.light .status-bar{background:rgba(240,242,248,.92)}
.status-dot{
  display:inline-block;width:6px;height:6px;
  background:var(--accent);border-radius:50%;margin-right:8px;
  animation:pulse 2s ease-in-out infinite;
  box-shadow:0 0 6px var(--accent);
}
@keyframes pulse{0%,100%{opacity:1;transform:scale(1)}50%{opacity:.5;transform:scale(.7)}}
@keyframes fadeUp{to{opacity:1;transform:translateY(0)}}

/* ── MOBILE TOUCH TARGETS ── */
@media(max-width:768px){
  .nav-pill,.theme-btn,.filter-btn,.controls-bar .list-link{
    min-height:44px;min-width:44px;display:inline-flex;align-items:center;justify-content:center;
  }
  .controls-bar{padding:0 8px;height:44px}
  .search-wrap{min-width:80px;padding:0 10px}
  .search-wrap::before{display:none}
  .filter-btn{padding:0 10px;font-size:.68rem}
  .controls-bar .list-link{padding:0 10px;font-size:.68rem}
}
@media(max-width:480px){
  .controls-bar{padding:0 4px;height:40px;gap:0;overflow-x:auto;-webkit-overflow-scrolling:touch}
  .search-wrap{min-width:60px;flex:0 0 auto;padding:0 8px}
  .search-wrap input{width:60px}
  .filter-btn{padding:0 8px;font-size:.65rem;letter-spacing:1px}
  .controls-bar .list-link{padding:0 8px;font-size:.65rem;letter-spacing:1px}
  .controls-bar .list-link:last-child{border-right:none}
}

/* ── RESPONSIVE ── */
@media(max-width:1200px){
  .card-grid{grid-template-columns:repeat(auto-fill,minmax(420px,1fr))}
}
@media(max-width:900px){
  .main{padding:48px 24px 80px}
  .controls-bar{padding:0 24px}
  .hero-strip{grid-template-columns:1fr}
  .hero-left{padding:48px 24px 36px;border-right:none;border-bottom:1px solid var(--border)}
  .hero-right{flex-direction:row;padding:24px;border-bottom:1px solid var(--border)}
  .stat-divider{width:40px;height:1px}
  .card-grid{grid-template-columns:1fr}
  .nav-center{display:none}
}
  
"""


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
    <article class="radar-card">
      <div class="radar-card-top">
        <h2 class="radar-card-title">{it["title"]}{case_badge}</h2>
        <div class="radar-score">{score_display}<span>/10</span></div>
      </div>
      <div class="radar-card-meta">
        {f'<span>{it["source"]}</span>' if it.get('source') and it['source'] != 'N/A' else ''}
        {f'<span>·</span>' if it.get('source') and link_html else ''}
        {link_html}
        {f'<span>·</span>' if chapter_html and (it.get('source') or link_html) else ''}
        {chapter_html}
      </div>
      <div class="radar-card-body">{it["summary"]}</div>{implications_html}
      {f'<div class="radar-card-footer">{tags_html}</div>' if tags_html else ''}
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
  <style>{CSS_TEMPLATE}
  </style>
</head>
<body>
  <nav>
    <a href="https://brook-han.github.io/Renegade-AI/" class="nav-brand">RENEGADE AI v5.4</a>
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
    <span>Renegade AI v5.4 · Brooks Han</span>
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