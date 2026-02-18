"""
NetLoader-X attack-pattern tuning models.
These tune abstract load behavior; they do not send network traffic.
"""

from dataclasses import dataclass
from typing import Dict


@dataclass(frozen=True)
class PatternTuning:
    name: str
    description: str
    event_multiplier: float
    slow_ratio: float
    retry_bias: float
    jitter: float


PATTERNS: Dict[str, PatternTuning] = {
    "HTTP": PatternTuning(
        name="HTTP",
        description="Steady request pressure",
        event_multiplier=1.0,
        slow_ratio=0.03,
        retry_bias=0.05,
        jitter=0.10,
    ),
    "BURST": PatternTuning(
        name="BURST",
        description="Short, repeated spike windows",
        event_multiplier=1.35,
        slow_ratio=0.05,
        retry_bias=0.08,
        jitter=0.18,
    ),
    "SLOW": PatternTuning(
        name="SLOW",
        description="Connection-hold pressure simulation",
        event_multiplier=0.65,
        slow_ratio=0.45,
        retry_bias=0.03,
        jitter=0.06,
    ),
    "WAVE": PatternTuning(
        name="WAVE",
        description="Periodic demand oscillation",
        event_multiplier=1.1,
        slow_ratio=0.08,
        retry_bias=0.07,
        jitter=0.15,
    ),
    "RETRY": PatternTuning(
        name="RETRY",
        description="Client retry-storm simulation under failures",
        event_multiplier=1.0,
        slow_ratio=0.06,
        retry_bias=0.22,
        jitter=0.12,
    ),
    "CACHE": PatternTuning(
        name="CACHE",
        description="Cache-bypass and expensive-request pressure",
        event_multiplier=1.2,
        slow_ratio=0.12,
        retry_bias=0.10,
        jitter=0.17,
    ),
    "MIXED": PatternTuning(
        name="MIXED",
        description="Multi-vector mixed stress profile",
        event_multiplier=1.28,
        slow_ratio=0.20,
        retry_bias=0.16,
        jitter=0.20,
    ),
}


def get_pattern(name: str) -> PatternTuning:
    return PATTERNS.get(name.upper(), PATTERNS["HTTP"])


class SimulationModel:
    name = "BASE_SIM"
    description = "Base simulation model"
    profile_key = "HTTP"

    def tuning(self) -> PatternTuning:
        return get_pattern(self.profile_key)


class SimSlowloris(SimulationModel):
    name = "SIM_SLOWLORIS"
    description = "Connection-hold pressure simulation"
    profile_key = "SLOW"


class SimHTTPFlood(SimulationModel):
    name = "SIM_HTTP_FLOOD"
    description = "Steady high-rate request simulation"
    profile_key = "HTTP"


class SimICMP(SimulationModel):
    name = "SIM_ICMP"
    description = "Interrupt-style CPU pressure simulation"
    profile_key = "BURST"


class SimRetryStorm(SimulationModel):
    name = "SIM_RETRY_STORM"
    description = "Retry amplification behavior"
    profile_key = "RETRY"


class SimCacheBypass(SimulationModel):
    name = "SIM_CACHE_BYPASS"
    description = "Cache-thrash style expensive request simulation"
    profile_key = "CACHE"


class SimMixedVector(SimulationModel):
    name = "SIM_MIXED_VECTOR"
    description = "Combined wave, slow, and retry behavior"
    profile_key = "MIXED"
