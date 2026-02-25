from __future__ import annotations

from typing import Any, Dict

from filters.base import SnapshotFilter


class LatencyCapFilter(SnapshotFilter):
    name = "latency-cap"
    description = "Caps extreme latency outliers for stable chart readability."

    def apply(self, snapshot: Dict[str, Any], state: Dict[str, Any]) -> Dict[str, Any]:
        timeout_ms = float(snapshot.get("timeout_ms", 0.0) or 0.0)
        cap = max(500.0, timeout_ms * 1.2) if timeout_ms > 0 else 10000.0
        snapshot["latency_ms"] = min(float(snapshot.get("latency_ms", 0.0)), cap)
        return snapshot
