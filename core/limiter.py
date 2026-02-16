import time
import threading

class RateLimiter:
    """
    Token-bucket rate limiter for SAFE simulations
    """
    def __init__(self, rate_per_sec):
        self.rate = rate_per_sec
        self.allowance = rate_per_sec
        self.last_check = time.time()
        self.lock = threading.Lock()

    def wait(self):
        with self.lock:
            now = time.time()
            elapsed = now - self.last_check
            self.last_check = now

            self.allowance += elapsed * self.rate
            if self.allowance > self.rate:
                self.allowance = self.rate

            if self.allowance < 1:
                time.sleep((1 - self.allowance) / self.rate)
                self.allowance = 0
            else:
                self.allowance -= 1


class SafetyLimiter:
    """
    Enforces hard safety limits to prevent misuse.
    Caps max requests and connections.
    """
    
    def __init__(self, max_events=100000, max_slow_clients=10000):
        self.max_events = max_events
        self.max_slow_clients = max_slow_clients
    
    def limit(self, events: int, slow_clients: int):
        """
        Enforce safety caps on events and slow clients.
        Returns (capped_events, capped_slow_clients)
        """
        events = min(events, self.max_events)
        slow_clients = min(slow_clients, self.max_slow_clients)
        return events, slow_clients