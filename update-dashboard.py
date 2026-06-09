#!/usr/bin/env python3
"""
选题看板数据更新脚本
读取 00-选题记录.md + 扫描 02-选题内容/ 目录，基于模板生成 dashboard.html
用法: python3 update-dashboard.py
"""

import json
import re
from pathlib import Path

BASE_DIR = Path(__file__).parent
TOPIC_FILE = BASE_DIR / "01-选题管理" / "00-选题记录.md"
CONTENT_DIR = BASE_DIR / "02-选题内容"
TEMPLATE_FILE = BASE_DIR / "index.template.html"
OUTPUT_FILE = BASE_DIR / "index.html"
GITHUB_PAGES_BASE = "https://gabyzheng.github.io/content-system"

PIPELINE_STAGES = {
    "公众号文章": [
        ("01-素材检索", "素材检索"),
        ("02-内容生成", "内容生成"),
        ("03-去AI化", "去AI化"),
        ("04-配图", "配图"),
        ("05-可视化", "可视化"),
        ("06-质量检查", "质量检查"),
        ("07-已发布", "已发布"),
    ],
    "PPT": [
        ("01-打透观点", "打透观点"),
        ("02-拆页设计", "拆页设计"),
        ("03-素材检索", "素材检索"),
        ("04-输出JSON", "输出JSON"),
        ("05-配图", "配图"),
        ("06-质量检查", "质量检查"),
        ("07-已发布", "已发布"),
    ],
    "H5-Deck": [
        ("01-打透观点", "打透观点"),
        ("02-拆页设计", "拆页设计"),
        ("03-素材检索", "素材检索"),
        ("04-生成HTML", "生成HTML"),
        ("05-配图", "配图"),
        ("06-质量检查", "质量检查"),
        ("07-已发布", "已发布"),
    ],
    "日报": [
        ("01-素材检索", "素材检索"),
        ("02-内容生成", "内容生成"),
        ("03-去AI化", "去AI化"),
        ("04-质量检查", "质量检查"),
        ("05-已发布", "已发布"),
    ],
    "竞品分析": [
        ("01-素材检索", "素材检索"),
        ("02-内容生成", "内容生成"),
        ("03-质量检查", "质量检查"),
        ("04-已发布", "已发布"),
    ],
    "社交卡片": [
        ("01-素材检索", "素材检索"),
        ("02-内容生成", "内容生成"),
        ("03-可视化", "可视化"),
        ("04-质量检查", "质量检查"),
        ("05-已发布", "已发布"),
    ],
}

TYPE_ICONS = {
    "公众号文章": "fa-newspaper",
    "PPT": "fa-file-powerpoint",
    "H5-Deck": "fa-code",
    "日报": "fa-calendar-check",
    "竞品分析": "fa-chart-bar",
    "社交卡片": "fa-share-nodes",
    "其他": "fa-file-lines",
}

TYPE_COLORS = {
    "公众号文章": {"bg": "bg-emerald-500/10", "text": "text-emerald-400", "border": "border-emerald-500/30"},
    "PPT": {"bg": "bg-orange-500/10", "text": "text-orange-400", "border": "border-orange-500/30"},
    "H5-Deck": {"bg": "bg-cyan-500/10", "text": "text-cyan-400", "border": "border-cyan-500/30"},
    "日报": {"bg": "bg-blue-500/10", "text": "text-blue-400", "border": "border-blue-500/30"},
    "竞品分析": {"bg": "bg-purple-500/10", "text": "text-purple-400", "border": "border-purple-500/30"},
    "社交卡片": {"bg": "bg-pink-500/10", "text": "text-pink-400", "border": "border-pink-500/30"},
    "其他": {"bg": "bg-slate-500/10", "text": "text-slate-400", "border": "border-slate-500/30"},
}

STATUS_CONFIG = {
    "待深化": {"icon": "fa-circle", "color": "text-amber-400", "bg": "bg-amber-500/10"},
    "已深化": {"icon": "fa-circle-dot", "color": "text-blue-400", "bg": "bg-blue-500/10"},
    "已发布": {"icon": "fa-circle-check", "color": "text-emerald-400", "bg": "bg-emerald-500/10"},
    "放弃": {"icon": "fa-circle-xmark", "color": "text-slate-500", "bg": "bg-slate-500/10"},
}


