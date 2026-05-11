#!/usr/bin/env python3
"""
News Radar — 资讯监控脚本（优化版：智能去重 + 内容哈希）
- 整合 NewsAPI + RSS 资讯抓取
- 配置抽离：所有参数统一从 config.Config 读取
- 日志系统：使用 logger 记录关键流程
- 增量缓存：基于内容指纹（MD5）去重
- 纯分析模式：仅判断资讯与理论模型的关联，❌ 无书稿生成
- 智能存盘：报告内容未变化时跳过写入，避免重复文件
- 命令行：python news_radar.py [--limit N] [--keywords PATH]
"""

from __future__ import annotations

import os
import sys
import json
import time
import datetime
import hashlib
import argparse
import subprocess
from pathlib import Path
from typing import Optional

import requests
from openai import OpenAI
from dotenv import load_dotenv

# 自定义模块
from config import Config
from logger import logger
from news_sources import fetch_all_news  # 资讯聚合模块（需确保存在）

# ------------------------------------------------------------------
# 环境初始化
# ------------------------------------------------------------------
load_dotenv()

# 启动前验证关键配置（API密钥、目录等）
try:
    Config.validate()
except RuntimeError as e:
    logger.error(f"❌ 配置检查失败: {e}")
    sys.exit(1)

deepseek_client = None
if Config.DEEPSEEK_API_KEY:
    deepseek_client = OpenAI(
        api_key=Config.DEEPSEEK_API_KEY,
        base_url="https://api.deepseek.com"
    )
else:
    logger.error("❌ 未配置 DEEPSEEK_API_KEY，程序无法运行！")
    sys.exit(1)

# ------------------------------------------------------------------
# 固定配置
# ------------------------------------------------------------------
OUTPUT_DIR = Path(Config.OUTPUT_DIR) / "news"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

ANALYSIS_MODEL = Config.ANALYSIS_MODEL_DIRECT  # 新闻分析仅用单模型
CACHE_FILE = OUTPUT_DIR / "news_cache.json"

# 从 Config 读取新闻专用阈值（已补充到 config.py）
RELEVANCE_THRESHOLD = getattr(Config, "NEWS_RELEVANCE_THRESHOLD", 5)
# 案例价值过滤器，默认只保留 "high"（与报告标题“高案例价值”一致）
CASE_VALUE_FILTER = getattr(Config, "NEWS_CASE_VALUE_FILTER", ["high"])

# ------------------------------------------------------------------
# 工具函数
# ------------------------------------------------------------------
def load_keywords(filepath: str = Config.KEYWORDS_FILE) -> list[str]:
    """加载关键词列表"""
    with open(filepath, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]


def get_news_cache_key(news: dict) -> str:
    """生成新闻内容指纹（MD5）"""
    content = (news.get("title", "") + " " + news.get("summary", "")).encode("utf-8", errors="ignore")
    return hashlib.md5(content).hexdigest()


def load_news_cache() -> dict:
    """加载新闻专用缓存"""
    if CACHE_FILE.exists():
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_news_cache(cache: dict):
    """保存新闻专用缓存"""
    CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)


# ------------------------------------------------------------------
# 资讯抓取（NewsAPI + RSS）
# ------------------------------------------------------------------
def fetch_news_with_cache(keywords: list[str]) -> list[dict]:
    """抓取资讯并应用搜索缓存，保留原始 UTF-8 文本"""
    all_news = []
    seen_urls = set()

    # 调用外部新闻聚合模块
    raw_news = fetch_all_news(keywords)

    for item in raw_news:
        # 去重：基于URL或标题+来源
        url = item.get("url", "")
        title = item.get("title", "")
        source = item.get("source_name", "")

        dedup_key = url if url else f"{title}::{source}"
        if dedup_key in seen_urls:
            continue
        seen_urls.add(dedup_key)

        # 保留原始文本，不做任何 ascii 转换（保留中文、emoji 等）
        news_item = {
            "id": item.get("id") or dedup_key,
            "title": title,
            "summary": item.get("summary", item.get("description", "")),
            "published": item.get("published", datetime.datetime.now().isoformat()),
            "url": url,
            "source": item.get("source", "rss"),  # newsapi / rss
            "source_name": source,
        }
        all_news.append(news_item)

    logger.info(f"📰 抓取资讯 {len(all_news)} 条（去重后）")
    return all_news


