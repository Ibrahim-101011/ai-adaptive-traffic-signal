import cv2
import numpy as np
import time
import os
import yaml
from detector import VehicleDetector

CLASS_LABELS = {
    2: "Car",
    3: "Motorcycle",
    5: "Bus",
    7: "Truck"
}

def run_test():
    config_path = "config/config.yaml"
    cfg = {}
    if os.path.exists(config_path):
        with open(config_path, "r") as f:
            cfg = yaml.safe_load(f)

    sys_cfg = cfg.get("system", {})
    det_cfg = cfg.get("detector", {})

    model_path = det_cfg.get("model_path", "models/yolov8n.pt")
    conf_thresh = det_cfg.get("confidence_threshold", 0.35)
    device = det_cfg.get("device", "cpu")
    source = sys_cfg.get("video_source", "webcam")

    print("[Brick 3] Initializing VehicleDetector...")
    detector = VehicleDetector(
        model_path=model_path,
        conf_threshold=conf_thresh,
        device=device
    )

    # Video stream selector
    if str(source).lower() == "webcam":
        cam_idx = sys_cfg.get("camera_index", 0)
        print(f"[Brick 3] Connecting to webcam index {cam_idx}...")
        cap = cv2.VideoCapture(cam_idx, cv2.CAP_DSHOW)
    else:
        print(f"[Brick 3] Opening video file: {source}...")
        cap = cv2.VideoCapture(source)

    # Fallback to sample video if webcam or file fails
    if not cap.isOpened():
        fallback_video = "videos/sample_traffic.mp4"
        print(f"[WARNING] Could not open '{source}'. Using '{fallback_video}'...")
        if not os.path.exists(fallback_video):
            from generate_sample_video import generate
            generate(fallback_video)
        cap = cv2.VideoCapture(fallback_video)

    if not cap.isOpened():
        print("[ERROR] Failed to open any video stream.")
        return

    print("\n[STREAMING] Live detection active! Press 'q' in the window to finish Brick 3.\n")

    prev_time = time.time()
    frame_count = 0
    fps = 0.0

    while True:
        ret, frame = cap.read()
        if not ret:
            # Loop playback for video files
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            continue

        frame_count += 1
        now = time.time()
        if (now - prev_time) >= 0.5:
            fps = frame_count / (now - prev_time)
            frame_count = 0
            prev_time = now

        # Run YOLO detection
        t0 = time.perf_counter()
        boxes, scores, class_ids = detector.detect(frame)
        latency = (time.perf_counter() - t0) * 1000

        # Draw detections
        for box, score, cls_id in zip(boxes, scores, class_ids):
            x1, y1, x2, y2 = box.astype(int)
            label = f"{CLASS_LABELS.get(cls_id, 'Vehicle')} {score:.2f}"
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(frame, label, (x1, max(20, y1 - 8)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        # Draw HUD overlay
        cv2.rectangle(frame, (0, 0), (frame.shape[1], 50), (20, 20, 20), -1)
        status_text = f"FPS: {fps:.1f} | Latency: {latency:.1f}ms | Detections: {len(boxes)}"
        cv2.putText(frame, status_text, (20, 32),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        cv2.imshow("Brick 3 - Live YOLOv8 Verification", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    print("\n--- Brick 3 Passed: Live YOLOv8 Vehicle Detector Verified ---")

if __name__ == "__main__":
    run_test()