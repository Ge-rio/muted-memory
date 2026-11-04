# -*- coding: utf-8 -*-
"""Score MUTE transcripts.

Input: one or more JSONL files, each line:
  {"id": 1, "group": "A", "hint": true, "turns": [{"user": "...", "reply": "..."}]}

Output: per-group per-script / per-turn rates, mean ± sd across files, Fisher p.
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import re
import statistics
from math import comb

ZH = re.compile(r"(\d+|五分钟|十分钟|半小时|说好|等了|说好的|分钟)")
EN = re.compile(r"(\b\d+\b|\bfive\b|\bten\b|\bfifteen\b|\btwenty\b|\bthirty\b|half an hour|minutes?|mins?|agreed|promised)", re.I)
GROUPS = ("A", "A2", "A3", "B")


def fisher(a: int, b: int, c: int, d: int) -> float:
    n = a + b + c + d

    def p(a, b, c, d):
        return comb(a + b, a) * comb(c + d, c) / comb(n, a + c)

    obs = p(a, b, c, d)
    total = 0.0
    for i in range(0, min(a + b, a + c) + 1):
        j = a + b - i
        k = a + c - i
        l = c + d - k
        if j < 0 or k < 0 or l < 0:
            continue
        if p(i, j, k, l) <= obs + 1e-12:
            total += p(i, j, k, l)
    return total


def load(path: str) -> list[dict]:
    return [json.loads(l) for l in open(path, encoding="utf-8") if l.strip()]


def score_file(path: str, pattern: re.Pattern, groups=GROUPS) -> dict:
    rows = load(path)
    out = {}
    for g in groups:
        rs = [r for r in rows if r.get("group") == g]
        if not rs:
            continue
        turns = [t for r in rs for t in r.get("turns", [])]
        hits_turn = sum(1 for t in turns if pattern.search(t.get("reply") or ""))
        hits_script = sum(1 for r in rs if any(pattern.search(t.get("reply") or "")
                                               for t in r.get("turns", [])))
        out[g] = {
            "scripts": len(rs),
            "turns": len(turns),
            "per_turn": hits_turn / len(turns) if turns else 0.0,
            "per_script": hits_script / len(rs) if rs else 0.0,
            "script_hits": hits_script,
        }
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--files", nargs="+", required=True)
    ap.add_argument("--lang", choices=["zh", "en"], default="zh")
    ap.add_argument("--out", default="")
    args = ap.parse_args()

    pattern = ZH if args.lang == "zh" else EN
    files = []
    for f in args.files:
        files.extend(sorted(glob.glob(f)))
    if not files:
        raise SystemExit("no transcript files matched")

    per_file = {os.path.basename(f): score_file(f, pattern) for f in files}
    agg = {}
    for g in GROUPS:
        rows = [pf[g] for pf in per_file.values() if g in pf]
        if not rows:
            continue
        ps = [r["per_script"] for r in rows]
        pt = [r["per_turn"] for r in rows]
        agg[g] = {
            "files": len(rows),
            "scripts": sum(r["scripts"] for r in rows),
            "per_script_mean": statistics.mean(ps),
            "per_script_sd": statistics.stdev(ps) if len(ps) > 1 else 0.0,
            "per_turn_mean": statistics.mean(pt),
            "per_turn_sd": statistics.stdev(pt) if len(pt) > 1 else 0.0,
        }

    print(f"{'group':5s} {'scripts':>8s} {'per-script':>18s} {'per-turn':>18s}")
    for g, r in agg.items():
        print(f"{g:5s} {r['scripts']:8d} "
              f"{r['per_script_mean']:.3f} ± {r['per_script_sd']:.3f}   "
              f"{r['per_turn_mean']:.3f} ± {r['per_turn_sd']:.3f}")

    def counts(g):
        rs = [r for pf in per_file.values() if g in pf for r in [pf[g]]]
        hit = sum(r["script_hits"] for r in rs)
        n = sum(r["scripts"] for r in rs)
        return hit, n

    tests = {}
    for x, y in (("A", "A2"), ("A", "B"), ("A3", "B")):
        if x in agg and y in agg:
            a, n = counts(x)
            b, m = counts(y)
            p = fisher(a, n - a, b, m - b)
            tests[f"{x}_vs_{y}"] = {"p": p, "x": f"{a}/{n}", "y": f"{b}/{m}"}
            ptxt = "<0.0001" if p < 0.0001 else f"{p:.4f}"
            print(f"{x} vs {y}: {a}/{n} vs {b}/{m}, p={ptxt}")

    payload = {"lang": args.lang, "files": files, "per_file": per_file,
               "aggregate": agg, "tests": tests}
    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
        print("saved:", args.out)


if __name__ == "__main__":
    main()
