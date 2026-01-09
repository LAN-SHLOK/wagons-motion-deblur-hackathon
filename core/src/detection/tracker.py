"""
DeepSORT Tracker for Wagon ID Tracking
"""
import numpy as np
from scipy.spatial.distance import cdist
from filterpy.kalman import KalmanFilter

class KalmanBoxTracker:
    def __init__(self, bbox):
        self.kf = KalmanFilter(dim_x=7, dim_z=4)
        self.kf.F = np.array([[1,0,0,0,1,0,0],
                             [0,1,0,0,0,1,0],
                             [0,0,1,0,0,0,1],
                             [0,0,0,1,0,0,0],
                             [0,0,0,0,1,0,0],
                             [0,0,0,0,0,1,0],
                             [0,0,0,0,0,0,1]])
        self.kf.H = np.array([[1,0,0,0,0,0,0],
                             [0,1,0,0,0,0,0],
                             [0,0,1,0,0,0,0],
                             [0,0,0,1,0,0,0]])
        self.kf.R *= 10.
        self.kf.P *= 1000.
        self.kf.x[:4] = bbox
        self.time_since_update = 0
        self.id = KalmanBoxTracker.count
        KalmanBoxTracker.count += 1
        self.history = []
    
    def update(self, bbox):
        self.time_since_update = 0
        self.history = []
        self.kf.update(bbox)
    
    def predict(self):
        if self.kf.x is None:
            return None
        self.time_since_update += 1
        self.history.append(self.kf.x)
        self.kf.predict()
        return self.kf.x[:4]

KalmanBoxTracker.count = 0

class DeepSORTTracker:
    def __init__(self):
        self.trackers = []
        self.next_id = 1
    
    def update(self, detections):
        # Simple IOU + distance matching
        matched = []
        for det in detections:
            best_iou = 0
            best_tracker = None
            for tracker in self.trackers:
                pred_bbox = tracker.predict()
                if pred_bbox is None:
                    continue
                iou = self._iou(det['bbox'], pred_bbox)
                if iou > best_iou:
                    best_iou = iou
                    best_tracker = tracker
            
            if best_tracker and best_iou > 0.3:
                best_tracker.update(det['bbox'])
                matched.append((best_tracker, det))
            else:
                # New track
                tracker = KalmanBoxTracker(det['bbox'])
                tracker.id = self.next_id
                self.next_id += 1
                self.trackers.append(tracker)
        
        # Remove lost tracks
        self.trackers = [t for t in self.trackers if t.time_since_update < 10]
        return self.trackers
