from __future__ import annotations

from typing import Any, Dict

from plugins.base import SimulationPlugin


class TrendLensPlugin(SimulationPlugin):
    name = "trend-lens"
    description = "Annotates per-tick trend deltas for throughput and latency."

    def apply(self, snapshot: Dict[str, Any], state: Dict[str, Any]) -> Dict[str, Any]:
        prev_rps = float(state.get("prev_rps", snapshot.get("requests_per_second", 0.0)))
        prev_latency = float(state.get("prev_latency", snapshot.get("latency_ms", 0.0)))

        cur_rps = float(snapshot.get("requests_per_second", 0.0))
        cur_latency = float(snapshot.get("latency_ms", 0.0))

        snapshot["trend_rps_delta"] = round(cur_rps - prev_rps, 2)
        snapshot["trend_latency_delta"] = round(cur_latency - prev_latency, 2)

        state["prev_rps"] = cur_rps
        state["prev_latency"] = cur_latency
        return snapshot
