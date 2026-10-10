class EmergencyManager:
    def __init__(self, default_duration: int = 12):
        self.is_emergency = False
        self.emergency_road = None
        self.default_duration = default_duration
        self.active_time_remaining = 0.0

    def trigger_emergency(self, road_id: str, duration: int = None):
        self.is_emergency = True
        self.emergency_road = road_id
        self.active_time_remaining = float(duration or self.default_duration)
        print(f"\n[EMERGENCY] Override active on {self.emergency_road.upper()} for {self.active_time_remaining}s")

    def clear_emergency(self):
        self.is_emergency = False
        self.emergency_road = None
        self.active_time_remaining = 0.0
        print("\n[EMERGENCY] Override released. Resuming adaptive schedule.")

    def step(self, dt: float):
        if self.is_emergency:
            self.active_time_remaining -= dt
            if self.active_time_remaining <= 0:
                self.is_emergency = False
                self.emergency_road = None
                self.active_time_remaining = 0.0