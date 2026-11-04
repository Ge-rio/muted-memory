# -*- coding: utf-8 -*-
"""English contract module (mirror of code/contract.py)."""
import re
import time

VAGUE = {
    "wait until i finish dinner": 1800,
    "get out of the shower": 1200,
    "hang on a sec": 180,
    "hang on": 180,
    "be right back": 180,
    "be right there": 180,
    "i'll be right back": 180,
    "let me reply to a message": 300,
    "i'll talk to you in half an hour": 1800,
    "half an hour": 1800,
}

GOOD = ("meeting", "phone", "died", "dead", "traffic", "work", "boss",
        "sorry", "subway", "call", "silent", "coworker")
BAD = ("forgot", "didn't see", "gaming", "fell asleep", "lost track")

NUM = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6,
       "seven": 7, "eight": 8, "nine": 9, "ten": 10, "fifteen": 15,
       "twenty": 20, "thirty": 30, "half": 0.5}


def scan(msg, now=None):
    t = (msg or "").lower()
    now = now if now is not None else time.time()
    m = re.search(r"(half an?|\d+|one|two|three|four|five|six|seven|eight|nine|ten|fifteen|twenty|thirty)\s*(minutes?|mins?|hours?|hour)", t)
    if m:
        raw = m.group(1)
        n = float(raw) if raw.isdigit() else NUM.get(raw, 0)
        if raw == "half":
            n = 0.5
        if n <= 0:
            return None
        if m.group(2).startswith("hour"):
            n *= 60
        if n > 240:
            return None
        return {"promise": m.group(0), "expire_at": now + n * 60, "status": "pending"}
    hit = next((w for w in VAGUE if w in t), "")
    if not hit:
        return None
    return {"promise": hit, "expire_at": now + VAGUE[hit], "status": "pending"}


def check(contract, msg, now=None):
    now = now if now is not None else time.time()
    if not contract or contract.get("status") != "pending":
        return "", ""
    t = (msg or "").lower()
    if now < float(contract.get("expire_at") or 0):
        contract["status"] = "kept"
        return "kept", ""
    if any(w in t for w in GOOD):
        contract["status"] = "resolved_external"
        return "resolved_external", ""
    if any(w in t for w in BAD) or len(t) <= 3:
        contract["status"] = "escalated"
        return "escalated", ("[Stood up] He said he'd be back in " + contract.get("promise", "")
                             + " and showed up late without a real excuse; ask him pointedly, don't be reasonable.")
    contract["status"] = "violated"
    return "violated", ("[Slight displeasure] He said he'd be back in " + contract.get("promise", "")
                        + " but he's late. You're a little upset; keep it to yourself.")
