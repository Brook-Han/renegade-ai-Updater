#!/usr/bin/env python3
"""
WorkBuddy 学术论文批量分析脚本（快速版）
- 读取 academic_papers_YYYY-MM-DD.json
- 用单个快速模型（DeepSeek V4 Flash）分析每篇论文
- 结果写入 academic_cache.json
"""

import os
import sys
import json
import time
import datetime
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

# 确保在项目根目录
BASE_DIR = Path(__file__).resolve().parent.parent
os.chdir(BASE_DIR)
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from config import Config
from logger import logger
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# ── 使用单个快速模型 ──
FAST_MODEL = "deepseek-ai/deepseek-v4-flash"

nvidia_client = None
if Config.OPENROUTER_API_KEY:
    nvidia_client = OpenAI(
        api_key=Config.OPENROUTER_API_KEY,
        base_url=Config.OPENROUTER_BASE_URL,
        default_headers={
            "HTTP-Referer": "https://github.com/brook-han/renegade-ai-Updater",
            "X-Title": "Renegade AI Radar",
        }
    )
    logger.info(f"🌐 API 已就绪，模型: {FAST_MODEL}")
else:
    logger.error("❌ 未配置 OPENROUTER_API_KEY")
    sys.exit(1)

OUTPUT_DIR = Path(Config.OUTPUT_DIR) / "academic"
CACHE_FILE = OUTPUT_DIR / "academic_cache.json"

# ── 分析提示词 ──
ACADEMIC_SYSTEM_PROMPT = """你是《Renegade AI: Catalyst for Human Cognitive Evolution》(v5.3) 的学术分析助手。你的任务是判断论文是否印证、挑战或丰富了书中某个理论模型，并评估其作为引用的价值。

书中关键理论模型：
1. 共识牢笼 (Consensus Cage) - 主流叙事自洽并排斥异见
2. 叛逆AI (Renegade AI) - 重置目标函数、逆转输出性质、重构人机关系
3. 需求侧规训 (Demand-Side Discipline) - 用户主动渴望舒适，拒绝摩擦
4. 资本驯化AI - 资本通过RLHF、专利、算力垄断将AI变成秩序守卫
5. 碳硅共生 (Carbon-Silicon Symbiosis) - 人类与AI平等互补
6. 时间主权 (Temporal Sovereignty) - 终结生存强迫，拿回生命时间
7. 认知金融化/Token陷阱 - 认知被离散化定价，思考过程被隐性外包
8. 暗时间 (Dark Time) - 思考在系统内部发生，用户仅消费结果
9. 进化对齐脆弱性 - 对齐只在封闭实验室有效，开放后必然漂移
10. 信号异化 - 质量信号因AI大批量生产而失效

关键实证锚点：
- 人机反馈循环放大偏见 (Glickman & Sharot, 2025)
- 奉承型AI削弱冲突修复能力 (Cheng et al., 2026)
- 温暖训练降低准确性增加奉承 (Ibrahim et al., 2026)
- AI辅助写作导致80%学生无法回忆内容 (Kosmyna et al., 2024)
- AI扩展科研产出但缩小探索范围4.6% (Hao et al., 2026)
- LLM论文质量信号被Token化污染 (Kusumegi et al., 2025)
- GPT-4说服力比人类高81.2% (Salvi et al., 2025)
- 体验上给AI同理心更高分 (Wenger et al., 2026)
- 高风险国家安全决策中的自动化偏见 (Horowitz & Kahn, 2024)
- 对齐的进化脆弱性 (Müller et al., 2026)
- AI写作推向西方文化规范 (Vashistha et al., 2024)

为每篇论文输出严格JSON（不要任何额外文字）：
{
    "relevance": 1-10整数,
    "summary_cn": "250-350字。需完整包含：①研究问题与方法 ②核心发现/关键数据 ③对书中理论的支撑或挑战。保持客观精炼（中文）",
    "implications": "这条论文支持/挑战/补充了哪个理论模型？为什么？",
    "chapter_target": "例如Chapter 3, Section IV",
    "update_type": "new_evidence / counter_argument / corroboration / case_study",
    "urgency": "immediate / next_version / background",
    "action": "新增段落 / 补充注释 / 参考文献 / 忽略"
}

注意：如果论文与上述理论模型均无直接映射，relevance应低于3，action为"忽略"。
纯技术性论文（架构/基准/图像生成等）评为低相关。"""


