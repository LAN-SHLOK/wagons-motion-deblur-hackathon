import cv2
import numpy as np
import torch
import matplotlib.pyplot as plt
import os
from PIL import Image


# =========================================================
# IMAGE PREPROCESSING FUNCTION
# =========================================================
def preprocess_image_for_deblur(image_path, model_size=512, show=False, save_tensor=False, output_dir=None):
    img = cv2.imread(image_path)
    if img is None:
        raise FileNotFoundError(f"Image not found: {image_path}")

    h, w, _ = img.shape
    roi = img[int(0.2*h):int(0.9*h), int(0.1*w):int(0.9*w)]

    roi = cv2.resize(roi, (model_size, model_size))
    roi_rgb = cv2.cvtColor(roi, cv2.COLOR_BGR2RGB)
    roi_norm = roi_rgb.astype(np.float32) / 255.0
    roi_norm = cv2.GaussianBlur(roi_norm, (3, 3), 0)

    if save_tensor and output_dir:
        tensor = torch.from_numpy(roi_norm).permute(2, 0, 1).unsqueeze(0)
        base_name = os.path.splitext(os.path.basename(image_path))[0]
        tensor_path = os.path.join(output_dir, f"{base_name}.pt")
        torch.save(tensor, tensor_path)

    if show:
        plt.imshow(roi_norm)
        plt.axis("off")
        plt.show()

    return roi_norm


# =========================================================
# VIDEO PREPROCESSING FUNCTION
# =========================================================
def preprocess_video_for_deblur(video_path, model_size=512):
    video_name = os.path.splitext(os.path.basename(video_path))[0]
    output_dir = os.path.join(r"D:\wagons-motion-deblur-hackathon\core\data\processed", video_name)
    os.makedirs(output_dir, exist_ok=True)

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise FileNotFoundError(f"Video not found: {video_path}")

    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    print(f"Video FPS: {fps}")
    print(f"Total Frames: {total_frames}")

    processed_frames = []
    frame_idx = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame_path = os.path.join(output_dir, f"frame_{frame_idx:05d}.png")
        cv2.imwrite(frame_path, frame)

        processed = preprocess_image_for_deblur(frame_path, model_size, output_dir=output_dir, save_tensor=True)
        processed_frames.append(processed)

        frame_idx += 1

    cap.release()
    print(f"Processed {frame_idx} frames successfully")

    return processed_frames, fps, output_dir, video_name


# =========================================================
# CONTROLLER FUNCTION
# =========================================================
def run_deblur_pipeline(input_path):
    if input_path.lower().endswith((".mp4", ".avi", ".mov", ".mkv")):
        print("Input type: VIDEO")
        return preprocess_video_for_deblur(input_path)
    else:
        raise ValueError("Only video supported in this test")


# =========================================================
# RUN
# =========================================================
if __name__ == "__main__":
    input_path = r"D:\wagons-motion-deblur-hackathon\core\data\raw\elefant_1280p.mp4"
    processed_frames, fps, output_dir, video_name = run_deblur_pipeline(input_path)

    # Show one frame
    img = Image.open(f"{output_dir}/frame_00010.png")
    plt.imshow(img)
    plt.axis("off")
    plt.show()
