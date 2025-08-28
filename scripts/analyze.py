import os
from collections import Counter

labels_dir = "../data/test2/labels/train"  # 训练集标签目录
class_map = {0: 'car', 1: 'collision'}  # 你的类别映射

class_counts = Counter()
for txt in os.listdir(labels_dir):
    if txt.endswith('.txt'):
        with open(os.path.join(labels_dir, txt), 'r') as f:
            lines = f.readlines()
        for line in lines:
            class_id = int(line.strip().split()[0])
            class_counts[class_id] += 1

print("类别分布:")
for class_id, count in class_counts.items():
    print(f"{class_map[class_id]}: {count} 个实例")

print(f"car 是 collision 的 {class_counts[0] / class_counts[1]:.2f} 倍")