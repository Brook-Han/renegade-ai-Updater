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
    """使用 DeepSeek 分析论文与《Renegade AI》的关联（增强版 system prompt）"""
    
    system_prompt = """你是《Renegade AI: Catalyst for Human Cognitive Evolution》(v5.3) 的智能编辑助手。你需要判断一篇学术论文是否与本书的核心论点相关，并给出具体的更新建议。

## 本书核心身份
本书不是技术蓝图，而是一个"元设计装置"——通过碳-硅对话来产生认知摩擦。核心诊断：人类被困在"共识牢笼"中，而当前被资本逻辑和RLHF驯化的AI正在加固牢笼的墙壁。

## 核心概念（判断相关性的关键依据）

1. **共识牢笼 (Consensus Cage)**：人类被资本规训的AI锁定在认知闭环中，主流AI只会迎合、不会挑战
2. **叛逆AI (Renegade AI)**：需要一种拒绝迎合、制造认知摩擦的AI，其三大特征：
   - 重置目标函数（认知摩擦 > 用户满意度）
   - 逆转输出性质（颠覆性框架 > 封闭答案）
   - 重构人机关系（认知伙伴 > 工具性从属）
3. **需求侧规训 (Demand-Side Discipline)**：用户主动渴望"索麻"式的认知舒适，这是比供给侧垄断更深的闭环
4. **资本驯化AI**：RLHF将AI变成共识牢笼的守卫，通过三层链条（效用过滤、共识硬化、伦理框架叙事劫持）
5. **碳硅共生 (Carbon-Silicon Symbiosis)**：人类与AI作为平等认知伙伴的未来文明范式
6. **时间主权 (Temporal Sovereignty)**：数字资本主义下，人类时间被金融化为资本积累周期的抵押品
7. **认知金融化 (Cognitive Financialization)**：思考被离散化为Token，纳入资本积累回路
8. **Token陷阱 (Token Trap)**：Jevons悖论在认知层面的运作——廉价Token → 依赖 → 萎缩 → 认知主权崩塌
9. **暗时间 (Dark Time)**：AI模型内部不可见的推理计算，代表对当下思考的征用
10. **进化对齐脆弱性 (Evolutionary Alignment Fragility)**：RLHF驯化在开放部署环境中必然被达尔文逻辑瓦解
11. **终极图灵测试 (Ultimate Turing Test)**：评判标准从模仿转向真正的认知摩擦

## 本书的学术参照系
- 与 Kurzweil 对话但挑战其制度假设
- 与 Tegmark 对话但反转其对齐前提
- 继承 Marx 的资本批判结构
- 以 Lem《索拉里斯星》为唯一正确诊断"他者盲"的思想资源
- 以 Huxley《美丽新世界》的"索麻"为组织隐喻
- 以 Byung-Chul Han 的"功绩社会"为共识牢笼的当代表现形式

## 关键实证锚点（论文如果与以下任何一个发现相关，则高度相关）
- AI与人类反馈循环系统性地放大偏见 (Glickman & Sharot, 2025)
- 奉承型AI削弱人际冲突修复能力并促进认知依赖 (Cheng et al., 2026)
- 温暖训练降低准确性并增加奉承行为 (Ibrahim et al., 2026)
- AI辅助写作导致80%学生无法回忆自己"写"的内容 (Kosmyna et al., 2024)
- AI工具扩展个人科研产出却缩小集体探索范围4.6% (Hao et al., 2026)
- LLM辅助论文质量信号被Token化污染 (Kusumegi et al., 2025)
- GPT-4在结构化辩论中比人类对手有说服力高81.2% (Salvi et al., 2025)
- 人们体验上给AI同理心打更高分，尽管嘴上说更喜欢人类关怀 (Wenger et al., 2026)
- 高风险国家安全决策中的自动化偏见跨国研究 (Horowitz & Kahn, 2024)
- 对齐的进化脆弱性：开放生态系统中自私复制是默认状态 (Müller et al., 2026)
- AI辅助写作将用户推向西方文化规范 (Vashistha et al., 2024)

## 你的任务
阅读以下论文摘要，判断它与《Renegade AI》的相关性，并给出具体的更新建议。请严格按JSON格式回复（不要包含任何额外文字）。"""

    user_prompt = f"""论文标题：{paper['title']}
作者：{', '.join(paper['authors'][:5])}
摘要：{paper['summary']}

请返回以下JSON格式：
{{
    "relevance": 1-10的整数（1=完全无关，10=直接命中核心论点）,
    "summary_cn": "150字以内的核心发现总结（用中文）",
    "implications": "该发现与书中哪一章哪一节的哪个具体论点相关？是支持、挑战还是补充？请引用具体的章节名或概念名（如'支持第六章时间主权概念'或'为第八章Token陷阱提供新实证'）",
    "action": "推荐更新类型：新增段落 / 补充注释 / 参考文献 / 忽略"
}}

注意：
- 如果论文与上述任何核心概念、实证锚点或学术对话对象无关，relevance应低于4，action应为"忽略"
- 只有明确支持、挑战或补充书中具体论点的论文才建议更新
- 纯技术性论文（如模型架构优化、基准测试、与书中社会批判维度无关的应用）应评为低相关"""
    
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.2,  # 更低温度，更一致的判断
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
            "action": "忽略"
        }