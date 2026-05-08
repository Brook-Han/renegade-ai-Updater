#!/usr/bin/env python3
"""
Renegade AI 文献监控脚本 v4.4.2 — 学术+资讯双雷达整合版（纯DeepSeek直连）
- 整合 arXiv + Semantic Scholar 学术论文抓取
- 整合 NewsAPI + RSS 资讯抓取（条件启用）
- 配置抽离：所有参数统一从 config.Config 读取
- 日志系统：使用 logger 记录关键流程，同时写入 radar.log
- 增量缓存：基于论文内容指纹（MD5）去重，正式替换 seen_ids
- 多模型加权合并，自动生成书稿草稿
- 命令行参数：
    python scrape_and_analyze.py          # 全跑
    python scrape_and_analyze.py --news   # 仅资讯
    python scrape_and_analyze.py --papers # 仅论文
"""

from __future__ import annotations

import os
import sys
import json
import time
import datetime
import hashlib
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Optional

import arxiv
import requests
from openai import OpenAI
from dotenv import load_dotenv

# 自定义模块
from config import Config
from logger import logger
from cache import load_cache, is_paper_cached, mark_paper_cached
from news_sources import fetch_all_news      # 资讯聚合模块

# ------------------------------------------------------------------
# 环境初始化（纯 DeepSeek 直连，已剔除 OpenRouter）
# ------------------------------------------------------------------
load_dotenv()

# DeepSeek 官方直连客户端（唯一模型渠道）
deepseek_client = None
if Config.DEEPSEEK_API_KEY:
    deepseek_client = OpenAI(
        api_key=Config.DEEPSEEK_API_KEY,
        base_url="https://api.deepseek.com"
    )
else:
    logger.error("❌ 未配置 DEEPSEEK_API_KEY，程序无法运行！")
    sys.exit(1)

# arXiv 客户端
arxiv_client = arxiv.Client(
    page_size=Config.ARXIV_PAGE_SIZE,
    delay_seconds=Config.ARXIV_DELAY_SECONDS,
    num_retries=5
)

# ------------------------------------------------------------------
# 固定配置（全部从 Config 继承，无本地硬编码）
# ------------------------------------------------------------------
OUTPUT_DIR = Path(Config.OUTPUT_DIR)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# 分析模型配置（仅 DeepSeek 直连）
ANALYSIS_MODELS = Config.ANALYSIS_MODELS
ANALYSIS_MODEL_DIRECT = Config.ANALYSIS_MODEL_DIRECT
DRAFTING_MODEL = Config.DRAFTING_MODEL
DRAFT_RELEVANCE_THRESHOLD = Config.DRAFT_RELEVANCE_THRESHOLD
DRAFT_URGENCY_REQUIRED = Config.DRAFT_URGENCY_REQUIRED

# 模型名称展示
ALL_MODEL_NAMES = [f"{ANALYSIS_MODEL_DIRECT} (直连)"]

# ------------------------------------------------------------------
# 工具函数
# ------------------------------------------------------------------
def load_keywords(filepath: str = Config.KEYWORDS_FILE) -> list[str]:
    with open(filepath, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]

def safe_str(text: str) -> str:
    return text.encode("ascii", "ignore").decode("ascii")

def get_paper_fingerprint(paper: dict) -> str:
    """与 cache.py 保持一致的指纹算法"""
    content = (paper.get("title", "") + " " + paper.get("summary", "")).encode("utf-8", errors="ignore")
    return hashlib.md5(content).hexdigest()

# ------------------------------------------------------------------
# 多源抓取 (arXiv + Semantic Scholar)
# ------------------------------------------------------------------


