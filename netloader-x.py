#!/usr/bin/env python3
"""
NetLoader-X :: Main Entry Point
================================
Defensive Load & Failure Simulation Framework

Supports both interactive and CLI modes.

Usage:
  python netloader-x.py                    # Interactive menu
  python netloader-x.py run --profile http # Run HTTP profile
  python netloader-x.py quick-test         # Quick demo
  python netloader-x.py labs --list        # Show guided labs

Author  : voltsparx
Contact : voltsparx@gmail.com
"""

import os
import sys
import time
from pathlib import Path

# Ensure current directory is in path
sys.path.insert(0, str(Path(__file__).parent))

from core.config import GlobalConfig, validate_safety
from core.engine import Engine
from core.profiles import HTTPSteady, HTTPBurst, SlowClient
from core.simulations import SimSlowloris, SimHTTPFlood, SimICMP
from ui.banner import show_banner
from ui.menu import main_menu, run_menu
from ui.dashboard import live_dashboard
from cli import CLIParser


PROFILES = {
    "1": HTTPSteady(),
    "2": HTTPBurst(),
    "3": SlowClient(),
    "4": SimSlowloris(),
    "5": SimHTTPFlood(),
    "6": SimICMP(),
}


def clear():
    """Clear screen cross-platform."""
    os.system("cls" if os.name == "nt" else "clear")


def interactive_mode():
    """
    Original interactive menu mode.
    """
    clear()
    show_banner()
    choice = main_menu()

    workload = PROFILES.get(choice)
    if not workload:
        print("Invalid choice")
        return

    threads = 50
    duration = 60

    engine = Engine()
    engine.configure(
        "small-web",
        "HTTP" if isinstance(workload, HTTPSteady)
        else "BURST" if isinstance(workload, HTTPBurst)
        else "SLOW",
        threads,
        duration
    )

    confirm = input("[?] Start simulation? (yes/no): ").lower()
    if confirm != "yes":
        return

    clear()
    engine.run()
    live_dashboard(engine)


def quick_test_mode(args):
    """
    Quick demo mode with sensible defaults.
    """
    clear()
    show_banner()

    profile = getattr(args, "profile", "http")
    short = getattr(args, "short", False)
    skip_dashboard = getattr(args, "skip_dashboard", False)

    print("\n[*] Quick Test Mode")
    print(f"    Profile: {profile}")
    print(f"    Duration: {'10 sec' if short else '30 sec'}")
    print(f"    Dashboard: {'Disabled' if skip_dashboard else 'Enabled'}")
    print(f"\n[+] Starting simulation...\n")

    engine = Engine()
    duration = 10 if short else 30
    threads = 30 if short else 50

    engine.configure("small-web", profile.upper(), threads, duration)

    engine.run()

    if not skip_dashboard:
        live_dashboard(engine)
    else:
        # Show summary
        print(f"\n[+] Simulation complete")
        print(f"    Total ticks: {engine.current_tick}")
        print(f"    Metrics collected: {len(engine.metrics._raw_ticks)}")

    # Generate reports
    export = engine.export_metrics()
    print(f"    Peak RPS: {max([s.get('requests_per_second', 0) for s in export.get('raw', [])], default=0)}")


def run_command(args):
    """Handle 'run' subcommand."""
    clear()
    show_banner()

    batch = getattr(args, "batch", False)
    profile = getattr(args, "profile", None)
    threads = getattr(args, "threads", 50)
    duration = getattr(args, "duration", 60)

    if batch and not profile:
        print("[!] Batch mode requires --profile argument")
        return

    if batch:
        # Batch mode: skip prompts
        print(f"[*] Batch Mode")
        print(f"    Profile: {profile}")
        print(f"    Threads: {threads}")
        print(f"    Duration: {duration}s")

        engine = Engine()
        engine.configure("small-web", profile.upper(), threads, duration)
        engine.run()
        live_dashboard(engine)
    else:
        # Interactive mode
        if profile:
            # Skip menu and use provided profile
            engine = Engine()
            engine.configure("small-web", profile.upper(), threads, duration)
            
            confirm = input("\n[?] Start simulation? (yes/no): ").lower()
            if confirm == "yes":
                clear()
                engine.run()
                live_dashboard(engine)
        else:
            # Full interactive menu
            interactive_mode()


