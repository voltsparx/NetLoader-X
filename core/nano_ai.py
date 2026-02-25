"""
NetLoader-X :: Nano AI Advisor

Small, rule-based assistant that gives safe educational hints.
No model calls, no networking, and no autonomous actions.
"""

from __future__ import annotations

from typing import Any, Dict, List


class NanoAIAdvisor:
    """
    Lightweight advisor for simulation setup and runtime interpretation.
    """

    def advise_config(self, config: Dict[str, Any]) -> List[str]:
        tips: List[str] = []
        threads = int(config.get("threads", 0) or 0)
        duration = int(config.get("duration", 0) or 0)
        rate = int(config.get("rate", 0) or 0)
        jitter = float(config.get("jitter", 0.0) or 0.0)

        if threads > 1200:
            tips.append("High thread count selected; compare with a lower baseline for clearer learning.")
        if rate > 50000:
            tips.append("Rate is very high; monitor queue depth and error rate before increasing further.")
        if duration > 300:
            tips.append("Long duration run detected; export reports to compare early vs late behavior.")
        if jitter < 0.03:
            tips.append("Low jitter may hide bursty behavior. Try 0.05-0.15 for realism.")
        if jitter > 0.30:
            tips.append("High jitter can add noise; use 0.08-0.20 for easier interpretation.")

        if not tips:
            tips.append("Configuration looks balanced for an educational run.")
        return tips

    def risk_score(self, snapshot: Dict[str, Any]) -> int:
        queue = float(snapshot.get("queue_depth", 0.0) or 0.0)
        error = float(snapshot.get("error_rate", 0.0) or 0.0)
        cpu = float(snapshot.get("cpu_pressure", 0.0) or 0.0)
        latency = float(snapshot.get("latency_ms", 0.0) or 0.0)

        score = 0.0
        score += min(40.0, queue / 20.0)
        score += min(30.0, error * 140.0)
        score += min(20.0, cpu * 25.0)
        score += min(10.0, latency / 200.0)
        return int(max(0.0, min(100.0, score)))

    def advise_tick(self, snapshot: Dict[str, Any]) -> str:
        score = self.risk_score(snapshot)
        if score >= 85:
            return "Critical saturation: reduce rate, add queue controls, and inspect retry pressure."
        if score >= 65:
            return "Elevated stress: watch latency trend and error cascade indicators."
        if score >= 40:
            return "Moderate pressure: compare with baseline to identify weak points."
        return "Stable window: useful baseline for contrast against stress scenarios."