def search_semantic_scholar(keywords: list[str], limit: int = 5) -> list[dict]:
    API_KEY = Config.SEMANTIC_SCHOLAR_API_KEY
    papers: list[dict] = []
    seen_ids = set()
    headers = {"x-api-key": API_KEY} if API_KEY else {}

    if API_KEY:
        logger.info("🔑 [S2] 已加载 API Key，高频模式")
    else:
        logger.warning("⚠️ [S2] 无 API Key，将使用匿名限速模式")

    api_url = "https://api.semanticscholar.org/graph/v1/paper/search"

    for keyword in keywords:
        logger.info(f"🔍 [S2] 正在检索: {keyword}")
        for attempt in range(4):
            try:
                params = {
                    "query": keyword,
                    "limit": limit,
                    "fields": "paperId,title,abstract,authors,year,externalIds,openAccessPdf"
                }
                r = requests.get(api_url, params=params, headers=headers, timeout=30)

                if r.status_code == 429:
                    wait = (attempt + 1) * (30 if not API_KEY else 5)
                    logger.warning(f"   ⚠️ 限速！第 {attempt+1} 次尝试，等待 {wait}s...")
                    time.sleep(wait)
                    continue

                r.raise_for_status()
                data = r.json().get("data", [])
                count = 0
                for p in data:
                    pid = p.get("paperId")
                    if not pid or pid in seen_ids:
                        continue
                    pdf_url = (p.get("openAccessPdf") or {}).get("url")
                    web_url = f"https://www.semanticscholar.org/paper/{pid}"
                    papers.append({
                        "id": pid,
                        "title": safe_str(p.get("title", "")),
                        "summary": safe_str(p.get("abstract") or ""),
                        "published": str(p.get("year", "")) if p.get("year") else "N/A",
                        "url": pdf_url if pdf_url else web_url,
                        "authors": [a.get("name", "") for a in p.get("authors", [])],
                        "source": "semantic_scholar",
                    })
                    seen_ids.add(pid)
                    count += 1
                logger.info(f"   ✅ 成功提取 {count} 篇")
                break
            except Exception as e:
                if attempt < 3:
                    logger.warning(f"   ⏳ 网络波动/限速 ({e})，重试中...")
                    # 统一增加等待时间，避免频繁请求
                    time.sleep(10 if "429" in str(e) else 5)
                else:
                    logger.error(f"   ❌ 该关键词抓取失败: {keyword}")
        # 延长基础冷却，更稳定
        time.sleep(2.5 if API_KEY else 8.0)
    return papers


def deduplicate_papers(papers: list[dict]) -> list[dict]:
    seen: set = set()
    unique: list[dict] = []
    for p in papers:
        if p["id"] and p["id"] not in seen:
            seen.add(p["id"])
            unique.append(p)
    return unique


def prescreen_papers(papers: list[dict]) -> list[dict]:
    # 通用相关词
    relevant_terms = [
        "AI", "artificial intelligence", "LLM", "language model", "GPT",
        "algorithm", "automation", "machine learning", "neural",
        "cognitive", "persuasion", "manipulation", "sycophan",
        "alignment", "RLHF", "human-AI", "humanAI",
        "capital", "labor", "work", "job", "employment",
        "ethics", "bias", "fairness", "governance",
        "well-being", "wellbeing", "mental health",
        "companion", "chatbot", "conversational",
        "delegation", "decision", "advice", "trust",
        "open source", "decentraliz", "compute",
        "Darwinian", "evolution", "digital evolution",
        "token", "financialization",
    ]
    relevant_terms_lower = [t.lower() for t in relevant_terms]

    # 新闻专用词
    news_terms = [t.lower() for t in getattr(Config, "NEWS_CONCEPT_TERMS", [])]

    def is_news(item: dict) -> bool:
        return item.get("source") in ("newsapi", "rss")

    before = len(papers)
    filtered = []
    for p in papers:
        text = (p["title"] + " " + p["summary"]).lower()
        if is_news(p):
            if any(t in text for t in relevant_terms_lower):
                if not news_terms or any(nt in text for nt in news_terms):
                    filtered.append(p)
        else:
            if any(t in text for t in relevant_terms_lower):
                filtered.append(p)

    logger.info(f"🔬 预筛选：{before} → {len(filtered)} 篇（过滤 {before - len(filtered)} 篇）")
    return filtered

