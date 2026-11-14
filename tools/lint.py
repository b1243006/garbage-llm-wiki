"""
lint.py — Wiki 的定期檢查（AGENTS.md 第 7 節）。

用法（在專案根目錄）：  python tools/lint.py

檢查四件事：
  1. 出處      每條重點都有 [doc_NN]，編號列在該頁的 sources 裡，頁尾也有連結定義
  2. 斷連結    頁面裡的相對連結都指得到檔案
  3. 孤立頁    每一頁都列在 index.md，而且至少有一個其他頁面連到它
  4. 漏掉的來源 raw/ 每一篇都有來源頁，而且至少被一個非來源頁引用
還沒 ingest 的原始資料平常只列為提醒；全部讀完後加 --strict，沒讀到的就算錯誤。
有錯誤時結束碼是 1。只用 Python 內建模組。
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WIKI = ROOT / "wiki"
RAW = ROOT / "raw"

CITE = re.compile(r"\[(doc_\d{2})\](?!:)")
REFDEF = re.compile(r"^\[(doc_\d{2})\]:\s*(\S+)")
LINK = re.compile(r"\]\(([^)\s]+?\.md)(?:#[^)]*)?\)")
NO_CITE_SECTIONS = {"相關頁面", "用在哪些頁面", "原始資料"}
TYPES = {"source": "sources", "concept": "concepts", "dispute": "disputes", "myth": "myths"}


def front_matter(text):
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        return None
    fm = {}
    for line in m.group(1).splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            fm[k.strip()] = v.strip()
    fm["sources"] = re.findall(r"doc_\d{2}", fm.get("sources", ""))
    return fm


def main():
    strict = "--strict" in sys.argv
    pending = []
    errors = {"出處": [], "斷連結": [], "孤立頁": [], "漏掉的來源": []}
    pages = sorted(p for p in WIKI.rglob("*.md") if p.name not in ("index.md", "log.md"))
    rel = lambda p: p.relative_to(WIKI).as_posix()
    inbound = {rel(p): set() for p in pages}
    cited_by_non_source = set()

    for p in pages:
        text = p.read_text(encoding="utf-8")
        name = rel(p)
        fm = front_matter(text)
        if fm is None:
            errors["出處"].append(f"{name}：開頭沒有 --- 資料區塊")
            continue
        folder = TYPES.get(fm.get("type"))
        if folder is None or p.parent.name != folder:
            errors["出處"].append(f"{name}：type「{fm.get('type')}」和所在資料夾不符")
        refdefs, section = {}, ""
        for n, line in enumerate(text.splitlines(), 1):
            d = REFDEF.match(line)
            if d:
                refdefs[d.group(1)] = d.group(2)
                continue
            if line.startswith("## "):
                section = line[3:].strip()
            cites = CITE.findall(line)
            if re.match(r"^\s*- ", line) and section not in NO_CITE_SECTIONS and not cites:
                errors["出處"].append(f"{name} 第 {n} 行：這條重點沒有標出處")
            for c in cites:
                if c not in fm["sources"]:
                    errors["出處"].append(f"{name} 第 {n} 行：引用了 {c}，但開頭的 sources 沒有列")
                if fm.get("type") != "source":
                    cited_by_non_source.add(c)
        used = set(CITE.findall(text))
        for c in sorted(used - refdefs.keys()):
            errors["出處"].append(f"{name}：引用了 {c}，但頁尾沒有 [{c}]: … 的連結定義")
        # 連結（一般連結＋頁尾的連結定義）
        targets = LINK.findall(text) + [t for t in refdefs.values()]
        for t in targets:
            dest = (p.parent / t).resolve()
            if not dest.exists():
                errors["斷連結"].append(f"{name}：連到 {t}，但檔案不存在")
            elif WIKI in dest.parents and rel(dest) in inbound and dest != p:
                inbound[rel(dest)].add(name)

    index = (WIKI / "index.md").read_text(encoding="utf-8") if (WIKI / "index.md").exists() else ""
    listed = set()
    for t in LINK.findall(index):
        dest = (WIKI / t).resolve()
        if not dest.exists():
            errors["斷連結"].append(f"index.md：連到 {t}，但檔案不存在")
        else:
            listed.add(rel(dest))
    for name in inbound:
        if name not in listed:
            errors["孤立頁"].append(f"{name}：沒有列在 index.md")
        if not inbound[name]:
            errors["孤立頁"].append(f"{name}：沒有任何其他頁面連到它")

    for r in sorted(RAW.glob("doc_*.txt")):
        doc = r.stem
        if not (WIKI / "sources" / f"{doc}.md").exists():
            if strict:
                errors["漏掉的來源"].append(f"{doc}：raw/ 有這篇，但還沒有來源頁（還沒 ingest）")
            else:
                pending.append(doc)
        elif doc not in cited_by_non_source:
            errors["漏掉的來源"].append(f"{doc}：有來源頁，但沒有任何概念、爭議或誤解頁引用它")

    total = sum(len(v) for v in errors.values())
    print(f"檢查了 {len(pages)} 個頁面、{len(list(RAW.glob('doc_*.txt')))} 篇原始資料")
    for kind, items in errors.items():
        print(f"[{kind}] {'通過' if not items else f'{len(items)} 個問題'}")
        for e in items:
            print(f"  - {e}")
    if pending:
        print(f"[提醒] 還有 {len(pending)} 篇沒 ingest：{'、'.join(pending)}")
    print("全部通過" if not total else f"沒有通過：共 {total} 個問題")
    return 1 if total else 0


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main())
