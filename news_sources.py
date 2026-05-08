#!/usr/bin/env python3
"""
Renegade AI 文献监控系统 — 资讯源聚合模块 (v1.1)
功能:
- 支持 NewsAPI 结构化新闻检索，带指数退避重试
- 支持 RSS/Atom 订阅源解析
- 输出格式与论文抓取模块完全兼容 (id, title, summary, published, url, ...)
- 内置日期解析兼容性增强
"""

from __future__ import annotations

import hashlib
import datetime
import time
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
        NEWS_DAYS_BACK: int = 7

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
# NewsAPI 抓取器
# =============================================================================

# 完整修改版 news_sources.py（核心部分）
def fetch_newsapi(keywords: List[str], days_back: int = 7,
                  max_retries: int = 3, max_requests_per_day: int = 95) -> List[Dict]:
    """
    通过 NewsAPI 检索新闻，增强版：
    1. 每日请求配额控制（预留5次余量）
    2. 智能解析 Retry-After 头（精确等待）
    3. 空结果快速跳过（避免浪费配额）
    4. 关键词批量合并（减少请求数）
    """
    if not getattr(Config, "NEWS_API_KEY", ""):
        logger.warning("⏭️  [NewsAPI] 未配置 API Key，跳过")
        return []

    # 全局请求计数器（跨进程可用文件存储）
    import json
    from pathlib import Path
    counter_file = Path("newsapi_counter.json")
    today = datetime.date.today().isoformat()
    
    # 初始化/重置计数器
    if not counter_file.exists():
        counter_data = {"date": today, "count": 0}
    else:
        counter_data = json.loads(counter_file.read_text())
        if counter_data["date"] != today:
            counter_data = {"date": today, "count": 0}
    
    if counter_data["count"] >= max_requests_per_day:
        logger.warning(f"⏭️  [NewsAPI] 今日配额已达上限 ({max_requests_per_day}/day)，跳过")
        return []

    articles: List[Dict] = []
    base_url = "https://newsapi.org/v2/everything"
    headers = {"X-Api-Key": Config.NEWS_API_KEY}
    from_date = (datetime.datetime.now() - datetime.timedelta(days=days_back)).strftime("%Y-%m-%d")

    # 优化1：关键词批量合并（每3个关键词合并一次请求，减少请求数）
    BATCH_SIZE = 3
    keyword_batches = [keywords[i:i+BATCH_SIZE] for i in range(0, len(keywords), BATCH_SIZE)]
    
    for batch_idx, batch in enumerate(keyword_batches):
        if counter_data["count"] >= max_requests_per_day:
            logger.warning("⚠️  [NewsAPI] 配额即将耗尽，停止请求")
            break
            
        batch_query = " OR ".join([f'"{kw}"' for kw in batch])  # 精确匹配短语
        logger.info(f"🔍 [NewsAPI] 批量搜索 ({batch_idx+1}/{len(keyword_batches)}): {batch_query}")
        
        params = {
            "q": batch_query,
            "language": "en",
            "sortBy": "relevancy",
            "from": from_date,
            "pageSize": 15,
        }

        success = False
        for attempt in range(max_retries):
            try:
                # 检查配额
                if counter_data["count"] >= max_requests_per_day:
                    break
                    
                resp = requests.get(base_url, params=params, headers=headers, timeout=30)
                counter_data["count"] += 1
                counter_file.write_text(json.dumps(counter_data))
                
                if resp.status_code == 429:
                    # 优化2：解析 Retry-After 头（精确等待）
                    retry_after = int(resp.headers.get("Retry-After", 10*(attempt+1)))
                    logger.warning(f"⚠️  [NewsAPI] 429 限速，等待 {retry_after}s 后重试...")
                    time.sleep(retry_after)
                    continue
                    
                resp.raise_for_status()
                data = resp.json()
                
                if data.get("status") != "ok":
                    logger.warning(f"⚠️  [NewsAPI] 返回异常: {data.get('message')}")
                    break

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
                
                # 优化3：空结果跳过后续批量（节省配额）
                if count == 0:
                    logger.info(f"   ⚠️  无匹配结果，跳过剩余{len(keyword_batches)-batch_idx-1}个批量")
                    break
                    
                logger.info(f"   ✅ 获取 {count} 篇 | 今日已用: {counter_data['count']}/{max_requests_per_day}")
                success = True
                break

            except requests.exceptions.RequestException as e:
                if attempt == max_retries - 1:
                    logger.error(f"❌ [NewsAPI] 搜索失败 [{batch_query}]: {e}")
                else:
                    wait = 5*(attempt+1)
                    logger.warning(f"⚠️  [NewsAPI] 请求错误，{wait}s后重试: {e}")
                    time.sleep(wait)
                continue
            except Exception as e:
                logger.error(f"❌ [NewsAPI] 未知错误 [{batch_query}]: {e}")
                break

        # 优化4：动态调整冷却时间（根据配额剩余）
        remaining = max_requests_per_day - counter_data["count"]
        cool_down = 5 if remaining > 30 else 10 if remaining > 10 else 20
        time.sleep(cool_down)

    return articles


# =============================================================================
# RSS/Atom 解析器
# =============================================================================

def fetch_rss_feeds(max_entries_per_feed: int = 10) -> List[Dict]:
    """解析配置的所有 RSS/Atom 源，返回标准化文章列表"""
    feeds: Dict[str, str] = getattr(Config, "RSS_FEEDS", {})
    if not feeds:
        logger.warning("⏭️  [RSS] 未配置订阅源，跳过")
        return []

    articles: List[Dict] = []
    for feed_name, url in feeds.items():
        logger.info(f"📡 [RSS] 正在解析: {feed_name}")
        try:
            feed = feedparser.parse(url, agent="RenegadeAI-Updater/1.0")
            if feed.bozo and feed.bozo_exception:
                logger.debug(f"   ⚠️  {feed_name} 解析警告: {feed.bozo_exception}")

            count = 0
            for entry in feed.entries[:max_entries_per_feed]:
                if not entry.get("title") or not entry.get("link"):
                    continue
                articles.append({
                    "id": generate_article_id("rss", entry.get("link", ""), entry.get("title", "")),
                    "title": entry.title.strip(),
                    "summary": (entry.get("summary") or entry.get("description") or "").strip()[:500],
                    "published": normalize_rss_date(entry),
                    "url": entry.get("link", ""),
                    "authors": [a.get("name", "") for a in entry.get("authors", [])],
                    "source": "rss",
                    "source_name": feed.feed.get("title", feed_name),
                })
                count += 1
            logger.info(f"   ✅ 获取 {count} 篇")

        except Exception as e:
            logger.error(f"❌ [RSS] 解析失败 [{feed_name}]: {e}")

        time.sleep(1)

    return articles


# =============================================================================
# 统一聚合入口
# =============================================================================

def fetch_all_news(keywords: List[str]) -> List[Dict]:
    """聚合所有可用资讯源 (NewsAPI + RSS)，返回标准化文章列表"""
    all_articles: List[Dict] = []

    if getattr(Config, "ENABLE_NEWS_API", False):
        days = getattr(Config, "NEWS_DAYS_BACK", 7)
        all_articles.extend(fetch_newsapi(keywords, days_back=days))

    if getattr(Config, "ENABLE_RSS_FEEDS", False):
        all_articles.extend(fetch_rss_feeds())

    logger.info(f"📰 资讯源共抓取 {len(all_articles)} 篇")
    return all_articles


__all__ = ["fetch_all_news", "fetch_newsapi", "fetch_rss_feeds"]