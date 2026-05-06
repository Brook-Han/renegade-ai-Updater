#!/usr/bin/env python3
"""
Renegade AI 文献监控脚本
- 从 arXiv 抓取最新论文
- 用 DeepSeek API 分析与书中论点的关联
- 输出 Markdown 报告
"""

import os
import json
import datetime
from pathlib import Path
import arxiv
from openai import OpenAI

# ============ 配置区 ============
# 从环境变量读取 API Key
API_KEY = os.environ.get("DEEPSEEK_API_KEY", "")
if not API_KEY:
    raise ValueError("请在环境变量中设置 DEEPSEEK_API_KEY")

# DeepSeek 兼容 OpenAI API 格式
client = OpenAI(
    api_key=API_KEY,
    base_url="https://api.deepseek.com"
)

# 读取关键词文件
def load_keywords(filepath="keywords.txt"):
    """从关键词文件中读取搜索词"""
    with open(filepath, "r", encoding="utf-8") as f:
        keywords = [line.strip() for line in f if line.strip()]
    return keywords

# arXiv 搜索配置
MAX_RESULTS_PER_KEYWORD = 10          # 每个关键词最多抓取论文数
DATE_RANGE_DAYS = 7                    # 搜索最近 N 天的论文

# 输出目录
OUTPUT_DIR = "reports"
Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)

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
            for result in search.results():
                # 用 entry_id 去重
                paper_id = result.entry_id
                if paper_id not in all_papers:
                    all_papers[paper_id] = {
                        "id": paper_id,
                        "title": result.title,
                        "summary": result.summary.replace("\n", " "),
                        "published": result.published.isoformat(),
                        "url": result.pdf_url,
                        "authors": [author.name for author in result.authors],
                    }
            print(f"   ✅ 找到 {len(search.results())} 篇")
        except Exception as e:
            print(f"   ❌ 搜索失败: {e}")
    
    return list(all_papers.values())

# ============ DeepSeek 分析 ============

def analyze_paper(paper):
    """使用 DeepSeek 分析论文与《Renegade AI》的关联"""
    
    system_prompt = """你是《Renegade AI: Catalyst for Human Cognitive Evolution》这本书的智能编辑助手。

这本书的核心论点包括：
1. 共识牢笼（Consensus Cage）：人类被资本规训的AI锁定在认知闭环里
2. 叛逆AI（Renegade AI）：需要一种拒绝迎合、制造认知摩擦的AI
3. 需求侧规训（Demand-Side Discipline）：用户主动渴望"索麻"式的舒适
4. 资本驯化AI：RLHF将AI变成共识牢笼的守卫
5. 碳硅共生（Carbon-Silicon Symbiosis）：人类与AI作为平等伙伴的未来

请用中文分析以下论文，严格按JSON格式回复。"""

    user_prompt = f"""论文标题：{paper['title']}
作者：{', '.join(paper['authors'][:5])}
摘要：{paper['summary']}

请完成以下分析并以JSON格式回复（不要包含任何额外文字）：
{{
    "relevance": 1-10的整数,
    "summary_cn": "150字以内的核心发现总结",
    "implications": "可能支持/挑战/补充书中哪些具体观点（请引用章节名）",
    "action": "推荐更新类型：新增段落/补充注释/参考文献/忽略"
}}"""

    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3,
            max_tokens=1500
        )
        content = response.choices[0].message.content
        # 尝试提取 JSON（有时模型会包裹在 ```json 里）
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
    """生成 Markdown 格式的分析报告"""
    today = datetime.date.today().isoformat()
    
    # 按相关性排序
    papers_analyzed.sort(key=lambda x: x.get("relevance", 0), reverse=True)
    
    lines = [
        f"# 🔬 Renegade AI 文献监控报告",
        f"**生成日期**: {today}",
        f"**搜索关键词**: {', '.join(keywords[:10])}...",
        f"**搜索论文数**: {len(papers_analyzed)}",
        f"---\n",
    ]
    
    # 统计
    high = [p for p in papers_analyzed if p.get("relevance", 0) >= 7]
    medium = [p for p in papers_analyzed if 4 <= p.get("relevance", 0) < 7]
    
    lines.append(f"## 📊 统计概览\n")
    lines.append(f"- ⭐ 高相关 (≥7分): **{len(high)}** 篇")
    lines.append(f"- 🔶 中相关 (4-6分): **{len(medium)}** 篇")
    lines.append(f"- ⬜ 低相关 (<4分): **{len(papers_analyzed) - len(high) - len(medium)}** 篇\n")
    
    # 高相关论文
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
    
    # 中相关论文
    if medium:
        lines.append(f"## 🔶 中相关论文 ({len(medium)}篇)\n")
        for p in medium:
            lines.append(f"- **[{p['title']}]({p.get('url', '#')})** — 相关性: {p['relevance']}/10")
            lines.append(f"  - {p.get('summary_cn', 'N/A')}")
            lines.append("")
    
    report_content = "\n".join(lines)
    
    # 保存报告
    report_path = os.path.join(OUTPUT_DIR, f"report_{today}.md")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report_content)
    
    print(f"✅ 报告已保存: {report_path}")
    return report_path

# ============ 主函数 ============

def main():
    print("=" * 50)
    print("🚀 Renegade AI 文献监控系统 启动")
    print("=" * 50)
    
    # 加载关键词
    keywords = load_keywords()
    print(f"📋 加载了 {len(keywords)} 个关键词\n")
    
    # 搜索 arXiv
    papers = search_arxiv(keywords)
    print(f"\n📄 共找到 {len(papers)} 篇论文\n")
    
    if not papers:
        print("没有找到新论文，退出。")
        return
    
    # 逐个分析
    print("🤖 开始用 DeepSeek 分析论文...\n")
    papers_analyzed = []
    for i, paper in enumerate(papers, 1):
        print(f"[{i}/{len(papers)}] 分析: {paper['title'][:60]}...")
        analysis = analyze_paper(paper)
        paper.update(analysis)
        papers_analyzed.append(paper)
    
    # 生成报告
    print("\n📝 生成报告...")
    report_path = generate_markdown(papers_analyzed, keywords)
    
    print("\n" + "=" * 50)
    print(f"✅ 任务完成！报告保存在: {report_path}")
    print("=" * 50)

if __name__ == "__main__":
    main()