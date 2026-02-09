"""
NetLoader-X :: Reporting & Evidence Engine
------------------------------------------------------
Generates structured output artifacts for each
simulation run.

Outputs:
- JSON (raw metrics)
- CSV (analysis-friendly)
- HTML (human-readable report with graphs)

NO real traffic.
NO protocol simulation.
Metrics are provided by abstract simulation engines.

Author  : voltsparx
Contact : voltsparx@gmail.com
------------------------------------------------------
"""

import os
import json
import csv
import time
from datetime import datetime
from typing import List, Dict


# ==================================================
# REPORT MANAGER
# ==================================================

class ReportManager:
    """
    Central reporting engine responsible for
    creating per-run directories and exporting
    simulation artifacts.
    """

    def __init__(self, base_dir="output"):
        self.base_dir = base_dir
        os.makedirs(self.base_dir, exist_ok=True)

    # --------------------------------------------------
    # RUN DIRECTORY
    # --------------------------------------------------

    def create_run_directory(self, scenario_name: str) -> str:
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        safe_name = scenario_name.replace(" ", "_").lower()
        run_dir = os.path.join(self.base_dir, f"{timestamp}_{safe_name}")

        os.makedirs(run_dir, exist_ok=True)
        return run_dir

    # --------------------------------------------------
    # METADATA
    # --------------------------------------------------

    def write_metadata(self, run_dir: str, metadata: Dict):
        path = os.path.join(run_dir, "metadata.json")
        metadata["generated_at"] = datetime.utcnow().isoformat() + "Z"

        with open(path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=4)

    # --------------------------------------------------
    # JSON EXPORT
    # --------------------------------------------------

    def export_json(self, run_dir: str, samples: List[Dict]):
        path = os.path.join(run_dir, "metrics.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(samples, f, indent=2)

    # --------------------------------------------------
    # CSV EXPORT
    # --------------------------------------------------

    def export_csv(self, run_dir: str, samples: List[Dict]):
        if not samples:
            return

        path = os.path.join(run_dir, "metrics.csv")
        fieldnames = samples[0].keys()

        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(samples)

    # --------------------------------------------------
    # HTML REPORT
    # --------------------------------------------------

    def export_html(self, run_dir: str, metadata: Dict, samples: List[Dict]):
        path = os.path.join(run_dir, "report.html")

        html = self._build_html(metadata, samples)

        with open(path, "w", encoding="utf-8") as f:
            f.write(html)

    # --------------------------------------------------
    # HTML BUILDER
    # --------------------------------------------------

    def _build_html(self, meta: Dict, samples: List[Dict]) -> str:
        timestamps = [s["timestamp"] for s in samples]
        rps = [s["rps"] for s in samples]
        latency = [s["latency_ms"] for s in samples]
        errors = [s["error_rate"] for s in samples]
        queue = [s["queue_depth"] for s in samples]

        return f"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>NetLoader-X Simulation Report</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<style>
body {{
    font-family: Arial, sans-serif;
    background: #0d1b2a;
    color: #e0e1dd;
    padding: 20px;
}}
h1, h2 {{
    color: #4da3ff;
}}
.card {{
    background: #1b263b;
    padding: 15px;
    margin-bottom: 20px;
    border-radius: 8px;
}}
canvas {{
    background: #ffffff;
    border-radius: 4px;
}}
table {{
    width: 100%;
    border-collapse: collapse;
}}
th, td {{
    border: 1px solid #415a77;
    padding: 6px;
    text-align: center;
}}
th {{
    background: #415a77;
}}
</style>
</head>

<body>

<h1>NetLoader-X Simulation Report</h1>

<div class="card">
<h2>Run Metadata</h2>
<pre>{json.dumps(meta, indent=2)}</pre>
</div>

<div class="card">
<h2>Requests Per Second</h2>
<canvas id="rpsChart"></canvas>
</div>

<div class="card">
<h2>Latency (ms)</h2>
<canvas id="latencyChart"></canvas>
</div>

<div class="card">
<h2>Queue Depth</h2>
<canvas id="queueChart"></canvas>
</div>

<div class="card">
<h2>Error Rate</h2>
<canvas id="errorChart"></canvas>
</div>

<script>
const labels = {timestamps};

function makeChart(id, label, data, color) {{
    new Chart(document.getElementById(id), {{
        type: 'line',
        data: {{
            labels: labels,
            datasets: [{{
                label: label,
                data: data,
                borderColor: color,
                fill: false
            }}]
        }},
        options: {{
            responsive: true,
            scales: {{
                x: {{ display: false }},
                y: {{ beginAtZero: true }}
            }}
        }}
    }});
}}

makeChart("rpsChart", "RPS", {rps}, "#4da3ff");
makeChart("latencyChart", "Latency (ms)", {latency}, "#ffb703");
makeChart("queueChart", "Queue Depth", {queue}, "#90dbf4");
makeChart("errorChart", "Error Rate", {errors}, "#ef476f");
</script>

</body>
</html>
"""

    # --------------------------------------------------
    # FULL PIPELINE
    # --------------------------------------------------

    def generate_full_report(
        self,
        scenario_name: str,
        metadata: Dict,
        metric_samples: List[Dict]
    ):
        run_dir = self.create_run_directory(scenario_name)
        self.write_metadata(run_dir, metadata)
        self.export_json(run_dir, metric_samples)
        self.export_csv(run_dir, metric_samples)
        self.export_html(run_dir, metadata, metric_samples)

        return run_dir