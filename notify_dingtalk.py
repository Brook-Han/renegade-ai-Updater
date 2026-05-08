#!/usr/bin/env python3
"""解析最新资讯报告，将紧急高相关条目推送到钉钉群"""

import os
import re
import sys
import time
import hmac
import hashlib
import base64
import urllib.parse
import requests
from pathlib import Path
from datetime import date


def generate_sign(secret: str) -> tuple:
    """生成钉钉加签"""
    timestamp = str(round(time.time() * 1000))
    string_to_sign = f"{timestamp}\n{secret}"
    hmac_code = hmac.new(
        secret.encode(), string_to_sign.encode(), digestmod=hashlib.sha256
    ).digest()
    sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))
    return timestamp, sign


def send_dingtalk(webhook: str, secret: str, title: str, text: str) -> bool:
    """发送 Markdown 消息到钉钉"""
    timestamp, sign = generate_sign(secret)
    url = f"{webhook}&timestamp={timestamp}&sign={sign}"
    payload = {"msgtype": "markdown", "markdown": {"title": title, "text": text}}
    try:
        r = requests.post(url, json=payload, timeout=10)
        if r.status_code == 200 and r.json().get("errcode") == 0:
            print("✅ 钉钉推送成功")
            return True
        print(f"❌ 钉钉推送失败: {r.text}")
    except Exception as e:
        print(f"❌ 推送异常: {e}")
    return False


def extract_field_from_line(line: str, field_name: str) -> str:
    """从 Markdown 列表项中提取字段值，如 '- **最终评分**: 8.5/10'"""
    # 匹配 "- **字段名**: 值" 或 "- **字段名**: **值**"
    pattern = rf"-\s*\*+\s*{re.escape(field_name)}\s*\*+\s*:\s*(.*)"
    m = re.search(pattern, line, re.IGNORECASE)
    if m:
        val = m.group(1).strip()
        # 去除可能的 markdown 加粗
        val = re.sub(r"\*+", "", val).strip()
        return val
    return ""


def extract_high_relevance_immediate(report_path: str) -> list[dict]:
    """从 Markdown 报告中提取评分≥7 且 urgency=immediate 的条目"""
    items, current = [], {}
    try:
        content = Path(report_path).read_text(encoding="utf-8")
    except Exception:
        return []

    for line in content.split("\n"):
        stripped = line.strip()
        # 标题行：以 ### 开头且后面有文字
        if stripped.startswith("### ") and len(stripped) > 4:
            if current.get("title"):
                items.append(current)
            current = {"title": stripped[4:].strip()}
            continue

        # 提取字段
        if not current.get("score"):
            s = extract_field_from_line(stripped, "最终评分")
            if s:
                current["score"] = s

        if not current.get("urgency"):
            s = extract_field_from_line(stripped, "紧迫度")
            if s:
                current["urgency"] = s

        if not current.get("summary"):
            s = extract_field_from_line(stripped, "核心发现")
            if s:
                current["summary"] = s

        if not current.get("url"):
            s = extract_field_from_line(stripped, "链接")
            if s:
                current["url"] = s

    if current.get("title"):
        items.append(current)

    result = []
    for i in items:
        urgency = i.get("urgency", "").strip().lower()
        score_str = i.get("score", "0").strip()
        try:
            score = float(score_str.split("/")[0].strip())
        except ValueError:
            continue
        if urgency == "immediate" and score >= 7:
            result.append(i)
    return result


def build_markdown(items: list[dict]) -> str:
    """构建简洁的手机可读消息"""
    lines = [
        f"## 🔬 Renegade AI 紧急警报",
        f"**日期**: {date.today().isoformat()}  |  **紧急条目**: {len(items)} 篇\n",
        "---\n",
    ]
    for idx, item in enumerate(items[:5], 1):
        title = item.get("title", "N/A")[:60]
        score = item.get("score", "N/A")
        summary = item.get("summary", "")[:120]
        url = item.get("url", "#")
        lines.append(f"### {idx}. [{title}]({url})")
        lines.append(f"- 评分: **{score}**")
        lines.append(f"- {summary}")
        lines.append("")
    if len(items) > 5:
        lines.append(f"\n> 共 {len(items)} 条，仅显示前 5 条")
    return "\n".join(lines)


if __name__ == "__main__":
    webhook = os.getenv("DINGTALK_WEBHOOK", "")
    secret = os.getenv("DINGTALK_SECRET", "")
    if not webhook or not secret:
        print("❌ 缺少 DINGTALK_WEBHOOK 或 DINGTALK_SECRET 环境变量")
        sys.exit(1)

    # 获取最新报告文件
    report_files = sorted(Path("reports").glob("news_report_multi_*.md"))
    if not report_files:
        print("ℹ️ 未找到资讯报告，跳过推送")
        sys.exit(0)

    latest = report_files[-1]
    print(f"📄 解析报告: {latest}")
    items = extract_high_relevance_immediate(str(latest))

    if not items:
        print("ℹ️ 今日无紧急高相关条目，跳过推送")
        sys.exit(0)

    message = build_markdown(items)
    send_dingtalk(webhook, secret, f"Renegade AI 紧急警报 ({len(items)}条)", message)