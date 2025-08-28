import albumentations as A
from albumentations.pytorch import ToTensorV2
from ultralytics import YOLO
from ultralytics.data import YOLODataset
from ultralytics.models.yolo.detect import DetectionTrainer

# --------------------------
# 1. 差异化增强管道
# --------------------------
collision_aug = A.Compose([
    A.RandomRotate90(p=0.5),
    A.Flip(p=0.5),
    A.RandomBrightnessContrast(brightness_limit=0.3, contrast_limit=0.2, p=0.6),
    A.HueSaturationValue(hue_shift_limit=10, sat_shift_limit=20, p=0.4),
    A.GaussNoise(var_limit=(10, 50), p=0.3),
    A.CoarseDropout(max_holes=3, max_height=20, max_width=20, p=0.3),
    A.Resize(640, 640),
    ToTensorV2()
], bbox_params=A.BboxParams(format='yolo', label_fields=['class_labels']))

car_aug = A.Compose([
    A.Flip(p=0.5),
    A.Resize(640, 640),
    ToTensorV2()
], bbox_params=A.BboxParams(format='yolo', label_fields=['class_labels']))

# --------------------------
# 2. 自定义数据集（含增强）
# --------------------------
class CustomDataset(YOLODataset):
    def __getitem__(self, index):
        img, bboxes, cls, path, _, _ = super().__getitem__(index)
        has_collision = 1 in cls  # 碰撞类标签索引为1（根据data.yaml调整）
        
        if has_collision:
            transformed = collision_aug(image=img, bboxes=bboxes, class_labels=cls)
        else:
            transformed = car_aug(image=img, bboxes=bboxes, class_labels=cls)
        
        return transformed['image'], transformed['bboxes'], transformed['class_labels'], path, "", ""

# --------------------------
# 3. 修复自定义训练器（关键修正）
# --------------------------
class CustomTrainer(DetectionTrainer):
    # 必须显式接收所有参数，并传递给父类方法
    def get_dataset(self, img_path, mode="train"):
        # 调用父类的get_dataset方法，确保参数完整
        dataset = super().get_dataset(img_path, mode)
        if mode == "train":
            # 替换为带增强的自定义数据集
            return CustomDataset(
                img_path=img_path,
                imgsz=self.args.imgsz,
                augment=True,
                hyp=self.args,
                rect=self.args.rect,
                cache=self.args.cache,
                prefix=mode
            )
        return dataset  # 验证集用默认数据集

# --------------------------
# 4. 启动训练
# --------------------------
if __name__ == "__main__":
    model = YOLO("yolov8n.pt")  # 基础模型
    model.train(
        data="../test2.yaml",  # 确保路径正确
        epochs=100,
        batch=12,
        imgsz=640,
        device=0,
        patience=20,
        name="collision_enhanced_train",
        trainer=CustomTrainer  # 使用修复后的训练器
    )