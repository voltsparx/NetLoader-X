"""
Additional report analysis helpers.
"""

import json
from pathlib import Path
from typing import Dict, List


def find_metric_files(root: Path) -> List[Path]:
    return sorted(root.rglob("metrics.json"))


def _safe_num(value, default=0.0) -> float:
    try:
        if value is None or isinstance(value, bool):
            return float(default)
        return float(value)
    except (TypeError, ValueError):
        return float(default)


def analyze_metrics_file(path: Path) -> Dict:
    payload = json.loads(path.read_text(encoding="utf-8"))
    raw = payload.get("raw", [])

    if raw and "cluster_requests_total" in raw[-1]:
        # Cluster mode summary
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
            "file": str(path),
            "mode": "cluster",
            "ticks": len(raw),
            "duration": payload.get("meta", {}).get("duration", 0),
            # Backward-compatible keys used by existing report command:
            "peak_rps": round(max(cluster_requests, default=0.0), 2),
            "peak_latency_ms": 0.0,
            "peak_queue_depth": int(max(total_queue_points, default=0.0)),
            "avg_error_rate": round(error_ratio, 4),
            # Cluster-specific extras:
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
        "file": str(path),
        "mode": "engine",
        "ticks": len(raw),
        "duration": payload.get("meta", {}).get("duration", 0),
        "peak_rps": round(peak_rps, 2),
        "peak_latency_ms": round(peak_latency, 2),
        "peak_queue_depth": int(peak_queue),
        "avg_error_rate": round(avg_error, 4),
    }


def analyze_directory(input_dir: str) -> List[Dict]:
    root = Path(input_dir)
    if not root.exists():
        return []
    return [analyze_metrics_file(path) for path in find_metric_files(root)]
