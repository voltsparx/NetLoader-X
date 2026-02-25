from __future__ import annotations

from typing import Any, Dict

from core.nano_ai import NanoAIAdvisor
from plugins.base import SimulationPlugin


class NanoCoachPlugin(SimulationPlugin):
    name = "nano-coach"
    description = "Adds Nano AI risk score and runtime coaching hints."

    def __init__(self):
        self.advisor = NanoAIAdvisor()

    def apply(self, snapshot: Dict[str, Any], state: Dict[str, Any]) -> Dict[str, Any]:
        score = self.advisor.risk_score(snapshot)
        snapshot["nano_ai_risk_score"] = score
        snapshot["nano_ai_hint"] = self.advisor.advise_tick(snapshot)
        return snapshot
