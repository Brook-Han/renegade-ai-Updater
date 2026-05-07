#!/usr/bin/env python3
"""
Renegade AI 文献监控系统 — 资讯源聚合模块 (v1.1)

功能:
- 支持 NewsAPI 结构化新闻检索，带指数退避重试
- 支持 RSS/Atom 订阅源解析
- 输出格式与论文抓取模块完全兼容 (id, title, summary, published, url, ...)
- 内置日期解析兼容性增强

使用前:
  1. 确保已安装依赖: pip install feedparser requests
  2. 在 config.py 中配置:
     - NEWS_API_KEY: str            # NewsAPI 密钥 (免费版: https://newsapi.org)
     - ENABLE_NEWS_API: bool        # 是否启用 NewsAPI
     - ENABLE_RSS_FEEDS: bool       # 是否启用 RSS
     - RSS_FEEDS: dict[str, str]    # {名称: 订阅地址}
     - NEWS_DAYS_BACK: int          # NewsAPI 回溯天数 (默认 7)
"""

from __future__ import annotations

import hashlib
import datetime
import time
from typing import List, Dict, Optional

import requests
import feedparser

# 尝试导入项目全局配置与日志，如未配置则使用内置 fallback
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

    # 常见格式，按出现频率排序
    formats = [
        "%Y-%m-%dT%H:%M:%S%z",      # 2024-01-01T12:00:00+00:00
        "%Y-%m-%dT%H:%M:%SZ",       # 2024-01-01T12:00:00Z
        "%Y-%m-%d %H:%M:%S",        # 2024-01-01 12:00:00
        "%a, %d %b %Y %H:%M:%S %z", # RSS 常见格式
    ]

    clean_str = date_str.strip()
    # 移除末尾可能多余的时区冒号 "2024-01-01T12:00:00+00:00" 有时写成 +0000
    if clean_str.endswith("Z") or clean_str.endswith("z"):
        # 标准 ISO 或带 Z 的格式已在 formats 中尝试
        pass

    for fmt in formats:
        try:
            dt = datetime.datetime.strptime(clean_str, fmt)
            return dt.isoformat()
        except ValueError:
            continue

    # 最后尝试用 dateutil 解析（如果可用）
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

def fetch_newsapi(keywords: List[str], days_back: int = 7,
                  max_retries: int = 3) -> List[Dict]:
    """
    通过 NewsAPI 检索新闻。
    - 自动处理 429 限速 (指数退避重试)
    - 单关键词结果最多返回 Config 中设置的条数 (默认 15)
    """
    if not getattr(Config, "NEWS_API_KEY", ""):
        logger.warning("⏭️  [NewsAPI] 未配置 API Key，跳过")
        return []

    articles: List[Dict] = []
    base_url = "https://newsapi.org/v2/everything"
    headers = {"X-Api-Key": Config.NEWS_API_KEY}
    from_date = (datetime.datetime.now() - datetime.timedelta(days=days_back)).strftime("%Y-%m-%d")

    for kw in keywords:
        logger.info(f"🔍 [NewsAPI] 正在搜索: {kw}")
        params = {
            "q": kw,
            "language": "en",
            "sortBy": "relevancy",
            "from": from_date,
            "pageSize": 15,  # 可通过 Config 调整
        }

        for attempt in range(max_retries):
            try:
                resp = requests.get(base_url, params=params,
                                    headers=headers, timeout=30)
                if resp.status_code == 429:
                    wait = 10 * (attempt + 1)
                    logger.warning(f"⚠️  [NewsAPI] 429 限速，等待 {wait}s 后重试...")
                    time.sleep(wait)
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
                logger.info(f"   ✅ 获取 {count} 篇")
                break  # 成功，跳出重试循环

            except requests.exceptions.RequestException as e:
                if attempt == max_retries - 1:
                    logger.error(f"❌ [NewsAPI] 搜索失败 [{kw}]: {e}")
                else:
                    logger.warning(f"⚠️  [NewsAPI] 请求错误，等待后重试: {e}")
                    time.sleep(5)
                continue
            except Exception as e:
                logger.error(f"❌ [NewsAPI] 未知错误 [{kw}]: {e}")
                break

        # 关键词间冷却，遵守免费版限制
        time.sleep(2)

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
            # 设置 user-agent 以避免某些源的拒绝
            feed = feedparser.parse(url,
                                    agent="RenegadeAI-Updater/1.0")
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

        # 避免对源站造成冲击
        time.sleep(1)

    return articles


# =============================================================================
# 统一聚合入口
# =============================================================================

def fetch_all_news(keywords: List[str]) -> List[Dict]:
    """
    聚合所有可用资讯源 (NewsAPI + RSS)，返回标准化文章列表。
    输出格式:
    [
        {
            "id": str,          # 唯一标识
            "title": str,
            "summary": str,     # 截断至 500 字符
            "published": str,   # ISO 8601 或 "N/A"
            "url": str,
            "authors": List[str],
            "source": "newsapi"|"rss",
            "source_name": str,
        },
        ...
    ]
    """
    all_articles: List[Dict] = []

    # 1. NewsAPI
    if getattr(Config, "ENABLE_NEWS_API", False):
        days = getattr(Config, "NEWS_DAYS_BACK", 7)
        all_articles.extend(fetch_newsapi(keywords, days_back=days))

    # 2. RSS Feeds
    if getattr(Config, "ENABLE_RSS_FEEDS", False):
        all_articles.extend(fetch_rss_feeds())

    logger.info(f"📰 资讯源共抓取 {len(all_articles)} 篇")
    return all_articles


# 暴露给外部使用的公共接口
__all__ = [
    "fetch_all_news",
    "fetch_newsapi",
    "fetch_rss_feeds",
    "generate_article_id",
    "normalize_date",
]