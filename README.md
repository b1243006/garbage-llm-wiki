# 垃圾分類 LLM Wiki

TAICA「生成式 AI：文字與圖像生成的原理與實務」第十週作業：先建一個 LLM Wiki，再用它當知識庫做一份教學 HTML 簡報。

- 教學簡報：https://b1243006.github.io/garbage-llm-wiki/slides/garbage-intro/deck.html
- 網站首頁：https://b1243006.github.io/garbage-llm-wiki/
- Wiki 目錄：[wiki/index.md](wiki/index.md)（49 頁：來源 18、概念 19、爭議 3、常見誤解 9）
- 建 Wiki 之前的訪談與需求摘要：[discussion/](discussion/)
- Wiki 的規則：[AGENTS.md](AGENTS.md)
- 做簡報的 Graph：[.agents/workflows/topic-slides.md](.agents/workflows/topic-slides.md)，流程圖 [graph.png](slides/garbage-intro/graph.png)
- git 紀錄：[git-log.txt](git-log.txt)（每一步都有 commit）
- 實際執行紀錄：[slides/garbage-intro/run-log.md](slides/garbage-intro/run-log.md)、[report.md](slides/garbage-intro/report.md)
- Wiki 的操作紀錄：[wiki/log.md](wiki/log.md)

## 資料夾

| 位置 | 內容 |
|---|---|
| `raw/` | 18 篇原始資料（第七週整理的公開資料摘要），不修改 |
| `wiki/` | AI 維護的 Wiki |
| `tools/lint.py` | Wiki 的四項檢查 |
| `tools/slides/` | 做簡報用的關卡程式和渲染程式 |
| `slides/garbage-intro/` | 這次簡報每一關的產出：sources.md、cards/、outline.md、drafts/、review-*.md、deck.html、shots/、run-log.md、report.md |

## 自己跑一次檢查

```bash
python tools/lint.py --strict
python tools/slides/gate_coverage.py garbage-intro
python tools/slides/gate_cards.py garbage-intro
python tools/slides/gate_outline.py garbage-intro
python tools/slides/gate_drafts.py garbage-intro
python tools/slides/render.py garbage-intro
python tools/slides/gate_render.py garbage-intro   # 需要 playwright
```
