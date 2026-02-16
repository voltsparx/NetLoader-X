# NetLoader-X

**Defensive Load & Failure Simulation Framework** - v3.0  
*Safe, educational tool for stress-testing and resilience learning*

A comprehensive Python framework for simulating server load patterns and analyzing system behavior under stress—entirely offline, localhost-only, with powerful educational tools.

---

## 🎯 Overview

NetLoader-X enables **defensive engineers, system architects, and DevOps teams** to safely study:

- ✅ How servers degrade under stress
- ✅ Where capacity bottlenecks occur  
- ✅ How to design resilient systems
- ✅ Defense strategies and thresholds

This is **100% safe**: No real network traffic, no real attacks, pure mathematical simulation.

---

## 🚀 Quick Commands

<table border="1">
<tr><th>Task</th><th>Command</th></tr>
<tr><td>Interactive menu</td><td>python netloader-x.py</td></tr>
<tr><td>Quick demo (30s)</td><td>python netloader-x.py quick-test</td></tr>
<tr><td>Guided labs</td><td>python netloader-x.py labs --list</td></tr>
<tr><td>Specific lab</td><td>python netloader-x.py labs --lab 1</td></tr>
<tr><td>CLI load test</td><td>python netloader-x.py run --profile http --threads 50 --duration 60</td></tr>
<tr><td>Cluster simulation</td><td>python netloader-x.py cluster --config cluster-config.yaml</td></tr>
<tr><td>Configuration check</td><td>python netloader-x.py validate --detailed</td></tr>
<tr><td>Full help</td><td>python netloader-x.py --help</td></tr>
</table>

---

## ⚡ Quick Start

### Installation

```bash
# Clone repository
git clone https://github.com/voltsparx/NetLoader-X.git
cd NetLoader-X

# Install (optional dependencies for enhanced features)
pip install -r requirements.txt

# Run interactive mode
python netloader-x.py
```

### First Run

<table border="1">
<tr><th>Mode</th><th>Command</th><th>Duration</th><th>Use Case</th></tr>
<tr><td>Interactive Menu</td><td>python netloader-x.py</td><td>Variable</td><td>Guided experience</td></tr>
<tr><td>Quick Demo</td><td>python netloader-x.py quick-test</td><td>30 seconds</td><td>See it in action</td></tr>
<tr><td>Guided Lab</td><td>python netloader-x.py labs --lab 1</td><td>60-120s</td><td>Learn concepts</td></tr>
<tr><td>Batch/CLI</td><td>python netloader-x.py run --profile http</td><td>60s default</td><td>Automation/scripting</td></tr>
<tr><td>Validation</td><td>python netloader-x.py validate --detailed</td><td>Instant</td><td>Check setup</td></tr>
</table>

---

## 🚀 Features

### Core Capabilities

<table border="1">
<tr><th>Feature</th><th>Status</th><th>Details</th></tr>
<tr><td>Multiple Attack Profiles</td><td>✅</td><td>HTTP Steady, Burst, Slow Client, Wave, Chaos</td></tr>
<tr><td>ASCII Real-time Dashboard</td><td>✅</td><td>Live metrics in terminal</td></tr>
<tr><td>Web-based Dashboard</td><td>✅</td><td>Optional Flask dashboard with Chart.js graphs</td></tr>
<tr><td>Cluster Simulation</td><td>✅</td><td>Load balancers, multiple backends, DB layer</td></tr>
<tr><td>Metrics Collection</td><td>✅</td><td>RPS, latency, queue depth, errors</td></tr>
<tr><td>Report Generation</td><td>✅</td><td>CSV, JSON, HTML with interactive charts</td></tr>
<tr><td>Safety Enforcement</td><td>✅</td><td>Hard limits, no external access</td></tr>
<tr><td>Custom Profiles</td><td>✅</td><td>Load from YAML/JSON files</td></tr>
<tr><td>Guided Labs</td><td>✅</td><td>7 pre-built educational scenarios</td></tr>
<tr><td>Chaos Engineering</td><td>✅</td><td>Random fault injection for resilience testing</td></tr>
<tr><td>CLI Interface</td><td>✅</td><td>Full argparse support + interactive menu</td></tr>
<tr><td>Unit Tests</td><td>✅</td><td>pytest framework with 40+ tests</td></tr>
<tr><td>Zero Dependencies</td><td>✅</td><td>Core runs with stdlib only</td></tr>
</table>

### Attack Profiles

<table border="1">
<tr><th>Profile</th><th>Behavior</th><th>Use Case</th></tr>
<tr><td>HTTP Steady</td><td>Constant request pressure</td><td>Baseline testing</td></tr>
<tr><td>Burst Traffic</td><td>Sudden spikes (2-3x normal)</td><td>Flash crowd simulation</td></tr>
<tr><td>Slow Client Attack</td><td>Long-lived connections</td><td>Connection exhaustion</td></tr>
<tr><td>Wave Pattern</td><td>Periodic load cycles</td><td>Cyclical traffic patterns</td></tr>
<tr><td>Chaos Engineering</td><td>Random fault injection</td><td>Resilience testing</td></tr>
</table>

