"""⑥ 大綱關卡：頁數、教學結構、每頁有卡、每張卡都有用到。"""
import sys
from common import topic_dir, record

d = topic_dir()
problems, rows = [], []
for line in (d / "outline.md").read_text(encoding="utf-8").splitlines():
    cells = [c.strip() for c in line.strip().strip("|").split("|")]
    if line.startswith("|") and len(cells) == 5 and cells[0].isdigit():
        rows.append({"page": int(cells[0]), "layout": cells[1], "title": cells[2], "goal": cells[3],
                     "cards": [c.strip() for c in cells[4].replace("、", ",").split(",") if c.strip() and c.strip() != "—"]})
cards = {c.stem for c in (d / "cards").glob("*.md")}
n = len(rows)
if not 13 <= n <= 16:
    problems.append(f"共 {n} 頁，要在 13～16 頁之間")
if [r["page"] for r in rows] != list(range(1, n + 1)):
    problems.append("頁碼沒有從 1 開始連續編號")
if rows and rows[0]["layout"] != "cover":
    problems.append("第 1 頁要是封面（cover）")
if rows and rows[-1]["layout"] != "summary":
    problems.append("最後一頁要是總結（summary）")
if not any(r["layout"] == "quiz" for r in rows):
    problems.append("至少要有 1 頁小測驗（quiz），讓讀者檢查自己學會了沒")
used = set()
for r in rows:
    if r["layout"] != "cover" and not r["cards"]:
        problems.append(f"第 {r['page']} 頁「{r['title']}」沒有列任何證據卡")
    if not r["goal"]:
        problems.append(f"第 {r['page']} 頁沒有寫「這頁要學會什麼」")
    for c in r["cards"]:
        if c not in cards:
            problems.append(f"第 {r['page']} 頁用了不存在的卡 {c}")
        used.add(c)
for c in sorted(cards - used):
    problems.append(f"證據卡 {c} 沒有被任何一頁用到（不是多抽了，就是大綱漏了主題）")
sys.exit(record(d, "⑥ 大綱關卡", problems, f"共 {n} 頁，用到 {len(used & cards)}／{len(cards)} 張卡"))
