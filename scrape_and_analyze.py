#!/usr/bin/env python3
"""
Renegade AI 文献监控脚本 v4.1 — 多模型复证版 (最终版)
改进点：
1. 修复合并策略：加权平均 + 异常值剔除，避免单一模型误判
2. 修复 Semantic Scholar URL 逻辑
3. 增加论文间间隔，避免 OpenRouter 限流
4. 报告底部自动生成 Markdown 待办清单
"""

import os
import json
import time
import datetime
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import arxiv
import requests
from openai import OpenAI
from dotenv import load_dotenv

# ============ 环境初始化 ============
load_dotenv()

DEEPSEEK_KEY = os.environ.get("DEEPSEEK_API_KEY", "")
OPENROUTER_KEY = os.environ.get("OPENROUTER_API_KEY", "")
if not DEEPSEEK_KEY and not OPENROUTER_KEY:
    raise ValueError("请至少设置 DEEPSEEK_API_KEY 或 OPENROUTER_API_KEY 环境变量")

deepseek_client = OpenAI(api_key=DEEPSEEK_KEY, base_url="https://api.deepseek.com") if DEEPSEEK_KEY else None
openrouter_client = (
    OpenAI(
        api_key=OPENROUTER_KEY,
        base_url="https://openrouter.ai/api/v1",
        default_headers={
            "HTTP-Referer": "https://github.com/Brook-Han/renegade-ai-Updater",
            "X-Title": "Renegade AI Radar"
        }
    ) if OPENROUTER_KEY else None
)

arxiv_client = arxiv.Client(page_size=100, delay_seconds=5.0, num_retries=5)

# ============ 配置 ============
KEYWORDS_FILE = "keywords.txt"
MAX_RESULTS_PER_KEYWORD = 10
OUTPUT_DIR = "reports"
Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
SEEN_IDS_FILE = "seen_ids.json"

FREE_MODELS = [
    "google/gemini-2.0-flash-exp:free",
    "qwen/qwen3.6-plus-preview:free",
    "meta-llama/llama-3.3-70b-instruct:free",
    "nvidia/nemotron-3-super:free",
]
CHEAP_PAID_MODELS = [
    "google/gemini-2.5-flash",
    "deepseek/deepseek-chat",
    "mistralai/mistral-small-3.1-24b",
]
STRONG_PAID_MODELS = [
    "anthropic/claude-sonnet-4",
    "openai/gpt-4o-mini",
]
ANALYSIS_MODELS = FREE_MODELS + CHEAP_PAID_MODELS

# ============ 工具函数 ============
def load_keywords(filepath=KEYWORDS_FILE):
    with open(filepath, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]

def safe_str(text):
    return text.encode('ascii', 'ignore').decode('ascii')

def load_seen_ids():
    if Path(SEEN_IDS_FILE).exists():
        with open(SEEN_IDS_FILE) as f:
            return set(json.load(f))
    return set()

def save_seen_ids(seen_ids):
    with open(SEEN_IDS_FILE, "w") as f:
        json.dump(list(seen_ids), f)

# ============ 多源抓取 ============
def search_arxiv(keywords, max_results=MAX_RESULTS_PER_KEYWORD):
    all_papers = {}
    for keyword in keywords:
        print(f"🔍 [arXiv] 正在搜索: {keyword}")
        for attempt in range(3):
            try:
                search = arxiv.Search(query=keyword, max_results=max_results, sort_by=arxiv.SortCriterion.SubmittedDate)
                count = 0
                for result in arxiv_client.results(search):
                    paper_id = result.entry_id
                    if paper_id not in all_papers:
                        all_papers[paper_id] = {
                            "id": paper_id,
                            "title": safe_str(result.title),
                            "summary": safe_str(result.summary.replace("\n", " ")),
                            "published": result.published.isoformat() if result.published else "N/A",
                            "url": result.pdf_url,
                            "authors": [a.name for a in result.authors],
                        }
                        count += 1
                print(f"   ✅ 找到 {count} 篇")
                break
            except Exception as e:
                if attempt < 2:
                    wait = (attempt + 1) * 10
                    print(f"   ⚠️ 请求失败，{wait}秒后重试... ({e})")
                    time.sleep(wait)
                else:
                    print(f"   ❌ 三次重试后仍失败: {e}")
        time.sleep(3)
    return list(all_papers.values())

