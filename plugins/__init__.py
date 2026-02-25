from __future__ import annotations

from typing import Dict, Type

from plugins.base import SimulationPlugin
from plugins.nano_coach import NanoCoachPlugin
from plugins.resilience_score import ResilienceScorePlugin
from plugins.trend_lens import TrendLensPlugin


PLUGIN_REGISTRY: Dict[str, Type[SimulationPlugin]] = {
    NanoCoachPlugin.name: NanoCoachPlugin,
    TrendLensPlugin.name: TrendLensPlugin,
    ResilienceScorePlugin.name: ResilienceScorePlugin,
}


def available_plugins() -> Dict[str, Type[SimulationPlugin]]:
    return dict(PLUGIN_REGISTRY)
