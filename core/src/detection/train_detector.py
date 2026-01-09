"""
🚀 Role 3 Training - GPU + LOW EPOCHS (10) + Dynamic Paths
Hackathon-optimized: Fast training → Competition ready
"""
from ultralytics import YOLO
from pathlib import Path
import yaml
import torch

def get_smart_device():
    """🔥 GPU for training, CPU fallback"""
    if torch.cuda.is_available():
        print(f"✅ GPU: {torch.cuda.get_device_name(0)}")
        return 0
    print("⚠️  CPU training (slower)")
    return 'cpu'

def fix_data_yaml_path(yaml_path):
    """🔥 DYNAMIC PATH: Auto-fix data.yaml"""
    dataset_yaml = Path(yaml_path)
    if not dataset_yaml.exists():
        print(f"❌ {yaml_path} missing!")
        return None
    
    with open(dataset_yaml, 'r') as f:
        data = yaml.safe_load(f)
    
    print(f"📄 Old path: {data.get('path')}")
    data['path'] = str(dataset_yaml.parent.resolve())  # DYNAMIC FIX
    
    # Backup + rewrite
    backup = dataset_yaml.with_suffix('.backup')
    dataset_yaml.rename(backup)
    with open(dataset_yaml, 'w') as f:
        yaml.dump(data, f, default_flow_style=False)
    
    print(f"✅ NEW path: {data['path']}")
    return str(dataset_yaml)

def train_wagon_detector():
    """🚀 10 EPOCHS - Hackathon perfect!"""
    YAML_PATH = Path(__file__).parent.parent.parent / "datasets" / "wagon_blurred" / "data.yaml"
    
    # Dynamic path fix
    fixed_yaml = fix_data_yaml_path(YAML_PATH)
    if not fixed_yaml: return
    
    # Smart GPU
    device = get_smart_device()
    
    print(f"\n🎯 HACKATHON MODE: 10 EPOCHS + GPU={device}")
    
    model = YOLO('yolov8n.pt')
    model.train(
        data=fixed_yaml,
        epochs=10,                    # 🔥 REDUCED: Perfect for hackathon
        imgsz=640,
        batch=16 if isinstance(device, int) else 4,  # GPU=16, CPU=4
        name='wagon_hackathon',
        device=device,
        patience=3,                   # 🔥 Early stop after 3 stagnant epochs
        save=True,
        project='runs/detect',
        exist_ok=True,
        amp=True,                     # GPU mixed precision
        cache=True,                   # Speed boost
        workers=8
    )
    
    print("\n✅ HACKATHON TRAINING COMPLETE!")
    print("📁 Model: runs/detect/wagon_hackathon/weights/best.pt")

if __name__ == "__main__":
    train_wagon_detector()
