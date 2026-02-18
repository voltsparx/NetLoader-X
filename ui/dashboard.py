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
from ui.banner import show_banner


# Dashboard configuration
REFRESH_INTERVAL = 0.5
ROLLING_WINDOW = 60


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
            snapshot = self.metrics.summary() if hasattr(self.metrics, 'summary') else {}
            self._record(snapshot)
            self._render(snapshot)
            time.sleep(REFRESH_INTERVAL)

    # --------------------------------------------------
    # METRIC COLLECTION
    # --------------------------------------------------

    def _record(self, snap):
        self.history["rps"].append(snap.get("requests_per_second", 0))
        self.history["latency"].append(snap.get("latency_ms", 0))
        self.history["errors"].append(snap.get("error_rate", 0))
        self.history["queue"].append(snap.get("queue_depth", 0))

    # --------------------------------------------------
    # RENDERING
    # --------------------------------------------------

    def _render(self, snap):
        self._clear()
        show_banner()

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

        print(f"Simulation Time     : {snap.get('uptime', 0):.1f} seconds")
        print(f"Virtual Clients     : {snap.get('active_clients', snap.get('active_workers', 0))}")
        print(f"Profile             : {snap.get('profile_name', 'N/A')}")
        print(f"Attack Profile      : {snap.get('attack_profile', 'N/A')}")

    def _render_rates(self):
        print(colorize("\nRequest Rate", "section"))
        print(colorize("-" * 60, "section"))

        avg = self._safe_mean(self.history["rps"])
        peak = max(self.history["rps"], default=0)

        print(f"Current RPS         : {self.history['rps'][-1]:.1f}" if self.history["rps"] else "Current RPS         : 0.0")
        print(f"Average RPS         : {avg:.1f}")
        print(f"Peak RPS            : {peak:.1f}")

    def _render_latency(self):
        print(colorize("\nLatency (ms)", "section"))
        print(colorize("-" * 60, "section"))

        avg = self._safe_mean(self.history["latency"])
        jitter = self._safe_stdev(self.history["latency"])

        print(f"Average Latency     : {avg:.1f} ms")
        print(f"Latency Jitter      : {jitter:.1f} ms")

    def _render_queue(self):
        print(colorize("\nQueue Depth", "section"))
        print(colorize("-" * 60, "section"))

        max_q = max(self.history["queue"], default=0)

        print(f"Current Queue Depth : {self.history['queue'][-1]}" if self.history["queue"] else "Current Queue Depth : 0")
        print(f"Max Queue Observed  : {max_q}")

    def _render_errors(self):
        print(colorize("\nError Rate", "section"))
        print(colorize("-" * 60, "section"))

        avg = self._safe_mean(self.history["errors"])

        if self.history["errors"]:
            print(f"Current Error Rate  : {self.history['errors'][-1]*100:.2f}%")
        else:
            print("Current Error Rate  : 0.00%")
        print(f"Average Error Rate  : {avg*100:.2f}%")

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


# ==================================================
# PUBLIC INTERFACE
# ==================================================

def live_dashboard(engine):
    """
    Start a live dashboard display for an engine.
    """
    dashboard = LiveDashboard(engine.metrics)
    dashboard.start()
    
    try:
        # Keep dashboard running while engine runs
        while engine.running.is_set():
            time.sleep(0.5)
    except KeyboardInterrupt:
        pass
    finally:
        dashboard.stop()
        engine.stop()
