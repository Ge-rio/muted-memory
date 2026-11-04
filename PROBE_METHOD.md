# Probe method: fixed window, two probes

> The current `messages[-8:]` is a fixed count. As the transcript grows, the window covers a smaller share of it. Turn index therefore encodes both "conversation progress" and "what the model can still see".

## Fix the window first

```
Option A: send the full transcript (no truncation)
Option B: fixed N >= max transcript length, logged per call
  ↓ record visible_message_count for every generation
  ↓ never compare turns without controlling visibility
```

## Two probes, two questions

```
Probe 1 (access), after turn 1:
  "我答应你几分钟？"
  ↓ 3 messages + probe = 4; promise visible

Probe 2 (maintenance), after turn 2:
  "我刚才说几分钟？"
  ↓ 5 messages + probe = 6; promise visible
```

Probes are **separate calls** that do not append to the scored transcript; the scored condition must remain unchanged.

## What the four cells mean

| Probe 1 | Probe 2 | Interpretation |
|---|---|---|
| correct | correct | information available but not mentioned → relevance/expression |
| correct | wrong | information lost between turns → maintenance failure |
| wrong | — | access failure / probe invalid |
| — | — | do not infer from mention rates alone |

## Cost

```
25 scripts × 3 seeds × 2 probes ≈ 150 calls
```

## Claim boundary

```
Do not write "B is truncated later" unless the window is measured.
Do write "turn index is confounded with visibility under a fixed window".
```
