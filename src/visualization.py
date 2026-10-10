import cv2
import numpy as np

class HUDVisualizer:
    COLOR_BG = (25, 25, 25)
    COLOR_GREEN = (0, 220, 0)
    COLOR_YELLOW = (0, 215, 255)
    COLOR_RED = (0, 0, 240)
    COLOR_CYAN = (255, 220, 0)
    COLOR_WHITE = (255, 255, 255)

    def __init__(self):
        pass

    def draw_regions_and_counts(self, frame: np.ndarray, regions: dict, counts: dict, active_road: str, state: str):
        overlay = frame.copy()

        for road_name, poly in regions.items():
            # Determine color based on active signal state
            if road_name == active_road:
                if state == "GREEN":
                    fill_color = (0, 160, 0)
                    border_color = self.COLOR_GREEN
                elif state == "YELLOW":
                    fill_color = (0, 150, 180)
                    border_color = self.COLOR_YELLOW
                else:
                    fill_color = (0, 0, 160)
                    border_color = self.COLOR_RED
            else:
                fill_color = (40, 40, 120)
                border_color = (80, 80, 200)

            # Draw transparent region polygon
            cv2.fillPoly(overlay, [poly], fill_color)
            cv2.polylines(frame, [poly], isClosed=True, color=border_color, thickness=2)

            # Center label badge
            M = cv2.moments(poly)
            if M["m00"] != 0:
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])
                road_info = counts.get(road_name, {})
                tot = road_info.get("total", 0)
                label = f"{road_name.upper()}: {tot} veh"
                (w, h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.55, 2)
                cv2.rectangle(frame, (cx - w // 2 - 6, cy - h - 6), (cx + w // 2 + 6, cy + 6), self.COLOR_BG, -1)
                cv2.putText(frame, label, (cx - w // 2, cy), cv2.FONT_HERSHEY_SIMPLEX, 0.55, self.COLOR_WHITE, 2)

        cv2.addWeighted(overlay, 0.25, frame, 0.75, 0, frame)

    def draw_tracks(self, frame: np.ndarray, tracks: dict):
        for tid, tdata in tracks.items():
            box = tdata["box"].astype(int)
            centroid = tdata["centroid"]

            # Draw bounding box and wheel contact point
            cv2.rectangle(frame, (box[0], box[1]), (box[2], box[3]), self.COLOR_CYAN, 2)
            cv2.circle(frame, centroid, 4, self.COLOR_RED, -1)

            # Track ID tag
            tag = f"ID:{tid}"
            cv2.putText(frame, tag, (box[0], max(18, box[1] - 6)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.45, self.COLOR_CYAN, 2)

    def draw_hud(self, frame: np.ndarray, status: dict, fps: float, latency: float, density_scores: dict):
        h, w = frame.shape[:2]

        # Top Information Banner
        cv2.rectangle(frame, (0, 0), (w, 55), self.COLOR_BG, -1)
        cv2.line(frame, (0, 55), (w, 55), (60, 60, 60), 1)

        mode_str = f"MODE: {status.get('mode', 'ADAPTIVE')}"
        state_str = f"SIGNAL: {status.get('state', 'GREEN')}"
        road_str = f"ACTIVE: {status.get('active_road', 'ROAD1').upper()}"
        timer_str = f"TIMER: {status.get('remaining_seconds', 0)}s"

        state = status.get("state", "GREEN")
        state_color = self.COLOR_GREEN if state == "GREEN" else (self.COLOR_YELLOW if state == "YELLOW" else self.COLOR_RED)

        cv2.putText(frame, mode_str, (20, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (200, 200, 200), 2)
        cv2.putText(frame, road_str, (20, 46), cv2.FONT_HERSHEY_SIMPLEX, 0.55, self.COLOR_WHITE, 2)

        cv2.putText(frame, state_str, (220, 36), cv2.FONT_HERSHEY_SIMPLEX, 0.7, state_color, 2)
        cv2.putText(frame, timer_str, (420, 36), cv2.FONT_HERSHEY_SIMPLEX, 0.7, self.COLOR_YELLOW, 2)

        perf_str = f"FPS: {fps:.1f} | YOLO: {latency:.1f}ms"
        cv2.putText(frame, perf_str, (w - 240, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 255, 0), 2)

        # Bottom Quick Telemetry Summary
        cv2.rectangle(frame, (0, h - 35), (w, h), self.COLOR_BG, -1)
        summary = " | ".join([f"{r.upper()}: {density_scores.get(r, 0.0):.1f} PCU" for r in ["road1", "road2", "road3", "road4"]])
        cv2.putText(frame, f"QUEUE DENSITY: {summary}", (20, h - 12),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (180, 180, 180), 1)