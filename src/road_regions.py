import cv2
import numpy as np

class RoadRegionManager:
    def __init__(self, region_configs: dict, frame_width: int, frame_height: int):
        self.frame_width = frame_width
        self.frame_height = frame_height
        self.regions = {}
        self.update_regions(region_configs, frame_width, frame_height)

    def update_regions(self, region_configs: dict, frame_width: int, frame_height: int):
        self.frame_width = frame_width
        self.frame_height = frame_height
        self.regions = {}

        for road_key, points in region_configs.items():
            pixel_points = np.array([
                [int(pt[0] * self.frame_width), int(pt[1] * self.frame_height)]
                for pt in points
            ], dtype=np.int32)
            self.regions[road_key] = pixel_points

    def assign_road(self, centroid: tuple):
        for road_name, polygon in self.regions.items():
            if cv2.pointPolygonTest(polygon, (float(centroid[0]), float(centroid[1])), measureDist=False) >= 0:
                return road_name
        return None