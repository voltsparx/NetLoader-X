"""
NetLoader-X :: Cluster Simulation Engine
================================================
Simulates entire server clusters with:
- Load balancer with multiple routing algorithms
- Multiple backend servers with different capacities
- Database/cache layer simulation
- Microservices architecture support

Author  : voltsparx
Contact : voltsparx@gmail.com

Safe, offline, localhost-only cluster simulation.
"""

import time
import random
import threading
from typing import Dict, List, Tuple, Any
from enum import Enum
from collections import defaultdict
import queue

from core.fake_server import ServerProfile, FakeServerEngine


class LoadBalancerAlgorithm(Enum):
    """Load balancing algorithms"""
    ROUND_ROBIN = "round-robin"
    LEAST_CONNECTIONS = "least-connections"
    RANDOM = "random"
    WEIGHTED_ROUND_ROBIN = "weighted-round-robin"
    IP_HASH = "ip-hash"


class DatabaseLayer:
    """Simulates database/cache layer with connection pooling"""

    def __init__(self, pool_size: int = 20, cache_enabled: bool = False):
        """
        Initialize database layer.

        Args:
            pool_size: Number of available connections
            cache_enabled: Whether caching is enabled
        """
        self.pool_size = pool_size
        self.cache_enabled = cache_enabled
        self.available_connections = pool_size
        self.lock = threading.Lock()
        
        # Metrics
        self.total_queries = 0
        self.cache_hits = 0
        self.cache_misses = 0
        self.pool_exhausted_count = 0

    def acquire_connection(self) -> bool:
        """Try to acquire a connection from pool"""
        with self.lock:
            self.total_queries += 1
            if self.available_connections > 0:
                self.available_connections -= 1
                return True
            else:
                self.pool_exhausted_count += 1
                return False

    def release_connection(self):
        """Release a connection back to pool"""
        with self.lock:
            if self.available_connections < self.pool_size:
                self.available_connections += 1

    def check_cache(self) -> bool:
        """Simulate cache hit/miss"""
        if not self.cache_enabled:
            return False
        
        hit = random.random() < 0.7  # 70% cache hit rate
        with self.lock:
            if hit:
                self.cache_hits += 1
            else:
                self.cache_misses += 1
        return hit

    def snapshot(self) -> Dict[str, Any]:
        """Get database metrics snapshot"""
        with self.lock:
            return {
                "db_total_queries": self.total_queries,
                "db_cache_hits": self.cache_hits,
                "db_cache_misses": self.cache_misses,
                "db_pool_available": self.available_connections,
                "db_pool_size": self.pool_size,
                "db_pool_exhausted": self.pool_exhausted_count,
                "db_cache_hit_rate": round(
                    self.cache_hits / max(self.total_queries, 1) * 100, 2
                )
            }


class LoadBalancer:
    """Load balancer that distributes requests across backend servers"""

    def __init__(
        self,
        algorithm: LoadBalancerAlgorithm = LoadBalancerAlgorithm.ROUND_ROBIN,
        backends: List[Tuple[str, FakeServerEngine]] = None
    ):
        """
        Initialize load balancer.

        Args:
            algorithm: Load balancing algorithm to use
            backends: List of (name, server) tuples
        """
        self.algorithm = algorithm
        self.backends = backends or []
        self.current_index = 0
        self.lock = threading.Lock()
        self.request_count = 0
        self.requests_per_backend = defaultdict(int)
        self.failed_requests = 0

    def add_backend(self, name: str, server: FakeServerEngine):
        """Add a backend server"""
        self.backends.append((name, server))

    def select_backend(self) -> Tuple[str, FakeServerEngine]:
        """Select a backend using configured algorithm"""
        if not self.backends:
            raise ValueError("No backends available")

        with self.lock:
            self.request_count += 1

            if self.algorithm == LoadBalancerAlgorithm.ROUND_ROBIN:
                idx = self.current_index % len(self.backends)
                self.current_index += 1
                return self.backends[idx]

            elif self.algorithm == LoadBalancerAlgorithm.LEAST_CONNECTIONS:
                # Select server with smallest queue
                min_queue = float('inf')
                selected = None
                for name, server in self.backends:
                    queue_size = server.request_queue.qsize()
                    if queue_size < min_queue:
                        min_queue = queue_size
                        selected = (name, server)
                return selected

            elif self.algorithm == LoadBalancerAlgorithm.RANDOM:
                idx = random.randint(0, len(self.backends) - 1)
                return self.backends[idx]

            elif self.algorithm == LoadBalancerAlgorithm.WEIGHTED_ROUND_ROBIN:
                # Weight by worker count (stored in server.workers)
                total_weight = sum(
                    getattr(server, "worker_count", getattr(server, "workers", 50))
                    for _, server in self.backends
                )
                idx = self.current_index % total_weight
                self.current_index += 1
                
                cumulative = 0
                for i, (name, server) in enumerate(self.backends):
                    weight = getattr(server, "worker_count", getattr(server, "workers", 50))
                    cumulative += weight
                    if idx < cumulative:
                        return self.backends[i]
                return self.backends[0]

            elif self.algorithm == LoadBalancerAlgorithm.IP_HASH:
                # Simulate consistent hashing (deterministic but distributed)
                hash_val = self.request_count
                idx = hash_val % len(self.backends)
                return self.backends[idx]

            return self.backends[0]

    def forward_request(self) -> str:
        """Forward a request to selected backend"""
        name, server = self.select_backend()
        result = server.submit_request()
        
        with self.lock:
            self.requests_per_backend[name] += 1
            if result in ["REFUSED", "QUEUE_FULL"]:
                self.failed_requests += 1
        
        return result

    def snapshot(self) -> Dict[str, Any]:
        """Get load balancer metrics"""
        with self.lock:
            return {
                "lb_algorithm": self.algorithm.value,
                "lb_requests_total": self.request_count,
                "lb_failed_requests": self.failed_requests,
                "lb_backends_count": len(self.backends),
                "lb_requests_per_backend": dict(self.requests_per_backend)
            }


