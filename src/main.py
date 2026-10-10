import os
import sys
import time
import csv
import cv2

SRC_DIR = os.path.dirname(os.path.abspath(__file__))
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from sim_feed import SimulationStream
from road_regions import RoadRegionManager
from counter import VehicleCounter
from density import TrafficDensityEstimator
from signal_controller import AdaptiveSignalController
from emergency import EmergencyManager

CSV_PATH = "data/processed/traffic_telemetry.csv"

def init_csv():
    os.makedirs(os.path.dirname(CSV_PATH), exist_ok=True)
    with open(CSV_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "timestamp", "mode", "active_road", "state", "remaining_seconds",
            "r1_count", "r1_pcu", "r2_count", "r2_pcu",
            "r3_count", "r3_pcu", "r4_count", "r4_pcu"
        ])

def log_telemetry(status, road_counts, density_scores):
    row = [
        time.strftime("%Y-%m-%d %H:%M:%S"),
        status.get("mode", "ADAPTIVE"),
        status.get("active_road", "road1"),
        status.get("state", "ALL_RED"),
        status.get("remaining_seconds", 0),
        road_counts.get("road1", {}).get("total", 0), round(density_scores.get("road1", 0.0), 2),
        road_counts.get("road2", {}).get("total", 0), round(density_scores.get("road2", 0.0), 2),
        road_counts.get("road3", {}).get("total", 0), round(density_scores.get("road3", 0.0), 2),
        road_counts.get("road4", {}).get("total", 0), round(density_scores.get("road4", 0.0), 2)
    ]
    with open(CSV_PATH, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(row)
        f.flush()

def main():
    print("[Main] Launching AI-Adaptive Signal Digital Twin...")
    init_csv()

    # Approach detection zones mapped to 800x800 layout
    regions_cfg = {
        "road1": [[355, 0],   [400, 0],   [400, 347], [355, 347]],
        "road2": [[453, 355], [800, 355], [800, 400], [453, 400]],
        "road3": [[400, 453], [445, 453], [445, 800], [400, 800]],
        "road4": [[0, 400],   [347, 400], [347, 445], [0, 445]],
    }

    cap = SimulationStream(800, 800)
    region_mgr = RoadRegionManager(regions_cfg, 800, 800)
    counter = VehicleCounter()
    density_estimator = TrafficDensityEstimator()
    controller = AdaptiveSignalController()
    emergency_mgr = EmergencyManager(default_duration=12)

    prev_time = time.time()
    last_log_time = 0.0

    cv2.namedWindow("AI-Adaptive Traffic Signal Pipeline", cv2.WINDOW_AUTOSIZE)

    while True:
        curr_time = time.time()
        dt = max(curr_time - prev_time, 0.001)
        prev_time = curr_time

        ret, frame = cap.read()
        if not ret:
            break

        # 1. Ground-Truth Tracking & Counting
        tracks = cap.get_ground_truth_detections()
        road_counts = counter.process_tracks(tracks, region_mgr)
        density_scores = {r: density_estimator.compute_priority_score(road_counts[r]) for r in regions_cfg}

        # 2. Advance Signal FSM
        emergency_mgr.step(dt)
        status = controller.step(dt, density_scores, emergency_mgr)

        # 3. Synchronize with Simulation
        cap.set_signal_state(status["active_road"], status["state"])

        # 4. Telemetry Logging (1 Hz)
        if curr_time - last_log_time >= 1.0:
            log_telemetry(status, road_counts, density_scores)
            last_log_time = curr_time

        # 5. Render HUD Overlay
        hud_frame = frame.copy()

        # Outline Approach Zones
        for r_name, poly in region_mgr.regions.items():
            is_active = (r_name == status["active_road"] and status["state"] == "GREEN")
            color = (0, 255, 0) if is_active else (0, 220, 220)
            cv2.polylines(hud_frame, [poly], True, color, 2)

        # Top Diagnostic Banner
        cv2.rectangle(hud_frame, (0, 0), (800, 65), (25, 25, 25), -1)
        st_color = (0, 230, 0) if status["state"] == "GREEN" else ((0, 215, 255) if status["state"] == "YELLOW" else (0, 0, 230))
        cv2.putText(hud_frame, f"MODE: {status['mode']}", (15, 26), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (220, 220, 220), 2)
        cv2.putText(hud_frame, f"ACTIVE: {status['active_road'].upper()} ({status['state']})", (15, 52), cv2.FONT_HERSHEY_SIMPLEX, 0.55, st_color, 2)
        cv2.putText(hud_frame, f"TIMER: {status['remaining_seconds']}s", (340, 42), cv2.FONT_HERSHEY_SIMPLEX, 0.85, (0, 240, 255), 2)

        # Approach Counts & PCU Metrics
        y_pos = 18
        for r in ["road1", "road2", "road3", "road4"]:
            cnt = road_counts[r]["total"]
            pcu = density_scores[r]
            cv2.putText(hud_frame, f"{r.upper()}: cnt={cnt} | pcu={pcu:.1f}", (580, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (220, 220, 220), 1)
            y_pos += 14

        cv2.imshow("AI-Adaptive Traffic Signal Pipeline", hud_frame)

        # 6. Controls
        key = cv2.waitKey(1) & 0xFF
        if key in [27, ord('q')]:
            break
        elif key in [ord('1'), ord('2'), ord('3'), ord('4')]:
            emergency_mgr.trigger_emergency(f"road{chr(key)}")
        elif key == ord('c'):
            emergency_mgr.clear_emergency()
        elif key == ord('m'):
            controller.set_mode("FIXED" if controller.mode == "ADAPTIVE" else "ADAPTIVE")

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()