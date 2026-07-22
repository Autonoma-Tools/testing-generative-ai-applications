"""Deterministic prompt-construction and response-parsing helpers.

This module intentionally contains no model calls. It is the "code around
the model" that Layer 1 (prompt unit tests) exists to cover: prompt
templating and response parsing, both of which are fully deterministic and
should never need an LLM call to test. Pin temperature to zero at the call
site in your real app; that's what makes exact-match assertions on the
model's *behavior* (not just this template) meaningful.
"""

from __future__ import annotations

import json

# The exact, narrow set of intents this classifier is allowed to return.
# Prompt unit tests exist to guarantee the parser never accepts anything
# outside this enum, even if the model itself misbehaves.
VALID_INTENTS = frozenset({
    "billing_question",
    "cancel_subscription",
    "technical_issue",
    "general_inquiry",
})

PROMPT_TEMPLATE = """You are an intent classifier for a customer support system.
Classify the user's message into exactly one of the following intents:
{intent_list}

Respond with a single JSON object of the form {{"intent": "<one_of_the_above>"}}.
Do not include any other text.

User message: {user_message}"""


def build_intent_prompt(user_message: str) -> str:
    """Build the deterministic intent-classification prompt.

    Raises ValueError on empty input so a blank message can never silently
    become "classify nothing" at the model boundary.
    """
    if not user_message or not user_message.strip():
        raise ValueError("user_message must be a non-empty string")

    intent_list = "\n".join(f"- {intent}" for intent in sorted(VALID_INTENTS))
    return PROMPT_TEMPLATE.format(intent_list=intent_list, user_message=user_message.strip())


def parse_intent_response(raw_json: str) -> dict:
    """Parse and validate a model's intent-classification response.

    This is the boundary most genAI features get wrong: trusting that the
    model returned well-formed JSON with a value from the allowed enum.
    Both failure modes raise, so a broken parse never gets silently missed
    downstream.
    """
    try:
        parsed = json.loads(raw_json)
    except json.JSONDecodeError as exc:
        raise ValueError(f"model response was not valid JSON: {raw_json!r}") from exc

    if not isinstance(parsed, dict) or "intent" not in parsed:
        raise ValueError(f"model response missing required 'intent' key: {parsed!r}")

    intent = parsed["intent"]
    if intent not in VALID_INTENTS:
        raise ValueError(
            f"model returned intent {intent!r} outside the allowed enum: {sorted(VALID_INTENTS)}"
        )

    return {"intent": intent}
