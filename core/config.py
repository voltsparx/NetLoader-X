"""
NetLoader-X
--------------------------------------------------
Simulation Configuration & Safety Caps

This module defines:
- Global simulation limits
- Hard safety enforcement (no real traffic)
- Default profiles & tunables
- Output/reporting behavior
- Tool metadata

Author  : voltsparx
Contact : voltsparx@gmail.com
License : Educational / Defensive Simulation Only
--------------------------------------------------
"""

from dataclasses import dataclass, field
from typing import Dict, List
import os
import datetime

# ==================================================
# TOOL METADATA
# ==================================================

TOOL_NAME = "NetLoader-X"
TOOL_TAGLINE = "Defensive Load & Failure Simulation Framework"
TOOL_VERSION = "1.0.0-sim"
AUTHOR = "voltsparx"
CONTACT = "voltsparx@gmail.com"

# ==================================================
# HARD SAFETY CAPS (NON-NEGOTIABLE)
# ==================================================
# These exist to guarantee this tool CANNOT be
# repurposed into a real attack framework.

SAFETY_CAPS = {
    "ALLOW_NETWORK_IO": False,        # Absolutely no sockets
    "ALLOW_EXTERNAL_TARGETS": False,  # No IPs, no domains
    "ALLOW_RAW_TRAFFIC": False,       # No packets, ever
    "MAX_SIMULATION_TIME_SEC": 3600,  # 1 hour max
    "MAX_VIRTUAL_CLIENTS": 100_000,   # Abstract entities only
    "MAX_EVENTS_PER_SECOND": 1_000_000,
    "FORCE_LOCAL_MODE": True,
}

# ==================================================
# OUTPUT & REPORTING
# ==================================================

BASE_OUTPUT_DIR = "outputs"

DEFAULT_REPORT_FORMATS = [
    "csv",
    "json",
    "html"
]

HTML_REPORT_SETTINGS = {
    "theme": "blue",
    "include_graphs": True,
    "include_summary": True,
    "include_timeline": True,
    "graph_backend": "plotly",   # conceptual, not imported here
}

# ==================================================
# SIMULATION ENGINE DEFAULTS
# ==================================================

ENGINE_DEFAULTS = {
    "tick_resolution_ms": 10,      # Discrete event resolution
    "random_seed": None,           # Deterministic if set
    "enable_jitter": True,
    "jitter_percent": 5.0,
    "log_every_n_ticks": 100,
}

# ==================================================
# RATE & LOAD LIMITER DEFAULTS
# ==================================================

LIMITER_DEFAULTS = {
    "max_virtual_rps": 50_000,
    "ramp_up_seconds": 30,
    "ramp_down_seconds": 20,
    "burst_multiplier": 2.0,
    "cooldown_seconds": 15,
}

# ==================================================
# FAKE SERVER BEHAVIOR MODEL
# ==================================================

SERVER_MODEL_DEFAULTS = {
    "worker_pool_size": 256,
    "max_queue_depth": 10_000,
    "base_latency_ms": 50,
    "latency_growth_factor": 1.15,
    "timeout_threshold_ms": 5_000,
    "error_rate_base": 0.01,
    "error_rate_growth": 1.2,
    "enable_backpressure": True,
}

# ==================================================
# ADVANCED SIMULATION PROFILES
# ==================================================

@dataclass
class SimulationProfile:
    """
    Describes a *behavioral* traffic pattern.
    No networking. Only abstract event generation.
    """
    name: str
    description: str
    base_clients: int
    request_rate: int
    variability: float
    long_lived_ratio: float
    burst_chance: float
    burst_multiplier: float
    educational_notes: List[str] = field(default_factory=list)


PROFILES: Dict[str, SimulationProfile] = {
    "steady_load": SimulationProfile(
        name="steady_load",
        description="Constant, predictable load pattern",
        base_clients=1_000,
        request_rate=5_000,
        variability=0.05,
        long_lived_ratio=0.0,
        burst_chance=0.0,
        burst_multiplier=1.0,
        educational_notes=[
            "Represents normal baseline traffic",
            "Useful for capacity planning"
        ],
    ),

    "burst_traffic": SimulationProfile(
        name="burst_traffic",
        description="Sudden spikes in virtual demand",
        base_clients=2_000,
        request_rate=8_000,
        variability=0.2,
        long_lived_ratio=0.1,
        burst_chance=0.3,
        burst_multiplier=3.0,
        educational_notes=[
            "Models flash crowd behavior",
            "Shows queue growth & latency amplification"
        ],
    ),

    "slow_client_sim": SimulationProfile(
        name="slow_client_sim",
        description="Long-lived sessions occupying server resources",
        base_clients=500,
        request_rate=1_000,
        variability=0.1,
        long_lived_ratio=0.7,
        burst_chance=0.05,
        burst_multiplier=1.5,
        educational_notes=[
            "Demonstrates worker exhaustion effects",
            "Explains why connection limits matter"
        ],
    ),
}

# ==================================================
# CONFIG FILE SUPPORT
# ==================================================

def generate_run_id() -> str:
    """Generate a unique simulation run ID."""
    return datetime.datetime.utcnow().strftime("run_%Y%m%d_%H%M%S")


def ensure_output_dirs(run_id: str) -> str:
    """
    Create output directory tree for a simulation run.
    """
    base = os.path.join(BASE_OUTPUT_DIR, run_id)
    os.makedirs(base, exist_ok=True)

    for fmt in DEFAULT_REPORT_FORMATS:
        os.makedirs(os.path.join(base, fmt), exist_ok=True)

    return base


# ==================================================
# VALIDATION HELPERS
# ==================================================

def validate_safety():
    """
    Enforce non-negotiable safety constraints.
    This should be called at startup.
    """
    if SAFETY_CAPS["ALLOW_NETWORK_IO"]:
        raise RuntimeError("Safety violation: Network I/O is disabled.")

    if SAFETY_CAPS["ALLOW_EXTERNAL_TARGETS"]:
        raise RuntimeError("Safety violation: External targets are not allowed.")


# ==================================================
# DEBUG / INTROSPECTION
# ==================================================

def dump_config() -> Dict:
    """
    Returns a full snapshot of configuration
    for reporting and reproducibility.
    """
    return {
        "tool": {
            "name": TOOL_NAME,
            "version": TOOL_VERSION,
            "author": AUTHOR,
            "contact": CONTACT,
        },
        "safety_caps": SAFETY_CAPS,
        "engine_defaults": ENGINE_DEFAULTS,
        "limiter_defaults": LIMITER_DEFAULTS,
        "server_model": SERVER_MODEL_DEFAULTS,
        "profiles": {k: vars(v) for k, v in PROFILES.items()},
    }