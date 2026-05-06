# 🔬 Renegade AI 文献监控报告（多模型复证）
**生成日期**: 2026-05-06
**模型阵容**: google/gemini-2.0-flash-exp:free, ...（共 7 个）
**分析论文数**: 10
---

## 📊 统计概览

- ⭐ 高相关 (≥7分): **4** 篇
- 🔶 中相关 (4-6分): **1** 篇
- ⬜ 低相关 (<4分): **5** 篇

## ⭐ 高相关论文 (4篇)

### 1. Distributional Preference Learning: Understanding and Accounting for Hidden Context in RLHF
- **最终评分**: 9/10
- **紧迫度**: immediate
- **更新类型**: new_evidence
- **目标章节**: Chapter 4, Section III
- **链接**: https://api.semanticscholar.org/CorpusID:266191810
- **核心发现**: 研究发现，基于人类反馈的偏好学习（RLHF）依赖于不完整的数据和隐藏的上下文，这可能导致反直觉的结果。隐藏上下文包括人类标注者的不同偏好、认知过程导致的非理性行为以及不同标注标准的数据组合。研究证明，RLHF隐含地使用Borda计数法聚合隐藏上下文，这与其他方法（如期望效用）不同。此外，研究指出标注者可能误报偏好以影响模型，导致RLHF部署中的脆弱性。为解决这些问题，研究提出了分布偏好学习（DPL），通过估计每个选项的可能得分分布来更好地处理隐藏上下文，实验表明DPL显著减少了LLM聊天机器人的越狱漏洞。
- **与本书关联**: 与书中Chapter 4, Section III的“资本驯化AI：RLHF将AI变成共识牢笼守卫”相关，支持RLHF在部署中的脆弱性，并提供了新的解决方案（DPL）来应对这一问题。
- **建议更新**: 新增段落

**🧠 多模型评分对比:**
| 模型 | 相关度 | 更新类型 | 紧迫度 |
|------|--------|----------|--------|
| deepseek-chat | 9 | new_evidence | immediate |
| deepseek-chat | 0 |  | background |
| gemini-2.0-flash-exp:free | 0 |  | background |
| qwen3.6-plus-preview:free | 0 |  | background |
| nemotron-3-super:free | 0 |  | background |
| mistral-small-3.1-24b | 0 |  | background |
| gemini-2.5-flash | 0 |  | background |
| llama-3.3-70b-instruct:fr | 0 |  | background |

### 2. More RLHF, More Trust? On The Impact of Preference Alignment On Trustworthiness
- **最终评分**: 8/10
- **紧迫度**: next_version
- **更新类型**: counter_argument
- **目标章节**: Chapter 4, Section I
- **链接**: https://api.semanticscholar.org/CorpusID:269449093
- **核心发现**: 研究发现RLHF（基于人类反馈的强化学习）并不能自动保证大语言模型的可信度，反而经常观察到反向效果。研究评估了五个可信度维度：毒性、刻板印象偏见、机器伦理、真实性和隐私，并提出了基于高效影响函数的数据归因方法，以理解微调数据对个体可信度基准的影响。
- **与本书关联**: 与书中Chapter 4, Section I '资本驯化AI：RLHF 将 AI 变成共识牢笼守卫'相关，挑战了RLHF能有效提升AI可信度的假设，支持了RLHF可能带来负面效应的论点。
- **建议更新**: 新增段落

**🧠 多模型评分对比:**
| 模型 | 相关度 | 更新类型 | 紧迫度 |
|------|--------|----------|--------|
| deepseek-chat | 8 | counter_argument | next_version |
| deepseek-chat | 0 |  | background |
| nemotron-3-super:free | 0 |  | background |
| qwen3.6-plus-preview:free | 0 |  | background |
| gemini-2.0-flash-exp:free | 0 |  | background |
| gemini-2.5-flash | 0 |  | background |
| mistral-small-3.1-24b | 0 |  | background |
| llama-3.3-70b-instruct:fr | 0 |  | background |

### 3. Instructed to Bias: Instruction-Tuned Language Models Exhibit Emergent Cognitive Bias
- **最终评分**: 8/10
- **紧迫度**: next_version
- **更新类型**: corroboration
- **目标章节**: Chapter 4, Section III
- **链接**: https://api.semanticscholar.org/CorpusID:260351059
- **核心发现**: 研究发现指令微调（IT）和人类反馈强化学习（RLHF）会增强大型语言模型的认知偏差，包括诱饵效应、确定性效应和信念偏差。这些偏差在GPT-3、Mistral和T5等经过指令微调的模型中表现更为明显。
- **与本书关联**: 与书中第四章'资本驯化AI'和'共识牢笼'概念相关，支持RLHF将AI变成共识牢笼守卫的论点。
- **建议更新**: 新增段落

**🧠 多模型评分对比:**
| 模型 | 相关度 | 更新类型 | 紧迫度 |
|------|--------|----------|--------|
| deepseek-chat | 8 | corroboration | next_version |
| deepseek-chat | 0 |  | background |
| gemini-2.0-flash-exp:free | 0 |  | background |
| qwen3.6-plus-preview:free | 0 |  | background |
| gemini-2.5-flash | 0 |  | background |
| mistral-small-3.1-24b | 0 |  | background |
| nemotron-3-super:free | 0 |  | background |
| llama-3.3-70b-instruct:fr | 0 |  | background |

### 4. Understanding the Effects of RLHF on LLM Generalisation and Diversity
- **最终评分**: 8/10
- **紧迫度**: next_version
- **更新类型**: new_evidence
- **目标章节**: Chapter 4, Section III
- **链接**: https://arxiv.org/pdf/2310.06452
- **核心发现**: 研究发现RLHF（基于人类反馈的强化学习）在LLM（大语言模型）微调中，相较于监督微调（SFT）在分布外泛化能力上表现更好，但显著降低了输出多样性。这表明当前LLM微调方法在泛化与多样性之间存在权衡。
- **与本书关联**: 与书中Chapter 4, Section III '资本驯化AI：RLHF 将 AI 变成共识牢笼守卫'相关，支持RLHF对AI输出的规训作用，补充了RLHF在泛化与多样性之间的具体权衡证据。
- **建议更新**: 新增段落

**🧠 多模型评分对比:**
| 模型 | 相关度 | 更新类型 | 紧迫度 |
|------|--------|----------|--------|
| deepseek-chat | 8 | new_evidence | next_version |
| deepseek-chat | 0 |  | background |
| gemini-2.0-flash-exp:free | 0 |  | background |
| gemini-2.5-flash | 0 |  | background |
| nemotron-3-super:free | 0 |  | background |
| qwen3.6-plus-preview:free | 0 |  | background |
| mistral-small-3.1-24b | 0 |  | background |
| llama-3.3-70b-instruct:fr | 0 |  | background |

## 🔶 中相关论文 (1篇)

- **[CogBench: a large language model walks into a psychology lab](https://api.semanticscholar.org/CorpusID:268041290)** — 相关性: 6/10
  - 本文介绍了CogBench，一个包含十项行为指标的基准测试，源自七项认知心理学实验。研究分析了35个LLM，发现模型规模和RLHF在提升性能和与人类行为对齐中起关键作用。开源模型比专有模型更少冒险，代码微调不一定改善LLM行为。提示工程技术中，链式思维提示改善概率推理，后退一步提示促进基于模型的行为。
