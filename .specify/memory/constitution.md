# Art by Priti Constitution

A Hugo portfolio showing one artist's work, deployed to GitHub Pages. Small project,
so this is deliberately short: four principles, no invented ceremony. A constitution
listing rules nobody follows is worse than none.

## Core Principles

### I. The live site is someone's portfolio (NON-NEGOTIABLE)

This is a working artist's public presence, not a sandbox. Merging to `main` deploys
automatically, so **`main` must always build**. Verify `hugo` succeeds locally before
opening a PR; a broken build takes the whole site down, not one page.

### II. Images are the product

The artwork is the reason the site exists. Therefore:

- Never re-encode, crop or "optimise" an existing image without being asked. Colour and
  detail are the work itself, and a lossy pass is not reversible.
- Every image referenced in content must exist on disk with the correct path. A missing
  image renders as a broken box on a portfolio — the single most damaging failure here.
- Keep image filenames stable; they appear in URLs and in links people have shared.

### III. URLs that exist must keep existing

Galleries get linked from social posts, messages and email signatures, and those links
outlive any redesign. Changing a slug or a collection name breaks them permanently.

If a path must change, add an alias so the old URL still resolves. Deleting a page is a
deliberate decision, not a side effect of reorganising.

### IV. Respect the repository's size constraints

The repo is large (~567 MB of history) because the artwork and a legacy WordPress backup
live in it. There is no Git LFS, so **GitHub's 100 MB per-file limit is a hard wall.**

The WordPress backup is stored as 99 MB chunks for exactly this reason — see
[`docs/linux-file-split-and-merge-guide.md`](../../docs/linux-file-split-and-merge-guide.md).
Do not commit a file over 100 MB; split it or leave it out. Do not "tidy up" history to
reclaim space — rewriting this history would invalidate every existing clone for the sake
of disk that costs nothing.

## Development Workflow

Changes land through a reviewed PR. Before opening one:

```bash
hugo            # must succeed — merging deploys
hugo server -D  # check the pages you touched actually render
```

Look at the rendered pages, not just the exit code. This site has no test suite; the
build succeeding proves the templates parsed, not that a gallery looks right or an image
resolved.

## Governance

These four exist because they match how this project can actually break: a failed build
taking the site down, a lost or mangled image, a dead link, or a file too large to push.

Amendments happen in the same PR as the change that motivated them, with the reason
stated. If a principle here is being routinely ignored, delete it rather than leaving a
rule that teaches people rules are optional.

**Version**: 1.0.0 | **Ratified**: 2026-08-08 | **Last Amended**: 2026-08-08
