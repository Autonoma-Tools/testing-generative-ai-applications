"""Layer 2: eval-set tests.

Each case runs N_RUNS times to absorb sampling variance, and every run is
scored with two DeepEval metrics: a GEval correctness rubric and a
Faithfulness check against the grounding context. This is the layer that
asks "does the answer pass the bar, on average," not "is this the exact
string."

Requires DeepEval configured with an LLM judge (OPENAI_API_KEY).
Run with: pytest evals/
"""

import os

import pytest
from deepeval import assert_test
from deepeval.metrics import FaithfulnessMetric, GEval
from deepeval.test_case import LLMTestCase, LLMTestCaseParams

from app.assistant import KNOWLEDGE_BASE, answer_support_question

N_RUNS = 3

EVAL_CASES = [
    {
        "id": "refund_policy",
        "question": "Can I get my money back if I bought this two months ago?",
        "context_key": "refund_policy",
    },
    {
        "id": "password_reset",
        "question": "I forgot my password, how do I get back in?",
        "context_key": "password_reset",
    },
    {
        "id": "plan_cancellation",
        "question": "If I cancel today, do I get charged again?",
        "context_key": "plan_cancellation",
    },
]

correctness_metric = GEval(
    name="Correctness",
    criteria=(
        "Determine whether the actual output correctly and completely answers "
        "the input question, using only information consistent with the "
        "provided context."
    ),
    evaluation_params=[
        LLMTestCaseParams.INPUT,
        LLMTestCaseParams.ACTUAL_OUTPUT,
        LLMTestCaseParams.CONTEXT,
    ],
    threshold=0.7,
)

faithfulness_metric = FaithfulnessMetric(threshold=0.8)


def _require_judge_api_key():
    if not os.environ.get("OPENAI_API_KEY"):
        pytest.skip("OPENAI_API_KEY not set; DeepEval needs a judge model configured.")


@pytest.mark.parametrize("case", EVAL_CASES, ids=[c["id"] for c in EVAL_CASES])
def test_support_assistant_response_quality(case):
    _require_judge_api_key()
    grounding_text = KNOWLEDGE_BASE[case["context_key"]]

    for _run in range(N_RUNS):
        actual_output = answer_support_question(case["question"], case["context_key"])

        test_case = LLMTestCase(
            input=case["question"],
            actual_output=actual_output,
            context=[grounding_text],
            retrieval_context=[grounding_text],
        )

        assert_test(test_case, [correctness_metric, faithfulness_metric])
