#!/usr/bin/env python3
"""
Academic Radar — 学术论文监控脚本（独立版）
- 整合 arXiv + Semantic Scholar 学术论文抓取
- 配置抽离：所有参数统一从 config.Config 读取
- 日志系统：使用 logger 记录关键流程，同时写入 radar.log
- 增量缓存：基于论文内容指纹（MD5）去重
- 多模型加权合并，自动生成书稿草稿
- 命令行：python academic_radar.py [--limit N]
"""

from __future__ import annotations

import os
import sys
import json
import time
import datetime
import hashlib
import argparse
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
from cache import (
    load_cache,
    is_paper_cached,
    mark_paper_cached,
    save_draft,
    get_search_cache,
    set_search_cache,
)

# ------------------------------------------------------------------
# 环境初始化
# ------------------------------------------------------------------
load_dotenv()

deepseek_client = None
if Config.DEEPSEEK_API_KEY:
    deepseek_client = OpenAI(
        api_key=Config.DEEPSEEK_API_KEY,
        base_url="https://api.deepseek.com"
    )
else:
    logger.error("❌ 未配置 DEEPSEEK_API_KEY，程序无法运行！")
    sys.exit(1)

arxiv_client = arxiv.Client(
    page_size=Config.ARXIV_PAGE_SIZE,
    delay_seconds=Config.ARXIV_DELAY_SECONDS,
    num_retries=5
)

# ------------------------------------------------------------------
# 固定配置
# ------------------------------------------------------------------
OUTPUT_DIR = Path(Config.OUTPUT_DIR) / "academic"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

ANALYSIS_MODELS = Config.ANALYSIS_MODELS
ANALYSIS_MODEL_DIRECT = Config.ANALYSIS_MODEL_DIRECT
DRAFTING_MODEL = Config.DRAFTING_MODEL
DRAFT_RELEVANCE_THRESHOLD = Config.DRAFT_RELEVANCE_THRESHOLD
DRAFT_URGENCY_REQUIRED = Config.DRAFT_URGENCY_REQUIRED

CACHE_FILE = OUTPUT_DIR / "academic_cache.json"

# ------------------------------------------------------------------
# 工具函数
# ------------------------------------------------------------------
def load_keywords(filepath: str = Config.KEYWORDS_FILE) -> list[str]:
    with open(filepath, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]

def safe_str(text: str) -> str:
    return text.encode("ascii", "ignore").decode("ascii")

def get_paper_cache_key(paper: dict) -> str:
    content = (paper.get("title", "") + " " + paper.get("summary", "")).encode("utf-8", errors="ignore")
    return hashlib.md5(content).hexdigest()

def load_academic_cache() -> dict:
    """加载学术论文专用缓存"""
    if CACHE_FILE.exists():
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_academic_cache(cache: dict):
    """保存学术论文专用缓存"""
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)

# ------------------------------------------------------------------
# 学术源抓取 (arXiv + Semantic Scholar)
# ------------------------------------------------------------------
def search_arxiv(keywords: list[str], max_results: int = Config.MAX_RESULTS_PER_KEYWORD) -> list[dict]:
    all_papers: dict[str, dict] = {}
    for keyword in keywords:
        # 搜索缓存
        cached = get_search_cache("arxiv", keyword, "papers")
        if cached is not None:
            logger.info(f"📦 [arXiv] 使用搜索缓存: {keyword} ({len(cached)} 篇)")
            for p in cached:
                pid = p.get("id")
                if pid and pid not in all_papers:
                    all_papers[pid] = p
            continue

        logger.info(f"🔍 [arXiv] 正在搜索: {keyword}")
        papers_from_kw = []
        for attempt in range(3):
            try:
                search = arxiv.Search(
                    query=keyword,
                    max_results=max_results,
                    sort_by=arxiv.SortCriterion.SubmittedDate
                )
                count = 0
                for result in arxiv_client.results(search):
                    pid = result.entry_id
                    paper_dict = {
                        "id": pid,
                        "title": safe_str(result.title),
                        "summary": safe_str(result.summary.replace("\n", " ")),
                        "published": result.published.isoformat() if result.published else "N/A",
                        "url": result.pdf_url,
                        "authors": [a.name for a in result.authors],
                        "source": "arxiv",
                    }
                    papers_from_kw.append(paper_dict)
                    if pid not in all_papers:
                        all_papers[pid] = paper_dict
                    count += 1
                logger.info(f"   ✅ 找到 {count} 篇")
                set_search_cache("arxiv", keyword, papers_from_kw, "papers")
                break
            except Exception as e:
                if attempt < 2:
                    wait = (attempt + 1) * 20
                    logger.warning(f"   ⚠️ 请求失败，{wait}s 后重试… ({e})")
                    time.sleep(wait)
                else:
                    logger.error(f"   ❌ 三次重试后仍失败: {e}")
        time.sleep(3)
    return list(all_papers.values())


