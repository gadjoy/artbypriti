# Tasks: Automated Quality Gates

**Branch**: `001-quality-gates` | **Spec**: [spec.md](./spec.md) | **Plan**: [plan.md](./plan.md)

Status recorded after implementation. Every task marked done was verified by observing the check
fail on an injected defect, not merely by running it once green.

## Phase 1 — Output assertions (US1, P1)

- [x] **T001** Write `scripts/check-output.py` asserting on the built site: no published masters,
      40 MB payload budget, every artwork renders an image, captions present where front matter
      promises one, expected pages exist, all internal links resolve.
- [x] **T002** Scope the master check to page-bundle output directories. *Caught in review: the first
      version flagged `static/images/favicon.png` and `apple-touch-icon.png`, which are legitimately
      copied verbatim.*
- [x] **T003** Extend `check-content.py` to validate `content/_index.md`. *Caught by the SC-001
      acceptance test: the loop over `content/*/index.md` never inspected the branch bundle, so the
      home-cover defect — one of the four this feature exists to prevent — was **not** caught by the
      first implementation. The error message now names the child bundle holding the file.*
- [x] **T004** Enforce `--panicOnWarning` and `--cleanDestinationDir` in the build. *Verified the
      current site emits zero warnings first, so the flag cannot land already-red.*
- [x] **T005** Negative-test T001: plant a master (fails, names `olive/Olive.jpg`), break an internal
      link (fails, names source and target), then confirm the clean tree passes.

## Phase 2 — Visual regression (US2, P2)

- [x] **T006** Add `package.json` + `package-lock.json` pinned to `@playwright/test` 1.62.1.
      *Generated inside the container — the host npm is offline.*
- [x] **T007** Write `playwright.config.js` targeting the pinned container, fixed viewport 1280×900,
      `colorScheme: light`, UTC, animations disabled, `python3 -m http.server` serving `public/`.
- [x] **T008** Write `tests/visual/gallery.spec.js`: one page per distinct layout (home, artwork,
      about, request, category) plus assertions for the lightbox variant and lazy-loading wiring.
- [x] **T009** Make image loading deterministic. *First version scrolled to trigger lazysizes and
      timed out on 2 of 6 tests; diagnosis showed 7 of 46 home-page images never received a `src`
      because lazysizes drops out-of-range images. Now promotes `data-src` → `src` directly.*
- [x] **T010** **Calibrate the threshold.** *The gate initially did not work: with Playwright's
      default `threshold: 0.2`, shifting the site background `#f4efe0` → `#e8dcc0` passed all 7
      tests. Changed to `threshold: 0` with `maxDiffPixelRatio: 0.01`; the same change now fails at
      47–51% of pixels. This was the difference between a real gate and theatre.*
- [x] **T011** Right-size baselines: viewport captures for long listing pages, full-page for short
      ones. *12 MB → 3.5 MB committed, per Constitution Principle IV.*
- [x] **T012** Record baselines in the container and commit them.
- [x] **T013** Negative-test the gate: colour shift fails with diff artifacts; caption `font-size`
      change fails only the artwork page; unchanged site passes 3 consecutive runs.

## Phase 3 — Wiring and process (US3, P3)

- [x] **T014** `Makefile`: `check`, `check-all`, `visual`, `visual-update`, with the container
      invocation shared so local and CI cannot drift.
- [x] **T015** `.github/workflows/pr-check.yml`: two jobs — fast gates and visual regression — both
      reusing the deploy workflow's image cache; upload `*-diff.png` on failure.
- [x] **T016** `.gitignore`: ignore `node_modules/`, `test-results/`, `playwright-report/`; keep
      baselines tracked.
- [x] **T017** Fill `.specify/memory/constitution.md` with five principles, each traced to a real
      incident. Removes all 16 `[PLACEHOLDER]` tokens.
- [x] **T018** Rewrite `CLAUDE.md` so no instruction dangles. *It previously said only "read the
      current plan", which resolved to nothing — every session, human or agent, started from a broken
      pointer.*
- [x] **T019** Write `tests/README.md` documenting each gate, the threshold calibration (so nobody
      re-loosens it), and how to re-record baselines.

## Deferred

- [ ] **T020** Resolve the 7 content warnings — 3 artworks with no `dimensions`, 2 with an empty
      `description`, 2 in inches. **Blocked on the artist**: automation must not invent a painting's
      size, write her copy, or convert her chosen units (Principle III).
- [ ] **T021** Consider Lighthouse/accessibility auditing. Out of scope here; no known defect.
- [ ] **T022** Emit author metadata in the markup so `params.author` stops being inert. Needs a
      template change (~2 lines in `single.html` or `opengraph.html`); deliberately excluded from a
      change set that promises no front-end modification.
