import cv2
import numpy as np
import random
import time

class SimVehicle:
    def __init__(self, road: str, v_type: str, v_id: int):
        self.id = v_id
        self.road = road
        self.v_type = v_type

        # Dimensions & Top Speeds
        if v_type == "motorcycle":
            self.width, self.length = 12, 26
            self.max_speed = 7.5
        elif v_type in ["bus", "truck"]:
            self.width, self.length = 28, 62
            self.max_speed = 4.8
        else:  # car
            self.width, self.length = 22, 38
            self.max_speed = 6.4

        self.speed = self.max_speed

        palette = {
            "car": random.choice([
                (45, 45, 210), (210, 140, 30), (230, 230, 230),
                (40, 160, 220), (60, 60, 60)
            ]),
            "motorcycle": (30, 180, 240),
            "bus": (35, 170, 70),
            "truck": (160, 70, 140)
        }
        self.body_color = palette.get(v_type, (180, 180, 180))

        if road == "road1":
            self.x, self.y = 377.0, -80.0
            self.angle = 90
        elif road == "road2":
            self.x, self.y = 880.0, 377.0
            self.angle = 180
        elif road == "road3":
            self.x, self.y = 423.0, 880.0
            self.angle = 270
        elif road == "road4":
            self.x, self.y = -80.0, 423.0
            self.angle = 0

    def get_bbox(self):
        hw, hl = self.width / 2.0, self.length / 2.0
        if self.road in ["road1", "road3"]:
            return [self.x - hw, self.y - hl, self.x + hw, self.y + hl]
        else:
            return [self.x - hl, self.y - hw, self.x + hl, self.y + hw]

    def update(self, lead_vehicle, signal_state: str, stop_line: float):
        target_speed = self.max_speed

        # Precise distance from front bumper to the white stop line
        if self.road == "road1":
            dist_to_stop = stop_line - (self.y + self.length / 2)
        elif self.road == "road2":
            dist_to_stop = (self.x - self.length / 2) - stop_line
        elif self.road == "road3":
            dist_to_stop = (self.y - self.length / 2) - stop_line
        elif self.road == "road4":
            dist_to_stop = stop_line - (self.x + self.length / 2)

        # Stop crisp right at the white bar (within 4-8px) on RED/YELLOW
        if signal_state in ["RED", "ALL_RED"]:
            if 0 < dist_to_stop <= 65:
                # Smooth progressive braking right up to the paint
                target_speed = max(0.0, (dist_to_stop - 6.0) / 10.0)
                if dist_to_stop <= 8.0:
                    target_speed = 0.0
        elif signal_state == "YELLOW":
            if 0 < dist_to_stop <= 45:
                target_speed = max(0.0, (dist_to_stop - 6.0) / 8.0)
                if dist_to_stop <= 8.0:
                    target_speed = 0.0

        # Car-following logic in queue
        if lead_vehicle:
            lead_bbox = lead_vehicle.get_bbox()
            if self.road == "road1":
                gap = lead_bbox[1] - (self.y + self.length / 2)
            elif self.road == "road2":
                gap = (self.x - self.length / 2) - lead_bbox[2]
            elif self.road == "road3":
                gap = (self.y - self.length / 2) - lead_bbox[3]
            elif self.road == "road4":
                gap = lead_bbox[0] - (self.x + self.length / 2)

            if gap < 28:
                if lead_vehicle.speed < 0.2:
                    target_speed = 0.0
                else:
                    target_speed = min(target_speed, max(lead_vehicle.speed, 3.5))

        # Snappy response
        rate = 0.50 if target_speed > self.speed else 0.38
        self.speed += (target_speed - self.speed) * rate

        # Prevent backward creeping
        if self.speed < 0.05:
            self.speed = 0.0

        if self.road == "road1": self.y += self.speed
        elif self.road == "road2": self.x -= self.speed
        elif self.road == "road3": self.y -= self.speed
        elif self.road == "road4": self.x += self.speed
        
    def draw(self, canvas: np.ndarray):
        pad = 20
        sw = int(self.length + pad * 2)
        sh = int(self.width + pad * 2)
        sprite = np.zeros((sh, sw, 4), dtype=np.uint8)

        cx, cy = sw // 2, sh // 2
        hl, hw = int(self.length // 2), int(self.width // 2)

        # Tires
        tire_color = (20, 20, 20, 255)
        tw, th = max(3, int(self.length * 0.18)), max(2, int(self.width * 0.18))
        if self.v_type != "motorcycle":
            cv2.rectangle(sprite, (cx + hl - tw - 2, cy - hw - 1), (cx + hl - 2, cy - hw + th), tire_color, -1)
            cv2.rectangle(sprite, (cx + hl - tw - 2, cy + hw - th), (cx + hl - 2, cy + hw + 1), tire_color, -1)
            cv2.rectangle(sprite, (cx - hl + 2, cy - hw - 1), (cx - hl + tw + 2, cy - hw + th), tire_color, -1)
            cv2.rectangle(sprite, (cx - hl + 2, cy + hw - th), (cx - hl + tw + 2, cy + hw + 1), tire_color, -1)

        b_color = (*self.body_color, 255)
        outline_color = (20, 20, 20, 255)
        glass_color = (40, 40, 40, 255)

        if self.v_type == "motorcycle":
            cv2.ellipse(sprite, (cx, cy), (hl, hw), 0, 0, 360, b_color, -1)
            cv2.ellipse(sprite, (cx, cy), (hl, hw), 0, 0, 360, outline_color, 1)
            cv2.line(sprite, (cx + 4, cy - 6), (cx + 4, cy + 6), (20, 20, 20, 255), 2)
            cv2.circle(sprite, (cx - 2, cy), 4, (240, 240, 240, 255), -1)
            cv2.circle(sprite, (cx + hl, cy), 2, (180, 255, 255, 255), -1)
            cv2.circle(sprite, (cx - hl, cy), 2, (0, 0, 255, 255), -1)

        elif self.v_type in ["bus", "truck"]:
            cv2.rectangle(sprite, (cx - hl, cy - hw), (cx + hl, cy + hw), b_color, -1)
            cv2.rectangle(sprite, (cx - hl, cy - hw), (cx + hl, cy + hw), outline_color, 1)
            if self.v_type == "truck":
                cab = cx + hl - 16
                cv2.line(sprite, (cab, cy - hw), (cab, cy + hw), outline_color, 1)
                cv2.rectangle(sprite, (cx + hl - 8, cy - hw + 2), (cx + hl - 4, cy + hw - 2), glass_color, -1)
            else:
                cv2.rectangle(sprite, (cx + hl - 6, cy - hw + 2), (cx + hl - 2, cy + hw - 2), glass_color, -1)
            cv2.rectangle(sprite, (cx + hl - 1, cy - hw + 1), (cx + hl + 1, cy - hw + 4), (180, 255, 255, 255), -1)
            cv2.rectangle(sprite, (cx + hl - 1, cy + hw - 4), (cx + hl + 1, cy + hw - 1), (180, 255, 255, 255), -1)
            cv2.rectangle(sprite, (cx - hl - 1, cy - hw + 1), (cx - hl + 1, cy - hw + 4), (0, 0, 255, 255), -1)
            cv2.rectangle(sprite, (cx - hl - 1, cy + hw - 4), (cx - hl + 1, cy + hw - 1), (0, 0, 255, 255), -1)

        else: # Car
            cv2.rectangle(sprite, (cx - hl + 3, cy - hw), (cx + hl - 3, cy + hw), b_color, -1)
            cv2.ellipse(sprite, (cx + hl - 3, cy), (3, hw), 0, -90, 90, b_color, -1)
            cv2.ellipse(sprite, (cx - hl + 3, cy), (3, hw), 0, 90, 270, b_color, -1)
            cv2.rectangle(sprite, (cx - hl + 3, cy - hw), (cx + hl - 3, cy + hw), outline_color, 1)

            pts_f = np.array([[cx + 3, cy - hw + 2], [cx + 8, cy - hw + 3], [cx + 8, cy + hw - 3], [cx + 3, cy + hw - 2]], np.int32)
            cv2.fillPoly(sprite, [pts_f], glass_color)
            pts_b = np.array([[cx - 7, cy - hw + 3], [cx - 4, cy - hw + 2], [cx - 4, cy + hw - 2], [cx - 7, cy + hw - 3]], np.int32)
            cv2.fillPoly(sprite, [pts_b], glass_color)

            cv2.rectangle(sprite, (cx - 4, cy - hw + 3), (cx + 3, cy + hw - 3), b_color, -1)
            cv2.circle(sprite, (cx + hl, cy - hw + 3), 2, (180, 255, 255, 255), -1)
            cv2.circle(sprite, (cx + hl, cy + hw - 3), 2, (180, 255, 255, 255), -1)
            cv2.rectangle(sprite, (cx - hl - 1, cy - hw + 2), (cx - hl + 1, cy - hw + 4), (0, 0, 255, 255), -1)
            cv2.rectangle(sprite, (cx - hl - 1, cy + hw - 4), (cx - hl + 1, cy + hw - 2), (0, 0, 255, 255), -1)

        # Rotate sprite
        M = cv2.getRotationMatrix2D((cx, cy), -self.angle, 1.0)
        rotated = cv2.warpAffine(sprite, M, (sw, sh), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0, 0))

        # --- FAST VECTORIZED NUMPY BLIT (NO PYTHON LOOPS) ---
        x1, y1 = int(round(self.x - cx)), int(round(self.y - cy))
        x2, y2 = x1 + sw, y1 + sh

        # Intersection bounds with canvas
        can_h, can_w = canvas.shape[:2]
        cx1, cy1 = max(0, x1), max(0, y1)
        cx2, cy2 = min(can_w, x2), min(can_h, y2)

        if cx1 < cx2 and cy1 < cy2:
            sx1, sy1 = cx1 - x1, cy1 - y1
            sx2, sy2 = sx1 + (cx2 - cx1), sy1 + (cy2 - cy1)

            sprite_crop = rotated[sy1:sy2, sx1:sx2]
            alpha = (sprite_crop[:, :, 3] / 255.0)[:, :, None]
            canvas[cy1:cy2, cx1:cx2] = ((1.0 - alpha) * canvas[cy1:cy2, cx1:cx2] + alpha * sprite_crop[:, :, :3]).astype(np.uint8)


