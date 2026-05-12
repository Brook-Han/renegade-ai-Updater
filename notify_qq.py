#!/usr/bin/env python3
"""
龙虾 QQ 机器人推送脚本（只推送评分最高的前 5 条）
用途：将每天/每周生成的 AI 报告推送到 QQ 群
用法：
    python notify_qq.py --type news
    python notify_qq.py --type papers
"""

import os
import sys
import re
import requests
from pathlib import Path

# ==================== QQ 机器人发送 ====================

QQ_BOT_URL = os.getenv("QQ_BOT_URL", "http://127.0.0.1:3000/send_group_msg")
QQ_GROUP_ID = os.getenv("QQ_GROUP_ID")


def md_to_qq(text: str) -> str:
    """
    把 Markdown 转成 QQ 能正常显示的纯文本
    """
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"[*_#~>`-]{1,}", "", text)
    return text.strip()


def send_qq(text: str) -> bool:
    """
    发送消息到 QQ 群
    """
    if not QQ_GROUP_ID:
        print("❌ 未设置 QQ_GROUP_ID")
        return False

    payload = {
        "group_id": int(QQ_GROUP_ID),
        "message": md_to_qq(text)
    }

    try:
        r = requests.post(QQ_BOT_URL, json=payload, timeout=10)
        return r.status_code == 200
    except Exception as e:
        print("❌ QQ 推送失败:", e)
        return False


# ==================== Markdown 报告解析 ====================

def extract_field(line: str, field_name: str) -> str:
    pattern = rf"-\s*\*+\s*{re.escape(field_name)}\s*\*+\s*:\s*(.*)"
    m = re.search(pattern, line, re.IGNORECASE)
    if m:
        return re.sub(r"\*+", "", m.group(1)).strip()
    return ""


def parse_items(report_path: str, min_score: float = 4.0) -> list[dict]:
    content = Path(report_path).read_text(encoding="utf-8")
    items = []
    cur = {}
    in_draft = False
    draft_lines = []

    for line in content.split("\n"):
        s = line.strip()

        if s.startswith("### ") and not s.startswith("### 高相关") and not s.startswith("### 中相关"):
            if cur.get("title"):
                if draft_lines:
                    cur["draft"] = "\n".join(draft_lines).strip()
                items.append(cur)
                draft_lines = []
            cur = {"title": s[4:].strip()}
            in_draft = False
            continue

        if "✍️ 自动生成书稿草稿" in s:
            in_draft = True
            continue

        if in_draft:
            draft_lines.append(s)
            if s.startswith("###") or s.startswith("---"):
                in_draft = False
                cur["draft"] = "\n".join(draft_lines[:-1]).strip()
                draft_lines = []
            continue

        if not cur.get("score"):
            cur["score"] = extract_field(s, "最终评分")
        if not cur.get("urgency"):
            cur["urgency"] = extract_field(s, "紧迫度")
        if not cur.get("summary"):
            cur["summary"] = extract_field(s, "核心发现")
        if not cur.get("url"):
            cur["url"] = extract_field(s, "链接")
        if not cur.get("implications"):
            cur["implications"] = extract_field(s, "与本书关联")
        if not cur.get("chapter"):
            cur["chapter"] = extract_field(s, "目标章节")

    if cur.get("title"):
        if draft_lines:
            cur["draft"] = "\n".join(draft_lines).strip()
        items.append(cur)

    result = []
    for it in items:
        score_str = it.get("score", "0").split("/")[0]
        try:
            score = float(score_str)
        except ValueError:
            continue
        if score >= min_score:
            it["score_num"] = score
            result.append(it)

    return result


# ==================== 构造消息 ====================

def build_brief(top_items, report_type, report_url, total):
    if report_type == "papers":
        title_prefix = "📚 Renegade AI 每周论文简报"
    else:
        title_prefix = "📰 Renegade AI 每日资讯简报"

    lines = [
        f"## {title_prefix}",
        f"{top_items[0]['date']} · 总条目 {total} | 展示评分最高 {len(top_items)} 条",
        ""
    ]

    for idx, it in enumerate(top_items, 1):
        title = it.get("title", "")[:100]
        score = f"{it.get('score_num', 0):.1f}/10"
        url = it.get("url", "#")
        chapter = it.get("chapter", "")
        summary = it.get("summary", "")
        implications = it.get("implications", "")

        lines.append(f"### {idx}. {title}")
        lines.append(f"- ⭐ 评分：{score} {url}")
        if chapter and chapter != "N/A":
            lines.append(f"- 📍 {chapter}")
        if summary and summary != "N/A":
            lines.append(f"- 📝 {summary[:200]}")
        if implications and implications != "N/A":
            lines.append(f"- 🔗 {implications}")
        lines.append("")

    lines.append(f"> 📄 完整报告：{report_url}")
    return "\n".join(lines)


# ==================== 主入口 ====================

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="推送 Renegade AI 报告到 QQ")
    parser.add_argument("--type", choices=["news", "papers"], default="news")
    parser.add_argument("--file", default=None)
    args = parser.parse_args()

    base_url = os.getenv("REPORT_BASE_URL", "").rstrip("/")
    if not base_url:
        sys.exit("❌ 缺少 REPORT_BASE_URL")

    if args.file:
        latest_md = Path(args.file)
    else:
        pattern = f"reports/{args.type}_report_multi_*.md"
        files = sorted(Path().glob(pattern))
        if not files:
            print("⚠️ 未找到报告文件")
            sys.exit(0)
        latest_md = files[-1]

    if not latest_md.exists():
        sys.exit(f"❌ 文件不存在: {latest_md}")

    items = parse_items(str(latest_md), min_score=4.0)
    if not items:
        print("⚠️ 没有符合评分标准的条目")
        sys.exit(0)

    items.sort(key=lambda x: x["score_num"], reverse=True)
    top5 = items[:5]

    html_file = latest_md.with_suffix(".html").name
    report_url = f"{base_url}/{html_file}"
    if not report_url.startswith("http"):
        report_url = f"https://{report_url}"

    date_match = re.search(r'(\d{4}-\d{2}-\d{2})', latest_md.name)
    if date_match:
        for it in top5:
            it["date"] = date_match.group(1)

    msg = build_brief(top5, args.type, report_url, len(items))

    ok = send_qq(msg)
    if ok:
        print("✅ QQ 推送成功")
    else:
        print("❌ QQ 推送失败")
        sys.exit(1)