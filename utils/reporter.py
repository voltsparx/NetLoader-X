"""
NetLoader-X report orchestrator.
"""

import csv
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

import core.config as cfg
from utils import html_report, logger


def _output_root() -> str:
    """
    Resolve the configured output directory to an absolute path.
    """
    base = cfg.BASE_OUTPUT_DIR
    if os.path.isabs(base):
        return base
    return os.path.join(os.getcwd(), base)


class Reporter:
    """
    Export simulation outputs in JSON, CSV, and HTML.
    """

    def __init__(self, attack_name: str):
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        safe_name = attack_name.replace(" ", "_").replace("/", "-")
        self.attack_name = safe_name
        self.folder = os.path.join(_output_root(), f"{safe_name}_{timestamp}")
        os.makedirs(self.folder, exist_ok=True)
        logger.log_info(f"Created report folder: {self.folder}")

    def export_json(self, data: Dict[str, Any]):
        path = os.path.join(self.folder, "metrics.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        logger.log_info(f"JSON report saved: {path}")

    def export_csv(self, data: Dict[str, Any]):
        raw = data.get("raw", [])
        if not raw:
            logger.log_warning("No raw tick data available for CSV export")
            return

        headers = sorted({k for row in raw for k in row.keys()})
        path = os.path.join(self.folder, "metrics.csv")
        with open(path, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=headers)
            writer.writeheader()
            for row in raw:
                writer.writerow({key: row.get(key, "") for key in headers})
        logger.log_info(f"CSV report saved: {path}")

    def export_html(self, data: Dict[str, Any]):
        path = os.path.join(self.folder, "metrics.html")
        html_report.generate_html_report(data, path, attack_name=self.attack_name)
        logger.log_info(f"HTML report saved: {path}")

    def export_text_summary(self, data: Dict[str, Any]):
        path = os.path.join(self.folder, "summary.txt")
        meta = data.get("meta", {})
        raw = data.get("raw", [])

        peak_rps = max((row.get("requests_per_second", 0) for row in raw), default=0)
        peak_latency = max((row.get("latency_ms", 0) for row in raw), default=0)
        peak_error = max((row.get("error_rate", 0) for row in raw), default=0)
        degraded_ticks = sum(1 for row in raw if row.get("degraded"))
        crashed_ticks = sum(1 for row in raw if row.get("crashed"))

        lines = [
            "NetLoader-X Summary",
            "=" * 32,
            f"Run: {self.attack_name}",
            f"Duration: {meta.get('duration', 0)} s",
            f"Ticks: {meta.get('ticks', 0)}",
            "",
            f"Peak requests per second: {peak_rps:.2f}",
            f"Peak latency (ms): {peak_latency:.2f}",
            f"Peak error rate: {peak_error:.4f}",
            f"Degraded ticks: {degraded_ticks}",
            f"Crashed ticks: {crashed_ticks}",
            "",
            "Interpretation:",
            "- High queue depth before high error rate indicates congestion buildup.",
            "- Sustained high latency with low throughput indicates saturation.",
            "- Tune worker capacity, queue limits, and retry budgets based on these results.",
            "",
        ]
        Path(path).write_text("\n".join(lines), encoding="utf-8")
        logger.log_info(f"Text summary saved: {path}")

    def export_all(self, data: Dict[str, Any]):
        self.export_json(data)
        self.export_csv(data)
        self.export_html(data)
        self.export_text_summary(data)
