"""
NetLoader-X :: Localhost Target Simulator
-------------------------------------------------------
This module simulates server-side behavior under load.

NO networking
NO sockets
NO protocols

It models:
- Request queues
- Worker pools
- Latency growth
- Error probability
- Overload collapse
- Recovery dynamics

Used ONLY for defensive education and resilience testing.

Author  : voltsparx
Contact : voltsparx@gmail.com
-------------------------------------------------------
"""

import time
import random
import threading
from typing import Dict


# =====================================================
# SERVER PROFILE DEFINITIONS
# =====================================================

SERVER_PROFILES = {
    "small-web": {
        "max_workers": 20,
        "queue_limit": 200,
        "base_latency_ms": 40,
        "timeout_ms": 2000,
        "crash_threshold": 0.95
    },
    "api-backend": {
        "max_workers": 50,
        "queue_limit": 500,
        "base_latency_ms": 25,
        "timeout_ms": 1500,
        "crash_threshold": 0.92
    },
    "enterprise-app": {
        "max_workers": 120,
        "queue_limit": 1200,
        "base_latency_ms": 60,
        "timeout_ms": 3000,
        "crash_threshold": 0.98
    }
}


# =====================================================
# LOCALHOST SIMULATOR
# =====================================================

class LocalhostSimulator:
    """
    Simulated server that responds to abstract load events.
    """

    def __init__(self, profile_name: str = "small-web"):
        if profile_name not in SERVER_PROFILES:
            raise ValueError("Unknown server profile")

        self.profile = SERVER_PROFILES[profile_name]

        # Capacity
        self.max_workers = self.profile["max_workers"]
        self.queue_limit = self.profile["queue_limit"]

        # Performance
        self.base_latency = self.profile["base_latency_ms"]
        self.timeout_ms = self.profile["timeout_ms"]

        # State
        self.active_workers = 0
        self.queue_depth = 0
        self.error_rate = 0.0
        self.cpu_pressure = 0.0
        self.is_degraded = False
        self.is_crashed = False

        # Internals
        self.lock = threading.Lock()
        self.last_update = time.time()
        self.recovery_rate = 0.03

    # -------------------------------------------------
    # LOAD INGESTION
    # -------------------------------------------------

    def ingest_load(self, events: int, slow_clients: int = 0):
        """
        Ingest simulated incoming requests.

        events: number of new request events
        slow_clients: long-lived sessions occupying workers
        """
        with self.lock:
            # Slow clients directly consume workers
            self.active_workers += slow_clients

            # Normal requests go into queue
            self.queue_depth += events

            # Hard queue limit
            if self.queue_depth > self.queue_limit:
                overflow = self.queue_depth - self.queue_limit
                self.queue_depth = self.queue_limit
                self.error_rate += overflow * 0.002

    # -------------------------------------------------
    # TICK UPDATE (CORE LOGIC)
    # -------------------------------------------------

    def update(self):
        """
        Advance server state by one tick (~1 second).
        """
        with self.lock:
            now = time.time()
            delta = now - self.last_update
            self.last_update = now

            if self.is_crashed:
                self._recover(delta)
                return

            # Worker assignment
            available = max(self.max_workers - self.active_workers, 0)
            processed = min(self.queue_depth, available)

            self.queue_depth -= processed
            self.active_workers += processed

            # Simulate processing completion
            completed = int(self.active_workers * 0.6)
            self.active_workers = max(self.active_workers - completed, 0)

            # CPU pressure
            self.cpu_pressure = min(
                1.0,
                (self.active_workers + self.queue_depth) /
                (self.max_workers + self.queue_limit)
            )

            # Latency grows non-linearly
            self.latency_ms = self.base_latency * (1 + self.cpu_pressure ** 2)

            # Error probability
            self.error_rate = min(
                1.0,
                self.cpu_pressure * 0.7 +
                (self.queue_depth / self.queue_limit) * 0.5
            )

            # Degraded mode
            self.is_degraded = self.cpu_pressure > 0.7

            # Crash condition
            if self.cpu_pressure >= self.profile["crash_threshold"]:
                self.is_crashed = True
                self.error_rate = 1.0

    # -------------------------------------------------
    # RECOVERY MODEL
    # -------------------------------------------------

    def _recover(self, delta: float):
        """
        Gradual recovery after crash.
        """
        self.queue_depth = max(
            0,
            int(self.queue_depth * (1 - self.recovery_rate))
        )

        self.active_workers = max(
            0,
            int(self.active_workers * (1 - self.recovery_rate))
        )

        self.error_rate = max(
            0.0,
            self.error_rate - self.recovery_rate
        )

        self.cpu_pressure = max(
            0.0,
            self.cpu_pressure - self.recovery_rate
        )

        if self.cpu_pressure < 0.3:
            self.is_crashed = False
            self.is_degraded = False

    # -------------------------------------------------
    # METRICS EXPORT
    # -------------------------------------------------

    def snapshot(self) -> Dict:
        """
        Return current server metrics.
        """
        with self.lock:
            return {
                "queue_depth": self.queue_depth,
                "active_workers": self.active_workers,
                "cpu_pressure": round(self.cpu_pressure, 3),
                "latency_ms": round(self.latency_ms, 2),
                "error_rate": round(self.error_rate, 3),
                "degraded": self.is_degraded,
                "crashed": self.is_crashed
            }

    # -------------------------------------------------
    # RESET
    # -------------------------------------------------

    def reset(self):
        with self.lock:
            self.queue_depth = 0
            self.active_workers = 0
            self.cpu_pressure = 0.0
            self.error_rate = 0.0
            self.is_degraded = False
            self.is_crashed = False
            self.last_update = time.time()