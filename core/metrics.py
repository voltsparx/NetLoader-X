"""
NetLoader-X :: Metrics Collection Engine
-------------------------------------------------------
Responsible for collecting, aggregating and exporting
simulation metrics for reporting and visualization.

Safe, offline, localhost-only simulation metrics.
-------------------------------------------------------
"""

import time
import statistics
from typing import Dict, List, Any
from collections import defaultdict
import copy


class MetricsCollector:
    """
    Stores per-tick metrics and produces
    aggregated analytics for reporting engines.
    """

    def __init__(self):
        self._raw_ticks: List[Dict[str, Any]] = []
        self._start_time = time.time()
        self._end_time = None

        # cached aggregates
        self._aggregates = {}
        self._series_cache = {}

    # --------------------------------------------------
    # RECORDING
    # --------------------------------------------------

    def record(self, snapshot: Dict[str, Any]):
        """
        Record one simulation tick snapshot.
        """
        self._raw_ticks.append(copy.deepcopy(snapshot))

    def finalize(self):
        """
        Called once simulation completes.
        """
        self._end_time = time.time()
        self._build_aggregates()

    # --------------------------------------------------
    # AGGREGATION CORE
    # --------------------------------------------------

    def _build_aggregates(self):
        """
        Build statistical summaries across all ticks.
        """
        if not self._raw_ticks:
            return

        numeric_fields = defaultdict(list)

        for tick in self._raw_ticks:
            for key, value in tick.items():
                if isinstance(value, (int, float)):
                    numeric_fields[key].append(value)

        aggregates = {}

        for field, values in numeric_fields.items():
            if len(values) < 2:
                continue

            aggregates[field] = {
                "min": min(values),
                "max": max(values),
                "avg": round(statistics.mean(values), 3),
                "median": round(statistics.median(values), 3),
                "stdev": round(statistics.stdev(values), 3)
                if len(values) > 2 else 0.0,
                "p90": round(self._percentile(values, 90), 3),
                "p99": round(self._percentile(values, 99), 3)
            }

        self._aggregates = aggregates

    # --------------------------------------------------
    # HELPERS
    # --------------------------------------------------

    def _percentile(self, data: List[float], percentile: int) -> float:
        """
        Percentile calculation without numpy.
        """
        if not data:
            return 0.0

        data_sorted = sorted(data)
        k = (len(data_sorted) - 1) * (percentile / 100)
        f = int(k)
        c = min(f + 1, len(data_sorted) - 1)

        if f == c:
            return data_sorted[int(k)]

        return data_sorted[f] + (data_sorted[c] - data_sorted[f]) * (k - f)

    # --------------------------------------------------
    # TIME SERIES
    # --------------------------------------------------

    def get_series(self, field: str) -> List[Any]:
        """
        Extract time-series data for one metric.
        """
        if field in self._series_cache:
            return self._series_cache[field]

        series = [tick.get(field, 0) for tick in self._raw_ticks]
        self._series_cache[field] = series
        return series

    def all_series(self) -> Dict[str, List[Any]]:
        """
        Return all numeric fields as time series.
        """
        series_map = defaultdict(list)

        for tick in self._raw_ticks:
            for key, value in tick.items():
                if isinstance(value, (int, float)):
                    series_map[key].append(value)

        return dict(series_map)

    # --------------------------------------------------
    # EXPORT INTERFACE
    # --------------------------------------------------

    def export(self) -> Dict[str, Any]:
        """
        Unified export payload for reporters.
        """
        if self._end_time is None:
            self.finalize()

        return {
            "meta": {
                "start_time": self._start_time,
                "end_time": self._end_time,
                "duration": round(self._end_time - self._start_time, 2),
                "ticks": len(self._raw_ticks)
            },
            "aggregates": self._aggregates,
            "series": self.all_series(),
            "raw": self._raw_ticks
        }

    # --------------------------------------------------
    # DEBUG / INSPECTION
    # --------------------------------------------------

    def summary(self) -> Dict[str, Dict[str, float]]:
        """
        Lightweight summary for UI dashboards.
        """
        if not self._aggregates:
            self._build_aggregates()
        return self._aggregates