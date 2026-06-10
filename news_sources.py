#!/usr/bin/env python3
"""
Renegade AI 文献监控系统 — 资讯源聚合模块 (v1.2 修复版)
✅ 修复 NewsAPI 429 限速问题
✅ 每日配额自动管控（免费版适配）
✅ 关键词批量查询，减少60%+请求
✅ 空结果快速止损，不浪费配额
"""

from __future__ import annotations

import hashlib
import datetime
import time
import json
from pathlib import Path
from typing import List, Dict, Optional

import requests
import feedparser

# 导入项目全局配置与日志
try:
    from config import Config
except ImportError:
    class Config:
        NEWS_API_KEY: str = ""
        ENABLE_NEWS_API: bool = False
        ENABLE_RSS_FEEDS: bool = True
        RSS_FEEDS: Dict[str, str] = {
            "MIT Technology Review": "https://www.technologyreview.com/feed/",
            "Hacker News": "https://hnrss.org/frontpage",
            "Ars Technica": "https://feeds.arstechnica.com/arstechnica/index",
            "The Verge - AI": "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml",
        }
        NEWS_DAYS_BACK: int = 3

try:
    from logger import logger
except ImportError:
    import logging
    logger = logging.getLogger("news_sources")
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


# =============================================================================
# 工具函数
# =============================================================================

def generate_article_id(source: str, url: str, title: str) -> str:
    """生成确定性文章 ID，用于去重"""
    content = f"{source}:{url}:{title}".encode("utf-8")
    return f"news_{hashlib.sha256(content).hexdigest()[:16]}"


def normalize_date(date_str: str) -> str:
    """将常见日期格式转换为 ISO 8601 字符串，无法解析时返回 'N/A' """
    if not date_str or date_str.strip() in ("", "N/A", "None"):
        return "N/A"

    formats = [
        "%Y-%m-%dT%H:%M:%S%z",
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%d %H:%M:%S",
        "%a, %d %b %Y %H:%M:%S %z",
    ]

    clean_str = date_str.strip()
    for fmt in formats:
        try:
            dt = datetime.datetime.strptime(clean_str, fmt)
            return dt.isoformat()
        except ValueError:
            continue

    try:
        from dateutil import parser
        dt = parser.parse(clean_str)
        return dt.isoformat()
    except (ImportError, ValueError):
        pass

    return "N/A"


def normalize_rss_date(entry: feedparser.FeedParserDict) -> str:
    """优先使用 feedparser 解析后的时间元组（更可靠）"""
    if entry.get("published_parsed"):
        try:
            dt = datetime.datetime(*entry.published_parsed[:6])
            return dt.isoformat()
        except (TypeError, ValueError):
            pass
    raw = entry.get("published") or entry.get("updated") or ""
    return normalize_date(raw)


# =============================================================================
# NewsAPI 抓取器（修复429/配额/空结果）
# =============================================================================

