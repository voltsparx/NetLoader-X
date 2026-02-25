from __future__ import annotations

from typing import Any, Dict


class SnapshotFilter:
    name = "base"
    description = "Base filter"

    def apply(self, snapshot: Dict[str, Any], state: Dict[str, Any]) -> Dict[str, Any]:
        return snapshot
