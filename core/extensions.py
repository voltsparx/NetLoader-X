"""
NetLoader-X :: Plugin + Filter extension pipeline.
"""

from __future__ import annotations

from typing import Any, Dict, Iterable, List, Optional

from filters import available_filters
from plugins import available_plugins


def _normalize_name(name: str) -> str:
    return str(name or "").strip().lower()


def parse_name_list(raw: Any) -> List[str]:
    """
    Normalize plugin/filter arguments from list or comma-separated string.
    """
    if raw is None:
        return []
    if isinstance(raw, str):
        parts = [raw]
    elif isinstance(raw, Iterable):
        parts = [str(item) for item in raw]
    else:
        parts = [str(raw)]

    names: List[str] = []
    for part in parts:
        for token in str(part).split(","):
            name = _normalize_name(token)
            if name and name not in names:
                names.append(name)
    return names


def available_plugin_names() -> List[str]:
    return sorted(available_plugins().keys())


def available_filter_names() -> List[str]:
    return sorted(available_filters().keys())


class ExtensionPipeline:
    """
    Runs selected plugins then filters on each snapshot.
    """

    def __init__(self, plugin_names: Optional[List[str]] = None, filter_names: Optional[List[str]] = None):
        self.plugin_names = parse_name_list(plugin_names)
        self.filter_names = parse_name_list(filter_names)
        self.plugins = self._build_plugins(self.plugin_names)
        self.filters = self._build_filters(self.filter_names)
        self._plugin_state: Dict[str, Dict[str, Any]] = {}
        self._filter_state: Dict[str, Dict[str, Any]] = {}

    def _build_plugins(self, names: List[str]):
        registry = available_plugins()
        built = []
        for name in names:
            plugin_cls = registry.get(name)
            if plugin_cls is None:
                raise ValueError(f"Unknown plugin: {name}")
            built.append(plugin_cls())
        return built

    def _build_filters(self, names: List[str]):
        registry = available_filters()
        built = []
        for name in names:
            filter_cls = registry.get(name)
            if filter_cls is None:
                raise ValueError(f"Unknown filter: {name}")
            built.append(filter_cls())
        return built

    def apply(self, snapshot: Dict[str, Any]) -> Dict[str, Any]:
        for plugin in self.plugins:
            state = self._plugin_state.setdefault(plugin.name, {})
            snapshot = plugin.apply(snapshot, state)

        for snapshot_filter in self.filters:
            state = self._filter_state.setdefault(snapshot_filter.name, {})
            snapshot = snapshot_filter.apply(snapshot, state)

        return snapshot
