# Activation change in a real deployment

The study isolates one line. In the deployed companion, the contract hint originally read:

```text
【轻不满】他说好的「{promise}」超时了，心里不太舒服，嘴上别发作
```

After the experiment it was changed to:

```text
【轻不满】他说好的「{promise}」超时了，心里不太舒服；可以自然提一句，别报时，也别闹
```

This keeps the persona (short, slightly proud, not clingy) but removes the behavioral inhibition that made the state unobservable.

The public `code/contract.py` keeps the **original inhibiting wording**, because it is condition A2 in the experiment. If you want the post-experiment behavior, replace `check()`'s last return with the second string above.

Regression test (in the private deployment) asserts:

```python
assert "可以自然提一句" in hint
assert "别报时" in hint
assert "嘴上别发作" not in hint
```
