"""
NetLoader-X :: Local web dashboard server.
"""

import csv
import json
import threading
from datetime import datetime
from pathlib import Path

import core.config as cfg

try:
    from flask import Flask, jsonify, render_template_string, send_file
    from flask_cors import CORS
    from werkzeug.serving import make_server

    HAS_FLASK = True
except ImportError:
    HAS_FLASK = False

from core.metrics import MetricsCollector


class WebDashboard:
    """
    Serve metrics over a local Flask UI.
    """

    def __init__(self, metrics: MetricsCollector, host: str = "127.0.0.1", port: int = 8080):
        if not HAS_FLASK:
            raise ImportError("Flask required. Install with: pip install flask flask-cors")
        self.metrics = metrics
        self.host = host
        self.port = port
        self.app = self._build_app()
        self.server_thread = None
        self.is_running = False
        self._server_lock = threading.Lock()
        self._http_server = None

    def _build_app(self):
        app = Flask(__name__)
        CORS(app)

        @app.route("/")
        def dashboard():
            return render_template_string(self._template())

        @app.route("/api/metrics")
        def api_metrics():
            payload = self.metrics.export()
            return jsonify(
                {
                    "meta": payload["meta"],
                    "latest": payload["raw"][-1] if payload["raw"] else {},
                    "aggregates": payload["aggregates"],
                }
            )

        @app.route("/api/series")
        def api_series():
            return jsonify(self.metrics.all_series())

        @app.route("/api/export/json")
        def export_json():
            payload = self.metrics.export()
            filename = f"metrics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            out = Path(cfg.BASE_OUTPUT_DIR) / filename
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
            return send_file(out, as_attachment=True, download_name=filename, mimetype="application/json")

        @app.route("/api/export/csv")
        def export_csv():
            payload = self.metrics.export()
            raw = payload.get("raw", [])
            filename = f"metrics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            out = Path(cfg.BASE_OUTPUT_DIR) / filename
            out.parent.mkdir(parents=True, exist_ok=True)

            headers = sorted({k for row in raw for k in row.keys()}) if raw else []
            with open(out, "w", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(handle, fieldnames=headers)
                if headers:
                    writer.writeheader()
                    for row in raw:
                        writer.writerow({k: row.get(k, "") for k in headers})
            return send_file(out, as_attachment=True, download_name=filename, mimetype="text/csv")

        @app.route("/api/health")
        def health():
            return jsonify({"status": "ok"})

        return app

    def start(self):
        if self.is_running:
            return
        self.is_running = True
        self.server_thread = threading.Thread(target=self._run_server, daemon=True)
        self.server_thread.start()
        print(f"\nWeb Dashboard: http://{self.host}:{self.port}")

    def _run_server(self):
        try:
            with self._server_lock:
                self._http_server = make_server(self.host, self.port, self.app, threaded=True)
            self._http_server.serve_forever()
        except Exception as exc:
            print(f"Web server error: {exc}")
        finally:
            with self._server_lock:
                if self._http_server is not None:
                    try:
                        self._http_server.server_close()
                    except Exception:
                        pass
                    self._http_server = None
            self.is_running = False

    def stop(self):
        with self._server_lock:
            server = self._http_server
        if server is not None:
            try:
                server.shutdown()
            except Exception:
                pass
        if self.server_thread and self.server_thread.is_alive():
            self.server_thread.join(timeout=2.0)
        self.is_running = False

    @staticmethod
    def _template() -> str:
        return """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>NetLoader-X Dashboard</title>
  <style>
    body { font-family: "Segoe UI", Tahoma, sans-serif; background: #f7f9fc; margin: 0; padding: 24px; color: #1f2937; }
    .wrap { max-width: 960px; margin: 0 auto; }
    .card { background: #fff; border: 1px solid #dde6f2; border-radius: 8px; padding: 16px; margin-bottom: 16px; }
    h1 { margin: 0 0 10px; color: #114c80; }
    table { width: 100%; border-collapse: collapse; }
    th, td { border: 1px solid #e7edf6; padding: 8px; text-align: left; }
    th { background: #eef4fb; }
    .actions a { margin-right: 10px; text-decoration: none; color: #114c80; font-weight: 600; }
    .muted { color: #6b7280; }
    pre { background: #f3f6fb; border: 1px solid #e5ecf6; padding: 12px; border-radius: 6px; overflow: auto; }
  </style>
</head>
<body>
  <div class="wrap">
    <div class="card">
      <h1>NetLoader-X Live Dashboard</h1>
      <div class="actions">
        <a href="/api/export/json">Export JSON</a>
        <a href="/api/export/csv">Export CSV</a>
      </div>
      <p class="muted">Auto-refresh every 2 seconds</p>
    </div>

    <div class="card">
      <h2>Latest Metrics</h2>
      <table id="latest-table"></table>
    </div>

    <div class="card">
      <h2>Metadata</h2>
      <pre id="meta"></pre>
    </div>
  </div>

  <script>
    async function refresh() {
      const resp = await fetch('/api/metrics');
      const data = await resp.json();
      const latest = data.latest || {};
      const meta = data.meta || {};

      const table = document.getElementById('latest-table');
      const rows = Object.keys(latest)
        .sort()
        .map((key) => `<tr><th>${key}</th><td>${latest[key]}</td></tr>`)
        .join('');
      table.innerHTML = rows || '<tr><td>No data yet</td></tr>';
      document.getElementById('meta').textContent = JSON.stringify(meta, null, 2);
    }
    refresh();
    setInterval(refresh, 2000);
  </script>
</body>
</html>
"""
