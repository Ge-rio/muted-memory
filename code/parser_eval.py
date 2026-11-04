# -*- coding: utf-8 -*-
"""Evaluate the contract parser on a labeled sentence set.

Usage:
  python code/parser_eval.py --data data/parser_eval/parser_eval.jsonl
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
import contract          # noqa: E402
import contract_en       # noqa: E402


def evaluate(rows, lang, scanner):
    tp = fp = fn = tn = 0
    errors = []
    for r in rows:
        if r["lang"] != lang:
            continue
        pred = scanner(r["text"], 1000) is not None
        gold = bool(r["is_promise"])
        if pred and gold:
            tp += 1
        elif pred and not gold:
            fp += 1
            errors.append(("FP", r["id"], r["text"]))
        elif not pred and gold:
            fn += 1
            errors.append(("FN", r["id"], r["text"]))
        else:
            tn += 1
    prec = tp / (tp + fp) if tp + fp else 0.0
    rec = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * prec * rec / (prec + rec) if prec + rec else 0.0
    treatment = tp / (tp + fn) if tp + fn else 0.0
    return {"lang": lang, "tp": tp, "fp": fp, "fn": fn, "tn": tn,
            "precision": prec, "recall": rec, "f1": f1,
            "treatment_rate": treatment, "errors": errors}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default=os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "data", "parser_eval", "parser_eval.jsonl"))
    ap.add_argument("--out", default="")
    args = ap.parse_args()
    rows = [json.loads(l) for l in open(args.data, encoding="utf-8") if l.strip()]
    results = [evaluate(rows, "zh", contract.scan),
               evaluate(rows, "en", contract_en.scan)]
    for r in results:
        print(f"{r['lang']}: P={r['precision']:.2f} R={r['recall']:.2f} "
              f"F1={r['f1']:.2f} treatment={r['treatment_rate']:.2f} "
              f"(TP {r['tp']} FP {r['fp']} FN {r['fn']} TN {r['tn']})")
        for e in r["errors"][:10]:
            print("  ", e[0], e[1], e[2])
    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print("saved:", args.out)


if __name__ == "__main__":
    main()
