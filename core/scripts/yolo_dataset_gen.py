"""
core/scripts/yolo_dataset_gen.py - UNIVERSAL YOLO DATASET CREATOR
Auto-detects: video.mp4 → images/*.jpg → frames/*.jpg → YOLO dataset + videos
"""
import os
import shutil
import cv2
import numpy as np
from pathlib import Path
import argparse
import random

# Detect Project Root (assuming script is in core/scripts)
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

def create_vehicle_labels(image_path: str, txt_path: str):
    """Generate YOLO labels for vehicles (cars/wagons)"""
    img = cv2.imread(image_path)
    if img is None:
        return
    
    h, w = img.shape[:2]
    x1, y1, x2, y2 = 0.10*w, 0.15*h, 0.90*w, 0.75*h
    x_center = (x1 + x2) / 2 / w
    y_center = (y1 + y2) / 2 / h
    width = (x2 - x1) / w
    height = (y2 - y1) / h
    
    with open(txt_path, 'w') as f:
        f.write(f"0 {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}\n")

def deblur_frame(frame_path: str) -> np.ndarray:
    """YOUR sharpening deblur"""
    img = cv2.imread(frame_path)
    kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]]) * 1.5
    sharpened = cv2.filter2D(img, -1, kernel)
    return cv2.addWeighted(img, 0.7, sharpened, 0.3, 0)

def extract_frames_from_video(video_path: str, temp_frames_dir: str):
    """Extract 8 FPS frames from video"""
    cap = cv2.VideoCapture(video_path)
    frame_count = 0
    
    Path(temp_frames_dir).mkdir(exist_ok=True)
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # 8 FPS extraction (from 30 FPS)
        if frame_count % 4 == 0:
            frame_idx = frame_count // 4
            cv2.imwrite(f"{temp_frames_dir}/frame_{frame_idx:04d}.jpg", frame)
        
        frame_count += 1
    
    cap.release()
    print(f"✅ Extracted {frame_count//4} frames from video")
    return temp_frames_dir

def is_video_file(path: str) -> bool:
    """Check if file is video"""
    video_exts = {'.mp4', '.avi', '.mov', '.mkv', '.m4v'}
    return Path(path).suffix.lower() in video_exts

def is_image_folder(path: str) -> bool:
    """Check if folder contains images"""
    path_obj = Path(path)
    images = list(path_obj.glob("*.jpg")) + list(path_obj.glob("*.png"))
    return len(images) > 0

def process_frames_to_dataset(input_frames_dir: str, output_dataset_dir: Path):
    """Frames → YOLO dataset + videos (8 FPS)"""
    frames_dir = Path(input_frames_dir)
    dataset_dir = output_dataset_dir
    dataset_dir.mkdir(exist_ok=True)
    
    frame_files = sorted(frames_dir.glob("*.jpg"))
    total_frames = len(frame_files)
    
    # Deblur frames
    deblurred_frames = [deblur_frame(str(f)) for f in frame_files]
    frame_names = [f.stem for f in frame_files]
    
    height, width = deblurred_frames[0].shape[:2]
    
    # 80/20 split
    indices = list(range(total_frames))
    random.shuffle(indices)
    split_idx = int(0.8 * total_frames)
    
    for split_name, idx_range in [("train", indices[:split_idx]), ("val", indices[split_idx:])]:
        split_path = dataset_dir / split_name
        (split_path / "images").mkdir(parents=True, exist_ok=True)
        (split_path / "labels").mkdir(parents=True, exist_ok=True)
        
        for idx in idx_range:
            frame_name = frame_names[idx]
            cv2.imwrite(str(split_path / "images" / f"{frame_name}.jpg"), deblurred_frames[idx])
            create_vehicle_labels(str(split_path / "images" / f"{frame_name}.jpg"), 
                                split_path / "labels" / f"{frame_name}.txt")
        
        # Split video
        video_path = split_path / f"{split_name}_video.mp4"
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(str(video_path), fourcc, 8.0, (width, height))
        for idx in idx_range:
            out.write(deblurred_frames[idx])
        out.release()
    
    # Main video
    main_video = dataset_dir / "deblurred_video.mp4"
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(str(main_video), fourcc, 8.0, (width, height))
    for frame in deblurred_frames:
        out.write(frame)
    out.release()
    
    # data.yaml
    with open(dataset_dir / "data.yaml", 'w') as f:
        f.write(f"""path: {dataset_dir}
train: train/images
val: val/images
nc: 1
names: ['vehicle']
""")