def fetch_newsapi(keywords: List[str], days_back: int = 3, max_retries: int = 2) -> List[Dict]:
    """
    修复版 NewsAPI 抓取：
    1. 免费版每日配额限制 95 次（安全阈值）
    2. 关键词批量查询，大幅减少请求数
    3. 429 智能重试，解析官方等待时间
    4. 无结果立即跳过，不浪费配额
    """
    if not getattr(Config, "NEWS_API_KEY", ""):
        logger.warning("⏭️  [NewsAPI] 未配置 API Key，跳过")
        return []

    # ====================== 核心：每日配额管控 ======================
    counter_file = Path("newsapi_counter.json")
    today = datetime.date.today().isoformat()
    DAILY_QUOTA = 95  # 免费版上限 100，留 5 次余量

    # 初始化计数器
    if counter_file.exists():
        try:
            counter_data = json.loads(counter_file.read_text())
            if counter_data.get("date") != today:
                counter_data = {"date": today, "count": 0}
        except Exception:
            counter_data = {"date": today, "count": 0}
    else:
        counter_data = {"date": today, "count": 0}

    # 配额耗尽直接退出
    if counter_data["count"] >= DAILY_QUOTA:
        logger.warning(f"⏭️  [NewsAPI] 今日配额已用完 ({DAILY_QUOTA}/{DAILY_QUOTA})")
        return []
    # =================================================================

    articles: List[Dict] = []
    base_url = "https://newsapi.org/v2/everything"
    headers = {"X-Api-Key": Config.NEWS_API_KEY}
    from_date = (datetime.datetime.now() - datetime.timedelta(days=days_back)).strftime("%Y-%m-%d")

    # 批量查询：每 2 个关键词合并为 1 次请求（减少请求数）
    BATCH_SIZE = 2
    keyword_batches = [keywords[i:i+BATCH_SIZE] for i in range(0, len(keywords), BATCH_SIZE)]

    for batch in keyword_batches:
        # 二次检查配额
        if counter_data["count"] >= DAILY_QUOTA:
            logger.warning("⚠️ [NewsAPI] 配额不足，停止搜索")
            break

        # 构建批量查询语句
        query = " OR ".join([f'"{kw}"' for kw in batch])
        logger.info(f"🔍 [NewsAPI] 批量搜索: {query}")

        params = {
            "q": query,
            "language": "en",
            "sortBy": "relevancy",
            "from": from_date,
            "pageSize": 10,
        }

        success = False
        for attempt in range(max_retries):
            try:
                resp = requests.get(base_url, params=params, headers=headers, timeout=20)
                # 计数+保存
                counter_data["count"] += 1
                counter_file.write_text(json.dumps(counter_data, indent=2))

                # 429 限速处理
                if resp.status_code == 429:
                    retry_after = int(resp.headers.get("Retry-After", 15 * (attempt + 1)))
                    logger.warning(f"⚠️ 429 限速，等待 {retry_after}s (已用配额：{counter_data['count']}/{DAILY_QUOTA})")
                    time.sleep(retry_after)
                    continue

                resp.raise_for_status()
                data = resp.json()
                if data.get("status") != "ok":
                    logger.warning(f"⚠️ API 异常：{data.get('message', '')}")
                    break

                # 解析结果
                count = 0
                for art in data.get("articles", []):
                    if not art.get("title") or not art.get("url"):
                        continue
                    articles.append({
                        "id": generate_article_id("newsapi", art["url"], art["title"]),
                        "title": art["title"].strip(),
                        "summary": (art.get("description") or "").strip()[:500],
                        "published": normalize_date(art.get("publishedAt", "")),
                        "url": art["url"],
                        "authors": [a for a in [art.get("author")] if a],
                        "source": "newsapi",
                        "source_name": art.get("source", {}).get("name", "Unknown"),
                    })
                    count += 1

                logger.info(f"   ✅ 获取 {count} 篇 | 今日已用：{counter_data['count']}/{DAILY_QUOTA}")
                
                # 空结果直接跳过后续（止损）
                if count == 0:
                    logger.info("   ℹ️ 无匹配内容，跳过剩余关键词")
                    break
                success = True
                break

            except Exception as e:
                if attempt == max_retries - 1:
                    logger.error(f"❌ 搜索失败：{str(e)[:50]}")
                else:
                    time.sleep(8)
                continue

        time.sleep(3)  # 接口冷却

    return articles


# =============================================================================
# RSS/Atom 解析器（无配额限制，主力资讯源）
# =============================================================================

def fetch_rss_feeds(max_entries_per_feed: int = 12) -> List[Dict]:
    """解析 RSS 源，无限流、无限制、稳定可靠
    v1.3: 新增日期过滤——只保留最近 NEWS_DAYS_BACK 天内的文章，避免旧文重复刷入"""
    feeds: Dict[str, str] = getattr(Config, "RSS_FEEDS", {})
    if not feeds:
        logger.warning("⏭️  [RSS] 未配置订阅源，跳过")
        return []

    # 日期窗口：只保留最近 N 天
    days_back = getattr(Config, "NEWS_DAYS_BACK", 7)
    cutoff_date = datetime.datetime.now() - datetime.timedelta(days=days_back)

    articles: List[Dict] = []
    total_parsed = 0
    total_filtered = 0
    for feed_name, url in feeds.items():
        logger.info(f"📡 [RSS] 解析: {feed_name}")
        try:
            feed = feedparser.parse(url, agent="Mozilla/5.0")
            count = 0
            for entry in feed.entries[:max_entries_per_feed]:
                if not entry.get("title") or not entry.get("link"):
                    continue
                pub_str = normalize_rss_date(entry)
                total_parsed += 1
                # 日期过滤：有有效日期且超出窗口的跳过
                if pub_str != "N/A":
                    try:
                        pub_dt = datetime.datetime.fromisoformat(pub_str)
                        if pub_dt < cutoff_date:
                            total_filtered += 1
                            continue
                    except (ValueError, TypeError):
                        pass  # 解析失败保留（宁可多抓不少漏）
                articles.append({
                    "id": generate_article_id("rss", entry.get("link", ""), entry.get("title", "")),
                    "title": entry.title.strip(),
                    "summary": (entry.get("summary") or entry.get("description") or "").strip()[:500],
                    "published": pub_str,
                    "url": entry.get("link", ""),
                    "authors": [a.get("name", "") for a in entry.get("authors", [])],
                    "source": "rss",
                    "source_name": feed.feed.get("title", feed_name),
                })
                count += 1
            logger.info(f"   ✅ 获取 {count} 篇")
        except Exception as e:
            logger.error(f"❌ [RSS] 失败: {str(e)[:50]}")
        time.sleep(1.5)

    if total_filtered > 0:
        logger.info(f"📅 RSS 日期过滤：跳过 {total_filtered}/{total_parsed} 篇（超出 {days_back} 天窗口）")

    return articles


