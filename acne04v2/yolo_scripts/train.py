from ultralytics import YOLO
from datetime import date
import os

# Load the model (YOLOv8 Nano - lightweight, fast, and optimized for personal computers)
model = YOLO('yolov8n.pt')
 
# Training.
results = model.train(
    data='acne_detection.yaml',
    imgsz=640,       # Standard image size (much faster)
    epochs=50,       # 50 epochs is plenty to train a working detector
    patience=10,     # Early stopping patience
    batch=16,        # Batch size of 16
    device='mps',    # Run on Apple Silicon GPU (Neural Engine/Metal GPU) to avoid lag
    name='yolov8n_640_acne_detection_'+date.today().strftime("%d%m%Y")
)

