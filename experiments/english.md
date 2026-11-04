# English replication

Same protocol as the Chinese experiment, translated with cultural equivalence rather than literal MT. English persona, English contract module, English judge.

## Rule-based (per-script binary recall, n=60 per condition)

| Condition | Hits / 60 | Rate |
|---|---|---|
| A strong wake | 55 | **91.7%** |
| A3 natural | 35 | 58.3% |
| A2 inhibited | 17 | 28.3% |
| B context only | 14 | 23.3% |

Fisher exact:

```
A vs A2  p < 0.001
A vs B   p < 0.001
A3 vs B  p < 0.001
```

## Blind judge (English prompt, mean over 3 seeds)

```
A 1.83  >  A3 1.45  >  A2 0.87  >  B 0.73
```

## What replicates

- **A2 ≈ B**: an inhibited state machine is again observationally close to no memory.
- **A > A2 and A > B**: permitting expression again produces a large, significant gap.
- **A3 sits between**: natural injection helps, less than an explicit wake.

## What changes

The absolute level is higher in English: A reaches 91.7% per-script (vs 58.3% in Chinese), and A3 reaches 58.3% (vs 40.0%). This suggests the same model is more willing to surface the fact in English, while the inhibition still suppresses it.

This weakens a purely language-specific explanation for prior null results: the null can be reproduced in English by using an inhibited prompt (A2 ≈ B). The mechanism — trigger vs expression — survives translation.

## Caveats

- Same model (DeepSeek Flash), same 20 scripts, one English persona.
- The English scripts are translated by the author with LLM assistance; phrasing may differ in subtle ways.
- Still a pilot-scale mechanism study, not a benchmark.
