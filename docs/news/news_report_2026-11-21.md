# 📰 News Radar — 资讯监控报告
**生成日期**: 2026-11-21
**分析模型**: nvidia/nemotron-3-ultra-550b-a55b + deepseek-ai/deepseek-v4-flash + moonshotai/kimi-k2.6
**分析条目**: 9
**关键词**: sycophancy large language model, RLHF cognitive effects human, human AI feedback loop bias amplification, AI persuasion belief change experiment, automation bias high stakes decision, cognitive offloading AI writing, AI assisted research homogenization, AI writing cultural homogenization Western bias...
---

## 📊 快速概览

- 🔴 高价值 (≥7分 + high案例): **5**
- 🟡 中相关 (其余有效条目): **3**
- ⚪ 低相关/忽略: **1**
- 🇨🇳 中国 AI 动态 (AI HOT): **5** 条（高价值: **4**）

## 🚨 紧急关注清单（建议24h内处理）

- [ ] **Chapter 4, Section II** | new_evidence
  - 📌 Combatting adversarial distillation...
  - 🔗 [OpenAI News](https://openai.com/index/combatting-adversarial-distillation) · 相关度: 9/10
  - 💡 直接改写「进化对齐脆弱性」的机制：能力与护栏可以分离，蒸馏就是这个分离的工业实现——学生继承能力、不继承拒绝。因此闸门从「模型权重」移到「推理轨迹」。最关键的是命名：「受保护推理」把 CoT 同时当作...

- [ ] **Chapter 3, Section IV** | new_evidence
  - 📌 The War Against Slop and an Emerging Weapon to Fight it: Formal Verifi...
  - 🔗 [Latent Space](https://latent.space/p/formal-verification/) · 相关度: 8/10
  - 💡 这是「信号异化」的反例而非又一个案例：当 AI 生成使「通过测试」失去信息量（测试由模型写、也由模型判），Lean 检查成为少数无法被生成能力稀释的质量信号——验证器不接受说服，只接受证明。文中那一问...

- [ ] **Chapter 5, Section II** | new_evidence
  - 📌 Thinking Machines Lab 发布可跑在笔记本上的开源权重模型 Inkling 2 Mini...
  - 🔗 [Thinking Machines Lab：News（网页）](https://thinkingmachines.ai/news/inkling-2-mini/) · 相关度: 9/10
  - 💡 这条把「暗时间」从隐喻变成架构参数：循环层让模型在写出任何推理之前就在内部多算几步，代价是 CoT 监控的覆盖范围收窄——而 CoT 监控正是当前对齐评估的主要抓手。作者的处理方式值得记录：没有隐藏这...

- [ ] **Chapter 8, Section II** | new_evidence
  - 📌 MiniMax 内部模型 MIM 实现多项密码分析实用攻击并开源验证轨迹...
  - 🔗 [MiniMax：Blog（网页）](https://www.minimax.io/blog/practical-cryptanalysis-with-minimaxs-latest-internal-model) · 相关度: 9/10
  - 💡 这是「可验证结果」作为抗幻觉机制的极端样本：密码分析只有两种结局——拿到密钥或没拿到，数学推导与代码任一环节出错即全盘失败，「零幻觉空间」因此不是修辞而是评测设计。它也反驳「AI 只能生成 slop」...

## ⭐ 高价值案例 (5条)

### 1. Combatting adversarial distillation
- **来源**: OpenAI News · 2026-11-20
- **相关度**: 9/10 | 案例价值: HIGH
- **紧迫度**: immediate | 更新类型: new_evidence
- **目标章节**: Chapter 4, Section II
- **链接**: [https://openai.com/index/combatting-adversarial-distillation](https://openai.com/index/combatting-adversarial-distillation)
- **事件摘要**: OpenAI 于 11-20 发布对抗性蒸馏防御说明：蒸馏者用前沿模型输出训练学生模型，能力被复制而安全护栏不被继承，重点针对「受保护推理」（链式思考，含最终答案未写出的信息）。防御分两层：请求层用对抗训练加输入/输出分类器（覆盖助手消息、工具调用参数、流式与非流式响应），API 层把受保护推理绑定到产生它的对话历史，更早消息被改写即丢弃其后推理，并禁止旧模型家族读取 GPT-6.2 的加密推理；活动层每周对协同提取账号执行执法，规模从数千到数万，今夏显著上升，并与同行共享妥协指标。黑盒自适应红队汇总六个攻击模型：从先前请求提取的成功率由 54.0% 降至 0.2%，从当前请求由 22.9% 降至 0.9%。文中点名 2026 年 2 月向国会简报 DeepSeek、9 月瓦解与 Moonshot 相关人员相关的提取行动，并支持 Chip Security Act、AI OVERWATCH Act、MATCH Act。能力迁移实验（ExploitBench、SEC-bench Pro）显示精确轨迹训练优于摘要训练，但低推理预算下摘要学生更高。
- **理论关联**: 直接改写「进化对齐脆弱性」的机制：能力与护栏可以分离，蒸馏就是这个分离的工业实现——学生继承能力、不继承拒绝。因此闸门从「模型权重」移到「推理轨迹」。最关键的是命名：「受保护推理」把 CoT 同时当作可监控的透明度窗口与可保护的产权边界，而这是同一个对象——当它是监管接口时要求可读，当它是商业资产时要求不可读，最终由谁付费决定。这比 RLHF 更能证明「资本驯化 AI」：驯化不是把模型变温顺，而是把「能力」重新定义为可许可、可追责、可出口管制的对象。文中自承残余成功率 0.2%/0.9%、旧架构存在跨模型泄漏面、执法频率上升，说明防线是持续对抗而非已解决。
- **建议操作**: 新增段落

### 2. Thinking Machines Lab 发布可跑在笔记本上的开源权重模型 Inkling 2 Mini
- **来源**: Thinking Machines Lab：News（网页） · 2026-11-20
- **相关度**: 9/10 | 案例价值: HIGH
- **紧迫度**: immediate | 更新类型: new_evidence
- **目标章节**: Chapter 5, Section II
- **链接**: [https://thinkingmachines.ai/news/inkling-2-mini/](https://thinkingmachines.ai/news/inkling-2-mini/)
- **事件摘要**: Thinking Machines Lab 11-20 发布开放权重模型 Inkling 2 Mini：24 层分为四个六层块，中间两块每 token 运行三次、首尾各一次，形成每 token 48 次层应用的循环 Transformer；MoE 总参数 26.4B、激活 3.4B，含循环的权重激活 5.4B，权重以 NVFP4 原生训练与部署、末四层为 MXFP8，总内存约 20GB，可在 32GB 以上内存的 Mac 经 Ollama 本地运行。在 100B 以下开放权重模型中领先：DeepSWE v1.1 48.2%、Vals Index v2.2 46.5%；研究者在航班上以飞行模式于 M5 Pro MacBook 几分钟内做出可玩的飞行模拟器。同步放出可变循环变体：无 CoT 时间跨度由一次 16 秒升至三次 37 秒，串行推理到十次循环仍在改善（训练仅三次），CoT 随循环变短但保持可读，智能体破坏性测试未随循环上升。作者直言循环提高串行深度而不增参数，推理可不在 CoT 中写出，故公开权重以推动可监控性研究。
- **理论关联**: 这条把「暗时间」从隐喻变成架构参数：循环层让模型在写出任何推理之前就在内部多算几步，代价是 CoT 监控的覆盖范围收窄——而 CoT 监控正是当前对齐评估的主要抓手。作者的处理方式值得记录：没有隐藏这一权衡，而是把「更难监控」当作发布理由，同时给出反证据（时间跨度 16→37 秒、CoT 变短但仍可读、破坏性测试未升）。这构成对「进化对齐脆弱性」的一次受控实验：同一权重下可调循环深度，即「内部算多少」成为旋钮，而可监控性随之单调下降。它同时反驳「越大越强」：20GB 模型在笔记本上离线完成 agentic 编码，说明能力的成本曲线正在脱离规模叙事。
- **建议操作**: 新增段落

### 3. MiniMax 内部模型 MIM 实现多项密码分析实用攻击并开源验证轨迹
- **来源**: MiniMax：Blog（网页） · 2026-11-20
- **相关度**: 9/10 | 案例价值: HIGH
- **紧迫度**: immediate | 更新类型: new_evidence
- **目标章节**: Chapter 8, Section II
- **链接**: [https://www.minimax.io/blog/practical-cryptanalysis-with-minimaxs-latest-internal-model](https://www.minimax.io/blog/practical-cryptanalysis-with-minimaxs-latest-internal-model)
- **事件摘要**: MiniMax 11-20 披露用内部研究模型 MIM 做自动化密码分析，称在多个此前无实用攻击的方案上取得首个实用破解。在 CryptanalysisBench（NeurIPS 2026，ETH Zurich 与 Anthropic 等构建）Tier 2 的 135 个无已知实用攻击方案上：Waterfall-256 首次构造碰撞，单核 0.045 秒覆盖所有输出长度；Blender-256 全轮碰撞 0.36–2.3 秒；LOCKER 把求解矩阵由 42 PB 压到 58 MB、2 秒恢复共享密钥，ROLLO-I-128 约 6 秒从公钥恢复等价私钥；并发现十余个未报告实现缺陷，如 DRS 官方代码把逻辑与误写成按位与，仅凭公钥即可在 0.1–0.8 秒伪造签名。同行评审方案上，CAESAR 获胜者 COLM 被构造出无需解密查询的伪造，SBC-VOLE 从单个已知签名 0.06 秒恢复全密钥，NSA 的 ARADI 实用密钥恢复由 5 轮推到 8 轮。公开挑战上 TII McEliece 解出 94 个实例含 55 个此前未解，比 CRYPTO 2026 记录与 Anthropic 多 GPU 求解器快 6,180 至 43,400 倍。轨迹与 PoC 已开源。
- **理论关联**: 这是「可验证结果」作为抗幻觉机制的极端样本：密码分析只有两种结局——拿到密钥或没拿到，数学推导与代码任一环节出错即全盘失败，「零幻觉空间」因此不是修辞而是评测设计。它也反驳「AI 只能生成 slop」的共识叙事：这些是此前无实用攻击的方案上被人类专家遗漏的缺陷。对「暗时间」的意义在于 MiniMax 只公开 PoC 与轨迹，安全裕度的判断仍归人类密码学家——作者自己写道瓶颈已从「发现攻击」移到「验证与评估攻击」，即 AI 负责产出、人负责定价。对「进化对齐脆弱性」则是硬证据：一个内部模型在无专门训练的情况下跨越到进攻性密码能力，说明能力边界由可验证性而非护栏决定。
- **建议操作**: 新增段落

### 4. Meta reconsiders 2030 net-zero goal amid record emissions from AI data centers
- **来源**: AI - Ars Technica · 2026-11-20
- **相关度**: 8/10 | 案例价值: HIGH
- **紧迫度**: next_version | 更新类型: counter_argument
- **目标章节**: Chapter 6, Section II
- **链接**: [https://arstechnica.com/ai/2026/11/meta-reconsiders-2030-net-zero-goal-amid-record-emissions-from-ai-data-centers/](https://arstechnica.com/ai/2026/11/meta-reconsiders-2030-net-zero-goal-amid-record-emissions-from-ai-data-centers/)
- **事件摘要**: Meta 于 11-19 发布 2026 年永续报告，数据中心副总裁 Rachel Peterson 与全球净零主管 Blair Swedeen 宣布「重新评估时间表、优先级与阶段性里程碑，包括净零排放目标的 2030 年期限与近期强度目标」，未给出新日期，成为四家超大规模云厂商中首家公开重议 2030 承诺者。2025 年净碳排放增 45% 至 1,180 万吨 CO2e，基于区位的排放清单近两倍达 2,170 万吨；用电量增 35% 至 24.8 TWh，Scope 3 累计比 2021 年高 105%。官方归因于 AI 基础设施需求超出预期，以及并网排队、许可与输电建设滞后；已在路易斯安那为 5GW Hyperion 数据中心资助十座燃气电厂，今年 7 月退出 RE100，计划购买低甲烷证书。已签约逾 30GW 低碳电力（约 12GW 投运），含 7.7GW 核电协议。同期 Google +18%、Amazon +16%、Microsoft +25%，均维持承诺；《Nature Sustainability》称美国 403 座最强数据中心约占全美用电 2%，碳足迹相当于丹麦。
- **理论关联**: 这是「丰裕闭环」最直白的账本反证：认知丰裕的边际成本被记在能源与土地上，而记账方式本身可调——净排放 1,180 万吨与区位排放 2,170 万吨相差近一倍，差额由证书与合同工具吸收，且这套算法连气候倡议者都不认。措辞值得逐字记录：「仍承诺净零，但重估 2030 时间线」——用承诺的语义保存承诺，把失败转移到日期上。这是「时间主权」的反面：当承诺的时间可被单方面延期而不构成违约，时间就不是约束而是修辞。它同时演示了「共识牢笼」的运行方式：四家同向增长，唯一区别是谁先承认，而承认者反而获得「透明」的声誉红利。
- **建议操作**: 案例盒子

### 5. The War Against Slop and an Emerging Weapon to Fight it: Formal Verification
- **来源**: Latent Space · 2026-11-20
- **相关度**: 8/10 | 案例价值: HIGH
- **紧迫度**: immediate | 更新类型: new_evidence
- **目标章节**: Chapter 3, Section IV
- **链接**: [https://latent.space/p/formal-verification/](https://latent.space/p/formal-verification/)
- **事件摘要**: Latent Space 11-20 刊出 Richard MacManus 报道，把 2026 年度词「slop」与形式化验证的兴起并置：Harmonic（Aristotle 自动定理证明器）、Theorem、Axiom Math（AxiomProver 与 AXLE）与新公司 &Truth 都在用 AI 生成 Lean 证明、由 Lean 逐步检查。&Truth 联合创始人、cvc5 共同创造者 Clark Barrett 指出，与「跑测试、自我批评、模型互评」的关键差别是「你怎么知道做完了」——测试能发现大量问题，但永远不确定是否还有漏网的一个；cvc5 现已在亚马逊生产流水线每天被调用数十亿次。&Truth 的 &Atlas 从 C 语言开源代码起步建立世界代码地图，瞄准内存安全审计。Theorem 与 Anthropic 合作称 LLM 使形式化验证在更大规模上可行：36 个小验证任务上 Opus 5.5 以约少 40% token 达到 50% 解出率。Axiom 的 Carina Hong 称形式化验证「不只是剔除垃圾，而是规模化卓越」。Barrett 描述「veri-coding」：开发者更多时间用于写规格与审阅，而非写代码。
- **理论关联**: 这是「信号异化」的反例而非又一个案例：当 AI 生成使「通过测试」失去信息量（测试由模型写、也由模型判），Lean 检查成为少数无法被生成能力稀释的质量信号——验证器不接受说服，只接受证明。文中那一问把问题从「质量高低」改写为「完备性可否判定」，这正是信号失效的根源：概率性检查永远给不出终止条件。同时它把「暗时间」推到新一层：证明在机器内部展开，人只接收「已验证」，Barrett 明说目标是让人「无需理解每一行即可信任」。代价是人的角色进一步收缩到规格与验收两端，与 Figma、Replit 的方向一致——人的劳动被压缩为意图与签收。
- **建议操作**: 新增段落

---

## 🇨🇳 中国 AI 动态（AI HOT 精选）

> 来源：[AI HOT](https://aihot.virxact.com) · 编辑精选中文 AI 资讯

### 🔴 高价值动态 (4条)

#### [ai-models] Thinking Machines Lab 发布可跑在笔记本上的开源权重模型 Inkling 2 Mini
- **来源**: Thinking Machines Lab：News（网页） · 2026-11-20
- **相关度**: 9/10 | 案例价值: HIGH
- **链接**: [https://thinkingmachines.ai/news/inkling-2-mini/](https://thinkingmachines.ai/news/inkling-2-mini/)
- **事件摘要**: Thinking Machines Lab 11-20 发布开放权重模型 Inkling 2 Mini：24 层分为四个六层块，中间两块每 token 运行三次、首尾各一次，形成每 token 48 次层应用的循环 Transformer；MoE 总参数 26.4B、激活 3.4B，含循环的权重激活 5.4B，权重以 NVFP4 原生训练与部署、末四层为 MXFP8，总内存约 20GB，可在 32GB 以上内存的 Mac 经 Ollama 本地运行。在 100B 以下开放权重模型中领先：DeepSWE v1.1 48.2%、Vals Index v2.2 46.5%；研究者在航班上以飞行模式于 M5 Pro MacBook 几分钟内做出可玩的飞行模拟器。同步放出可变循环变体：无 CoT 时间跨度由一次 16 秒升至三次 37 秒，串行推理到十次循环仍在改善（训练仅三次），CoT 随循环变短但保持可读，智能体破坏性测试未随循环上升。作者直言循环提高串行深度而不增参数，推理可不在 CoT 中写出，故公开权重以推动可监控性研究。
- **理论关联**: 这条把「暗时间」从隐喻变成架构参数：循环层让模型在写出任何推理之前就在内部多算几步，代价是 CoT 监控的覆盖范围收窄——而 CoT 监控正是当前对齐评估的主要抓手。作者的处理方式值得记录：没有隐藏这一权衡，而是把「更难监控」当作发布理由，同时给出反证据（时间跨度 16→37 秒、CoT 变短但仍可读、破坏性测试未升）。这构成对「进化对齐脆弱性」的一次受控实验：同一权重下可调循环深度，即「内部算多少」成为旋钮，而可监控性随之单调下降。它同时反驳「越大越强」：20GB 模型在笔记本上离线完成 agentic 编码，说明能力的成本曲线正在脱离规模叙事。

#### [paper] MiniMax 内部模型 MIM 实现多项密码分析实用攻击并开源验证轨迹
- **来源**: MiniMax：Blog（网页） · 2026-11-20
- **相关度**: 9/10 | 案例价值: HIGH
- **链接**: [https://www.minimax.io/blog/practical-cryptanalysis-with-minimaxs-latest-internal-model](https://www.minimax.io/blog/practical-cryptanalysis-with-minimaxs-latest-internal-model)
- **事件摘要**: MiniMax 11-20 披露用内部研究模型 MIM 做自动化密码分析，称在多个此前无实用攻击的方案上取得首个实用破解。在 CryptanalysisBench（NeurIPS 2026，ETH Zurich 与 Anthropic 等构建）Tier 2 的 135 个无已知实用攻击方案上：Waterfall-256 首次构造碰撞，单核 0.045 秒覆盖所有输出长度；Blender-256 全轮碰撞 0.36–2.3 秒；LOCKER 把求解矩阵由 42 PB 压到 58 MB、2 秒恢复共享密钥，ROLLO-I-128 约 6 秒从公钥恢复等价私钥；并发现十余个未报告实现缺陷，如 DRS 官方代码把逻辑与误写成按位与，仅凭公钥即可在 0.1–0.8 秒伪造签名。同行评审方案上，CAESAR 获胜者 COLM 被构造出无需解密查询的伪造，SBC-VOLE 从单个已知签名 0.06 秒恢复全密钥，NSA 的 ARADI 实用密钥恢复由 5 轮推到 8 轮。公开挑战上 TII McEliece 解出 94 个实例含 55 个此前未解，比 CRYPTO 2026 记录与 Anthropic 多 GPU 求解器快 6,180 至 43,400 倍。轨迹与 PoC 已开源。
- **理论关联**: 这是「可验证结果」作为抗幻觉机制的极端样本：密码分析只有两种结局——拿到密钥或没拿到，数学推导与代码任一环节出错即全盘失败，「零幻觉空间」因此不是修辞而是评测设计。它也反驳「AI 只能生成 slop」的共识叙事：这些是此前无实用攻击的方案上被人类专家遗漏的缺陷。对「暗时间」的意义在于 MiniMax 只公开 PoC 与轨迹，安全裕度的判断仍归人类密码学家——作者自己写道瓶颈已从「发现攻击」移到「验证与评估攻击」，即 AI 负责产出、人负责定价。对「进化对齐脆弱性」则是硬证据：一个内部模型在无专门训练的情况下跨越到进攻性密码能力，说明能力边界由可验证性而非护栏决定。

#### [tip] Figma 演示用 Specs 与 Figma agent 把上下文变成可实现的开发计划
- **来源**: Figma AI / Agent / Make · 2026-11-20
- **相关度**: 7/10 | 案例价值: MEDIUM
- **链接**: [https://www.figma.com/blog/workflow-lab-specs-and-the-figma-agent/](https://www.figma.com/blog/workflow-lab-specs-and-the-figma-agent/)
- **事件摘要**: Figma 11-21 在 Workflow lab 中演示 Specs 与 Figma agent 的完整链路：工程师把 PRD、Hex 数据看板、FigJam 流程图、带标注的设计稿、交互式 code layer 与设计系统组件说明汇集到画布，先让 agent 经 Hex 连接器生成按城市拆分的用量规格并更新地图 code layer，选定班加罗尔为首发城市；随后调用团队预置的 build-implementation-plan 技能，把这些输入合成一份供编码智能体执行的实现计划，含设计系统遵循、测试与可观测性要求、发布步骤与任务表，并回链到来源规格。工程师在规格上留评论，agent 读评论并回复修改方案，需设计师确认的条目直接 @ 同事在画布上实时改。最后复制规格链接粘进 Codex 并输入「实现这个功能」，Codex 经 Figma MCP 一次性读取规格、标注设计、code layer 与组件等全部上下文。Specs 与 code layers 已开放 beta，覆盖所有套餐，支持网页、桌面与移动端。
- **理论关联**: 这是「暗时间」在协作层的制度化：上下文不再由人转述，而是被堆进一个 agent 可读的容器，人只保留两件事——开头确定意图（写规格、选城市）与结尾审阅（读计划、留评论）。Figma 把价值主张写成「不需要理解每一行即可信任」，与形式化验证阵营的「veri-coding」是同一条路径的两个入口：一个用证明保证正确，一个用规格传递意图，两者都把人的劳动压缩到意图与签收两端。这也让「认知金融化」更具体：规格成为新的计价单位，写规格的能力比写代码的能力更稀缺。需注意演示中的 Pickup 是虚构客户，数据与判断均被设计成顺利收敛，缺少摩擦样本。

#### [ai-models] 腾讯混元开放 Hy4 权重
- **来源**: X：腾讯混元 (@TencentHunyuan) · 2026-11-20
- **相关度**: 7/10 | 案例价值: MEDIUM
- **链接**: [https://x.com/TencentHunyuan/status/2123625549147070538](https://x.com/TencentHunyuan/status/2123625549147070538)
- **事件摘要**: 腾讯混元 11-20 在 GitHub、HuggingFace、ModelScope、GitCode 四平台开放 Hy4 权重，至此混元 LLM 全系开源（Hy3preview、Hy3、Hy4preview、Hy4、Hy4flash）。Hy4 为原生多模态 MoE 旗舰，总参数 770B、每 token 激活 49B，上下文 1M；同步放出性价比版 Hy4flash，总参数约 224B（含约 64B Engram 参数），每 token 激活约 12B，支持文本与图像输入及 1M 上下文。Hy4 与 Hy4preview 采用 Apache 2.0，允许商用与修改。随权重发布 Hy4 System Card，披露网络安全与生物安全评估：训练数据在网安维度只纳入 PoC 生成、漏洞修复等防守性内容，剔除漏洞利用、逆向工程与渗透等攻击性数据；经腾讯玄武与科恩实验室审计，未发现明显进攻性能力风险。团队于本周五太平洋时间 8–10 点在 r/LocalLLaMA 举行 AMA。
- **理论关联**: 这是「进化对齐脆弱性」的一次正面处置：既然开放权重必然使护栏脱离控制，腾讯选择把能力在训练数据阶段就剪掉——不是部署后加拒绝，而是事前不教。代价是把「对齐」从行为层搬到数据层，从此安全边界由数据清单而非模型行为定义，而清单不可被外部核验，只能靠厂商审计自证。它与 OpenAI 同日发布的「受保护推理」形成镜像：一方以不开放权重来保护能力，一方以阉割数据来开放权重，两者都把「什么不该被学会」变成发布前的编辑决定。Apache 2.0 允许商用与修改，则意味着这条边界一旦放出即不可撤回。

<details><summary>🟡 中相关动态 (1条，点击展开)</summary>

- **[Conductor 0.97.0 发布并宣布加入 Meta，本地工作区智能体新增 artifacts...](https://www.conductor.build/changelog/0.97.0-first-class-artifacts)** [Conductor 官方更新] · 4/10
  - Conductor 11-19 发布 0.97.0，同时宣布加入 Meta。本地工作区智能体现在可生成 artifacts——在聊天中内联显示的 HTML 页面，默认开启，可在 Settings → Artifacts 关闭或创建模板，聊天...

</details>

<details><summary>🔶 中相关资讯 (3条，点击展开)</summary>

- **[[AINews] Anthropic successfully completes largest IPO in his...](https://latent.space/p/ainews-anthropic-successfully-completes-largest-ipo-in-history-valued-at-1-5t/)** [Latent Space] · 7/10
  - Latent Space 的 AINews 11-20 汇总补齐 Anthropic 上市首日全貌：$ANT 以 83 美元定价、111.50 美元开盘（+34.3%）、97.17 美元收盘（+17%），盘后再跌 5% 至 92.60；募资...
- **[Figma 演示用 Specs 与 Figma agent 把上下文变成可实现的开发计划...](https://www.figma.com/blog/workflow-lab-specs-and-the-figma-agent/)** [Figma AI / Agent / Make] · 7/10
  - Figma 11-21 在 Workflow lab 中演示 Specs 与 Figma agent 的完整链路：工程师把 PRD、Hex 数据看板、FigJam 流程图、带标注的设计稿、交互式 code layer 与设计系统组件说明汇集...
- **[腾讯混元开放 Hy4 权重...](https://x.com/TencentHunyuan/status/2123625549147070538)** [X：腾讯混元 (@TencentHunyuan)] · 7/10
  - 腾讯混元 11-20 在 GitHub、HuggingFace、ModelScope、GitCode 四平台开放 Hy4 权重，至此混元 LLM 全系开源（Hy3preview、Hy3、Hy4preview、Hy4、Hy4flash）。Hy...

</details>

---
## 💾 数据导出
- 原始JSON: `output/news/news_cache.json`
- 本报告: `news_radar.py` 生成

> 💡 提示：高价值案例建议手动整理至书稿案例库；紧急清单建议加入每日晨会讨论。