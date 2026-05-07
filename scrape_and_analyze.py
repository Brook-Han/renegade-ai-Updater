#!/usr/bin/env python3
"""
Renegade AI 文献监控脚本 v4.3.1 — 多模型复证终版（信息对齐修正）
- 配置抽离：所有参数统一从 config.Config 读取
- 日志系统：使用 logger 记录关键流程，同时写入 radar.log
- 增量缓存：基于论文内容指纹（MD5）去重，正式替换 seen_ids
- 多模型加权合并，自动生成书稿草稿
"""
ALL_MODEL_NAMES = [f"DeepSeek V4 Flash (直连)"] + ANALYSIS_MODELS
from __future__ import annotations

import os
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

openrouter_client = None
if Config.OPENROUTER_API_KEY:
    openrouter_client = OpenAI(
        api_key=Config.OPENROUTER_API_KEY,
        base_url="https://openrouter.ai/api/v1",
        default_headers={
            "HTTP-Referer": "https://github.com/Brook-Han/renegade-ai-Updater",
            "X-Title": "Renegade AI Radar",
        },
    )

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

# 分析模型列表（仅OpenRouter，不含直连）
ANALYSIS_MODELS = Config.ANALYSIS_MODELS

# 草稿生成设置（统一从配置读取）
DRAFTING_MODEL = Config.DRAFTING_MODEL
DRAFT_RELEVANCE_THRESHOLD = Config.DRAFT_RELEVANCE_THRESHOLD   # 默认 8
DRAFT_URGENCY_REQUIRED    = Config.DRAFT_URGENCY_REQUIRED      # 默认 "immediate"

# 所有分析模型的完整名称（用于报告展示）
ALL_MODEL_NAMES = ["DeepSeek V4 Pro (直连)"] + ANALYSIS_MODELS

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
def search_arxiv(keywords: list[str], max_results: int = Config.MAX_RESULTS_PER_KEYWORD) -> list[dict]:
    all_papers: dict[str, dict] = {}
    for keyword in keywords:
        logger.info(f"🔍 [arXiv] 正在搜索: {keyword}")
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
                    if pid not in all_papers:
                        all_papers[pid] = {
                            "id": pid,
                            "title": safe_str(result.title),
                            "summary": safe_str(result.summary.replace("\n", " ")),
                            "published": result.published.isoformat() if result.published else "N/A",
                            "url": result.pdf_url,
                            "authors": [a.name for a in result.authors],
                        }
                        count += 1
                logger.info(f"   ✅ 找到 {count} 篇")
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
                    })
                    seen_ids.add(pid)
                    count += 1
                logger.info(f"   ✅ 成功提取 {count} 篇")
                break
            except Exception as e:
                if attempt < 3:
                    logger.warning(f"   ⏳ 网络波动 ({e})，重试中...")
                    time.sleep(5)
                else:
                    logger.error(f"   ❌ 该关键词抓取失败: {keyword}")
        # 冷却间隔
        time.sleep(1.5 if API_KEY else 6.0)
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
    before = len(papers)
    filtered = [
        p for p in papers
        if any(t.lower() in (p["title"] + " " + p["summary"]).lower() for t in relevant_terms)
    ]
    logger.info(f"🔬 预筛选：{before} → {len(filtered)} 篇（过滤 {before - len(filtered)} 篇）")
    return filtered

