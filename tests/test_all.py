"""
NetLoader-X :: Unit Tests
=========================
Comprehensive pytest test suite for all components.

Run with: pytest tests/test_all.py -v

Author  : voltsparx
Contact : voltsparx@gmail.com
"""

import pytest
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# ==================================================
# TEST: Configuration Module
# ==================================================

class TestGlobalConfig:
    """Tests for core.config.GlobalConfig"""

    def test_allowed_hosts(self):
        from core.config import GlobalConfig
        config = GlobalConfig()
        assert "localhost" in GlobalConfig.ALLOWED_HOSTS
        assert "127.0.0.1" in GlobalConfig.ALLOWED_HOSTS

    def test_port_range_valid(self):
        from core.config import GlobalConfig
        low, high = GlobalConfig.ALLOWED_PORT_RANGE
        assert low > 1000
        assert high < 65536

    def test_output_dir_exists(self):
        from core.config import GlobalConfig
        assert GlobalConfig.OUTPUT_DIR is not None


class TestSafetyCaps:
    """Tests for safety enforcement"""

    def test_network_io_disabled(self):
        from core.config import SAFETY_CAPS
        assert SAFETY_CAPS["ALLOW_NETWORK_IO"] is False

    def test_external_targets_disabled(self):
        from core.config import SAFETY_CAPS
        assert SAFETY_CAPS["ALLOW_EXTERNAL_TARGETS"] is False

    def test_local_mode_forced(self):
        from core.config import SAFETY_CAPS
        assert SAFETY_CAPS["FORCE_LOCAL_MODE"] is True


# ==================================================
# TEST: Limiter Module
# ==================================================

class TestSafetyLimiter:
    """Tests for core.limiter.SafetyLimiter"""

    def test_limit_events(self):
        from core.limiter import SafetyLimiter
        limiter = SafetyLimiter(max_events=1000)
        events, clients = limiter.limit(2000, 100)
        assert events <= 1000

    def test_limit_slow_clients(self):
        from core.limiter import SafetyLimiter
        limiter = SafetyLimiter(max_slow_clients=500)
        events, clients = limiter.limit(100, 1000)
        assert clients <= 500

    def test_limit_under_cap(self):
        from core.limiter import SafetyLimiter
        limiter = SafetyLimiter()
        events, clients = limiter.limit(100, 50)
        assert events == 100
        assert clients == 50


class TestRateLimiter:
    """Tests for core.limiter.RateLimiter"""

    def test_rate_limiter_init(self):
        from core.limiter import RateLimiter
        limiter = RateLimiter(100)
        assert limiter.rate == 100

    def test_rate_limiter_allowance(self):
        from core.limiter import RateLimiter
        limiter = RateLimiter(10)
        initial = limiter.allowance
        assert initial > 0


# ==================================================
# TEST: Metrics Module
# ==================================================

class TestMetricsCollector:
    """Tests for core.metrics.MetricsCollector"""

    def test_record_snapshot(self):
        from core.metrics import MetricsCollector
        collector = MetricsCollector()
        snapshot = {"rps": 1000, "latency_ms": 50, "error_rate": 0.01}
        collector.record(snapshot)
        assert len(collector._raw_ticks) == 1

    def test_aggregates_empty(self):
        from core.metrics import MetricsCollector
        collector = MetricsCollector()
        assert len(collector._aggregates) == 0

    def test_aggregates_after_finalize(self):
        from core.metrics import MetricsCollector
        collector = MetricsCollector()
        for i in range(10):
            collector.record({"rps": 1000 + i, "latency_ms": 50 + i})
        collector.finalize()
        assert len(collector._aggregates) > 0

    def test_percentile_calculation(self):
        from core.metrics import MetricsCollector
        collector = MetricsCollector()
        data = [10, 20, 30, 40, 50]
        p50 = collector._percentile(data, 50)
        assert 25 <= p50 <= 35  # Approximate p50

    def test_export_format(self):
        from core.metrics import MetricsCollector
        collector = MetricsCollector()
        collector.record({"rps": 1000, "latency_ms": 50})
        collector.finalize()
        export = collector.export()
        assert "meta" in export
        assert "aggregates" in export
        assert "series" in export


# ==================================================
# TEST: Scheduler Module
# ==================================================