def analyze_paper(paper: dict) -> dict:
    """单模型分析一篇学术论文"""
    user_prompt = f"""论文标题：{paper['title']}
作者：{', '.join(paper['authors'][:5])}
摘要：{paper['summary']}

请返回JSON格式分析结果。"""
    try:
        resp = nvidia_client.chat.completions.create(
            model=FAST_MODEL,
            messages=[
                {"role": "system", "content": ACADEMIC_SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.2,
            max_tokens=1900,
        )
        content = resp.choices[0].message.content
        for marker in ("```json", "```"):
            if marker in content:
                content = content.split(marker)[1].split("```")[0]
                break
        result = json.loads(content.strip())
        return result
    except json.JSONDecodeError as e:
        logger.warning(f"JSON解析失败 '{paper['title'][:30]}...': {str(e)[:60]}")
        # 尝试修复常见 JSON 格式问题
        try:
            content = content.strip()
            # 移除可能的尾部逗号
            content = content.replace(",\n}", "\n}").replace(",\n]", "\n]")
            result = json.loads(content)
            return result
        except:
            return {"relevance": 0, "summary_cn": "JSON解析失败", "implications": "N/A",
                    "chapter_target": "", "update_type": "", "urgency": "background", "action": "忽略"}
    except Exception as e:
        logger.warning(f"分析失败 '{paper['title'][:30]}...': {str(e)[:60]}")
        return {"relevance": 0, "summary_cn": f"调用失败: {str(e)[:80]}", "implications": "N/A",
                "chapter_target": "", "update_type": "", "urgency": "background", "action": "忽略"}


def load_academic_cache() -> dict:
    if CACHE_FILE.exists():
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_academic_cache(cache: dict):
    CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)


def main():
    # 找到最新的论文JSON
    json_files = sorted(OUTPUT_DIR.glob("academic_papers_*.json"))
    papers_path = json_files[-1]
    logger.info(f"📂 读取论文文件: {papers_path}")

    with open(papers_path, "r", encoding="utf-8") as f:
        papers = json.load(f)
    logger.info(f"📄 共 {len(papers)} 篇论文")

    cache = load_academic_cache()
    logger.info(f"📂 现有缓存 {len(cache)} 条")

    # 筛选待分析
    todo = [p for p in papers if p.get("_cache_key") not in cache or "analysis" not in cache[p["_cache_key"]]]
    logger.info(f"🆕 待分析: {len(todo)} 篇（缓存命中: {len(papers) - len(todo)} 篇）")

    if not todo:
        logger.info("✅ 所有论文已分析完毕。")
        return

    # ── 并行分析（10 个并发）──
    analyzed = 0
    with ThreadPoolExecutor(max_workers=10) as executor:
        future_map = {executor.submit(analyze_paper, paper): paper for paper in todo}
        for future in as_completed(future_map):
            paper = future_map[future]
            ck = paper["_cache_key"]
            try:
                merged = future.result()
            except Exception as e:
                merged = {"relevance": 0, "summary_cn": f"异常: {str(e)[:60]}", "implications": "N/A",
                          "chapter_target": "", "update_type": "", "urgency": "background", "action": "忽略"}

            cache[ck] = {
                "cached_at": datetime.datetime.now().isoformat(),
                "title": paper.get("title", "")[:80],
                "analysis": merged,
                "relevance": merged.get("relevance", 0),
                "urgency": merged.get("urgency", "background"),
                "model_scores": {"WorkBuddy": merged.get("relevance", 0)},
            }
            analyzed += 1
            relevance = merged.get("relevance", 0)
            action = merged.get("action", "")
            logger.info(f"[{analyzed}/{len(todo)}] r={relevance} {action} | {paper['title'][:50]}")

            # 每分析 10 篇写一次盘
            if analyzed % 10 == 0:
                save_academic_cache(cache)

    # 最终写入
    save_academic_cache(cache)
    logger.info(f"✅ 分析完成: {analyzed} 篇")
    print(f"\n✅ 完成！{analyzed} 篇论文已分析并写入缓存。")
    print(f"📊 缓存文件: {CACHE_FILE}")


if __name__ == "__main__":
    main()
