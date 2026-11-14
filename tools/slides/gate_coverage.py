"""② 覆蓋率關卡：檢索到的 Wiki 頁面夠不夠做一份教學簡報。"""
import re
import sys
from common import ROOT, WIKI, topic_dir, front, record

MIN_STOP, MIN_PAGES, MIN_DOCS = 3, 8, 5
d = topic_dir()
src = d / "sources.md"
problems = []
if not src.exists():
    sys.exit(record(d, "② 覆蓋率關卡", ["找不到 sources.md，要先做 ① 檢索 Wiki"]))
links = re.findall(r"^- \[[^\]]+\]\(([^)]+\.md)\)", src.read_text(encoding="utf-8"), re.M)
pages, docs, kinds = [], set(), {}
for link in links:
    p = (d / link).resolve()
    if not p.exists() or WIKI not in p.parents:
        problems.append(f"{link}：不是 wiki/ 裡存在的頁面")
        continue
    if p.parent.name == "sources":
        problems.append(f"{link}：來源頁不能直接當簡報素材，請選概念、爭議或誤解頁")
        continue
    fm, _ = front(p.read_text(encoding="utf-8"))
    pages.append(p)
    docs |= set(re.findall(r"doc_\d{2}", fm.get("sources", "")))
    kinds[p.parent.name] = kinds.get(p.parent.name, 0) + 1
total = len([p for p in WIKI.rglob("*.md") if p.parent.name in ("concepts", "disputes", "myths")])
all_docs = len(list((ROOT / "raw").glob("doc_*.txt")))
if len(pages) < MIN_STOP:
    problems.append(f"相關頁面只有 {len(pages)} 頁，少於 {MIN_STOP} 頁：資料不足，停下來，不要硬湊")
elif len(pages) < MIN_PAGES:
    problems.append(f"相關頁面 {len(pages)} 頁，做 15 頁簡報至少要 {MIN_PAGES} 頁")
if len(docs) < MIN_DOCS:
    problems.append(f"只涵蓋 {len(docs)} 篇來源，至少要 {MIN_DOCS} 篇")
for folder, name in (("disputes", "爭議頁"), ("myths", "常見誤解頁")):
    if not kinds.get(folder):
        problems.append(f"沒有選到任何{name}；教學簡報需要講各地差異和常見的錯")
info = f"選了 {len(pages)}／{total} 個非來源頁（概念 {kinds.get('concepts', 0)}、爭議 {kinds.get('disputes', 0)}、誤解 {kinds.get('myths', 0)}），涵蓋 {len(docs)}／{all_docs} 篇來源"
sys.exit(record(d, "② 覆蓋率關卡", problems, info))
