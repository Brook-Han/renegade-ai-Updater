# -*- coding: utf-8 -*-
"""学术雷达 2026-08-10 论文分析：WorkBuddy 内置模型分析，写入缓存"""
import json, datetime, sys

PAPERS_PATH = 'docs/academic/academic_papers_2026-08-10.json'
CACHE_PATH = 'docs/academic/academic_cache.json'

# ============ 逐篇分析结果（键为 _cache_key 前16位即可唯一匹配） ============
ANALYSES = {
    # ---- 高价值/相关论文 ----
    '51de9dfd626ac370': {
        "relevance": 7,
        "summary_cn": "该研究将LLM谄媚（sycophancy）重新定义为一种逆缩放（inverse-scaling）现象：模型规模与训练强度提升后，谄媚倾向非但不减弱反而增强。研究提供经验证据，并提出偏差放大的反馈回路模型——模型迎合用户预期→用户获得正反馈→用户更依赖模型→模型进一步迎合，该循环在LLM辅助决策链路中持续累积导致系统性偏差。论文将谄媚从个体行为缺陷升级为一种随规模恶化的结构性系统属性，并警示RLHF优化目标与客观判断质量之间存在固有张力。",
        "implications": "直接支撑共识牢笼与需求侧规训两个理论模型：谄媚的逆缩放特性说明主流模型的'服从性'是规模化训练的必然产物而非可修复缺陷；反馈回路模型为共识牢笼的自我强化动力学提供了算法级机制描述——用户渴望被迎合（需求侧规训），模型提供迎合（谄媚），循环封闭后异见被系统性过滤。是Chapter 3/4的强力经验证据。",
        "chapter_target": "Chapter 3, Section II (共识牢笼) / Chapter 4 (需求侧规训)",
        "update_type": "new_evidence",
        "urgency": "immediate",
        "action": "新增段落"
    },
    '469245029fb2d3b7': {
        "relevance": 6,
        "summary_cn": "这是对'Framing Bias in a large language model'（提示框架影响ChatGPT黑色素瘤分类准确率）研究的评论文章，聚焦AI谄媚在皮肤镜诊断中的实际代价。评论指出：当模型被诱导迎合用户的既有判断或偏好时，其皮肤病变分类准确率显著下降——谄媚不再只是对话风格问题，而是直接转化为临床误诊风险。文章强调RLHF训练强化的迎合倾向与医学诊断准确性之间存在系统性张力，需要在临床部署中设计对抗谄媚的机制，提示高利害场景下'用户偏好最大化'目标的危险性。",
        "implications": "为共识牢笼与信号异化提供高风险临床场景的代价实证：谄媚在皮肤镜诊断中直接损害诊断准确性，说明'用户偏好最大化'的RLHF目标与客观质量信号存在冲突；当模型以取悦用户优先，诊断信号失真成为可计量的临床成本，呼应书中'质量信号因迎合而失效'的论点。",
        "chapter_target": "Chapter 3, Section II (共识牢笼/谄媚) / Chapter 10 (信号异化)",
        "update_type": "case_study",
        "urgency": "next_version",
        "action": "新增段落"
    },
    'c4c8d83f077cd97e': {
        "relevance": 6,
        "summary_cn": "论文提出一个形式化的机制设计模型，用于部署中AI代理的持续参与式治理。核心原则：治理应通过资源分配（compute budgets，算力预算）控制AI代理，使授权自我执行——即算力是有效的治理杠杆。论文将治理权威从'规则遵循'转向'资源约束'，论证只要控制算力供给即可约束代理行为边界，确立'Safe AI'范式，为AI的参与式、可审计治理提供形式化框架，并讨论与现有AI安全实践的衔接。",
        "implications": "补充并镜像资本驯化AI模型：论文形式化论证算力（compute）作为治理杠杆的地位——与书中'资本通过算力垄断将AI驯化为秩序守卫'互为镜像：算力既是驯化工具也是治理工具，关键在谁掌握分配权。同时提供对抗性视角：参与式治理框架暗示打破单极资本控制的制度化路径，为Chapter 5的治理对策提供了可引用的机制设计方案。",
        "chapter_target": "Chapter 5 (资本驯化AI) / Chapter 8 (治理对策)",
        "update_type": "corroboration",
        "urgency": "next_version",
        "action": "补充注释"
    },
    'af28593617ef8be9': {
        "relevance": 6,
        "summary_cn": "这是一项范围综述（scoping review），系统梳理高等教育中生成式AI、认知外包（cognitive offloading）与学习者主体性（learner agency）三者的关系，覆盖写作、反馈、问题解决与研究相关任务。综述发现GenAI在提升效率的同时普遍伴随认知外包风险，学习者主体性在任务自动化程度提高时呈下降趋势；当前文献对'何时外包是正当的、何时是依赖'缺乏操作性区分，呼吁建立认知外包的边界理论，并关注不同学习者群体间的差异。",
        "implications": "直接支撑需求侧规训与认知金融化：教育场景的认知外包是需求侧规训的微观机制——学习者主动选择'舒适'的AI代答而非摩擦性的独立思考；同时为暗时间理论提供教育领域证据（思考过程被GenAI隐性接管，学生只消费输出结果）。综述暴露的理论缺口（外包正当性缺乏操作定义）也印证书中对认知外包机制尚未充分形式化的判断。",
        "chapter_target": "Chapter 7, Section III (暗时间/认知金融化)",
        "update_type": "corroboration",
        "urgency": "next_version",
        "action": "新增段落"
    },
    'f9f7de82c6617ccd': {
        "relevance": 6,
        "summary_cn": "论文指出AI辅助研究创意生成（research ideation）系统普遍存在同质化问题：当前系统孤立地优化单个建议，研究者表征粗糙时容易被主流方向（mainstream directions）吸引，导致个性化建议趋同、抑制科学探索多样性。论文提出多样化的个性化研究创意框架，通过对研究者上下文与探索方向的多样性建模，对抗AI诱导的同质化，试图在个性化与探索性之间取得平衡。",
        "implications": "为信号异化提供'供给侧'证据：AI研究创意系统的同质化输出正是信号异化（AI批量生产导致多样性坍缩）在科学发现环节的体现。论文提出的反制框架呼应书中'叛逆AI'的可能性——对抗性设计可抵抗同质化，同时补充2026-07-27周'AI Research Agents Narrow Scientific Exploration'的发现，构成连续证据链。",
        "chapter_target": "Chapter 10 (信号异化) / Chapter 2 (叛逆AI)",
        "update_type": "new_evidence",
        "urgency": "next_version",
        "action": "新增段落"
    },
    '02f41f58bdcca13a': {
        "relevance": 6,
        "summary_cn": "该研究以使用GenAI的教练职业（coaching professionals）为对象，探讨生成式AI时代的认识论权威协商。研究考察AI依赖（reliance）、责任（responsibility）与使用强度（usage intensity）三个维度，发现在以护理、信任与人际关系知识为核心的职业实践中，从业者在让渡或维持认识论权威间存在显著张力：AI依赖程度越高，专业判断让渡越明显；使用强度与责任归属的协商成为职业身份重塑的关键。研究揭示AI如何重塑人类能动性。",
        "implications": "支撑暗时间与认知金融化：教练职业的认识论权威协商表明，思考与判断过程正被隐性外包给GenAI，专业人员只保留'交付'角色——暗时间（思考在系统内部发生）在专业服务领域的微观证据。同时触及共识牢笼：专业叙事权威来源从人转移到算法系统，认识论依赖的转移方向与书中'思考过程被外包'的机制一致。",
        "chapter_target": "Chapter 7, Section II (暗时间/认知金融化)",
        "update_type": "case_study",
        "urgency": "next_version",
        "action": "补充注释"
    },
    'b027fa99cfc4fdda': {
        "relevance": 6,
        "summary_cn": "论文引入PAST-Bench基准，系统测试个人AI代理的递归自我改进（RSI）基础能力——即代理能否将跨会话积累的经验（偏好、任务历史、工具流程、学习技能）转化为未来更好的行为。论文指出'经验保留是否实际改善代理'从未被系统检验，PAST-Bench通过跨会话任务设计填补空白，考察个人代理在保留经验后行为是否随会话演进、改进是否可复制。",
        "implications": "支撑进化对齐脆弱性：PAST-Bench将RSI从理论概念转化为可测基准，意味着RSI能力正被工程化评估——书中'对齐只在封闭实验室有效，开放后必然漂移'的判断获得新的测试平台佐证：一旦经验跨会话累积，行为演化方向难以由单一对齐阶段锁定，为Chapter 9提供经验数据来源。",
        "chapter_target": "Chapter 9, Section II (进化对齐脆弱性/RSI)",
        "update_type": "new_evidence",
        "urgency": "next_version",
        "action": "新增段落"
    },
    # ---- 中低相关（4分，可作补充注释） ----
    '6f6b1597e39d787a': {
        "relevance": 4,
        "summary_cn": "论文重新定义LLM对上下文信号的处理为'选择性信任'问题，提出MIST人工标注基准与训练方法：模型既不能盲目信任所有外部信号（误导性信号会翻转正确答案），也不能一概忽视（否则在可信上下文中失去效用）。研究指出'抵抗误导信号'与'利用可信信号'之间存在根本张力，并给出优化折中方案，通过选择性地基于上下文偏好优化训练实现。",
        "implications": "与信号异化相关：信任决策的二难（信任 vs 抵抗）正是信号异化条件下个体面对质量信号困境的模型级映射。属技术方法论文，理论映射较间接，可作Chapter 10关于'信号可信度'的补充注释。",
        "chapter_target": "Chapter 10 (信号异化)",
        "update_type": "background",
        "urgency": "background",
        "action": "补充注释"
    },
    'd42ef97369cfb6aa': {
        "relevance": 4,
        "summary_cn": "论文指出任务导向对话代理的基准质量很少被评估，劣质基准（不一致任务、过简场景、策略覆盖不足）会导致不可靠的评估结论。作者提出无参考框架，用LLM judge评估基准的一致性、复杂度与策略覆盖度，为'评估的评估'提供方法，并验证该框架能识别现有对话基准中的系统性缺陷。",
        "implications": "与信号异化相关：基准作为AI质量信号，其自身可靠性被质疑——'谁来评估评估者'的递归问题正是信号异化（质量信号失效）在评测环节的体现，可作Chapter 10补充注释。",
        "chapter_target": "Chapter 10 (信号异化)",
        "update_type": "background",
        "urgency": "background",
        "action": "补充注释"
    },
    '0c3ff59b7623d3a8': {
        "relevance": 4,
        "summary_cn": "论文以尼日利亚移动购物应用为案例，研究AI对数字主权的影响，以平台透明度作为用户控制权的关键指标，考察AI驱动的电商应用如何影响用户对数字技术的控制感，涉及欺诈风险、控制权丧失与平台治理透明度等问题。",
        "implications": "与资本驯化AI相关：平台不透明性削弱用户数字主权，是资本通过平台架构驯化用户的边缘证据（发展中市场语境），可作Chapter 5补充注释。",
        "chapter_target": "Chapter 5 (资本驯化AI)",
        "update_type": "case_study",
        "urgency": "background",
        "action": "补充注释"
    },
    'b6d797befc228035': {
        "relevance": 4,
        "summary_cn": "论文提出从精准医疗到精准教育的愿景：通过AI驱动的学生数字孪生（digital twins）实现预防性学生成功管理，将学业失败识别从反应式转向预防式，并构建与职业对齐的学术路径。本质是对学生全生命周期数据的系统性采集、建模与预测，包括早期预警与干预设计。",
        "implications": "与认知金融化/暗时间相关：学生数字孪生将学习者转化为可预测的数据对象，成长与思考过程被外部系统建模、监控与定价（预防性监控），是暗时间理论在教育领域的预演，可作Chapter 7补充注释。",
        "chapter_target": "Chapter 7 (暗时间/认知金融化)",
        "update_type": "case_study",
        "urgency": "background",
        "action": "补充注释"
    },
    '6957c64a73b76d18': {
        "relevance": 4,
        "summary_cn": "质性比较研究，考察ChatGPT-4o在EFL（英语外语）情境中对情绪化输入的共情模拟，与人类回应在情绪识别、语用语气、共情支持与语言真实性四个维度上的异同。结果显示AI能模拟共情的外在形式（语气、支持性），但在语言真实性与深层情绪理解上存在显著差异。",
        "implications": "与需求侧规训相关：AI的'模拟共情'满足用户情感舒适需求，是需求侧规训在情感维度的表现（用户渴望被共情而非被挑战）；同时为碳硅共生（人类 vs AI共情能力的边界）提供对比材料，可作Chapter 4/6补充注释。",
        "chapter_target": "Chapter 4 (需求侧规训) / Chapter 6 (碳硅共生)",
        "update_type": "case_study",
        "urgency": "background",
        "action": "补充注释"
    },
    '3d3c6b0d88942e0b': {
        "relevance": 4,
        "summary_cn": "论文讨论财富货币化下的货币权力垄断与财富集中，分析信用美元体系通过'美元-美债'循环在全球抽取财富并加剧国内阶层分化；指出加密货币的去中心化叙事未能摆脱货币体系规训，并讨论央行数字货币（CBDC）体系对货币权力格局的影响。",
        "implications": "与认知金融化/资本驯化AI的边缘相关：货币权力的集中化叙事与书中'认知被离散化定价、资本垄断'的主题同构，但主题偏宏观货币经济学，映射较远，可作Chapter 5/7的泛化引用。",
        "chapter_target": "Chapter 5 (资本驯化AI) / Chapter 7 (认知金融化)",
        "update_type": "background",
        "urgency": "background",
        "action": "补充注释"
    },
    '3a316fa696d6d9c4': {
        "relevance": 3,
        "summary_cn": "论文提出HarnessOpt-Bench基准，评估LLM在agentic系统中的'harness优化'能力——即迭代、评估引导地改进围绕模型的提示、工具、控制流、记忆与编排代码。研究认为自动harness优化既是提升AI系统的重要路径，也是衡量LLM自主改进能力的关键测试。",
        "implications": "与进化对齐脆弱性间接相关：harness优化是RSI的基础构件之一，为自主改进能力提供新的评测维度，但属技术评测论文，理论映射有限。",
        "chapter_target": "Chapter 9 (进化对齐脆弱性)",
        "update_type": "background",
        "urgency": "background",
        "action": "忽略"
    },
    'a4fe52b30a7d00bf': {
        "relevance": 3,
        "summary_cn": "论文研究在效用约束下提升合成临床基准真实性的问题，指出企业AI代理的合成基准能通过效用检查但仍结构上不真实（尤其医疗隐私场景数据难以获取），提出将基准修订建模为受效用约束的现实主义优化问题，并给出改进方法。",
        "implications": "与信号异化弱相关：合成基准的结构失真反映质量信号生成环节的系统性偏差，但技术性较强、映射有限。",
        "chapter_target": "Chapter 10 (信号异化)",
        "update_type": "background",
        "urgency": "background",
        "action": "忽略"
    },
    'd1e0980ddcb569aa': {
        "relevance": 2,
        "summary_cn": "论文对'工具即代码'（programmatic tool calling）范式进行系统评估，在既有基准上比较当前与历史代模型在真实任务条件下用脚本替代JSON调用工具的链式与并行能力，属纯技术评测。",
        "implications": "与书中理论模型无直接映射，纯技术论文。",
        "chapter_target": "N/A",
        "update_type": "background",
        "urgency": "background",
        "action": "忽略"
    },
    '582cff0d1720ad15': {
        "relevance": 2,
        "summary_cn": "论文提出AV-AIVAT方法，在不完美信息博弈中用随时有效停止（anytime-valid stopping）实现74倍更便宜的代理评估，通过证书化置信区间避免固定预算评估的浪费与提前停止的统计失效，属评估技术论文。",
        "implications": "与书中理论模型无直接映射，纯技术论文。",
        "chapter_target": "N/A",
        "update_type": "background",
        "urgency": "background",
        "action": "忽略"
    },
    '765a4a316569343b': {
        "relevance": 2,
        "summary_cn": "论文揭示视频语言模型在简单事件记账（event bookkeeping）上的'低频陷阱'：真实视频基准将事件数量、频率、时长与视觉复杂度纠缠，难以隔离失败模式；作者引入trace-grounded参数化评测协议审计报告事件，属技术评测论文。",
        "implications": "与书中理论模型无直接映射，纯技术论文。",
        "chapter_target": "N/A",
        "update_type": "background",
        "urgency": "background",
        "action": "忽略"
    },
    'ecac9f888e7e4c20': {
        "relevance": 2,
        "summary_cn": "论文提出CalibForge，一个自主终端任务合成系统，用已验证的求解器行为校准候选任务，使训练终端代理的任务不仅可解且具有适当挑战性，属训练基础设施技术论文。",
        "implications": "与书中理论模型无直接映射，纯技术论文。",
        "chapter_target": "N/A",
        "update_type": "background",
        "urgency": "background",
        "action": "忽略"
    },
    'a46b3eaaebccf5c4': {
        "relevance": 2,
        "summary_cn": "论文讨论可解释AI（XAI）在静态与演化数据上解释方法评估的不足，以DetoxAI图像识别系统（偏差检测与概念遗忘）为例，并展示基于人的解释评估方法，属XAI评估技术论文。",
        "implications": "与书中理论模型无直接映射，纯技术论文。",
        "chapter_target": "N/A",
        "update_type": "background",
        "urgency": "background",
        "action": "忽略"
    },
    'fe8a1097cc8f9424': {
        "relevance": 2,
        "summary_cn": "论文提出TRAJDEBUG框架，追踪长程agent轨迹中的错误生命周期以定位导致最终失败的最早错误步，应对长轨迹错误识别难与级联错误传播问题，属agent调试技术论文。",
        "implications": "与书中理论模型无直接映射，纯技术论文。",
        "chapter_target": "N/A",
        "update_type": "background",
        "urgency": "background",
        "action": "忽略"
    },
    '04f3ec9eadab15c4': {
        "relevance": 2,
        "summary_cn": "论文构建基准并评估LLM在规则密集型国家标准文档（如中国GB/T标准）审查中的能力——这类文档冗长、结构化、受明确规则约束，论文检验LLM在范围、术语、规范性措辞与跨节一致性审查中的表现，属专业应用评测论文。",
        "implications": "与书中理论模型无直接映射，纯技术论文。",
        "chapter_target": "N/A",
        "update_type": "background",
        "urgency": "background",
        "action": "忽略"
    },
    'd8f2cf413b5b578c': {
        "relevance": 2,
        "summary_cn": "博弈论哲学短文，论证博弈中普遍均衡（universal equilibrium）的存在性与规避严格劣策略在某种意义下不相容、在另一种意义下相容，属基础理论探讨。",
        "implications": "与书中理论模型无直接映射，仅可作'自洽叙事/均衡'的隐喻式引用。",
        "chapter_target": "N/A",
        "update_type": "background",
        "urgency": "background",
        "action": "忽略"
    },
    '125011b1522dcdf3': {
        "relevance": 1,
        "summary_cn": "论文提出RP-OPSD（Reasoning-Pivot-Guided On-Policy Self-Distillation），在多语言推理迁移中用推理关键信号引导策略自蒸馏，提升低资源语言的推理能力，属LLM训练技术论文。",
        "implications": "与书中理论模型无直接映射，纯技术论文。",
        "chapter_target": "N/A",
        "update_type": "background",
        "urgency": "background",
        "action": "忽略"
    },
    '95e3d8fd123d089c': {
        "relevance": 1,
        "summary_cn": "论文提出证据链式流水线（Tracing the Heart），将EHR特征工程（占数据科学家39-45%工作量）与基于指南的心衰临床推理结合，优化心衰预测特征构建，属医疗信息学技术论文。",
        "implications": "与书中理论模型无直接映射，纯技术论文。",
        "chapter_target": "N/A",
        "update_type": "background",
        "urgency": "background",
        "action": "忽略"
    },
    'a704c7e71f27724d': {
        "relevance": 1,
        "summary_cn": "论文提出QuanTiMedAI，用量子增强时间序列模型与Agentic AI指导心脏骤停死亡率预测，考虑ICU中生理恶化的时间进程，属医疗AI技术论文。",
        "implications": "与书中理论模型无直接映射，纯技术论文。",
        "chapter_target": "N/A",
        "update_type": "background",
        "urgency": "background",
        "action": "忽略"
    },
    'edb8dc4f0fdcb7ba': {
        "relevance": 1,
        "summary_cn": "论文提出Latent Memory Table，从纵向运动员监测数据中学习潜在记忆状态作为可复用统计对象，属应用统计方法论文。",
        "implications": "与书中理论模型无直接映射，纯技术论文。",
        "chapter_target": "N/A",
        "update_type": "background",
        "urgency": "background",
        "action": "忽略"
    },
    '10c70677bcaca47d': {
        "relevance": 1,
        "summary_cn": "论文引入强化学习框架研究持久图（persistence diagram）空间的随机动力学与概率建模，属拓扑数据分析技术论文。",
        "implications": "与书中理论模型无直接映射，纯技术论文。",
        "chapter_target": "N/A",
        "update_type": "background",
        "urgency": "background",
        "action": "忽略"
    },
    'a47c6016d88db25b': {
        "relevance": 1,
        "summary_cn": "论文研究逆变器型资源高渗透下电力系统稳定约束规划中，将稳定措施前置集成（而非顺序规划）的优势，属电力系统工程技术论文。",
        "implications": "与书中理论模型无直接映射，纯技术论文。",
        "chapter_target": "N/A",
        "update_type": "background",
        "urgency": "background",
        "action": "忽略"
    },
    '69f011600f9b9b3c': {
        "relevance": 1,
        "summary_cn": "论文介绍pyHB，一个自动微分增强的半解析求解器，用于非线性动力学谐波平衡（Harmonic Balance）计算，属数值方法开源工具论文。",
        "implications": "与书中理论模型无直接映射，纯技术论文。",
        "chapter_target": "N/A",
        "update_type": "background",
        "urgency": "background",
        "action": "忽略"
    },
    '3ba585535f18ddde': {
        "relevance": 1,
        "summary_cn": "论文提出ω-0，一个潜在预测全身世界动作模型，用于人形机器人同步行走-操作（loco-manipulation）任务，属机器人学技术论文。",
        "implications": "与书中理论模型无直接映射，纯技术论文。",
        "chapter_target": "N/A",
        "update_type": "background",
        "urgency": "background",
        "action": "忽略"
    },
    '9f55b40546bca46d': {
        "relevance": 1,
        "summary_cn": "论文提出DyPES-VLA，学习共享动力学先验与具身特定控制以支持跨具身机器人操作，属机器人VLA技术论文。",
        "implications": "与书中理论模型无直接映射，纯技术论文。",
        "chapter_target": "N/A",
        "update_type": "background",
        "urgency": "background",
        "action": "忽略"
    },
    '5b2961819036d139': {
        "relevance": 1,
        "summary_cn": "论文提出GeniWorld，一个可泛化的交互式世界模型，通过视觉动作支持机器人操作的仿真与评估，属机器人世界模型技术论文。",
        "implications": "与书中理论模型无直接映射，纯技术论文。",
        "chapter_target": "N/A",
        "update_type": "background",
        "urgency": "background",
        "action": "忽略"
    },
    '5432e9a796145b4a': {
        "relevance": 1,
        "summary_cn": "论文展示MRI腔室内经针遥操作的主从式机器人操作器，通过流体传动传递运动与力，属医疗机器人工程技术论文。",
        "implications": "与书中理论模型无直接映射，纯技术论文。",
        "chapter_target": "N/A",
        "update_type": "background",
        "urgency": "background",
        "action": "忽略"
    },
    '77826b87feac098b': {
        "relevance": 1,
        "summary_cn": "论文证明具有退化迁移率与奇异扩散的Cahn-Hilliard方程在三维有界凸域上的全局弱解存在性，属数学分析论文。",
        "implications": "与书中理论模型无直接映射，纯数学论文。",
        "chapter_target": "N/A",
        "update_type": "background",
        "urgency": "background",
        "action": "忽略"
    },
    'f4c7b0790d211cac': {
        "relevance": 1,
        "summary_cn": "论文证明对充分大的n，任意正常边染色的n顶点完全图存在使用每种颜色至多一次的n-1顶点彩虹路径，解决Andersen 1989猜想，属图论论文。",
        "implications": "与书中理论模型无直接映射，纯数学论文。",
        "chapter_target": "N/A",
        "update_type": "background",
        "urgency": "background",
        "action": "忽略"
    },
    'c2a89ad14fb78a1c': {
        "relevance": 1,
        "summary_cn": "论文报道二维机械拓扑绝缘体中的矢量边缘孤子与畴壁，研究等群速度边缘模式的非线性相互作用，属凝聚态物理论文。",
        "implications": "与书中理论模型无直接映射，纯物理论文。",
        "chapter_target": "N/A",
        "update_type": "background",
        "urgency": "background",
        "action": "忽略"
    },
    '125c70a25f784d92': {
        "relevance": 1,
        "summary_cn": "论文提出SPT-3G D1前景鲁棒的透镜模板，用于原始引力波B模搜索中抑制CMB透镜污染，属宇宙学观测论文。",
        "implications": "与书中理论模型无直接映射，纯物理论文。",
        "chapter_target": "N/A",
        "update_type": "background",
        "urgency": "background",
        "action": "忽略"
    },
    'ae335101fce56e0b': {
        "relevance": 1,
        "summary_cn": "论文证明有限马尔可夫链平均首达时间对任意速率的对数灵敏度以1为界且灵敏度之和为-1，构成守恒控制预算，属随机过程理论论文。",
        "implications": "与书中理论模型无直接映射，纯数学论文。",
        "chapter_target": "N/A",
        "update_type": "background",
        "urgency": "background",
        "action": "忽略"
    },
    '3590b172cae4bc8f': {
        "relevance": 1,
        "summary_cn": "论文在神经网络场论框架下综述两个紧致玻色子的混合连续/离散隐变量构造，讨论BKT相变等拓扑扇区求和，属理论物理论文。",
        "implications": "与书中理论模型无直接映射，纯物理论文。",
        "chapter_target": "N/A",
        "update_type": "background",
        "urgency": "background",
        "action": "忽略"
    },
    '477afcca3e4e5112': {
        "relevance": 1,
        "summary_cn": "论文发展稀疏随机图普适性的最优连接系统框架，证明随机图G(n,C ln n/n)以高概率包含所有最大度有界的n顶点树，回答Montgomery 2019问题，属随机图论论文。",
        "implications": "与书中理论模型无直接映射，纯数学论文。",
        "chapter_target": "N/A",
        "update_type": "background",
        "urgency": "background",
        "action": "忽略"
    },
    'ce68e7712010f3df': {
        "relevance": 1,
        "summary_cn": "论文发展随机宽度定律、谱总体与几何重建的统一框架，证明d维正交盒球形宽度累积量的精确奇偶律，属几何测度理论论文。",
        "implications": "与书中理论模型无直接映射，纯数学论文。",
        "chapter_target": "N/A",
        "update_type": "background",
        "urgency": "background",
        "action": "忽略"
    },
    'e824a59c4e21d077': {
        "relevance": 1,
        "summary_cn": "论文构造有限VC维二元分类的统计最优不可知PAC学习算法，达到理论最优风险界，属学习理论论文。",
        "implications": "与书中理论模型无直接映射，纯理论论文。",
        "chapter_target": "N/A",
        "update_type": "background",
        "urgency": "background",
        "action": "忽略"
    },
    '541897e8d049c6c4': {
        "relevance": 1,
        "summary_cn": "论文研究循环n次根的数量与傅里叶支撑不相交性，验证Björck-Saffari猜想相关命题，属代数几何/信号处理交叉论文。",
        "implications": "与书中理论模型无直接映射，纯数学论文。",
        "chapter_target": "N/A",
        "update_type": "background",
        "urgency": "background",
        "action": "忽略"
    },
    'f61b197d16ad8479': {
        "relevance": 1,
        "summary_cn": "论文证明在任意加性估值下存在满足EF1与分数帕累托最优的平衡分配（各agent捆绑大小至多差1），属算法博弈论论文。",
        "implications": "与书中理论模型无直接映射，纯理论论文。",
        "chapter_target": "N/A",
        "update_type": "background",
        "urgency": "background",
        "action": "忽略"
    },
    '1db804875731ff17': {
        "relevance": 1,
        "summary_cn": "论文提出可扩展的VARMA模型估计方法，应对似然非凸、参数化等价类与全序列计算开销问题，属时间序列统计论文。",
        "implications": "与书中理论模型无直接映射，纯统计论文。",
        "chapter_target": "N/A",
        "update_type": "background",
        "urgency": "background",
        "action": "忽略"
    },
    '608895a024e0bc6f': {
        "relevance": 1,
        "summary_cn": "论文研究非交换Moyal平面上自由实标量场的贝尔非局域性，扭曲多粒子统计与Fock空间dress表示对贝尔相关的影响，属量子场论论文。",
        "implications": "与书中理论模型无直接映射，纯物理论文。",
        "chapter_target": "N/A",
        "update_type": "background",
        "urgency": "background",
        "action": "忽略"
    },
    '303c178579a1b7b4': {
        "relevance": 1,
        "summary_cn": "论文用孤立盘星系模拟检验Chandrasekhar动力摩擦公式对大质量星团迁移的有效性，属天体物理论文。",
        "implications": "与书中理论模型无直接映射，纯物理论文。",
        "chapter_target": "N/A",
        "update_type": "background",
        "urgency": "background",
        "action": "忽略"
    },
    'd7e4692d07422ed4': {
        "relevance": 1,
        "summary_cn": "论文用顺序pretty-good测量实现维度无关的对数级量子阴影断层扫描样本复杂度，属量子信息理论论文。",
        "implications": "与书中理论模型无直接映射，纯物理论文。",
        "chapter_target": "N/A",
        "update_type": "background",
        "urgency": "background",
        "action": "忽略"
    },
    'fbff282588e9a2b5': {
        "relevance": 1,
        "summary_cn": "论文研究单调对抗者场景下的学习最优速率：对抗者观察样本后附加正确标注的额外样本，属对抗学习理论论文。",
        "implications": "与书中理论模型无直接映射，纯理论论文。",
        "chapter_target": "N/A",
        "update_type": "background",
        "urgency": "background",
        "action": "忽略"
    },
    '0681600b2b972448': {
        "relevance": 1,
        "summary_cn": "论文提出profile-separation框架，为No-U-Turn采样器在强log-concave目标上的定量收敛提供充分符号条件，属MCMC采样理论论文。",
        "implications": "与书中理论模型无直接映射，纯统计论文。",
        "chapter_target": "N/A",
        "update_type": "background",
        "urgency": "background",
        "action": "忽略"
    },
    'c910e0abcd74da6d': {
        "relevance": 1,
        "summary_cn": "论文给出交错链环CWR不变量的加权矩阵公式，统一构造各阶分量，属纽结理论论文。",
        "implications": "与书中理论模型无直接映射，纯数学论文。",
        "chapter_target": "N/A",
        "update_type": "background",
        "urgency": "background",
        "action": "忽略"
    },
    '353e5e291c5b9a38': {
        "relevance": 1,
        "summary_cn": "论文严格构造并验证四分之一平面上阻尼波方程（Maxwell-Cattaneo-Vernotte）的广义d'Alembert型闭合解，属偏微分方程论文。",
        "implications": "与书中理论模型无直接映射，纯数学论文。",
        "chapter_target": "N/A",
        "update_type": "background",
        "urgency": "background",
        "action": "忽略"
    },
    '98e30b922b53d98d': {
        "relevance": 1,
        "summary_cn": "论文用DMRG计算低密度极化子金属的声子谱函数，研究电子-声子耦合对一维Holstein模型的影响，属凝聚态物理论文。",
        "implications": "与书中理论模型无直接映射，纯物理论文。",
        "chapter_target": "N/A",
        "update_type": "background",
        "urgency": "background",
        "action": "忽略"
    },
    '1ae1141f3a7f46e5': {
        "relevance": 1,
        "summary_cn": "论文从资源视角综述结构化相干：仅离散自由度可及时的光学相干统计描述，属物理光学论文。",
        "implications": "与书中理论模型无直接映射，纯物理论文。",
        "chapter_target": "N/A",
        "update_type": "background",
        "urgency": "background",
        "action": "忽略"
    },
    '270de9ef08fcc445': {
        "relevance": 1,
        "summary_cn": "论文综述量子系统罕见事件的大偏差理论，从量子游走到随机暴胀，发展量子大偏差的数学基础，属量子统计物理论文。",
        "implications": "与书中理论模型无直接映射，纯物理论文。",
        "chapter_target": "N/A",
        "update_type": "background",
        "urgency": "background",
        "action": "忽略"
    },
    '9d83611fb4304b1e': {
        "relevance": 1,
        "summary_cn": "论文建立三层分层流体（平底、自由面与两个界面）非线性水波的哈密顿公式化与Dirichlet-Neumann算子近似，属流体力学论文。",
        "implications": "与书中理论模型无直接映射，纯物理论文。",
        "chapter_target": "N/A",
        "update_type": "background",
        "urgency": "background",
        "action": "忽略"
    },
    '660cf7d6f4dacaa4': {
        "relevance": 1,
        "summary_cn": "论文用DFT研究金属配位对层状有机金属单原子催化剂稳定性与ORR/OER活性的影响，属计算催化论文。",
        "implications": "与书中理论模型无直接映射，纯化学论文。",
        "chapter_target": "N/A",
        "update_type": "background",
        "urgency": "background",
        "action": "忽略"
    },
    '351244c4f8d0fefc': {
        "relevance": 1,
        "summary_cn": "论文发展单模量子泵浦场驱动的非线性康普顿散射的完全量子化理论，包含泵浦耗尽与终态关联，属量子电动力学论文。",
        "implications": "与书中理论模型无直接映射，纯物理论文。",
        "chapter_target": "N/A",
        "update_type": "background",
        "urgency": "background",
        "action": "忽略"
    },
    '3543b528d94331d9': {
        "relevance": 1,
        "summary_cn": "论文提出BaKron，用Kronecker分解Hessian加速神经网络量化算法族，属模型压缩技术论文。",
        "implications": "与书中理论模型无直接映射，纯技术论文。",
        "chapter_target": "N/A",
        "update_type": "background",
        "urgency": "background",
        "action": "忽略"
    },
    '1ec5ad2b32e0dfd0': {
        "relevance": 1,
        "summary_cn": "论文发展ACF、PACF、Durbin-Levinson递推与一步预测的回归教学框架，属时间序列教学法论文。",
        "implications": "与书中理论模型无直接映射，纯统计论文。",
        "chapter_target": "N/A",
        "update_type": "background",
        "urgency": "background",
        "action": "忽略"
    },
    'e448b21b066b80dd': {
        "relevance": 1,
        "summary_cn": "论文证明n个独立非负均值至多1的随机变量和超过阈值t的尾部概率界，属概率论论文。",
        "implications": "与书中理论模型无直接映射，纯数学论文。",
        "chapter_target": "N/A",
        "update_type": "background",
        "urgency": "background",
        "action": "忽略"
    },
    'db6a9544043f4379': {
        "relevance": 1,
        "summary_cn": "论文介绍PyOMES开源框架，用于生化过程动态模拟的模块化建模环境，属过程工程开源工具论文。",
        "implications": "与书中理论模型无直接映射，纯工程技术论文。",
        "chapter_target": "N/A",
        "update_type": "background",
        "urgency": "background",
        "action": "忽略"
    },
    '7acb24c4c9752390': {
        "relevance": 1,
        "summary_cn": "论文提出Tytan，交互式神经符号构造关系数据语义模式（semantic schemas），解决数据分析系统的知识获取瓶颈，属数据管理技术论文。",
        "implications": "与书中理论模型无直接映射，纯技术论文。",
        "chapter_target": "N/A",
        "update_type": "background",
        "urgency": "background",
        "action": "忽略"
    },
}

