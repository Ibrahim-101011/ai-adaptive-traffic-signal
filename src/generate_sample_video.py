import cv2
import numpy as np
import os

def generate(output_path="videos/sample_traffic.mp4", duration_sec=10, fps=30):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    width, height = 1280, 720
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    total_frames = duration_sec * fps
    print(f"[Video Generator] Creating synthetic traffic video ({total_frames} frames)...")

    for f in range(total_frames):
        frame = np.full((height, width, 3), 45, dtype=np.uint8)

        # Draw intersection roads (Asphalt)
        cv2.rectangle(frame, (int(width * 0.38), 0), (int(width * 0.62), height), (70, 70, 70), -1)
        cv2.rectangle(frame, (0, int(height * 0.38)), (width, int(height * 0.62)), (70, 70, 70), -1)

        # Center intersection box
        cv2.rectangle(frame, (int(width * 0.38), int(height * 0.38)), (int(width * 0.62), int(height * 0.62)), (85, 85, 85), -1)

        # Lane divider markings
        cv2.line(frame, (width // 2, 0), (width // 2, height), (220, 220, 220), 2)
        cv2.line(frame, (0, height // 2), (width, height // 2), (220, 220, 220), 2)

        # Mock vehicle 1 (Road 1 Southbound)
        y1 = int((f * 6) % (height * 0.32)) + 30
        cv2.rectangle(frame, (int(width * 0.45), y1), (int(width * 0.45) + 60, y1 + 95), (0, 180, 255), -1)
        cv2.putText(frame, "CAR", (int(width * 0.45), y1 - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

        # Mock vehicle 2 (Road 4 Eastbound)
        x2 = int((f * 5) % (width * 0.32)) + 40
        cv2.rectangle(frame, (x2, int(height * 0.48)), (x2 + 90, int(height * 0.48) + 50), (200, 50, 50), -1)
        cv2.putText(frame, "TRUCK", (x2, int(height * 0.48) - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

        cv2.putText(frame, f"TEST BENCH FRAME: {f:04d}", (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        out.write(frame)

    out.release()
    print(f"[Video Generator] Video generated successfully at: {output_path}")

if __name__ == "__main__":
    generate()