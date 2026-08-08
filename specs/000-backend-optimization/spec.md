# Feature Specification: Backend & Build Optimization

**Feature Branch**: `worktree-backend-perf-plan` (PR #15)

**Created**: 2026-08-04 · **Backfilled**: 2026-08-06

**Status**: ⚠️ **RETROACTIVE** — implemented before this project adopted spec-driven development

**Input**: User description: "Without changing much of the front end, can any back end modifications
be done to make it much more faster, much more easier to maintain? Can you come up with a plan,
please?"

---

## Why this document is numbered 000

This feature shipped **without a spec**. The work was investigated, planned in
`docs/backend-optimization-plan.md`, implemented, and pushed as PR #15 before the project's SDD
scaffolding was adopted in `001-quality-gates`. The number `000` marks it as out-of-band: it
precedes the process rather than following it.

It is backfilled here because a shipped feature with no recorded intent cannot be reviewed,
revisited, or safely reversed — and because a process adopted in 001 that leaves the preceding work
undocumented is a process with a hole in it.

**This is a record, not a reconstruction.** Every number below was measured during the session on
2026-08-04/05, and the two conclusions that turned out to be wrong are recorded as wrong, with what
disproved them. Rewriting history into a clean narrative would defeat the purpose.

---

## Problem

The site was slow to build and heavy to deploy, and nothing was watching either. Measured baseline
(`main` @ `8d0cf6e`, Hugo 0.147.8 extended):

| Metric | Baseline |
| --- | --- |
| Artwork bundles | 46 (plus the `about` page = 47 bundles) |
| Source images | 48 files, **115.8 MB**, 2490–3900 px long edge |
| Images processed per build | 187 |
| Cold build (local) | **197.6 s** |
| Warm build (local) | 5.6 s |
| Build on GitHub Actions | **43.8 s on every deploy** — no cache persisted |
| Published site | **140 MB** |
| — full-resolution masters within it | **115.8 MB (83%)** |
| Repo tip tree (checked out every CI run) | **1497 MB**, of which `legacy/` = 1380 MB |
| Packed git history | 561 MB |
| Deploy success rate | 16/16 green |

Three structural causes:

1. **No CI cache for image variants.** Hugo caches them under the path set by `[caches.images]`
   (default `resources/_gen`), *not* `HUGO_CACHEDIR`. The workflow set `HUGO_CACHEDIR` and persisted
   nothing, so all 187 conversions re-ran on every deploy.
2. **Masters published for nothing.** 116 MB of originals shipped in every deploy.
3. **`legacy/` dominated the checkout.** Five near-identical WordPress→Hugo migration snapshots plus
   a 335 MB WordPress backup — 1380 MB that no build step reads, downloaded on every CI run.

Alongside these, maintenance had drifted: a stock archetype (so all artwork front matter was
hand-authored, and had diverged), a `Makefile` whose only target hardcoded an absolute
`/Users/...` path, a `.gitmodules` claiming a submodule for a vendored theme, and **no pull-request
validation of any kind**.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Deploys are fast and cheap (Priority: P1)

As the site owner, when I merge a change, the deploy completes quickly and ships only what visitors
need, so that adding a painting is not a two-hundred-second, hundred-megabyte event.

**Why this priority**: Largest measured waste, and fixable in configuration alone — no content or
markup risk.

**Independent Test**: Deploy twice; the second is materially faster and the published payload is a
fraction of its former size.

**Acceptance Scenarios**:

1. **Given** a deploy following a previous one, **When** CI builds, **Then** it reuses cached image
   variants instead of regenerating all 187.
2. **Given** a successful build, **When** the site is published, **Then** no full-resolution master
   is included.
3. **Given** the removal of `legacy/` from the tree, **When** CI checks out, **Then** it fetches
   roughly a tenth of what it did before.
4. **Given** any of the above, **When** pages render, **Then** they are visually identical to before.

---

### User Story 2 - The archive stays retrievable (Priority: P1)

As the site owner, I can still reach the old WordPress site and migration snapshots whenever I need
them, by a link rather than by remembering git incantations — even though they are no longer in the
working tree.

**Why this priority**: Ships with US1's checkout reduction; removing 1.38 GB is only acceptable if
retrieval is genuinely guaranteed.

**Independent Test**: Open a URL and browse the removed files; separately, restore them into a
working tree with one command.

**Acceptance Scenarios**:

1. **Given** `legacy/` is gone from the tree, **When** the archive URL is opened, **Then** the files
   are browsable, and this holds for an anonymous visitor.
2. **Given** a fresh clone, **When** the documented restore command is run, **Then** `legacy/`
   returns intact.
3. **Given** future branch activity, **When** the archive reference is resolved, **Then** it still
   works — it must not depend on a branch that may move or be deleted.
4. **Given** a contributor who has never seen this work, **When** they read the README, **Then** they
   can find the archive without knowing which doc to open.

---

### User Story 3 - Silent misconfiguration becomes visible (Priority: P2)

As the site owner, configuration that does nothing — or does the wrong thing quietly — is corrected
and documented, so the next reader is not misled the way the last one was.

**Why this priority**: Individually small, collectively the reason the repository was hard to reason
about. Lower than P1 because nothing here is on fire.

**Independent Test**: Read the config and CI cold; every declaration corresponds to something real.

**Acceptance Scenarios**:

1. **Given** front matter declaring an image resource, **When** that file does not exist, **Then**
   the discrepancy is corrected (Hugo will not report it).
2. **Given** CI, **When** a step does nothing (Dart Sass, `npm ci`, `submodules: recursive`),
   **Then** it is removed with the reason recorded.
3. **Given** the vendored theme, **When** a contributor considers editing it, **Then** its upstream,
   version, and every local modification are documented.
4. **Given** image quality settings, **When** defaults are wrong for an art gallery, **Then** they
   are set deliberately, with the measured trade-off stated.

---

### User Story 4 - Adding a painting is a documented, checked operation (Priority: P3)

As the artist's collaborator, I can scaffold a new artwork and have obvious mistakes caught before
they reach production, instead of copying an existing directory and hoping.

**Why this priority**: Real, but the sharper version of it became `001-quality-gates`; this story is
the first step only.

**Acceptance Scenarios**:

1. **Given** a new artwork, **When** it is scaffolded, **Then** the front matter shape is correct by
   construction.
2. **Given** a pull request, **When** it is opened, **Then** something validates it — previously
   nothing did.
3. **Given** an invalid resource declaration, **When** validation runs, **Then** it fails and names
   the file.

## Requirements *(mandatory)*

### Functional

- **FR-001**: CI persists Hugo's processed-image cache across runs, keyed on image content and
  config.
- **FR-002**: Full-resolution masters are not copied into the published site.
- **FR-003**: `legacy/` is removed from the working tree with a permanent, browsable retrieval path;
  no history rewrite and no force-push.
- **FR-004**: `hugo.toml` sets image quality/resampling deliberately, raises the render timeout above
  the 60 s default, strips EXIF GPS, and declares a minimum Hugo version.
- **FR-005**: Front-matter resource declarations that name absent files are corrected; caption format
  is normalised to one documented form.
- **FR-006**: CI steps that have no effect are removed.
- **FR-007**: The vendored theme records upstream, version, and local modifications.
- **FR-008**: A pull-request workflow validates changes before merge.
- **FR-009**: `make` exposes the real commands; the archetype scaffolds real artwork front matter.
- **FR-010**: Inline `<style>` moves into the compiled stylesheet without changing rendering.

### Non-functional

- **NFR-001**: **The front end does not change.** Rendered pages must be visually identical, and this
  must be demonstrated rather than asserted.
- **NFR-002**: Every performance claim carries its measurement and method.
- **NFR-003**: No destructive git operation: no force-push, no history rewrite, nothing unrecoverable.
- **NFR-004**: Artist-authored content is never invented — not a painting's dimensions, not her copy,
  not her choice of units.

## Success Criteria

- **SC-001**: Deploy build time falls by an order of magnitude. → **43.8 s → 0.35 s** on GitHub
  Actions (verified across three real runs); 197.6 s → 3.0 s locally.
- **SC-002**: Published payload falls substantially. → **140 MB → 28 MB**.
- **SC-003**: CI checkout falls substantially. → tip tree **1497 MB → 118 MB**.
- **SC-004**: Rendered output is unchanged. → HTML diffed before/after: the **only** difference on an
  artwork page is the removed inline `<style>` block; all other markup byte-identical after
  normalising content hashes. Inline `<style>` blocks 47 → 0.
- **SC-005**: The archive is retrievable by link. → tag `legacy-archive` at
  `8d0cf6e376da7eb0e482d328cda45b472408ef6b`; 14 documented URLs verified HTTP 200 anonymously;
  restore verified from a fresh fetch.
- **SC-006**: One behavioural change, understood and stated. → PhotoSwipe's download button is hidden
  (`enableDownload` true→false, a single bit in the built JS). It served the 1600 px variant, never a
  master.

## Decisions and rejected alternatives

Recorded because the rejections carry as much information as the changes:

| Considered | Outcome | Evidence |
| --- | --- | --- |
| WebP/AVIF conversion | **Rejected** | `Olive.jpg` at 1600 px: **665 KB WebP vs 568 KB JPEG** — larger for this dense brushwork. Theme also warns of level shifts on resize. |
| Downscale masters to 2000 px | **Rejected** | Would cut sources 115.8 → 24.9 MB, but the delivered 1600 px image measured **32.2 dB (q85) / 34.2 (q92) / 35.1 (q95)** PSNR against today's — visible on fine detail. CI caching already removed the build-time motive. Masters untouched. |
| Raise `imaging.quality` | **Accepted (82)** | Default q75 measured **30.1 dB** against q92 — the site's largest fidelity deficit, larger than downscaling would have cost. Price: ~+2.5 MB across the variant set. |
| Drop the RSS feed | **Rejected** | Worth 25% of image conversions (46 of 187, the 900×600 fills) but user-visible and not requested. |
| Rewrite git history | **Rejected** | Would cut the 561 MB pack to ~50 MB, but needs a force-push and re-clones. Removing `legacy/` from the tip fixed CI and shallow clones without it. |
| Archive `legacy/` elsewhere | **Superseded** | Owner chose a git-history reference; implemented as tag + browsable links. |

## Corrections — claims that were wrong

Both were disproved by inspecting build output, and both are recorded because the *method* is the
lesson (Constitution Principle II, which this work is the origin of):

1. **"The grid links full-resolution masters, so disabling them removes a download feature."**
   **Wrong.** Grepping built HTML found **zero** non-derived image references across all 61 pages.
   The `gallery-item` grid branch of `gallery.html` never executes on this site — the home page
   renders via `home.html` → `album-card.html` and there are no image-bearing section lists. The
   masters were reachable only by guessing a URL.
2. **"Setting `params.author` is a free SEO win."** **Wrong.** Its only consumer is that same
   never-rendered branch; built HTML contains zero `itemprop=creator` both before and after. The
   setting is kept as correct metadata but is inert.

A third correction of record: the baseline was described as "47 artworks". It is **46 artworks plus
the `about` page**. Corrected in `docs/backend-optimization-plan.md` as part of this backfill.

## Out of Scope

- Front-end/design change of any kind (NFR-001).
- Reducing the 561 MB packed history (needs a force-push).
- Automated testing — deliberately deferred, and delivered as
  [`001-quality-gates`](../001-quality-gates/spec.md).
- Resolving content gaps: 3 artworks without `dimensions`, 2 with empty `description`, 2 in inches.
  These need the artist (NFR-004).