# ------------------------------------------------------------------
# 多模型分析
# ------------------------------------------------------------------
SYSTEM_PROMPT = """你是《Renegade AI: Catalyst for Human Cognitive Evolution》(v5.3) 的智能编辑助手。你需要判断一篇学术论文是否与本书的核心论点相关，并给出具体的更新建议。

## 本书核心概念（相关性判断依据）
1. 共识牢笼 (Consensus Cage)
2. 叛逆AI (Renegade AI)：重置目标函数、逆转输出性质、重构人机关系
3. 需求侧规训 (Demand-Side Discipline)：用户渴望“索麻”式认知舒适
4. 资本驯化AI：RLHF 将 AI 变成共识牢笼守卫
5. 碳硅共生 (Carbon-Silicon Symbiosis)
6. 时间主权 (Temporal Sovereignty)
7. 认知金融化 (Cognitive Financialization)
8. Token陷阱 (Token Trap)：廉价Token → 依赖 → 萎缩 → 认知主权崩塌
9. 暗时间 (Dark Time)
10. 进化对齐脆弱性 (Evolutionary Alignment Fragility)
11. 终极图灵测试 (Ultimate Turing Test)

## 关键实证锚点（高度相关）
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


def analyze_single_model(paper: dict, model_name: str, client: OpenAI) -> dict:
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
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.2,
            max_tokens=1500,
        )
        content = resp.choices[0].message.content
        # 清理代码块
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

    # 异常值剔除（仅用于计算最终均值和确定文本来源）
    if max(scores) - avg > 3 and len(scores) > 2:
        # 去除最高分后重新计算均值和有效列表
        trimmed_scores = sorted(scores)[:-1]
        avg = sum(trimmed_scores) / len(trimmed_scores)
        # 重新确定有效集合（排除了最高分的那一个结果）
        max_val = max(scores)
        valid = [r for r in valid if r["relevance"] != max_val]  # 如果有多个相同最高分，会全部去除，需要更精细控制，但简单用第一个即可
        # 简单处理：只剔除第一个遇到的最高分结果
        # 由于 valid 是列表，遍历剔除第一个最高分匹配项
        found = False
        new_valid = []
        for r in valid:
            if not found and r["relevance"] == max_val:
                found = True
                continue
            new_valid.append(r)
        valid = new_valid if found else valid

    # 在有效结果中寻找最接近平均分的模型作为文本来源
    consensus = min(valid, key=lambda r: abs(r["relevance"] - avg))
    merged = {k: v for k, v in consensus.items() if not k.startswith("_")}
    merged["relevance"] = round(avg, 1)
    merged["model_scores"] = {r["_model"]: r["relevance"] for r in results}
    # 低分过滤：合并分低于 3 时强制 action=忽略
    if merged["relevance"] < 3:
        merged["action"] = "忽略"
    return merged


def analyze_paper_multi_model(paper: dict, models: list[str]) -> tuple[list[dict], dict]:
    tasks: list[tuple[str, OpenAI]] = []
    
    # DeepSeek 官网直连 (使用分析专用模型，默认 deepseek-v4-flash)
    if deepseek_client:
        tasks.append((Config.ANALYSIS_MODEL_DIRECT, deepseek_client))
    
    # OpenRouter 模型（目前只有免费 Llama）
    if openrouter_client:
        for m in models:
            tasks.append((m, openrouter_client))
    
    # OpenRouter 模型
    if openrouter_client:
        for m in models:
            tasks.append((m, openrouter_client))

    results: list[dict] = []
    with ThreadPoolExecutor(max_workers=min(len(tasks), 3)) as executor:
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
风格：学术但锋利，长句密集，论证坚定。引用格式：(Author et al., Year)。
本书为中文原著，英文章节保持同等力度。"""

