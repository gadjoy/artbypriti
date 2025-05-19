
Ran tool

Read file: legacy/migration/content/posts/apple-with-dots.md

Ran tool

Ran tool

Ran tool
Here’s what we’ll do for the grouping and migration, as you requested:

**Goal:**  
- Move `apple-with-dots.md` and its images into `clarity/content/acrylic-on-canvas/apple-with-dots/index.md` and the images in the same folder.
- Update the markdown so all image references are local (i.e., just the filename).
- Keep the rest of the content unchanged.

---

### **Steps (Script/Manual):**

1. **Create the folder structure:**
   ```
   clarity/content/acrylic-on-canvas/apple-with-dots/
   ```

2. **Move/copy the markdown file:**
   - Rename `apple-with-dots.md` to `index.md` and place it in the new folder.

3. **Move/copy all relevant images:**
   - All files matching `Apple-with-dots*` from `legacy/migration/static/images/2021/02/` to the new folder.

4. **Update image references in `index.md`:**
   - Change `![](../../static/images/2021/02/Apple-with-dots.jpg)` to `![](Apple-with-dots.jpg)`

---

### **Resulting Structure:**
```
clarity/
  content/
    acrylic-on-canvas/
      apple-with-dots/
        index.md
        Apple-with-dots.jpg
        Apple-with-dots-150x150.jpg
        Apple-with-dots-300x297.jpg
        Apple-with-dots-768x761.jpg
        Apple-with-dots-1024x1015.jpg
        Apple-with-dots-1200x1190.jpg
        Apple-with-dots-1536x1523.jpg
        Apple-with-dots-1980x1963.jpg
        Apple-with-dots-2048x2031.jpg
```

---

### **Updated `index.md`:**
```markdown
---
title: "Apple with Dots"
date: 2021-02-21
draft: false
categories: [Acrylic on Canvas]
---

![](Apple-with-dots.jpg)

(15 cm X 15 cm)

Our house in Bangalore has a staircase behind the dining table and the empty blocks of the steps called out to be filled. They inspired me to fill them up with one small canvas on each step. Given the location - the subjects had to be food inspired!
```

---

Would you like a bash script for this, or is this step-by-step guide sufficient for you to proceed manually?
