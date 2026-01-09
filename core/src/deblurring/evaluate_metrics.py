"""
🚀 DeblurGAN + SSIM/PSNR → JSON for Frontend (NO re-computation)
"""
import cv2
import numpy as np
from pathlib import Path
from skimage.metrics import structural_similarity as ssim
import matplotlib.pyplot as plt
import argparse
import json
import warnings
import pandas as pd
warnings.filterwarnings("ignore")

BASE_PATH = Path(__file__).parent.parent.parent.parent.resolve()
DATA_PATH = BASE_PATH / "core" / "data" / "processed"

def calculate_psnr(img1, img2):
    mse = np.mean((img1.astype(np.float64) - img2.astype(np.float64)) ** 2)
    if mse == 0: return 100
    return 20 * np.log10(255.0 / np.sqrt(mse))

def calculate_ssim(img1, img2):
    gray1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
    gray2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
    return ssim(gray1, gray2, data_range=255)

def sharpen_opencv(image):
    kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]]) * 1.5
    sharpened = cv2.filter2D(image, -1, kernel)
    return cv2.addWeighted(image, 0.7, sharpened, 0.3, 0)

def evaluate_and_store(blurred_dir, sharp_dir, output_name):
    blurred_path = BASE_PATH / blurred_dir.lstrip('/')
    sharp_path = BASE_PATH / sharp_dir.lstrip('/')
    output_path = DATA_PATH / output_name
    output_path.mkdir(parents=True, exist_ok=True)
    
    print(f"🔍 Blurred: {blurred_path} | Sharp: {sharp_path}")
    
    blurred_files = sorted(blurred_path.glob("*.png")) + sorted(blurred_path.glob("*.jpg"))
    sharp_files = sorted(sharp_path.glob("*.png")) + sorted(sharp_path.glob("*.jpg"))
    
    if len(blurred_files) == 0 or len(sharp_files) == 0:
        print("❌ No images!")
        return
    
    min_count = min(len(blurred_files), len(sharp_files))
    blurred_files = blurred_files[:min_count]
    sharp_files = sharp_files[:min_count]
    
    print(f"🔄 Computing {min_count} pairs...")
    
    # Deblur + metrics (in memory)
    psnr_scores = []
    ssim_scores = []
    filenames = []
    
    for blurred_file, sharp_file in zip(blurred_files, sharp_files):
        blurred = cv2.imread(str(blurred_file))
        sharp = cv2.imread(str(sharp_file))
        
        if blurred is None or sharp is None: continue
        
        # Deblur (OpenCV for now - replace with DeblurGAN)
        deblurred = sharpen_opencv(blurred)
        
        psnr = calculate_psnr(deblurred, sharp)
        ssim_score = calculate_ssim(deblurred, sharp)
        
        psnr_scores.append(float(psnr))
        ssim_scores.append(float(ssim_score))
        filenames.append(blurred_file.name)
    
    # 📊 SUMMARY JSON for Frontend
    metrics_summary = {
        "avg_psnr": float(np.mean(psnr_scores)),
        "avg_ssim": float(np.mean(ssim_scores)),
        "best_psnr": float(max(psnr_scores)),
        "worst_psnr": float(min(psnr_scores)),
        "total_images": len(psnr_scores),
        "timestamp": str(pd.Timestamp.now())
    }
    
    # 📈 DETAILED JSON (per-image)
    detailed_metrics = {
        "images": [
            {
                "filename": fname,
                "psnr": psnr,
                "ssim": ssim
            }
            for fname, psnr, ssim in zip(filenames, psnr_scores, ssim_scores)
        ]
    }
    
    # SAVE JSON FILES
    with open(output_path / "metrics_summary.json", "w") as f:
        json.dump(metrics_summary, f, indent=2)
    
    with open(output_path / "metrics_detailed.json", "w") as f:
        json.dump(detailed_metrics, f, indent=2)
    
    # Plot
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
    ax1.plot(psnr_scores); ax1.axhline(np.mean(psnr_scores), color='r', ls='--')
    ax1.set_title(f'Avg PSNR: {np.mean(psnr_scores):.2f}')
    ax2.plot(ssim_scores); ax2.axhline(np.mean(ssim_scores), color='r', ls='--')
    ax2.set_title(f'Avg SSIM: {np.mean(ssim_scores):.3f}')
    plt.tight_layout()
    plt.savefig(output_path / 'metrics.png', dpi=300)
    plt.close()
    
    print(f"\n✅ SAVED FOR FRONTEND:")
    print(f"   📊 Summary: {output_path}/metrics_summary.json")
    print(f"   📈 Detailed: {output_path}/metrics_detailed.json")
    print(f"   📉 Plot:     {output_path}/metrics.png")
    print(f"   Avg PSNR: {metrics_summary['avg_psnr']:.2f} | SSIM: {metrics_summary['avg_ssim']:.3f}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--blurred", required=True)
    parser.add_argument("--sharp", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    
    evaluate_and_store(args.blurred, args.sharp, args.output)
