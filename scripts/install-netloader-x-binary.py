#!/usr/bin/env python3
"""
CLI wrapper for install_netloader_x_binary module.
"""

from pathlib import Path
import sys


THIS_DIR = Path(__file__).resolve().parent
if str(THIS_DIR) not in sys.path:
    sys.path.insert(0, str(THIS_DIR))

from install_netloader_x_binary import main


if __name__ == "__main__":
    main()