def draft_patch(paper: dict, merged: dict) -> Optional[str]:
    """为 immediate + 高分论文生成书稿草稿 (DeepSeek 直连)"""
    if not deepseek_client:
        return None

    first_author = paper["authors"][0].split()[-1] if paper["authors"] else "et al."
    year = paper.get("published", "")[:4] if paper.get("published") else ""
    cite = f"({first_author} et al., {year})" if year else f"({first_author} et al.)"

    user_prompt = f"""将以下论文整合进书中：

论文标题：{paper['title']}
作者：{', '.join(paper['authors'][:3])}
引用格式：{cite}
核心发现（中文摘要）：{merged.get('summary_cn', '')}
目标章节：{merged.get('chapter_target', '')}
更新类型：{merged.get('update_type', '')}
与书的关联：{merged.get('implications', '')}

请生成一段 150-250 字的英文书稿，要求：
- 直接点明论文发现与书中具体论点的连接
- 以 {cite} 格式引用
- 风格与全书一致：论断式，有锋芒，论证密度高
- 不要加任何标题或说明，直接输出段落正文
- 段落以论点开头，以引用结尾"""

    try:
        resp = deepseek_client.chat.completions.create(   # DeepSeek 直连
            model=DRAFTING_MODEL,                        # 使用统一配置的模型名
            messages=[
                {"role": "system", "content": DRAFT_SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.3,
            max_tokens=800,
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"草稿生成失败: {e}")
        return None

# ------------------------------------------------------------------
# 报告生成
# ------------------------------------------------------------------
def generate_markdown_multi(papers_data: list[dict], keywords: list[str]) -> str:
    today = datetime.date.today().isoformat()
    papers_data.sort(key=lambda d: d["merged"].get("relevance", 0), reverse=True)

    # 模型阵容展示优化
    model_list_str = ", ".join(ALL_MODEL_NAMES)

    lines = [
        "# 🔬 Renegade AI 文献监控报告（多模型复证）",
        f"**生成日期**: {today}",
        f"**模型阵容**: {model_list_str}（共 {len(ALL_MODEL_NAMES)} 个）",
        f"**草稿模型**: {DRAFTING_MODEL}",
        f"**分析论文数**: {len(papers_data)}",
        "---\n",
    ]

    high = [d for d in papers_data if d["merged"].get("relevance", 0) >= 7]
    medium = [d for d in papers_data if 4 <= d["merged"].get("relevance", 0) < 7]

    lines += [
        "## 📊 统计概览\n",
        f"- ⭐ 高相关 (≥7分): **{len(high)}** 篇",
        f"- 🔶 中相关 (4-6分): **{len(medium)}** 篇",
        f"- ⬜ 低相关 (<4分): **{len(papers_data) - len(high) - len(medium)}** 篇\n",
    ]

    if high:
        urgency_order = {"immediate": 0, "next_version": 1, "background": 2}
        high.sort(key=lambda d: urgency_order.get(d["merged"].get("urgency", "background"), 2))

        lines.append(f"## ⭐ 高相关论文 ({len(high)}篇)\n")
        for i, d in enumerate(high, 1):
            p, m = d["paper"], d["merged"]
            lines += [
                f"### {i}. {p['title']}",
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
                lines.append("\n**🧠 多模型评分对比:**")
                lines.append("| 模型 | 相关度 |")
                lines.append("|------|--------|")
                for mn, sc in sorted(m["model_scores"].items(), key=lambda x: x[1], reverse=True):
                    # 美化模型显示名
                    display_name = mn.split("/")[-1][:28]
                    if mn == Config.DRAFTING_MODEL:
                        display_name = "DeepSeek V4 Pro"
                    lines.append(f"| {display_name} | {sc} |")

            if d.get("draft"):
                lines.append("\n**✍️ 自动生成书稿草稿（供参考，请核实后使用）:**")
                lines.append(f"\n> {d['draft']}\n")

            lines.append("")

    # 立即更新清单
    immediate_items = [d for d in papers_data if d["merged"].get("urgency") == DRAFT_URGENCY_REQUIRED and d["merged"].get("relevance", 0) >= DRAFT_RELEVANCE_THRESHOLD]
    if immediate_items:
        lines.append("\n## 🚨 立即更新清单\n")
        for d in immediate_items:
            p, m = d["paper"], d["merged"]
            has_draft = "✍️ 已生成草稿" if d.get("draft") else "⬜ 无草稿"
            lines.append(f"- [ ] **{m.get('chapter_target', '待定')}** — {p['title'][:55]}... ({m.get('update_type', '')}) {has_draft} [链接]({p.get('url', '#')})")

    if medium:
        lines.append(f"\n## 🔶 中相关论文 ({len(medium)}篇)\n")
        for d in medium:
            p, m = d["paper"], d["merged"]
            lines.append(f"- **[{p['title']}]({p.get('url', '#')})** — 相关性: {m['relevance']}/10")
            lines.append(f"  - {m.get('summary_cn', 'N/A')}")
            lines.append("")

    report_path = OUTPUT_DIR / f"report_multi_{today}.md"
    report_path.write_text("\n".join(lines), encoding="utf-8")
    logger.info(f"✅ 多模型报告已保存: {report_path}")
    return str(report_path)

# ------------------------------------------------------------------
# 主函数
# ------------------------------------------------------------------
def main() -> None:
    logger.info("🚀 Renegade AI 文献监控系统 v4.3.1 启动")
    logger.info(f"配置: 分析模型 {len(ALL_MODEL_NAMES)} 个, 草稿模型 {DRAFTING_MODEL}")

    # 加载关键词
    keywords = load_keywords()
    logger.info(f"📋 加载了 {len(keywords)} 个关键词")

    # 多源抓取
    arxiv_papers = search_arxiv(keywords)
    s2_papers = search_semantic_scholar(keywords)
    all_papers = deduplicate_papers(arxiv_papers + s2_papers)
    logger.info(f"📄 合并去重后共 {len(all_papers)} 篇论文")

    if not all_papers:
        logger.info("没有找到新论文，退出。")
        return

    # 增量缓存去重
    cache = load_cache()
    new_papers = [p for p in all_papers if not is_paper_cached(p, cache)]
    logger.info(f"🆕 其中 {len(new_papers)} 篇为新论文（已缓存 {len(all_papers)-len(new_papers)} 篇）")

    if not new_papers:
        logger.info("没有新论文需要分析，退出。")
        return

    # 预筛选
    to_analyze = prescreen_papers(new_papers)
    if not to_analyze:
        logger.info("预筛选后无相关论文，退出。")
        return

    # 多模型分析
    logger.info(f"🤖 开始用 {len(ALL_MODEL_NAMES)} 个模型并发分析 {len(to_analyze)} 篇论文...")
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
        time.sleep(2)  # 论文间冷却，防止 OpenRouter 限流

    # 更新缓存（仅对成功分析的论文）
    for d in papers_data:
        mark_paper_cached(d["paper"], d["merged"], cache)

    # 生成草稿（仅对 immediate 高分论文）
    draft_candidates = [
        d for d in papers_data
        if d["merged"].get("urgency") == DRAFT_URGENCY_REQUIRED
        and d["merged"].get("relevance", 0) >= DRAFT_RELEVANCE_THRESHOLD
    ]
    if draft_candidates:
        logger.info(f"✍️ 为 {len(draft_candidates)} 篇高优先级论文生成书稿草稿...")
        for d in draft_candidates:
            logger.info(f"   草稿: {d['paper']['title'][:55]}...")
            d["draft"] = draft_patch(d["paper"], d["merged"])
            time.sleep(3)

    # 生成报告
    generate_markdown_multi(papers_data, keywords)
    logger.info("✅ 任务完成！")

if __name__ == "__main__":
    main()