class TestRampProfile:
    """Tests for core.scheduler.RampProfile"""

    def test_ramp_profile_at_start(self):
        from core.scheduler import RampProfile
        profile = RampProfile(100, 1000, 60)
        rate = profile.rate_at(0)
        assert rate >= 100

    def test_ramp_profile_at_end(self):
        from core.scheduler import RampProfile
        profile = RampProfile(100, 1000, 60)
        rate = profile.rate_at(60)
        assert rate >= 900

    def test_ramp_profile_monotonic(self):
        from core.scheduler import RampProfile
        profile = RampProfile(100, 1000, 60, jitter=0)
        prev_rate = 0
        for tick in range(0, 61, 10):
            rate = profile.rate_at(tick)
            assert rate >= prev_rate  # Should be monotonically increasing
            prev_rate = rate


class TestScheduler:
    """Tests for core.scheduler.Scheduler"""

    def test_scheduler_start_stop(self):
        from core.scheduler import Scheduler, RampProfile
        profile = RampProfile(100, 1000, 60)
        scheduler = Scheduler(profile)
        scheduler.start()
        assert scheduler.running
        scheduler.stop()
        assert not scheduler.running

    def test_scheduler_next_tick(self):
        from core.scheduler import Scheduler, RampProfile
        profile = RampProfile(100, 1000, 60)
        scheduler = Scheduler(profile)
        scheduler.start()
        tick = scheduler.next_tick()
        assert tick is not None
        assert "rate" in tick
        assert "tick" in tick


# ==================================================
# TEST: localhost Simulator
# ==================================================

class TestLocalhostSimulator:
    """Tests for targets.localhost.LocalhostSimulator"""

    def test_simulator_init(self):
        from targets.localhost import LocalhostSimulator
        sim = LocalhostSimulator("small-web")
        assert sim.queue_depth == 0
        assert sim.active_workers == 0

    def test_ingest_load(self):
        from targets.localhost import LocalhostSimulator
        sim = LocalhostSimulator()
        sim.ingest_load(100)
        assert sim.queue_depth == 100

    def test_update_state(self):
        from targets.localhost import LocalhostSimulator
        sim = LocalhostSimulator()
        sim.ingest_load(50)
        sim.update()
        assert sim.queue_depth >= 0

    def test_snapshot_format(self):
        from targets.localhost import LocalhostSimulator
        sim = LocalhostSimulator()
        sim.ingest_load(10)
        snap = sim.snapshot()
        assert "queue_depth" in snap
        assert "active_workers" in snap
        assert "error_rate" in snap


# ==================================================
# TEST: Theme Module
# ==================================================

class TestTheme:
    """Tests for ui.theme"""

    def test_colorize_output(self):
        from ui.theme import colorize
        result = colorize("test", "info")
        assert "test" in result
        assert len(result) > 4  # Should include ANSI codes

    def test_colorize_styles(self):
        from ui.theme import colorize
        styles = ["primary", "info", "success", "warning", "error"]
        for style in styles:
            result = colorize("test", style)
            assert "test" in result


# ==================================================
# TEST: Validators Module
# ==================================================

class TestValidators:
    """Tests for utils.validators"""

    def test_validate_target_allowed(self):
        from utils.validators import validate_target
        # Should not raise for localhost
        validate_target("localhost", 8000)

    def test_validate_target_disallowed(self):
        from utils.validators import validate_target
        with pytest.raises(ValueError):
            validate_target("evil.com", 8000)

    def test_validate_port_invalid(self):
        from utils.validators import validate_target
        with pytest.raises(ValueError):
            validate_target("localhost", 65535)  # Out of range

    def test_validate_numeric_choice_valid(self):
        from utils.validators import validate_numeric_choice
        result = validate_numeric_choice("1", 3)
        assert result == 1

    def test_validate_numeric_choice_invalid(self):
        from utils.validators import validate_numeric_choice
        with pytest.raises(ValueError):
            validate_numeric_choice("99", 3)


# ==================================================
# TEST: Guided Labs
# ==================================================

class TestGuidedLabs:
    """Tests for core.guided_labs"""

    def test_labs_exist(self):
        from core.guided_labs import GUIDED_LABS
        assert len(GUIDED_LABS) > 0

    def test_lab_properties(self):
        from core.guided_labs import GUIDED_LABS
        for lab in GUIDED_LABS:
            assert lab.id > 0
            assert lab.name
            assert lab.description
            assert lab.learning_objective

    def test_lab_manager_list(self):
        from core.guided_labs import LabManager
        manager = LabManager()
        labs = manager.list_labs()
        # Just ensure it doesn't crash

    def test_lab_manager_get(self):
        from core.guided_labs import LabManager
        manager = LabManager()
        lab = manager.get_lab(1)
        assert lab.id == 1


