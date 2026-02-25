"""
NetLoader-X :: Command-Line Interface
"""

import argparse
from pathlib import Path

from core.extensions import available_filter_names, available_plugin_names
from core.metadata import PROJECT_NAME, PROJECT_TAGLINE, VERSION_STRING
from core.user_settings import get_default_output_dir


USAGE_EXAMPLES = """
Examples:
  python netloader-x.py
  python netloader-x.py quick-test --profile mixed --short
  python netloader-x.py run --profile retry --threads 80 --duration 90 --rate 2000 --jitter 0.12 --batch
  python netloader-x.py run --profile spike --plugins nano-coach trend-lens --filters latency-cap error-smooth
  python netloader-x.py run --profile recovery --queue-limit 800 --timeout-ms 1800 --crash-threshold 0.9 --recovery-rate 0.08
  python netloader-x.py run --profile brownout --threads 400 --rate 12000 --explain
  python netloader-x.py sweep --profile spike --threads-values 30,60,120 --rate-values 1500,4000
  python netloader-x.py compare "$HOME/netloader-x-output/run_a" "$HOME/netloader-x-output/run_b"
  python netloader-x.py debrief "$HOME/netloader-x-output"
  python netloader-x.py labs --list
  python netloader-x.py cluster --config cluster-config-example.yaml
  python netloader-x.py validate --detailed
"""


PROFILE_CHOICES = [
    "http",
    "burst",
    "slow",
    "wave",
    "retry",
    "cache",
    "mixed",
    "spike",
    "brownout",
    "recovery",
]

PLUGIN_CHOICES = available_plugin_names()
FILTER_CHOICES = available_filter_names()

FLAG_EXPLANATIONS = {
    "--threads": "Virtual clients in simulation. Higher values increase synthetic pressure.",
    "--duration": "Runtime length in seconds.",
    "--rate": "Planned request rate baseline for scheduler.",
    "--jitter": "Traffic randomness between 0.0 and 0.5.",
    "--queue-limit": "Simulated server queue capacity.",
    "--timeout-ms": "Synthetic timeout boundary in milliseconds.",
    "--crash-threshold": "CPU/pressure threshold where simulated crash mode starts.",
    "--recovery-rate": "Per-tick recovery speed after overload.",
    "--error-floor": "Minimum synthetic error baseline.",
    "--plugins": f"Enable one or more plugins: {', '.join(PLUGIN_CHOICES)}.",
    "--filters": f"Enable one or more filters: {', '.join(FILTER_CHOICES)}.",
    "--nano-ai": "Enable Nano AI runtime coach hints.",
    "--chaos": "Enable random fault injection.",
    "--chaos-rate": "Fault injection probability from 0.0 to 1.0.",
    "--profile": "Select attack profile behavior model.",
    "--no-dashboard": "Disable live terminal dashboard.",
    "--batch": "Run non-interactively without confirmation prompt.",
    "--seed": "Deterministic random seed for reproducible runs.",
    "--output-dir": "Directory where reports are written.",
    "--no-report": "Skip report file export.",
    "--debrief": "Show teaching debrief after simulation/report commands.",
    "--threads-values": "CSV list for sweep threads values.",
    "--duration-values": "CSV list for sweep duration values.",
    "--rate-values": "CSV list for sweep rate values.",
    "--jitter-values": "CSV list for sweep jitter values.",
    "--top": "Top ranked sweep results to print.",
    "--max-runs": "Hard cap on total sweep combinations.",
    "--score-mode": "Sweep ranking mode: balanced, throughput, stability.",
    "--baseline": "Baseline metrics file or folder for compare.",
    "--candidate": "Candidate metrics file or folder for compare.",
    "--json": "Output command result in JSON format.",
    "--explain": "Explain selected flags and safe usage examples.",
}