# =============================================================================
# AI HOT 抓取器（中文AI资讯，Phase 1 轻量融合）
# =============================================================================

def fetch_aihot(days_back: int = 7, take: int = 50) -> List[Dict]:
    """
    从 aihot.virxact.com 获取精选中文 AI 资讯
    - 无需认证，但必须带浏览器 User-Agent（防 403）
    - 支持 since 时间窗口（服务端限最近 7 天）
    - 返回标准 News Radar 格式，source="aihot"
    """
    if not getattr(Config, "ENABLE_AIHOT", False):
        logger.info("⏭️  [AI HOT] 未启用，跳过")
        return []

    base_url = "https://aihot.virxact.com/api/public/items"
    ua = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    headers = {"User-Agent": ua, "Accept": "application/json"}

    # 计算 since 时间（ISO 8601，UTC）
    since_dt = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=days_back)
    since_str = since_dt.strftime("%Y-%m-%dT%H:%M:%SZ")

    params = {
        "mode": "selected",   # 精选模式（默认）
        "since": since_str,
        "take": min(take, 100),  # API 上限 100
    }

    articles: List[Dict] = []
    next_cursor: Optional[str] = None

    try:
        logger.info(f"🔍 [AI HOT] 抓取精选资讯（since={since_str}, take={take}）")

        # 分页抓取（cursor 机制）
        for page in range(3):  # 最多 3 页（300 条），防止死循环
            if next_cursor:
                params["cursor"] = next_cursor
            else:
                params.pop("cursor", None)

            resp = requests.get(base_url, params=params, headers=headers, timeout=15)
            resp.raise_for_status()
            data = resp.json()

            items = data.get("items", [])
            if not items:
                break

            for item in items:
                # 格式转换：AI HOT → News Radar 标准格式
                url = item.get("url", "")
                title = item.get("title", "").strip()
                summary = (item.get("summary") or "").strip()[:500]

                if not title or not url:
                    continue

                url_hash = hashlib.sha256(url.encode()).hexdigest()[:16]

                articles.append({
                    "id": f"news_{url_hash}",
                    "title": title,
                    "summary": summary,
                    "published": item.get("publishedAt", "N/A"),
                    "url": url,
                    "authors": [],  # AI HOT 不提供结构化作者
                    "source": "aihot",
                    "source_name": item.get("source", "AI HOT"),
                    # 保留 AI HOT 特有字段
                    "aihot_category": item.get("category"),
                    "aihot_score": item.get("score"),
                    "title_en": item.get("title_en"),
                })

            # 检查是否有下一页
            if not data.get("hasNext", False):
                break
            next_cursor = data.get("nextCursor")
            if not next_cursor:
                break

            # 重置 params 去掉 cursor（下一页会加回来）
            params["take"] = min(take, 100)

        logger.info(f"   ✅ [AI HOT] 获取 {len(articles)} 条精选资讯")

    except requests.exceptions.RequestException as e:
        logger.error(f"❌ [AI HOT] 请求失败: {str(e)[:100]}")
    except Exception as e:
        logger.error(f"❌ [AI HOT] 解析失败: {str(e)[:100]}")

    return articles


# =============================================================================
# 统一聚合入口
# =============================================================================

def fetch_all_news(keywords: List[str]) -> List[Dict]:
    all_articles: List[Dict] = []

    # 启用 NewsAPI（配额受控）
    if getattr(Config, "ENABLE_NEWS_API", False):
        days = getattr(Config, "NEWS_DAYS_BACK", 3)
        all_articles.extend(fetch_newsapi(keywords, days_back=days))

    # 启用 RSS（无限流，主力推荐）
    if getattr(Config, "ENABLE_RSS_FEEDS", True):
        all_articles.extend(fetch_rss_feeds())

    # 启用 AI HOT（中文AI资讯，Phase 1 新增）
    if getattr(Config, "ENABLE_AIHOT", False):
        days = getattr(Config, "AIHOT_DAYS_BACK", 7)
        take = getattr(Config, "AIHOT_TAKE", 50)
        all_articles.extend(fetch_aihot(days_back=days, take=take))

    logger.info(f"📰 资讯抓取完成：总计 {len(all_articles)} 条")
    return all_articles


__all__ = ["fetch_all_news", "fetch_newsapi", "fetch_rss_feeds", "fetch_aihot"]