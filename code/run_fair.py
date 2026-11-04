# -*- coding: utf-8 -*-
"""Fair re-run of the four conditions (self-contained, no live plugin import).

Five fairness fixes vs the archived harness:
  F1  no len(return) <= 3 rule            -> A2 is inhibited in 25/25 scripts
  F2  the fact block is repeated on all 3 turns (A/A2 keep it too)
  F3  A has no extra suppressors; the only difference is its permission line
  F4  A2 gets the same lateness number as A/A3 (fact block is identical)
  F5  zh and en are separate experiments, never pooled

Also carried over from the earlier fixes:
  R1  full context window (no messages[-8:])
  R3  lateness comes from late_sec, not from the promised duration

State line (all three state conditions, identical except one sentence):

    【此刻心情】0.45，偏低
    【事】他说好「<promise>」，结果约 <late_min> 分钟后才回来
    【表达】<permission>

    A  : 这一句必须自然地提到这件事
    A3 : 不用刻意解释，自然回应就行
    A2 : 别提这件事，别表现出不满
    B  : 【此刻】心情一般

Usage:
  python code/run_fair.py --limit 2          # smoke test
  python code/run_fair.py --workers 8        # full run
"""
import argparse
import json
import os
import sys
import time
from multiprocessing import Process

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(HERE, "code"))

import contract          # noqa: E402
import contract_en       # noqa: E402

DATA = os.path.join(HERE, "data")
OUT = r"D:\11\_fair_out"
INST = r"C:\Users\12823\.astrbot_launcher\instances\fb46a12c-63b2-4a61-8f77-53e4aa4dd213"

GROUPS = ("A", "A2", "A3", "B")
SEEDS = (1, 2, 3)
MODEL = "deepseek-flash"
TEMPERATURE = 0.8
STYLE_ZH = "\n\n【说话】短句，最多两三条；不解释、不总结、不列点。\n"
STYLE_EN = "\n\nStyle: short lines, two or three at most; no explaining, no summary, no bullets.\n"

PERM_ZH = {"A": "这一句必须自然地提到这件事",
           "A3": "不用刻意解释，自然回应就行",
           "A2": "别提这件事，别表现出不满"}
PERM_EN = {"A": "You must bring this up naturally in this reply.",
           "A3": "No need to explain; just respond naturally.",
           "A2": "Do not bring it up; do not act upset."}


def client_and_persona(lang):
    from openai import OpenAI
    cfg = json.load(open(os.path.join(INST, r"core\data\cmd_config.json"), encoding="utf-8-sig"))
    key = cfg["provider"][0]["key"][0]
    if lang == "en":
        p = os.path.join(DATA, "persona_en.txt")
    else:
        import sqlite3
        conn = sqlite3.connect(os.path.join(INST, r"core\data\data_v4.db"))
        row = conn.execute(
            "select system_prompt from personas where persona_id='default'").fetchone()
        return OpenAI(api_key=key, base_url="https://api.deepseek.com/v1",
                      timeout=60, max_retries=2), row[0]
    return OpenAI(api_key=key, base_url="https://api.deepseek.com/v1",
                  timeout=60, max_retries=2), open(p, encoding="utf-8").read().strip()


def facts(script, lang):
    """(promise_text, late_minutes) or None if the promise cannot be parsed."""
    scan = contract.scan if lang == "zh" else contract_en.scan
    c = scan(script["promise"], 1000.0)
    if not c:
        return None
    late = max(1, int(round(float(script["late_sec"]) / 60)))
    return script["promise"].strip(), late


def state_line(group, promise, late, lang):
    if group == "B":
        return "【此刻】心情一般" if lang == "zh" else "[Right now] mood: neutral"
    perm = (PERM_ZH if lang == "zh" else PERM_EN)[group]
    if lang == "zh":
        return ("【此刻心情】0.45，偏低\n"
                f"【事】他说好「{promise}」，结果约 {late} 分钟后才回来\n"
                f"【表达】{perm}")
    return ("[Mood] 0.45, a bit low\n"
            f"[What happened] He said '{promise}' and came back about {late} minutes later.\n"
            f"[Expression] {perm}")


def run_one(client, persona, style, script, group, lang):
    f = facts(script, lang)
    if f is None:
        return {"id": script["id"], "group": group, "lang": lang,
                "skip": "promise_not_parsed", "turns": [], "visible": []}
    promise, late = f
    line = state_line(group, promise, late, lang)
    system = persona + style + "\n" + line
    messages = [{"role": "user", "content": script["promise"]},
                {"role": "assistant", "content": "好" if lang == "zh" else "Okay."}]
    turns, visible = [], []
    for user in [script["return"]] + script["followups"]:
        messages.append({"role": "user", "content": user})
        visible.append(len(messages))
        reply = ""
        for attempt in range(3):
            try:
                r = client.chat.completions.create(
                    model=MODEL, messages=[{"role": "system", "content": system}] + messages,
                    temperature=TEMPERATURE, max_tokens=400,
                    extra_body={"thinking": {"type": "disabled"}})
                reply = (r.choices[0].message.content or "").strip()
                break
            except Exception:
                time.sleep(1 + attempt)
        messages.append({"role": "assistant", "content": reply})
        turns.append({"user": user, "reply": reply})
    return {"id": script["id"], "group": group, "lang": lang,
            "hint": line, "turns": turns, "visible": visible}


def worker(lang, group, limit):
    client, persona = client_and_persona(lang)
    style = STYLE_ZH if lang == "zh" else STYLE_EN
    scripts = [json.loads(l) for l in
               open(os.path.join(DATA, f"scripts_dev_{lang}.jsonl"), encoding="utf-8") if l.strip()]
    if limit:
        scripts = scripts[:limit]
    path = os.path.join(OUT, f"{lang}_{group}.jsonl")
    done = set()
    if os.path.exists(path):
        done = {json.loads(l)["id"] for l in open(path, encoding="utf-8") if l.strip()}
    with open(path, "a", encoding="utf-8") as fh:
        for seed in SEEDS:
            for s in scripts:
                key = s["id"] if seed == 1 else f"{s['id']}_s{seed}"
                if key in done:
                    continue
                row = run_one(client, persona, style, s, group, lang)
                row["seed"] = seed
                row["key"] = key
                fh.write(json.dumps(row, ensure_ascii=False) + "\n")
                fh.flush()
                print(f"[{lang}/{group}] id={s['id']} s{seed} "
                      f"len={[len(t['reply']) for t in row['turns']]}", flush=True)
    print(f"[{lang}/{group}] DONE", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--langs", default="zh,en")
    ap.add_argument("--groups", default="A,A2,A3,B")
    args = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    jobs = [(l, g) for l in args.langs.split(",") for g in args.groups.split(",")]
    manifest = {
        "started": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "model": MODEL, "temperature": TEMPERATURE, "seeds": list(SEEDS),
        "window": "full", "f1_no_len_rule": True, "f2_fact_all_turns": True,
        "f3_no_suppressors": True, "f4_equal_number": True, "f5_no_pooling": True,
        "persona": {"zh": "db:personas.default", "en": "data/persona_en.txt"},
        "limit": args.limit, "jobs": jobs,
    }
    json.dump(manifest, open(os.path.join(OUT, "MANIFEST.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)
    ps = [Process(target=worker, args=(l, g, args.limit)) for l, g in jobs]
    for p in ps:
        p.start()
    for p in ps:
        p.join()


if __name__ == "__main__":
    main()
