#!/usr/bin/env python3
"""
Renegade AI 文献监控脚本 v3.0
- 多源抓取：arXiv + Semantic Scholar
- 窄而精的关键词组合
- 增量去重，避免重复分析
- 增强版 system prompt，输出结构化更新任务
- 生成 Markdown 报告
"""

import os
import json
import datetime
from pathlib import Path
import arxiv
import requests
from openai import OpenAI
from dotenv import load_dotenv

# ============ 环境初始化 ============
load_dotenv()
API_KEY = os.environ.get("DEEPSEEK_API_KEY", "")
if not API_KEY:
    raise ValueError("请设置环境变量 DEEPSEEK_API_KEY (或创建 .env 文件)")

client = OpenAI(api_key=API_KEY, base_url="https://api.deepseek.com")
arxiv_client = arxiv.Client()

# ============ 配置 ============
KEYWORDS_FILE = "keywords.txt"
MAX_RESULTS_PER_KEYWORD = 10
OUTPUT_DIR = "reports"
Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
SEEN_IDS_FILE = "seen_ids.json"

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
    """arXiv 抓取"""
    all_papers = {}
    for keyword in keywords:
        print(f"🔍 [arXiv] 正在搜索: {keyword}")
        try:
            search = arxiv.Search(
                query=keyword,
                max_results=max_results,
                sort_by=arxiv.SortCriterion.SubmittedDate
            )
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
        except Exception as e:
            print(f"   ❌ 搜索失败: {e}")
    return list(all_papers.values())

def search_semantic_scholar(keywords, limit=10):
    """Semantic Scholar 抓取"""
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
            r = requests.get(url, params=params, timeout=15)
            r.raise_for_status()
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
    return papers

def deduplicate_papers(papers):
    """按 ID 去重，保留第一批次"""
    seen = set()
    unique = []
    for p in papers:
        if p["id"] not in seen:
            seen.add(p["id"])
            unique.append(p)
    return unique

def prescreen_papers(papers):
    """预筛选：过滤明显不相关的论文"""
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

# ============ DeepSeek 分析（增强版） ============

def analyze_paper(paper):
    """使用 DeepSeek 分析论文，输出结构化更新任务"""
    system_prompt = """你是《Renegade AI: Catalyst for Human Cognitive Evolution》(v5.3) 的智能编辑助手。你需要判断一篇学术论文是否与本书的核心论点相关，并给出具体的更新建议。

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
- 若与上述概念、实证锚点无关，relevance应低于4，action为“忽略”
- 纯技术性论文评为低相关"""

    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.2,
            max_tokens=1500
        )
        content = response.choices[0].message.content
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0]
        elif "```" in content:
            content = content.split("```")[1].split("```")[0]
        return json.loads(content.strip())
    except Exception as e:
        print(f"   ⚠️ 分析失败: {e}")
        return {
            "relevance": 0,
            "summary_cn": "Analysis failed",
            "implications": "N/A",
            "chapter_target": "",
            "update_type": "",
            "urgency": "background",
            "action": "忽略"
        }

# ============ 生成报告 ============

def generate_markdown(papers_analyzed, keywords):
    today = datetime.date.today().isoformat()
    papers_analyzed.sort(key=lambda x: x.get("relevance", 0), reverse=True)

    lines = [
        f"# 🔬 Renegade AI 文献监控报告",
        f"**生成日期**: {today}",
        f"**搜索关键词数**: {len(keywords)}",
        f"**分析论文数**: {len(papers_analyzed)}",
        f"---\n",
    ]

    high = [p for p in papers_analyzed if p.get("relevance", 0) >= 7]
    medium = [p for p in papers_analyzed if 4 <= p.get("relevance", 0) < 7]

    lines.append(f"## 📊 统计概览\n")
    lines.append(f"- ⭐ 高相关 (≥7分): **{len(high)}** 篇")
    lines.append(f"- 🔶 中相关 (4-6分): **{len(medium)}** 篇")
    lines.append(f"- ⬜ 低相关 (<4分): **{len(papers_analyzed) - len(high) - len(medium)}** 篇\n")

    # 高相关论文，按紧迫度排序
    if high:
        urgency_order = {"immediate": 0, "next_version": 1, "background": 2}
        high.sort(key=lambda p: urgency_order.get(p.get("urgency", "background"), 2))

        lines.append(f"## ⭐ 高相关论文 ({len(high)}篇) 按更新紧迫度排序\n")
        for i, p in enumerate(high, 1):
            lines.append(f"### {i}. {p['title']}")
            lines.append(f"- **相关性评分**: {p['relevance']}/10")
            lines.append(f"- **紧迫度**: {p.get('urgency', 'N/A')}")
            lines.append(f"- **更新类型**: {p.get('update_type', 'N/A')}")
            lines.append(f"- **目标章节**: {p.get('chapter_target', 'N/A')}")
            lines.append(f"- **作者**: {', '.join(p.get('authors', []))}")
            lines.append(f"- **发表时间**: {p.get('published', 'N/A')}")
            lines.append(f"- **链接**: {p.get('url', 'N/A')}")
            lines.append(f"- **核心发现**: {p.get('summary_cn', 'N/A')}")
            lines.append(f"- **与本书关联**: {p.get('implications', 'N/A')}")
            lines.append(f"- **建议更新**: {p.get('action', 'N/A')}")
            lines.append("")

    if medium:
        lines.append(f"## 🔶 中相关论文 ({len(medium)}篇)\n")
        for p in medium:
            lines.append(f"- **[{p['title']}]({p.get('url', '#')})** — 相关性: {p['relevance']}/10")
            lines.append(f"  - {p.get('summary_cn', 'N/A')}")
            lines.append("")

    report_path = os.path.join(OUTPUT_DIR, f"report_{today}.md")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"✅ 报告已保存: {report_path}")
    return report_path

# ============ 主函数 ============

def main():
    print("=" * 50)
    print("🚀 Renegade AI 文献监控系统 启动 (v3.0)")
    print("=" * 50)

    keywords = load_keywords()
    print(f"📋 加载了 {len(keywords)} 个关键词\n")

    # 抓取
    arxiv_papers = search_arxiv(keywords)
    s2_papers = search_semantic_scholar(keywords)
    all_papers = deduplicate_papers(arxiv_papers + s2_papers)
    print(f"\n📄 合并去重后共 {len(all_papers)} 篇论文\n")

    if not all_papers:
        print("没有找到新论文，退出。")
        return

    # 增量去重
    seen_ids = load_seen_ids()
    new_papers = [p for p in all_papers if p["id"] not in seen_ids]
    print(f"🆕 其中 {len(new_papers)} 篇为新论文（已分析过的 {len(seen_ids)} 篇已跳过）")
    if not new_papers:
        print("没有新论文需要分析，退出。")
        return

    # 预筛选
    to_analyze = prescreen_papers(new_papers)
    if not to_analyze:
        print("预筛选后无相关论文，退出。")
        return

    # 分析
    print(f"\n🤖 开始用 DeepSeek 分析 {len(to_analyze)} 篇论文...\n")
    for i, paper in enumerate(to_analyze, 1):
        print(f"[{i}/{len(to_analyze)}] 分析: {paper['title'][:60]}...")
        analysis = analyze_paper(paper)
        paper.update(analysis)

    # 标记已分析
    for p in to_analyze:
        seen_ids.add(p["id"])
    save_seen_ids(seen_ids)

    print("\n📝 生成报告...")
    generate_markdown(to_analyze, keywords)
    print("\n" + "=" * 50)
    print("✅ 任务完成！")
    print("=" * 50)

if __name__ == "__main__":
    main()