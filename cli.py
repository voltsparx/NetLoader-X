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

Author  : voltsparx
Contact : voltsparx@gmail.com
"""

import argparse
import sys
import os
from pathlib import Path


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
            prog="NetLoader-X",
            description="Defensive Load & Failure Simulation Framework",
            epilog="For educational and defensive testing only.",
            formatter_class=argparse.RawDescriptionHelpFormatter,
        )

        # Global options
        parser.add_argument(
            "--version",
            action="version",
            version="NetLoader-X v1.0.0-sim",
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


def main():
    """
    Entry point for CLI testing.
    """
    cli = CLIParser()
    args = cli.parse()

    if args.command is None:
        # Default: interactive menu mode
        from ui.menu import run_menu
        run_menu()
    else:
        print(f"Command: {args.command}")
        print(f"Args: {args}")


if __name__ == "__main__":
    main()
