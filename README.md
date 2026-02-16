# NetLoader-X

**Defensive Load & Failure Simulation Framework** - v1.0.0  
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

```bash
# Option 1: Interactive Menu (default)
python netloader-x.py

# Option 2: Quick Demo (30 second HTTP load)
python netloader-x.py quick-test

# Option 3: Guided Labs (educational scenarios)
python netloader-x.py labs --list
python netloader-x.py labs --lab 1

# Option 4: Batch Mode with CLI
python netloader-x.py run --profile http --threads 50 --duration 60

# Option 5: Validation
python netloader-x.py validate --detailed
```

---

## 🚀 Features

### Core Capabilities

| Feature | Status | Details |
|---------|--------|---------|
| **Multiple Attack Profiles** | ✅ | HTTP Steady, Burst, Slow Client, Wave, Chaos |
| **Real-time Dashboard** | ✅ | Live metrics with ASCII graphs |
| **Metrics Collection** | ✅ | RPS, latency, queue depth, errors |
| **Report Generation** | ✅ | CSV, JSON, HTML with interactive charts |
| **Safety Enforcement** | ✅ | Hard limits, no external access |
| **Custom Profiles** | ✅ | Load from YAML/JSON files |
| **Guided Labs** | ✅ | 7 pre-built educational scenarios |
| **Chaos Engineering** | ✅ | Random fault injection for resilience testing |
| **CLI Interface** | ✅ | Full argparse support + interactive menu |
| **Unit Tests** | ✅ | pytest framework with 40+ tests |
| **Zero Dependencies** | ✅ | Core runs with stdlib only |

### Attack Profiles

```
HTTP Steady Load     → Constant request pressure
Burst Traffic        → Sudden spikes (flash crowd)
Slow Client Attack   → Long-lived connections  
Wave Pattern         → Periodic load cycles
Chaos Engineering    → Random fault injection
```

### Guided Labs (Educational)

```
Lab 1  → Queue Overflow Basics (BEGINNER)
Lab 2  → Slowloris Connection Exhaustion (BEGINNER)
Lab 3  → Burst Traffic Response (INTERMEDIATE)
Lab 4  → Error Rate Cascade (INTERMEDIATE)
Lab 5  → Queue Limit Impact (INTERMEDIATE)
Lab 6  → Server Recovery Dynamics (ADVANCED)
Lab 7  → Chaos Engineering (ADVANCED)
```

Each lab includes:
- Pre-configured scenario
- Educational narration
- Real-time metrics
- Key insight summary

---

## 🔧 Usage Modes

### 1. Interactive Menu Mode (Default)

```bash
python netloader-x.py

→ Configure Simulation
→ Select Attack Profile
→ View Server Behavior
→ Access Help/Theory
→ Start Simulation
→ View Real-time Dashboard
```

### 2. Quick Test (Demo Mode)

```bash
# 30-second HTTP load test with defaults
python netloader-x.py quick-test

# Short version (10 seconds)
python netloader-x.py quick-test --short

# Without dashboard
python netloader-x.py quick-test --skip-dashboard
```

### 3. Guided Labs (Learning Mode)

```bash
# List all available labs
python netloader-x.py labs --list

# Run specific lab with narration
python netloader-x.py labs --lab 1

# Show lab description without running
python netloader-x.py labs --lab 1 --description-only

# Run without educational narration
python netloader-x.py labs --lab 3 --no-interactive
```

### 4. Batch Mode (CLI)

```bash
# HTTP profile, 50 threads, 60 seconds
python netloader-x.py run --profile http --threads 50 --duration 60

# Burst profile with custom rate
python netloader-x.py run --profile burst --rate 8000 --duration 45

# Slow client attack
python netloader-x.py run --profile slow --threads 100 --duration 120

# Batch mode (skip interactive prompts)
python netloader-x.py run --profile http --batch
```

### 5. Configuration Validation

```bash
# Basic validation
python netloader-x.py validate

# Detailed validation report
python netloader-x.py validate --detailed

# Validate custom config file
python netloader-x.py validate --config profiles.json
```

### 6. Custom Profile Mode

```bash
# Create custom profiles file
cat > my-profiles.json << 'EOF'
{
  "attack_profiles": [
    {
      "name": "custom-http",
      "description": "My custom HTTP load",
      "profile_type": "http",
      "threads": 75,
      "duration": 90,
      "base_rate": 2000,
      "max_rate": 6000,
      "jitter": 0.1
    }
  ]
}
EOF

# Load custom profiles
python netloader-x.py run --config-file my-profiles.json
```

---

## 📊 Output & Reports