def labs_command(args):
    """Handle 'labs' subcommand."""
    clear()
    show_banner()

    from core.guided_labs import LabManager, LabDifficulty

    manager = LabManager()

    if getattr(args, "list", False):
        manager.list_labs()
        return

    if getattr(args, "description_only", False):
        lab_id = getattr(args, "lab", 1)
        try:
            lab = manager.get_lab(lab_id)
            print(f"\n{lab.name}")
            print(f"{'=' * 60}")
            print(f"Difficulty: {lab.difficulty.name}")
            print(f"Objective: {lab.learning_objective}")
            print(f"Duration: {lab.duration}s")
            print(f"\n{lab.description}")
            print(f"\nKey Insight: {lab.key_insight}")
        except ValueError as e:
            print(f"[!] {e}")
        return

    lab_id = getattr(args, "lab", None)
    if not lab_id:
        # Show list and prompt
        manager.list_labs()
        try:
            lab_id = int(input("\n[?] Select lab (1-7): "))
        except:
            return

    try:
        lab = manager.get_lab(lab_id)
        interactive = getattr(args, "interactive", True)

        clear()
        show_banner()

        if interactive:
            print(lab.narrative)
            input("\n[Press ENTER to begin lab...]")

        # Configure engine based on lab
        engine = Engine()
        engine.configure(
            lab.configuration.get("server_profile", "small-web"),
            lab.profile.upper(),
            lab.threads,
            lab.duration
        )

        clear()
        print(f"\n[*] Running Lab {lab.id}: {lab.name}")
        engine.run()
        live_dashboard(engine)

        if interactive:
            print(f"\n{lab.key_insight}")

    except ValueError as e:
        print(f"[!] {e}")


def validate_command(args):
    """Handle 'validate' subcommand."""
    clear()
    show_banner()

    print("\n[*] Validating NetLoader-X Configuration")
    print("=" * 60)

    try:
        validate_safety()
        print("[OK] Safety constraints validated")
    except RuntimeError as e:
        print(f"[!] {e}")
        return

    # Check imports
    try:
        from core.config import GlobalConfig, SAFETY_CAPS
        from core.engine import Engine
        from ui.menu import run_menu
        print("[OK] Core modules importable")
    except ImportError as e:
        print(f"[!] Import error: {e}")
        return

    # Check configuration
    from core.config import GlobalConfig
    config = GlobalConfig()
    print(f"[OK] Output directory: {config.OUTPUT_DIR}")
    print(f"[OK] Allowed hosts: {', '.join(GlobalConfig.ALLOWED_HOSTS)}")
    print(f"[OK] Port range: {GlobalConfig.ALLOWED_PORT_RANGE[0]}-{GlobalConfig.ALLOWED_PORT_RANGE[1]}")

    if getattr(args, "detailed", False):
        from core.config import dump_config
        print("\n[*] Full Configuration Dump:")
        import json
        config_dump = dump_config()
        print(json.dumps(config_dump, indent=2))

    print("\n[+] Validation complete - all systems ready")


def main():
    """Main entry point with CLI support."""
    cli = CLIParser()
    args = cli.parse()

    # Safety check at startup
    try:
        validate_safety()
    except RuntimeError as e:
        print(f"[!] Safety validation failed: {e}")
        sys.exit(1)

    command = getattr(args, "command", None)

    if command in ["run", "r", None]:
        # Default is 'run' command
        run_command(args)
    elif command in ["quick-test", "qt", "q"]:
        quick_test_mode(args)
    elif command in ["labs", "lab", "l"]:
        labs_command(args)
    elif command in ["validate", "check", "v"]:
        validate_command(args)
    else:
        cli.print_help()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[*] Simulation interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n[!] Error: {e}", file=sys.stderr)
        sys.exit(1)
