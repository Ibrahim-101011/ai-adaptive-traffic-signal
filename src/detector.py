import os
import cv2
import numpy as np
from ultralytics import YOLO

class VehicleDetector:
    def __init__(self, model_path: str = "models/yolov8n.pt", conf_threshold: float = 0.35, target_classes: list = None, device: str = "cpu"):
        self.conf_threshold = conf_threshold
        # COCO IDs: 2=car, 3=motorcycle, 5=bus, 7=truck
        self.target_classes = target_classes or [2, 3, 5, 7]
        self.device = device
        
        # Ensure target folder exists
        os.makedirs(os.path.dirname(model_path), exist_ok=True)
        
        try:
            self.model = YOLO(model_path)
            print(f"[Detector] Loaded local weights from '{model_path}' on device '{self.device}'.")
        except Exception as e:
            print(f"[Detector] Local model not found ({e}). Downloading official yolov8n weights...")
            self.model = YOLO("yolov8n.pt")
            self.model.save(model_path)
            print(f"[Detector] Cached model weights saved to '{model_path}'.")

    def detect(self, frame: np.ndarray):
        """
        Executes inference on a single BGR frame.
        
        Returns:
            boxes: np.ndarray shape (N, 4) in [x1, y1, x2, y2] format
            scores: np.ndarray shape (N,)
            class_ids: np.ndarray shape (N,)
        """
        if frame is None or frame.size == 0:
            return np.empty((0, 4)), np.empty((0,)), np.empty((0,))

        results = self.model.predict(
            source=frame,
            conf=self.conf_threshold,
            classes=self.target_classes,
            device=self.device,
            verbose=False
        )

        if not results or len(results[0].boxes) == 0:
            return np.empty((0, 4)), np.empty((0,)), np.empty((0,))

        boxes = results[0].boxes.xyxy.cpu().numpy()
        scores = results[0].boxes.conf.cpu().numpy()
        class_ids = results[0].boxes.cls.cpu().numpy().astype(int)

        return boxes, scores, class_ids