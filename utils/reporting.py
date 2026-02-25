"""
Additional report analysis helpers.
"""

import json
from pathlib import Path
from typing import Dict, List, Optional


def find_metric_files(root: Path) -> List[Path]:
    return sorted(root.rglob("metrics.json"))


def _safe_num(value, default=0.0) -> float:
    try:
        if value is None or isinstance(value, bool):
            return float(default)
        return float(value)
    except (TypeError, ValueError):
        return float(default)


def resolve_metrics_file(path_input: str) -> Optional[Path]:
    """
    Resolve a file/directory input to a specific metrics.json file.
    - If file is provided: return it.
    - If directory is provided: return latest metrics.json in that tree.
    """
    if not path_input:
        return None

    path = Path(path_input)
    if not path.exists():
        return None

    if path.is_file():
        return path

    files = find_metric_files(path)
    if not files:
        return None
    return max(files, key=lambda p: p.stat().st_mtime)


def load_metrics_payload(path_input: str) -> Optional[Dict]:
    metrics_file = resolve_metrics_file(path_input)
    if metrics_file is None:
        return None
    return json.loads(metrics_file.read_text(encoding="utf-8"))


def summarize_payload(payload: Dict, file_label: str = "<memory>") -> Dict:
    raw = payload.get("raw", [])

    if raw and "cluster_requests_total" in raw[-1]:
        cluster_requests = [_safe_num(row.get("cluster_requests_total", 0), 0.0) for row in raw]
        cluster_errors = [_safe_num(row.get("cluster_errors", 0), 0.0) for row in raw]
        cache_hit_rate = [_safe_num(row.get("db_cache_hit_rate", 0), 0.0) for row in raw]

        total_queue_points = []
        for row in raw:
            q_sum = 0.0
            for key, value in row.items():
                if key.endswith("_queue_depth"):
                    q_sum += _safe_num(value, 0.0)
            total_queue_points.append(q_sum)

        last = raw[-1] if raw else {}
        total_requests = _safe_num(last.get("cluster_requests_total", 0), 0.0)
        total_errors = _safe_num(last.get("cluster_errors", 0), 0.0)
        error_ratio = (total_errors / total_requests) if total_requests > 0 else 0.0

        return {
            "file": str(file_label),
            "mode": "cluster",
            "ticks": len(raw),
            "duration": payload.get("meta", {}).get("duration", 0),
            "peak_rps": round(max(cluster_requests, default=0.0), 2),
            "peak_latency_ms": 0.0,
            "peak_queue_depth": int(max(total_queue_points, default=0.0)),
            "avg_error_rate": round(error_ratio, 4),
            "peak_cluster_requests": round(max(cluster_requests, default=0.0), 2),
            "peak_cluster_errors": int(max(cluster_errors, default=0.0)),
            "avg_cache_hit_rate": round(
                (sum(cache_hit_rate) / len(cache_hit_rate)) if cache_hit_rate else 0.0,
                2,
            ),
            "lb_failed_requests": int(_safe_num(last.get("lb_failed_requests", 0), 0.0)),
        }

    peak_rps = max((row.get("requests_per_second", 0) for row in raw), default=0)
    peak_latency = max((row.get("latency_ms", 0) for row in raw), default=0)
    peak_queue = max((row.get("queue_depth", 0) for row in raw), default=0)
    avg_error = (
        sum((row.get("error_rate", 0) for row in raw)) / len(raw)
        if raw
        else 0
    )

    return {
        "file": str(file_label),
        "mode": "engine",
        "ticks": len(raw),
        "duration": payload.get("meta", {}).get("duration", 0),
        "peak_rps": round(peak_rps, 2),
        "peak_latency_ms": round(peak_latency, 2),
        "peak_queue_depth": int(peak_queue),
        "avg_error_rate": round(avg_error, 4),
    }


def analyze_metrics_file(path: Path) -> Dict:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return summarize_payload(payload, file_label=str(path))


