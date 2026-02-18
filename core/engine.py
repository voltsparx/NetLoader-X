"""
NetLoader-X :: Core Simulation Engine
"""

import random
import threading
import time
from typing import Dict

from core.chaos_engineering import ChaosInjector
from core.config import GlobalConfig, SAFETY_CAPS
from core.limiter import SafetyLimiter
from core.metrics import MetricsCollector
from core.profiles import get_profile
from core.scheduler import (
    BurstProfile,
    RampProfile,
    Scheduler,
    SlowClientProfile,
    StairStepProfile,
    WaveProfile,
)
from core.simulations import get_pattern
from targets.localhost import LocalhostSimulator


class Engine:
    """
    Safe simulation engine for abstract load/failure modeling.
    """

    def __init__(self, target_profile: str = "small-web"):
        self.config = GlobalConfig()
        self.server = LocalhostSimulator(target_profile)
        self.limiter = SafetyLimiter()
        self.metrics = MetricsCollector()
        self.random = random.Random()
        self.chaos = ChaosInjector(enabled=False, fault_rate=0.0)

        self.running = threading.Event()
        self.attack_name = f"SIMULATION-{int(time.time())}"
        self.attack_profile = "HTTP"
        self.target_profile = target_profile
        self.threads = 50
        self.duration = 60
        self.tick_interval = 1.0
        self.slow_client_ratio = 0.1
        self.burst_factor = 1.0
        self.current_tick = 0
        self.last_error_rate = 0.0

        self.scheduler = Scheduler(
            RampProfile(base_rate=100, max_rate=500, duration=self.duration, jitter=0.05),
            tick_interval=self.tick_interval,
        )

    def configure(
        self,
        profile: str,
        attack_profile: str,
        threads: int = 50,
        duration: int = 60,
        slow_client_ratio: float = 0.1,
        burst_factor: float = 1.0,
        seed: int = None,
        chaos_enabled: bool = False,
        chaos_fault_rate: float = 0.0,
    ):
        max_clients = SAFETY_CAPS["MAX_VIRTUAL_CLIENTS"]
        max_duration = SAFETY_CAPS["MAX_SIMULATION_TIME_SEC"]

        threads = max(1, min(int(threads), max_clients))
        duration = max(1, min(int(duration), max_duration))

        self.target_profile = profile
        self.server = LocalhostSimulator(profile)
        self.server.reset()

        self.attack_profile = attack_profile.upper()
        self.threads = threads
        self.duration = duration
        self.slow_client_ratio = max(0.0, min(1.0, float(slow_client_ratio)))
        self.burst_factor = max(0.1, min(5.0, float(burst_factor)))
        self.attack_name = f"{self.attack_profile}-{int(time.time())}"
        self.current_tick = 0
        self.last_error_rate = 0.0

        if seed is not None:
            self.random.seed(seed)

        self.chaos = ChaosInjector(
            enabled=bool(chaos_enabled),
            fault_rate=max(0.0, min(1.0, float(chaos_fault_rate))),
            seed=seed,
        )

        self.scheduler = Scheduler(
            self._build_schedule_profile(seed=seed),
            tick_interval=self.tick_interval,
        )
        self.metrics = MetricsCollector()

    def _build_schedule_profile(self, seed: int = None):
        profile = get_profile(self.attack_profile)
        base_rate = max(1, int(self.threads * profile.base_multiplier))
        max_rate = max(base_rate + 1, int(self.threads * profile.max_multiplier))

        if profile.scheduler == "burst":
            return BurstProfile(
                base_rate=base_rate,
                max_rate=max_rate,
                duration=self.duration,
                burst_interval=8,
                burst_length=3,
                jitter=0.10,
                seed=seed,
            )
        if profile.scheduler == "slow":
            return SlowClientProfile(
                base_rate=max(1, int(base_rate * 0.65)),
                max_rate=max_rate,
                duration=self.duration,
                hold_factor=1.6,
                jitter=0.05,
                seed=seed,
            )
        if profile.scheduler == "wave":
            return WaveProfile(
                base_rate=base_rate,
                max_rate=max_rate,
                duration=self.duration,
                period=14,
                jitter=0.08,
                seed=seed,
            )
        if profile.scheduler == "stair":
            return StairStepProfile(
                base_rate=base_rate,
                max_rate=max_rate,
                duration=self.duration,
                steps=6,
                jitter=0.10,
                seed=seed,
            )
        return RampProfile(
            base_rate=base_rate,
            max_rate=max_rate,
            duration=self.duration,
            jitter=0.06,
            seed=seed,
        )

    def tick(self, planned_rate: int = None, scheduler_tick: int = None):
        """
        Simulate one time slice of load.
        """
        scheduled = int(planned_rate if planned_rate is not None else self.threads * 20)
        scheduled = max(1, scheduled)

        pattern = get_pattern(self.attack_profile)
        variation = self.random.uniform(1 - pattern.jitter, 1 + pattern.jitter)
        events = int(scheduled * pattern.event_multiplier * variation * self.burst_factor)
        events = max(1, events)

        retry_events = int(events * pattern.retry_bias * self.last_error_rate)
        events += retry_events

        slow_ratio = max(self.slow_client_ratio, pattern.slow_ratio)
        slow_clients = int(self.threads * slow_ratio * self.random.uniform(0.7, 1.3))

        if self.attack_profile == "MIXED":
            phase = (scheduler_tick or self.current_tick) % 12
            if phase in (3, 4, 9):
                events = int(events * 1.4)
            if phase in (7, 8):
                slow_clients = int(slow_clients * 1.8)

        raw_events = events
        events, slow_clients = self.limiter.limit(events, slow_clients)
        dropped_events = max(0, raw_events - events)

        self.server.ingest_load(events, slow_clients)
        self.server.update()

        snapshot = self.server.snapshot()
        if self.chaos.enabled:
            snapshot = self.chaos.inject_fault(snapshot)

        snapshot["timestamp"] = round(time.time(), 4)
        snapshot["tick"] = self.current_tick
        snapshot["attack_name"] = self.attack_name
        snapshot["attack_profile"] = self.attack_profile
        snapshot["target_profile"] = self.target_profile
        snapshot["threads"] = self.threads
        snapshot["duration"] = self.duration
        snapshot["planned_rate"] = scheduled
        snapshot["generated_events"] = events
        snapshot["dropped_events"] = dropped_events
        snapshot["slow_clients"] = slow_clients
        snapshot["retry_events"] = retry_events
        snapshot["rps"] = snapshot.get("requests_per_second", 0)
        snapshot["latency"] = snapshot.get("latency_ms", 0)
        snapshot["active_clients"] = snapshot.get("active_workers", 0) + snapshot.get(
            "slow_workers", 0
        )
        snapshot["chaos_faults"] = self.chaos.total_faults_injected

        self.metrics.record(snapshot)
        self.last_error_rate = float(snapshot.get("error_rate", 0.0))
        self.current_tick += 1

    def run(self):
        """
        Execute the configured simulation.
        """
        self.running.set()
        self.scheduler.start()
        max_ticks = max(1, int(self.duration / self.tick_interval))

        while self.running.is_set():
            payload = self.scheduler.next_tick()
            if payload is None:
                break
            if payload["tick"] >= max_ticks:
                break
            self.tick(planned_rate=payload["rate"], scheduler_tick=payload["tick"])

        self.scheduler.stop()
        self.running.clear()
        self.metrics.finalize()

    def stop(self):
        self.running.clear()
        self.scheduler.stop()

    def export_metrics(self) -> Dict:
        return self.metrics.export()
