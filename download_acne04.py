import os
import sys
import tarfile
import zipfile
import json
import shutil
import gdown

def main():
    dest_dir = "ACNE04"
    jpeg_dir = os.path.join(dest_dir, "Classification", "JPEGImages")
    
    # Create directories
    os.makedirs(dest_dir, exist_ok=True)
    
    # The original ACNE04 Google Drive folder ID
    folder_id = "18yJcHXhzOv7H89t-Lda6phheAicLqMuZ"
    
    print(f"Downloading ACNE04 dataset folder from Google Drive (ID: {folder_id})...")
    print("Note: This might take a few minutes depending on connection speed.")
    
    # Download the folder contents using gdown
    download_temp = "acne04_download_temp"
    os.makedirs(download_temp, exist_ok=True)
    
    try:
        gdown.download_folder(id=folder_id, output=download_temp, quiet=False, use_cookies=False)
    except Exception as e:
        print(f"Error downloading folder: {e}")
        print("Attempting to download files directly if folder download failed...")
        # Fallback to direct file download if folder fails
        # Common file names in the folder: 'Classification.tar', 'Detection.tar'
        # Let's try downloading the folder or individual files
    
    print("Processing downloaded files...")
    # Find any tar or zip files downloaded
    extracted = False
    for root, dirs, files in os.walk(download_temp):
        for file in files:
            file_path = os.path.join(root, file)
            if file.endswith(".tar") or file.endswith(".tar.gz"):
                print(f"Extracting tar file: {file_path}")
                try:
                    with tarfile.open(file_path, "r:") as tar:
                        tar.extractall(path=dest_dir)
                    extracted = True
                except Exception as e:
                    print(f"Failed to extract {file}: {e}")
            elif file.endswith(".zip"):
                print(f"Extracting zip file: {file_path}")
                try:
                    with zipfile.ZipFile(file_path, "r") as zip_ref:
                        zip_ref.extractall(dest_dir)
                    extracted = True
                except Exception as e:
                    print(f"Failed to extract {file}: {e}")
            elif file.endswith(".jpg") or file.endswith(".png"):
                # If images were downloaded directly as files, move them to JPEGImages
                os.makedirs(jpeg_dir, exist_ok=True)
                shutil.move(file_path, os.path.join(jpeg_dir, file))
                extracted = True

    # If the folder was structured directly
    if not extracted:
        # Check if the folder contains directories directly
        for item in os.listdir(download_temp):
            item_path = os.path.join(download_temp, item)
            if os.path.isdir(item_path):
                # If there's a folder like Classification/ or Detection/
                shutil.copytree(item_path, os.path.join(dest_dir, item), dirs_exist_ok=True)
                extracted = True

    # Clean up temp download folder
    if os.path.exists(download_temp):
        shutil.rmtree(download_temp)
        
    # Verify we have images
    if not os.path.exists(jpeg_dir) or len(os.listdir(jpeg_dir)) == 0:
        print("Error: Could not locate JPEGImages. Checking alternate folders...")
        # Check if Classification/JPEGImages was placed in a different path
        found = False
        for root, dirs, files in os.walk(dest_dir):
            if root.endswith("JPEGImages") and len(files) > 0:
                print(f"Found images in: {root}")
                if root != jpeg_dir:
                    shutil.copytree(root, jpeg_dir, dirs_exist_ok=True)
                found = True
                break
        if not found:
            print("Failed to find any images. Please make sure the dataset downloaded correctly.")
            sys.exit(1)

    print(f"Total images found: {len(os.listdir(jpeg_dir))}")

    # Now filter to keep only 50% of the images in Acne04-v2_annotations.json
    annotations_path = "acne04v2/Acne04-v2_annotations.json"
    if not os.path.exists(annotations_path):
        print(f"Error: Annotations file {annotations_path} not found.")
        sys.exit(1)

    with open(annotations_path, "r") as f:
        annotations = json.load(f)

    all_images = annotations.get("images", [])
    # Sort or select 50% of the images
    half_count = len(all_images) // 2
    images_to_keep = set(img["file_name"] for img in all_images[:half_count])
    
    print(f"Filtering to keep {half_count} images (50% of {len(all_images)} annotations)...")

    removed_count = 0
    kept_count = 0
    
    for filename in os.listdir(jpeg_dir):
        if filename in images_to_keep:
            kept_count += 1
        else:
            os.remove(os.path.join(jpeg_dir, filename))
            removed_count += 1

    print(f"Filtering complete: Kept {kept_count} images, deleted {removed_count} images.")

if __name__ == "__main__":
    main()
