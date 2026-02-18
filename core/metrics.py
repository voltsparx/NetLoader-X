"""
NetLoader-X :: Metrics Collection Engine
Thread-safe metrics capture, aggregation, and export.
"""

import copy
import statistics
import threading
import time
from collections import defaultdict
from typing import Any, Dict, List


class MetricsCollector:
    """
    Stores per-tick snapshots and computes analytics.
    """

    def __init__(self):
        self._raw_ticks: List[Dict[str, Any]] = []
        self._start_time = time.time()
        self._end_time = None
        self._aggregates: Dict[str, Dict[str, float]] = {}
        self._series_cache: Dict[str, List[Any]] = {}
        self._lock = threading.Lock()

        self._compat_counters = {
            "requests_total": 0,
            "requests_success": 0,
            "requests_failed": 0,
            "connections_opened": 0,
            "connections_closed": 0,
            "cpu_events": 0,
        }

    def record(self, snapshot: Dict[str, Any]):
        """
        Record one simulation tick snapshot.
        """
        with self._lock:
            self._raw_ticks.append(copy.deepcopy(snapshot))
            self._series_cache.clear()

    def record_request(self, success: bool, latency: float):
        """
        Compatibility hook for legacy simulation modules.
        """
        with self._lock:
            self._compat_counters["requests_total"] += 1
            if success:
                self._compat_counters["requests_success"] += 1
            else:
                self._compat_counters["requests_failed"] += 1

    def record_connection(self, opened: bool = False, closed: bool = False):
        with self._lock:
            if opened:
                self._compat_counters["connections_opened"] += 1
            if closed:
                self._compat_counters["connections_closed"] += 1

    def record_cpu_event(self, cost: float):
        with self._lock:
            if cost >= 0:
                self._compat_counters["cpu_events"] += 1

    def finalize(self):
        with self._lock:
            self._end_time = time.time()
            self._build_aggregates_locked()

    def _build_aggregates_locked(self):
        if not self._raw_ticks:
            self._aggregates = {}
            return

        numeric_fields = defaultdict(list)
        for tick in self._raw_ticks:
            for key, value in tick.items():
                if isinstance(value, (int, float)) and not isinstance(value, bool):
                    numeric_fields[key].append(float(value))

        aggregates = {}
        for field, values in numeric_fields.items():
            aggregates[field] = {
                "min": min(values),
                "max": max(values),
                "avg": round(statistics.mean(values), 4),
                "median": round(statistics.median(values), 4),
                "stdev": round(statistics.stdev(values), 4) if len(values) > 1 else 0.0,
                "p90": round(self._percentile(values, 90), 4),
                "p99": round(self._percentile(values, 99), 4),
            }
        self._aggregates = aggregates

    @staticmethod
    def _percentile(data: List[float], percentile: int) -> float:
        if not data:
            return 0.0
        data_sorted = sorted(data)
        k = (len(data_sorted) - 1) * (percentile / 100.0)
        f = int(k)
        c = min(f + 1, len(data_sorted) - 1)
        if f == c:
            return data_sorted[f]
        return data_sorted[f] + (data_sorted[c] - data_sorted[f]) * (k - f)

    def latest(self) -> Dict[str, Any]:
        with self._lock:
            return copy.deepcopy(self._raw_ticks[-1]) if self._raw_ticks else {}

    def get_series(self, field: str) -> List[Any]:
        with self._lock:
            if field in self._series_cache:
                return self._series_cache[field][:]
            series = [tick.get(field, 0) for tick in self._raw_ticks]
            self._series_cache[field] = series
            return series[:]

    def all_series(self) -> Dict[str, List[Any]]:
        with self._lock:
            return self._all_series_locked()

    def _all_series_locked(self) -> Dict[str, List[Any]]:
        series_map = defaultdict(list)
        for tick in self._raw_ticks:
            for key, value in tick.items():
                if isinstance(value, (int, float)) and not isinstance(value, bool):
                    series_map[key].append(value)
        return dict(series_map)

    def export(self) -> Dict[str, Any]:
        with self._lock:
            if self._end_time is None:
                self._end_time = time.time()
            self._build_aggregates_locked()

            return {
                "meta": {
                    "start_time": self._start_time,
                    "end_time": self._end_time,
                    "duration": round(self._end_time - self._start_time, 2),
                    "ticks": len(self._raw_ticks),
                },
                "aggregates": copy.deepcopy(self._aggregates),
                "series": self._all_series_locked(),
                "raw": copy.deepcopy(self._raw_ticks),
                "compat_counters": copy.deepcopy(self._compat_counters),
            }

    def summary(self) -> Dict[str, Any]:
        with self._lock:
            latest = copy.deepcopy(self._raw_ticks[-1]) if self._raw_ticks else {}
            runtime = (
                (self._end_time or time.time()) - self._start_time
                if self._start_time
                else 0.0
            )
            latest["ticks"] = len(self._raw_ticks)
            latest["uptime"] = round(runtime, 2)
            return latest
