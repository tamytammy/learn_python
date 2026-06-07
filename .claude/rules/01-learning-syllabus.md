# 詳細課程大綱與練習題庫

## 課程設計原則

- 所有練習題以「模擬 EDA 工具 Log 解析」為核心情境
- 每道題目分為三個難度層級：⭐ 基礎 / ⭐⭐ 進階 / ⭐⭐⭐ 挑戰
- 提供骨架（Scaffolding）但不給答案，引導使用者自行推導邏輯
- 每週結束前執行一次 `@review` 以確保代碼品質

---

## 第一週：變數與資料型態

### 學習目標
- 理解 Python 的動態型別系統（vs JavaScript 的差異）
- 掌握 `int`, `float`, `str`, `bool` 四種基礎型態
- 熟悉 `list` 的索引、切片、常用方法（`append`, `extend`, `pop`）
- 熟悉 `dict` 的鍵值操作（`get`, `update`, `keys`, `values`, `items`）
- 理解 `list` vs `dict` 的使用場景選擇

### 情境連結（EDA 視角）
EDA 工具（如 Synopsys DC、Cadence Innovus）每次跑完後都會產生結構化的報告。
這些報告的資料天然對應到 Python 的資料結構：
- **List** → 時序路徑清單、DRC 違規清單（有順序、可重複）
- **Dict** → 單筆 Timing Path 的屬性（`{"path": "A/B", "slack": -0.32, "type": "setup"}`）

### 核心觀念骨架

```python
# List：有順序的違規記錄
drc_violations = []          # 先宣告空 list
drc_violations.append(...)   # 逐一加入違規
print(drc_violations[0])     # 索引取值

# Dict：單筆 timing path 的所有屬性
timing_path = {
    "startpoint": "...",
    "endpoint":   "...",
    "slack":      0.0,       # 正數 = 有餘裕，負數 = 違反時序
    "path_type":  "setup"
}
print(timing_path.get("slack", 0))  # 安全取值，鍵不存在時回傳預設值
```

### 練習題庫

#### 題目 W1-1：DRC 違規統計（⭐⭐）
**情境：** 你收到一份 DRC 報告，裡面有若干違規紀錄，每筆紀錄是一個 dict，包含 `rule_name`、`layer`、`severity`（`"ERROR"` 或 `"WARNING"`）三個欄位。

**任務：**
1. 建立一個 list，至少包含 5 筆違規資料（自行捏造合理數值）
2. 計算 `"ERROR"` 與 `"WARNING"` 各自的數量
3. 找出所有在 `"metal2"` 層上的違規，印出其 `rule_name`

**骨架提示：**
```python
violations = [
    {"rule_name": "...", "layer": "metal1", "severity": "ERROR"},
    # 繼續加入更多筆 ...
]

error_count = 0
warning_count = 0

for v in violations:
    # 如何判斷 severity？用什麼比較運算子？
    pass

# 最後印出統計結果
```

**思考引導：**
- `for` 迴圈如何遍歷 list 內的每個 dict？
- `dict["key"]` 和 `dict.get("key")` 有什麼差別？哪個更安全？

---

#### 題目 W1-2：Timing Path 排行榜（⭐⭐⭐）
**情境：** 一份 Timing Report 內有數十條 timing paths，每條都有 `slack` 值。負數 slack 代表時序違反（Timing Violation），slack 越負越嚴重。

**任務：**
1. 建立至少 6 條 timing path 的 list（每條是一個 dict，含 `name` 和 `slack`）
2. 找出 slack 最小（最嚴重）的 3 條路徑
3. 計算所有 **負 slack** 路徑的平均違反量

**骨架提示：**
```python
paths = [
    {"name": "path_A", "slack": -0.45},
    {"name": "path_B", "slack":  0.12},
    # ...
]

# 如何對 list of dicts 排序？提示：sorted() + key= 參數
# 如何篩選只取負 slack 的路徑？
worst_paths = sorted(paths, key=lambda p: p["slack"])[:3]
```

**思考引導：**
- `lambda` 是什麼？能不能先不用 lambda，改用普通 `def` 寫一個 key function？
- 計算平均值時要注意「除以零」的邊界情況嗎？

---

## 第二週：流程控制

### 學習目標
- 掌握 `if / elif / else` 多條件判斷
- 理解 `for` 迴圈的三種常見模式：遍歷元素、`range()`、`enumerate()`
- 理解 `while` 迴圈與中斷條件（`break`, `continue`）
- **重點：** 如何用 `with open()` 搭配 `for line in file` 逐行讀取超大 Log（記憶體友善）

### 情境連結（EDA 視角）
EDA 工具跑完後的 Log 檔可能高達數 GB，**絕對不能** 用 `readlines()` 整份載入記憶體。
工程師的標準做法是「串流讀取（Streaming）」，每次只處理一行。

