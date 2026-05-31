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

    card_elements = tree.xpath("//div[@class='card']")
    if card_elements:
        print(f"   🔍 {html_path.name}: 找到 {len(card_elements)} 个卡片区块")

    cards = []
    for card_el in card_elements:
        card = {"type": report_type}

        title_els = card_el.xpath(".//div[@class='card-title']")
        if not title_els:
            continue
        card["title"] = title_els[0].text_content().strip()

        score_els = card_el.xpath(".//div[@class='card-score']")
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

        body_els = card_el.xpath(".//div[@class='card-body']")
        if body_els:
            card["summary"] = body_els[0].text_content().strip()
        else:
            card["summary"] = ""

        card["has_draft"] = bool(card_el.xpath(".//div[@class='card-draft']"))

        meta_els = card_el.xpath(".//div[@class='card-meta']")
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
    card_blocks = re.findall(
        r'<div class="card">(.*?)</div>\s*(?=<div class="card">|</main>|</body>|$)',
        content,
        re.DOTALL,
    )
    if card_blocks:
        print(f"   🔍 {html_path.name}: 找到 {len(card_blocks)} 个卡片区块")

    for block in card_blocks:
        card = {"type": report_type}

        title_m = re.search(r'<div class="card-title">(.*?)</div>', block, re.DOTALL)
        if title_m:
            card["title"] = re.sub(r"<[^>]+>", "", title_m.group(1)).strip()

        score_m = re.search(r'<div class="card-score">([\d.]+)\s*<span>/10</span>', block)
        card["score"] = score_m.group(1) if score_m else "5.0"

        link_m = re.search(r'<a href="([^"]+)" target="_blank"[^>]*>↗\s*(?:原文|PDF/原文)</a>', block)
        if link_m:
            card["link"] = link_m.group(1)

        summary_m = re.search(r'<div class="card-body">(.*?)</div>', block, re.DOTALL)
        if summary_m:
            card["summary"] = re.sub(r"<[^>]+>", "", summary_m.group(1)).strip()

        card["has_draft"] = '<div class="card-draft">' in block

        chapter_m = re.search(r"📍\s*([^<\s][^<]*?)(?:</span>|<|&nbsp;|$)", block)
        if chapter_m:
            card["chapter"] = chapter_m.group(1).strip()

        if card.get("title"):
            cards.append(card)

    return cards


def extract_cards_from_html(html_path: Path, report_type: str) -> list[dict]:
    """
    从 HTML 报告中提取卡片信息。
    自动选择 lxml（优先）或正则降级方案。
    """
    if _HAS_LXML:
        return _extract_with_lxml(html_path, report_type)
    else:
        return _extract_with_regex(html_path, report_type)


__all__ = ["extract_cards_from_html"]
