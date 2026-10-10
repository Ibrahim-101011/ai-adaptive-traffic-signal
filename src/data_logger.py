import os
import csv
import time

class TelemetryLogger:
    def __init__(self, output_path: str = "data/processed/traffic_telemetry.csv", log_interval: float = 1.0):
        self.output_path = output_path
        self.log_interval = log_interval
        self.last_log_time = 0.0

        os.makedirs(os.path.dirname(self.output_path), exist_ok=True)
        self._init_csv()

    def _init_csv(self):
        if not os.path.exists(self.output_path):
            with open(self.output_path, mode="w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow([
                    "timestamp",
                    "mode",
                    "active_road",
                    "state",
                    "remaining_seconds",
                    "r1_count", "r1_pcu",
                    "r2_count", "r2_pcu",
                    "r3_count", "r3_pcu",
                    "r4_count", "r4_pcu"
                ])

    def log(self, status: dict, road_counts: dict, density_scores: dict, force: bool = False):
        now = time.time()
        if not force and (now - self.last_log_time) < self.log_interval:
            return

        self.last_log_time = now

        row = [
            time.strftime("%Y-%m-%d %H:%M:%S"),
            status.get("mode", "ADAPTIVE"),
            status.get("active_road", "road1"),
            status.get("state", "GREEN"),
            status.get("remaining_seconds", 0),
            road_counts.get("road1", {}).get("total", 0), round(density_scores.get("road1", 0.0), 2),
            road_counts.get("road2", {}).get("total", 0), round(density_scores.get("road2", 0.0), 2),
            road_counts.get("road3", {}).get("total", 0), round(density_scores.get("road3", 0.0), 2),
            road_counts.get("road4", {}).get("total", 0), round(density_scores.get("road4", 0.0), 2)
        ]

        with open(self.output_path, mode="a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(row)