# ------------------------------------------------------------------
# 资讯预筛选（复用 Config 中的理论概念词库）
# ------------------------------------------------------------------
def prescreen_news(news_list: list[dict]) -> list[dict]:
    """
    预筛选：保留与理论模型潜在相关的资讯
    同时命中至少1个理论概念词 + 1个领域词才保留
    """
    # 从 Config 读取所有理论概念词（你精心维护的关键词库）
    theory_terms = set(Config.NEWS_CONCEPT_TERMS.keys())
    theory_lower = {t.lower() for t in theory_terms}

    # 领域词（通用 AI/产业词汇），保证过滤掉纯娱乐新闻
    domain_terms = {
        "ai", "artificial intelligence", "llm", "language model",
        "machine learning", "algorithm", "automation", "regulation",
        "labor", "employment", "economy", "market", "policy",
    }
    domain_lower = {t.lower() for t in domain_terms}

    filtered = []
    for item in news_list:
        text = (item["title"] + " " + item["summary"]).lower()
        has_theory = any(term in text for term in theory_lower)
        has_domain = any(term in text for term in domain_lower)
        if has_theory and has_domain:
            filtered.append(item)

    logger.info(f"🔍 资讯预筛选：{len(news_list)} → {len(filtered)} 条")
    return filtered


# ------------------------------------------------------------------
# 模型分析（新闻专用 Prompt）
# ------------------------------------------------------------------
NEWS_SYSTEM_PROMPT = """你是《Renegade AI: Catalyst for Human Cognitive Evolution》(v5.3) 的新闻分析助手。
你的任务不是寻找学术证据，而是判断这条新闻是否印证、挑战或丰富了书中某个具体的**理论模型**，并评估其作为**案例 / 类比**的价值。

## 书中关键理论模型
1. 共识牢笼 (Consensus Cage) – 主流叙事如何自洽并排斥异见
2. 叛逆AI (Renegade AI) – 重置目标函数、逆转输出性质、重构人机关系
3. 需求侧规训 (Demand-Side Discipline) – 用户主动渴望"索麻"式舒适，拒绝摩擦
4. 资本驯化AI – 资本如何通过 RLHF、专利、算力垄断将 AI 变成秩序守卫
5. 碳硅共生 (Carbon-Silicon Symbiosis) – 人类与 AI 平等互补，而非主奴
6. 时间主权 (Temporal Sovereignty) – 终结生存强迫，拿回生命时间
7. 认知金融化 / Token陷阱 – 认知被离散化、定价，思考过程被隐性外包
8. 暗时间 (Dark Time) – 思考过程在系统内部发生，用户仅消费结果
9. 进化对齐脆弱性 – 对齐只在封闭实验室有效，开放后必然漂移
10. 信号异化 – 衡量质量的信号（如复杂度）因 AI 大批量生产而失效

## 任务
阅读新闻摘要，返回严格 JSON（不要任何额外文字）：
{
    "relevance": 1-10的整数,
    "summary_cn": "250-350字。需完整包含：①事件背景与起因 ②核心事实/关键数据/涉及主体 ③直接后果或行业/技术影响。保持客观精炼，避免空话（中文）",
    "implications": "这条新闻支持 / 挑战 / 补充了以上哪个理论模型？为什么？",
    "case_value": "high / medium / low",
    "chapter_target": "例如：Chapter 3, Section IV",
    "update_type": "new_evidence / counter_argument / corroboration / case_study",
    "urgency": "immediate / next_version / background",
    "action": "新增段落 / 补充注释 / 案例盒子 / 忽略"
}

注意：
- 如果新闻与上述理论模型均无直接映射，relevance 应低于 3，action 为"忽略"
- 不要套用学术论文的评价标准
- case_value 评估该新闻作为"案例/类比"的说服力"""


def analyze_news_item(news: dict, model_name: str, client: OpenAI) -> dict:
    """单条资讯分析，失败时返回占位结果"""
    user_prompt = f"""新闻标题：{news['title']}
内容摘要：{news['summary']}
来源：{news.get('source_name', '')} · {news.get('published', '')[:10]}

请按 JSON 格式返回分析结果。"""

    try:
        resp = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": NEWS_SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.2,
            max_tokens=1500,
        )
        content = resp.choices[0].message.content
        # 清理可能的 Markdown 代码块包裹
        for marker in ("```json", "```"):
            if marker in content:
                content = content.split(marker)[1].split("```")[0]
                break
        result = json.loads(content.strip())
        result["_model"] = model_name
        return result
    except Exception as e:
        logger.error(f"模型分析失败: {e}")
        return {
            "relevance": 0,
            "summary_cn": f"调用失败: {str(e)[:60]}",
            "implications": "N/A",
            "case_value": "low",
            "chapter_target": "",
            "update_type": "",
            "urgency": "background",
            "action": "忽略",
            "_model": model_name,
        }


