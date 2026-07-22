# Testing Generative AI Applications: Where to Start

Companion code for the Autonoma blog post *"Testing Generative AI Applications: Where to Start"* — a runnable example for each of the four testing layers (prompt unit tests, eval sets, behavioral E2E, production monitoring), plus the GitHub Actions workflow that composes the CI-facing layers.

> Companion code for the Autonoma blog post: **[Testing Generative AI Applications: Where to Start](https://getautonoma.com/blog/testing-generative-ai-applications)**

## Requirements

Python 3.10+, Node 20+, an `OPENAI_API_KEY` for the DeepEval judge model (Layer 2 only), and a running app instance (`BASE_URL`) for the Playwright E2E test (Layer 3 only).

## Quickstart

```bash
git clone https://github.com/Autonoma-Tools/testing-generative-ai-applications.git
cd testing-generative-ai-applications

# Layer 1: deterministic prompt unit tests
pip install -r requirements.txt
pytest tests/

# Layer 2: eval-set assertions (requires OPENAI_API_KEY)
export OPENAI_API_KEY=sk-...
pytest evals/

# Layer 3: behavioral E2E (requires a running app instance)
npm install
BASE_URL=http://localhost:3000 npx playwright test e2e/
```

## Project structure

```
.github/workflows/genai-tests.yml   Layer 1 + 2 + 3 CI composition
app/prompts.py                      fake prompt-template + response-parser (Layer 1 subject)
app/assistant.py                    fake support assistant (Layer 2 subject)
tests/test_prompt_unit.py           Layer 1: deterministic prompt unit tests
evals/test_response_quality.py      Layer 2: DeepEval eval-set assertions
e2e/genai-feature.spec.js           Layer 3: behavioral E2E (Playwright)
monitoring/sample_and_eval.py       Layer 4: production sampling + drift-alert reference
examples/                           runnable one-liners for each layer
playwright.config.js                Playwright config for e2e/
package.json                        Node/Playwright dependency for the E2E layer
requirements.txt                    Python dependencies (pytest, deepeval)
```

- `app/` — the fake application modules the tests exercise, standing in for your real LLM-calling code.
- `tests/`, `evals/`, `e2e/`, `monitoring/` — one directory per testing layer from the blog post.
- `examples/` — runnable shell entry points you can execute as-is.

## About

This repository is maintained by [Autonoma](https://getautonoma.com) as reference material for the linked blog post. Autonoma builds autonomous AI agents that plan, execute, and maintain end-to-end tests directly from your codebase.

If something here is wrong, out of date, or unclear, please [open an issue](https://github.com/Autonoma-Tools/testing-generative-ai-applications/issues/new).

## License

Released under the [MIT License](./LICENSE) © 2026 Autonoma Labs.
