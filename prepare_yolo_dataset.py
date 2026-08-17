import os
import json
import shutil
import random

def main():
    # Paths
    annotations_path = "acne04v2/Acne04-v2_annotations.json"
    src_images_dir = "ACNE04/Classification/JPEGImages"
    dest_dataset_dir = "dataset"
    
    if not os.path.exists(annotations_path):
        print(f"Error: Annotations file {annotations_path} not found.")
        return
        
    if not os.path.exists(src_images_dir):
        print(f"Error: Source images directory {src_images_dir} not found. Please run the download script first.")
        return

    # Load annotations
    with open(annotations_path, "r") as f:
        data = json.load(f)

    # Get the list of files actually present in our filtered 50% subset
    available_images = set(os.listdir(src_images_dir))
    print(f"Found {len(available_images)} images in filtered subset directory.")

    # Create destination directories
    subdirs = [
        "images/train", "images/val",
        "labels/train", "labels/val"
    ]
    for subdir in subdirs:
        os.makedirs(os.path.join(dest_dataset_dir, subdir), exist_ok=True)

    # Filter images list from annotations
    images_metadata = [img for img in data["images"] if img["file_name"] in available_images]
    print(f"Matching annotations found for {len(images_metadata)} images.")

    # Shuffle and split (80% train, 20% validation)
    random.seed(42)  # For reproducibility
    random.shuffle(images_metadata)
    
    split_idx = int(len(images_metadata) * 0.8)
    train_metadata = images_metadata[:split_idx]
    val_metadata = images_metadata[split_idx:]
    
    print(f"Split: {len(train_metadata)} train images, {len(val_metadata)} val images.")

    # Group annotations by image_id
    annotations_by_img = {}
    for ann in data["annotations"]:
        img_id = ann["image_id"]
        if img_id not in annotations_by_img:
            annotations_by_img[img_id] = []
        annotations_by_img[img_id].append(ann)

    def process_split(metadata_list, split_name):
        copied_images = 0
        labeled_images = 0
        
        for img in metadata_list:
            img_id = img["id"]
            file_name = img["file_name"]
            img_w = img["width"]
            img_h = img["height"]
            
            src_img_path = os.path.join(src_images_dir, file_name)
            dest_img_path = os.path.join(dest_dataset_dir, "images", split_name, file_name)
            
            # Copy image file
            if os.path.exists(src_img_path):
                shutil.copy2(src_img_path, dest_img_path)
                copied_images += 1
            else:
                continue

            # Convert annotations to YOLO format
            label_file_name = os.path.splitext(file_name)[0] + ".txt"
            label_file_path = os.path.join(dest_dataset_dir, "labels", split_name, label_file_name)
            
            img_anns = annotations_by_img.get(img_id, [])
            yolo_lines = []
            
            for ann in img_anns:
                # Annotation has coordinates [x_center, y_center] and radius r
                coords = ann.get("coordinates")
                radius = ann.get("radius")
                
                if coords is not None and radius is not None:
                    cx, cy = coords
                    # width and height of bbox is 2 * radius
                    w = 2 * radius
                    h = 2 * radius
                    
                    # Normalize coordinates relative to image dimensions
                    cx_norm = cx / img_w
                    cy_norm = cy / img_h
                    w_norm = w / img_w
                    h_norm = h / img_h
                    
                    # Class ID is 0 for acne
                    line = f"0 {cx_norm:.6f} {cy_norm:.6f} {w_norm:.6f} {h_norm:.6f}\n"
                    yolo_lines.append(line)
            
            # Write label file (even if empty, YOLO handles it)
            with open(label_file_path, "w") as lf:
                lf.writelines(yolo_lines)
            labeled_images += 1
            
        print(f"[{split_name.upper()}] Copied {copied_images} images, created {labeled_images} label files.")

    # Process both splits
    process_split(train_metadata, "train")
    process_split(val_metadata, "val")

    # Generate acne_detection.yaml
    yaml_content = f"""# YOLOv8 Acne Detection configuration
path: {os.path.abspath(dest_dataset_dir)}
train: images/train
val: images/val

names:
  0: acne
"""
    yaml_path = "acne_detection.yaml"
    with open(yaml_path, "w") as yf:
        yf.write(yaml_content)
    
    # Copy yaml to acne04v2 folder too so train.py can find it
    shutil.copy2(yaml_path, os.path.join("acne04v2", yaml_path))
    print(f"Generated YOLO configuration: {yaml_path} and copied to acne04v2/")

if __name__ == "__main__":
    main()
