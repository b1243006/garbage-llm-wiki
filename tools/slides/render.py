"""⑩ 渲染 HTML：把通過檢查的逐頁稿排成 deck.html。只排版，不改任何一個字。"""
import html
import json
import re
import sys
from common import ROOT, WIKI, CITE, topic_dir, front, as_list

REPO = "https://github.com/b1243006/garbage-llm-wiki/blob/main"
d = topic_dir()
esc = html.escape
titles = {}
for p in (WIKI / "sources").glob("doc_*.md"):
    titles[p.stem] = front(p.read_text(encoding="utf-8"))[0].get("title", p.stem)
goals = {}
for line in (d / "outline.md").read_text(encoding="utf-8").splitlines():
    cells = [c.strip() for c in line.strip().strip("|").split("|")]
    if line.startswith("|") and len(cells) == 5 and cells[0].isdigit():
        goals[int(cells[0])] = cells[3]


def cite_html(text):
    """把句尾的 [doc_NN] 變成小小的出處標籤，文字本身不動。"""
    docs = CITE.findall(text)
    plain = esc(CITE.sub("", text).strip())
    tags = "".join(f'<a class="c" href="{REPO}/wiki/sources/{x}.md" title="{esc(titles.get(x, x))}">{x[4:]}</a>' for x in docs)
    return plain, tags, docs


def parse(body):
    lead, cols, sections, cur = "", [], [], None
    for line in body.splitlines():
        if line.startswith("> "):
            lead = line[2:].strip()
        elif line.startswith("cols:"):
            cols = [c.strip() for c in line[5:].split("|")]
        elif line.startswith("## "):
            cur = [line[3:].strip(), []]
            sections.append(cur)
        elif line.startswith("- "):
            if cur is None:
                cur = ["", []]
                sections.append(cur)
            cur[1].append(line[2:].strip())
    return lead, cols, sections


def li(items, ordered=False):
    out = []
    for b in items:
        plain, tags, _ = cite_html(b)
        out.append(f"<li><span>{plain}</span>{tags}</li>")
    tag = "ol" if ordered else "ul"
    return f"<{tag}>{''.join(out)}</{tag}>"


slides = []
files = sorted((d / "drafts").glob("[0-9][0-9].md"))
for f in files:
    fm, body = front(f.read_text(encoding="utf-8"))
    page, layout, title = int(fm["page"]), fm["layout"], fm["title"]
    lead, cols, sections = parse(body)
    docs = sorted(set(CITE.findall(body)))
    lead_plain, lead_tags, _ = cite_html(lead) if lead else ("", "", [])
    lead_html = f'<p class="lead"><span>{lead_plain}</span>{lead_tags}</p>' if lead else ""
    if layout == "cover":
        inner = f'<div class="cover"><div class="stripe"></div><h1>{esc(title)}</h1>{lead_html}<p class="hint">按 → 或點畫面右側開始</p></div>'
    else:
        if layout == "table":
            rows = []
            for b in sections[0][1]:
                plain, tags, _ = cite_html(b)
                cells = [c.strip() for c in plain.split(" | ")]
                rows.append("<tr>" + "".join(f"<td>{c}</td>" for c in cells[:-1]) + f"<td>{cells[-1]}{tags}</td></tr>")
            content = f"<table><thead><tr>{''.join(f'<th>{esc(c)}</th>' for c in cols)}</tr></thead><tbody>{''.join(rows)}</tbody></table>"
        elif layout == "two-col":
            content = '<div class="two">' + "".join(f'<div class="col"><h3>{esc(h)}</h3>{li(items)}</div>' for h, items in sections) + "</div>"
        elif layout == "quiz":
            q = next(items for h, items in sections if h == "題目")
            a = next(items for h, items in sections if h == "答案")
            content = f'<div class="quiz"><ol class="q">{"".join(f"<li>{esc(x)}</li>" for x in q)}</ol><button class="reveal">看答案</button><div class="ans" hidden>{li(a, True)}</div></div>'
        else:
            content = "".join((f"<h3>{esc(h)}</h3>" if h else "") + li(items, layout == "steps") for h, items in sections)
        src = "、".join(f'<a href="{REPO}/wiki/sources/{x}.md">{x} {esc(titles.get(x, ""))}</a>' for x in docs)
        inner = f'''<header><div class="goal">這頁要學會：{esc(goals.get(page, ""))}</div><h2>{esc(title)}</h2></header>
<div class="body {layout}">{lead_html}{content}</div>
<footer><span class="src">出處：{src}</span><span class="no">{page} / {len(files)}</span></footer>'''
    slides.append(f'<section class="slide {layout}" data-page="{page}">{inner}</section>')

