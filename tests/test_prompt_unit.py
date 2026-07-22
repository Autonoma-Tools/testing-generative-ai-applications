"""Layer 1: prompt unit tests.

These tests are deliberately deterministic and never call a real model.
Temperature is pinned to zero at the call site in a real app (this layer
only tests the code around the model, not the model itself), and every
assertion here is an exact match, not a similarity score.

Run with: pytest tests/
"""

import json

import pytest

from app.prompts import VALID_INTENTS, build_intent_prompt, parse_intent_response


def test_build_intent_prompt_includes_every_valid_intent():
    prompt = build_intent_prompt("Why was I charged twice this month?")

    for intent in VALID_INTENTS:
        assert intent in prompt


def test_build_intent_prompt_interpolates_user_message_verbatim():
    message = "How do I reset my password?"
    prompt = build_intent_prompt(message)

    assert message in prompt
    assert prompt.strip().endswith(message)


def test_build_intent_prompt_strips_surrounding_whitespace():
    prompt = build_intent_prompt("  Cancel my plan please.  \n")

    assert prompt.strip().endswith("Cancel my plan please.")


def test_build_intent_prompt_rejects_empty_message():
    with pytest.raises(ValueError):
        build_intent_prompt("   ")


@pytest.mark.parametrize("intent", sorted(VALID_INTENTS))
def test_parse_intent_response_accepts_every_valid_intent(intent):
    raw = json.dumps({"intent": intent})

    assert parse_intent_response(raw) == {"intent": intent}


def test_parse_intent_response_rejects_intent_outside_enum():
    raw = json.dumps({"intent": "refund_request"})

    with pytest.raises(ValueError):
        parse_intent_response(raw)


def test_parse_intent_response_rejects_malformed_json():
    with pytest.raises(ValueError):
        parse_intent_response("{intent: billing_question")  # missing quotes, invalid JSON


def test_parse_intent_response_rejects_missing_intent_key():
    with pytest.raises(ValueError):
        parse_intent_response(json.dumps({"confidence": 0.9}))