class CLIParser:
    """
    Handles argument parsing for all modes.
    """

    def __init__(self):
        self._common_parser = None
        self.parser = self._build_parser()

    @staticmethod
    def _add_runtime_tunable_flags(parser: argparse.ArgumentParser):
        parser.add_argument("--rate", type=int, default=None, help="Planned request rate baseline")
        parser.add_argument("--jitter", type=float, default=None, help="Traffic jitter between 0.0 and 0.5")
        parser.add_argument("--queue-limit", type=int, default=None, help="Simulated server queue limit")
        parser.add_argument("--timeout-ms", type=int, default=None, help="Simulated timeout threshold in ms")
        parser.add_argument("--crash-threshold", type=float, default=None, help="Crash threshold (0.70-0.99)")
        parser.add_argument("--recovery-rate", type=float, default=None, help="Recovery rate per tick (0.01-0.20)")
        parser.add_argument("--error-floor", type=float, default=None, help="Baseline error floor (0.0-0.20)")
        parser.add_argument(
            "--plugins",
            nargs="*",
            default=None,
            metavar="PLUGIN",
            help=f"Plugins to enable ({', '.join(PLUGIN_CHOICES)})",
        )
        parser.add_argument(
            "--filters",
            nargs="*",
            default=None,
            metavar="FILTER",
            help=f"Filters to enable ({', '.join(FILTER_CHOICES)})",
        )
        parser.add_argument("--nano-ai", action="store_true", help="Enable Nano AI coach hints")
        parser.add_argument("--debrief", action="store_true", help="Show teaching debrief after run")

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
            "--explain",
            action="store_true",
            default=None,
            help="Explain selected flags and safe examples",
        )
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
        self._add_compare_command(subparsers, parents=common_parents)
        self._add_debrief_command(subparsers, parents=common_parents)
        self._add_sweep_command(subparsers, parents=common_parents)
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
        self._add_runtime_tunable_flags(run_parser)
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
        quicktest_parser.add_argument("--threads", type=int, default=None, help="Override quick-test threads")
        quicktest_parser.add_argument("--duration", type=int, default=None, help="Override quick-test duration")
        quicktest_parser.add_argument("--short", action="store_true", help="Run 10-second demo")
        self._add_runtime_tunable_flags(quicktest_parser)
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
            dest="interactive",
            default=True,
            help="Show educational narration",
        )
        labs_parser.add_argument(
            "--no-interactive",
            action="store_false",
            dest="interactive",
            help="Disable educational narration",
        )
        labs_parser.add_argument("--description-only", action="store_true")
        self._add_runtime_tunable_flags(labs_parser)

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
        report_parser.add_argument("--debrief", action="store_true", help="Show teaching debrief for each file")

    def _add_compare_command(self, subparsers, parents=None):
        compare_parser = subparsers.add_parser(
            "compare",
            aliases=["cmp"],
            help="Compare two report runs with causal hints",
            parents=parents or [],
        )
        compare_parser.add_argument("baseline", nargs="?", default=None, help="Baseline metrics file or folder")
        compare_parser.add_argument("candidate", nargs="?", default=None, help="Candidate metrics file or folder")
        compare_parser.add_argument("--baseline", dest="baseline_opt", default=None, help="Baseline file/folder")
        compare_parser.add_argument("--candidate", dest="candidate_opt", default=None, help="Candidate file/folder")
        compare_parser.add_argument("--json", action="store_true", help="Print comparison as JSON")

    def _add_debrief_command(self, subparsers, parents=None):
        debrief_parser = subparsers.add_parser(
            "debrief",
            aliases=["dbf"],
            help="Generate teaching debrief for a run",
            parents=parents or [],
        )
        debrief_parser.add_argument(
            "input_path",
            nargs="?",
            default=None,
            help="metrics.json file or directory containing reports",
        )
        debrief_parser.add_argument("--json", action="store_true", help="Print debrief as JSON")

    def _add_sweep_command(self, subparsers, parents=None):
        sweep_parser = subparsers.add_parser(
            "sweep",
            aliases=["sw"],
            help="Run parameter sweep and rank outcomes",
            parents=parents or [],
        )
        sweep_parser.add_argument("--profile", choices=PROFILE_CHOICES, default="http")
        sweep_parser.add_argument("--threads-values", default="20,50,100")
        sweep_parser.add_argument("--duration-values", default="20,40")
        sweep_parser.add_argument("--rate-values", default="1000,3000,5000")
        sweep_parser.add_argument("--jitter-values", default="0.05,0.10,0.20")
        sweep_parser.add_argument("--top", type=int, default=5)
        sweep_parser.add_argument("--max-runs", type=int, default=36)
        sweep_parser.add_argument(
            "--score-mode",
            choices=["balanced", "throughput", "stability"],
            default="balanced",
        )
        sweep_parser.add_argument("--queue-limit", type=int, default=None)
        sweep_parser.add_argument("--timeout-ms", type=int, default=None)
        sweep_parser.add_argument("--crash-threshold", type=float, default=None)
        sweep_parser.add_argument("--recovery-rate", type=float, default=None)
        sweep_parser.add_argument("--error-floor", type=float, default=None)
        sweep_parser.add_argument(
            "--plugins",
            nargs="*",
            default=None,
            metavar="PLUGIN",
            help=f"Plugins to enable ({', '.join(PLUGIN_CHOICES)})",
        )
        sweep_parser.add_argument(
            "--filters",
            nargs="*",
            default=None,
            metavar="FILTER",
            help=f"Filters to enable ({', '.join(FILTER_CHOICES)})",
        )
        sweep_parser.add_argument("--nano-ai", action="store_true")
        sweep_parser.add_argument("--debrief", action="store_true", help="Show debrief for top result")
        sweep_parser.add_argument("--json", action="store_true", help="Print sweep result as JSON")

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
        cluster_parser.add_argument("--debrief", action="store_true", help="Show teaching debrief after run")
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
        parsed.explain = bool(
            getattr(common_ns, "explain", False) or getattr(parsed, "explain", False)
        )

        parsed.output_dir = (
            getattr(parsed, "output_dir", None)
            or getattr(common_ns, "output_dir", None)
            or get_default_output_dir()
        )

        if getattr(parsed, "seed", None) is None and getattr(common_ns, "seed", None) is not None:
            parsed.seed = common_ns.seed

        return parsed

    def print_help(self):
        self.parser.print_help()