def build_from_images(image_dir: str, dataset_name: str):
    """Static images → YOLO dataset"""
    image_dir = Path(image_dir)
    if not image_dir.is_absolute():
        image_dir = PROJECT_ROOT / image_dir

    dataset_path = PROJECT_ROOT / "core" / "datasets" / dataset_name
    
    (dataset_path / "train/images").mkdir(parents=True, exist_ok=True)
    (dataset_path / "train/labels").mkdir(parents=True, exist_ok=True)
    (dataset_path / "val/images").mkdir(parents=True, exist_ok=True)
    (dataset_path / "val/labels").mkdir(parents=True, exist_ok=True)
    
    images = list(image_dir.glob("*.jpg")) + list(image_dir.glob("*.png"))
    np.random.shuffle(images)
    split_idx = int(0.8 * len(images))
    
    for split, img_range in [("train", images[:split_idx]), ("val", images[split_idx:])]:
        split_path = dataset_path / split
        for img_path in img_range:
            img_name = img_path.stem
            shutil.copy2(img_path, split_path / "images" / f"{img_name}.jpg")
            create_vehicle_labels(str(img_path), split_path / "labels" / f"{img_name}.txt")
    
    with open(dataset_path / "data.yaml", 'w') as f:
        f.write(f"""path: {dataset_path}
train: train/images
val: val/images
nc: 1
names: ['vehicle']
""")

def auto_detect_and_process(input_path: str):
    """MAGIC: Auto-detect input type and process"""
    input_path_obj = Path(input_path)
    if not input_path_obj.is_absolute():
        input_path_obj = PROJECT_ROOT / input_path
    
    # CASE 1: Single video file
    if input_path_obj.is_file() and is_video_file(str(input_path_obj)):
        print(f"🎥 VIDEO detected: {input_path_obj}")
        temp_frames = PROJECT_ROOT / "temp_frames"
        extract_frames_from_video(str(input_path_obj), str(temp_frames))
        dataset_name = input_path_obj.stem
        process_frames_to_dataset(str(temp_frames), PROJECT_ROOT / "core/data/processed" / f"{dataset_name}_dataset")
        shutil.rmtree(str(temp_frames))  # Cleanup
        return
    
    # CASE 2: Image folder
    elif input_path_obj.is_dir() and is_image_folder(str(input_path_obj)):
        print(f"🖼️  IMAGE FOLDER detected: {input_path_obj}")
        dataset_name = input_path_obj.name
        build_from_images(str(input_path_obj), dataset_name)
        return
    
    # CASE 3: Frames folder (already extracted)
    elif input_path_obj.is_dir():
        print(f"📁 FRAMES FOLDER detected: {input_path_obj}")
        dataset_name = input_path_obj.name
        process_frames_to_dataset(str(input_path_obj), PROJECT_ROOT / "core/data/processed" / f"{dataset_name}_dataset")
        return
    
    else:
        print(f"❌ Unknown input: {input_path}")
        print("Supported: video.mp4 OR images/ OR frames/")

def main():
    parser = argparse.ArgumentParser(description="Universal YOLO Dataset Generator")
    parser.add_argument("--input", default="core/data/raw/wagon_blurred", help="Video/images/frames folder")
    args = parser.parse_args()
    
    auto_detect_and_process(args.input)

if __name__ == "__main__":
    main()