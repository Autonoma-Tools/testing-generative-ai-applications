"""Empty on purpose.

Its presence at the repository root is what makes pytest add the repo root
to sys.path, so `from app.prompts import ...` and `from app.assistant import
...` resolve correctly when running `pytest tests/` or `pytest evals/` from
here.
"""
