"""
NetLoader-X :: Core Simulation Engine
-------------------------------------------------------
Responsible for driving attack simulations against
localhost targets in a safe and educational manner.

Author  : voltsparx
Contact : voltsparx@gmail.com
-------------------------------------------------------
"""

import time
import threading
import random
from typing import Dict
from core.limiter import SafetyLimiter
from core.metrics import MetricsCollector
from core.scheduler import Scheduler
from targets.localhost import LocalhostSimulator

# =====================================================
# SIMULATION ENGINE
# =====================================================

class Engine:
    """
    Simulation engine drives:
    - Load profiles (HTTP, burst, slow clients)
    - Scheduler ticks
    - Metrics collection
    - Safety limiter enforcement
    """

    def __init__(self, target_profile: str = "small-web"):
        self.server = LocalhostSimulator(target_profile)
        self.limiter = SafetyLimiter()
        self.metrics = MetricsCollector()
        
        # Create a default RampProfile for scheduler
        from core.scheduler import RampProfile
        default_profile = RampProfile(
            base_rate=100,
            max_rate=5000,
            duration=60,
            jitter=0.05
        )
        self.scheduler = Scheduler(default_profile)
        
        self.running = threading.Event()
        self.attack_name = "SIMULATION-" + str(int(time.time()))
        self.tick_interval = 1.0  # seconds per tick
        self.attack_profile = "HTTP"  # default
        self.threads = 50
        self.duration = 60
        self.slow_client_ratio = 0.1  # fraction of threads for slow clients
        self.burst_factor = 1.0  # multiplier for burst intensity

        # internal tracking
        self.current_tick = 0

    # -------------------------------------------------
    # CONFIGURATION
    # -------------------------------------------------

    def configure(self, profile: str, attack_profile: str,
                  threads: int = 50, duration: int = 60,
                  slow_client_ratio: float = 0.1,
                  burst_factor: float = 1.0):
        self.server.reset()
        self.attack_profile = attack_profile
        self.threads = threads
        self.duration = duration
        self.slow_client_ratio = slow_client_ratio
        self.burst_factor = burst_factor
        self.attack_name = f"{attack_profile.upper()}-{int(time.time())}"

    # -------------------------------------------------
    # SIMULATION TICK
    # -------------------------------------------------

    def tick(self):
        """
        Simulate one tick (~1 second) of server load.
        """
        # Determine number of requests
        base_events = self.threads
        if self.attack_profile == "HTTP":
            events = int(base_events * random.uniform(0.8, 1.2) * self.burst_factor)
            slow_clients = 0
        elif self.attack_profile == "BURST":
            events = int(base_events * random.uniform(1.2, 1.8) * self.burst_factor)
            slow_clients = int(base_events * self.slow_client_ratio)
        elif self.attack_profile == "SLOW":
            events = int(base_events * 0.5)
            slow_clients = int(base_events * self.slow_client_ratio * 1.5)
        else:
            events = base_events
            slow_clients = int(base_events * self.slow_client_ratio)

        # Apply safety limiter
        events, slow_clients = self.limiter.limit(events, slow_clients)

        # Inject load into server
        self.server.ingest_load(events, slow_clients)

        # Update server state
        self.server.update()

        # Record metrics
        snapshot = self.server.snapshot()
        snapshot["tick"] = self.current_tick
        snapshot["attack_name"] = self.attack_name
        snapshot["attack_profile"] = self.attack_profile
        snapshot["threads"] = self.threads
        snapshot["slow_clients"] = slow_clients
        self.metrics.record(snapshot)

        self.current_tick += 1

    # -------------------------------------------------
    # RUN SIMULATION
    # -------------------------------------------------

    def run(self):
        """
        Execute the simulation for the specified duration.
        """
        self.running.set()
        start_time = time.time()
        end_time = start_time + self.duration

        while self.running.is_set() and time.time() < end_time:
            self.tick()
            time.sleep(self.tick_interval)

        self.running.clear()

    # -------------------------------------------------
    # STOP
    # -------------------------------------------------

    def stop(self):
        self.running.clear()

    # -------------------------------------------------
    # SNAPSHOT EXPORT
    # -------------------------------------------------

    def export_metrics(self) -> Dict:
        """
        Returns a copy of all collected metrics.
        """
        return self.metrics.export()