### 核心觀念骨架

```python
# 記憶體不友善（禁止用於大檔案）
with open("report.log") as f:
    lines = f.readlines()    # 全部載入記憶體！

# 記憶體友善（正確做法）
with open("report.log") as f:
    for line in f:           # Python file object 本身就是 iterator
        line = line.strip()
        if not line:         # 跳過空行
            continue
        # 在這裡處理每一行
```

### 練習題庫

#### 題目 W2-1：Timing Log 逐行掃描（⭐⭐）
**情境：** 模擬一個 Timing Report 的多行字串（用 `io.StringIO` 模擬檔案物件）。

**任務：**
1. 建立一個多行字串模擬 Log 內容，包含 `[INFO]`、`[WARNING]`、`[ERROR]` 三種前綴
2. 逐行讀取，將 `[ERROR]` 行收集到一個 list
3. 遇到含有 `"END OF REPORT"` 的行時立即停止讀取（不要繼續掃描後面）

**骨架提示：**
```python
import io

log_content = """
[INFO] Starting Timing Analysis...
[WARNING] Slack margin is tight: path_X slack=-0.05
[ERROR] Timing violation found: path_Y slack=-0.32
[INFO] Checking hold time...
[ERROR] Hold violation: path_Z slack=-0.11
END OF REPORT
[INFO] This line should NOT be processed
"""

errors = []
f = io.StringIO(log_content)

for line in f:
    line = line.strip()
    # 如何判斷是否要停止？
    # 如何判斷是否為 ERROR 行？
    pass

print(f"共發現 {len(errors)} 個 Error")
```

---

#### 題目 W2-2：DRC 層別錯誤計數器（⭐⭐⭐）
**情境：** DRC Log 每行格式如：`LAYER metal2: SPACING_ERROR at (100, 200)`

**任務：**
1. 模擬 10 行以上的 DRC Log（包含不同 LAYER 名稱）
2. 用一個 `dict` 統計每個 layer 的錯誤總數（`{"metal1": 3, "metal2": 5, ...}`）
3. 最後印出錯誤最多的前 2 個 layer

**骨架提示：**
```python
layer_counts = {}   # 用 dict 當計數器

for line in log_lines:
    # 如何從字串 "LAYER metal2: SPACING_ERROR at (100, 200)" 取出 "metal2"？
    # 提示：字串的 split() 方法
    # 如何對一個 dict 的 value 做累加？注意「鍵第一次出現」的邊界情況
    pass
```

---

## 第三週：函數與模組

### 學習目標
- 掌握 `def` 定義函數、`return` 回傳值、預設參數
- 理解 Python 的模組系統（`import`、`from X import Y`）
- 熟悉 `os` 模組核心 API：`os.path`, `os.listdir`, `os.walk`, `os.environ`
- 熟悉 `sys` 模組：`sys.argv`（命令列參數）、`sys.exit()`
- 理解函數的單一職責原則（SRP）

### 情境連結（EDA 視角）
EDA 工程師需要管理複雜的目錄結構（工藝節點 / 專案 / 跑次）：
```
/project/
  tsmc28nm/
    run_001/
      timing.rpt
      drc.log
    run_002/
      ...
```
用 Python 的 `os.walk` 可以自動化掃描整棵目錄樹，取代手工 `find` 指令。

### 核心觀念骨架

```python
import os
import sys

def find_reports(root_dir, extension=".rpt"):
    """掃描目錄樹，回傳所有符合副檔名的檔案路徑 list"""
    found = []
    for dirpath, dirnames, filenames in os.walk(root_dir):
        for fname in filenames:
            if fname.endswith(extension):
                full_path = os.path.join(dirpath, fname)
                found.append(full_path)
    return found

if __name__ == "__main__":
    # sys.argv[0] 是腳本本身的名稱
    # sys.argv[1] 才是使用者傳入的第一個參數
    if len(sys.argv) < 2:
        print("Usage: python script.py <root_dir>")
        sys.exit(1)
    reports = find_reports(sys.argv[1])
    print(f"找到 {len(reports)} 份報告")
```

### 練習題庫

#### 題目 W3-1：EDA 報告路徑掃描器（⭐⭐）
**任務：**
1. 用 `os.makedirs` 在本地建立模擬的專案目錄結構（至少 3 層深）
2. 在各目錄內建立假的 `.rpt` 和 `.log` 檔案（`open(path, 'w').close()` 即可）
3. 實作 `find_reports(root, ext)` 函數，回傳符合副檔名的所有路徑
4. 用 `sys.argv` 讓使用者從命令列傳入根目錄路徑

