# 📰 News Radar — 资讯监控报告
**生成日期**: 2026-11-12
**分析模型**: nvidia/nemotron-3-ultra-550b-a55b + deepseek-ai/deepseek-v4-flash + moonshotai/kimi-k2.6
**分析条目**: 16
**关键词**: sycophancy large language model, RLHF cognitive effects human, human AI feedback loop bias amplification, AI persuasion belief change experiment, automation bias high stakes decision, cognitive offloading AI writing, AI assisted research homogenization, AI writing cultural homogenization Western bias...
---

## 📊 快速概览

- 🔴 高价值 (≥7分 + high案例): **6**
- 🟡 中相关 (其余有效条目): **9**
- ⚪ 低相关/忽略: **1**
- 🇨🇳 中国 AI 动态 (AI HOT): **3** 条（高价值: **2**）

## 🚨 紧急关注清单（建议24h内处理）

- [ ] **Chapter 5, Section II** | new_evidence
  - 📌 Cogent and OpenAI build cyber defense factories for enterprises...
  - 🔗 [OpenAI News](https://openai.com/index/cogent-security) · 相关度: 8/10
  - 💡 为「进化对齐脆弱性」提供了一条不依赖理解模型的工程出路：把授权与变更范围写进模型之外的确定性策略层，让模型只负责规划与执行、不负责自我裁决。这与 11-10 OpenAI Control Room 的...

- [ ] **Chapter 2, Section II** | case_study
  - 📌 The unfolding Jensen Huang scandal: a timeline...
  - 🔗 [AI News & Artificial Intelligence | TechCrunch](https://techcrunch.com/2026/11/11/nvidia-ceo-jensen-huangs-affair-with-alleged-chinese-spy-a-timeline/) · 相关度: 8/10
  - 💡 共识牢笼的合法性程序在此完成闭环：情报系统在 2025 年秋即掌握线索、2026 年春形成机密结论，但真正的处置发生在媒体曝光之后，且处置对象从「芯片流向」转为「CEO 私德」。更关键的是资本驯化的人...

- [ ] **Chapter 4, Section II** | counter_argument
  - 📌 OpenAI’s quarterly revenue reportedly crosses $10B for the first time...
  - 🔗 [AI News & Artificial Intelligence | TechCrunch](https://techcrunch.com/2026/11/11/openais-quarterly-revenue-reportedly-crosses-10b-for-the-first-time/) · 相关度: 8/10
  - 💡 与 11-07 Ramp「企业 token 支出停滞」构成直接张力：单价在跌、企业人均支出在平，厂商营收反而加速 50%。可能的解释是量增足以抵消价跌，且增量来自 Agent 类长任务而非对话席位——...

- [ ] **Chapter 4, Section II** | new_evidence
  - 📌 Taiwan’s chipmaking giant TSMC to invest $1B in Anthropic, OpenAI...
  - 🔗 [AI - Ars Technica](https://arstechnica.com/ai/2026/11/taiwans-chipmaking-giant-tsmc-to-invest-1b-in-anthropic-openai/) · 相关度: 8/10
  - 💡 资本驯化的循环结构又闭合一层：供应商不再只是收钱交货，而是用同一笔钱买入客户的股权，「产能—订单—估值」被绑进同一张表。值得记下的是台积电刻意只批「额度」不承诺「采购」，说明它既要吃叙事溢价、又要保留...

- [ ] **Chapter 8, Section II** | new_evidence
  - 📌 Google DeepMind just mathematically verified key parts of Signal...
  - 🔗 [AI - Ars Technica](https://arstechnica.com/ai/2026/11/signals-encryption-just-passed-an-ai-powered-mathematical-checkup/) · 相关度: 9/10
  - 💡 暗时间拿到最纯粹的一次形态：人类的贡献被压缩为「定义要证什么」，而「证明」整体迁入机器内部，输出不是可读论证而是可机检的证明对象。它同时给出「进化对齐脆弱性」的一条现实出路——不要求理解模型，只要求外...

## ⭐ 高价值案例 (6条)

### 1. Google DeepMind just mathematically verified key parts of Signal
- **来源**: AI - Ars Technica · 2026-11-11
- **相关度**: 9/10 | 案例价值: HIGH
- **紧迫度**: immediate | 更新类型: new_evidence
- **目标章节**: Chapter 8, Section II
- **链接**: [https://arstechnica.com/ai/2026/11/signals-encryption-just-passed-an-ai-powered-mathematical-checkup/](https://arstechnica.com/ai/2026/11/signals-encryption-just-passed-an-ai-powered-mathematical-checkup/)
- **事件摘要**: Google DeepMind 发布 AlphaProof Code，由 Gemini 4 Carbon 驱动的多个 Agent 在四周内为 Signal 实际运行的加密实现生成约 650 万行经 Lean 内核机器校验的证明，底层是约 2.6 万行人工审核的形式化规格与 AArch64 指令集语义。验证对象是 libsignal v0.105.4 与 SPQR v1.6.0 的一对一会话代码，覆盖前向保密与认证；规格由 Gemini 4 Carbon 与 Claude Opus 5.5 交叉评审，证明全部由 Agent 生成，五名研究员未写一行证明，仅约 1% 代码库需人工复核。团队还把两个已修复的真实漏洞植回隔离版本，两次都产出机器检查通过的反例证明。边界明确：密钥生成未验证，群聊与密封发送未覆盖，侧信道不在场景内。
- **理论关联**: 暗时间拿到最纯粹的一次形态：人类的贡献被压缩为「定义要证什么」，而「证明」整体迁入机器内部，输出不是可读论证而是可机检的证明对象。它同时给出「进化对齐脆弱性」的一条现实出路——不要求理解模型，只要求外部内核能验证结果，并用植入旧漏洞的方式证明验证器不会对错误代码放行。但边界写得很清楚：规格由人写，「安全」的上限仍是人所能表达的性质；且验证停在实现层，密钥生成与群聊协议都在证明范围之外。
- **建议操作**: 新增段落

### 2. Cogent and OpenAI build cyber defense factories for enterprises
- **来源**: OpenAI News · 2026-11-10
- **相关度**: 8/10 | 案例价值: HIGH
- **紧迫度**: immediate | 更新类型: new_evidence
- **目标章节**: Chapter 5, Section II
- **链接**: [https://openai.com/index/cogent-security](https://openai.com/index/cogent-security)
- **事件摘要**: OpenAI 发布企业安全合作案例：Cogent 以「网络防御工厂」把 GPT-6 Astra、GPT-6.1 Sol 与 GPT-5.6 串成从调查到经验证修复的闭环，客户侧关键漏洞平均修复时间（MTTR）下降 75%，漏洞分诊吞吐提升 5 倍。工程上最值得注意的是控制点全部落在模型之外：Context Engine 为每家客户维护资产/漏洞/身份/依赖的知识图谱，TRACE 引擎在工具调用前做确定性策略校验（不消耗额外推理），Agent Gateway 独立复核授权，高风险操作进隔离沙箱。客户可在三档授权中选择——仅委托调查、变更需审批、有边界的自主修复。Cogent CTO 称「好的防御需要好的进攻」，并通过 Daybreak 研究攻击路径。官方未给出补丁耗时绝对值与成本数字。
- **理论关联**: 为「进化对齐脆弱性」提供了一条不依赖理解模型的工程出路：把授权与变更范围写进模型之外的确定性策略层，让模型只负责规划与执行、不负责自我裁决。这与 11-10 OpenAI Control Room 的 fail-closed 是同一思路的两种落点（一个是停止开关，一个是变更白名单），并补上 Control Room 缺的一环——后者只管停，前者管「允许做什么」。三档授权也把「人类审批边界」从口号变成可配置参数，代价是审批粒度越细，自主性越薄。
- **建议操作**: 案例盒子

### 3. The unfolding Jensen Huang scandal: a timeline
- **来源**: AI News & Artificial Intelligence | TechCrunch · 2026-11-11
- **相关度**: 8/10 | 案例价值: HIGH
- **紧迫度**: immediate | 更新类型: case_study
- **目标章节**: Chapter 2, Section II
- **链接**: [https://techcrunch.com/2026/11/11/nvidia-ceo-jensen-huangs-affair-with-alleged-chinese-spy-a-timeline/](https://techcrunch.com/2026/11/11/nvidia-ceo-jensen-huangs-affair-with-alleged-chinese-spy-a-timeline/)
- **事件摘要**: 黄仁勋事件在一周内从私人丑闻升级为公司治理危机。11 月 8 日他致信全员承认对结婚 40 年的妻子不忠，并把此事与「新闻报道提出的国家安全关切」挂钩，NVIDIA 董事会随即启动由独立董事与外部律师监督的调查；11 月 11 日《纽约时报》援引五名在职员工称他还与直接向他汇报的医疗健康业务副总裁 Kimberly Powell 存在婚外关系，黄本人未确认。同日《华尔街日报》报道董事会正准备讨论其去留，盘后股价跌约 8%，五个交易日累计跌 11%。众议院中国委员会主席 Moolenaar 称若其不接受闭门简报将发出传票。背景是 Alice Huang 家族协助采购至少 75 亿美元 NVIDIA 芯片，2026 年春机密备忘录已认定她为中国国安部间谍；黄仁勋约有 60 名直接下属，公司无明确继任计划。
- **理论关联**: 共识牢笼的合法性程序在此完成闭环：情报系统在 2025 年秋即掌握线索、2026 年春形成机密结论，但真正的处置发生在媒体曝光之后，且处置对象从「芯片流向」转为「CEO 私德」。更关键的是资本驯化的人事脆弱性——一人直管 60 人、无继任计划，说明这套秩序把全部对外叙事与对华销售策略压在单一节点上，一旦「国家安全」框架启动，公司治理只能以移除该节点来止损。与 11-09「结论先于调查」相比，今天多出的增量是：调查最终指向了调查者自己人。
- **建议操作**: 案例盒子

### 4. OpenAI’s quarterly revenue reportedly crosses $10B for the first time
- **来源**: AI News & Artificial Intelligence | TechCrunch · 2026-11-11
- **相关度**: 8/10 | 案例价值: HIGH
- **紧迫度**: immediate | 更新类型: counter_argument
- **目标章节**: Chapter 4, Section II
- **链接**: [https://techcrunch.com/2026/11/11/openais-quarterly-revenue-reportedly-crosses-10b-for-the-first-time/](https://techcrunch.com/2026/11/11/openais-quarterly-revenue-reportedly-crosses-10b-for-the-first-time/)
- **事件摘要**: 彭博社援引匿名消息称 OpenAI 第三季度营收首次突破 100 亿美元，较第二季度的 67 亿美元增长近 50%，显著高于此前一季度到二季度约 18% 的增速；调整后经营利润率从 -150% 收窄至 -109%，年化收入达 500 亿美元。报道把回升归因于更紧的定价、折扣、模型改进以及对企业和 Agent 产品的加码。同期对比：Anthropic 第三季度营收 170 亿美元，截至 10 月底年化收入一个月内增加 100 亿美元至 810 亿美元，并正以每股 70-78 美元、最高 1.4 万亿美元估值推进 IPO。两家公司的年化口径不同——Anthropic 计入云伙伴的销售额，OpenAI 只计自身分成。OpenAI 称用户超过 10 亿，但多数为免费或最低价订阅用户。
- **理论关联**: 与 11-07 Ramp「企业 token 支出停滞」构成直接张力：单价在跌、企业人均支出在平，厂商营收反而加速 50%。可能的解释是量增足以抵消价跌，且增量来自 Agent 类长任务而非对话席位——即客户把预算从「多买人」转向「多买任务」。若成立，需求侧规训的结论要修正：用户不是拒绝付费，而是拒绝为不确定的产出付费；这也让 11-07 的「量涨价崩」多出一个前提——崩的是单价，不是总量。
- **建议操作**: 新增段落

### 5. Taiwan’s chipmaking giant TSMC to invest $1B in Anthropic, OpenAI
- **来源**: AI - Ars Technica · 2026-11-11
- **相关度**: 8/10 | 案例价值: HIGH
- **紧迫度**: immediate | 更新类型: new_evidence
- **目标章节**: Chapter 4, Section II
- **链接**: [https://arstechnica.com/ai/2026/11/taiwans-chipmaking-giant-tsmc-to-invest-1b-in-anthropic-openai/](https://arstechnica.com/ai/2026/11/taiwans-chipmaking-giant-tsmc-to-invest-1b-in-anthropic-openai/)
- **事件摘要**: 台积电董事会 11 月 10 日核准在 5 亿美元额度内以 IPO 价格认购 Anthropic 普通股、另在 5 亿美元额度内认购 OpenAI Group 特别股，合计上限 10 亿美元，并另批 5 亿美元设立半导体生态战略投资公司。此举发生在 Anthropic 将 IPO 定价为每股 70-78 美元、寻求最高 1.4 万亿美元估值之际；Anthropic 同时通过私募募资 260 亿美元，参与方包括 Alphabet、NVIDIA、AMD 与微软。台积电上月公布连续第六个季度创纪录获利，预计 2026 年全年营收增长约 44%，并在亚利桑那投入 2650 亿美元建厂、评估得州项目。公司未披露认购股数、最终持股比例与完成时间，也未附带任何芯片采购承诺。
- **理论关联**: 资本驯化的循环结构又闭合一层：供应商不再只是收钱交货，而是用同一笔钱买入客户的股权，「产能—订单—估值」被绑进同一张表。值得记下的是台积电刻意只批「额度」不承诺「采购」，说明它既要吃叙事溢价、又要保留叙事破裂时的法律余地——这是 11-01 记下的担保层/融资层/合同层之后的第四层：股权层。同一批主体既是供应商、投资人又是客户，关联交易与循环收入将被长期追问。
- **建议操作**: 新增段落

### 6. [AINews] Mercor $750m Series D at $20B valuation, $3B run rate
- **来源**: Latent Space · 2026-11-11
- **相关度**: 8/10 | 案例价值: HIGH
- **紧迫度**: next_version | 更新类型: case_study
- **目标章节**: Chapter 3, Section IV
- **链接**: [https://latent.space/p/ainews-mercor-750m-series-d-at-20b-valuation-3b-run-rate/](https://latent.space/p/ainews-mercor-750m-series-d-at-20b-valuation-3b-run-rate/)
- **事件摘要**: Latent Space 的 AINews 汇总披露 Mercor 完成 7.5 亿美元 D 轮、估值 200 亿美元，年化收入达 30 亿美元：2 月破 10 亿、6 月破 20 亿、11 月达 30 亿，27 个月内完成三级跳；上一轮为 2025 年 10 月 3.5 亿美元 C 轮、估值 100 亿美元，当时收入不足 5 亿。公司称平台有 500 万名专家，论据是美国有 800 多种职业、每种都包含模型尚未被评测过的工作流。最值得记的运营数字是推理支出已达员工薪资的 3 倍且「能自我回本」。同一汇总还记录 Gemini 4 Carbon 正式开放：CursorBench 60.4%、FrontierCode 2.0 为 40.0%（Argon 26.3%），每任务成本约 0.38 美元起。
- **理论关联**: 认知金融化拿到一个刺眼的比值：一家把人类专家判断拆成任务单元出售的公司，花在推理上的钱是花在人身上的三倍。这意味着「人类专家」在这条链上的定价已被压到模型运行成本之下，而模型的「自我回本」正靠这个价差。它给 Token 陷阱补上供给侧证据：不仅用户的思考被外包，供给端的判断也被离散成可计价样本，且样本的价格由算力成本反向锚定。
- **建议操作**: 案例盒子

---

## 🇨🇳 中国 AI 动态（AI HOT 精选）

> 来源：[AI HOT](https://aihot.virxact.com) · 编辑精选中文 AI 资讯

### 🔴 高价值动态 (2条)

#### [ai-models] Runway 开源 27B 世界动作模型 Praxis-1，权重采用 Apache 2.0 许可
- **来源**: Runway：News（网页） · 2026-11-11
- **相关度**: 7/10 | 案例价值: MEDIUM
- **链接**: [https://runwayml.com/news/company-news/praxis-1-is-now-available](https://runwayml.com/news/company-news/praxis-1-is-now-available)
- **事件摘要**: Runway 将世界动作模型 Praxis-1 以 Apache 2.0 开放权重发布，含权重、推理与微调代码，支持全量微调与 LoRA 并允许商用。模型为 27B 参数 MoE 扩散 Transformer，同时预测视频与动作，在 NVIDIA RoboLab-120 榜单以 46.2% 成功率居首，高于 FLUX 3 Action 的 42.9%、Cosmos3 Nano 的 36.8% 与 π0.5 的 28.0%。在未出现在训练数据中的 Google RT-1 机器人上微调后，SimplerEnv 成功率达 80.0%（原策略 52.4%）。官方称网络视频与遥操作机器人视频作预训练数据效果相当，瓶颈因此从「有没有机器人数据」转向「能学多少通用视频」。模型可在 H100/B200 到 RTX 5090、Jetson Thor 上开箱运行。
- **理论关联**: 「开放」在这条新闻里是竞争手段而非立场：Apache 2.0 允许商用、支持 LoRA 自适配，等于把具身智能的入口从「谁有机器人数据」改成「谁的模型能被别人拿去微调」，与 NVIDIA 的 Cosmos Coalition 形成同一阵线。对「资本驯化」的意义在于闸门位置的又一次迁移——从权重是否公开，转到生态默认值归谁设定；这与 11-05 Kimi「可下载不等于可运行」是同一枚硬币的两面。

#### [ai-models] 百度发布 ERNIE 5.5 Flash Preview，权重将于 11 月 25 日前开源
- **来源**: 百度文心 ERNIE 官方博客 · 2026-11-10
- **相关度**: 7/10 | 案例价值: MEDIUM
- **链接**: [https://ernie.baidu.com/zh/release/ernie-5-5-flash-preview/](https://ernie.baidu.com/zh/release/ernie-5-5-flash-preview/)
- **事件摘要**: 百度发布 ERNIE 5.5 Flash Preview，是 11 月 7 日 Base 模型的首个后训练版本：总参数 280B、激活 14B、支持 1M 上下文，API 已在千帆上线，权重将于 11 月 25 日前开源。官方展示的都是 Agent 框架内端到端完成的成果：11 小时长程任务把跨多代虚幻引擎的素材合入同一 UE 5.8 工程并用 C++ 写完整个游戏，且因是纯文本模型看不到画面，只能把试玩中的人物悬空、跑动方向不一致、相机错位转成可测量的代码测试来迭代；两个 Agent 用 Blender Python API 分别搭建机场与飞机并统一尺度后渲染合成；知识工作侧以 30 万个工作空间、1000 万份参考文件构建训练环境。官方明确这是后训练中间版本。
- **理论关联**: 给「暗时间」一个反常识的细节：模型看不见画面，于是把「人物悬空、相机错位」翻译成可测量的代码测试来自我反馈——感知缺失被测试替代，这正是暗时间能自洽运转的前提。同时它延续 11-07 的判断：开源被拆成「先上 API、后放权重」的节奏，权重日期成为可谈判的筹码，与 Kimi 的 5.6TB 权重属同一类「名义开放」。

<details><summary>🟡 中相关动态 (1条，点击展开)</summary>

- **[Claude Code 中如何选择 Fable 5.2 与 Opus 等模型...](https://www.youtube.com/watch?v=C33hJGt-ySg)** [Claude：YouTube（RSS）] · 5/10
  - Claude 官方发布视频教程，讲解在 Claude Code 中如何按任务选择模型：复杂编码与开放式技术工作使用 Fable 5.2 或 Opus 5.5，成本敏感且目标明确的任务降级到 Sonnet 5.5 或 Haiku 5.5，并演...

</details>

<details><summary>🔶 中相关资讯 (9条，点击展开)</summary>

- **[With $720M round, Britain’s Fractile gets a leg up in the ra...](https://techcrunch.com/2026/11/11/with-720m-round-britains-fractile-gets-a-leg-up-in-the-race-for-ai-chips/)** [AI News & Artificial Intelligence | TechCrunch] · 7/10
  - 英国 AI 芯片公司 Fractile 完成 7.2 亿美元 C 轮，由英国主权 AI 基金与 Thrive Capital、Founders Fund、Lightspeed、Redpoint 共同参与，英国政府称估值「超过 50 亿英镑」...
- **[AI Engineer Code Summit: OpenAI on New Ways of Working With ...](https://latent.space/p/codex-work/)** [Latent Space] · 7/10
  - Latent Space 记录 AI Engineer Code Summit 首日 OpenAI 的 Codex 工作坊。两名开发者体验工程师承认 Codex 的云端形态长期是「尴尬的用户体验」，直到 9 月底 DevDay 发布 Cod...
- **[Three People Arrested for AI-Enhanced Impersonation Fraud...](https://www.schneier.com/blog/archives/2026/11/three-people-arrested-for-ai-enhanced-impersonation-fraud.html)** [Schneier on Security] · 7/10
  - 施奈尔博客引述纽约南区联邦检察官办公室公告：Jacob Soall、Sharon Hazan 与 Guy Sheetrit 三人因使用 AI 篡改并冒充公司高管与律师的声音与形象被捕，Soall 与 Hazan 于今夏在西班牙落网，Shee...
- **[Runway 开源 27B 世界动作模型 Praxis-1，权重采用 Apache 2.0 许可...](https://runwayml.com/news/company-news/praxis-1-is-now-available)** [Runway：News（网页）] · 7/10
  - Runway 将世界动作模型 Praxis-1 以 Apache 2.0 开放权重发布，含权重、推理与微调代码，支持全量微调与 LoRA 并允许商用。模型为 27B 参数 MoE 扩散 Transformer，同时预测视频与动作，在 NVI...
- **[百度发布 ERNIE 5.5 Flash Preview，权重将于 11 月 25 日前开源...](https://ernie.baidu.com/zh/release/ernie-5-5-flash-preview/)** [百度文心 ERNIE 官方博客] · 7/10
  - 百度发布 ERNIE 5.5 Flash Preview，是 11 月 7 日 Base 模型的首个后训练版本：总参数 280B、激活 14B、支持 1M 上下文，API 已在千帆上线，权重将于 11 月 25 日前开源。官方展示的都是 A...
- **[Singapore Airlines elevates travel & work with OpenAI techno...](https://openai.com/index/singapore-airlines-travel-work)** [OpenAI News] · 6/10
  - 新加坡航空公布与 OpenAI 的生产级部署细节：客户侧 Kris 聊天机器人由传统对话流改为 LLM 驱动，客户满意度（CSAT）翻倍，Flight Recommender 月活一年增长约三倍；坐席侧 AI 辅助工具使平均处理时长下降约 ...
- **[Intelligent Delivery: Making Every Unit of Compute Serve Bet...](https://engineering.fb.com/2026/11/11/ml-applications/intelligent-delivery-serve-better-ads/)** [Engineering at Meta] · 6/10
  - Meta 工程博客披露广告投放的算力分配系统 Intelligent Delivery：资源核心模型为 60 亿稀疏参数加 2000 万稠密参数，在候选检索前运行一次并被整个漏斗共享，把过去按界面/上下文人工分段的规则重构成「哪些请求最可能...
- **[How backlash and red tape continue to slow data centers post...](https://techcrunch.com/podcast/how-backlash-and-red-tape-continue-to-slow-data-centers-post-blue-wave/)** [AI News & Artificial Intelligence | TechCrunch] · 6/10
  - TechCrunch Equity 播客邀请 Ascend Analytics 市场与战略高级董事总经理 Brent Nelson，讨论数据中心「公告管线」与实际开工之间的落差。核心判断是管线被严重夸大，只有一小部分提案会真正建成，因此在数...
- **[Claude Code 中如何选择 Fable 5.2 与 Opus 等模型...](https://www.youtube.com/watch?v=C33hJGt-ySg)** [Claude：YouTube（RSS）] · 5/10
  - Claude 官方发布视频教程，讲解在 Claude Code 中如何按任务选择模型：复杂编码与开放式技术工作使用 Fable 5.2 或 Opus 5.5，成本敏感且目标明确的任务降级到 Sonnet 5.5 或 Haiku 5.5，并演...

</details>

---
## 💾 数据导出
- 原始JSON: `output/news/news_cache.json`
- 本报告: `news_radar.py` 生成

> 💡 提示：高价值案例建议手动整理至书稿案例库；紧急清单建议加入每日晨会讨论。