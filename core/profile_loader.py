"""
NetLoader-X :: Custom Profile Loader
====================================
Load attack profiles and server configurations from
YAML or JSON files instead of editing code.

This allows non-developers to create custom scenarios.

Author  : voltsparx
Contact : voltsparx@gmail.com
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict


@dataclass
class AttackProfileConfig:
    """Attack profile loaded from file."""
    name: str
    description: str
    profile_type: str  # "http", "burst", "slow", "wave", "chaos"
    threads: int
    duration: int
    base_rate: int
    max_rate: int
    jitter: float = 0.05
    burst_interval: Optional[int] = None
    burst_length: Optional[int] = None
    chaos_enabled: bool = False
    chaos_fault_rate: float = 0.0


@dataclass
class ServerProfileConfig:
    """Server behavior profile loaded from file."""
    name: str
    description: str
    max_workers: int
    queue_limit: int
    base_latency_ms: float
    timeout_ms: int
    error_rate_base: float = 0.01
    error_rate_growth: float = 1.2
    crash_threshold: float = 0.95


class ProfileLoader:
    """Loads attack and server profiles from YAML/JSON files."""

    SUPPORTED_FORMATS = [".json", ".yaml", ".yml"]

    def __init__(self):
        self.attack_profiles: Dict[str, AttackProfileConfig] = {}
        self.server_profiles: Dict[str, ServerProfileConfig] = {}

    def load_file(self, filepath: Path) -> bool:
        """
        Load profiles from a JSON or YAML file.

        Args:
            filepath: Path to configuration file

        Returns:
            True if successful, False otherwise
        """
        filepath = Path(filepath)

        if not filepath.exists():
            print(f"[!] File not found: {filepath}")
            return False

        if filepath.suffix not in self.SUPPORTED_FORMATS:
            print(f"[!] Unsupported format: {filepath.suffix}")
            print(f"    Supported: {self.SUPPORTED_FORMATS}")
            return False

        try:
            if filepath.suffix == ".json":
                return self._load_json(filepath)
            else:
                return self._load_yaml(filepath)
        except Exception as e:
            print(f"[!] Error loading {filepath}: {e}")
            return False

    def _load_json(self, filepath: Path) -> bool:
        """Load profiles from JSON file."""
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        return self._parse_config(data)

    def _load_yaml(self, filepath: Path) -> bool:
        """Load profiles from YAML file."""
        try:
            import yaml
        except ImportError:
            print("[!] YAML support requires: pip install pyyaml")
            return False

        with open(filepath, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        return self._parse_config(data)

    def _parse_config(self, data: Dict[str, Any]) -> bool:
        """
        Parse loaded configuration data.

        Expected structure:
        {
            "attack_profiles": [ {...}, {...} ],
            "server_profiles": [ {...}, {...} ]
        }
        """
        try:
            if "attack_profiles" in data:
                for profile_data in data["attack_profiles"]:
                    profile = AttackProfileConfig(**profile_data)
                    self.attack_profiles[profile.name] = profile

            if "server_profiles" in data:
                for profile_data in data["server_profiles"]:
                    profile = ServerProfileConfig(**profile_data)
                    self.server_profiles[profile.name] = profile

            return len(self.attack_profiles) > 0 or len(self.server_profiles) > 0

        except TypeError as e:
            print(f"[!] Configuration format error: {e}")
            return False

    def get_attack_profile(self, name: str) -> Optional[AttackProfileConfig]:
        """Get loaded attack profile by name."""
        return self.attack_profiles.get(name)

    def get_server_profile(self, name: str) -> Optional[ServerProfileConfig]:
        """Get loaded server profile by name."""
        return self.server_profiles.get(name)

    def list_attack_profiles(self) -> List[str]:
        """List all loaded attack profile names."""
        return list(self.attack_profiles.keys())

    def list_server_profiles(self) -> List[str]:
        """List all loaded server profile names."""
        return list(self.server_profiles.keys())

    def export_example_config(self, output_path: Path) -> bool:
        """
        Generate example configuration file.

        Args:
            output_path: Where to write example config

        Returns:
            True if successful
        """
        example = {
            "attack_profiles": [
                {
                    "name": "http-steady",
                    "description": "Constant HTTP load",
                    "profile_type": "http",
                    "threads": 50,
                    "duration": 60,
                    "base_rate": 1000,
                    "max_rate": 5000,
                    "jitter": 0.05
                },
                {
                    "name": "burst-spike",
                    "description": "Sudden traffic bursts",
                    "profile_type": "burst",
                    "threads": 100,
                    "duration": 60,
                    "base_rate": 2000,
                    "max_rate": 8000,
                    "burst_interval": 10,
                    "burst_length": 3
                },
                {
                    "name": "slowloris-sim",
                    "description": "Slow client attack simulation",
                    "profile_type": "slow",
                    "threads": 50,
                    "duration": 45,
                    "base_rate": 500,
                    "max_rate": 2000,
                    "jitter": 0.1
                },
                {
                    "name": "chaos-test",
                    "description": "Load with random fault injection",
                    "profile_type": "chaos",
                    "threads": 75,
                    "duration": 60,
                    "base_rate": 3000,
                    "max_rate": 9000,
                    "chaos_enabled": True,
                    "chaos_fault_rate": 0.05
                }
            ],
            "server_profiles": [
                {
                    "name": "tiny-server",
                    "description": "Small test server",
                    "max_workers": 10,
                    "queue_limit": 50,
                    "base_latency_ms": 20,
                    "timeout_ms": 1000
                },
                {
                    "name": "medium-server",
                    "description": "Medium production server",
                    "max_workers": 50,
                    "queue_limit": 500,
                    "base_latency_ms": 40,
                    "timeout_ms": 2000
                },
                {
                    "name": "large-server",
                    "description": "Large enterprise server",
                    "max_workers": 200,
                    "queue_limit": 2000,
                    "base_latency_ms": 50,
                    "timeout_ms": 3000
                }
            ]
        }

        try:
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(example, f, indent=2)
            print(f"[+] Example config written to: {output_path}")
            return True
        except Exception as e:
            print(f"[!] Failed to write example config: {e}")
            return False


# ==================================================
# EXAMPLE CONFIGURATION FILES (as strings)
# ==================================================

EXAMPLE_JSON = """{
  "attack_profiles": [
    {
      "name": "http-steady",
      "description": "Constant HTTP load pressure",
      "profile_type": "http",
      "threads": 50,
      "duration": 60,
      "base_rate": 1000,
      "max_rate": 5000,
      "jitter": 0.05
    },
    {
      "name": "burst-spike",
      "description": "Sudden traffic bursts (flash crowd simulation)",
      "profile_type": "burst",
      "threads": 100,
      "duration": 60,
      "base_rate": 2000,
      "max_rate": 8000,
      "burst_interval": 10,
      "burst_length": 3
    },
    {
      "name": "slowloris-attack",
      "description": "Slow client connection exhaustion",
      "profile_type": "slow",
      "threads": 50,
      "duration": 45,
      "base_rate": 500,
      "max_rate": 2000,
      "jitter": 0.1
    },
    {
      "name": "chaos-engineering",
      "description": "Load with random fault injection (5% error rate)",
      "profile_type": "chaos",
      "threads": 75,
      "duration": 60,
      "base_rate": 3000,
      "max_rate": 9000,
      "chaos_enabled": true,
      "chaos_fault_rate": 0.05
    }
  ],
  "server_profiles": [
    {
      "name": "tiny-server",
      "description": "Small test/dev server (10 workers)",
      "max_workers": 10,
      "queue_limit": 50,
      "base_latency_ms": 20.0,
      "timeout_ms": 1000
    },
    {
      "name": "medium-server",
      "description": "Medium production server (50 workers)",
      "max_workers": 50,
      "queue_limit": 500,
      "base_latency_ms": 40.0,
      "timeout_ms": 2000
    },
    {
      "name": "large-server",
      "description": "Large enterprise server (200 workers)",
      "max_workers": 200,
      "queue_limit": 2000,
      "base_latency_ms": 50.0,
      "timeout_ms": 3000
    }
  ]
}
"""

EXAMPLE_YAML = """# NetLoader-X Custom Profiles Configuration
# Copy this file and modify as needed