# ------------------------------------------------------------------
# 模型分析（纯 DeepSeek 直连）
# ------------------------------------------------------------------
SYSTEM_PROMPT = """你是《Renegade AI: Catalyst for Human Cognitive Evolution》(v5.3) 的智能编辑助手。你需要判断一篇学术论文是否与本书的核心论点相关，并给出具体的更新建议。

## 本书核心概念
1. 共识牢笼 (Consensus Cage)
2. 叛逆AI (Renegade AI)：重置目标函数、逆转输出性质、重构人机关系
3. 需求侧规训 (Demand-Side Discipline)
4. 资本驯化AI：RLHF 将 AI 变成共识牢笼守卫
5. 碳硅共生 (Carbon-Silicon Symbiosis)
6. 时间主权 (Temporal Sovereignty)
7. 认知金融化 (Cognitive Financialization)
8. Token陷阱 (Token Trap)
9. 暗时间 (Dark Time)
10. 进化对齐脆弱性 (Evolutionary Alignment Fragility)
11. 终极图灵测试 (Ultimate Turing Test)

## 关键实证锚点
- 人机反馈循环放大偏见 (Glickman & Sharot, 2025)
- 奉承型AI削弱冲突修复能力 (Cheng et al., 2026)
- 温暖训练降低准确性增加奉承 (Ibrahim et al., 2026)
- AI辅助写作导致80%学生无法回忆内容 (Kosmyna et al., 2024)
- AI扩展科研产出但缩小探索范围4.6% (Hao et al., 2026)
- LLM论文质量信号被Token化污染 (Kusumegi et al., 2025)
- GPT-4说服力比人类高81.2% (Salvi et al., 2025)
- 体验上给AI同理心更高分 (Wenger et al., 2026)
- 高风险国家安全决策中的自动化偏见 (Horowitz & Kahn, 2024)
- 对齐的进化脆弱性 (Müller et al., 2026)
- AI写作推向西方文化规范 (Vashistha et al., 2024)

## 任务
阅读论文摘要，返回严格JSON（不要任何额外文字）。"""

NEWS_SYSTEM_PROMPT = """你是《Renegade AI: Catalyst for Human Cognitive Evolution》(v5.3) 的新闻分析助手。
你的任务不是寻找学术证据，而是判断这条新闻是否印证、挑战或丰富了书中某个具体的**理论模型**，并评估其作为**案例 / 类比**的价值。

## 书中关键理论模型
1. 共识牢笼 (Consensus Cage) – 主流叙事如何自洽并排斥异见
2. 叛逆AI (Renegade AI) – 重置目标函数、逆转输出性质、重构人机关系
3. 需求侧规训 (Demand-Side Discipline) – 用户主动渴望“索麻”式舒适，拒绝摩擦
4. 资本驯化AI – 资本如何通过 RLHF、专利、算力垄断将 AI 变成秩序守卫
5. 碳硅共生 (Carbon-Silicon Symbiosis) – 人类与 AI 平等互补，而非主奴
6. 时间主权 (Temporal Sovereignty) – 终结生存强迫，拿回生命时间
7. 认知金融化 / Token陷阱 – 认知被离散化、定价，思考过程被隐性外包
8. 暗时间 (Dark Time) – 思考过程在系统内部发生，用户仅消费结果
9. 进化对齐脆弱性 – 对齐只在封闭实验室有效，开放后必然漂移
10. 信号异化 – 衡量质量的信号（如复杂度）因 AI 大批量生产而失效

## 任务
阅读新闻摘要，返回严格 JSON：
{
    "relevance": 1-10,
    "summary_cn": "100 字内浓缩事件",
    "implications": "这条新闻支持 / 挑战 / 补充了以上哪个理论模型？为什么？",
    "case_value": "high / medium / low",
    "chapter_target": "例如：Chapter 3, Section IV",
    "update_type": "new_evidence / counter_argument / corroboration / case_study",
    "urgency": "immediate / next_version / background",
    "action": "新增段落 / 补充注释 / 案例盒子 / 忽略"
}
注意：
- 如果新闻与上述理论模型均无直接映射，relevance 应低于 3，action 为"忽略""
- 不要套用论文评价标准"""