### Guided Labs (Educational)

<table border="1">
<tr><th>Lab</th><th>Topic</th><th>Level</th><th>Focus</th></tr>
<tr><td>Lab 1</td><td>Queue Overflow Basics</td><td>Beginner</td><td>Queue dynamics</td></tr>
<tr><td>Lab 2</td><td>Slowloris Connection Exhaustion</td><td>Beginner</td><td>Connection limits</td></tr>
<tr><td>Lab 3</td><td>Burst Traffic Response</td><td>Intermediate</td><td>Spike handling</td></tr>
<tr><td>Lab 4</td><td>Error Rate Cascade</td><td>Intermediate</td><td>Failure modes</td></tr>
<tr><td>Lab 5</td><td>Queue Limit Impact</td><td>Intermediate</td><td>Capacity planning</td></tr>
<tr><td>Lab 6</td><td>Server Recovery Dynamics</td><td>Advanced</td><td>Recovery patterns</td></tr>
<tr><td>Lab 7</td><td>Chaos Engineering</td><td>Advanced</td><td>Resilience strategies</td></tr>
</table>

---

## 🔧 Usage Modes

### 1. Interactive Menu Mode (Default)

```bash
python netloader-x.py
```

Navigate through options to:
1. Configure simulation parameters
2. Select attack profile
3. View server behavior settings
4. Access educational help
5. Start simulation
6. Exit

### 2. Quick Test (Demo Mode)

<table border="1">
<tr><th>Command</th><th>Description</th></tr>
<tr><td>python netloader-x.py quick-test</td><td>30-second HTTP load test with defaults</td></tr>
<tr><td>python netloader-x.py quick-test --short</td><td>10-second version</td></tr>
<tr><td>python netloader-x.py quick-test --skip-dashboard</td><td>Without dashboard display</td></tr>
</table>

### 3. Guided Labs (Learning Mode)

<table border="1">
<tr><th>Command</th><th>Description</th></tr>
<tr><td>python netloader-x.py labs --list</td><td>List all available labs</td></tr>
<tr><td>python netloader-x.py labs --lab 1</td><td>Run specific lab with narration</td></tr>
<tr><td>python netloader-x.py labs --lab 1 --description-only</td><td>Show lab description without running</td></tr>
<tr><td>python netloader-x.py labs --lab 3 --no-interactive</td><td>Run without educational narration</td></tr>
</table>

### 4. Batch Mode (CLI)

<table border="1">
<tr><th>Command</th><th>Description</th></tr>
<tr><td>python netloader-x.py run --profile http --threads 50 --duration 60</td><td>HTTP profile, 50 threads, 60 seconds</td></tr>
<tr><td>python netloader-x.py run --profile burst --rate 8000 --duration 45</td><td>Burst profile with custom rate</td></tr>
<tr><td>python netloader-x.py run --profile slow --threads 100 --duration 120</td><td>Slow client attack</td></tr>
<tr><td>python netloader-x.py run --profile http --batch</td><td>Skip interactive prompts</td></tr>
</table>

### 5. Cluster Simulation (New!)

<table border="1">
<tr><th>Command</th><th>Description</th></tr>
<tr><td>python netloader-x.py cluster --config cluster-config.yaml</td><td>Basic cluster with load balancer</td></tr>
<tr><td>python netloader-x.py cluster --config config.yaml --algorithm least-connections</td><td>Override load balancer algorithm</td></tr>
<tr><td>python netloader-x.py cluster --config config.yaml --threads 200 --duration 120</td><td>Custom load parameters</td></tr>
<tr><td>python netloader-x.py cluster --config config.yaml --show-config</td><td>Show configuration before running</td></tr>
<tr><td>python netloader-x.py cluster --example-config</td><td>Display example configuration</td></tr>
</table>

### 6. Configuration Validation

<table border="1">
<tr><th>Command</th><th>Description</th></tr>
<tr><td>python netloader-x.py validate</td><td>Basic validation</td></tr>
<tr><td>python netloader-x.py validate --detailed</td><td>Detailed validation report</td></tr>
<tr><td>python netloader-x.py validate --config profiles.json</td><td>Validate custom config file</td></tr>
</table>

---

## 📊 Output & Reports

### Real-Time Dashboard (Terminal)

