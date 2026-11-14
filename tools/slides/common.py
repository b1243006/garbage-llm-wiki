"""簡報 Graph 的共用函式：讀檔、解析、把每一關的結果寫進 run-log.md。"""
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
WIKI = ROOT / "wiki"
CITE = re.compile(r"\[(doc_\d{2})\]")
NUM = re.compile(r"\d[\d,]*")


def topic_dir():
    if len(sys.argv) < 2:
        sys.exit("用法：python tools/slides/<程式>.py <主題資料夾名稱>")
    d = ROOT / "slides" / sys.argv[1]
    d.mkdir(parents=True, exist_ok=True)
    return d


def front(text):
    m = re.match(r"^---\n(.*?)\n---\n?", text, re.S)
    fm = {}
    if m:
        for line in m.group(1).splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                fm[k.strip()] = v.strip()
    return fm, (text[m.end():] if m else text)


def as_list(v):
    return [x.strip() for x in v.strip("[]").split(",") if x.strip()]


def bullets(body):
    """回傳 [(段落標題, 這一條的文字)]"""
    out, sec = [], ""
    for line in body.splitlines():
        if line.startswith("## "):
            sec = line[3:].strip()
        elif line.startswith("- "):
            out.append((sec, line[2:].strip()))
    return out


def strip_cites(s):
    return CITE.sub("", s).strip()


def nums(s):
    return {n.replace(",", "") for n in NUM.findall(CITE.sub("", s))}


def record(d, gate, problems, info=""):
    """把這一關的結果印出來，並加到 run-log.md。回傳結束碼。"""
    now = datetime.now(timezone(timedelta(hours=8))).strftime("%Y-%m-%d %H:%M:%S")
    ok = not problems
    lines = [f"## {now}｜{gate}｜{'通過' if ok else f'不通過（{len(problems)} 個問題）'}"]
    if info:
        lines.append(info)
    lines += [f"- {p}" for p in problems]
    text = "\n".join(lines)
    print(text)
    log = d / "run-log.md"
    head = "" if log.exists() else "# 執行紀錄\n\n每支關卡程式自動寫入，時間是台灣時間。\n"
    with open(log, "a", encoding="utf-8") as f:
        f.write(head + "\n" + text + "\n")
    return 0 if ok else 1
