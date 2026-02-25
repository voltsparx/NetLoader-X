"""
NetLoader-X
--------------------------------------------------
Simulation Configuration & Safety Caps

This module defines:
- Global simulation limits
- Hard safety enforcement (no real traffic)
- Default profiles & tunables
- Output/reporting behavior

Tool metadata is imported from core.metadata

License : Educational / Defensive Simulation Only
--------------------------------------------------
"""

from dataclasses import dataclass, field
from typing import Dict, List
import os
import datetime
from core.user_settings import get_default_output_dir

# Import metadata from dedicated module
from core.metadata import (
    PROJECT_NAME,
    PROJECT_TAGLINE,
    VERSION_FULL,
    AUTHOR_NAME,
    AUTHOR_EMAIL,
)

# ==================================================
# TOOL METADATA (from core.metadata)
# ==================================================

TOOL_NAME = PROJECT_NAME
TOOL_TAGLINE = PROJECT_TAGLINE
TOOL_VERSION = VERSION_FULL
AUTHOR = AUTHOR_NAME
CONTACT = AUTHOR_EMAIL

# ==================================================
# GLOBAL CONFIG CLASS
# ==================================================

class GlobalConfig:
    """
    Centralized configuration for simulation engine.
    """
    ALLOWED_HOSTS = ["localhost", "127.0.0.1"]
    ALLOWED_PORT_RANGE = (1024, 65534)
    OUTPUT_DIR = get_default_output_dir()
    
    def __init__(self):
        self.max_rps = 50000
        self.burst_size = 100
        self.burst_cooldown = 2
        self.slow_hold_time = 10
        self.slow_chunk_delay = 0.5
        self.simulated_connections = 100

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

BASE_OUTPUT_DIR = get_default_output_dir()

DEFAULT_REPORT_FORMATS = [
    "csv",
    "json",
    "html"
]

HTML_REPORT_SETTINGS = {
    "theme": "blue",
    # HTML reports include lightweight SVG/CSS charts by default.
    "include_graphs": True,
    "include_summary": True,
    "include_timeline": True,
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
# USER TUNABLE SAFETY LOCKS
# ==================================================

USER_TUNABLE_LIMITS = {
    "threads": {"min": 1, "max": 5000, "step": 5},
    "duration": {"min": 5, "max": 900, "step": 5},
    "rate": {"min": 1, "max": 50000, "step": 100},
    "jitter": {"min": 0.0, "max": 0.5, "step": 0.01},
    "queue_limit": {"min": 25, "max": 5000, "step": 25},
    "timeout_ms": {"min": 200, "max": 10000, "step": 100},
    "crash_threshold": {"min": 0.70, "max": 0.99, "step": 0.01},
    "recovery_rate": {"min": 0.01, "max": 0.20, "step": 0.01},
    "error_floor": {"min": 0.0, "max": 0.20, "step": 0.01},
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
    return datetime.datetime.utcnow().strftime("run_%Y-%m-%d_%H-%M-%S")


def ensure_output_dirs(run_id: str) -> str:
    """
    Create output directory tree for a simulation run.
    """
    base = os.path.join(BASE_OUTPUT_DIR, run_id)
    os.makedirs(base, exist_ok=True)

    for fmt in DEFAULT_REPORT_FORMATS:
        os.makedirs(os.path.join(base, fmt), exist_ok=True)

    return base


def set_output_dir(output_dir: str) -> str:
    """
    Set the base output directory for reports/logs.

    Accepts relative or absolute paths. Returns the configured value.
    """
    out = str(output_dir or "").strip() or get_default_output_dir()
    GlobalConfig.OUTPUT_DIR = out
    global BASE_OUTPUT_DIR
    BASE_OUTPUT_DIR = out
    return out


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
        "user_tunable_limits": USER_TUNABLE_LIMITS,
        "engine_defaults": ENGINE_DEFAULTS,
        "limiter_defaults": LIMITER_DEFAULTS,
        "server_model": SERVER_MODEL_DEFAULTS,
        "profiles": {k: vars(v) for k, v in PROFILES.items()},
    }
