#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📰 Renegade AI 新闻列表页生成器 (v5.4)

完全重写 - 使用正确的v5.4结构
基于 docs/index.html 的v5.4模板

用法：
    python generate_news_index.py
输出：
    docs/news/index.html
"""

import re
from pathlib import Path
from html import escape

from config import Config
from card_utils import extract_cards_from_html

# ── 配置 ──
NEWS_DIR   = Config.OUTPUT_DIR / "news"
OUTPUT_FILE = NEWS_DIR / "index.html"
TEMPLATE_FILE = Config.BASE_DIR / "news_template_v54.html"


# ── 收集新闻报告 ──
def collect_news_reports() -> dict:
    if not NEWS_DIR.exists():
        print("❌ docs/news 目录不存在")
        return {"dates": [], "by_date": {}, "stats": {"total": 0, "days": 0}}

    entries = []
    for html_file in sorted(NEWS_DIR.glob("news_report_*.html")):
        if html_file.name == "index.html":
            continue
        m = re.search(r"(\d{4}-\d{2}-\d{2})(?:_(\d{6}))?", html_file.name)
        if not m:
            continue
        entries.append({
            "date":          m.group(1),
            "time":          m.group(2) if m.group(2) else "000000",
            "path":          html_file,
            "relative_link":  html_file.name,
        })

    by_date = {}
    for e in entries:
        by_date.setdefault(e["date"], []).append(e)
    for lst in by_date.values():
        lst.sort(key=lambda x: x["time"], reverse=True)

    sorted_dates = sorted(by_date.keys(), reverse=True)
    return {
        "dates":   sorted_dates,
        "by_date": by_date,
        "stats":   {"total": len(entries), "days": len(sorted_dates)},
    }


# ── 生成日期区块 (v5.4 结构) ──
def generate_day_block(date: str, entries: list[dict], top_n: int = None) -> str:
    """
    date: 日期字符串
    entries: 该日期的报告文件列表
    top_n: 显示前 N 条卡片，None 表示全部显示
    """
    all_cards = []
    for e in entries:
        cards = extract_cards_from_html(e["path"], "news")
        for c in cards:
            c["_report_link"] = e["relative_link"]
        all_cards.extend(cards)

    # 去重
    seen, unique = set(), []
    for c in all_cards:
        key = (c.get("title", ""), c.get("summary", "")[:80])
        if key not in seen:
            seen.add(key)
            unique.append(c)
    all_cards = unique

    # 按评分降序
    all_cards.sort(key=lambda c: float(c.get("score", 0)), reverse=True)

    if not all_cards:
        return ""

    # 选择要展示的卡片数量
    total_cards   = len(all_cards)
    display_cards = all_cards[:top_n] if top_n is not None else all_cards

    # 格式化时间
    latest_time   = entries[0]["time"]
    formatted_time = f"{latest_time[:2]}:{latest_time[2:4]}:{latest_time[4:]}"

    # 构建元信息
    if top_n is not None and total_cards > top_n:
        count_label = f"TOP {len(display_cards)} / {total_cards} NEWS"
    else:
        count_label = f"{total_cards} NEWS"

    # v5.4 正确结构
    html  = f'<div class="day-group" data-date="{date}">\n'
    html += f'  <div class="day-header-row">\n'
    html += f'    <div class="day-header-left">\n'
    html += f'      <div class="day-eyebrow">NEWS · {formatted_time}</div>\n'
    html += f'      <h2 class="day-date">{date}</h2>\n'
    html += f'    </div>\n'
    html += f'    <div class="day-header-right">{count_label}</div>\n'
    html += f'  </div>\n'
    html += f'  <div class="card-grid">\n'

    for card in display_cards:
        title       = escape(card.get("title", ""))
        score       = card.get("score", "5.0")
        summary     = escape(card.get("summary", "")[:240])
        chapter    = escape(card.get("chapter", ""))
        link        = card.get("link", "#")
        report_link = card.get("_report_link", "")

        chapter_html = f'<span class="card-chapter">§ {chapter}</span>' if chapter else ""
        source_html  = (f'<a class="card-source-link" href="{escape(link)}" '
                         f'target="_blank" rel="noopener">↗ 原文</a>'
                         if link and link != "#" else "")
        truncated    = "…" if len(card.get("summary", "")) > 240 else ""

        # 计算 score-bar 宽度
        try:
            score_width = float(score) * 10  # 7.7 -> 77%
        except:
            score_width = 50

        html += f'''    <article class="radar-card" data-type="news">
      <div class="radar-card-top">
        <div class="radar-card-meta">
          <span class="type-tag news">📰 新闻</span>
          {chapter_html}
        </div>
        <div class="radar-score">{score}<span>/10</span></div>
        <div class="score-bar"><div class="score-bar-fill mid" style="width:{score_width}%"></div></div>
      </div>
      <h3 class="radar-card-title">
        <a href="{escape(link)}" target="_blank" rel="noopener">{title}</a>
      </h3>
      <p class="radar-card-body">{summary}{truncated}</p>
      <div class="radar-card-footer">
        {source_html}
        <a class="full-report-link" href="./{report_link}">查看 {date} 完整报告 →</a>
      </div>
    </article>\n'''

    html += f'  </div>\n</div>\n'
    return html


# ── 主函数 ──
def main():
    print("📰 生成新闻列表页 (v5.4)...")

    # 检查模板文件是否存在
    if not TEMPLATE_FILE.exists():
        print(f"❌ 模板文件不存在: {TEMPLATE_FILE}")
        print("   请先运行之前的步骤生成 news_template_v54.html")
        return

    # 读取模板
    with open(TEMPLATE_FILE, 'r', encoding='utf-8') as f:
        template = f.read()

    # 收集数据
    data = collect_news_reports()
    if not data["dates"]:
        print("❌ 没有找到新闻报告文件")
        return

    latest_date = data["dates"][0] if data["dates"] else None

    # 生成每个日期的区块
    day_sections = []
    for date in data["dates"]:
        entries = data["by_date"][date]
        # 最新日期显示 Top 3，历史日期显示 Top 1
        top_n = 3 if date == latest_date else 1
        block = generate_day_block(date, entries, top_n=top_n)
        if block:
            day_sections.append(block)

    # 填充模板
    html = template.replace("{{ day_sections }}", "\n".join(day_sections))
    html = html.replace("{{ total_reports }}", str(data["stats"]["total"]))
    html = html.replace("{{ days_count }}", str(data["stats"]["days"]))

    # 写回文件
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text(html, encoding="utf-8")
    print(f"✅ 新闻列表页已生成 (v5.4): {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
