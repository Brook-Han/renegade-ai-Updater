#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
backfill_medium_cards.py

一次性回填：用现有 docs/news/news_report_*.md 重新生成全部 HTML，
使「中相关」条目以 `<article class="card card-medium">` 卡片形式呈现，
从而被 card_utils 提取、进入索引卡片网格。

不触碰 MD、缓存与数据 JSON；只重写 news_report_*.html。
"""
import sys
import traceback
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))

from news_md_to_html import parse_news_report, generate_news_html  # noqa: E402


def main() -> int:
    mds = sorted(BASE.glob("docs/news/news_report_*.md"))
    if not mds:
        print("❌ 未找到 news_report_*.md")
        return 1

    ok = fail = 0
    rows = []
    for md in mds:
        try:
            data = parse_news_report(str(md))
            out = md.with_suffix(".html")
            generate_news_html(data, str(out))
            rows.append((md.name, data["high_n"], data["med_n"], len(data["medium_items"])))
            ok += 1
        except Exception as e:  # noqa: BLE001
            print(f"❌ {md.name}: {e}")
            traceback.print_exc()
            fail += 1

    total_med = sum(r[3] for r in rows)
    empty_med = [r[0] for r in rows if r[3] == 0]
    print(f"✅ 重新生成 {ok} 份 / 失败 {fail} 份")
    print(f"📊 中相关卡片合计: {total_med}")
    if empty_med:
        print(f"⚠️ 无中相关条目的报告 {len(empty_med)} 份（正常，取决于当日预筛选）")
    return 0 if fail == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
