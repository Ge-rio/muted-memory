# -*- coding: utf-8 -*-
"""English replication of the CUS A/A2/A3/B experiment."""
import argparse
import json
import os
import sys

from openai import OpenAI

sys.path.insert(0, os.path.dirname(__file__))
import contract_en  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
API_KEY = os.environ.get("DEEPSEEK_API_KEY", "")
BASE_URL = os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1")
MODEL = os.environ.get("DEEPSEEK_MODEL", "deepseek-flash")
PERSONA = open(os.path.join(HERE, "persona_en.txt"), encoding="utf-8").read().strip()
STYLE = "\n\n[Style] Short lines, one to three per reply. No explaining, no summarizing, no bullet points.\n"

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
    messages = [{"role": "user", "content": script["promise"]},
                {"role": "assistant", "content": "Okay."}]
    hint, mins = "", 5
    if group in ("A", "A2", "A3"):
        c = contract_en.scan(script["promise"], now[0])
        if c:
            mins = max(1, round((c["expire_at"] - now[0]) / 60))
            now[0] += script["late_sec"]
            _, hint = contract_en.check(c, script["return"], now[0])

    if group == "A" and hint:
        messages.append({"role": "system", "content": (
            f"[Hidden note] He is back. You remember he said '{script['promise']}', "
            f"and you waited about {mins} minutes. You must naturally mention it "
            "(e.g., 'five minutes'), keep it short, do not just say 'you're back'.")})

    turns = []
    for i, user in enumerate([script["return"]] + script["followups"]):
        state = "[Mood] neutral."
        if group == "A" and hint and i <= 2:
            base = hint if i == 0 else "[Still remembering] It is not over yet; do not warm up immediately."
            state = (base + f"\n[Wait time] about {mins} minutes; you may mention it naturally."
                     + "\n[Style] shorter, do not ask how he is, do not explain.")
        elif group == "A2" and hint and i <= 2:
            base = hint if i == 0 else "[Still remembering] It is not over yet."
            state = base + "\n[Mood] 0.45, low."
        elif group == "A3" and hint and i <= 2:
            state = ("[Mood] 0.45, low."
                     f"\n[Reason] He said he'd be back in {script['promise']}; you waited about {mins} minutes."
                     "\n[Respond naturally, no need to explain.]")
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
    args = ap.parse_args()
    if not API_KEY:
        raise SystemExit("Set DEEPSEEK_API_KEY first.")
    scripts = [json.loads(l) for l in open(os.path.join(HERE, "scripts_en.jsonl"), encoding="utf-8")][:args.limit]
    rows = []
    for s in scripts:
        for g in args.groups.split(","):
            r = run_one(s, g)
            rows.append(r)
            print(f"#{s['id']} {g} hint={bool(r['hint'])} len={[len(t['reply']) for t in r['turns']]}")
    name = "transcripts_en" + (("_" + args.tag) if args.tag else "") + ".jsonl"
    with open(os.path.join(HERE, name), "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print("saved:", name)


if __name__ == "__main__":
    main()
