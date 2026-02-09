"""
NetLoader-X Attack Simulations (SAFE MODELS)
These simulate EFFECTS, not traffic
"""

import time
import random


class SimulationModel:
    name = "BASE_SIM"
    description = "Base simulation model"

    def simulate(self, engine, metrics):
        raise NotImplementedError


class SimSlowloris(SimulationModel):
    name = "SIM_SLOWLORIS"
    description = "Simulates connection exhaustion via slow clients"

    def simulate(self, engine, metrics):
        for _ in range(engine.config.simulated_connections):
            metrics.record_connection(opened=True)
            time.sleep(engine.config.slow_chunk_delay)

        time.sleep(engine.config.slow_hold_time)

        for _ in range(engine.config.simulated_connections):
            metrics.record_connection(closed=True)


class SimHTTPFlood(SimulationModel):
    name = "SIM_HTTP_FLOOD"
    description = "Simulates request rate pressure"

    def simulate(self, engine, metrics):
        while engine.running:
            metrics.record_request(
                success=random.choice([True, True, False]),
                latency=random.uniform(10, 200)
            )
            time.sleep(1 / engine.config.max_rps)


class SimICMPStorm(SimulationModel):
    name = "SIM_ICMP"
    description = "Simulates CPU/interrupt pressure (no packets)"

    def simulate(self, engine, metrics):
        while engine.running:
            metrics.record_cpu_event(
                cost=random.uniform(0.1, 0.5)
            )
            time.sleep(0.01)


class SimConnFlood(SimulationModel):
    name = "SIM_CONN_FLOOD"
    description = "Simulates rapid open/close connections"

    def simulate(self, engine, metrics):
        while engine.running:
            metrics.record_connection(opened=True)
            time.sleep(0.005)
            metrics.record_connection(closed=True)