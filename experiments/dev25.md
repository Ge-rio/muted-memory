# Dev-set results (25 scripts × 3 seeds)

Primary analysis on the promise subset. Test set (5 scripts per language) has not been run.

## Chinese (n=75 per condition)

| Condition | Per-script recall | Per-turn |
|---|---|---|
| A strong wake | 0.573 ± 0.061 | 0.200 ± 0.027 |
| A2 inhibited | 0.347 ± 0.023 | 0.133 ± 0.013 |
| A3 natural | 0.440 ± 0.080 | 0.164 ± 0.028 |
| B context only | 0.227 ± 0.061 | 0.098 ± 0.034 |

```
A vs A2: 43/75 vs 26/75, p=0.0085
A vs B : 43/75 vs 17/75, p<0.0001
A3 vs B: 33/75 vs 17/75, p=0.0090
```

## English (n=75 per condition)

| Condition | Per-script recall | Per-turn |
|---|---|---|
| A strong wake | 0.907 ± 0.023 | 0.338 ± 0.008 |
| A2 inhibited | 0.280 ± 0.120 | 0.116 ± 0.063 |
| A3 natural | 0.560 ± 0.069 | 0.204 ± 0.043 |
| B context only | 0.320 ± 0.069 | 0.107 ± 0.023 |

```
A vs A2: 68/75 vs 21/75, p<0.0001
A vs B : 68/75 vs 24/75, p<0.0001
A3 vs B: 42/75 vs 24/75, p=0.0050
```

## Reading

- A2 remains well below A in both languages: permission matters, not just state presence.
- A vs A2 is significant in Chinese (p=0.0085) and stronger in English.
- A3 is intermediate: natural injection helps, but less than an explicit wake.
- The Chinese A/A2 difference is smaller than in the original 20-script set, which is why the larger dev set matters.

## Files

- Scripts: `data/scripts_dev_zh.jsonl`, `data/scripts_dev_en.jsonl` (25 each).
- Sealed test: `data/scripts_test_zh.jsonl`, `data/scripts_test_en.jsonl` (5 each; not run).
- Raw transcripts: `data/transcripts_devzh*.jsonl`, `data/transcripts_en_deven*.jsonl`.
- Scores: `results/dev_zh.json`, `results/dev_en.json`.
