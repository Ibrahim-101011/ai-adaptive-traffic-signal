from typing import Dict, Any

class AdaptiveSignalController:
    def __init__(self, min_green: int = 5, max_green: int = 20, fixed_green: int = 10, yellow_dur: float = 2.0, red_dur: float = 1.0):
        self.min_green = min_green
        self.max_green = max_green
        self.fixed_green = fixed_green
        self.yellow_duration = yellow_dur
        self.all_red_duration = red_dur
        self.starvation_threshold = 3

        self.roads = ["road1", "road2", "road3", "road4"]
        self.active_road = "road1"
        self.current_state = "ALL_RED"
        self.mode = "ADAPTIVE"

        self.elapsed_time = 0.0
        self.allocated_green = self.min_green
        self.starvation_counters = {r: 0 for r in self.roads}

    def set_mode(self, mode: str):
        self.mode = mode
        if mode == "FIXED":
            self.allocated_green = float(self.fixed_green)

    def _calc_green(self, pcu: float) -> float:
        if pcu <= 0:
            return float(self.min_green)
        scaled = self.min_green + (pcu * 2.0)
        return float(min(self.max_green, max(self.min_green, scaled)))

    def step(self, dt: float, density_scores: Dict[str, float], emergency_mgr: Any) -> Dict[str, Any]:
        self.elapsed_time += dt

        # 1. Emergency Preemption Override
        if emergency_mgr and getattr(emergency_mgr, "is_emergency", False):
            self.mode = "EMERGENCY"
            target = emergency_mgr.emergency_road or "road1"
            rem = max(0, int(round(emergency_mgr.active_time_remaining)))

            if self.active_road != target or self.current_state != "GREEN":
                self.active_road = target
                self.current_state = "GREEN"
                self.elapsed_time = 0.0
                self.allocated_green = float(rem or 10.0)

            return {
                "active_road": self.active_road,
                "state": self.current_state,
                "remaining_seconds": rem,
                "mode": self.mode
            }

        # Return from emergency state
        if self.mode == "EMERGENCY":
            self.mode = "ADAPTIVE"
            self.current_state = "YELLOW"
            self.elapsed_time = 0.0

        current_pcu = density_scores.get(self.active_road, 0.0)
        total_pcu = sum(density_scores.values())

        # 2. State Machine Transitions
        if self.current_state == "GREEN":
            if self.mode == "FIXED":
                # In FIXED mode: Run the entire timer regardless of queue emptiness
                if self.elapsed_time >= self.allocated_green:
                    self.current_state = "YELLOW"
                    self.elapsed_time = 0.0
            else:
                # In ADAPTIVE mode: Cut off early if empty, or timeout expires
                if current_pcu <= 0.0 or self.elapsed_time >= self.allocated_green:
                    self.current_state = "YELLOW"
                    self.elapsed_time = 0.0

        elif self.current_state == "YELLOW":
            if self.elapsed_time >= self.yellow_duration:
                self.current_state = "ALL_RED"
                self.elapsed_time = 0.0

        elif self.current_state == "ALL_RED":
            if self.mode == "FIXED":
                # Deterministic sequential round-robin: 1 -> 2 -> 3 -> 4 -> 1
                if self.elapsed_time >= self.all_red_duration:
                    curr_idx = self.roads.index(self.active_road)
                    self.active_road = self.roads[(curr_idx + 1) % len(self.roads)]
                    self.current_state = "GREEN"
                    self.elapsed_time = 0.0
                    self.allocated_green = float(self.fixed_green)
            else:
                # ADAPTIVE mode: rest-in-red if all approaches empty
                if total_pcu <= 0.0:
                    self.elapsed_time = 0.0
                    return {
                        "active_road": self.active_road,
                        "state": "ALL_RED",
                        "remaining_seconds": 0,
                        "mode": self.mode
                    }

                # Starvation prioritization followed by max PCU selection
                chosen_road = None
                for r in self.roads:
                    if self.starvation_counters[r] >= self.starvation_threshold and density_scores.get(r, 0.0) > 0:
                        chosen_road = r
                        break

                if not chosen_road:
                    chosen_road = max(self.roads, key=lambda r: density_scores.get(r, 0.0))

                if density_scores.get(chosen_road, 0.0) > 0.0 and self.elapsed_time >= self.all_red_duration:
                    self.active_road = chosen_road
                    self.current_state = "GREEN"
                    self.elapsed_time = 0.0
                    for r in self.roads:
                        if r == self.active_road:
                            self.starvation_counters[r] = 0
                        elif density_scores.get(r, 0.0) > 0:
                            self.starvation_counters[r] += 1
                    self.allocated_green = self._calc_green(density_scores.get(self.active_road, 0.0))

        # 3. Calculate Display Countdown
        if self.current_state == "GREEN":
            rem = max(0, int(round(self.allocated_green - self.elapsed_time)))
        elif self.current_state == "YELLOW":
            rem = max(0, int(round(self.yellow_duration - self.elapsed_time)))
        else:
            rem = 0

        return {
            "active_road": self.active_road,
            "state": self.current_state,
            "remaining_seconds": rem,
            "mode": self.mode
        }