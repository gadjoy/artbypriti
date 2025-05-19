import os
import shutil
import re
from pathlib import Path

SRC = "legacy/migration_3/content"
DST = "legacy/migration_4/content"

def humanize_category(cat):
    # Replace dashes with spaces and capitalize
    return cat.replace("-", " ").replace("_", " ").capitalize()

def generate_description(title):
    return f"These paintings are examples of {title}."

def get_image_from_index(index_path):
    """Get the image filename from resources.src in index.md"""
    try:
        with open(index_path, "r") as f:
            content = f.read()
            # Look for src: in the resources section
            match = re.search(r'resources:.*?\n\s*-\s*src:\s*([^\n]+)', content, re.DOTALL)
            if match:
                return match.group(1).strip()
    except Exception as e:
        print(f"Error reading {index_path}: {e}")
    return None

def process_artwork_folder(folder_path):
    """Process a single artwork folder"""
    index_path = os.path.join(folder_path, "index.md")
    if not os.path.exists(index_path):
        print(f"No index.md found in {folder_path}")
        return None
    
    # Get the target image filename
    target_image = get_image_from_index(index_path)
    if not target_image:
        print(f"No image source found in {index_path}")
        return None
    
    print(f"\nProcessing folder: {folder_path}")
    print(f"Target image to keep: {target_image}")
    
    # List all image files
    image_files = [f for f in os.listdir(folder_path) 
                  if f.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp'))]
    
    # Remove other images
    for img in image_files:
        if img != target_image:
            try:
                file_path = os.path.join(folder_path, img)
                print(f"Removing: {img}")
                os.remove(file_path)
            except Exception as e:
                print(f"Error removing {img}: {e}")
        else:
            print(f"Keeping: {img}")
    
    return target_image

def create_category_index(category_path, category_name, cover_image):
    """Create or update category _index.md with cover image"""
    title = humanize_category(category_name)
    description = f"These paintings are examples of {title}."
    
    index_content = f"""---
description: {description}
title: {title}
resources:
  - src: {cover_image}
    params:
      cover: true
---

"""
    index_path = os.path.join(category_path, "_index.md")
    with open(index_path, "w") as f:
        f.write(index_content)
    print(f"Created/Updated category index at: {index_path}")

def process_category(category_path):
    """Process category folder and its artwork subfolders"""
    print(f"\nProcessing category: {category_path}")
    category_name = os.path.basename(category_path)
    
    # Process first artwork folder to get cover image
    cover_image = None
    for entry in sorted(os.listdir(category_path)):
        artwork_path = os.path.join(category_path, entry)
        if os.path.isdir(artwork_path) and not entry.startswith('.'):
            # Process artwork folder
            image = process_artwork_folder(artwork_path)
            if image and not cover_image:  # Use first found image as cover
                cover_image = image
                # Copy the image to category folder
                src_image_path = os.path.join(artwork_path, image)
                dst_image_path = os.path.join(category_path, image)
                if os.path.exists(src_image_path):
                    shutil.copy2(src_image_path, dst_image_path)
                    print(f"Copied cover image to category folder: {dst_image_path}")
    
    if cover_image:
        # Create/update category index with cover image
        create_category_index(category_path, category_name, cover_image)
    else:
        print(f"No cover image found for category: {category_name}")

def migrate():
    if os.path.exists(DST):
        print(f"Destination {DST} already exists. Remove it or choose another name.")
        return
    shutil.copytree(SRC, DST)

    for category in os.listdir(DST):
        cat_path = os.path.join(DST, category)
        if not os.path.isdir(cat_path):
            continue

        process_category(cat_path)

def main():
    # Base content directory
    content_dir = "legacy/migration_4/content"
    
    # Skip these directories
    skip_dirs = {'about', 'categories', 'tags', '.git', '.venv'}
    
    # Process each category
    for category in os.listdir(content_dir):
        category_path = os.path.join(content_dir, category)
        if os.path.isdir(category_path) and category not in skip_dirs and not category.startswith('.'):
            process_category(category_path)
            print(f"Completed processing category: {category}")

if __name__ == "__main__":
    print("Starting cleanup and category bundle creation process...")
    migrate()
    main()
    print("\nProcess completed!")