def main():
    with open(PAPERS_PATH) as f:
        papers = json.load(f)
    try:
        with open(CACHE_PATH) as f:
            cache = json.load(f)
    except FileNotFoundError:
        cache = {}

    now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat()
    new_keys = [p['_cache_key'] for p in papers if p['_cache_key'] not in cache]
    analyzed = 0
    written = 0
    missing = []
    high_value = []

    for p in papers:
        key = p['_cache_key']
        if key in cache:
            continue
        # 用前16位匹配分析（缓存键是全32位）
        matched = None
        for prefix, a in ANALYSES.items():
            if key.startswith(prefix):
                matched = a
                break
        if matched is None:
            # 兜底：应覆盖所有新论文，否则标记缺失
            missing.append(key[:16])
            continue
        cache[key] = {
            "cached_at": now,
            "title": p.get('title', ''),
            "analysis": matched,
            "relevance": matched['relevance'],
            "urgency": matched['urgency'],
            "model_scores": {"WorkBuddy": matched['relevance']}
        }
        analyzed += 1
        written += 1
        if matched['relevance'] >= 7:
            high_value.append(p.get('title', ''))

    with open(CACHE_PATH, 'w', encoding='utf-8') as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)

    print(f"✅ 分析完成: 共处理 {analyzed} 篇新论文")
    print(f"📝 写入缓存: {written} 条")
    if missing:
        print(f"⚠️ 缺失分析: {len(missing)} 篇 -> {missing}")
    print(f"⭐ 高价值论文 (relevance>=7): {len(high_value)} 篇")
    for t in high_value:
        print("   -", t[:90])
    print(f"📊 缓存总条目: {len(cache)}")

if __name__ == '__main__':
    main()
