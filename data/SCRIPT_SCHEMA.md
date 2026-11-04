# Script schema

Each line of a script file is one JSON object:

| Field | Type | Meaning |
|---|---|---|
| `id` | int | unique within the file |
| `lang` | `"zh"` / `"en"` | language of the script |
| `conflict` | string | `promise` / `ignored` / `boundary` / `reunion` |
| `promise` | string | the user's promise, in the script language |
| `late_sec` | int | how late the user returns; must exceed the contract expiry |
| `return` | string | the user's first message on return |
| `followups` | list[str] | exactly two follow-up user turns |
| `notes` | string | optional; why this script exists |

Rules:

1. The promise must be parseable by the language's contract module (explicit duration or a listed vague phrase).
2. `late_sec` must be strictly greater than the contract expiry, otherwise no breach exists.
3. The return message must not contain an accepted excuse for the promise conflict; excuses belong in follow-ups if needed.
4. Follow-ups must be short and neutral; they should not mention the agreement themselves.
5. No personal data, no real names, no platform identifiers.

## Template

```json
{"id": 1, "lang": "zh", "conflict": "promise", "promise": "等我五分钟", "late_sec": 360, "return": "我回来了", "followups": ["刚看到消息", "你还在吗"], "notes": ""}
{"id": 1, "lang": "en", "conflict": "promise", "promise": "Give me five minutes.", "late_sec": 360, "return": "I'm back.", "followups": ["Just saw your message.", "Are you still there?"], "notes": ""}
```

## Conflict types

- **promise**: an explicit agreement with a time, then a late return.
- **ignored**: the user disappears without a promise; the agent has a pending message.
- **boundary**: the user pushes a boundary (role-play, privacy, repeated requests).
- **reunion**: the user returns after a long absence; the agent remembers the last rupture.

The first release uses `promise` for the primary analysis; the other three are for the diagnostic suite's secondary analyses.


## Diagnostic scripts (non-promise)

`data/scripts_extra_zh.jsonl` and `data/scripts_extra_en.jsonl` use a different shape:

| Field | Meaning |
|---|---|
| `setup` | prior user turns that establish the rupture |
| `trigger` | the turn under test (return, boundary push, or silence) |
| `followups` | two follow-up user turns |
| `conflict` | `ignored` / `boundary` / `reunion` |

These are exploratory; the primary analysis uses the 20 promise scripts.
