import cv2
import numpy as np
import time
import os
import yaml
from visualization import HUDVisualizer
from data_logger import TelemetryLogger

def run_test():
    with open("config/config.yaml", "r") as f:
        cfg = yaml.safe_load(f)

    w, h = 1280, 720
    test_frame = np.full((h, w, 3), 40, dtype=np.uint8)

    # Convert normalized config regions to absolute pixels
    regions = {}
    for r_name, pts in cfg.get("regions", {}).items():
        regions[r_name] = np.array([[int(p[0]*w), int(p[1]*h)] for p in pts], np.int32)

    visualizer = HUDVisualizer()
    logger = TelemetryLogger(output_path="data/processed/traffic_telemetry.csv", log_interval=0.5)

    mock_status = {
        "mode": "ADAPTIVE",
        "active_road": "road1",
        "state": "GREEN",
        "remaining_seconds": 18
    }

    mock_counts = {
        "road1": {"total": 4, "cars": 3, "motorcycles": 2, "buses": 0, "trucks": 0},
        "road2": {"total": 2, "cars": 2, "motorcycles": 0, "buses": 0, "trucks": 0},
        "road3": {"total": 7, "cars": 4, "motorcycles": 2, "buses": 1, "trucks": 0},
        "road4": {"total": 1, "cars": 1, "motorcycles": 0, "buses": 0, "trucks": 0}
    }

    mock_scores = {"road1": 4.0, "road2": 2.0, "road3": 7.5, "road4": 1.0}

    mock_tracks = {
        101: {"box": np.array([450, 200, 510, 280]), "centroid": (480, 275)},
        102: {"box": np.array([750, 420, 810, 500]), "centroid": (780, 495)}
    }

    # Render overlays
    visualizer.draw_regions_and_counts(test_frame, regions, mock_counts, "road1", "GREEN")
    visualizer.draw_tracks(test_frame, mock_tracks)
    visualizer.draw_hud(test_frame, mock_status, fps=30.0, latency=28.4, density_scores=mock_scores)

    # Log 3 telemetry snapshots
    for _ in range(3):
        logger.log(mock_status, mock_counts, mock_scores, force=True)
        time.sleep(0.05)

    print(f"[Brick 7] Telemetry successfully recorded in: {logger.output_path}")
    print("[Brick 7] Displaying HUD verification frame. Press any key to finish.")

    cv2.imshow("Brick 7 - HUD Overlay & Logger Verification", test_frame)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    print("--- Brick 7 Passed: HUD and Logger Engine Verified ---")

if __name__ == "__main__":
    run_test()