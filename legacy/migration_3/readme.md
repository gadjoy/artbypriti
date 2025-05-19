Absolutely! Here’s what you want to do for migration_3:

**Goal:**  
For each `index.md` in migration_2, update the image reference from a markdown image (e.g., `![](OM-with-Bandhani-1.jpg)`) to a Hugo resources block like:

```yaml
resources:
  - src: OM-with-Bandhani-1.jpg
    title: (51 cm X 41 cm)
```

And move the image description (currently below the image) to a `description` field.

---

### Migration Steps

For each `index.md`:
1. Find the first image markdown line: `![](image.jpg)`
2. Extract the image filename.
3. Extract the next line as the description.
4. Remove the image markdown line from the content.
5. Add/replace a `resources:` block in the front matter (YAML) with the image filename and the size (if available).
6. Add a `description:` field in the front matter with the description.

---

### Example Transformation

**Before:**
```markdown
---
title: "OM with Bandhani"
date: 2021-02-21
draft: false
categories: [Acrylic and Fabric on Canvas]
---

![](OM-with-Bandhani-1.jpg)

(51 cm X 41 cm)

The textured figure of OM - the original vibration - emerging from the purple void
```

**After:**
```markdown
---
title: "OM with Bandhani"
date: 2021-02-21
draft: false
categories: [Acrylic and Fabric on Canvas]
resources:
  - src: OM-with-Bandhani-1.jpg
    title: (51 cm X 41 cm)
description: The textured figure of OM - the original vibration - emerging from the purple void
---

```

---

### Migration Script

Here’s a Python script to automate this for all `index.md` files in `legacy/migration_2`, writing the results to `legacy/migration_3`:

```python
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
```

---

**How to use:**
1. Save this as `migrate_images.py` (or similar).
2. Run it: `python3 migrate_images.py`
3. It will create `legacy/migration_3` with updated `index.md` files.

Let me know if you want to handle multiple images per file, or if you want to tweak the logic!
