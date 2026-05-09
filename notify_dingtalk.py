#!/usr/bin/env python3
"""解析最新报告（资讯或论文），整理成简报推送到钉钉（对齐 HTML 页面信息）"""

import os, sys, time, hmac, hashlib, base64, urllib.parse, re, requests
from pathlib import Path
from datetime import date

# -------------------- 钉钉签名与发送 --------------------
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

# -------------------- MD 解析 --------------------
def extract_field(line: str, field_name: str) -> str:
    pattern = rf"-\s*\*+\s*{re.escape(field_name)}\s*\*+\s*:\s*(.*)"
    m = re.search(pattern, line, re.IGNORECASE)
    if m:
        val = m.group(1).strip()
        return re.sub(r"\*+", "", val).strip()
    return ""

def parse_items(report_path: str, min_score: float = 4.0) -> list[dict]:
    """提取评分>=min_score的所有条目，包含核心发现、关联、章节、草稿状态"""
    content = Path(report_path).read_text(encoding="utf-8")
    items, cur = [], {}
    in_draft = False
    draft_lines = []
    for line in content.split("\n"):
        s = line.strip()
        # 检测新条目
        if s.startswith("### ") and len(s) > 4:
            # 保存上一个条目
            if cur.get("title"):
                if draft_lines:
                    cur["draft"] = "\n".join(draft_lines).strip()
                items.append(cur)
                draft_lines = []
            cur = {"title": s[4:].strip()}
            in_draft = False
            continue
        # 采集草稿段落（在 ✍️ 之后）
        if "✍️ 自动生成书稿草稿" in s or "自动生成书稿草稿" in s:
            in_draft = True
            continue
        if in_draft:
            draft_lines.append(s)
            if s.startswith("###") or s.startswith("---"):  # 草稿区域结束
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
    # 最后一个条目
    if cur.get("title"):
        if draft_lines:
            cur["draft"] = "\n".join(draft_lines).strip()
        items.append(cur)

    # 过滤评分
    result = []
    for it in items:
        try:
            score = float(it.get("score", "0").split("/")[0])
        except ValueError:
            continue
        if score >= min_score:
            it["score_num"] = score
            result.append(it)
    return result

# -------------------- 构造钉钉消息 --------------------
def build_brief(items: list[dict], report_type: str = "news", report_base_url: str = "") -> str:
    """生成对齐 HTML 页面的简报"""
    total = len(items)
    urgent = [i for i in items if i.get("urgency", "").strip().lower() == "immediate"]
    high = [i for i in items if i.get("score_num", 0) >= 6.5 and i not in urgent]
    medium = [i for i in items if 4.0 <= i.get("score_num", 0) < 6.5]

    today = date.today().isoformat()
    # 报告链接（优先使用 HTML 版本，否则用 MD）
    if report_base_url:
        if report_type == "news":
            report_url = f"{report_base_url}/news_report_multi_{today}.html"  # 需确保文件名匹配
        else:
            report_url = f"{report_base_url}/papers_report_multi_{today}.html"
    else:
        # 回退到 GitHub MD 链接
        if report_type == "news":
            report_url = f"https://github.com/Brook-Han/renegade-ai-Updater/blob/main/reports/news_report_multi_{today}.md"
        else:
            report_url = f"https://github.com/Brook-Han/renegade-ai-Updater/blob/main/reports/papers_report_multi_{today}.md"

    title_prefix = "📚 **Renegade AI 每周论文简报**" if report_type == "papers" else "📰 **Renegade AI 每日资讯简报**"
    lines = [
        f"## {title_prefix}",
        f"**{today}** · 总条目 {total} | 🔥 高相关 {len(high)} | 📌 其他关注 {len(medium)}",
        "",
    ]

    # --- 紧急更新 ---
    if urgent:
        lines.append("### 🚨 需立即更新 (Immediate)")
        for it in urgent:
            lines.extend(_format_item(it))
        lines.append("")

    # --- 高相关 ---
    if high:
        lines.append("### 🔥 高相关 (≥6.5)")
        for it in high:
            lines.extend(_format_item(it))
        lines.append("")

    # --- 中等关注（最多显示 5 条）---
    if medium:
        lines.append("### 📌 其他关注 (4.0–6.4)")
        for it in medium[:5]:
            lines.extend(_format_item(it, brief=True))
        if len(medium) > 5:
            lines.append(f"\n> ⚡ 还有 {len(medium) - 5} 条，详见完整报告")
        lines.append("")

    lines.append(f"> 📄 [查看完整报告（含书稿草稿）]({report_url})")
    return "\n".join(lines)


def _format_item(it: dict, brief: bool = False) -> list[str]:
    """格式化单个条目，对齐 HTML 卡片信息"""
    title = it.get("title", "")[:150]
    score = f"{it.get('score_num', 0):.1f}/10"
    url = it.get("url", "#")
    chapter = it.get("chapter", "")
    summary = it.get("summary", "")
    implications = it.get("implications", "")
    has_draft = bool(it.get("draft", "") and len(it["draft"]) > 30)

    block = []
    block.append(f"**{title}** [原文]({url})")
    block.append(f"- ⭐ 评分：{score}")
    if chapter and chapter != "N/A":
        block.append(f"- 📍 {chapter}")
    if summary and summary != "N/A":
        block.append(f"- 📝 {summary[:200]}")
    if implications and implications != "N/A":
        block.append(f"- 🔗 {implications}")
    if has_draft:
        block.append(f"- ✍️ 已生成书稿草稿")
    if not brief and has_draft:
        # 展示草稿前 80 字预览
        draft_preview = it["draft"].replace("\n", " ")[:80]
        block.append(f"  > {draft_preview}...")
    block.append("")
    return block


# -------------------- 主入口 --------------------
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--type", choices=["news", "papers"], default="news")
    args = parser.parse_args()

    webhook = os.getenv("DINGTALK_WEBHOOK", "")
    secret = os.getenv("DINGTALK_SECRET", "")
    if not webhook or not secret:
        sys.exit("missing env")

    # 报告基础 URL（用于 HTML 版本；不设置则默认 GitHub MD）
    base_url = os.getenv("REPORT_BASE_URL", "")

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

    msg = build_brief(items, args.type, base_url)
    title = f"Renegade AI {'论文' if args.type == 'papers' else '资讯'}简报 ({len(items)}条)"
    ok = send_dingtalk(webhook, secret, title, msg)
    print("✅" if ok else "❌")