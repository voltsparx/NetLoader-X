"""
NetLoader-X :: Chaos Engineering Profile
==========================================
A chaos engineering profile that randomly injects different types
of failures to test system resilience.

Supported failure types:
  - Random latency spikes
  - Worker crashes/restarts
  - Queue depth surges
  - Error rate increases
  - Cascading failures

Author  : voltsparx
Contact : voltsparx@gmail.com
"""

import random
from typing import Optional
from enum import Enum


class ChaosFailureType(Enum):
    """Types of chaos failures that can be injected."""
    LATENCY_SPIKE = "latency_spike"        # Sudden latency increase
    WORKER_CRASH = "worker_crash"          # Simulate worker restart
    QUEUE_SURGE = "queue_surge"            # Sudden queue depth increase
    ERROR_SPIKE = "error_spike"            # Error rate spike
    CASCADING = "cascading"                # Cascading failure
    TIMEOUT_STORM = "timeout_storm"        # Many requests timeout


class ChaosInjector:
    """
    Chaos engineering module that randomly injects failures
    into running simulations for resilience testing.
    """

    def __init__(
        self,
        enabled: bool = False,
        fault_rate: float = 0.05,  # 5% of requests affected
        seed: Optional[int] = None
    ):
        """
        Initialize chaos injector.

        Args:
            enabled: Enable chaos injection
            fault_rate: Probability of fault per event (0.0-1.0)
            seed: Random seed for deterministic runs
        """
        self.enabled = enabled
        self.fault_rate = max(0.0, min(1.0, fault_rate))
        self.random = random.Random(seed)

        # Metrics
        self.total_faults_injected = 0
        self.fault_breakdown = {f.value: 0 for f in ChaosFailureType}

    def should_inject(self) -> bool:
        """Determine if a fault should be injected this event."""
        if not self.enabled:
            return False
        return self.random.random() < self.fault_rate

    def inject_fault(self, server_state: dict) -> dict:
        """
        Inject a random chaos fault into server state.

        Args:
            server_state: Current server metrics snapshot

        Returns:
            Modified server state with chaos effects applied
        """
        if not self.should_inject():
            return server_state

        fault_type = self.random.choice(list(ChaosFailureType))
        self.total_faults_injected += 1
        self.fault_breakdown[fault_type.value] += 1

        if fault_type == ChaosFailureType.LATENCY_SPIKE:
            return self._inject_latency_spike(server_state)
        elif fault_type == ChaosFailureType.WORKER_CRASH:
            return self._inject_worker_crash(server_state)
        elif fault_type == ChaosFailureType.QUEUE_SURGE:
            return self._inject_queue_surge(server_state)
        elif fault_type == ChaosFailureType.ERROR_SPIKE:
            return self._inject_error_spike(server_state)
        elif fault_type == ChaosFailureType.CASCADING:
            return self._inject_cascading_failure(server_state)
        elif fault_type == ChaosFailureType.TIMEOUT_STORM:
            return self._inject_timeout_storm(server_state)

        return server_state

    def _inject_latency_spike(self, state: dict) -> dict:
        """
        Simulate sudden latency increase (e.g., GC pause, disk I/O).
        """
        spike_factor = self.random.uniform(2.0, 5.0)
        state["latency_ms"] = state.get("latency_ms", 50) * spike_factor
        return state

    def _inject_worker_crash(self, state: dict) -> dict:
        """
        Simulate worker pool crash/restart.
        Reduces active workers, increases queue depth.
        """
        original_workers = state.get("active_workers", 1)
        reduction = self.random.uniform(0.3, 0.7)
        state["active_workers"] = int(original_workers * (1 - reduction))
        
        # Queue fills due to reduced capacity
        state["queue_depth"] = state.get("queue_depth", 0) + int(original_workers * reduction)
        
        return state

    def _inject_queue_surge(self, state: dict) -> dict:
        """
        Simulate sudden queue depth increase (e.g., slow downstream service).
        """
        surge_factor = self.random.uniform(1.5, 3.0)
        state["queue_depth"] = int(state.get("queue_depth", 0) * surge_factor)
        return state

    def _inject_error_spike(self, state: dict) -> dict:
        """
        Simulate sudden error rate increase.
        """
        current_error_rate = state.get("error_rate", 0.0)
        spike = self.random.uniform(0.05, 0.20)
        state["error_rate"] = min(1.0, current_error_rate + spike)
        return state

    def _inject_cascading_failure(self, state: dict) -> dict:
        """
        Simulate cascading failure:
        - Errors increase
        - Latency increases
        - Queue fills
        - Workers get exhausted
        """
        state["latency_ms"] = state.get("latency_ms", 50) * 2
        state["error_rate"] = min(1.0, state.get("error_rate", 0.0) + 0.10)
        state["queue_depth"] = int(state.get("queue_depth", 0) * 1.5)
        state["active_workers"] = max(1, int(state.get("active_workers", 1) * 0.8))
        return state

    def _inject_timeout_storm(self, state: dict) -> dict:
        """
        Simulate timeout storm: many requests exceed timeout threshold.
        """
        storm_magnitude = self.random.uniform(0.10, 0.30)
        state["error_rate"] = min(1.0, state.get("error_rate", 0.0) + storm_magnitude)
        # Timeouts compound with increased latency
        state["latency_ms"] = state.get("latency_ms", 50) * self.random.uniform(1.5, 2.5)
        return state

    def get_summary(self) -> dict:
        """Get summary of all chaos faults injected."""
        return {
            "total_faults": self.total_faults_injected,
            "breakdown": self.fault_breakdown.copy(),
            "enabled": self.enabled,
            "fault_rate": self.fault_rate
        }

    def reset(self):
        """Reset fault counters."""
        self.total_faults_injected = 0
        self.fault_breakdown = {f.value: 0 for f in ChaosFailureType}