doc = f'''<!doctype html>
<html lang="zh-Hant">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>垃圾分類入門｜教學簡報</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@400;700&display=swap">
<style>
:root {{ --bg:#f6f5f1; --ink:#1f2933; --muted:#5c6b77; --line:#dde2e5; --navy:#17324d; --truck:#f2c230; --link:#1f5f99; }}
* {{ box-sizing:border-box; }}
html, body {{ margin:0; height:100%; background:#0f1c2b; overflow:hidden; font-family:"Noto Sans TC","PingFang TC","Microsoft JhengHei",sans-serif; color:var(--ink); }}
#stage {{ position:absolute; left:50%; top:50%; width:1280px; height:720px; transform-origin:0 0; background:var(--bg); }}
.slide {{ position:absolute; inset:0; display:none; flex-direction:column; padding:44px 64px 30px; border-top:10px solid var(--navy); }}
.slide.on {{ display:flex; }}
header {{ flex:none; margin-bottom:18px; }}
.goal {{ font-size:18px; color:var(--muted); }}
h2 {{ margin:4px 0 0; font-size:42px; line-height:1.25; }}
h2::after {{ content:""; display:block; width:96px; height:8px; background:var(--truck); margin-top:12px; }}
.body {{ flex:1; min-height:0; overflow:hidden; font-size:26px; line-height:1.55; }}
.lead {{ margin:0 0 14px; font-size:26px; color:var(--navy); font-weight:700; }}
ul, ol {{ margin:0; padding-left:1.2em; }}
li {{ margin:0 0 10px; }}
ul > li:last-child, ol > li:last-child {{ margin-bottom:0; }}
ul + h3, ol + h3 {{ margin-top:10px; }}
h3 {{ margin:0 0 10px; font-size:26px; color:var(--navy); }}
a.c {{ display:inline-block; margin-left:6px; padding:0 6px; font-size:13px; line-height:20px; vertical-align:middle; color:var(--muted); border:1px solid var(--line); border-radius:4px; background:#fff; text-decoration:none; }}
.body.two-col {{ display:flex; flex-direction:column; }}
.two {{ display:grid; grid-template-columns:1fr 1fr; gap:28px; flex:1; min-height:0; }}
.col {{ background:#fff; border:1px solid var(--line); border-radius:12px; padding:20px 24px; }}
table {{ width:100%; border-collapse:collapse; background:#fff; font-size:24px; }}
th {{ text-align:left; background:#e9edf0; color:var(--muted); font-size:20px; padding:10px 16px; }}
td {{ padding:12px 16px; border-top:1px solid var(--line); vertical-align:top; }}
td:first-child {{ font-weight:700; white-space:nowrap; }}
.quiz .q li {{ margin-bottom:14px; }}
.reveal {{ font:inherit; font-size:22px; padding:8px 22px; margin:6px 0 14px; border:0; border-radius:8px; background:var(--navy); color:#fff; cursor:pointer; }}
.ans {{ background:#fff; border-left:8px solid var(--truck); padding:14px 20px; font-size:22px; }}
.ans li {{ margin-bottom:6px; }}
footer {{ flex:none; display:flex; justify-content:space-between; gap:20px; padding-top:12px; border-top:1px solid var(--line); font-size:14px; color:var(--muted); }}
footer a {{ color:var(--muted); }}
.src {{ overflow:hidden; white-space:nowrap; text-overflow:ellipsis; }}
.no {{ flex:none; }}
.cover {{ margin:auto 0; }}
.cover .stripe {{ width:140px; height:14px; background:var(--truck); margin-bottom:26px; }}
.cover h1 {{ margin:0; font-size:72px; line-height:1.2; }}
.cover .lead {{ margin-top:22px; font-size:30px; font-weight:400; color:var(--muted); }}
.cover .hint {{ margin-top:60px; font-size:18px; color:var(--muted); }}
#nav {{ position:fixed; left:0; right:0; bottom:0; height:4px; background:rgba(255,255,255,.15); }}
#bar {{ height:100%; width:0; background:var(--truck); transition:width .2s; }}
@media print {{ html, body {{ overflow:visible; height:auto; background:#fff; }} #stage {{ position:static; transform:none !important; width:auto; height:auto; }} .slide {{ display:flex !important; position:relative; width:1280px; height:720px; page-break-after:always; }} #nav {{ display:none; }} .ans {{ display:block !important; }} }}
</style>
</head>
<body>
<div id="stage">
{chr(10).join(slides)}
</div>
<div id="nav"><div id="bar"></div></div>
<script>
(function () {{
  var slides = [].slice.call(document.querySelectorAll(".slide")), cur = 0, stage = document.getElementById("stage");
  function fit() {{
    var s = Math.min(innerWidth / 1280, innerHeight / 720);
    stage.style.transform = "scale(" + s + ") translate(-50%, -50%)";
  }}
  function go(i) {{
    cur = Math.max(0, Math.min(slides.length - 1, i));
    slides.forEach(function (el, k) {{ el.classList.toggle("on", k === cur); }});
    document.getElementById("bar").style.width = ((cur + 1) / slides.length * 100) + "%";
    history.replaceState(null, "", "#" + (cur + 1));
  }}
  addEventListener("resize", fit);
  addEventListener("keydown", function (e) {{
    if (["ArrowRight", "PageDown", " ", "Enter"].indexOf(e.key) >= 0) go(cur + 1);
    if (["ArrowLeft", "PageUp", "Backspace"].indexOf(e.key) >= 0) go(cur - 1);
    if (e.key === "Home") go(0);
    if (e.key === "End") go(slides.length - 1);
  }});
  stage.addEventListener("click", function (e) {{
    if (e.target.closest("a, button")) return;
    var r = stage.getBoundingClientRect();
    go(cur + ((e.clientX - r.left) / r.width < 0.3 ? -1 : 1));
  }});
  var x0 = null;
  addEventListener("touchstart", function (e) {{ x0 = e.touches[0].clientX; }});
  addEventListener("touchend", function (e) {{
    if (x0 === null) return;
    var dx = e.changedTouches[0].clientX - x0;
    if (Math.abs(dx) > 40) go(cur + (dx < 0 ? 1 : -1));
    x0 = null;
  }});
  document.querySelectorAll(".reveal").forEach(function (b) {{
    b.addEventListener("click", function () {{ b.nextElementSibling.hidden = false; b.hidden = true; }});
  }});
  window.deck = {{ go: go, count: slides.length }};
  fit();
  go((parseInt(location.hash.slice(1), 10) || 1) - 1);
}})();
</script>
</body>
</html>
'''
(d / "deck.html").write_text(doc, encoding="utf-8")
print(f"已產生 {d.relative_to(ROOT)}/deck.html，共 {len(slides)} 頁")