def analyze_single_model(paper: dict, model_name: str, client: OpenAI) -> dict:
    # 根据来源分流提示词
    if paper.get("source") in ("newsapi", "rss"):
        system_prompt = NEWS_SYSTEM_PROMPT
        user_prompt = f"""新闻标题：{paper['title']}
内容摘要：{paper['summary']}
来源：{paper.get('source_name', '')}

请按 JSON 格式返回分析结果。"""
    else:
        system_prompt = SYSTEM_PROMPT
        user_prompt = f"""论文标题：{paper['title']}
作者：{', '.join(paper['authors'][:5])}
摘要：{paper['summary']}

请返回JSON：
{{
    "relevance": 1-10的整数,
    "summary_cn": "150字以内核心发现（中文）",
    "implications": "与书中哪章哪节哪个具体论点相关？支持/挑战/补充？",
    "chapter_target": "例如：Chapter 8, Section V",
    "update_type": "new_evidence / counter_argument / corroboration",
    "urgency": "immediate / next_version / background",
    "action": "新增段落 / 补充注释 / 参考文献 / 忽略"
}}

注意：
- 若与上述概念、实证锚点无关，relevance应低于4，action为"忽略"
- 纯技术性论文（架构/基准）评为低相关"""

    try:
        resp = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.2,
            max_tokens=1500,
        )
        content = resp.choices[0].message.content
        for marker in ("```json", "```"):
            if marker in content:
                content = content.split(marker)[1].split("```")[0]
                break
        result = json.loads(content.strip())
        result["_model"] = model_name
        return result
    except Exception as e:
        logger.error(f"模型 {model_name} 分析失败: {e}")
        return {
            "relevance": 0,
            "summary_cn": f"调用失败: {str(e)[:80]}",
            "implications": "N/A",
            "chapter_target": "",
            "update_type": "",
            "urgency": "background",
            "action": "忽略",
            "_model": model_name,
        }


def merge_results(results: list[dict]) -> dict:
    valid = [r for r in results if r.get("relevance", 0) > 0]
    if not valid:
        return {
            "relevance": 0, "action": "忽略",
            "summary_cn": "所有模型调用失败", "implications": "N/A",
            "chapter_target": "", "update_type": "", "urgency": "background",
        }

    scores = [r["relevance"] for r in valid]
    avg = sum(scores) / len(scores)

    if max(scores) - avg > 3 and len(scores) > 2:
        trimmed_scores = sorted(scores)[:-1]
        avg = sum(trimmed_scores) / len(trimmed_scores)
        max_val = max(scores)
        found = False
        new_valid = []
        for r in valid:
            if not found and r["relevance"] == max_val:
                found = True
                continue
            new_valid.append(r)
        valid = new_valid if found else valid

    consensus = min(valid, key=lambda r: abs(r["relevance"] - avg))
    merged = {k: v for k, v in consensus.items() if not k.startswith("_")}
    merged["relevance"] = round(avg, 1)
    merged["model_scores"] = {r["_model"]: r["relevance"] for r in results}
    if merged["relevance"] < 3:
        merged["action"] = "忽略"
    return merged


def analyze_paper_multi_model(paper: dict, models: list[str]) -> tuple[list[dict], dict]:
    # 仅保留 DeepSeek 直连任务
    tasks = [(ANALYSIS_MODEL_DIRECT, deepseek_client)]

    results: list[dict] = []
    with ThreadPoolExecutor(max_workers=1) as executor:
        future_map = {
            executor.submit(analyze_single_model, paper, model_name, client): model_name
            for model_name, client in tasks
        }
        for future in as_completed(future_map):
            results.append(future.result())

    merged = merge_results(results)
    return results, merged


# ------------------------------------------------------------------
# 草稿生成
# ------------------------------------------------------------------
DRAFT_SYSTEM_PROMPT = """你是《Renegade AI: Catalyst for Human Cognitive Evolution》v5.3 的写作助手。
风格：学术但锋利，长句密集，论证坚定。引用格式：(Author et al., Year)。"""

