#!/usr/bin/env python3
"""解析最新报告（资讯或论文），整理成简报推送到钉钉"""

import os, sys, time, hmac, hashlib, base64, urllib.parse, re, requests
from pathlib import Path
from datetime import date


def generate_sign(secret: str) -> tuple:
    ts = str(round(time.time() * 1000))
    to_sign = f"{ts}\n{secret}".encode()
    sign = urllib.parse.quote_plus(base64.b64encode(hmac.new(secret.encode(), to_sign, hashlib.sha256).digest()))
    return ts, sign


def send_dingtalk(webhook, secret, title, text):
    ts, sign = generate_sign(secret)
    url = f"{webhook}&timestamp={ts}&sign={sign}"
    r = requests.post(url, json={"msgtype":"markdown","markdown":{"title":title,"text":text}}, timeout=10)
    return r.json().get("errcode") == 0


def extract_field(line: str, field_name: str) -> str:
    pattern = rf"-\s*\*+\s*{re.escape(field_name)}\s*\*+\s*:\s*(.*)"
    m = re.search(pattern, line, re.IGNORECASE)
    if m:
        val = m.group(1).strip()
        return re.sub(r"\*+", "", val).strip()
    return ""


def parse_items(report_path: str, min_score: float = 4.0) -> list[dict]:
    """提取评分>=min_score的所有条目，包含核心发现和关联"""
    content = Path(report_path).read_text(encoding="utf-8")
    items, cur = [], {}
    for line in content.split("\n"):
        s = line.strip()
        if s.startswith("### ") and len(s) > 4:
            if cur.get("title"):
                items.append(cur)
            cur = {"title": s[4:].strip()}
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
    if cur.get("title"):
        items.append(cur)

    result = []
    for it in items:
        try:
            score = float(it.get("score","0").split("/")[0])
        except ValueError:
            continue
        if score >= min_score:
            result.append(it)
    return result


def build_brief(items: list[dict], report_type: str = "news") -> str:
    """根据报告类型构建不同样式的简报"""
    total = len(items)
    urgent_count = sum(1 for i in items if i.get("urgency","").strip().lower() == "immediate")

    if report_type == "papers":
        title_prefix = "📚 **Renegade AI 每周论文简报**"
        report_url = f"https://github.com/Brook-Han/renegade-ai-Updater/blob/main/reports/papers_report_multi_{date.today().isoformat()}.md"
    else:
        title_prefix = "📰 **Renegade AI 每日资讯简报**"
        report_url = f"https://github.com/Brook-Han/renegade-ai-Updater/blob/main/reports/news_report_multi_{date.today().isoformat()}.md"

    lines = [
        f"## {title_prefix}",
        f"**{date.today().isoformat()}** · 共 {total} 条",
        "",
    ]

    # 紧急条目
    if urgent_count:
        urgency_title = "🕙 及时更新" if report_type == "news" else "🚨 紧急更新"
        lines.append(f"### {urgency_title}")
        lines.append("")
        for i in items:
            if i.get("urgency","").strip().lower() == "immediate":
                # 放宽长度，不再粗暴截断
                title = i.get("title","")[:150]
                score = i.get("score","")
                summary = i.get("summary","")
                implications = i.get("implications","")
                url = i.get("url","#")
                
                lines.append(f"**{title}** [查看原文]({url})")
                lines.append(f"- 评分：{score}")
                lines.append(f"- 概要：{summary}")
                if implications:
                    lines.append(f"- 关联：{implications}")
                # 每条之间空一行分隔
                lines.append("")

    # 高相关
    high = [i for i in items if float(i.get("score","0").split("/")[0]) >= 7 and i.get("urgency","").strip().lower() != "immediate"]
    if high:
        lines.append("### 🔥 高相关")
        lines.append("")
        for i in high:
            title = i.get("title","")[:150]
            score = i.get("score","")
            summary = i.get("summary","")
            url = i.get("url","#")
            lines.append(f"- **{title}** [查看原文]({url})")
            lines.append(f"  评分：{score}｜{summary}")
            lines.append("")

    # 中相关
    medium = [i for i in items if 4 <= float(i.get("score","0").split("/")[0]) < 7]
    if medium:
        lines.append("### 📌 其他关注")
        lines.append("")
        for i in medium[:5]:
            title = i.get("title","")[:150]
            score = i.get("score","")
            url = i.get("url","#")
            lines.append(f"- **{title}** [查看原文]({url}) （评分：{score}）")
            lines.append("")

    if total > len(high) + len(medium) + urgent_count:
        lines.append(f"\n> 更多完整内容见 [完整报告]({report_url})")

    return "\n".join(lines)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--type", choices=["news", "papers"], default="news",
                        help="报告类型: news (默认) 或 papers")
    args = parser.parse_args()

    webhook = os.getenv("DINGTALK_WEBHOOK","")
    secret = os.getenv("DINGTALK_SECRET","")
    if not webhook or not secret:
        sys.exit("missing env")

    # 根据类型选择文件匹配模式
    file_pattern = "news_report_multi_*.md" if args.type == "news" else "papers_report_multi_*.md"
    report_files = sorted(Path("reports").glob(file_pattern))
    if not report_files:
        print("no report")
        sys.exit(0)

    latest = report_files[-1]
    print(f"📄 {latest}")
    items = parse_items(str(latest), min_score=4.0)

    if not items:
        print("no relevant items")
        sys.exit(0)

    msg = build_brief(items, args.type)
    title = f"Renegade AI {'每周论文' if args.type == 'papers' else '每日资讯'}简报 ({len(items)}条)"
    ok = send_dingtalk(webhook, secret, title, msg)
    print("✅" if ok else "❌")