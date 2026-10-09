import numpy as np

class VehicleTracker:
    def __init__(self, max_missing_frames: int = 150, iou_thresh: float = 0.20):
        # 150 frames = ~5 seconds of complete loss tolerance
        self.max_missing_frames = max_missing_frames
        self.iou_thresh = iou_thresh
        self.next_track_id = 1
        self.tracks = {}

    def _compute_iou(self, boxA, boxB):
        xA = max(boxA[0], boxB[0])
        yA = max(boxA[1], boxB[1])
        xB = min(boxA[2], boxB[2])
        yB = min(boxA[3], boxB[3])

        interArea = max(0, xB - xA) * max(0, yB - yA)
        boxAArea = (boxA[2] - boxA[0]) * (boxA[3] - boxA[1])
        boxBArea = (boxB[2] - boxB[0]) * (boxB[3] - boxB[1])
        denom = float(boxAArea + boxBArea - interArea)
        return interArea / denom if denom > 0 else 0.0

    def update(self, boxes: np.ndarray, class_ids: np.ndarray):
        detections = []
        for box, cls_id in zip(boxes, class_ids):
            cx = int((box[0] + box[2]) / 2.0)
            cy = int(box[3] - 5)  # Tire contact patch
            detections.append({
                "box": box.copy(),
                "centroid": (cx, cy),
                "class_id": cls_id
            })

        unmatched_dets = list(range(len(detections)))
        matched_tracks = set()

        # 1. IoU Association
        if len(self.tracks) > 0 and len(detections) > 0:
            track_ids = list(self.tracks.keys())
            iou_mat = np.zeros((len(track_ids), len(detections)), dtype=np.float32)

            for i, tid in enumerate(track_ids):
                for j, det in enumerate(detections):
                    iou_mat[i, j] = self._compute_iou(self.tracks[tid]["box"], det["box"])

            while True:
                max_iou = np.max(iou_mat) if iou_mat.size > 0 else 0
                if max_iou < self.iou_thresh:
                    break
                row, col = np.unravel_index(np.argmax(iou_mat), iou_mat.shape)
                tid = track_ids[row]

                # Update track coordinates & history
                old_c = self.tracks[tid]["centroid"]
                new_c = detections[col]["centroid"]
                movement = np.hypot(old_c[0] - new_c[0], old_c[1] - new_c[1])

                self.tracks[tid]["box"] = detections[col]["box"]
                self.tracks[tid]["centroid"] = new_c
                self.tracks[tid]["class_id"] = detections[col]["class_id"]
                self.tracks[tid]["missing"] = 0

                # Mark as stationary if barely moving
                if movement < 8.0:
                    self.tracks[tid]["stationary_frames"] += 1
                else:
                    self.tracks[tid]["stationary_frames"] = 0

                matched_tracks.add(tid)
                if col in unmatched_dets:
                    unmatched_dets.remove(col)

                iou_mat[row, :] = -1.0
                iou_mat[:, col] = -1.0

        # 2. Euclidean Distance Match for stationary cars with noisy bounding boxes
        for tid in list(self.tracks.keys()):
            if tid not in matched_tracks and len(unmatched_dets) > 0:
                t_cx, t_cy = self.tracks[tid]["centroid"]
                best_dist = float("inf")
                best_idx = None

                for det_idx in unmatched_dets:
                    d_cx, d_cy = detections[det_idx]["centroid"]
                    dist = np.hypot(t_cx - d_cx, t_cy - d_cy)
                    if dist < 50.0 and dist < best_dist:
                        best_dist = dist
                        best_idx = det_idx

                if best_idx is not None:
                    self.tracks[tid]["box"] = detections[best_idx]["box"]
                    self.tracks[tid]["centroid"] = detections[best_idx]["centroid"]
                    self.tracks[tid]["class_id"] = detections[best_idx]["class_id"]
                    self.tracks[tid]["missing"] = 0
                    self.tracks[tid]["stationary_frames"] += 1
                    matched_tracks.add(tid)
                    unmatched_dets.remove(best_idx)

        # 3. Decay & Stopped Latch Logic
        for tid in list(self.tracks.keys()):
            if tid not in matched_tracks:
                self.tracks[tid]["missing"] += 1

                # If the vehicle was established as stationary before dropping,
                # give it a higher lifetime (up to 300 frames ~ 10 seconds)
                allowed_missing = 300 if self.tracks[tid]["stationary_frames"] > 5 else self.max_missing_frames

                if self.tracks[tid]["missing"] > allowed_missing:
                    del self.tracks[tid]

        # 4. Spawn new tracks
        for det_idx in unmatched_dets:
            det = detections[det_idx]
            self.tracks[self.next_track_id] = {
                "box": det["box"],
                "centroid": det["centroid"],
                "class_id": det["class_id"],
                "missing": 0,
                "stationary_frames": 0
            }
            self.next_track_id += 1

        # Return all active tracks
        # Stationary tracks stay visible even during temporary dropouts
        return {
            tid: data for tid, data in self.tracks.items()
            if data["missing"] < 60  # Stays actively rendered for 2s of consecutive YOLO misses
        }