def search_semantic_scholar(keywords: list[str], limit: int = 5) -> list[dict]:
    API_KEY = Config.SEMANTIC_SCHOLAR_API_KEY
    headers = {"x-api-key": API_KEY} if API_KEY else {}
    
    all_papers = []
    seen_ids = set()
    api_url = "https://api.semanticscholar.org/graph/v1/paper/search"

    for keyword in keywords:
        # 搜索缓存
        cached = get_search_cache("semantic_scholar", keyword, "papers")
        if cached is not None:
            logger.info(f"📦 [S2] 使用搜索缓存: {keyword} ({len(cached)} 篇)")
            for p in cached:
                pid = p.get("id")
                if pid and pid not in seen_ids:
                    all_papers.append(p)
                    seen_ids.add(pid)
            continue

        logger.info(f"🔍 [S2] 正在检索: {keyword}")
        papers_from_kw = []
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
                    logger.warning(f"   ⚠️ 限速！等待 {wait}s...")
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
                    paper_dict = {
                        "id": pid,
                        "title": safe_str(p.get("title", "")),
                        "summary": safe_str(p.get("abstract") or ""),
                        "published": str(p.get("year", "")) if p.get("year") else "N/A",
                        "url": pdf_url if pdf_url else web_url,
                        "authors": [a.get("name", "") for a in p.get("authors", [])],
                        "source": "semantic_scholar",
                    }
                    papers_from_kw.append(paper_dict)
                    all_papers.append(paper_dict)
                    seen_ids.add(pid)
                    count += 1
                logger.info(f"   ✅ 成功提取 {count} 篇")
                set_search_cache("semantic_scholar", keyword, papers_from_kw, "papers")
                break
            except Exception as e:
                if attempt < 3:
                    logger.warning(f"   ⏳ 网络波动，重试中...")
                    time.sleep(5)
                else:
                    logger.error(f"   ❌ 该关键词抓取失败: {keyword}")
        time.sleep(1.5 if API_KEY else 6.0)
    return all_papers


def deduplicate_papers(papers: list[dict]) -> list[dict]:
    seen: set = set()
    unique: list[dict] = []
    for p in papers:
        if p["id"] and p["id"] not in seen:
            seen.add(p["id"])
            unique.append(p)
    return unique


def prescreen_academic_papers(papers: list[dict]) -> list[dict]:
    """学术论文预筛选（仅保留学术相关术语）"""
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

    before = len(papers)
    filtered = []
    for p in papers:
        # 学术源才进行筛选
        if p.get("source") in ("arxiv", "semantic_scholar"):
            text = (p["title"] + " " + p["summary"]).lower()
            if any(t in text for t in relevant_terms_lower):
                filtered.append(p)

    logger.info(f"🔬 学术预筛选：{before} → {len(filtered)} 篇")
    return filtered

# ------------------------------------------------------------------
# 模型分析（纯学术论文版）
# ------------------------------------------------------------------
ACADEMIC_SYSTEM_PROMPT = """你是《Renegade AI: Catalyst for Human Cognitive Evolution》(v5.3) 的智能编辑助手。你需要判断一篇学术论文是否与本书的核心论点相关，并给出具体的更新建议。

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
阅读论文摘要，返回严格JSON（不要任何额外文字）：
{
    "relevance": 1-10的整数,
    "summary_cn": "250-350字以内核心发现（中文）",
    "implications": "与书中哪章哪节哪个具体论点相关？支持/挑战/补充？",
    "chapter_target": "例如：Chapter 8, Section V",
    "update_type": "new_evidence / counter_argument / corroboration",
    "urgency": "immediate / next_version / background",
    "action": "新增段落 / 补充注释 / 参考文献 / 忽略"
}

注意：
- 若与上述概念、实证锚点无关，relevance应低于4，action为"忽略"
- 纯技术性论文（架构/基准）评为低相关"""


def analyze_single_model(paper: dict, model_name: str, client: OpenAI) -> dict:
    """单模型分析学术论文"""
    system_prompt = ACADEMIC_SYSTEM_PROMPT
    user_prompt = f"""论文标题：{paper['title']}
作者：{', '.join(paper['authors'][:5])}
摘要：{paper['summary']}

请返回JSON格式分析结果。"""

    try:
        resp = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.2,
            max_tokens=1800,
        )
        content = resp.choices[0].message.content
        # 清理Markdown标记
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
    """多模型结果加权合并"""
    valid = [r for r in results if r.get("relevance", 0) > 0]
    if not valid:
        return {
            "relevance": 0, "action": "忽略",
            "summary_cn": "所有模型调用失败", "implications": "N/A",
            "chapter_target": "", "update_type": "", "urgency": "background",
        }

    scores = [r["relevance"] for r in valid]
    avg = sum(scores) / len(scores)

    # 剔除异常高分
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
    """多模型并行分析"""
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
    """为高相关论文生成书稿草稿"""
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
            max_tokens=1800,
        )
        draft = resp.choices[0].message.content.strip()
        if len(draft) < 50:
            logger.warning(f"   ⚠️ 草稿过短，重试生成...")
            return draft_patch(paper, merged)
        return draft
    except Exception as e:
        logger.error(f"草稿生成失败: {e}")
        return None


