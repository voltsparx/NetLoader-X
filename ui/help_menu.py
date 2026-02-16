"""
NetLoader-X :: Help & Learning Module
--------------------------------------------------
This module provides THEORY-ONLY explanations
of traffic stress patterns and server behavior.

NO operational attack instructions are included.
NO real-world execution steps are provided.

This exists purely to understand:
- Load behavior
- Failure patterns
- Defensive response logic

Author  : voltsparx
Contact : voltsparx@gmail.com
--------------------------------------------------
"""

import os
import time
from ui.theme import colorize
from ui.banner import show_banner


# ==================================================
# SCREEN UTIL
# ==================================================

def clear_screen():
    if os.name == "nt":
        os.system("cls")
    else:
        os.system("clear")


def pause():
    input(colorize("\nPress ENTER to return...", "muted"))


# ==================================================
# HELP CONTENT
# ==================================================

HELP_SECTIONS = [
    ("What is NetLoader-X?", "intro"),
    ("Traffic Load vs Attacks", "concepts"),
    ("Simulated Attack Profiles", "profiles"),
    ("Threading & Speed Model", "threading"),
    ("Server Failure Behavior", "server"),
    ("Defensive Takeaways", "defense"),
    ("Ethical Use & Scope", "ethics"),
    ("Back", "back")
]


# ==================================================
# CONTENT RENDERERS
# ==================================================

def render_intro():
    print(colorize("\nWhat is NetLoader-X?", "primary"))
    print(colorize("--------------------", "primary"))
    print(colorize("""
NetLoader-X is a defensive traffic stress simulator.

It does NOT generate real network floods.
It does NOT send packets to external systems.
It does NOT open uncontrolled sockets.

Instead, it models:
- How load increases
- How queues fill
- How latency spikes
- How errors emerge
- How services degrade

This allows safe study of:
- DDoS concepts
- Server bottlenecks
- Defensive thresholds
""", "info"))


def render_concepts():
    print(colorize("\nTraffic Load vs Attacks", "primary"))
    print(colorize("------------------------", "primary"))
    print(colorize("""
Real attacks are illegal and unethical.

However, understanding their *patterns* is essential
for defense engineers.

Key difference:
--------------------------------------------------
Traffic Load     : Controlled, measurable demand
Attack Pattern   : Abusive, asymmetric pressure

NetLoader-X models ATTACK PATTERNS
using SAFE mathematical behavior:
- Arrival rates
- Burst clustering
- Long-lived connections
- Resource starvation logic
""", "info"))


def render_profiles():
    print(colorize("\nSimulated Attack Profiles", "primary"))
    print(colorize("--------------------------", "primary"))
    print(colorize("""
Each profile is a BEHAVIOR MODEL, not an attack.

HTTP Flood Simulation:
- Many short-lived requests
- High concurrency
- Focuses on request parsing overhead

Burst Pattern:
- Sudden traffic spikes
- Quiet recovery windows
- Used to study autoscaling failure

Slow Client Simulation:
- Long-lived sessions
- Header delays
- Resource locking behavior

Wave / Pulse Load:
- Periodic pressure
- Sinusoidal traffic curves
- Useful for alert tuning

All profiles operate ONLY on localhost simulation.
""", "info"))


def render_threading():
    print(colorize("\nThreading & Speed Model", "primary"))
    print(colorize("-----------------------", "primary"))
    print(colorize("""
Threads in NetLoader-X do NOT map to OS sockets.

They represent:
- Virtual clients
- Request generators
- Timing models

Speed is governed by:
- Rate limits
- Jitter (random delay)
- Scheduler ramps

This avoids:
- CPU exhaustion
- Network abuse
- Uncontrolled loops

Everything is capped, bounded, and observable.
""", "info"))


def render_server_behavior():
    print(colorize("\nServer Failure Behavior", "primary"))
    print(colorize("------------------------", "primary"))
    print(colorize("""
The fake server engine simulates:

Queue Overflow:
- Requests exceed processing capacity
- Requests are dropped or delayed

Timeouts:
- Processing exceeds client patience
- Latency grows non-linearly

Errors:
- Synthetic 4xx / 5xx responses
- Failure rate increases with load

This mirrors REAL systems without touching the network.
""", "info"))


def render_defense():
    print(colorize("\nDefensive Takeaways", "primary"))
    print(colorize("-------------------", "primary"))
    print(colorize("""
Blue teams study:
- When queues overflow
- How fast latency rises
- Which thresholds trigger collapse

Red teams (ethical) study:
- Pressure asymmetry
- Resource exhaustion patterns
- Detection blind spots

NetLoader-X exists at the INTERSECTION:
Understanding offense to build defense.
""", "info"))


def render_ethics():
    print(colorize("\nEthical Use & Scope", "primary"))
    print(colorize("-------------------", "primary"))
    print(colorize("""
This tool is intentionally limited.

It CANNOT:
- Attack external hosts
- Generate raw packets
- Be used for real DDoS

Any attempt to modify it for harm:
- Violates ethics
- Violates law
- Defeats the purpose of learning

Use responsibly.
Study deeply.
Defend systems.
""", "warning"))


# ==================================================
# MENU HANDLER
# ==================================================

def render_help():
    while True:
        clear_screen()
        show_banner()

        print(colorize("\nHelp & Learning Menu", "primary"))
        print(colorize("--------------------", "primary"))

        for idx, (title, _) in enumerate(HELP_SECTIONS, start=1):
            print(colorize(f"[{idx}] {title}", "info"))

        choice = input(colorize("\nSelect section > ", "prompt")).strip()

        try:
            idx = int(choice)
            key = HELP_SECTIONS[idx - 1][1]
        except:
            print(colorize("[!] Invalid selection.", "error"))
            time.sleep(1)
            continue

        clear_screen()
        show_banner()

        if key == "intro":
            render_intro()
        elif key == "concepts":
            render_concepts()
        elif key == "profiles":
            render_profiles()
        elif key == "threading":
            render_threading()
        elif key == "server":
            render_server_behavior()
        elif key == "defense":
            render_defense()
        elif key == "ethics":
            render_ethics()
        elif key == "back":
            return

        pause()