#!/bin/bash

SRC_MD_DIR="legacy/migration/content/posts"
SRC_IMG_ROOT="legacy/migration/static/images"
DEST_ROOT="clarity/content"
LOG_FILE="migration_errors.log"

mkdir -p "$DEST_ROOT"
> "$LOG_FILE"  # Clear log file at start

for mdfile in "$SRC_MD_DIR"/*.md; do
  # Extract slug and category
  SLUG=$(basename "$mdfile" .md)
  CATEGORY=$(grep '^categories:' "$mdfile" | sed 's/categories: \[\(.*\)\]/\1/' | tr -d '"' | tr '[:upper:]' '[:lower:]' | tr ' ' '-')
  DEST_DIR="$DEST_ROOT/$CATEGORY/$SLUG"
  mkdir -p "$DEST_DIR"

  # Find and copy images recursively matching the slug (case-insensitive, allow underscores/dashes)
  IMG_FOUND=0
  find "$SRC_IMG_ROOT" -type f \( -iname "*${SLUG//-/_}*" -o -iname "*${SLUG//_/-}*" -o -iname "*${SLUG}*" \) | while read -r img; do
    cp "$img" "$DEST_DIR/"
    IMG_FOUND=1
  done

  # Log warning if no images found
  if [ $(ls -1q "$DEST_DIR" | grep -v index.md | wc -l) -eq 0 ]; then
    echo "ERROR: No images found for $SLUG ($mdfile)" >> "$LOG_FILE"
  fi

  # Update all image references in markdown to just the filename (robust for any path)
  # Use perl for cross-platform compatibility and correct markdown matching
  perl -pe 's|!\[\]\([^)]*/([^/]+)\)|![](\1)|g' "$mdfile" > "$DEST_DIR/index.md"

  echo "Migrated $SLUG to $DEST_DIR"
done

echo "Migration complete! Errors (if any) are logged in $LOG_FILE"
