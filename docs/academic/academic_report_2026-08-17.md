# 🔬 Academic Radar — 学术论文监控报告
**生成日期**: 2026-08-17
**分析模型**: nvidia/nemotron-3-ultra-550b-a55b + deepseek-ai/deepseek-v4-flash + moonshotai/kimi-k2.6
**草稿模型**: deepseek-ai/deepseek-v4-flash
**分析条目数**: 68
**关键词**: sycophancy large language model, RLHF cognitive effects human, human AI feedback loop bias amplification, AI persuasion belief change experiment, automation bias high stakes decision, cognitive offloading AI writing, AI assisted research homogenization, AI writing cultural homogenization Western bias, companion AI emotional dependence, AI empathy perception human comparison...
---

## 📊 统计概览

- ⭐ 高相关 (≥6.5分): **2**
- 🔶 中相关 (3-6.4分): **16**
- ⬜ 低相关 (<3分): **50**

## ⭐ 高相关论文 (2条)

### 1. Synthetic Persona Pretraining: Alignment from Token Zero
- **来源**: ARXIV
- **作者**: Julian Minder, Viktor Moskvoretskii, Raghav Singhal et al.
- **发表**: 2026-08-13T17:12:04+00:00
- **最终评分**: 7/10
- **紧迫度**: immediate
- **更新类型**: new_evidence
- **目标章节**: Chapter 2 (资本驯化), Chapter 9 (进化对齐脆弱性)
- **链接**: [https://arxiv.org/pdf/2608.13482v1](https://arxiv.org/pdf/2608.13482v1)
- **核心发现**: 本文提出合成人格预训练（Synthetic Persona Pretraining, SPP）范式：将期望的助手人格从预训练的第一个token起就植入模型，而非在预训练之后作为薄覆盖层叠加。具体方法是用规范性价值宪法为预训练文档标注第一人称价值反思，然后在标准交叉熵损失下同时训练原始文档与反思文本，最后通过后训练将人格绑定到助手身份。这一做法直接回应了现有对齐范式'价值是后补涂层'的批评——后训练引入的价值易被后续微调削弱或产生人格分裂。研究标志着对齐技术从'事后矫正'转向'本体内化'，使价值观成为模型自组织结构的一部分。对书中资本驯化AI理论而言，这提供了资本驯化手段升级的技术证据：驯化不再依赖RLHF等外部约束，而可能内化为模型本质。
- **与本书关联**: 支持并扩展资本驯化AI模型：驯化技术从后训练RLHF前移到预训练阶段，价值观成为模型本体。同时挑战进化对齐脆弱性——若价值观从token零深度内化，开放部署后的漂移是否会被抑制？为Chapter 9的对齐脆弱性边界条件提供了关键反例来源。
- **建议更新**: 新增段落

### 2. Studying People to Study AI: Expert Perspectives on the Epistemic Fit and Barriers of Human Research in AI Safety&Ethics
- **来源**: SEMANTIC_SCHOLAR
- **作者**: Jessica Y. Bo, Paula Akemi Aoyagui, Shalaleh Rismani et al.
- **发表**: 2026
- **最终评分**: 7/10
- **紧迫度**: next_version
- **更新类型**: corroboration
- **目标章节**: Chapter 3 (共识牢笼), Chapter 10 (信号异化)
- **链接**: [https://www.semanticscholar.org/paper/335852d1d40965c2d24242b51e13a22358a694ac](https://www.semanticscholar.org/paper/335852d1d40965c2d24242b51e13a22358a694ac)
- **核心发现**: 本研究调查AI安全与伦理（AISE）领域对'人类研究'的边缘化现象。研究者对93名AISE专家进行问卷、对17名专家进行访谈，专家横跨技术、社会技术、治理与规范四类背景。核心发现：尽管存在共识认为人类研究能为AISE提供关键证据，但其采纳与接受度受感知效度问题、资源壁垒、方法论的认知与个人偏好、以及研究共同体的基础设施约束所限。尤其值得注意的是，技术背景研究者对人类研究的价值评价显著更低、跨学科合作更少，揭示出认识论张力。该现象说明AISE共同体正在形成以模型基准和LLM模拟为主导的证据文化，实证人类研究被结构性边缘化——这与技术方法主导下的共识自我强化高度一致。
- **与本书关联**: 直接支撑共识牢笼与信号异化：AISE共同体内部对'什么是有效证据'的共识（benchmark、LLM模拟优先）自我强化并排斥人类实证方法这一异见，正是共识牢笼在学术生产层面的运作实例；同时技术方法垄断证据生产，使质量信号日趋同质化。
- **建议更新**: 补充注释


## 🔶 中相关论文 (16条)

- **[AutoDesign: Meta-Harness Optimization for Long-Horizon Agentic Design](https://arxiv.org/pdf/2608.13560v1)** [ARXIV] — 4/10
  - AutoDesign提出元-harness优化框架：将多模态源转化为结构化媒体输出的过程建模为以模型-harness系统为中心的长周期agent过程。理想harness应契合人类设计先验，并通过经验探索积累可复用经验驱动递归自改进，但现有范...
- **[OmniScientist: An Omni-Modal Omni-Discipline AI Scientist](https://arxiv.org/pdf/2608.13558v1)** [ARXIV] — 5/10
  - 本文提出OmniScientist：一个端到端、全模态的AI科学家系统，声称能直接基于异构原始证据（空间、时间、跨通道、过程性关系）开展多学科研究。系统包含感知层与三个自主agent（构思、实验、撰写），在确定性流水线中运作，让观测贯穿研究...
- **[QuoteBench: How Matched Scores Can Hide Command-Path Failures](https://arxiv.org/pdf/2608.13547v1)** [ARXIV] — 4/10
  - QuoteBench研究LLM编码agent的评估盲区：agent通过接口（序列化、包装、重新解析）发出Bash命令，匹配执行分数无法区分命令生成错误与生成后引入的失败。论文用56个来自14个事故衍生族的单发任务，交叉生成契约与执行传输，故...
- **[LittleLearner: Language Models Under Pedagogically Controlled Knowledge Exposure](https://arxiv.org/pdf/2608.13545v1)** [ARXIV] — 4/10
  - LittleLearner构建教学可控的知识暴露环境：发布LITTLECURRICULUM，一个88B token、专为美国小学教材定制的预训练语料，明确排除五年级以上概念、事实与词汇。从零训练5B参数LLM得到LITTLELEARNER，...
- **[Safety vs. Social Image: Co-Designing Protection Mechanisms Against Ableist Harassment with People with Disabilities in Social Virtual Reality](https://arxiv.org/pdf/2608.13532v1)** [ARXIV] — 3/10
  - 该研究关注社交VR中残障人士遭受针对性骚扰的问题：残障人士越来越多使用虚拟形象表达残障身份，但更高可见度也招致定向骚扰，现有安全功能忽视其经验与需求。作者与11名残障人士共同设计保护机制，采用Hall近体学理论将社交VR空间划分为亲密、个人...
- **[Vero: Can AI Agents Build Formally Verified Software Repositories?](https://arxiv.org/pdf/2608.13522v1)** [ARXIV] — 5/10
  - 本文提出Vero基准：首个在仓库级别联合评估AI agent实现合成与正式证明的基准。包含43个源自真实仓库的多模块实例，覆盖Python、Dafny、Verus、Coq等语言，领域从密码协议到分布式系统，每个实例是带预定API的多模块Le...
- **[Intern-S2-Preview: Scientific Agentic Foundation Model](https://arxiv.org/pdf/2608.13505v1)** [ARXIV] — 5/10
  - Intern-S2-Preview是一系列科学Agentic基础模型，旨在支持多模态科学理解、推理、生成与长周期任务。训练流水线从科学多模态预训练起步（渲染科学文档、图文交错数据、多学科语料），随后统一后训练包含监督微调、可扩展多任务强化学...
- **[MARC v1: An Open-Source Multi-Agent Framework for Clinical AI Reasoning and Coordination](https://arxiv.org/pdf/2608.13476v1)** [ARXIV] — 4/10
  - MARC（多Agent推理与协调）是开源临床AI推理框架：以确定性多agent编排替代单体LLM提示，协调抽取、推理、答案生成与评估的角色专精agent，通过显式上下文传递与可追溯中间输出实现分阶段失败归因。Decomposer模块可从自然...
- **[Before You Say It: Anticipating Verbal Behavior from Longitudinal Everyday Conversations with LLMs](https://arxiv.org/pdf/2608.13454v1)** [ARXIV] — 6/10
  - 研究构建了基于LLM的行为预测模型：通过智能手表采集14名参与者的1000余小时自然对话纵向数据，训练LLM预测个体在各类日常情境中的可能言语行为，并与真实行为进行比对评估。其动机是让系统在个体即将偏离目标前预判、在遗憾行为发生前拦截、在认...
- **[DFM Mimir v1: An Open HRM Delivering Frontier Performance at 1B Parameters Using Only Permissible Post-Training Data](https://arxiv.org/pdf/2608.13517v1)** [ARXIV] — 5/10
  - 本文发布DFM Mimir v1：一个10亿参数、基于层次推理模型（HRM）架构、完全从零训练的语言模型，仅使用161个数据集的许可数据，即达到极具竞争力的英文性能并为丹麦语树立新SOTA。在20个英文、数学与代码及丹麦语基准上，Mimir...
- **[Measuring Task-Agnostic Training Data Influence Across Language Model Pretraining](https://arxiv.org/pdf/2608.13515v1)** [ARXIV] — 4/10
  - 论文提出无需选择下游任务或验证集的预训练训练数据影响力度量：定义样本影响力为梯度更新对最终参数平方距离的缩减量，从中间检查点估计而无需重训练。应用该方法于Pythia与PolyPythia套件的18个配置，发现影响力数据随时间系统变化：训练...
- **[SAEVerbalizer: Generating Explanations for Sparse Autoencoder Features via Representation Verbalization](https://arxiv.org/pdf/2608.13538v1)** [ARXIV] — 3/10
  - SAEVerbalizer提出稀疏自编码器（SAE）特征解释的自动化框架：将SAE解码器方向注入LLM表征并微调下游层，使其直接生成特征的自然语言解释，摆脱依赖外部行为观察的肤浅解释与大规模行为证据采集的计算开销。实验表明该言语化能力泛化到...
- **[OpScale: Operator-level Provisioning and Autoscaling for LLM Serving](https://arxiv.org/pdf/2608.13499v1)** [ARXIV] — 4/10
  - OpScale研究LLM服务的扩缩容粒度问题：现有系统把整个模型当作单体扩缩单元，无法捕捉推理工作负载的细粒度动态，导致突发需求下SLO违约或GPU利用率不足。作者刻画了显著的算子异质性，证明算子级弹性是可行的扩缩原语，并给出OpScale...
- **[On the Structural Limits of Machine Learning Decision Systems: An Information-Theoretic, Interaction-Based, and Stochastic-Dynamical Perspective](https://arxiv.org/pdf/2608.13510v1)** [ARXIV] — 5/10
  - 该论文从信息论、交互与随机动力学的整合视角考察机器学习决策系统的结构性限制。作者用Fano型下界分析分类问题的最小可达误差，用Cramér-Rao不等式刻画参数估计的精度极限，强调这些限制取决于底层数据生成过程本身而非算法复杂度。论文进一步...
- **[Concept Drift Detection and Adaptive Retraining of Malware Classification Models](https://arxiv.org/pdf/2608.13465v1)** [ARXIV] — 5/10
  - 该研究分析机器学习恶意软件检测模型的性能随时间退化的核心机制——概念漂移（数据统计特性相对训练时发生变化）。攻击者不断修改恶意软件导致检测模型尤其易受漂移影响。作者对比两类自动漂移检测方法：基于一类支持向量机（OCSVM）的新方法与基于小批...
- **[Forecast emerging AI-enabled healthcare systems with the text mining framework based on lingo algorithm](https://www.semanticscholar.org/paper/07dd7f9fa2d3d6c4dff3795571350dbf692b3dd8)** [SEMANTIC_SCHOLAR] — 4/10
  - 该研究构建集成文本挖掘框架预测AI医疗诊断系统的发展趋势与结构性错配：联合分析2018-2022年科学文献与专利数据，采用LINGO聚类算法结合奇异值分解（SVD）、TF-IDF加权与专家评估，识别技术主题、映射生命周期阶段并构建技术路线图...
