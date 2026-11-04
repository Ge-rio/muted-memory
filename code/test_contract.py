# -*- coding: utf-8 -*-
"""Tests for the standalone contract module (no API key needed)."""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
import contract  # noqa: E402


def test_explicit_promise_expires():
    c = contract.scan("等我五分钟", now=1000)
    assert c["promise"] == "等我五分钟"
    assert c["expire_at"] == 1300
    assert c["status"] == "pending"


def test_vague_promise_uses_phrase_duration():
    c = contract.scan("等我吃完饭", now=1000)
    assert c is not None
    assert c["expire_at"] == 2800


def test_late_without_excuse_yields_inhibiting_hint():
    c = contract.scan("等我五分钟", now=1000)
    status, hint = contract.check(c, "我回来了", now=1400)
    assert status == "violated"
    assert "轻不满" in hint
    assert "嘴上别发作" in hint  # this is condition A2


def test_on_time_is_kept():
    c = contract.scan("等我十分钟", now=2000)
    status, hint = contract.check(c, "来了", now=2100)
    assert status == "kept"
    assert hint == ""


def test_good_excuse_resolves():
    c = contract.scan("等我五分钟", now=3000)
    status, hint = contract.check(c, "刚开会，手机静音了", now=3400)
    assert status == "resolved_external"
    assert hint == ""
