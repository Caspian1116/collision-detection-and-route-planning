# import os
# import cv2
# from pathlib import Path
#
#
# def convert_kitti_to_yolo(kitti_label_dir, image_dir, yolo_label_dir, class_map):
#     """
#     Convert KITTI labels to YOLO format.
#
#     Args:
#         kitti_label_dir (str): Path to KITTI label directory (e.g., 'data/labels/train').
#         image_dir (str): Path to image directory (e.g., 'data/images/train').
#         yolo_label_dir (str): Path to output YOLO label directory (e.g., 'data/yolo_labels/train').
#         class_map (dict): Mapping of KITTI class names to YOLO class IDs (e.g., {'Car': 0, 'Pedestrian': 1}).
#     """
#     # Create output directory
#     Path(yolo_label_dir).mkdir(parents=True, exist_ok=True)
#
#     # Process each label file
#     for label_file in os.listdir(kitti_label_dir):
#         if not label_file.endswith('.txt'):
#             continue
#
#         # Get corresponding image file
#         image_file = label_file.replace('.txt', '.png')  # KITTI images are .png
#         image_path = os.path.join(image_dir, image_file)
#
#         # Read image dimensions
#         img = cv2.imread(image_path)
#         if img is None:
#             print(f"Warning: Image {image_path} not found, skipping.")
#             continue
#         img_height, img_width = img.shape[:2]
#
#         # Read KITTI label
#         kitti_label_path = os.path.join(kitti_label_dir, label_file)
#         yolo_label_path = os.path.join(yolo_label_dir, label_file)
#
#         with open(kitti_label_path, 'r') as f:
#             lines = f.readlines()
#
#         yolo_labels = []
#         for line in lines:
#             parts = line.strip().split()
#             class_name = parts[0]
#
#             # Skip irrelevant classes (e.g., DontCare)
#             if class_name not in class_map:
#                 continue
#
#             class_id = class_map[class_name]
#             left, top, right, bottom = map(float, parts[4:8])
#
#             # Convert to YOLO format
#             center_x = (left + right) / 2 / img_width
#             center_y = (top + bottom) / 2 / img_height
#             width = (right - left) / img_width
#             height = (bottom - top) / img_height
#
#             # Ensure values are within [0, 1]
#             center_x = max(0, min(1, center_x))
#             center_y = max(0, min(1, center_y))
#             width = max(0, min(1, width))
#             height = max(0, min(1, height))
#
#             yolo_labels.append(f"{class_id} {center_x:.6f} {center_y:.6f} {width:.6f} {height:.6f}")
#
#         # Write YOLO label file
#         with open(yolo_label_path, 'w') as f:
#             f.write('\n'.join(yolo_labels) + '\n')
#
#         print(f"Converted {label_file} to YOLO format.")
#
#
# def main():
#     # Define paths
#     kitti_label_dir = "../data/KITTI/training_labels/label_2"  # KITTI labels
#     image_dir = "../data/KITTI/training/image_2"  # KITTI images
#     yolo_label_dir = "../data/KITTI/yolo_labels"  # Output YOLO labels
#
#     # Define class mapping (adjust based on your needs)
#     class_map = {
#         'Car': 0,
#         'Truck': 1,
#         # Add more classes if needed (e.g., 'Truck', 'Cyclist')
#     }
#
#     # Convert labels
#     convert_kitti_to_yolo(kitti_label_dir, image_dir, yolo_label_dir, class_map)
#
#     # # Repeat for validation set if needed
#     # kitti_label_dir_val = "data/labels/val"
#     # image_dir_val = "data/images/val"
#     # yolo_label_dir_val = "data/yolo_labels/val"
#     # convert_kitti_to_yolo(kitti_label_dir_val, image_dir_val, yolo_label_dir_val, class_map)
#
#
# if __name__ == "__main__":
#     main()

import os
import cv2
from pathlib import Path


