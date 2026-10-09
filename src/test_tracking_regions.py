import cv2
import yaml
import time
import os
import sys

from detector import VehicleDetector
from tracker import VehicleTracker
from road_regions import RoadRegionManager
from counter import VehicleCounter

def run_test():
    with open("config/config.yaml", "r") as f:
        cfg = yaml.safe_load(f)

    sys_cfg = cfg.get("system", {})
    source = sys_cfg.get("video_source", "webcam")

    if str(source).lower() == "webcam":
        cap = cv2.VideoCapture(sys_cfg.get("camera_index", 0), cv2.CAP_DSHOW)
    else:
        cap = cv2.VideoCapture(source)

    if not cap.isOpened():
        print(f"[ERROR] Could not open video source: {source}")
        sys.exit(1)

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)) or 1280
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)) or 720

    detector = VehicleDetector(conf_threshold=0.3)
    tracker = VehicleTracker()
    region_mgr = RoadRegionManager(cfg.get("regions", {}), width, height)
    counter = VehicleCounter()

    print("[Brick 4] Running Tracking & Spatial Assignment Test. Press 'q' to exit.")

    while True:
        ret, frame = cap.read()
        if not ret:
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            continue

        h, w = frame.shape[:2]
        if w != width or h != height:
            width, height = w, h
            region_mgr.update_regions(cfg.get("regions", {}), width, height)

        # 1. Detection
        boxes, scores, class_ids = detector.detect(frame)

        # 2. Tracking
        tracks = tracker.update(boxes, class_ids)

        # 3. Spatial Counting
        road_counts = counter.process_tracks(tracks, region_mgr)

        # 4. Draw Polygons & Count Badges
        overlay = frame.copy()
        for r_name, poly in region_mgr.regions.items():
            cv2.fillPoly(overlay, [poly], (50, 50, 150))
            cv2.polylines(frame, [poly], isClosed=True, color=(0, 255, 255), thickness=2)
            M = cv2.moments(poly)
            if M["m00"] != 0:
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])
                cnt = road_counts[r_name]["total"]
                cv2.putText(frame, f"{r_name.upper()}: {cnt}", (cx - 40, cy),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

        cv2.addWeighted(overlay, 0.25, frame, 0.75, 0, frame)

        # Draw Tracks
        for tid, t_data in tracks.items():
            bx = t_data["box"].astype(int)
            cv2.rectangle(frame, (bx[0], bx[1]), (bx[2], bx[3]), (0, 255, 0), 2)
            cv2.circle(frame, t_data["centroid"], 4, (0, 0, 255), -1)
            cv2.putText(frame, f"ID: {tid}", (bx[0], bx[1] - 8),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        cv2.imshow("Brick 4: Tracking & Spatial ROIs", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    print("--- Brick 4 Passed: Tracking & Spatial Regions Verified ---")

if __name__ == "__main__":
    run_test()