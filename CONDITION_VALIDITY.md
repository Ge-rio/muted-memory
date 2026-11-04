# Condition validity: A / A2 / A3 / B / C

> Evidence: public `cus_ab.py` has no filler; B starts with the promise and `messages[-8:]` never truncates it. B transcripts often reproduce the exact promised value ("五分钟", "十分钟", "半小时"). Therefore **B is "fact present, no state hint"**, not "no memory".

## Table

| Condition | Fact in context | State injected | Expression allowed | Can support | Cannot support |
|---|---|---|---|---|---|
| **A** | yes | yes | yes (explicit) | A vs A2 (permission) | "state vs no state" alone |
| **A2** | yes | yes | no (inhibited) | suppression effect | "muted = no memory" |
| **A3** | yes | yes | natural (no command) | intermediate dose-response | "no state" |
| **B** | **yes** | no | n/a | fact available but unprompted; reference | "no memory"; cannot be the zero point for A2 |
| **C** | **no** | no | n/a | true absence baseline; A2 vs C tests "muted ≈ absent" | permission effect alone |

## What this breaks

```
A vs A2: still valid (the permission manipulation)
A vs B: no longer "state machine vs no state" — B knows the fact
A2 vs B: cannot be read as "muted ≈ absent"
  ↓ need A2 vs C
```

## C design

```
C: the promise never appears
  ↓ first user turn: "我去忙了" (no duration, no promise)
  ↓ same return + followups as A/A2/B
  ↓ no state hint
  ↓ A2 vs C = does suppression collapse to a true no-fact baseline?
```

## B manipulation check

After the B transcript, ask:

```
"他答应你几分钟？"
```

If B answers correctly at a high rate, B is confirmed as "fact present"; it is not a no-memory baseline. Report the probe rate separately; do not use it in the main metric.

## Indicator anchor

The model is told the **promised** duration (`mins` from `contract.scan`), not `late_sec`. Therefore score should match the **promise value**, not the actual lateness. A reply saying the actual lateness is not evidence of recall under this injection.

## Doc corrections

- `code/cus_ab.py` docstring: B is "fact in context, no state hint"; remove "truncated after fillers" unless filler is implemented.
- `method.md` / README: same correction; disclose that the intended filler was not implemented in the archived run.
- Pre-register C before Test 2; do not add it after seeing results.
