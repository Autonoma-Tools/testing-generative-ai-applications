"""Fake support assistant used by the Layer 2 eval-set tests.

In a real app this module would call an LLM. Here it's a small,
deterministic, context-grounded responder so the eval-set tests in this
repo run against something concrete. You still need a judge model
configured (OPENAI_API_KEY) for DeepEval's own metrics, since GEval and
Faithfulness both score with an LLM-as-judge, independent of how the
assistant itself is implemented.
"""

from __future__ import annotations

KNOWLEDGE_BASE = {
    "refund_policy": (
        "Refunds are available within 30 days of purchase. After 30 days, "
        "we offer account credit instead of a cash refund."
    ),
    "password_reset": (
        "Users can reset their password from the login screen by selecting "
        "'Forgot password' and following the emailed link, which expires "
        "after 1 hour."
    ),
    "plan_cancellation": (
        "Subscriptions can be canceled anytime from Account > Billing. "
        "Cancellation takes effect at the end of the current billing period; "
        "there is no early-termination fee."
    ),
}


def answer_support_question(question: str, context_key: str) -> str:
    """Answer a support question, grounded strictly in the given context.

    Raises KeyError for an unknown context_key rather than guessing, so a
    caller can never silently receive an ungrounded answer.
    """
    if context_key not in KNOWLEDGE_BASE:
        raise KeyError(f"no knowledge base entry for context_key={context_key!r}")

    context = KNOWLEDGE_BASE[context_key]
    return f"Based on our policy: {context}"
