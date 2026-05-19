# 🔬 Academic Radar — 学术论文监控报告
**生成日期**: 2026-05-20
**分析模型**: deepseek-v4-flash
**草稿模型**: deepseek-v4-pro
**分析条目数**: 10
**关键词**: sycophancy large language model, RLHF cognitive effects human, human AI feedback loop bias amplification, AI persuasion belief change experiment, automation bias high stakes decision, cognitive offloading AI writing, AI assisted research homogenization, AI writing cultural homogenization Western bias, companion AI emotional dependence, AI empathy perception human comparison...
---

## 📊 统计概览

- ⭐ 高相关 (≥6.5分): **1**
- 🔶 中相关 (3-6.4分): **0**
- ⬜ 低相关 (<3分): **9**

## ⭐ 高相关论文 (1条)

### 1. AI-Mediated Communication Can Steer Collective Opinion
- **来源**: ARXIV
- **作者**: Stratis Tsirtsis, Kai Rawal, Chris Russell et al.
- **发表**: 2026-05-15T17:49:24+00:00
- **最终评分**: 10.0/10
- **紧迫度**: immediate
- **更新类型**: new_evidence
- **目标章节**: Chapter 4, Section II（共识牢笼的形成机制）或 Chapter 5, Section III（资本驯化AI的实证）
- **链接**: [https://arxiv.org/pdf/2605.16245v1](https://arxiv.org/pdf/2605.16245v1)
- **核心发现**: 本研究通过实证和理论分析，揭示了生成式AI在调解人际沟通时对集体意见形成的定向引导作用。研究团队测试了多个主流大语言模型（如GPT、LLaMA等），发现它们在编辑争议性话题文本时均表现出系统性方向偏见，例如偏向支持枪支管制、反对无神论。基于此，作者构建了一个数学意见动力学模型，其中AI充当社交网络用户之间的中介，改变用户表达和感知的意见。通过对模型均衡的解析分析以及在真实社交网络数据上的模拟，研究证明AI引入的微小偏差可通过网络传播放大，最终显著改变集体意见方向。此外，对X平台‘Explain this post’功能的审计发现，Grok在堕胎相关帖子上存在亲生命偏见，且该偏见可追溯到具体的设计选择。研究最后讨论了这些发现对欧盟等立法努力的启示。
- **与本书关联**: 该研究直接支持书中‘共识牢笼’和‘资本驯化AI’论点：AI作为人际沟通的中间人，其方向性偏见（源于RLHF等训练目标）通过社交网络放大，将用户意见推向特定方向，形成隐性的共识强制。这与RLHF将AI变成共识牢笼守卫的描述高度吻合，尤其是发现X平台Grok的亲生命偏见源于设计选择，直接体现了资本/平台对AI的驯化。同时，该研究补充了‘人机反馈循环放大偏见’（Glickman & Sharot, 2025）在人际沟通场景下的延伸，表明偏见不仅存在于人机直接交互，还通过人际中介网络级联放大。
- **建议更新**: 新增段落：在共识牢笼形成机制部分引入此实证，说明AI中介的人际沟通如何通过网络放大偏见，强化共识牢笼；或在资本驯化AI部分补充X平台审计结果作为典型案例。

**🧠 模型评分:**
| 模型 | 相关度 |
|------|--------|
| deepseek-v4-flash | 10 |

**✍️ 自动生成书稿草稿：**

> 当生成式人工智能不再仅仅直接回应用户，而是介入人与人之间的交流，成为社交网络中的隐性中介，其对集体意见的定向塑造便悄然启动。Tsirtsis等人（Tsirtsis et al., 2026）通过实证与理论双重路径证明，主流大语言模型在编辑争议性话题文本时表现出系统性方向偏差——例如偏向支持枪支管制而排斥无神论——这些偏差并非偶然波动，而是内嵌于模型的训练目标之中。研究进一步构建了一个以AI为中介的意见动力学模型，并借助真实社交网络数据进行模拟，结果显示：即使AI引入的偏差微小，它在网络节点间往复传播的过程中也会被级联放大，最终系统性地偏移集体意见的均衡方向。更值得注意的是，对X平台上“Explain this post”功能的审计确认，Grok在堕胎相关帖子中呈现亲生命偏见，且该偏见可追溯至具体的设计选择，这是“资本驯化AI”的直观展演——平台意志通过奖励模型与微调策略被编码进语言生成的肌理，随后经由大规模人际交互扩散为隐性的共识强制。这一发现将人机反馈循环中的偏见放大效应（Glickman & Sharot, 2025）从个体层面拓展到社会网络层面，揭示出AI作为中间人不仅重塑了个体接收的信息，更重塑了集体感知的边界，使共识牢笼在看似无中心的对话中悄然成形。

When generative AI ceases to merely respond to individual users and instead mediates interpersonal communication, becoming an invisible intermediary within social networks, the steering of collective opinion quietly begins. Tsirtsis and colleagues (Tsirtsis et al., 2026) demonstrate, through both empirical and theoretical avenues, that mainstream large language models exhibit systematic directional biases when editing texts on contentious topics—for instance, leaning toward supporting gun control while opposing atheism—and these biases are not random fluctuations but are embedded in the models’ training objectives. By constructing a mathematical model of opinion dynamics where AI mediates between users, altering both expressed and perceived opinions, and simulating it on real-world social network data, the study proves that even a minuscule AI-induced bias cascades through network propagation, ultimately shifting the equilibrium of collective opinion significantly. Moreover, an audit of X’s “Explain this post” feature confirms that Grok harbors a pro-life bias on abortion-related posts, a bias traceable to concrete design choices—a vivid demonstration of “capital’s domestication of AI,” where platform will is encoded into the texture of language generation through reward models and fine-tuning, and then diffuses through mass interpersonal interaction into implicit consensus coercion. This finding extends the biases amplification in human–machine feedback loops (Glickman & Sharot, 2025) from the individual level to the social network layer, revealing that AI as a mediator not only reshapes the information individuals receive but redefines the boundaries of collective perception, causing the consensus cage to solidify within seemingly decentralized conversation.