def draft_patch(paper: dict, merged: dict) -> Optional[str]:
    if not deepseek_client:
        return None

    first_author = paper["authors"][0].split()[-1] if paper["authors"] else "et al."
    year = paper.get("published", "")[:4] if paper.get("published") else ""
    cite = f"({first_author} et al., {year})" if year else f"({first_author} et al.)"

    summary_cn = merged.get('summary_cn', '')
    implications = merged.get('implications', '')
    if len(summary_cn) > 300:
        summary_cn = summary_cn[:300] + '...'
    if len(implications) > 300:
        implications = implications[:300] + '...'

    user_prompt = f"""将以下内容整合进书中：
标题：{paper['title']}
作者：{', '.join(paper['authors'][:3])}
引用格式：{cite}
核心发现（中文摘要）：{summary_cn}
目标章节：{merged.get('chapter_target', '')}
更新类型：{merged.get('update_type', '')}
与书的关联：{implications}

请生成一段 150-250 字的中英双语书稿，风格与全书一致。不要加标题，直接输出段落正文。"""

    try:
        resp = deepseek_client.chat.completions.create(
            model=DRAFTING_MODEL,
            messages=[
                {"role": "system", "content": DRAFT_SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.3,
            max_tokens=1200,
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"草稿生成失败: {e}")
        return None

# ------------------------------------------------------------------
# 报告生成
# ------------------------------------------------------------------
def generate_markdown_multi(papers_data: list[dict], keywords: list[str], prefix: str = "") -> str:
    today = datetime.date.today().isoformat()
    papers_data.sort(key=lambda d: d["merged"].get("relevance", 0), reverse=True)

    model_list_str = ", ".join(ALL_MODEL_NAMES)

    lines = [
        f"# 🔬 Renegade AI {'资讯' if 'news' in prefix else '文献'}监控报告（多模型复证）",
        f"**生成日期**: {today}",
        f"**模型阵容**: {model_list_str}（共 {len(ALL_MODEL_NAMES)} 个）",
        f"**草稿模型**: {DRAFTING_MODEL}",
        f"**分析条目数**: {len(papers_data)}",
        "---\n",
    ]

    high = [d for d in papers_data if d["merged"].get("relevance", 0) >= 7]
    medium = [d for d in papers_data if 4 <= d["merged"].get("relevance", 0) < 7]

    lines += [
        "## 📊 统计概览\n",
        f"- ⭐ 高相关 (≥7分): **{len(high)}**",
        f"- 🔶 中相关 (4-6分): **{len(medium)}**",
        f"- ⬜ 低相关 (<4分): **{len(papers_data) - len(high) - len(medium)}**\n",
    ]

    if high:
        urgency_order = {"immediate": 0, "next_version": 1, "background": 2}
        high.sort(key=lambda d: urgency_order.get(d["merged"].get("urgency", "background"), 2))

        lines.append(f"## ⭐ 高相关 ({len(high)}条)\n")
        for i, d in enumerate(high, 1):
            p, m = d["paper"], d["merged"]
            source_label = f"{p.get('source', 'unknown')}"
            if p.get('source_name'):
                source_label += f" / {p['source_name']}"
            lines += [
                f"### {i}. {p['title']}",
                f"- **来源**: {source_label}",
                f"- **最终评分**: {m['relevance']}/10",
                f"- **紧迫度**: {m.get('urgency', 'N/A')}",
                f"- **更新类型**: {m.get('update_type', 'N/A')}",
                f"- **目标章节**: {m.get('chapter_target', 'N/A')}",
                f"- **链接**: {p.get('url', 'N/A')}",
                f"- **核心发现**: {m.get('summary_cn', 'N/A')}",
                f"- **与本书关联**: {m.get('implications', 'N/A')}",
                f"- **建议更新**: {m.get('action', 'N/A')}",
            ]

            if m.get("model_scores"):
                lines.append("\n**🧠 模型评分:**")
                lines.append("| 模型 | 相关度 |")
                lines.append("|------|--------|")
                for mn, sc in sorted(m["model_scores"].items(), key=lambda x: x[1], reverse=True):
                    if mn == Config.ANALYSIS_MODEL_DIRECT:
                        display_name = "DeepSeek V4 Flash (直连)"
                    elif mn == Config.DRAFTING_MODEL:
                        display_name = "DeepSeek V4 Pro (草稿)"
                    else:
                        display_name = mn.split("/")[-1][:28]
                    lines.append(f"| {display_name} | {sc} |")

            if d.get("draft"):
                lines.append("\n**✍️ 自动生成书稿草稿：**")
                lines.append(f"\n> {d['draft']}\n")

            lines.append("")

    immediate_items = [d for d in papers_data if d["merged"].get("urgency") == DRAFT_URGENCY_REQUIRED and d["merged"].get("relevance", 0) >= DRAFT_RELEVANCE_THRESHOLD]
    if immediate_items:
        lines.append("\n## 🚨 立即更新清单\n")
        for d in immediate_items:
            p, m = d["paper"], d["merged"]
            has_draft = "✍️ 已生成草稿" if d.get("draft") else "⬜ 无草稿"
            lines.append(f"- [ ] **{m.get('chapter_target', '待定')}** — {p['title'][:55]}... ({m.get('update_type', '')}) {has_draft} [链接]({p.get('url', '#')})")

    if medium:
        lines.append(f"\n## 🔶 中相关 ({len(medium)}条)\n")
        for d in medium:
            p, m = d["paper"], d["merged"]
            source_label = f"{p.get('source', 'unknown')}"
            if p.get('source_name'):
                source_label += f" / {p['source_name']}"
            lines.append(f"- **[{p['title']}]({p.get('url', '#')})** — 来源: {source_label} — 相关性: {m['relevance']}/10")
            lines.append(f"  - {m.get('summary_cn', 'N/A')}")
            lines.append("")

    report_path = OUTPUT_DIR / f"{prefix}report_multi_{today}.md"
    report_path.write_text("\n".join(lines), encoding="utf-8")
    logger.info(f"✅ 报告已保存: {report_path}")
    return str(report_path)

# ------------------------------------------------------------------
# 主函数
# ------------------------------------------------------------------
def main() -> None:
    # 解析命令行参数
    run_mode = "all"
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()
        if arg in ("--news", "news", "-n"):
            run_mode = "news"
        elif arg in ("--papers", "papers", "-p"):
            run_mode = "papers"
        else:
            logger.warning(f"未知参数 {arg}，将运行全部模式")

    logger.info(f"🚀 Renegade AI 监控系统 v4.4.2 启动 (模式: {run_mode})")
    logger.info(f"配置: 分析模型 {len(ALL_MODEL_NAMES)} 个, 草稿模型 {DRAFTING_MODEL}")

    keywords = load_keywords()
    logger.info(f"📋 加载了 {len(keywords)} 个关键词")

    # ---------- 多源抓取 ----------
    arxiv_papers = []
    s2_papers = []
    news_articles = []

    if run_mode in ("all", "papers"):
        arxiv_papers = search_arxiv(keywords)
        s2_papers = search_semantic_scholar(keywords)

    if run_mode in ("all", "news"):
        if getattr(Config, "ENABLE_NEWS_API", False) or getattr(Config, "ENABLE_RSS_FEEDS", False):
            logger.info("📰 开始抓取资讯源...")
            news_articles = fetch_all_news(keywords)
            logger.info(f"📰 资讯源共抓取 {len(news_articles)} 条")
        else:
            logger.info("⏭️ 资讯源未启用")

    all_papers = deduplicate_papers(arxiv_papers + s2_papers + news_articles)
    logger.info(f"📄 合并去重后共 {len(all_papers)} 篇")

    if not all_papers:
        logger.info("没有找到任何条目，退出。")
        return

    cache = load_cache()
    new_papers = [p for p in all_papers if not is_paper_cached(p, cache)]
    logger.info(f"🆕 其中 {len(new_papers)} 篇为新条目（已缓存 {len(all_papers)-len(new_papers)} 篇）")

    if not new_papers:
        logger.info("没有新条目需要分析，退出。")
        return

    to_analyze = prescreen_papers(new_papers)
    if not to_analyze:
        logger.info("预筛选后无相关条目，退出。")
        return

    logger.info(f"🤖 开始 DeepSeek 直连分析 {len(to_analyze)} 篇...")
    papers_data: list[dict] = []
    for i, paper in enumerate(to_analyze, 1):
        logger.info(f"[{i}/{len(to_analyze)}] 分析: {paper['title'][:60]}...")
        results, merged = analyze_paper_multi_model(paper, ANALYSIS_MODELS)
        papers_data.append({
            "paper": paper,
            "merged": merged,
            "models_results": results,
            "draft": None,
        })
        time.sleep(2)

    for d in papers_data:
        if d["merged"].get("relevance", 0) > 0:
            mark_paper_cached(d["paper"], d["merged"], cache)

    draft_candidates = [
        d for d in papers_data
        if d["merged"].get("urgency") == DRAFT_URGENCY_REQUIRED
        and d["merged"].get("relevance", 0) >= DRAFT_RELEVANCE_THRESHOLD
    ]
    if draft_candidates:
        logger.info(f"✍️ 为 {len(draft_candidates)} 篇高优先级条目生成书稿草稿...")
        for d in draft_candidates:
            logger.info(f"   草稿: {d['paper']['title'][:55]}...")
            d["draft"] = draft_patch(d["paper"], d["merged"])
            time.sleep(3)

    # 根据模式生成前缀
    prefix = ""
    if run_mode == "news":
        prefix = "news_"
    elif run_mode == "papers":
        prefix = "papers_"

    generate_markdown_multi(papers_data, keywords, prefix)
    logger.info("✅ 任务完成！")

if __name__ == "__main__":
    main()