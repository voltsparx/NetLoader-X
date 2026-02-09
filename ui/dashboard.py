"""
NetLoader-X :: Real-Time Dashboard Engine
--------------------------------------------------
This module renders live simulation statistics in a
professional, SOC-style terminal dashboard.

NO network operations.
NO packet generation.
Metrics are consumed from simulated engines only.

Author  : voltsparx
Contact : voltsparx@gmail.com
--------------------------------------------------
"""

import time
import threading
from collections import deque
from statistics import mean, stdev

from ui.theme import colorize
from ui.banner import render_banner
from core.metrics import MetricsSnapshot


# ==================================================
# DASHBOARD CONFIGURATION
# ==================================================

REFRESH_INTERVAL = 0.5          # seconds
ROLLING_WINDOW = 60             # samples
MAX_GRAPH_WIDTH = 40


# ==================================================
# DASHBOARD CLASS
# ==================================================

class LiveDashboard:
    """
    Renders real-time metrics in a structured,
    readable, SOC-style layout.
    """

    def __init__(self, metrics_engine):
        self.metrics = metrics_engine
        self.running = threading.Event()
        self.history = {
            "rps": deque(maxlen=ROLLING_WINDOW),
            "latency": deque(maxlen=ROLLING_WINDOW),
            "errors": deque(maxlen=ROLLING_WINDOW),
            "queue": deque(maxlen=ROLLING_WINDOW)
        }

    # --------------------------------------------------
    # CONTROL
    # --------------------------------------------------

    def start(self):
        self.running.set()
        threading.Thread(target=self._run, daemon=True).start()

    def stop(self):
        self.running.clear()

    # --------------------------------------------------
    # MAIN LOOP
    # --------------------------------------------------

    def _run(self):
        while self.running.is_set():
            snapshot = self.metrics.snapshot()
            self._record(snapshot)
            self._render(snapshot)
            time.sleep(REFRESH_INTERVAL)

    # --------------------------------------------------
    # METRIC COLLECTION
    # --------------------------------------------------

    def _record(self, snap: MetricsSnapshot):
        self.history["rps"].append(snap.requests_per_second)
        self.history["latency"].append(snap.avg_latency_ms)
        self.history["errors"].append(snap.error_rate)
        self.history["queue"].append(snap.queue_depth)

    # --------------------------------------------------
    # RENDERING
    # --------------------------------------------------

    def _render(self, snap: MetricsSnapshot):
        self._clear()
        render_banner()

        print(colorize("\n[ Live Simulation Dashboard ]", "primary"))
        print(colorize("=" * 60, "primary"))

        self._render_overview(snap)
        self._render_rates()
        self._render_latency()
        self._render_queue()
        self._render_errors()

        print(colorize("\n[CTRL+C] Stop simulation safely", "muted"))

    # --------------------------------------------------
    # SECTIONS
    # --------------------------------------------------

    def _render_overview(self, snap):
        print(colorize("\nOverview", "section"))
        print(colorize("-" * 60, "section"))

        print(f"Scenario Name       : {snap.scenario_name}")
        print(f"Simulation Time     : {snap.uptime:.1f} seconds")
        print(f"Virtual Clients     : {snap.active_clients}")
        print(f"Profile             : {snap.profile_name}")
        print(f"Scheduler Phase     : {snap.scheduler_phase}")

    def _render_rates(self):
        print(colorize("\nRequest Rate", "section"))
        print(colorize("-" * 60, "section"))

        avg = self._safe_mean(self.history["rps"])
        peak = max(self.history["rps"], default=0)

        print(f"Current RPS         : {self.history['rps'][-1]:.1f}")
        print(f"Average RPS         : {avg:.1f}")
        print(f"Peak RPS            : {peak:.1f}")
        print(self._bar_graph(self.history["rps"], "rps"))

    def _render_latency(self):
        print(colorize("\nLatency (ms)", "section"))
        print(colorize("-" * 60, "section"))

        avg = self._safe_mean(self.history["latency"])
        jitter = self._safe_stdev(self.history["latency"])

        print(f"Average Latency     : {avg:.1f} ms")
        print(f"Latency Jitter      : {jitter:.1f} ms")
        print(self._bar_graph(self.history["latency"], "latency"))

    def _render_queue(self):
        print(colorize("\nQueue Depth", "section"))
        print(colorize("-" * 60, "section"))

        max_q = max(self.history["queue"], default=0)

        print(f"Current Queue Depth : {self.history['queue'][-1]}")
        print(f"Max Queue Observed  : {max_q}")
        print(self._bar_graph(self.history["queue"], "queue"))

    def _render_errors(self):
        print(colorize("\nError Rate", "section"))
        print(colorize("-" * 60, "section"))

        avg = self._safe_mean(self.history["errors"])

        print(f"Current Error Rate  : {self.history['errors'][-1]*100:.2f}%")
        print(f"Average Error Rate  : {avg*100:.2f}%")
        print(self._bar_graph(self.history["errors"], "errors"))

    # --------------------------------------------------
    # GRAPH UTILITIES
    # --------------------------------------------------

    def _bar_graph(self, values, label):
        if not values:
            return ""

        peak = max(values)
        if peak <= 0:
            peak = 1

        scaled = int((values[-1] / peak) * MAX_GRAPH_WIDTH)
        bar = "#" * scaled

        return f"[{label:<8}] |{bar:<{MAX_GRAPH_WIDTH}}|"

    # --------------------------------------------------
    # SAFE STATS
    # --------------------------------------------------

    @staticmethod
    def _safe_mean(data):
        return mean(data) if len(data) > 1 else (data[0] if data else 0)

    @staticmethod
    def _safe_stdev(data):
        return stdev(data) if len(data) > 2 else 0

    # --------------------------------------------------
    # SCREEN
    # --------------------------------------------------

    @staticmethod
    def _clear():
        import os
        os.system("cls" if os.name == "nt" else "clear")