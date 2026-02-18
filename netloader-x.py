#!/usr/bin/env python3
"""
NetLoader-X :: Main Entry Point
Defensive load and failure simulation framework.
"""

import json
import os
import sys
import threading
import time
import webbrowser
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from cli import CLIParser, show_guide
from core.cluster import LoadBalancerAlgorithm, ServerCluster
from core.cluster_config import ClusterConfigParser
from core.config import GlobalConfig, dump_config, set_output_dir, validate_safety
from core.engine import Engine
from core.guided_labs import LabManager
from core.metrics import MetricsCollector
from core.web_server import WebDashboard
from ui.banner import show_banner
from ui.dashboard import live_dashboard
from ui.menu import main_menu
from utils import logger
from utils.reporting import analyze_directory
from utils.reporter import Reporter


PROFILE_MAP = {
    "http": "HTTP",
    "burst": "BURST",
    "slow": "SLOW",
    "wave": "WAVE",
    "retry": "RETRY",
    "cache": "CACHE",
    "mixed": "MIXED",
}

MENU_PROFILE_MAP = {
    "1": "HTTP",
    "2": "BURST",
    "3": "SLOW",
    "4": "WAVE",
    "5": "RETRY",
    "6": "CACHE",
    "7": "MIXED",
}


def clear():
    os.system("cls" if os.name == "nt" else "clear")


def _run_engine(engine: Engine, show_dashboard: bool):
    if show_dashboard:
        worker = threading.Thread(target=engine.run, daemon=True)
        worker.start()
        live_dashboard(engine)
        worker.join()
    else:
        engine.run()


def _export_reports(engine: Engine, no_report: bool = False):
    if no_report:
        return None
    reporter = Reporter(engine.attack_name)
    reporter.export_all(engine.export_metrics())
    return reporter.folder


def interactive_mode(no_report: bool = False):
    clear()
    show_banner()
    menu_choice = main_menu()
    profile = MENU_PROFILE_MAP.get(menu_choice, "HTTP")

    threads = 50
    duration = 60

    engine = Engine()
    engine.configure("small-web", profile, threads, duration)

    confirm = input("[?] Start simulation? (yes/no): ").strip().lower()
    if confirm not in ("yes", "y"):
        return

    clear()
    _run_engine(engine, show_dashboard=True)
    report_folder = _export_reports(engine, no_report=no_report)
    if report_folder:
        print(f"\n[+] Reports exported to: {report_folder}")


def quick_test_mode(args):
    clear()
    show_banner()

    profile = PROFILE_MAP.get(getattr(args, "profile", "http"), "HTTP")
    duration = 10 if getattr(args, "short", False) else 30
    threads = 24 if getattr(args, "short", False) else 40
    show_dashboard = not getattr(args, "no_dashboard", getattr(args, "skip_dashboard", False))

    print("\n[*] Quick Test Mode")
    print(f"    Profile : {profile}")
    print(f"    Duration: {duration}s")
    print(f"    Threads : {threads}")

    engine = Engine()
    engine.configure(
        "small-web",
        profile,
        threads,
        duration,
        seed=getattr(args, "seed", None),
    )
    _run_engine(engine, show_dashboard=show_dashboard)

    report_folder = _export_reports(engine, no_report=getattr(args, "no_report", False))
    if report_folder:
        print(f"[+] Reports exported to: {report_folder}")


def run_command(args):
    clear()
    show_banner()

    if getattr(args, "batch", False) and not getattr(args, "profile", None):
        print("[!] Batch mode requires --profile")
        return

    profile_name = getattr(args, "profile", None)
    if not profile_name:
        interactive_mode(no_report=getattr(args, "no_report", False))
        return

    profile = PROFILE_MAP.get(profile_name, "HTTP")
    threads = getattr(args, "threads", 50)
    duration = getattr(args, "duration", 60)
    chaos = getattr(args, "chaos", False)
    chaos_rate = getattr(args, "chaos_rate", 0.05)
    batch = getattr(args, "batch", False)

    engine = Engine()
    engine.configure(
        "small-web",
        profile,
        threads=threads,
        duration=duration,
        seed=getattr(args, "seed", None),
        chaos_enabled=chaos,
        chaos_fault_rate=chaos_rate,
    )

    if not batch:
        confirm = input("\n[?] Start simulation? (yes/no): ").strip().lower()
        if confirm not in ("yes", "y"):
            return

    show_dashboard = not getattr(args, "no_dashboard", False)
    _run_engine(engine, show_dashboard=show_dashboard)
    report_folder = _export_reports(engine, no_report=getattr(args, "no_report", False))
    if report_folder:
        print(f"\n[+] Reports exported to: {report_folder}")


