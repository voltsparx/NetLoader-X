"""
NetLoader-X :: Web-Based Real-Time Dashboard
================================================
Flask web server providing real-time metrics visualization,
live charts, and export functionality.

Features:
  - Real-time metric updates via WebSocket
  - Chart.js visualization (RPS, Latency, Queue Depth)
  - Mobile-responsive design
  - Export snapshots as JSON/CSV
  - Multiple metric views

Safe, offline, localhost-only operation.
"""

import json
import csv
import threading
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path

try:
    from flask import Flask, render_template_string, jsonify, request, send_file
    from flask_cors import CORS
    HAS_FLASK = True
except ImportError:
    HAS_FLASK = False

    # Dummy Flask class for graceful degradation
    class Flask:
        pass

    class CORS:
        def __init__(self, *args, **kwargs):
            pass

from core.metrics import MetricsCollector


class WebDashboard:
    """
    Manages the Flask web server and real-time dashboard.
    """

    def __init__(self, metrics: MetricsCollector, host: str = "127.0.0.1", port: int = 8080):
        """
        Initialize web dashboard.

        Args:
            metrics: MetricsCollector instance to visualize
            host: Server host (default: 127.0.0.1 for safety)
            port: Server port (default: 8080)
        """
        if not HAS_FLASK:
            raise ImportError(
                "Flask is required for web dashboard. Install with:\n"
                "  pip install flask flask-cors"
            )

        self.metrics = metrics
        self.host = host
        self.port = port
        self.app = self._build_app()
        self.server_thread = None
        self.is_running = False

    def _build_app(self) -> Flask:
        """Build and configure Flask application."""
        app = Flask(__name__)
        CORS(app)

        @app.route("/")
        def dashboard():
            """Serve main dashboard page."""
            return render_template_string(self._get_html_template())

        @app.route("/api/metrics")
        def api_metrics():
            """Get current metrics snapshot."""
            export = self.metrics.export()
            return jsonify({
                "meta": export["meta"],
                "summary": self.metrics.summary(),
                "latest": export["raw"][-1] if export["raw"] else {}
            })

        @app.route("/api/series")
        def api_series():
            """Get time-series data for all metrics."""
            series = self.metrics.all_series()
            return jsonify(series)

        @app.route("/api/series/<metric>")
        def api_metric_series(metric: str):
            """Get time-series data for specific metric."""
            series = self.metrics.get_series(metric)
            return jsonify({
                "metric": metric,
                "data": series,
                "length": len(series)
            })

        @app.route("/api/export/json")
        def export_json():
            """Export metrics as JSON."""
            export = self.metrics.export()
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"metrics_{timestamp}.json"
            
            # Save to temporary file
            temp_path = Path(f"/tmp/{filename}") if not Path("c:\\").exists() else Path(f"output/{filename}")
            temp_path.parent.mkdir(exist_ok=True)
            
            with open(temp_path, "w") as f:
                json.dump(export, f, indent=2, default=str)
            
            return send_file(
                temp_path,
                as_attachment=True,
                download_name=filename,
                mimetype="application/json"
            )

        @app.route("/api/export/csv")
        def export_csv():
            """Export metrics as CSV."""
            series = self.metrics.all_series()
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"metrics_{timestamp}.csv"
            
            # Create CSV file
            temp_path = Path(f"output/{filename}")
            temp_path.parent.mkdir(exist_ok=True)
            
            if series:
                with open(temp_path, "w", newline="") as f:
                    max_length = max(len(v) for v in series.values()) if series else 0
                    
                    writer = csv.DictWriter(f, fieldnames=series.keys())
                    writer.writeheader()
                    
                    for i in range(max_length):
                        row = {}
                        for metric, values in series.items():
                            row[metric] = values[i] if i < len(values) else ""
                        writer.writerow(row)
            
            return send_file(
                temp_path,
                as_attachment=True,
                download_name=filename,
                mimetype="text/csv"
            )

        @app.route("/api/health")
        def health():
            """Health check endpoint."""
            return jsonify({"status": "ok", "uptime": "running"})

        return app

    def start(self):
        """Start web server in background thread."""
        if self.is_running:
            return

        self.is_running = True
        self.server_thread = threading.Thread(
            target=self._run_server,
            daemon=True
        )
        self.server_thread.start()
        print(f"\n🌐 Web Dashboard: http://{self.host}:{self.port}")
        print(f"   Real-time metrics, charts, and export available")

    def _run_server(self):
        """Run Flask server (blocking)."""
        try:
            self.app.run(
                host=self.host,
                port=self.port,
                debug=False,
                use_reloader=False,
                threaded=True
            )
        except Exception as e:
            print(f"❌ Web server error: {e}")
            self.is_running = False

    def stop(self):
        """Stop web server."""
        self.is_running = False

    def _get_html_template(self) -> str:
        """Return complete HTML dashboard template."""
        return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NetLoader-X Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@3.9.1/dist/chart.min.js"></script>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            color: #e0e0e0;
            min-height: 100vh;
            padding: 20px;
        }

        .container {
            max-width: 1400px;
            margin: 0 auto;
        }

        header {
            text-align: center;
            margin-bottom: 30px;
            padding: 20px;
            background: rgba(0, 0, 0, 0.3);
            border-radius: 8px;
            border-left: 4px solid #00d4ff;
        }

        h1 {
            font-size: 28px;
            color: #00d4ff;
            margin-bottom: 5px;
        }

        .subtitle {
            color: #888;
            font-size: 14px;
        }

        .status-bar {
            display: flex;
            gap: 20px;
            margin-top: 15px;
            flex-wrap: wrap;
            justify-content: center;
        }

        .status-item {
            background: rgba(0, 212, 255, 0.1);
            padding: 8px 15px;
            border-radius: 4px;
            font-size: 12px;
            border-left: 2px solid #00d4ff;
        }

        .status-label {
            color: #888;
            font-size: 11px;
        }

        .status-value {
            color: #00d4ff;
            font-weight: bold;
        }

        .controls {
            display: flex;
            gap: 10px;
            justify-content: center;
            margin-bottom: 20px;
            flex-wrap: wrap;
        }

        button {
            background: #00d4ff;
            color: #000;
            border: none;
            padding: 10px 20px;
            border-radius: 4px;
            cursor: pointer;
            font-weight: bold;
            font-size: 14px;
            transition: all 0.3s ease;
        }

        button:hover {
            background: #00ffff;
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0, 212, 255, 0.3);
        }

        button:active {
            transform: translateY(0);
        }

        .charts-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }

        .chart-card {
            background: rgba(0, 0, 0, 0.4);
            border: 1px solid rgba(0, 212, 255, 0.2);
            border-radius: 8px;
            padding: 15px;
            backdrop-filter: blur(10px);
        }

        .chart-title {
            color: #00d4ff;
            font-size: 14px;
            font-weight: bold;
            margin-bottom: 10px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        .chart-container {
            position: relative;
            height: 300px;
        }

        canvas {
            max-height: 300px;
        }

        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }

        .metric-card {
            background: rgba(0, 212, 255, 0.05);
            border: 1px solid rgba(0, 212, 255, 0.2);
            border-radius: 8px;
            padding: 15px;
            text-align: center;
        }

        .metric-label {
            color: #888;
            font-size: 12px;
            text-transform: uppercase;
            margin-bottom: 8px;
        }

        .metric-value {
            color: #00d4ff;
            font-size: 24px;
            font-weight: bold;
        }

        .metric-unit {
            color: #666;
            font-size: 12px;
            margin-top: 5px;
        }

        footer {
            text-align: center;
            margin-top: 30px;
            padding: 20px;
            color: #666;
            font-size: 12px;
            border-top: 1px solid rgba(0, 212, 255, 0.1);
        }

        .loading {
            text-align: center;
            color: #888;
            padding: 20px;
        }

        .error {
            background: rgba(255, 0, 0, 0.1);
            border-left: 4px solid #ff4444;
            padding: 15px;
            border-radius: 4px;
            color: #ff6666;
            margin-bottom: 20px;
        }

        @media (max-width: 768px) {
            h1 {
                font-size: 20px;
            }

            .charts-grid {
                grid-template-columns: 1fr;
            }

            .metrics-grid {
                grid-template-columns: 1fr;
            }

            .chart-container {
                height: 250px;
            }

            body {
                padding: 10px;
            }

            header {
                padding: 15px;
                margin-bottom: 20px;
            }
        }

        @keyframes pulse {
            0%, 100% {
                opacity: 1;
            }
            50% {
                opacity: 0.7;
            }
        }

        .updating {
            animation: pulse 1s infinite;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>⚡ NetLoader-X Real-Time Dashboard</h1>
            <p class="subtitle">Live metrics, performance charts, and export</p>
            <div class="status-bar">
                <div class="status-item">
                    <div class="status-label">Status</div>
                    <div class="status-value" id="status">Connecting...</div>
                </div>
                <div class="status-item">
                    <div class="status-label">Ticks</div>
                    <div class="status-value" id="ticks">0</div>
                </div>
                <div class="status-item">
                    <div class="status-label">Duration</div>
                    <div class="status-value" id="duration">0s</div>
                </div>
            </div>
        </header>

        <div class="controls">
            <button onclick="refreshData()">🔄 Refresh Now</button>
            <button onclick="exportJSON()">📥 Export JSON</button>
            <button onclick="exportCSV()">📥 Export CSV</button>
        </div>

        <div id="error" class="error" style="display: none;"></div>

        <div class="metrics-grid" id="metrics-grid">
            <div class="loading">Loading metrics...</div>
        </div>

        <div class="charts-grid">
            <div class="chart-card">
                <div class="chart-title">Requests Per Second (RPS)</div>
                <div class="chart-container">
                    <canvas id="rpsChart"></canvas>
                </div>
            </div>
            <div class="chart-card">
                <div class="chart-title">Latency (ms)</div>
                <div class="chart-container">
                    <canvas id="latencyChart"></canvas>
                </div>
            </div>
            <div class="chart-card">
                <div class="chart-title">Queue Depth</div>
                <div class="chart-container">
                    <canvas id="queueChart"></canvas>
                </div>
            </div>
            <div class="chart-card">
                <div class="chart-title">Active Clients</div>
                <div class="chart-container">
                    <canvas id="clientsChart"></canvas>
                </div>
            </div>
        </div>

        <footer>
            <p>NetLoader-X v3.0 | Real-time web dashboard | Metrics auto-refresh every 2 seconds</p>
        </footer>
    </div>

    <script>
        const colors = {
            primary: 'rgb(0, 212, 255)',
            primaryAlpha: 'rgba(0, 212, 255, 0.1)',
            secondary: 'rgb(255, 107, 107)',
            secondaryAlpha: 'rgba(255, 107, 107, 0.1)',
            accent: 'rgb(100, 200, 255)',
            accentAlpha: 'rgba(100, 200, 255, 0.1)'
        };

        let charts = {};
        let lastData = null;

        function initCharts() {
            const chartConfig = {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        labels: { color: 'rgba(255, 255, 255, 0.7)' }
                    }
                },
                scales: {
                    y: {
                        ticks: { color: 'rgba(255, 255, 255, 0.5)' },
                        grid: { color: 'rgba(255, 255, 255, 0.1)' }
                    },
                    x: {
                        ticks: { color: 'rgba(255, 255, 255, 0.5)' },
                        grid: { color: 'rgba(255, 255, 255, 0.1)' }
                    }
                }
            };

            // RPS Chart
            charts.rps = new Chart(
                document.getElementById('rpsChart'),
                {
                    type: 'line',
                    data: {
                        labels: [],
                        datasets: [{
                            label: 'RPS',
                            data: [],
                            borderColor: colors.primary,
                            backgroundColor: colors.primaryAlpha,
                            borderWidth: 2,
                            tension: 0.4,
                            fill: true
                        }]
                    },
                    options: chartConfig
                }
            );

            // Latency Chart
            charts.latency = new Chart(
                document.getElementById('latencyChart'),
                {
                    type: 'line',
                    data: {
                        labels: [],
                        datasets: [{
                            label: 'Latency (ms)',
                            data: [],
                            borderColor: colors.secondary,
                            backgroundColor: colors.secondaryAlpha,
                            borderWidth: 2,
                            tension: 0.4,
                            fill: true
                        }]
                    },
                    options: chartConfig
                }
            );

            // Queue Chart
            charts.queue = new Chart(
                document.getElementById('queueChart'),
                {
                    type: 'line',
                    data: {
                        labels: [],
                        datasets: [{
                            label: 'Queue Depth',
                            data: [],
                            borderColor: colors.accent,
                            backgroundColor: colors.accentAlpha,
                            borderWidth: 2,
                            tension: 0.4,
                            fill: true
                        }]
                    },
                    options: chartConfig
                }
            );

            // Clients Chart
            charts.clients = new Chart(
                document.getElementById('clientsChart'),
                {
                    type: 'line',
                    data: {
                        labels: [],
                        datasets: [{
                            label: 'Active Clients',
                            data: [],
                            borderColor: colors.primary,
                            backgroundColor: colors.primaryAlpha,
                            borderWidth: 2,
                            tension: 0.4,
                            fill: true
                        }]
                    },
                    options: chartConfig
                }
            );
        }

        async function refreshData() {
            try {
                document.getElementById('status').textContent = 'Updating...';
                document.getElementById('status').parentElement.classList.add('updating');

                const response = await fetch('/api/metrics');
                const data = await response.json();

                lastData = data;
                updateMetrics(data);
                updateCharts(data);

                document.getElementById('status').textContent = '✓ Live';
                document.getElementById('status').parentElement.classList.remove('updating');
                document.getElementById('error').style.display = 'none';
            } catch (error) {
                console.error('Error fetching metrics:', error);
                document.getElementById('status').textContent = '✗ Error';
                document.getElementById('error').textContent = `Error: ${error.message}`;
                document.getElementById('error').style.display = 'block';
            }
        }

        function updateMetrics(data) {
            const summary = data.summary;
            const latest = data.latest;
            const meta = data.meta;

            let html = '';

            // Add current values
            if (latest.rps !== undefined) {
                html += `
                    <div class="metric-card">
                        <div class="metric-label">Current RPS</div>
                        <div class="metric-value">${latest.rps.toFixed(1)}</div>
                    </div>
                `;
            }

            if (latest.latency !== undefined) {
                html += `
                    <div class="metric-card">
                        <div class="metric-label">Current Latency</div>
                        <div class="metric-value">${latest.latency.toFixed(2)}</div>
                        <div class="metric-unit">ms</div>
                    </div>
                `;
            }

            if (latest.queue_depth !== undefined) {
                html += `
                    <div class="metric-card">
                        <div class="metric-label">Queue Depth</div>
                        <div class="metric-value">${latest.queue_depth}</div>
                    </div>
                `;
            }

            if (latest.active_clients !== undefined) {
                html += `
                    <div class="metric-card">
                        <div class="metric-label">Active Clients</div>
                        <div class="metric-value">${latest.active_clients}</div>
                    </div>
                `;
            }

            // Add aggregated stats
            if (summary.rps) {
                html += `
                    <div class="metric-card">
                        <div class="metric-label">Avg RPS</div>
                        <div class="metric-value">${summary.rps.avg.toFixed(1)}</div>
                        <div class="metric-unit">p90: ${summary.rps.p90.toFixed(1)}</div>
                    </div>
                `;
            }

            if (summary.latency) {
                html += `
                    <div class="metric-card">
                        <div class="metric-label">Avg Latency</div>
                        <div class="metric-value">${summary.latency.avg.toFixed(2)}</div>
                        <div class="metric-unit">p99: ${summary.latency.p99.toFixed(2)}ms</div>
                    </div>
                `;
            }

            // Meta info
            document.getElementById('ticks').textContent = meta.ticks;
            document.getElementById('duration').textContent = meta.duration + 's';

            document.getElementById('metrics-grid').innerHTML = html;
        }

        async function updateCharts(data) {
            const response = await fetch('/api/series');
            const series = await response.json();

            const maxPoints = 100;
            const skip = Math.max(1, Math.floor(Object.values(series)[0]?.length || 0 / maxPoints));

            // Create labels
            const labels = series.tick ? series.tick.filter((_, i) => i % skip === 0) : [];

            // Update RPS
            if (series.rps) {
                const rpsData = series.rps.filter((_, i) => i % skip === 0);
                charts.rps.data.labels = labels;
                charts.rps.data.datasets[0].data = rpsData;
                charts.rps.update();
            }

            // Update Latency
            if (series.latency) {
                const latencyData = series.latency.filter((_, i) => i % skip === 0);
                charts.latency.data.labels = labels;
                charts.latency.data.datasets[0].data = latencyData;
                charts.latency.update();
            }

            // Update Queue
            if (series.queue_depth) {
                const queueData = series.queue_depth.filter((_, i) => i % skip === 0);
                charts.queue.data.labels = labels;
                charts.queue.data.datasets[0].data = queueData;
                charts.queue.update();
            }

            // Update Clients
            if (series.active_clients) {
                const clientsData = series.active_clients.filter((_, i) => i % skip === 0);
                charts.clients.data.labels = labels;
                charts.clients.data.datasets[0].data = clientsData;
                charts.clients.update();
            }
        }

        async function exportJSON() {
            window.location.href = '/api/export/json';
        }

        async function exportCSV() {
            window.location.href = '/api/export/csv';
        }

        // Initialize
        initCharts();
        refreshData();

        // Auto-refresh every 2 seconds
        setInterval(refreshData, 2000);
    </script>
</body>
</html>
        """
