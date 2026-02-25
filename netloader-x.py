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
from itertools import product
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).parent))

from cli import CLIParser, render_explain_text, show_guide
from core.cluster import LoadBalancerAlgorithm, ServerCluster
from core.cluster_config import ClusterConfigParser
from core.config import GlobalConfig, dump_config, set_output_dir, validate_safety
from core.engine import Engine
from core.extensions import available_filter_names, available_plugin_names, parse_name_list
from core.guided_labs import LabManager
from core.metrics import MetricsCollector
from core.user_settings import get_default_output_dir
from core.web_server import WebDashboard
from ui.banner import show_banner
from ui.dashboard import live_dashboard
from ui.menu import main_menu
from utils import logger
from utils.reporting import (
    analyze_directory,
    build_debrief,
    compare_summaries,
    find_metric_files,
    format_compare_text,
    format_debrief_text,
    load_metrics_payload,
    resolve_metrics_file,
    score_summary,
    summarize_payload,
)
from utils.reporter import Reporter


PROFILE_MAP = {
    "http": "HTTP",
    "burst": "BURST",
    "slow": "SLOW",
    "wave": "WAVE",
    "retry": "RETRY",
    "cache": "CACHE",
    "mixed": "MIXED",
    "spike": "SPIKE",
    "brownout": "BROWNOUT",
    "recovery": "RECOVERY",
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


def _engine_kwargs_from_args(args):
    plugin_names = parse_name_list(getattr(args, "plugins", None))
    filter_names = parse_name_list(getattr(args, "filters", None))

    valid_plugins = set(available_plugin_names())
    valid_filters = set(available_filter_names())

    invalid_plugins = [name for name in plugin_names if name not in valid_plugins]
    invalid_filters = [name for name in filter_names if name not in valid_filters]
    if invalid_plugins:
        raise ValueError(
            f"Unknown plugins: {', '.join(invalid_plugins)}. "
            f"Available: {', '.join(sorted(valid_plugins))}"
        )
    if invalid_filters:
        raise ValueError(
            f"Unknown filters: {', '.join(invalid_filters)}. "
            f"Available: {', '.join(sorted(valid_filters))}"
        )

    return {
        "rate": getattr(args, "rate", None),
        "jitter": getattr(args, "jitter", None),
        "queue_limit": getattr(args, "queue_limit", None),
        "timeout_ms": getattr(args, "timeout_ms", None),
        "crash_threshold": getattr(args, "crash_threshold", None),
        "recovery_rate": getattr(args, "recovery_rate", None),
        "error_floor": getattr(args, "error_floor", None),
        "plugins": plugin_names,
        "filters": filter_names,
        "nano_ai": bool(getattr(args, "nano_ai", False)),
    }


def _parse_csv_values(raw: str, cast=float, low=None, high=None):
    values = []
    for chunk in str(raw or "").split(","):
        token = chunk.strip()
        if not token:
            continue
        value = cast(token)
        if low is not None and value < low:
            value = low
        if high is not None and value > high:
            value = high
        values.append(value)
    return values


def _latest_report_metrics(default_dir: str):
    root = Path(default_dir)
    if not root.exists():
        return None
    files = find_metric_files(root)
    if not files:
        return None
    return max(files, key=lambda p: p.stat().st_mtime)


def _print_debrief_for_payload(payload: dict, label: str = ""):
    summary = summarize_payload(payload, file_label=label or "<run>")
    debrief = build_debrief(payload, summary, label=label)
    print(format_debrief_text(debrief))
    return debrief


def _run_engine_fast(engine: Engine):
    max_ticks = max(1, int(engine.duration / engine.tick_interval))
    for tick in range(max_ticks):
        planned_rate = engine.scheduler.profile.rate_at(tick)
        engine.tick(planned_rate=planned_rate, scheduler_tick=tick)
    engine.metrics.finalize()


def interactive_mode(no_report: bool = False):
    clear()
    show_banner()
    state = main_menu()
    action = getattr(state, "action", "run")

    if action == "compare":
        compare_command(
            SimpleNamespace(
                baseline=getattr(state, "compare_baseline", None),
                candidate=getattr(state, "compare_candidate", None),
                json=False,
            )
        )
        return

    if action == "debrief":
        debrief_command(
            SimpleNamespace(
                input_path=getattr(state, "debrief_input", None),
                output_dir=GlobalConfig.OUTPUT_DIR,
                json=False,
            )
        )
        return

    if action == "sweep":
        sweep_spec = getattr(state, "sweep_spec", {}) or {}
        sweep_command(
            SimpleNamespace(
                profile=sweep_spec.get("profile", state.attack_profile),
                threads_values=sweep_spec.get("threads_values", "20,50,100"),
                duration_values=sweep_spec.get("duration_values", "20,40"),
                rate_values=sweep_spec.get("rate_values", "1000,3000,5000"),
                jitter_values=sweep_spec.get("jitter_values", "0.05,0.10,0.20"),
                top=sweep_spec.get("top", 5),
                max_runs=sweep_spec.get("max_runs", 36),
                score_mode=sweep_spec.get("score_mode", "balanced"),
                queue_limit=state.target_behavior.get("queue_limit"),
                timeout_ms=state.target_behavior.get("timeout_ms"),
                crash_threshold=state.target_behavior.get("crash_threshold"),
                recovery_rate=state.target_behavior.get("recovery_rate"),
                error_floor=state.target_behavior.get("error_floor"),
                plugins=state.plugins,
                filters=state.filters,
                nano_ai=state.nano_ai,
                seed=None,
                debrief=True,
                json=False,
            )
        )
        return

    profile = PROFILE_MAP.get(state.attack_profile, "HTTP")

    engine = Engine()
    engine.configure(
        "small-web",
        profile,
        threads=state.config["threads"],
        duration=state.config["duration"],
        rate=state.config["rate"],
        jitter=state.config["jitter"],
        queue_limit=state.target_behavior["queue_limit"],
        timeout_ms=state.target_behavior["timeout_ms"],
        crash_threshold=state.target_behavior["crash_threshold"],
        recovery_rate=state.target_behavior["recovery_rate"],
        error_floor=state.target_behavior["error_floor"],
        plugins=state.plugins,
        filters=state.filters,
        nano_ai=state.nano_ai,
    )

    clear()
    _run_engine(engine, show_dashboard=True)
    if state.auto_debrief:
        _print_debrief_for_payload(engine.export_metrics(), label=engine.attack_name)
    report_folder = _export_reports(engine, no_report=no_report)
    if report_folder:
        print(f"\n[+] Reports exported to: {report_folder}")


def quick_test_mode(args):
    clear()
    show_banner()

    profile = PROFILE_MAP.get(getattr(args, "profile", "http"), "HTTP")
    default_duration = 10 if getattr(args, "short", False) else 30
    default_threads = 24 if getattr(args, "short", False) else 40
    duration = int(getattr(args, "duration", None) or default_duration)
    threads = int(getattr(args, "threads", None) or default_threads)
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
        **_engine_kwargs_from_args(args),
    )
    clear()
    _run_engine(engine, show_dashboard=show_dashboard)
    if getattr(args, "debrief", False):
        _print_debrief_for_payload(engine.export_metrics(), label=engine.attack_name)

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
        **_engine_kwargs_from_args(args),
    )

    if not batch:
        confirm = input("\n[?] Start simulation? (yes/no): ").strip().lower()
        if confirm not in ("yes", "y"):
            return

    show_dashboard = not getattr(args, "no_dashboard", False)
    clear()
    _run_engine(engine, show_dashboard=show_dashboard)
    if getattr(args, "debrief", False):
        _print_debrief_for_payload(engine.export_metrics(), label=engine.attack_name)
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
        **_engine_kwargs_from_args(args),
    )

    clear()
    _run_engine(engine, show_dashboard=True)
    if getattr(args, "debrief", False):
        _print_debrief_for_payload(engine.export_metrics(), label=engine.attack_name)
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
    payload = metrics.export()

    if getattr(args, "no_report", False):
        last = payload["raw"][-1] if payload.get("raw") else {}
        print("\n[+] Cluster simulation complete (reports disabled).")
        print(f"    Requests total : {last.get('cluster_requests_total', 0)}")
        print(f"    Cluster errors : {last.get('cluster_errors', 0)}")
        print(f"    LB algorithm   : {last.get('lb_algorithm', algorithm.value)}")
        if getattr(args, "debrief", False):
            _print_debrief_for_payload(payload, label=f"CLUSTER-{algorithm.value}")
        return

    reporter = Reporter(f"CLUSTER-{algorithm.value}")
    reporter.export_all(payload)
    print(f"\n[+] Cluster simulation complete. Reports: {reporter.folder}")
    if getattr(args, "debrief", False):
        _print_debrief_for_payload(payload, label=f"CLUSTER-{algorithm.value}")