### Real-Time Dashboard

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
[rps     ] |######################                    |

Latency (ms)
------------------------------------------------------------
Average Latency     : 145.3 ms
Latency Jitter      : 52.1 ms
[latency ] |###########                               |

Queue Depth
------------------------------------------------------------
Current Queue Depth : 487
Max Queue Observed  : 892
[queue   ] |####################                      |

Error Rate
------------------------------------------------------------
Current Error Rate  : 8.45%
Average Error Rate  : 2.34%
[errors  ] |##                                        |
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

#### HTML Report Features

- Interactive Chart.js graphs
- Real-time metrics with statistics
- Time-series visualization
- Exportable data tables
- Responsive design
- Professional dark theme

#### CSV Format

```csv
tick,queue_depth,active_workers,cpu_pressure,latency_ms,error_rate,degraded,crashed
1,12,8,0.125,52.5,0.001,False,False
2,18,12,0.187,68.3,0.002,False,False
3,25,15,0.234,85.9,0.003,False,False
...
```

---

## 🎓 Learning Content

### Built-in Help Menu

Access comprehensive theory explanations:

```
[1] What is NetLoader-X?
[2] Traffic Load vs Attacks
[3] Simulated Attack Profiles
[4] Threading & Speed Model
[5] Server Failure Behavior
[6] Defensive Takeaways
[7] Ethical Use & Scope
```

### Guided Labs with Narration

Each lab includes:
- **Description**: What you'll observe
- **Narrative**: Educational explanation during run
- **Metrics**: Real-time data collection
- **Key Insight**: Main takeaway for learning

Example (Lab 1: Queue Overflow):
```
"Watch the metrics as the simulation runs:
1. Queue depth will grow steadily
2. Latency will increase non-linearly
3. Error rate will climb as queue fills
4. The server won't crash, but degradation is obvious

KEY INSIGHT: Queues are your warning system.
When queue depth exceeds 50% of capacity, act immediately."
```

---

## ⚙️ Configuration

### Predefined Server Profiles

```python
"small-web"       # 20 workers, 200 queue
"api-backend"     # 50 workers, 500 queue
"enterprise-app"  # 120 workers, 1200 queue
```

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

```python
SAFETY_CAPS = {
    "ALLOW_NETWORK_IO": False,           # No sockets
    "ALLOW_EXTERNAL_TARGETS": False,     # Localhost only
    "ALLOW_RAW_TRAFFIC": False,          # No packets
    "MAX_SIMULATION_TIME_SEC": 3600,     # 1 hour max
    "MAX_VIRTUAL_CLIENTS": 100_000,      # Abstract only
    "MAX_EVENTS_PER_SECOND": 1_000_000,  # Rate cap
}
```

---

## 🔬 Testing

### Run Unit Tests

```bash
# Install pytest (if needed)
pip install pytest

# Run all tests
pytest tests/test_all.py -v

# Run specific test class
pytest tests/test_all.py::TestMetricsCollector -v

# With coverage
pytest tests/test_all.py --cov=core --cov=ui --cov=utils

# Run only integration tests
pytest tests/test_all.py::TestIntegration -v
```

### Test Coverage

- ✅ Core simulation (95%+)
- ✅ Safety limits (100%)
- ✅ Metrics (100%)
- ✅ Configuration (95%)
- ✅ CLI parsing (90%)
- ✅ Validators (95%)

---

## 🛡️ Security Features

### Absolute Safety Guarantees

- ✅ **No External Network Access**: Hard-coded, impossible to bypass
- ✅ **Localhost Only**: Enforced at every layer
- ✅ **No Real Attacks**: Pure simulation, behavioral modeling
- ✅ **Rate Limited**: Hard caps on all operations
- ✅ **Thread-Safe**: Concurrent access properly synchronized
- ✅ **Input Validated**: All user input checked
- ✅ **No Code Injection**: Zero `eval()`, `exec()`, dangerous patterns

### Compliance

- ✅ Safe for student lab environments
- ✅ Safe for air-gapped networks
- ✅ GDPR compliant (no data collection)
- ✅ No telemetry or external calls
- ✅ Transparent, auditable code

See [SECURITY.md](SECURITY.md) for detailed security policy and best practices.
---

## 📚 Project Structure

