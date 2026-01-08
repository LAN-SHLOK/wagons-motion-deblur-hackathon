"""
Frames → Deblurred Frames + Demo Video (Your Project Structure)
core/src/deblurring/frames_to_deblurred_video.py - VIDEO FIXED
"""
import cv2
import numpy as np
from pathlib import Path
import argparse

# ✅ FIXED: Correct BASE_PATH for your structure
BASE_PATH = Path(__file__).parent.parent.parent.resolve()  # core/src/deblurring → projectname/core
DATA_PATH = BASE_PATH / "data" / "processed"

class FrameDeblur:
    def deblur_frame(self, frame_path):
        img = cv2.imread(frame_path)
        kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]]) * 1.5
        sharpened = cv2.filter2D(img, -1, kernel)
        return cv2.addWeighted(img, 0.7, sharpened, 0.3, 0)
    
    def process_complete(self, input_dir, output_name):
        input_path = Path(input_dir).resolve()
        print(f"📁 Input: {input_path}")
        
        # ✅ Split video and frames into ROOT processed/
        processed_root = DATA_PATH  # core/data/processed/
        output_base = processed_root / output_name
        output_base.mkdir(parents=True, exist_ok=True)
        
        # ✅ FRAMES go to ROOT deblurred_frames/
        deblurred_dir = processed_root / "deblurred_frames"
        deblurred_dir.mkdir(exist_ok=True)
        
        # Get ALL frames numerically sorted
        frame_files = sorted(input_path.glob("*.png")) + sorted(input_path.glob("*.jpg"))
        def numerical_sort(f):
            numbers = ''.join(filter(str.isdigit, f.stem))
            return int(numbers) if numbers else float('inf')
        frame_files.sort(key=numerical_sort)
        
        print(f"🔄 Processing {len(frame_files)} frames...")
        
        # Deblur ALL frames → ROOT deblurred_frames/
        deblurred_frames = []
        for frame_path in frame_files:
            sharp_frame = self.deblur_frame(str(frame_path))
            output_frame_name = frame_path.name
            cv2.imwrite(str(deblurred_dir / output_frame_name), sharp_frame)
            deblurred_frames.append(sharp_frame)
        
        if not deblurred_frames:
            print("❌ No frames to process!")
            return
            
        height, width = deblurred_frames[0].shape[:2]
        print(f"📐 Frame size: {width}x{height}")
        
        # AUTO-DETECT ORIGINAL FPS
        original_video_fps = 30.0
        raw_video = BASE_PATH / "data" / "raw" / "original_video.mp4"
        if raw_video.exists():
            cap = cv2.VideoCapture(str(raw_video))
            original_video_fps = cap.get(cv2.CAP_PROP_FPS)
            cap.release()
            print(f"📹 Original FPS: {original_video_fps:.1f}")
        
        # ✅ FIXED VIDEO WRITING - MP4 + VERIFICATION
        video_dir = processed_root / "video"
        video_dir.mkdir(exist_ok=True)
        demo_video = video_dir / f"deblurred_demo_{output_name}_{int(original_video_fps)}fps.mp4"
        
        # ✅ FIXED: MP4V codec (works everywhere)
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(str(demo_video), fourcc, original_video_fps, (width, height))
        
        # ✅ CRITICAL: Check if VideoWriter opened
        if not out.isOpened():
            print(f"❌ VideoWriter FAILED for: {demo_video}")
            print("🔄 Trying alternative codec...")
            fourcc = cv2.VideoWriter_fourcc(*'XVID')
            out = cv2.VideoWriter(str(demo_video.with_suffix('.avi')), fourcc, original_video_fps, (width, height))
            demo_video = demo_video.with_suffix('.avi')
        
        if not out.isOpened():
            print("❌ ALL CODECS FAILED! Check OpenCV installation.")
            return
        
        print(f"✅ VideoWriter OK: {demo_video}")
        
        # Write frames with progress
        for i, frame in enumerate(deblurred_frames):
            success = out.write(frame)
            if i % 10 == 0:
                print(f"   📹 Frame {i+1}/{len(deblurred_frames)}")
        
        out.release()
        print(f"✅ VIDEO SAVED: {demo_video}")
        
        # ✅ FINAL VERIFICATION
        if demo_video.exists():
            file_size = demo_video.stat().st_size
            print(f"✅ File verified: {file_size/1024/1024:.1f} MB")
        else:
            print(f"❌ Video file not created: {demo_video}")
        
        print(f"""
🎉 COMPLETE! PERFECT STRUCTURE!
📁 Friend's DeepSORT: {deblurred_dir}
📹 Frontend demo:     {demo_video}
📊 {len(deblurred_frames)} frames @ {original_video_fps:.1f}fps
        """)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="ABSOLUTE path to frames/")
    parser.add_argument("--output", required=True, help="output name (e.g., deblurred_smooth)")
    args = parser.parse_args()
    
    deblur = FrameDeblur()
    deblur.process_complete(args.input, args.output)
