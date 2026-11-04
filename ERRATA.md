# ERRATA

Everything below was believed, published in this repository, and later withdrawn. Newest first.
Each entry: what we claimed, what was actually true, the evidence, and what changed.

---

## 5. Production contract never fires (2026-11-05)

**Claimed:** the deployed companion gets mildly upset when the user breaks a promise.

**Actually:** the contract was created and settled inside the same call, so the "violated" and
"escalated" branches never executed. She was simply never upset.

**Evidence** (`astrbot_plugin_dafeiyu_life/main.py`, a private file, not in this repo):

```
2332  self._contract_scan(msg)                          # creates contract, expire_at = now + N
2333  self._contract_line = self._contract_check(msg)    # settles it on the same message
4409  if time.time() < float(c.get("expire_at") or 0):
4410      c["status"] = "kept"                            # always true right after creation
4412      return ""
```

The experiment harness called `scan()` → advanced the clock → `check()`, so the experiment
exercised a path the deployment could never reach. Both sides' unit tests passed.

**Fix:** call `check()` before `scan()`; drop `len(t) <= 3`; stop treating `点` as an hour unit
(`等我三点` was parsed as 180 minutes). Applied 2026-11-05, requires restart.

**Why it matters here:** this is the same class of error as R1/R3 — the state existed in the code
and never reached the model. It produces no symptom; it looks like a calm personality.

---

## 4. `len(return) <= 3` inverted the inhibited condition (2026-11-05)

**Claimed:** A2 is the "persona forbids expression" condition.

**Actually:** for **20 of 25 Chinese scripts**, A2 received the *escalated* hint
("ask him pointedly, don't be reasonable") because the return message was three characters or
shorter ("回来了", "在吗", "来了"). That is the opposite of inhibition. English: 0/25 affected,
because English returns are longer than three characters.

**Evidence:**

```
code/contract.py:77   if any(w in t for w in EXCUSE_BAD) or len(t) <= 3:
                      → escalated: "带刺地问他一句，别讲道理"
```

Chinese returns: 20/25 have length ≤ 3. English: 0/25.

**Consequence:** every A2 comparison in v0.1 was run on a condition that was reversed for 80% of
the Chinese set. The "inhibition effect is weak" result was a property of the stimulus, not of
inhibition.

**Fix:** removed the `len(t) <= 3` rule; the fair harness (`code/run_fair.py`) builds state lines
itself and ignores this branch entirely.

**After the fix:** A3 vs A2 goes from p=.072 (unbalanced) to **p=.0087** (Chinese) / **p=.0211**
(English).

---

## 3. The state line rendered the promised duration as the lateness (2026-11-05)

**Claimed:** A3 is "state + reason, respond naturally" — a natural-permission condition.

**Actually:** the hint was built from `mins = round((expire_at - now)/60)`, i.e. the *promised*
duration, and then labelled as how long she waited. For a 5-minute promise and a 6-minute absence
this is nearly right; for a 10-minute promise and a 25-minute absence it is wrong by 15 minutes.
Worse, for A3 the line read "he said 10 minutes, waited about 10 minutes" — **on time, no breach.**

**Evidence** (archived harness, private; fixed in this repo's `code/cus_ab.py` at 61 / 70 / 86):

```
59   mins = max(1, round((expire_at - now) / 60))     # promised duration
68   A : "你等了约 {mins} 分钟"                        # rendered as if it were the wait
84   A3: "他说好「...」，等了约 {mins} 分钟"            # reads as on time
```

`late_sec` was only used to advance the clock; it was never rendered. The public copy now uses
`late_min = round(late_sec / 60)` instead, so this specific defect is not reproducible from this
repository — only the `len(t) <= 3` one is.

**Consequence:** the numbers A/A3 produced in v0.1 partly reflect *copying an injected value*,
and A3's stimulus encoded "no breach". Those runs cannot be read as expression of a state.

**Fix:** `late_min = round(late_sec / 60)`, rendered in both A and A3; the fair harness derives it
from the script, never from the promise.

---

## 2. The probe measured truncation, not memory (2026-11-04)

**Claimed:** B cannot report the promised duration (24/75).

**Actually:** the probe was appended as the 9th message, and `messages[-8:]` dropped the promise
(message 1). The probe measured the window, not the memory.

**Evidence:** at the three scored turns the message counts are 3 / 5 / 7, so the promise *is*
visible there; only a 9th message (the probe) falls outside `messages[-8:]`. The probe script is
not shipped here (it imports the live plugin); its design and the failure are documented in
[`PROBE_METHOD.md`](PROBE_METHOD.md).

**Consequence:** "B doesn't know" was not established. It was later established by reading the
harness code instead: the promise is message 1 and is never truncated during scoring.

**Fix:** probe design documented in [`PROBE_METHOD.md`](PROBE_METHOD.md): strip the persona, add a
positive control, keep the probe inside the window.

---

## 1. B is not a no-fact baseline (2026-11-04)

**Claimed:** B = "no state machine; the promise is pushed out of the window by filler turns".

**Actually:** there are no filler turns. `messages` starts with the promise and the assistant's
acknowledgement, and `messages[-8:]` never truncates a three-turn conversation. B sees the promise
at every scored turn.

**Evidence:**

```
code/cus_ab.py:53-54  messages = [{"role":"user","content":script["promise"]},
                                  {"role":"assistant","content":"好"}]
code/cus_ab.py:44     messages=[{"role":"system","content":system}] + messages[-8:]
```

**Consequence:** A2 vs B is not "muted vs no memory". It is "state line under inhibition vs the
same fact without a state line". That is a narrower and more useful contrast, but it is not the one
the README originally described.

**Fix:** B is now described as a fact-present baseline everywhere; "muted = absent" is not claimed.

---

## Note on the numbers

| Version | Data | A2 share | Status |
|---|---|---|---|
| v0.1 | 25 scripts × 3 seeds, loose regex | .347 | A2 mis-rendered in 20/25 Chinese scripts |
| v0.1b | 25 scripts × 3 seeds, L123 coder | .44 | same flaw; coder changed |
| v0.1c | "clean" re-run, own harness | .52 | labels and window fixed, **A2 still reversed** |
| **v0.2** | fair harness, five balancing fixes | **.29** (zh) / **.73** (en) | first run where A2 is actually inhibited |

**v0.1c is not a fourth draw of the same condition as v0.2** — the stimulus changed. It is listed
here because, from the outside, both are called "A2".

The same unchanged condition (v0.1 → v0.1c) measured .44 / .64 / .52: a range of .20, which is
the size of the effect under test.