```
NetLoader-X/
├── netloader-x.py                    # Main entry point (CLI + interactive)
├── cli.py                            # argparse interface
│
├── core/                             # Simulation engine
│   ├── config.py                     # Configuration & safety limits
│   ├── engine.py                     # Core loop orchestrator
│   ├── scheduler.py                  # Load scheduling (RampProfile, WaveProfile, etc)
│   ├── profiles.py                   # Attack profiles (HTTP, Burst, SlowClient)
│   ├── simulations.py                # Behavior models
│   ├── metrics.py                    # Data collection & aggregation
│   ├── limiter.py                    # RateLimiter & SafetyLimiter
│   ├── fake_server.py                # Server behavior simulation
│   ├── guided_labs.py                # 7 pre-built learning scenarios
│   ├── chaos_engineering.py          # Random fault injection
│   └── profile_loader.py             # Load YAML/JSON profiles
│
├── ui/                               # User interface
│   ├── menu.py                       # Interactive menu system
│   ├── banner.py                     # ASCII art banner
│   ├── dashboard.py                  # Real-time metrics display
│   ├── help_menu.py                  # Educational content
│   └── theme.py                      # ANSI colors & styling
│
├── targets/                          # Target simulators
│   └── localhost.py                  # Simulated server behavior
│
├── utils/                            # Utilities
│   ├── logger.py                     # Event logging
│   ├── validators.py                 # Input validation
│   ├── reporter.py                   # Report orchestration
│   ├── reporting.py                  # Format exporters
│   └── html_report.py                # HTML template generation
│
├── tests/                            # Unit tests
│   └── test_all.py                   # Complete pytest suite
│
├── output/                           # Generated reports (created at runtime)
├── requirements.txt                  # Python dependencies (optional)
├── README.md                         # This file
├── SECURITY.md                       # Security policy & best practices
├── CONTRIBUTING.md                   # Contribution guidelines
├── DOCS.md                           # Documentation index
├── .gitignore                        # Version control exclusions
└── LICENSE                           # Educational use license
```

---

## 🎓 Educational Value

### What Students Learn

1. **Load Behavior Patterns**
   - How request rate affects latency
   - Queue dynamics under stress
   - Non-linear degradation curves

2. **Server Characteristics**
   - Worker pool exhaustion
   - Queue overflow handling
   - Timeout and error emergence

3. **Defensive Strategies**
   - Rate limiting effectiveness
   - Connection timeouts necessity
   - Queue depth monitoring
   - Circuit breaker patterns

4. **Chaos Engineering**
   - Resilience testing approaches
   - Failure mode simulation
   - Recovery observation

5. **System Design Principles**
   - Capacity planning
   - SLA definition
   - Threshold setting
   - Alert tuning

### Example Lesson Flow

```
Lesson 1: Understand queue growth
→ Run Lab 1 with 20 threads
→ Observe queue filling at ~200 requests
→ Learn: Queue is early warning system

Lesson 2: Connection exhaustion  
→ Run Lab 2 with slow clients
→ See few clients blocking all workers
→ Learn: Timeouts are critical

Lesson 3: Design defenses
→ Adjust limits in config
→ Re-run with new parameters
→ Measure improvement
→ Build intuition about thresholds
```

---

## 🔍 Troubleshooting

### Common Issues

**Q: Menu selections not recognized**  
A: Enter only the number (1-6), then press ENTER

**Q: Dashboard appears frozen**  
A: Normal - it updates every 0.5 seconds. Press Ctrl+C to see summary

**Q: "ImportError: No module named 'pyyaml'"**  
A: Optional. Install with: `pip install pyyaml`

**Q: Simulation won't start**  
A: Ensure you've selected a profile (option [2] first)

**Q: No reports generated**  
A: Check `outputs/` directory exists and is writable

**Q: "Permission denied" on outputs**  
A: Run from directory where you have write access

### Debug Mode

```bash
# Enable verbose logging
python netloader-x.py --verbose

# Validate configuration
python netloader-x.py validate --detailed

# Check imports
python -c "import netloader-x; print('OK')"
```

---

## 📈 Performance Metrics

### Typical Run (50 threads, 60 sec)

```
Ticks Executed:        ~60
Virtual Clients:       50
Peak RPS:              4,500+
Memory Usage:          <50MB
CPU Per Thread:        <1%
Report Generation:     <100ms
```

### Scalability Limits

| Metric | Limit | Reason |
|--------|-------|--------|
| Duration | 3600 sec | Hard cap in config |
| Threads | 100,000 | Virtual client limit |
| Events/sec | 1,000,000 | Rate limit |
| Simulation Time | <1 hour | Resource constraint |

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

- ✅ Use for learning
- ✅ Use for defensive testing
- ✅ Use in academic settings
- ✅ Modify for your needs

- ❌ Use for real attacks
- ❌ Use for unauthorized testing  
- ❌ Claim as your own
- ❌ Remove this license

---