def analyze_directory(input_dir: str) -> List[Dict]:
    root = Path(input_dir)
    if not root.exists():
        return []
    return [analyze_metrics_file(path) for path in find_metric_files(root)]


def build_debrief(payload: Dict, summary: Dict, label: str = "") -> Dict:
    raw = payload.get("raw", [])
    mode = summary.get("mode", "engine")
    timeline = []
    insights = []
    recommendations = []

    if mode == "engine":
        queue_limit = _safe_num(raw[0].get("queue_limit", 0), 0) if raw else 0

        high_queue_tick = None
        high_error_tick = None
        crash_tick = None
        recovery_tick = None

        for row in raw:
            tick = int(_safe_num(row.get("tick", 0), 0))
            queue = _safe_num(row.get("queue_depth", 0), 0)
            error = _safe_num(row.get("error_rate", 0), 0)
            crashed = bool(row.get("crashed", False))

            if high_queue_tick is None:
                if queue_limit > 0:
                    if queue >= queue_limit * 0.6:
                        high_queue_tick = tick
                elif queue >= 100:
                    high_queue_tick = tick
            if high_error_tick is None and error >= 0.12:
                high_error_tick = tick
            if crash_tick is None and crashed:
                crash_tick = tick
            if crash_tick is not None and recovery_tick is None and not crashed and error < 0.08 and tick > crash_tick:
                recovery_tick = tick

        if high_queue_tick is not None:
            timeline.append(f"Queue pressure crossed warning threshold at tick {high_queue_tick}.")
        if high_error_tick is not None:
            timeline.append(f"Error escalation began at tick {high_error_tick}.")
        if crash_tick is not None:
            timeline.append(f"Crash mode entered at tick {crash_tick}.")
        if recovery_tick is not None:
            timeline.append(f"Recovery window observed at tick {recovery_tick}.")

        peak_rps = _safe_num(summary.get("peak_rps", 0), 0)
        peak_latency = _safe_num(summary.get("peak_latency_ms", 0), 0)
        peak_queue = _safe_num(summary.get("peak_queue_depth", 0), 0)
        avg_error = _safe_num(summary.get("avg_error_rate", 0), 0)

        insights.append(
            f"Peak throughput reached {peak_rps:.2f} RPS with peak latency {peak_latency:.2f} ms."
        )
        insights.append(
            f"Average error rate was {avg_error:.2%} and peak queue depth reached {int(peak_queue)}."
        )

        if avg_error >= 0.15:
            recommendations.append("Reduce planned rate or increase queue controls before scaling threads.")
        if peak_latency >= 1500:
            recommendations.append("Tune timeout and recovery settings; latency climbed into severe range.")
        if crash_tick is not None:
            recommendations.append("Use lower jitter and smaller rate steps to study pre-crash signals.")
        if not recommendations:
            recommendations.append("Run a comparison against a higher-rate variant to find breaking points.")

    else:
        total_req = _safe_num(summary.get("peak_cluster_requests", summary.get("peak_rps", 0)), 0)
        peak_errors = _safe_num(summary.get("peak_cluster_errors", 0), 0)
        insights.append(
            f"Cluster processed up to {total_req:.0f} requests with peak error count {peak_errors:.0f}."
        )
        recommendations.append("Compare two load-balancer algorithms to observe distribution effects.")

    return {
        "label": label or summary.get("file", ""),
        "mode": mode,
        "summary": summary,
        "timeline": timeline,
        "insights": insights,
        "recommendations": recommendations,
    }


def format_debrief_text(debrief: Dict) -> str:
    lines = []
    lines.append("\nTeaching Debrief")
    lines.append("=" * 70)
    lines.append(f"Run   : {debrief.get('label', '')}")
    lines.append(f"Mode  : {debrief.get('mode', 'unknown')}")
    summary = debrief.get("summary", {})
    lines.append(f"Ticks : {summary.get('ticks', 0)}")
    lines.append(f"Dur   : {summary.get('duration', 0)} sec")
    lines.append("")

    lines.append("What Happened")
    lines.append("-" * 70)
    timeline = debrief.get("timeline", [])
    if timeline:
        lines.extend(f"- {item}" for item in timeline)
    else:
        lines.append("- No major transition markers detected.")

    lines.append("")
    lines.append("Key Insights")
    lines.append("-" * 70)
    lines.extend(f"- {item}" for item in debrief.get("insights", []))

    lines.append("")
    lines.append("Recommended Next Runs")
    lines.append("-" * 70)
    lines.extend(f"- {item}" for item in debrief.get("recommendations", []))
    return "\n".join(lines)


