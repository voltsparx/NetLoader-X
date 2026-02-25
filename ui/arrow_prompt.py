"""
Arrow-key terminal prompts for safe interactive configuration.
"""

from __future__ import annotations

import os
import sys
from typing import Dict, List, Optional

from ui.theme import colorize


def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


def supports_arrow_ui() -> bool:
    return bool(sys.stdin.isatty() and sys.stdout.isatty())


def _read_key_windows() -> str:
    import msvcrt

    key = msvcrt.getwch()
    if key in ("\x00", "\xe0"):
        key2 = msvcrt.getwch()
        mapping = {
            "H": "UP",
            "P": "DOWN",
            "K": "LEFT",
            "M": "RIGHT",
            "I": "PAGEUP",
            "Q": "PAGEDOWN",
        }
        return mapping.get(key2, "")
    if key in ("\r", "\n"):
        return "ENTER"
    if key == " ":
        return "SPACE"
    if key == "\x1b":
        return "ESC"
    if key.lower() == "a":
        return "A"
    if key.lower() == "d":
        return "D"
    if key.lower() == "n":
        return "N"
    if key.lower() == "q":
        return "Q"
    return ""


def _read_key_unix() -> str:
    import termios
    import tty

    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        ch1 = sys.stdin.read(1)
        if ch1 in ("\r", "\n"):
            return "ENTER"
        if ch1 == " ":
            return "SPACE"
        if ch1 == "\x1b":
            ch2 = sys.stdin.read(1)
            if ch2 != "[":
                return "ESC"
            ch3 = sys.stdin.read(1)
            mapping = {
                "A": "UP",
                "B": "DOWN",
                "C": "RIGHT",
                "D": "LEFT",
                "5": "PAGEUP",
                "6": "PAGEDOWN",
            }
            if ch3 in ("5", "6"):
                _ = sys.stdin.read(1)  # trailing "~"
            return mapping.get(ch3, "")
        if ch1.lower() == "a":
            return "A"
        if ch1.lower() == "d":
            return "D"
        if ch1.lower() == "n":
            return "N"
        if ch1.lower() == "q":
            return "Q"
        return ""
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)


def read_key() -> str:
    if os.name == "nt":
        return _read_key_windows()
    return _read_key_unix()


def select_single(title: str, options: List[Dict[str, str]], default_index: int = 0) -> str:
    """
    options item: {"label": str, "value": str, "hint": str}
    """
    if not supports_arrow_ui():
        for idx, item in enumerate(options, start=1):
            print(colorize(f"[{idx}] {item['label']}", "info"))
        while True:
            raw = input(colorize("Select option > ", "prompt")).strip()
            try:
                val = int(raw)
                if 1 <= val <= len(options):
                    return options[val - 1]["value"]
            except ValueError:
                pass
            print(colorize("Invalid selection.", "error"))

    idx = max(0, min(default_index, len(options) - 1))
    while True:
        clear_screen()
        print(colorize(title, "primary"))
        print(colorize("Use Up/Down + Enter", "muted"))
        print("")

        for row, item in enumerate(options):
            cursor = ">" if row == idx else " "
            print(colorize(f"{cursor} {item['label']}", "info"))
            if row == idx and item.get("hint"):
                print(colorize(f"    {item['hint']}", "muted"))

        key = read_key()
        if key == "UP":
            idx = (idx - 1) % len(options)
        elif key == "DOWN":
            idx = (idx + 1) % len(options)
        elif key == "ENTER":
            return options[idx]["value"]
        elif key in ("Q", "ESC"):
            return options[-1]["value"]