def search_semantic_scholar(keywords, limit=5):
    papers = []
    for keyword in keywords:
        print(f"🔍 [Semantic Scholar] 正在搜索: {keyword}")
        try:
            url = "https://api.semanticscholar.org/graph/v1/paper/search"
            params = {
                "query": keyword,
                "limit": limit,
                "fields": "paperId,title,abstract,authors,year,externalIds,openAccessPdf"
            }
            
            # 改进后的重试机制：更长初始等待、更大间隔
            max_retries = 3
            r = None
            for attempt in range(max_retries):
                try:
                    r = requests.get(url, params=params, timeout=30)
                    if r.status_code == 429:
                        wait = (attempt + 1) * 15  # 15s → 30s → 45s
                        print(f"   ⚠️ Semantic Scholar 限速，等待 {wait} 秒...")
                        time.sleep(wait)
                        continue
                    r.raise_for_status()
                    break  # 成功跳出
                except requests.exceptions.RequestException as e:
                    if r is not None and r.status_code == 429:
                        continue
                    raise e
            
            if r is None or r.status_code == 429:
                print(f"   ❌ Semantic Scholar 搜索失败（重试耗尽），跳过: {keyword}")
                continue
            
            data = r.json().get("data", [])
            for p in data:
                papers.append({
                    "id": p.get("paperId", ""),
                    "title": safe_str(p.get("title", "")),
                    "summary": safe_str(p.get("abstract", "") or ""),
                    "published": str(p.get("year", "")) if p.get("year") else "N/A",
                    "url": (p.get("openAccessPdf") or {}).get("url") or
                           f"https://api.semanticscholar.org/CorpusID:{p.get('externalIds', {}).get('CorpusId', '')}",
                    "authors": [a.get("name", "") for a in p.get("authors", [])],
                })
            print(f"   ✅ 找到 {len(data)} 篇")
            
        except Exception as e:
            print(f"   ❌ 搜索失败: {e}")
        
        # 每个关键词之间等待，降低请求频率
        time.sleep(3)
    
    return papers

def deduplicate_papers(papers):
    seen = set()
    unique = []
    for p in papers:
        if p["id"] not in seen:
            seen.add(p["id"])
            unique.append(p)
    return unique

def prescreen_papers(papers):
    relevant_terms = [
        'AI', 'artificial intelligence', 'LLM', 'language model', 'GPT',
        'algorithm', 'automation', 'machine learning', 'neural',
        'cognitive', 'persuasion', 'manipulation', 'sycophan',
        'alignment', 'RLHF', 'human-AI', 'humanAI',
        'capital', 'labor', 'work', 'job', 'employment',
        'ethics', 'bias', 'fairness', 'governance',
        'well-being', 'wellbeing', 'mental health',
        'companion', 'chatbot', 'conversational',
        'delegation', 'decision', 'advice', 'trust',
        'open source', 'decentraliz', 'compute',
        'Darwinian', 'evolution', 'digital evolution',
        'token', 'financialization'
    ]
    filtered = []
    for p in papers:
        text = (p['title'] + ' ' + p['summary']).lower()
        if any(term.lower() in text for term in relevant_terms):
            filtered.append(p)
    print(f"🔬 预筛选：{len(papers)} → {len(filtered)} 篇（过滤 {len(papers)-len(filtered)} 篇）")
    return filtered

# ============ 多模型分析核心 ============
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
阅读以下论文摘要，返回严格JSON（不要其他文字）。"""

def analyze_single_model(paper, model_name, client):
    user_prompt = f"""论文标题：{paper['title']}
作者：{', '.join(paper['authors'][:5])}
摘要：{paper['summary']}

请返回JSON：
{{
    "relevance": 1-10的整数,
    "summary_cn": "150字以内核心发现（中文）",
    "implications": "与书中哪章哪节哪个具体论点相关？支持/挑战/补充？",
    "chapter_target": "例如：Chapter 6, Section II",
    "update_type": "new_evidence / counter_argument / corroboration",
    "urgency": "immediate / next_version / background",
    "action": "新增段落 / 补充注释 / 参考文献 / 忽略"
}}

