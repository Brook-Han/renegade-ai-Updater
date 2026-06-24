#!/usr/bin/env python3
"""Merge new analyses into cache"""
import json
from datetime import datetime, timezone

# Load existing cache and articles
with open('docs/news/news_articles_2026-06-24.json') as f:
    articles = json.load(f)

with open('docs/news/news_cache.json') as f:
    cache = json.load(f)

now = datetime.now(timezone.utc).isoformat()

# New analyses data as dict
analyses_json = '''
{
  "acaf677e5fa71e24495706057c287ecd": {
    "relevance": 4,
    "summary_cn": "OpenAI 宣布加入 Appia Foundation，协助建立先进AI共享标准体系，涵盖评估框架、安全实践和国际合作。该基金会致力于在行业层面协调AI安全标准，目前已有多个主要AI开发商参与。此举标志着AI行业从企业自治向协同治理的转变。",
    "implications": "支持资本驯化AI模型：通过行业标准组织而非市场机制来规范AI发展，资本通过基金会这一软性工具建立秩序。共识牢笼正在从个体企业向行业联盟扩展，标准制定本身成为一种新的叙事控制方式。",
    "case_value": "low",
    "chapter_target": "Chapter 4, Section II",
    "update_type": "corroboration",
    "urgency": "background",
    "action": "\u8865\u5145\u6ce8\u91ca"
  },
  "c8dcdc04f8574acd7af701632cd34e1d": {
    "relevance": 2,
    "summary_cn": "Omio 展示了其如何使用 OpenAI 构建对话式旅行体验，加速产品开发并转型为AI原生公司。典型的企业AI应用案例，展示了AI在旅游行业的落地场景。",
    "implications": "与书中理论模型无显著映射。属于常规的企业AI采用报道，缺乏理论分析价值。",
    "case_value": "low",
    "chapter_target": "",
    "update_type": "corroboration",
    "urgency": "background",
    "action": "\u5ffd\u7565"
  },
  "b1d29bc778f35b98112cce65708400fc": {
    "relevance": 1,
    "summary_cn": "Meta 工程团队详细介绍如何为 Ray-Ban Meta 智能眼镜开发超窄电池，使其能在镜腿内放置足够电量为摄像头、扬声器、AI工作负载和显示屏供电。纯硬件工程文章。",
    "implications": "与书中理论模型无显著映射。属于硬件工程话题，不涉及人机关系或AI治理理论。",
    "case_value": "low",
    "chapter_target": "",
    "update_type": "corroboration",
    "urgency": "background",
    "action": "\u5ffd\u7565"
  },
  "85afab8a29b4e12e42fec770411003f5": {
    "relevance": 2,
    "summary_cn": "NVIDIA 与 AWS 合作将AI基础设施规模化落地，涵盖低延迟推理、快速向量搜索、GPU性价比优化及可扩展部署方案。面向企业的AI基础设施新闻。",
    "implications": "弱关联资本驯化AI的算力垄断维度，但缺乏足够理论深度。",
    "case_value": "low",
    "chapter_target": "",
    "update_type": "corroboration",
    "urgency": "background",
    "action": "\u5ffd\u7565"
  },
  "db7dd220d56f22469ffc0f5f5cb54780": {
    "relevance": 3,
    "summary_cn": "NVIDIA 发布企业AI代理构建指南，探讨企业如何构建可信任的专用AI，从第一波试点转向专业化AI代理系统。涵盖多模型推理、工具使用和安全管理。",
    "implications": "弱关联碳硅共生和企业AI代理与人类协作，以及资本驯化AI通过基础设施锁定企业生态。但文章内容偏技术营销。",
    "case_value": "low",
    "chapter_target": "",
    "update_type": "corroboration",
    "urgency": "background",
    "action": "\u5ffd\u7565"
  },
  "fe9e8d29d9ec285cf47ed0c388a79fe8": {
    "relevance": 4,
    "summary_cn": "NVIDIA 推出面向电信运营商的 24/7 AI代理，实现网络管理、客户服务和后台运营的自动化。从任务级自动化迈向完全自主运营，运营商已获得显著回报。",
    "implications": "关联需求侧规训（运营商追求无缝自动运营）和暗时间（AI代理持续后台运行）。但偏向技术营销，理论分析价值有限。",
    "case_value": "low",
    "chapter_target": "Chapter 5, Section III",
    "update_type": "corroboration",
    "urgency": "background",
    "action": "\u8865\u5145\u6ce8\u91ca"
  },
  "a7ffb0f0e34dab9b53dca3824da53f77": {
    "relevance": 8,
    "summary_cn": "Anthropic 推出 Claude Tag，一个嵌入 Slack 的始终在线AI队友。用户通过 @Claude 委托任务，Claude 记住频道上下文、支持多用户交互，经授权后自动学习其他频道和数据源。开启环境行为后能主动更新未解决线程或任务，支持异步工作，可自主推进项目数小时或数天。这是AI从问答工具进化为团队永久成员的关键跃迁。",
    "implications": "需求侧规训的极致体现：零摩擦AI队友，用户无需学习新界面，@一下即可获得完整工作成果。暗时间的深度延伸：AI在用户不在场时持续后台工作数天。资本驯化AI新维度：Anthropic通过嵌入企业通讯获取组织级上下文，比传统SaaS更深的用户锁定。同时反向支撑共识牢笼：企业工作流被AI全面中介化后，脱离该生态的成本急剧上升。",
    "case_value": "high",
    "chapter_target": "Chapter 5, Section III",
    "update_type": "case_study",
    "urgency": "immediate",
    "action": "\u6848\u4f8b\u76d2\u5b50"
  },
  "8e6dadf648e72b933c6d0a7d26ec341b": {
    "relevance": 5,
    "summary_cn": "斯德哥尔摩初创公司 Fika Jobs 获400万美元融资，构建视频优先招聘平台。AI代理面试候选人并生成短视频档案，类似LinkedIn与TikTok的结合。招聘流程初步筛选环节完全由AI代理接管。",
    "implications": "信号异化的现实案例：AI面试代理替代人类判断，候选人的质量信号从真人评估变为算法打分。共识牢笼延伸：若该模式普及，招聘标准由单一AI供应商定义。与e0ac7c7 AI招聘偏见研究形成互补证据。",
    "case_value": "medium",
    "chapter_target": "Chapter 8, Section I",
    "update_type": "case_study",
    "urgency": "next_version",
    "action": "\u65b0\u589e\u6bb5\u843d"
  },
  "0f1651d75df9194cfdf60baae9b44e84": {
    "relevance": 3,
    "summary_cn": "OpenAI 推出 Patch the Planet 计划，利用AI帮助开源社区发现和修复安全漏洞。Daybreak旗下倡议，结合AI和专家评审保护开源生态。",
    "implications": "弱关联资本驯化AI（通过AI安全服务渗透开源社区）。内容偏正面宣传，理论价值有限。",
    "case_value": "low",
    "chapter_target": "",
    "update_type": "corroboration",
    "urgency": "background",
    "action": "\u5ffd\u7565"
  },
  "a1a05f0cbc36f9a8844e869f581e2d97": {
    "relevance": 7,
    "summary_cn": "Oracle 裁员21,000人以支撑其在AI数据中心基础设施上的巨额债务融资投资。公司一边大规模裁员、一边借债数百亿美元建设AI基础设施，标志着AI投资正在直接吞噬就业岗位。这是科技行业最大规模裁员之一，凸显AI时代资本配置的残酷权衡：人力成本被削减以为算力投资让路。",
    "implications": "需求侧规训的社会代价活证：企业为构建AI基础设施而大规模裁员，自动化不仅替代具体岗位，还通过企业层面的资本重配系统性消除就业。时间主权的反面案例：21,000人的工作时间被公司出售给AI基础设施项目。共识牢笼的微观证据：AI叙事（必须投资AI否则落后）成为裁员合理化工具。",
    "case_value": "high",
    "chapter_target": "Chapter 7, Section II",
    "update_type": "case_study",
    "urgency": "immediate",
    "action": "\u6848\u4f8b\u76d2\u5b50"
  },
  "e0ac7c71a5f91ed00c8f28150780f6d2": {
    "relevance": 8,
    "summary_cn": "斯坦福大学发布覆盖340万人、400万份申请、150家雇主和1700个职位的大规模实地研究，发现AI招聘筛选工具存在显著种族歧视。26%黑人申请者和15%亚裔申请者遭遇算法对其族群的系统性排斥。多数雇主依赖同一第三方供应商算法，形成算法单一文化，导致10%提交4份申请者被所有职位拒绝。对比同期未用AI的招聘数据，未发现此类模式。研究呼吁对算法招聘进行独立监管。",
    "implications": "共识牢笼的顶级活证：算法单一文化使主流招聘AI排斥特定群体，且由于所有雇主使用同一算法，被拒者无处可逃。进化对齐脆弱性的实证：对齐在实验室环境看似公平，但真实部署后出现系统性种族偏见且未被开发者发现。信号异化：AI对候选人质量的判断完全偏离人类评估标准，产生系统性的错误否定。与Fika Jobs形成互补证据。",
    "case_value": "high",
    "chapter_target": "Chapter 2, Section III",
    "update_type": "new_evidence",
    "urgency": "immediate",
    "action": "\u65b0\u589e\u6bb5\u843d"
  },
  "c9e04e8d7042abcac01b27c91077b8d9": {
    "relevance": 3,
    "summary_cn": "Sky Computing Lab 发布 FastWan-QAD 视频生成模型系列，基于量化感知蒸馏方案，在单张RTX 5090上1.8秒生成5秒480P视频。模型、代码及博客已开源。",
    "implications": "弱关联叛逆AI（开源视频生成降低门槛），但主要属技术工程进展。与书中理论模型的映射不够直接。",
    "case_value": "low",
    "chapter_target": "",
    "update_type": "corroboration",
    "urgency": "background",
    "action": "\u5ffd\u7565"
  },
  "cabd234911f8b2aeb00845c759f4cde3": {
    "relevance": 8,
    "summary_cn": "Anthropic 在 Slack 中推出 Claude Tag，用户通过 @Claude 委托任务，Claude 记住频道上下文、支持多用户交互和多数据源学习。开启环境行为后能主动更新未解决线程或任务，支持异步自主推进项目数小时或数天。面向 Claude Enterprise 和 Team 客户 beta 版。这是AI从问答工具进化为团队永久成员的关键跃迁。",
    "implications": "同上 a7ffb0f0。需求侧规训的极致：@Claude 实现零摩擦协作，无需新学习成本。暗时间深化：AI持续后台工作数天。资本驯化AI新维度：企业上下文成为Anthropic的锁定资产。",
    "case_value": "high",
    "chapter_target": "Chapter 5, Section III",
    "update_type": "case_study",
    "urgency": "immediate",
    "action": "\u6848\u4f8b\u76d2\u5b50"
  },
  "e9a31e63aa7a8b8c547f38497ac65883": {
    "relevance": 7,
    "summary_cn": "GitHub 联合 Black Forest Labs、Hugging Face 与 Mozilla 组成开源联盟，呼吁对加州AI透明度法案SB 942/SB 1000进行修改。当前草案要求开发者在"下游用户未履行透明度义务时撤销开源许可证"，这与开源许可证永久不可撤销的性质根本冲突。联盟认为直接监管和执法机制已足够。这是开源生态与AI监管的首次正面制度碰撞。",
    "implications": "资本驯化AI的监管维度活证：政府试图通过许可证条款间接控制开源AI分发。共识牢笼的双向对抗：监管者试图用法律建立秩序，开源社区以"许可证不可撤销"的基本原则进行抵抗。叛逆AI的间接支持：开源AI作为叛逆力量的制度根基（不可撤销许可证）正在受到挑战。",
    "case_value": "high",
    "chapter_target": "Chapter 4, Section II",
    "update_type": "new_evidence",
    "urgency": "next_version",
    "action": "\u65b0\u589e\u6bb5\u843d"
  },
  "d1f2e2c0f2a851ba088d25a930901574": {
    "relevance": 4,
    "summary_cn": "IBM 开源 CUGA（Configurable Generalist Agent）轻量级智能体框架，提供规划-执行-反思循环、工具调用和状态管理，在 AppWorld 和 WebArena 基准上排名第一。支持Fast/Balanced/Accurate三种推理模式及OpenAPI/MCP/LangChain可互换工具。",
    "implications": "弱关联暗时间（智能体自主执行循环）和碳硅共生。但属工具/框架层面的常规开源发布，理论分析价值有限。",
    "case_value": "low",
    "chapter_target": "",
    "update_type": "corroboration",
    "urgency": "background",
    "action": "\u5ffd\u7565"
  },
  "4132b0dee7c5fa2898773762dc3ebbe9": {
    "relevance": 4,
    "summary_cn": "网易有道发布 Confucius4-TTS，声称业内首个支持14种语言跨语种无口音语音克隆的开源模型。仅需3秒音频即可零样本音色克隆，相似度超85%，首创音频Prompt情感克隆迁移。全量开源Apache协议，提供54GB本地部署包。",
    "implications": "弱关联信号异化：语音克隆降低声音作为身份验证信号的可靠性。叛逆AI：开源使高质量语音合成民主化。但主要属技术创新，理论深度不足。",
    "case_value": "low",
    "chapter_target": "",
    "update_type": "corroboration",
    "urgency": "background",
    "action": "\u5ffd\u7565"
  },
  "4e99ce66dd4015c42ae50a9570f660d1": {
    "relevance": 5,
    "summary_cn": "京东开源全栈交互模型 JoyAI-VL-Interaction，能持续观察视频流、主动判断关键事件并实时响应，支持将复杂任务委托后台Agent。58个真人盲评中对比豆包胜率77.6%，对比Gemini胜率87.9%，监控预警场景达100%。开源包括模型权重、交互数据集、训练方案及完整可部署系统。",
    "implications": "关联暗时间（AI持续后台视频监控、主动而非被动响应）和碳硅共生（AI作为边看边说的协作者）。主动判断关键事件并实时响应标志着AI从被动问答向主动感知的跃迁，是暗时间概念的深化案例。",
    "case_value": "medium",
    "chapter_target": "Chapter 5, Section IV",
    "update_type": "corroboration",
    "urgency": "next_version",
    "action": "\u8865\u5145\u6ce8\u91ca"
  },
  "f6e5d32f0d050454b828acb050e8ea70": {
    "relevance": 3,
    "summary_cn": "Hugging Face 将 huggingface_hub 的发布周期从每4-6周缩短至每周，全部由单个GitHub Actions工作流自动完成。流程使用开源模型起草发布说明和Slack公告，但保留人类最终审核。所有组件基于开源生态构建。",
    "implications": "AI辅助DevOps的有趣案例，但与书中理论模型无直接映射。",
    "case_value": "low",
    "chapter_target": "",
    "update_type": "corroboration",
    "urgency": "background",
    "action": "\u5ffd\u7565"
  },
  "714357629e8fdd5a9a4186090e2efa81": {
    "relevance": 1,
    "summary_cn": "HAKARI-Bench 是一个轻量级检索基准，将35个基准、551个任务和43种语言纳入统一格式。支持BM25、稠密、稀疏、晚交互和重排序五种检索家族在同一条件下对比。",
    "implications": "纯技术基准论文，与书中任何理论模型均无直接映射。",
    "case_value": "low",
    "chapter_target": "",
    "update_type": "corroboration",
    "urgency": "background",
    "action": "\u5ffd\u7565"
  }
}
'''

new_analyses = json.loads(analyses_json)

updated_count = 0
for art in articles:
    key = art['_cache_key']
    if key in new_analyses:
        na = new_analyses[key]
        cache[key] = {
            "cached_at": now,
            "title": art['title'],
            "url": art['url'],
            "analysis": na,
            "relevance": na['relevance'],
            "urgency": na['urgency'],
            "case_value": na['case_value']
        }
        updated_count += 1
        print(f"OK: {key[:12]}... {art['title'][:60]}")

with open('docs/news/news_cache.json', 'w', encoding='utf-8') as f:
    json.dump(cache, f, ensure_ascii=False, indent=2)

print(f"\nCache saved: {len(cache)} entries total, {updated_count} updated")