def extract_selected_flags(raw_args):
    selected = []
    for token in raw_args or []:
        if not token.startswith("--"):
            continue
        flag = token.split("=", 1)[0].lower()
        if flag not in selected:
            selected.append(flag)
    return selected


def render_explain_text(raw_args=None) -> str:
    selected = [f for f in extract_selected_flags(raw_args) if f in FLAG_EXPLANATIONS and f != "--explain"]
    if not selected:
        selected = sorted(FLAG_EXPLANATIONS.keys())

    lines = []
    lines.append("\nFlag Explanation")
    lines.append("=" * 70)
    for flag in selected:
        lines.append(f"{flag}")
        lines.append(f"  {FLAG_EXPLANATIONS.get(flag, 'No description available.')}")
    lines.append("\nExamples")
    lines.append("  python netloader-x.py run --profile spike --threads 300 --rate 8000 --jitter 0.12")
    lines.append("  python netloader-x.py run --profile recovery --queue-limit 800 --timeout-ms 1800 --recovery-rate 0.08")
    lines.append("  python netloader-x.py run --profile mixed --plugins nano-coach trend-lens --filters latency-cap error-smooth")
    lines.append("  python netloader-x.py quick-test --profile brownout --nano-ai --explain")
    lines.append("  python netloader-x.py sweep --profile spike --threads-values 30,60,120 --rate-values 1500,3500")
    lines.append('  python netloader-x.py compare "$HOME/netloader-x-output/run_a" "$HOME/netloader-x-output/run_b"')
    lines.append('  python netloader-x.py debrief "$HOME/netloader-x-output"')
    return "\n".join(lines)


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
