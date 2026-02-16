"""
NetLoader-X :: Menu System
--------------------------------------------------
Numeric, defensive-first interaction layer.

- No command shell
- No free-text execution
- Explicit confirmations
- Cross-platform UI safety

Author  : voltsparx
Contact : voltsparx@gmail.com
--------------------------------------------------
"""

import os
import sys
import time
from typing import Dict, Any

from ui.banner import show_banner
from ui.help_menu import render_help
from ui.theme import colorize
from utils.validators import validate_numeric_choice
from utils.logger import log_event


# ==================================================
# SCREEN UTILS
# ==================================================

def clear_screen():
    """
    Clear terminal screen for Windows & Unix.
    """
    if os.name == "nt":
        os.system("cls")
    else:
        os.system("clear")


def pause(msg: str = "Press ENTER to continue..."):
    input(colorize(msg, "muted"))


# ==================================================
# MENU DEFINITIONS
# ==================================================

MAIN_MENU = [
    ("Configure Simulation", "config"),
    ("Select Attack Profile", "profile"),
    ("Target & Server Behavior", "target"),
    ("View Help / Theory", "help"),
    ("Start Simulation", "start"),
    ("Exit", "exit")
]

PROFILE_MENU = [
    ("HTTP Flood (Simulated)", "http"),
    ("Burst Traffic Pattern", "burst"),
    ("Slow Client Behavior", "slow"),
    ("Wave / Pulsing Load", "wave"),
    ("Back", "back")
]


# ==================================================
# MENU RENDERING
# ==================================================

def render_menu(title: str, options):
    clear_screen()
    show_banner()

    print(colorize(f"\n{title}", "primary"))
    print(colorize("-" * len(title), "primary"))

    for idx, (label, _) in enumerate(options, start=1):
        print(colorize(f"[{idx}] {label}", "info"))

    print("")


def get_choice(options) -> str:
    """
    Enforce numeric-only input.
    """
    while True:
        try:
            choice = input(colorize("Select option > ", "prompt")).strip()
            index = validate_numeric_choice(choice, len(options))
            return options[index - 1][1]
        except ValueError as e:
            print(colorize(f"[!] {e}", "error"))


# ==================================================
# CONFIGURATION STATE
# ==================================================

class MenuState:
    """
    Shared configuration state across menus.
    """

    def __init__(self):
        self.attack_profile = None
        self.simulation_name = None
        self.confirmed = False

        self.config: Dict[str, Any] = {
            "threads": 50,
            "duration": 120,
            "rate": 100,
            "jitter": 0.1
        }

        self.target_behavior: Dict[str, Any] = {
            "queue_limit": 500,
            "timeout_ms": 1200,
            "error_rate": 0.05
        }


# ==================================================
# SUB-MENUS
# ==================================================

def profile_menu(state: MenuState):
    while True:
        render_menu("Attack Profile (Simulation)", PROFILE_MENU)
        choice = get_choice(PROFILE_MENU)

        if choice == "back":
            return

        state.attack_profile = choice
        log_event("PROFILE_SELECTED", {"profile": choice})

        print(colorize(f"[+] Profile set to: {choice}", "success"))
        pause()
        return


def configuration_menu(state: MenuState):
    clear_screen()
    render_banner()

    print(colorize("\nSimulation Configuration", "primary"))
    print(colorize("------------------------", "primary"))

    for k, v in state.config.items():
        print(colorize(f"{k:<15}: {v}", "info"))

    print("")
    pause("Configuration is preloaded for safety. Press ENTER to go back.")


def target_menu(state: MenuState):
    clear_screen()
    render_banner()

    print(colorize("\nFake Server Behavior Model", "primary"))
    print(colorize("---------------------------", "primary"))

    for k, v in state.target_behavior.items():
        print(colorize(f"{k:<15}: {v}", "info"))

    print("")
    pause("Behavior models are locked to localhost simulation.")


# ==================================================
# CONFIRMATION
# ==================================================

def confirm_start(state: MenuState) -> bool:
    clear_screen()
    render_banner()

    print(colorize("\nSimulation Summary", "primary"))
    print(colorize("-------------------", "primary"))

    print(colorize(f"Profile       : {state.attack_profile}", "info"))
    print(colorize(f"Duration      : {state.config['duration']} sec", "info"))
    print(colorize(f"Threads       : {state.config['threads']}", "info"))
    print(colorize(f"Target        : localhost (simulated)", "info"))

    print("")
    print(colorize("[!] This is a LOCAL SIMULATION ONLY.", "warning"))
    print(colorize("[!] No real traffic will be generated.", "warning"))

    while True:
        ans = input(colorize("\nConfirm start? (yes/no) > ", "prompt")).strip().lower()
        if ans in ("yes", "y"):
            state.confirmed = True
            log_event("SIMULATION_CONFIRMED", {})
            return True
        elif ans in ("no", "n"):
            log_event("SIMULATION_ABORTED", {})
            return False
        else:
            print(colorize("[!] Please type yes or no.", "error"))


# ==================================================
# MAIN MENU LOOP
# ==================================================

def run_menu() -> MenuState:
    state = MenuState()

    while True:
        render_menu("Main Menu", MAIN_MENU)
        choice = get_choice(MAIN_MENU)

        if choice == "config":
            configuration_menu(state)

        elif choice == "profile":
            profile_menu(state)

        elif choice == "target":
            target_menu(state)

        elif choice == "help":
            render_help()
            pause()

        elif choice == "start":
            if not state.attack_profile:
                print(colorize("[!] Select an attack profile first.", "error"))
                pause()
                continue

            if confirm_start(state):
                return state

        elif choice == "exit":
            clear_screen()
            print(colorize("Exiting NetLoader-X.", "muted"))
            sys.exit(0)


# ==================================================
# PUBLIC INTERFACE
# ==================================================

def main_menu():
    """
    Main menu interface - returns selected profile choice
    """
    state = run_menu()
    
    # Map profile names to choice numbers
    profile_map = {
        "http": "1",
        "burst": "2", 
        "slow": "3",
        "wave": "4"
    }
    
    return profile_map.get(state.attack_profile, "1")