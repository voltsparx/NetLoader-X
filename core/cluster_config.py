"""
NetLoader-X :: Cluster Configuration Parser
================================================
Loads and validates cluster configurations from YAML/JSON files.

Example cluster-config.yaml:
  load_balancer:
    algorithm: round-robin
    backends:
      - name: server1
        workers: 50
        max_queue: 100
      - name: server2
        workers: 50
        max_queue: 100
      - name: server3
        workers: 30
        max_queue: 80
  database:
    connection_pool: 20
    cache_enabled: true
"""

import json
import copy
from typing import Dict, Any
from pathlib import Path

from core.config import SAFETY_CAPS

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False


class ClusterConfigParser:
    """Parse and validate cluster configuration files"""

    MAX_BACKENDS = 128
    MAX_DB_POOL = 50_000

    # Default configuration
    DEFAULT_CONFIG = {
        "load_balancer": {
            "algorithm": "round-robin",
            "backends": [
                {
                    "name": "backend-1",
                    "workers": 50,
                    "max_queue": 100,
                    "base_latency": 0.05,
                    "max_latency": 2.0
                }
            ]
        },
        "database": {
            "connection_pool": 20,
            "cache_enabled": False
        }
    }

    @staticmethod
    def load_from_file(filepath: str) -> Dict[str, Any]:
        """
        Load cluster configuration from YAML or JSON file.

        Args:
            filepath: Path to config file (.yaml or .json)

        Returns:
            Parsed configuration dictionary
        """
        path = Path(filepath)

        if not path.exists():
            raise FileNotFoundError(f"Config file not found: {filepath}")

        if path.suffix in [".yaml", ".yml"]:
            if not HAS_YAML:
                raise ImportError(
                    "PyYAML is required for YAML config files.\n"
                    "Install with: pip install pyyaml"
                )
            with open(path, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f)
        elif path.suffix == ".json":
            with open(path, "r", encoding="utf-8") as f:
                config = json.load(f)
        else:
            raise ValueError("Config file must be .yaml, .yml, or .json")

        return ClusterConfigParser.validate(config)

    @staticmethod
    def load_from_string(config_str: str, format: str = "yaml") -> Dict[str, Any]:
        """
        Load cluster configuration from string.

        Args:
            config_str: Configuration string
            format: "yaml" or "json"

        Returns:
            Parsed configuration dictionary
        """
        if format == "yaml":
            if not HAS_YAML:
                raise ImportError("PyYAML required for YAML format")
            config = yaml.safe_load(config_str)
        elif format == "json":
            config = json.loads(config_str)
        else:
            raise ValueError("Format must be 'yaml' or 'json'")

        return ClusterConfigParser.validate(config)

    @staticmethod
    def validate(config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and normalize cluster configuration.

        Args:
            config: Configuration dictionary

        Returns:
            Validated and normalized configuration

        Raises:
            ValueError: If configuration is invalid
        """
        if not isinstance(config, dict):
            raise ValueError("Configuration must be a dictionary")

        # Validate load balancer section
        lb_config = config.get("load_balancer", {})
        
        # Validate algorithm
        algorithm = lb_config.get("algorithm", "round-robin").lower()
        valid_algorithms = [
            "round-robin", "least-connections", "random",
            "weighted-round-robin", "ip-hash"
        ]
        if algorithm not in valid_algorithms:
            raise ValueError(
                f"Invalid algorithm '{algorithm}'. "
                f"Must be one of: {', '.join(valid_algorithms)}"
            )

        # Validate backends
        backends = lb_config.get("backends", [])
        if not isinstance(backends, list):
            raise ValueError("Backends must be a list")

        if len(backends) == 0:
            raise ValueError("At least one backend must be configured")
        if len(backends) > ClusterConfigParser.MAX_BACKENDS:
            raise ValueError(
                f"Backends cannot exceed {ClusterConfigParser.MAX_BACKENDS}"
            )

        validated_backends = []
        for i, backend in enumerate(backends):
            if isinstance(backend, dict):
                validated_backend = ClusterConfigParser._validate_backend(backend, i)
                validated_backends.append(validated_backend)
            else:
                raise ValueError(f"Backend {i} must be a dictionary")

        # Validate database section
        db_config = config.get("database", {})
        pool_size = db_config.get("connection_pool", 20)
        if (
            not isinstance(pool_size, int)
            or pool_size < 1
            or pool_size > ClusterConfigParser.MAX_DB_POOL
        ):
            raise ValueError(
                f"connection_pool must be between 1 and {ClusterConfigParser.MAX_DB_POOL}"
            )

        cache_enabled = db_config.get("cache_enabled", False)
        if not isinstance(cache_enabled, bool):
            raise ValueError("cache_enabled must be a boolean")

        # Build validated config
        return {
            "load_balancer": {
                "algorithm": algorithm,
                "backends": validated_backends
            },
            "database": {
                "connection_pool": pool_size,
                "cache_enabled": cache_enabled
            }
        }

    @staticmethod
    def _validate_backend(backend: Dict[str, Any], index: int) -> Dict[str, Any]:
        """Validate a single backend configuration"""
        # Generate name if not provided
        name = backend.get("name", f"backend-{index}")
        if not isinstance(name, str):
            raise ValueError(f"Backend {index} name must be a string")

        # Validate workers
        workers = backend.get("workers", 50)
        max_workers = SAFETY_CAPS["MAX_VIRTUAL_CLIENTS"]
        if not isinstance(workers, int) or workers < 1 or workers > max_workers:
            raise ValueError(
                f"Backend '{name}' workers must be between 1 and {max_workers}"
            )

        # Validate queue size
        max_queue = backend.get("max_queue", 100)
        max_events = SAFETY_CAPS["MAX_EVENTS_PER_SECOND"]
        if not isinstance(max_queue, int) or max_queue < 1 or max_queue > max_events:
            raise ValueError(
                f"Backend '{name}' max_queue must be between 1 and {max_events}"
            )

        # Validate latency parameters
        base_latency = backend.get("base_latency", 0.05)
        if not isinstance(base_latency, (int, float)) or base_latency < 0:
            raise ValueError(
                f"Backend '{name}' base_latency must be non-negative"
            )

        max_latency = backend.get("max_latency", 2.0)
        if not isinstance(max_latency, (int, float)) or max_latency < base_latency:
            raise ValueError(
                f"Backend '{name}' max_latency must be >= base_latency"
            )

        # Validate thresholds
        for threshold_name in ["error_threshold", "timeout_threshold", "refuse_threshold"]:
            value = backend.get(threshold_name, None)
            if value is not None:
                if not isinstance(value, (int, float)) or not (0 <= value <= 2.0):
                    raise ValueError(
                        f"Backend '{name}' {threshold_name} must be between 0 and 2.0"
                    )

        return {
            "name": name,
            "workers": workers,
            "max_queue": max_queue,
            "base_latency": base_latency,
            "max_latency": max_latency,
            "error_threshold": backend.get("error_threshold", 0.8),
            "timeout_threshold": backend.get("timeout_threshold", 0.95),
            "refuse_threshold": backend.get("refuse_threshold", 1.1)
        }

    @staticmethod
    def get_default_config() -> Dict[str, Any]:
        """Get default cluster configuration"""
        return copy.deepcopy(ClusterConfigParser.DEFAULT_CONFIG)

    @staticmethod
    def create_example_yaml() -> str:
        """Generate example YAML configuration"""
        return """
# NetLoader-X Cluster Configuration Example

load_balancer:
  # Routing algorithm: round-robin, least-connections, random, weighted-round-robin, ip-hash
  algorithm: round-robin
  
  # Backend servers configuration
  backends:
    # Primary server 1
    - name: server1
      workers: 50                    # Virtual worker threads
      max_queue: 100                 # Request queue size
      base_latency: 0.05            # Base processing latency (seconds)
      max_latency: 2.0              # Max latency under stress
      error_threshold: 0.8          # Load at which errors start
      timeout_threshold: 0.95       # Load at which timeouts occur
      refuse_threshold: 1.1         # Load at which requests refused

    # Primary server 2
    - name: server2
      workers: 50
      max_queue: 100
      base_latency: 0.05
      max_latency: 2.0

    # Smaller backup server
    - name: server3
      workers: 30
      max_queue: 80
      base_latency: 0.06
      max_latency: 2.5

# Database/Cache layer configuration
database:
  connection_pool: 20              # Number of DB connections available
  cache_enabled: true              # Enable caching simulation
  # With cache_enabled, ~70% of queries hit cache
"""

    @staticmethod
    def create_example_json() -> str:
        """Generate example JSON configuration"""
        return json.dumps(
            ClusterConfigParser.DEFAULT_CONFIG,
            indent=2
        )
