import os
import cv2
import numpy as np
import albumentations as A

# 定义增强变换
transform = A.Compose([
    A.RandomRotate90(p=0.7),
    A.HorizontalFlip(p=0.5),
    A.VerticalFlip(p=0.5),
    A.RandomBrightnessContrast(brightness_limit=0.2, contrast_limit=0.2, p=0.6),
    A.ShiftScaleRotate(shift_limit=0.1, scale_limit=0.1, rotate_limit=45, p=0.6),
    A.HueSaturationValue(hue_shift_limit=20, sat_shift_limit=30, val_shift_limit=20, p=0.5),
    A.GaussNoise(p=0.3),
    A.Blur(blur_limit=3, p=0.3),
], bbox_params=A.BboxParams(format='yolo', min_visibility=0.3, label_fields=['class_labels']))

# 数据集路径
images_dir = "../data/test2/images/train"
labels_dir = "../data/test2/labels/train"
output_images_dir = images_dir  # 保存到原目录
output_labels_dir = labels_dir

# 确保输出目录存在
os.makedirs(output_images_dir, exist_ok=True)
os.makedirs(output_labels_dir, exist_ok=True)

# 扫描包含 collision 的图像
collision_images = []
for txt in os.listdir(labels_dir):
    if txt.endswith('.txt'):
        with open(os.path.join(labels_dir, txt), 'r') as f:
            lines = f.readlines()
        has_collision = any(int(line.strip().split()[0]) == 1 for line in lines if line.strip())
        if has_collision:
            img_name = txt.replace('.txt', '.jpg')  # 假设图像为 .jpg
            if os.path.exists(os.path.join(images_dir, img_name)):
                collision_images.append(img_name)

print(f"Found {len(collision_images)} images with collision.")

# 对每个 collision 图像进行 7 次增强（总 8 倍）
for img_name in collision_images:
    img_path = os.path.join(images_dir, img_name)
    label_path = os.path.join(labels_dir, img_name.replace('.jpg', '.txt'))

    img = cv2.imread(img_path)
    if img is None:
        print(f"Skip invalid image {img_name}")
        continue

    bboxes = []
    class_labels = []
    with open(label_path, 'r') as f:
        lines = f.readlines()
    for line in lines:
        if line.strip():
            parts = line.strip().split()
            class_id = int(parts[0])
            bbox = list(map(float, parts[1:5]))
            if len(bbox) == 4:
                bboxes.append(bbox)
                class_labels.append(class_id)

    for aug_id in range(7):  # 生成 7 个增强版本
        augmented = transform(image=img, bboxes=bboxes, class_labels=class_labels)
        aug_img = augmented['image']
        aug_bboxes = augmented['bboxes']
        aug_classes = augmented['class_labels']

        if not aug_bboxes:  # 跳过增强后无有效边界框的样本
            continue

        aug_img_name = f"{os.path.splitext(img_name)[0]}_aug{aug_id}.jpg"
        aug_label_name = f"{os.path.splitext(img_name)[0]}_aug{aug_id}.txt"
        cv2.imwrite(os.path.join(output_images_dir, aug_img_name), aug_img)

        with open(os.path.join(output_labels_dir, aug_label_name), 'w') as f:
            for cls, bbox in zip(aug_classes, aug_bboxes):
                f.write(f"{cls} {bbox[0]:.6f} {bbox[1]:.6f} {bbox[2]:.6f} {bbox[3]:.6f}\n")

print("Data augmentation completed. New images and labels added to original directories.")