"""
NetLoader-X :: Help & Learning Module
"""

from __future__ import annotations

from ui.arrow_prompt import clear_screen, select_single
from ui.banner import show_banner
from ui.theme import colorize


HELP_SECTIONS = [
    {"label": "What is NetLoader-X?", "value": "intro", "hint": "Offline-only simulation scope"},
    {"label": "Theory: Load vs Failure", "value": "concepts", "hint": "How systems degrade"},
    {"label": "Attack Profiles (10)", "value": "profiles", "hint": "Behavior models overview"},
    {"label": "Safe Configuration Locks", "value": "locks", "hint": "Why min/max limits exist"},
    {"label": "Server Failure Model", "value": "server", "hint": "Queue, timeout, crash, recovery"},
    {"label": "Plugins, Filters, Nano AI", "value": "extensions", "hint": "Learning extensions"},
    {"label": "Defensive Takeaways", "value": "defense", "hint": "How to interpret outcomes"},
    {"label": "Ethical Scope", "value": "ethics", "hint": "Legal and responsible use"},
    {"label": "Back", "value": "back", "hint": ""},
]


def _pause():
    input(colorize("\nPress ENTER to return...", "muted"))


def _render_intro():
    print(colorize("\nWhat is NetLoader-X?", "primary"))
    print(colorize("--------------------", "primary"))
    print(colorize(
        """
NetLoader-X is an educational simulator for resilience learning.

It does not send real network traffic.
It does not target external systems.
It runs safe, bounded behavior models on localhost.

Use it to study overload patterns, queue dynamics, and recovery behavior.
""",
        "info",
    ))


def _render_concepts():
    print(colorize("\nTheory: Load vs Failure", "primary"))
    print(colorize("-----------------------", "primary"))
    print(colorize(
        """
Core concepts:
- Throughput pressure increases queue depth.
- Queue growth drives latency and timeout risk.
- Error rates can cascade when retries amplify load.
- Recovery is usually slower than degradation.

The simulator lets you inspect these relationships safely.
""",
        "info",
    ))


def _render_profiles():
    print(colorize("\nAttack Profiles (10)", "primary"))
    print(colorize("--------------------", "primary"))
    print(colorize(
        """
1. http      : steady request pressure
2. burst     : repeated spikes
3. slow      : long-held client pressure
4. wave      : periodic oscillation
5. retry     : retry amplification
6. cache     : expensive-request bias
7. mixed     : combined vectors
8. spike     : flash crowd surge
9. brownout  : sustained partial degradation
10. recovery : overload then stabilization
""",
        "info",
    ))


def _render_locks():
    print(colorize("\nSafe Configuration Locks", "primary"))
    print(colorize("------------------------", "primary"))
    print(colorize(
        """
Editable values are safety-clamped:
- threads, duration, rate, jitter
- queue limit, timeout, crash threshold, recovery rate, error floor

These limits keep simulations educational and prevent unsafe local overload.
""",
        "info",
    ))


def _render_server():
    print(colorize("\nServer Failure Model", "primary"))
    print(colorize("--------------------", "primary"))
    print(colorize(
        """
Queue limit:
- Higher values buffer bursts, but increase latency risk.

Timeout:
- Lower timeout fails fast; higher timeout tolerates wait.

Crash threshold:
- Pressure point where model enters failure state.

Recovery rate:
- How quickly synthetic service recovers after stress.
""",
        "info",
    ))


def _render_extensions():
    print(colorize("\nPlugins, Filters, Nano AI", "primary"))
    print(colorize("--------------------------", "primary"))
    print(colorize(
        """
Plugins (annotate metrics):
- nano-coach
- trend-lens
- resilience-score

Filters (clean/smooth metrics):
- latency-cap
- error-smooth
- queue-floor

Nano AI provides rule-based hints for safer interpretation.
""",
        "info",
    ))


def _render_defense():
    print(colorize("\nDefensive Takeaways", "primary"))
    print(colorize("-------------------", "primary"))
    print(colorize(
        """
Watch these first:
- queue depth (early warning)
- latency trend (degradation)
- error rate (instability)
- recovery slope (resilience)

Run baseline + stressed scenarios and compare reports side by side.
""",
        "info",
    ))


def _render_ethics():
    print(colorize("\nEthical Scope", "primary"))
    print(colorize("-------------", "primary"))
    print(colorize(
        """
This project is for defensive education.
No external targets, no raw traffic, no attack execution.

Use responsibly and lawfully.
""",
        "warning",
    ))


RENDERERS = {
    "intro": _render_intro,
    "concepts": _render_concepts,
    "profiles": _render_profiles,
    "locks": _render_locks,
    "server": _render_server,
    "extensions": _render_extensions,
    "defense": _render_defense,
    "ethics": _render_ethics,
}


def render_help():
    while True:
        clear_screen()
        show_banner()
        choice = select_single("Help & Learning Menu", HELP_SECTIONS, default_index=0)
        if choice == "back":
            return

        clear_screen()
        show_banner()
        RENDERERS[choice]()
        _pause()
