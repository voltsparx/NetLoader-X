"""
NetLoader-X logging helpers.
"""

import logging
import os
from datetime import datetime

import core.config as cfg

_VERBOSE = False


def set_verbose(enabled: bool):
    global _VERBOSE
    _VERBOSE = bool(enabled)


def _emit(level: str, message: str):
    prefix = datetime.utcnow().strftime("%H:%M:%S")
    print(f"[{prefix}] {level}: {message}")


def log_info(message: str):
    _emit("INFO", message)


def log_warning(message: str):
    _emit("WARN", message)


def log_error(message: str):
    _emit("ERROR", message)


def log_debug(message: str):
    if _VERBOSE:
        _emit("DEBUG", message)


def get_logger(run_name: str):
    """
    File + console logger for integration compatibility.
    """
    log_dir = os.path.join(cfg.BASE_OUTPUT_DIR, run_name)
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, "run.log")

    logger = logging.getLogger(run_name)
    logger.setLevel(logging.DEBUG)

    if not logger.handlers:
        formatter = logging.Formatter("[%(asctime)s] %(levelname)s: %(message)s")
        fh = logging.FileHandler(log_file)
        ch = logging.StreamHandler()
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)
        logger.addHandler(fh)
        logger.addHandler(ch)

    return logger


def log_event(event_type: str, data: dict = None):
    if data is None:
        data = {}
    log_info(f"{event_type}: {data}")
