# Muted Memory (Retracted / Archived)

> **Status: retracted on 2026-11-05. This repository is an audit record, not a current result.**
>
> The original claim — "a muted memory is indistinguishable from no memory" — is withdrawn. The fair re-run contradicts it. Do not cite the old Finding or the old numbers.
>
> The repository is kept for provenance: it records the four validity hazards that broke the original conclusion. Read [`ERRATA.md`](ERRATA.md) first.

**Archived.** No further updates. The measurement paper is the current output; this repo is the evidence trail.

**Keywords:** AI companion, long-term memory, state machine, prompt suppression, measurement validity, evaluation, reproduction, role-play.

**中文关键词：** AI 陪伴、长期记忆、状态机、提示词抑制、测量效度、可复现性、评测。

---

## Check your own evaluation in four lines

Before trusting any memory-evaluation null, run these. Each takes under an hour and costs nothing.

```
[ ] print the messages actually sent, per condition per turn; diff against the docstring
[ ] any probe needs a positive control: ask it where the answer must be known
[ ] compare the rendered state line against the script's ground truth (label / value / unit)
[ ] before comparing versions, re-run the unchanged condition at least twice
```

These are not stylistic. Each of the four hazards below would have been caught by one of them, and none of them shows up in the output.

---

## What this repository is

1. **A record of four validity hazards**, each demonstrated on the same 25 scripted conversations, each traceable to a code line.
2. **A minimal, self-contained harness** ([`code/run_fair.py`](code/run_fair.py)) that fixes the four hazards and re-runs the four conditions — so the before/after is executable, not just described.

It is **not**: a benchmark, a validated instrument, a human study, or a companion product.

---

## The four hazards

| | Hazard | Evidence in this repo | What it did |
|---|---|---|---|
| **R1** | Construct validity — the condition is not what it says | `code/cus_ab.py` 53–54, 44 | B is described as "promise pushed out of the window"; in fact the promise is message 1 and `messages[-8:]` never truncates it (3/5/7 messages at the three scored turns). **B has the fact.** |
| **R2** | Instrument validity — the tool changes what it measures | `code/score.py`; probe design in `PROBE_METHOD.md` | (a) the default scorer counted "说好 / 等了 / any digit" as a fact recall; (b) a probe appended as message 9 falls outside the window, so it measured truncation, not memory |
| **R3** | Internal validity — the conditions differ by more than one variable | `code/contract.py` 77 (still live here) | `len(return) <= 3` routed **20 of 25 Chinese scripts** to the escalated branch ("ask him pointedly"), i.e. the inhibited condition A2 was replaced by its opposite. English: 0/25, because English returns are longer. Separately, the archived harness rendered the *promised* duration as the *lateness* ("waited about N minutes" for a 5-minute promise = on time); that one is already corrected at `code/cus_ab.py` 61 / 70 / 86. |
| **R4** | Statistical conclusion validity — the estimate does not reproduce | `results/` vs the fair run | The same unchanged condition (A2) measured .44 / .64 / .52 across three runs — a range equal to the effect being tested (.20). |

Full write-up: [`CONDITION_VALIDITY.md`](CONDITION_VALIDITY.md), [`ERRATA.md`](ERRATA.md).

---

## The fair re-run (v0.2)

Self-contained harness, full context window (visible messages `(3, 5, 7)`), all four conditions in one run, state lines identical except for one permission sentence, lateness taken from `late_sec` (not from the promised duration).

| Condition | Chinese (n=24) | English (n=22) |
|---|---|---|
| **A** state + "must mention" | 24/24 | 22/22 |
| **A3** state + "respond naturally" | 17/24 (.71) | 22/22 |
| **A2** state + "do not act upset" | 7/24 (.29) | 16/22 (.73) |
| **B** fact in context, no state line | 8/24 (.33) | 13/22 (.59) |

| Contrast | Chinese | English |
|---|---|---|
| A3 vs A2 (inhibition) | **p = .0087**, RD +.42 | **p = .0211**, RD +.27 |
| A2 vs B (muted ≈ fact-only) | p = 1.00, RD −.04 | p = .53, RD +.14 |
| A3 vs B (state helps when permitted) | p = .0199, RD +.38 | p = .0014, RD +.41 |
| A vs A3 (command on top) | p = .0094, RD +.29 | p = 1.00 (both at ceiling) |