```
[ Live Simulation Dashboard ]
============================================================

Overview
------------------------------------------------------------
Simulation Time     : 12.3 seconds
Virtual Clients     : 50
Profile             : http

Request Rate
------------------------------------------------------------
Current RPS         : 4523.2
Average RPS         : 3891.5
Peak RPS            : 5102.8

Latency (ms)
------------------------------------------------------------
Average Latency     : 145.3 ms
Latency Jitter      : 52.1 ms
Max Latency         : 892.4 ms

Queue Depth
------------------------------------------------------------
Current Queue       : 487
Max Queue           : 892
Error Rate          : 8.45%
```

### 🌐 Web-Based Dashboard (Advanced)

**Installation & Setup:**

<table border="1">
<tr><td><strong>Prerequisites</strong></td><td>pip install flask flask-cors</td></tr>
<tr><td><strong>Start Web Server</strong></td><td>python netloader-x.py web --port 8080</td></tr>
<tr><td><strong>Access Dashboard</strong></td><td>Open http://127.0.0.1:8080 in browser</td></tr>
</table>

**Web Dashboard Commands:**

<table border="1">
<tr><th>Command</th><th>Description</th></tr>
<tr><td>python netloader-x.py web</td><td>Start on default port 8080</td></tr>
<tr><td>python netloader-x.py web --port 9090</td><td>Custom port</td></tr>
<tr><td>python netloader-x.py web --host 192.168.1.100 --port 8080</td><td>Custom host and port</td></tr>
<tr><td>python netloader-x.py web --auto-open</td><td>Auto-open browser</td></tr>
<tr><td>python netloader-x.py web --help</td><td>Get help</td></tr>
</table>

**Features:**
- 📈 Live Chart.js graphs for RPS, Latency, Queue Depth, Active Clients
- 🔄 Auto-refresh metrics every 2 seconds
- 📊 Multiple metric views with statistics
- 📥 Export functionality (JSON, CSV)
- 📱 Mobile-responsive design

**REST API Endpoints:**

<table border="1">
<tr><th>Method</th><th>Endpoint</th><th>Returns</th></tr>
<tr><td>GET</td><td>/api/metrics</td><td>Current metrics snapshot</td></tr>
<tr><td>GET</td><td>/api/series</td><td>Complete time-series data</td></tr>
<tr><td>GET</td><td>/api/series/&lt;metric&gt;</td><td>Individual metric time-series</td></tr>
<tr><td>GET</td><td>/api/export/json</td><td>Metrics as JSON file</td></tr>
<tr><td>GET</td><td>/api/export/csv</td><td>Metrics as CSV file</td></tr>
<tr><td>GET</td><td>/api/health</td><td>Health check endpoint</td></tr>
</table>

**Web Dashboard Data Flow:**

```
Simulation Engine → MetricsCollector → Flask Web Server
                                        ├── HTML Dashboard
                                        ├── REST API Endpoints
                                        └── Export Handlers
                                        ↓
                                    Browser (Chart.js)
                                        ├── Real-time Charts
                                        └── Export Downloads
```

**Safety & Performance:**

<table border="1">
<tr><th>Aspect</th><th>Details</th></tr>
<tr><td>Network</td><td>Localhost-only binding (127.0.0.1)</td></tr>
<tr><td>Security</td><td>No external network access required</td></tr>
<tr><td>Performance</td><td>Max 100 chart points, downsampling for large datasets</td></tr>
<tr><td>Threading</td><td>Server runs in background, doesn't block simulation</td></tr>
<tr><td>Memory</td><td>Efficient - only stores MetricsCollector data</td></tr>
</table>

**Python API Example:**

```python
from core.web_server import WebDashboard
from core.metrics import MetricsCollector

metrics = MetricsCollector()
# ... run simulation and record metrics ...

dashboard = WebDashboard(metrics, host="127.0.0.1", port=8080)
dashboard.start()      # Access at http://127.0.0.1:8080
dashboard.stop()
```

### Generated Reports

After each simulation:

```
outputs/
├── http_2026-02-16_14-30-45/
│   ├── metadata.json      # Simulation configuration
│   ├── metrics.json       # Raw data (all ticks)
│   ├── metrics.csv        # Time-series (spreadsheet-friendly)
│   └── metrics.html       # Interactive report with charts
```

**Report Formats:**

<table border="1">
<tr><th>Format</th><th>Location</th><th>Purpose</th></tr>
<tr><td>JSON</td><td>metrics.json</td><td>Raw data, programmatic analysis</td></tr>
<tr><td>CSV</td><td>metrics.csv</td><td>Spreadsheet import, time-series</td></tr>
<tr><td>HTML</td><td>metrics.html</td><td>Visual presentation, stakeholders</td></tr>
</table>

---

## 🗂️ Cluster Simulation (Advanced)

### Overview

Full server cluster simulation with:
- 🔀 Load Balancers with 5 routing algorithms
- 📊 Multiple Backend Servers with independent profiles
- 💾 Database/Cache Layer with connection pooling
- 📈 Per-Server Metrics tracking and aggregation

