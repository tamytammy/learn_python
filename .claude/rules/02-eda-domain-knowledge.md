# EDA 專有名詞知識庫

## 什麼是 EDA？

**EDA（Electronic Design Automation）電子設計自動化** 是指用軟體工具自動化晶片設計流程的一整套產業與技術。
沒有 EDA 工具，現代的先進製程晶片（如台積電 3nm / 5nm）根本無法被設計出來。

主要 EDA 公司：Synopsys、Cadence、Siemens EDA（前身 Mentor Graphics）

---

## IC 設計全流程概覽（RTL-to-GDSII）

```
RTL 設計（Verilog/VHDL）
        ↓
[邏輯合成 Logic Synthesis]        ← Synopsys Design Compiler (DC)
        ↓
網表（Gate-Level Netlist）
        ↓
[佈局規劃 Floorplan]
        ↓
[置入 Placement]                   ← Cadence Innovus / Synopsys ICC2
        ↓
[時脈樹合成 CTS]
        ↓
[繞線 Routing]
        ↓
[設計規則檢查 DRC / 版圖對照電路 LVS]  ← Mentor Calibre
        ↓
GDSII（最終製造格式，送晶圓廠）
```

---

## 核心術語表

### 時序分析（Static Timing Analysis, STA）

| 術語 | 英文全名 | 解釋 |
|------|---------|------|
| Slack | — | 時序裕量 = 「要求時間 - 實際到達時間」。**正數 = 時序通過（MET）；負數 = 時序違反（VIOLATED）** |
| Setup Time | Setup Hold Timing | 資料必須在時脈上升沿**之前**穩定的最短時間 |
| Hold Time | Hold Timing | 資料必須在時脈上升沿**之後**維持穩定的最短時間 |
| WNS | Worst Negative Slack | 所有路徑中最差（最負）的 slack 值，是時序健康度的關鍵指標 |
| TNS | Total Negative Slack | 所有違反路徑的 slack 總和，代表整體修復工作量 |
| Critical Path | — | Slack 最小的路徑，是優化的首要目標 |
| Startpoint | — | 時序路徑的起點（通常是暫存器 FF 的輸出或輸入埠） |
| Endpoint | — | 時序路徑的終點（通常是暫存器 FF 的輸入或輸出埠） |
| Clock Period | — | 時脈週期。越短代表頻率越高，時序越難收斂 |

#### 典型 Timing Report 格式解析
```
slack (VIOLATED) :             -0.48  ← 負數 = 違反，需修復
slack (MET)      :              0.15  ← 正數 = 通過
```

---

### 設計規則檢查（Design Rule Check, DRC）

| 術語 | 解釋 |
|------|------|
| DRC | 檢查版圖是否符合晶圓廠的製造規則（如最小線寬、最小間距） |
| Spacing Error | 兩條金屬線距離太近，違反最小間距規則 |
| Width Error | 金屬線太細，違反最小線寬規則 |
| Enclosure Error | 通孔（Via）沒有被金屬充分包圍 |
| Layer | 金屬層，如 metal1, metal2, poly, diffusion 等 |
| Via | 連接不同金屬層的垂直導體（通孔） |
| Clean / Pass | DRC 零違規，代表版圖可以送廠製造 |

#### 典型 DRC Log 格式
```
DRC SUMMARY:
  RULE metal2.spacing.1: 15 violations
  RULE metal1.width.1:    3 violations
  TOTAL: 18 violations
  
VIOLATION DETAIL:
  LAYER metal2: SPACING_ERROR at (1050, 2300) size (0.08um x 0.05um)
  LAYER metal1: WIDTH_ERROR at (500, 1100)
```

---

### 繞線（Routing）

| 術語 | 解釋 |
|------|------|
| Routing | 將所有邏輯閘用金屬線連接起來 |
| Net | 一個需要被連接的電氣網路（一個訊號名稱） |
| Congestion | 繞線擁塞，某區域可用的繞線資源不足 |
| DRV | Design Rule Violation，繞線後仍存在的設計規則違反 |
| Unrouted Net | 尚未成功繞通的網路，是嚴重問題（晶片功能不正確） |
| Wire Length | 金屬線總長，影響時序與功耗 |
| Via Count | 通孔數量，過多會增加電阻與製造成本 |

