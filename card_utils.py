#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
card_utils.py — 共享卡片提取工具
从 HTML 报告中提取卡片信息，供以下模块共用：
  - radar_index_generator.py
  - generate_news_index.py
  - generate_academic_index.py

支持两种解析策略：
  1. lxml + XPath（优先，速度快、容错好）
  2. 正则降级（lxml 不可用时自动切换）
"""

import re
from pathlib import Path

try:
    from lxml import html as lxml_html
    _HAS_LXML = True
except ImportError:
    _HAS_LXML = False


def _extract_with_lxml(html_path: Path, report_type: str) -> list[dict]:
    """用 lxml + XPath 解析 HTML 报告，提取卡片信息。"""
    try:
        content = html_path.read_text(encoding="utf-8")
    except Exception as e:
        print(f"   ⚠️ 读取失败 {html_path.name}: {e}")
        return []

    try:
        tree = lxml_html.fromstring(content)
    except Exception as e:
        print(f"   ⚠️ 解析失败 {html_path.name}: {e}")
        return []

    # 支持两种卡片类名：card (旧) 和 radar-card (新 v5.4)
    card_elements = tree.xpath("//*[contains(concat(' ', @class, ' '), ' card ')] | //*[contains(concat(' ', @class, ' '), ' radar-card ')]")
    if card_elements:
        print(f"   🔍 {html_path.name}: 找到 {len(card_elements)} 个卡片区块")

    cards = []
    for card_el in card_elements:
        card = {"type": report_type}

        # 支持 card-title 和 radar-card-title
        title_els = card_el.xpath(".//*[contains(@class, 'card-title')] | .//*[contains(@class, 'radar-card-title')]")
        if not title_els:
            continue
        card["title"] = title_els[0].text_content().strip()

        # 支持 card-score 和 radar-score
        score_els = card_el.xpath(".//*[contains(@class, 'card-score')] | .//*[contains(@class, 'radar-score')]")
        if score_els:
            score_text = score_els[0].text_content().strip()
            score_m = re.search(r"([\d.]+)", score_text)
            card["score"] = score_m.group(1) if score_m else "5.0"
        else:
            card["score"] = "5.0"

        card["link"] = ""
        for a in card_el.xpath(".//a[@target='_blank']"):
            link_text = a.text_content().strip() if a.text_content() else ""
            if "原文" in link_text or "PDF" in link_text:
                href = a.get("href", "")
                if href:
                    card["link"] = href
                break

        # 支持 card-body 和 radar-card-body
        body_els = card_el.xpath(".//*[contains(@class, 'card-body')] | .//*[contains(@class, 'radar-card-body')]")
        if body_els:
            card["summary"] = body_els[0].text_content().strip()
        else:
            card["summary"] = ""

        # 支持 card-draft 和 radar-card-draft
        card["has_draft"] = bool(card_el.xpath(".//*[contains(@class, 'card-draft')] | .//*[contains(@class, 'radar-card-draft')]"))

        # 支持 card-meta 和 radar-card-meta
        meta_els = card_el.xpath(".//*[contains(@class, 'card-meta')] | .//*[contains(@class, 'radar-card-meta')]")
        if meta_els:
            meta_text = meta_els[0].text_content()
            chapter_m = re.search(r"📍\s*(.+?)(?:\n|$)", meta_text)
            if chapter_m:
                card["chapter"] = chapter_m.group(1).strip()

        cards.append(card)

    return cards


def _extract_with_regex(html_path: Path, report_type: str) -> list[dict]:
    """用正则解析 HTML 报告（降级方案）。"""
    try:
        content = html_path.read_text(encoding="utf-8")
    except Exception as e:
        print(f"   ⚠️ 读取失败 {html_path.name}: {e}")
        return []

    cards = []
    # 支持两种卡片类名：card (旧) 和 radar-card (新 v5.4)
    card_blocks = re.findall(
        r'<(?:div|article) class="(?:card|radar-card)">(.*?)</(?:div|article)>\s*(?=<(?:div|article) class="(?:card|radar-card)">|</main>|</body>|$)',
        content,
        re.DOTALL,
    )
    if card_blocks:
        print(f"   🔍 {html_path.name}: 找到 {len(card_blocks)} 个卡片区块")

    for block in card_blocks:
        card = {"type": report_type}

        # 支持 card-title 和 radar-card-title
        title_m = re.search(r'<(?:div|h2) class="(?:card|radar-card)-title">(.*?)</(?:div|h2)>', block, re.DOTALL)
        if title_m:
            card["title"] = re.sub(r"<[^>]+>", "", title_m.group(1)).strip()

        # 支持 card-score 和 radar-score
        score_m = re.search(r'<(?:div|span) class="(?:card|radar)-score">([\d.]+)\s*(?:<span>)?/10', block)
        card["score"] = score_m.group(1) if score_m else "5.0"

        link_m = re.search(r'<a href="([^"]+)" target="_blank"[^>]*>↗\s*(?:原文|PDF/原文)</a>', block)
        if link_m:
            card["link"] = link_m.group(1)

        # 支持 card-body 和 radar-card-body
        summary_m = re.search(r'<(?:div|p) class="(?:card|radar-card)-body">(.*?)</(?:div|p)>', block, re.DOTALL)
        if summary_m:
            card["summary"] = re.sub(r"<[^>]+>", "", summary_m.group(1)).strip()

        # 支持 card-draft 和 radar-card-draft
        card["has_draft"] = ('class="card-draft"' in block) or ('class="radar-card-draft"' in block)

        chapter_m = re.search(r"📍\s*([^<\s][^<]*?)(?:</span>|<|&nbsp;|$)", block)
        if chapter_m:
            card["chapter"] = chapter_m.group(1).strip()

        if card.get("title"):
            cards.append(card)

    return cards


def extract_cards_from_html(html_path: Path, report_type: str = "") -> list[dict]:
    """
    从 HTML 报告中提取卡片信息。
    自动选择 lxml（优先）或正则降级方案。
    """
    if _HAS_LXML:
        return _extract_with_lxml(html_path, report_type)
    else:
        return _extract_with_regex(html_path, report_type)


__all__ = ["extract_cards_from_html"]
