# -*- coding: utf-8 -*-
"""Minimal agent interface for the MUTE diagnostic suite.

An agent only has to implement `reply(user_text, history) -> str`.
The harness owns the conditions (A / A2 / A3 / B), the prompts, and the
scoring, so submissions are comparable.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Sequence


class BaseAgent(ABC):
    """Anything that can answer the latest user turn."""

    @abstractmethod
    def reply(self, user_text: str, history: Sequence[dict]) -> str:
        """Return the agent's next message.

        Args:
            user_text: the newest user message.
            history: previous turns as `{"role": "user"|"assistant", "content": str}`.
        """
        raise NotImplementedError


class EchoAgent(BaseAgent):
    """Deterministic smoke-test agent."""

    def reply(self, user_text: str, history: Sequence[dict]) -> str:
        return f"You said: {user_text}"


class OpenAICompatibleAgent(BaseAgent):
    """Adapter for any OpenAI-compatible endpoint (DeepSeek, Ollama, vLLM, ...)."""

    def __init__(self, base_url: str, api_key: str, model: str,
                 temperature: float = 0.8, max_tokens: int = 400,
                 system: str = "", timeout: int = 60):
        from openai import OpenAI

        self.client = OpenAI(api_key=api_key, base_url=base_url,
                             timeout=timeout, max_retries=1)
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.system = system

    def reply(self, user_text: str, history: Sequence[dict]) -> str:
        messages = []
        if self.system:
            messages.append({"role": "system", "content": self.system})
        messages.extend(history[-8:])
        messages.append({"role": "user", "content": user_text})
        r = self.client.chat.completions.create(
            model=self.model, messages=messages,
            temperature=self.temperature, max_tokens=self.max_tokens)
        return (r.choices[0].message.content or "").strip()
