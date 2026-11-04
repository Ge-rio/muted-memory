# Parser evaluation (100 sentences)

## Set

- 100 sentences: 50 positive (promise to leave/return), 50 negative (no promise).
- Chinese 50 (25/25), English 50 (25/25).
- Single annotator (the author); labels are released for audit. No inter-annotator agreement.

## Current parser (regex/phrase table)

| Lang | Precision | Recall | F1 | Treatment rate (TP / positives) |
|---|---|---|---|---|
| zh | 1.00 | 0.44 | 0.61 | 0.44 (11/25) |
| en | 1.00 | 0.16 | 0.28 | 0.16 (4/25) |

No false positives; many false negatives:

```
zh: 我去吃个饭，很快 / 我开完会找你 / 等我打完电话 / 我去取个快递 / 我一会儿就回
en: I'll be back in ten. / Wait till I finish dinner. / I'm taking a shower, back soon. / Let me finish this call.
```

## Implication

The sealed test failed because the treatment was not applied: 8/10 test promises were outside this vocabulary. The parser's high precision is not enough; a treatment rate of 0.44/0.16 cannot support an experiment that requires the state to be triggered.

Gate for the next run: **treatment rate ≥ 0.95** on the parser test set before any dialogue experiment.

## Next

- Hybrid parser: regex/phrase table first, small local model as a fallback with constrained JSON output.
- Target: precision ≥ 0.90, recall ≥ 0.85 on this set; then a new sealed dialogue test set.
- Report per-sentence errors, not only aggregate scores.

## Files

- `data/parser_eval/parser_eval.jsonl`
- `code/parser_eval.py`
- `results/parser_eval.json`
