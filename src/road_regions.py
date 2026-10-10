import cv2
import numpy as np

class RoadRegionManager:
    def __init__(self, regions_dict: dict, frame_w: int = 800, frame_h: int = 800):
        self.frame_w = frame_w
        self.frame_h = frame_h
        self.regions = {}

        for name, pts in regions_dict.items():
            pts_array = np.array(pts, dtype=np.float32)
            if np.max(pts_array) <= 1.0:
                pts_array[:, 0] *= frame_w
                pts_array[:, 1] *= frame_h
            self.regions[name] = pts_array.astype(np.int32)

    def assign_road(self, centroid: tuple):
        if centroid is None:
            return None
        pt = (float(centroid[0]), float(centroid[1]))
        for road_name, poly in self.regions.items():
            if cv2.pointPolygonTest(poly, pt, False) >= 0:
                return road_name
        return None