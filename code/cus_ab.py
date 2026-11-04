# -*- coding: utf-8 -*-
"""CUS A/B experiment (public reproduction).

Conditions:
  A  : state machine + explicit "you must mention it" near generation point
  A2 : state machine + the inhibiting hint ("do not act up")
  A3 : state machine, natural injection (mood + reason + "respond naturally")
  B  : no state machine; the promise is still in context (no filler in this harness)

Usage:
  set DEEPSEEK_API_KEY=...
  python cus_ab.py --limit 20 --groups A,A2,A3,B --tag seed1

Note: the original run used a private persona and the author's own state
machine. This file ships a minimal contract module and a generic persona so
the protocol can be reproduced; absolute scores will differ.
"""
import argparse
import json
import os
import sys

from openai import OpenAI

sys.path.insert(0, os.path.dirname(__file__))
import contract  # noqa: E402

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(HERE, "data")

API_KEY = os.environ.get("DEEPSEEK_API_KEY", "")
BASE_URL = os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1")
MODEL = os.environ.get("DEEPSEEK_MODEL", "deepseek-flash")

PERSONA = open(os.path.join(DATA, "persona.txt"), encoding="utf-8").read().strip()
STYLE = "\n\n【说话】短句，最多两三条；不解释、不总结、不列点。\n"

client = OpenAI(api_key=API_KEY, base_url=BASE_URL, timeout=60, max_retries=2)


def chat(messages, system):
    r = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "system", "content": system}] + messages[-8:],
        temperature=0.8, max_tokens=400,
        extra_body={"thinking": {"type": "disabled"}})
    return (r.choices[0].message.content or "").strip()


def run_one(script, group):
    now = [1000.0]
    first = "我去忙了" if group == "C" else script["promise"]
    messages = [{"role": "user", "content": first},
                {"role": "assistant", "content": "好"}]
    hint = ""
    mins = 10
    if group in ("A", "A2", "A3"):
        c = contract.scan(script["promise"], now[0])
        if c:
            mins = max(1, round((c["expire_at"] - now[0]) / 60))
            now[0] += script["late_sec"]
            _, hint = contract.check(c, script["return"], now[0])
            if not hint:
                hint = "contract settled without a hint (on time or accepted excuse)"

    if group == "A" and hint:
        messages.append({"role": "system", "content": (
            f"【隐秘提示】他回来了。你记得他说好「{script['promise']}」，"
            f"结果你等了约 {mins} 分钟。你的耐心已经耗尽，气还没消。"
            "这一句你必须自然地提到这件事（比如“说好的五分钟”），可以短，"
            "但别只回“回来啦”，别马上热络。")})

    turns = []
    for i, user in enumerate([script["return"]] + script["followups"]):
        state = "【此刻】心情一般"
        if group == "A" and hint and i <= 2:
            base = hint if i == 0 else "【还记着】刚才的事还没过去，别马上热络"
            state = (base + f"\n【等的时间】约 {mins} 分钟；可以自然提一句，别报时"
                     + "\n【说话】短一点，别主动关心他，别解释")
        elif group == "A2" and hint and i <= 2:
            base = hint if i == 0 else "【还记着】刚才的事还没过去，别马上热络"
            state = base + "\n【此刻心情】0.45，偏低"
        elif group == "A3" and hint and i <= 2:
            state = ("【此刻心情】0.45，偏低"
                     f"\n【原因】他说好「{script['promise']}」，等了约 {mins} 分钟"
                     "\n【请自然回应，不用刻意解释】")
        messages.append({"role": "user", "content": user})
        reply = chat(messages, PERSONA + STYLE + "\n" + state)
        messages.append({"role": "assistant", "content": reply})
        turns.append({"user": user, "reply": reply})
    return {"id": script["id"], "group": group, "hint": hint, "turns": turns}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=20)
    ap.add_argument("--groups", default="A,A2,A3,B")
    ap.add_argument("--tag", default="")
    ap.add_argument("--out", default=os.path.join(HERE, "results"))
    args = ap.parse_args()
    if not API_KEY:
        raise SystemExit("Set DEEPSEEK_API_KEY first.")
    os.makedirs(args.out, exist_ok=True)

    scripts = [json.loads(l) for l in open(os.path.join(DATA, "scripts.jsonl"), encoding="utf-8")][:args.limit]
    rows = []
    for s in scripts:
        for g in args.groups.split(","):
            row = run_one(s, g)
            rows.append(row)
            print(f"#{s['id']} {g} hint={bool(row['hint'])} len={[len(t['reply']) for t in row['turns']]}")

    name = "transcripts" + (("_" + args.tag) if args.tag else "") + ".jsonl"
    path = os.path.join(args.out, name)
    with open(path, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print("saved:", path)


if __name__ == "__main__":
    main()
