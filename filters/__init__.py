from __future__ import annotations

from typing import Dict, Type

from filters.base import SnapshotFilter
from filters.error_smooth import ErrorSmoothFilter
from filters.latency_cap import LatencyCapFilter
from filters.queue_floor import QueueFloorFilter


FILTER_REGISTRY: Dict[str, Type[SnapshotFilter]] = {
    LatencyCapFilter.name: LatencyCapFilter,
    ErrorSmoothFilter.name: ErrorSmoothFilter,
    QueueFloorFilter.name: QueueFloorFilter,
}


def available_filters() -> Dict[str, Type[SnapshotFilter]]:
    return dict(FILTER_REGISTRY)
