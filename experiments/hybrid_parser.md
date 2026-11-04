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


## v3: two-stage parser (role check, then duration)

| Parser | Precision | Recall | F1 | Treatment |
|---|---|---|---|---|
| regex only | 1.00 | 0.30 | 0.46 | 0.30 |
| hybrid v2 | 0.97 | 0.64 | 0.77 | 0.64 |
| **two-stage v3** | **0.93** | **1.00** | **0.96** | **1.00** |

Stage 1 alone (YES/NO):

```
DeepSeek Flash: P=0.94 R=0.98
Qwen 2.5 1.5B: P=0.71 R=0.90
```

The role-check fixes the English imperative failures ("Wait till I wake up"). The cost is four false positives, all present-state statements rather than promises:

```
我在吃饭 / 我去洗澡了 / 你忙你的 / I'm eating.
```

Gate: precision ≥ 0.90, recall ≥ 0.85, treatment ≥ 0.95 — **passed (0.93 / 1.00 / 1.00)**.

Caveat: stage 1 needs a model strong enough for the role distinction; the 1.5B local model fails precision (0.71). The two-stage run used an API model for iteration speed.


## v3.1: dual-pass stage 1

Pass 1 is the high-recall YES/NO gate. For every YES, pass 2 classifies the message as `USER_LEAVING`, `COMMANDING_ASSISTANT`, or `STATE_DESCRIPTION`; only `USER_LEAVING` becomes a contract.

| Parser | Precision | Recall | F1 | Treatment |
|---|---|---|---|---|
| two-stage v3 | 0.93 | 1.00 | 0.96 | 1.00 |
| **two-stage v3.1 (dual-pass)** | **0.98** | **1.00** | **0.99** | **1.00** |

The dual pass removes the state-description false positives (`我在吃饭`, `I'm eating`) at the cost of one remaining FP (`我去洗澡了`, past tense) and one FN in the stage-1-only check (`我下班了找你`). Full parser: TP 50, FP 1, FN 0.

Stage-1 model check: Qwen 2.5 1.5B gives P=0.71 / R=0.90 on the same set; it is not precise enough for the routing layer. A larger local model was not evaluated for latency reasons.
