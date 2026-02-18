"""
Minimal stdlib-only smoke tests.

These are intentionally lightweight so contributors can run a quick sanity check
without installing pytest or any optional dependencies.
"""

import unittest


class TestSmoke(unittest.TestCase):
    def test_engine_tick_export_and_html_report(self):
        from core.engine import Engine
        from utils.html_report import build_html_report

        engine = Engine()
        engine.configure("small-web", "HTTP", threads=10, duration=10, seed=123)

        # Manual ticks keep the test fast (Engine.run sleeps per tick).
        for _ in range(5):
            engine.tick(planned_rate=120, scheduler_tick=engine.current_tick)

        engine.metrics.finalize()
        payload = engine.export_metrics()
        html = build_html_report(payload, attack_name="SMOKE")

        self.assertIn("<html", html.lower())
        self.assertIn("metrics.json", html)  # report artifacts links
        self.assertIn("bar-fill", html)  # bar graph CSS class
        self.assertIn("class=\"spark\"", html)  # SVG chart class

    def test_cli_accepts_global_flags_after_subcommand(self):
        from cli import CLIParser

        parser = CLIParser()

        args_after = parser.parse(["quick-test", "--short", "--no-dashboard", "--no-report"])
        self.assertTrue(args_after.no_report)
        self.assertTrue(args_after.no_dashboard)

        # Regression guard: global flag before subcommand must also work.
        args_before = parser.parse(["--no-report", "quick-test", "--short", "--no-dashboard"])
        self.assertTrue(args_before.no_report)
        self.assertTrue(args_before.no_dashboard)


if __name__ == "__main__":
    unittest.main(verbosity=2)
