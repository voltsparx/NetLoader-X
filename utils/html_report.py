"""
HTML report generation utilities.

Design goals:
- Self-contained report (no external JS/CSS dependencies)
- Lightweight charts (SVG sparklines + CSS bar charts)
- Works for both single-server and cluster simulation outputs
"""

from __future__ import annotations

import html as _html
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple

MAX_CHART_POINTS = 240


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None or isinstance(value, bool):
            return float(default)
        return float(value)
    except (TypeError, ValueError):
        return float(default)


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        if value is None or isinstance(value, bool):
            return int(default)
        return int(value)
    except (TypeError, ValueError):
        return int(default)


def _slugify(text: str) -> str:
    out = []
    for ch in str(text or ""):
        if ch.isalnum():
            out.append(ch.lower())
        else:
            out.append("-")
    slug = "".join(out).strip("-")
    while "--" in slug:
        slug = slug.replace("--", "-")
    return slug or "chart"


def _downsample_xy(xs: List[float], ys: List[float], max_points: int = MAX_CHART_POINTS) -> Tuple[List[float], List[float]]:
    n = len(ys)
    if n == 0 or n <= max_points:
        return xs[:], ys[:]

    step = max(1, int(math.ceil(n / max_points)))
    out_xs = xs[::step]
    out_ys = ys[::step]

    # Ensure last point is kept for end-of-run readability.
    if out_xs and out_xs[-1] != xs[-1]:
        out_xs.append(xs[-1])
        out_ys.append(ys[-1])

    return out_xs, out_ys


def _series(raw: List[Dict[str, Any]], field: str, default: float = 0.0) -> List[float]:
    return [_safe_float(row.get(field, default), default=default) for row in raw]


def _truthy_count(raw: List[Dict[str, Any]], field: str) -> int:
    return sum(1 for row in raw if bool(row.get(field)))


def _svg_line_chart(
    chart_id: str,
    xs: List[float],
    ys: List[float],
    color: str = "#0f4c81",
    height: int = 160,
    width: int = 560,
) -> str:
    """
    Very small, self-contained SVG line chart. No axes, just a readable trend.
    """
    if not ys:
        return '<div class="chart-empty">No data</div>'

    xs_ds, ys_ds = _downsample_xy(xs, ys)
    n = len(ys_ds)
    if n == 0:
        return '<div class="chart-empty">No data</div>'

    margin = 18
    plot_w = max(10, width - (margin * 2))
    plot_h = max(10, height - (margin * 2))

    min_v = min(ys_ds)
    max_v = max(ys_ds)
    if abs(max_v - min_v) < 1e-9:
        max_v = min_v + 1.0

    def x_at(i: int) -> float:
        if n <= 1:
            return float(margin)
        return margin + (i / (n - 1)) * plot_w

    def y_at(v: float) -> float:
        t = (v - min_v) / (max_v - min_v)
        return margin + (1.0 - t) * plot_h

    points = [(x_at(i), y_at(v)) for i, v in enumerate(ys_ds)]
    line_points = " ".join(f"{x:.2f},{y:.2f}" for x, y in points)

    # Area fill under the curve for a more "finished" look.
    first_x, first_y = points[0]
    last_x, _last_y = points[-1]
    floor_y = margin + plot_h
    area_path = f"M {first_x:.2f},{floor_y:.2f} L {line_points} L {last_x:.2f},{floor_y:.2f} Z"

    grad_id = f"grad-{_slugify(chart_id)}"
    clip_id = f"clip-{_slugify(chart_id)}"

    return f"""
<svg class="spark" viewBox="0 0 {width} {height}" role="img" aria-label="chart {chart_id}">
  <defs>
    <linearGradient id="{grad_id}" x1="0" x2="0" y1="0" y2="1">
      <stop offset="0%" stop-color="{color}" stop-opacity="0.22"/>
      <stop offset="100%" stop-color="{color}" stop-opacity="0.02"/>
    </linearGradient>
    <clipPath id="{clip_id}">
      <rect x="{margin}" y="{margin}" width="{plot_w}" height="{plot_h}" rx="10" ry="10"></rect>
    </clipPath>
  </defs>

  <g clip-path="url(#{clip_id})">
    <path d="{area_path}" fill="url(#{grad_id})"></path>
    <polyline fill="none" stroke="{color}" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" points="{line_points}"></polyline>
  </g>
</svg>
""".strip()


