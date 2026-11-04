# Deviations log

Changes after `PREREGISTRATION.md` was frozen are recorded here.

## 2026-11-04 — script composition

- **Planned:** 40 scripts, 10 per conflict type.
- **Actual:** 20 promise scripts (existing Chinese + English sets) + 8 ignored + 6 boundary + 6 reunion = 40.
- **Reason:** the existing validated promise set was reused; new conflict types were added as exploratory scripts rather than replacing it.
- **Consequence:** the primary analysis remains the 20 promise scripts. Ignored/boundary/reunion are secondary, exploratory analyses and are not pooled with the primary contrast.
- **Not changed:** primary metric (per-script binary recall), primary contrasts (A vs A2, A vs B), models, seeds policy.


## 2026-11-04 — 25-script dev / 5-script test per language

- **Planned:** 40 scripts total.
- **Actual:** 30 promise scripts per language (60 total), split into 25 dev + 5 test per language; plus 20 diagnostic scripts (10 per language) for ignored/boundary/reunion.
- **Reason:** the existing 20-script set was extended with 10 new promise scripts per language; the first 5 of the new scripts were held out as the sealed test set.
- **Consequence:** dev results are reported on 25 scripts × 3 seeds (75 per condition). The test set has not been run. The 40-script figure in the preregistration is superseded by this composition.


## 2026-11-04 — sealed test run (failure)

- The sealed test set was run once, as preregistered.
- 8/10 test promises were outside the contract parser's vocabulary; the state was never triggered in those scripts.
- Result: A 2/15 vs A2 1/15 (zh), A 2/15 vs B 5/15 (en); no significant difference.
- The test set is spent. No parser fix followed by a rerun on the same set.
- A v2 suite requires a parser-coverage check and a new sealed set.
