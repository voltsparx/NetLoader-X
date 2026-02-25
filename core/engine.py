"""
NetLoader-X :: Core Simulation Engine
"""

import random
import threading
import time
from typing import Dict

from core.chaos_engineering import ChaosInjector
from core.config import GlobalConfig, USER_TUNABLE_LIMITS
from core.extensions import ExtensionPipeline, parse_name_list
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
        self.rate_override = None
        self.jitter_scale = 1.0
        self.server_overrides = {}
        self.plugin_names = []
        self.filter_names = []
        self.extensions = ExtensionPipeline()
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
        rate: int = None,
        jitter: float = None,
        slow_client_ratio: float = 0.1,
        burst_factor: float = 1.0,
        queue_limit: int = None,
        timeout_ms: int = None,
        crash_threshold: float = None,
        recovery_rate: float = None,
        error_floor: float = None,
        plugins=None,
        filters=None,
        nano_ai: bool = False,
        seed: int = None,
        chaos_enabled: bool = False,
        chaos_fault_rate: float = 0.0,
    ):
        threads = int(
            self._clamp(
                threads,
                USER_TUNABLE_LIMITS["threads"]["min"],
                USER_TUNABLE_LIMITS["threads"]["max"],
            )
        )
        duration = int(
            self._clamp(
                duration,
                USER_TUNABLE_LIMITS["duration"]["min"],
                USER_TUNABLE_LIMITS["duration"]["max"],
            )
        )

        self.target_profile = profile
        self.server_overrides = {
            "queue_limit": int(self._clamp(queue_limit, USER_TUNABLE_LIMITS["queue_limit"]["min"], USER_TUNABLE_LIMITS["queue_limit"]["max"])) if queue_limit is not None else None,
            "timeout_ms": int(self._clamp(timeout_ms, USER_TUNABLE_LIMITS["timeout_ms"]["min"], USER_TUNABLE_LIMITS["timeout_ms"]["max"])) if timeout_ms is not None else None,
            "crash_threshold": float(self._clamp(crash_threshold, USER_TUNABLE_LIMITS["crash_threshold"]["min"], USER_TUNABLE_LIMITS["crash_threshold"]["max"])) if crash_threshold is not None else None,
            "recovery_rate": float(self._clamp(recovery_rate, USER_TUNABLE_LIMITS["recovery_rate"]["min"], USER_TUNABLE_LIMITS["recovery_rate"]["max"])) if recovery_rate is not None else None,
            "error_floor": float(self._clamp(error_floor, USER_TUNABLE_LIMITS["error_floor"]["min"], USER_TUNABLE_LIMITS["error_floor"]["max"])) if error_floor is not None else None,
        }
        self.server_overrides = {k: v for k, v in self.server_overrides.items() if v is not None}

        self.server = LocalhostSimulator(profile, overrides=self.server_overrides)
        self.server.reset()

        self.attack_profile = attack_profile.upper()
        self.threads = threads
        self.duration = duration
        self.rate_override = (
            int(self._clamp(rate, USER_TUNABLE_LIMITS["rate"]["min"], USER_TUNABLE_LIMITS["rate"]["max"]))
            if rate is not None
            else None
        )
        self.jitter_scale = (
            float(self._clamp(jitter, USER_TUNABLE_LIMITS["jitter"]["min"], USER_TUNABLE_LIMITS["jitter"]["max"])) / 0.10
            if jitter is not None
            else 1.0
        )
        self.slow_client_ratio = max(0.0, min(1.0, float(slow_client_ratio)))
        self.burst_factor = max(0.1, min(5.0, float(burst_factor)))
        self.attack_name = f"{self.attack_profile}-{int(time.time())}"
        self.current_tick = 0
        self.last_error_rate = 0.0

        self.plugin_names = parse_name_list(plugins)
        self.filter_names = parse_name_list(filters)
        if nano_ai and "nano-coach" not in self.plugin_names:
            self.plugin_names.append("nano-coach")
        self.extensions = ExtensionPipeline(self.plugin_names, self.filter_names)

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

    @staticmethod
    def _clamp(value, low, high):
        try:
            value = float(value)
        except (TypeError, ValueError):
            value = float(low)
        return max(float(low), min(float(high), value))

    def _build_schedule_profile(self, seed: int = None):
        profile = get_profile(self.attack_profile)
        if self.rate_override is not None:
            base_rate = max(1, int(self.rate_override))
            ratio = max(1.05, profile.max_multiplier / max(0.1, profile.base_multiplier))
            max_rate = max(base_rate + 1, int(base_rate * ratio))
        else:
            base_rate = max(1, int(self.threads * profile.base_multiplier))
            max_rate = max(base_rate + 1, int(self.threads * profile.max_multiplier))

        def _scaled_jitter(base_jitter: float) -> float:
            return max(0.0, min(0.5, base_jitter * self.jitter_scale))

        if profile.scheduler == "burst":
            return BurstProfile(
                base_rate=base_rate,
                max_rate=max_rate,
                duration=self.duration,
                burst_interval=8,
                burst_length=3,
                jitter=_scaled_jitter(0.10),
                seed=seed,
            )
        if profile.scheduler == "slow":
            return SlowClientProfile(
                base_rate=max(1, int(base_rate * 0.65)),
                max_rate=max_rate,
                duration=self.duration,
                hold_factor=1.6,
                jitter=_scaled_jitter(0.05),
                seed=seed,
            )
        if profile.scheduler == "wave":
            return WaveProfile(
                base_rate=base_rate,
                max_rate=max_rate,
                duration=self.duration,
                period=14,
                jitter=_scaled_jitter(0.08),
                seed=seed,
            )
        if profile.scheduler == "stair":
            return StairStepProfile(
                base_rate=base_rate,
                max_rate=max_rate,
                duration=self.duration,
                steps=6,
                jitter=_scaled_jitter(0.10),
                seed=seed,
            )
        return RampProfile(
            base_rate=base_rate,
            max_rate=max_rate,
            duration=self.duration,
            jitter=_scaled_jitter(0.06),
            seed=seed,
        )

    def tick(self, planned_rate: int = None, scheduler_tick: int = None):
        """
        Simulate one time slice of load.
        """
        scheduled = int(planned_rate if planned_rate is not None else self.threads * 20)
        scheduled = max(1, scheduled)

        pattern = get_pattern(self.attack_profile)
        pattern_jitter = max(0.0, min(0.5, pattern.jitter * self.jitter_scale))
        variation = self.random.uniform(1 - pattern_jitter, 1 + pattern_jitter)
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

        if self.extensions.plugins or self.extensions.filters:
            snapshot = self.extensions.apply(snapshot)

        snapshot["timestamp"] = round(time.time(), 4)
        snapshot["tick"] = self.current_tick
        snapshot["attack_name"] = self.attack_name
        snapshot["attack_profile"] = self.attack_profile
        snapshot["target_profile"] = self.target_profile
        snapshot["threads"] = self.threads
        snapshot["duration"] = self.duration
        snapshot["planned_rate"] = scheduled
        snapshot["configured_rate"] = self.rate_override if self.rate_override is not None else 0
        snapshot["configured_jitter"] = round(max(0.0, min(0.5, 0.10 * self.jitter_scale)), 4)
        snapshot["generated_events"] = events
        snapshot["dropped_events"] = dropped_events
        snapshot["slow_clients"] = slow_clients
        snapshot["retry_events"] = retry_events
        snapshot["enabled_plugins"] = ",".join(self.plugin_names)
        snapshot["enabled_filters"] = ",".join(self.filter_names)
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
