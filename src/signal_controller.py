class AdaptiveSignalController:
    STATE_GREEN = "GREEN"
    STATE_YELLOW = "YELLOW"
    STATE_ALL_RED = "ALL_RED"

    def __init__(self, config: dict):
        timing = config.get("signal_timing", {})
        self.min_green = timing.get("min_green", 10)
        self.max_green = timing.get("max_green", 45)
        self.yellow_duration = timing.get("yellow_duration", 3)
        self.all_red_duration = timing.get("all_red_duration", 2)
        self.starvation_threshold = timing.get("starvation_threshold", 3)
        self.fixed_time_duration = timing.get("fixed_time_duration", 20)

        self.mode = "ADAPTIVE"
        self.active_road = "road1"
        self.current_state = self.STATE_GREEN
        self.allocated_duration = float(self.min_green)
        self.elapsed_in_state = 0.0

        # Anti-starvation cycle counter
        self.cycles_starved = {"road1": 0, "road2": 0, "road3": 0, "road4": 0}

    def set_mode(self, mode: str):
        if mode in ["ADAPTIVE", "FIXED"]:
            self.mode = mode

    def calculate_green_time(self, priority_score: float) -> int:
        """Dynamically scales green duration linearly between min_green and max_green."""
        if priority_score <= 2.0:
            return self.min_green
        # Normalizes score between 2.0 and 20.0 to map across green window
        normalized = min(1.0, (priority_score - 2.0) / 18.0)
        calculated = self.min_green + (self.max_green - self.min_green) * normalized
        return int(round(calculated))

    def select_next_road(self, density_scores: dict) -> str:
        """Selects highest weighted road, accounting for cumulative starvation penalties."""
        weighted_scores = {}
        for road, score in density_scores.items():
            if road == self.active_road:
                # Active road cannot immediately repeat if others are waiting
                weighted_scores[road] = -1.0
            else:
                penalty = 1.0 + (self.cycles_starved[road] * 0.75)
                weighted_scores[road] = score * penalty

        # If all approaches are empty, round-robin to the next sequential road
        if max(weighted_scores.values()) <= 0:
            order = ["road1", "road2", "road3", "road4"]
            current_idx = order.index(self.active_road)
            return order[(current_idx + 1) % 4]

        return max(weighted_scores, key=weighted_scores.get)

    def step(self, dt: float, density_scores: dict, emergency_manager) -> dict:
        self.elapsed_in_state += dt

        # --- Emergency Mode Preemption ---
        if emergency_manager.is_emergency:
            target_road = emergency_manager.emergency_road
            if self.active_road != target_road:
                # Safely clear the current green road before switching
                if self.current_state == self.STATE_GREEN:
                    self.current_state = self.STATE_YELLOW
                    self.allocated_duration = float(self.yellow_duration)
                    self.elapsed_in_state = 0.0
                elif self.current_state == self.STATE_YELLOW and self.elapsed_in_state >= self.allocated_duration:
                    self.current_state = self.STATE_ALL_RED
                    self.allocated_duration = float(self.all_red_duration)
                    self.elapsed_in_state = 0.0
                elif self.current_state == self.STATE_ALL_RED and self.elapsed_in_state >= self.allocated_duration:
                    self.active_road = target_road
                    self.current_state = self.STATE_GREEN
                    self.allocated_duration = emergency_manager.active_time_remaining
                    self.elapsed_in_state = 0.0
            else:
                # Keep active road on green for the duration of the emergency
                self.current_state = self.STATE_GREEN
                self.allocated_duration = emergency_manager.active_time_remaining
            return self._build_status(emergency_manager.is_emergency)

        # --- Standard FSM Phase Transitions ---
        if self.elapsed_in_state >= self.allocated_duration:
            if self.current_state == self.STATE_GREEN:
                self.current_state = self.STATE_YELLOW
                self.allocated_duration = float(self.yellow_duration)
                self.elapsed_in_state = 0.0

            elif self.current_state == self.STATE_YELLOW:
                self.current_state = self.STATE_ALL_RED
                self.allocated_duration = float(self.all_red_duration)
                self.elapsed_in_state = 0.0

            elif self.current_state == self.STATE_ALL_RED:
                if self.mode == "FIXED":
                    order = ["road1", "road2", "road3", "road4"]
                    next_road = order[(order.index(self.active_road) + 1) % 4]
                    green_time = self.fixed_time_duration
                else:
                    next_road = self.select_next_road(density_scores)
                    green_time = self.calculate_green_time(density_scores.get(next_road, 0.0))

                # Update starvation counters
                for r in self.cycles_starved:
                    if r == next_road:
                        self.cycles_starved[r] = 0
                    else:
                        self.cycles_starved[r] += 1

                self.active_road = next_road
                self.current_state = self.STATE_GREEN
                self.allocated_duration = float(green_time)
                self.elapsed_in_state = 0.0

        return self._build_status(emergency_manager.is_emergency)

    def _build_status(self, is_emergency: bool) -> dict:
        remaining = max(0, int(round(self.allocated_duration - self.elapsed_in_state)))
        return {
            "mode": "EMERGENCY" if is_emergency else self.mode,
            "active_road": self.active_road,
            "state": self.current_state,
            "remaining_seconds": remaining,
            "allocated_duration": self.allocated_duration
        }