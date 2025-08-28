import os
images_dir = "../data/test2/images/train"
labels_dir = "../data/test2/labels/train"
images = [f for f in os.listdir(images_dir) if f.endswith(('.jpg', '.png'))]
for img in images:
    label = img.replace('.jpg', '.txt').replace('.png', '.txt')
    label_path = os.path.join(labels_dir, label)
    if not os.path.exists(label_path):
        print(f"Missing label for {img}")
    elif os.path.getsize(label_path) == 0:
        print(f"Empty label file: {label}")
print("everything is fine!")