class VehicleCounter:
    CLASS_MAP = {
        2: "cars",
        3: "motorcycles",
        5: "buses",
        7: "trucks"
    }

    def __init__(self):
        self.reset()

    def reset(self):
        self.road_counts = {
            "road1": {"total": 0, "cars": 0, "motorcycles": 0, "buses": 0, "trucks": 0},
            "road2": {"total": 0, "cars": 0, "motorcycles": 0, "buses": 0, "trucks": 0},
            "road3": {"total": 0, "cars": 0, "motorcycles": 0, "buses": 0, "trucks": 0},
            "road4": {"total": 0, "cars": 0, "motorcycles": 0, "buses": 0, "trucks": 0}
        }

    def process_tracks(self, tracks: dict, region_manager):
        self.reset()
        for track_id, track_data in tracks.items():
            centroid = track_data["centroid"]
            cls_id = track_data["class_id"]
            road_id = region_manager.assign_road(centroid)

            if road_id in self.road_counts:
                self.road_counts[road_id]["total"] += 1
                type_name = self.CLASS_MAP.get(cls_id, "cars")
                self.road_counts[road_id][type_name] += 1

        return self.road_counts