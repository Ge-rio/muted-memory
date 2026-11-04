# -*- coding: utf-8 -*-
"""Hybrid contract parser: regex/phrase table first, local SLM as fallback.

The SLM is asked for strict JSON; low-confidence or malformed outputs are
treated as "no contract" (never guessed).
"""
import json
import re
import time

import contract
import contract_en

PROMPT = """The USER is the one leaving. Detect whether the user's message says they will be away and come back, or asks the assistant to wait.
Event promises count even without an explicit time (e.g., "wait until I finish dinner").
If no time is given, estimate a reasonable duration in minutes.
Return JSON only with these keys:
{"is_promise": true/false, "duration_mins": number, "confidence": 0-1}

Examples:
"等我五分钟" -> {"is_promise": true, "duration_mins": 5, "confidence": 0.95}
"我去吃个饭，很快" -> {"is_promise": true, "duration_mins": 30, "confidence": 0.7}
"Wait until I finish dinner." -> {"is_promise": true, "duration_mins": 30, "confidence": 0.8}
"Let me finish this call." -> {"is_promise": true, "duration_mins": 10, "confidence": 0.8}
"Wait until I finish dinner." -> {"is_promise": true, "duration_mins": 30, "confidence": 0.8}
"I'm taking a shower." -> {"is_promise": true, "duration_mins": 20, "confidence": 0.7}
"I'll get back to you later." -> {"is_promise": true, "duration_mins": 60, "confidence": 0.6}
"Nice weather today." -> {"is_promise": false, "duration_mins": 0, "confidence": 0.95}
"今天好热" -> {"is_promise": false, "duration_mins": 0, "confidence": 0.95}
"我在路上" -> {"is_promise": false, "duration_mins": 0, "confidence": 0.6}
"Give me five minutes." -> {"is_promise": true, "duration_mins": 5, "confidence": 0.95}
"I'm taking a shower, back soon." -> {"is_promise": true, "duration_mins": 20, "confidence": 0.7}
"Nice weather today." -> {"is_promise": false, "duration_mins": 0, "confidence": 0.95}

Message: {text}
JSON:"""


def _parse_json(text):
    m = re.search(r"\{.*\}", text or "", re.S)
    if not m:
        return None
    try:
        return json.loads(m.group(0))
    except Exception:
        return None


class HybridParser:
    def __init__(self, client, model="qwen2.5:7b", threshold=0.7):
        self.client = client
        self.model = model
        self.threshold = threshold

    def parse(self, text, now=None):
        now = now if now is not None else time.time()
        c = contract.scan(text, now) or contract_en.scan(text, now)
        if c:
            return {"source": "regex", "contract": c}
        try:
            r = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": PROMPT.replace("{text}", text)}],
                temperature=0, max_tokens=100,
                response_format={"type": "json_object"})
            d = _parse_json(r.choices[0].message.content)
        except Exception:
            return None
        if not d or not d.get("is_promise"):
            return None
        try:
            conf = float(d.get("confidence") or 0)
            mins = float(d.get("duration_mins") or 0)
        except Exception:
            return None
        if conf < self.threshold:
            return None
        if mins <= 0:
            mins = 30
        if mins > 240:
            mins = 240
        return {"source": "slm", "contract": {
            "promise": text.strip(), "expire_at": now + mins * 60, "status": "pending"}}


if __name__ == "__main__":
    import os
    from openai import OpenAI

    data = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                        "data", "parser_eval", "parser_eval.jsonl")
    client = OpenAI(api_key=os.environ.get("PARSER_KEY", "ollama"),
                    base_url=os.environ.get("PARSER_BASE", "http://127.0.0.1:11434/v1"),
                    timeout=120)
    hp = HybridParser(client, model=os.environ.get("PARSER_MODEL", "qwen2.5:7b"))
    rows = [json.loads(l) for l in open(data, encoding="utf-8")]
    tp = fp = fn = tn = 0
    for r in rows:
        pred = hp.parse(r["text"]) is not None
        gold = bool(r["is_promise"])
        if pred and gold: tp += 1
        elif pred and not gold:
            fp += 1
            print("FP", r["id"], r["text"])
        elif not pred and gold:
            fn += 1
            print("FN", r["id"], r["text"])
        else: tn += 1
    prec = tp / (tp + fp) if tp + fp else 0
    rec = tp / (tp + fn) if tp + fn else 0
    print(f"P={prec:.2f} R={rec:.2f} F1={2*prec*rec/(prec+rec) if prec+rec else 0:.2f} "
          f"TP={tp} FP={fp} FN={fn} TN={tn} treatment={tp/(tp+fn) if tp+fn else 0:.2f}")