## 📞 Contact & Support

**Author**: voltsparx  
**Email**: voltsparx@gmail.com  
**GitHub**: https://github.com/voltsparx/NetLoader-X  
**Version**: 1.0.0-sim  

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

- [Security Policy](SECURITY.md) - Security guarantees and best practices
- [Contributing Guide](CONTRIBUTING.md) - How to contribute to the project
- [Guided Labs Guide](core/guided_labs.py) - Educational scenarios
- [API Documentation](core/engine.py) - Core engine reference
- [Configuration Reference](core/config.py) - Configuration options

---

**NetLoader-X** — *Learn. Simulate. Defend.* 🛡️
    "burst_multiplier": 2.0,
    "cooldown_seconds": 15,
}

SERVER_MODEL_DEFAULTS = {
    "worker_pool_size": 256,       # Virtual workers
    "max_queue_depth": 10_000,     # Request queue limit
    "base_latency_ms": 50,         # Normal response time
    "latency_growth_factor": 1.15, # Degradation rate
    "timeout_threshold_ms": 5_000,
    "error_rate_base": 0.01,
    "error_rate_growth": 1.2,
}
```

### Server Profiles

Choose from pre-configured profiles in `targets/localhost.py`:

```python
SERVER_PROFILES = {
    "small-web": {
        "max_workers": 20,
        "queue_limit": 200,
        "base_latency_ms": 40,
        "timeout_ms": 2000,
        "crash_threshold": 0.95
    },
    "api-backend": {
        "max_workers": 50,
        "queue_limit": 500,
        "base_latency_ms": 25,
        "timeout_ms": 1500,
        "crash_threshold": 0.92
    },
    "enterprise-app": {
        "max_workers": 120,
        "queue_limit": 1200,
        "base_latency_ms": 60,
        "timeout_ms": 3000,
        "crash_threshold": 0.98
    }
}
```

---

## Output & Reports

### Real-Time Dashboard

Press **[CTRL+C]** to stop and see final summary.

### Generated Reports

After each simulation, reports are saved to:

```
outputs/
  ├── <PROFILE>_<TIMESTAMP>/
  │   ├── metrics.json     # Raw simulation data
  │   ├── metrics.csv      # Time-series for analysis
  │   └── metrics.html     # Interactive report
