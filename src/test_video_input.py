import cv2
import yaml
import time
import os
import sys

def test_stream():
    config_path = "config/config.yaml"
    if not os.path.exists(config_path):
        print(f"[FAIL] Missing config file: {config_path}")
        sys.exit(1)

    with open(config_path, "r") as f:
        cfg = yaml.safe_load(f)

    source = cfg.get("system", {}).get("video_source", "webcam")

    if str(source).lower() == "webcam":
        cam_idx = cfg.get("system", {}).get("camera_index", 0)
        print(f"[Brick 2] Connecting to Webcam index: {cam_idx}...")
        cap = cv2.VideoCapture(cam_idx, cv2.CAP_DSHOW)
    else:
        print(f"[Brick 2] Opening Video file: {source}...")
        cap = cv2.VideoCapture(source)

    # Fallback to sample video if webcam fails to open
    if not cap.isOpened():
        print(f"[WARNING] Could not open '{source}'. Falling back to 'videos/sample_traffic.mp4'...")
        fallback_path = "videos/sample_traffic.mp4"
        if not os.path.exists(fallback_path):
            from generate_sample_video import generate
            generate()
        cap = cv2.VideoCapture(fallback_path)

    if not cap.isOpened():
        print("[CRITICAL] Unable to open any video capture stream.")
        sys.exit(1)

    print("[SUCCESS] Video stream active! Press 'q' inside the OpenCV window to exit.")

    prev_time = time.time()
    frames = 0
    fps = 0.0

    while True:
        ret, frame = cap.read()
        if not ret:
            # Loop playback for video files
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            continue

        frames += 1
        now = time.time()
        if (now - prev_time) >= 1.0:
            fps = frames / (now - prev_time)
            frames = 0
            prev_time = now

        cv2.putText(frame, f"Brick 2 Video Test | FPS: {fps:.1f}", (30, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        cv2.imshow("Brick 2 Verification Window", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    print("--- Brick 2 Passed: Video Ingestion Engine Verified ---")

if __name__ == "__main__":
    test_stream()