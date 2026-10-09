import cv2
import yaml
import numpy as np
import os
import sys

CONFIG_PATH = "config/config.yaml"

def calibrate():
    if not os.path.exists(CONFIG_PATH):
        print(f"[ERROR] Cannot find {CONFIG_PATH}")
        sys.exit(1)

    with open(CONFIG_PATH, "r") as f:
        cfg = yaml.safe_load(f)

    source = cfg.get("system", {}).get("video_source", "webcam")
    if str(source).lower() == "webcam":
        cap = cv2.VideoCapture(cfg.get("system", {}).get("camera_index", 0), cv2.CAP_DSHOW)
    else:
        cap = cv2.VideoCapture(source)

    ret, frame = cap.read()
    cap.release()
    if not ret or frame is None:
        print(f"[ERROR] Could not grab frame from {source}")
        sys.exit(1)

    h, w = frame.shape[:2]
    roads = ["road1", "road2", "road3", "road4"]
    current_road_idx = 0
    points_dict = {r: [] for r in roads}

    clone = frame.copy()

    def mouse_callback(event, x, y, flags, param):
        nonlocal clone, frame
        if event == cv2.EVENT_LBUTTONDOWN:
            r_name = roads[current_road_idx]
            if len(points_dict[r_name]) < 4:
                # Store normalized coordinates
                norm_x = round(x / w, 3)
                norm_y = round(y / h, 3)
                points_dict[r_name].append([norm_x, norm_y])

    cv2.namedWindow("ROI Calibrator")
    cv2.setMouseCallback("ROI Calibrator", mouse_callback)

    print("\n--- ROI CALIBRATION INSTRUCTIONS ---")
    print("Click 4 corners for each road approach in order: road1 -> road2 -> road3 -> road4.")
    print("Press [N] to move to the next road once 4 points are set.")
    print("Press [R] to reset current road points.")
    print("Press [S] to save calibrated ROIs directly to config.yaml.")
    print("Press [Q] to quit without saving.\n")

    colors = {
        "road1": (0, 255, 0),
        "road2": (255, 255, 0),
        "road3": (0, 165, 255),
        "road4": (255, 0, 255)
    }

    while True:
        display = frame.copy()
        current_road = roads[current_road_idx]

        # Draw already defined roads
        for r_name, pts in points_dict.items():
            if len(pts) > 0:
                pixel_pts = np.array([[int(p[0]*w), int(p[1]*h)] for p in pts], np.int32)
                for pt in pixel_pts:
                    cv2.circle(display, tuple(pt), 5, colors[r_name], -1)
                if len(pts) == 4:
                    cv2.polylines(display, [pixel_pts], isClosed=True, color=colors[r_name], thickness=2)
                    M = cv2.moments(pixel_pts)
                    if M["m00"] != 0:
                        cx = int(M["m10"] / M["m00"])
                        cy = int(M["m01"] / M["m00"])
                        cv2.putText(display, r_name.upper(), (cx - 30, cy),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, colors[r_name], 2)

        # Draw guidance banner
        cv2.rectangle(display, (0, 0), (w, 40), (25, 25, 25), -1)
        status_msg = f"Configuring {current_road.upper()} ({len(points_dict[current_road])}/4 points). Press 'N' next, 'S' save, 'R' reset."
        cv2.putText(display, status_msg, (20, 26), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)

        cv2.imshow("ROI Calibrator", display)
        key = cv2.waitKey(20) & 0xFF

        if key == ord('q'):
            break
        elif key == ord('r'):
            points_dict[current_road] = []
        elif key == ord('n'):
            if len(points_dict[current_road]) == 4:
                current_road_idx = min(len(roads) - 1, current_road_idx + 1)
            else:
                print(f"[WARN] Select all 4 points for {current_road} first.")
        elif key == ord('s'):
            all_valid = all(len(points_dict[r]) == 4 for r in roads)
            if not all_valid:
                print("[ERROR] Complete 4 points for all four roads before saving.")
                continue

            cfg["regions"] = points_dict
            with open(CONFIG_PATH, "w") as f:
                yaml.dump(cfg, f, default_flow_style=None, sort_keys=False)
            print("[SUCCESS] New road boundaries saved into config/config.yaml!")
            break

    cv2.destroyAllWindows()

if __name__ == "__main__":
    calibrate()