```

#### CSV Format Example

```csv
tick,requests,latency_ms,error_rate,queue_depth
1,150,45.3,0.001,12
2,156,47.2,0.002,18
3,142,44.8,0.001,15
...
```

#### HTML Report Example

- Interactive metrics tables
- Statistical summary (min, max, avg, p90, p99)
- Time-series graphs
- Export-ready visualizations

---

## Project Structure

```
NetLoader-X/
├── netloader-x.py              # Main entry point
│
├── core/                        # Simulation engine
│   ├── config.py               # Configuration & safety limits
│   ├── engine.py               # Core simulation loop
│   ├── profiles.py             # Traffic profiles
│   ├── simulations.py          # Attack pattern models
│   ├── metrics.py              # Data collection
│   ├── limiter.py              # Rate limiting & safety
│   ├── scheduler.py            # Load scheduling
│   └── fake_server.py          # Server behavior model
│
├── targets/                     # Target simulation
│   └── localhost.py            # Simulated server
│
├── ui/                         # User interface
│   ├── banner.py               # ASCII art banner
│   ├── menu.py                 # Interactive menus
│   ├── dashboard.py            # Live monitoring
│   ├── help_menu.py            # Educational content
│   └── theme.py                # Styling & colors
│
├── utils/                      # Utilities
│   ├── logger.py               # Logging functions
│   ├── validators.py           # Input validation
│   ├── reporter.py             # Report generation
│   ├── reporting.py            # Export formats
│   └── html_report.py          # HTML templates
│
├── output/                     # Generated reports
├── README.md                   # This file
└── requirements.txt            # Python dependencies
```

---

## Safety & Ethics

### What NetLoader-X Does NOT Do

❌ **No real network traffic** - Pure mathematical simulation
❌ **No external targets** - Localhost only
❌ **No packet generation** - No raw sockets
❌ **No real denial-of-service** - No attack capability

### Safety Enforcement

Hard safety caps are enforced at runtime:

```python
SAFETY_CAPS = {
    "ALLOW_NETWORK_IO": False,           # Absolutely no sockets
    "ALLOW_EXTERNAL_TARGETS": False,     # No IPs, no domains
    "ALLOW_RAW_TRAFFIC": False,          # No packets
    "MAX_SIMULATION_TIME_SEC": 3600,     # 1 hour max
    "MAX_VIRTUAL_CLIENTS": 100_000,
    "MAX_EVENTS_PER_SECOND": 1_000_000,
    "FORCE_LOCAL_MODE": True,
}
```

### Educational Use Only

This tool is designed for:
- ✓ Learning load behavior concepts
- ✓ Understanding server degradation
- ✓ Testing defensive strategies
- ✓ Capacity planning
- ✓ Academic research
- ✓ Safe resilience testing

**NOT** for:
- ✗ Attacking real systems
- ✗ Unauthorized testing
- ✗ Malicious purposes
- ✗ Violating terms of service

---

## Defensive Takeaways

### Key Concepts Demonstrated

**1. Request Rate vs Response Time**
- As load increases, latency grows exponentially
- Queue depth fills before errors appear
- Graceful degradation prevents collapse

**2. Connection Exhaustion (Slowloris)**
- Few threads can exhaust worker pools
- Long-lived connections hold resources
- Timeout enforcement is critical

**3. Burst Behavior**
- Flash crowds create unexpected pressure
- Burst multipliers show vulnerability window
- Circuit breakers can prevent cascades

**4. Error Rates**
- Error rates grow with load quadratically
- Client-side retry storms amplify effects
- Exponential backoff is essential

### Recommended Defenses

1. **Rate Limiting** - Enforce per-IP/user limits
2. **Connection Timeouts** - Disconnect idle clients
3. **Queue Caps** - Reject when queue exceeds threshold
4. **Circuit Breakers** - Fail fast under stress
5. **Load Shedding** - Prioritize critical requests
6. **Auto-scaling** - Add capacity before degradation
7. **Monitoring** - Alert on queue growth and error rates

---

## Troubleshooting

### Menu Navigation Issues

**Problem:** Menu selections aren't being recognized
- **Solution:** Enter only the number (1-6), press Enter

### Dashboard Not Updating

**Problem:** Real-time dashboard appears frozen
- **Solution:** This is normal; it updates every 0.5 seconds. Wait or press Ctrl+C to see final summary

### Missing Dependencies

**Problem:** `ImportError: No module named 'rich'`
- **Solution:** Install optional dependencies: `pip install rich`

### Simulation Won't Start

**Problem:** "Select an attack profile first"
- **Solution:** Use menu option [2] to choose a profile before starting

### Reports Not Generated

**Problem:** No output files created
- **Solution:** Check that `outputs/` directory exists and is writable

---

## Performance Notes

- Simulations are CPU-bound, not I/O bound
- Default 50 threads on a modern CPU runs at 5000+ RPS
- Increase `--threads` parameter for higher load
- Longer durations provide more statistical data

---

## Requirements

```txt
rich>=12.0.0          # Optional: Enhanced terminal output
```

No other external dependencies required. Python standard library is sufficient.

---

## Author

**voltsparx**
- Email: voltsparx@gmail.com
- GitHub: https://github.com/voltsparx

---

## Version

**v1.0.0-sim** (Simulation Framework)

---

## License

Educational & Defensive Simulation Only

This tool is provided for educational purposes and defensive testing only. Use responsibly and ethically. Unauthorized testing against systems you don't own or have permission to test is illegal.

---

## Contributing

Found a bug? Have an idea? Feel free to submit issues and pull requests.

---

## Disclaimer

This is a **SIMULATION TOOL ONLY**. It does not generate real network traffic or perform actual attacks. Use for learning and defensive purposes only. The author assumes no liability for misuse of this tool.

---

## Quick Reference

### Commands

| Command | Effect |
|---------|--------|
| `python netloader-x.py` | Start interactive menu |
| Menu [1] | Configure simulation parameters |
| Menu [2] | Select attack profile |
| Menu [3] | View server behavior settings |
| Menu [4] | Access educational content |
| Menu [5] | Begin simulation |
| Menu [6] | Exit tool |
| Ctrl+C | Stop active simulation |

### Profiles

| Profile | Behavior | Use Case |
|---------|----------|----------|
| HTTP Steady | Constant load | Baseline testing |
| HTTP Burst | Sudden spikes | Flash crowd simulation |
| Slow Client | Long-lived connections | Connection exhaustion |
| Wave Pattern | Periodic waves | Cyclical traffic |

### Reports

| Format | Location | Purpose |
|--------|----------|---------|
| JSON | `metrics.json` | Raw data, programmatic analysis |
| CSV | `metrics.csv` | Spreadsheet import, time-series |
| HTML | `metrics.html` | Visual presentation, stakeholders |

---

**Happy simulating!** Stay safe and keep learning. 🛡️
