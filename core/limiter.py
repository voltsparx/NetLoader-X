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