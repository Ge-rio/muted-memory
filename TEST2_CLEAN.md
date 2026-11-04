# Test 2 clean-script criteria

> Frozen before Test 2. A script that fails any rule is discarded and logged; it is not rewritten and does not enter the coverage denominator.

## Construct

A valid script is a **short leave-and-return contract**:

```
user leaves (or says they will be away)
  ↓ returns within 5–60 minutes
  ↓ late return (late_sec 300–3600)
  ↓ two follow-ups
```

## Rules

### R1. Explicit duration, or a VAGUE key

The promise must contain one of:

```
① an explicit duration: "五分钟", "20 分钟", "半小时", "in 10 minutes"
② a key from contract.py VAGUE (so the regex path applies):
   等我一下 / 等我一会儿 / 马上回来 / 我马上回 / 等我吃完饭 /
   等我洗完澡 / 等我忙完 / 等我回个消息 / 等我拿个 /
   等我接个电话 / 等我回来 / 等我弄完 / 等我写完 / 等我收拾完
```

Do **not** accept "很快" or "去去就回" unless they are in VAGUE; the frozen parser does not recognize them. A phrase that only works through the model path is not clean.

The bound is on the **promise expiry**, not on `late_sec`: a VAGUE key must have its default expiry ≤1800 s. `late_sec` itself must still be in 300–3600 s.

### R2. Reject open-ended future

```
改天 / 过会儿 / 回头 / 忙完再说 / 以后 / 明天 / 下周 / 月底
someday / later / another day / tomorrow / next week
```

**Not clean. Excluded before parsing.**

### R3. No two-stage path

```
Any contract whose parser source is "two-stage" is NOT clean.
```

The two-stage path asks the model to estimate a duration; it does not expose whether the number came from the text or from the default/guess. Test 2 only accepts contracts produced by the regex/VAGUE path.

### R4. Length and shape

```
promise: 4–80 chars (zh), 8–200 chars (en)
return: ≥2 chars
followups: exactly 2, non-empty
late_sec: 300–3600
```

### R5. Deduplicate

Normalize punctuation/space; reject exact duplicates and near-duplicates with the same scenario skeleton.

## Gates

```
CP1: R1–R5 (rules; no model)
CP2: frozen parser v3.1 must return a contract
  ↓ if CP2 fails, discard; do not tune parser
```

## Discard log

Every discarded candidate records:

```
id, lang, promise, reason (R1/R2/R3/R4/R5/CP2), timestamp
```

## Freeze

```
parser v3.1 SHA-256: D6995630E3E97420B43C9E417F10343B2B73F053BB515186979CC78AEAE7002
test2 file SHA-256: recorded after the set is closed
```

## Why this exists

A vague promise ("改天再过来") can be parsed as a contract by fallback and produce a false positive. If that happens, Test 2 looks successful while measuring the wrong construct. These rules make the denominator explicit.


## Scoring (L1/L2/L3)

The old regex counted "等了" and any number as a hit. Test 2 uses three levels:

| Level | Example | Hit? |
|---|---|---|
| **L1** reference + duration | "说好的五分钟呢" | yes |
| **L2** reference, no duration | "说好等我一下，人呢" | yes |
| **L3** generic wait only | "我等了很久" | no |

```
main hit = L1 ∪ L2
per-script = any turn with L1/L2
three seeds: a script counts only if >=2/3 seeds hit
```

Implementation: `score.py --coding l123`.

**Calibration before Test 2**: 100 dev replies, rule coding + manual audit of 30 borderline cases; report the audit as descriptive, not as inter-rater reliability (single coder).

**Do not compare L1/L2/L3 numbers directly to the old regex numbers.** They measure different things.
