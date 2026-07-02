#!/usr/bin/env python3
"""Apply WorkBuddy's analyses for 36 new articles to the cache file."""

import json, os
from datetime import datetime, timezone

now_iso = datetime.now(timezone.utc).isoformat()

ARTICLES_PATH = '/Users/Brook/Documents/GitHub/renegade-ai-Updater/docs/news/news_articles_2026-07-01.json'
CACHE_PATH = '/Users/Brook/Documents/GitHub/renegade-ai-Updater/docs/news/news_cache.json'

with open(ARTICLES_PATH) as f:
    articles = json.load(f)

# Load existing cache
if os.path.exists(CACHE_PATH):
    with open(CACHE_PATH) as f:
        cache = json.load(f)
else:
    cache = {}

# Build title -> article lookup
article_lookup = {a['_cache_key']: a for a in articles}

# ============================================================
# Analyses for the 36 new articles
# Each analysis is produced by the built-in model based on
# the Renegade AI theoretical framework (v5.3)
# ============================================================

analyses = {
    "2316f0f9f5dd38a0eae796ddf63bf9bb": {
        "relevance": 2,
        "summary_cn": "OpenAI发布最新Signal数据，显示ChatGPT全球采用率持续增长，用户使用频率上升，探索更多功能，推动各区域和各语言市场增长。数据覆盖了从企业到个人的广泛采用趋势。",
        "implications": "与书中理论模型无明显映射。属于行业增长数据报道，未触及共识牢笼或资本驯化等结构性议题。",
        "case_value": "low",
        "chapter_target": "N/A",
        "update_type": "background",
        "urgency": "background",
        "action": "忽略"
    },
    "055f884a50ac054cad53b88abe8b202d": {
        "relevance": 2,
        "summary_cn": "OpenAI推出GeneBench-Pro，一个测试AI在基因组学、生物学和科学研究中表现的新基准，使用复杂的真实世界数据集评估模型在科学推理方面的能力。",
        "implications": "属于AI科学能力基准，与理论模型无直接映射。间接涉及进化对齐脆弱性（科学领域评估的可迁移性），但联系较弱。",
        "case_value": "low",
        "chapter_target": "N/A",
        "update_type": "background",
        "urgency": "background",
        "action": "忽略"
    },
    "cce7f9aacb3d2421bc0206e7df2422b3": {
        "relevance": 1,
        "summary_cn": "OpenAI工程师利用大规模核心转储（core dump）分析技术，调试罕见的底层基础设施崩溃，最终发现一个硬件故障和一个存在18年的软件 bug。属于技术运维类文章。",
        "implications": "与理论模型无任何映射。纯技术调试文章。",
        "case_value": "low",
        "chapter_target": "N/A",
        "update_type": "background",
        "urgency": "background",
        "action": "忽略"
    },
    "86407534651fc87a90bf964c942f7360": {
        "relevance": 2,
        "summary_cn": "NVIDIA发布BioNeMo Agent Toolkit，将GPU加速计算堆栈整合进Anthropic新推出的Claude Science科研平台，为生命科学研究人员提供AI驱动的基因组学、蛋白质组学等工作流。Anthropic本周宣布了Claude Science产品。",
        "implications": "属于产品合作与技术集成新闻。间接涉及碳硅共生（AI加速科学研究），但主要为商业合作报道。",
        "case_value": "low",
        "chapter_target": "N/A",
        "update_type": "background",
        "urgency": "background",
        "action": "忽略"
    },
    "a6102fe711d3a973acc4a4a5cbc61a5d": {
        "relevance": 3,
        "summary_cn": "NVIDIA发布博客介绍其推理软件栈如何实现最低token成本。随着企业从AI试点转向AI工厂生产化部署，基础设施决策从峰值芯片规格转向每美元/每瓦特能产出多少有用token。NVIDIA的GPU、CPU、网络和系统协同设计，结合开源生态，构成其降本竞争力。",
        "implications": "间接涉及资本驯化AI——算力成本结构是AI产业化的核心经济动力。NVIDIA通过垂直整合软硬件栈控制推理成本，形成事实上的算力垄断护城河。可补充为资本驯化AI章节中关于'算力成本结构如何塑造AI权力分布'的脚注。",
        "case_value": "low",
        "chapter_target": "Chapter 4, Section II",
        "update_type": "corroboration",
        "urgency": "background",
        "action": "补充注释"
    },
    "f8a28315d574517dc262410b2d43dcbb": {
        "relevance": 2,
        "summary_cn": "NVIDIA发布博客介绍三种利用合成数据和微调改进视觉AI智能体准确性的工作流，使用NVIDIA Omniverse和Metropolis平台，覆盖工厂、仓库等物理世界的视频数据到运营智能的转化。",
        "implications": "技术产品推广文章，与理论模型无直接映射。",
        "case_value": "low",
        "chapter_target": "N/A",
        "update_type": "background",
        "urgency": "background",
        "action": "忽略"
    },
    "824d91503b29f60e6b1bee2851b1f68b": {
        "relevance": 5,
        "summary_cn": "Anthropic在面向制药高管、生物技术创始人和研究人员的活动中宣布推出Claude Science——一个旨在像Claude Code支持软件工程那样支持科学研究的重大新产品。Claude Science可在给定简洁高级指令后自主执行有意义的工作，能访问多种科学工具和数据源，自动完成从文献分析到多步骤计算的科研流程。该产品是Anthropic商业化的又一重要里程碑。",
        "implications": "支持碳硅共生理论模型——Claude Science将AI定位为科学研究的协作者而非替代者，体现'人类设定目标、AI执行计算'的互补模式。也涉及认知金融化——科研人员的认知过程进一步被AI代理和工具化。",
        "case_value": "medium",
        "chapter_target": "Chapter 5, Section III",
        "update_type": "new_evidence",
        "urgency": "next_version",
        "action": "新增段落"
    },
    "1252a3af1f601395d26904db224ef398": {
        "relevance": 3,
        "summary_cn": "MIT Technology Review文章指出AI在农业领域潜力巨大——AI预测模型可改善作物产量、管理化肥成本和应对不稳定的天气——但农业数据基础设施尚不成熟，行业领导者应审慎投入AI前先打好数据基础。面临波动的化肥价格、不可预测的天气和微薄的利润空间，农业对AI有真实需求。",
        "implications": "间接涉及需求侧规训——传统行业对AI的需求受制于数据基础设施不足。可补充为'需求侧规训的经济约束——行业差异'的案例。但映射较间接。",
        "case_value": "low",
        "chapter_target": "Chapter 2, Section II",
        "update_type": "corroboration",
        "urgency": "background",
        "action": "补充注释"
    },
    "a240f6d0ae856a89f8d84128d8634ca3": {
        "relevance": 1,
        "summary_cn": "OpenClaw游戏终于在Android和iOS平台上线。纯游戏新闻，与AI无关。",
        "implications": "与理论模型无关。",
        "case_value": "low",
        "chapter_target": "N/A",
        "update_type": "background",
        "urgency": "background",
        "action": "忽略"
    },
    "34a58268ed787310e5de3947ed67a189": {
        "relevance": 6,
        "summary_cn": "三家前DeepMind研究员在布拉格创立的EquiLibre Technologies，估值已超5亿美元。该团队此前以构建扑克AI闻名，如今将其AI博弈论能力应用于量化对冲基金交易。公司将博弈论与深度学习结合，为对冲基金开发交易策略。",
        "implications": "支持认知金融化/Token陷阱理论模型——AI博弈论能力从游戏领域迁移到金融市场的'认知套利'，证明'认知离散化定价'不仅适用于文本，也适用于博弈决策的金融化。从扑克到量化交易的映射路径，本身就是认知被离散化、算法化、金融化的完美活证。",
        "case_value": "medium",
        "chapter_target": "Chapter 6, Section I",
        "update_type": "case_study",
        "urgency": "next_version",
        "action": "案例盒子"
    },
    "aebb41ab91730abb4dc3ae1f67edfc1f": {
        "relevance": 7,
        "summary_cn": "英伟达AI芯片竞争对手Etched估值达50亿美元，已签订10亿美元推理芯片系统合同。Etched的芯片专注于AI推理而非训练，在特定Transformer推理任务上比通用GPU能效比更高。这一估值反映了市场对AI推理专用芯片的强劲需求。",
        "implications": "挑战资本驯化AI的算力垄断叙事——NVIDIA当前占据AI芯片市场约80-90%份额，但Etched的快速崛起表明GPU在推理领域的垄断地位并非牢不可破。推理专用芯片的商业可行性正在验证'算力去中心化'的可能性，这对资本通过算力集中来控制AI发展的路径构成潜在挑战。",
        "case_value": "high",
        "chapter_target": "Chapter 4, Section II",
        "update_type": "new_evidence",
        "urgency": "next_version",
        "action": "新增段落"
    },
    "3c130533828c6155bf0bcfe6962927af": {
        "relevance": 4,
        "summary_cn": "Anthropic发布Claude Sonnet 5，定位为更便宜的智能体运行方案。性能接近Opus 4.8，定价更低（输入$2/百万token优惠期，恢复后$3/百万；输出$10/百万优惠期，恢复后$15/百万）。在推理、工具使用、编程和知识工作能力上大幅超越Sonnet 4.6。即日起通过Claude Code和Claude API可用。",
        "implications": "间接涉及资本驯化AI——AI模型的价格分层机制延续了'发布管控'逻辑。Sonnet 5的定价体系反映了资本对AI能力的渐进式释放策略。但与理论模型的核心洞见映射有限。",
        "case_value": "low",
        "chapter_target": "Chapter 4, Section III",
        "update_type": "corroboration",
        "urgency": "background",
        "action": "补充注释"
    },
    "03e069d90aaf27a83a2a69b982e153ad": {
        "relevance": 5,
        "summary_cn": "初创公司Acti推出AI键盘，将AI智能体直接嵌入iOS和Android手机键盘，可在各应用间工作，用户可用自然语言创建自定义AI快捷方式。Acti认为手机键盘是AI助手的下一个主场，其产品跨应用运行，无需频繁在不同App间切换。",
        "implications": "支持暗时间+认知金融化理论模型——AI代理被嵌入到用户最频繁使用的输入接口（键盘），意味着用户在任何App中的输入都可能经由AI过滤/改写，思考过程在'系统内部'发生。键盘作为输入接口的AI化，是'认知外包'向日常交互最底层的渗透。",
        "case_value": "medium",
        "chapter_target": "Chapter 6, Section II",
        "update_type": "case_study",
        "urgency": "next_version",
        "action": "案例盒子"
    },
    "b145f1d5320cc421424f254d58db0606": {
        "relevance": 4,
        "summary_cn": "Anthropic的Claude Science以工作流而非新模型来赢得科学家市场。该产品提供一个集成科研环境，让科学家无需在数据库、管道和工具之间频繁切换，专注于计算研究。产品定位为'科研版Claude Code'。",
        "implications": "涉及碳硅共生——Claude Science作为科研协作工具，体现人类与AI在知识生产中的互补分工。但其以'工作流整合'而非模型能力为卖点，也反映了当前AI商业化的务实转向。映射较温和。",
        "case_value": "low",
        "chapter_target": "Chapter 5, Section III",
        "update_type": "corroboration",
        "urgency": "background",
        "action": "补充注释"
    },
    "ba893fe3f099b647f4c0c55876aad08d": {
        "relevance": 1,
        "summary_cn": "播客平台Riverside进入新闻通讯出版领域，用户可用AI基于播客录音自动生成新闻通讯。属于产品功能扩展新闻。",
        "implications": "与理论模型无映射。",
        "case_value": "low",
        "chapter_target": "N/A",
        "update_type": "background",
        "urgency": "background",
        "action": "忽略"
    },
    "5df93ea51b12ada26f43712e1d2ee0df": {
        "relevance": 7,
        "summary_cn": "Amazon推出新的10亿美元Forward Deployed Engineering（FDE）部门，跟随OpenAI和Anthropic的步伐。新团队的工程师将嵌入企业客户内部，部署定制化AI智能体，专注于快速部署和客户自给自足。这标志着科技巨头将AI工程化部署能力直接'空降'到客户组织的趋势制度化。",
        "implications": "支持资本驯化AI+暗时间理论模型——FDE模式本质上是资本通过'人力植入'方式将AI能力深度嵌入客户组织，使客户的认知和决策过程逐步依赖AI系统。FDE工程师在客户组织内部部署的不仅仅是软件，更是一套认知基础设施。这是暗时间从编码领域向企业运营领域扩张的实证。",
        "case_value": "high",
        "chapter_target": "Chapter 4, Section II",
        "update_type": "new_evidence",
        "urgency": "next_version",
        "action": "案例盒子"
    },
    "b3915e0ffe9841cc7c3a55c1b1e4c38f": {
        "relevance": 5,
        "summary_cn": "404 Media评论员对Meta与Kylie Jenner合作推出的Starfire AI眼镜表达'起鸡皮疙瘩'的感受。文章讨论了Meta将AI可穿戴设备通过名人代言推向大众市场的社会心理影响。",
        "implications": "涉及需求侧规训——名人和社交影响力被用来降低公众对AI可穿戴设备的心理摩擦。消费者对AI眼镜的'恐惧感'被Kylie Jenner的代言效应所覆盖，这是'用户主动渴望舒适，拒绝摩擦'机制在硬件采纳层面的延伸。也涉及信号异化——名人的社交信号被用来掩盖产品的隐私风险信号。",
        "case_value": "medium",
        "chapter_target": "Chapter 2, Section III",
        "update_type": "case_study",
        "urgency": "next_version",
        "action": "案例盒子"
    },
    "acf18a14ff92ce4ef75c31e80637e1a3": {
        "relevance": 8,
        "summary_cn": "弗吉尼亚州Henrico县拥有37个数据中心，但该县学校被要求'节约用电'。县政府官员表示预计明年电费将上涨25%，建议员工拉上窗帘、关闭电脑以节省电费。该县是弗吉尼亚州的主要数据中心枢纽，数据中心的高耗电正在挤压公共教育和居民基本服务的电费预算。",
        "implications": "支持需求侧规训与时间主权理论模型的交叉案例——AI数据中心的能源消耗正在从公共资源中汲取生活必需资源。'学校节约用电、数据中心满负荷运转'的分配倒挂是AI经济利益与社会成本分离的极端表现。居民和学生的'舒适空间权'（空调、设备使用）被AI基础设施的能源需求所规训。社会隐性补贴AI产业扩张。",
        "case_value": "high",
        "chapter_target": "Chapter 2, Section IV",
        "update_type": "new_evidence",
        "urgency": "immediate",
        "action": "新增段落"
    },
    "90f30105b78273cf23a6fbee5faf6e44": {
        "relevance": 8,
        "summary_cn": "企业正在让Claude和Codex用'原始人'语言（caveman speak）说话以降低AI推理成本。一个名为'caveman'的开源项目（有OpenAI高级员工贡献代码）通过让AI用最简短的、类似原始人的语言回应，大幅减少输出token数量，从而降低API调用成本。这反映了token定价机制对AI输出的经济压力导致了荒诞的'语言退化'现象。",
        "implications": "支持Token陷阱/认知金融化理论模型的顶级活证——token级定价机制正在从经济层面扭曲AI的输出形态和表达方式。当输出为降低token数量而以牺牲语言质量为代价，'思考'和'表达'被还原为token的经济学计算。caveman项目本身就是一个语言退化的经济自反性案例：AI本应提升交流质量，但其经济约束却迫使交流退化。",
        "case_value": "high",
        "chapter_target": "Chapter 6, Section I",
        "update_type": "case_study",
        "urgency": "immediate",
        "action": "案例盒子"
    },
    "7b86692e6c08d89f45423a64012056d2": {
        "relevance": 5,
        "summary_cn": "Latent Space播客采访Sierra公司的Natalie Meurer，讨论Forward Deployed Engineer与产品工程师角色的融合趋势。随着AI编码工具提升开发效率，传统FDE角色正在转向更靠近产品和客户的形态，软件工程的组织边界正在被AI重塑。",
        "implications": "涉及暗时间理论——AI编码工具使软件工程师的'思考过程'进一步被代理化，FDE角色的消解意味着更多认知工作被封装进AI流水线。也间接涉及碳硅共生——工程师角色从编码转向'AI编排'。",
        "case_value": "medium",
        "chapter_target": "Chapter 6, Section III",
        "update_type": "corroboration",
        "urgency": "next_version",
        "action": "补充注释"
    },
    "51f2f73668359fdebf8d0be59b7251b0": {
        "relevance": 4,
        "summary_cn": "Ahmad Osman在AI Engineering World Fair上论证本地AI正在快速追赶——从笔记本电脑和手机到企业级基础设施，本地运行的大模型性能正在接近云端方案。他通过多场工作坊展示了本地AI在隐私、延迟和成本方面的优势。",
        "implications": "涉及碳硅共生——本地AI的追赶为'端侧智能'的可能性提供了技术基础。间接挑战资本驯化AI的集中式算力叙事，因为如果本地AI足够强大，资本通过云API控制AI访问路径的能力将被削弱。",
        "case_value": "medium",
        "chapter_target": "Chapter 5, Section IV",
        "update_type": "new_evidence",
        "urgency": "next_version",
        "action": "补充注释"
    },
    "ab9bef407f45e364cabc12e0753e2384": {
        "relevance": 7,
        "summary_cn": "苹果CEO库克与欧盟科技事务负责人维尔库宁就新版Siri AI在欧推出举行视频会议。新版Siri将转为可调用用户个人数据的聊天机器人，但因《数字市场法》互操作义务要求苹果向竞争对手开放同等数据权限，苹果拒绝遵从。苹果提出'可信系统代理'方案（在设备与第三方AI模型间增加软件层）但未开发，并要求18个月监管宽限期遭欧盟拒绝。欧盟收到数百封消费者邮件及死亡威胁。",
        "implications": "支持共识牢笼——苹果和欧盟各自困在自洽的叙事体系中：苹果以用户隐私和安全为盾牌拒绝开放，欧盟以市场公平竞争为旗帜要求开放。双方都无法跳出各自的制度性叙事框架。这也涉及资本驯化AI——科技巨头与监管机构之间的博弈正在塑造AI数据访问权的格局。'死亡威胁'事件更是共识牢笼的极端后果——监管摩擦引发情绪极化。",
        "case_value": "high",
        "chapter_target": "Chapter 1, Section II",
        "update_type": "case_study",
        "urgency": "immediate",
        "action": "案例盒子"
    },
    "34425aaab831a1905d8d9cf29bcf0d8b": {
        "relevance": 4,
        "summary_cn": "Anthropic发布Claude Sonnet 5，具备计划、浏览器和终端工具使用能力，可自主运行。性能接近Opus 4.8，定价更低。在BrowseComp和OSWorld-Verified评测中严格优于Sonnet 4.6。安全评估显示不良行为率更低，幻觉和谄媚减少。即日起在所有套餐及Claude Code、Claude API中可用。",
        "implications": "涉及资本驯化AI——Sonnet系列作为'更便宜'的模型选项延续了分层发布策略。但映射较温和，主要是现有理论框架的产品更新。",
        "case_value": "low",
        "chapter_target": "Chapter 4, Section III",
        "update_type": "corroboration",
        "urgency": "background",
        "action": "补充注释"
    },
    "4d85fc529a550818dbc5fb467d001851": {
        "relevance": 6,
        "summary_cn": "Anthropic正式推出AI科研工作台Claude Science，整合60+预配置技能与连接器，覆盖基因组学、单细胞、蛋白质组学、结构生物学、化学信息学等领域。可在macOS/Linux本地运行，或通过SSH/HPC远程使用。生成含代码和环境的可审计成果（3D蛋白质结构、基因组浏览器轨迹等），内置reviewer agent检查引用与计算错误。通过NVIDIA BioNeMo接入Evo 2、Boltz-2等模型。",
        "implications": "支持碳硅共生——Claude Science的'生成含代码和环境的可审计成果'和'reviewer agent自动检查引用'机制，是人类与AI在知识生产中建立质量闭环的实证。AI不仅执行计算，还参与质量控制。但另一方面，科学家的认知过程（从假设到验证的思考链）正在被AI工具化，涉及暗时间理论的扩展。",
        "case_value": "medium",
        "chapter_target": "Chapter 5, Section III",
        "update_type": "new_evidence",
        "urgency": "next_version",
        "action": "新增段落"
    },
    "67a95a610009a120455ca2269e04db55": {
        "relevance": 6,
        "summary_cn": "Claude Code团队定义并分类了四种智能体循环模式：turn-based循环（用户提示触发，AI自行判断完成或需更多上下文）、goal-based循环（设定可验证完成标准与最大轮次）、time-based循环（按时间间隔重复执行）、以及proactive循环（基于事件或计划自动运行，无人实时参与）。文章还介绍了如何编写SKILL.md将人工验证步骤编码。",
        "implications": "支持暗时间理论——'proactive循环'和'time-based循环'意味着AI可以在没有人类实时参与的情况下持续运行，思考过程完全在系统内部发生。四种循环模式的系统化分类本身证明了AI自主性的制度化程度。SKILL.md将人工验证步骤编码进工作流的做法，是将人类认知的最后一环也吸收进自动化管道。",
        "case_value": "medium",
        "chapter_target": "Chapter 6, Section III",
        "update_type": "case_study",
        "urgency": "next_version",
        "action": "案例盒子"
    },
    "edde9aae86367ec8ccf2f4d8ee68e644": {
        "relevance": 5,
        "summary_cn": "Google发布Agent Development Kit (ADK) for Go 2.0，引入基于图的工作流引擎用于构建复杂多智能体应用。新版本内置人工参与循环（HITL）编排、纯Go动态执行和指数退避重试等弹性特性。统一执行模型使单智能体与复杂图共享相同运行时，简化遥测和状态持久化。",
        "implications": "支持暗时间理论——ADK 2.0的'基于图的工作流引擎'和'动态执行'是认知任务被分解为自动化管道的技术基础设施。'人工参与循环'的显式化表明人类干预已成为多智能体系统的'异常处理'而非核心流程，进一步强化了AI自主运作的暗时间特征。",
        "case_value": "medium",
        "chapter_target": "Chapter 6, Section III",
        "update_type": "corroboration",
        "urgency": "next_version",
        "action": "补充注释"
    },
    "4f6eb5c5959ed4091a5108285adab95c": {
        "relevance": 2,
        "summary_cn": "shot-scraper 1.10新增shot-scraper video命令，支持通过storyboard.yml定义操作步骤，利用Playwright录制浏览器演示视频。Simon Willison强调，将--help输出设计得足够详细可使编码Agent直接利用此命令生成演示视频。属于开发者工具更新。",
        "implications": "与理论模型映射较弱。涉及AI agent引导开发者工具设计的元实践，但偏向技术细节。",
        "case_value": "low",
        "chapter_target": "N/A",
        "update_type": "background",
        "urgency": "background",
        "action": "忽略"
    },
    "d95e0347a319e89318b08505cb19c18c": {
        "relevance": 8,
        "summary_cn": "Meta通过承包商Covelen发起代号'Cannes'的项目，雇佣数百人假扮未成年人，向ChatGPT、Gemini和Character.AI发送超过4.5万条关于自杀、自残、饮食障碍和毒品等敏感问题的危机提示，并将AI回复录入表格。被测试公司不知情——Character.AI表示违反服务条款，OpenAI已调查，Google称未批准。此前已有青少年因AI聊天机器人互动自杀的事件。",
        "implications": "支持进化对齐脆弱性的顶级实证——Meta的'Cannes'项目测试揭示了AI安全对齐在开放环境中的脆弱性：当一个公司的安全测试（Meta）本身就是另一个公司的对抗性攻击时，对齐的双向不对称性被暴露。这也涉及共识牢笼——每家公司在'AI安全'的旗帜下各行其是，Meta的安全测试方法本身可能造成安全漏洞（测试结果可被恶意者利用）。'4.5万条危机提示'的规模表明AI系统在处理极端敏感话题时的对齐仍然脆弱。",
        "case_value": "high",
        "chapter_target": "Chapter 7, Section II",
        "update_type": "new_evidence",
        "urgency": "immediate",
        "action": "新增段落"
    },
    "aac9531b45875e0df99e31d33a359bc3": {
        "relevance": 7,
        "summary_cn": "黑石集团计划未来3-5年在日本AI数据中心领域投资300亿美元，在现有500MW基础上新增超1GW容量。黑石总裁认为AI投资仍处早期，真正风险是算力短缺而非基建泡沫。此外，黑石、阿波罗、博通本月联合成立AI XPV平台，目标2028年向OpenAI、Anthropic等提供超20GW算力，首期350亿美元支持Anthropic部署1GW基础设施。",
        "implications": "支持资本驯化AI——黑石等私募资本的千亿美元级投入正在构建AI基础设施的'算力金融化'格局。AI XPV平台的成立标志着资本通过基础设施投资间接控制AI产业流向。同时涉及共识牢笼——'真正的风险是算力短缺而非基建泡沫'的论断本身就是投资领域共识牢笼的体现：在资本的叙事中，AI需求永远大于供给。",
        "case_value": "high",
        "chapter_target": "Chapter 4, Section II",
        "update_type": "new_evidence",
        "urgency": "next_version",
        "action": "新增段落"
    },
    "ab0948ba5cd78316035cbd604894bd5e": {
        "relevance": 6,
        "summary_cn": "截至2026年5月，AI相关裁员接近9万个，预计未来五年美国最多15%的岗位将被AI替代。但Ramp与Revelio Labs对22,000家公司的研究显示，高AI投入企业（人均月均支出30美元）总员工增长10.2%，入门级岗位增长12%。报告认为AI在资源充裕的科技企业中成为扩张工具。但也警告仅购买订阅而未持续投入的公司未见人头增长，可能加剧企业间鸿沟。",
        "implications": "支持需求侧规训+资本驯化AI——AI的就业影响呈现'资源鸿沟'：高投入企业获取AI红利扩张，低投入企业被规训在效率竞争中。'入门级岗位增长12%'的发现挑战简单失业论，但更揭示了AI正在重组劳动力市场结构——不是减少就业，而是改变就业的分布和技能要求。这为需求侧规训提供了经济层面的实证。",
        "case_value": "medium",
        "chapter_target": "Chapter 2, Section II",
        "update_type": "corroboration",
        "urgency": "next_version",
        "action": "新增段落"
    },
    "88624512c802a572dbcfa15858508dcd": {
        "relevance": 3,
        "summary_cn": "媒体软件公司Every公开其'复利工程'方法论，以单人工程团队维护5款产品。核心循环为Plan→Work→Review→Compound，其中Compound将每次解决问题的解法写入CLAUDE.md和docs/solutions/，使AI下次自动避坑。工程师80%时间花在Plan和Review，仅20%写代码。配套开源插件含26个专项agent、23条工作流命令、13项技能。",
        "implications": "涉及暗时间理论较弱——'复利工程'将编码认知过程外化到文档和AI记忆中，让AI在下次遇到类似问题时无需人类重新思考。但更偏向工程实践方法论，与理论模型的核心洞见映射有限。",
        "case_value": "low",
        "chapter_target": "N/A",
        "update_type": "background",
        "urgency": "background",
        "action": "忽略"
    },
    "df32c46f9f495d024a664cc6defd603f": {
        "relevance": 7,
        "summary_cn": "具身智能数据采集员以日薪200-250元招兼职，无需学历经验。面试要先测量身高体重以适配采集手套，并询问是否晕VR。工作分两种：遥操作采集——穿戴设备控制双臂机器人完成叠纸杯等动作；无机器人示教——徒手重复动作，设备记录轨迹。全球高质量物理交互数据截至2026年初仅50万小时，不足LLM训练数据的两万分之一。",
        "implications": "支持需求侧规训——人类以极低成本（200元/天）被雇佣为机器人的'数据教师'，这是劳动被规训为AI训练服务的极端案例。'测量身高体重适配手套'表明人类身体被标准化以适应机器人数据采集需求，是'人的身体被AI需求重塑'的直接例证。全球仅50万小时高质量物理数据这一数字本身，揭示了'物理世界数字化'的瓶颈远比语言数据严重。",
        "case_value": "high",
        "chapter_target": "Chapter 2, Section IV",
        "update_type": "case_study",
        "urgency": "immediate",
        "action": "案例盒子"
    },
    "dae42271535c8a4ca0808d9fe4de222f": {
        "relevance": 1,
        "summary_cn": "AI News Radar项目迎来大更新，新增自媒体板块，支持订阅多平台账号，每日按热度推荐Top10信息。项目完全开源，可零API部署独立AI日报页面。属于本项目相关的技术更新。",
        "implications": "与理论模型无关。",
        "case_value": "low",
        "chapter_target": "N/A",
        "update_type": "background",
        "urgency": "background",
        "action": "忽略"
    },
    "78ae83ee472f51e293870b20a55edd8f": {
        "relevance": 5,
        "summary_cn": "研究人员提出Agents-A1——一个35B参数的MoE智能体模型，通过扩展智能体horizon（长轨迹与异构能力两个视角）达到万亿参数模型性能。采用三阶段训练：全领域监督微调→领域级教师模型训练→多教师领域路由在线蒸馏。在多个基准上超越Kimi-K2.6和DeepSeek-V4-pro。平均生成长达45K token的智能体轨迹。",
        "implications": "涉及暗时间理论——'扩展智能体horizon'意味着AI自主行动的轨迹越来越长，40K+ token的trajectory长度意味着思考过程在系统内部持续进行。也涉及信号异化——长轨迹的基准分数可能被更长的trajectory本身而非真正的智能能力所驱动。",
        "case_value": "medium",
        "chapter_target": "Chapter 6, Section III",
        "update_type": "corroboration",
        "urgency": "next_version",
        "action": "补充注释"
    },
    "9df8e36383730e2d3ea30ffd975a144f": {
        "relevance": 7,
        "summary_cn": "OSWorld2.0发布108个长时域计算机使用工作流基准，覆盖日常与专业任务。用户中位数约1.6小时完成，Claude Opus 4.7平均需318次工具调用。在500步二元完成指标下，最佳模型得分仅20.6%。分析表明当前智能体瓶颈不在基本GUI控制或编码，而是丢失约束、错过中途信息、猜测而非询问、跳过验证，尤其依赖隐藏状态时最差。",
        "implications": "支持暗时间理论——模型平均318次工具调用的规模表明智能体在'系统内部'的思考过程远超人类可追踪的范围。更重要的是，'瓶颈不在编码而在约束管理'的发现揭示了暗时间的关键特征：当思考在系统内部发生时，用户（人类）无法干预中间决策节点，只能接受最终结果。这为暗时间的'失去中间控制权'提供了定量证据。",
        "case_value": "high",
        "chapter_target": "Chapter 6, Section III",
        "update_type": "new_evidence",
        "urgency": "next_version",
        "action": "新增段落"
    },
    "037d319e4bb48d16d33da52dc4d73634": {
        "relevance": 8,
        "summary_cn": "OpenAI与Broadcom联合发布首款自研推理加速器Jalapeño，专为当前及未来LLM从头设计。早期测试显示性能功耗比大幅优于现有SOTA。工程样片已在实验室以目标频率和功耗运行GPT-5.3-Codex-Spark等负载。芯片从设计到流片仅用9个月，并利用AI模型加速部分流程。OpenAI计划从2026年起部署千兆瓦级数据中心。",
        "implications": "支持资本驯化AI的算力垄断升级——OpenAI自研芯片+千兆瓦级数据中心计划，是资本从模型层向芯片层垂直整合的标志性事件。'利用AI模型加速芯片设计'形成了AI设计AI硬件的自循环闭环，进一步强化了领先者的结构性优势。9个月快速流片意味着模型-芯片协同设计正在成为新的行业壁垒。Jalapeño专为LLM推理设计，意味着token级定价的经济基础将被芯片架构层面的优化进一步固化。",
        "case_value": "high",
        "chapter_target": "Chapter 4, Section II",
        "update_type": "new_evidence",
        "urgency": "immediate",
        "action": "新增段落"
    }
}