注意：
- 若与上述概念、实证锚点无关，relevance应低于4，action为"忽略"
- 纯技术性论文评为低相关"""

    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=[{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": user_prompt}],
            temperature=0.2, max_tokens=1500
        )
        content = response.choices[0].message.content
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0]
        elif "```" in content:
            content = content.split("```")[1].split("```")[0]
        result = json.loads(content.strip())
        result["_model"] = model_name
        return result
    except Exception as e:
        return {"relevance": 0, "summary_cn": f"调用失败: {str(e)[:80]}", "_model": model_name,
                "implications": "N/A", "chapter_target": "", "update_type": "", "urgency": "background", "action": "忽略"}

def merge_results(results):
    """加权平均 + 异常值剔除"""
    valid = [r for r in results if r.get("relevance", 0) > 0]
    if not valid:
        return {"relevance": 0, "action": "忽略", "summary_cn": "所有模型调用失败", "implications": "N/A",
                "chapter_target": "", "update_type": "", "urgency": "background"}

    scores = [r["relevance"] for r in valid]
    avg = sum(scores) / len(scores)
    # 异常值剔除：最高分与平均分差距超过3，去掉最高分
    max_score = max(scores)
    if max_score - avg > 3 and len(scores) > 2:
        scores_trimmed = sorted(scores)[:-1]
        avg = sum(scores_trimmed) / len(scores_trimmed)

    consensus = min(valid, key=lambda r: abs(r["relevance"] - avg))
    merged = {k: v for k, v in consensus.items() if not k.startswith("_")}
    merged["relevance"] = round(avg, 1)
    merged["model_scores"] = {r["_model"]: r["relevance"] for r in valid}
    return merged

def analyze_paper_multi_model(paper, models):
    tasks = []
    if deepseek_client:
        tasks.append(("deepseek/deepseek-chat", deepseek_client))
    if openrouter_client:
        for model_name in models:
            tasks.append((model_name, openrouter_client))

    results = []
    with ThreadPoolExecutor(max_workers=min(len(tasks), 3)) as executor:
        future_map = {
            executor.submit(analyze_single_model, paper, model_name, client): model_name
            for model_name, client in tasks
        }
        for future in as_completed(future_map):
            results.append(future.result())

    merged = merge_results(results)
    return results, merged

# ============ 报告生成 ============
def generate_markdown_multi(papers_data, keywords):
    today = datetime.date.today().isoformat()
    papers_data.sort(key=lambda d: d["merged"].get("relevance", 0), reverse=True)

    lines = [
        f"# 🔬 Renegade AI 文献监控报告（多模型复证）",
        f"**生成日期**: {today}",
        f"**模型阵容**: {ANALYSIS_MODELS[0]}, ...（共 {len(ANALYSIS_MODELS)} 个）",
        f"**分析论文数**: {len(papers_data)}",
        f"---\n",
    ]

    high = [d for d in papers_data if d["merged"].get("relevance", 0) >= 7]
    medium = [d for d in papers_data if 4 <= d["merged"].get("relevance", 0) < 7]

    lines.append(f"## 📊 统计概览\n")
    lines.append(f"- ⭐ 高相关 (≥7分): **{len(high)}** 篇")
    lines.append(f"- 🔶 中相关 (4-6分): **{len(medium)}** 篇")
    lines.append(f"- ⬜ 低相关 (<4分): **{len(papers_data) - len(high) - len(medium)}** 篇\n")

    if high:
        urgency_order = {"immediate": 0, "next_version": 1, "background": 2}
        high.sort(key=lambda d: urgency_order.get(d["merged"].get("urgency", "background"), 2))

        lines.append(f"## ⭐ 高相关论文 ({len(high)}篇)\n")
        for i, d in enumerate(high, 1):
            p = d["paper"]
            m = d["merged"]
            lines.append(f"### {i}. {p['title']}")
            lines.append(f"- **最终评分**: {m['relevance']}/10")
            lines.append(f"- **紧迫度**: {m.get('urgency', 'N/A')}")
            lines.append(f"- **更新类型**: {m.get('update_type', 'N/A')}")
            lines.append(f"- **目标章节**: {m.get('chapter_target', 'N/A')}")
            lines.append(f"- **链接**: {p.get('url', 'N/A')}")
            lines.append(f"- **核心发现**: {m.get('summary_cn', 'N/A')}")
            lines.append(f"- **与本书关联**: {m.get('implications', 'N/A')}")
            lines.append(f"- **建议更新**: {m.get('action', 'N/A')}")

            if m.get("model_scores"):
                lines.append(f"\n**🧠 多模型评分对比:**")
                lines.append("| 模型 | 相关度 |")
                lines.append("|------|--------|")
                for model_name, score in sorted(m["model_scores"].items(), key=lambda x: x[1], reverse=True):
                    model_short = model_name.split("/")[-1][:25]
                    lines.append(f"| {model_short} | {score} |")
            lines.append("")

    # 🚨 立即更新清单
    immediate_items = [
        d for d in papers_data
        if d["merged"].get("urgency") == "immediate" and d["merged"].get("relevance", 0) >= 7
    ]
    if immediate_items:
        lines.append("\n## 🚨 立即更新清单\n")
        for d in immediate_items:
            p = d["paper"]
            m = d["merged"]
            lines.append(
                f"- [ ] **{m.get('chapter_target', '待定')}** — "
                f"{p['title'][:60]}... "
                f"({m.get('update_type', '')}) "
                f"[链接]({p.get('url', '#')})"
            )

    if medium:
        lines.append(f"\n## 🔶 中相关论文 ({len(medium)}篇)\n")
        for d in medium:
            p = d["paper"]
            m = d["merged"]
            lines.append(f"- **[{p['title']}]({p.get('url', '#')})** — 相关性: {m['relevance']}/10")
            lines.append(f"  - {m.get('summary_cn', 'N/A')}")
            lines.append("")

    report_path = os.path.join(OUTPUT_DIR, f"report_multi_{today}.md")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"✅ 多模型报告已保存: {report_path}")
    return report_path

# ============ 主函数 ============
def main():
    print("=" * 50)
    print("🚀 Renegade AI 文献监控系统 v4.1 启动")
    print("=" * 50)

    keywords = load_keywords()
    print(f"📋 加载了 {len(keywords)} 个关键词\n")

    arxiv_papers = search_arxiv(keywords)
    s2_papers = search_semantic_scholar(keywords)
    all_papers = deduplicate_papers(arxiv_papers + s2_papers)
    print(f"\n📄 合并去重后共 {len(all_papers)} 篇论文\n")

    if not all_papers:
        print("没有找到新论文，退出。")
        return

    seen_ids = load_seen_ids()
    new_papers = [p for p in all_papers if p["id"] not in seen_ids]
    print(f"🆕 其中 {len(new_papers)} 篇为新论文（已分析过的 {len(seen_ids)} 篇已跳过）")
    if not new_papers:
        print("没有新论文需要分析，退出。")
        return

    to_analyze = prescreen_papers(new_papers)
    if not to_analyze:
        print("预筛选后无相关论文，退出。")
        return

    print(f"\n🤖 开始用 {len(ANALYSIS_MODELS)} 个模型并发分析 {len(to_analyze)} 篇论文...\n")
    papers_data = []
    for i, paper in enumerate(to_analyze, 1):
        print(f"[{i}/{len(to_analyze)}] 分析: {paper['title'][:60]}...")
        models_results, merged = analyze_paper_multi_model(paper, ANALYSIS_MODELS)
        papers_data.append({"paper": paper, "merged": merged, "models_results": models_results})
        time.sleep(2)  # 论文间间隔2秒，防止 OpenRouter 限流

    for p in to_analyze:
        seen_ids.add(p["id"])
    save_seen_ids(seen_ids)

    print("\n📝 生成多模型报告...")
    generate_markdown_multi(papers_data, keywords)
    print("\n" + "=" * 50)
    print("✅ 任务完成！")
    print("=" * 50)

if __name__ == "__main__":
    main()