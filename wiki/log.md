# 操作紀錄

只能往下加，不改舊的。

## [2026-11-12] setup | 訪談後建立骨架
- 和使用者訪談 11 題、確認需求摘要（見 discussion/）
- 新增：AGENTS.md、CLAUDE.md、tools/lint.py、raw/doc_01～doc_18（從第七週 RAG 資料複製，未修改）
- 還沒 ingest 任何一篇

## [2026-11-12] ingest | doc_01、doc_02（先讀 2 篇給使用者看）
- 新增：sources/doc_01.md、sources/doc_02.md、concepts/drink-cups.md、concepts/meal-boxes.md、myths/must-wash-clean.md
- 更新：index.md
- lint 第 1 次：沒過，1 個問題。myths/must-wash-clean.md 的「誤解」那一條沒有出處。
- 原因：「一般人怎麼誤會」這件事原始資料沒有寫，本來就標不出出處；「為什麼會搞錯」也是資料沒有的內容。
- 修正：常見誤解頁的格式改成「錯的說法（引號段落）→ 資料怎麼說（條列＋出處）」，拿掉「為什麼會搞錯」；AGENTS.md 第 4 節同步更新。
- lint 第 2 次：通過

## [2026-11-12] ingest | doc_03～doc_07（紙類、鋁箔包、塑膠容器、塑膠袋、保麗龍）
- 新增：sources/doc_03～doc_07、concepts/paper.md、cartons.md、plastic-containers.md、plastic-bags.md、styrofoam.md、myths/all-paper-recyclable.md、all-plastic-recyclable.md、styrofoam-not-recyclable.md
- 更新：concepts/meal-boxes.md（保麗龍餐具補上 doc_07）、index.md、來源頁的「用在哪些頁面」
- lint 第 1 次：沒過，1 個斷連結。plastic-bags.md 連到 disputes/local-rules.md，但那一頁要等 doc_18 讀進來才會建。
- 修正：先拿掉這個連結，等爭議頁建好再加回去（記在這裡避免忘記）。
- lint 第 2 次：通過

## [2026-11-12] ingest | doc_08～doc_13（金屬罐、玻璃陶瓷、電池、燈管、廚餘、廢食用油）
- 新增：sources/doc_08～doc_13、concepts/metal-cans.md、glass-ceramic.md、hand-over-items.md、food-waste.md、cooking-oil.md、disputes/eggshell.md、myths/ceramic-is-glass.md、battery-in-trash.md
- 說法不同：doc_12 寫蛋殼在 9 個縣市算廚餘、臺中等地當一般垃圾 → 照規則兩邊都寫，建立第一個爭議頁 disputes/eggshell.md
- 綜合：高壓罐（doc_08）、電池（doc_10）、燈管與水銀（doc_11）都是「要單獨交付」，合成一頁 hand-over-items.md
- lint：第 1 次就通過

## [2026-11-12] ingest | doc_14～doc_18（舊衣、手機家電、巨大垃圾、罰則、各地規定）＋綜合頁
- 新增：sources/doc_14～doc_18、concepts/clothes.md、phones-appliances.md、bulky.md、penalty.md、where-to-ask.md
- 綜合頁：concepts/overview.md（五種去處）、concepts/prep-steps.md（拆、倒、沖、壓、包）。這兩頁是跨多篇來源整理的，頁面開頭有註明是本 Wiki 的整理。
- 說法不同：disputes/local-rules.md（各縣市不同的項目）、disputes/fine-amount.md（罰鍰上限新舊不同，屬於「新舊資料不同」，有寫清楚各自的時間）
- 常見誤解：myths/furniture-on-street.md、same-everywhere.md、fined-100k.md
- 補回：plastic-bags.md → disputes/local-rules.md 的連結（第一批先拿掉的那個）
- lint --strict：通過。18 篇都有來源頁，也都被非來源頁引用。
- 目前共 49 頁：來源 18、概念 19、爭議 3、常見誤解 9

## [2026-11-12] fix | 簡報的忠實度審查回頭抓到 Wiki 本身的問題
- 來源：slides/garbage-intro/review-1.md。獨立 AI 審簡報逐頁稿時發現 16 個問題，追回去有 10 個其實是 Wiki 頁面就寫錯或寫過頭，lint 抓不到（lint 只看有沒有標出處，看不出內容對不對）。
- 修正的頁面：
  - concepts/overview.md：「五種去處」改成「大致分成四類」。原本的「要單獨交付」其實都是交給資源回收車或回收點，併回資源回收；拿掉「都交給資源回收車」這種資料沒有的通則；舊衣、果皮因為有「依各地公告」的條件，不再當例子。
  - concepts/prep-steps.md：標題從「回收前」改成「交出去之前」；碎玻璃、刀片另外寫一條，註明資料沒有說它們是回收物；「略為沖洗」不再掛在沒有這兩個字的 doc_05 上。
  - concepts/drink-cups.md：拿掉「拆成四份」的例子（資料裡的「四」是四個步驟）；補回「多數」「不要留在杯子裡」。
  - concepts/meal-boxes.md：「擦乾」改回資料的「擦乾淨」；拿掉資料沒有的「交給資源回收車」。
  - myths/must-wash-clean.md：錯的說法原本寫「沾了油就只能丟垃圾」，但 doc_02 根本沒提到油，是我讀入時自己加的；改成只留「要洗到全新才能回收」。
  - concepts/hand-over-items.md：標題和一句話說明改成「要特別處理的回收物」。
  - disputes/eggshell.md：「以清潔隊公告為準」原本標 doc_12，但那句講的是果皮和骨頭；改成引用 doc_18 講蛋殼的那句。
- 規則調整（AGENTS.md）：每批 ingest 之後加一道「獨立 AI 對照 raw/ 審查」；一句話說明和「錯的說法」不能出現頁面裡沒有出處的新事實。
- lint --strict：通過

## [2026-11-12] review | 第一次做「獨立 AI 對照 raw/ 審查」（新規則的第 7 步）
- 範圍：概念 19、爭議 3、誤解 9、手寫的來源頁 2，共 33 頁、160 條重點，加上 33 句一句話說明和 9 段「錯的說法」。結果在 reviews/wiki-review-1.md。
- 結果：26 個問題（必須修 1、建議修 25）。沒有講反、沒有數字錯、沒有標到無關的來源。
- 問題集中在三種地方：沒標出處的一句話說明（9 個）、我自己編的例子（7 個）、限定詞或條件被省略（5 個）。有 3 個例子的情境其實是從 raw 的【檢索練習問題】拿的，那一段不算資料本體。
- 必須修的那一個：overview.md 把 Wiki 自己整理的四類寫成「以上是共通原則」，等於說成資料認定的原則。
- 修正：34 處文字，分布在 17 個頁面；disputes/local-rules.md 不再引用 doc_17。
- lint --strict：通過
- 心得：lint 四項全過的 Wiki，獨立審查還是找出 26 個問題。程式檢查得出「有沒有標出處」，檢查不出「出處有沒有真的支持這句話」。

## [2026-11-12] fix | concepts/prep-steps.md
- 簡報第 2 輪忠實度審查指出「把不是同一種材質的東西分開」這個理由資料沒寫，源頭在這一頁。拿掉理由，只留動作。
- lint --strict：通過