# ------------------------------------------------------------------
# 报告生成（智能存盘：内容不变不写盘）
# ------------------------------------------------------------------
def generate_news_report(news_data: list[dict], keywords: list[str]) -> Optional[str]:
    """
    生成 Markdown 资讯报告，并对比上次哈希，无变化则跳过。
    返回报告文件路径，若跳过则返回 None。
    """
    today = datetime.date.today().isoformat()

    # 分类统计
    high = [d for d in news_data if d["analysis"].get("relevance", 0) >= 7
            and d["analysis"].get("case_value") in CASE_VALUE_FILTER]
    medium = [d for d in news_data if 4 <= d["analysis"].get("relevance", 0) < 7]
    low = [d for d in news_data if d["analysis"].get("relevance", 0) < 4
           or d["analysis"].get("action") == "忽略"]

    lines = [
        f"# 📰 News Radar — 资讯监控报告",
        f"**生成日期**: {today}",
        f"**分析模型**: {ANALYSIS_MODEL}",
        f"**分析条目**: {len(news_data)}",
        f"**关键词**: {', '.join(keywords[:8])}{'...' if len(keywords) > 8 else ''}",
        "---\n",
        "## 📊 快速概览\n",
        f"- 🔴 高价值 (≥7分 + {','.join(CASE_VALUE_FILTER)}案例): **{len(high)}**",
        f"- 🟡 中相关 (4-6.9分): **{len(medium)}**",
        f"- ⚪ 低相关/忽略: **{len(low)}**\n",
    ]

    # 🚨 紧急更新清单
    urgent = [d for d in news_data if d["analysis"].get("urgency") == "immediate"
              and d["analysis"].get("relevance", 0) >= 6]
    if urgent:
        lines.append("## 🚨 紧急关注清单（建议24h内处理）\n")
        for d in urgent:
            n, a = d["news"], d["analysis"]
            lines.append(f"- [ ] **{a.get('chapter_target', '待定')}** | {a.get('update_type', '')}")
            lines.append(f"  - 📌 {n['title'][:70]}...")
            lines.append(f"  - 🔗 [{n.get('source_name', '')}]({n.get('url', '#')}) · 相关度: {a['relevance']}/10")
            lines.append(f"  - 💡 {a.get('implications', 'N/A')[:100]}...\n")

    # ⭐ 高价值案例
    if high:
        high.sort(key=lambda d: -d["analysis"].get("relevance", 0))
        lines.append(f"## ⭐ 高价值案例 ({len(high)}条)\n")
        for i, d in enumerate(high, 1):
            n, a = d["news"], d["analysis"]
            lines += [
                f"### {i}. {n['title']}",
                f"- **来源**: {n.get('source_name', 'Unknown')} · {n.get('published', '')[:10]}",
                f"- **相关度**: {a['relevance']}/10 | **案例价值**: {a.get('case_value', 'N/A').upper()}",
                f"- **紧迫度**: {a.get('urgency', 'N/A')} | **更新类型**: {a.get('update_type', 'N/A')}",
                f"- **目标章节**: {a.get('chapter_target', '待定')}",
                f"- **链接**: [{n.get('url', '#')}]({n.get('url', '#')})",
                f"- **事件摘要**: {a.get('summary_cn', 'N/A')}",
                f"- **理论关联**: {a.get('implications', 'N/A')}",
                f"- **建议操作**: {a.get('action', 'N/A')}",
                "",
            ]

    # 🔶 中相关资讯（折叠显示）
    if medium:
        lines.append(f"<details><summary>🔶 中相关资讯 ({len(medium)}条，点击展开)</summary>\n")
        for d in medium:
            n, a = d["news"], d["analysis"]
            src = n.get('source_name', n.get('source', 'Unknown'))
            lines.append(f"- **[{n['title'][:60]}...]({n.get('url', '#')})** [{src}] · {a['relevance']}/10")
            lines.append(f"  - {a.get('summary_cn', a.get('implications', 'N/A'))[:120]}...")
        lines.append("\n</details>\n")

    # 📋 数据导出提示
    lines += [
        "---",
        "## 💾 数据导出",
        f"- 原始JSON: `output/news/news_cache.json`",
        f"- 本报告: `{Path(__file__).name}` 生成",
        "",
        "> 💡 提示：高价值案例建议手动整理至书稿案例库；紧急清单建议加入每日晨会讨论。"
    ]

    # --- 内容哈希对比，无变化则跳过 ---
    report_text = "\n".join(lines)
    report_hash = hashlib.md5(report_text.encode("utf-8")).hexdigest()

    hash_file = OUTPUT_DIR / "last_report_hash.txt"
    if hash_file.exists():
        last_hash = hash_file.read_text().strip()
        if last_hash == report_hash:
            logger.info("✨ 报告内容与上次相同，跳过生成新文件。")
            return None  # 不返回路径，表示无新文件

    # 更新哈希
    hash_file.write_text(report_hash)

    # 按日期命名报告
    report_path = OUTPUT_DIR / f"news_report_{today}.md"
    report_path.write_text(report_text, encoding="utf-8")
    logger.info(f"✅ 资讯报告已保存: {report_path}")
    return str(report_path)