attack_profiles:
  - name: http-steady
    description: "Constant HTTP load pressure"
    profile_type: http
    threads: 50
    duration: 60
    base_rate: 1000
    max_rate: 5000
    jitter: 0.05

  - name: burst-spike
    description: "Sudden traffic bursts (flash crowd simulation)"
    profile_type: burst
    threads: 100
    duration: 60
    base_rate: 2000
    max_rate: 8000
    burst_interval: 10
    burst_length: 3

  - name: slowloris-attack
    description: "Slow client connection exhaustion"
    profile_type: slow
    threads: 50
    duration: 45
    base_rate: 500
    max_rate: 2000
    jitter: 0.1

  - name: chaos-engineering
    description: "Load with random fault injection (5% error rate)"
    profile_type: chaos
    threads: 75
    duration: 60
    base_rate: 3000
    max_rate: 9000
    chaos_enabled: true
    chaos_fault_rate: 0.05

server_profiles:
  - name: tiny-server
    description: "Small test/dev server (10 workers)"
    max_workers: 10
    queue_limit: 50
    base_latency_ms: 20.0
    timeout_ms: 1000

  - name: medium-server
    description: "Medium production server (50 workers)"
    max_workers: 50
    queue_limit: 500
    base_latency_ms: 40.0
    timeout_ms: 2000

  - name: large-server
    description: "Large enterprise server (200 workers)"
    max_workers: 200
    queue_limit: 2000
    base_latency_ms: 50.0
    timeout_ms: 3000
"""
