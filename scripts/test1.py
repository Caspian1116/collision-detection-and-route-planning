import os
import shutil
import random

# 路径
images_dir = "../data/test1/images/train"
labels_dir = "../data/test1/labels/train"
val_images_dir = "../data/test1/images/val"
val_labels_dir = "../data/test1/labels/val"
test_images_dir = "../data/test1/images/test"
test_labels_dir = "../data/test1/labels/test"

# 创建测试目录
os.makedirs(test_images_dir, exist_ok=True)
os.makedirs(test_labels_dir, exist_ok=True)

# 随机选择 50 张训练 + 10 张验证
train_images = [f for f in os.listdir(images_dir) if f.endswith('.jpg') or f.endswith('.png')]
val_images = [f for f in os.listdir(val_images_dir) if f.endswith('.jpg') or f.endswith('.png')]
random.shuffle(train_images)
random.shuffle(val_images)
selected_train = train_images[:50]
selected_val = val_images[:10]

# 复制到测试目录
for img in selected_train:
    shutil.copy(os.path.join(images_dir, img), test_images_dir)
    shutil.copy(os.path.join(labels_dir, img.replace('.jpg', '.txt').replace('.png', '.txt')), test_labels_dir)
for img in selected_val:
    shutil.copy(os.path.join(val_images_dir, img), test_images_dir)
    shutil.copy(os.path.join(val_labels_dir, img.replace('.jpg', '.txt').replace('.png', '.txt')), test_labels_dir)

# 创建临时 dataset.yaml
with open("../test_dataset.yaml", "w") as f:
    f.write("train: ./data/test1/images/test\n")
    f.write("val: ./data/test1/images/test\n")
    f.write("nc: 3\n")
    f.write("names: ['car', 'truck', 'collision']\n")