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

### R1. Explicit duration, or bounded whitelist

The promise must contain one of:

```
① an explicit duration: "五分钟", "20 分钟", "半小时", "in 10 minutes"
② a bounded whitelist: "一会儿", "马上", "很快", "去去就回"
   ↓ only if late_sec <= 1800
```

### R2. Reject open-ended future

```
改天 / 过会儿 / 回头 / 忙完再说 / 以后 / 明天 / 下周 / 月底
someday / later / another day / tomorrow / next week
```

**Not clean. Excluded before parsing.**

### R3. No parser fallback

```
If the only reason a promise becomes a contract is the parser's
default duration (30 minutes), the script is NOT clean.
```

The parser's `_duration()` default is a known source of false positives; Test 2 must not rely on it.

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