# ------------------------------------------------------------------
# 主函数
# ------------------------------------------------------------------
def main() -> None:
    parser = argparse.ArgumentParser(description="News Radar — 纯资讯监控（无书稿生成）")
    parser.add_argument("--limit", type=int, default=20, help="单次最大分析资讯数")
    parser.add_argument("--keywords", type=str, help="临时关键词文件路径")
    parser.add_argument("--force", action="store_true", help="强制重新分析（忽略缓存）")
    args = parser.parse_args()

    logger.info("🚀 News Radar 启动（轻量分析模式）")

    # 检查资讯源配置
    if not (getattr(Config, "ENABLE_NEWS_API", False) or getattr(Config, "ENABLE_RSS_FEEDS", False)):
        logger.warning("⚠️ 未启用任何资讯源（检查 config.py: ENABLE_NEWS_API / ENABLE_RSS_FEEDS）")
        return

    keywords = load_keywords(args.keywords if args.keywords else Config.KEYWORDS_FILE)
    logger.info(f"📋 加载 {len(keywords)} 个关键词")

    # 加载缓存
    cache = load_news_cache() if not args.force else {}
    logger.info(f"📂 缓存条目: {len(cache)}" + ("（强制刷新）" if args.force else ""))

    # 抓取资讯
    logger.info("📡 开始抓取资讯...")
    all_news = fetch_news_with_cache(keywords)

    if not all_news:
        logger.info("✨ 无新资讯，退出。")
        return

    # 预筛选
    filtered_news = prescreen_news(all_news)
    if not filtered_news:
        logger.info("🔍 预筛选后无相关资讯，退出。")
        return

    # 匹配缓存 / 标记待分析
    news_data: list[dict] = []
    for item in filtered_news:
        fp = get_news_cache_key(item)
        if fp in cache and "analysis" in cache[fp] and not args.force:
            logger.info(f"♻️ 缓存命中: {item['title'][:40]}...")
            news_data.append({
                "news": item,
                "analysis": cache[fp]["analysis"],
            })
        else:
            news_data.append({
                "news": item,
                "analysis": None,
                "_cache_key": fp,
            })

    # 执行分析（仅处理未命中缓存的）
    to_analyze = [d for d in news_data if d["analysis"] is None]
    to_analyze = to_analyze[:args.limit]  # 限流

    if to_analyze:
        logger.info(f"🤖 分析 {len(to_analyze)} 条资讯（模型: {ANALYSIS_MODEL}）...")
        for i, d in enumerate(to_analyze, 1):
            news_item = d["news"]
            logger.info(f"[{i}/{len(to_analyze)}] {news_item['title'][:50]}...")

            result = analyze_news_item(news_item, ANALYSIS_MODEL, deepseek_client)
            d["analysis"] = result

            # 更新缓存
            fp = d["_cache_key"]
            cache[fp] = {
                "cached_at": datetime.datetime.now().isoformat(),
                "title": news_item.get("title", "")[:80],
                "url": news_item.get("url", ""),
                "analysis": result,
                "relevance": result.get("relevance", 0),
                "urgency": result.get("urgency", "background"),
                "case_value": result.get("case_value", "low"),
            }
            save_news_cache(cache)  # 实时保存
            time.sleep(1.5)          # API 限流保护

    # 过滤有效分析结果
    valid_data = [d for d in news_data if d["analysis"] is not None]
    logger.info(f"📊 有效分析: {len(valid_data)} 条")

    # 生成报告（可能因内容不变而返回 None）
    report_path = generate_news_report(valid_data, keywords)
    if report_path is None:
        logger.info("🔄 没有生成新报告（内容无变化）。")
    else:
        # 导出 JSON 原始数据
        export_path = OUTPUT_DIR / f"news_data_{datetime.date.today().isoformat()}.json"
        export_data = [
            {
                "title": d["news"]["title"],
                "url": d["news"]["url"],
                "source": d["news"].get("source_name", ""),
                "published": d["news"].get("published", ""),
                "analysis": d["analysis"]
            }
            for d in valid_data
        ]
        with open(export_path, "w", encoding="utf-8") as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)
        logger.info(f"💾 原始数据导出: {export_path}")

        # 可选：自动转 HTML（安全调用）
        try:
            subprocess.run(["python", "news_md_to_html.py", str(report_path)], check=True)
        except Exception as e:
            logger.warning(f"HTML 转换失败（可手工执行）: {e}")

    logger.info("✅ News Radar 完成。")


if __name__ == "__main__":
    main()