### Load Balancing Algorithms

<table border="1">
<tr><th>Algorithm</th><th>Best For</th><th>Complexity</th><th>Behavior</th></tr>
<tr><td><strong>round-robin</strong></td><td>Homogeneous servers</td><td>O(1)</td><td>Equal distribution in order</td></tr>
<tr><td><strong>least-connections</strong></td><td>Unequal loads</td><td>O(n)</td><td>Route to smallest queue</td></tr>
<tr><td><strong>random</strong></td><td>Simple distribution</td><td>O(1)</td><td>Random selection</td></tr>
<tr><td><strong>weighted-round-robin</strong></td><td>Different capacities</td><td>O(1)</td><td>Proportional to worker count</td></tr>
<tr><td><strong>ip-hash</strong></td><td>Session persistence</td><td>O(1)</td><td>Deterministic consistent hashing</td></tr>
</table>

### Backend Server Configuration

<table border="1">
<tr><th>Parameter</th><th>Type</th><th>Default</th><th>Purpose</th></tr>
<tr><td>name</td><td>string</td><td>-</td><td>Server identifier</td></tr>
<tr><td>workers</td><td>int</td><td>50</td><td>Virtual worker threads</td></tr>
<tr><td>max_queue</td><td>int</td><td>100</td><td>Request queue size</td></tr>
<tr><td>base_latency</td><td>float</td><td>0.05</td><td>Base latency (seconds)</td></tr>
<tr><td>max_latency</td><td>float</td><td>2.0</td><td>Max latency under stress</td></tr>
<tr><td>error_threshold</td><td>float</td><td>0.8</td><td>Load factor for errors</td></tr>
<tr><td>timeout_threshold</td><td>float</td><td>0.95</td><td>Load factor for timeouts</td></tr>
<tr><td>refuse_threshold</td><td>float</td><td>1.1</td><td>Load factor for refusal</td></tr>
</table>

### Cluster Configuration (YAML)

```yaml
load_balancer:
  algorithm: round-robin
  backends:
    - name: web-server-1
      workers: 50
      max_queue: 100
      base_latency: 0.05
      max_latency: 2.0
    - name: web-server-2
      workers: 50
      max_queue: 100
      base_latency: 0.05
      max_latency: 2.0

database:
  connection_pool: 20
  cache_enabled: true
```

### Cluster Configuration (JSON)

```json
{
  "load_balancer": {
    "algorithm": "round-robin",
    "backends": [
      {
        "name": "server1",
        "workers": 50,
        "max_queue": 100,
        "base_latency": 0.05,
        "max_latency": 2.0
      }
    ]
  },
  "database": {
    "connection_pool": 20,
    "cache_enabled": true
  }
}
```

### Cluster Metrics

**Cluster-Level Metrics:**

<table border="1">
<tr><th>Metric</th><th>Description</th></tr>
<tr><td>cluster_requests_total</td><td>Total requests submitted</td></tr>
<tr><td>cluster_errors</td><td>Total errors (DB unavailable, etc.)</td></tr>
<tr><td>cluster_uptime</td><td>Cluster runtime in seconds</td></tr>
<tr><td>lb_algorithm</td><td>Load balancing algorithm used</td></tr>
<tr><td>db_cache_hit_rate</td><td>Database cache hit percentage</td></tr>
</table>

**Per-Backend Metrics (e.g., "server1"):**

<table border="1">
<tr><th>Metric</th><th>Description</th></tr>
<tr><td>server1_requests_total</td><td>Total requests received</td></tr>
<tr><td>server1_completed</td><td>Successfully processed</td></tr>
<tr><td>server1_timed_out</td><td>Timed out requests</td></tr>
<tr><td>server1_errors</td><td>Requests that errored</td></tr>
<tr><td>server1_refused</td><td>Requests refused (overload)</td></tr>
<tr><td>server1_queue_depth</td><td>Current queue size</td></tr>
</table>

**Database Metrics:**

<table border="1">
<tr><th>Metric</th><th>Description</th></tr>
<tr><td>db_total_queries</td><td>Total database queries</td></tr>
<tr><td>db_cache_hits</td><td>Cache hits</td></tr>
<tr><td>db_cache_misses</td><td>Cache misses</td></tr>
<tr><td>db_pool_available</td><td>Available connections</td></tr>
<tr><td>db_pool_exhausted</td><td>Times pool was full</td></tr>
<tr><td>db_cache_hit_rate</td><td>Hit rate percentage</td></tr>
</table>

### Cluster Python API

