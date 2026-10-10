import os
import sys
import time
import yaml
import cv2
import numpy as np

from detector import VehicleDetector
from tracker import VehicleTracker
from road_regions import RoadRegionManager
from counter import VehicleCounter
from density import TrafficDensityEstimator
from emergency import EmergencyManager
from signal_controller import AdaptiveSignalController
from communication import SerialInterface
from visualization import HUDVisualizer
from data_logger import TelemetryLogger

def load_config(config_path: str = "config/config.yaml") -> dict:
    if not os.path.exists(config_path):
        print(f"[ERROR] Config file not found at: {config_path}")
        sys.exit(1)
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def get_signal_token(active_road: str, state: str) -> str:
    """Maps FSM state to framed ESP32 command tokens."""
    if state == "ALL_RED":
        return "ALL_RED"
    
    # Extract road index: road1 -> 1
    idx = active_road.replace("road", "")
    aspect = "G" if state == "GREEN" else "Y"
    return f"R{idx}_{aspect}"

def main():
    cfg = load_config()

    sys_cfg = cfg.get("system", {})
    det_cfg = cfg.get("detector", {})
    density_cfg = cfg.get("density_thresholds", {})
    ser_cfg = cfg.get("serial", {})
    log_cfg = cfg.get("logging", {})

    # 1. Initialize Ingestion
    source = sys_cfg.get("video_source", "webcam")
    if str(source).lower() == "webcam":
        cam_idx = sys_cfg.get("camera_index", 0)
        print(f"[Main] Opening Webcam index {cam_idx}...")
        cap = cv2.VideoCapture(cam_idx, cv2.CAP_DSHOW)
    else:
        print(f"[Main] Opening Video file: {source}...")
        cap = cv2.VideoCapture(source)

    if not cap.isOpened():
        print(f"[ERROR] Could not open video source: {source}")
        sys.exit(1)

    frame_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)) or 1280
    frame_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)) or 720
    frame_skip = max(1, sys_cfg.get("frame_skip", 1))

    # 2. Initialize Pipeline Modules
    print("[Main] Initializing pipeline components...")
    detector = VehicleDetector(
        model_path=det_cfg.get("model_path", "models/yolov8n.pt"),
        conf_threshold=det_cfg.get("confidence_threshold", 0.20),
        target_classes=det_cfg.get("target_classes", [2, 3, 5, 7]),
        device=det_cfg.get("device", "cpu")
    )
    tracker = VehicleTracker()
    region_mgr = RoadRegionManager(cfg.get("regions", {}), frame_w, frame_h)
    counter = VehicleCounter()
    density_estimator = TrafficDensityEstimator(
        low_max=density_cfg.get("low_max", 3),
        medium_max=density_cfg.get("medium_max", 8)
    )
    emergency_mgr = EmergencyManager(
        default_duration=cfg.get("signal_timing", {}).get("emergency_duration", 15)
    )
    controller = AdaptiveSignalController(cfg)
    serial_comm = SerialInterface(
        port=ser_cfg.get("port", "COM3"),
        baud_rate=ser_cfg.get("baud_rate", 115200),
        enabled=ser_cfg.get("enabled", False)
    )
    visualizer = HUDVisualizer()
    logger = TelemetryLogger(
        output_path=log_cfg.get("output_csv", "data/processed/traffic_telemetry.csv"),
        log_interval=log_cfg.get("log_interval_seconds", 1.0)
    )

    print("\n--- SYSTEM CONTROLS ---")
    print(" [1-4] : Trigger Emergency Preemption on Road 1, 2, 3, or 4")
    print(" [C]   : Clear / Cancel Active Emergency")
    print(" [M]   : Toggle Mode (ADAPTIVE <-> FIXED)")
    print(" [Q]   : Graceful Shutdown\n")

    prev_time = time.time()
    frame_idx = 0
    fps = 0.0
    latency = 0.0
    last_sent_token = ""
    boxes, scores, class_ids = np.empty((0, 4)), np.empty((0,)), np.empty((0,))

    try:
        while True:
            loop_start = time.time()
            ret, frame = cap.read()
            if not ret:
                # Video file loopback
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                continue

            frame_idx += 1
            h, w = frame.shape[:2]
            if (w != frame_w or h != frame_h) and (w > 0 and h > 0):
                frame_w, frame_h = w, h
                region_mgr.update_regions(cfg.get("regions", {}), frame_w, frame_h)

            # 3. Detection (with frame skip optimization)
            if frame_idx % frame_skip == 0:
                det_start = time.perf_counter()
                boxes, scores, class_ids = detector.detect(frame)
                latency = (time.perf_counter() - det_start) * 1000.0

            # 4. Tracking & Spatial Counts
            tracks = tracker.update(boxes, class_ids)
            road_counts = counter.process_tracks(tracks, region_mgr)

            # 5. Density Scoring (PCE calculation)
            density_scores = {
                r: density_estimator.compute_priority_score(road_counts[r])
                for r in ["road1", "road2", "road3", "road4"]
            }

            # 6. Step FSM Timing & State
            dt = loop_start - prev_time
            prev_time = loop_start
            emergency_mgr.step(dt)
            status = controller.step(dt, density_scores, emergency_mgr)

            # 7. Hardware UART Synchronization
            current_token = get_signal_token(status["active_road"], status["state"])
            if current_token != last_sent_token:
                serial_comm.send_command(current_token)
                last_sent_token = current_token

            # 8. Telemetry Logging
            logger.log(status, road_counts, density_scores)

            # 9. FPS Calculation
            fps = 1.0 / max(dt, 0.001)

            # 10. HUD Visualization
            visualizer.draw_regions_and_counts(
                frame, region_mgr.regions, road_counts, status["active_road"], status["state"]
            )
            visualizer.draw_tracks(frame, tracks)
            visualizer.draw_hud(frame, status, fps, latency, density_scores)

            cv2.imshow("AI-Adaptive Traffic Signal Pipeline", frame)

            # Keyboard Events
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                print("[Main] Shutdown requested by user.")
                break
            elif key in [ord('1'), ord('2'), ord('3'), ord('4')]:
                target = f"road{chr(key)}"
                emergency_mgr.trigger_emergency(target)
            elif key == ord('c'):
                emergency_mgr.clear_emergency()
            elif key == ord('m'):
                new_mode = "FIXED" if controller.mode == "ADAPTIVE" else "ADAPTIVE"
                controller.set_mode(new_mode)
                print(f"[Main] Control Mode switched to: {new_mode}")

    finally:
        cap.release()
        cv2.destroyAllWindows()
        serial_comm.close()
        print("[Main] Cleanup complete. Pipeline terminated safely.")

if __name__ == "__main__":
    main()