def report_command(args):
    clear()
    show_banner()

    input_dir = getattr(args, "input_dir", None) or getattr(args, "output_dir", get_default_output_dir())
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
        if getattr(args, "debrief", False):
            payload = load_metrics_payload(item["file"])
            if payload:
                print(format_debrief_text(build_debrief(payload, item, label=item["file"])))
                print("-" * 80)


def compare_command(args):
    baseline_input = getattr(args, "baseline_opt", None) or getattr(args, "baseline", None)
    candidate_input = getattr(args, "candidate_opt", None) or getattr(args, "candidate", None)

    if not baseline_input or not candidate_input:
        print("[!] compare requires baseline and candidate paths.")
        print("    Example: python netloader-x.py compare outputs/run_a outputs/run_b")
        return

    baseline_file = resolve_metrics_file(baseline_input)
    candidate_file = resolve_metrics_file(candidate_input)
    if baseline_file is None:
        print(f"[!] Baseline metrics file not found: {baseline_input}")
        return
    if candidate_file is None:
        print(f"[!] Candidate metrics file not found: {candidate_input}")
        return

    baseline_payload = load_metrics_payload(str(baseline_file))
    candidate_payload = load_metrics_payload(str(candidate_file))
    if not baseline_payload or not candidate_payload:
        print("[!] Failed to load metrics payload(s).")
        return

    baseline_summary = summarize_payload(baseline_payload, file_label=str(baseline_file))
    candidate_summary = summarize_payload(candidate_payload, file_label=str(candidate_file))
    comp = compare_summaries(baseline_summary, candidate_summary)

    if getattr(args, "json", False):
        print(json.dumps(comp, indent=2))
    else:
        print(format_compare_text(comp))