#### 典型 Routing Log 格式
```
[ROUTE] Starting global routing...
[WARNING] Congestion detected in region (500,500)-(1000,1000)
[ERROR] UNROUTED net: u_cpu/data_bus[7]
[ERROR] UNROUTED net: u_mem/addr[15]
[INFO] Routing complete. DRV count: 3
```

---

### 邏輯合成（Logic Synthesis）

| 術語 | 解釋 |
|------|------|
| Synthesis | 將 RTL（Verilog 硬體描述語言）轉換為邏輯閘電路 |
| RTL | Register Transfer Level，描述資料如何在暫存器間流動的抽象層次 |
| Netlist | 合成後的閘極層網表，記錄所有邏輯閘與連接關係 |
| Gate Count | 邏輯閘數量，代表電路複雜度與面積 |
| PPA | Power（功耗）/ Performance（效能）/ Area（面積），晶片設計的三大優化維度 |
| Liberty (.lib) | 描述邏輯閘時序與功耗特性的資料庫檔案 |

---

### 電源與功耗（Power）

| 術語 | 解釋 |
|------|------|
| Dynamic Power | 動態功耗，電路切換時產生 |
| Leakage Power | 靜態漏電功耗，即使電路不動作也存在 |
| IR Drop | 電源網路上的電壓降，過大會導致邏輯錯誤 |
| Power Domain | 電源域，不同電壓區域的設計分區 |

---

## 常見 EDA Log 關鍵字速查

### 嚴重程度分級

| 關鍵字 | 嚴重程度 | 含義 |
|--------|---------|------|
| `[ERROR]` / `Error:` | 致命 | 必須修復，否則流程無法繼續或結果錯誤 |
| `[WARNING]` / `Warning:` | 警告 | 應檢查，可能影響品質但不阻擋流程 |
| `[INFO]` / `Information:` | 資訊 | 流程進度回報，通常不需處理 |
| `VIOLATED` | 致命（時序） | Timing slack 為負，路徑時序不過 |
| `MET` | 通過（時序） | Timing slack 為正或零，路徑時序過 |
| `UNROUTED` | 致命（繞線） | 有 net 尚未繞通 |

### 常見正規表示式 Pattern（供練習參考）

```python
import re

# 擷取 slack 值（正負數均支援）
slack_re = re.compile(r"slack\s+\((MET|VIOLATED)\)\s+([-+]?\d*\.?\d+)")

# 擷取 DRC 層別與違規類型
drc_re = re.compile(r"LAYER\s+(\w+):\s+(\w+)\s+at\s+\((\d+),\s*(\d+)\)")

# 擷取 UNROUTED net 名稱
unrouted_re = re.compile(r"UNROUTED\s+net:\s+([\w/\[\]]+)")

# 擷取工具版本號（如 "Innovus 21.1.0"）
version_re = re.compile(r"(\w+)\s+(\d+\.\d+\.\d+)")

# 擷取時間戳記（如 "2024-01-15 14:32:07"）
timestamp_re = re.compile(r"(\d{4}-\d{2}-\d{2})\s+(\d{2}:\d{2}:\d{2})")
```

---

## 工具對照表

| 流程階段 | 常用工具 | 公司 | 輸出 Log 特徵 |
|---------|---------|------|--------------|
| 邏輯合成 | Design Compiler (DC) | Synopsys | `.rpt` 報告，含 timing / area |
| 佈局繞線 | Innovus | Cadence | 大量 `[INFO]` 流程日誌 |
| 佈局繞線 | ICC2 | Synopsys | 類似 Innovus 格式 |
| 靜態時序 | PrimeTime (PT) | Synopsys | 詳細 timing path 報告 |
| DRC/LVS | Calibre | Siemens | 結構化違規清單 |
| 形式驗證 | Formality | Synopsys | PASS/FAIL 驗證結果 |

---

## 學習路徑補充

學完四週 Python 基礎後，AI for EDA 的進階方向：

1. **ML for EDA** — 用機器學習預測 timing / congestion（論文關鍵字：`ML EDA`, `GNN Placement`）
2. **LLM Agent for EDA** — 用 Claude / GPT 自動解讀 Log、生成修復建議腳本
3. **TCL 腳本自動化** — EDA 工具原生支援 TCL，Python 可呼叫 TCL 腳本驅動工具
4. **Python-based EDA** — 開源工具如 OpenROAD、KLayout 提供 Python API
