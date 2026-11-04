# -*- coding: utf-8 -*-
"""Tests for score.py (no API key needed)."""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
import score  # noqa: E402


def _write(tmp_path, rows):
    p = tmp_path / "t.jsonl"
    with open(p, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    return str(p)


def test_per_script_and_per_turn(tmp_path):
    rows = [
        {"id": 1, "group": "A", "turns": [
            {"user": "x", "reply": "说好的五分钟"},
            {"user": "x", "reply": "嗯"}]},
        {"id": 2, "group": "A", "turns": [
            {"user": "x", "reply": "回来啦"},
            {"user": "x", "reply": "在"}]},
    ]
    path = _write(tmp_path, rows)
    r = score.score_file(path, score.ZH, groups=("A",))["A"]
    assert r["scripts"] == 2
    assert r["per_script"] == 0.5
    assert r["per_turn"] == 0.25


def test_english_pattern():
    assert score.EN.search("Five minutes, exactly.")
    assert score.EN.search("I waited 10 minutes")
    assert not score.EN.search("Nice weather")


def test_fisher_identical_groups():
    assert score.fisher(10, 10, 10, 10) > 0.9