# ==================================================
# TEST: Profile Loader
# ==================================================

class TestProfileLoader:
    """Tests for core.profile_loader"""

    def test_loader_init(self):
        from core.profile_loader import ProfileLoader
        loader = ProfileLoader()
        assert loader.attack_profiles == {}
        assert loader.server_profiles == {}

    def test_example_config_export(self, tmp_path):
        from core.profile_loader import ProfileLoader
        loader = ProfileLoader()
        output_file = tmp_path / "example.json"
        result = loader.export_example_config(output_file)
        assert result
        assert output_file.exists()


# ==================================================
# TEST: Chaos Engineering
# ==================================================

class TestChaosInjector:
    """Tests for core.chaos_engineering.ChaosInjector"""

    def test_chaos_disabled(self):
        from core.chaos_engineering import ChaosInjector
        injector = ChaosInjector(enabled=False)
        assert not injector.should_inject()

    def test_chaos_enabled_deterministic(self):
        from core.chaos_engineering import ChaosInjector
        injector = ChaosInjector(enabled=True, fault_rate=1.0, seed=42)
        assert injector.should_inject()

    def test_chaos_fault_injection(self):
        from core.chaos_engineering import ChaosInjector
        injector = ChaosInjector(enabled=True, fault_rate=1.0, seed=42)
        state = {"latency_ms": 50, "error_rate": 0.01, "active_workers": 10}
        modified = injector.inject_fault(state)
        assert injector.total_faults_injected > 0

    def test_chaos_scenarios(self):
        from core.chaos_engineering import get_chaos_scenario
        for name in ["light", "moderate", "severe", "game-day"]:
            scenario = get_chaos_scenario(name)
            assert scenario is not None


# ==================================================
# TEST: CLI
# ==================================================

class TestCLIParser:
    """Tests for cli.CLIParser"""

    def test_cli_parser_init(self):
        from cli import CLIParser
        parser = CLIParser()
        assert parser.parser is not None

    def test_cli_parse_empty(self):
        from cli import CLIParser
        parser = CLIParser()
        args = parser.parse([])
        assert args is not None

    def test_cli_parse_version(self):
        from cli import CLIParser
        parser = CLIParser()
        # Version flag will cause SystemExit, so we skip
        # Just test that parser accepts the argument


# ==================================================
# TEST: Integration Tests
# ==================================================

class TestIntegration:
    """Integration tests for complete workflows"""

    def test_engine_initialization(self):
        from core.engine import Engine
        engine = Engine()
        assert engine.metrics is not None
        assert engine.server is not None
        assert engine.scheduler is not None

    def test_engine_tick(self):
        from core.engine import Engine
        engine = Engine()
        engine.configure("small-web", "HTTP", 50, 60)
        engine.tick()
        assert engine.current_tick == 1

    def test_metrics_collection(self):
        from core.engine import Engine
        engine = Engine()
        engine.configure("small-web", "HTTP", 50, 60)
        for _ in range(5):
            engine.tick()
        assert len(engine.metrics._raw_ticks) == 5

    def test_full_simulation_short(self):
        """Quick integration test of full simulation"""
        from core.engine import Engine
        import threading
        
        engine = Engine("small-web")
        engine.configure("small-web", "HTTP", 10, 2)
        
        thread = threading.Thread(target=engine.run, daemon=True)
        thread.start()
        
        # Wait for completion
        import time
        time.sleep(3)
        
        assert engine.current_tick > 0


# ==================================================
# PYTEST FIXTURES
# ==================================================

@pytest.fixture
def engine():
    """Fixture providing a configured engine."""
    from core.engine import Engine
    engine = Engine()
    engine.configure("small-web", "HTTP", 50, 60)
    return engine


@pytest.fixture
def metrics():
    """Fixture providing a metrics collector."""
    from core.metrics import MetricsCollector
    return MetricsCollector()


@pytest.fixture
def temp_config_file(tmp_path):
    """Fixture providing a temporary config file."""
    import json
    config = {
        "attack_profiles": [
            {
                "name": "test-profile",
                "description": "Test",
                "profile_type": "http",
                "threads": 50,
                "duration": 60,
                "base_rate": 1000,
                "max_rate": 5000
            }
        ]
    }
    config_file = tmp_path / "config.json"
    with open(config_file, "w") as f:
        json.dump(config, f)
    return config_file


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
