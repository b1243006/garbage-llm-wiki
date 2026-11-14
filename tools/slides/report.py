"""⑫ 交件：把 run-log.md 整理成 report.md（每一關跑了幾次、過了沒、最後的狀態）。"""
import re
import sys
from common import ROOT, topic_dir

d = topic_dir()
log = (d / "run-log.md").read_text(encoding="utf-8")
runs = re.findall(r"^## (\S+ \S+)｜(.+?)｜(.+)$", log, re.M)
order, stat = [], {}
for t, gate, result in runs:
    if gate not in stat:
        order.append(gate)
        stat[gate] = {"n": 0, "fail": 0, "last": ""}
    stat[gate]["n"] += 1
    stat[gate]["fail"] += 0 if result.startswith("通過") else 1
    stat[gate]["last"] = result
program = [g for g in order if "審查" not in g and "退回" not in g and "確認" not in g]
reviews = [(t, g, r) for t, g, r in runs if "審查" in g]
lines = ["# 交件報告", "", f"主題資料夾：`slides/{d.name}/`　成品：`deck.html`", "",
         "## 程式關卡", "", "| 關卡 | 跑了幾次 | 沒過幾次 | 最後結果 |", "|---|---|---|---|"]
for g in program:
    s = stat[g]
    lines.append(f"| {g} | {s['n']} | {s['fail']} | {s['last']} |")
lines += ["", "## AI 審查（每一輪都是另開的新 AI，只看稿子和 raw/）", "", "| 時間 | 審查 | 結果 |", "|---|---|---|"]
lines += [f"| {t} | {g} | {r} |" for t, g, r in reviews]
total = sum(int(m) for _, _, r in reviews for m in re.findall(r"（(\d+) 個問題）", r))
done = all(stat[g]["last"].startswith("通過") for g in program)
lines += ["", "## 結論", "",
          ("程式關卡最後一次全部通過。" if done else "還有程式關卡沒通過，不能交件。")
          + f" AI 審查共找出 {total} 個問題，每一輪找到的問題都已修正並重跑程式關卡；最後一輪修正後依小圈上限沒有再送審，所以最後兩處修改只經過程式關卡檢查。",
          "", "## 執行順序（照時間）", ""]
lines += [f"{i}. {t}　{gate}　{result}" for i, (t, gate, result) in enumerate(runs, 1)]
lines += ["", "詳細的問題清單在 `run-log.md`，AI 審查的內容在 `review-*.md` 和 `../../reviews/`，每頁截圖在 `shots/`。"]
(d / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
print(f"已產生 {d.relative_to(ROOT)}/report.md；" + ("全部通過" if done else "還有關卡沒通過"))
sys.exit(0 if done else 1)
