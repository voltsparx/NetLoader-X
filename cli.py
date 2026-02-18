"""
NetLoader-X :: Command-Line Interface
"""

import argparse
from pathlib import Path

from core.metadata import PROJECT_NAME, PROJECT_TAGLINE, VERSION_STRING


USAGE_EXAMPLES = """
Examples:
  python netloader-x.py
  python netloader-x.py quick-test --profile mixed --short
  python netloader-x.py run --profile retry --threads 80 --duration 90 --batch
  python netloader-x.py labs --list
  python netloader-x.py cluster --config cluster-config-example.yaml
  python netloader-x.py validate --detailed
"""


PROFILE_CHOICES = ["http", "burst", "slow", "wave", "retry", "cache", "mixed"]


class CLIParser:
    """
    Handles argument parsing for all modes.
    """

    def __init__(self):
        self._common_parser = None
        self.parser = self._build_parser()

    def _build_parser(self) -> argparse.ArgumentParser:
        # Common/global flags should work both before and after the subcommand:
        #   python netloader-x.py --no-report quick-test ...
        #   python netloader-x.py quick-test ... --no-report
        common = argparse.ArgumentParser(add_help=False)
        common.add_argument("--verbose", "-v", action="store_true", default=None, help="Enable verbose output")
        common.add_argument("--output-dir", "-o", default=None, help="Output directory")
        common.add_argument("--seed", type=int, help="Random seed for deterministic runs")
        common.add_argument("--no-report", action="store_true", default=None, help="Disable report export")
        common.add_argument(
            "--guide",
            action="store_true",
            default=None,
            help="Interactive command selection guide",
        )
        self._common_parser = common

        parser = argparse.ArgumentParser(
            prog=PROJECT_NAME,
            description=PROJECT_TAGLINE,
            epilog=USAGE_EXAMPLES,
            formatter_class=argparse.RawDescriptionHelpFormatter,
            parents=[common],
        )

        parser.add_argument(
            "--version",
            action="version",
            version=f"{PROJECT_NAME} {VERSION_STRING}",
            help="Show version information",
        )

        subparsers = parser.add_subparsers(dest="command", title="Commands")
        common_parents = [common]
        self._add_run_command(subparsers, parents=common_parents)
        self._add_quicktest_command(subparsers, parents=common_parents)
        self._add_labs_command(subparsers, parents=common_parents)
        self._add_validate_command(subparsers, parents=common_parents)
        self._add_report_command(subparsers, parents=common_parents)
        self._add_web_command(subparsers, parents=common_parents)
        self._add_cluster_command(subparsers, parents=common_parents)
        return parser

    def _add_run_command(self, subparsers, parents=None):
        run_parser = subparsers.add_parser(
            "run",
            aliases=["r"],
            help="Run simulation",
            parents=parents or [],
        )
        run_parser.add_argument("--profile", choices=PROFILE_CHOICES, help="Simulation profile")
        run_parser.add_argument("--threads", type=int, default=50, help="Virtual client count")
        run_parser.add_argument("--duration", type=int, default=60, help="Duration in seconds")
        run_parser.add_argument("--batch", action="store_true", help="Run without prompts")
        run_parser.add_argument("--no-dashboard", action="store_true", help="Disable live dashboard")
        run_parser.add_argument(
            "--chaos",
            action="store_true",
            help="Enable random fault injection during simulation",
        )
        run_parser.add_argument("--chaos-rate", type=float, default=0.05, help="Chaos fault rate")

    def _add_quicktest_command(self, subparsers, parents=None):
        quicktest_parser = subparsers.add_parser(
            "quick-test",
            aliases=["qt", "q"],
            help="Run a fast demo",
            parents=parents or [],
        )
        quicktest_parser.add_argument(
            "--profile",
            choices=PROFILE_CHOICES,
            default="http",
            help="Profile for quick demo",
        )
        quicktest_parser.add_argument("--short", action="store_true", help="Run 10-second demo")
        # Back-compat: keep --skip-dashboard, but standardize on --no-dashboard everywhere.
        quicktest_parser.add_argument(
            "--no-dashboard",
            "--skip-dashboard",
            action="store_true",
            dest="no_dashboard",
            help="Disable live dashboard",
        )

    def _add_labs_command(self, subparsers, parents=None):
        labs_parser = subparsers.add_parser(
            "labs",
            aliases=["lab", "l"],
            help="Run guided labs",
            parents=parents or [],
        )
        labs_parser.add_argument("--list", action="store_true", help="List labs")
        labs_parser.add_argument("--lab", type=int, help="Run specific lab ID")
        labs_parser.add_argument(
            "--interactive",
            action="store_true",
            default=True,
            help="Show educational narration",
        )
        labs_parser.add_argument("--description-only", action="store_true")

    def _add_validate_command(self, subparsers, parents=None):
        validate_parser = subparsers.add_parser(
            "validate",
            aliases=["check", "v"],
            help="Validate configuration",
            parents=parents or [],
        )
        validate_parser.add_argument("--config", type=Path, help="Validate specific config file")
        validate_parser.add_argument("--detailed", action="store_true", help="Print full config")

    def _add_report_command(self, subparsers, parents=None):
        report_parser = subparsers.add_parser(
            "report",
            aliases=["rep", "rp"],
            help="Analyze existing report files",
            parents=parents or [],
        )
        report_parser.add_argument(
            "input_dir",
            nargs="?",
            default=None,
            help="Input folder (defaults to --output-dir)",
        )
        report_parser.add_argument(
            "--format",
            choices=["html", "csv", "json", "all"],
            default="all",
        )

    def _add_web_command(self, subparsers, parents=None):
        web_parser = subparsers.add_parser(
            "web",
            aliases=["w", "dashboard"],
            help="Start local web dashboard",
            parents=parents or [],
        )
        web_parser.add_argument("--port", type=int, default=8080)
        web_parser.add_argument("--host", default="127.0.0.1")
        web_parser.add_argument("--auto-open", action="store_true")

    def _add_cluster_command(self, subparsers, parents=None):
        cluster_parser = subparsers.add_parser(
            "cluster",
            aliases=["c", "cluster-test"],
            help="Run cluster simulation mode",
            parents=parents or [],
        )
        cluster_parser.add_argument("--config", type=Path, required=True)
        cluster_parser.add_argument(
            "--algorithm",
            choices=[
                "round-robin",
                "least-connections",
                "random",
                "weighted-round-robin",
                "ip-hash",
            ],
        )
        cluster_parser.add_argument("--threads", type=int, default=100)
        cluster_parser.add_argument("--duration", type=int, default=60)
        cluster_parser.add_argument("--rate", type=int)
        cluster_parser.add_argument("--batch", action="store_true")
        cluster_parser.add_argument("--show-config", action="store_true")
        cluster_parser.add_argument("--example-config", action="store_true")

    def parse(self, args=None) -> argparse.Namespace:
        common_ns, _ = self._common_parser.parse_known_args(args)
        parsed = self.parser.parse_args(args)

        # Reconcile duplicated global flags from root + subcommands.
        # This preserves flags set before the subcommand even when a subparser
        # would otherwise overwrite them with its own defaults.
        parsed.verbose = bool(
            getattr(common_ns, "verbose", False) or getattr(parsed, "verbose", False)
        )
        parsed.no_report = bool(
            getattr(common_ns, "no_report", False) or getattr(parsed, "no_report", False)
        )
        parsed.guide = bool(
            getattr(common_ns, "guide", False) or getattr(parsed, "guide", False)
        )

        parsed.output_dir = (
            getattr(parsed, "output_dir", None)
            or getattr(common_ns, "output_dir", None)
            or "outputs"
        )

        if getattr(parsed, "seed", None) is None and getattr(common_ns, "seed", None) is not None:
            parsed.seed = common_ns.seed

        return parsed

    def print_help(self):
        self.parser.print_help()


def show_guide():
    """
    Minimal interactive helper for selecting commands.
    """
    print("\n" + "=" * 70)
    print("NetLoader-X Interactive Guide")
    print("=" * 70)
    print("\nPick your goal:\n")

    goals = {
        "1": ("Learn concepts", "python netloader-x.py labs --list"),
        "2": ("Run a quick demo", "python netloader-x.py quick-test"),
        "3": ("Run a custom simulation", "python netloader-x.py run --profile http"),
        "4": ("Run cluster mode", "python netloader-x.py cluster --config cluster-config-example.yaml"),
        "5": ("Validate setup", "python netloader-x.py validate --detailed"),
    }

    for key, (name, _) in goals.items():
        print(f"  {key}. {name}")

    choice = input("\nEnter 1-5 or q: ").strip().lower()
    if choice == "q":
        return

    selected = goals.get(choice)
    if not selected:
        print("Invalid choice")
        return

    print("\nRecommended command:")
    print(selected[1])


def main():
    cli = CLIParser()
    args = cli.parse()
    if args.guide:
        show_guide()
        return

    if args.command is None:
        from ui.menu import run_menu

        run_menu()
    else:
        print(f"Command: {args.command}")
        print(f"Args: {args}")


if __name__ == "__main__":
    main()
