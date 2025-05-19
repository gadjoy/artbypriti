import os
import shutil

CONTENT_DIR = "content"
EXCLUDE = {"about"}

def flatten_content_folders():
    for category in os.listdir(CONTENT_DIR):
        category_path = os.path.join(CONTENT_DIR, category)
        if not os.path.isdir(category_path) or category in EXCLUDE:
            continue
        for subfolder in os.listdir(category_path):
            subfolder_path = os.path.join(category_path, subfolder)
            if os.path.isdir(subfolder_path):
                dest_path = os.path.join(CONTENT_DIR, subfolder)
                if os.path.exists(dest_path):
                    print(f"WARNING: {dest_path} already exists and will be overwritten!")
                    shutil.rmtree(dest_path)
                shutil.move(subfolder_path, dest_path)
                print(f"Moved folder: {subfolder_path} -> {dest_path}")
        # Remove the now-empty category folder
        if not os.listdir(category_path):
            os.rmdir(category_path)

if __name__ == "__main__":
    flatten_content_folders()
