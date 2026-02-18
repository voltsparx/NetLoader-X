import threading
import time

from core.config import SAFETY_CAPS


class RateLimiter:
    """
    Token-bucket limiter for simulation pacing.
    """

    def __init__(self, rate_per_sec: int):
        if rate_per_sec <= 0:
            raise ValueError("rate_per_sec must be positive")
        self.rate = int(rate_per_sec)
        self.allowance = float(self.rate)
        self.last_check = time.monotonic()
        self.lock = threading.Lock()

    def wait(self):
        with self.lock:
            now = time.monotonic()
            elapsed = now - self.last_check
            self.last_check = now

            self.allowance = min(float(self.rate), self.allowance + elapsed * self.rate)
            if self.allowance >= 1.0:
                self.allowance -= 1.0
                return

            sleep_for = (1.0 - self.allowance) / self.rate

        time.sleep(max(0.0, sleep_for))
        with self.lock:
            self.allowance = max(0.0, self.allowance - 1.0)


class SafetyLimiter:
    """
    Enforce non-negotiable simulation caps.
    """

    def __init__(self, max_events: int = None, max_slow_clients: int = None):
        self.max_events = int(max_events or SAFETY_CAPS["MAX_EVENTS_PER_SECOND"])
        self.max_slow_clients = int(max_slow_clients or SAFETY_CAPS["MAX_VIRTUAL_CLIENTS"])

    def limit(self, events: int, slow_clients: int):
        events = max(0, min(int(events), self.max_events))
        slow_clients = max(0, min(int(slow_clients), self.max_slow_clients))
        return events, slow_clients