# ------------------------------------------------------------------
# 报告生成（学术版）
# ------------------------------------------------------------------
def generate_academic_report(papers_data: list[dict], keywords: list[str]) -> str:
    today = datetime.date.today().isoformat()
    lines = [
        f"# 🔬 Academic Radar — 学术论文监控报告",
        f"**生成日期**: {today}",
        f"**分析模型**: {ANALYSIS_MODEL_DIRECT}",
        f"**草稿模型**: {DRAFTING_MODEL}",
        f"**分析条目数**: {len(papers_data)}",
        f"**关键词**: {', '.join(keywords[:10])}{'...' if len(keywords)>10 else ''}",
        "---\n",
    ]

    high = [d for d in papers_data if d["merged"].get("relevance", 0) >= 6.5]
    medium = [d for d in papers_data if 3 <= d["merged"].get("relevance", 0) < 6.5]

    lines += [
        "## 📊 统计概览\n",
        f"- ⭐ 高相关 (≥6.5分): **{len(high)}**",
        f"- 🔶 中相关 (3-6.4分): **{len(medium)}**",
        f"- ⬜ 低相关 (<3分): **{len(papers_data) - len(high) - len(medium)}**\n",
    ]

    # 高相关论文
    if high:
        high.sort(key=lambda d: (0 if d.get("draft") and len(d["draft"].strip())>50 else 1,
                                -d["merged"].get("relevance", 0)))
        lines.append(f"## ⭐ 高相关论文 ({len(high)}条)\n")
        for i, d in enumerate(high, 1):
            p, m = d["paper"], d["merged"]
            source_label = p.get('source', 'unknown').upper()
            lines += [
                f"### {i}. {p['title']}",
                f"- **来源**: {source_label}",
                f"- **作者**: {', '.join(p['authors'][:3])}{' et al.' if len(p['authors'])>3 else ''}",
                f"- **发表**: {p.get('published', 'N/A')}",
                f"- **最终评分**: {m['relevance']}/10",
                f"- **紧迫度**: {m.get('urgency', 'N/A')}",
                f"- **更新类型**: {m.get('update_type', 'N/A')}",
                f"- **目标章节**: {m.get('chapter_target', 'N/A')}",
                f"- **链接**: [{p.get('url', 'N/A')}]({p.get('url', '#')})",
                f"- **核心发现**: {m.get('summary_cn', 'N/A')}",
                f"- **与本书关联**: {m.get('implications', 'N/A')}",
                f"- **建议更新**: {m.get('action', 'N/A')}",
            ]
            if m.get("model_scores"):
                lines.append("\n**🧠 模型评分:**")
                lines.append("| 模型 | 相关度 |")
                lines.append("|------|--------|")
                for mn, sc in sorted(m["model_scores"].items(), key=lambda x: x[1], reverse=True):
                    display_name = mn.split("/")[-1][:30]
                    lines.append(f"| {display_name} | {sc} |")

            if d.get("draft") and len(d["draft"].strip()) > 50:
                lines.append("\n**✍️ 自动生成书稿草稿：**")
                lines.append(f"\n> {d['draft']}\n")
            lines.append("")

    # 立即更新清单
    immediate_items = [d for d in papers_data if d["merged"].get("urgency") == DRAFT_URGENCY_REQUIRED and d["merged"].get("relevance", 0) >= DRAFT_RELEVANCE_THRESHOLD]
    if immediate_items:
        lines.append("\n## 🚨 立即更新清单\n")
        for d in immediate_items:
            p, m = d["paper"], d["merged"]
            has_draft = "✍️" if (d.get("draft") and len(d["draft"].strip())>50) else "⬜"
            lines.append(f"- [ ] {has_draft} **{m.get('chapter_target', '待定')}** — {p['title'][:60]}... [{p.get('source','').upper()}]({p.get('url', '#')})")

    # 中相关论文（简略）
    if medium:
        lines.append(f"\n## 🔶 中相关论文 ({len(medium)}条)\n")
        for d in medium:
            p, m = d["paper"], d["merged"]
            source_label = p.get('source', 'unknown').upper()
            lines.append(f"- **[{p['title']}]({p.get('url', '#')})** [{source_label}] — {m['relevance']}/10")
            lines.append(f"  - {m.get('summary_cn', 'N/A')[:120]}...")
        lines.append("")

    # 保存报告
    now = datetime.datetime.now()
    report_path = OUTPUT_DIR / f"academic_report_{now.date().isoformat()}_{now.strftime('%H%M%S')}.md"
    report_path.write_text("\n".join(lines), encoding="utf-8")
    logger.info(f"✅ 学术报告已保存: {report_path}")
    return str(report_path)


