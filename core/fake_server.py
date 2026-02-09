"""
NetLoader-X Fake Server Behavior Engine
Author  : voltsparx
Contact : voltsparx@gmail.com

Purpose:
- Safely simulate how servers behave under stress
- No real denial-of-service
- No OS-level resource exhaustion
"""

import time
import threading
import queue
import random

class ServerProfile:
    """
    Describes how a server behaves under load
    """

    def __init__(
        self,
        max_queue=100,
        base_latency=0.05,
        max_latency=2.0,
        error_threshold=0.8,
        timeout_threshold=0.95,
        refuse_threshold=1.1
    ):
        self.max_queue = max_queue
        self.base_latency = base_latency
        self.max_latency = max_latency
        self.error_threshold = error_threshold
        self.timeout_threshold = timeout_threshold
        self.refuse_threshold = refuse_threshold


class FakeServerEngine:
    """
    Simulates server-side stress behavior safely
    """

    def __init__(self, profile: ServerProfile):
        self.profile = profile
        self.request_queue = queue.Queue(maxsize=profile.max_queue)
        self.running = False

        # Metrics
        self.total_requests = 0
        self.completed = 0
        self.timed_out = 0
        self.refused = 0
        self.errors = 0

        self.lock = threading.Lock()

    def start(self):
        self.running = True
        self.worker = threading.Thread(target=self._process_loop, daemon=True)
        self.worker.start()

    def stop(self):
        self.running = False

    def submit_request(self):
        """
        Client submits a request (safe, local)
        """
        with self.lock:
            self.total_requests += 1

        load_factor = self._current_load()

        # Simulate refusal
        if load_factor >= self.profile.refuse_threshold:
            with self.lock:
                self.refused += 1
            return "REFUSED"

        try:
            self.request_queue.put_nowait(time.time())
            return "QUEUED"
        except queue.Full:
            with self.lock:
                self.refused += 1
            return "QUEUE_FULL"

    def _current_load(self):
        return self.request_queue.qsize() / max(self.profile.max_queue, 1)

    def _process_loop(self):
        while self.running:
            try:
                ts = self.request_queue.get(timeout=0.1)
            except queue.Empty:
                continue

            load = self._current_load()

            # Dynamic latency
            latency = min(
                self.profile.base_latency + load * self.profile.max_latency,
                self.profile.max_latency
            )

            time.sleep(latency)

            # Timeout simulation
            if load >= self.profile.timeout_threshold:
                with self.lock:
                    self.timed_out += 1
                continue

            # Error simulation
            if load >= self.profile.error_threshold:
                with self.lock:
                    self.errors += 1
                continue

            with self.lock:
                self.completed += 1

    def snapshot(self):
        """
        Export metrics safely
        """
        with self.lock:
            return {
                "server_requests_total": self.total_requests,
                "server_completed": self.completed,
                "server_timed_out": self.timed_out,
                "server_refused": self.refused,
                "server_errors": self.errors,
                "queue_depth": self.request_queue.qsize(),
                "queue_capacity": self.profile.max_queue
            }