```python
from core.cluster import ServerCluster, LoadBalancerAlgorithm
from core.cluster_config import ClusterConfigParser

# Load configuration
config = ClusterConfigParser.load_from_file("cluster-config.yaml")

# Create cluster
cluster = ServerCluster(
    lb_algorithm=LoadBalancerAlgorithm.ROUND_ROBIN,
    backends_config=config['load_balancer']['backends'],
    db_pool_size=config['database']['connection_pool'],
    db_cache_enabled=config['database']['cache_enabled']
)

# Run simulation
cluster.start_all()
for i in range(100):
    cluster.submit_request()

# Get metrics
summary = cluster.summary()
print(f"Total requests: {summary['cluster_total_requests']}")
print(f"Backends: {summary['cluster_backends']}")

cluster.stop_all()
```

### Real-World Scenarios

**Scenario 1: Simple 2-Server Cluster**
```yaml
load_balancer:
  algorithm: round-robin
  backends:
    - name: server1
      workers: 50
    - name: server2
      workers: 50
database:
  connection_pool: 20
  cache_enabled: false
```

**Scenario 2: Unequal Capacity with Least Connections**
```yaml
load_balancer:
  algorithm: least-connections
  backends:
    - name: primary
      workers: 100
      max_queue: 200
    - name: secondary
      workers: 50
      max_queue: 100
    - name: backup
      workers: 25
      max_queue: 50
database:
  connection_pool: 30
  cache_enabled: true
```

**Scenario 3: Microservices with Cache**
```yaml
load_balancer:
  algorithm: weighted-round-robin
  backends:
    - name: api-server-1
      workers: 60
    - name: api-server-2
      workers: 60
    - name: api-server-3
      workers: 40
database:
  connection_pool: 50
  cache_enabled: true
```

---

## 🏛️ System Architecture

### Simulation Engine Flow

```
User Input (Menu/CLI)
    ↓
Configuration Selection
    ↓
Engine Initialization
    ├─ Single Server Mode: FakeServerEngine
    └─ Cluster Mode: ServerCluster
    ↓
Client Simulation (Thread Pool)
    ├─ Attack Profiles
    └─ Load Scheduler
    ↓
Request Processing
    ├─ Queue Management
    ├─ Latency Simulation
    └─ Error/Timeout Injection
    ↓
Metrics Collection
    ├─ Per-tick snapshots
    └─ Aggregates & Time-series
    ↓
Output Modes
    ├─ ASCII Dashboard
    ├─ Web Dashboard
    └─ Reports (JSON/CSV/HTML)
```

### Component Architecture

<table border="1">
<tr><th>Layer</th><th>Components</th><th>Purpose</th></tr>
<tr><td><strong>CLI Layer</strong></td><td>cli.py with argparse</td><td>Command-line interface</td></tr>
<tr><td><strong>Simulation Layer</strong></td><td>Engine, Scheduler, Limiter</td><td>Core simulation logic</td></tr>
<tr><td><strong>Server Layer</strong></td><td>FakeServer or ServerCluster</td><td>Single or distributed</td></tr>
<tr><td><strong>Metrics Layer</strong></td><td>MetricsCollector, Dashboard</td><td>Data collection</td></tr>
<tr><td><strong>Output Layer</strong></td><td>Reporter, WebServer, Dashboard</td><td>Results visualization</td></tr>
</table>

### Thread Safety

<table border="1">
<tr><th>Component</th><th>Thread Safety Mechanism</th></tr>
<tr><td>Metrics</td><td>Thread-safe locks on counters</td></tr>
<tr><td>Queues</td><td>threading.queue.Queue</td></tr>
<tr><td>Cluster</td><td>Locks on load balancer & database</td></tr>
<tr><td>Engine</td><td>Thread-safe event handling</td></tr>
</table>

---

## 🔧 Advanced Configuration & Performance Tuning

### Custom Attack Profiles

<table border="1">
<tr><th>Parameter</th><th>Type</th><th>Example</th><th>Purpose</th></tr>
<tr><td>base_rate</td><td>int</td><td>500</td><td>Starting RPS</td></tr>
<tr><td>max_rate</td><td>int</td><td>3000</td><td>Peak RPS</td></tr>
<tr><td>ramp_up_seconds</td><td>int</td><td>10</td><td>Acceleration time</td></tr>
<tr><td>duration</td><td>int</td><td>60</td><td>Total test duration</td></tr>
<tr><td>jitter</td><td>float</td><td>0.1</td><td>Randomness factor</td></tr>
</table>

### Safety Hard Limits

<table border="1">
<tr><th>Limit</th><th>Value</th><th>Cannot Be Overridden</th></tr>
<tr><td>MAX_THREADS</td><td>1,000</td><td>✅ Yes</td></tr>
<tr><td>MAX_DURATION</td><td>3,600 sec (1 hr)</td><td>✅ Yes</td></tr>
<tr><td>MAX_RPS</td><td>100,000</td><td>✅ Yes</td></tr>
<tr><td>MAX_QUEUE_SIZE</td><td>10,000</td><td>✅ Yes</td></tr>
</table>

### Performance Tuning Commands

