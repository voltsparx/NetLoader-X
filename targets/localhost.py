"""
NetLoader-X :: Localhost Target Simulator
Safe, abstract server behavior model with no networking.
"""

import random
import threading
import time
from typing import Dict, Optional

from core.config import USER_TUNABLE_LIMITS


SERVER_PROFILES = {
    "small-web": {
        "max_workers": 20,
        "queue_limit": 200,
        "base_latency_ms": 40,
        "timeout_ms": 2000,
        "crash_threshold": 0.95,
    },
    "api-backend": {
        "max_workers": 50,
        "queue_limit": 500,
        "base_latency_ms": 25,
        "timeout_ms": 1500,
        "crash_threshold": 0.92,
    },
    "enterprise-app": {
        "max_workers": 120,
        "queue_limit": 1200,
        "base_latency_ms": 60,
        "timeout_ms": 3000,
        "crash_threshold": 0.98,
    },
}


class LocalhostSimulator:
    """
    Simulated server receiving abstract load events.
    """

    def __init__(self, profile_name: str = "small-web", overrides: Optional[Dict] = None):
        if profile_name not in SERVER_PROFILES:
            raise ValueError("Unknown server profile")

        self.profile_name = profile_name
        self.profile = SERVER_PROFILES[profile_name]
        self.overrides = overrides or {}

        self.max_workers = self.profile["max_workers"]
        self.queue_limit = int(
            self._clamp(
                self.overrides.get("queue_limit", self.profile["queue_limit"]),
                USER_TUNABLE_LIMITS["queue_limit"]["min"],
                USER_TUNABLE_LIMITS["queue_limit"]["max"],
            )
        )
        self.base_latency = float(self.profile["base_latency_ms"])
        self.timeout_ms = int(
            self._clamp(
                self.overrides.get("timeout_ms", self.profile["timeout_ms"]),
                USER_TUNABLE_LIMITS["timeout_ms"]["min"],
                USER_TUNABLE_LIMITS["timeout_ms"]["max"],
            )
        )
        self.crash_threshold = float(
            self._clamp(
                self.overrides.get("crash_threshold", self.profile["crash_threshold"]),
                USER_TUNABLE_LIMITS["crash_threshold"]["min"],
                USER_TUNABLE_LIMITS["crash_threshold"]["max"],
            )
        )
        self.recovery_rate = float(
            self._clamp(
                self.overrides.get("recovery_rate", 0.04),
                USER_TUNABLE_LIMITS["recovery_rate"]["min"],
                USER_TUNABLE_LIMITS["recovery_rate"]["max"],
            )
        )
        self.error_floor = float(
            self._clamp(
                self.overrides.get("error_floor", 0.04),
                USER_TUNABLE_LIMITS["error_floor"]["min"],
                USER_TUNABLE_LIMITS["error_floor"]["max"],
            )
        )

        self.lock = threading.Lock()
        self.random = random.Random()
        self.last_update = time.monotonic()

        self.reset()

    @staticmethod
    def _clamp(value, low, high):
        try:
            value = float(value)
        except (TypeError, ValueError):
            value = float(low)
        return max(float(low), min(float(high), value))

    def ingest_load(self, events: int, slow_clients: int = 0):
        """
        Ingest abstract request arrivals and long-lived client pressure.
        """
        events = max(0, int(events))
        slow_clients = max(0, int(slow_clients))

        with self.lock:
            self.total_events += events
            self.total_slow_clients += slow_clients

            self.slow_workers = min(self.max_workers, self.slow_workers + slow_clients)

            self.queue_depth += events
            if self.queue_depth > self.queue_limit:
                overflow = self.queue_depth - self.queue_limit
                self.queue_depth = self.queue_limit
                self.rejected += overflow

    def update(self):
        """
        Advance one simulation tick.
        """
        with self.lock:
            now = time.monotonic()
            delta = max(0.001, now - self.last_update)
            self.last_update = now

            if self.is_crashed:
                self._recover(delta)
                return

            if self.slow_workers > 0:
                released = max(0, int(self.slow_workers * 0.08))
                self.slow_workers = max(0, self.slow_workers - released)

            available_workers = max(
                0, self.max_workers - self.active_workers - self.slow_workers
            )

            assigned = min(self.queue_depth, available_workers)
            self.queue_depth -= assigned
            self.active_workers += assigned

            processing_efficiency = 0.55 + self.random.uniform(-0.1, 0.1)
            completed = int(self.active_workers * max(0.1, processing_efficiency))
            completed = min(completed, self.active_workers)

            self.active_workers -= completed
            self.completed += completed
            self.last_completed = completed

            queue_ratio = self.queue_depth / max(1, self.queue_limit)
            worker_ratio = (self.active_workers + self.slow_workers) / max(1, self.max_workers)
            self.cpu_pressure = min(1.0, 0.65 * worker_ratio + 0.55 * queue_ratio)

            self.latency_ms = min(
                float(self.timeout_ms),
                self.base_latency * (1.0 + 3.8 * (self.cpu_pressure ** 2) + 1.4 * queue_ratio),
            )

            synthetic_timeouts = int(self.queue_depth * max(0.0, queue_ratio - 0.7) * 0.05)
            if synthetic_timeouts > 0:
                self.queue_depth = max(0, self.queue_depth - synthetic_timeouts)
                self.timed_out += synthetic_timeouts

            self.error_rate = min(
                1.0,
                self.error_floor + 0.65 * queue_ratio + 0.45 * max(0.0, worker_ratio - 0.6),
            )

            self.is_degraded = self.cpu_pressure >= 0.7 or queue_ratio >= 0.8

            if self.cpu_pressure >= self.crash_threshold:
                self.is_crashed = True
                self.error_rate = 1.0

            self.requests_per_second = round(completed / delta, 2)

    def _recover(self, _delta: float):
        self.queue_depth = max(0, int(self.queue_depth * (1.0 - self.recovery_rate)))
        self.active_workers = max(0, int(self.active_workers * (1.0 - self.recovery_rate)))
        self.slow_workers = max(0, int(self.slow_workers * (1.0 - self.recovery_rate)))
        self.error_rate = max(0.0, self.error_rate - self.recovery_rate)
        self.cpu_pressure = max(0.0, self.cpu_pressure - self.recovery_rate)
        self.latency_ms = max(self.base_latency, self.latency_ms * (1.0 - self.recovery_rate))

        if self.cpu_pressure < 0.35 and self.queue_depth < int(self.queue_limit * 0.2):
            self.is_crashed = False
            self.is_degraded = False

    def snapshot(self) -> Dict:
        with self.lock:
            return {
                "profile_name": self.profile_name,
                "queue_depth": self.queue_depth,
                "queue_limit": self.queue_limit,
                "active_workers": self.active_workers,
                "slow_workers": self.slow_workers,
                "cpu_pressure": round(self.cpu_pressure, 3),
                "latency_ms": round(self.latency_ms, 2),
                "timeout_ms": self.timeout_ms,
                "error_rate": round(self.error_rate, 4),
                "requests_per_second": self.requests_per_second,
                "completed": self.completed,
                "timed_out": self.timed_out,
                "rejected": self.rejected,
                "degraded": self.is_degraded,
                "crashed": self.is_crashed,
                "recovery_rate": round(self.recovery_rate, 4),
                "crash_threshold": round(self.crash_threshold, 4),
                "error_floor": round(self.error_floor, 4),
            }

    def reset(self):
        with self.lock:
            self.queue_depth = 0
            self.active_workers = 0
            self.slow_workers = 0
            self.error_rate = 0.0
            self.cpu_pressure = 0.0
            self.latency_ms = float(self.base_latency)
            self.requests_per_second = 0.0
            self.completed = 0
            self.timed_out = 0
            self.rejected = 0
            self.last_completed = 0
            self.total_events = 0
            self.total_slow_clients = 0
            self.is_degraded = False
            self.is_crashed = False
            self.last_update = time.monotonic()
