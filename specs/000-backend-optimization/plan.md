# Implementation Plan: Backend & Build Optimization

**Branch**: `worktree-backend-perf-plan` (PR #15) | **Date**: 2026-08-04 | **Backfilled**: 2026-08-06
| **Spec**: [spec.md](./spec.md)

**Status**: ⚠️ **RETROACTIVE** — records the plan that was actually followed, from
`docs/backend-optimization-plan.md` and the session that produced it.

## Summary

Cut build time, deploy payload, and maintenance overhead on a Hugo gallery **without changing the
front end**. Investigation first (measure where time and bytes actually go), then configuration-only
changes ahead of anything touching content, with rendered output diffed before and after to prove
appearance is unchanged.

The long-form narrative version — with the full baseline tables and the sequencing rationale — is
`docs/backend-optimization-plan.md`. That document was written *as* the plan; this file states it in
spec-kit terms and records how it turned out.

## Technical Context

**Language/Version**: Hugo Extended 0.147.8 (CI had drifted to 0.128.0); Python 3.8 stdlib for the
validator; no application code

**Primary Dependencies**: `hugo-theme-gallery` v4.9.0, vendored

**Storage**: N/A — static site, images as page-bundle resources

**Testing**: None at the time. Verification was manual HTML diffing plus measured timings, which is
precisely the weakness that motivated `001-quality-gates`

**Target Platform**: GitHub Pages via GitHub Actions `ubuntu-latest`

**Project Type**: Hugo static site

**Performance Goals**: order-of-magnitude faster deploys; substantially smaller payload

**Constraints**: rendered pages visually identical; no force-push; no history rewrite; nothing
unrecoverable

**Scale/Scope**: 46 artworks, 48 source images (115.8 MB), 187 processed variants, 61 built pages

## Constitution Check

The constitution did not exist yet — it was written in `001-quality-gates`, **derived from this
work**. Checking retroactively:

| Principle | Verdict |
| --- | --- |
| I — a green build is not evidence | **Originates here.** 16/16 green deploys had hidden 3 broken declarations for ~15 months. |
| II — the rendered page is the contract | **Originates here.** Two template-based conclusions were disproved by grepping built HTML. Complied with, eventually — by correcting the claims rather than defending them. |
| III — structural fails, content warns | Complied: the validator errors on broken declarations, warns on missing dimensions/descriptions. |
| IV — performance is a budget | **Originates here.** The 40 MB / 15 s budgets were set from these measurements. |
| V — vendored deps declare themselves | Complied: `themes/gallery/UPSTREAM.md` created, misleading `.gitmodules` removed. |

No retroactive violations. The one process violation is structural and is the reason this document
exists: **the work shipped with no spec.**

## Technical decisions

### Measure before changing anything

Roughly half the session was investigation: timing cold and warm builds, attributing all 187 image
variants to their consumers, sizing the tip tree per directory, dating each latent defect with
`git log -S`. Two headline conclusions inverted once measured — WebP turned out *larger* than JPEG
here, and downscaling masters turned out unnecessary because caching removed its motive. Neither
inversion was predictable from reading.

### Sequencing: configuration before content

Ordered by risk, not by size of win: CI caching and dead-step removal (no content touched), then
config, then content-affecting changes, then the `legacy/` removal that rewrites the tree. Each step
independently revertible.

### Proving "the front end does not change"

The only available method at the time: build before and after, normalise content hashes and image
dimensions, diff every one of the 61 pages, and inspect the compiled JS for behavioural deltas. That
found the single intended behaviour change (`enableDownload` true→false) and confirmed everything
else identical. It also demonstrated why this needed automating — `001-quality-gates` replaced this
manual procedure with screenshots.

### Archive by reference rather than by copy

The owner's decision. Implemented as an annotated tag (`legacy-archive`) plus browsable GitHub URLs,
so the reference cannot rot with branch movement, and verified as HTTP 200 for an anonymous visitor.
Rejected: a separate repository or release attachment, both of which add a second thing to maintain.

## Project Structure

```
.github/workflows/hugo.yml    # cache image variants; drop dart-sass, npm, submodules steps
.github/workflows/pr-check.yml # NEW — first pre-merge validation this repo ever had
hugo.toml                     # quality 82 + CatmullRom, timeout 180s, caches.images, EXIF, robots
content/_index.md             # publishResources cascade; corrected cover declaration
content/about/index.md        # corrected portrait filename
content/<5 artworks>/index.md # corrected declaration + normalised captions
layouts/partials/gallery.html # inline <style> removed
assets/css/custom.css         # those rules, verbatim
archetypes/default.md         # real artwork front matter
Makefile                      # real targets, replacing a hardcoded /Users path
scripts/check-content.py      # NEW — front-matter validation
themes/gallery/UPSTREAM.md    # NEW — vendored provenance + 5 local modifications
docs/backend-optimization-plan.md  # NEW — the measured plan
docs/legacy-archive.md        # NEW — archive links, inventory, restore commands
legacy/                       # REMOVED from the tree (1477 files, 1380 MB)
.gitmodules                   # REMOVED — claimed a submodule for a vendored theme
```

## Phasing

As implemented, in this order:

1. **CI cache + dead-step removal** — pure win, no content touched, makes every later step's CI fast.
2. **Config hardening** — `hugo.toml`, plus the two dead resource declarations.
3. **Content correctness** — the third broken declaration and caption normalisation.
4. **Stop publishing masters** — needed the owner's decision on downloads.
5. **Remove `legacy/`** — after the archive reference existed and was verified.
6. **Tooling and provenance** — validator, PR check, Makefile, archetype, `UPSTREAM.md`.
7. **CSS consolidation** — last, because it is the only change touching rendering machinery.

## Verification approach

| Claim | How it was verified |
| --- | --- |
| Build time | `/usr/bin/time` on cold and warm builds locally; three real GitHub Actions runs |
| Payload | `du` on `public/`, plus a per-variant attribution of all 187 images |
| Front end unchanged | Normalised HTML diff of all 61 pages, before vs after |
| Behaviour change | Diff of the compiled JS bundle (one bit: `enableDownload`) |
| Archive retrievable | `curl` on 14 URLs anonymously; restore from a fresh `git fetch` |
| Masters unreferenced | Grep of built HTML for non-derived image references (found 0) |

**Known weakness of this approach**: every check above was a one-off, run by hand. None of it would
catch a regression tomorrow. That gap is the whole subject of `001-quality-gates`.
