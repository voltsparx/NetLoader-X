"""
Persistent user settings for NetLoader-X.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Dict


SETTINGS_DIR = Path.home() / ".netloader-x"
SETTINGS_FILE = SETTINGS_DIR / "settings.json"
DEFAULT_OUTPUT_DIR_NAME = "netloader-x-output"
ENV_OUTPUT_DIR = "NETLOADER_X_OUTPUT_DIR"


def _ensure_settings_dir():
    SETTINGS_DIR.mkdir(parents=True, exist_ok=True)


def load_user_settings() -> Dict:
    if not SETTINGS_FILE.exists():
        return {}
    try:
        return json.loads(SETTINGS_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}


def save_user_settings(payload: Dict):
    _ensure_settings_dir()
    SETTINGS_FILE.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def default_output_dir_home() -> str:
    return str((Path.home() / DEFAULT_OUTPUT_DIR_NAME).resolve())


def get_default_output_dir() -> str:
    env_value = os.environ.get(ENV_OUTPUT_DIR, "").strip()
    if env_value:
        return str(Path(env_value).expanduser().resolve())

    settings = load_user_settings()
    saved = str(settings.get("output_dir", "")).strip()
    if saved:
        return str(Path(saved).expanduser().resolve())

    return default_output_dir_home()


def set_persistent_output_dir(path_value: str) -> str:
    target = str(Path(path_value).expanduser().resolve())
    settings = load_user_settings()
    settings["output_dir"] = target
    save_user_settings(settings)
    return target
