class EmergencyManager:
    def __init__(self, default_duration: int = 15):
        self.is_emergency = False
        self.emergency_road = None
        self.default_duration = default_duration
        self.active_time_remaining = 0.0

    def trigger_emergency(self, road_id: str, duration: int = None):
        """Preempts signal sequence to clear an emergency approach."""
        self.is_emergency = True
        self.emergency_road = road_id
        self.active_time_remaining = float(duration or self.default_duration)
        print(f"\n[EMERGENCY OVERRIDE] Priority clearance active on {self.emergency_road.upper()} for {self.active_time_remaining}s")

    def clear_emergency(self):
        """Manually releases emergency preemption."""
        self.is_emergency = False
        self.emergency_road = None
        self.active_time_remaining = 0.0
        print("\n[EMERGENCY OVERRIDE] Preemption released. Resuming normal adaptive scheduling.")

    def step(self, dt: float):
        """Advances active emergency countdown."""
        if self.is_emergency:
            self.active_time_remaining -= dt
            if self.active_time_remaining <= 0:
                print(f"\n[EMERGENCY OVERRIDE] Window expired on {self.emergency_road.upper()}. Resuming normal schedule.")
                self.is_emergency = False
                self.emergency_road = None
                self.active_time_remaining = 0.0