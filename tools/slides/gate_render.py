"""⑪ 渲染關卡：用瀏覽器實際打開 deck.html，檢查頁數、文字、有沒有超出畫面、出處，並每頁截圖。"""
import re
import sys
from playwright.sync_api import sync_playwright
from common import CITE, topic_dir, front, bullets, strip_cites, record

d = topic_dir()
problems = []
drafts = sorted((d / "drafts").glob("[0-9][0-9].md"))
shots = d / "shots"
shots.mkdir(exist_ok=True)
squash = lambda s: re.sub(r"\s+", "", s)
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 1280, "height": 720})
    pg.goto((d / "deck.html").as_uri())
    pg.wait_for_timeout(500)
    count = pg.evaluate("window.deck.count")
    if count != len(drafts):
        problems.append(f"簡報有 {count} 頁，逐頁稿有 {len(drafts)} 頁，數量不一樣")
    for i, f in enumerate(drafts[:count]):
        fm, body = front(f.read_text(encoding="utf-8"))
        page = int(fm["page"])
        where = f"第 {page} 頁「{fm['title']}」"
        pg.evaluate(f"window.deck.go({i})")
        pg.wait_for_timeout(120)
        m = pg.evaluate("""() => {
            const s = document.querySelector('.slide.on'), body = s.querySelector('.body'), h = s.querySelector('header');
            const over = body ? body.scrollHeight - body.clientHeight : 0;
            const wide = body ? body.scrollWidth - body.clientWidth : 0;
            return { over, wide, head: h ? h.getBoundingClientRect().height : 0, text: s.textContent,
                     cites: s.querySelectorAll('a.c').length, src: (s.querySelector('.src') || {}).textContent || '' };
        }""")
        text = squash(m["text"])
        if m["over"] > 1:
            problems.append(f"{where}：內容超出畫面 {m['over']} px（字太多，要退回逐頁稿縮短）")
        if m["wide"] > 1:
            problems.append(f"{where}：內容橫向超出畫面 {m['wide']} px")
        if m["head"] > 190:
            problems.append(f"{where}：標題區太高（{m['head']:.0f} px），標題或學習目標太長")
        if squash(fm["title"]) not in text:
            problems.append(f"{where}：畫面上找不到標題")
        for _, bl in bullets(body) + [("", ln[2:]) for ln in body.splitlines() if ln.startswith("> ")]:
            for piece in strip_cites(bl).split(" | "):
                if squash(piece) not in text:
                    problems.append(f"{where}：畫面上的文字和逐頁稿不一樣（「{piece[:16]}…」）")
        if fm["layout"] != "cover":
            need = set(CITE.findall(body))
            if not m["cites"] or not need:
                problems.append(f"{where}：看不到任何出處")
            for c in sorted(need):
                if c not in m["src"]:
                    problems.append(f"{where}：頁尾的出處少了 {c}")
        pg.screenshot(path=str(shots / f"{page:02d}.png"))
    b.close()
sys.exit(record(d, "⑪ 渲染關卡", problems, f"用 1280×720 檢查了 {min(count, len(drafts))} 頁，截圖在 shots/"))
