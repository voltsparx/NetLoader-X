"""
NetLoader-X Logger
"""

import logging
from pathlib import Path
import os


def get_logger(run_name: str):
    log_dir = os.path.join("outputs", run_name)
    os.makedirs(log_dir, exist_ok=True)

    log_file = os.path.join(log_dir, "run.log")

    logger = logging.getLogger(run_name)
    logger.setLevel(logging.DEBUG)

    if not logger.handlers:
        fh = logging.FileHandler(log_file)
        ch = logging.StreamHandler()

        formatter = logging.Formatter(
            "[%(asctime)s] %(levelname)s: %(message)s"
        )

        fh.setFormatter(formatter)
        ch.setFormatter(formatter)

        logger.addHandler(fh)
        logger.addHandler(ch)

    return logger


def log_event(event_type: str, data: dict = None):
    """Log event for debugging/auditing purposes"""
    if data is None:
        data = {}
    print(f"[*] {event_type}: {data}")