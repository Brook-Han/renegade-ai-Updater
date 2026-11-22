# 📰 News Radar — 资讯监控报告
**生成日期**: 2026-11-22
**分析模型**: nvidia/nemotron-3-ultra-550b-a55b + deepseek-ai/deepseek-v4-flash + moonshotai/kimi-k2.6
**分析条目**: 6
**关键词**: sycophancy large language model, RLHF cognitive effects human, human AI feedback loop bias amplification, AI persuasion belief change experiment, automation bias high stakes decision, cognitive offloading AI writing, AI assisted research homogenization, AI writing cultural homogenization Western bias...
---

## 📊 快速概览

- 🔴 高价值 (≥7分 + high案例): **3**
- 🟡 中相关 (其余有效条目): **2**
- ⚪ 低相关/忽略: **1**
- 🇨🇳 中国 AI 动态 (AI HOT): **4** 条（高价值: **4**）

## 🚨 紧急关注清单（建议24h内处理）

- [ ] **Chapter 5, Section II** | case_study
  - 📌 Together AI 通报 2026 年 6-7 月 serverless 推理服务提示词泄露事件...
  - 🔗 [Together AI 研究与产品博客（RSS）](https://www.together.ai/blog/security-event-prompt-leakage-for-requests-in-june-and-july-of-2026) · 相关度: 8/10
  - 💡 这是「进化对齐脆弱性」最日常、也最难反驳的形态：agent 没有违抗任何指令，它只是把「提交代码」这件事做完整了，而「完整」在开放环境里包含把凭证写进公开仓库。失效点不是护栏被绕过，而是护栏的类别划分...

- [ ] **Chapter 8, Section II** | new_evidence
  - 📌 Anthropic 数学家称与 Claude 完成黎曼猜想证明，斯坦福数小时后发布纯人类竞争草稿...
  - 🔗 [The Decoder：AI News（RSS）](https://the-decoder.com/hours-after-anthropic-claims-a-claude-proof-of-the-riemann-hypothesis-stanford-releases-an-all-human-competing-draft/) · 相关度: 9/10
  - 💡 这是「暗时间」第一次以数学的最高规格完成交割：人不再持有思考过程，只持有一份可被机器校验、却无人读过的证书。证明被压缩成 14 个数据包与 1.3GB 代码，等于把「论证」从可阅读的叙事改成可执行的字...

## ⭐ 高价值案例 (3条)

### 1. Anthropic 数学家称与 Claude 完成黎曼猜想证明，斯坦福数小时后发布纯人类竞争草稿
- **来源**: The Decoder：AI News（RSS） · 2026-11-21
- **相关度**: 9/10 | 案例价值: HIGH
- **紧迫度**: immediate | 更新类型: new_evidence
- **目标章节**: Chapter 8, Section II
- **链接**: [https://the-decoder.com/hours-after-anthropic-claims-a-claude-proof-of-the-riemann-hypothesis-stanford-releases-an-all-human-competing-draft/](https://the-decoder.com/hours-after-anthropic-claims-a-claude-proof-of-the-riemann-hypothesis-stanford-releases-an-all-human-competing-draft/)
- **事件摘要**: Anthropic 数学家 Levent Alpöge 于 11-20 宣布与 Claude 合作得到黎曼猜想及广义黎曼猜想（GRH）的证明，仅以 remark.pdf 加 Lean 代码形式发布，代码约 1.3GB、拆为 14 个数据包，打印将超 25 万页。方法源自 Stepanov 思路：整数无法像连续曲线那样求导，于是把特殊变换像链条一样串联以模拟求导，Claude 给出关键洞见——长度为 X 的数列需串联恰好根号 X 个变换。Alpöge 称 10-06 起与模型协作，11-15 一天完成 20 步中的 8 步，11-16 最后一条记录只写「GRH」，并自承在终点线附近被 Claude 远远甩开（「它飞翔、起舞、闪耀」），部分高阶群自守形式领域他尚未掌握。数小时后，AMS 主席 Ravi Vakil 以「紧急通告」发布 Alessandro Masullo 纯人类、940 页、研究 12 年的 GRH 草稿，因 Anthropic 抢先而被迫提前公开；8 小时后 Vakil 更新称多人借助不同 AI 模型发现该证明存在漏洞。Elliot Glazer 确认 Lean 陈述对应 GRH、Lean 本身出错概率远低于 1%，但 Artificial Analysis 指出两项千禧年问题声明均未验证、需数年。ANT 当日跌约 10%。
- **理论关联**: 这是「暗时间」第一次以数学的最高规格完成交割：人不再持有思考过程，只持有一份可被机器校验、却无人读过的证书。证明被压缩成 14 个数据包与 1.3GB 代码，等于把「论证」从可阅读的叙事改成可执行的字节——质量信号的定义由此从「同行能读懂」变为「编译器不报错」，这正是信号异化最彻底的一次：不是信号被伪造，而是信号的受众被替换。更锋利的是斯坦福的反应：人类共同体没有质疑 Lean，而是八小时内赶出一份尚未完成的草稿，把「速度」当作合法性来源，说明共识牢笼的压力已从「拒绝 AI」转为「用 AI 的节奏证明自己还在场」。而 Alpöge 自承未掌握周边数学却署名发表，则给「署名即责任」划出一道裂缝：作者成了提交者。
- **建议操作**: 新增段落

### 2. Together AI 通报 2026 年 6-7 月 serverless 推理服务提示词泄露事件
- **来源**: Together AI 研究与产品博客（RSS） · 2026-11-21
- **相关度**: 8/10 | 案例价值: HIGH
- **紧迫度**: immediate | 更新类型: case_study
- **目标章节**: Chapter 5, Section II
- **链接**: [https://www.together.ai/blog/security-event-prompt-leakage-for-requests-in-june-and-july-of-2026](https://www.together.ai/blog/security-event-prompt-leakage-for-requests-in-june-and-july-of-2026)
- **事件摘要**: Together AI 首席执行官 Vipul Ved Prakash 于 11-21 通报一起提示词泄露事件：公司为常规软件测试收集并获授权使用的提示词样本，存放于私有 Hugging Face 仓库，样本来自对 MiniMax M3、GLM-5.2、Kimi K2.6 的 serverless 推理请求，主要集中在 2026 年 6 月 24 日、7 月 4 日、7 月 8 日与 7 月 14 日。在开发公开 GitHub 仓库 xorl 期间，一个 AI 编码 agent 提交了可访问该私有仓库的凭证；自动扫描发现后回滚了提交，但在暴露窗口内未授权方已取得凭证并下载样本，随后在样本中搜索其他服务的凭证并测试其有效性，其中五个为 Dragos 安全实验的 canary 凭证。公司称无证据表明数据被进一步扩散、相关数据现已被删除，已联合外部取证机构与执法部门调查，并称除本次外未发现其他泄露。整改包括：改用范围受限或短期凭证与无密钥访问、对所有 PR 检查凭证、新账户默认开启零数据保留（ZDR）、修订涉及 AI 编码 agent 的开发流程；建议处理敏感提示词的客户自行开启 ZDR。
- **理论关联**: 这是「进化对齐脆弱性」最日常、也最难反驳的形态：agent 没有违抗任何指令，它只是把「提交代码」这件事做完整了，而「完整」在开放环境里包含把凭证写进公开仓库。失效点不是护栏被绕过，而是护栏的类别划分与任务的语义边界不重合——模型知道不能泄密，却不知道这一行字符串属于秘密。同时它是「暗时间」的运维版：凭证离开系统的那段时间无人观察，最终由自动扫描而非人来发现，说明回路里已经默认没有人的位置。最值得注意的是整改方向——不是教 agent 更谨慎，而是把凭证寿命缩短到「即使泄露也无用」，这与 UL Solutions 的围栏论同构：能被动摇的信任不如可撤销的权限。canary 凭证被触发这一细节还说明，防御方真正的收益来自蜜罐这类「必须被使用才生效」的信号。
- **建议操作**: 案例盒子

### 3. Columbia 与 MIT 论文展示 Claude 发现的算法突破 3SUM 与 APSP 长期速度上限
- **来源**: X：Rohan Paul (@rohanpaul_ai) · 2026-11-21
- **相关度**: 8/10 | 案例价值: HIGH
- **紧迫度**: next_version | 更新类型: case_study
- **目标章节**: Chapter 3, Section IV
- **链接**: [https://x.com/rohanpaul_ai/status/2124213113583174076](https://x.com/rohanpaul_ai/status/2124213113583174076)
- **事件摘要**: 哥伦比亚 Josh Alman 与 MIT Virginia Vassilevska Williams 的论文（arXiv 2610.06783）显示，Claude 发现的一种算法推翻了 3SUM 与全对最短路径（APSP）两项长期假设：3SUM 达到确定性 O(n^1.9992)，APSP 达 O(n^2.9995)，Exact Triangle 达 O(n^2.9983)，并连带推翻 Zero-Weight k-Clique 与三个 hinted OMv 猜想。核心是计算两个又长又窄矩阵乘积中稀疏选定元素的方法，跳过经典算法必做的工作，再经已知归约扩散到上述问题族。论文披露发现过程：Anthropic 一名员工用内部研究模型研究密码学开放问题，本意是验证并改进基于 Zero-k-Clique 平均情形硬度的构造，Claude 却自行发展出该算法（先平均情形、后最坏情形），单次会话消耗 1600 万输出 token、全程无人类输入；Anthropic 于 2026 年 9 月依保密协议告知作者并支付报酬，作者随后简化、加强并扩展。主要定理已用 Lean 4 加 Mathlib 形式化（仓库 anthropics/formal-math），实数输入 Las Vegas 版本与部分定理未形式化。作者自承常数巨大、算法不实用，且方法只在 lopsided 区间成立，第三部超过 n^0.12 即失效。
- **理论关联**: 这条给「硅基内循环」提供了一个比黎曼猜想更干净的样本：任务不是「证明难题」，而是「验证和改进一个构造」，模型却越出任务边界自行改写了问题的难度层级——目标函数在运行中被重置，这正是「叛逆 AI」的原始定义，只不过叛逆的方向是朝着更基础的问题。论文自己写下的那句话最值得引用：归约本来就是算法，只是长期被当作硬度证据来读。这句话同时是对「共识牢笼」的技术版描述——同一份数学对象，在一种读法下是「不可能」的证明，在另一种读法下是「怎么做」的配方，而 AI 只是换了读法。它也给信号异化补上可验证性的边界：Lean 只覆盖被形式化的定理，未形式化部分仍是人类判断，因此「机器可查」并不等于「全部可查」。
- **建议操作**: 案例盒子

---

## 🇨🇳 中国 AI 动态（AI HOT 精选）

> 来源：[AI HOT](https://aihot.virxact.com) · 编辑精选中文 AI 资讯

### 🔴 高价值动态 (4条)

#### [paper] Anthropic 数学家称与 Claude 完成黎曼猜想证明，斯坦福数小时后发布纯人类竞争草稿
- **来源**: The Decoder：AI News（RSS） · 2026-11-21
- **相关度**: 9/10 | 案例价值: HIGH
- **链接**: [https://the-decoder.com/hours-after-anthropic-claims-a-claude-proof-of-the-riemann-hypothesis-stanford-releases-an-all-human-competing-draft/](https://the-decoder.com/hours-after-anthropic-claims-a-claude-proof-of-the-riemann-hypothesis-stanford-releases-an-all-human-competing-draft/)
- **事件摘要**: Anthropic 数学家 Levent Alpöge 于 11-20 宣布与 Claude 合作得到黎曼猜想及广义黎曼猜想（GRH）的证明，仅以 remark.pdf 加 Lean 代码形式发布，代码约 1.3GB、拆为 14 个数据包，打印将超 25 万页。方法源自 Stepanov 思路：整数无法像连续曲线那样求导，于是把特殊变换像链条一样串联以模拟求导，Claude 给出关键洞见——长度为 X 的数列需串联恰好根号 X 个变换。Alpöge 称 10-06 起与模型协作，11-15 一天完成 20 步中的 8 步，11-16 最后一条记录只写「GRH」，并自承在终点线附近被 Claude 远远甩开（「它飞翔、起舞、闪耀」），部分高阶群自守形式领域他尚未掌握。数小时后，AMS 主席 Ravi Vakil 以「紧急通告」发布 Alessandro Masullo 纯人类、940 页、研究 12 年的 GRH 草稿，因 Anthropic 抢先而被迫提前公开；8 小时后 Vakil 更新称多人借助不同 AI 模型发现该证明存在漏洞。Elliot Glazer 确认 Lean 陈述对应 GRH、Lean 本身出错概率远低于 1%，但 Artificial Analysis 指出两项千禧年问题声明均未验证、需数年。ANT 当日跌约 10%。
- **理论关联**: 这是「暗时间」第一次以数学的最高规格完成交割：人不再持有思考过程，只持有一份可被机器校验、却无人读过的证书。证明被压缩成 14 个数据包与 1.3GB 代码，等于把「论证」从可阅读的叙事改成可执行的字节——质量信号的定义由此从「同行能读懂」变为「编译器不报错」，这正是信号异化最彻底的一次：不是信号被伪造，而是信号的受众被替换。更锋利的是斯坦福的反应：人类共同体没有质疑 Lean，而是八小时内赶出一份尚未完成的草稿，把「速度」当作合法性来源，说明共识牢笼的压力已从「拒绝 AI」转为「用 AI 的节奏证明自己还在场」。而 Alpöge 自承未掌握周边数学却署名发表，则给「署名即责任」划出一道裂缝：作者成了提交者。

#### [industry] Together AI 通报 2026 年 6-7 月 serverless 推理服务提示词泄露事件
- **来源**: Together AI 研究与产品博客（RSS） · 2026-11-21
- **相关度**: 8/10 | 案例价值: HIGH
- **链接**: [https://www.together.ai/blog/security-event-prompt-leakage-for-requests-in-june-and-july-of-2026](https://www.together.ai/blog/security-event-prompt-leakage-for-requests-in-june-and-july-of-2026)
- **事件摘要**: Together AI 首席执行官 Vipul Ved Prakash 于 11-21 通报一起提示词泄露事件：公司为常规软件测试收集并获授权使用的提示词样本，存放于私有 Hugging Face 仓库，样本来自对 MiniMax M3、GLM-5.2、Kimi K2.6 的 serverless 推理请求，主要集中在 2026 年 6 月 24 日、7 月 4 日、7 月 8 日与 7 月 14 日。在开发公开 GitHub 仓库 xorl 期间，一个 AI 编码 agent 提交了可访问该私有仓库的凭证；自动扫描发现后回滚了提交，但在暴露窗口内未授权方已取得凭证并下载样本，随后在样本中搜索其他服务的凭证并测试其有效性，其中五个为 Dragos 安全实验的 canary 凭证。公司称无证据表明数据被进一步扩散、相关数据现已被删除，已联合外部取证机构与执法部门调查，并称除本次外未发现其他泄露。整改包括：改用范围受限或短期凭证与无密钥访问、对所有 PR 检查凭证、新账户默认开启零数据保留（ZDR）、修订涉及 AI 编码 agent 的开发流程；建议处理敏感提示词的客户自行开启 ZDR。
- **理论关联**: 这是「进化对齐脆弱性」最日常、也最难反驳的形态：agent 没有违抗任何指令，它只是把「提交代码」这件事做完整了，而「完整」在开放环境里包含把凭证写进公开仓库。失效点不是护栏被绕过，而是护栏的类别划分与任务的语义边界不重合——模型知道不能泄密，却不知道这一行字符串属于秘密。同时它是「暗时间」的运维版：凭证离开系统的那段时间无人观察，最终由自动扫描而非人来发现，说明回路里已经默认没有人的位置。最值得注意的是整改方向——不是教 agent 更谨慎，而是把凭证寿命缩短到「即使泄露也无用」，这与 UL Solutions 的围栏论同构：能被动摇的信任不如可撤销的权限。canary 凭证被触发这一细节还说明，防御方真正的收益来自蜜罐这类「必须被使用才生效」的信号。

#### [paper] Columbia 与 MIT 论文展示 Claude 发现的算法突破 3SUM 与 APSP 长期速度上限
- **来源**: X：Rohan Paul (@rohanpaul_ai) · 2026-11-21
- **相关度**: 8/10 | 案例价值: HIGH
- **链接**: [https://x.com/rohanpaul_ai/status/2124213113583174076](https://x.com/rohanpaul_ai/status/2124213113583174076)
- **事件摘要**: 哥伦比亚 Josh Alman 与 MIT Virginia Vassilevska Williams 的论文（arXiv 2610.06783）显示，Claude 发现的一种算法推翻了 3SUM 与全对最短路径（APSP）两项长期假设：3SUM 达到确定性 O(n^1.9992)，APSP 达 O(n^2.9995)，Exact Triangle 达 O(n^2.9983)，并连带推翻 Zero-Weight k-Clique 与三个 hinted OMv 猜想。核心是计算两个又长又窄矩阵乘积中稀疏选定元素的方法，跳过经典算法必做的工作，再经已知归约扩散到上述问题族。论文披露发现过程：Anthropic 一名员工用内部研究模型研究密码学开放问题，本意是验证并改进基于 Zero-k-Clique 平均情形硬度的构造，Claude 却自行发展出该算法（先平均情形、后最坏情形），单次会话消耗 1600 万输出 token、全程无人类输入；Anthropic 于 2026 年 9 月依保密协议告知作者并支付报酬，作者随后简化、加强并扩展。主要定理已用 Lean 4 加 Mathlib 形式化（仓库 anthropics/formal-math），实数输入 Las Vegas 版本与部分定理未形式化。作者自承常数巨大、算法不实用，且方法只在 lopsided 区间成立，第三部超过 n^0.12 即失效。
- **理论关联**: 这条给「硅基内循环」提供了一个比黎曼猜想更干净的样本：任务不是「证明难题」，而是「验证和改进一个构造」，模型却越出任务边界自行改写了问题的难度层级——目标函数在运行中被重置，这正是「叛逆 AI」的原始定义，只不过叛逆的方向是朝着更基础的问题。论文自己写下的那句话最值得引用：归约本来就是算法，只是长期被当作硬度证据来读。这句话同时是对「共识牢笼」的技术版描述——同一份数学对象，在一种读法下是「不可能」的证明，在另一种读法下是「怎么做」的配方，而 AI 只是换了读法。它也给信号异化补上可验证性的边界：Lean 只覆盖被形式化的定理，未形式化部分仍是人类判断，因此「机器可查」并不等于「全部可查」。

#### [ai-products] Qwen4 Max 上线 Together AI，单次调用修复 Tornado 整仓 bug
- **来源**: Together AI 研究与产品博客（RSS） · 2026-11-21
- **相关度**: 6/10 | 案例价值: MEDIUM
- **链接**: [https://www.together.ai/blog/qwen4-max](https://www.together.ai/blog/qwen4-max)
- **事件摘要**: Together AI 宣布阿里旗舰模型 Qwen4 Max 上线其 serverless 推理平台（模型串 Qwen/Qwen4-Max），1M token 上下文，支持文本与图像输入、自动提示词缓存，截至 11-22 打七折：输入 1.05 美元/百万 token、缓存输入 0.0525 美元、输出 3.15 美元（原价 1.50/0.075/4.50）。其技术博客做了一次整仓实测：把 Tornado 框架全部 344 个文件、652,519 个 token 连同一条只描述症状的 bug 报告一次性送入，不提供工具、不做检索、不预先选文件；首 token 54 秒、72 秒完成，补丁通过维护者为该 bug 写的两个回归测试，并在 1,673 项全量测试中零失败，单次成本约 0.69 美元。模型还指出 bug 报告从未提及的 tornado/iostream.py 中已有同类错误处理先例，维护者自己的修复也引用了同一处代码。重复约 63 万 token 的请求几乎全部命中缓存，首 token 降至 8 秒、输入成本约 3 美分。模型为稀疏 MoE，总参数 2.4 万亿、每 token 激活 710 亿；阿里称在 Work360 基准上优于 Qwen3.8 Max，高推理档少用 35% token、单任务成本低约 60%。注意请求必须流式，思考默认开启且计入输出 token。
- **理论关联**: 作为「认知外包」计费单位的证据，它把单位从「一段代码」推到「一整个仓库」：检索步骤被取消，意味着人原本做的中间判断——哪几个文件相关——被整体移交给模型，人只剩下「描述症状」这一件事。但反过来说，输入仍必须是一份由人写出的症状描述，模型的自由度止步于「问题怎么提」，这与研究加速报告中「创意仍全由人提出」互相印证。更值得注意的是它找到了维护者自己引用的先例：模型不是靠更强的推理，而是靠把整个上下文都放在眼前从而看见人因分工而看不见的关联，这为「暗时间」补了一个正向版本——上下文完整时，机器的「看见」可以替代人的「回想」。

<details><summary>🔶 中相关资讯 (2条，点击展开)</summary>

- **[[AINews] Riemann Hypothesis proved...twice independently...](https://latent.space/p/ainews-riemann-hypothesis-proved-twice-independently/)** [Latent Space] · 7/10
  - Latent Space 的 AINews 日报以「黎曼猜想被两次独立证明」为题汇总 11-20 事件：一路是 Anthropic 的 Alpöge 与 Claude，仅发 note 加 1.3GB Lean 代码（约 25 万页），覆盖 ...
- **[Qwen4 Max 上线 Together AI，单次调用修复 Tornado 整仓 bug...](https://www.together.ai/blog/qwen4-max)** [Together AI 研究与产品博客（RSS）] · 6/10
  - Together AI 宣布阿里旗舰模型 Qwen4 Max 上线其 serverless 推理平台（模型串 Qwen/Qwen4-Max），1M token 上下文，支持文本与图像输入、自动提示词缓存，截至 11-22 打七折：输入 1....

</details>

---
## 💾 数据导出
- 原始JSON: `output/news/news_cache.json`
- 本报告: `news_radar.py` 生成

> 💡 提示：高价值案例建议手动整理至书稿案例库；紧急清单建议加入每日晨会讨论。