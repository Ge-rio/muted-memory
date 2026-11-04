# Hybrid parser (Day 2)

Regex/phrase table first; a small model is called only when the regex layer misses. The model is asked for strict JSON (`is_promise`, `duration_mins`, `confidence`); low confidence or malformed output yields no contract (never guessed).

## Results on the 100-sentence parser set

| Parser | Precision | Recall | F1 | Treatment rate |
|---|---|---|---|---|
| regex only | 1.00 | 0.30 | 0.46 | 0.30 |
| hybrid (v1) | 1.00 | 0.38 | 0.55 | 0.38 |
| **hybrid (v2)** | **0.97** | **0.64** | **0.77** | **0.64** |

v2 prompt changes: the user is explicitly the one leaving; event promises count; missing durations are estimated rather than rejected.

## Remaining false negatives (examples)

```
Wait till I wake up.
I'm stepping out, I'll tell you when I'm back.
Wait until I finish this task.
Wait till I get to the office.
I'll get back to you later.
```

These are mostly English event promises phrased as imperatives; the model still reads them as commands to the assistant rather than the user leaving.

## Gate

The preregistered gate is treatment rate ≥ 0.95. v2 is at **0.64**, so it does **not** pass. No new dialogue test should be run with this parser.

## Notes

- The fallback model used here is an API model for iteration speed. A local Qwen 2.5 7B gives the same shape but ~10 s/call on CPU; a full 100-sentence pass is ~15 min.
- The parser set is the dev set for the parser; the dialogue test set remains spent and untouched.
- Next: more event-promise examples and a second-pass check, or a grammar-constrained local model.
