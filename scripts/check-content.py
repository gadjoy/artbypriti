#!/usr/bin/env python3
"""Validate artwork front matter before it reaches production.

Hugo is forgiving: a resource declaration naming a file that does not exist, or a
missing caption field, produces no warning at all — it silently renders something
slightly wrong. Two such declarations sat broken in this repo for months. This
script makes those cases loud.

Usage:  python3 scripts/check-content.py [content_dir]
Exit:   0 = clean (warnings allowed), 1 = errors found
"""

import os
import re
import sys

# Canonical caption format, e.g. "(92 cm X 61 cm)" or "(46 cm Diameter)".
DIMENSIONS_RE = re.compile(r"^\(.+\)$")
IMAGE_EXTS = (".jpg", ".jpeg", ".png")
# Bundles that are pages, not artworks, and so are exempt from artwork rules.
NON_ARTWORK = {"about"}

errors = []
warnings = []


def split_front_matter(text, path):
    """Return the YAML front-matter block, or None if absent/unterminated."""
    if not text.startswith("---"):
        errors.append(f"{path}: no YAML front matter (must start with '---')")
        return None
    end = text.find("\n---", 3)
    if end == -1:
        errors.append(f"{path}: front matter is not terminated")
        return None
    return text[3:end]


def scalar(block, key):
    """Read a top-level scalar key. Deliberately line-based: no YAML dependency,
    so this runs anywhere python3 does."""
    m = re.search(rf"^{key}:[ \t]*(.*)$", block, re.MULTILINE)
    if not m:
        return None
    return m.group(1).strip().strip("\"'") or None


def declared_resources(block):
    """Collect 'src:' values from the resources list."""
    m = re.search(r"^resources:[ \t]*$(.*?)(?=^\S)", block + "\n\x00", re.MULTILINE | re.DOTALL)
    if not m:
        return []
    return [s.strip().strip("\"'") for s in re.findall(r"^\s*-?\s*src:[ \t]*(.+)$", m.group(1), re.MULTILINE)]


def check_bundle(d, name):
    index = os.path.join(d, "index.md")
    rel = os.path.relpath(index)
    with open(index, encoding="utf-8") as fh:
        block = split_front_matter(fh.read(), rel)
    if block is None:
        return

    images_on_disk = sorted(f for f in os.listdir(d) if f.lower().endswith(IMAGE_EXTS))

    # Every declared resource must actually exist — the check that would have caught
    # both historical bugs (content/_index.md and content/about/index.md).
    for src in declared_resources(block):
        if src and src not in os.listdir(d):
            errors.append(
                f"{rel}: declares resource '{src}' but that file is not in the bundle"
                + (f" (found: {', '.join(images_on_disk)})" if images_on_disk else "")
            )

    if not images_on_disk:
        errors.append(f"{rel}: page bundle contains no image")

    if name in NON_ARTWORK:
        return

    for key in ("title", "date", "categories"):
        if not scalar(block, key):
            errors.append(f"{rel}: missing or empty '{key}'")

    # A warning, not an error: only the artist can write this copy, so a missing one
    # must not be able to block a deploy.
    if not scalar(block, "description"):
        warnings.append(f"{rel}: empty 'description' — no subtext will render under the title")

    if not declared_resources(block):
        warnings.append(f"{rel}: no 'resources:' declaration (Hugo will pick an image implicitly)")

    dims = scalar(block, "dimensions")
    if not dims:
        warnings.append(f"{rel}: no 'dimensions' — the size caption will be absent on this page")
    else:
        if not DIMENSIONS_RE.match(dims):
            errors.append(f"{rel}: dimensions {dims!r} should be wrapped in parentheses, e.g. '(92 cm X 61 cm)'")
        if re.search(r"\bx\b", dims):
            errors.append(f"{rel}: dimensions {dims!r} uses a lowercase 'x' separator; use 'X'")
        if '"' in dims or "inch" in dims.lower():
            warnings.append(f"{rel}: dimensions {dims!r} are in inches while the rest of the site uses cm")


def check_branch_bundle(root):
    """Validate content/_index.md — the home page.

    A branch bundle's resources must be files sitting in the same directory. Naming a file
    that lives inside a child bundle matches nothing, and Hugo answers by silently falling
    back to another image. That is exactly how the home page's OpenGraph card pointed at the
    wrong file for ~15 months, so it needs its own check: the loop over content/*/index.md
    never looks at this file.
    """
    index = os.path.join(root, "_index.md")
    if not os.path.isfile(index):
        warnings.append(f"{index}: no home page front matter found")
        return
    rel = os.path.relpath(index)
    with open(index, encoding="utf-8") as fh:
        block = split_front_matter(fh.read(), rel)
    if block is None:
        return

    here = set(os.listdir(root))
    for src in declared_resources(block):
        if not src or src in here:
            continue
        # Point at the likely intent rather than just refusing.
        elsewhere = [
            os.path.join(d, src)
            for d in sorted(os.listdir(root))
            if os.path.isdir(os.path.join(root, d)) and src in os.listdir(os.path.join(root, d))
        ]
        hint = (
            f" — it is in {elsewhere[0]}, but a branch bundle can only use files in {root}/"
            if elsewhere
            else ""
        )
        errors.append(f"{rel}: declares resource '{src}' which is not in {root}/{hint}")


def main():
    root = sys.argv[1] if len(sys.argv) > 1 else "content"
    if not os.path.isdir(root):
        print(f"error: no such directory: {root}", file=sys.stderr)
        return 1

    check_branch_bundle(root)

    bundles = sorted(
        (os.path.join(root, n), n)
        for n in os.listdir(root)
        if os.path.isfile(os.path.join(root, n, "index.md"))
    )
    for d, name in bundles:
        check_bundle(d, name)

    for w in warnings:
        print(f"warning: {w}")
    for e in errors:
        print(f"ERROR:   {e}")

    print(f"\nchecked {len(bundles)} page bundles: {len(errors)} error(s), {len(warnings)} warning(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
