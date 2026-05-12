#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔔 QQ开放平台机器人推送
AppID+AppSecret 鉴权，无需OpenClaw、无需本地网关
"""

import os
import sys
import time
import hashlib
import requests
import re
from pathlib import Path
from typing import List, Dict

# ==================== 你的机器人配置 ====================
QQ_APPID = "1903998907"
QQ_APPSECRET = "fgiknquy38EKRZhqz9JUfr3GUixCSizG"
# 改成你要发的 QQ群ID / 频道ID
QQ_GUILD_ID = "在这里填你的群ID"
# ========================================================

def get_signature(appid: str, secret: str, timestamp: str) -> str:
    """QQ开放平台接口签名"""
    raw = f"{appid}{timestamp}{secret}"
    return hashlib.md5(raw.encode("utf-8")).hexdigest()

def send_qq_msg(content: str) -> bool:
    """调用QQ开放平台发送文本消息到群"""
    ts = str(int(time.time()))
    sign = get_signature(QQ_APPID, QQ_APPSECRET, ts)

    url = f"https://bot.q.qq.com/openapi/v2/guilds/{QQ_GUILD_ID}/messages"
    headers = {
        "Content-Type": "application/json"
    }
    payload = {
        "appid": QQ_APPID,
        "timestamp": ts,
        "signature": sign,
        "content": content
    }

    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=15)
        print("QQ接口返回：", resp.text)
        data = resp.json()
        if data.get("code") == 0:
            print("✅ QQ机器人推送成功")
            return True
        else:
            print("❌ QQ推送失败", data)
            return False
    except Exception as e:
        print("❌ 请求异常：", str(e))
        return False

# -------- 以下完全复用你钉钉脚本的解析逻辑，无任何改动 --------
def extract_field(line: str, field_name: str) -> str:
    pattern = rf"-\s*\*+\s*{re.escape(field_name)}\s*\*+\s*:\s*(.*)"
    m = re.search(pattern, line, re.IGNORECASE)
    if m:
        return re.sub(r"\*+", "", m.group(1)).strip()
    return ""

def parse_items(report_path: str, min_score: float = 4.0) -> List[Dict]:
    content = Path(report_path).read_text(encoding="utf-8")
    items = []
    cur = {}
    in_draft = False
    draft_lines = []

    for line in content.split("\n"):
        s = line.strip()
        if s.startswith("### ") and not any(x in s for x in ["高相关", "中相关", "低相关", "紧急"]):
            if cur.get("title"):
                if draft_lines:
                    cur["draft"] = "\n".join(draft_lines).strip()
                items.append(cur)
                draft_lines = []
            cur = {"title": s[4:].strip()}
            in_draft = False
            continue

        if "✍️" in s and ("草稿" in s or "draft" in s.lower()):
            in_draft = True
            continue
        if in_draft:
            if s.startswith("###") or s.startswith("---"):
                in_draft = False
                if draft_lines:
                    cur["draft"] = "\n".join(draft_lines).strip()
                draft_lines = []
                continue
            draft_lines.append(s)
            continue

        if not cur.get("score"):
            cur["score"] = extract_field(s, "最终评分") or extract_field(s, "相关度")
        if not cur.get("summary"):
            cur["summary"] = extract_field(s, "核心发现") or extract_field(s, "事件摘要")
        if not cur.get("url"):
            cur["url"] = extract_field(s, "链接")
        if not cur.get("implications"):
            cur["implications"] = extract_field(s, "与本书关联") or extract_field(s, "理论关联")
        if not cur.get("chapter"):
            cur["chapter"] = extract_field(s, "目标章节")

    if cur.get("title"):
        if draft_lines:
            cur["draft"] = "\n".join(draft_lines).strip()
        items.append(cur)

    result = []
    for it in items:
        score_str = str(it.get("score", "0")).split("/")[0]
        try:
            score = float(score_str)
        except ValueError:
            continue
        if score >= min_score:
            it["score_num"] = score
            result.append(it)
    return result

def build_brief(top_items: List[Dict], report_type: str, report_url: str, total: int, date_str: str) -> str:
    if report_type == "papers":
        title_prefix = "📚 Renegade AI 学术简报"
    else:
        title_prefix = "📰 Renegade AI 资讯简报"

    lines = [
        f"【{title_prefix}】",
        f"日期：{date_str} | 共{total}条 | 精选{len(top_items)}条",
        "——————————————————"
    ]

    for it in top_items:
        title = it.get("title", "")[:75]
        score = f"{it.get('score_num',0):.1f}/10"
        url = it.get("url", "")
        summary = it.get("summary", "")

        lines.append(f"标题：{title}")
        lines.append(f"评分：{score}")
        lines.append(f"链接：{url}")
        if summary and summary != "N/A":
            lines.append(f"摘要：{summary[:130]}...")
        lines.append("——————————————————")

    lines.append(f"完整报告：{report_url}")
    return "\n".join(lines)

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--type", choices=["news","papers"], default="news")
    parser.add_argument("--file", default=None)
    parser.add_argument("--min-score", type=float, default=4.0)
    parser.add_argument("--top-n", type=int, default=5)
    args = parser.parse_args()

    base_url = os.getenv("REPORT_BASE_URL", "https://brook-han.github.io/renegade-ai-Updater")

    if args.file and Path(args.file).exists():
        latest_md = Path(args.file)
    else:
        rt = "academic" if args.type=="papers" else "news"
        files = sorted(Path().glob(f"reports/{rt}/*.md"), key=lambda x:x.stat().st_mtime, reverse=True)
        if not files:
            print("⚠️ 未找到报告文件")
            return
        latest_md = files[0]

    items = parse_items(str(latest_md), args.min_score)
    if not items:
        print("⚠️ 无满足评分内容")
        return

    items.sort(key=lambda x:x["score_num"], reverse=True)
    top = items[:args.top_n]

    date_match = re.search(r'(\d{4}-\d{2}-\d{2})', latest_md.name)
    date_str = date_match.group(1) if date_match else ""
    rel_path = latest_md.relative_to("reports").with_suffix(".html")
    report_url = f"{base_url}/{rel_path}"

    msg = build_brief(top, args.type, report_url, len(items), date_str)
    send_qq_msg(msg)

if __name__ == "__main__":
    main()