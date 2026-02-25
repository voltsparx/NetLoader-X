import threading
import time

import pytest

from cli import CLIParser, render_explain_text
from core.cluster_config import ClusterConfigParser
from core.config import SAFETY_CAPS, USER_TUNABLE_LIMITS
from core.extensions import ExtensionPipeline, available_filter_names, available_plugin_names
from core.fake_server import FakeServerEngine, ServerProfile
from core.profiles import PROFILE_CATALOG
from core.scheduler import RampProfile, Scheduler
from core.web_server import HAS_FLASK, WebDashboard
from core.metrics import MetricsCollector
from targets.localhost import LocalhostSimulator
from utils.reporting import build_debrief, compare_summaries, summarize_payload


def _completed_after_burst(worker_count: int) -> int:
    profile = ServerProfile(max_queue=1000, base_latency=0.01, max_latency=0.05)
    server = FakeServerEngine(profile, worker_count=worker_count)
    server.start()
    try:
        for _ in range(80):
            server.submit_request()
        time.sleep(0.25)
        return int(server.snapshot().get("server_completed", 0))
    finally:
        server.stop()


def test_fake_server_worker_count_impacts_throughput():
    single_worker_completed = _completed_after_burst(worker_count=1)
    many_workers_completed = _completed_after_burst(worker_count=8)
    assert many_workers_completed > single_worker_completed


def test_scheduler_stop_not_blocked_when_paused():
    scheduler = Scheduler(RampProfile(100, 1000, 60), tick_interval=0.4)
    scheduler.start()
    scheduler.pause()

    tick_thread = threading.Thread(target=scheduler.next_tick)
    tick_thread.start()
    time.sleep(0.05)

    started = time.perf_counter()
    scheduler.stop()
    elapsed = time.perf_counter() - started

    tick_thread.join(timeout=1.0)
    assert elapsed < 0.2
    assert scheduler.running is False


def test_cluster_default_config_isolation():
    config_a = ClusterConfigParser.get_default_config()
    config_a["load_balancer"]["algorithm"] = "random"

    config_b = ClusterConfigParser.get_default_config()
    assert config_b["load_balancer"]["algorithm"] == "round-robin"


def test_cluster_config_rejects_excessive_workers():
    too_many_workers = SAFETY_CAPS["MAX_VIRTUAL_CLIENTS"] + 1
    config = {
        "load_balancer": {
            "algorithm": "round-robin",
            "backends": [{"name": "backend-a", "workers": too_many_workers}],
        },
        "database": {"connection_pool": 20, "cache_enabled": False},
    }
    with pytest.raises(ValueError):
        ClusterConfigParser.validate(config)


def test_cli_labs_supports_no_interactive_flag():
    parser = CLIParser()
    args = parser.parse(["labs", "--no-interactive"])
    assert args.interactive is False


def test_profiles_catalog_expanded_to_ten():
    assert len(PROFILE_CATALOG) >= 10
    assert {"SPIKE", "BROWNOUT", "RECOVERY"}.issubset(set(PROFILE_CATALOG.keys()))


def test_cli_accepts_runtime_extension_flags():
    parser = CLIParser()
    args = parser.parse(
        [
            "run",
            "--profile",
            "spike",
            "--threads",
            "120",
            "--duration",
            "45",
            "--rate",
            "5000",
            "--jitter",
            "0.2",
            "--plugins",
            "nano-coach",
            "trend-lens",
            "--filters",
            "latency-cap",
            "--queue-limit",
            "600",
            "--timeout-ms",
            "1600",
            "--crash-threshold",
            "0.9",
            "--recovery-rate",
            "0.08",
            "--error-floor",
            "0.03",
            "--nano-ai",
        ]
    )
    assert args.profile == "spike"
    assert args.plugins == ["nano-coach", "trend-lens"]
    assert args.filters == ["latency-cap"]
    assert args.nano_ai is True