class ServerCluster:
    """Simulates an entire server cluster"""

    def __init__(
        self,
        lb_algorithm: LoadBalancerAlgorithm = LoadBalancerAlgorithm.ROUND_ROBIN,
        backends_config: List[Dict[str, Any]] = None,
        db_pool_size: int = 20,
        db_cache_enabled: bool = False
    ):
        """
        Initialize a server cluster.

        Args:
            lb_algorithm: Load balancing algorithm
            backends_config: List of backend configs
                [{name: str, workers: int, profile: ServerProfile}, ...]
            db_pool_size: Database connection pool size
            db_cache_enabled: Enable database caching
        """
        self.lb_algorithm = lb_algorithm
        self.load_balancer = LoadBalancer(lb_algorithm)
        self.database = DatabaseLayer(db_pool_size, db_cache_enabled)
        self.backends = {}
        self.lock = threading.Lock()

        # Cluster metrics
        self.total_requests = 0
        self.cluster_errors = 0
        self.start_time = time.time()

        # Initialize backends
        backends_config = backends_config or []
        for config in backends_config:
            self.add_backend(config)

    def add_backend(self, config: Dict[str, Any]):
        """
        Add a backend server to the cluster.

        Args:
            config: {name, workers, max_queue, base_latency, ...}
        """
        name = config.get("name", f"backend-{len(self.backends)}")
        workers = config.get("workers", 50)
        
        # Create server profile
        profile = ServerProfile(
            max_queue=config.get("max_queue", 100),
            base_latency=config.get("base_latency", 0.05),
            max_latency=config.get("max_latency", 2.0),
            error_threshold=config.get("error_threshold", 0.8),
            timeout_threshold=config.get("timeout_threshold", 0.95),
            refuse_threshold=config.get("refuse_threshold", 1.1)
        )

        # Create server instance
        server = FakeServerEngine(profile, worker_count=workers)
        server.start()

        self.backends[name] = server
        self.load_balancer.add_backend(name, server)

    def submit_request(self) -> str:
        """
        Submit request through load balancer to backend.
        Includes database interaction simulation.
        """
        with self.lock:
            self.total_requests += 1

        # Check if database is available
        if not self.database.acquire_connection():
            with self.lock:
                self.cluster_errors += 1
            return "DB_UNAVAILABLE"

        try:
            # Simulate cache hit
            if self.database.check_cache():
                self.database.release_connection()
                return "CACHE_HIT"

            # Forward through load balancer
            result = self.load_balancer.forward_request()
            return result
        finally:
            self.database.release_connection()

    def get_backend(self, name: str) -> FakeServerEngine:
        """Get specific backend server"""
        return self.backends.get(name)

    def start_all(self):
        """Start all backend servers"""
        for server in self.backends.values():
            if not server.running:
                server.start()

    def stop_all(self):
        """Stop all backend servers"""
        for server in self.backends.values():
            server.stop()

    def snapshot(self) -> Dict[str, Any]:
        """Get comprehensive cluster snapshot"""
        cluster_snapshot = {
            "cluster_requests_total": self.total_requests,
            "cluster_errors": self.cluster_errors,
            "cluster_uptime": round(time.time() - self.start_time, 2),
            "cluster_backends": len(self.backends)
        }

        # Load balancer metrics
        cluster_snapshot.update(self.load_balancer.snapshot())

        # Database metrics
        cluster_snapshot.update(self.database.snapshot())

        # Per-backend metrics
        for name, server in self.backends.items():
            backend_snapshot = server.snapshot()
            # Prefix with backend name
            for key, value in backend_snapshot.items():
                cluster_snapshot[f"{name}_{key}"] = value

        return cluster_snapshot

    def summary(self) -> Dict[str, Any]:
        """Get cluster summary for dashboards"""
        snapshot = self.snapshot()
        
        # Calculate aggregate metrics
        total_completed = sum(
            snapshot.get(f"{name}_server_completed", 0)
            for name in self.backends.keys()
        )
        total_errors = sum(
            snapshot.get(f"{name}_server_errors", 0)
            for name in self.backends.keys()
        )
        total_queue_depth = sum(
            snapshot.get(f"{name}_queue_depth", 0)
            for name in self.backends.keys()
        )

        return {
            "cluster_backends": len(self.backends),
            "cluster_total_requests": self.total_requests,
            "cluster_completed": total_completed,
            "cluster_errors": total_errors,
            "cluster_queue_depth": total_queue_depth,
            "cluster_db_pool_available": snapshot.get("db_pool_available", 0),
            "cluster_cache_hit_rate": snapshot.get("db_cache_hit_rate", 0),
            "lb_algorithm": self.lb_algorithm.value,
            "per_backend": {
                name: {
                    "completed": snapshot.get(f"{name}_server_completed", 0),
                    "queue": snapshot.get(f"{name}_queue_depth", 0),
                    "errors": snapshot.get(f"{name}_server_errors", 0)
                }
                for name in self.backends.keys()
            }
        }
