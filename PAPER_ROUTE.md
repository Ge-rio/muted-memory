# Two paper routes (decide before more runs)

## Route 1: measurement paper (recommended)

**Confirmatory claim**: the same transcripts can support opposite conclusions depending on three analyst choices.

| Degree of freedom | What changes | Evidence already in hand |
|---|---|---|
| **Condition validity** | B treated as "no memory" vs "fact present, no state hint" | B reproduces the exact promised value; no filler in harness |
| **Manipulation** | "permission" vs "command" | A has "you must mention"; A3 vs A2 (both no command) is p=.256/.321 |
| **Estimator** | any-seed vs >=2/3 | A vs A2: p=.0072 (any-seed) vs p=.110 (>=2/3) |

**Mechanism** (inhibition lowers expression) is reported as directional/exploratory, not confirmatory.

**Title**:

> Muted Memory: A Measurement Confound in AI Companion Memory Evaluation

**No Test 2 required for the confirmatory claim.** Test 2 becomes optional replication.

## Route 2: equivalence claim ("invisible")

**Claim**: A2 is equivalent to B (no state contribution) within a pre-specified margin.

```
Primary: A2 vs B, TOST
n: ~100 scripts/language
C: not needed (B already fixes the fact)
Cost: ~2x scripts, ~2000+ calls
```

**If significant equivalence**: "muted memory" as invisibility.
**If not**: the residual is real; the title must be "attenuated", not "invisible".

## Why not 50 + C + "attenuated"

```
A2 vs B equivalence: CI half-width ~.27 at n=25, ~.19 at n=50
  ↓ cannot fit a ±.15 margin
A3 vs A2: effect .20, n=50 power ~.52
  ↓ likely null/edge
```

**Combination is underpowered for every claim it would make.**

## Decision rule

```
If the goal is a defensible paper now: Route 1.
If the goal is the word "invisible": Route 2, 100/language, TOST.
Do not run 50 scripts and write an equivalence/attenuation claim.
```