# ------------------------------------------------------------------
# 主函数
# ------------------------------------------------------------------
def main() -> None:
    parser = argparse.ArgumentParser(description="Academic Radar — 学术论文监控")
    parser.add_argument("--limit", type=int, default=20, help="每次运行最大分析论文数")
    parser.add_argument("--keywords", type=str, help="临时关键词文件路径")
    args = parser.parse_args()

    logger.info("🚀 Academic Radar 启动")
    
    keywords = load_keywords(args.keywords if args.keywords else Config.KEYWORDS_FILE)
    logger.info(f"📋 加载 {len(keywords)} 个关键词")

    # 加载缓存
    cache = load_academic_cache()
    logger.info(f"📂 加载缓存 {len(cache)} 条")

    # 多源抓取
    logger.info("🔍 开始抓取学术论文...")
    arxiv_papers = search_arxiv(keywords)
    s2_papers = search_semantic_scholar(keywords)
    all_papers = deduplicate_papers(arxiv_papers + s2_papers)
    logger.info(f"📄 合并去重后共 {len(all_papers)} 篇")

    if not all_papers:
        logger.info("✨ 没有找到新论文，退出。")
        return

    # 分析缓存匹配
    papers_data: list[dict] = []
    for paper in all_papers:
        fp = get_paper_cache_key(paper)
        if fp in cache and "analysis" in cache[fp]:
            cached_entry = cache[fp]
            logger.info(f"♻️ 缓存命中: {paper['title'][:50]}...")
            papers_data.append({
                "paper": paper,
                "merged": cached_entry["analysis"],
                "draft": cached_entry.get("draft_paragraph"),
            })
        else:
            papers_data.append({
                "paper": paper,
                "merged": None,
                "draft": None,
            })

    need_analysis = [d for d in papers_data if d["merged"] is None]
    logger.info(f"🆕 待分析: {len(need_analysis)} 篇")

    if need_analysis:
        to_analyze = prescreen_academic_papers([d["paper"] for d in need_analysis])
        to_analyze = to_analyze[:args.limit]  # 限制单次分析数量
        
        if to_analyze:
            logger.info(f"🤖 开始分析 {len(to_analyze)} 篇...")
            need_map = {d["paper"]["id"]: d for d in need_analysis}
            
            for i, paper in enumerate(to_analyze, 1):
                logger.info(f"[{i}/{len(to_analyze)}] {paper['title'][:50]}...")
                results, merged = analyze_paper_multi_model(paper, ANALYSIS_MODELS)
                target = need_map.get(paper["id"])
                if target:
                    target["merged"] = merged
                # 保存分析缓存
                fp = get_paper_cache_key(paper)
                cache[fp] = {
                    "cached_at": datetime.datetime.now().isoformat(),
                    "title": paper.get("title", "")[:80],
                    "analysis": merged,
                    "relevance": merged.get("relevance", 0),
                    "urgency": merged.get("urgency", "background"),
                    "model_scores": merged.get("model_scores", {}),
                }
                save_academic_cache(cache)
                time.sleep(2)

    # 过滤有效结果
    papers_data = [d for d in papers_data if d["merged"] is not None]
    logger.info(f"📊 有效分析: {len(papers_data)} 篇")

    # 草稿生成
    draft_candidates = [
        d for d in papers_data 
        if d["merged"].get("urgency") == DRAFT_URGENCY_REQUIRED 
        and d["merged"].get("relevance", 0) >= DRAFT_RELEVANCE_THRESHOLD
        and not (d.get("draft") and len(d["draft"].strip()) > 50)
    ]
    
    if draft_candidates:
        logger.info(f"✍️ 生成 {len(draft_candidates)} 篇草稿...")
        for d in draft_candidates:
            draft = draft_patch(d["paper"], d["merged"])
            d["draft"] = draft
            if draft and len(draft.strip()) > 50:
                fp = get_paper_cache_key(d["paper"])
                if fp in cache:
                    cache[fp]["draft_paragraph"] = draft
                    save_academic_cache(cache)
            time.sleep(3)

    # 生成报告
    report_path = generate_academic_report(papers_data, keywords)
    logger.info(f"✅ 完成: {report_path}")

    # 自动生成 HTML 版
    import subprocess
    subprocess.run(['python', 'academic_md_to_html.py', report_path])


if __name__ == "__main__":
    main()