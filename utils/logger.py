"""
NetLoader-X Logger
"""

import logging
from pathlib import Path
from core.config import GlobalConfig


def get_logger(run_name: str):
    log_dir = GlobalConfig.OUTPUT_DIR / run_name
    log_dir.mkdir(parents=True, exist_ok=True)

    log_file = log_dir / "run.log"

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