def _extract_mode(raw: List[Dict[str, Any]]) -> str:
    if not raw:
        return "unknown"
    sample = raw[-1]
    if any(k in sample for k in ("requests_per_second", "latency_ms", "queue_depth", "error_rate")):
        return "engine"
    if any(k in sample for k in ("cluster_requests_total", "cluster_errors", "lb_algorithm", "db_total_queries")):
        return "cluster"
    return "unknown"


def _extract_highlights(data: Dict[str, Any]) -> Dict[str, Any]:
    raw = data.get("raw", []) or []
    mode = _extract_mode(raw)
    meta = data.get("meta", {}) or {}

    ticks = len(raw)
    duration = _safe_float(meta.get("duration", 0), 0.0)

    highlights: Dict[str, Any] = {
        "mode": mode,
        "ticks": ticks,
        "duration": duration,
    }

    if not raw:
        return highlights

    # Shared "state" counts if present.
    crashed = 0
    degraded = 0
    healthy = 0
    for row in raw:
        if bool(row.get("crashed")):
            crashed += 1
        elif bool(row.get("degraded")):
            degraded += 1
        else:
            healthy += 1
    highlights.update(
        {
            "state_healthy": healthy,
            "state_degraded": degraded,
            "state_crashed": crashed,
        }
    )

    if mode == "engine":
        rps = _series(raw, "requests_per_second", 0.0)
        latency = _series(raw, "latency_ms", 0.0)
        error = _series(raw, "error_rate", 0.0)
        queue_depth = _series(raw, "queue_depth", 0.0)
        cpu_pressure = _series(raw, "cpu_pressure", 0.0)

        highlights.update(
            {
                "peak_rps": max(rps) if rps else 0.0,
                "avg_rps": (sum(rps) / len(rps)) if rps else 0.0,
                "peak_latency_ms": max(latency) if latency else 0.0,
                "avg_latency_ms": (sum(latency) / len(latency)) if latency else 0.0,
                "peak_error_rate": max(error) if error else 0.0,
                "avg_error_rate": (sum(error) / len(error)) if error else 0.0,
                "peak_queue_depth": max(queue_depth) if queue_depth else 0.0,
                "avg_queue_depth": (sum(queue_depth) / len(queue_depth)) if queue_depth else 0.0,
                "peak_cpu_pressure": max(cpu_pressure) if cpu_pressure else 0.0,
                "avg_cpu_pressure": (sum(cpu_pressure) / len(cpu_pressure)) if cpu_pressure else 0.0,
            }
        )

        last = raw[-1] if raw else {}
        highlights.update(
            {
                "completed_total": _safe_int(last.get("completed", 0), 0),
                "timed_out_total": _safe_int(last.get("timed_out", 0), 0),
                "rejected_total": _safe_int(last.get("rejected", 0), 0),
                "generated_events_total": sum(_safe_int(r.get("generated_events", 0), 0) for r in raw),
                "dropped_events_total": sum(_safe_int(r.get("dropped_events", 0), 0) for r in raw),
            }
        )
    elif mode == "cluster":
        errors_total = _series(raw, "cluster_errors", 0.0)
        cache_hit_rate = _series(raw, "db_cache_hit_rate", 0.0)

        last = raw[-1] if raw else {}
        per_backend = last.get("lb_requests_per_backend") if isinstance(last.get("lb_requests_per_backend"), dict) else {}

        highlights.update(
            {
                "cluster_requests_total": _safe_int(last.get("cluster_requests_total", 0), 0),
                "cluster_errors_total": _safe_int(last.get("cluster_errors", 0), 0),
                "peak_cluster_errors": max(errors_total) if errors_total else 0.0,
                "avg_cache_hit_rate": (sum(cache_hit_rate) / len(cache_hit_rate)) if cache_hit_rate else 0.0,
                "lb_failed_requests_total": _safe_int(last.get("lb_failed_requests", 0), 0),
                "lb_requests_per_backend": per_backend,
            }
        )

    return highlights


