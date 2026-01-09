"""
YOLOv8 Wagon Detection
"""
from ultralytics import YOLO
import cv2
import numpy as np
from pathlib import Path

class WagonDetector:
    def __init__(self, model_path='core/models/yolo_wagon.pt'):
        self.model = YOLO(model_path)
        self.model.to('cuda' if torch.cuda.is_available() else 'cpu')
    
    def detect_wagons(self, frame):
        results = self.model(frame, verbose=False)
        detections = []
        
        for r in results:
            boxes = r.boxes
            if boxes is not None:
                for box in boxes:
                    # [x1, y1, x2, y2, conf, class_id]
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                    conf = box.conf[0].cpu().numpy()
                    class_id = int(box.cls[0].cpu().numpy())
                    
                    if conf > 0.5:  # Confidence threshold
                        detections.append({
                            'bbox': [float(x1), float(y1), float(x2-x1), float(y2-y1)],
                            'confidence': float(conf),
                            'class_id': class_id
                        })
        return detections
