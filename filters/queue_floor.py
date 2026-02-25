from __future__ import annotations

from typing import Any, Dict

from filters.base import SnapshotFilter


class QueueFloorFilter(SnapshotFilter):
    name = "queue-floor"
    description = "Suppresses tiny queue oscillations to reduce dashboard noise."

    def apply(self, snapshot: Dict[str, Any], state: Dict[str, Any]) -> Dict[str, Any]:
        queue_depth = int(snapshot.get("queue_depth", 0) or 0)
        floor = 3
        if queue_depth <= floor:
            snapshot["queue_depth"] = 0
        return snapshot
