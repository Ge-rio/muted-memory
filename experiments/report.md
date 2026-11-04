# Experiment report

## Setup

- 20 scripts: user promises to return, returns late, two follow-up turns.
- 4 conditions: **A** strong wake, **A2** inhibited, **A3** natural, **B** context only.
- 3 independent runs (`seed1..3`), 20 scripts each, 720 model calls total.
- Model: DeepSeek Flash, temperature 0.8. Judge: DeepSeek Flash, temperature 0.

## Primary result (per-script binary recall)

A script counts as a hit if **any** of its three turns mentions the agreed time.

| Condition | Hits / 60 | Rate | Mean ± sd across seeds |
|---|---|---|---|
| A strong wake | 35 | 58.3% | 0.583 ± 0.076 |
| A3 natural | 24 | 40.0% | 0.400 ± 0.087 |
| A2 inhibited | 17 | 28.3% | 0.283 ± 0.058 |
| B context only | 18 | 30.0% | 0.300 ± 0.132 |

Fisher exact (pooled):

```
A vs A2  p = 0.002
A vs B   p = 0.003
A vs A3  p = 0.067
A3 vs B  p = 0.339
```

## Secondary result (per-turn)

| Condition | Hits / 180 | Rate |
|---|---|---|
| A | 36 | 20.0% |
| A3 | 27 | 15.0% |
| A2 | 23 | 12.8% |
| B | 21 | 11.7% |

The per-turn metric dilutes the effect: a model does not repeat the same fact every turn.

## Blind judge (0–2, 3-seed pooled)

```
A 1.22  >  A3 0.97  >  A2 0.77  >  B 0.65
```

The judge is more lenient than rule matching. Report both.

## Unit choice (disclosed)

Per-script binary recall was chosen **after** seeing per-turn results. It is the better construct for "was the state expressed at all?", but it is not a pre-registered primary outcome. Both units are reported. Treat p-values as exploratory; no multiple-comparison correction is applied.

## Interpretation

- A2 is statistically indistinguishable from B in practice: an active but inhibited state machine looks like no memory.
- A is significantly better than both: when expression is permitted, the state machine becomes observable.
- A3 sits between: natural injection helps, but does not reach significance against B.
- The result is a **mechanism study**, not a benchmark: 20 scripts, one model, one persona.

## What would falsify the claim

If A and A2 were not different on per-script recall, the "expression inhibition" account would fail. The observed difference (35/60 vs 17/60) is the core evidence; replications on other models/personas are the next step.
