#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
arXiv 预取器（韧性版）——绕过 arxiv.py 库在出口 API 降级时的脆弱性。

背景
----
arXiv 出口 API 偶发间歇性降级：同一时刻可能返回 200 / 429 / 读取超时。
arxiv.py 库内部重试次数少、且不做"成功即缓存"以外的保护，一旦连续 429
就会触发主流程的 5 次指数退避（单关键词最坏 ~15 分钟），31 个关键词最坏
可达 ~10 小时，导致整个雷达无法完成。

策略
----
1. 直接调用 export.arxiv.org API（urllib），完全绕开库。
2. 每个关键词最多重试 N 次，固定间隔 + 抖动，短超时（快失败、快重试）。
3. 成功后立即写入 cache/search_results（键格式与 cache.set_search_cache
   完全一致），主流程 academic_radar.py 便会命中缓存、跳过网络请求。
4. 关键词之间保持节流，避免再次触发 arXiv 限速。

用法
----
    venv/bin/python3 scripts/arxiv_prefetch.py            # 默认 6 次重试
    venv/bin/python3 scripts/arxiv_prefetch.py --retries 10 --timeout 20

注意：本脚本只负责"把真实抓取结果落缓存"，不做任何数据编造或时间戳伪造。
"""
from __future__ import annotations

import argparse
import datetime
import random
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

# 允许从项目根目录导入 config / cache
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from cache import get_search_cache, set_search_cache  # noqa: E402
from config import Config  # noqa: E402

API_URL = "http://export.arxiv.org/api/query"
ATOM = "{http://www.w3.org/2005/Atom}"
USER_AGENT = "renegade-ai-academic-radar/1.0 (mailto:noreply@example.com)"

# 复用的日志器（与主流程一致的格式）
try:
    from logger import setup_logging  # type: ignore

    logger = setup_logging("renegade_radar")
except Exception:  # pragma: no cover - 回退到基础日志
    import logging

    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    logger = logging.getLogger("arxiv_prefetch")


def load_keywords(path: str) -> list[str]:
    """读取关键词文件，跳过注释与空行。"""
    out: list[str] = []
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        out.append(line)
    return out


def _clean(text: str | None) -> str:
    """压缩空白并剔除无法编码的代理字符，保持与主流程 safe_str 语义一致。"""
    if not text:
        return ""
    text = " ".join(text.split())
    return text.encode("utf-8", "ignore").decode("utf-8")


def parse_atom(xml_bytes: bytes) -> list[dict]:
    """把 arXiv Atom 响应解析为主流程期望的 paper dict 列表。"""
    root = ET.fromstring(xml_bytes)
    papers: list[dict] = []
    for entry in root.findall(f"{ATOM}entry"):
        raw_id = (entry.findtext(f"{ATOM}id") or "").strip()
        if not raw_id:
            continue

        title = _clean(entry.findtext(f"{ATOM}title"))
        summary = _clean(entry.findtext(f"{ATOM}summary"))
        published_raw = (entry.findtext(f"{ATOM}published") or "").strip()
        published = "N/A"
        if published_raw:
            try:
                published = datetime.datetime.fromisoformat(
                    published_raw.replace("Z", "+00:00")
                ).isoformat()
            except ValueError:
                published = published_raw

        pdf_url = ""
        for link in entry.findall(f"{ATOM}link"):
            if link.get("title") == "pdf" or link.get("type") == "application/pdf":
                pdf_url = link.get("href") or ""
                break

        authors = [
            _clean(a.findtext(f"{ATOM}name"))
            for a in entry.findall(f"{ATOM}author")
        ]
        authors = [a for a in authors if a]

        papers.append(
            {
                "id": raw_id,
                "title": title,
                "summary": summary,
                "published": published,
                "url": pdf_url,
                "authors": authors,
                "source": "arxiv",
            }
        )
    return papers


def fetch_keyword(keyword: str, retries: int, timeout: float, gap: float) -> list[dict] | None:
    """抓取单个关键词；成功返回论文列表，全部重试失败返回 None。"""
    days_back = getattr(Config, "ACADEMIC_DAYS_BACK", 7)
    cutoff = (datetime.datetime.now() - datetime.timedelta(days=days_back)).strftime("%Y%m%d")
    query = f"({keyword}) AND submittedDate:[{cutoff}000000 TO 99991231235959]"

    params = {
        "search_query": query,
        "start": 0,
        "max_results": Config.MAX_RESULTS_PER_KEYWORD,
        "sortBy": "submittedDate",
        "sortOrder": "descending",
    }
    url = f"{API_URL}?{urllib.parse.urlencode(params)}"

    for attempt in range(1, retries + 1):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                papers = parse_atom(resp.read())
            logger.info(f"   ✅ [{attempt}/{retries}] {len(papers)} 篇")
            return papers
        except urllib.error.HTTPError as e:
            logger.warning(f"   ⚠️ [{attempt}/{retries}] HTTP {e.code}")
        except Exception as e:  # 超时、连接重置、解析异常等
            logger.warning(f"   ⚠️ [{attempt}/{retries}] {type(e).__name__}: {e}")

        if attempt < retries:
            wait = gap * (1 + random.uniform(-0.25, 0.25))
            time.sleep(wait)

    logger.error(f"   ❌ 重试 {retries} 次后仍失败，跳过: {keyword}")
    return None


def main() -> int:
    ap = argparse.ArgumentParser(description="arXiv 韧性预取器")
    ap.add_argument("--retries", type=int, default=6, help="每个关键词最大尝试次数（默认 6）")
    ap.add_argument("--timeout", type=float, default=15.0, help="单次请求超时秒数（默认 15）")
    ap.add_argument("--gap", type=float, default=5.0, help="重试间隔基准秒数（默认 5，带 ±25% 抖动）")
    ap.add_argument("--inter", type=float, default=4.0, help="关键词之间节流秒数（默认 4）")
    ap.add_argument("--force", action="store_true", help="忽略已有缓存，强制重新抓取")
    args = ap.parse_args()

    keywords = load_keywords(Config.KEYWORDS_FILE)
    logger.info(f"📚 arXiv 预取启动：{len(keywords)} 个关键词，最多 {args.retries} 次尝试/关键词")

    ok = cached = failed = 0
    total_papers = 0
    failed_keywords: list[str] = []

    for i, kw in enumerate(keywords, 1):
        if not args.force and get_search_cache("arxiv", kw, "papers") is not None:
            logger.info(f"📦 [{i}/{len(keywords)}] 缓存命中: {kw}")
            cached += 1
            continue

        logger.info(f"🔍 [{i}/{len(keywords)}] 抓取: {kw}")
        papers = fetch_keyword(kw, args.retries, args.timeout, args.gap)
        if papers is None:
            failed += 1
            failed_keywords.append(kw)
        else:
            set_search_cache("arxiv", kw, papers, "papers")
            ok += 1
            total_papers += len(papers)

        if i < len(keywords):
            time.sleep(args.inter)

    logger.info(
        f"📊 arXiv 预取完成：新抓取 {ok} | 缓存命中 {cached} | 失败 {failed} | 论文条目 {total_papers}"
    )
    if failed_keywords:
        logger.warning("⚠️ 失败关键词: " + ", ".join(failed_keywords))
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
