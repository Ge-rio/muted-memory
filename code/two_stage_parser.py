# -*- coding: utf-8 -*-
"""Two-stage parser: YES/NO role check, then duration extraction."""
import json
import re
import time

import contract
import contract_en

STAGE1 = """The USER is speaking to an assistant. Decide whether the USER is about to leave,
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

Message: {text}
Answer:"""

STAGE2_ROLE = """Classify the user's message into one of:
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

STAGE2 = """The user is leaving or asking the assistant to wait. Extract the duration.
Return JSON only: {"duration_mins": number, "event": "short phrase"}
If no duration is given, use 30 minutes.

Message: {text}
JSON:"""


class TwoStageParser:
    def __init__(self, client, model="deepseek-flash", stage1_model=None, stage2_model=None):
        self.client = client
        self.m1 = stage1_model or model
        self.m2 = stage2_model or model
        self.threshold = 0.5

    def _yes(self, text):
        r = self.client.chat.completions.create(
            model=self.m1,
            messages=[{"role": "user", "content": STAGE1.replace("{text}", text)}],
            temperature=0, max_tokens=20,
            extra_body={"thinking": {"type": "disabled"}})
        out = (r.choices[0].message.content or "").upper()
        m = re.search(r"\b(YES|NO)\b", out)
        if not (m and m.group(1) == "YES"):
            return False
        r2 = self.client.chat.completions.create(
            model=self.m1,
            messages=[{"role": "user", "content": STAGE2_ROLE.replace("{text}", text)}],
            temperature=0, max_tokens=20,
            extra_body={"thinking": {"type": "disabled"}})
        out2 = (r2.choices[0].message.content or "").upper()
        return "USER_LEAVING" in out2

    def _duration(self, text):
        try:
            r = self.client.chat.completions.create(
                model=self.m2,
                messages=[{"role": "user", "content": STAGE2.replace("{text}", text)}],
                temperature=0, max_tokens=80,
                response_format={"type": "json_object"},
                extra_body={"thinking": {"type": "disabled"}})
            m = re.search(r"\{.*\}", r.choices[0].message.content or "", re.S)
            d = json.loads(m.group(0)) if m else {}
            mins = float(d.get("duration_mins") or 30)
        except Exception:
            mins = 30
        return min(max(mins, 1), 240)

    def parse(self, text, now=None):
        now = now if now is not None else time.time()
        c = contract.scan(text, now) or contract_en.scan(text, now)
        if c:
            return {"source": "regex", "contract": c}
        if not self._yes(text):
            return None
        mins = self._duration(text)
        return {"source": "two-stage", "contract": {
            "promise": text.strip(), "expire_at": now + mins * 60, "status": "pending"}}


if __name__ == "__main__":
    import os
    from openai import OpenAI

    rows = [json.loads(l) for l in open(
        r"D:\11\muted-memory\data\parser_eval\parser_eval.jsonl", encoding="utf-8")]
    client = OpenAI(api_key=os.environ.get("PARSER_KEY"), base_url=os.environ.get("PARSER_BASE"),
                    timeout=60, max_retries=1)
    p = TwoStageParser(client, model=os.environ.get("PARSER_MODEL", "deepseek-flash"))
    tp = fp = fn = tn = 0
    for r in rows:
        pred = p.parse(r["text"]) is not None
        gold = bool(r["is_promise"])
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