def parse_topics():
    if not TOPIC_FILE.exists():
        print(f"⚠️  选题记录文件不存在: {TOPIC_FILE}")
        return []

    content = TOPIC_FILE.read_text(encoding="utf-8")
    parts = content.split("## 选题列表")
    if len(parts) < 2:
        return []
    topic_section = parts[1]

    pattern = r"### \[([^\]]+)\] (.+?)\n((?:- [^\n]+\n?)+)"
    topics = []
    for match in re.finditer(pattern, topic_section):
        date = match.group(1)
        title = match.group(2).strip()
        meta_block = match.group(3)

        meta = {}
        for line in meta_block.strip().split("\n"):
            line = line.strip()
            if line.startswith("- 类型："):
                meta["type"] = line.replace("- 类型：", "").strip()
            elif line.startswith("- 关键词："):
                meta["keywords"] = [k.strip() for k in line.replace("- 关键词：", "").split(",")]
            elif line.startswith("- 初步想法："):
                meta["idea"] = line.replace("- 初步想法：", "").strip()
            elif line.startswith("- 状态："):
                raw_status = line.replace("- 状态：", "").strip()
                for s in ["待深化", "已深化", "已发布", "放弃"]:
                    if s in raw_status:
                        meta["status"] = s
                        break
                if "status" not in meta:
                    meta["status"] = raw_status
            elif line.startswith("- 工作目录："):
                meta["work_dir"] = line.replace("- 工作目录：", "").strip()

        topics.append({
            "date": date,
            "title": title,
            "type": meta.get("type", "其他"),
            "keywords": meta.get("keywords", []),
            "idea": meta.get("idea", ""),
            "status": meta.get("status", "待深化"),
            "work_dir": meta.get("work_dir", ""),
        })

    return topics


def scan_pipeline(topic):
    work_dir = topic.get("work_dir", "")
    if not work_dir:
        return {"stages": [], "total_files": 0}

    full_path = CONTENT_DIR.parent / work_dir
    if not full_path.exists():
        return {"stages": [], "total_files": 0}

    topic_type = topic.get("type", "其他")
    stages_def = PIPELINE_STAGES.get(topic_type, [])

    stages = []
    total_files = 0
    for dir_name, label in stages_def:
        stage_path = full_path / dir_name
        files = []
        if stage_path.exists():
            for f in sorted(stage_path.iterdir()):
                if f.is_file() and not f.name.startswith("."):
                    rel_path = str(f.relative_to(CONTENT_DIR.parent))
                    ext = f.suffix.lower()
                    gh_pages_url = f"{GITHUB_PAGES_BASE}/{rel_path}" if ext in (".html", ".xml", ".json") else None
                    files.append({
                        "name": f.name,
                        "size": f.stat().st_size,
                        "path": rel_path,
                        "ext": ext,
                        "is_image": ext in (".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg"),
                        "is_md": ext == ".md",
                        "is_html": ext == ".html",
                        "is_xml": ext == ".xml",
                        "is_json": ext == ".json",
                        "gh_pages_url": gh_pages_url,
                    })
        stages.append({
            "dir": dir_name,
            "label": label,
            "file_count": len(files),
            "files": files,
            "exists": stage_path.exists(),
        })
        total_files += len(files)

    return {"stages": stages, "total_files": total_files}


def main():
    print("📊 选题看板生成器")
    print("=" * 40)

    topics = parse_topics()
    print(f"✅ 解析选题: {len(topics)} 个")

    for t in topics:
        pipeline = scan_pipeline(t)
        t["pipeline"] = pipeline["stages"]
        t["total_files"] = pipeline["total_files"]
        file_count = sum(s["file_count"] for s in pipeline["stages"])
        print(f"   📝 {t['title'][:30]}... → {t['status']} ({file_count} 文件)")

    if not TEMPLATE_FILE.exists():
        print(f"❌ 模板文件不存在: {TEMPLATE_FILE}")
        return

    template = TEMPLATE_FILE.read_text(encoding="utf-8")

    html = template.replace("__DATA_JSON__", json.dumps(topics, ensure_ascii=False, indent=2))
    html = html.replace("__TYPE_ICONS__", json.dumps(TYPE_ICONS, ensure_ascii=False))
    html = html.replace("__TYPE_COLORS__", json.dumps(TYPE_COLORS, ensure_ascii=False))
    html = html.replace("__STATUS_CONFIG__", json.dumps(STATUS_CONFIG, ensure_ascii=False))

    OUTPUT_FILE.write_text(html, encoding="utf-8")
    print(f"\n✅ 已生成: {OUTPUT_FILE}")
    print(f"   大小: {len(html):,} bytes")


if __name__ == "__main__":
    main()
