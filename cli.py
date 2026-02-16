"""
NetLoader-X :: Command-Line Interface (CLI)
================================================
Modern argparse-based CLI for interactive and batch execution.

Supports:
  - Interactive menu mode (default)
  - Quick-test mode for demo
  - Custom profiles from YAML/JSON
  - Headless batch execution
  - Guided labs mode
  - Report-only mode

Metadata imported from core.metadata
"""

import argparse
import sys
import os
from pathlib import Path
from core.metadata import PROJECT_NAME, VERSION_STRING, PROJECT_TAGLINE


# Usage examples for help text
USAGE_EXAMPLES = f"""
Examples:

  For beginners (interactive menu):
    python netloader-x.py

  For quick demo (30-second test):
    python netloader-x.py quick-test

  To learn with guided labs:
    python netloader-x.py labs --list
    python netloader-x.py labs --lab 1

  For automation (CLI mode):
    python netloader-x.py run --profile http --threads 50 --duration 60
    python netloader-x.py run --profile burst --batch

  For cluster simulation (load balancer + backends):
    python netloader-x.py cluster --config cluster-config.yaml
    python netloader-x.py cluster --config cluster-config.yaml --algorithm least-connections
    python netloader-x.py cluster --config cluster-config.yaml --threads 200 --batch

  To verify configuration:
    python netloader-x.py validate --detailed

  For real-time web dashboard (requires Flask):
    python netloader-x.py web --port 8080
    # Then open http://127.0.0.1:8080 in your browser

  To see version:
    python netloader-x.py --version
"""


