"""
NetLoader-X Reporting Engine
Author  : voltsparx
Contact : voltsparx@gmail.com

Generates:
- JSON (raw metrics)
- CSV (spreadsheet-ready)
- HTML (visual dashboard)
"""

import os
import json
import csv
import datetime

class ReportEngine:
    def __init__(self, base_dir, run_name):
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        self.output_dir = os.path.join(base_dir, f"{run_name}_{ts}")
        os.makedirs(self.output_dir, exist_ok=True)

    def save_json(self, metrics_snapshot):
        path = os.path.join(self.output_dir, "metrics.json")
        with open(path, "w") as f:
            json.dump(metrics_snapshot, f, indent=4)

    def save_csv(self, metrics_snapshot):
        path = os.path.join(self.output_dir, "metrics.csv")
        with open(path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Metric", "Value"])
            for k, v in metrics_snapshot.items():
                writer.writerow([k, v])

    def save_metadata(self, metadata):
        path = os.path.join(self.output_dir, "metadata.json")
        with open(path, "w") as f:
            json.dump(metadata, f, indent=4)

    def generate_html(self, metrics_snapshot, metadata):
        path = os.path.join(self.output_dir, "report.html")

        html = self._html_template(metrics_snapshot, metadata)

        with open(path, "w", encoding="utf-8") as f:
            f.write(html)

    def _html_template(self, metrics, meta):
        # Simple serialization for JS
        metrics_js = json.dumps(metrics)
        meta_js = json.dumps(meta)

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>NetLoader-X Report</title>

<style>
body {{
    font-family: Arial, sans-serif;
    background-color: #0b1c2d;
    color: #e6eef7;
    margin: 0;
    padding: 0;
}}

header {{
    background: #0a3d62;
    padding: 20px;
    text-align: center;
}}

section {{
    padding: 20px;
}}

.card {{
    background: #132f4c;
    border-radius: 6px;
    padding: 15px;
    margin-bottom: 20px;
}}

table {{
    width: 100%;
    border-collapse: collapse;
}}

th, td {{
    padding: 10px;
    border-bottom: 1px solid #2f4f6f;
}}

th {{
    text-align: left;
    color: #9ecbff;
}}

canvas {{
    background: #0f263d;
    padding: 10px;
    border-radius: 6px;
}}
</style>
</head>

<body>

<header>
<h1>NetLoader-X Defensive Load Report</h1>
<p>Author: voltsparx | Contact: voltsparx@gmail.com</p>
</header>

<section class="card">
<h2>Run Metadata</h2>
<table id="metaTable"></table>
</section>

<section class="card">
<h2>Metrics Summary</h2>
<table id="metricsTable"></table>
</section>

<section class="card">
<h2>Request & Connection Visualization</h2>
<canvas id="metricsChart"></canvas>
</section>

<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

<script>
const metrics = {metrics_js};
const metadata = {meta_js};

// Populate metadata table
const metaTable = document.getElementById("metaTable");
for (const key in metadata) {{
    const row = metaTable.insertRow();
    row.insertCell(0).innerText = key;
    row.insertCell(1).innerText = metadata[key];
}}

// Populate metrics table
const metricsTable = document.getElementById("metricsTable");
for (const key in metrics) {{
    const row = metricsTable.insertRow();
    row.insertCell(0).innerText = key;
    row.insertCell(1).innerText = metrics[key];
}}

// Chart
const ctx = document.getElementById("metricsChart").getContext("2d");

new Chart(ctx, {{
    type: 'bar',
    data: {{
        labels: [
            'Requests',
            'Failures',
            'Connections Opened',
            'Connections Closed'
        ],
        datasets: [{{
            label: 'Simulation Metrics',
            data: [
                metrics.requests,
                metrics.failures,
                metrics.connections_opened,
                metrics.connections_closed
            ],
            backgroundColor: [
                '#4da3ff',
                '#ff6b6b',
                '#6bff95',
                '#ffd56b'
            ]
        }}]
    }},
    options: {{
        responsive: true,
        plugins: {{
            legend: {{
                labels: {{ color: '#e6eef7' }}
            }}
        }},
        scales: {{
            x: {{ ticks: {{ color: '#e6eef7' }} }},
            y: {{ ticks: {{ color: '#e6eef7' }} }}
        }}
    }}
}});
</script>

</body>
</html>
"""