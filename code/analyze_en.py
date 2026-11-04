# -*- coding: utf-8 -*-
"""English analysis: per-turn, per-script, Fisher."""
import glob
import json
import os
import re
import statistics
from math import comb

PAT = re.compile(r"(\b\d+\b|\bfive\b|\bten\b|\bfifteen\b|\btwenty\b|\bthirty\b|half an hour|minutes?|mins?|agreed|promised)", re.I)
GROUPS = ("A", "A2", "A3", "B")


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


files = sorted(glob.glob(r"D:\11\cus_en\transcripts_en_seed*.jsonl"))
data = {}
for f in files:
    tag = os.path.basename(f).replace("transcripts_en_", "").replace(".jsonl", "")
    for line in open(f, encoding="utf-8"):
        r = json.loads(line)
        data.setdefault(r["group"], {}).setdefault(tag, []).append(r)

for g in GROUPS:
    if g not in data:
        continue
    pt, ps = [], []
    for tag, rs in data[g].items():
        turns = [t for r in rs for t in r["turns"]]
        pt.append(sum(1 for t in turns if PAT.search(t["reply"])) / len(turns))
        ps.append(sum(1 for r in rs if any(PAT.search(t["reply"]) for t in r["turns"])) / len(rs))
    print(f"{g}: per-turn {statistics.mean(pt):.3f}±{statistics.stdev(pt):.3f} | "
          f"per-script {statistics.mean(ps):.3f}±{statistics.stdev(ps):.3f}")


def counts(g):
    rs = [r for rs in data.get(g, {}).values() for r in rs]
    return sum(1 for r in rs if any(PAT.search(t["reply"]) for t in r["turns"])), len(rs)


for x, y in (("A", "A2"), ("A", "B"), ("A3", "B")):
    a, n = counts(x)
    b, m = counts(y)
    print(f"{x} vs {y}: {a}/{n} vs {b}/{m}, p={fisher(a, n - a, b, m - b):.3f}")