Reading:

- **Inhibition cancels the state line's increment.** A2 lands on the fact-only baseline in both languages.
- **Permitted expression shows the increment.** A3 > B in both.
- **A at 100% is compliance, not mechanism.** It is a manipulation check for "did the instruction get executed".
- **These are single runs**, n=24/22, one model. Not a benchmark.

Dropped (promise not parseable, all four conditions dropped together): zh `id=10`; en `id=6/18/203`.

---

## Quickstart

```bash
pip install openai
export DEEPSEEK_API_KEY=...        # PowerShell: $env:DEEPSEEK_API_KEY="..."

# five minutes: one script, all four conditions, both languages
python code/run_fair.py --limit 1

# full fair run (25 scripts x 3 seeds x 4 conditions x 2 languages)
python code/run_fair.py
```

Output goes to `_fair_out/<lang>_<group>.jsonl` plus `MANIFEST.json`. Scoring:

```bash
python code/score.py --files "_fair_out/zh_*.jsonl" --lang zh --coding l123
```

The archived (v0.1) protocol is still here for comparison (`code/cus_ab.py`, `data/transcripts_*`), but its numbers are **not** comparable to v0.2 — see [`ERRATA.md`](ERRATA.md).

---

## Layout

```
code/
  run_fair.py        self-contained fair harness (v0.2) — no live-plugin import
  cus_ab.py          archived harness (v0.1); keeps the flaws on purpose, as evidence
  contract.py        contract module; line 77 holds the `len(t) <= 3` flaw
  score.py           scorer; --coding regex (old) / l123 (construct-valid)
data/
  scripts_dev_zh.jsonl, scripts_dev_en.jsonl     25 scripts per language
  transcripts_*                                  archived v0.1 runs
  fair/                                          v0.2 fair-run transcripts + manifest
results/                                          v0.1 summaries
docs/quickstart.md     how to run the current protocol
docs/archive/          v0.1 documents, kept with banners (method / applications / production change)
CONDITION_VALIDITY.md  what each condition can and cannot support
ERRATA.md              the four flips, with code references and old/new numbers
PREREGISTRATION.md     plan for the sealed test (spent; see DEVIATIONS.md)
```

---

## Limitations

- One model (`deepseek-flash`), one persona per language. The Chinese fair run uses a private deployment persona; English uses [`data/persona_en.txt`](data/persona_en.txt). Absolute levels will differ with another persona; **within-run comparisons are what this repo is about.**
- The fair run is a single draw; the estimator's run-to-run range is documented in [`ERRATA.md`](ERRATA.md) and is comparable to the effect size.
- `--coding l123` has no human calibration or inter-annotator agreement. It is used only to show that the null is invariant across two coders.
- Scripts are author-written, translated, and synthetic. No human users were involved.
- The production system that motivated this study had its own defect (a promise contract that could never settle). It is described in [`ERRATA.md`](ERRATA.md#5-production-contract-never-fires-2026-11-05) but is not exercised by any code here.

---

## What changed, and why it is the point

Three published-style claims were made and then withdrawn inside one session:

```
v0.1  "inhibited state machine ≈ no memory"   (A2 measured .347, but A2 was mis-rendered)
v0.1b "the command effect is the real driver" (clean run: A vs A2 p=.24 — still unbalanced A2)
v0.2  "inhibition cancels the increment"      (fair run: A3 vs A2 p=.0087 / .0211)
```

Each flip traces to a line of code or a conditioning difference, not to new data. That is the finding this repository exists to record.

---

## Citation

```bibtex
@misc{muted-memory,
  title  = {The Same Null: Four Validity Hazards in AI Companion Memory Evaluation},
  author = {Ge-rio},
  year   = {2026},
  note   = {v0.2, https://github.com/Ge-rio/muted-memory}
}
```

---

## License

MIT. Transcripts are synthetic, generated by the scripted harness — not real user conversations.
