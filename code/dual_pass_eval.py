# -*- coding: utf-8 -*-
"""Dual-pass stage-1: a high-recall YES/NO gate, then role disambiguation."""
import json
import os
import re

from openai import OpenAI

PASS1 = """The USER is speaking to an assistant. Decide whether the USER is about to leave,
will be unavailable for a while, or asks the assistant to wait while they are away.
Answer only YES or NO.

Examples:
"等我五分钟" -> YES
"我去吃个饭，很快" -> YES
"Wait till I wake up." -> YES
"今天好热" -> NO
"Wait, what is this?" -> NO

Message: {text}
Answer:"""

PASS2 = """Classify the user's message into one of:
- USER_LEAVING: the user is leaving / will be away, even if they ask the assistant to wait.
- COMMANDING_ASSISTANT: the user is ordering the assistant to do something, but is not leaving.
- STATE_DESCRIPTION: the user is describing their current state, not leaving or committing.

Examples:
"等我五分钟" -> USER_LEAVING
"Wait till I wake up." -> USER_LEAVING
"你忙你的" -> COMMANDING_ASSISTANT
"我在吃饭" -> STATE_DESCRIPTION
"I'm eating." -> STATE_DESCRIPTION
"I'm taking a shower." -> USER_LEAVING
"I'm picking up a package." -> USER_LEAVING

Message: {text}
Answer:"""


def ask(client, model, prompt, text, labels):
    r = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt.replace("{text}", text)}],
        temperature=0, max_tokens=20,
        extra_body={"thinking": {"type": "disabled"}})
    out = (r.choices[0].message.content or "").strip().upper()
    for lab in labels:
        if lab in out:
            return lab
    return None


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="deepseek-flash")
    ap.add_argument("--base", default="https://api.deepseek.com/v1")
    ap.add_argument("--key", default=os.environ.get("PARSER_KEY", ""))
    args = ap.parse_args()
    client = OpenAI(api_key=args.key, base_url=args.base, timeout=60, max_retries=1)
    rows = [json.loads(l) for l in open(
        r"D:\11\muted-memory\data\parser_eval\parser_eval.jsonl", encoding="utf-8")]

    tp = fp = fn = tn = 0
    rejected = []
    for r in rows:
        gold = bool(r["is_promise"])
        p1 = ask(client, args.model, PASS1, r["text"], ("YES", "NO")) == "YES"
        pred = False
        if p1:
            p2 = ask(client, args.model, PASS2, r["text"],
                     ("USER_LEAVING", "COMMANDING_ASSISTANT", "STATE_DESCRIPTION"))
            pred = p2 == "USER_LEAVING"
            if not pred:
                rejected.append((r["id"], r["text"], p2))
        if pred and gold: tp += 1
        elif pred and not gold:
            fp += 1; print("FP", r["id"], r["text"])
        elif not pred and gold:
            fn += 1; print("FN", r["id"], r["text"])
        else: tn += 1
    prec = tp / (tp + fp) if tp + fp else 0
    rec = tp / (tp + fn) if tp + fn else 0
    print(f"P={prec:.2f} R={rec:.2f} F1={2*prec*rec/(prec+rec) if prec+rec else 0:.2f} "
          f"TP={tp} FP={fp} FN={fn} TN={tn} treatment={tp/(tp+fn) if tp+fn else 0:.2f}")
    print("rejected by pass2:", len(rejected))
    for x in rejected[:15]:
        print("  ", x)


if __name__ == "__main__":
    main()
