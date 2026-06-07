# 📝 練習題 W1-1：DRC 違規統計（⭐⭐）

# 情境： 你拿到一份 DRC 報告，內含若干筆違規紀錄，每筆是一個 dict，欄位有 rule_name、layer、severity（值為 "ERROR" 或 "WARNING"）。

violations = [
    {"rule_name": "FAS", "layer": "metal2", "severity": "WARNING"},
    {"rule_name": "SS1", "layer": "metal1", "severity": "ERROR"},
    {"rule_name": "SLO", "layer": "metal2", "severity": "ERROR"},
    {"rule_name": "LAO", "layer": "metal2", "severity": "WARNING"},
    {"rule_name": "ALS", "layer": "metal1", "severity": "ERROR"}
]

error_count = 0
warning_count = 0

for v in violations:
    if v["severity"] == "ERROR":
        error_count += 1
    elif v["severity"] == "WARNING":
        warning_count += 1
    if v["layer"] == "metal2":
        print(f"Violation on metal2: {v['rule_name']}")


# 📝 練習題 W1-2：Timing Path 排行榜（⭐⭐⭐）

# 情境： 一份 Timing Report 內有數十條 timing path，每條都有 slack 值。負數代表時序違反，越負越嚴重。

paths = [
    {"name": "path_A", "slack": -0.45},
    {"name": "path_B", "slack":  0.12},
    {"name": "path_C", "slack":  -0.41},
    {"name": "path_D", "slack":  0.33},
    {"name": "path_E", "slack":  0.38},
    {"name": "path_F", "slack":  0.24},
    {"name": "path_G", "slack":  0.45},
    {"name": "path_H", "slack":  -4.33},
    {"name": "path_I", "slack":  -1.12},
    {"name": "path_J", "slack":  5.12}
]
paths_negative_count = 0
slack_negative_sum = 0
for p in paths:
    if p["slack"] < 0:
        paths_negative_count += 1
        slack_negative_sum += p["slack"]

if(paths_negative_count > 0):
    slack_avg = slack_negative_sum / paths_negative_count
else:
    slack_avg = 0
    print("No negative slack paths found.")

paths_new = sorted(paths, key=lambda p: p["slack"])
paths_new_third = paths_new[:3]

print(f"Top 3 worst paths: {paths_new_third}")
print(f"Average slack: {slack_avg}")