def test_cli_supports_compare_and_sweep_commands():
    parser = CLIParser()
    compare_args = parser.parse(
        [
            "compare",
            "--baseline",
            "outputs\\run_a",
            "--candidate",
            "outputs\\run_b",
            "--json",
        ]
    )
    assert compare_args.command == "compare"
    assert compare_args.baseline_opt == "outputs\\run_a"
    assert compare_args.candidate_opt == "outputs\\run_b"
    assert compare_args.json is True

    sweep_args = parser.parse(
        [
            "sweep",
            "--profile",
            "spike",
            "--threads-values",
            "20,40",
            "--duration-values",
            "15,30",
            "--rate-values",
            "1000,3000",
            "--jitter-values",
            "0.05,0.10",
            "--score-mode",
            "balanced",
            "--top",
            "3",
        ]
    )
    assert sweep_args.command == "sweep"
    assert sweep_args.profile == "spike"
    assert sweep_args.top == 3


def test_render_explain_text_includes_selected_flag():
    text = render_explain_text(["run", "--threads", "100", "--rate", "4000", "--explain"])
    assert "--threads" in text
    assert "--rate" in text


def test_extension_pipeline_applies_plugin_and_filter():
    pipeline = ExtensionPipeline(
        plugin_names=[available_plugin_names()[0]],
        filter_names=[available_filter_names()[0]],
    )
    snapshot = {"requests_per_second": 100, "latency_ms": 2500, "error_rate": 0.1, "queue_depth": 5}
    out = pipeline.apply(snapshot)
    assert isinstance(out, dict)
    assert "latency_ms" in out


def test_reporting_debrief_and_compare_helpers():
    baseline_payload = {
        "meta": {"duration": 5, "ticks": 5},
        "raw": [
            {"tick": 0, "requests_per_second": 100, "latency_ms": 80, "queue_depth": 10, "error_rate": 0.01},
            {"tick": 1, "requests_per_second": 90, "latency_ms": 120, "queue_depth": 30, "error_rate": 0.05},
        ],
    }
    candidate_payload = {
        "meta": {"duration": 5, "ticks": 5},
        "raw": [
            {"tick": 0, "requests_per_second": 130, "latency_ms": 70, "queue_depth": 8, "error_rate": 0.01},
            {"tick": 1, "requests_per_second": 120, "latency_ms": 95, "queue_depth": 20, "error_rate": 0.03},
        ],
    }

    baseline_summary = summarize_payload(baseline_payload, "baseline")
    candidate_summary = summarize_payload(candidate_payload, "candidate")
    comp = compare_summaries(baseline_summary, candidate_summary)
    assert "deltas" in comp

    debrief = build_debrief(candidate_payload, candidate_summary, label="candidate")
    assert debrief["mode"] == "engine"
    assert len(debrief["insights"]) > 0


def test_localhost_simulator_clamps_override_limits():
    sim = LocalhostSimulator(
        "small-web",
        overrides={
            "queue_limit": USER_TUNABLE_LIMITS["queue_limit"]["max"] + 9999,
            "timeout_ms": USER_TUNABLE_LIMITS["timeout_ms"]["min"] - 100,
            "crash_threshold": USER_TUNABLE_LIMITS["crash_threshold"]["max"] + 1,
            "recovery_rate": USER_TUNABLE_LIMITS["recovery_rate"]["min"] - 1,
            "error_floor": USER_TUNABLE_LIMITS["error_floor"]["max"] + 1,
        },
    )
    assert sim.queue_limit == USER_TUNABLE_LIMITS["queue_limit"]["max"]
    assert sim.timeout_ms == USER_TUNABLE_LIMITS["timeout_ms"]["min"]
    assert sim.crash_threshold == USER_TUNABLE_LIMITS["crash_threshold"]["max"]
    assert sim.recovery_rate == USER_TUNABLE_LIMITS["recovery_rate"]["min"]
    assert sim.error_floor == USER_TUNABLE_LIMITS["error_floor"]["max"]


@pytest.mark.skipif(not HAS_FLASK, reason="Flask is optional")
def test_web_dashboard_stop_terminates_server_thread():
    dashboard = WebDashboard(MetricsCollector(), host="127.0.0.1", port=0)
    dashboard.start()
    time.sleep(0.2)
    dashboard.stop()

    assert dashboard.is_running is False
    if dashboard.server_thread is not None:
        assert dashboard.server_thread.is_alive() is False