def select_multiple(
    title: str,
    options: List[Dict[str, str]],
    initial_selected: Optional[List[str]] = None,
) -> List[str]:
    """
    Multi-select prompt.
    Space toggles an item, Enter confirms.
    A selects all, N clears all.
    """
    selected = set(initial_selected or [])
    if not supports_arrow_ui():
        print(colorize(title, "primary"))
        print(colorize("Comma separate names or type 'none':", "muted"))
        print(colorize(", ".join(item["value"] for item in options), "info"))
        raw = input(colorize("Selection > ", "prompt")).strip().lower()
        if raw in ("", "none", "no"):
            return []
        picks = [s.strip() for s in raw.split(",") if s.strip()]
        valid = {item["value"] for item in options}
        return [name for name in picks if name in valid]

    idx = 0
    valid_values = [item["value"] for item in options]
    while True:
        clear_screen()
        print(colorize(title, "primary"))
        print(colorize("Up/Down move, Space toggle, A all, N none, Enter confirm", "muted"))
        print("")
        for row, item in enumerate(options):
            cursor = ">" if row == idx else " "
            check = "[x]" if item["value"] in selected else "[ ]"
            print(colorize(f"{cursor} {check} {item['label']} ({item['value']})", "info"))
            if row == idx and item.get("hint"):
                print(colorize(f"    {item['hint']}", "muted"))

        key = read_key()
        if key == "UP":
            idx = (idx - 1) % len(options)
        elif key == "DOWN":
            idx = (idx + 1) % len(options)
        elif key == "SPACE":
            value = options[idx]["value"]
            if value in selected:
                selected.remove(value)
            else:
                selected.add(value)
        elif key == "A":
            selected = set(valid_values)
        elif key == "N":
            selected = set()
        elif key == "ENTER":
            return [name for name in valid_values if name in selected]
        elif key in ("Q", "ESC"):
            return [name for name in valid_values if name in selected]


def edit_numeric_config(
    title: str,
    values: Dict[str, float],
    schema: List[Dict[str, object]],
) -> Dict[str, float]:
    """
    Arrow-key numeric editor.
    Left/Right changes by step, PageUp/PageDown changes by 10x step.
    """
    if not supports_arrow_ui():
        updated = dict(values)
        for field in schema:
            key = field["key"]
            label = field["label"]
            low = field["min"]
            high = field["max"]
            prompt = f"{label} ({low}-{high}) [{updated[key]}] > "
            raw = input(colorize(prompt, "prompt")).strip()
            if raw:
                try:
                    val = float(raw)
                    updated[key] = _clamp(val, low, high, field.get("precision"))
                except ValueError:
                    pass
        return updated

    idx = 0
    edited = dict(values)
    while True:
        clear_screen()
        print(colorize(title, "primary"))
        print(colorize("Up/Down select field. Left/Right adjust. Enter saves.", "muted"))
        print("")

        for row, field in enumerate(schema):
            key = field["key"]
            low = field["min"]
            high = field["max"]
            marker = ">" if row == idx else " "
            value = edited.get(key)
            if field.get("precision") is not None:
                shown = f"{float(value):.{int(field['precision'])}f}"
            else:
                shown = f"{int(value)}"
            print(colorize(f"{marker} {field['label']:<18} {shown:<8} [{low}..{high}]", "info"))
            if row == idx and field.get("hint"):
                print(colorize(f"    {field['hint']}", "muted"))

        key_name = read_key()
        if key_name == "UP":
            idx = (idx - 1) % len(schema)
        elif key_name == "DOWN":
            idx = (idx + 1) % len(schema)
        elif key_name in ("LEFT", "RIGHT", "PAGEUP", "PAGEDOWN"):
            field = schema[idx]
            step = float(field.get("step", 1))
            if key_name == "PAGEUP":
                step *= 10
            elif key_name == "PAGEDOWN":
                step *= -10
            elif key_name == "LEFT":
                step *= -1

            key = field["key"]
            low = float(field["min"])
            high = float(field["max"])
            precision = field.get("precision")
            edited[key] = _clamp(float(edited.get(key, low)) + step, low, high, precision)
        elif key_name == "ENTER":
            return edited
        elif key_name in ("ESC", "Q"):
            return values


def _clamp(value: float, low: float, high: float, precision=None):
    bounded = max(low, min(high, value))
    if precision is None:
        return int(round(bounded))
    return round(float(bounded), int(precision))
