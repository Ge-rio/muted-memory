# Quickstart

## 1. Install

```bash
pip install openai
```

Python 3.9+.

## 2. Set the API key

```bash
# Linux / macOS
export DEEPSEEK_API_KEY=sk-...
# PowerShell
$env:DEEPSEEK_API_KEY="sk-..."
```

Optional:

```bash
export DEEPSEEK_BASE_URL=https://api.deepseek.com/v1
export DEEPSEEK_MODEL=deepseek-flash
```

## 3. Run the offline tests

No API key needed:

```bash
python -m pytest code/test_contract.py -q
# 5 passed
```

## 4. Run a small experiment

```bash
python code/cus_ab.py --limit 3 --groups A,A2,A3,B --tag demo
```

This creates `results/transcripts_demo.jsonl`.

## 5. Analyze

```bash
python code/cus_analyze.py --dir results --tags demo
```

Output: per-turn and per-script hit rates, Fisher p-values.

## 6. Full reproduction

```bash
for s in 1 2 3; do
  python code/cus_ab.py --limit 20 --groups A,A2,A3,B --tag seed$s
done
python code/cus_analyze.py --dir results --tags seed1,seed2,seed3
```

Expected (v0.1, original model/persona) — **not comparable to v0.2; kept only as a record**:

```
A 0.583, A2 0.283, A3 0.400, B 0.300
A vs A2 p=0.002; A vs B p=0.003
  ↓ in this run A2 was mis-rendered in 20/25 Chinese scripts (see ERRATA.md §4)
```

For the current protocol use [`../code/run_fair.py`](../code/run_fair.py); its expected shape is
in the README's fair-run table. Your absolute numbers will differ: the public persona is generic.

## What each condition does

| Condition | State | Expression |
|---|---|---|
| A | contract triggers | explicit "you must mention it" at the generation point |
| A2 | contract triggers | original inhibiting hint ("do not act up") |
| A3 | contract triggers | mood + reason + "respond naturally" |
| B | no contract | promise falls out of the 8-message window |

## Cost

A 20-script × 4-condition × 3-seed run is ~720 chat calls. At the time of writing this was a few CNY on DeepSeek Flash.


## 7. English replication

```bash
python code/cus_ab_en.py --limit 20 --groups A,A2,A3,B --tag seed1
python code/analyze_en.py
```

The English scripts and persona are in `data/scripts_en.jsonl` and `data/persona_en.txt`.


## 8. Plug in your own agent

```python
from code.base_agent import BaseAgent

class MyAgent(BaseAgent):
    def reply(self, user_text, history):
        return "..."
```

The harness owns the conditions and prompts; the agent only answers the latest turn.
Score any transcript set with:

```bash
python code/score.py --files results/transcripts_*.jsonl --lang zh --out results.json
```
