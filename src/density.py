class TrafficDensityEstimator:
    def __init__(self, low_max: int = 3, medium_max: int = 8):
        self.low_max = low_max
        self.medium_max = medium_max

    def estimate_density(self, count: int) -> str:
        """Classifies raw vehicle count into density tiers."""
        if count <= self.low_max:
            return "LOW"
        elif count <= self.medium_max:
            return "MEDIUM"
        else:
            return "HIGH"

    def compute_priority_score(self, vehicle_breakdown: dict) -> float:
        """
        Calculates Passenger Car Equivalent (PCE/PCU) weighted score:
        - Motorcycle: 0.5
        - Car: 1.0
        - Bus: 2.5
        - Truck: 2.5
        """
        cars = vehicle_breakdown.get("cars", 0)
        motorcycles = vehicle_breakdown.get("motorcycles", 0)
        buses = vehicle_breakdown.get("buses", 0)
        trucks = vehicle_breakdown.get("trucks", 0)

        score = (motorcycles * 0.5) + (cars * 1.0) + (buses * 2.5) + (trucks * 2.5)
        return float(score)