def convert_kitti_to_yolo(kitti_label_dir, image_dir, yolo_label_dir, class_map):
    """
    Convert KITTI labels to YOLO format, skipping empty or irrelevant label files.

    Args:
        kitti_label_dir (str): Path to KITTI label directory (e.g., 'data/labels/train').
        image_dir (str): Path to image directory (e.g., 'data/images/train').
        yolo_label_dir (str): Path to output YOLO label directory (e.g., 'data/yolo_labels/train').
        class_map (dict): Mapping of KITTI class names to YOLO class IDs (e.g., {'Car': 0}).
    """
    # Create output directory
    Path(yolo_label_dir).mkdir(parents=True, exist_ok=True)

    # Process each label file
    for label_file in os.listdir(kitti_label_dir):
        if not label_file.endswith('.txt'):
            continue

        # Get corresponding image file
        image_file = label_file.replace('.txt', '.png')  # KITTI images are .png
        image_path = os.path.join(image_dir, image_file)

        # Check if image exists
        if not os.path.exists(image_path):
            print(f"Warning: Image {image_path} not found, skipping {label_file}.")
            continue

        # Read image dimensions
        img = cv2.imread(image_path)
        if img is None:
            print(f"Warning: Failed to read image {image_path}, skipping {label_file}.")
            continue
        img_height, img_width = img.shape[:2]

        # Read KITTI label
        kitti_label_path = os.path.join(kitti_label_dir, label_file)
        with open(kitti_label_path, 'r') as f:
            lines = f.readlines()

        yolo_labels = []
        has_valid_class = False
        for line in lines:
            parts = line.strip().split()
            if not parts:  # Skip empty lines
                continue
            class_name = parts[0]

            # Skip irrelevant classes (e.g., DontCare)
            if class_name not in class_map:
                continue

            has_valid_class = True
            class_id = class_map[class_name]
            left, top, right, bottom = map(float, parts[4:8])

            # Convert to YOLO format
            center_x = (left + right) / 2 / img_width
            center_y = (top + bottom) / 2 / img_height
            width = (right - left) / img_width
            height = (bottom - top) / img_height

            # Ensure values are within [0, 1]
            center_x = max(0, min(1, center_x))
            center_y = max(0, min(1, center_y))
            width = max(0, min(1, width))
            height = max(0, min(1, height))

            yolo_labels.append(f"{class_id} {center_x:.6f} {center_y:.6f} {width:.6f} {height:.6f}")

        # Only save non-empty label files
        if has_valid_class and yolo_labels:
            yolo_label_path = os.path.join(yolo_label_dir, label_file)
            with open(yolo_label_path, 'w') as f:
                f.write('\n'.join(yolo_labels) + '\n')
            print(f"Converted {label_file} to YOLO format.")
        else:
            print(f"Skipped {label_file}: No valid classes (Car/Truck) found.")


def main():
    # Define paths
    # kitti_label_dir = "data/labels/train"  # KITTI labels
    # image_dir = "data/images/train"  # KITTI images
    # yolo_label_dir = "data/yolo_labels/train"  # Output YOLO labels
    kitti_label_dir = "../data/KITTI/training_labels/label_2"  # KITTI labels
    image_dir = "../data/KITTI/training/image_2"  # KITTI images
    yolo_label_dir = "../data/KITTI/yolo_labels"  # Output YOLO labels

    # Define class mapping (only Car for now)
    class_map = {
        'Car': 0,
        'Truck': 1
    }

    # Convert labels for training set
    convert_kitti_to_yolo(kitti_label_dir, image_dir, yolo_label_dir, class_map)

    # # Repeat for validation set
    # kitti_label_dir_val = "data/labels/val"
    # image_dir_val = "data/images/val"
    # yolo_label_dir_val = "data/yolo_labels/val"
    # convert_kitti_to_yolo(kitti_label_dir_val, image_dir_val, yolo_label_dir_val, class_map)


if __name__ == "__main__":
    main()