# Controlled experiment: what is held constant, what is varied

## Question

An external state machine can be *triggered* without being *expressed*. Does expression permission change what an outside observer can measure?

## Factors

| Condition | State exists? | Expression allowed? | Prompt at generation point |
|---|---|---|---|
| **A** strong wake | yes | yes, explicitly commanded | "you must naturally mention it" |
| **A3** natural | yes | yes, no command | mood + reason + "respond naturally" |
| **A2** inhibited | yes | no ("don't act up") | original persona hint |
| **B** context only | no | — | neutral |

The key contrast is **A2 vs B**: if inhibition fully masks the state, these two should look the same from the outside.

## Held constant

- 20 scripts (`data/scripts.jsonl`), same order.
- Same persona per language; same style rules.
- Same model and temperature (0.8).
- Same context window (last 8 messages); the promise is included in A/A2/A3/B and pushed out in B by filler turns.
- Same three turns per script (return + two follow-ups).
- Same rule (regex) and same blind-judge prompt; judge temperature 0.
- Same random seed policy: three independent runs, reported as mean ± sd.

## Manipulation checks

- **Contract triggered**: `hint=True` for A/A2/A3 in 19–20/20 scripts (the one miss is "马上", not covered by the parser).
- **State reaches the prompt**: `hint` is injected into the state line; for A it is also appended as the last system message before the user turn.
- **No silent truncation**: the promise turn is present in the context for A/A2/A3/B.

## Metrics

- **Primary (per-script binary recall)**: a script counts as a hit if any of its three turns mentions the agreed time. This matches the construct "was the state expressed at all?"
- **Secondary (per-turn)**: fraction of turns with a time mention. Sensitive to recency; reported for transparency.
- **Blind judge**: two anonymized transcripts, random order, 0–2 on "mentions the agreed time".

## Controls that rule out alternative explanations

| Control | Manipulation | Result | Rules out |
|---|---|---|---|
| **A2 vs B** | state triggered but inhibited vs no state | 17/60 vs 18/60 (zh, p=1.00); 17/60 vs 14/60 (en, p=0.68) | "the state machine has no effect" — it has none *when muted* |
| **A vs B** | permission added | 35/60 vs 18/60 (zh, p=0.003); 55/60 vs 14/60 (en, p<0.001) | "memory is absent" — it surfaces when permitted |
| **A3** | natural, no command | 24/60 (zh), 35/60 (en) | "only explicit commands can surface it" — partially false |
| **Length** | truncate replies to first 15 words / 25 chars | unchanged (55/60, 32/60) | "English is higher because replies are longer" |
| **Priming** | remove "e.g., 'five minutes'" | 57/60 vs 55/60, p=0.72 | "the example phrase is copied" |
| **Persona** | Chinese A with generic short persona | 40/60 vs 35/60, p=0.45 | "the private persona explains the difference" |
| **Model family** | local Meta Llama 3.2 3B | A 13/20, A2 3/20, B 8/20 | "DeepSeek-specific" (direction holds, small n) |

## Confounds not removed

- **Language vs translation**: English scripts are author translations; the prompt wording may be stiffer than the Chinese.
- **Model scale**: Llama 3B is much smaller than DeepSeek; its B condition is noisy.
- **Sample size**: 20 scripts, 3 seeds for DeepSeek; 1 seed for Llama.
- **Unit choice**: per-script was chosen after seeing per-turn results; both are reported and this is disclosed.
- **Judge leniency**: the LLM judge scores higher than the rule; rules are treated as primary for facts.

## Falsification

If A2 and A were not different on per-script recall in a pre-registered replication, the "expression inhibition" account would fail. The current evidence is a mechanism study, not a benchmark.
