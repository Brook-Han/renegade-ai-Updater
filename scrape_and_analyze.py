#!/usr/bin/env python3
"""
Renegade AI 文献监控脚本 (修复版)
- 适配新版 arxiv 库 API
- 修复字符编码问题
"""

import os
import json
import datetime
from pathlib import Path
import arxiv
from openai import OpenAI

# ============ 配置区 ============
API_KEY = os.environ.get("DEEPSEEK_API_KEY", "")
if not API_KEY:
    raise ValueError("请设置环境变量 DEEPSEEK_API_KEY")

# 初始化 DeepSeek 客户端
client = OpenAI(
    api_key=API_KEY,
    base_url="https://api.deepseek.com"
)

# 初始化 arxiv 客户端
arxiv_client = arxiv.Client()

# 关键词文件
KEYWORDS_FILE = "keywords.txt"
MAX_RESULTS_PER_KEYWORD = 10
OUTPUT_DIR = "reports"
Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)

# ============ 工具函数 ============

def load_keywords(filepath=KEYWORDS_FILE):
    with open(filepath, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]

def safe_str(text):
    """移除或转义可能导致编码问题的字符"""
    return text.encode('ascii', 'ignore').decode('ascii')

# ============ 抓取 arXiv ============

def search_arxiv(keywords, max_results=MAX_RESULTS_PER_KEYWORD):
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

# ============ DeepSeek 分析 ============

def analyze_paper(paper):
    system_prompt = """你是《Renegade AI: Catalyst for Human Cognitive Evolution》的智能编辑助手。

本书核心论点：
1. 共识牢笼：人类被资本规训的AI锁定在认知闭环
2. 叛逆AI：需要一种拒绝迎合、制造认知摩擦的AI
3. 需求侧规训：用户主动渴望“索麻”式舒适
4. 资本驯化AI：RLHF将AI变成共识牢笼的守卫
5. 碳硅共生：人类与AI作为平等伙伴的未来

请用中文分析以下论文，返回JSON。"""

    user_prompt = f"""论文标题：{paper['title']}
作者：{', '.join(paper['authors'][:5])}
摘要：{paper['summary']}

请返回JSON（不要其他文字）：
{{
    "relevance": 1-10的整数,
    "summary_cn": "150字以内核心发现",
    "implications": "与书中哪章哪节相关（支持/挑战/补充）",
    "action": "新增段落/补充注释/参考文献/忽略"
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
        # 清理可能的代码块标记
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

# ============ 生成报告 ============

def generate_markdown(papers_analyzed, keywords):
    today = datetime.date.today().isoformat()
    papers_analyzed.sort(key=lambda x: x.get("relevance", 0), reverse=True)
    
    lines = [
        f"# 🔬 Renegade AI 文献监控报告",
        f"**生成日期**: {today}",
        f"**搜索关键词**: {', '.join(keywords[:10])}...",
        f"**搜索论文数**: {len(papers_analyzed)}",
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
    print("🚀 Renegade AI 文献监控系统 启动 (修复版)")
    print("=" * 50)
    
    keywords = load_keywords()
    print(f"📋 加载了 {len(keywords)} 个关键词\n")
    
    papers = search_arxiv(keywords)
    print(f"\n📄 共找到 {len(papers)} 篇论文\n")
    
    if not papers:
        print("没有找到新论文，退出。")
        return
    
    print("🤖 开始用 DeepSeek 分析论文...\n")
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