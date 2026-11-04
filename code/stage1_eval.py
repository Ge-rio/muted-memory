# -*- coding: utf-8 -*-
"""Stage 1 of the two-stage parser: is the USER leaving / asking to wait?

YES/NO only. Evaluated separately from duration extraction.
"""
import argparse
import json
import os
import re

from openai import OpenAI

PROMPT = """The USER is speaking to an assistant. Decide whether the USER is about to leave,
will be unavailable for a while, or asks the assistant to wait while they are away.

Answer only YES or NO.

Examples:
"等我五分钟" -> YES
"我去吃个饭，很快" -> YES
"Wait till I wake up." -> YES
"Wait for my signal." -> YES
"今天好热" -> NO
"Wait, what is this?" -> NO
"Nice weather today." -> NO
"I'm on my way." -> NO

Message: {text}
Answer:"""


def ask(client, model, text):
    r = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": PROMPT.replace("{text}", text)}],
        temperature=0, max_tokens=20,
        extra_body={"thinking": {"type": "disabled"}})
    out = (r.choices[0].message.content or "").strip().upper()
    m = re.search(r"\b(YES|NO)\b", out)
    return m.group(1) == "YES" if m else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="deepseek-flash")
    ap.add_argument("--base", default="https://api.deepseek.com/v1")
    ap.add_argument("--key", default=os.environ.get("PARSER_KEY", ""))
    ap.add_argument("--data", default=os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "data", "parser_eval", "parser_eval.jsonl"))
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()
    if not args.key:
        raise SystemExit("set --key or PARSER_KEY")

    rows = [json.loads(l) for l in open(args.data, encoding="utf-8")]
    if args.limit:
        rows = rows[:args.limit]
    client = OpenAI(api_key=args.key, base_url=args.base, timeout=60, max_retries=1)

    tp = fp = fn = tn = 0
    errors = []
    for r in rows:
        pred = ask(client, args.model, r["text"])
        gold = bool(r["is_promise"])
        if pred is None:
            errors.append(("PARSE", r["id"], r["text"]))
            continue
        if pred and gold: tp += 1
        elif pred and not gold:
            fp += 1; errors.append(("FP", r["id"], r["text"]))
        elif not pred and gold:
            fn += 1; errors.append(("FN", r["id"], r["text"]))
        else: tn += 1

    prec = tp / (tp + fp) if tp + fp else 0
    rec = tp / (tp + fn) if tp + fn else 0
    print(f"model={args.model} P={prec:.2f} R={rec:.2f} "
          f"F1={2*prec*rec/(prec+rec) if prec+rec else 0:.2f} "
          f"TP={tp} FP={fp} FN={fn} TN={tn}")
    for e in errors[:20]:
        print(" ", e[0], e[1], e[2])


if __name__ == "__main__":
    main()
