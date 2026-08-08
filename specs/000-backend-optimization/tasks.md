# Tasks: Backend & Build Optimization

**Branch**: `worktree-backend-perf-plan` (PR #15) | **Spec**: [spec.md](./spec.md) |
**Plan**: [plan.md](./plan.md)

**Status**: ⚠️ **RETROACTIVE** — reconstructed from the commits actually pushed, not from a task list
written in advance. Each task cites its commit so the record is checkable rather than merely
plausible.

## Phase 0 — Investigation (US1–US4)

- [x] **T001** Measure the baseline: cold/warm build times, per-variant image attribution, payload
      composition, tip-tree size per directory. → `3204605`
- [x] **T002** Date each latent defect with `git log -S`. *Found three broken resource declarations
      and the CI cache miss, all introduced 2025-04/05 — roughly 15 months in production behind 16
      green deploys. This measurement is what reframed the whole task from "make it faster" to "the
      pipeline cannot see defects".*
- [x] **T003** Test WebP/AVIF rather than assume. *Rejected: 665 KB WebP vs 568 KB JPEG at 1600 px.*
- [x] **T004** Test downscaling masters rather than assume. *Rejected: 32.2–35.1 dB PSNR on the
      delivered image; caching had already removed the build-time motive.*
- [x] **T005** Write the measured plan with sequencing and open decisions. → `3204605`

## Phase 1 — CI (US1, P1)

- [x] **T006** Persist Hugo's image-variant cache in CI, keyed on image content + config, with a
      `restore-keys` fallback so adding one painting reuses the rest. → `d78f6d7`
- [x] **T007** Remove the Dart Sass step. *Verified unnecessary first: the theme's SCSS compiled with
      no dart-sass installed, via Hugo Extended's bundled LibSass.* → `d78f6d7`
- [x] **T008** Remove the no-op `npm ci` guard and `submodules: recursive`. → `d78f6d7`, `155946c`
- [x] **T009** Align `HUGO_VERSION` with the version in use (0.128.0 → 0.147.8). → `d78f6d7`
- [x] **T010** Verify on real CI. *Three runs: 43.8 s cold → 0.35 s restored. First two runs missed
      the cache; diagnosed as GitHub scoping caches by ref, not a bad key — documented in both
      workflows so it is not mistaken for a fault.* → `e0c829b`

## Phase 2 — Configuration (US3, P2)

- [x] **T011** `hugo.toml`: quality 82 + CatmullRom, `timeout` 180 s, `[caches.images]`,
      `disableLatLong`, `enableRobotsTXT`, `hugoVersion` floor. → `abde87d`
- [x] **T012** Verify the quality trade-off before choosing 82. *q75 measured 30.1 dB against q92;
      cost ~+2.5 MB across the variant set.* → `abde87d`
- [x] **T013** Confirm the site emits zero Hugo warnings, so strictness could be added later without
      landing red. → verified during `abde87d`
- [x] **T014** Fix the home cover declaration (named a file inside a child bundle) and the `about`
      portrait filename. → `abde87d`

## Phase 3 — Content correctness (US3, US4)

- [x] **T015** Fix `ganeshas-blessings` (`.jpg` declared, `.jpeg` on disk). *Found by the validator
      built in T021 — not by reading the file, which I had already done twice.* → `8c0bb3c`
- [x] **T016** Normalise size captions to `(W cm X H cm)` across five files. **Deliberately did not**
      convert the two inch-based measurements: that changes what visitors read and is the artist's
      call (NFR-004). → `8c0bb3c`

## Phase 4 — Payload (US1, P1)

- [x] **T017** Enable the `publishResources: false` cascade already present, commented out, in
      `content/_index.md`. → `cf1ae6e`
- [x] **T018** Verify the payload drop and that no master ships. *140 MB → 28 MB; 0 non-derived
      images published.* → `cf1ae6e`
- [x] **T019** Establish what actually changed for visitors. *Diffed the compiled JS: one bit,
      `enableDownload` true→false. Corrected my own earlier claim — no page ever linked the masters.*
      → `1685271`

## Phase 5 — Archive and removal (US2, P1)

- [x] **T020** Create the `legacy-archive` tag, write `docs/legacy-archive.md` with an inventory and
      restore commands, then `git rm -r legacy/`. *Archive created and verified **before** removal.*
      → `27a2764`
- [x] **T021** Make the archive reachable by link, not just by SHA: browsable tag URLs,
      per-subdirectory links, zip, raw-file pattern, plus a README pointer. *All 14 URLs verified
      HTTP 200 anonymously; restore verified from a fresh fetch.* → `a117ee0`

## Phase 6 — Maintainability (US4, P3)

- [x] **T022** `scripts/check-content.py` — front-matter validation, errors vs warnings split.
      → `28ef8a6`
- [x] **T023** `.github/workflows/pr-check.yml` — the first pre-merge validation in this repo's
      history. → `28ef8a6`
- [x] **T024** Real `Makefile`, replacing a `sync` target that hardcoded an absolute `/Users/...`
      path. → `28ef8a6`
- [x] **T025** Archetype scaffolding real artwork front matter. → `28ef8a6`
- [x] **T026** `themes/gallery/UPSTREAM.md` recording v4.9.0 and all five local modifications; drop
      `.gitmodules`. *The diff against the import commit found five modifications, not the one the
      commit message implied, and revealed the theme's own `gallery.html` is dead code shadowed by the
      root override.* → `155946c`
- [x] **T027** Move the inline `<style>` block into `custom.css`. *Verified by HTML diff: inline
      `<style>` blocks 47 → 0, rendering unchanged.* → `cc72c3a`

## Phase 7 — Record (all stories)

- [x] **T028** Record implementation status and correct two wrong claims in place. → `1685271`
- [x] **T029** Backfill this spec, plan, and task list. → this change (2026-08-06)
- [x] **T030** Correct "47 artworks" to 46 in `docs/backend-optimization-plan.md`. *Spotted while
      building output assertions, which report 46; left unfixed at the time.* → this change

## Not done, deliberately

- [ ] **T031** Downscale masters to 2000 px — rejected on measurement (T004). Masters untouched.
- [ ] **T032** Drop the RSS feed — worth 25% of image conversions, but user-visible and not requested.
- [ ] **T033** Rewrite history to shrink the 561 MB pack — needs a force-push.
- [ ] **T034** Emit author metadata in markup so `params.author` stops being inert — needs a template
      change, excluded from a change set promising no front-end modification. *Carried into
      `001-quality-gates` T022.*
- [ ] **T035** Resolve 7 content warnings (3 missing `dimensions`, 2 empty `description`, 2 in
      inches). **Blocked on the artist** (NFR-004).

## Process failure recorded

This feature shipped with **no spec**, no acceptance criteria agreed in advance, and verification that
was entirely manual and one-off. It worked because the session was unusually measurement-heavy, not
because the process ensured it. Two corrections mid-flight and one uncorrected error (T030) are what
that looks like in practice.

The fix is `002-spec-process`, which makes a missing spec and a missing regression gate fail CI
instead of relying on diligence.
