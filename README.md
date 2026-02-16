# NetLoader-X

**Defensive Load & Failure Simulation Framework**

A safe, educational tool for simulating server stress patterns and analyzing how systems behave under load—entirely offline, localhost-only, with no real network traffic.

---

## Overview

NetLoader-X is designed for **defensive engineers, system architects, and DevOps teams** who need to understand:

- How servers degrade under stress
- Where capacity bottlenecks occur
- How to design resilient systems
- What defensive thresholds to implement

This is **NOT** a real attack tool. It models the *effects* of various load patterns using pure mathematical simulation, allowing you to study attack concepts safely in a controlled environment.

---

## Features

✓ **100% Offline & Safe**
- No network I/O, no sockets, no packets sent
- Localhost-only simulation
- Hard safety caps enforced at runtime

✓ **Multiple Attack Profiles**
- HTTP Steady Load
- HTTP Burst Traffic
- Slow Client Attacks (Slowloris-style)
- HTTP Flood Simulation
- ICMP Storm Simulation
- Connection Flood Simulation

✓ **Realistic Server Modeling**
- Virtual worker pools
- Request queues
- Dynamic latency growth
- Error rate simulation
- Graceful degradation & recovery

✓ **Professional Reporting**
- Real-time dashboard
- CSV metrics export
- JSON raw data
- HTML visual reports with graphs

✓ **Educational First**
- Detailed theory documentation
- Load pattern explanations
- Defensive takeaways
- Built-in help menu

---

## Installation

### Prerequisites

- Python 3.8 or higher
- `pip` (Python package manager)

### Quick Start

1. **Clone the repository:**
   ```bash
   git clone https://github.com/voltsparx/NetLoader-X.git
   cd NetLoader-X
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run NetLoader-X:**
   ```bash
   python netloader-x.py
   ```

### Optional Dependencies

For enhanced terminal output:
```bash
pip install rich
```

---

## Usage

### Interactive Menu

Simply run the tool:

```bash
python netloader-x.py
```

You'll be presented with an interactive menu:

```
[1] Configure Simulation
[2] Select Attack Profile
[3] Target & Server Behavior
[4] View Help / Theory
[5] Start Simulation
[6] Exit
```

### Menu Options

**1. Configure Simulation**
- Adjust thread count (default: 50)
- Set duration (default: 60 seconds)
- Configure rate limiting
- Set jitter and variability

**2. Select Attack Profile**
```
[1] HTTP Flood (Simulated)        - Constant request pressure
[2] Burst Traffic Pattern         - Sudden spikes
[3] Slow Client Behavior          - Connection exhaustion
[4] Wave / Pulsing Load           - Periodic waves
```

**3. Target & Server Behavior**
- View server profile settings
- Queue limits
- Timeout thresholds
- Error rate models

**4. View Help / Theory**
- Learn about load patterns
- Understand server degradation
- Defensive recommendations
- Ethical guidelines

**5. Start Simulation**
- See real-time dashboard
- Monitor requests/second
- Track latency growth
- Watch error rates increase
- Observe queue buildup

---

## Examples

### Example 1: HTTP Flood Simulation

```bash
$ python netloader-x.py
```

```
Select option > 2  (Select Attack Profile)
Select option > 1  (HTTP Flood)
Select option > 5  (Start Simulation)

[?] Start simulation? (yes/no): yes

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

[CTRL+C] Stop simulation safely
```

### Example 2: Slow Client Behavior

```bash
$ python netloader-x.py
```

```
Select option > 2  (Select Attack Profile)
Select option > 3  (Slow Client Behavior)
Select option > 5  (Start Simulation)
```

This simulates long-lived connections that hold resources without completing requests, similar to a Slowloris attack.

### Example 3: Burst Traffic Pattern

```bash
Select option > 2  (Select Attack Profile)
Select option > 2  (Burst Traffic Pattern)
Select option > 5  (Start Simulation)
```

Models flash-crowd behavior with sudden spikes followed by calm periods.

---

## Configuration

### Simulation Parameters

Edit defaults in `core/config.py`:

```python
ENGINE_DEFAULTS = {
    "tick_resolution_ms": 10,      # Event granularity
    "random_seed": None,           # Set for deterministic runs
    "enable_jitter": True,         # Realistic variability
    "jitter_percent": 5.0,         # Amount of variation
    "log_every_n_ticks": 100,      # Logging frequency
}

LIMITER_DEFAULTS = {
    "max_virtual_rps": 50_000,     # Safety cap on requests
    "ramp_up_seconds": 30,
    "ramp_down_seconds": 20,
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