class CLIParser:
    """
    Handles all CLI argument parsing for NetLoader-X.
    """

    def __init__(self):
        self.parser = self._build_parser()

    def _build_parser(self) -> argparse.ArgumentParser:
        """
        Construct the main argument parser with all subcommands and options.
        """
        parser = argparse.ArgumentParser(
            prog=PROJECT_NAME,
            description=PROJECT_TAGLINE,
            epilog=USAGE_EXAMPLES,
            formatter_class=argparse.RawDescriptionHelpFormatter,
        )

        # Global options
        parser.add_argument(
            "--version",
            action="version",
            version=f"{PROJECT_NAME} {VERSION_STRING}",
            help="Show version information"
        )

        parser.add_argument(
            "--verbose", "-v",
            action="store_true",
            help="Enable verbose logging"
        )

        parser.add_argument(
            "--output-dir", "-o",
            default="outputs",
            help="Output directory for reports (default: outputs)"
        )

        parser.add_argument(
            "--config-file", "-c",
            type=Path,
            help="Path to custom YAML/JSON configuration file"
        )

        parser.add_argument(
            "--no-report",
            action="store_true",
            help="Skip report generation after simulation"
        )

        parser.add_argument(
            "--seed",
            type=int,
            help="Set random seed for deterministic runs"
        )

        parser.add_argument(
            "--guide",
            action="store_true",
            help="Interactive guide to help you choose the best method for your goals"
        )

        # Subcommands
        subparsers = parser.add_subparsers(
            dest="command",
            title="Commands",
            description="Available commands",
            help="Command to execute"
        )

        # Run command (default behavior)
        self._add_run_command(subparsers)

        # Quick-test command
        self._add_quicktest_command(subparsers)

        # Labs command
        self._add_labs_command(subparsers)

        # Validate command
        self._add_validate_command(subparsers)

        # Report command
        self._add_report_command(subparsers)

        # Web command
        self._add_web_command(subparsers)

        # Cluster command
        self._add_cluster_command(subparsers)

        return parser

    def _add_run_command(self, subparsers):
        """Add the 'run' subcommand for normal simulation execution."""
        run_parser = subparsers.add_parser(
            "run",
            help="Execute a simulation (interactive or batch mode)",
            aliases=["r"]
        )

        run_parser.add_argument(
            "--interactive", "-i",
            action="store_true",
            default=True,
            help="Use interactive menu mode (default)"
        )

        run_parser.add_argument(
            "--profile",
            choices=["http", "burst", "slow", "wave"],
            help="Attack profile (skip menu if provided)"
        )

        run_parser.add_argument(
            "--threads",
            type=int,
            default=50,
            help="Number of virtual clients (default: 50)"
        )

        run_parser.add_argument(
            "--duration",
            type=int,
            default=60,
            help="Simulation duration in seconds (default: 60)"
        )

        run_parser.add_argument(
            "--rate",
            type=int,
            help="Target request rate (RPS)"
        )

        run_parser.add_argument(
            "--batch",
            action="store_true",
            help="Run without interactive prompts (requires --profile)"
        )

    def _add_quicktest_command(self, subparsers):
        """Add the 'quick-test' subcommand for demonstration."""
        quicktest_parser = subparsers.add_parser(
            "quick-test",
            help="Run a quick demo with sensible defaults",
            aliases=["qt", "q"]
        )

        quicktest_parser.add_argument(
            "--profile",
            choices=["http", "burst", "slow", "wave"],
            default="http",
            help="Attack profile for quick test (default: http)"
        )

        quicktest_parser.add_argument(
            "--short",
            action="store_true",
            help="Run shorter test (10 seconds instead of 30)"
        )

        quicktest_parser.add_argument(
            "--skip-dashboard",
            action="store_true",
            help="Don't show live dashboard"
        )

    def _add_labs_command(self, subparsers):
        """Add the 'labs' subcommand for guided learning scenarios."""
        labs_parser = subparsers.add_parser(
            "labs",
            help="Run pre-set guided learning scenarios",
            aliases=["lab", "l"]
        )

        labs_parser.add_argument(
            "--list",
            action="store_true",
            help="List all available guided labs"
        )

        labs_parser.add_argument(
            "--lab",
            type=int,
            help="Run specific lab by number"
        )

        labs_parser.add_argument(
            "--interactive",
            action="store_true",
            default=True,
            help="Show educational content during lab (default)"
        )

        labs_parser.add_argument(
            "--description-only",
            action="store_true",
            help="Show lab description without running"
        )

    def _add_validate_command(self, subparsers):
        """Add the 'validate' subcommand for configuration validation."""
        validate_parser = subparsers.add_parser(
            "validate",
            help="Validate configuration and check safety constraints",
            aliases=["check", "v"]
        )

        validate_parser.add_argument(
            "--config",
            type=Path,
            help="Validate specific configuration file"
        )

        validate_parser.add_argument(
            "--detailed",
            action="store_true",
            help="Show detailed validation report"
        )

    def _add_report_command(self, subparsers):
        """Add the 'report' subcommand for report generation/analysis."""
        report_parser = subparsers.add_parser(
            "report",
            help="Generate or analyze existing simulation reports",
            aliases=["rep", "rp"]
        )

        report_parser.add_argument(
            "input_dir",
            nargs="?",
            help="Input directory with simulation results"
        )

        report_parser.add_argument(
            "--format",
            choices=["html", "csv", "json", "all"],
            default="all",
            help="Report format(s) to generate (default: all)"
        )

        report_parser.add_argument(
            "--template",
            choices=["basic", "detailed", "minimal"],
            default="detailed",
            help="HTML report template style (default: detailed)"
        )

        report_parser.add_argument(
            "--open",
            action="store_true",
            help="Open generated HTML report in browser"
        )

    def _add_web_command(self, subparsers):
        """Add the 'web' subcommand for real-time web dashboard."""
        web_parser = subparsers.add_parser(
            "web",
            help="Start real-time web-based dashboard",
            aliases=["w", "dashboard"]
        )

        web_parser.add_argument(
            "--port",
            type=int,
            default=8080,
            help="Port for web dashboard (default: 8080)"
        )

        web_parser.add_argument(
            "--host",
            default="127.0.0.1",
            help="Host to bind to (default: 127.0.0.1)"
        )

        web_parser.add_argument(
            "--auto-open",
            action="store_true",
            help="Automatically open dashboard in browser"
        )

    def _add_cluster_command(self, subparsers):
        """Add the 'cluster' subcommand for cluster simulation."""
        cluster_parser = subparsers.add_parser(
            "cluster",
            help="Simulate server clusters with load balancing",
            aliases=["c", "cluster-test"]
        )

        cluster_parser.add_argument(
            "--config",
            type=Path,
            required=True,
            help="Cluster configuration file (YAML or JSON)"
        )

        cluster_parser.add_argument(
            "--algorithm",
            choices=["round-robin", "least-connections", "random", "weighted-round-robin", "ip-hash"],
            help="Override load balancer algorithm from config"
        )

        cluster_parser.add_argument(
            "--threads",
            type=int,
            default=100,
            help="Number of client threads (default: 100)"
        )

        cluster_parser.add_argument(
            "--duration",
            type=int,
            default=60,
            help="Simulation duration in seconds (default: 60)"
        )

        cluster_parser.add_argument(
            "--rate",
            type=int,
            help="Target request rate (RPS)"
        )

        cluster_parser.add_argument(
            "--batch",
            action="store_true",
            help="Run without interactive prompts"
        )

        cluster_parser.add_argument(
            "--show-config",
            action="store_true",
            help="Display loaded configuration and exit"
        )

        cluster_parser.add_argument(
            "--example-config",
            action="store_true",
            help="Show example cluster configuration"
        )

    def parse(self, args=None) -> argparse.Namespace:
        """
        Parse command-line arguments.

        Args:
            args: List of arguments (default: sys.argv[1:])

        Returns:
            argparse.Namespace with parsed arguments
        """
        return self.parser.parse_args(args)

    def print_help(self):
        """Print help message."""
        self.parser.print_help()


