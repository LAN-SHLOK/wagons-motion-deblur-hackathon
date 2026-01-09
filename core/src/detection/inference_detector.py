"""
🚀 MAIN PIPELINE: Test on train dataset + count wagons
"""
from ultralytics import YOLO
import cv2
from pathlib import Path
import argparse
import numpy as np

def evaluate_wagon_detection(model_path, test_frames_dir):
    """Evaluate trained model on train dataset"""
    model = YOLO(model_path)
    
    test_path = Path(test_frames_dir)
    frame_files = sorted(test_path.glob("*.png")) + sorted(test_path.glob("*.jpg"))
    
    total_wagons = 0
    confidences = []
    
    print(f"🔄 Evaluating {len(frame_files)} test frames...")
    
    for i, frame_path in enumerate(frame_files):
        frame = cv2.imread(str(frame_path))
        results = model(frame, conf=0.25, verbose=False)
        
        frame_wagon_count = 0
        for r in results:
            boxes = r.boxes
            if boxes is not None:
                frame_wagon_count = len(boxes)
                total_wagons += frame_wagon_count
                confidences.extend(boxes.conf.cpu().numpy())
        
        if i % 10 == 0:
            print(f"   Frame {i}: {frame_wagon_count} wagons")
    
    avg_conf = np.mean(confidences) if confidences else 0
    print(f"\n📊 EVALUATION RESULTS:")
    print(f"├── Total detections: {total_wagons}")
    print(f"├── Avg confidence:  {avg_conf:.3f}")
    print(f"└── Unique frames:    {len(frame_files)}")
    
    return total_wagons

def count_wagons_production(frames_dir):
    """Production wagon counting"""
    model = YOLO('runs/detect/wagon_detector/weights/best.pt')
    
    frames_path = Path(frames_dir)
    frame_files = sorted(frames_path.glob("*.png")) + sorted(frames_path.glob("*.jpg"))
    
    unique_wagons = set()
    print(f"🔄 Counting {len(frame_files)} production frames...")
    
    for i, frame_path in enumerate(frame_files):
        frame = cv2.imread(str(frame_path))
        results = model(frame, conf=0.3, verbose=False)
        
        for r in results:
            boxes = r.boxes
            if boxes is not None:
                for box in boxes:
                    wagon_id = f"wagon_{i}_{int(box.conf[0]*100)}"
                    unique_wagons.add(wagon_id)
    
    print(f"\n🎉 PRODUCTION: {len(unique_wagons)} UNIQUE WAGONS!")
    return len(unique_wagons)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="test_frames/ or deblurred_frames/")
    parser.add_argument("--mode", choices=['train', 'eval', 'count'], default='count')
    args = parser.parse_args()
    
    if args.mode == 'train':
        from train_detector import train_wagon_detector
        train_wagon_detector()
    else:
        wagon_count = evaluate_wagon_detection('runs/detect/wagon_detector/weights/best.pt', args.input)
        print(f"✅ EVALUATION COMPLETE: {wagon_count} wagons")
