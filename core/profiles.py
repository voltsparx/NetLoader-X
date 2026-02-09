import time
import random
from core.limiter import RateLimiter

class BaseProfile:
    name = "BASE"
    description = ""

    def run(self, engine, metrics):
        raise NotImplementedError


class HTTPSteady(BaseProfile):
    name = "HTTP_STEADY"
    description = "Constant request rate"

    def run(self, engine, metrics):
        limiter = RateLimiter(engine.config.max_rps)
        while engine.running:
            limiter.wait()
            metrics.record_request(
                success=True,
                latency=random.uniform(20, 80)
            )
            time.sleep(0.01)


class HTTPBurst(BaseProfile):
    name = "HTTP_BURST"
    description = "Short bursts of traffic"

    def run(self, engine, metrics):
        while engine.running:
            for _ in range(engine.config.burst_size):
                metrics.record_request(
                    success=True,
                    latency=random.uniform(30, 150)
                )
            time.sleep(engine.config.burst_cooldown)


class SlowClient(BaseProfile):
    name = "SLOW_CLIENT"
    description = "Slow header/body transmission"

    def run(self, engine, metrics):
        metrics.record_connection(opened=True)
        start = time.time()
        while engine.running and time.time() - start < engine.config.slow_hold_time:
            metrics.record_request(success=True, latency=500)
            time.sleep(engine.config.slow_chunk_delay)
        metrics.record_connection(closed=True)