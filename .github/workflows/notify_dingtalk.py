#!/usr/bin/env python3
"""
钉钉通知脚本 — 将高相关警报推送到钉钉群
"""

import sys
import json
import time
import hmac
import hashlib
import base64
import urllib.parse
import requests
import os
from pathlib import Path

def generate_sign(secret: str) -> tuple[str, str]:
    """生成钉钉机器人加签"""
    timestamp = str(round(time.time() * 1000))
    string_to_sign = f"{timestamp}\n{secret}"
    hmac_code = hmac.new(
        secret.encode("utf-8"),
        string_to_sign.encode("utf-8"),
        digestmod=hashlib.sha256
    ).digest()
    sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))
    return timestamp, sign

def send_dingtalk(webhook: str, secret: str, title: str, text: str):
    """发送 Markdown 消息到钉钉"""
    timestamp, sign = generate_sign(secret)
    url = f"{webhook}&timestamp={timestamp}&sign={sign}"

    payload = {
        "msgtype": "markdown",
        "markdown": {
            "title": title,
            "text": text,
        },
    }

    resp = requests.post(url, json=payload, timeout=10)
    if resp.status_code == 200 and resp.json().get("errcode") == 0:
        print(f"✅ 钉钉推送成功: {title}")
    else:
        print(f"❌ 钉钉推送失败: {resp.text}")

def parse_high_relevance_items(report_path: str) -> list[dict]:
    """从报告中提取高相关且紧急的条目"""
    content = Path(report_path).read_text(encoding="utf-8")
    items = []
    
    # 简单解析 Markdown 报告中的高相关条目
    in_high_section = False
    current_item = {}
    
    for line in content.split("\n"):
        if line.startswith("## ⭐ 高相关"):
            in_high_section = True
            continue
        if in_high_section and line.startswith("## "):
            break
        
        if in_high_section:
            if line.startswith("### "):
                if current_item.get("title"):
                    items.append(current_item)
                current_item = {"title": line.replace("### ", "").strip()}
            elif line.startswith("- **最终评分**"):
                current_item["score"] = line.split("**")[3] if "**" in line else "N/A"
            elif line.startswith("- **紧迫度**"):
                current_item["urgency"] = line.split("**")[3] if "**" in line else "N/A"
            elif line.startswith("- **核心发现**"):
                current_item["summary"] = line.split("**")[3] if "**" in line else "N/A"
            elif line.startswith("- **链接**"):
                current_item["url"] = line.split("**: ")[-1] if "**: " in line else "#"

    if current_item.get("title"):
        items.append(current_item)
    
    # 只保留 urgency 为 immediate 的
    return [it for it in items if it.get("urgency") == "immediate"]

def build_markdown_message(report_date: str, items: list[dict]) -> str:
    """构建钉钉 Markdown 消息"""
    lines = [
        f"## 🔬 Renegade AI 资讯警报",
        f"**日期**: {report_date}",
        f"**紧急条目**: {len(items)} 篇\n",
        "---\n",
    ]
    
    for i, item in enumerate(items[:5], 1):  # 最多显示5条
        url = item.get("url", "#")
        lines.append(f"### {i}. [{item.get('title', 'N/A')[:50]}...]({url})")
        lines.append(f"- **评分**: {item.get('score', 'N/A')}")
        lines.append(f"- **发现**: {item.get('summary', 'N/A')[:100]}...")
        lines.append("")
    
    if len(items) > 5:
        lines.append(f"\n> *共 {len(items)} 条，仅显示前 5 条*")
    
    return "\n".join(lines)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python notify_dingtalk.py <报告文件路径>")
        sys.exit(1)

    report_path = sys.argv[1]
    webhook = os.getenv("DINGTALK_WEBHOOK", "")
    secret = os.getenv("DINGTALK_SECRET", "")

    if not webhook or not secret:
        print("❌ 请设置 DINGTALK_WEBHOOK 和 DINGTALK_SECRET 环境变量")
        sys.exit(1)

    from datetime import date
    report_date = date.today().isoformat()
    
    high_items = parse_high_relevance_items(report_path)
    
    if high_items:
        message = build_markdown_message(report_date, high_items)
        send_dingtalk(webhook, secret, f"Renegade AI 紧急警报 ({len(high_items)}条)", message)
    else:
        # 也可以选择不推无紧急条目，或推送一条"今日无紧急条目"
        print("ℹ️ 今日无紧急条目，跳过推送")