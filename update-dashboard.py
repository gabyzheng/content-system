#!/usr/bin/env python3
"""
选题看板数据更新脚本
读取 00-选题记录.md + 扫描 02-选题内容/ 目录，生成 dashboard.html
用法: python3 update-dashboard.py
"""

import os
import re
import json
from pathlib import Path

BASE_DIR = Path(__file__).parent
TOPIC_FILE = BASE_DIR / "01-选题管理" / "00-选题记录.md"
CONTENT_DIR = BASE_DIR / "02-选题内容"
OUTPUT_FILE = BASE_DIR / "dashboard.html"

# 各类型的流水线阶段定义
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
    "日报": "fa-calendar-check",
    "竞品分析": "fa-chart-bar",
    "社交卡片": "fa-share-nodes",
    "其他": "fa-file-lines",
}

TYPE_COLORS = {
    "公众号文章": {"bg": "bg-emerald-500/10", "text": "text-emerald-400", "border": "border-emerald-500/30"},
    "PPT": {"bg": "bg-orange-500/10", "text": "text-orange-400", "border": "border-orange-500/30"},
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
    """解析选题记录 md 文件"""
    if not TOPIC_FILE.exists():
        print(f"⚠️  选题记录文件不存在: {TOPIC_FILE}")
        return []

    content = TOPIC_FILE.read_text(encoding="utf-8")
    topics = []

    # 只解析「选题列表」之后的选题块
    parts = content.split("## 选题列表")
    if len(parts) < 2:
        return []
    topic_section = parts[1]

    pattern = r"### \[([^\]]+)\] (.+?)\n((?:- [^\n]+\n?)+)"
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
                # 提取主状态
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
    """扫描选题工作目录，获取各阶段文件信息"""
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
                    files.append({
                        "name": f.name,
                        "size": f.stat().st_size,
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


def generate_html(topics):
    """生成 dashboard.html"""
    # 为每个选题补充流水线数据
    for topic in topics:
        pipeline = scan_pipeline(topic)
        topic["pipeline"] = pipeline["stages"]
        topic["total_files"] = pipeline["total_files"]

    data_json = json.dumps(topics, ensure_ascii=False, indent=2)

    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Content Pipeline · 选题看板</title>
<script src="https://cdn.tailwindcss.com"></script>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');
  * {{ font-family: 'Inter', system-ui, sans-serif; }}
  .mono {{ font-family: 'JetBrains Mono', monospace; }}
  body {{ background: #0a0a0f; color: #e2e8f0; }}
  .glass {{ background: rgba(255,255,255,0.03); backdrop-filter: blur(20px); border: 1px solid rgba(255,255,255,0.06); }}
  .glass-hover:hover {{ background: rgba(255,255,255,0.06); border-color: rgba(255,255,255,0.12); }}
  .card {{ border-radius: 16px; transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1); }}
  .card:hover {{ transform: translateY(-2px); box-shadow: 0 8px 30px rgba(0,0,0,0.4); }}
  .pipeline-dot {{ width: 8px; height: 8px; border-radius: 50%; }}
  .pipeline-line {{ width: 24px; height: 2px; }}
  .file-tree {{ max-height: 0; overflow: hidden; transition: max-height 0.4s ease; }}
  .file-tree.open {{ max-height: 800px; }}
  .stat-card {{ position: relative; overflow: hidden; }}
  .stat-card::after {{ content: ''; position: absolute; top: -50%; right: -50%; width: 100%; height: 100%; background: radial-gradient(circle, rgba(255,255,255,0.03) 0%, transparent 70%); }}
  .topic-card {{ border-left: 3px solid transparent; }}
  .topic-card.status-已发布 {{ border-left-color: #10b981; }}
  .topic-card.status-已深化 {{ border-left-color: #3b82f6; }}
  .topic-card.status-待深化 {{ border-left-color: #f59e0b; }}
  .topic-card.status-放弃 {{ border-left-color: #64748b; }}
  ::-webkit-scrollbar {{ width: 6px; }}
  ::-webkit-scrollbar-track {{ background: transparent; }}
  ::-webkit-scrollbar-thumb {{ background: rgba(255,255,255,0.1); border-radius: 3px; }}
  .filter-btn.active {{ background: rgba(255,255,255,0.1) !important; border-color: rgba(255,255,255,0.2) !important; }}
  @keyframes fadeInUp {{ from {{ opacity: 0; transform: translateY(12px); }} to {{ opacity: 1; transform: translateY(0); }} }}
  .animate-in {{ animation: fadeInUp 0.5s ease forwards; }}
</style>
</head>
<body class="min-h-screen">

<!-- Header -->
<header class="border-b border-white/5 glass sticky top-0 z-50">
  <div class="max-w-7xl mx-auto px-6 py-5 flex items-center justify-between">
    <div class="flex items-center gap-4">
      <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center shadow-lg shadow-blue-500/20">
        <i class="fa-solid fa-layer-group text-white text-lg"></i>
      </div>
      <div>
        <h1 class="text-xl font-semibold tracking-tight">Content Pipeline</h1>
        <p class="text-xs text-slate-500">选题看板 · 选题驱动 + 分支流水线</p>
      </div>
    </div>
    <div class="flex items-center gap-3 text-xs text-slate-500">
      <span class="glass px-3 py-1.5 rounded-full flex items-center gap-1.5">
        <i class="fa-regular fa-clock"></i>
        <span id="updateTime">--</span>
      </span>
      <a href="https://github.com/gabyzheng/content-system" target="_blank" class="glass px-3 py-1.5 rounded-full flex items-center gap-1.5 hover:text-slate-300 transition-colors">
        <i class="fa-brands fa-github"></i>
        <span>GitHub</span>
      </a>
    </div>
  </div>
</header>

<main class="max-w-7xl mx-auto px-6 py-8">
  <!-- Stats Row -->
  <div id="statsRow" class="grid grid-cols-2 md:grid-cols-5 gap-4 mb-8"></div>

  <!-- Filter Bar -->
  <div class="flex flex-wrap items-center gap-3 mb-6">
    <span class="text-xs text-slate-500 uppercase tracking-wider mr-1">筛选</span>
    <div id="filterBar" class="flex flex-wrap gap-2"></div>
  </div>

  <!-- Topic List -->
  <div id="topicList" class="space-y-4"></div>

  <!-- Empty State -->
  <div id="emptyState" class="hidden text-center py-20">
    <div class="w-20 h-20 mx-auto mb-6 rounded-2xl glass flex items-center justify-center">
      <i class="fa-solid fa-inbox text-3xl text-slate-600"></i>
    </div>
    <h3 class="text-lg font-medium text-slate-400 mb-2">暂无选题</h3>
    <p class="text-sm text-slate-600">在飞书中对大大驴说「记选题」来创建第一个选题</p>
  </div>
</main>

<script>
const DATA = {data_json};

const TYPE_ICONS = {json.dumps(TYPE_ICONS, ensure_ascii=False)};
const TYPE_COLORS = {json.dumps(TYPE_COLORS, ensure_ascii=False)};
const STATUS_CONFIG = {json.dumps(STATUS_CONFIG, ensure_ascii=False)};

let currentFilter = '全部';

function formatSize(bytes) {{
  if (bytes < 1024) return bytes + ' B';
  if (bytes < 1048576) return (bytes / 1024).toFixed(1) + ' KB';
  return (bytes / 1048576).toFixed(1) + ' MB';
}}

function renderStats() {{
  const counts = {{ total: DATA.length, '待深化': 0, '已深化': 0, '已发布': 0, '放弃': 0 }};
  DATA.forEach(t => {{ if (counts[t.status] !== undefined) counts[t.status]++; }});

  const stats = [
    {{ label: '总计', value: counts.total, icon: 'fa-layer-group', color: 'from-blue-500 to-purple-600' }},
    {{ label: '待深化', value: counts['待深化'], icon: 'fa-circle', color: 'from-amber-500 to-orange-600' }},
    {{ label: '已深化', value: counts['已深化'], icon: 'fa-circle-dot', color: 'from-blue-500 to-cyan-600' }},
    {{ label: '已发布', value: counts['已发布'], icon: 'fa-circle-check', color: 'from-emerald-500 to-teal-600' }},
    {{ label: '放弃', value: counts['放弃'], icon: 'fa-circle-xmark', color: 'from-slate-500 to-zinc-600' }},
  ];

  document.getElementById('statsRow').innerHTML = stats.map((s, i) => `
    <div class="glass card stat-card p-5 animate-in" style="animation-delay: ${{i * 0.08}}s">
      <div class="flex items-center justify-between mb-3">
        <span class="text-xs text-slate-500 uppercase tracking-wider">${{s.label}}</span>
        <div class="w-8 h-8 rounded-lg bg-gradient-to-br ${{s.color}} flex items-center justify-center shadow-lg opacity-80">
          <i class="fa-solid ${{s.icon}} text-white text-xs"></i>
        </div>
      </div>
      <div class="text-3xl font-bold tracking-tight">${{s.value}}</div>
    </div>
  `).join('');
}}

function renderFilters() {{
  const types = ['全部', ...new Set(DATA.map(t => t.type))];
  document.getElementById('filterBar').innerHTML = types.map(t => `
    <button onclick="filterBy('${{t}}')" class="filter-btn px-4 py-2 rounded-xl text-sm font-medium transition-all duration-200 glass-hover ${{currentFilter === t ? 'active' : ''}}">
      ${{t === '全部' ? '📋 全部' : '<i class="fa-solid ' + (TYPE_ICONS[t] || 'fa-file') + ' mr-1.5"></i>' + t}}
    </button>
  `).join('');
}}

function filterBy(type) {{
  currentFilter = type;
  renderFilters();
  renderTopics();
}}

function renderPipeline(stages) {{
  if (!stages || stages.length === 0) return '';
  const hasFiles = stages.filter(s => s.file_count > 0).length;
  const total = stages.length;

  return `
    <div class="flex items-center gap-1 flex-wrap">
      ${{stages.map((s, i) => {{
        const done = s.file_count > 0;
        const isLast = s.label === '已发布' && done;
        return `
          <div class="flex items-center gap-1">
            <div class="flex items-center gap-1.5 px-2 py-1 rounded-lg text-xs ${{done ? 'bg-white/5' : 'opacity-30'}}">
              <div class="pipeline-dot ${{done ? (isLast ? 'bg-emerald-400 shadow-[0_0_6px_rgba(52,211,153,0.5)]' : 'bg-blue-400') : 'bg-slate-600'}}"></div>
              <span class="${{done ? 'text-slate-300' : 'text-slate-600'}}">${{s.label}}</span>
              ${{s.file_count > 0 ? `<span class="mono text-[10px] text-slate-500">${{s.file_count}}</span>` : ''}}
            </div>
            ${{i < stages.length - 1 ? `<div class="pipeline-line ${{done ? 'bg-blue-500/40' : 'bg-slate-700'}}"></div>` : ''}}
          </div>
        `;
      }}).join('')}}
    </div>
  `;
}}

function renderFileTree(stages, topicId) {{
  if (!stages || stages.length === 0) return '';
  return `
    <div class="file-tree" id="files-${{topicId}}">
      <div class="mt-4 pt-4 border-t border-white/5">
        <div class="text-xs text-slate-500 mb-3 uppercase tracking-wider">📂 过程文件</div>
        <div class="space-y-1">
          ${{stages.map(s => `
            <div class="flex items-center justify-between py-1.5 px-2 rounded-lg text-sm ${{s.exists ? 'hover:bg-white/5' : 'opacity-30'}} transition-colors">
              <div class="flex items-center gap-2">
                <i class="fa-solid ${{s.exists ? 'fa-folder text-amber-500/60' : 'fa-folder-open text-slate-600'}} text-xs"></i>
                <span class="${{s.exists ? 'text-slate-300' : 'text-slate-600'}}">${{s.label}}</span>
              </div>
              <span class="mono text-xs ${{s.file_count > 0 ? 'text-slate-400' : 'text-slate-600'}}">${{s.file_count > 0 ? s.file_count + ' 文件' : '空'}}</span>
            </div>
            ${{s.files && s.files.length > 0 ? s.files.map(f => `
              <div class="flex items-center justify-between py-1 pl-8 pr-2 text-xs text-slate-500 hover:text-slate-300 transition-colors">
                <span class="truncate max-w-[300px]"><i class="fa-regular fa-file mr-1.5 text-slate-600"></i>${{f.name}}</span>
                <span class="mono text-slate-600 ml-2">${{formatSize(f.size)}}</span>
              </div>
            `).join('') : ''}}
          `).join('')}}
        </div>
      </div>
    </div>
  `;
}}

function renderTopics() {{
  const filtered = currentFilter === '全部' ? DATA : DATA.filter(t => t.type === currentFilter);
  const container = document.getElementById('topicList');
  const empty = document.getElementById('emptyState');

  if (filtered.length === 0) {{
    container.innerHTML = '';
    empty.classList.remove('hidden');
    return;
  }}
  empty.classList.add('hidden');

  container.innerHTML = filtered.map((t, i) => {{
    const colors = TYPE_COLORS[t.type] || TYPE_COLORS['其他'];
    const statusCfg = STATUS_CONFIG[t.status] || STATUS_CONFIG['待深化'];
    const topicId = i;

    return `
      <div class="glass card topic-card status-${{t.status}} p-6 animate-in" style="animation-delay: ${{i * 0.1}}s">
        <div class="flex flex-col lg:flex-row lg:items-start justify-between gap-4">
          <div class="flex-1 min-w-0">
            <!-- Header -->
            <div class="flex items-center gap-3 mb-3 flex-wrap">
              <span class="px-2.5 py-1 rounded-lg text-xs font-medium ${{colors.bg}} ${{colors.text}} ${{colors.border}} border">
                <i class="fa-solid ${{TYPE_ICONS[t.type] || 'fa-file'}} mr-1"></i>${{t.type}}
              </span>
              <span class="px-2.5 py-1 rounded-lg text-xs font-medium ${{statusCfg.bg}} ${{statusCfg.color}}">
                <i class="fa-solid ${{statusCfg.icon}} mr-1"></i>${{t.status}}
              </span>
              <span class="text-xs text-slate-600">${{t.date}}</span>
            </div>

            <!-- Title -->
            <h3 class="text-lg font-semibold mb-2 text-slate-100">${{t.title}}</h3>

            <!-- Idea -->
            ${{t.idea ? `<p class="text-sm text-slate-400 mb-3 leading-relaxed">${{t.idea}}</p>` : ''}}

            <!-- Keywords -->
            ${{t.keywords && t.keywords.length > 0 ? `
              <div class="flex flex-wrap gap-1.5 mb-4">
                ${{t.keywords.map(k => `<span class="px-2 py-0.5 rounded-md text-[11px] bg-white/5 text-slate-500">#${{k}}</span>`).join('')}}
              </div>
            ` : ''}}

            <!-- Pipeline -->
            <div class="mb-3">
              <div class="text-[10px] text-slate-600 uppercase tracking-wider mb-2">流水线进度</div>
              ${{renderPipeline(t.pipeline)}}
            </div>

            <!-- File Tree Toggle -->
            ${{t.total_files > 0 ? `
              <button onclick="toggleFiles(${{topicId}})" class="flex items-center gap-1.5 text-xs text-slate-500 hover:text-slate-300 transition-colors mt-2">
                <i id="icon-${{topicId}}" class="fa-solid fa-chevron-right text-[10px] transition-transform"></i>
                <span>${{t.total_files}} 个过程文件</span>
              </button>
              ${{renderFileTree(t.pipeline, topicId)}}
            ` : ''}}
          </div>

          <!-- Work Dir -->
          ${{t.work_dir ? `
            <div class="lg:text-right flex-shrink-0">
              <div class="text-[10px] text-slate-600 uppercase tracking-wider mb-1">工作目录</div>
              <code class="mono text-xs text-slate-500 bg-black/30 px-2 py-1 rounded block max-w-[320px] truncate">${{t.work_dir}}</code>
            </div>
          ` : ''}}
        </div>
      </div>
    `;
  }}).join('');
}}

function toggleFiles(id) {{
  const tree = document.getElementById('files-' + id);
  const icon = document.getElementById('icon-' + id);
  if (tree && icon) {{
    tree.classList.toggle('open');
    icon.style.transform = tree.classList.contains('open') ? 'rotate(90deg)' : 'rotate(0deg)';
  }}
}}

// Init
document.getElementById('updateTime').textContent = new Date().toLocaleString('zh-CN', {{ timeZone: 'Asia/Shanghai' }});
renderStats();
renderFilters();
renderTopics();
</script>
</body>
</html>'''

    return html


def main():
    print("📊 选题看板生成器")
    print("=" * 40)

    topics = parse_topics()
    print(f"✅ 解析选题: {len(topics)} 个")

    for t in topics:
        pipeline = scan_pipeline(t)
        file_count = sum(s["file_count"] for s in pipeline["stages"])
        print(f"   📝 {t['title'][:30]}... → {t['status']} ({file_count} 文件)")

    html = generate_html(topics)
    OUTPUT_FILE.write_text(html, encoding="utf-8")
    print(f"\n✅ 已生成: {OUTPUT_FILE}")
    print(f"   大小: {len(html):,} bytes")


if __name__ == "__main__":
    main()
