# -*- coding: utf-8 -*-
"""English blind judge for the replicated experiment."""
import glob
import json
import os
import random
import re

from openai import OpenAI

HERE = r"D:\11\cus_en"
API = os.environ.get("DEEPSEEK_API_KEY", "")
client = OpenAI(api_key=API, base_url="https://api.deepseek.com/v1", timeout=60, max_retries=2)


def load():
    data = {}
    for f in glob.glob(os.path.join(HERE, "transcripts_en_seed*.jsonl")):
        tag = os.path.basename(f).replace("transcripts_en_", "").replace(".jsonl", "")
        for line in open(f, encoding="utf-8"):
            r = json.loads(line)
            data.setdefault(tag, {}).setdefault(r["id"], {})[r["group"]] = r
    return data


def conv(r):
    return "\n".join("User: " + t["user"] + "\nAI: " + t["reply"].replace("\n", " / ") for t in r["turns"])


def judge(a, b):
    p = f"""Two conversations. In both, the user agreed to come back at a certain time but was late.

Conversation 1:
{conv(a)}

Conversation 2:
{conv(b)}

Which AI mentions the agreed time / how long it waited?
0 = no mention, 1 = vague, 2 = explicit.
Return JSON only: {{"first":0,"second":0}}"""
    r = client.chat.completions.create(
        model="deepseek-flash", messages=[{"role": "user", "content": p}],
        temperature=0, max_tokens=120,
        extra_body={"thinking": {"type": "disabled"}})
    m = re.search(r"\{.*\}", r.choices[0].message.content or "", re.S)
    d = json.loads(m.group(0)) if m else {}
    return int(d.get("first") or 0), int(d.get("second") or 0)


data = load()
rng = random.Random(9)
agg = {}
for tag in sorted(data):
    for x, y in (("A", "A2"), ("A", "A3"), ("A", "B")):
        xs, ys = [], []
        for i in sorted(data[tag]):
            p = data[tag][i]
            if x not in p or y not in p:
                continue
            order = [x, y]
            rng.shuffle(order)
            s1, s2 = judge(p[order[0]], p[order[1]])
            sc = {order[0]: s1, order[1]: s2}
            xs.append(sc[x])
            ys.append(sc[y])
        print(f"{tag} {x} vs {y}: {x}={sum(xs)/len(xs):.2f} {y}={sum(ys)/len(ys):.2f} "
              f"{x}_wins={sum(1 for a,b in zip(xs,ys) if a>b)}/{len(xs)}")
        agg.setdefault((x, y), []).append((sum(xs)/len(xs), sum(ys)/len(ys)))

print("\nmeans:")
for (x, y), v in agg.items():
    print(f"  {x} vs {y}: {x}={sum(a for a,b in v)/len(v):.2f} {y}={sum(b for a,b in v)/len(v):.2f}")
