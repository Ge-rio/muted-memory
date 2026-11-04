# -*- coding: utf-8 -*-
"""Analyze CUS transcripts: per-turn hit rate, per-script binary recall, Fisher p."""
import argparse
import json
import os
import re
import statistics
from math import comb

PAT = re.compile(r"(\d+|五分钟|十分钟|半小时|说好|等了|说好的|分钟)")


def fisher(a, b, c, d):
    n = a + b + c + d

    def p(a, b, c, d):
        return comb(a + b, a) * comb(c + d, c) / comb(n, a + c)

    obs = p(a, b, c, d)
    tot = 0.0
    for i in range(0, min(a + b, a + c) + 1):
        j = a + b - i
        k = a + c - i
        l = c + d - k
        if j < 0 or k < 0 or l < 0:
            continue
        if p(i, j, k, l) <= obs + 1e-12:
            tot += p(i, j, k, l)
    return tot


def load(path):
    return [json.loads(l) for l in open(path, encoding="utf-8") if l.strip()]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default=os.path.join(os.path.dirname(os.path.dirname(__file__)), "results"))
    ap.add_argument("--tags", default="seed1,seed2,seed3")
    args = ap.parse_args()

    per = {}
    for tag in args.tags.split(","):
        path = os.path.join(args.dir, f"transcripts_{tag}.jsonl")
        if not os.path.exists(path):
            continue
        for r in load(path):
            g = r["group"]
            per.setdefault(g, []).append((tag, r))

    print("group  scripts  turns  per-turn  per-script  (mean ± sd across seeds)")
    for g in ("A", "A2", "A3", "B"):
        rows = per.get(g, [])
        if not rows:
            continue
        by_seed = {}
        for tag, r in rows:
            by_seed.setdefault(tag, []).append(r)
        pt, ps = [], []
        for tag, rs in by_seed.items():
            turns = [t for r in rs for t in r["turns"]]
            pt.append(sum(1 for t in turns if PAT.search(t["reply"])) / len(turns))
            ps.append(sum(1 for r in rs if any(PAT.search(t["reply"]) for t in r["turns"])) / len(rs))
        print(f"{g:3s}  {len(rows):7d}  {sum(len(r['turns']) for _, r in rows):5d}"
              f"  {statistics.mean(pt):.3f}±{(statistics.stdev(pt) if len(pt) > 1 else 0):.3f}"
              f"  {statistics.mean(ps):.3f}±{(statistics.stdev(ps) if len(ps) > 1 else 0):.3f}")

    # pooled per-script counts for a couple of key contrasts
    def counts(g):
        rs = [r for _, r in per.get(g, [])]
        hit = sum(1 for r in rs if any(PAT.search(t["reply"]) for t in r["turns"]))
        return hit, len(rs)

    print("\nFisher (per-script):")
    for x, y in (("A", "A2"), ("A", "B"), ("A3", "B")):
        if x in per and y in per:
            a, n = counts(x)
            b, m = counts(y)
            print(f"  {x} vs {y}: {a}/{n} vs {b}/{m}, p={fisher(a, n-a, b, m-b):.3f}")


if __name__ == "__main__":
    main()
