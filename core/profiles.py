"""
NetLoader-X profile catalog.
Profiles define scheduler and behavior defaults for abstract simulations.
"""

from dataclasses import dataclass
from typing import Dict


@dataclass(frozen=True)
class AttackProfile:
    key: str
    label: str
    scheduler: str
    base_multiplier: float
    max_multiplier: float
    default_duration: int


PROFILE_CATALOG: Dict[str, AttackProfile] = {
    "HTTP": AttackProfile(
        key="HTTP",
        label="HTTP Steady",
        scheduler="ramp",
        base_multiplier=16.0,
        max_multiplier=32.0,
        default_duration=60,
    ),
    "BURST": AttackProfile(
        key="BURST",
        label="Burst Spikes",
        scheduler="burst",
        base_multiplier=14.0,
        max_multiplier=42.0,
        default_duration=60,
    ),
    "SLOW": AttackProfile(
        key="SLOW",
        label="Slow Connection Hold",
        scheduler="slow",
        base_multiplier=8.0,
        max_multiplier=22.0,
        default_duration=60,
    ),
    "WAVE": AttackProfile(
        key="WAVE",
        label="Wave Demand",
        scheduler="wave",
        base_multiplier=10.0,
        max_multiplier=30.0,
        default_duration=75,
    ),
    "RETRY": AttackProfile(
        key="RETRY",
        label="Retry Storm",
        scheduler="burst",
        base_multiplier=12.0,
        max_multiplier=40.0,
        default_duration=75,
    ),
    "CACHE": AttackProfile(
        key="CACHE",
        label="Cache Bypass",
        scheduler="wave",
        base_multiplier=11.0,
        max_multiplier=34.0,
        default_duration=75,
    ),
    "MIXED": AttackProfile(
        key="MIXED",
        label="Mixed Vector",
        scheduler="stair",
        base_multiplier=13.0,
        max_multiplier=45.0,
        default_duration=90,
    ),
    "SPIKE": AttackProfile(
        key="SPIKE",
        label="Flash Spike",
        scheduler="burst",
        base_multiplier=18.0,
        max_multiplier=56.0,
        default_duration=60,
    ),
    "BROWNOUT": AttackProfile(
        key="BROWNOUT",
        label="Brownout Drift",
        scheduler="slow",
        base_multiplier=9.0,
        max_multiplier=24.0,
        default_duration=75,
    ),
    "RECOVERY": AttackProfile(
        key="RECOVERY",
        label="Recovery Curve",
        scheduler="stair",
        base_multiplier=10.0,
        max_multiplier=28.0,
        default_duration=80,
    ),
}


def get_profile(name: str) -> AttackProfile:
    return PROFILE_CATALOG.get(name.upper(), PROFILE_CATALOG["HTTP"])


class BaseProfile:
    name = "BASE"
    description = ""
    profile_key = "HTTP"


class HTTPSteady(BaseProfile):
    name = "HTTP_STEADY"
    description = "Constant request pressure"
    profile_key = "HTTP"


class HTTPBurst(BaseProfile):
    name = "HTTP_BURST"
    description = "Short bursts of traffic"
    profile_key = "BURST"


class SlowClient(BaseProfile):
    name = "SLOW_CLIENT"
    description = "Long-lived connection simulation"
    profile_key = "SLOW"