def compare_summaries(baseline: Dict, candidate: Dict) -> Dict:
    mode = baseline.get("mode", "engine")
    metrics = ["peak_rps", "peak_latency_ms", "peak_queue_depth", "avg_error_rate"]
    deltas = {}
    for key in metrics:
        deltas[key] = round(
            _safe_num(candidate.get(key, 0), 0.0) - _safe_num(baseline.get(key, 0), 0.0),
            4,
        )

    insights = []
    if deltas["peak_rps"] > 0 and deltas["avg_error_rate"] < 0:
        insights.append("Throughput increased while errors dropped, indicating stronger resilience.")
    if deltas["peak_latency_ms"] > 0 and deltas["peak_queue_depth"] > 0:
        insights.append("Latency and queue depth both increased; bottleneck likely shifted to queue pressure.")
    if deltas["avg_error_rate"] > 0 and deltas["peak_rps"] < 0:
        insights.append("Error amplification reduced effective throughput, suggesting saturation.")
    if not insights and all(abs(_safe_num(v, 0.0)) < 1e-9 for v in deltas.values()):
        insights.append("No meaningful metric difference detected between runs.")
    elif not insights:
        insights.append("Difference is moderate; run a wider sweep to isolate dominant factors.")

    return {
        "mode": mode,
        "baseline": baseline,
        "candidate": candidate,
        "deltas": deltas,
        "insights": insights,
    }


def format_compare_text(comp: Dict) -> str:
    base = comp.get("baseline", {})
    cand = comp.get("candidate", {})
    delta = comp.get("deltas", {})
    lines = []
    lines.append("\nComparison Report")
    lines.append("=" * 70)
    lines.append(f"Baseline : {base.get('file', '')}")
    lines.append(f"Candidate: {cand.get('file', '')}")
    lines.append(f"Mode     : {comp.get('mode', 'engine')}")
    lines.append("")
    lines.append("Metric Deltas (candidate - baseline)")
    lines.append("-" * 70)
    lines.append(f"Peak RPS       : {delta.get('peak_rps', 0):+.2f}")
    lines.append(f"Peak Latency   : {delta.get('peak_latency_ms', 0):+.2f} ms")
    lines.append(f"Peak Queue     : {delta.get('peak_queue_depth', 0):+}")
    lines.append(f"Avg Error Rate : {delta.get('avg_error_rate', 0):+.4f}")
    lines.append("")
    lines.append("Causal Notes")
    lines.append("-" * 70)
    lines.extend(f"- {item}" for item in comp.get("insights", []))
    return "\n".join(lines)


def score_summary(summary: Dict, mode: str = "balanced") -> float:
    """
    Score engine summaries for sweep ranking.
    Higher is better.
    """
    peak_rps = _safe_num(summary.get("peak_rps", 0), 0)
    peak_latency = _safe_num(summary.get("peak_latency_ms", 0), 0)
    peak_queue = _safe_num(summary.get("peak_queue_depth", 0), 0)
    avg_error = _safe_num(summary.get("avg_error_rate", 0), 0)

    if mode == "throughput":
        return round((peak_rps * 0.02) - (peak_latency * 0.004) - (avg_error * 120), 4)
    if mode == "stability":
        return round((peak_rps * 0.01) - (peak_latency * 0.008) - (peak_queue * 0.01) - (avg_error * 250), 4)
    return round((peak_rps * 0.015) - (peak_latency * 0.006) - (peak_queue * 0.006) - (avg_error * 180), 4)
