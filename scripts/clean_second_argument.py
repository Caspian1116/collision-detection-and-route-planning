import os
import re

# 数据集路径
images_dir = "../data/test2/images/train"
labels_dir = "../data/test2/labels/train"

# 正则表达式匹配第二次增强的文件（含 _augX_augY 模式）
pattern = re.compile(r'_aug\d+_aug\d+\.(jpg|txt)')

# 统计删除的文件
deleted_images = 0
deleted_labels = 0

# 删除第二次增强的图像
for img in os.listdir(images_dir):
    if pattern.search(img):
        try:
            os.remove(os.path.join(images_dir, img))
            deleted_images += 1
            print(f"Deleted image: {img}")
        except Exception as e:
            print(f"Error deleting image {img}: {e}")

# 删除第二次增强的标签
for txt in os.listdir(labels_dir):
    if pattern.search(txt):
        try:
            os.remove(os.path.join(labels_dir, txt))
            deleted_labels += 1
            print(f"Deleted label: {txt}")
        except Exception as e:
            print(f"Error deleting label {txt}: {e}")

print(f"Deleted {deleted_images} images and {deleted_labels} labels.")
print("Cleanup completed. Training set restored to first augmentation.")