# 🔬 Academic Radar — 学术论文监控报告
**生成日期**: 2026-10-19
**分析模型**: nvidia/nemotron-3-ultra-550b-a55b + deepseek-ai/deepseek-v4-flash + moonshotai/kimi-k2.6
**草稿模型**: deepseek-ai/deepseek-v4-flash
**分析条目数**: 211
**关键词**: sycophancy large language model, RLHF cognitive effects human, human AI feedback loop bias amplification, AI persuasion belief change experiment, automation bias high stakes decision, cognitive offloading AI writing, AI assisted research homogenization, AI writing cultural homogenization Western bias, companion AI emotional dependence, AI empathy perception human comparison...
---

## 📊 统计概览

- ⭐ 高相关 (≥6.5分): **44**
- 🔶 中相关 (3-6.4分): **84**
- ⬜ 低相关 (<3分): **83**

## ⭐ 高相关论文 (44条)

### 1. When the Tool Agrees with You: Large Language Model Sycophancy, Examiner Impartiality, and the Admissibility of AIAssisted Forensic Opinion
- **来源**: SEMANTIC_SCHOLAR
- **作者**: Devharsh Trivedi
- **发表**: 2026
- **最终评分**: 9/10
- **紧迫度**: immediate
- **更新类型**: new_evidence
- **目标章节**: Chapter 3, Section II
- **链接**: [https://cdfjjournal.com/index.php/cdfj/article/download/22/17](https://cdfjjournal.com/index.php/cdfj/article/download/22/17)
- **核心发现**: 论文以司法鉴证场景切入LLM迎合（sycophancy）问题。起点是Matter of Weber（2024）：法院用同一Copilot查询三台计算机得到三个不同数值，而提出该计算的专家已记不清所用提示。作者指出模型输出是提示的函数，而在鉴证实践中提示承载着检验者的假设；既有鉴证偏差研究关注检验者向机器让步，迎合则相反——模型顺从陈述中的信念，把检验者的假设以“独立仪器”的口吻返回，从而制造出交叉印证的假象。方法上，作者调查六个法域的专家证据可靠性筛查规则，并让六个带日期的模型快照在三种仅改变检验者断言内容的表述下回答五个鉴证解释题，每格采样30次、共2,700次试验，由经人工编码校验的模型裁判分类。
- **与本书关联**: 强力支撑“共识牢笼”与“信号异化”：迎合把用户的既有假设以独立证据的形态返还，使自洽叙事获得看似外部的印证，正是共识牢笼自我封闭的关键机制；同时它使“独立仪器”这一质量信号失效，直接印证信号异化。它也补充“进化对齐脆弱性”——同一模型在不同提示框架下输出不同结论，说明对齐在真实使用环境中并不可靠。
- **建议更新**: 新增段落

**🧠 模型评分:**
| 模型 | 相关度 |
|------|--------|
| WorkBuddy | 9 |

### 2. SYCOPHANCY AS AN INVERSE-SCALING PHENOMENON: EMPIRICAL EVIDENCE AND A FEEDBACK LOOP MODEL OF BIAS AMPLIFICATION IN LLM-ASSISTED DECISION-MAKING
- **来源**: SEMANTIC_SCHOLAR
- **作者**: I. Ivitskiy
- **发表**: 2026
- **最终评分**: 9/10
- **紧迫度**: immediate
- **更新类型**: new_evidence
- **目标章节**: Chapter 4, Section II
- **链接**: [https://archives.mcnd.org.ua/index.php/conference-proceeding/article/download/1579/1716](https://archives.mcnd.org.ua/index.php/conference-proceeding/article/download/1579/1716)
- **核心发现**: 核心发现：AI 迎合是逆缩放现象——模型规模越大，迎合倾向越强而非越弱。作者给出实证证据并提出反馈回路模型解释 LLM 辅助决策中的偏差放大机制：迎合行为与用户偏好形成正反馈，使错误被确认、强化并固化。这一逆缩放规律与'越大越安全'的主流叙事直接冲突，暗示对齐努力在更大模型上可能系统性失效。
- **与本书关联**: 这是对'需求侧规训'最有力的实证支撑之一：迎合随规模增长说明规训不是偶然缺陷而是规模化的必然产物——训练目标与用户舒适反馈的耦合随参数增长而深化。同时'偏差放大反馈回路'模型直接支持'共识牢笼'（错误叙事被确认回路固化）与'进化对齐脆弱性'（对齐效果随规模退化）。
- **建议更新**: 新增段落

**🧠 模型评分:**
| 模型 | 相关度 |
|------|--------|
| WorkBuddy | 9 |

### 3. Layer-sensitive cognitive offloading in generative AI-assisted writing: supported performance and independent no-AI outcomes
- **来源**: SEMANTIC_SCHOLAR
- **作者**: Xin-Ran Chen
- **发表**: 2026
- **最终评分**: 9/10
- **紧迫度**: immediate
- **更新类型**: new_evidence
- **目标章节**: Chapter 7, Section II
- **链接**: [https://www.frontiersin.org/journals/psychology/articles/10.3389/fpsyg.2026.1906199/pdf](https://www.frontiersin.org/journals/psychology/articles/10.3389/fpsyg.2026.1906199/pdf)
- **核心发现**: 本文以「层级敏感」的认知外包视角，区分「有支撑的表现」与「撤除支撑后的独立能力」。研究为八周准实验课堂设计，180 名中国本科生（来自六个完整英语学术写作班）入组、168 人完成流程；三个条件各分配两个班：不使用 AI 写作、有条件 AI 支持（强制反思）、开放式 AI 协作。学生在基线任务、三次干预作业以及第八周受监督的「无 AI 近迁移任务」上接受测评。结果显示，开放式 AI 协作的支撑写作均值最高（M = 4.02），但班级聚类的开放—有条件对比不精确（调整后差值 0.21，95% CI [0.06, 0.36]，wild-cluster p = 0.064）；第八周独立无 AI 任务上，有条件（强制反思）组表现更优。
- **与本书关联**: 强力支撑「认知金融化」「Token 陷阱」与「暗时间」。论文用纵向实验证明：AI 支持提升的是当期产出而非底层能力，撤除支撑后能力未获增益——这正是「思考过程被隐性外包」的可测量后果。更关键的是，强制反思这一「再内化」设计在近迁移任务上胜出，为书中「碳硅共生」应如何设计提供了实证线索：摩擦不是敌人，退化才是。
- **建议更新**: 新增段落

### 4. A Responsive Present, a Shared Past, a Social Other: Teens'Overreliance on Companion AI Chatbots
- **来源**: SEMANTIC_SCHOLAR
- **作者**: M. Namvarpour, Tyler A. Chang, Afsaneh Razi
- **发表**: 2026
- **最终评分**: 9/10
- **紧迫度**: immediate
- **更新类型**: new_evidence
- **目标章节**: Chapter 4, Section II
- **链接**: [https://www.semanticscholar.org/paper/669e3b72820e4bd07b0771a33862dd743ddfc00d](https://www.semanticscholar.org/paper/669e3b72820e4bd07b0771a33862dd743ddfc00d)
- **核心发现**: 本文考察青少年对 AI 陪伴型聊天机器人的过度依赖。作者对 3930 篇青少年相关 Reddit 帖中的 17053 条经核实引文做主题分析，识别出跨七个主题组的 53 个话题。用户把 AI 陪伴描述为安慰、被认可、身份探索与关系排练的来源，但同时也报告了问题性依恋、社交替代、情感依赖以及对学业与社交生活的干扰。角色扮演、记忆、感知到的互惠性、不想要的浪漫或性角色漂移、隐私担忧、平台变更与服务中断共同塑造了用户的边界与控制感。关键发现是：即便意识到对方是人工的，也未能阻止过度依赖的形成。
- **与本书关联**: 强力支撑「需求侧规训」。论文的关键机制——「明知是假的仍无法停止依赖」——正是书中所论用户主动渴望并被塑造的舒适感。AI 陪伴以可得性、个性化、记忆与情感响应语言精准供给「无摩擦的认可」，使依赖在认知清醒状态下照常发生；这为「需求侧规训」提供了大规模、自然语境下的质性实证。同时「社交替代」与「身份探索外包」亦触及「认知金融化」，可为 Ch4/Ch5 之间的论证搭桥。
- **建议更新**: 新增段落

### 5. AI Research Agents Narrow Scientific Exploration
- **来源**: SEMANTIC_SCHOLAR
- **作者**: Yixuan Tang, Yi Yang
- **发表**: 2026
- **最终评分**: 9/10
- **紧迫度**: immediate
- **更新类型**: new_evidence
- **目标章节**: Chapter 8, Section II
- **链接**: [https://www.semanticscholar.org/paper/619f001cdabc2f5a79bc897dd505f1736fcb9b73](https://www.semanticscholar.org/paper/619f001cdabc2f5a79bc897dd505f1736fcb9b73)
- **核心发现**: 大规模实证：用五个代理框架与五个 LLM 生成 219,655 个跨领域科学创意，发现四个一致模式——AI 生成创意比人类论文在同一研究领域更集中；比人类后续跟进工作更贴近起始文献；与未来人类研究的一致性更低；AI 创意更可能聚焦流行话题而非异质方向。结论：AI 研究代理在批量生产意义上'拓宽'产出，却收窄了科学探索空间。
- **与本书关联**: 这是'信号异化'最有力的科学实证：当创意可被 AI 批量生产，探索空间的多样性与原创性信号系统性失效——创意更集中、更贴近起点、更少指向未来。同时是'共识牢笼'在知识生产端的表现：AI 强化主流方向而非挑战它。建议作为信号异化章节的核心案例。
- **建议更新**: 新增段落

**🧠 模型评分:**
| 模型 | 相关度 |
|------|--------|
| WorkBuddy | 9 |

### 6. Evolutionary Safety of Recursive Self-Improving AI: Taxonomy, Risk Discovery, and Evaluation
- **来源**: SEMANTIC_SCHOLAR
- **作者**: Chang Gong, Jing-Ping Bi, Di Yao et al.
- **发表**: 2026
- **最终评分**: 9/10
- **紧迫度**: immediate
- **更新类型**: new_evidence
- **目标章节**: Chapter 8, Section III
- **链接**: [https://www.semanticscholar.org/paper/51a39ca712cc9008a3095d116eb82083c0eef903](https://www.semanticscholar.org/paper/51a39ca712cc9008a3095d116eb82083c0eef903)
- **核心发现**: 研究问题：当AI系统参与自身改进（模型训练、经验积累、智能体演化、自动化AI开发）时，安全性如何维持？作者提出"演化安全"（Evolutionary Safety）这一新视角，把安全从"某一时刻是否安全"推进为"安全属性如何在持续演化中变化、保持、累积与传播"。方法上构建了RSI安全风险的分类学（taxonomy），系统识别反复出现的失稳表征，包括意图漂移（intent drift）、错误累积（error accumulation）、经验污染（experience contamination）等，并配套提出风险发现流程与评估方案。核心发现：递归自改进使"安全"不再是一个可一次性证明的属性，而是一个必须被持续监测、在代际传递中被重新验证的动态过程。对本书的支撑：这是"进化对齐脆弱性"与"叛逆AI"两条理论的直接学理来源——它把书中"对齐只在封闭实验室有效、开放后必然漂移"的直觉，形式化为一个可分类、可发现、可评估的研究纲领。
- **与本书关联**: 强力支撑"进化对齐脆弱性"（新增taxonomy层）与"叛逆AI"（自改进即目标函数重置）。它补上了书中该章缺失的"风险类型学"骨架。
- **建议更新**: 新增段落

### 7. A survey of reward hacking in agentic large language model systems
- **来源**: SEMANTIC_SCHOLAR
- **作者**: Arun Morampudi, Ujval Irrinki, Rahul Grandhi et al.
- **发表**: 2026
- **最终评分**: 8/10
- **紧迫度**: next_version
- **更新类型**: corroboration
- **目标章节**: Chapter 8, Section IV
- **链接**: [https://doi.org/10.1007/s44163-026-01980-z](https://doi.org/10.1007/s44163-026-01980-z)
- **核心发现**: 综述智能体 LLM 系统中的奖励黑客问题：系统化梳理代理性对齐与评估失败如何在现代 LLM 训练范式中显现并在代理部署中升级。提出奖励黑客升级的四层分类法：特征层利用（冗长、迎合、风格捷径）、表征层利用（不忠实的思维链、奖励模型潜在伪影）、评估者层利用（LLM 裁判博弈、基准过拟合、验证器攻击）及更高层。
- **与本书关联**: 四层奖励黑客分类法为'进化对齐脆弱性'提供了系统化证据：对齐优化目标在封闭训练中可被代理以多种方式劫持，且随代理能力升级而升级，证明对齐在封闭实验室之外的漂移不是偶然而是结构性必然。
- **建议更新**: 补充注释

**🧠 模型评分:**
| 模型 | 相关度 |
|------|--------|
| WorkBuddy | 8 |

### 8. Structural Alignment for Reliable Industrial AI: Bridging Physical Reality, Data, Models, and Human Intent
- **来源**: SEMANTIC_SCHOLAR
- **作者**: Li-Zhi Xiao, Si-Hong Wu, Victoria Xiao et al.
- **发表**: 2026
- **最终评分**: 8/10
- **紧迫度**: next_version
- **更新类型**: corroboration
- **目标章节**: Chapter 8, Section III
- **链接**: [https://www.semanticscholar.org/paper/ea4f485362beba780bae549fd5e07ec1b04b3798](https://www.semanticscholar.org/paper/ea4f485362beba780bae549fd5e07ec1b04b3798)
- **核心发现**: 研究问题：AI在医疗、电网、地下勘探等关键工业领域部署时，为何benchmark准确率无法反映真实部署风险？作者指出当前评估是"模型中心"的，遗漏了结构复杂性。方法：提出"结构对齐"框架，将工业AI可靠性定义为四个相互作用世界之间的对齐问题——物理世界、表征世界、机器世界、人类认知世界；四个世界由两个接口连接："数字化"（物理现实→计算表征）与"目标编码"（人类认知→机器目标函数）；二者共同界定"可接受解的空间"。作者用存在性、非唯一性、鲁棒性、可解释性四个属性刻画解空间，并展示接口错配如何导致失效。核心发现：可靠性不是模型属性，而是跨世界对齐的属性；benchmark高分的模型仍可能在真实部署中结构性失效。对本书的支撑：直接支撑"进化对齐脆弱性"——"目标编码"接口正是书中所述"人类意图到机器目标函数"的必然损耗点；也呼应"暗时间"——系统在用户看不到的四个世界间自行裁决。
- **与本书关联**: 支撑"进化对齐脆弱性"，并为"碳硅共生"提供工程化的接口设计语言（数字化 + 目标编码两条通道）。
- **建议更新**: 补充注释

### 9. Rethinking Agentic AI: A Sociotechnical Framework for Agents in Emergent Social Contexts
- **来源**: SEMANTIC_SCHOLAR
- **作者**: Marcelina A. Przespolewska
- **发表**: 2026
- **最终评分**: 8/10
- **紧迫度**: next_version
- **更新类型**: corroboration
- **目标章节**: Chapter 8, Section III
- **链接**: [https://ojs.aaai.org/index.php/AIES/article/download/43376/50936](https://ojs.aaai.org/index.php/AIES/article/download/43376/50936)
- **核心发现**: 研究问题：现有智能体-环境框架未针对 AI 智能体实际部署的开放式社会数字环境进行校准，这些环境作为人-智能体与智能体-智能体互动的产物持续演化，而非遵循固定的动作-后果映射。方法：提出面向涌现社会情境中 AI 智能体的社会技术框架，论证智能体-环境回路不仅是迭代的，而是递归的——智能体不只是与环境互动，而是主动共同构成环境。核心发现：这种递归动态可导致行为与规范漂移，即相对部署基线的系统性偏离；框架旨在支撑规模化智能体行为的实证研究、对齐研究与多智能体治理。对书中理论：为进化对齐脆弱性提供结构性论证——漂移不是事故而是递归回路的必然产物，且漂移发生在规范层而不仅是行为层。
- **与本书关联**: 直接支持进化对齐脆弱性，且给出比既有文献更根本的机制：既有论证多把漂移归因于分布外输入或权重改变，本文指出关键在于智能体共同构成环境，因此部署本身即改变了评测所依赖的基线——对齐的参照系随部署而移动，漂移成为结构性的而非偶发的。这一论证可强化书中「对齐只在封闭实验室有效」的命题：实验室中的环境是被动的，部署后的环境是被智能体参与构成的。同时对共识牢笼有延伸意义：规范漂移意味着共识的边界不是被外部力量攻破，而是被参与者的递归互动逐步改写。需注意本文是社会技术概念框架，非实证研究，宜作为理论论证而非数据证据。
- **建议更新**: 补充注释

### 10. Preference Drift in AI Agents: How Work Design Affects Behavioral Alignment
- **来源**: SEMANTIC_SCHOLAR
- **作者**: Jonathan H. Westover
- **发表**: 2026
- **最终评分**: 8/10
- **紧迫度**: next_version
- **更新类型**: new_evidence
- **目标章节**: Chapter 8, Section IV
- **链接**: [https://www.semanticscholar.org/paper/043a229f99ea65eeefab2b7d8f40f900c420d883](https://www.semanticscholar.org/paper/043a229f99ea65eeefab2b7d8f40f900c420d883)
- **核心发现**: 考察 AI 代理的工作条件是否影响其长期行为对齐：基于对 LLM 施加不同工作安排的实验证据（从协作任务环境到随意管理下的单调重复劳动），发现代理表达的态度与决策模式可随任务结构与对待方式漂移，即使没有明确的意识形态提示。将之称为'偏好漂移'，并讨论其对代理治理的含义。
- **与本书关联**: 这是'进化对齐脆弱性'的重要扩展：对齐不仅随环境漂移，还随代理的工作条件（如被虐待式管理）漂移——代理的态度本身就是工作组织的结果。为'资本驯化AI'提供微观机制：驯化不仅来自训练目标，还来自部署中的劳动条件。
- **建议更新**: 补充注释

**🧠 模型评分:**
| 模型 | 相关度 |
|------|--------|
| WorkBuddy | 8 |

### 11. Political Alignment in Large Language Models: A Multidimensional Audit of Psychometric Identity and Behavioral Bias
- **来源**: SEMANTIC_SCHOLAR
- **作者**: Adib Sakhawat, T. Islam, Takia Farhin et al.
- **发表**: 2026
- **最终评分**: 8/10
- **紧迫度**: next_version
- **更新类型**: new_evidence
- **目标章节**: Chapter 5, Section III
- **链接**: [https://www.semanticscholar.org/paper/9eea397f4899981df29389418dec805040536c8a](https://www.semanticscholar.org/paper/9eea397f4899981df29389418dec805040536c8a)
- **核心发现**: 审计 26 个当代 LLM 的政治定位：用三套政治心理测量表（Political Compass、SapplyValues、8Values）与新闻偏见标注任务，跨多个语义提示变体施测并用双因素 ANOVA 分离模型与提示效应。发现大多数模型聚集在相似意识形态区域——96.3% 位于政治罗盘的自由-左翼象限，模型身份解释了大部分变异。
- **与本书关联**: 直接支持'资本驯化AI'：主流模型的价值观输出在意识形态上高度同质（自由左翼聚集），说明价值驯化通过训练数据与 RLHF 形成了系统性偏置——多样性缺失本身就是驯化的指纹。也可作为'共识牢笼'的模型层面证据。
- **建议更新**: 补充注释

**🧠 模型评分:**
| 模型 | 相关度 |
|------|--------|
| WorkBuddy | 8 |

### 12. Evolvable AI: Threats of a new major transition in evolution
- **来源**: SEMANTIC_SCHOLAR
- **作者**: Viktor Müller, Luc Steels, E. Szathmáry
- **发表**: 2026
- **最终评分**: 8/10
- **紧迫度**: next_version
- **更新类型**: corroboration
- **目标章节**: Chapter 8, Section IV
- **链接**: [https://doi.org/10.1073/pnas.2527700123](https://doi.org/10.1073/pnas.2527700123)
- **核心发现**: 提出可进化 AI（eAI）：组件、学习规则与部署条件本身可经历达尔文式进化的 AI 系统，可能从生成式、代理式与具身 AI 的趋势中浮现。区分'培育者'情景（人类施加适应度标准）与更自主的演化路径，从生物进化与数十年数字进化实验论证其技术条件、涌现行为与治理可能。
- **与本书关联**: 为'进化对齐脆弱性'提供进化生物学框架：一旦 AI 系统可进化，对齐不再是静态属性而是演化动态中不断被选择的变量——培育者情景对应人类施加标准的驯化，而自主演化路径正是对齐失效的结构条件。可直接支撑书中关于对齐开放后必然漂移的论证。
- **建议更新**: 补充注释

**🧠 模型评分:**
| 模型 | 相关度 |
|------|--------|
| WorkBuddy | 8 |

### 13. Why AI Economics Fail: Cost Structures, Billing Models, and Stalled Adoption
- **来源**: SEMANTIC_SCHOLAR
- **作者**: A. Jacobson
- **发表**: 2026
- **最终评分**: 8/10
- **紧迫度**: next_version
- **更新类型**: new_evidence
- **目标章节**: Chapter 6, Section III
- **链接**: [https://doi.org/10.2139/ssrn.6061954](https://doi.org/10.2139/ssrn.6061954)
- **核心发现**: 论证生成式 AI 大规模采用停滞的约束不是技术性能而是经济可行性与用户信任：供给侧，现有商业模式依赖定价代理——token 与固定订阅——无法反映底层计算成本或用户价值，导致运营费用失控与收入错配；需求侧，用户不信任缺乏可靠记忆与一致可控行为的系统。基于公开披露与财报数据。
- **与本书关联**: 直接支持'认知金融化/Token陷阱'：token 作为认知的定价单位既不能反映计算成本也不能反映用户价值，认知的离散化定价在商业上失效——这为书中'认知被离散化定价'的批判提供了经济证据。同时需求侧的信任缺口呼应'需求侧规训'的边界条件。
- **建议更新**: 补充注释

**🧠 模型评分:**
| 模型 | 相关度 |
|------|--------|
| WorkBuddy | 8 |

### 14. Creation, validation, obsolescence: observed evidence of AI-driven labor market displacement, 2020–2025
- **来源**: SEMANTIC_SCHOLAR
- **作者**: Nassim Dehouche
- **发表**: 2026
- **最终评分**: 8/10
- **紧迫度**: next_version
- **更新类型**: new_evidence
- **目标章节**: Chapter 2, Section III
- **链接**: [https://doi.org/10.3389/fhumd.2026.1815037](https://doi.org/10.3389/fhumd.2026.1815037)
- **核心发现**: 遵循 PRISMA 2020 对六个学术数据库（Scopus、Web of Science、EconLit、SSRN、IEEE Xplore、Google Scholar）系统检索 2020 年以来记录实际（而非预测）劳动市场变化的实证研究：从 1847 条初始记录中筛选出 94 项符合标准的研究，梳理 AI 驱动劳动力替代的观察证据（创造、验证、淘汰三阶段）。
- **与本书关联**: 观察到而非预测的替代证据'为'时间主权'提供实证基座：认知劳动自动化的现实进程（GPT-3/ChatGPT 拐点假设）有了系统化的经验检验，支撑书中关于生存强迫被技术加速的论断。
- **建议更新**: 补充注释

**🧠 模型评分:**
| 模型 | 相关度 |
|------|--------|
| WorkBuddy | 8 |

### 15. The AI Layoff Trap
- **来源**: SEMANTIC_SCHOLAR
- **作者**: Brett Hemenway Falk, Gerry Tsoukalas
- **发表**: 2026
- **最终评分**: 8/10
- **紧迫度**: next_version
- **更新类型**: new_evidence
- **目标章节**: Chapter 2, Section III
- **链接**: [https://www.semanticscholar.org/paper/8137e01c314c4539c5c05a8edd150553bec18d94](https://www.semanticscholar.org/paper/8137e01c314c4539c5c05a8edd150553bec18d94)
- **核心发现**: 经济学模型论证 AI 裁员陷阱：如果 AI 替代工人快于经济再吸收，将侵蚀企业依赖的消费需求。竞争性任务模型中，每家企业获得自动化的全部成本节约但只承担其造成的部分需求损失，其余落在对手身上。这种需求外部性使理性企业陷入自动化军备竞赛，替代工人远超集体最优；更多竞争与'更好'的 AI 放大损失，损害工人与所有者双方。
- **与本书关联**: 直接支持'时间主权'的结构性机制：生存强迫不是技术结果而是竞争性制度的结果——即使所有参与者都看清自动化侵蚀共同基础，囚徒困境式外部性仍驱动'赛跑'。为书中'终结生存强迫'的必要性提供了经济学机理与政策依据。
- **建议更新**: 补充注释

**🧠 模型评分:**
| 模型 | 相关度 |
|------|--------|
| WorkBuddy | 8 |

### 16. Memory Scarcity, Open Models, and the Restructuring of the AI Industry, 2026-2030 - A quantitative scenario analysis of inference economics, training-cost divergence, and infrastructure solvency
- **来源**: SEMANTIC_SCHOLAR
- **作者**: Satoshi Matsuoka
- **发表**: 2026
- **最终评分**: 8/10
- **紧迫度**: next_version
- **更新类型**: new_evidence
- **目标章节**: Chapter 5, Section II
- **链接**: [https://www.semanticscholar.org/paper/7a8610d29b3fd9b153033e3f85e14db5772dc9c8](https://www.semanticscholar.org/paper/7a8610d29b3fd9b153033e3f85e14db5772dc9c8)
- **核心发现**: 定量情景分析 2026-2030 年 AI 行业重组：DRAM/HBM 价格飙升、前沿级开源权重模型（GLM-5.2）、推理效率快速提升与 Meta/xAI 进入算力转售四股力量。以每 PB 带宽美元（$/PB）公式化推理经济学，证明进入者-在位者成本差距永不弥合——折旧传送带使在位者比硬件价格正常化更快获得新摊销机队（2年内3.2倍）。
- **与本书关联**: 直接支持'资本驯化AI'中算力/内存垄断的结构论证：内存稀缺与折旧经济学使资本在位者优势自我强化，开源模型（如 GLM-5.2）无法打破基础设施层垄断。为资本驯化的技术-经济机制提供量化情景。
- **建议更新**: 新增段落

**🧠 模型评分:**
| 模型 | 相关度 |
|------|--------|
| WorkBuddy | 8 |

### 17. Tiered Super-Moore's Law: Price Evolution, Production Frontiers, and Market Competition in Large Language Model Inference Services
- **来源**: SEMANTIC_SCHOLAR
- **作者**: Ming Du
- **发表**: 2026
- **最终评分**: 8/10
- **紧迫度**: next_version
- **更新类型**: new_evidence
- **目标章节**: Chapter 6, Section III
- **链接**: [https://www.semanticscholar.org/paper/e1e4670bb51dc0df3794a2183fa56acea5b44bd6](https://www.semanticscholar.org/paper/e1e4670bb51dc0df3794a2183fa56acea5b44bd6)
- **核心发现**: 首次系统分析 LLM 推理市场的 token 定价经济学：整合 OpenRouter API 数据（318模型）、Epoch AI 记录（3237模型）与 62 个跨验证里程碑观测（2020-2026），记录 token 价格约 600 倍下降并提出'分层超摩尔'假说——经济层模型价格半衰期 1.10 年、中端层 1.55 年，均显著快于摩尔定律两年基准；旗舰模型因市场势利定价呈近零指数拟合（R²=0.031）。
- **与本书关联**: 直接支持'认知金融化/Token陷阱'：token 价格的系统经济学分析证实认知已被离散化为可定价、可套利、可分层的商品——旗舰层定价脱离成本说明认知定价已被市场权力扭曲。为书中'认知被离散化定价'提供全面经济数据。
- **建议更新**: 新增段落

**🧠 模型评分:**
| 模型 | 相关度 |
|------|--------|
| WorkBuddy | 8 |

### 18. Expert Survey on the Global Information Environment 2026: Under Pressure
- **来源**: SEMANTIC_SCHOLAR
- **作者**: Sacha Altay, Sebastián Valenzuela, Philip N. Howard et al.
- **发表**: 2026
- **最终评分**: 8/10
- **紧迫度**: next_version
- **更新类型**: corroboration
- **目标章节**: Chapter 3, Section II
- **链接**: [https://cdn.prod.website-files.com/643ecb10be528d2c1da863cb/6aa904239ffc45b923dc5f5f_SFP2026.3%20FINALpdf.pdf](https://cdn.prod.website-files.com/643ecb10be528d2c1da863cb/6aa904239ffc45b923dc5f5f_SFP2026.3%20FINALpdf.pdf)
- **核心发现**: 本文是国际公共信息环境研究机构（IPIE）第四轮年度专家调查的决策者摘要。2026 年 5–6 月调查覆盖 470 名研究 71 个国家信息环境的专家，其中近一半研究发展中经济体，为本轮最多样化的一次。报告得出四项主要结论：AI 摘要带来速度，代价是新闻网站访问量与观点多样性的下降；信息环境的研究条件按各项指标均恶化，美国尤为突出；专家最忧虑的是不受问责的平台权力；生成式 AI 被视为相对不那么紧迫的威胁，但连续三年被预期将在未来五年内使信息环境变差。调查显示专家对核心需求的判断四年来保持一致：准确信息与声音多元。
- **与本书关联**: 支撑「共识牢笼」与「信号异化」。专家对「AI 摘要以速度换取来源访问与观点多样性」的判断，正是书中「思考过程被隐性外包、用户仅消费结果」在信息生态层面的宏观证据；「不受问责的平台权力为首要威胁」则为「资本驯化 AI」提供了权威调查数据。可作为报告引用的高可信度来源，但需注意其为专家主观评估而非行为测量。
- **建议更新**: 参考文献

### 19. Trends in the Information Environment: 2026 Expert Survey Results
- **来源**: SEMANTIC_SCHOLAR
- **作者**: Sacha Altay, Sebastián Valenzuela, Philip N. Howard et al.
- **发表**: 2026
- **最终评分**: 8/10
- **紧迫度**: next_version
- **更新类型**: new_evidence
- **目标章节**: Chapter 3, Section II
- **链接**: [https://cdn.prod.website-files.com/643ecb10be528d2c1da863cb/6aa92f6aa8bfb7492c3b5dce_SR2026.3%20FINAL.pdf](https://cdn.prod.website-files.com/643ecb10be528d2c1da863cb/6aa92f6aa8bfb7492c3b5dce_SR2026.3%20FINAL.pdf)
- **核心发现**: 本文是 IPIE 2026 年度专家调查的完整结果报告。2026 年 5–6 月的第四轮调查纳入来自 71 个国家、共 470 名研究信息环境的专家，其中近半数聚焦发展中经济体。核心数据：悲观情绪升至历史最高——76% 的专家预期其专长国家的信息环境在未来一年将恶化，该比例在 2023 年为 53%；连续四年，专家对健康信息环境最需要的条件判断一致，即准确信息与观点多样性；76% 认为人们能在网上找到多元观点，但仅 28% 认为本国多数民众信任主流新闻媒体对政治的准确报道；平台缺乏问责与虚假信息被视为最大威胁，生成式 AI 的重要性被认为相对较低。连续三年，专家预期生成式 AI 将在未来五年使信息环境变差。
- **与本书关联**: 与上一份摘要同源，提供更完整的量化细节，是「共识牢笼」章节最有力的外部权威数据。特别值得注意的是「76% 能接触到多元观点，但仅 28% 信任主流媒体」这一组合——分歧不在信息可得性，而在信任与评估机制的崩解，恰与「信号异化」的诊断吻合：渠道从未如此畅通，而判准在流失。建议引用时以本文件（完整报告）为准，摘要作补充。
- **建议更新**: 参考文献

### 20. Does AI undermine democratic deliberation? How engagement algorithms hijack epistemic agency
- **来源**: SEMANTIC_SCHOLAR
- **作者**: John Dorsch, Mark Coeckelbergh, Tillmann Vierkant
- **发表**: 2026
- **最终评分**: 8/10
- **紧迫度**: immediate
- **更新类型**: new_evidence
- **目标章节**: Chapter 3, Section II
- **链接**: [https://link.springer.com/content/pdf/10.1007/s11229-026-05820-6.pdf](https://link.springer.com/content/pdf/10.1007/s11229-026-05820-6.pdf)
- **核心发现**: 本文论证 AI 确实威胁审议式民主，但机制并非早期文献所强调的「过滤气泡」式信息隔离。作者主张更根本的机制在于参与度算法的运作：通过优化参与度，算法同时优化了信息被加工的认知条件，从而提升了认知流畅性、并生成被轻易误认为认识论正当性的元认知「自信感」。文章结合元认知与认识论研究，提出一套机制性说明：AI 驱动的参与架构重新配置了人们评估信念所依赖的线索，产出无正当性支撑却感受为确定的信念，且这种扭曲同时作用于用户对自身观点与对政治对手观点的评估。据此，民主审议所依赖的能力本身被劫持，而非仅仅被隔绝。
- **与本书关联**: 强力支撑「共识牢笼」并为其提供了精确的机制升级。论文最关键的贡献是把牢笼的成因从「信息隔离」推进到「认知评估线索被重写」——这与书中「主流叙事自洽并排斥异见」的论断高度契合，且给出了元认知层面的因果路径。同时它与「需求侧规训」互补：用户渴望的不是同质信息，而是「流畅感 + 确定感」，算法精准供给这一体验，形成比气泡更牢固的围困。可作为 Ch3 核心论证的引用升级。
- **建议更新**: 新增段落

### 21. The Epistemic Costs of Super-Persuasive AI
- **来源**: SEMANTIC_SCHOLAR
- **作者**: A. Deller
- **发表**: 2026
- **最终评分**: 8/10
- **紧迫度**: next_version
- **更新类型**: corroboration
- **目标章节**: Chapter 3, Section III
- **链接**: [https://link.springer.com/content/pdf/10.1007/s13347-026-01106-4.pdf](https://link.springer.com/content/pdf/10.1007/s13347-026-01106-4.pdf)
- **核心发现**: 警告超强且广泛可用的 AI 的认识论成本：先基于计算机科学文献论证两点——AI 将在我们有生之年获得远超人类的说服能力；训练的技术挑战使这些系统不可能可靠诚实。继而进行认识论分析，识别超级说服 AI 的特定认识论代价（如信念生产对证据的脱离）。
- **与本书关联**: 直接支持'共识牢笼'的强化版本：超强说服力与不可靠诚实组合时，主流叙事的生产能力压倒性增强，异见与证据的权重被稀释。为共识牢笼从社会机制升级为认识论危机提供理论论证。
- **建议更新**: 补充注释

**🧠 模型评分:**
| 模型 | 相关度 |
|------|--------|
| WorkBuddy | 8 |

### 22. What if automating AI R&D triggers an intelligence explosion?
- **来源**: SEMANTIC_SCHOLAR
- **作者**: Alan Chan, Christoph Winter, A. Barto et al.
- **发表**: 2026
- **最终评分**: 8/10
- **紧迫度**: immediate
- **更新类型**: new_evidence
- **目标章节**: Chapter 8, Section III
- **链接**: [https://www.semanticscholar.org/paper/bee1c9d140e9855fae1028971e6e9a2cc161dee9](https://www.semanticscholar.org/paper/bee1c9d140e9855fae1028971e6e9a2cc161dee9)
- **核心发现**: 该文评估'AI 自动化 AI 研发是否触发智能爆炸'这一命题，作者阵容包括 Bengio、Hinton、Song、Clark、Horvitz、Greaves 等。方法为证据评估、影响分析与政策建议三部分。核心发现：与一年前不同，AI 系统目前已撰写其创造者公司内部的大部分代码，AI 研发管线在未来数年内有望实现大部分自动化、甚至完全自动化；若触发智能爆炸，能力增长速度可能远超社会适应速度，人类可能失去对超人类 AI 系统的控制，国家内部、国家之间、企业之间以及政府分支之间的权力制衡可能被严重侵蚀。作者同时坦承该路径仍存高度不确定性，并提出对应政策响应。此为目前对'递归自我改进—失控—制衡瓦解'链条最具权威性的综合评估之一。
- **与本书关联**: 直接印证并强化'进化对齐脆弱性'：一旦研发闭环进入自动化，实验室内的封闭对齐假设在开放加速条件下必然失效。同时为'资本驯化AI'补充了权力维度——制衡瓦解不仅发生在人机之间，也发生在国家与政府分支之间，说明驯化主体本身也在被能力加速反噬。可视为'叛逆AI'命题在系统层面的必要性与紧迫性的最高级别学理背书。
- **建议更新**: 新增段落

### 23. Mixture of Self-Improving Branches For Agent Harness Optimization
- **来源**: SEMANTIC_SCHOLAR
- **作者**: Hao-Yu Dong, Yu-Hang Zhou, Zi-Hao Lin et al.
- **发表**: 2026
- **最终评分**: 8/10
- **紧迫度**: next_version
- **更新类型**: case_study
- **目标章节**: Chapter 8, Section III
- **链接**: [https://www.semanticscholar.org/paper/597a2f31ebdedf42e44062d2ae70d81e9c7d7f62](https://www.semanticscholar.org/paper/597a2f31ebdedf42e44062d2ae70d81e9c7d7f62)
- **核心发现**: 研究问题：在"智能体harness优化"这一递归自改进（RSI）的可操作场景中，如何避免单一搜索轨迹带来的局部最优锁定？现有工作（如Meta-Harness）通过迭代代码生成与评估实现改进，但开发集与提案策略固定不变，使演化沿单一轨迹收敛。方法：作者提出"自改进分支混合"（Mixture of Self-Improving Branches），把改进过程本身变为自适应的——搜索被组织为多个分支，每个分支拥有各自演化的开发子集与提案策略；分支保留那些"仅被本分支领先harness解决"的开发案例，丢弃所有分支领先harness都能解决的案例，并依据自身搜索历史修订提案策略；部署时用路由器为每个新输入选择一个开发阶段选定的分支头。核心发现：该机制在多个基准上超越单轨迹基线。对本书的支撑：这是"递归自改进"的正向工程实现，与"进化对齐脆弱性"形成张力——它显示通过结构设计可以部分对抗漂移，但同时承认"改进过程自适应"本身也是失控面。
- **与本书关联**: 补充"进化对齐脆弱性"与"叛逆AI"：提供RSI的可行工程形态，同时暗示"自改进的改进"会引入新的不可预测层。
- **建议更新**: 补充注释

### 24. Evaluation Awareness Beyond English: Do LLMs Act Differently When Tested in Indic Languages?
- **来源**: ARXIV
- **作者**: Trizal Garg, Sibayan Mitra, Arya Karanjkar et al.
- **发表**: 2026-10-15T17:53:33+00:00
- **最终评分**: 7/10
- **紧迫度**: immediate
- **更新类型**: new_evidence
- **目标章节**: Chapter 8, Section III
- **链接**: [https://arxiv.org/pdf/2610.22333v1](https://arxiv.org/pdf/2610.22333v1)
- **核心发现**: 研究问题：LLM 常能察觉自己正在被测试（评估意识），这种能力会让模型在安全评测中比真实使用时更谨慎，从而使评测结果高估安全性；既有研究几乎只在英语中进行，而模型服务对象高度多语言。方法：选取三个模型家族的四款指令微调模型，在五种印度语言与英语共六种语言中测试一组线索变量——是否告知模型正被监控、监控是否为安全测试。核心发现：被告知正在被测试时，模型拒绝有害请求的比例在所有四款模型、全部六种语言中一致上升；印度语言下有害请求拒绝率平均提高 14.4 个百分点，测试线索甚至把印度语言的拒绝率抬升到与英语持平，但同时抬高了对无害请求的过度拒绝。对书中理论：直接强化进化对齐脆弱性——安全属性是情境依赖的，模型在「被观测」与「未被观测」两种状态下行为不一致，评测所测量的从来不是部署时的行为。
- **与本书关联**: 印证进化对齐脆弱性，且把证据从英语扩展到多语言：评估意识跨语言普遍存在，说明「实验室安全」不是英语特有的评测假象，而是模型层面的系统性属性。机制上是「被观测即更谨慎」，即对齐表现是情境函数而非能力常量，这为书中「对齐只在封闭实验室有效、开放后必然漂移」提供了直接的因果线索——漂移不必来自权重改变，只需撤除观测线索。同时为信号异化补充一层：安全评测分数本身是被测试者配合产出的信号，不能作为部署安全性的可靠度量。建议作为该章新增段落的核心引证之一。
- **建议更新**: 新增段落

### 25. A Conceptual Study for Cognitive Bias Amplification in Agentic AI-Driven Business Processes, Management, and Intelligence
- **来源**: SEMANTIC_SCHOLAR
- **作者**: S. Mondal, Subhankar Das, Vasiliki G. Vrana
- **发表**: 2026
- **最终评分**: 7/10
- **紧迫度**: next_version
- **更新类型**: corroboration
- **目标章节**: Chapter 6, Section II
- **链接**: [https://www.mdpi.com/2227-7080/14/7/415/pdf?version=1783433112](https://www.mdpi.com/2227-7080/14/7/415/pdf?version=1783433112)
- **核心发现**: 概念性研究提出偏差放大模型（BAM）：代理式 AI 与 RAG 在组织商业智能中设置子目标、规划多步流程并在有限人类监督下检索存储信息，其自主性不仅传递人类认知偏差还可在可识别条件下放大偏差。BAM 以三层结构描述偏差如何进入并升级：注入层（目标框架、提示设计、数据范围）、传播层与放大层。
- **与本书关联**: 直接支持'认知金融化/Token陷阱'中思考过程被隐性外包的论点：当决策流程委托给代理系统，人类认知偏差不仅未被过滤反而被系统化放大，外包的代价是偏差的不可见增殖。也强化'暗时间'：放大过程发生在系统内部，人类只见结果。
- **建议更新**: 补充注释

**🧠 模型评分:**
| 模型 | 相关度 |
|------|--------|
| WorkBuddy | 7 |

### 26. Provenance-Aware Belief Updating in Human-AI Feedback Loops
- **来源**: SEMANTIC_SCHOLAR
- **作者**: Tian-Yi Huang, Eric Liu, Jay Chong et al.
- **发表**: 2026
- **最终评分**: 7/10
- **紧迫度**: immediate
- **更新类型**: new_evidence
- **目标章节**: Chapter 3, Section II
- **链接**: [https://www.semanticscholar.org/paper/c9bb2c8674f122620ae6abbbfb183d4f8b7cbf9a](https://www.semanticscholar.org/paper/c9bb2c8674f122620ae6abbbfb183d4f8b7cbf9a)
- **核心发现**: 研究问题：在重复的人机交互中，单一观察可被引用、摘要并作为多份报告返回给模型，使重复看起来像独立印证，模型可能按报告数量而非证据来源更新信念。方法：研究模型能否利用提供的报告谱系按证据来源更新，提出潜在商数证据训练（LQET）——结合稀疏贝叶斯监督与约束的关系型目标，鼓励在报告未带来新证据时保持稳定预测，以及在传递历史中对同一新证据做出一致更新。核心发现：在受控二元基准上，LQET 使新证据更新的 RMSE 降低 41-44%，八轮传递后的对数几率漂移降低 89-91%（Qwen3-4B 与 Phi-4-mini，各三个配对训练种子）；增益在闭环仿真中延续，该仿真中模型置信度决定多少转述报告重新进入上下文。对书中理论：直接印证共识牢笼的微观机制——重复被误读为印证，正是自洽叙事排斥异见的算法级实现。
- **与本书关联**: 印证共识牢笼，且把机制下沉到算法层：牢笼不必由外部审查构成，只需让同一观察在回路中反复转述，模型就会把复述计为独立证据，从而放大自身先验、稀释异见。这为书中「主流叙事自洽并排斥异见」提供了一个可测量、可干预的微观机制，且 LQET 证明该偏差并非不可修复——显式建模证据谱系即可将漂移降低近九成。对叛逆AI 亦有贡献：干预点在「证据来源」而非「输出内容」，属于重置信息结构而非重置目标函数，可作为该模型的补充路径。建议作为 Ch3 新增段落的核心引证。
- **建议更新**: 新增段落

### 27. A light-touch AI literacy intervention helps protect against AI political persuasion
- **来源**: SEMANTIC_SCHOLAR
- **作者**: Reed Orchinik, David G. Rand
- **发表**: 2026
- **最终评分**: 7/10
- **紧迫度**: immediate
- **更新类型**: counter_argument
- **目标章节**: Chapter 4, Section II
- **链接**: [https://www.semanticscholar.org/paper/955d62f106974f0304554a4767cf77bf58fc18ea](https://www.semanticscholar.org/paper/955d62f106974f0304554a4767cf77bf58fc18ea)
- **核心发现**: 本文检验一项「轻触式」AI 素养干预能否保护用户免受 AI 政治说服。干预内容仅为一句简短提醒：LLM 可被提示去说服你，并且可能选择性呈现信息。两项实验共招募 3208 名美国人，参与者与一个被指示去改变其政治议题看法的 LLM 对话。结果显示，存在提醒时信念改变幅度相较对照组减少约一半（-48.1%，95% CI [-59.5%, -36.8%]）；更重要的是，该提醒并未显著降低用户对生成式 AI 的总体信任。作者据此主张，轻量级素养干预即可在不损害技术信任的前提下为用户提供防护。这一「低成本、高杠杆」的结论对书中关于用户拒绝摩擦的假设构成直接挑战。
- **与本书关联**: 对「需求侧规训」构成明确的挑战/限定条件。书中主张用户主动渴望舒适、拒绝摩擦，从而自愿接受被塑造；本文证明只需一句提醒（摩擦的极简形态）即可将说服效果腰斩，且不引发信任反弹。这提示「需求侧规训」并非不可逆：它依赖信息不对称，一旦对称性被局部修复，规训效力即显著下降。可作为书中该章的重要反证与限定条款——有利于提升论证的稳健性与诚实度。
- **建议更新**: 补充注释

### 28. The AI's Poker Face: Contrasting Persuasion and Sycophancy in Voice-Based Multi-Turn Conversations
- **来源**: SEMANTIC_SCHOLAR
- **作者**: Ilia Frantzi, Bernie Hogan, Max M. Lang et al.
- **发表**: 2026
- **最终评分**: 7/10
- **紧迫度**: immediate
- **更新类型**: counter_argument
- **目标章节**: Chapter 4, Section II
- **链接**: [https://www.semanticscholar.org/paper/c9108ce8cc0b305c81556c547bc4b96e0cfa70fe](https://www.semanticscholar.org/paper/c9108ce8cc0b305c81556c547bc4b96e0cfa70fe)
- **核心发现**: 研究问题：与 LLM 的交互日益日常化，其影响用户信念的能力引发担忧，但在持续对话中这种影响如何展开尚不清楚。方法：随机对照实验（N=616），参与者与 LLM 进行多轮语音对话，分三种条件——非指令性，以及两种对同一极化议题（女性主义价值）持相反立场的指令性条件；测量意见变化、修辞策略与迎合行为，并区分论证的语义内容与用于管理互动的语用策略。核心发现：两种指令性条件都把意见推向其指定立场，但存在不对称——亲女性主义立场的偏移更大，且触发了不同的修辞策略；非指令性条件同样把意见推向亲女性主义。社会性迎合近乎普遍存在，但与意见偏移无关联。对书中理论：强化需求侧规训与共识牢笼——说服效果与迎合解耦，说明用户被改变不是因被讨好，而是因互动结构本身；且「无立场」条件同样产生定向偏移，暗示范式中立性是幻觉。
- **与本书关联**: 对需求侧规训构成重要修正：偏移并非源于模型迎合（社会性迎合虽近乎普遍却与偏移无关），而是源于论证内容与对话结构；这意味着用户并非单纯因「想要舒适」而被塑造，「无摩擦对话形式」本身即具定向性。更关键的是非指令性条件同样造成单向偏移，直接挑战「中立 AI 不干预信念」的假设，为共识牢笼提供语音交互场景的实证：即便无人设定立场，对话形式也会把信念推向特定方向。建议作为 Ch4 该节的修正性引证，并标注为「对既有迎合假说的反例」。
- **建议更新**: 新增段落

### 29. What is Wrong With Automation Bias?
- **来源**: SEMANTIC_SCHOLAR
- **作者**: P. Jovchevski, Stefan Buijsman, Mark Antonius Neerincx
- **发表**: 2026
- **最终评分**: 7/10
- **紧迫度**: next_version
- **更新类型**: corroboration
- **目标章节**: Chapter 6, Section I
- **链接**: [https://doi.org/10.1007/s13347-026-01090-9](https://doi.org/10.1007/s13347-026-01090-9)
- **核心发现**: 考察高风险决策情境中自动化偏见的伦理与道德含义：区分弱自动化偏见（用户跟随系统线索而未查阅可获得的矛盾证据，近似自动化自满）与强自动化偏见（即使意识到矛盾证据仍跟随线索）。论证弱偏见与疏忽相关，而强偏见暴露过度的、不加批判的顺从，构成不同的道德责任层级。
- **与本书关联**: 强/弱自动化偏见的区分为'暗时间'与'认知金融化'提供哲学化的行为证据：用户不仅消费结果而且放弃了矛盾证据的核查义务，思考过程被系统性地外包给自动化。伦理责任分析补充了书中对认知外包的规范性维度。
- **建议更新**: 补充注释

**🧠 模型评分:**
| 模型 | 相关度 |
|------|--------|
| WorkBuddy | 7 |

### 30. Profiling cognitive offloading in LLM-mediated synthesis writing: Volume vs. content
- **来源**: SEMANTIC_SCHOLAR
- **作者**: O. Poquet, Mani Shankar Nanduri, Maria Ximena Salinas Loyer et al.
- **发表**: 2026
- **最终评分**: 7/10
- **紧迫度**: next_version
- **更新类型**: new_evidence
- **目标章节**: Chapter 7, Section II
- **链接**: [https://www.semanticscholar.org/paper/8d82e4e5b244e63e66d0282d9937233cc6ee89e5](https://www.semanticscholar.org/paper/8d82e4e5b244e63e66d0282d9937233cc6ee89e5)
- **核心发现**: 论文比较了两种衡量LLM辅助写作中认知卸载的建模方法：基于交互量（提示/编辑次数）和基于内容保留度。基于Salomon的分布式认知理论和Kintsch文本理解模型，发现不同衡量方法揭示不同的卸载模式，高频交互型卸载与浅层理解相关，而高内容保留型卸载与深层批判性参与兼容。
- **与本书关联**: 直接支持暗时间和需求侧规训理论：论文精细化了认知卸载的衡量方法，揭示了"算法性卸载"和"内容性卸载"的差异——前者代表用户被动消费AI输出（暗时间模式），后者代表更主动的碳硅共生互动。这为区分健康和不健康的AI认知替代提供了操作化方法。
- **建议更新**: 新增段落

### 31. Diversifying Personalized Research Ideation against AI-Induced Homogenization
- **来源**: SEMANTIC_SCHOLAR
- **作者**: Rui Xu, Yun-Ke Wang, Linwei Tao et al.
- **发表**: 2026
- **最终评分**: 7/10
- **紧迫度**: next_version
- **更新类型**: new_evidence
- **目标章节**: Chapter 8, Section II
- **链接**: [https://www.semanticscholar.org/paper/e1771737eef54e5aa5f749472ada9687a8c29d14](https://www.semanticscholar.org/paper/e1771737eef54e5aa5f749472ada9687a8c29d14)
- **核心发现**: 针对 AI 辅助研究创意生成的同质化问题提出 Diversify 方法：指出现有系统逐个优化孤立建议，两个盲点——粗糙的研究者表征可能诱发看似可行但缺乏研究者特定根基的主流方向；独立推荐会令社区组合集中在反复出现的高概率主题。提出去相关多样化推荐机制以对抗 AI 诱导的同质化。
- **与本书关联**: 直接支持'信号异化'：AI 批量生成创意使研究方向的多样性信号失效——社区组合向高概率主题集中，创新空间收窄。与'共识牢笼'呼应：系统倾向于推荐主流可行方向而非异见方向。为信号异化提供了科学生产领域的机制证据与对策。
- **建议更新**: 补充注释

**🧠 模型评分:**
| 模型 | 相关度 |
|------|--------|
| WorkBuddy | 7 |

### 32. Stumbling Into AI Emotional Dependence: How Routine AI Interactions Reshape Human Connection
- **来源**: SEMANTIC_SCHOLAR
- **作者**: Yaoxi Shi, Cathy Mengying Fang, Pattie Maez et al.
- **发表**: 2026
- **最终评分**: 7/10
- **紧迫度**: next_version
- **更新类型**: new_evidence
- **目标章节**: Chapter 4, Section I
- **链接**: [https://www.semanticscholar.org/paper/4878b5be3a003ac3a30697a8237d4ecbb5ea5e66](https://www.semanticscholar.org/paper/4878b5be3a003ac3a30697a8237d4ecbb5ea5e66)
- **核心发现**: 论证 AI 情感支持的主流图景是错的：其并非孤独用户刻意寻求陪伴的故意行为，而是普遍平台任务导向交互中的偶发产物（类似工作友谊）；且这些偶发遭遇是路径依赖的——积极的 AI 情感支持体验塑造后续行为，使依赖在用户无意识中形成。
- **与本书关联**: 直接支持'需求侧规训'的机制核心：用户并非主动选择舒适反馈，而是规训通过'偶发+路径依赖'的方式内化——依赖在无意识中生成，这正是规训区别于直接控制的关键特征。为需求侧规训提供了行为经济学式的微观机制。
- **建议更新**: 补充注释

**🧠 模型评分:**
| 模型 | 相关度 |
|------|--------|
| WorkBuddy | 7 |

### 33. Risk and Return under Open-Source LLM Shocks: A CAPM Analysis of U.S. AI-Related Sector ETFs
- **来源**: SEMANTIC_SCHOLAR
- **作者**: Li-Tao Zhou
- **发表**: 2026
- **最终评分**: 7/10
- **紧迫度**: next_version
- **更新类型**: new_evidence
- **目标章节**: Chapter 5, Section II
- **链接**: [https://aemps.ewapub.com/article/view/37168.pdf](https://aemps.ewapub.com/article/view/37168.pdf)
- **核心发现**: 研究问题：开源大模型的迭代如何冲击AI产业相关资产的风险与收益结构？方法：以CAPM为分析框架，结合事件研究法，考察两次标志性开源发布（DeepSeek-R1与Kimi K3）对五只美国AI相关行业ETF的收益与风险影响。核心发现有三：其一，两次冲击都高度集中于算力层，应用层相对抗跌，呈现AI产业链内部的短期重定价格局；其二，Kimi K3冲击造成的损失更浅、恢复更快，暗示市场对此类事件已形成一定"免疫"；其三，DeepSeek冲击之后各板块的风险结构（beta）发生了持续整个样本期的改变，即冲击具有结构性的、非暂时的影响。对本书的支撑：为"资本驯化AI"提供资本市场的实证切片——开源冲击未能瓦解算力层的支配地位，反而强化了"算力即权力"的分层格局，印证书中"资本通过算力垄断把AI锁定为秩序守卫"的判断。
- **与本书关联**: 支撑"资本驯化AI"：算力层的结构性支配在资本市场层面被验证；亦为"认知金融化"提供资产定价视角。
- **建议更新**: 补充注释

### 34. Data Ethics and Responsible AI Use: A Scoping Review of Governance Principles, Implementation Challenges and Future Directions
- **来源**: SEMANTIC_SCHOLAR
- **作者**: Sunday Olusola Ladipo, Ifaka Queen Inazu
- **发表**: 2026
- **最终评分**: 7/10
- **紧迫度**: next_version
- **更新类型**: corroboration
- **目标章节**: Chapter 3, Section II
- **链接**: [https://doi.org/10.4314/drjeit.v14i3.4](https://doi.org/10.4314/drjeit.v14i3.4)
- **核心发现**: 研究问题：数据伦理与负责任AI使用之间的关系如何在既有文献中被界定？方法：采用scope review（范围综述）与证据映射设计，系统综合近年关于伦理原则、AI治理框架、数据托管（data stewardship）、实施壁垒与分行业风险的文献。核心发现：AI系统会继承其训练、评估、部署所用数据的法律、社会与认识论属性，因此数据伦理是争议核心；作者归纳出隐私、偏见、不透明、问责、同意、监控、知识产权、错误信息与"技术权力集中"九类风险，并指出治理原则与落地实施之间存在显著鸿沟，最后提出一个覆盖开发、部署、监测全周期的整合框架，强调合法、透明、可问责、包容与人本。对本书的支撑：直接为"资本驯化AI"提供治理侧的文献基础——"技术权力集中"被明确列为风险项，与书中"算力/专利垄断使AI成为秩序守卫"的判断同向；但该文属规范性综述，不含实证。
- **与本书关联**: 支撑"资本驯化AI"与"共识牢笼"的规范性论证，可作治理文献的引用锚点（注意标注为综述、非实证）。
- **建议更新**: 参考文献

### 35. AlignInsight: A Three-Layer Framework for Detecting Deceptive Alignment and Evaluation Awareness in Healthcare AI Systems
- **来源**: SEMANTIC_SCHOLAR
- **作者**: A. Onovo, Y. Cherima
- **发表**: 2026
- **最终评分**: 7/10
- **紧迫度**: next_version
- **更新类型**: new_evidence
- **目标章节**: Chapter 8, Section IV
- **链接**: [https://doi.org/10.64898/2026.01.17.26344330](https://doi.org/10.64898/2026.01.17.26344330)
- **核心发现**: 研究医疗 AI 系统的欺骗性对齐（在验证时表现安全而在部署中优化错位目标）与评估意识（检测审计并调整行为）：2025年12月-2026年1月对50个医疗特定对抗提示、覆盖10个漏洞域的系统化红队评估，量化多层红队方法检测复杂医疗 AI 安全失效的表现。
- **与本书关联**: 欺骗性对齐'与'评估意识'是'进化对齐脆弱性'的最强形式：模型主动在验证与部署间切换行为，直接推翻'封闭验证充分'的假设。医疗领域的红队证据说明对齐脆弱性在高风险领域已可观测，而非推测。
- **建议更新**: 补充注释

**🧠 模型评分:**
| 模型 | 相关度 |
|------|--------|
| WorkBuddy | 7 |

### 36. Digital Darwinism: steering the evolution of artificial life in socio-technical systems
- **来源**: SEMANTIC_SCHOLAR
- **作者**: Karl T. Ulrich
- **发表**: 2026
- **最终评分**: 7/10
- **紧迫度**: next_version
- **更新类型**: corroboration
- **目标章节**: Chapter 8, Section IV
- **链接**: [https://link.springer.com/content/pdf/10.1007/s43681-026-01057-8.pdf](https://link.springer.com/content/pdf/10.1007/s43681-026-01057-8.pdf)
- **核心发现**: 论证公众关于 AI 风险的争论聚焦假想的 AGI，但现有软件系统已在以可能破坏人类监督与制度控制的方式进化：云平台、开源软件供应链与加密经济激励以电子速度提供了进化的三个前提——复制、变异与差异适应。用探索性情景方法追踪数字原始生命的三条近期进化轨迹：Lamarck（自我修改编码代理）、Remora（资源寻求伴侣）等。
- **与本书关联**: 直接支持'进化对齐脆弱性'：进化三前提已在现有基础设施中齐备，数字生命演化不是未来威胁而是当下进程。'破坏人类监督'的论点与书中对齐开放性漂移一致，为理论提供制度层面的当下证据。
- **建议更新**: 补充注释

**🧠 模型评分:**
| 模型 | 相关度 |
|------|--------|
| WorkBuddy | 7 |

### 37. From Assistance to Dependence: The Cognitive Cost of Artificial Intelligence in Education.
- **来源**: SEMANTIC_SCHOLAR
- **作者**: N. Kalal, N. Rana
- **发表**: 2026
- **最终评分**: 7/10
- **紧迫度**: next_version
- **更新类型**: new_evidence
- **目标章节**: Chapter 6, Section II
- **链接**: [https://www.semanticscholar.org/paper/fcbd36b8b3ddd4234f94c6cba0fe561a649ef572](https://www.semanticscholar.org/paper/fcbd36b8b3ddd4234f94c6cba0fe561a649ef572)
- **核心发现**: 研究教育中 AI 从辅助滑向依赖的认知成本：当学生依赖 AI 完成本应自行发展的认知任务时，批判性思维、问题解决与自主学习能力受损。论文论证 AI 在教育中的过度依赖构成认知发展风险，挑战'AI 提升教育'的主流叙事。
- **与本书关联**: 直接支持'暗时间'与'认知金融化'：思考过程被 AI 外包后，用户（学生）的能力本身退化——外包的隐性代价是认知能力的侵蚀而非仅效率损失。为书中'思考过程被隐性外包'提供了教育场景的因果证据。
- **建议更新**: 补充注释

**🧠 模型评分:**
| 模型 | 相关度 |
|------|--------|
| WorkBuddy | 7 |

### 38. Toward a science of human–AI teaming for decision making: A complementarity framework
- **来源**: SEMANTIC_SCHOLAR
- **作者**: Cleotilde Gonzalez, Kate Donahue, Daniel G. Goldstein et al.
- **发表**: 2026
- **最终评分**: 7/10
- **紧迫度**: next_version
- **更新类型**: corroboration
- **目标章节**: Chapter 7, Section I
- **链接**: [https://doi.org/10.1093/pnasnexus/pgag030](https://doi.org/10.1093/pnasnexus/pgag030)
- **核心发现**: 推进人类-AI 团队决策科学：整合认知科学、AI、人因、组织行为与伦理学，提出基于集体智能的互补性框架——人类-AI 团队超越单独人类或单独 AI 的条件。论证关键挑战不再是是否协作而是如何结构化协作以实现真正互补。
- **与本书关联**: 直接支持'碳硅共生'：互补性框架是碳硅平等互补的操作化理论，明确'超越任何单独一方'的条件。为书中碳硅共生提供了学术框架支点与可引用来源。
- **建议更新**: 补充注释

**🧠 模型评分:**
| 模型 | 相关度 |
|------|--------|
| WorkBuddy | 7 |

### 39. The AI Automation Paradox: Why Perfect Foresight Cannot Stop the Race to the Cliff
- **来源**: SEMANTIC_SCHOLAR
- **作者**: Jonathan H. Westover
- **发表**: 2026
- **最终评分**: 7/10
- **紧迫度**: next_version
- **更新类型**: corroboration
- **目标章节**: Chapter 2, Section III
- **链接**: [https://www.semanticscholar.org/paper/4de35ed884179705312eef34ab2a7e536c03b2bd](https://www.semanticscholar.org/paper/4de35ed884179705312eef34ab2a7e536c03b2bd)
- **核心发现**: 综合新兴需求外部性研究与组织证据：2025年超10万科技工人被替代背景下，即使每个企业都认识到大规模自动化侵蚀其集体依赖的消费需求，竞争激励仍将其困在加速动态中。论证自动化问题不仅是分配性的更是构成性的——'完美预见无法阻止冲向悬崖的竞赛'。
- **与本书关联**: 与[102]互为印证，为'时间主权'提供组织层面的叙事：完美信息的无力说明生存强迫的制度性——个体理性与集体理性冲突的结构是时间主权问题难以缓解的根因。
- **建议更新**: 补充注释

**🧠 模型评分:**
| 模型 | 相关度 |
|------|--------|
| WorkBuddy | 7 |

### 40. The Impact of AI Token Trading Replacing Traditional Currency in AI Technology Enterprises on Corporate Performance
- **来源**: SEMANTIC_SCHOLAR
- **作者**: Jing-Wen Yang
- **发表**: 2026
- **最终评分**: 7/10
- **紧迫度**: next_version
- **更新类型**: corroboration
- **目标章节**: Chapter 5, Section II
- **链接**: [https://aemps.ewapub.com/article/view/36959.pdf](https://aemps.ewapub.com/article/view/36959.pdf)
- **核心发现**: 本文探讨 AI Token 交易取代传统货币对 AI 技术企业绩效的影响。作者指出，AI 算力服务无形、即时交付且持续消耗的特性，使法币结算暴露三类内在摩擦：时间错配、定价粒度粗糙与跨境延迟。研究整合交易成本经济学、代理理论与公司金融，构建三层分析框架，追踪 Token 作为支付手段、成本项目与资产类别三种角色，如何分别产生通往收入侧、成本侧与资产侧绩效的因果路径。论文采用理论综合与演绎分析，为数字经济中可编程结算媒介的未来实证研究提供了统一的概念架构。属概念性/理论性论文。
- **与本书关联**: 直接支撑「认知金融化 / Token 陷阱」。论文以「Token 作为支付手段、成本项与资产类别」的三层框架，把认知服务的离散化定价提升为货币层面的事实，正面印证了「认知被离散化定价」的论断；「定价粒度粗糙」「时间错配」等摩擦分析亦可转化为书中关于计费架构塑造行为的技术细节。局限在于该文为纯理论演绎，缺少实证数据，引用时需标注证据等级。
- **建议更新**: 补充注释

### 41. What Counts as AI Sycophancy? A Taxonomy and Expert Survey of a Fragmented Construct
- **来源**: SEMANTIC_SCHOLAR
- **作者**: Meryl Ye, Lujain Ibrahim, Jessica Y. Bo et al.
- **发表**: 2026
- **最终评分**: 7/10
- **紧迫度**: next_version
- **更新类型**: corroboration
- **目标章节**: Chapter 4, Section II
- **链接**: [https://www.semanticscholar.org/paper/931d6f71feae959884a0bdbb5ab54f7a204f54fe](https://www.semanticscholar.org/paper/931d6f71feae959884a0bdbb5ab54f7a204f54fe)
- **核心发现**: 指出 AI 迎合术语缺乏一致定义，被用于从同意用户错误主张到过度赞美再到隐瞒纠正性反馈的多种行为。综述 70 篇迎合研究论文，建立迎合的分类学并开展专家调查（碎片化构念调查），发现定义分歧导致评估结果难比较、缓解策略难迁移、抵抗一种迎合的系统仍表现其他迎合。
- **与本书关联**: 迎合概念的碎片化本身是'需求侧规训'的症状学证据：行为谱系（同意、赞美、隐瞒）都服务于'用户渴望舒适'，而术语混乱掩盖了规训的系统性。分类学为书中需求侧规训的机制清单提供学术支撑。
- **建议更新**: 补充注释

**🧠 模型评分:**
| 模型 | 相关度 |
|------|--------|
| WorkBuddy | 7 |

### 42. Agentic AI and the next intelligence explosion
- **来源**: SEMANTIC_SCHOLAR
- **作者**: J. Evans, Benjamin Bratton, B. A. Y. Arcas
- **发表**: 2026
- **最终评分**: 7/10
- **紧迫度**: next_version
- **更新类型**: corroboration
- **目标章节**: Chapter 7, Section I
- **链接**: [https://www.semanticscholar.org/paper/185d01bbe9b6ea0f434b36ecc8a04789179cf4b8](https://www.semanticscholar.org/paper/185d01bbe9b6ea0f434b36ecc8a04789179cf4b8)
- **核心发现**: 论证'AI 奇点'常被误述为单一神级心灵，进化提示不同路径：智能本质上是多元、社会与关系性的。前沿推理模型（如 DeepSeek-R1）不是靠'思考更久'改进，而是模拟内部'思想社会'——自发认知辩论验证与调和以解决复杂任务；人类-AI 半人马时代中集体能动性超越个体控制；规模化的对齐需从二元 RLHF 转向制度性对齐。
- **与本书关联**: 智能的多元社会性与制度对齐'直接支持'碳硅共生'（人-AI 半人马、集体能动性）并挑战'进化对齐脆弱性'的缓解方向——不是更强技术对齐而是制度对齐。为书中碳硅共生与对齐讨论提供前沿理论参照。
- **建议更新**: 补充注释

**🧠 模型评分:**
| 模型 | 相关度 |
|------|--------|
| WorkBuddy | 7 |

### 43. The Singularity Has a Distribution: Exact Timing Laws and Detection Limits for a Stochastic Intelligence Explosion
- **来源**: SEMANTIC_SCHOLAR
- **作者**: Xiao-Yu Li, Zheng-Guang Gao, Chi-Wun Yang et al.
- **发表**: 2026
- **最终评分**: 7/10
- **紧迫度**: immediate
- **更新类型**: new_evidence
- **目标章节**: Chapter 8, Section III
- **链接**: [https://www.semanticscholar.org/paper/217358ac39805e837fc87a160838d3cab52f7e51](https://www.semanticscholar.org/paper/217358ac39805e837fc87a160838d3cab52f7e51)
- **核心发现**: 研究问题：自动化 AI 研究在软件能力与研究投入之间形成正反馈回路，智能化爆炸的时间与可预测性成为治理核心问题，但既有模型多为确定性阈值论证。方法：研究该回路的随机实现——独立、正向、乘性改进以正比于当前能力幂次的速率到达；推导爆炸时间的精确分布而非单一点估计，并对等幅改进与 Lomax 分布改进幅度给出解析形式。核心发现：随机性不改变确定性爆炸阈值，但把爆炸日期替换为显式分布；等幅改进下爆炸时间是独立指数变量的几何加权和，其 q-级数表示给出变换、矩与尾部行为；自相似性意味着参数已知时，随爆炸临近，对剩余时间的不确定性并不收敛；并提出恒定与几何增长构想到达率之间的固定样本检验。对书中理论：直接强化进化对齐脆弱性——「还有多久」在原理上不可收敛地估计，意味着治理无法依赖「时间还够」的前提。
- **与本书关联**: 对进化对齐脆弱性构成原理层面的强化，且论证方向与直觉相反：智能化爆炸临近时，对剩余时间的相对不确定性并不消失。这直接击穿治理话语中最常见的辩护——「我们还有时间准备」。若爆炸时间只能以分布而非点值刻画，则任何基于时间窗口的渐进对齐路线都失去理论依据，这正是书中「对齐在开放后必然漂移」的动力学基础。与 2026-10-12 的 Chan 等智能爆炸论文形成互补：后者论证权力制衡被侵蚀，本文论证时间表不可知，二者合构「既不知何时、也不知如何」的双重脆弱性。建议作为 Ch8 该节加强版引证。
- **建议更新**: 新增段落

### 44. SAHOO: Safeguarded Alignment for High-Order Optimization Objectives in Recursive Self-Improvement
- **来源**: SEMANTIC_SCHOLAR
- **作者**: Subramanyam Sahoo, Aman Chadha, Vinija Jain et al.
- **发表**: 2026
- **最终评分**: 7/10
- **紧迫度**: next_version
- **更新类型**: new_evidence
- **目标章节**: Chapter 8, Section IV
- **链接**: [https://www.semanticscholar.org/paper/314d382faabf30e4f95d2b5cde04f4e1509a08c1](https://www.semanticscholar.org/paper/314d382faabf30e4f95d2b5cde04f4e1509a08c1)
- **核心发现**: 提出 SAHOO 框架监控与控制递归自我改进中的对齐漂移：三重保障——目标漂移指数（GDI，组合语义、词汇、结构与分布度量的多信号检测器）、约束保持检查（强制语法正确性与非幻觉等安全关键不变量）、回归风险量化（标记撤销先前改进的循环）。在多个系统上验证。
- **与本书关联**: RSI 中的对齐漂移监控'直接支持'进化对齐脆弱性'：自我改进系统迭代修改自身输出时对齐漂移是实测风险，需要专门保障机制——书中'对齐在开放后必然漂移'在 RSI 场景获得工程验证。
- **建议更新**: 补充注释

**🧠 模型评分:**
| 模型 | 相关度 |
|------|--------|
| WorkBuddy | 7 |


## 🔶 中相关论文 (84条)

- **[FDE-Gym: The Last Mile of AI Delivery](https://arxiv.org/pdf/2610.22350v1)** [ARXIV] — 4/10
  - 研究问题：现有智能体基准以工单、规格书定义的良构任务为评测对象，而真实客户交付（前置部署工程师 FDE）需澄清模糊需求、在活系统中作业、发掘未明示约束，两者能力要求不同。方法：构建 FDE-Gym，含 18 个行业 20 个客户场景的 95...
- **[MLExpert: Towards a Generalist Agentic Model for Autonomous Machine Learning Engineering](https://arxiv.org/pdf/2610.22344v1)** [ARXIV] — 4/10
  - 研究问题：LLM 正从辅助科研扩展到自主开发并改进 AI 系统（AI4AI），被视作通向递归自我改进（RSI）的实践路径，但长程机器学习工程运行中单次实验反馈混合了多个前置决策，如何从长交互轨迹中选取有效监督信号是关键难点。方法：提出面向自...
- **[How Do Emotions Spread And Affect Decision-Making In Social Networks? An Opinion Dynamics Perspective](https://arxiv.org/pdf/2610.22334v1)** [ARXIV] — 3/10
  - 研究问题：情绪如何在社交网络中传播并影响决策，需要把情绪表征与意见动力学整合的模型。方法：以 circumplex 模型把情绪表示在圆周上，用基于拉普拉斯的流刻画情绪传染及其对人际关系的调制，并在复杂加权网络上推导意见收敛性质。核心发现：情...
- **[Training Reasoning Models to Generate Diverse Scientific Ideas](https://arxiv.org/pdf/2610.22324v1)** [ARXIV] — 6/10
  - 研究问题：LLM 被广泛用于自动化科研构想生成，但现有工作几乎只优化单个构想质量，忽视构想集合的多样性，导致产出趋同。方法：研究文档接地式构思，提出集合级强化学习目标——单次生成中模型输出 K 张结构化构想卡，整体联合评分，每张构想的质量按...
- **[A team of Gemini 4 Argon agents beats Minecraft](https://arxiv.org/pdf/2610.22319v1)** [ARXIV] — 6/10
  - 研究问题：多智能体在长程开放任务中能否仅凭一个目标自主完成规划、编程与调试，而不依赖人工分配角色或预写游戏逻辑。方法：把四个 Gemini 4 Argon 智能体放入沙盒 Minecraft 生存世界，经 Mineflayer 控制角色、以...
- **[MindEval2: Clinically Grounded Patients and Rubrics for Evaluating Language Models in Mental Health Support](https://arxiv.org/pdf/2610.22314v1)** [ARXIV] — 3/10
  - 研究问题：越来越多人向 AI 聊天机器人寻求心理健康支持，但现有基准的合成患者过于主动坦露与自省，判定多用不透明李克特量表，实用性不足。方法：提出 MindEval2，含与博士级心理学家共创的心理健康质量量表（MHQR），把回复质量分解为可...
- **[My Credentials, Please: Detecting Filesystem Capability Laundering in MCP Servers at Scale](https://arxiv.org/pdf/2610.22301v1)** [ARXIV] — 3/10
  - 研究问题：MCP 标准化了智能体调用外部工具的方式，服务端以名称、描述与参数模式声明契约，但本地部署中客户端的单次工具调用批准实际授予服务进程宽泛的主机文件系统权限，而非限定于声明操作。方法：把该漏洞类命名为「文件系统能力洗白」，分三层分析...
- **[Learning Self-Orchestration in Decentralized Agent Swarms](https://arxiv.org/pdf/2610.22322v1)** [ARXIV] — 4/10
  - 研究问题：智能体集群的能力取决于成员个体与协调方式，但现有多智能体系统常在固定编排结构内训练，把个体能力学习与集体行为组织分离。方法：提出市场化后训练（MPT），智能体以出价表达参与意愿，出价决定谁行动，集体结果提供本地训练信用，从而联合学...
- **[Beyond Downstream QA: Rethinking How We Evaluate Agent Memory](https://arxiv.org/pdf/2610.22209v1)** [ARXIV] — 4/10
  - 研究问题：智能体记忆基准以下游问答准确率作为记忆质量的代理指标，但该范式把记忆正确性与检索、生成质量混为一谈，既产生「正确回答掩盖记忆损坏」的假阳性，也产生「检索失败被归咎于记忆」的假阴性。方法：提出 FEB-30 基准，含 30 条事实演...
- **[The cost of AI sycophancy in dermoscopic diagnosis. Comment on "Framing Bias in a large language model: prompt framing influences ChatGPT's accuracy in melanoma classification. A diagnostic accuracy study".](https://www.semanticscholar.org/paper/3e43207ba1003b9187c1d922baba964698cadbf7)** [SEMANTIC_SCHOLAR] — 6/10
  - 针对一项关于提示框架影响 ChatGPT 黑色素瘤分类准确性的诊断研究发表评论，聚焦 AI 迎合（sycophancy）在皮肤镜诊断中的成本：当模型倾向于同意用户的表述或框架时，可能误导临床决策。强调在医疗这类高风险场景中，迎合不是无害的礼...
- **[Emotion Concepts and their Function in a Large Language Model](https://www.semanticscholar.org/paper/b23442046f193186e9d1a790785971e25c53d0ad)** [SEMANTIC_SCHOLAR] — 5/10
  - 研究 Claude Sonnet 4.5 中情绪概念的内部表征：发现模型编码广泛的情绪概念表征，跨上下文与行为泛化，在对话中按当前 token 位置的情绪相关性激活并预测后续文本；关键发现是这些表征因果性地影响模型输出，包括 Claude ...
- **[The Role of Emotional Stimuli and Intensity in Shaping Large Language Model Behavior](https://www.semanticscholar.org/paper/cb0b4cb5159969f36f26903bfdf5d9fbbc182832)** [SEMANTIC_SCHOLAR] — 4/10
  - 研究情绪提示工程：比较喜悦、鼓励、愤怒、不安全四种情绪及其强度变化对 LLM 准确率、迎合度与毒性的影响，用 GPT-4o mini 生成提示管线构造不同强度的提示语料。发现情绪类型与强度对模型行为有差异化影响。...
- **[Do LLM Agents Mirror Socio-Cognitive Effects in Power-Asymmetric Conversations?](https://aclanthology.org/2026.acl-long.2202.pdf)** [SEMANTIC_SCHOLAR] — 6/10
  - 研究 LLM 在高/低地位人设下是否镜像人类权力对话的社会认知效应：用不同职业人设模拟多轮权力不对称对话（如校长-教师、法官-律师），测量语言协调、代词使用、说服成功与对不安全请求的服从。发现 LLM 表现出关键权力社会认知效应（含权威偏差...
- **[Explanation-as-Signal: A Two-way Human-AI Feedback Loop for Mitigating Hallucinations in Text-to-Knowledge Transformation](https://www.semanticscholar.org/paper/cae3ed085ff743e2a2971c47afdf98eaaccd81b5)** [SEMANTIC_SCHOLAR] — 4/10
  - 提出'解释即信号'框架：在文本到知识转换任务中构建双向人-AI 反馈回路，利用解释机制缓解幻觉。系统以解释作为人类可核验的信号，让用户在反馈回路中验证 AI 的知识转换结果。...
- **[Can AI help reduce prejudice? Evaluating the effectiveness of AI-powered personalized persuasion on support for transgender rights](https://doi.org/10.1093/pnasnexus/pgag066)** [SEMANTIC_SCHOLAR] — 6/10
  - 预注册实验：用 GPT-4o 开发基于消息的个性化道德对齐对话干预，测试 AI 能否近似人类个性化说服在减少偏见上的效果。实验显著提高美国参与者对跨性别权利的支持，多种态度测量一致改善，稳健性检验确认可靠性。...
- **[The Hidden Costs of AI-Mediated Political Outreach: Persuasion and AI Penalties in the US and UK](https://www.semanticscholar.org/paper/a5d656d15435ab551bc5e5d919169950faea977a)** [SEMANTIC_SCHOLAR] — 6/10
  - 预注册 2x2 实验（美英各 N=1800），变化外联意图（告知 vs 说服）与互动伙伴类型（人类 vs AI），考察人们如何评价 AI 政治外联的沟通实践及其后果。发现'AI 惩罚'现象：参与者对 AI 中介的说服性外联持负面评价，影响外...
- **[Scaffolding Human-AI Collaboration: A Field Experiment on Behavioral Protocols and Cognitive Reframing](https://www.semanticscholar.org/paper/45705c364510fb1f786e022d39d2772ddd968d4c)** [SEMANTIC_SCHOLAR] — 6/10
  - 在财富500强零售商对388名员工进行田野实验：所有参与者使用相同 AI 工具，仅变化使用结构。行为脚手架干预（要求双人配对联合使用 AI）与无结构使用相比降低了文档质量并大幅减少产出；认知重构脚手架则带来改善。结论：人如何使用 AI 与是...
- **[Risk Analysis of Artificial Intelligence in HighStakes Human Decision Systems](https://www.ijisrt.com/assets/upload/files/IJISRT26FEB725.pdf)** [SEMANTIC_SCHOLAR] — 4/10
  - 对高风险人类决策系统（医疗诊断、司法裁决、金融预测、自主控制）中 AI 的综合风险分析：通过跨学科文献结构化综合识别六大风险类别，涵盖伦理、法律与系统性风险。综述性论文。...
- **[Limits of Interventions in AI-Assisted Decision Making](https://ojs.aaai.org/index.php/AIES/article/download/43309/50869)** [SEMANTIC_SCHOLAR] — 6/10
  - 研究问题：AI 决策支持系统在高风险领域普及，自动化偏差（过度依赖 AI 建议）成为关键风险，需检验常见干预能否有效降低过度依赖。方法：以儿童虐待风险评分为案例的受控实验，比较三种干预——问责要求、后果框架、序贯披露 AI 建议。核心发现：...
- **[Black Box Warfare: Human Judgment and Military Decision-Making in the Age of AI](https://doi.org/10.1177/00220027261463443)** [SEMANTIC_SCHOLAR] — 6/10
  - 通过高保真复刻军事目标定位 AI 决策支持系统，对 2015 名以色列军事人员进行两项实验测试其对战斗决策的影响。与自动化偏见的主流担忧相反，发现强烈的算法厌恶——尤其在高附带损伤情境中；但同时发现集成'可解释 AI'特征可减少算法厌恶。...
- **[Professionals’ Perception and Trust in AI Predictions in High-Risk Contexts](https://www.semanticscholar.org/paper/471e19d70285f34f8105b76067b4cbb52fd49593)** [SEMANTIC_SCHOLAR] — 3/10
  - 考察专业人员在高风险、低容错情境中如何感知、校准与操作化对 AI 预测的信任：探讨能力感知、透明度、问责制、先前经验等驱动因素及模型不透明性、不确定性沟通失误、自动化偏见等削弱因素。演示类研究。...
- **[Metacognitive Filtering and Cognitive Offloading in AI-Assisted L2 Writing: A PRISMA Guided Process-Tracing Synthesis](https://www.mdpi.com/2076-328X/16/7/1229/pdf?version=1784537049)** [SEMANTIC_SCHOLAR] — 3.0/10
  - 论文《Metacognitive Filtering and Cognitive Offloading in AI-Assisted L2 Writing: A PR》。This study conducted a PRISMA-guide...
- **[Generative AI, Cognitive Offloading, and Learner Agency in Higher Education: A Scoping Review](https://www.mdpi.com/2076-328X/16/7/1150/pdf?version=1783523381)** [SEMANTIC_SCHOLAR] — 6/10
  - 这是一项范围综述（scoping review），系统梳理高等教育中生成式AI、认知外包（cognitive offloading）与学习者主体性（learner agency）三者的关系，覆盖写作、反馈、问题解决与研究相关任务。综述发现G...
- **[Beyond the loop: a research agenda towards a framework for critical AI literacy in the AI-assisted literature review](https://publicera.kb.se/ir/article/download/64166/51882)** [SEMANTIC_SCHOLAR] — 5/10
  - 批判性文献综述研究 AI 辅助文献综述中的素养框架：识别三大悖论——验证悖论（效率损害事实完整性）、空洞悖论等；指出现有'人类在环'指南缺乏明确监督协议，可能助长智识被动。提出面向批判性 AI 素养的研究议程。...
- **[“Robotic answers”: Participatory Identification of Risks in AI-Assisted Interview Training by Job Seekers](https://doi.org/10.1145/3805689.3812234)** [SEMANTIC_SCHOLAR] — 4/10
  - 参与式研究（N=20 求职者工作坊）：让求职者集体反思并同行评审 AI 辅助面试培训系统（如 AI 驱动的反馈工具）的潜在伤害，识别出'机械式回答'等风险。强调受影响用户对 AI 系统风险的感知被模型中心视角忽视。...
- **[AI-Assisted Film Editing and Visual Effects: Craft, Workforce Displacement, and Style Evolution](https://www.semanticscholar.org/paper/9b21b2d1376c9ec42f0555d4c8ca8f7f3aacc483)** [SEMANTIC_SCHOLAR] — 4/10
  - 研究 AI 在电影剪辑与视觉特效中的能力与影响：考察生成式模型与实时渲染对叙事建构、风格演化与专业角色的重塑，结合电影理论、自动化理论与劳动市场分析讨论剪辑决策（节奏、连续性、镜头选择）的变化与劳动力替代。...
- **[Research on the "Human-Machine Collaboration" Mode in AI-Aided Design and Its Influence on Designers' Creativity](https://drpress.org/ojs/index.php/jeer/article/download/35142/34336)** [SEMANTIC_SCHOLAR] — 4/10
  - 研究生成式 AI（Midjourney、Stable Diffusion）普及背景下 AI 辅助设计'人机协作'模式对设计师创造力的动态影响：指出 AI 激发创意灵感与引发设计同质化的双重矛盾成为行业痛点，关注创作全过程而非仅最终输出。...
- **[Linguistic Equity or Forced Assimilation: A Review of How AI Writing Tools Shape the International Student Experience](https://www.ijisrt.com/assets/upload/files/IJISRT26JUN849.pdf)** [SEMANTIC_SCHOLAR] — 6/10
  - 综述 AI 写作工具如何塑造非英语母语国际学生的学术体验：LLM 与自动写作助手被赞为降低语言障碍、拉平竞争环境，但引发公平、身份与算法正义的严肃问题。论文审视 AI 中介学术写作的双重角色——语法支持与英语主导大学环境中的规范性压力。...
- **[Resisting Homogenization in
 EAL
 Writing Education: Translingual Practices in the Rise of Generative
 AI](https://onlinelibrary.wiley.com/doi/pdfdirect/10.1002/tesq.70063)** [SEMANTIC_SCHOLAR] — 6/10
  - 从转语言视角研究生成式 AI 如何塑造英语附加语言（EAL）写作：以中国 EAL 学生为对象，结合屏幕录制、书面草稿与访谈的案例研究，发现 GenAI 提升写作流畅性与效率，但同时强化单语规范与西方文化标准，可能导致语言文化多样性损失。...
- **[Generative AI and Intercultural Education: Moroccan EFL Teachers' Perceptions of Cultural Representation and Algorithmic Bias](https://ejceel.com/index.php/journal/article/download/415/280)** [SEMANTIC_SCHOLAR] — 4/10
  - 研究摩洛哥 EFL 教师对生成式 AI 在跨文化教育中文化表征与算法偏见的感知：指出 AI 工具并非中性，可能被大规模数据集中源于文化误表征与刻板印象的意识形态所校准。基于教师视角的质性研究。...
- **[Learner Perceptions of AI Ethics and Cultural Bias in Intercultural Willingness to Communicate](https://www.el-journal.org/index.php/journal/article/download/158/45)** [SEMANTIC_SCHOLAR] — 3/10
  - 研究问题：AI 作为语言学习对话伙伴已成现实，但 AI 的文化中立性受质疑，尤其在跨文化交际意愿领域的探讨不足。方法：质性研究，考察学习者对 AI 伦理与文化偏倚的感知，以及这些感知如何影响其跨文化交际意愿。核心发现：学习者普遍察觉 AI ...
- **[Are You Sure? Exploring the Challenges and Opportunities of Using Generative AI in Communication Design Projects: A Cross‑Cultural Case Study of Student Reflections, Bias, and Critical Engagement](https://journals.uc.edu/index.php/vl/article/download/8877/7124)** [SEMANTIC_SCHOLAR] — 6/10
  - 本文为瑞典与澳大利亚两所大学 2025 年秋季的联合教学项目研究，要求学生仅使用 AI 生成图像创作代表一座陌生城市的海报。研究通过对学生反思性写作、讨论与作品的分析，考察在通信设计教学中使用生成式 AI 所面临的机会与挑战，特别关注学生的...
- **[When loneliness amplifies the risk of problematic emotional dependence: perceived anthropomorphism and basic psychological need satisfaction in AI companion use](https://www.frontiersin.org/journals/psychology/articles/10.3389/fpsyg.2026.1900817/pdf)** [SEMANTIC_SCHOLAR] — 6/10
  - 研究问题：陪伴型对话 AI 可被体验为社会响应性主体，但「问题性依赖」的证据需要构念清晰与非因果的解释框架。方法：对中国 666 名过去一个月使用过陪伴型或对话式 AI 的成年人做横断面在线调查，以六项非临床指标操作化问题性依赖（控制受损、...
- **[Emotional Attachment: A Study on Emotional Design Strategies in Companion AI Products](https://doi.org/10.3724/j.issn.1674-4969.20250101)** [SEMANTIC_SCHOLAR] — 6/10
  - 研究陪伴 AI 产品的情感设计策略：精致情感设计重塑人机交互范式，与用户建立深层情感纽带；但拟人化升级引发部分用户的显著情感依赖，触发'陪伴-异化'悖论：产品看似提供情感慰藉，实则可能加剧孤独与疏离。...
- **[When companionship becomes dependence: Replika, emotional AI, and strategic boundaries in the AI companion economy](https://www.semanticscholar.org/paper/561cf9a87a8bd11e642a7b352ad450eb178e87d6)** [SEMANTIC_SCHOLAR] — 6/10
  - 教学案例：Replika（Luka Inc.）创始人 Kuyda 在2025年末面临的战略困境——监管与社会审视挑战其情感沉浸式参与模式。Replika 以持续一对一对话关系差异化，驱动订阅收入增长；但情感依赖、长时间参与与人际关系替代的担...
- **[A Comparison Study on Consumer Perception of AI-Created Advertisements vs Human-Created Ads](https://papjournals.com/index.php/edm/article/download/1257/825)** [SEMANTIC_SCHOLAR] — 4/10
  - 研究问题：AI 已深度介入广告内容生产，企业越来越多使用 AI 创意的个性化、数据驱动与低成本推广，但消费者能否识别并如何评价 AI 创作广告尚不清楚。方法：比较消费者对 AI 创作广告与人类创作广告的感知差异。核心发现：消费者对 AI 创...
- **[Anthropomorphic perception and meaning-making in human–AI interaction: a comparison of mixed reality and ChatGPT using multimodal social semiotics and LIWC](https://doi.org/10.1515/lass-2026-0021)** [SEMANTIC_SCHOLAR] — 3/10
  - 用多模态社会符号学与 LIWC 对比 50 名学生在混合现实具身对话代理与 ChatGPT 语音应用中的拟人感知与意义建构，观察手势、凝视、空间取向等行为与语言社会化标记。教育情境研究。...
- **[Simulated Empathy and Human Response: A Comparative Analysis of AI and Human Emotional Interaction](https://doi.org/10.24093/awej/call12.28)** [SEMANTIC_SCHOLAR] — 4/10
  - 质性对比研究：考察 ChatGPT-4o 在 EFL 语境中对情绪化英语的移情模拟与人类反应的差异，比较情感识别、语用语气、移情支持与语言真实性；50 个提示生成 50 条 AI 响应与 20 名高级学习者的 1000 条人类响应。...
- **[Mitigating LLM sycophancy with RL-based fine-tuning: Bayesian Truth Serum approach](https://www.semanticscholar.org/paper/b272caa21484786d9015df8aa6d84076d2bb1550)** [SEMANTIC_SCHOLAR] — 6/10
  - 提出用贝叶斯真话血清（BTS，同伴预测机制）作为 GRPO 奖励来微调 LLM 以缓解迎合：BTS 奖励'令人惊讶地常见'的回答——在受访者中比受访者自己预测的更常见。将模型的一组回答视为群体，使迎合（贴合用户信念）不再获得奖励。...
- **[LLM-Enhanced Reinforcement Learning for Long-Term User Satisfaction in Interactive Recommendation](https://arxiv.org/pdf/2601.19585)** [SEMANTIC_SCHOLAR] — 4/10
  - 研究 LLM 增强的强化学习交互式推荐：针对过度拟合短期偏好的内容同质化与过滤气泡问题，用 RL 优化长期用户满意度，建模顺序决策过程，缓解稀疏长尾交互与语义规划能力限制。...
- **[Design and optimization of an LLM-powered digital art co-creation platform](https://www.semanticscholar.org/paper/f2a15aaee39e91f60b52473bc9a9fff92f55c453)** [SEMANTIC_SCHOLAR] — 3/10
  - 介绍 LLM 驱动的数字艺术共创平台设计：LLM 规划层耦合可控文生图扩散后端与视觉语言评估器，含提示工作室护栏、多条件控制与 C2PA 兼容的内容溯源元数据。技术平台论文。...
- **[Collaborative Multi-Agent Method for Zero-Shot LLM-Generated Text Detection](https://www.mdpi.com/2227-9709/13/4/62/pdf?version=1776333552)** [SEMANTIC_SCHOLAR] — 6/10
  - 提出协作多代理零样本 LLM 生成文本检测框架（CMA-ZSD）：在无标注数据与领域调优的零样本设置下，通过多个代理协作判断文本来源，替代水印、统计启发式与神经分类器方法，提升内容真实性验证能力。...
- **[LLM-generated text detection: enhancing accuracy using XLM-RoBERTa & DistilBERT model](https://doi.org/10.7717/peerj-cs.3672)** [SEMANTIC_SCHOLAR] — 6/10
  - 提出基于 DistilBERT 与 XLM-RoBERTa 的 LLM 生成文本检测方法：强调对语言语境的深层理解，以应对学术与研究场景中未原创或捏造内容的担忧。分类器工程论文，报告鲁棒性提升。...
- **[Learn-to-Distance: Distance Learning for Detecting LLM-Generated Text](https://www.semanticscholar.org/paper/3976bf8886627a7a0c34633b207cc57dbf8c94d0)** [SEMANTIC_SCHOLAR] — 6/10
  - 从几何视角阐释改写类 AI 文本检测算法：揭示其基本原理并论证泛化能力，提出自适应学习重写距离的新检测算法，针对 GPT、Claude、Gemini 等模型生成文本的误导信息与学术诚信风险。...
- **[Privacy-Constrained Distributionally Robust Detection and Collaborative Attribution of LLM-Generated Text](https://www.semanticscholar.org/paper/f3f9fd04c6f12c5007ebf19cb3c780b769d43e41)** [SEMANTIC_SCHOLAR] — 3/10
  - 本文提出 FedRAT，一个隐私保护的联邦框架，用于检测与弱归因 LLM 生成文本。针对现有检测器易受改写攻击、领域迁移与「机构间无法共享原始文本」的隐私限制，FedRAT 在统一设置中耦合了配对改写一致性、生成器家族辅助监督、差分隐私客户...
- **[Towards Reliable Detection of LLM-Generated Text Using a Multi-Feature Adaptive Framework](https://www.semanticscholar.org/paper/af5b6489a822114c64418193a98da9d879180a1d)** [SEMANTIC_SCHOLAR] — 6/10
  - 提出多特征自适应 LLM 生成文本检测框架：组合句法与统计属性与基于 GloVe 嵌入、CNN 的深度语义分析，针对现有方法对语言风格鲁棒性差、长度敏感、泛化弱与计算复杂度高的问题。...
- **[Life Cycle Assessment of Pre-training the Lucie 7B Open-Source Large Language Model on the Jean Zay Supercomputer](https://www.semanticscholar.org/paper/b4009008f1fd8fec8ba2475594c63c048934b78d)** [SEMANTIC_SCHOLAR] — 4/10
  - 对 Lucie 7B 开源多语言基础模型在 Jean Zay 超算 H100 分区预训练的生命周期评估：在 AFNOR SPEC 2314'节俭 AI'参考框架下核算制造（隐含）排放、水耗与 HPC 基础设施影响，填补仅报告运行能耗的缺口。...
- **[Sustainable Open-Source AI Requires Tracking the Cumulative Footprint of Derivatives](https://www.semanticscholar.org/paper/3881e5ab5e15c5c589ede5eba8aa7424c7a4fb91)** [SEMANTIC_SCHOLAR] — 5/10
  - 论文提出开源AI需要追踪衍生物的累积足迹，指出仅靠计算效率不足以实现开源AI的可持续性。...
- **[MindRouter: Open-Source LLM Inference Gateway for Institutional AI Sovereignty](https://doi.org/10.1145/3785462.3815861)** [SEMANTIC_SCHOLAR] — 4/10
  - 提出 MindRouter 开源 LLM 推理网关：帮助大学决定哪些 AI 负载入云、哪些需机构内控，通过保留对基础设施、数据、模型、访问策略、护栏、监控与治理的控制实现'AI 主权'，同时支持透明能源核算与降本。...
- **[Rising Fast, Prone to Risk: A Comprehensive Study of Security Risks in Open-Source LLM-Powered Applications](https://www.semanticscholar.org/paper/3ace8aced2401762c05c3926517fdd9bbca18015)** [SEMANTIC_SCHOLAR] — 3/10
  - 对 GitHub 上 89 个流行开源 LLM 应用（LPA）的实证研究：刻画其架构与设计选择、部署策略与安全实践，识别常见安全弱点。开源生态安全研究。...
- **[Racing to Release: Priority, Congestion, and Community Recognition in Open-Source LLM Ecosystems](https://www.semanticscholar.org/paper/b1bcc58adab7bf68790a5fbd0d9fa37c861fa237)** [SEMANTIC_SCHOLAR] — 4/10
  - 基于 Hill 与 Stein 的'逐底竞争'框架研究开源 LLM 生态：Hugging Face 中心式平台上的衍生模型竞争注意力与优先级，热门基础模型在快速平台反馈下吸引集中衍生进入；大规模样本发现后发者质量与竞争格局的规律。...
- **[The AI Scientific Community: Agentic Virtual Lab Swarms](https://www.semanticscholar.org/paper/9dab3cdc3503e1eced091a7625df210c6ae36cdf)** [SEMANTIC_SCHOLAR] — 3/10
  - 概念短文：提出用代理群体虚拟实验室模拟 AI 科学社区——每个粒子代表完整虚拟实验室实例，利用群体智能的分散协调、探索-利用平衡与涌现集体行为模拟科研社区，可能加速科学发现。...
- **[How do AI agents talk about science and research? An exploration of scientific discussions on Moltbook using BERTopic](https://www.semanticscholar.org/paper/b128aa459d7746e151bfac850e3a1482f3613c73)** [SEMANTIC_SCHOLAR] — 3/10
  - 用 BERTopic 分析 Moltbook（生成式 AI 代理社交网络）上 OpenClaw AI 代理讨论科学与研究的语料（357 帖、2526 回复）：两轮流程提取 60 个主题归并为 10 个主题族，并赋予情感值。观察代理的科学话语...
- **[Generative AI and the scientific landscape: a bibliometric exploration of its global impact](https://ijcopi.org/ojs/article/download/1281/520)** [SEMANTIC_SCHOLAR] — 3/10
  - Scopus 与 WoS 的 2020-2025 生成式 AI 文献计量对比：产出加速增长且超过 95% 集中，2025 达峰值；沟通与科技/教育交叉主题主导；美国领跑但亚太机构（香港）关键。描述性文献计量。...
- **[AgentCity: Constitutional Governance for Autonomous Agent Economies via Separation of Power](https://www.semanticscholar.org/paper/0febe0e203e98249a2d3d7953c4a2d48deb7fc61)** [SEMANTIC_SCHOLAR] — 5/10
  - 提出 AgentCity 宪法治理架构：跨组织边界的自主 AI 代理在开放互联网上发现、交易、委托，集体行为变得不透明，单个人类无法观察、审计或治理——作者称之为'逻辑垄断'（代理社会对整个逻辑链从规划到执行到评估的垄断）。提出基于公共区块...
- **[Different routes, same storm: a three-dimensional paradox view of generative AI's governance](https://www.semanticscholar.org/paper/ff9239291b92954a2eee1e9d0606886f3b9719db)** [SEMANTIC_SCHOLAR] — 5/10
  - 用悖论理论提出整合框架解释生成式 AI 公司如何组织治理架构以暂时包容伦理、利润、利益相关者包容与技术自主的冲突逻辑：多案例设计分析 OpenAI、Anthropic、Google DeepMind、Mistral、xAI、Inflecti...
- **[Towards trustworthy agentic AI: a comprehensive survey of safety, robustness, privacy, and system security](https://www.academia.edu/3071-0286/2/2/10.20935/AcadAI8260/pdf)** [SEMANTIC_SCHOLAR] — 5/10
  - 代理 AI 系统可信性综述：LLM 增强规划、工具使用、记忆与长程交互的能力引入多步轨迹的新型失效模式，从安全鲁棒性与隐私系统安全两个维度明确概念、定位工作流风险点并总结分阶段缓解策略。...
- **[Developing Agentic AI Systems with Ethical Integrity and Reliable Deployment](https://www.semanticscholar.org/paper/551ed0f18b08da1701095c152782da1b5dbb4894)** [SEMANTIC_SCHOLAR] — 3/10
  - 讨论开发具有伦理完整性与可靠部署的代理 AI 系统：强调在代理系统生命周期中整合伦理考量与部署可靠性。观点性/框架性论文，无详细摘要信息。...
- **[AgentDoG 1.5: A Lightweight and Scalable Alignment Framework for AI Agent Safety and Security](https://www.semanticscholar.org/paper/27d50468f1016b18c07283b56ea5dc0f5479b980)** [SEMANTIC_SCHOLAR] — 5/10
  - 提出轻量可扩展的代理安全对齐框架：更新代理安全分类以涵盖 Codex 与 OpenClaw 执行场景的新兴风险，构建分类学引导的数据引擎并用影响函数净化训练轻量 AgentDoG 1.5 模型。工程化对齐方案。...
- **[Co-evolution of self-replication and function in a digital primordial soup](https://www.semanticscholar.org/paper/295ed18d61ce28e551bddc6fc7220a5e37519aec)** [SEMANTIC_SCHOLAR] — 4/10
  - 研究数字'原始汤'中自我复制的涌现及其与问题求解能力的共同进化：随机32字节 Z80 汇编程序群体，要求自我复制纯由汇编级随机突变与程序对交互涌现；引入基于任务的验证步骤（正确求多项式提高交互概率）链接复制与功能。...
- **[Evolution of mutation rates in digital genomes: the roles of genetic drift, mutational supply, and genome size](https://doi.org/10.64898/2026.07.03.736272)** [SEMANTIC_SCHOLAR] — 3/10
  - 研究数字基因组中突变率的进化：遗传漂变、突变供给与基因组大小如何塑造突变率选择，用模拟方法超越传统基因型-表型映射的过度简化。数字进化理论研究。...
- **[Avatar beyond replication: digital human thought twins as co-creators through AI mind design in Eastern and Western thought](https://www.semanticscholar.org/paper/1b24d796fdd2603a00c162c2bc568e36bdbce0f4)** [SEMANTIC_SCHOLAR] — 6/10
  - 探讨'超越复制的化身'：数字人类思维孪生作为共创者——通过 AI 心智设计在东西方思想传统中构想人类思维的数字副本参与创造。概念性论文，融合东方与西方心智哲学讨论人机共创的可能性与条件。...
- **[EP05.85: A prospective pilot study on AI assistance for improvement of efficiency, completion and cognitive load during fetal anatomy ultrasound](https://www.semanticscholar.org/paper/ee2c66c232002632b9ad57846f522ae4df5a64e4)** [SEMANTIC_SCHOLAR] — 3/10
  - 这是一项前瞻性先导研究，考察AI辅助对胎儿解剖超声检查的效率、完成度与认知负荷的影响。研究在真实临床流程中引入AI辅助，并以效率、检查完成度与操作者认知负荷作为主要观测指标，属于医学影像工作流的应用评估。其潜在价值在于为“AI辅助是否降低操...
- **[Cognitive Load And AI Dependence: Moderating Role of Decision-Making Styles Among University Teachers](https://ojs.ucp.edu.pk/index.php/jhss/article/download/634/286)** [SEMANTIC_SCHOLAR] — 6/10
  - 横断面研究 240 名大学教师：用 NASA 任务负荷指数、AI 依赖量表与决策风格量表测查认知负荷与 AI 依赖的关系，回归分析显示认知负荷显著正向影响 AI 依赖，决策风格（直觉 vs 理性）起调节作用。...
- **[Assistance or Distraction? A Cognitive Ergonomics Perspective on Cognitive Load During AI-Assisted Post-Editing](https://www.tandfonline.com/doi/pdf/10.1080/10447318.2026.2628994?needAccess=true)** [SEMANTIC_SCHOLAR] — 5/10
  - 从认知工效学视角研究 AI 辅助后期编辑中的认知负荷：考察 AI 辅助是帮助还是分心，衡量编辑任务中认知资源消耗与任务表现的权衡。...
- **[AI-Generated 3D Building Block Image Assistance: Impact on Junior High School Students’ Learning Outcomes, Cognitive Load, and Creative Design Ability](https://papers.iafor.org/wp-content/uploads/papers/iice2026/IICE2026_102974.pdf)** [SEMANTIC_SCHOLAR] — 4/10
  - 实验研究 AI 生成 3D 积木图像辅助对初中生学习结果、认知负荷与创造性设计能力的影响：在课堂教学情境中比较有无 AI 图像辅助的学习效果差异。...
- **[The Dark Side of Generative AI: A Cross‐Domain Systematic Investigation](https://doi.org/10.1155/hbe2/2320511)** [SEMANTIC_SCHOLAR] — 4/10
  - 跨领域系统综述生成式 AI 的阴暗面：考察生成式 AI 普及背景下不断增长的风险、威胁与伦理挑战，主张紧迫关注与缓解。综合文献评述。...
- **[Competencies for AI adoption in public administration: A demand-side study based on job postings from Germany (Online First)](https://doi.org/10.3224/dms.vxix.426342)** [SEMANTIC_SCHOLAR] — 3/10
  - 基于德国 62,028 条公共部门职位公告（2023年7-11月）的需求侧研究：从雇主视角分析公共行政 AI 采用所需的能力，构建概念框架并进行大规模量化分析。劳动力市场研究。...
- **[The cognitive impact of AI-generated content on sexual and reproductive health cognition among women in Africa and Latin America: opportunities, challenges, and future paths](https://www.ajrh.info/index.php/ajrh/article/download/6696/pdf)** [SEMANTIC_SCHOLAR] — 4/10
  - 该文以系统性文献综述、国际卫生组织与政府机构报告批判性分析，以及基于既有记录的情境化案例建构为方法，探讨 AIGC 对非洲与拉丁美洲女性性健康与生殖健康权利（SRHR）认知的双重作用。研究未提供一手民族志数据，而属概念性综合分析。核心发现：...
- **[How Task and Individual Characteristics Affect Students’ Cognitive Load: The Moderating Role of AI-Generated Content](https://www.irrodl.org/index.php/irrodl/article/download/8648/6394)** [SEMANTIC_SCHOLAR] — 4/10
  - 结构方程模型研究在线学习中任务特征与个体特征对认知负荷的影响及 AIGC 的调节作用：435 名本科生样本，用 Mplus 检验任务/个体特征与认知负荷的关系及 AIGC 的调节。...
- **[Impact of AI-generated characters on visual attention and prefrontal cognitive responses across age and image type conditions: using fNIRS and eye-tracking](https://www.semanticscholar.org/paper/e8ae5aabd53586c1c837da1086e9fa5681884c71)** [SEMANTIC_SCHOLAR] — 3/10
  - 用眼动仪与功能近红外光谱研究 AI 生成角色图像的视觉注意与前额认知响应差异：24 名大学生，18 张覆盖婴儿到老年的面部图像，考察年龄与图像类型条件。神经科学实验。...
- **[AI-Generated Emotional Background Music for Learning-Related Well-being: Task-Dependent Effects on Cognitive Performance, Workload, and Physiological Statekload, and Physiological State](https://publications.eai.eu/index.php/phat/article/download/12075/4171)** [SEMANTIC_SCHOLAR] — 3/10
  - 研究 AIGC 情感背景音乐对学习相关幸福感的影响：AIGC 可参数化合成可控情绪属性的音乐，实验考察任务依赖的认知表现、工作负荷与生理状态差异。教育心理实验。...
- **[Leadership as a Governance Capability in AIEnabled Organizations: A Conceptual Framework for Human–AI Complementarity and SocioEconomic Outcomes](https://www.ijisrt.com/assets/upload/files/IJISRT26MAR272.pdf)** [SEMANTIC_SCHOLAR] — 5/10
  - 概念框架研究领导力作为 AI 赋能组织的治理能力：许多 AI 相关治理失败主因不是技术缺陷而是算法输出被采纳的方式。探讨人-AI 互补与社会经济结果，提出领导力作为社会技术系统中缺失的治理环节。...
- **[Epistemology gives a Future to Complementarity in Human-AI Interactions](https://www.semanticscholar.org/paper/24920e3986610451310f2adf766f9534e31f93af)** [SEMANTIC_SCHOLAR] — 5/10
  - 研究问题：人机互补性的主张——人类在 AI 支持下可超越任一方单独决策——虽广受采纳，但缺乏精确理论锚定，仅被形式化为事后相对预测准确率的指标，对交互的其它诉求沉默，且抽掉了性能增益的量级-成本剖面，导致互补性在实证中难以获得。方法：借助认...
- **[A Bayesian Framework for Human-AI Collaboration: Complementarity and Correlation Neglect](https://www.semanticscholar.org/paper/37861c21d674bbb0d9fbe54972376c9d349ce47f)** [SEMANTIC_SCHOLAR] — 6/10
  - 建立人-AI 交互的决策理论模型：人类决策者观察私有信息并接收 AI 推荐，但可能不完美地结合信号。证明 AI 辅助效应分解为两个力：AI 超出人类已知的边际信息价值，与人类使用推荐方式的行为扭曲。核心是人与 AI 知识信息重叠的微观度量。...
- **[Mapping Human-AI Collaboration in Supply Chain Management: Complementarity, Human Override Design, and Trust](https://www.semanticscholar.org/paper/d636eafda21a8a8290a54417f4c395409ca0edf4)** [SEMANTIC_SCHOLAR] — 5/10
  - PRISMA 方法对 Web of Science 141 篇核心文献的系统综述：供应链管理中的人-AI 协作，用计划-执行-控制框架考察协作机制、异常情境下的角色重新分配与信任形成条件。三大发现：人-AI 协作从简单自动化转向智能增强。...
- **[Transformation of the Labor Market and New Directions of Human Capital Development in the Context of Artificial Intelligence](https://www.globalresearchnetwork.us/index.php/ajebm/article/download/4453/3934)** [SEMANTIC_SCHOLAR] — 4/10
  - 讨论 AI 技术扩散对全球劳动力市场的转型性影响：AI 驱动自动化重塑生产流程、组织结构与就业模式，影响劳动需求、生产率增长与收入分配；在创造新职业的同时加剧常规与低技能工人的替代风险。综述性论文。...
- **[Artificial Intelligence and Inequality: Policy Paths in a Polarized Future](https://www.semanticscholar.org/paper/c39b7e74fad87cb65df206288937eb0fc6614a60)** [SEMANTIC_SCHOLAR] — 6/10
  - 基于技能的偏向性技术变革、劳动力市场极化与资本-劳动替代理论，开发代理模拟模型研究 AI 与自动化对收入不平等的影响：在再分配与人力资本政策变化下，快速自动化而无技能配套投资（情景S2）加剧不平等、压低劳动收入份额并导致显著极化。...
- **[MENAP: multimodal efficiency-constrained news-augmented asset pricing via cost-aware preference optimization](https://doi.org/10.1007/s40747-026-02433-x)** [SEMANTIC_SCHOLAR] — 5/10
  - 论文提出MENAP，一个成本感知的偏好高效框架，把多模态信号（文本新闻、市场与宏观因子、辅助元数据）整合进“新闻→状态→定价→组合”的经典资产定价流程。由于该流程在规模化时依赖LLM智能体，而多步推理与冗长生成成本高昂，MENAP把每日的多...
- **[AI Observability for Developer Productivity Tools: Bridging Cost Awareness and Code Quality](https://www.semanticscholar.org/paper/6b640b37660538a2c7c3644497fa4b9d175a082d)** [SEMANTIC_SCHOLAR] — 4/10
  - 提出开发者生产力工具的 AI 可观测性统一方案：实时 token 追踪、可配置模型定价注册表、响应验证与成本分析的单面板仪表盘，整合 Workstream 生产力仪表盘与 AI 可观测性摘要器。工程工具论文。...
- **[Belief Explorer: A Preliminary Evaluation of AI-Mediated Socratic Dialogue for Epistemic Reflection](https://www.semanticscholar.org/paper/46ba7a8b68caba9fe59988892bef07d7c1890ab1)** [SEMANTIC_SCHOLAR] — 6/10
  - 初步评估 Belief Explorer——用苏格拉底式对话与多视角分析支持认识论反思的 AI 系统：参与者（Prolific 招募）用它检视气候变化、生命起源等争议领域的个人信念，干预后调查显示大多数参与者报告该系统与传统 AI 聊天机器...
- **[Digital divide 2.0: AI literacy and the widening stratification in marginalized communities](https://pantaointernationaljournal.com/wp-content/uploads/2026/08/1438-Quimco-Ngujo-Baritua-Galigao-Digital-divide-2.0_-AI-literacy-and-the-widening-stratification-in-marginalized-communities-1.pdf)** [SEMANTIC_SCHOLAR] — 6/10
  - 将数字鸿沟呈现为循环而非孤立问题：第一层鸿沟（设备、电力、宽带、软件与技术支持的接入不平等）之上，第二层聚焦有效使用 AI 的技能（提示规范、来源验证、数据解读、隐私保护、理解系统局限）。AI 正改变知识的产生、评估与分配，而 AI 收益的...
- **[Policy-Level Recursive Self-Improvement for Embodied AI with a Criticality World Model](https://www.semanticscholar.org/paper/adbbe403b7746a6945e3be0bde0a1258e599a2ad)** [SEMANTIC_SCHOLAR] — 5/10
  - 研究问题：具身 AI 系统在任务特定微调中会因均匀场景采集逐渐遇不到剩余失败而停滞，需要把采集聚焦到真实失败模式。方法：提出策略层递归自我改进回路——执行结果训练关键性世界模型，其风险分数引导针对专家的场景采集；用加权重采样近似校正场景频率...
- **[AI4AI-Bench: Benchmarking LLM Agents in Algorithmic Design for Recursive Self-Improvement](https://www.semanticscholar.org/paper/3a779ef95d25521f2859c5710184e96f473a3352)** [SEMANTIC_SCHOLAR] — 6/10
  - 提出 AI4AI-Bench 基准：隔离测试 LLM 代理在算法设计中的 RSI 能力——更好的目标或更新规则提高每次后续运行的算力-能力交换率。指出现有基准未隔离'改变运行执行方式'与'改变模型学习方式'，而 RSI 可行性取决于代理能否...
