#!/usr/bin/env python3
"""
Renegade AI 文献监控系统 — 资讯源聚合模块 (v1.0)

功能:
- 支持 NewsAPI 结构化新闻检索
- 支持 RSS/Atom 订阅源解析
- 自动标准化输出格式，无缝对接主脚本分析流水线
- 内置限速保护、错误重试、日期标准化

依赖:
  pip install feedparser requests
"""

from __future__ import annotations

import time
import hashlib
import datetime
from typing import Optional

import requests
import feedparser

from config import Config
from logger import logger


# =============================================================================
# 工具函数
# =============================================================================

def generate_article_id(source: str, url: str, title: str) -> str:
    """生成确定性文章 ID，用于主脚本去重"""
    content = f"{source}:{url}:{title}".encode("utf-8")
    return f"news_{hashlib.sha256(content).hexdigest()[:16]}"


def normalize_date(date_str: str) -> str:
    """将多种日期格式统一为 ISO 8601"""
    if not date_str or date_str.strip() in ("", "N/A", "None"):
        return "N/A"
    
    # 常见格式列表
    formats = [
        "%Y-%m-%dT%H:%M:%S%z",
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%d %H:%M:%S",
        "%a, %d %b %Y %H:%M:%S %z",
    ]
    for fmt in formats:
        try:
            dt = datetime.datetime.strptime(date_str.strip(), fmt)
            return dt.isoformat()
        except ValueError:
            continue
    return "N/A"


def normalize_rss_date(entry: feedparser.FeedParserDict) -> str:
    """优先使用 feedparser 解析后的时间元组，提高准确性"""
    if entry.get("published_parsed"):
        try:
            dt = datetime.datetime(*entry.published_parsed[:6])
            return dt.isoformat()
        except (TypeError, ValueError):
            pass
    return normalize_date(entry.get("published") or entry.get("updated") or "")


# =============================================================================
# NewsAPI 抓取器
# =============================================================================

def fetch_newsapi(keywords: list[str], days_back: int = 7) -> list[dict]:
    """
    通过 NewsAPI 检索近期新闻
    免费版限制: 100 请求/天，需控制调用频率
    """
    if not Config.NEWS_API_KEY:
        logger.warning("⏭️  [NewsAPI] 未配置 API Key，跳过")
        return []
    
    articles = []
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
            "pageSize": 10,
            "pageSize": 15  # 控制单次返回量
        }
        
        try:
            resp = requests.get(base_url, params=params, headers=headers, timeout=30)
            
            # 简单限速处理
            if resp.status_code == 429:
                logger.warning("⚠️ [NewsAPI] 触发限速，等待 60s")
                time.sleep(60)
                resp = requests.get(base_url, params=params, headers=headers, timeout=30)
            
            resp.raise_for_status()
            data = resp.json()
            
            if data.get("status") != "ok":
                logger.warning(f"⚠️ [NewsAPI] 返回异常: {data.get('message')}")
                continue
                
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
            
        except Exception as e:
            logger.error(f"❌ [NewsAPI] 搜索失败 [{kw}]: {e}")
        
        # 免费版严格限速，关键词间强制冷却
        time.sleep(3)
        
    return articles


# =============================================================================
# RSS/Atom 解析器
# =============================================================================

def fetch_rss_feeds(max_entries: int = 10) -> list[dict]:
    """
    解析预置的 RSS/Atom 订阅源
    """
    feeds = getattr(Config, "RSS_FEEDS", {})
    if not feeds:
        logger.warning("⏭️  [RSS] 未配置订阅源，跳过")
        return []
    
    articles = []
    for feed_name, url in feeds.items():
        logger.info(f"📡 [RSS] 正在解析: {feed_name}")
        try:
            feed = feedparser.parse(url)
            if feed.bozo and feed.bozo_exception:
                logger.debug(f"   ⚠️ {feed_name} 解析警告: {feed.bozo_exception}")
                
            count = 0
            for entry in feed.entries[:max_entries]:
                if not entry.get("title") or not entry.get("link"):
                    continue
                    
                articles.append({
                    "id": generate_article_id("rss", entry.get("link", ""), entry.get("title", "")),
                    "title": entry.title.strip(),
                    "summary": (entry.get("summary") or entry.get("description") or "").strip()[:500],
                    "published": normalize_rss_date(entry),
                    "url": entry.get("link", ""),
                    "authors": [a.name for a in entry.get("authors", [])],
                    "source": "rss",
                    "source_name": feed.feed.get("title", feed_name),
                })
                count += 1
            logger.info(f"   ✅ 获取 {count} 篇")
            
        except Exception as e:
            logger.error(f"❌ [RSS] 解析失败 [{feed_name}]: {e}")
        time.sleep(1)  # 避免对源站造成压力
        
    return articles


# =============================================================================
# 统一入口
# =============================================================================

def fetch_all_news(keywords: list[str]) -> list[dict]:
    """
    聚合所有资讯源，返回标准化文章列表
    格式与 arXiv/S2 抓取结果完全兼容，可直接送入 deduplicate_papers
    """
    all_articles = []
    
    # 1. NewsAPI
    if getattr(Config, "ENABLE_NEWS_API", False):
        days = getattr(Config, "NEWS_DAYS_BACK", 7)
        all_articles.extend(fetch_newsapi(keywords, days_back=days))
        
    # 2. RSS Feeds
    if getattr(Config, "ENABLE_RSS_FEEDS", False):
        all_articles.extend(fetch_rss_feeds())
        
    logger.info(f"📰 资讯源共抓取 {len(all_articles)} 篇")
    return all_articles


# 快捷导出
__all__ = ["fetch_all_news", "fetch_newsapi", "fetch_rss_feeds"]