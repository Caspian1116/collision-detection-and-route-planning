import os
from pathlib import Path


def remove_unmatched_images(images_dir, labels_dir):
    """
    删除图像文件夹中没有对应标注文件的图像

    参数:
        images_dir: 图像文件所在目录
        labels_dir: 标注文件所在目录
    """
    # 确保目录存在
    if not os.path.exists(images_dir):
        print(f"错误: 图像目录 {images_dir} 不存在")
        return

    if not os.path.exists(labels_dir):
        print(f"错误: 标注目录 {labels_dir} 不存在")
        return

    # 获取所有标注文件的文件名（不含扩展名）
    label_files = set()
    for label_file in Path(labels_dir).glob("*.*"):
        # 存储不带扩展名的文件名
        label_files.add(label_file.stem)

    # 统计删除的文件数量
    deleted_count = 0

    # 检查每个图像文件是否有对应的标注文件
    for image_file in Path(images_dir).glob("*.*"):
        # 获取图像文件不带扩展名的文件名
        image_name = image_file.stem

        # 如果没有对应的标注文件，则删除图像
        if image_name not in label_files:
            try:
                os.remove(image_file)
                deleted_count += 1
                print(f"已删除: {image_file}")
            except Exception as e:
                print(f"删除 {image_file} 失败: {e}")

    print(f"清理完成，共删除 {deleted_count} 个无对应标注的图像文件")


if __name__ == "__main__":
    # 配置图像和标注文件夹路径
    # 根据你的实际路径修改这两个变量
    images_directory = "../data/KITTI/training/image_2"  # 图像文件夹路径
    labels_directory = "../data/KITTI/yolo_labels_notrunk"  # 标注文件夹路径

    # 执行清理
    remove_unmatched_images(images_directory, labels_directory)