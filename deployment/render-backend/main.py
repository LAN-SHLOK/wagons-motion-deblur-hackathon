from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import time

app = FastAPI()

# CRITICAL: Allow AWS Amplify to talk to Render
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, replace with your Amplify URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/v1/health")
def health_check():
    return {"status": "online", "engine": "WagonAI Neural Pipeline v1.0"}

@app.post("/api/v1/pipeline")
async def run_pipeline(file: UploadFile = File(...)):
    # 1. Receive File
    contents = await file.read()
    
    # 2. Logic: Here you would call your deblur_module and yolo_module
    # For now, we simulate the processing time
    time.sleep(1.5) 
    
    # 3. Return the exact JSON structure your app.js expects
    return {
        "original_url": "https://your-s3-or-cloudinary-link.com/input.jpg",
        "processed_url": "https://your-s3-or-cloudinary-link.com/output.jpg",
        "detections": 5,
        "confidence": 93.8,
        "psnr_history": [22.4, 24.1, 26.5, 28.9, 27.2, 30.5]
    }
from fastapi import FastAPI

# This variable NAME must be exactly 'app'
app = FastAPI() 

@app.get("/")
async def root():
    return {"status": "WagonAI Engine Online"}
