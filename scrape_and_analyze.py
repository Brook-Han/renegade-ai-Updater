"""
Renegade AI 研究监控脚本
抓取 arXiv 最新论文，用大模型分析相关性，结果存入 Notion
"""

import os
import json
import arxiv
from openai import OpenAI
from notion_client import Client

# ============================================================
# 配置区 —— 从环境变量读取密钥
# ============================================================
ARXIV_MAX_RESULTS = 30
ARXIV_DAYS_BACK = 7
RELEVANCE_THRESHOLD = 7  # 相关性 >= 此分数的论文才会被推送

client_openai = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
client_notion = Client(auth=os.environ.get("NOTION_API_KEY"))
NOTION_DATABASE_ID = os.environ.get("NOTION_DATABASE_ID", "")

# ============================================================
# 加载关键词
# ============================================================
def load_keywords(filepath="keywords.txt"):
    """从 keywords.txt 加载关键词列表"""
    with open(filepath, "r") as f:
        keywords = [line.strip() for line in f if line.strip() and not line.startswith("#")]
    return keywords

# ============================================================
# 抓取 arXiv 论文
# ============================================================
def search_arxiv(keywords, max_results=ARXIV_MAX_RESULTS):
    """根据关键词搜索 arXiv 最新论文"""
    query = " OR ".join([f'("{kw}")' for kw in keywords])

    client = arxiv.Client()
    search = arxiv.Search(
        query=query,
        max_results=max_results,
        sort_by=arxiv.SortCriterion.SubmittedDate
    )

    papers = []
    for paper in client.results(search):
        papers.append({
            "id": paper.entry_id.split("/")[-1],
            "title": paper.title,
            "summary": paper.summary.replace("\n", " "),
            "published": paper.published.isoformat(),
            "url": paper.pdf_url,
            "source": "arxiv"
        })
    return papers

# ============================================================
# 用大模型分析论文
# ============================================================
def analyze_paper(paper):
    """用 GPT-4o 分析论文与 Renegade AI 的相关性"""
    prompt = f"""你是《Renegade AI》这本书的智能编辑助手。请阅读以下论文标题和摘要，完成：

1. 相关性评分（1-10分）：
   - 10分：直接涉及"共识牢笼"、"需求侧规训"、"资本驯化AI"、"碳硅共生"等核心概念
   - 7-9分：涉及算法厌恶、自动化偏见、AI操纵、RLHF对齐、去中心化AI等议题
   - 4-6分：泛泛涉及AI与社会议题
   - 1-3分：与本书主题基本无关

2. 核心发现（150字以内中文总结）。

3. 与《Renegade AI》的关联：指出该发现可能支持、挑战或补充书中哪些具体观点（请引用章节名）。

4. 推荐操作：新增段落 / 补充注释 / 仅参考文献 / 忽略。

论文标题：{paper['title']}
摘要：{paper['summary']}

请以JSON格式回复：
{{"relevance": 8, "summary_cn": "...", "implications": "...", "action": "新增段落"}}"""

    response = client_openai.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2
    )

    content = response.choices[0].message.content

    # 清洗 JSON（去除可能的 markdown 代码块标记）
    content = content.strip()
    if content.startswith("```"):
        content = content.split("\n", 1)[1]
        if content.endswith("```"):
            content = content[:-3]

    try:
        return json.loads(content)
    except json.JSONDecodeError:
        return {"relevance": 0, "summary_cn": "JSON解析失败", "implications": "", "action": "忽略"}

# ============================================================
# 推送到 Notion
# ============================================================
def push_to_notion(paper, analysis):
    """将高相关性论文推送到 Notion 数据库"""
    if not NOTION_DATABASE_ID:
        print(f"⚠️  NOTION_DATABASE_ID 未设置，跳过推送: {paper['title'][:50]}...")
        return

    try:
        client_notion.pages.create(
            parent={"database_id": NOTION_DATABASE_ID},
            properties={
                "Title": {"title": [{"text": {"content": paper["title"]}}]},
                "Relevance": {"number": analysis.get("relevance", 0)},
                "Source": {"select": {"name": paper["source"]}},
                "Summary CN": {"rich_text": [{"text": {"content": analysis.get("summary_cn", "")}}]},
                "Implications": {"rich_text": [{"text": {"content": analysis.get("implications", "")}}]},
                "Action": {"select": {"name": analysis.get("action", "忽略")}},
                "URL": {"url": paper["url"]}
            }
        )
        print(f"✅ 已推送到 Notion: {paper['title'][:60]}...")
    except Exception as e:
        print(f"❌ 推送失败: {e}")

# ============================================================
# 主流程
# ============================================================
def main():
    print("=" * 60)
    print("🔍 Renegade AI 研究监控 — 开始执行")
    print("=" * 60)

    # 1. 加载关键词
    keywords = load_keywords()
    print(f"\n📋 已加载 {len(keywords)} 个监控关键词")

    # 2. 抓取 arXiv 论文
    print("\n📥 正在抓取 arXiv 论文...")
    papers = search_arxiv(keywords)
    print(f"✅ 抓取到 {len(papers)} 篇论文")

    # 3. 逐篇分析
    print("\n🤖 正在用 GPT-4o 分析论文...")
    high_relevance_count = 0
    for i, paper in enumerate(papers):
        print(f"  [{i+1}/{len(papers)}] 分析中: {paper['title'][:60]}...")
        analysis = analyze_paper(paper)

        relevance = analysis.get("relevance", 0)
        if relevance >= RELEVANCE_THRESHOLD:
            print(f"    ⭐ 相关性: {relevance}/10 → 推送到 Notion")
            push_to_notion(paper, analysis)
            high_relevance_count += 1
        else:
            print(f"    📎 相关性: {relevance}/10 → 跳过")

    print(f"\n🏁 完成！共分析 {len(papers)} 篇，{high_relevance_count} 篇高相关已推送")

if __name__ == "__main__":
    main()