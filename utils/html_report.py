# utils/html_report.py

import os
from datetime import datetime

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>NetLoader-X Report</title>
<style>
    body {{
        font-family: Arial, sans-serif;
        background: #0b1220;
        color: #e6e6e6;
        padding: 20px;
    }}
    h1, h2 {{
        color: #4aa3ff;
    }}
    table {{
        width: 100%;
        border-collapse: collapse;
        margin-top: 20px;
    }}
    th, td {{
        border: 1px solid #2c3e50;
        padding: 10px;
        text-align: left;
    }}
    th {{
        background-color: #12263a;
    }}
    .box {{
        background: #111c2f;
        padding: 15px;
        margin-top: 20px;
        border-left: 4px solid #4aa3ff;
    }}
    .footer {{
        margin-top: 40px;
        font-size: 12px;
        color: #888;
    }}
</style>
</head>
<body>

<h1>NetLoader-X Simulation Report</h1>

<div class="box">
<b>Scenario:</b> {scenario}<br>
<b>Target:</b> {target}<br>
<b>Duration:</b> {duration}s<br>
<b>Threads:</b> {threads}<br>
<b>Generated:</b> {timestamp}
</div>

<h2>Summary Metrics</h2>
<table>
<tr><th>Metric</th><th>Value</th></tr>
<tr><td>Total Requests</td><td>{total}</td></tr>
<tr><td>Successful</td><td>{success}</td></tr>
<tr><td>Failed</td><td>{fail}</td></tr>
<tr><td>Average Latency (s)</td><td>{avg_latency}</td></tr>
<tr><td>P95 Latency (s)</td><td>{p95_latency}</td></tr>
</table>

<h2>How This Simulation Works</h2>
<div class="box">
This load simulation models client-side request pressure using controlled threading,
rate limiting, and synthetic latency. No real network flooding occurs.
<br><br>
<b>Key Concepts Demonstrated:</b>
<ul>
<li>Thread scheduling and ramp-up behavior</li>
<li>Rate limiting (requests per second)</li>
<li>Latency distributions</li>
<li>Failure modeling</li>
<li>Metrics aggregation</li>
</ul>
This mirrors how defenders evaluate service resilience safely.
</div>

<div class="footer">
NetLoader-X • Author: voltsparx • Contact: voltsparx@gmail.com<br>
For defensive research & education only.
</div>

</body>
</html>
"""

def write_html_report(path, config, metrics_summary):
    html = HTML_TEMPLATE.format(
        scenario=config.scenario_name,
        target=f"{config.target}:{config.port}",
        duration=config.duration,
        threads=config.threads,
        timestamp=datetime.now().isoformat(),
        total=metrics_summary["total_requests"],
        success=metrics_summary["success"],
        fail=metrics_summary["failures"],
        avg_latency=f"{metrics_summary['avg_latency']:.4f}",
        p95_latency=f"{metrics_summary['p95_latency']:.4f}"
    )

    with open(os.path.join(path, "report.html"), "w", encoding="utf-8") as f:
        f.write(html)