def show_guide():
    """
    Interactive guide to help users choose the best method for their goals.
    """
    print("\n" + "=" * 70)
    print("🧭 NetLoader-X :: Interactive Guide")
    print("=" * 70)
    print("\nLet me help you choose the best method for your goals!\n")

    # Goal selection
    print("What's your primary goal? Select one:\n")
    goals = {
        "1": {
            "name": "Learn how NetLoader-X works",
            "desc": "Interactive tutorial with explanations",
            "recommended": "Guided Labs",
            "commands": [
                "python netloader-x.py labs --list  # See available labs",
                "python netloader-x.py labs --lab 1  # Start with Lab 1"
            ]
        },
        "2": {
            "name": "Quick demo (see it in action)",
            "desc": "30-second test with default settings",
            "recommended": "Quick-Test Mode",
            "commands": [
                "python netloader-x.py quick-test  # Run standard demo",
                "python netloader-x.py quick-test --short  # 10-second version"
            ]
        },
        "3": {
            "name": "Custom testing (hands-on control)",
            "desc": "Configure your own simulation parameters",
            "recommended": "Interactive Run Mode",
            "commands": [
                "python netloader-x.py run  # Menu-driven configuration",
                "python netloader-x.py run -i  # Explicit interactive mode"
            ]
        },
        "4": {
            "name": "Automation (scripts/CI/CD)",
            "desc": "Headless mode for integration into workflows",
            "recommended": "Batch CLI Mode",
            "commands": [
                "python netloader-x.py run --profile http --threads 100 --duration 60 --batch",
                "python netloader-x.py run --profile burst --rate 1000 --batch"
            ]
        },
        "5": {
            "name": "Validate before running",
            "desc": "Check configuration and safety constraints",
            "recommended": "Validate Command",
            "commands": [
                "python netloader-x.py validate --detailed",
                "python netloader-x.py validate --config custom.yaml"
            ]
        },
        "6": {
            "name": "Analyze existing results",
            "desc": "Generate reports from previous runs",
            "recommended": "Report Command",
            "commands": [
                "python netloader-x.py report ./outputs --format html",
                "python netloader-x.py report ./outputs --format all --open"
            ]
        }
    }

    for key, goal in goals.items():
        print(f"  {key}. {goal['name']}")
        print(f"     → {goal['desc']}\n")

    # Get user selection
    while True:
        choice = input("Enter your choice (1-6) or 'q' to quit: ").strip().lower()
        if choice == 'q':
            print("\nGoodbye! 👋")
            return
        if choice in goals:
            break
        print("❌ Invalid choice. Please enter 1-6 or 'q'.\n")

    selected = goals[choice]
    
    # Display recommendation
    print("\n" + "-" * 70)
    print(f"✨ RECOMMENDED: {selected['recommended']}")
    print("-" * 70 + "\n")
    print("Here are the commands to get started:\n")
    
    for i, cmd in enumerate(selected['commands'], 1):
        print(f"  {i}. {cmd}")
    
    print("\n💡 TIP: You can always use 'python netloader-x.py --help' for full options")
    print("        or 'python netloader-x.py <command> --help' for command-specific help\n")
    
    # Offer to run a command
    run_cmd = input("Would you like me to show the help for this command? (y/n): ").strip().lower()
    if run_cmd == 'y':
        if selected['recommended'] == "Guided Labs":
            os.system("python netloader-x.py labs --help")
        elif selected['recommended'] == "Quick-Test Mode":
            os.system("python netloader-x.py quick-test --help")
        elif selected['recommended'] == "Interactive Run Mode":
            os.system("python netloader-x.py run --help")
        elif selected['recommended'] == "Batch CLI Mode":
            os.system("python netloader-x.py run --help")
        elif selected['recommended'] == "Validate Command":
            os.system("python netloader-x.py validate --help")
        elif selected['recommended'] == "Report Command":
            os.system("python netloader-x.py report --help")


def main():
    """
    Entry point for CLI testing.
    """
    cli = CLIParser()
    args = cli.parse()

    # Check for guide flag first (takes precedence)
    if args.guide:
        show_guide()
        return

    if args.command is None:
        # Default: interactive menu mode
        from ui.menu import run_menu
        run_menu()
    else:
        print(f"Command: {args.command}")
        print(f"Args: {args}")


if __name__ == "__main__":
    main()