class SimulationStream:
    def __init__(self, width: int = 800, height: int = 800):
        self.w, self.h = width, height
        self.vehicles = []
        self.next_id = 1
        self.active_road = "road1"
        self.signal_state = "ALL_RED"
        self.last_spawn = {f"road{i}": time.time() for i in range(1, 5)}
        self.spawn_intervals = {f"road{i}": random.uniform(2.5, 4.5) for i in range(1, 5)}

        self.stop_lines = {
            "road1": self.h // 2 - 53,
            "road2": self.w // 2 + 53,
            "road3": self.h // 2 + 53,
            "road4": self.w // 2 - 53
        }

        self.signal_positions = {
            "road1": (330, self.stop_lines["road1"] - 30),
            "road2": (self.stop_lines["road2"] + 20, 320),
            "road3": (465, self.stop_lines["road3"] + 10),
            "road4": (self.stop_lines["road4"] - 40, 460)
        }

    def set_signal_state(self, active_road: str, state: str):
        self.active_road = active_road
        self.signal_state = state

    def _draw_traffic_light(self, canvas: np.ndarray, x: int, y: int, state: str):
        box_w, box_h = 18, 44
        cv2.rectangle(canvas, (x, y), (x + box_w, y + box_h), (20, 20, 20), -1)
        cv2.rectangle(canvas, (x, y), (x + box_w, y + box_h), (80, 80, 80), 1)

        r_c = (x + box_w // 2, y + 8)
        y_c = (x + box_w // 2, y + 22)
        g_c = (x + box_w // 2, y + 36)

        dark_r, dark_y, dark_g = (0, 0, 50), (0, 50, 50), (0, 40, 0)

        if state == "GREEN":
            cv2.circle(canvas, g_c, 6, (0, 160, 0), -1)
            r_col, y_col, g_col = dark_r, dark_y, (0, 255, 0)
        elif state == "YELLOW":
            cv2.circle(canvas, y_c, 6, (0, 160, 200), -1)
            r_col, y_col, g_col = dark_r, (0, 220, 255), dark_g
        else:
            cv2.circle(canvas, r_c, 6, (0, 0, 180), -1)
            r_col, y_col, g_col = (0, 0, 255), dark_y, dark_g

        cv2.circle(canvas, r_c, 4, r_col, -1)
        cv2.circle(canvas, y_c, 4, y_col, -1)
        cv2.circle(canvas, g_c, 4, g_col, -1)

    def _spawn_vehicles(self):
        now = time.time()
        v_types = ["car", "car", "car", "motorcycle", "bus", "truck"]
        for r in ["road1", "road2", "road3", "road4"]:
            if now - self.last_spawn[r] >= self.spawn_intervals[r]:
                self.vehicles.append(SimVehicle(r, random.choice(v_types), self.next_id))
                self.next_id += 1
                self.last_spawn[r] = now
                self.spawn_intervals[r] = random.uniform(2.5, 4.5)

    def read(self):
        self._spawn_vehicles()
        frame = np.full((self.h, self.w, 3), 42, dtype=np.uint8)

        # Asphalt Cross
        cv2.rectangle(frame, (self.w // 2 - 45, 0), (self.w // 2 + 45, self.h), (55, 55, 55), -1)
        cv2.rectangle(frame, (0, self.h // 2 - 45), (self.w, self.h // 2 + 45), (55, 55, 55), -1)
        cv2.rectangle(frame, (self.w // 2 - 45, self.h // 2 - 45), (self.w // 2 + 45, self.h // 2 + 45), (70, 70, 70), -1)

        # Dashed dividers
        for y in range(0, self.h, 28):
            if abs(y - self.h // 2) > 50:
                cv2.line(frame, (self.w // 2, y), (self.w // 2, min(self.h, y + 16)), (210, 210, 210), 1)
        for x in range(0, self.w, 28):
            if abs(x - self.w // 2) > 50:
                cv2.line(frame, (x, self.h // 2), (min(self.w, x + 16), self.h // 2), (210, 210, 210), 1)

        # Stop lines
        cv2.line(frame, (355, self.stop_lines["road1"]), (400, self.stop_lines["road1"]), (250, 250, 250), 3)
        cv2.line(frame, (self.stop_lines["road2"], 355), (self.stop_lines["road2"], 400), (250, 250, 250), 3)
        cv2.line(frame, (400, self.stop_lines["road3"]), (445, self.stop_lines["road3"]), (250, 250, 250), 3)
        cv2.line(frame, (self.stop_lines["road4"], 400), (self.stop_lines["road4"], 445), (250, 250, 250), 3)

        # Signals
        for r_name, (lx, ly) in self.signal_positions.items():
            r_state = self.signal_state if self.active_road == r_name else "RED"
            self._draw_traffic_light(frame, lx, ly, r_state)

        # Update & Draw
        remaining = []
        for r in ["road1", "road2", "road3", "road4"]:
            road_vehs = [v for v in self.vehicles if v.road == r]
            if r == "road1": road_vehs.sort(key=lambda v: v.y, reverse=True)
            elif r == "road2": road_vehs.sort(key=lambda v: v.x)
            elif r == "road3": road_vehs.sort(key=lambda v: v.y)
            elif r == "road4": road_vehs.sort(key=lambda v: v.x, reverse=True)

            eff_state = self.signal_state if self.active_road == r else "RED"

            for i, v in enumerate(road_vehs):
                lead = road_vehs[i - 1] if i > 0 else None
                v.update(lead, eff_state, self.stop_lines[r])

                if -100 <= v.x <= self.w + 100 and -100 <= v.y <= self.h + 100:
                    remaining.append(v)
                    v.draw(frame)

        self.vehicles = remaining
        return True, frame

    def get_ground_truth_detections(self):
        tracks = {}
        for v in self.vehicles:
            bbox = v.get_bbox()
            cx, cy = (bbox[0] + bbox[2]) / 2.0, (bbox[1] + bbox[3]) / 2.0
            cls_id = 3 if v.v_type == "motorcycle" else (5 if v.v_type == "bus" else (7 if v.v_type == "truck" else 2))
            tracks[v.id] = {
                "bbox": bbox,
                "centroid": (cx, cy),
                "class_id": cls_id
            }
        return tracks

    def release(self):
        pass