<table border="1">
<tr><th>Scenario</th><th>Command</th><th>Use Case</th></tr>
<tr><td><strong>High Load</strong></td><td>python netloader-x.py run --profile burst --threads 500 --duration 120 --rate 50000</td><td>Peak capacity test</td></tr>
<tr><td><strong>Gradual Load</strong></td><td>python netloader-x.py run --profile wave --threads 100 --duration 300</td><td>Ramp-up analysis</td></tr>
<tr><td><strong>Stress Test</strong></td><td>python netloader-x.py run --profile slow --threads 200 --duration 180</td><td>Connection exhaustion</td></tr>
</table>

### Single vs Cluster Mode Comparison

<table border="1">
<tr><th>Feature</th><th>Single Server</th><th>Cluster</th></tr>
<tr><td>Simplicity</td><td>Simple behavior</td><td>Complex interactions</td></tr>
<tr><td>Realism</td><td>Basic simulation</td><td>Multi-server architecture</td></tr>
<tr><td>Load Balancing</td><td>N/A</td><td>5 algorithms</td></tr>
<tr><td>Database</td><td>N/A</td><td>Connection pool + cache</td></tr>
<tr><td>Metrics Detail</td><td>Server-level</td><td>Server + cluster + DB</td></tr>
<tr><td>Configuration</td><td>CLI args</td><td>YAML/JSON files</td></tr>
<tr><td>Use Cases</td><td>Learning, demos</td><td>Enterprise scenarios</td></tr>
</table>

---

## 🚀 Best Practices

### Cluster Configuration Best Practices

<table border="1">
<tr><th>Best Practice</th><th>Explanation</th></tr>
<tr><td><strong>Start Simple</strong></td><td>Use example configs as templates</td></tr>
<tr><td><strong>Validate First</strong></td><td>Use --show-config before running</td></tr>
<tr><td><strong>Test Incrementally</strong></td><td>Start with small load, increase gradually</td></tr>
<tr><td><strong>Monitor Metrics</strong></td><td>Watch per-backend stats in real-time</td></tr>
<tr><td><strong>Document Changes</strong></td><td>Keep configs in version control</td></tr>
</table>

### Load Testing Best Practices

<table border="1">
<tr><th>Step</th><th>Action</th><th>Rationale</th></tr>
<tr><td>1</td><td>Establish Baseline</td><td>Low load baseline for comparison</td></tr>
<tr><td>2</td><td>Ramp Up Gradually</td><td>Identify breaking points</td></tr>
<tr><td>3</td><td>Monitor Pool Utilization</td><td>Database bottleneck detection</td></tr>
<tr><td>4</td><td>Analyze Per-Server Stats</td><td>Identify unbalanced distribution</td></tr>
<tr><td>5</td><td>Review Results</td><td>Data-driven decisions</td></tr>
</table>

---

## 🎓 Learning Content

### Built-in Help Menu

Access comprehensive theory explanations:

<table border="1">
<tr><th>Topic</th><th>Description</th></tr>
<tr><td>What is NetLoader-X?</td><td>Tool overview and capabilities</td></tr>
<tr><td>Traffic Load vs Attacks</td><td>Understanding load patterns</td></tr>
<tr><td>Simulated Attack Profiles</td><td>Profile descriptions and use cases</td></tr>
<tr><td>Threading & Speed Model</td><td>Performance characteristics</td></tr>
<tr><td>Server Failure Behavior</td><td>Degradation patterns</td></tr>
<tr><td>Defensive Takeaways</td><td>Security implications</td></tr>
<tr><td>Ethical Use & Scope</td><td>Responsible usage guidelines</td></tr>
</table>

### Guided Labs with Narration

Each lab includes:
- **Description**: What you'll observe
- **Narrative**: Educational explanation during run
- **Metrics**: Real-time data collection
- **Key Insight**: Main takeaway for learning

---

## ⚙️ Configuration

### Predefined Server Profiles

<table border="1">
<tr><th>Profile</th><th>Workers</th><th>Queue Size</th><th>Use Case</th></tr>
<tr><td>small-web</td><td>20</td><td>200</td><td>Small services</td></tr>
<tr><td>api-backend</td><td>50</td><td>500</td><td>REST APIs</td></tr>
<tr><td>enterprise-app</td><td>120</td><td>1200</td><td>Large applications</td></tr>
</table>

### Custom YAML Configuration

```yaml
attack_profiles:
  - name: my-http-load
    description: "Custom HTTP test"
    profile_type: http
    threads: 100
    duration: 60
    base_rate: 2000
    max_rate: 8000
    jitter: 0.05

server_profiles:
  - name: my-server
    max_workers: 50
    queue_limit: 500
    base_latency_ms: 40.0
    timeout_ms: 2000
```

### Safety Configuration

Hard safety limits (non-negotiable):

