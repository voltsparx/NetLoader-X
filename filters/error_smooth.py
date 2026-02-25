from __future__ import annotations

from typing import Any, Dict

from filters.base import SnapshotFilter


class ErrorSmoothFilter(SnapshotFilter):
    name = "error-smooth"
    description = "Applies EWMA smoothing to error rate for easier trend reading."

    def apply(self, snapshot: Dict[str, Any], state: Dict[str, Any]) -> Dict[str, Any]:
        alpha = 0.30
        current = float(snapshot.get("error_rate", 0.0))
        prev = float(state.get("ewma_error", current))
        ewma = (alpha * current) + ((1.0 - alpha) * prev)
        state["ewma_error"] = ewma
        snapshot["error_rate"] = round(max(0.0, min(1.0, ewma)), 4)
        return snapshot