def labs_command(args):
    clear()
    show_banner()

    manager = LabManager()
    if getattr(args, "list", False):
        manager.list_labs()
        return

    if getattr(args, "description_only", False):
        lab = manager.get_lab(getattr(args, "lab", 1))
        print(f"\n{lab.name}")
        print("=" * 60)
        print(f"Difficulty: {lab.difficulty.name}")
        print(f"Objective : {lab.learning_objective}")
        print(f"Duration  : {lab.duration}s")
        print(f"\n{lab.description}")
        print(f"\nKey Insight: {lab.key_insight}")
        return

    lab_id = getattr(args, "lab", None)
    if not lab_id:
        manager.list_labs()
        try:
            lab_id = int(input("\n[?] Select lab (1-7): ").strip())
        except ValueError:
            return

    lab = manager.get_lab(lab_id)
    if getattr(args, "interactive", True):
        clear()
        show_banner()
        print(lab.narrative)
        input("\n[Press ENTER to begin lab]")

    engine = Engine()
    engine.configure(
        lab.configuration.get("server_profile", "small-web"),
        PROFILE_MAP.get(lab.profile.lower(), "HTTP"),
        threads=lab.threads,
        duration=lab.duration,
        slow_client_ratio=lab.configuration.get("slow_client_ratio", 0.1),
        chaos_enabled=lab.configuration.get("chaos_enabled", False),
        chaos_fault_rate=lab.configuration.get("fault_injection_rate", 0.05),
        seed=getattr(args, "seed", None),
    )

    _run_engine(engine, show_dashboard=True)
    report_folder = _export_reports(engine, no_report=getattr(args, "no_report", False))
    if report_folder:
        print(f"\n[+] Reports exported to: {report_folder}")
    print(f"\n[+] Key Insight: {lab.key_insight}")


def validate_command(args):
    clear()
    show_banner()

    print("\n[*] Validating NetLoader-X configuration")
    print("=" * 60)

    validate_safety()
    print("[OK] Safety constraints validated")
    print(f"[OK] Output directory: {GlobalConfig.OUTPUT_DIR}")
    print(f"[OK] Allowed hosts  : {', '.join(GlobalConfig.ALLOWED_HOSTS)}")
    low, high = GlobalConfig.ALLOWED_PORT_RANGE
    print(f"[OK] Port range     : {low}-{high}")

    if getattr(args, "detailed", False):
        print("\n[*] Full configuration:")
        print(json.dumps(dump_config(), indent=2))

    print("\n[+] Validation complete")


def cluster_command(args):
    clear()
    show_banner()

    if getattr(args, "example_config", False):
        print(ClusterConfigParser.create_example_yaml())
        return

    config = ClusterConfigParser.load_from_file(str(args.config))
    if getattr(args, "show_config", False):
        print(json.dumps(config, indent=2))
        return

    algorithm_name = getattr(args, "algorithm", None) or config["load_balancer"]["algorithm"]
    algorithm = LoadBalancerAlgorithm(algorithm_name)

    cluster = ServerCluster(
        lb_algorithm=algorithm,
        backends_config=config["load_balancer"]["backends"],
        db_pool_size=config["database"]["connection_pool"],
        db_cache_enabled=config["database"]["cache_enabled"],
    )
    cluster.start_all()

    metrics = MetricsCollector()
    duration = max(1, int(getattr(args, "duration", 60)))
    requests_per_tick = int(getattr(args, "rate", 0) or getattr(args, "threads", 100))
    requests_per_tick = max(1, requests_per_tick)

    for tick in range(duration):
        for _ in range(requests_per_tick):
            cluster.submit_request()
        snap = cluster.snapshot()
        snap["tick"] = tick
        snap["attack_profile"] = "CLUSTER"
        metrics.record(snap)
        time.sleep(1.0)

    cluster.stop_all()
    metrics.finalize()

    if getattr(args, "no_report", False):
        snap = metrics.export()
        last = snap["raw"][-1] if snap.get("raw") else {}
        print("\n[+] Cluster simulation complete (reports disabled).")
        print(f"    Requests total : {last.get('cluster_requests_total', 0)}")
        print(f"    Cluster errors : {last.get('cluster_errors', 0)}")
        print(f"    LB algorithm   : {last.get('lb_algorithm', algorithm.value)}")
        return

    reporter = Reporter(f"CLUSTER-{algorithm.value}")
    reporter.export_all(metrics.export())
    print(f"\n[+] Cluster simulation complete. Reports: {reporter.folder}")


