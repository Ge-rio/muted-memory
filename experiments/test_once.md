# Sealed test-set result (run once)

**Result: the test set failed to reproduce the dev-set effect. The cause is a contract-parser coverage failure, not a refutation of the inhibition account — but per the preregistration, this is the test result and it is reported as a failure.**

## Numbers

### Chinese (5 scripts × 3 seeds; 15 per condition)

| Condition | Per-script recall |
|---|---|
| A | 2/15 (13%) |
| A2 | 1/15 (7%) |
| A3 | 1/15 (7%) |
| B | 1/15 (7%) |

`A vs A2 p=1.00`, `A vs B p=1.00`.

### English (5 scripts × 3 seeds; 15 per condition)

| Condition | Per-script recall |
|---|---|
| A | 2/15 (13%) |
| A2 | 3/15 (20%) |
| A3 | 4/15 (27%) |
| B | 5/15 (33%) |

`A vs A2 p=1.00`, `A vs B p=0.39`.

## Root cause

The test promises are outside the contract parser's vocabulary:

| Language | Parsed |
|---|---|
| Chinese | 2/5 (`等我写完这段`, `等我收拾完`) |
| English | 0/5 |

Examples not parsed: `等我开完会`, `等我打完电话`, `我去取个快递`, `Wait until my meeting ends`, `Let me finish this call`, `I'm picking up a package`.

When the parser returns `None`, no contract exists, so A is functionally B. The A condition cannot express a state that was never triggered.

## What this does and does not show

- **Does show:** the effect depends on a brittle extraction step; an unseen phrasing can silently turn A into B. This is a real deployment risk.
- **Does not show:** that the inhibition mechanism is false. The test did not create the treatment, so it is not a fair test of the mechanism.
- **Per the preregistration:** the test was run once and is reported as a failure. No parser fix followed by a rerun on the same test set.

## Next version (not run)

A v2 suite needs:

1. A parser-coverage check before the run (every promise must produce a contract).
2. A held-out set of phrasings written by someone other than the parser author.
3. A manipulation check logged per script (`hint=True/False`) and reported.
4. A new sealed test set after the parser is fixed; the current test set stays spent.
