from ultralytics import YOLO
import os

data_yaml = "../test2.yaml"
model_path = "../yolov8n.pt"
if not os.path.exists(data_yaml) or not os.path.exists(model_path):
    raise FileNotFoundError("Dataset or model file not found")

model = YOLO(model_path)
model.train(
    data=data_yaml,
    epochs=80,
    imgsz=640,
    batch=12,
    device=0,  # GPU
    patience=10,
    cache=False,
    workers=8
)

print("Training completed. Results saved in runs/train/")