def report_command(args):
    clear()
    show_banner()

    input_dir = getattr(args, "input_dir", None) or getattr(args, "output_dir", "outputs")
    summary = analyze_directory(input_dir)
    if not summary:
        print("[!] No metrics.json files found")
        return

    print("\n[*] Report Summary")
    print("=" * 80)
    for item in summary:
        mode = item.get("mode", "engine")
        print(f"File           : {item['file']}")
        print(f"Mode           : {mode}")
        print(f"Duration/Ticks : {item['duration']}s / {item['ticks']}")
        if mode == "cluster":
            print(f"Peak Requests  : {item.get('peak_cluster_requests', item.get('peak_rps', 0))}")
            print(f"Peak Errors    : {item.get('peak_cluster_errors', 0)}")
            print(f"Peak Queue Sum : {item.get('peak_queue_depth', 0)}")
            print(f"Avg Cache Hit  : {item.get('avg_cache_hit_rate', 0)}%")
            print(f"LB Failed Req  : {item.get('lb_failed_requests', 0)}")
            print(f"Error Ratio    : {item.get('avg_error_rate', 0)}")
        else:
            print(f"Peak RPS       : {item['peak_rps']}")
            print(f"Peak Latency   : {item['peak_latency_ms']} ms")
            print(f"Peak Queue     : {item['peak_queue_depth']}")
            print(f"Avg Error Rate : {item['avg_error_rate']}")
        print("-" * 80)


def web_command(args):
    clear()
    show_banner()

    engine = Engine()
    engine.configure("small-web", "WAVE", threads=32, duration=300)

    dashboard = WebDashboard(
        engine.metrics,
        host=getattr(args, "host", "127.0.0.1"),
        port=getattr(args, "port", 8080),
    )
    dashboard.start()

    if getattr(args, "auto_open", False):
        webbrowser.open(f"http://{dashboard.host}:{dashboard.port}")

    print("\n[*] Running background simulation for dashboard stream")
    try:
        engine.run()
    except KeyboardInterrupt:
        pass
    finally:
        dashboard.stop()


def main():
    cli = CLIParser()
    args = cli.parse()

    logger.set_verbose(getattr(args, "verbose", False))
    set_output_dir(getattr(args, "output_dir", "outputs"))

    try:
        validate_safety()
    except RuntimeError as exc:
        print(f"[!] Safety validation failed: {exc}")
        sys.exit(1)

    if getattr(args, "guide", False):
        show_guide()
        return

    command = getattr(args, "command", None)
    if command in [None, "run", "r"]:
        run_command(args)
    elif command in ["quick-test", "qt", "q"]:
        quick_test_mode(args)
    elif command in ["labs", "lab", "l"]:
        labs_command(args)
    elif command in ["validate", "check", "v"]:
        validate_command(args)
    elif command in ["cluster", "c", "cluster-test"]:
        cluster_command(args)
    elif command in ["report", "rep", "rp"]:
        report_command(args)
    elif command in ["web", "w", "dashboard"]:
        web_command(args)
    else:
        cli.print_help()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[*] Simulation interrupted by user")
        sys.exit(0)
    except Exception as exc:
        print(f"\n[!] Error: {exc}", file=sys.stderr)
        sys.exit(1)
