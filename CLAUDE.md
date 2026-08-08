# Art by Priti — contributor & agent guide

> **Read [`.specify/memory/constitution.md`](.specify/memory/constitution.md).** Four
> principles, deliberately short — they match how this project can actually break.

Hugo portfolio site for the artist Priti, deployed to **GitHub Pages on merge to `main`**.
Machine-wide engineering principles are in `~/.claude/CLAUDE.md` and apply here too.

This file replaces a Spec Kit placeholder that said only "read the current plan"; the
constitution beside it was a template with 18 unfilled placeholders, which read as though
rules existed when none did.

## The four, in one line each

1. **The live site is someone's portfolio** — merging deploys, so `main` must always build.
2. **Images are the product** — never re-encode or rename artwork unasked; a missing image
   is the most damaging failure here.
3. **URLs that exist must keep existing** — gallery links outlive redesigns; add an alias
   rather than breaking one.
4. **Respect the size constraints** — no Git LFS, so GitHub's **100 MB per-file limit is a
   hard wall**.

## Commands

```bash
hugo             # must succeed — merging to main deploys to GitHub Pages
hugo server -D   # local preview; actually LOOK at the pages you changed
```

There is **no test suite**. A green build proves the templates parsed — not that a gallery
renders, an image resolved, or a link works. Open the pages you touched.

## The size trap, because it will catch you

`.git` is ~567 MB: the artwork plus a legacy WordPress backup live in this repo, and there
is no LFS. The backup is stored as **99 MB chunks** precisely because GitHub rejects files
over 100 MB — see
[`docs/linux-file-split-and-merge-guide.md`](docs/linux-file-split-and-merge-guide.md).

- Do not commit a file over 100 MB. Split it, or keep it out of the repo.
- Do not rewrite history to reclaim space. It would invalidate every existing clone in
  exchange for disk that costs nothing.
- Expect clones and CI checkouts to be slow. That is the accepted trade for keeping the
  artwork versioned alongside the site.

## Layout

- `content/` — the galleries; **the source of truth** (~117 MB)
- `layouts/`, `assets/`, `static/`, `themes/` — Hugo site (Gallery theme)
- `legacy/` — the WordPress era: split backup chunks and earlier migrations. **Reference
  only; never a source for the live site.**
- `docs/` — deployment notes, the file split/merge guide, SSG evaluation
- `.github/workflows/hugo.yml` — build + deploy to Pages

## Working here

Changes land through a reviewed PR. Keep changes proportionate: this is a small static
site for one person, and ceremony that would be right for a service with a database is
overhead here. The constitution is four principles for that reason — if a rule stops
matching how the project breaks, delete it rather than leaving a rule that teaches people
rules are optional.
