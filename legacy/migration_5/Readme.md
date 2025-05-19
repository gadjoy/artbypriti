
# Art by Priti - Content Structure and Hugo Setup

## Content Flattening

- The content directory was restructured to flatten all artwork folders directly under `content/`, removing the previous category-based subfolders (except for `about/`).
- This makes content management simpler and allows for easier referencing and linking.
- The original `categories` field in each content file's front matter is preserved, so Hugo can still group and display content by category.

## Hugo Taxonomy for Categories

- Hugo's taxonomy system is used to generate category pages for each artwork category.
- The following was added to `hugo.toml` to enable this:

  ```toml
  [taxonomies]
    category = "categories"
  ```

- This allows each content file to be associated with one or more categories, and for Hugo to generate pages like `/categories/<category>/` listing all content in that category.

## Hiding the /categories/ Index Page

- To prevent the blank or unwanted `/categories/` index page from appearing, an empty template was created at `themes/gallery/layouts/_default/terms.html`:

  ```go
  {{/* Empty template to hide taxonomy terms page */}}
  ```

- This ensures that while category links work and show the correct content, the top-level `/categories/` page is hidden from users.

## Menu Update

- The categories page was removed from the site menu to avoid navigation to the now-hidden `/categories/` index.

## Summary

- Content is now flat for easier management.
- Categories are preserved and used for grouping via Hugo taxonomy.
- The `/categories/` index page is hidden for a cleaner user experience. 