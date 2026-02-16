# NetLoader-X - Advanced Documentation

## Table of Contents
1. [Web Dashboard Feature](#-web-based-dashboard)
2. [Cluster Simulation Feature](#-cluster-simulation)
3. [Architecture Overview](#-architecture-overview)
4. [Advanced Configuration](#-advanced-configuration)

---

## 🌐 Web-Based Dashboard

### Overview

NetLoader-X includes an optional **real-time web-based dashboard** for advanced visualization. Install optional dependencies to enable:

```bash
pip install flask flask-cors
python netloader-x.py web --port 8080
# Open http://127.0.0.1:8080 in your browser
```

### Features

✅ **Real-Time Charts**
- 📈 Requests Per Second (RPS) - Line chart with live updates
- ⏱️ Latency (ms) - Latency trends with p90/p99 percentiles
- 📊 Queue Depth - Real-time queue visualization
- 👥 Active Clients - Client connection tracking

✅ **Multiple Metric Views**
- Current values in metric cards
- Aggregated statistics (min, max, avg, p90, p99)
- Duration and tick counters
- Real-time updates every 2 seconds

✅ **Export Snapshots**
- 📥 One-click JSON export with full metrics
- 📥 One-click CSV export for spreadsheets
- 🕐 Timestamped filenames for organization
- Direct download to user's device

✅ **Mobile-Responsive Design**
- Dark theme with cyan accents (NetLoader-X branding)
- Works on mobile, tablet, and desktop
- Touch-friendly controls
- Smooth animations and transitions

### REST API Endpoints

The web dashboard exposes several REST endpoints:

```
GET  /api/metrics              - Current metrics snapshot
GET  /api/series               - Complete time-series data
GET  /api/series/<metric>      - Individual metric time-series
GET  /api/export/json          - Export metrics as JSON
GET  /api/export/csv           - Export metrics as CSV
GET  /api/health               - Health check endpoint
```

### Command Line Usage

```bash
# Default port (8080)
python netloader-x.py web

# Custom port
python netloader-x.py web --port 9090

# Custom host and port
python netloader-x.py web --host 192.168.1.100 --port 8080

# Auto-open in browser
python netloader-x.py web --auto-open

# Get help
python netloader-x.py web --help
```

### Dashboard Architecture

```
Simulation Engine
    ↓
MetricsCollector (records snapshots)
    ↓
WebDashboard (Flask app)
    ├── HTML Template (Chart.js)
    ├── REST API Endpoints
    ├── Export Handlers (JSON/CSV)
    └── Real-time Updates (2-second intervals)
```

### Data Flow

1. **Recording**: Engine records metrics snapshots to `MetricsCollector`
2. **Web Server**: Flask app serves HTML dashboard and API endpoints
3. **Browser**: Dashboard fetches metrics via `/api/metrics` and `/api/series`
4. **Visualization**: Chart.js renders real-time charts with auto-refresh
5. **Export**: Users download JSON/CSV snapshots with one click

### Safety Considerations

- **Localhost-only binding** (127.0.0.1 by default)
- **No external network access** required or allowed
- **CORS enabled** for local development only
- **Flask debug mode disabled** in production
- **Automatic metric truncation** for large datasets (max 100 chart points)

### Performance Notes

- **Lightweight HTTP server**: Flask development server sufficient for local use
- **Efficient data transfer**: JSON format with optional compression
- **Chart optimization**: Max 100 points displayed, data downsampling for large datasets
- **Memory efficient**: Only stores what MetricsCollector provides
- **Threading**: Server runs in background thread, doesn't block simulation

### Python API

```python
from core.web_server import WebDashboard
from core.metrics import MetricsCollector

metrics = MetricsCollector()
# ... run simulation and record metrics ...

dashboard = WebDashboard(metrics, host="127.0.0.1", port=8080)
dashboard.start()
# Access at http://127.0.0.1:8080
dashboard.stop()
```

---

## 🗂️ Cluster Simulation

### Overview

NetLoader-X now supports **full server cluster simulation** with:
- 🔀 **Load Balancers** with 5 different routing algorithms
- 📊 **Multiple Backend Servers** with independent capacity profiles
- 💾 **Database/Cache Layer** simulation with connection pooling
- 📈 **Per-Server Metrics** tracking and aggregation
- 🏗️ **Microservices Architecture** support

### Architecture

```
┌─────────────────────────┐
│   Load Balancer         │
│  (Round-Robin, LCM...)  │
└────────┬────────────────┘
         │
    ┌────┼────┬─────────┐
    │    │    │         │
    ▼    ▼    ▼         ▼
┌────┐┌────┐┌────┐  ┌────────┐
│WEB1││WEB2││WEB3│  │Database│
│50w ││50w ││30w │  │Pool:20 │
└────┘└────┘└────┘  │Cache   │
                    └────────┘
     Backend Servers  & Storage
```

### Components

#### Load Balancer

Distributes requests across backend servers using 5 algorithms:

| Algorithm | Best For | Latency | Behavior |
|-----------|----------|---------|----------|
| **round-robin** | Homogeneous servers | O(1) | Equal distribution in order |
| **least-connections** | Unequal loads | O(n) | Route to smallest queue |
| **random** | Simple distribution | O(1) | Random selection |
| **weighted-round-robin** | Different capacities | O(1) | Proportional to worker count |
| **ip-hash** | Session persistence | O(1) | Deterministic consistent hashing |

#### Backend Servers

Each backend configured independently:

```yaml
backends:
  - name: web-server-1
    workers: 50              # Virtual worker threads
    max_queue: 100           # Request queue size
    base_latency: 0.05       # Base latency (seconds)
    max_latency: 2.0         # Max latency under stress
    error_threshold: 0.8     # Load at which errors start
    timeout_threshold: 0.95  # Load at which timeouts occur
    refuse_threshold: 1.1    # Load at which requests refused
```

#### Database/Cache Layer

Simulates realistic database behavior:

- **Connection Pooling**: Limited database connections (configurable)
- **Cache Simulation**: Optional caching with ~70% hit rate
- **Pool Exhaustion**: Tracks when pool is full
- **Cache Statistics**: Hit/miss ratio tracking
- **Realistic Flow**: Cache check → DB acquire → Process → Release

### Configuration Files

#### YAML Format

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

    - name: cache-server
      workers: 30
      max_queue: 80
      base_latency: 0.03
      max_latency: 1.5

database:
  connection_pool: 20      # Number of DB connections
  cache_enabled: true      # Enable caching simulation
```

#### JSON Format

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

### Command Line Usage

```bash
# Basic cluster simulation
python netloader-x.py cluster --config cluster-config.yaml

# Override load balancer algorithm
python netloader-x.py cluster --config cluster-config.yaml \
  --algorithm least-connections

# Custom load parameters
python netloader-x.py cluster --config cluster-config.yaml \
  --threads 200 \
  --duration 120 \
  --rate 5000

# Batch mode (no prompts)
python netloader-x.py cluster --config cluster-config.yaml --batch

# Show loaded configuration
python netloader-x.py cluster --config cluster-config.yaml --show-config

# Display example configuration
python netloader-x.py cluster --example-config
```

### Python API

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

# Start all backends
cluster.start_all()

# Submit requests through load balancer
for i in range(100):
    cluster.submit_request()

# Get metrics
summary = cluster.summary()
print(f"Total requests: {summary['cluster_total_requests']}")
print(f"Backends: {summary['cluster_backends']}")
print(f"Per-backend stats: {summary['per_backend']}")

# Stop simulation
cluster.stop_all()
```

### Metrics

#### Cluster-Level Metrics
- `cluster_requests_total` - Total requests submitted
- `cluster_errors` - Total errors (DB unavailable, etc.)
- `cluster_uptime` - Cluster runtime in seconds
- `cluster_backends` - Number of backend servers
- `lb_algorithm` - Load balancing algorithm used
- `lb_requests_total` - Requests routed by LB
- `lb_failed_requests` - Failed routing attempts
- `db_cache_hit_rate` - Database cache hit percentage

#### Per-Backend Metrics

For each backend (e.g., "server1"):
- `server1_server_requests_total` - Total requests received
- `server1_server_completed` - Successfully processed
- `server1_server_timed_out` - Timed out requests
- `server1_server_errors` - Requests that errored
- `server1_server_refused` - Requests refused (overload)
- `server1_queue_depth` - Current queue size
- `server1_queue_capacity` - Max queue capacity

#### Database Metrics
- `db_total_queries` - Total database queries
- `db_cache_hits` - Cache hits
- `db_cache_misses` - Cache misses
- `db_pool_available` - Available connections
- `db_pool_size` - Total pool size
- `db_pool_exhausted` - Times pool was full
- `db_cache_hit_rate` - Hit rate percentage

### Stress Simulation

Each backend realistically simulates stress:

- **Queue Filling**: Under load, queue grows
- **Latency Increases**: With load factor (queue_size / max_queue)
- **Errors Start**: At error_threshold load (default 0.8)
- **Timeouts Increase**: At timeout_threshold load (default 0.95)
- **Requests Refused**: Above refuse_threshold load (default 1.1)

### Real-World Scenarios

#### Scenario 1: Simple 2-Server Cluster
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

#### Scenario 2: Unequal Capacity with Least Connections
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

#### Scenario 3: Microservices with Cache
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

### Configuration Validation

The cluster configuration parser automatically validates:
- ✅ Valid algorithm names
- ✅ At least one backend configured
- ✅ Positive integer values for workers, pool size
- ✅ Latency consistency (base <= max)
- ✅ Threshold ranges (0-2.0)
- ✅ Required fields present

### Files

**Core Implementation:**
- **core/cluster.py** (~550 lines)
  - ServerCluster, LoadBalancer, DatabaseLayer classes
  - Complete cluster orchestration

- **core/cluster_config.py** (~400 lines)
  - ClusterConfigParser for YAML/JSON
  - Configuration validation
  - Example config generation

**Configuration Examples:**
- **cluster-config-example.yaml** - Ready-to-use template

---

## 🏛️ Architecture Overview

### Simulation Engine Flow

```
User Input (Menu/CLI)
    ↓
Configuration (Profile Selection)
    ↓
Engine Initialization
    ├─ Single Server Mode: FakeServerEngine
    └─ Cluster Mode: ServerCluster (with Load Balancer)
    ↓
Client Simulation
    ├─ Thread Pool (configured count)
    ├─ Attack Profiles (HTTP, Burst, Slow, Wave)
    └─ Load Scheduler
    ↓
Request Processing
    ├─ Queue Management
    ├─ Latency Simulation
    └─ Error/Timeout Injection
    ↓
Metrics Collection
    ├─ Per-tick snapshots
    ├─ Aggregates (min/max/avg/p90/p99)
    └─ Time-series data
    ↓
Output Modes
    ├─ ASCII Dashboard (Terminal)
    ├─ Web Dashboard (Browser)
    ├─ HTML Report (Interactive charts)
    ├─ CSV Report (Spreadsheet)
    └─ JSON Report (Raw data)
```

### Component Architecture

```
┌─────────────────────────────────────────────┐
│         NetLoader-X (v2.3.0)                 │
├─────────────────────────────────────────────┤
│                  CLI Layer                    │
│         (cli.py with argparse)                │
├─────────────────────────────────────────────┤
│              Simulation Layer                 │
│   ┌────────────────────────────────────┐    │
│   │ Engine / Scheduler / Limiter        │    │
│   ├────────────────────────────────────┤    │
│   │ Single Server  │  Cluster           │    │
│   │ FakeServer     │  ServerCluster      │    │
│   │                │  LoadBalancer       │    │
│   │                │  DatabaseLayer      │    │
│   └────────────────────────────────────┘    │
├─────────────────────────────────────────────┤
│            Metrics Layer                     │
│      MetricsCollector / Dashboard            │
├─────────────────────────────────────────────┤
│           Output Layer                       │
│   ASCII Dashboard | Web Dashboard | Reports  │
└─────────────────────────────────────────────┘
```

### Thread Safety

- **Metrics**: Thread-safe locks on counters
- **Queues**: thread.queue.Queue for request management
- **Cluster**: Locks on load balancer and database
- **Engine**: Thread-safe event handling

---

## 🔧 Advanced Configuration

### Custom Attack Profiles

Define custom profiles in YAML:

```yaml
profiles:
  custom-http:
    base_rate: 500
    max_rate: 3000
    ramp_up_seconds: 10
    duration: 60
    jitter: 0.1
```

### Safety Limiter Configuration

Configured in core/limiter.py:

```python
# Hard limits (cannot be overridden)
MAX_THREADS = 1000           # Max virtual clients
MAX_DURATION = 3600          # Max 1 hour
MAX_RPS = 100000             # Max 100k requests/sec
MAX_QUEUE_SIZE = 10000       # Max queue depth
```

### Performance Tuning

**For High Load Simulation:**
```bash
python netloader-x.py run --profile burst \
  --threads 500 \
  --duration 120 \
  --rate 50000
```

**For Gradual Load:**
```bash
python netloader-x.py run --profile wave \
  --threads 100 \
  --duration 300
```

**For Stress Testing:**
```bash
python netloader-x.py run --profile slow \
  --threads 200 \
  --duration 180
```

---

## 📊 Comparing Single vs Cluster Mode

| Feature | Single Server | Cluster |
|---------|---------------|---------|
| **Simplicity** | Simple behavior model | Complex interactions |
| **Realism** | Basic server simulation | Multi-server architecture |
| **Load Balancing** | N/A | 5 algorithms |
| **Database** | N/A | Connection pooling + cache |
| **Metrics** | Server-level | Server + cluster + DB level |
| **Configuration** | Simple CLI args | YAML/JSON config files |
| **Use Cases** | Learning, demos | Enterprise scenarios |

---

## 🚀 Best Practices

### Configuration

1. **Start Simple**: Use example configs as templates
2. **Validate First**: Use `--show-config` before running
3. **Incremental Testing**: Test with small load first
4. **Document Changes**: Keep configs in version control

### Load Testing

1. **Establish Baseline**: Run with low load first
2. **Ramp Up Gradually**: Increase load in steps
3. **Monitor Metrics**: Watch per-backend stats
4. **Analyze Results**: Review database pool utilization

### Cluster Tuning

1. **Choose Algorithm**: Match your topology
2. **Set Capacity**: Appropriate worker counts
3. **Configure DB**: Right pool size for load
4. **Test Failover**: Verify graceful degradation

---

## 📞 Additional Resources

- **README.md** - Quick start and user guide
- **CONTRIBUTING.md** - Development guide
- **SECURITY.md** - Safety guarantees
- **Example configs** - cluster-config-example.yaml

---

**Last Updated**: February 16, 2026  
**Version**: 2.3.0+  
**Status**: ✅ Production Ready
