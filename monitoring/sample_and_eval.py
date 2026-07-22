"""Layer 4: production monitoring.

This module is a REFERENCE implementation, not a runnable one. It shows the
shape of the sampling + baseline-drift-alert pattern described in the blog
post: sample a percentage of live traffic, re-run it through eval logic
asynchronously (off the user-facing request path), and alert when a rolling
metric drifts too far from its baseline.

Wire `score_faithfulness` to a real metric (e.g. a DeepEval
FaithfulnessMetric call, the same one used in Layer 2's eval-set tests, or
your own judge-model call) before running this in production. Everything
else here (sampling, rolling baselines, drift alerting) works standalone.
"""

from __future__ import annotations

import random
from collections import deque
from dataclasses import dataclass, field
from statistics import mean
from typing import Callable, Deque, List, Optional


@dataclass
class RequestRecord:
    """A single sampled production request/response pair."""

    request_id: str
    prompt: str
    response: str
    context: str
    cost_usd: float
    latency_ms: float


@dataclass
class DriftAlert:
    metric: str
    baseline_value: float
    rolling_average: float
    drift_pct: float

    def __str__(self) -> str:
        direction = "up" if self.drift_pct > 0 else "down"
        return (
            f"[drift-alert] {self.metric} is {direction} "
            f"{abs(self.drift_pct) * 100:.1f}% from baseline "
            f"({self.baseline_value:.3f} -> {self.rolling_average:.3f})"
        )


@dataclass
class MetricBaseline:
    """A rolling baseline for one metric, with a drift-alert threshold.

    `max_drift_pct` is the maximum allowed relative deviation of the current
    rolling average from the baseline before an alert fires. 0.2 means
    "page someone once the rolling average is 20% worse than baseline."
    """

    name: str
    baseline_value: float
    max_drift_pct: float
    window_size: int = 200
    _window: Deque[float] = field(default_factory=deque, repr=False)

    def record(self, value: float) -> Optional[DriftAlert]:
        self._window.append(value)
        while len(self._window) > self.window_size:
            self._window.popleft()

        min_samples = min(20, self.window_size)
        if len(self._window) < min_samples:
            # Not enough samples yet to trust a rolling average.
            return None

        rolling_average = mean(self._window)
        drift_pct = (rolling_average - self.baseline_value) / self.baseline_value

        if abs(drift_pct) > self.max_drift_pct:
            return DriftAlert(
                metric=self.name,
                baseline_value=self.baseline_value,
                rolling_average=rolling_average,
                drift_pct=drift_pct,
            )
        return None


def score_faithfulness(response: str, context: str) -> float:
    """Score how grounded `response` is in `context`, from 0.0 to 1.0.

    NOT IMPLEMENTED BY DESIGN. This is the one call in this module that
    needs a real judge model or metric library wired in before the module
    can run for real; everything around it (sampling, baselines, alerting)
    is a complete reference implementation.
    """
    raise NotImplementedError(
        "Wire score_faithfulness to a real metric (e.g. DeepEval's "
        "FaithfulnessMetric) before running production monitoring."
    )


def sample_request(sample_rate: float, rng: Optional[random.Random] = None) -> bool:
    """Decide whether a given request should be sampled for evaluation.

    Sampling happens on the request path (cheap: one random draw), but the
    actual scoring in `evaluate_sampled_request` should always run
    asynchronously, off the user-facing request path.
    """
    r = rng or random
    return r.random() < sample_rate


def evaluate_sampled_request(
    record: RequestRecord,
    faithfulness_baseline: MetricBaseline,
    cost_baseline: MetricBaseline,
    latency_baseline: MetricBaseline,
    score_fn: Callable[[str, str], float] = score_faithfulness,
) -> List[DriftAlert]:
    """Score one sampled request against all three rolling baselines.

    Returns any DriftAlert objects raised by this sample. Intended to run
    asynchronously (e.g. in a queue worker), never inline in the request path.
    """
    alerts: List[DriftAlert] = []

    faithfulness_score = score_fn(record.response, record.context)
    faithfulness_alert = faithfulness_baseline.record(faithfulness_score)
    if faithfulness_alert:
        alerts.append(faithfulness_alert)

    cost_alert = cost_baseline.record(record.cost_usd)
    if cost_alert:
        alerts.append(cost_alert)

    latency_alert = latency_baseline.record(record.latency_ms)
    if latency_alert:
        alerts.append(latency_alert)

    return alerts
