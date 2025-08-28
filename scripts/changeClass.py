import os
from pathlib import Path

# 原始标注文件所在文件夹路径
original_labels_path = Path("../data/test2/labels/val")
# 新的标注文件保存路径
new_labels_path = Path("../data/test2/labels/val1")
# 创建新的标注文件保存文件夹（如果不存在）
new_labels_path.mkdir(parents=True, exist_ok=True)

# 遍历原始标注文件所在文件夹下的所有文件
for label_file in original_labels_path.glob("*.txt"):
    file_name = label_file.name
    new_label_path = new_labels_path / file_name
    with open(label_file, 'r') as f:
        lines = f.readlines()
    new_lines = []
    for line in lines:
        parts = line.strip().split()
        if parts:
            class_id = int(parts[0])
            if class_id == 2:
                parts[0] = "1"
            new_line = " ".join(parts) + "\n"
            new_lines.append(new_line)
    with open(new_label_path, 'w') as f:
        f.writelines(new_lines)