import os
import shutil
from PIL import Image

def copy_tree(src, dst):
    if os.path.exists(dst):
        print(f"Destination {dst} already exists. Remove it or choose another name.")
        return False
    shutil.copytree(src, dst)
    return True

def get_image_resolution(image_path):
    try:
        with Image.open(image_path) as img:
            return img.width * img.height
    except Exception as e:
        print(f"Error reading {image_path}: {e}")
        return -1

def group_images_by_prefix(folder):
    images = [f for f in os.listdir(folder) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp', '.gif', '.bmp', '.tiff'))]
    groups = {}
    for img in images:
        # Use the part before the first dot as the base, or the longest common prefix
        # Here, we use everything up to the first '-' or the full name if no '-'
        base = img.split('-')[0]
        groups.setdefault(base, []).append(img)
    return groups

def retain_highest_resolution_images(root_folder):
    for dirpath, _, _ in os.walk(root_folder):
        groups = group_images_by_prefix(dirpath)
        for base, files in groups.items():
            if len(files) > 1:
                resolutions = [(f, get_image_resolution(os.path.join(dirpath, f))) for f in files]
                resolutions = [r for r in resolutions if r[1] > 0]
                if not resolutions:
                    continue
                # Keep the image with the highest resolution
                best_img = max(resolutions, key=lambda x: x[1])[0]
                for f, _ in resolutions:
                    if f != best_img:
                        os.remove(os.path.join(dirpath, f))
                        print(f"Removed {os.path.join(dirpath, f)}")
            # If only one file, nothing to do

if __name__ == "__main__":
    src = "legacy/migration_2"
    dst = "legacy/migration_3"
    if copy_tree(src, dst):
        retain_highest_resolution_images(dst)
        print("Migration complete. Only highest resolution images retained.")
