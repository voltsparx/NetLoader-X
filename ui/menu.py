"""
NetLoader-X :: Interactive Menu System

Arrow-key driven configuration with safety locks.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass, field
from typing import Any, Dict, List

from core.config import USER_TUNABLE_LIMITS
from core.nano_ai import NanoAIAdvisor
from filters import available_filters
from plugins import available_plugins
from ui.arrow_prompt import clear_screen, edit_numeric_config, select_multiple, select_single
from ui.banner import show_banner
from ui.help_menu import render_help
from ui.theme import colorize
from utils.logger import log_event


PROFILE_OPTIONS = [
    {"label": "HTTP Flood (Simulated)", "value": "http", "hint": "Steady request pressure baseline."},
    {"label": "Burst Traffic Pattern", "value": "burst", "hint": "Repeated burst windows."},
    {"label": "Slow Client Behavior", "value": "slow", "hint": "Long-held connection pressure."},
    {"label": "Wave / Pulsing Load", "value": "wave", "hint": "Periodic load oscillation."},
    {"label": "Retry Storm Behavior", "value": "retry", "hint": "Failures triggering retries."},
    {"label": "Cache Bypass Pattern", "value": "cache", "hint": "Expensive request bias."},
    {"label": "Mixed Multi-Vector Pattern", "value": "mixed", "hint": "Combined pressure modes."},
    {"label": "Flash Spike Pattern", "value": "spike", "hint": "Sudden high-amplitude spikes."},
    {"label": "Brownout Drift Pattern", "value": "brownout", "hint": "Sustained partial failure behavior."},
    {"label": "Recovery Curve Pattern", "value": "recovery", "hint": "Stress then stabilization dynamics."},
    {"label": "Back", "value": "back", "hint": ""},
]


def _plugin_options() -> List[Dict[str, str]]:
    registry = available_plugins()
    names = sorted(registry.keys())
    return [
        {"label": name, "value": name, "hint": registry[name].description}
        for name in names
    ]


def _filter_options() -> List[Dict[str, str]]:
    registry = available_filters()
    names = sorted(registry.keys())
    return [
        {"label": name, "value": name, "hint": registry[name].description}
        for name in names
    ]


def _schema_for(keys: List[str], labels: Dict[str, str], hints: Dict[str, str], precision: Dict[str, int]):
    schema = []
    for key in keys:
        spec = USER_TUNABLE_LIMITS[key]
        schema.append(
            {
                "key": key,
                "label": labels.get(key, key),
                "min": spec["min"],
                "max": spec["max"],
                "step": spec["step"],
                "precision": precision.get(key),
                "hint": hints.get(key, ""),
            }
        )
    return schema


@dataclass
class MenuState:
    attack_profile: str = "http"
    action: str = "run"
    confirmed: bool = False
    nano_ai: bool = False
    auto_debrief: bool = False
    compare_baseline: str = ""
    compare_candidate: str = ""
    debrief_input: str = ""
    sweep_spec: Dict[str, Any] = field(default_factory=dict)
    config: Dict[str, Any] = field(
        default_factory=lambda: {
            "threads": 50,
            "duration": 120,
            "rate": 2000,
            "jitter": 0.10,
        }
    )
    target_behavior: Dict[str, Any] = field(
        default_factory=lambda: {
            "queue_limit": 500,
            "timeout_ms": 1200,
            "crash_threshold": 0.95,
            "recovery_rate": 0.04,
            "error_floor": 0.04,
        }
    )
    plugins: List[str] = field(default_factory=list)
    filters: List[str] = field(default_factory=list)


def pause(msg: str = "Press ENTER to continue..."):
    input(colorize(msg, "muted"))


def _prompt_with_default(prompt: str, default: str) -> str:
    raw = input(colorize(f"{prompt} [{default}] > ", "prompt")).strip()
    return raw or default


def _to_int(raw: str, default: int) -> int:
    try:
        return int(raw)
    except (TypeError, ValueError):
        return int(default)


def profile_menu(state: MenuState):
    choice = select_single("Select Attack Profile", PROFILE_OPTIONS, default_index=0)
    if choice != "back":
        state.attack_profile = choice
        log_event("PROFILE_SELECTED", {"profile": choice})


def configuration_menu(state: MenuState):
    labels = {
        "threads": "Threads",
        "duration": "Duration (s)",
        "rate": "Rate",
        "jitter": "Jitter",
    }
    hints = {
        "threads": "Virtual clients. Higher means stronger synthetic pressure.",
        "duration": "Longer runs reveal recovery patterns.",
        "rate": "Scheduler baseline requests per tick.",
        "jitter": "Randomness in traffic timing.",
    }
    precision = {"jitter": 2}
    schema = _schema_for(["threads", "duration", "rate", "jitter"], labels, hints, precision)
    state.config = edit_numeric_config("Simulation Configuration", state.config, schema)

    toggle = select_single(
        "Nano AI Assistant",
        [
            {"label": "Enable Nano AI coach", "value": "on", "hint": "Adds realtime educational hints."},
            {"label": "Disable Nano AI coach", "value": "off", "hint": "Keep metrics unannotated."},
            {"label": "Back", "value": "back", "hint": ""},
        ],
        default_index=0 if state.nano_ai else 1,
    )
    if toggle == "on":
        state.nano_ai = True
    elif toggle == "off":
        state.nano_ai = False

    debrief_toggle = select_single(
        "Post-Run Debrief",
        [
            {"label": "Enable post-run teaching debrief", "value": "on", "hint": "Automatically show run debrief summary."},
            {"label": "Disable post-run teaching debrief", "value": "off", "hint": "Skip automatic debrief output."},
            {"label": "Back", "value": "back", "hint": ""},
        ],
        default_index=0 if state.auto_debrief else 1,
    )
    if debrief_toggle == "on":
        state.auto_debrief = True
    elif debrief_toggle == "off":
        state.auto_debrief = False

    clear_screen()
    show_banner()
    advisor = NanoAIAdvisor()
    print(colorize("\nNano AI Configuration Tips", "primary"))
    print(colorize("--------------------------", "primary"))
    for tip in advisor.advise_config(state.config):
        print(colorize(f"- {tip}", "info"))
    pause()


def target_menu(state: MenuState):
    labels = {
        "queue_limit": "Queue Limit",
        "timeout_ms": "Timeout (ms)",
        "crash_threshold": "Crash Threshold",
        "recovery_rate": "Recovery Rate",
        "error_floor": "Error Floor",
    }
    hints = {
        "queue_limit": "Max queued requests before overflow.",
        "timeout_ms": "Synthetic timeout boundary.",
        "crash_threshold": "Pressure level that triggers crash mode.",
        "recovery_rate": "How fast simulated service recovers.",
        "error_floor": "Minimum baseline error.",
    }
    precision = {
        "crash_threshold": 2,
        "recovery_rate": 2,
        "error_floor": 2,
    }
    schema = _schema_for(
        ["queue_limit", "timeout_ms", "crash_threshold", "recovery_rate", "error_floor"],
        labels,
        hints,
        precision,
    )
    state.target_behavior = edit_numeric_config("Server Failure Behavior (Safe Model)", state.target_behavior, schema)


def extensions_menu(state: MenuState):
    state.plugins = select_multiple(
        "Plugin Selection",
        _plugin_options(),
        initial_selected=state.plugins,
    )
    state.filters = select_multiple(
        "Filter Selection",
        _filter_options(),
        initial_selected=state.filters,
    )


def compare_menu(state: MenuState):
    clear_screen()
    show_banner()
    print(colorize("\nCompare Reports", "primary"))
    print(colorize("---------------", "primary"))
    print(colorize("Provide metrics.json file path or a report directory.", "muted"))
    baseline = _prompt_with_default("Baseline path", state.compare_baseline or "outputs")
    candidate = _prompt_with_default("Candidate path", state.compare_candidate or "outputs")
    state.compare_baseline = baseline
    state.compare_candidate = candidate
    state.action = "compare"


def debrief_menu(state: MenuState):
    clear_screen()
    show_banner()
    print(colorize("\nTeaching Debrief", "primary"))
    print(colorize("----------------", "primary"))
    print(colorize("Provide metrics.json file path or a report directory.", "muted"))
    state.debrief_input = _prompt_with_default("Input path", state.debrief_input or "outputs")
    state.action = "debrief"


def sweep_menu(state: MenuState):
    clear_screen()
    show_banner()
    print(colorize("\nParameter Sweep Setup", "primary"))
    print(colorize("---------------------", "primary"))
    print(colorize("CSV examples: 20,50,100", "muted"))
    state.sweep_spec = {
        "profile": _prompt_with_default("Profile", state.attack_profile),
        "threads_values": _prompt_with_default("Threads values", "20,50,100"),
        "duration_values": _prompt_with_default("Duration values", "20,40"),
        "rate_values": _prompt_with_default("Rate values", "1000,3000,5000"),
        "jitter_values": _prompt_with_default("Jitter values", "0.05,0.10,0.20"),
        "top": _to_int(_prompt_with_default("Top results", "5"), 5),
        "max_runs": _to_int(_prompt_with_default("Max runs", "36"), 36),
        "score_mode": _prompt_with_default("Score mode (balanced/throughput/stability)", "balanced"),
    }
    state.action = "sweep"


def _print_state_summary(state: MenuState):
    print(colorize("\nSimulation Summary", "primary"))
    print(colorize("------------------", "primary"))
    print(colorize(f"Profile       : {state.attack_profile}", "info"))
    print(colorize(f"Threads       : {state.config['threads']}", "info"))
    print(colorize(f"Duration      : {state.config['duration']} sec", "info"))
    print(colorize(f"Rate          : {state.config['rate']}", "info"))
    print(colorize(f"Jitter        : {state.config['jitter']}", "info"))
    print(colorize(f"Queue Limit   : {state.target_behavior['queue_limit']}", "info"))
    print(colorize(f"Timeout (ms)  : {state.target_behavior['timeout_ms']}", "info"))
    print(colorize(f"Crash Thresh  : {state.target_behavior['crash_threshold']}", "info"))
    print(colorize(f"Recovery Rate : {state.target_behavior['recovery_rate']}", "info"))
    print(colorize(f"Error Floor   : {state.target_behavior['error_floor']}", "info"))
    print(colorize(f"Plugins       : {', '.join(state.plugins) if state.plugins else 'none'}", "info"))
    print(colorize(f"Filters       : {', '.join(state.filters) if state.filters else 'none'}", "info"))
    print(colorize(f"Nano AI       : {'enabled' if state.nano_ai else 'disabled'}", "info"))
    print(colorize(f"Auto Debrief  : {'enabled' if state.auto_debrief else 'disabled'}", "info"))
    print(colorize("\n[!] Localhost simulation only. No real traffic is generated.", "warning"))


def confirm_start(state: MenuState) -> bool:
    clear_screen()
    show_banner()
    _print_state_summary(state)
    while True:
        ans = input(colorize("\nConfirm start? (yes/no) > ", "prompt")).strip().lower()
        if ans in ("yes", "y"):
            state.confirmed = True
            log_event("SIMULATION_CONFIRMED", {})
            return True
        if ans in ("no", "n"):
            log_event("SIMULATION_ABORTED", {})
            return False
        print(colorize("[!] Please type yes or no.", "error"))


def run_menu() -> MenuState:
    state = MenuState()
    menu_options = [
        {"label": "Configure Simulation", "value": "config", "hint": "Threads, duration, jitter, rate"},
        {"label": "Select Attack Profile", "value": "profile", "hint": "Choose one of 10 behavior profiles"},
        {"label": "Target & Server Behavior", "value": "target", "hint": "Queue/timeout/recovery safe knobs"},
        {"label": "Plugins & Filters", "value": "extensions", "hint": "Select none/single/multiple extensions"},
        {"label": "Run Parameter Sweep", "value": "sweep", "hint": "Grid search and ranking"},
        {"label": "Compare Two Reports", "value": "compare", "hint": "Causal diff between runs"},
        {"label": "Debrief Existing Report", "value": "debrief", "hint": "Teaching summary for a run"},
        {"label": "View Help / Theory", "value": "help", "hint": "Learning notes and profile theory"},
        {"label": "Start Simulation", "value": "start", "hint": "Run with current state"},
        {"label": "Exit", "value": "exit", "hint": "Quit"},
    ]

    while True:
        clear_screen()
        show_banner()
        choice = select_single("Main Menu", menu_options, default_index=0)

        if choice == "config":
            configuration_menu(state)
        elif choice == "profile":
            profile_menu(state)
        elif choice == "target":
            target_menu(state)
        elif choice == "extensions":
            extensions_menu(state)
        elif choice == "sweep":
            sweep_menu(state)
            return state
        elif choice == "compare":
            compare_menu(state)
            return state
        elif choice == "debrief":
            debrief_menu(state)
            return state
        elif choice == "help":
            render_help()
        elif choice == "start":
            if confirm_start(state):
                state.action = "run"
                return state
        elif choice == "exit":
            clear_screen()
            print(colorize("Exiting NetLoader-X.", "muted"))
            sys.exit(0)


def main_menu() -> MenuState:
    return run_menu()