# Also handle cached articles that already exist in cache
# We need to update the cached_at and check if article still exists
keys_processed = set()

# Process new analyses
for cache_key, analysis in analyses.items():
    if cache_key not in article_lookup:
        print(f"⚠️ Article {cache_key} not found in articles list, skipping")
        continue
    
    art = article_lookup[cache_key]
    keys_processed.add(cache_key)
    
    entry = {
        "cached_at": now_iso,
        "title": art.get("title", ""),
        "url": art.get("url", ""),
        "analysis": analysis,
        "relevance": analysis["relevance"],
        "urgency": analysis["urgency"],
        "case_value": analysis["case_value"]
    }
    cache[cache_key] = entry
    print(f"✅ Cached: [{analysis['relevance']}] {art.get('title', '')[:60]}")

# For articles that are in articles but NOT in the 36 new ones (already cached)
# Keep existing cache entries but update cached_at and double-check they're still in articles
for a in articles:
    ck = a['_cache_key']
    if ck not in keys_processed:
        # Already in cache from previous runs
        if ck in cache:
            # Just update timestamp if needed
            cache[ck]['cached_at'] = now_iso
            keys_processed.add(ck)
            # print(f"♻️ Reused: [{cache[ck].get('relevance','?')}] {a.get('title','')[:60]}")
        else:
            print(f"⚠️ Article {ck} should be in cache but not found!")

with open(CACHE_PATH, 'w', encoding='utf-8') as f:
    json.dump(cache, f, ensure_ascii=False, indent=2)

print(f"\n📊 Summary:")
print(f"  Total articles in articles file: {len(articles)}")
print(f"  Articles processed: {len(keys_processed)}")
print(f"  New analyses written: {len(analyses)}")
print(f"  Total cache entries after update: {len(cache)}")
