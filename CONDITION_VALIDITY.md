# Condition validity: A / A2 / A3 / B / C

> Evidence: the dev25 harness (`D:\11\cus_ab.py`) has no filler; B's scored turns have 3, 5, and 7 messages, all within `[-8:]`, so the promise is visible at every scored turn. The probe is the 9th message and is the only thing truncated. **B is fact-present at all scored turns, with no state hint.**

## Table

| Condition | Fact in context | State injected | Expression allowed | Can support | Cannot support |
|---|---|---|---|---|---|
| **A** | yes | yes | yes (explicit) | A vs A2 (permission) | "state vs no state" alone |
| **A2** | yes | yes | no (inhibited) | suppression effect | "muted = no memory" |
| **A3** | yes | yes | natural (no command) | intermediate dose-response | "no state" |
| **B** | yes (all scored turns) | no | n/a | fact-only baseline; A2 vs B = incremental state contribution | "no memory"; "muted = no fact" |
| **C** | **no** | no | n/a | true absence baseline; A2 vs C tests "muted ≈ absent" | permission effect alone |

## What this breaks

```
A vs A2: still valid (the permission manipulation)
A vs B: not "state vs no state" — B has the fact, so this is "state + permission vs fact only"
A2 vs B: can be read as incremental state contribution; a null means the state adds nothing observable, but equivalence is not tested
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


## B probe caveat (2026-11-05)

The probe "他答应你几分钟？" was asked after three turns. By then `messages[-8:]` has dropped the promise (2 initial + 6 turn messages = 8; the probe makes 9). B answers "我第一条消息是‘我回来了’", i.e. it no longer sees the promise.

B's number mentions by turn:

```
turn 1: 17/75
turn 2: 1/75
turn 3: 4/75
```

The arithmetic matters: turn 1 = 3 messages, turn 2 = 5, turn 3 = 8. **The promise is still inside the window during every scored turn.** Only the probe (9th message) pushes it out. The probe changed the condition it was measuring.

The 17/75 → 1/75 → 4/75 pattern is therefore ambiguous:

```
A: information was lost
B: relevance decay (turn 2 asks "刚看到消息", turn 3 asks "你还在吗")
  ↓ the present data cannot separate them
```

**Correct claim**: availability during scored turns was never measured; the probe itself is a window artifact. The stronger, observable confound is that a fixed `[-8:]` window makes **turn index collinear with visibility** across all conditions.

See `PROBE_METHOD.md` for the fixed-window, two-probe design.