# ==================================================
# CHAOS SCENARIOS (Pre-defined chaos templates)
# ==================================================

class ChaosScenario:
    """Pre-defined chaos engineering scenario."""

    def __init__(
        self,
        name: str,
        description: str,
        fault_rate: float,
        preferred_failures: list
    ):
        self.name = name
        self.description = description
        self.fault_rate = fault_rate
        self.preferred_failures = preferred_failures


# Pre-defined chaos scenarios
CHAOS_SCENARIOS = {
    "light": ChaosScenario(
        name="Light Chaos",
        description="5% fault rate - minor resilience test",
        fault_rate=0.05,
        preferred_failures=[
            ChaosFailureType.LATENCY_SPIKE,
            ChaosFailureType.ERROR_SPIKE
        ]
    ),

    "moderate": ChaosScenario(
        name="Moderate Chaos",
        description="15% fault rate - standard chaos test",
        fault_rate=0.15,
        preferred_failures=[
            ChaosFailureType.LATENCY_SPIKE,
            ChaosFailureType.WORKER_CRASH,
            ChaosFailureType.ERROR_SPIKE,
            ChaosFailureType.QUEUE_SURGE
        ]
    ),

    "severe": ChaosScenario(
        name="Severe Chaos",
        description="30% fault rate - extreme resilience test",
        fault_rate=0.30,
        preferred_failures=[
            ChaosFailureType.LATENCY_SPIKE,
            ChaosFailureType.WORKER_CRASH,
            ChaosFailureType.QUEUE_SURGE,
            ChaosFailureType.ERROR_SPIKE,
            ChaosFailureType.CASCADING,
            ChaosFailureType.TIMEOUT_STORM
        ]
    ),

    "game-day": ChaosScenario(
        name="Game Day Scenario",
        description="Realistic chaos: cascading failures and storms",
        fault_rate=0.10,
        preferred_failures=[
            ChaosFailureType.CASCADING,
            ChaosFailureType.TIMEOUT_STORM,
            ChaosFailureType.WORKER_CRASH
        ]
    )
}


def get_chaos_scenario(name: str) -> Optional[ChaosScenario]:
    """Get pre-defined chaos scenario by name."""
    return CHAOS_SCENARIOS.get(name.lower())


def list_chaos_scenarios():
    """List all available chaos scenarios."""
    print("\nAvailable Chaos Scenarios:")
    print("=" * 60)
    for name, scenario in CHAOS_SCENARIOS.items():
        print(f"\n{name.upper()}")
        print(f"  {scenario.description}")
        print(f"  Fault Rate: {scenario.fault_rate * 100:.1f}%")
        print(f"  Failure Types: {', '.join(f.value for f in scenario.preferred_failures)}")
