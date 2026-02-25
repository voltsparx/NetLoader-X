from __future__ import annotations

from typing import Any, Dict

from plugins.base import SimulationPlugin


class ResilienceScorePlugin(SimulationPlugin):
    name = "resilience-score"
    description = "Computes a normalized resilience score from key runtime metrics."

    def apply(self, snapshot: Dict[str, Any], state: Dict[str, Any]) -> Dict[str, Any]:
        error = float(snapshot.get("error_rate", 0.0))
        cpu = float(snapshot.get("cpu_pressure", 0.0))
        queue = float(snapshot.get("queue_depth", 0.0))
        rejected = float(snapshot.get("rejected", 0.0))

        score = 100.0
        score -= min(40.0, error * 120.0)
        score -= min(25.0, cpu * 30.0)
        score -= min(20.0, queue / 15.0)
        score -= min(15.0, rejected / 50.0)
        snapshot["resilience_score"] = int(max(0.0, min(100.0, score)))
        return snapshot
