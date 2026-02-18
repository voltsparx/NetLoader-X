"""
NetLoader-X :: Scheduler Engine
--------------------------------------------------
Controls how load evolves over time.

This is a BEHAVIORAL scheduler:
- No networking
- No sockets
- No real targets

Used to STUDY patterns, not execute them.

Author  : voltsparx
--------------------------------------------------
"""

import math
import random
import threading
import time
from typing import Dict, Optional


# ==================================================
# SCHEDULER PROFILES
# ==================================================

class ScheduleProfile:
    """
    Base class for all scheduler profiles.
    """

    def __init__(
        self,
        base_rate: int,
        max_rate: int,
        duration: int,
        jitter: float = 0.0,
        seed: Optional[int] = None
    ):
        self.base_rate = base_rate
        self.max_rate = max_rate
        self.duration = duration
        self.jitter = jitter

        self.random = random.Random(seed)

    def rate_at(self, tick: int) -> int:
        raise NotImplementedError

    def _apply_jitter(self, rate: float) -> int:
        if self.jitter > 0:
            rate *= self.random.uniform(1 - self.jitter, 1 + self.jitter)
        return max(0, int(rate))


# ==================================================
# RAMP PROFILE
# ==================================================

class RampProfile(ScheduleProfile):
    """
    Linear ramp-up then steady.
    """

    def rate_at(self, tick: int) -> int:
        if self.duration <= 0 or tick >= self.duration:
            rate = self.max_rate
        else:
            rate = self.base_rate + (
                (self.max_rate - self.base_rate)
                * (tick / self.duration)
            )

        return self._apply_jitter(rate)


# ==================================================
# WAVE PROFILE
# ==================================================

class WaveProfile(ScheduleProfile):
    """
    Sinusoidal wave load pattern.
    """

    def __init__(
        self,
        base_rate: int,
        max_rate: int,
        duration: int,
        period: int = 30,
        jitter: float = 0.0,
        seed: Optional[int] = None
    ):
        super().__init__(base_rate, max_rate, duration, jitter, seed)
        self.period = max(1, int(period))

    def rate_at(self, tick: int) -> int:
        amplitude = (self.max_rate - self.base_rate) / 2
        mid = self.base_rate + amplitude

        rate = mid + amplitude * math.sin(
            2 * math.pi * tick / self.period
        )

        return self._apply_jitter(rate)


# ==================================================
# BURST PROFILE
# ==================================================

class BurstProfile(ScheduleProfile):
    """
    Sudden spikes separated by calm periods.
    """

    def __init__(
        self,
        base_rate: int,
        max_rate: int,
        duration: int,
        burst_interval: int,
        burst_length: int,
        jitter: float = 0.0,
        seed: Optional[int] = None
    ):
        super().__init__(base_rate, max_rate, duration, jitter, seed)
        self.burst_interval = max(1, int(burst_interval))
        self.burst_length = max(1, int(burst_length))

    def rate_at(self, tick: int) -> int:
        phase = tick % self.burst_interval

        if phase < self.burst_length:
            rate = self.max_rate
        else:
            rate = self.base_rate

        return self._apply_jitter(rate)


# ==================================================
# SLOW-CLIENT (BEHAVIORAL)
# ==================================================

class SlowClientProfile(ScheduleProfile):
    """
    Simulates slow-client pressure patterns
    (e.g., long-hold connections conceptually).

    NOTE: purely behavioral - no connections.
    """

    def __init__(
        self,
        base_rate: int,
        max_rate: int,
        duration: int,
        hold_factor: float = 1.5,
        jitter: float = 0.0,
        seed: Optional[int] = None
    ):
        super().__init__(base_rate, max_rate, duration, jitter, seed)
        self.hold_factor = hold_factor

    def rate_at(self, tick: int) -> int:
        denom = max(1.0, self.duration * self.hold_factor)
        decay = math.exp(-tick / denom)
        rate = self.max_rate * decay + self.base_rate

        return self._apply_jitter(rate)


class StairStepProfile(ScheduleProfile):
    """
    Gradual staircase increase for mixed-vector scenarios.
    """

    def __init__(
        self,
        base_rate: int,
        max_rate: int,
        duration: int,
        steps: int = 5,
        jitter: float = 0.0,
        seed: Optional[int] = None,
    ):
        super().__init__(base_rate, max_rate, duration, jitter, seed)
        self.steps = max(1, int(steps))

    def rate_at(self, tick: int) -> int:
        if self.duration <= 0:
            return self._apply_jitter(self.max_rate)
        step_size = self.duration / self.steps
        current_step = min(self.steps, int(tick / max(1.0, step_size)) + 1)
        progress = current_step / self.steps
        rate = self.base_rate + ((self.max_rate - self.base_rate) * progress)
        return self._apply_jitter(rate)


# ==================================================
# SCHEDULER CORE
# ==================================================

class Scheduler:
    """
    Drives the simulation timeline.

    Provides:
    - Tick loop
    - Pause / resume
    - Deterministic pacing
    """

    def __init__(
        self,
        profile: ScheduleProfile,
        tick_interval: float = 1.0
    ):
        self.profile = profile
        self.tick_interval = tick_interval

        self.tick = 0
        self.running = False
        self.paused = False

        self.lock = threading.Lock()

    # --------------------------------------------------

    def start(self):
        with self.lock:
            self.running = True
            self.paused = False
            self.tick = 0

    # --------------------------------------------------

    def stop(self):
        with self.lock:
            self.running = False

    # --------------------------------------------------

    def pause(self):
        with self.lock:
            self.paused = True

    # --------------------------------------------------

    def resume(self):
        with self.lock:
            self.paused = False

    # --------------------------------------------------

    def next_tick(self) -> Optional[Dict]:
        """
        Advance scheduler by one tick.

        Returns:
            dict with tick & planned rate
        """
        with self.lock:
            if not self.running:
                return None

            if self.paused:
                time.sleep(self.tick_interval)
                return {
                    "tick": self.tick,
                    "rate": 0,
                    "paused": True
                }

            rate = self.profile.rate_at(self.tick)

            payload = {
                "tick": self.tick,
                "rate": rate,
                "paused": False,
                "timestamp": time.time(),
            }

            self.tick += 1

        time.sleep(self.tick_interval)
        return payload
