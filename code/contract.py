# -*- coding: utf-8 -*-
"""Minimal contract state machine: promise -> breach -> expression hint.

This is a standalone extraction of the logic used in the reported experiment.
It deliberately keeps the "inhibition" wording in `check()`; condition A2 in
the paper is exactly this hint, while condition A overrides it with an explicit
"you must mention it" instruction.
"""
import re
import time

VAGUE = {
    "等我一下": 180, "等我一会儿": 240, "马上回来": 180, "我马上回": 180,
    "等我吃完饭": 1800, "等我洗完澡": 1200, "等我忙完": 900,
    "等我回个消息": 300, "等我拿个": 240, "等我接个电话": 300,
    "等我回来": 300, "等我弄完": 600, "等我写完": 600, "等我收拾完": 600,
}

EXCUSE_GOOD = ("开会", "手机静音", "没电", "堵车", "加班", "老板", "临时", "抱歉", "对不起")
EXCUSE_BAD = ("忘了", "没看到", "打游戏", "睡着了", "懒得")


def parse_num(s):
    cn = {"一": 1, "二": 2, "两": 2, "三": 3, "四": 4, "五": 5,
          "六": 6, "七": 7, "八": 8, "九": 9, "十": 10, "半": 0.5}
    if s.isdigit():
        return float(s)
    if s in cn:
        return float(cn[s])
    if s.startswith("十"):
        return 10 + cn.get(s[1:], 0)
    if "十" in s:
        a, b = s.split("十", 1)
        return cn.get(a, 1) * 10 + cn.get(b, 0)
    return 0.0


def scan(msg, now=None):
    """Return a contract dict if the message contains a promise, else None."""
    t = msg or ""
    now = now if now is not None else time.time()
    m = re.search(r"(等我|再等我|大概|差不多)?\s*([0-9]+|[一二两三四五六七八九十半]+)\s*(分钟|分|小时|点)", t)
    if m:
        if not any(w in t for w in ("等我", "分钟", "分", "小时", "点")):
            return None
        n = parse_num(m.group(2))
        if n <= 0:
            return None
        if m.group(3) in ("小时", "点"):
            n *= 60
        if n > 240:
            return None
        return {"promise": m.group(0).strip(), "expire_at": now + n * 60,
                "status": "pending"}
    hit = next((w for w in VAGUE if w in t), "")
    if not hit:
        return None
    return {"promise": hit, "expire_at": now + VAGUE[hit], "status": "pending"}


def check(contract, msg, now=None):
    """Settle a pending contract on the user's return.

    Returns (status, hint). Hint is the behavioral-inhibition text used by A2;
    an empty hint means either on-time or a good excuse.
    """
    now = now if now is not None else time.time()
    if not contract or contract.get("status") != "pending":
        return "", ""
    t = msg or ""
    if now < float(contract.get("expire_at") or 0):
        contract["status"] = "kept"
        return "kept", ""
    if any(w in t for w in EXCUSE_GOOD):
        contract["status"] = "resolved_external"
        return "resolved_external", ""
    if any(w in t for w in EXCUSE_BAD) or len(t) <= 3:
        contract["status"] = "escalated"
        return "escalated", ("【被放鸽子】他说好" + contract.get("promise", "")
                             + "，结果超时了，还没好好解释；带刺地问他一句，别讲道理")
    contract["status"] = "violated"
    return "violated", ("【轻不满】他说好的「" + contract.get("promise", "")
                        + "」超时了，心里不太舒服，嘴上别发作")
