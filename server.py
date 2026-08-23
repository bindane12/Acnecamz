import uvicorn
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from ultralytics import YOLO
import cv2
import numpy as np
import math
import os

# Initialize FastAPI
app = FastAPI(title="Acne Detection API", version="1.0")

# Enable CORS so browser frontend can request from a different port
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins (file://, localhost, etc.)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

import glob

def get_latest_model_path():
    # 0. Check root directory best.pt
    if os.path.exists("best.pt"):
        return "best.pt"
        
    # 1. Check custom path in acne04v2
    custom_path = "acne04v2/yolo_scripts/runs/trained_acne_seg/yolov8x_1280_acne_detection_09022024_/weights/best.pt"
    if os.path.exists(custom_path):
        return custom_path
        
    # 2. Check for any weights/best.pt in runs/detect/
    patterns = [
        "runs/detect/*/weights/best.pt",
        "acne04v2/yolo_scripts/runs/detect/*/weights/best.pt",
        "acne04v2/yolo_scripts/runs/*/weights/best.pt"
    ]
    
    candidate_files = []
    for pattern in patterns:
        candidate_files.extend(glob.glob(pattern))
        
    if candidate_files:
        # Sort by modification time to get the newest trained model
        candidate_files.sort(key=os.path.getmtime, reverse=True)
        return candidate_files[0]
        
    return None

# Load YOLO model dynamically
model_path = get_latest_model_path()
if model_path:
    print(f"Loading custom trained YOLO model from {model_path}...")
    model = YOLO(model_path)
else:
    fallback_model = "yolov8n.pt"
    print("No custom trained model found in runs/detect/.")
    print(f"Loading/downloading pre-trained baseline model: {fallback_model}...")
    model = YOLO(fallback_model)


def bbox_to_circle(x1, y1, x2, y2):
    """Converts bounding box to center coordinates and radius."""
    cx = int((x1 + x2) / 2)
    cy = int((y1 + y2) / 2)
    # Use standard radius calculation
    radius = int(math.sqrt((cx - x1) ** 2 + (cy - y1) ** 2))
    return cx, cy, radius

import clinical_scoring

@app.post("/detect")
async def detect(file: UploadFile = File(...)):
    # Read image bytes
    contents = await file.read()
    nparr = np.frombuffer(contents, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    if img is None:
        return {"error": "Invalid image file"}

    img_h, img_w = img.shape[:2]

    # Run inference
    results = model(img, conf=0.25, verbose=False)
    
    raw_detections = []
    
    for result in results:
        boxes = result.boxes
        for box in boxes:
            # Get box coordinates in pixels
            x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
            conf = float(box.conf.cpu().numpy()[0])
            class_id = int(box.cls.cpu().numpy()[0])
            
            # Convert to circle coordinates
            cx, cy, radius = bbox_to_circle(x1, y1, x2, y2)
            
            raw_detections.append({
                "x": cx,
                "y": cy,
                "r": radius,
                "conf": conf,
                "class_id": class_id
            })
            
    # Perform clinical facial analysis
    analysis_result = clinical_scoring.analyze_facial_scan(raw_detections, img_w, img_h, image_matrix=img)
    
    return {
        "detections": analysis_result["processed_detections"],
        "analysis": {
            "hayashi_grade": analysis_result["hayashi_grade"],
            "severity_color": analysis_result["severity_color"],
            "total_lesions": analysis_result["total_lesions"],
            "total_counts": analysis_result["total_counts"],
            "zone_breakdown": analysis_result["zone_breakdown"],
            "skin_description": analysis_result["skin_description"],
            "targeted_actives": analysis_result["targeted_actives"],
            "scientific_evidence": analysis_result.get("scientific_evidence", []),
            "clinical_correlations": analysis_result.get("clinical_correlations", {}),
            "skincare_routine": analysis_result["skincare_routine"]
        }
    }

from fastapi.responses import FileResponse

@app.get("/")
async def read_index():
    if os.path.exists("index.html"):
        return FileResponse("index.html")
    return {"status": "Acne Detection API is running. index.html not found."}

@app.get("/health")
def health():
    return {"status": "ok", "model": model.names}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 7860))
    uvicorn.run("server:app", host="0.0.0.0", port=port, reload=True)