def build_html_report(data: Dict[str, Any], attack_name: str = "simulation") -> str:
    """
    Build the report HTML as a string.

    Keeping this separate makes it easy to test report generation without file I/O.
    """
    raw: List[Dict[str, Any]] = data.get("raw", []) or []
    meta: Dict[str, Any] = data.get("meta", {}) or {}
    generated = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    safe_attack_name = _html.escape(str(attack_name or "run"))

    highlights = _extract_highlights(data)
    mode = highlights.get("mode", "unknown")

    ticks = [float(_safe_int(row.get("tick", i), i)) for i, row in enumerate(raw)]

    # Engine charts (most common run mode)
    rps_series = _series(raw, "requests_per_second", 0.0)
    latency_series = _series(raw, "latency_ms", 0.0)
    error_series_pct = [_safe_float(v, 0.0) * 100.0 for v in _series(raw, "error_rate", 0.0)]
    queue_series = _series(raw, "queue_depth", 0.0)
    cpu_series_pct = [_safe_float(v, 0.0) * 100.0 for v in _series(raw, "cpu_pressure", 0.0)]

    # Cluster charts (fallback)
    cluster_requests_series = _series(raw, "cluster_requests_total", 0.0)
    cluster_errors_series = _series(raw, "cluster_errors", 0.0)
    db_pool_series = _series(raw, "db_pool_available", 0.0)
    cache_hit_series = _series(raw, "db_cache_hit_rate", 0.0)

    def _fmt(v: Any, precision: int = 2) -> str:
        try:
            if v is None:
                return "0"
            if isinstance(v, bool):
                return "1" if v else "0"
            if isinstance(v, int):
                return str(v)
            f = float(v)
            return f"{f:.{precision}f}"
        except (TypeError, ValueError):
            return "0"

    def _kpi(label: str, value: str, hint: str = "") -> str:
        hint_html = f'<div class="kpi-hint">{_html.escape(hint)}</div>' if hint else ""
        return f"""
<div class="kpi">
  <div class="kpi-label">{_html.escape(label)}</div>
  <div class="kpi-value">{_html.escape(value)}</div>
  {hint_html}
</div>
""".strip()

    # Bar charts (CSS-based)
    def _bars(title: str, items: List[Tuple[str, float]], unit: str = "") -> str:
        filtered = [(name, float(val)) for name, val in items if float(val) >= 0]
        if not filtered:
            return ""
        max_v = max((v for _n, v in filtered), default=0.0)
        max_v = max(max_v, 1.0)
        rows = []
        for name, val in filtered:
            pct = min(100.0, (val / max_v) * 100.0)
            rows.append(
                f"""
<div class="bar-row">
  <div class="bar-label">{_html.escape(name)}</div>
  <div class="bar-track"><div class="bar-fill" style="width: {pct:.2f}%"></div></div>
  <div class="bar-value">{_html.escape(_fmt(val, 0) if unit == '' else _fmt(val, 2))}{_html.escape(unit)}</div>
</div>
""".strip()
            )
        return f"""
<div class="panel">
  <div class="panel-head">
    <h2>{_html.escape(title)}</h2>
  </div>
  <div class="bars">
    {''.join(rows)}
  </div>
</div>
""".strip()

    # KPI blocks
    kpis: List[str] = []
    kpis.append(_kpi("Run", safe_attack_name, hint="scenario / profile name"))
    kpis.append(_kpi("Generated", generated, hint="UTC"))
    kpis.append(_kpi("Mode", str(mode), hint="engine or cluster"))
    kpis.append(_kpi("Duration", f"{_fmt(meta.get('duration', highlights.get('duration', 0)), 2)} s"))
    kpis.append(_kpi("Ticks", str(_safe_int(meta.get("ticks", highlights.get("ticks", 0)), 0))))

    if mode == "engine":
        kpis.extend(
            [
                _kpi("Peak RPS", _fmt(highlights.get("peak_rps", 0.0), 2)),
                _kpi("Avg RPS", _fmt(highlights.get("avg_rps", 0.0), 2)),
                _kpi("Peak Latency", f"{_fmt(highlights.get('peak_latency_ms', 0.0), 2)} ms"),
                _kpi("Avg Latency", f"{_fmt(highlights.get('avg_latency_ms', 0.0), 2)} ms"),
                _kpi("Peak Error", f"{_fmt(_safe_float(highlights.get('peak_error_rate', 0.0)) * 100.0, 2)}%"),
                _kpi("Avg Error", f"{_fmt(_safe_float(highlights.get('avg_error_rate', 0.0)) * 100.0, 2)}%"),
            ]
        )
    elif mode == "cluster":
        kpis.extend(
            [
                _kpi("Requests Total", str(_safe_int(highlights.get("cluster_requests_total", 0), 0))),
                _kpi("Errors Total", str(_safe_int(highlights.get("cluster_errors_total", 0), 0))),
                _kpi("LB Failed", str(_safe_int(highlights.get("lb_failed_requests_total", 0), 0))),
                _kpi("Avg Cache Hit", f"{_fmt(highlights.get('avg_cache_hit_rate', 0.0), 2)}%"),
            ]
        )

    # Charts (SVG)
    charts: List[str] = []

    def _chart_card(title: str, subtitle: str, svg: str) -> str:
        return f"""
<div class="panel chart">
  <div class="panel-head">
    <h2>{_html.escape(title)}</h2>
    <div class="sub">{_html.escape(subtitle)}</div>
  </div>
  {svg}
</div>
""".strip()

    if raw:
        if any(v != 0.0 for v in rps_series) or any(v != 0.0 for v in latency_series) or any(v != 0.0 for v in error_series_pct):
            charts.append(_chart_card("Requests/s", "Throughput trend", _svg_line_chart("rps", ticks, rps_series, color="#0f4c81")))
            charts.append(_chart_card("Latency (ms)", "Response time trend", _svg_line_chart("latency", ticks, latency_series, color="#7c2d12")))
            charts.append(_chart_card("Error Rate (%)", "Failures trend", _svg_line_chart("error", ticks, error_series_pct, color="#991b1b")))
            charts.append(_chart_card("Queue Depth", "Backlog trend", _svg_line_chart("queue", ticks, queue_series, color="#065f46")))
            charts.append(_chart_card("CPU Pressure (%)", "Synthetic saturation", _svg_line_chart("cpu", ticks, cpu_series_pct, color="#1d4ed8")))
        elif any(v != 0.0 for v in cluster_requests_series) or any(v != 0.0 for v in cluster_errors_series):
            charts.append(_chart_card("Cluster Requests", "Total requests over time", _svg_line_chart("cluster-req", ticks, cluster_requests_series, color="#0f4c81")))
            charts.append(_chart_card("Cluster Errors", "Total errors over time", _svg_line_chart("cluster-err", ticks, cluster_errors_series, color="#991b1b")))
            charts.append(_chart_card("DB Pool Available", "Connections free", _svg_line_chart("db-pool", ticks, db_pool_series, color="#065f46")))
            charts.append(_chart_card("Cache Hit Rate (%)", "Cache effectiveness", _svg_line_chart("cache-hit", ticks, cache_hit_series, color="#1d4ed8")))

    # Bar charts
    state_bars = _bars(
        "Tick State Breakdown",
        [
            ("Healthy", float(highlights.get("state_healthy", 0))),
            ("Degraded", float(highlights.get("state_degraded", 0))),
            ("Crashed", float(highlights.get("state_crashed", 0))),
        ],
    )

    totals_items: List[Tuple[str, float]] = []
    if mode == "engine":
        totals_items = [
            ("Completed", float(_safe_int(highlights.get("completed_total", 0), 0))),
            ("Timed out", float(_safe_int(highlights.get("timed_out_total", 0), 0))),
            ("Rejected", float(_safe_int(highlights.get("rejected_total", 0), 0))),
            ("Generated events", float(_safe_int(highlights.get("generated_events_total", 0), 0))),
            ("Dropped events", float(_safe_int(highlights.get("dropped_events_total", 0), 0))),
        ]
    totals_bars = _bars("Totals", totals_items)

    backend_bars = ""
    if mode == "cluster" and isinstance(highlights.get("lb_requests_per_backend"), dict):
        backend_map = highlights.get("lb_requests_per_backend") or {}
        try:
            items = [(str(k), float(_safe_int(v, 0))) for k, v in backend_map.items()]
            items = sorted(items, key=lambda kv: kv[1], reverse=True)
            backend_bars = _bars("Load Balancer Distribution", items)
        except Exception:
            backend_bars = ""

    raw_preview = raw[-10:] if raw else []

    # Helpful links (same folder as metrics.html)
    links = """
<div class="links">
  <a href="metrics.json">metrics.json</a>
  <a href="metrics.csv">metrics.csv</a>
  <a href="summary.txt">summary.txt</a>
</div>
""".strip()

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>NetLoader-X Report - {safe_attack_name}</title>
  <style>
    :root {{
      --bg0: #071024;
      --bg1: #0b1630;
      --panel: rgba(255, 255, 255, 0.08);
      --panel2: rgba(255, 255, 255, 0.06);
      --border: rgba(255, 255, 255, 0.12);
      --text: #e6edf7;
      --muted: rgba(230, 237, 247, 0.72);
      --accent: #63b3ff;
      --accent2: #a7f3d0;
      --danger: #ff9a9a;
      --shadow: 0 18px 40px rgba(0,0,0,0.35);
      --mono: ui-monospace, SFMono-Regular, Menlo, Consolas, "Liberation Mono", monospace;
      --sans: "Segoe UI", Tahoma, system-ui, -apple-system, Arial, sans-serif;
    }}

    * {{ box-sizing: border-box; }}

    body {{
      margin: 0;
      padding: 28px 18px 60px;
      font-family: var(--sans);
      color: var(--text);
      background:
        radial-gradient(1000px 600px at 12% 0%, rgba(99,179,255,0.20), transparent 60%),
        radial-gradient(900px 520px at 88% 12%, rgba(167,243,208,0.14), transparent 62%),
        linear-gradient(180deg, var(--bg0), var(--bg1));
    }}

    .container {{
      max-width: 1120px;
      margin: 0 auto;
    }}

    .hero {{
      border: 1px solid var(--border);
      border-radius: 18px;
      background: linear-gradient(180deg, rgba(255,255,255,0.10), rgba(255,255,255,0.04));
      box-shadow: var(--shadow);
      padding: 22px 20px;
      margin-bottom: 18px;
      position: relative;
      overflow: hidden;
    }}

    .hero::before {{
      content: "";
      position: absolute;
      inset: -120px -120px auto auto;
      width: 340px;
      height: 340px;
      border-radius: 999px;
      background: radial-gradient(circle at 30% 30%, rgba(99,179,255,0.35), transparent 60%);
      filter: blur(1px);
      pointer-events: none;
    }}

    h1 {{
      margin: 0;
      font-size: 1.6rem;
      letter-spacing: 0.2px;
    }}

    .tagline {{
      margin-top: 6px;
      color: var(--muted);
      line-height: 1.35;
    }}

    .links {{
      margin-top: 14px;
      display: flex;
      gap: 10px;
      flex-wrap: wrap;
    }}

    .links a {{
      display: inline-flex;
      align-items: center;
      gap: 8px;
      padding: 8px 10px;
      border: 1px solid var(--border);
      border-radius: 999px;
      color: var(--text);
      text-decoration: none;
      background: rgba(255,255,255,0.05);
      transition: transform 120ms ease, background 120ms ease;
    }}
    .links a:hover {{
      transform: translateY(-1px);
      background: rgba(255,255,255,0.08);
    }}

    .grid-kpi {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 12px;
      margin-top: 16px;
    }}

    .kpi {{
      padding: 12px 12px 10px;
      border: 1px solid var(--border);
      border-radius: 14px;
      background: rgba(255,255,255,0.06);
      box-shadow: 0 10px 20px rgba(0,0,0,0.18);
    }}

    .kpi-label {{
      font-size: 0.82rem;
      color: var(--muted);
      letter-spacing: 0.2px;
    }}

    .kpi-value {{
      margin-top: 6px;
      font-size: 1.18rem;
      font-weight: 700;
    }}

    .kpi-hint {{
      margin-top: 4px;
      font-size: 0.78rem;
      color: rgba(230, 237, 247, 0.55);
    }}

    .layout {{
      display: grid;
      grid-template-columns: 1.15fr 0.85fr;
      gap: 14px;
      margin-top: 14px;
    }}

    @media (max-width: 960px) {{
      .layout {{
        grid-template-columns: 1fr;
      }}
    }}

    .panel {{
      border: 1px solid var(--border);
      border-radius: 16px;
      background: rgba(255,255,255,0.06);
      box-shadow: 0 14px 26px rgba(0,0,0,0.20);
      overflow: hidden;
      margin-bottom: 14px;
    }}

    .panel-head {{
      padding: 14px 14px 10px;
      border-bottom: 1px solid rgba(255,255,255,0.10);
      background: rgba(255,255,255,0.03);
    }}

    h2 {{
      margin: 0;
      font-size: 1.02rem;
      letter-spacing: 0.2px;
    }}

    .sub {{
      margin-top: 6px;
      color: rgba(230, 237, 247, 0.68);
      font-size: 0.86rem;
    }}

    .charts {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
      gap: 14px;
    }}

    .chart .spark {{
      display: block;
      width: 100%;
      height: auto;
      padding: 12px 12px 14px;
    }}

    .chart-empty {{
      padding: 14px;
      color: rgba(230,237,247,0.65);
    }}

    .bars {{
      padding: 12px 14px 14px;
    }}

    .bar-row {{
      display: grid;
      grid-template-columns: 140px 1fr 90px;
      gap: 10px;
      align-items: center;
      margin: 10px 0;
    }}

    @media (max-width: 520px) {{
      .bar-row {{
        grid-template-columns: 110px 1fr 80px;
      }}
    }}

    .bar-label {{
      color: rgba(230,237,247,0.80);
      font-size: 0.90rem;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }}

    .bar-track {{
      height: 10px;
      border-radius: 999px;
      border: 1px solid rgba(255,255,255,0.10);
      background: rgba(255,255,255,0.04);
      overflow: hidden;
    }}

    .bar-fill {{
      height: 100%;
      width: 0;
      border-radius: 999px;
      background: linear-gradient(90deg, rgba(99,179,255,0.90), rgba(167,243,208,0.85));
    }}

    .bar-value {{
      text-align: right;
      font-family: var(--mono);
      color: rgba(230,237,247,0.78);
      font-size: 0.86rem;
    }}

    details {{
      border-top: 1px solid rgba(255,255,255,0.10);
      padding: 12px 14px 14px;
    }}

    summary {{
      cursor: pointer;
      color: rgba(230,237,247,0.86);
      font-weight: 650;
    }}

    pre {{
      margin: 12px 0 0;
      padding: 12px;
      border-radius: 12px;
      border: 1px solid rgba(255,255,255,0.10);
      background: rgba(0,0,0,0.20);
      overflow: auto;
      font-family: var(--mono);
      font-size: 0.84rem;
      line-height: 1.35;
      color: rgba(230,237,247,0.92);
    }}

    .note {{
      padding: 12px 14px 14px;
      color: rgba(230,237,247,0.74);
      line-height: 1.5;
    }}

    .note ul {{ margin: 10px 0 0 18px; }}
  </style>
