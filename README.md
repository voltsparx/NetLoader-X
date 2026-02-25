# NetLoader-X (v4.0)

Defensive Load & Failure Simulation Framework

NetLoader-X is a Python project for learning how systems degrade under stress by simulating load, backpressure, retries, and failure modes entirely offline.

This is not a real load generator. It does not send network traffic.

See also:
- `Usage.txt`
- `TERMINOLOGY.txt`

## Safety First (Non-Negotiable)

NetLoader-X is designed to stay defensive:
- No sockets, no packet crafting, no raw traffic features
- No external targets (localhost-only validation)
- Hard safety caps are enforced at startup (`core/config.py`)

If you need to performance-test a real service with real traffic, use a dedicated load-testing tool. NetLoader-X is for offline simulation and resilience learning.

## Requirements

- Python 3.8+ (tested on Python 3.13)
- Core simulation runs on the Python standard library

Optional dependencies (only needed for specific features):
- `pyyaml` to load `.yaml/.yml` cluster configs (JSON works with stdlib)
- `flask` + `flask-cors` for the local web dashboard
- `pytest` for the test suite

Install optional dependencies:

```bash
pip install -r requirements.txt
```

## Build Standalone Binary

NetLoader-X includes a small cross-platform binary build setup using PyInstaller.

Install build dependency:

```bash
pip install -r requirements-build.txt
```

Build binary (test mode: build only):

```bash
python scripts/install-netloader-x-binary.py --mode test --clean-dist --verify
```

Install binary (interactive mode):

```bash
python scripts/install-netloader-x-binary.py --mode install --clean-dist
```

Build output defaults to `bin/`.
Default persistent report output directory is `$HOME/netloader-x-output`.

For full details, see [`docs/BinaryBuild.md`](docs/BinaryBuild.md).

## Quick Start

Interactive menu:

```bash
python netloader-x.py
```

Quick demo:

```bash
python netloader-x.py quick-test
python netloader-x.py quick-test --short
```

CLI run:

```bash
python netloader-x.py run --profile http --threads 50 --duration 60
python netloader-x.py run --profile wave --threads 80 --duration 90 --chaos --chaos-rate 0.05
```

Guided labs:

```bash
python netloader-x.py labs --list
python netloader-x.py labs --lab 1
```

Validate safety + configuration:

```bash
python netloader-x.py validate
python netloader-x.py validate --detailed
```

## Commands

Run `python netloader-x.py --help` for the full list. Common subcommands:

| Command | Purpose |
| --- | --- |
| `run` | Run a configurable simulation from the CLI |
| `quick-test` | Fast demo run |
| `labs` | Guided educational scenarios |
| `validate` | Validate safety caps and show config |
| `cluster` | Multi-backend cluster simulation mode |
| `report` | Summarize existing `metrics.json` files |
| `web` | Local web dashboard (optional) |

### Global Flags

Global flags work both before or after the subcommand:

```bash
python netloader-x.py --no-report quick-test --short
python netloader-x.py quick-test --short --no-report
```

Common global flags:
- `--output-dir`, `-o`: base output folder (default: `$HOME/netloader-x-output`)
- `--seed`: deterministic runs
- `--no-report`: skip report export (no file writes)
- `--verbose`, `-v`: extra logs
- `--version`: print version and exit

## Profiles (What To Simulate)

The CLI uses these profile names:
- `http`: steady request pressure
- `burst`: repeated spike windows
- `slow`: slow/long-lived client pressure
- `wave`: periodic demand oscillation
- `retry`: retry-storm amplification behavior
- `cache`: cache-bypass / expensive-request pressure
- `mixed`: combined multi-vector behavior

Example:

```bash
python netloader-x.py run --profile mixed --threads 60 --duration 90
```

## Reports (HTML Output)

Unless you use `--no-report`, each run exports a new folder under your output directory (default: `$HOME/netloader-x-output`):

```
$HOME/netloader-x-output/<RUN_NAME>_<YYYY-MM-DD_HH-MM-SS>/
```

Files in that folder:
- `metrics.json`: full raw ticks + aggregates + time series
- `metrics.csv`: raw tick table
- `metrics.html`: HTML report with charts and bar graphs (self-contained)
- `summary.txt`: quick text summary

Open `metrics.html` in your browser to view:
- trend charts (SVG)
- bar graphs (tick states and totals)
- a quick link row to `metrics.json`, `metrics.csv`, `summary.txt`

## Cluster Mode

Cluster mode simulates:
- a load balancer (multiple algorithms)
- multiple backends with different capacities
- a database/cache layer with a connection pool

Run with the stdlib-only JSON example:

```bash
python netloader-x.py cluster --config cluster-config-example.json --duration 60 --rate 100
```

YAML configs are also supported, but require PyYAML:

```bash
pip install pyyaml
python netloader-x.py cluster --config cluster-config-example.yaml
```

Supported load balancer algorithms:
- `round-robin`
- `least-connections`
- `random`
- `weighted-round-robin`
- `ip-hash`

## Local Web Dashboard (Optional)

The web dashboard streams metrics locally from an offline simulation engine.

Install:

```bash
pip install flask flask-cors
```

Run:

```bash
python netloader-x.py web --host 127.0.0.1 --port 8080
```

## Report Analysis (Batch Summaries)

Summarize report folders containing `metrics.json` files:

```bash
python netloader-x.py report "$HOME/netloader-x-output"
```

## Development

Syntax check:

```bash
python -m compileall core utils ui targets cli.py netloader-x.py
```

Quick smoke tests (stdlib-only):

```bash
python -m unittest -v tests.test_smoke_unittest
```

Tests (requires pytest):

```bash
pip install pytest
python -m pytest tests/test_all.py -v
```

## Project Layout

| Path | Purpose |
| --- | --- |
| `netloader-x.py` | Main entry point |
| `cli.py` | Argument parsing |
| `core/` | Simulation engine, safety caps, metrics, cluster mode |
| `targets/` | Localhost-only simulation targets |
| `ui/` | Terminal banner/menu/dashboard |
| `utils/` | Reporting and helpers |
| `tests/` | Test suite |

## License

Educational & Defensive Simulation Only.

See `SECURITY.md` for additional safety notes.
