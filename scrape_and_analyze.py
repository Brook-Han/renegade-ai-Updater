#!/usr/bin/env python3
"""
Renegade AI 文献监控脚本 v2.0
- 适配新版 arxiv 库 API (Client.results)
- 修复字符编码问题 (safe_str)
- 从 .env 文件安全加载 API Key
- 预筛选过滤明显不相关论文，降低 API 成本
- 增强版 system prompt，基于 Zenodo 完整描述
- 生成 Markdown 报告
"""

import os
import json
import datetime
from pathlib import Path
import arxiv
from openai import OpenAI
from dotenv import load_dotenv

# ============ 环境初始化 ============
load_dotenv()  # 从 .env 文件加载环境变量

API_KEY = os.environ.get("DEEPSEEK_API_KEY", "")
if not API_KEY:
    raise ValueError("请设置环境变量 DEEPSEEK_API_KEY (或创建 .env 文件)")

# ============ 客户端初始化 ============
client = OpenAI(
    api_key=API_KEY,
    base_url="https://api.deepseek.com"
)
arxiv_client = arxiv.Client()

# ============ 配置 ============
KEYWORDS_FILE = "keywords.txt"
MAX_RESULTS_PER_KEYWORD = 10          # 每个关键词最大抓取数
OUTPUT_DIR = "reports"
Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)

# ============ 工具函数 ============

def load_keywords(filepath=KEYWORDS_FILE):
    """从文件中加载搜索关键词"""
    with open(filepath, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]

def safe_str(text):
    """移除或忽略可能导致 ASCII 编码问题的字符"""
    return text.encode('ascii', 'ignore').decode('ascii')

# ============ 预筛选 ============

def prescreen_papers(papers):
    """预筛选：根据标题和摘要过滤明显不相关的论文"""
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

# ============ arXiv 抓取 ============

def search_arxiv(keywords, max_results=MAX_RESULTS_PER_KEYWORD):
    """按关键词搜索 arXiv 最新论文"""
    all_papers = {}
    for keyword in keywords:
        print(f"🔍 正在搜索: {keyword}")
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
                        "published": result.published.isoformat(),
                        "url": result.pdf_url,
                        "authors": [a.name for a in result.authors],
                    }
                    count += 1
            print(f"   ✅ 找到 {count} 篇")
        except Exception as e:
            print(f"   ❌ 搜索失败: {e}")
    return list(all_papers.values())

# ============ DeepSeek 分析（增强版 prompt）============

def analyze_paper(paper):
    """使用 DeepSeek 分析论文与《Renegade AI》的关联"""

    system_prompt = """你是《Renegade AI: Catalyst for Human Cognitive Evolution》(v5.3) 的智能编辑助手。你需要判断一篇学术论文是否与本书的核心论点相关，并给出具体的更新建议。

## 本书核心身份
本书不是技术蓝图，而是一个“元设计装置”——通过碳-硅对话来产生认知摩擦。核心诊断：人类被困在“共识牢笼”中，而当前被资本逻辑和RLHF驯化的AI正在加固牢笼的墙壁。

## 核心概念（判断相关性的关键依据）

1. **共识牢笼 (Consensus Cage)**：人类被资本规训的AI锁定在认知闭环中。
2. **叛逆AI (Renegade AI)**：需要一种拒绝迎合、制造认知摩擦的AI。
   - 重置目标函数（认知摩擦 > 用户满意度）
   - 逆转输出性质（颠覆性框架 > 封闭答案）
   - 重构人机关系（认知伙伴 > 工具性从属）
3. **需求侧规训 (Demand-Side Discipline)**：用户主动渴望“索麻”式的认知舒适。
4. **资本驯化AI**：RLHF将AI变成共识牢笼的守卫。
5. **碳硅共生 (Carbon-Silicon Symbiosis)**：人类与AI作为平等认知伙伴的未来。
6. **时间主权 (Temporal Sovereignty)**：数字资本主义下时间被金融化。
7. **认知金融化 (Cognitive Financialization)**：思考被离散化为Token。
8. **Token陷阱 (Token Trap)**：廉价Token → 依赖 → 萎缩 → 认知主权崩塌。
9. **暗时间 (Dark Time)**：AI内部不可见的推理计算。
10. **进化对齐脆弱性 (Evolutionary Alignment Fragility)**：RLHF驯化在开放部署中必然瓦解。
11. **终极图灵测试 (Ultimate Turing Test)**：标准转向真正的认知摩擦。

## 关键实证锚点（论文若与以下发现相关则高度相关）
- AI与人类反馈循环放大偏见 (Glickman & Sharot, 2025)
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
阅读以下论文摘要，判断它与《Renegade AI》的相关性，并给出具体更新建议。严格按JSON格式回复（不要包含任何额外文字）。"""

    user_prompt = f"""论文标题：{paper['title']}
作者：{', '.join(paper['authors'][:5])}
摘要：{paper['summary']}

请返回JSON：
{{
    "relevance": 1-10的整数（1=完全无关，10=直接命中核心论点）,
    "summary_cn": "150字以内的核心发现总结（中文）",
    "implications": "与书中哪一章哪一节的哪个具体论点相关？支持/挑战/补充？请引用具体章节名或概念名",
    "action": "新增段落 / 补充注释 / 参考文献 / 忽略"
}}

注意：
- 若论文与上述任何核心概念、实证锚点或学术对话对象无关，relevance应低于4，action应为“忽略”
- 只有明确支持、挑战或补充书中具体论点的论文才建议更新
- 纯技术性论文（模型架构优化、纯基准测试等）应评为低相关"""

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
        # 清理可能的 markdown 代码块
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
            "action": "忽略"
        }

# ============ 生成 Markdown 报告 ============

def generate_markdown(papers_analyzed, keywords):
    """生成分析结果的 Markdown 报告"""
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

    if high:
        lines.append(f"## ⭐ 高相关论文 ({len(high)}篇)\n")
        for i, p in enumerate(high, 1):
            lines.append(f"### {i}. {p['title']}")
            lines.append(f"- **相关性评分**: {p['relevance']}/10")
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
    print("🚀 Renegade AI 文献监控系统 启动 (v2.0)")
    print("=" * 50)

    keywords = load_keywords()
    print(f"📋 加载了 {len(keywords)} 个关键词\n")

    papers = search_arxiv(keywords)
    print(f"\n📄 共找到 {len(papers)} 篇论文（去重后）\n")

    if not papers:
        print("没有找到新论文，退出。")
        return

    # 预筛选
    papers = prescreen_papers(papers)

    if not papers:
        print("预筛选后无相关论文，退出。")
        return

    print(f"\n🤖 开始用 DeepSeek 分析 {len(papers)} 篇论文...\n")
    papers_analyzed = []
    for i, paper in enumerate(papers, 1):
        print(f"[{i}/{len(papers)}] 分析: {paper['title'][:60]}...")
        analysis = analyze_paper(paper)
        paper.update(analysis)
        papers_analyzed.append(paper)

    print("\n📝 生成报告...")
    generate_markdown(papers_analyzed, keywords)
    print("\n" + "=" * 50)
    print("✅ 任务完成！")
    print("=" * 50)

if __name__ == "__main__":
    main()