</head>
<body>
  <div class="container">
    <div class="hero">
      <h1>NetLoader-X Report</h1>
      <div class="tagline">Safe, offline load and failure simulation. No sockets. No real traffic. Localhost-only.</div>
      {links}
      <div class="grid-kpi">
        {''.join(kpis)}
      </div>
    </div>

    <div class="layout">
      <div>
        <div class="charts">
          {''.join(charts)}
        </div>
      </div>
      <div>
        {state_bars}
        {totals_bars}
        {backend_bars}

        <div class="panel">
          <div class="panel-head">
            <h2>Latest 10 Ticks</h2>
            <div class="sub">Raw tick snapshots (tail)</div>
          </div>
          <details open>
            <summary>Show data</summary>
            <pre>{_html.escape(json.dumps(raw_preview, indent=2))}</pre>
          </details>
        </div>

        <div class="panel">
          <div class="panel-head">
            <h2>Teaching Notes</h2>
            <div class="sub">How to read the trends</div>
          </div>
          <div class="note">
            <ul>
              <li>Queue growth usually appears before error spikes. Watch queue depth and CPU pressure first.</li>
              <li>If error rate rises while throughput falls, the simulated service is in degradation mode.</li>
              <li>Use this report to learn resilience patterns, not to generate real traffic.</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  </div>
</body>
</html>
"""


def generate_html_report(data: Dict[str, Any], path: str, attack_name: str = "simulation"):
    html_text = build_html_report(data, attack_name=attack_name)
    Path(path).write_text(html_text, encoding="utf-8")


def write_html_report(path, config, metrics_summary):
    """
    Backward-compatible wrapper.
    """
    output_path = Path(path) / "report.html"
    payload = {
        "meta": {
            "duration": getattr(config, "duration", 0),
            "ticks": metrics_summary.get("ticks", 0),
        },
        "raw": metrics_summary.get("raw", []),
    }
    generate_html_report(payload, str(output_path), attack_name=getattr(config, "scenario_name", "run"))