def debrief_command(args):
    input_path = getattr(args, "input_path", None)
    if not input_path:
        latest = _latest_report_metrics(getattr(args, "output_dir", get_default_output_dir()))
        if latest is None:
            print("[!] No metrics.json found. Provide a file/folder path.")
            return
        input_path = str(latest)

    metrics_file = resolve_metrics_file(input_path)
    if metrics_file is None:
        print(f"[!] Could not find metrics.json from: {input_path}")
        return

    payload = load_metrics_payload(str(metrics_file))
    if not payload:
        print("[!] Failed to load metrics payload.")
        return

    summary = summarize_payload(payload, file_label=str(metrics_file))
    debrief = build_debrief(payload, summary, label=str(metrics_file))
    if getattr(args, "json", False):
        print(json.dumps(debrief, indent=2))
    else:
        print(format_debrief_text(debrief))


def sweep_command(args):
    try:
        threads_values = _parse_csv_values(getattr(args, "threads_values", ""), cast=int, low=1)
        duration_values = _parse_csv_values(getattr(args, "duration_values", ""), cast=int, low=5)
        rate_values = _parse_csv_values(getattr(args, "rate_values", ""), cast=int, low=1)
        jitter_values = _parse_csv_values(getattr(args, "jitter_values", ""), cast=float, low=0.0, high=0.5)
    except ValueError as exc:
        print(f"[!] Invalid sweep values: {exc}")
        return

    if not all([threads_values, duration_values, rate_values, jitter_values]):
        print("[!] Sweep lists cannot be empty.")
        return

    max_runs = max(1, int(getattr(args, "max_runs", 36)))
    combinations = list(product(threads_values, duration_values, rate_values, jitter_values))
    if len(combinations) > max_runs:
        print(f"[*] Sweep combinations capped at {max_runs} (from {len(combinations)}).")
        combinations = combinations[:max_runs]

    profile = PROFILE_MAP.get(getattr(args, "profile", "http"), "HTTP")
    static_kwargs = _engine_kwargs_from_args(args)
    static_kwargs.pop("rate", None)
    static_kwargs.pop("jitter", None)

    print("\n[*] Running parameter sweep (fast mode, no real-time waits)")
    print(f"    Profile      : {profile}")
    print(f"    Combinations : {len(combinations)}")
    print(f"    Score mode   : {getattr(args, 'score_mode', 'balanced')}")

    results = []
    for idx, (threads, duration, rate, jitter) in enumerate(combinations, start=1):
        engine = Engine()
        kwargs = dict(static_kwargs)
        kwargs["rate"] = rate
        kwargs["jitter"] = jitter
        engine.configure(
            "small-web",
            profile,
            threads=threads,
            duration=duration,
            seed=getattr(args, "seed", None),
            **kwargs,
        )
        _run_engine_fast(engine)
        payload = engine.export_metrics()
        summary = summarize_payload(payload, file_label=f"sweep-{idx}")
        score = score_summary(summary, mode=getattr(args, "score_mode", "balanced"))
        results.append(
            {
                "index": idx,
                "config": {
                    "threads": threads,
                    "duration": duration,
                    "rate": rate,
                    "jitter": jitter,
                },
                "score": score,
                "summary": summary,
                "payload": payload,
            }
        )

    ranked = sorted(results, key=lambda item: item["score"], reverse=True)
    top_n = max(1, int(getattr(args, "top", 5)))
    top_rows = ranked[:top_n]

    if getattr(args, "json", False):
        output = [
            {
                "index": row["index"],
                "config": row["config"],
                "score": row["score"],
                "summary": row["summary"],
            }
            for row in top_rows
        ]
        print(json.dumps(output, indent=2))
    else:
        print("\n[*] Sweep Ranking")
        print("=" * 100)
        print("Rank  Score    Threads  Duration  Rate    Jitter  PeakRPS   PeakLat(ms)  AvgErr")
        print("-" * 100)
        for rank, row in enumerate(top_rows, start=1):
            cfg = row["config"]
            summary = row["summary"]
            print(
                f"{rank:<5} {row['score']:<8.2f} "
                f"{cfg['threads']:<8} {cfg['duration']:<9} {cfg['rate']:<7} {cfg['jitter']:<7.2f} "
                f"{summary.get('peak_rps', 0):<9.2f} {summary.get('peak_latency_ms', 0):<12.2f} "
                f"{summary.get('avg_error_rate', 0):.4f}"
            )
        print("-" * 100)

    if getattr(args, "debrief", False) and ranked:
        best = ranked[0]
        best_label = (
            "sweep-best "
            f"(threads={best['config']['threads']}, duration={best['config']['duration']}, "
            f"rate={best['config']['rate']}, jitter={best['config']['jitter']:.2f})"
        )
        _print_debrief_for_payload(best["payload"], label=best_label)


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
    raw_args = sys.argv[1:]
    args = cli.parse(raw_args)

    if getattr(args, "explain", False):
        print(render_explain_text(raw_args))
        return

    logger.set_verbose(getattr(args, "verbose", False))
    set_output_dir(getattr(args, "output_dir", get_default_output_dir()))
    print(f"[*] Output base directory: {GlobalConfig.OUTPUT_DIR}")

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
    elif command in ["compare", "cmp"]:
        compare_command(args)
    elif command in ["debrief", "dbf"]:
        debrief_command(args)
    elif command in ["sweep", "sw"]:
        sweep_command(args)
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
