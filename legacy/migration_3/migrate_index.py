import os
import re
import shutil
from pathlib import Path

SRC = "legacy/migration_2"
DST = "legacy/migration_3"

def migrate_index_md(src_path, dst_path):
    with open(src_path, "r") as f:
        lines = f.readlines()

    # Find front matter
    if lines[0].strip() != "---":
        print(f"Skipping {src_path}: no front matter")
        return

    # Find end of front matter
    end_fm = 1
    while end_fm < len(lines) and lines[end_fm].strip() != "---":
        end_fm += 1
    end_fm += 1  # include the closing ---

    front_matter = lines[:end_fm]
    body = lines[end_fm:]

    # Find image markdown and description
    img_line_idx = next((i for i, l in enumerate(body) if l.strip().startswith("![](")), None)
    if img_line_idx is None:
        # No image, just copy as is
        shutil.copy2(src_path, dst_path)
        return

    img_line = body[img_line_idx]
    img_filename = re.search(r"!\[\]\((.*?)\)", img_line).group(1)

    # Next non-empty line after image is likely the size
    size_line_idx = img_line_idx + 1
    while size_line_idx < len(body) and not body[size_line_idx].strip():
        size_line_idx += 1
    size_line = body[size_line_idx].strip() if size_line_idx < len(body) else ""

    # Next non-empty line after size is the description
    desc_line_idx = size_line_idx + 1
    while desc_line_idx < len(body) and not body[desc_line_idx].strip():
        desc_line_idx += 1
    desc_line = body[desc_line_idx].strip() if desc_line_idx < len(body) else ""

    # Remove image, size, and description lines from body
    new_body = [l for i, l in enumerate(body) if i not in (img_line_idx, size_line_idx, desc_line_idx)]

    # Add resources and description to front matter
    # Insert before the closing '---'
    fm_insert_idx = len(front_matter) - 1
    front_matter.insert(fm_insert_idx, f"resources:\n  - src: {img_filename}\n    title: {size_line}\n")
    front_matter.insert(fm_insert_idx, f"description: {desc_line}\n")

    # Write new file
    with open(dst_path, "w") as f:
        f.writelines(front_matter)
        f.writelines(new_body)

def migrate_all():
    if os.path.exists(DST):
        print(f"Destination {DST} already exists. Remove it or choose another name.")
        return
    shutil.copytree(SRC, DST)
    for root, dirs, files in os.walk(DST):
        for file in files:
            if file == "index.md":
                src_md = os.path.join(root, file)
                migrate_index_md(src_md, src_md)
    print("Migration complete.")

if __name__ == "__main__":
    migrate_all()
