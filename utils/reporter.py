"""
NetLoader-X :: Reporter Orchestrator
-------------------------------------------------------
Responsible for creating output folders, naming attack
simulations, and dispatching metrics to CSV/JSON/HTML.

Safe, offline-only, localhost simulation.
-------------------------------------------------------
Author: voltsparx
Contact: voltsparx@gmail.com
"""

import os
import json
import csv
import time
from datetime import datetime
from typing import Dict, Any
from utils import html_report, logger

# Default output root folder
OUTPUT_ROOT = os.path.join(os.getcwd(), "outputs")


class Reporter:
    """
    Orchestrates reporting outputs for each attack simulation.
    """

    def __init__(self, attack_name: str):
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        safe_name = attack_name.replace(" ", "_").replace("/", "-")
        self.attack_name = safe_name
        self.folder = os.path.join(OUTPUT_ROOT, f"{safe_name}_{timestamp}")
        os.makedirs(self.folder, exist_ok=True)

        logger.log_info(f"[+] Created report folder: {self.folder}")

    # --------------------------------------------------
    # EXPORT INTERFACES
    # --------------------------------------------------

    def export_json(self, data: Dict[str, Any]):
        """
        Save metrics as JSON file.
        """
        try:
            path = os.path.join(self.folder, "metrics.json")
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)
            logger.log_info(f"[+] JSON report saved: {path}")
        except Exception as e:
            logger.log_error(f"[-] Failed to save JSON: {e}")

    def export_csv(self, data: Dict[str, Any]):
        """
        Save numeric time-series as CSV.
        """
        try:
            series = data.get("series", {})
            if not series:
                logger.log_info("[*] No series data to save as CSV")
                return

            path = os.path.join(self.folder, "metrics.csv")
            with open(path, "w", newline="", encoding="utf-8") as csvfile:
                writer = csv.writer(csvfile)
                # Header row
                headers = ["tick"] + list(series.keys())
                writer.writerow(headers)

                # Rows
                ticks = len(next(iter(series.values())))
                for i in range(ticks):
                    row = [i + 1]
                    for key in series.keys():
                        row.append(series[key][i])
                    writer.writerow(row)

            logger.log_info(f"[+] CSV report saved: {path}")
        except Exception as e:
            logger.log_error(f"[-] Failed to save CSV: {e}")

    def export_html(self, data: Dict[str, Any]):
        """
        Generate HTML report using html_report module.
        """
        try:
            path = os.path.join(self.folder, "metrics.html")
            html_report.generate_html_report(data, path, attack_name=self.attack_name)
            logger.log_info(f"[+] HTML report saved: {path}")
        except Exception as e:
            logger.log_error(f"[-] Failed to generate HTML: {e}")

    # --------------------------------------------------
    # UNIVERSAL EXPORT
    # --------------------------------------------------

    def export_all(self, data: Dict[str, Any]):
        """
        Export all formats: JSON, CSV, HTML.
        """
        logger.log_info("[*] Exporting all report formats...")
        self.export_json(data)
        self.export_csv(data)
        self.export_html(data)
        logger.log_info("[+] All exports completed")