#!/usr/bin/env python3
"""
generate_report.py
掃描練習檔案與 git log，自動更新 docs/data/progress.json。
每次執行 @save / @push 時自動呼叫。
"""
import json
import os
import subprocess
from datetime import date

# ── 課程定義（與 01-learning-syllabus.md 保持同步）────────────────────────────

SYLLABUS = {
    1: {
        "title":    "變數與資料型態",
        "subtitle": "List & Dict 在 EDA Log 解析的應用",
        "exercises": [
            {"id": "W1-1", "title": "DRC 違規統計"},
            {"id": "W1-2", "title": "Timing Path 排行榜"},
        ],
        "skills_unlocked": {
            "python": ["list", "dict", "sorted()", "lambda"],
            "eda":    ["DRC violations", "Timing slack"],
        },
    },
    2: {
        "title":    "流程控制",
        "subtitle": "逐行讀取超大 EDA Log 的迴圈邏輯",
        "exercises": [
            {"id": "W2-1", "title": "Timing Log 逐行掃描"},
            {"id": "W2-2", "title": "DRC 層別錯誤計數器"},
        ],
        "skills_unlocked": {
            "python": ["for/while loop", "if/elif/else", "break/continue", "streaming read"],
            "eda":    ["Log parsing", "Error classification"],
        },
    },
    3: {
        "title":    "函數與模組",
        "subtitle": "os / sys 模組控制 Linux 環境",
        "exercises": [
            {"id": "W3-1", "title": "EDA 報告路徑掃描器"},
            {"id": "W3-2", "title": "環境變數驅動設定系統"},
        ],
        "skills_unlocked": {
            "python": ["def / return", "os.walk", "sys.argv", "os.environ"],
            "tools":  ["Linux filesystem", "CLI scripting"],
        },
    },
    4: {
        "title":    "檔案讀寫與正規表示式",
        "subtitle": "re 模組高效過濾晶片設計工具報告",
        "exercises": [
            {"id": "W4-1", "title": "Timing Violation 擷取器"},
            {"id": "W4-2", "title": "多工具 Log 聚合分析器"},
        ],
        "skills_unlocked": {
            "python": ["re.compile", "re.search / findall", "with open()", "named groups"],
            "eda":    ["Timing Report parsing", "DRC/Routing log aggregation"],
            "tools":  ["Regex pattern design"],
        },
    },
}

# 掃描練習代碼時忽略的目錄（避免誤判儀表板自身的程式或第三方套件）
IGNORED_DIRS = {".git", "docs", "__pycache__", "node_modules", ".venv"}


def find_completed_exercise_ids(root="."):
    """掃描所有 .py 檔案內容，只要找到 'W1-1' 這類練習編號字串，就視為該題已完成。
    這樣不論使用者把練習存成哪個檔名、放在哪個資料夾，都能被正確偵測到。"""
    all_ids = [ex["id"] for info in SYLLABUS.values() for ex in info["exercises"]]
    found = set()
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in IGNORED_DIRS and not d.startswith(".")]
        for fname in filenames:
            if not fname.endswith(".py") or fname == "generate_report.py":
                continue
            try:
                with open(os.path.join(dirpath, fname), encoding="utf-8") as f:
                    content = f.read()
            except OSError:
                continue
            for ex_id in all_ids:
                if ex_id in content:
                    found.add(ex_id)
    return found

ALL_PENDING = [
    "list", "dict", "sorted() / lambda",
    "for/while loop", "streaming read",
    "def / return", "os.walk", "sys.argv",
    "re.compile", "re.search",
    "Timing Analysis", "DRC", "Routing", "Log aggregation",
]


# ── Git ───────────────────────────────────────────────────────────────────────

def _run(cmd):
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
        return r.stdout.strip()
    except Exception:
        return ""


def get_commits(max_count=30):
    out = _run(["git", "log",
                f"--max-count={max_count}",
                "--pretty=format:%h|%s|%ad",
                "--date=short"])
    commits = []
    for line in out.splitlines():
        parts = line.split("|", 2)
        if len(parts) == 3:
            commits.append({"hash": parts[0], "message": parts[1], "date": parts[2]})
    return commits


def get_start_date():
    d = _run(["git", "log", "--pretty=format:%ad", "--date=short",
              "--reverse", "--max-count=1"])
    return d or str(date.today())


# ── Progress ──────────────────────────────────────────────────────────────────

def week_status(exercises):
    statuses = [e["status"] for e in exercises]
    if all(s == "completed" for s in statuses):
        return "completed"
    if any(s == "completed" for s in statuses):
        return "in_progress"
    return "not_started"


def build_weeks(completed_ids):
    rows = []
    for num, info in sorted(SYLLABUS.items()):
        exercises = [
            {
                "id":     ex["id"],
                "title":  ex["title"],
                "status": "completed" if ex["id"] in completed_ids else "pending",
            }
            for ex in info["exercises"]
        ]
        rows.append({
            "id":        num,
            "title":     info["title"],
            "subtitle":  info["subtitle"],
            "status":    week_status(exercises),
            "exercises": exercises,
        })
    return rows


def build_skills(weeks):
    earned = {"python": set(), "eda": set(), "tools": set()}
    for w in weeks:
        if w["status"] in ("completed", "in_progress"):
            unlocked = SYLLABUS[w["id"]].get("skills_unlocked", {})
            for cat, items in unlocked.items():
                if cat in earned:
                    earned[cat].update(items)

    earned_flat = earned["python"] | earned["eda"] | earned["tools"]
    return {
        "python":  sorted(earned["python"]),
        "eda":     sorted(earned["eda"]),
        "tools":   sorted(earned["tools"]),
        "pending": [s for s in ALL_PENDING if s not in earned_flat],
    }


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    completed_ids = find_completed_exercise_ids()
    weeks   = build_weeks(completed_ids)
    commits = get_commits()
    skills  = build_skills(weeks)

    report = {
        "meta": {
            "last_updated": str(date.today()),
            "start_date":   get_start_date(),
            "github_url":   "https://github.com/tamytammy/learn_python",
        },
        "weeks":   weeks,
        "skills":  skills,
        "commits": commits,
    }

    os.makedirs("docs/data", exist_ok=True)
    with open("docs/data/progress.json", "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    done_w  = sum(1 for w in weeks if w["status"] == "completed")
    done_ex = sum(e["status"] == "completed" for w in weeks for e in w["exercises"])
    print(f"[generate_report] docs/data/progress.json 已更新")
    print(f"  週進度 {done_w}/4 ｜ 練習 {done_ex}/8 ｜ 提交 {len(commits)} 筆")


if __name__ == "__main__":
    main()
