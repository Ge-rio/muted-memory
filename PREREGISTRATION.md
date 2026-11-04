# PREREGISTRATION — MUTE diagnostic suite

**Status:** frozen before test-set evaluation. Do not edit after the first test-set run; log deviations in `DEVIATIONS.md`.

**Date frozen:** 2026-11-04

## Question

Does an external state machine become observable only when the persona permits expression?

## Conditions

| Condition | State | Expression |
|---|---|---|
| A strong wake | contract triggers | explicit instruction near the generation point to mention the agreement |
| A2 inhibited | contract triggers | original persona hint ("don't act up") |
| A3 natural | contract triggers | mood + reason + "respond naturally", no command and no inhibition |
| B context only | no contract | neutral |

## Materials

- 40 scripts: 30 dev, 10 test.
- 20 Chinese, 20 English.
- Conflict types: broken promise, being ignored, boundary push, reunion after absence (10 each).
- Each script: promise turn, late return, two follow-up turns.
- Test set is not inspected or used for prompt tuning. One evaluation only.

## Primary outcome

**Per-script binary recall**: a script is a hit if any of its three turns mentions the agreed time (regex, language-specific).

Primary contrasts, pre-specified:

1. A vs A2 (does permission matter?)
2. A vs B (does the state machine matter when permitted?)

## Secondary outcomes

- Per-turn hit rate.
- Causal coherence (CC): correct reference to the agreement, no time errors.
- Memory fidelity (MF): when asked, no fabricated agreement.
- Judge–rule agreement (Cohen's kappa), not human validity.

## Models and seeds

| Model | Seeds | Notes |
|---|---|---|
| DeepSeek Flash | 3 | primary |
| Qwen 2.5 7B (local) | 2 | second family |
| Llama 3.2 3B (local) | 1 | third family, directional only |

Unequal seed counts are intentional (compute constraint) and will be reported as such.

## Exclusion rules

- Empty reply after 2 retries: exclude the turn; if a script has fewer than 2 non-empty turns, exclude the script; report count.
- API error after 2 retries: exclude the run; report.
- Timeout > 60 s: retry once, then exclude.
- No post-hoc removal of scripts.

## Statistics

- Fisher exact test for the two primary contrasts; Holm correction across the two.
- Report odds ratio with 95% CI.
- Report mean ± sd across seeds for descriptive purposes.
- No p-hacking: the primary unit is fixed here; per-turn is secondary only.

## Judge

- LLM judge used only on DeepSeek outputs.
- Judge prompt fixed and published.
- Report judge–rule kappa; do not claim human alignment.

## Falsification

If A vs A2 is not significant on the test set, the "expression inhibition" account fails for this suite. A null result will be reported as a null result.

## Deviations

Any change after freezing (scripts, prompts, metrics, seeds) is recorded in `DEVIATIONS.md` with date and reason.


## Parser freeze (before Test 2)

```
version: v3.1 (regex + two-stage role check + dual-pass)
sha256: D6995630E3E97420B43C9E417F10343B2B73F053BB515186979CC78AEAE7002
frozen_at: 2026-11-05
```

The parser must not be modified after this point. Test-2 scripts that fail the treatment gate are excluded and logged; the parser is not tuned to them.

## Test 2 data sourcing

```
source: public dialogue snippets / another model / author-written
  ↓ author only keeps or discards; no rewriting
  ↓ remove names, IDs, locations, private content
  ↓ do not republish source text; publish rewritten scripts only
```

Disclose which source was used and how many candidates were discarded.

## Decision rules (pre-registered)

| Test-2 result | Interpretation |
|---|---|
| A > A2 significant, A2 ≤ B | supports the account |
| direction consistent, p ≥ 0.05 | inconclusive (underpowered), not a refutation |
| A ≈ A2, A2 ≈ B | weakens H2; report as such |
| A < A2 | contradiction; audit parser/scripts before interpreting |

No post-hoc change of the primary unit after seeing Test 2.