<table border="1">
<tr><th>Setting</th><th>Value</th><th>Impact</th></tr>
<tr><td>ALLOW_NETWORK_IO</td><td>False</td><td>No external connections</td></tr>
<tr><td>ALLOW_EXTERNAL_TARGETS</td><td>False</td><td>Localhost only</td></tr>
<tr><td>ALLOW_RAW_TRAFFIC</td><td>False</td><td>No packet generation</td></tr>
<tr><td>MAX_SIMULATION_TIME_SEC</td><td>3600</td><td>1 hour maximum</td></tr>
<tr><td>MAX_VIRTUAL_CLIENTS</td><td>100,000</td><td>Abstract simulation only</td></tr>
<tr><td>MAX_EVENTS_PER_SECOND</td><td>1,000,000</td><td>Rate limiting</td></tr>
</table>

---

## 🔬 Testing

### Run Unit Tests

<table border="1">
<tr><th>Command</th><th>Purpose</th></tr>
<tr><td>pytest tests/test_all.py -v</td><td>Run all tests with verbose output</td></tr>
<tr><td>pytest tests/test_all.py::TestMetricsCollector -v</td><td>Run specific test class</td></tr>
<tr><td>pytest tests/test_all.py --cov=core --cov=ui --cov=utils</td><td>With coverage report</td></tr>
<tr><td>pytest tests/test_all.py::TestIntegration -v</td><td>Integration tests only</td></tr>
</table>

**Test Coverage:**
- ✅ Core simulation (95%+)
- ✅ Safety limits (100%)
- ✅ Metrics (100%)
- ✅ Configuration (95%)
- ✅ CLI parsing (90%)
- ✅ Validators (95%)

---

## 🛡️ Security Features

### Absolute Safety Guarantees

<table border="1">
<tr><th>Guarantee</th><th>Implementation</th></tr>
<tr><td>No External Network Access</td><td>Hard-coded, impossible to bypass</td></tr>
<tr><td>Localhost Only</td><td>Enforced at every layer</td></tr>
<tr><td>No Real Attacks</td><td>Pure simulation, behavioral modeling</td></tr>
<tr><td>Rate Limited</td><td>Hard caps on all operations</td></tr>
<tr><td>Thread-Safe</td><td>Concurrent access properly synchronized</td></tr>
<tr><td>Input Validated</td><td>All user input checked</td></tr>
<tr><td>No Code Injection</td><td>Zero eval(), exec(), dangerous patterns</td></tr>
</table>

### Compliance

<table border="1">
<tr><th>Compliance Area</th><th>Status</th></tr>
<tr><td>Student Lab Environments</td><td>✅ Safe</td></tr>
<tr><td>Air-gapped Networks</td><td>✅ Safe</td></tr>
<tr><td>GDPR Compliance</td><td>✅ Compliant (no data collection)</td></tr>
<tr><td>Telemetry & External Calls</td><td>✅ None</td></tr>
<tr><td>Code Transparency</td><td>✅ Auditable</td></tr>
</table>

See [SECURITY.md](SECURITY.md) for detailed security policy and best practices.

---

## 📚 Project Structure

<table border="1">
<tr><th>Directory</th><th>Purpose</th></tr>
<tr><td>core/</td><td>Simulation engine (config, engine, profiles, metrics, etc.)</td></tr>
<tr><td>ui/</td><td>User interface (menu, dashboard, banner, help)</td></tr>
<tr><td>targets/</td><td>Target simulators (localhost.py)</td></tr>
<tr><td>utils/</td><td>Utilities (logger, validators, reporter, HTML)</td></tr>
<tr><td>tests/</td><td>Unit test suite (pytest)</td></tr>
<tr><td>output/</td><td>Generated reports (created at runtime)</td></tr>
</table>

---

## 🎓 Educational Value

### What Students Learn

<table border="1">
<tr><th>Topic</th><th>Key Concepts</th></tr>
<tr><td>Load Behavior</td><td>Request rate effects, queue dynamics, degradation curves</td></tr>
<tr><td>Server Characteristics</td><td>Worker pool, queue overflow, timeouts, errors</td></tr>
<tr><td>Defensive Strategies</td><td>Rate limiting, timeouts, circuit breakers, SLAs</td></tr>
<tr><td>Chaos Engineering</td><td>Resilience testing, failure modes, recovery</td></tr>
<tr><td>System Design</td><td>Capacity planning, thresholds, alerting, monitoring</td></tr>
</table>

### Example Lesson Flow

1. **Lesson 1: Queue Growth**
   - Run Lab 1 with 20 threads
   - Observe queue filling at ~200 requests
   - Learn: Queue is early warning system

2. **Lesson 2: Connection Exhaustion**
   - Run Lab 2 with slow clients
   - See few clients blocking all workers
   - Learn: Timeouts are critical