**思考引導：**
- `os.path.join` 和直接字串拼接有什麼差別？（跨平台 `/` vs `\`）
- 函數要不要印出結果？還是只 `return` 讓呼叫端決定怎麼用？

---

#### 題目 W3-2：環境變數驅動的設定系統（⭐⭐⭐）
**情境：** 真實 EDA 環境通常用環境變數控制工具路徑，例如：
```bash
export EDA_PROJECT_ROOT=/data/projects
export EDA_TECH_NODE=tsmc28nm
```

**任務：**
1. 實作 `load_eda_config()` 函數，從 `os.environ` 讀取上述兩個環境變數
2. 若變數不存在，使用合理的預設值並印出警告
3. 回傳一個 `dict`，供其他函數使用

**思考引導：**
- `os.environ["KEY"]` 和 `os.environ.get("KEY", default)` 的差異？
- 這個函數應該在哪裡被呼叫一次？（程式進入點 vs 每次需要時？）

---

## 第四週：檔案讀寫與正規表示式

### 學習目標
- 掌握 `with open()` 的讀（`r`）、寫（`w`）、附加（`a`）模式
- 理解 `re` 模組：`re.search`, `re.findall`, `re.compile`
- 掌握常用正規表示式語法：`\d+`, `\w+`, `[-+]?\d*\.?\d+`, `(?P<name>...)` 具名群組
- 能設計高效的 Log Parser，做到「一次掃描，多項擷取」

### 情境連結（EDA 視角）
Timing Report 的典型格式：
```
Startpoint: u_cpu/reg_A (rising edge-triggered flip-flop clocked by CLK)
Endpoint:   u_cpu/reg_B (rising edge-triggered flip-flop clocked by CLK)
Path Group: CLK
Path Type:  max

  Point                                    Incr       Path
  -----------------------------------------------------------
  clock CLK (rise edge)                    0.00       0.00
  u_cpu/reg_A/CK                           0.10       0.10
  u_cpu/comb_logic/Z                       0.35       0.45
  u_cpu/reg_B/D                            0.05       0.50
  -----------------------------------------------------------
  data arrival time                                   0.50

  clock CLK (rise edge)                    0.00       0.00
  clock uncertainty                       -0.05      -0.05
  u_cpu/reg_B/CK                           0.10       0.05
  library setup time                      -0.03       0.02
  -----------------------------------------------------------
  data required time                                  0.02
  -----------------------------------------------------------
  slack (MET)                                         -0.48
```

### 核心觀念骨架

```python
import re

# 編譯正規表示式（重複使用時效能更好）
SLACK_PATTERN = re.compile(
    r"slack\s+\((MET|VIOLATED)\)\s+([-+]?\d*\.?\d+)"
)

def parse_slack(line):
    m = SLACK_PATTERN.search(line)
    if m:
        status = m.group(1)      # "MET" 或 "VIOLATED"
        value  = float(m.group(2))
        return {"status": status, "value": value}
    return None
```

### 練習題庫

#### 題目 W4-1：Timing Violation 擷取器（⭐⭐）
**任務：**
1. 建立一個模擬 Timing Report 的 `.rpt` 文字檔
2. 用逐行讀取 + `re.search` 找出所有 `slack (VIOLATED)` 的行
3. 擷取 slack 數值，收集到 list 後計算最差值與平均違反量
4. 將結果寫入一個新的 `summary.txt` 檔案

---

#### 題目 W4-2：最終模擬 EDA 專案 — 多工具 Log 聚合分析器（⭐⭐⭐）
**專案規格書：**

**輸入：** 一個目錄，內含模擬的 `timing.rpt`、`drc.log`、`routing.log`
**輸出：** 一份 `eda_summary_report.txt`，包含：
  - 各工具的 Error / Warning 數量統計
  - Timing：列出所有 slack < -0.1 的路徑名稱與數值
  - DRC：列出出現次數前 3 名的違規類型（rule name）
  - Routing：列出所有含 `"UNROUTED"` 關鍵字的網路名稱

**架構要求：**
  - 每個工具的 parser 必須是獨立的函數（單一職責）
  - 主函數只負責呼叫各 parser 並整合結果
  - 使用 `sys.argv` 接受輸入目錄路徑
  - 必須用逐行串流讀取，不得用 `readlines()`

---

## 學習里程碑檢查點

| 里程碑 | 達成條件 |
|--------|---------|
| W1 完成 | 能用 list/dict 表達結構化 EDA 資料，並完成兩道練習 |
| W2 完成 | 能用逐行串流讀取模擬 Log，正確分類並統計 |
| W3 完成 | 能撰寫有 `sys.argv` 的可執行腳本，操作 `os.walk` 掃描目錄 |
| W4 完成 | 能用 `re` 模組從 Log 擷取數值，並輸出結構化的 summary 報告 |
| 月底衝刺 | 完成 W4-2 完整專案，代碼通過 `@review` 審查，完成 `@push` |
