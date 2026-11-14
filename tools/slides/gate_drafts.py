"""⑧ 逐頁稿關卡：每一條（v2 起包含引導句）都有出處、出處只能來自對應的卡、數字要在卡片裡找得到。
可以只檢查某幾頁：python tools/slides/gate_drafts.py <主題> 6 9
"""
import sys
from common import CITE, topic_dir, front, as_list, bullets, nums, record

d = topic_dir()
only = {int(x) for x in sys.argv[2:]}
problems, rows = [], []
for line in (d / "outline.md").read_text(encoding="utf-8").splitlines():
    cells = [c.strip() for c in line.strip().strip("|").split("|")]
    if line.startswith("|") and len(cells) == 5 and cells[0].isdigit():
        rows.append((int(cells[0]), cells[1], cells[2], [c.strip() for c in cells[4].replace("、", ",").split(",") if c.strip() and c.strip() != "—"]))
checked = 0
for page, layout, title, cards in rows:
    if only and page not in only:
        continue
    f = d / "drafts" / f"{page:02d}.md"
    where = f"第 {page} 頁"
    if not f.exists():
        problems.append(f"{where}：還沒有逐頁稿 drafts/{page:02d}.md")
        continue
    checked += 1
    fm, body = front(f.read_text(encoding="utf-8"))
    if fm.get("title") != title:
        problems.append(f"{where}：標題和大綱不一樣（大綱是「{title}」）")
    if fm.get("layout") != layout:
        problems.append(f"{where}：版型和大綱不一樣（大綱是 {layout}）")
    if sorted(as_list(fm.get("cards", ""))) != sorted(cards):
        problems.append(f"{where}：使用的卡和大綱不一樣（大綱是 {'、'.join(cards) or '無'}）")
    card_text = "\n".join((d / "cards" / f"{c}.md").read_text(encoding="utf-8") for c in cards if (d / "cards" / f"{c}.md").exists())
    allowed, card_nums = set(CITE.findall(card_text)), nums(card_text)
    items = bullets(body)
    # v2：引導句（> 開頭）也算內容，除了封面以外一樣要有出處
    if layout != "cover":
        items += [("引導句", ln[2:].strip()) for ln in body.splitlines() if ln.startswith("> ")]
    if layout != "cover" and not items:
        problems.append(f"{where}：沒有任何內容")
    for sec, b in items:
        if sec == "題目":
            continue
        cites = CITE.findall(b)
        if not cites:
            problems.append(f"{where}：「{b[:18]}…」沒有出處")
        for c in cites:
            if c not in allowed:
                problems.append(f"{where}：「{b[:18]}…」引用 {c}，但對應的卡片裡沒有這篇來源")
        for n in sorted(nums(b) - card_nums):
            problems.append(f"{where}：「{b[:18]}…」的數字 {n} 在對應卡片裡找不到")
sys.exit(record(d, "⑧ 逐頁稿關卡", problems, f"檢查了 {checked} 頁" + (f"（只檢查第 {'、'.join(map(str, sorted(only)))} 頁）" if only else "")))