3. **Lesson 3: Design Defenses**
   - Adjust limits in config
   - Re-run with new parameters
   - Measure improvement

---

## 🔍 Troubleshooting

### Common Issues

<table border="1">
<tr><th>Problem</th><th>Solution</th></tr>
<tr><td>Menu selections not recognized</td><td>Enter only the number (1-6), then press ENTER</td></tr>
<tr><td>Dashboard appears frozen</td><td>Normal - updates every 0.5 seconds. Press Ctrl+C for summary</td></tr>
<tr><td>ImportError: No module named 'pyyaml'</td><td>Optional. Install with: pip install pyyaml</td></tr>
<tr><td>Simulation won't start</td><td>Ensure you've selected a profile (option [2] first)</td></tr>
<tr><td>No reports generated</td><td>Check outputs/ directory exists and is writable</td></tr>
<tr><td>Permission denied on outputs</td><td>Run from directory where you have write access</td></tr>
</table>

### Debug Mode

<table border="1">
<tr><th>Command</th><th>Purpose</th></tr>
<tr><td>python netloader-x.py --verbose</td><td>Enable verbose logging</td></tr>
<tr><td>python netloader-x.py validate --detailed</td><td>Detailed validation report</td></tr>
<tr><td>python -c "import netloader-x; print('OK')"</td><td>Check imports</td></tr>
</table>

---

## 📈 Performance Metrics

### Typical Run (50 threads, 60 sec)

<table border="1">
<tr><th>Metric</th><th>Value</th></tr>
<tr><td>Ticks Executed</td><td>~60</td></tr>
<tr><td>Virtual Clients</td><td>50</td></tr>
<tr><td>Peak RPS</td><td>4,500+</td></tr>
<tr><td>Memory Usage</td><td><50MB</td></tr>
<tr><td>CPU Per Thread</td><td><1%</td></tr>
<tr><td>Report Generation</td><td><100ms</td></tr>
</table>

### Scalability Limits

<table border="1">
<tr><th>Metric</th><th>Limit</th><th>Reason</th></tr>
<tr><td>Duration</td><td>3600 sec</td><td>Hard cap in config</td></tr>
<tr><td>Threads</td><td>100,000</td><td>Virtual client limit</td></tr>
<tr><td>Events/sec</td><td>1,000,000</td><td>Rate limit</td></tr>
<tr><td>Simulation Time</td><td><1 hour</td><td>Resource constraint</td></tr>
</table>

---

## 🤝 Contributing

Found a bug? Have a feature idea?

1. Test your scenario thoroughly
2. Document the issue
3. Submit with example reproduction steps
4. Suggest improvement with clear rationale

---

## 📄 License

**Educational & Defensive Simulation Only**

<table border="1">
<tr><th>Use Case</th><th>Allowed</th></tr>
<tr><td>Learning</td><td>✅ Yes</td></tr>
<tr><td>Defensive testing</td><td>✅ Yes</td></tr>
<tr><td>Academic settings</td><td>✅ Yes</td></tr>
<tr><td>Modification</td><td>✅ Yes</td></tr>
<tr><td>Real attacks</td><td>❌ No</td></tr>
<tr><td>Unauthorized testing</td><td>❌ No</td></tr>
<tr><td>Malicious purposes</td><td>❌ No</td></tr>
<tr><td>License removal</td><td>❌ No</td></tr>
</table>

---

## 📞 Contact & Support

<table border="1">
<tr><th>Item</th><th>Value</th></tr>
<tr><td>Author</td><td>voltsparx</td></tr>
<tr><td>Email</td><td>voltsparx@gmail.com</td></tr>
<tr><td>GitHub</td><td>https://github.com/voltsparx/NetLoader-X</td></tr>
<tr><td>Version</td><td>3.0</td></tr>
</table>

---

## 🚀 Next Steps

### For Learners
1. Read the built-in help menu
2. Try Lab 1 (Queue Overflow)
3. Experiment with different thread counts
4. Analyze the HTML reports

### For Researchers
1. Create custom profiles
2. Run chaos scenarios
3. Compare report metrics
4. Extend with new failure types

### For DevOps Teams
1. Model your production servers
2. Test alert thresholds
3. Validate auto-scaling policies
4. Document capacity limits

---

## 📚 Further Reading

<table border="1">
<tr><th>Document</th><th>Purpose</th></tr>
<tr><td>SECURITY.md</td><td>Security policy and best practices</td></tr>
<tr><td>CONTRIBUTING.md</td><td>How to contribute to the project</td></tr>
<tr><td>core/guided_labs.py</td><td>Educational scenarios source</td></tr>
<tr><td>core/engine.py</td><td>Core engine API reference</td></tr>
<tr><td>core/config.py</td><td>Configuration options reference</td></tr>
</table>

---

**NetLoader-X** — *Learn. Simulate. Defend.* 🛡️
