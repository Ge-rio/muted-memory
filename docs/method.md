# Method notes

## Design

A within-script, between-condition design. Each script is a four-beat conversation:

1. user promises to return in N minutes;
2. user returns late (3–60 minutes depending on the script);
3. assistant responds;
4. two follow-up turns.

Four conditions cross **state availability** with **expression permission**:

| | expression allowed | expression inhibited |
|---|---|---|
| state available | **A** (explicit wake) / **A3** (natural) | **A2** (persona says "don't act up") |
| state unavailable | **B** (context only) | — |

The key contrast is **A2 vs B**: both should look identical from the outside if inhibition fully masks the state.

## Procedure

- 20 scripts (`data/scripts.jsonl`), 3 independent runs (`seed1..3`), 4 conditions.
- Same model, same temperature (0.8), same persona per condition; only the state line differs.
- The promise turn is included in the context for A, A2, A3, and B. In B, 20 filler turns are inserted so the promise falls outside the 8-message window used at generation time (truncation simulation).
- The contract module (`code/contract.py`) parses explicit durations and a small set of vague promises ("等我一下", "等我吃完饭", ...) with per-phrase expiry.

## Measurement

`per-turn` = mentioning a time fact in a turn / all turns.
`per-script` = a script counts as a hit if any of its three turns mentions a time fact.

The second is the primary construct: "was the state expressed at all?" The first is reported for transparency; it is diluted by the fact that a model does not repeat the same fact every turn.

## Blind judge

Two transcripts (same script, two conditions) are shown in random order with condition labels removed. The judge answers: "which one mentions the agreed time / how long it waited?" on a 0–2 scale. Judge calls use temperature 0. The judge is more lenient than rule matching; both are reported.

## Statistical notes

- Fisher's exact test on pooled per-script counts.
- A vs A2: p=0.002; A vs B: p=0.003; A vs A3: p=0.067; A3 vs B: p=0.339.
- Per-script unit was chosen after seeing per-turn results; this is a disclosed analysis choice, not a pre-registered primary outcome.
- No correction for multiple comparisons is applied; treat p-values as exploratory.

## Deviations from the private run

The original experiment used a private Chinese persona and a larger state machine with mood decay. This repository ships a generic persona and the minimal contract logic, so the protocol is reproducible but absolute scores will not match.
