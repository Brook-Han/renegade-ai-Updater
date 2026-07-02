#!/usr/bin/env python3
"""
WorkBuddy 新闻批量分析脚本（逐步版 - 每篇独立输出）
- 读取 news_articles_YYYY-MM-DD.json
- 用单个快速模型（DeepSeek V4 Flash）分析每篇文章
- 结果写入 news_cache.json
"""

import os
import sys
import json
import time
import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
os.chdir(BASE_DIR)
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from config import Config
from dotenv import load_dotenv

load_dotenv()

FAST_MODEL = "deepseek-ai/deepseek-v4-flash"

from openai import OpenAI

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
    print(f"[{datetime.datetime.now().isoformat()}] 🌐 API 已就绪，模型: {FAST_MODEL}", flush=True)
else:
    print("❌ 未配置 OPENROUTER_API_KEY")
    sys.exit(1)

OUTPUT_DIR = Path(Config.OUTPUT_DIR) / "news"
CACHE_FILE = OUTPUT_DIR / "news_cache.json"

NEWS_SYSTEM_PROMPT = """你是《Renegade AI: Catalyst for Human Cognitive Evolution》(v5.3) 的新闻分析助手。你的任务是判断新闻是否印证、挑战或丰富了书中某个理论模型，并评估其作为案例/类比的价值。

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

为每篇文章输出严格JSON（不要任何额外文字）：
{
    "relevance": 1-10整数,
    "summary_cn": "250-350字。需完整包含：①事件背景与起因 ②核心事实/关键数据/涉及主体 ③直接后果或行业/技术影响。保持客观精炼（中文）",
    "implications": "这条新闻支持/挑战/补充了哪个理论模型？为什么？",
    "case_value": "high / medium / low",
    "chapter_target": "例如Chapter 3, Section IV",
    "update_type": "new_evidence / counter_argument / corroboration / case_study",
    "urgency": "immediate / next_version / background",
    "action": "新增段落 / 补充注释 / 案例盒子 / 忽略"
}

注意：如果新闻与上述理论模型均无直接映射，relevance应低于3，action为"忽略"。不要套用学术论文的评价标准。case_value评估该新闻作为"案例/类比"的说服力。"""


def analyze_news(news: dict, timeout_sec: int = 30) -> dict:
    """单模型分析一篇新闻"""
    has_chinese = any('\u4e00' <= c <= '\u9fff' for c in (news.get('summary', '') + news.get('title', '')))
    lang_label = "中文" if has_chinese else "英文"

    user_prompt = f"""新闻标题：{news['title']}
内容摘要：{news['summary']}
来源：{news.get('source_name', '')} · {news.get('published', '')[:10]}
语言：{lang_label}

请按 JSON 格式返回分析结果。"""
    try:
        resp = nvidia_client.chat.completions.create(
            model=FAST_MODEL,
            messages=[
                {"role": "system", "content": NEWS_SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.2,
            max_tokens=1500,
            timeout=timeout_sec,
        )
        content = resp.choices[0].message.content
        for marker in ("```json", "```"):
            if marker in content:
                content = content.split(marker)[1].split("```")[0]
                break
        result = json.loads(content.strip())
        return result
    except json.JSONDecodeError as e:
        print(f"  ⚠ JSON解析失败: {str(e)[:60]}", flush=True)
        try:
            content = content.strip()
            content = content.replace(",\n}", "\n}").replace(",\n]", "\n]")
            result = json.loads(content)
            return result
        except:
            return {"relevance": 0, "summary_cn": "JSON解析失败", "implications": "N/A",
                    "chapter_target": "", "update_type": "", "urgency": "background", "action": "忽略"}
    except Exception as e:
        print(f"  ⚠ 分析失败: {str(e)[:80]}", flush=True)
        return {"relevance": 0, "summary_cn": f"调用失败: {str(e)[:80]}", "implications": "N/A",
                "chapter_target": "", "update_type": "", "urgency": "background", "action": "忽略"}


def load_cache() -> dict:
    if CACHE_FILE.exists():
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_cache(cache: dict):
    CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)


def main():
    json_files = sorted(OUTPUT_DIR.glob("news_articles_*.json"))
    if not json_files:
        print("❌ 未找到新闻文章文件")
        sys.exit(1)
    papers_path = json_files[-1]
    print(f"📂 读取新闻文件: {papers_path}", flush=True)

    with open(papers_path, "r", encoding="utf-8") as f:
        articles = json.load(f)
    print(f"📄 共 {len(articles)} 篇文章", flush=True)

    cache = load_cache()
    print(f"📂 现有缓存 {len(cache)} 条", flush=True)

    # 筛选待分析
    todo = [(i, a) for i, a in enumerate(articles) if a.get("_cache_key") not in cache or "analysis" not in cache[a["_cache_key"]]]
    cached_hit = len(articles) - len(todo)
    print(f"🆕 待分析: {len(todo)} 篇（缓存命中: {cached_hit} 篇）", flush=True)

    if not todo:
        print("✅ 所有文章已分析完毕。")
        return

    analyzed = 0
    for idx, article in todo:
        ck = article["_cache_key"]
        title_short = article.get("title", "")[:50]

        print(f"[{analyzed+1}/{len(todo)}] 分析: {title_short}...", end=" ", flush=True)
        merged = analyze_news(article)

        cache[ck] = {
            "cached_at": datetime.datetime.now().isoformat(),
            "title": article.get("title", "")[:80],
            "url": article.get("url", ""),
            "analysis": merged,
            "relevance": merged.get("relevance", 0),
            "urgency": merged.get("urgency", "background"),
            "case_value": merged.get("case_value", "low"),
        }
        analyzed += 1
        relevance = merged.get("relevance", 0)
        action = merged.get("action", "")
        print(f"r={relevance} {action}", flush=True)

        if analyzed % 10 == 0:
            save_cache(cache)
            print(f"  💾 已保存缓存（{analyzed}/{len(todo)}）", flush=True)

        time.sleep(1.5)  # 限流

    save_cache(cache)
    print(f"\n✅ 完成！{analyzed} 篇新分析已写入缓存。")
    print(f"📊 缓存文件: {CACHE_FILE}")


if __name__ == "__main__":
    main()
