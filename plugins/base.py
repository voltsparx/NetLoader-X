from __future__ import annotations

from typing import Any, Dict


class SimulationPlugin:
    name = "base"
    description = "Base plugin"

    def apply(self, snapshot: Dict[str, Any], state: Dict[str, Any]) -> Dict[str, Any]:
        return snapshot
