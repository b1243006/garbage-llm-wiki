"""④ 證據卡關卡：每張卡只來自一頁 Wiki，而且每一條都是那一頁的原文。"""
import re
import sys
from common import ROOT, CITE, topic_dir, front, bullets, strip_cites, record

d = topic_dir()
problems = []
listed = {(d / l).resolve() for l in re.findall(r"^- \[[^\]]+\]\(([^)]+\.md)\)", (d / "sources.md").read_text(encoding="utf-8"), re.M)}
carded, n_claims = set(), 0
for c in sorted((d / "cards").glob("*.md")):
    fm, body = front(c.read_text(encoding="utf-8"))
    page = (ROOT / fm.get("page", "")).resolve()
    if not fm.get("page") or not page.exists():
        problems.append(f"cards/{c.name}：page「{fm.get('page')}」不存在")
        continue
    if page not in listed:
        problems.append(f"cards/{c.name}：對應的頁面不在 sources.md 的清單裡")
    if page in carded:
        problems.append(f"cards/{c.name}：這一頁已經有另一張卡了")
    carded.add(page)
    wiki_text = page.read_text(encoding="utf-8")
    items = bullets(body)
    if not items:
        problems.append(f"cards/{c.name}：卡上沒有任何內容")
    for _, b in items:
        n_claims += 1
        if not CITE.search(b):
            problems.append(f"cards/{c.name}：「{b[:20]}…」沒有出處")
        if b not in wiki_text:
            problems.append(f"cards/{c.name}：「{b[:20]}…」不是 {page.name} 的原文（證據卡要照抄，不能改寫）")
for p in sorted(listed - carded):
    problems.append(f"{p.name}：在檢索清單裡，但沒有證據卡")
sys.exit(record(d, "④ 證據卡關卡", problems, f"檢查了 {len(carded)} 張卡、{n_claims} 條證據"))
