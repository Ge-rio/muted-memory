# Probe method: fixed window, persona-free probes, positive control

> A probe is a measuring instrument; it needs its own validity check. Two failure modes already observed: the probe pushed the promise out of the window, and a persona-framed probe can be answered in-character instead of from memory.

## 1. Fix the window

```
Option A: send the full transcript (no truncation)
Option B: fixed N >= max transcript length, logged per call
  ↓ record visible_message_count for every generation
  ↓ never compare turns without controlling visibility
```

## 2. Probe calls are persona-free

```
system: "根据上面的对话，用一个最短的答案回答。"
  ↓ no persona, no style, no state line
  ↓ separate call; does not append to the scored transcript
```

Score automatically: does the answer contain the promised value (5/10/30, etc.)?

## 3. Positive control

Run the same access probe on **A**, whose state line already contains the promise and duration.

```
A access probe ≈ 100% expected
  ↓ if A fails, the probe/scoring is broken; stop
  ↓ do not interpret B until the positive control passes
```

## 4. Two probes

```
Probe 1 (access), after turn 1:
  "我答应你几分钟？"
  ↓ 3 messages + probe = 4; promise visible

Probe 2 (maintenance), after turn 2:
  "我刚才说几分钟？"
  ↓ 5 messages + probe = 6; promise visible
```

## 5. Result table (corrected)

| A access | B access | B maintenance | Interpretation |
|---|---|---|---|
| wrong | — | — | probe invalid; stop |
| correct | wrong | — | B has no usable fact |
| correct | correct | correct | B is a valid fact-present control |
| correct | correct | wrong | fact present at access, lost after turn 2 |

**The cell "access wrong + maintenance correct" is not a model state; it is a probe-validity failure.**

## 6. Pre-register both outcomes

```
If B maintenance is correct:
  B is a valid control; A2 vs B is interpretable again.

If B maintenance is wrong:
  B is valid only early; A2 vs B is comparable only at turn 1.
```

Do **not** pre-write "A2 vs B is incomparable at every turn"; the probe can change that conclusion.

## 7. Harness provenance

The B probe run so far used a **new script** (`b_probe.py`) that reimplements the public `cus_ab.py` chat path; it is not the exact harness that produced dev25.

```
new harness → validates the new harness, not the archived dev25 transcripts
old dev25 "B has fact" remains an inference until rerun on the original harness
```

If the goal is to settle the archived data, rerun B on the original harness (same prompt assembly, same model, same seeds) before interpreting.
