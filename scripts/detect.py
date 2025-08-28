from ultralytics import YOLO

model = YOLO("runs/train/exp/weights/best.pt")  # 或 yolov8n.pt
results = model.predict(
    source="data/images/test",  # 图像文件夹、video.mp4 或 RTSP 流
    conf=0.5,                   # 置信度阈值
    iou=0.7,                    # 非极大值抑制阈值
    save=True                   # 保存结果到 runs/detect/
)

# model = YOLO("yolov8n.pt")
# results = model.predict("../test/car.jpg", save=True)