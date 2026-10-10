class TrafficDensityEstimator:
    def compute_priority_score(self, vehicle_breakdown: dict) -> float:
        cars = vehicle_breakdown.get("cars", 0)
        motorcycles = vehicle_breakdown.get("motorcycles", 0)
        buses = vehicle_breakdown.get("buses", 0)
        trucks = vehicle_breakdown.get("trucks", 0)

        score = (motorcycles * 0.5) + (cars * 1.0) + (buses * 2.5) + (trucks * 2.5)
        return float(score)