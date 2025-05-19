### 1. Category `_index.md` Generation
- For each category (e.g., `acrylic-and-fabric-on-canvas`), create a `_index.md` file in the category folder.
- The `_index.md` should have:
  - A `description` generated from the category title (e.g., "Acrylic and fabric on canvas" → "These paintings are examples of Acrylic and fabric on canvas.").
  - A `title` field set to the category name in a human-readable format.
  - A `resources` block containing a single image:
    - This image is the one referenced in the `index.md` of the first (or only) artwork subfolder in that category.

### 2. Image Cleanup in Artwork Folders
- For each artwork folder (e.g., `acrylic-and-fabric-on-canvas/om-with-bandhani`):
  - Read the `index.md` to find the image(s) referenced (e.g., `![](OM-with-Bandhani-1.jpg)`).
  - Keep only the image(s) referenced in the `index.md`.
  - Remove all other images from that folder.

### 3. Folder Structure
- The structure of migration_4 should mirror migration_3, but with the above changes applied.

---

**Summary of the process:**
- For each category, create a `_index.md` with a generated description and a cover image (from one of its artworks).
- For each artwork, keep only the images referenced in its `index.md`.
- Remove all other images from artwork folders.

---

**Next Steps:**
- I’ll write a script to automate this process.
- The script will:
  1. Copy migration_3 to migration_4.
  2. For each category, generate `_index.md` as described.
  3. For each artwork, clean up images as described.

Is this understanding correct?  
Would you like the description to be a simple template like:  
“These paintings are examples of {category title}.”  
or do you want a different phrasing?

Let me know if you want to tweak any part of this plan before I provide the script!
