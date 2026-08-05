# Implementation Plan: Automated Quality Gates

**Branch**: `001-quality-gates` | **Date**: 2026-08-05 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/001-quality-gates/spec.md`

## Summary

Add three layers of automated checking to a site that had none, targeted at the one defect class
that has actually shipped here: **a successful build producing wrong output.** Input validation
already exists (`check-content.py`); this adds output assertions over `public/` and visual
regression over rendered pages, then runs all three on every pull request.

## Technical Context

**Language/Version**: Python 3.8+ (stdlib only) for validators; Node 24 / JavaScript for Playwright

**Primary Dependencies**: `@playwright/test` 1.62.1 (dev-only). Hugo Extended ≥ 0.128 for the site

**Storage**: Screenshot baselines committed as PNGs under `tests/visual/*-snapshots/`

**Testing**: Playwright for visual regression; two stdlib Python scripts for assertions. No unit-test
framework — see spec "Out of Scope"

**Target Platform**: GitHub Actions `ubuntu-latest`, plus developer machines with Docker

**Project Type**: Hugo static site (no application code)

**Performance Goals**: `make check` under 60 s warm (achieved: **0.56 s**); full suite under 5 minutes

**Constraints**: Zero flaky failures (NFR-002). No runtime dependency added to the published site
(NFR-003). Committed baselines must stay small — the repo was just reduced from 1.5 GB

**Scale/Scope**: 46 artwork pages, 61 built HTML pages, ~1041 internal references, 5 baseline images

## Constitution Check

| Principle | How this work complies |
| --- | --- |
| I — a green build is not evidence | The entire point: `check-output.py` reads `public/` and fails on wrong-but-buildable output |
| II — the rendered page is the contract | Visual regression compares actual pixels; assertions grep built HTML |
| III — structural fails, content warns | Preserved: missing `dimensions` warns (3 artworks), broken declarations error |
| IV — performance is a budget | 40 MB payload budget enforced by `check-output.py`; baselines sized down 12 MB → 3.5 MB |
| V — vendored deps declare themselves | Unchanged; Playwright is a real dependency with a lockfile, not vendored |

No violations. No complexity-tracking entries required.

## Technical decisions

### Why a container for screenshots

Screenshots are only comparable when font rasterisation is identical. Running Playwright directly on
a runner and on a laptop yields different antialiasing, producing failures that track the host rather
than the change. Everything therefore runs through
`mcr.microsoft.com/playwright:v1.62.1-noble`, invoked identically by `make visual` locally and in CI.

### Threshold calibration (the decision that nearly made this worthless)

Playwright's default `threshold: 0.2` is a per-pixel YIQ tolerance of ~7043 out of ~35215. Shifting
the site background `#f4efe0` → `#e8dcc0` computes to a delta of ~193, so **the first working
version of this gate passed all 7 tests against an obviously wrong page.**

Resolution: `threshold: 0` (any non-identical pixel counts) with `maxDiffPixelRatio: 0.01` for
tolerance. The same change now fails at 47–51% pixels different. Determinism from the container is
what makes a zero threshold viable, and it is verified by three consecutive clean runs.

### Why lazy loading is bypassed in tests

lazysizes only unveils images near the viewport; measured, 7 of 46 home-page images still had no
`src` after a full scroll pass. Screenshots therefore promote `data-src` → `src` directly. The
mechanism keeps its own assertion so bypassing it in screenshots cannot hide its removal.

### Rejected alternatives

- **A unit-test framework** — there is nothing to unit test (681 lines of content, 123 of templates).
- **HTML/link checking via an external service or `htmltest`** — a 40-line stdlib walk over `public/`
  covers all 1041 references with no new dependency.
- **Grepping workflow YAML to guard the CI cache defect** — asserts the shape of a fix rather than a
  behaviour, and breaks on legitimate refactors. Documented and observable instead (see SC-001).
- **`fullPage` screenshots everywhere** — the home grid alone is a 6.7 MB PNG; committed baselines
  would undo the repository slimming just completed.

## Project Structure

```
scripts/
  check-content.py     # inputs: front matter, declared resources (extended here for content/_index.md)
  check-output.py      # NEW — asserts on the built site
tests/
  README.md            # NEW — what each gate guards, threshold calibration, how to re-record
  visual/
    gallery.spec.js    # NEW — 5 page screenshots + 2 behavioural assertions
    gallery.spec.js-snapshots/*.png   # NEW — committed baselines (3.5 MB)
playwright.config.js   # NEW — container-targeted config
package.json           # NEW — dev-only dependency
.github/workflows/pr-check.yml        # extended: two jobs (fast gates, visual)
Makefile               # extended: check, check-all, visual, visual-update
CLAUDE.md              # rewritten: no longer points at a nonexistent plan
.specify/memory/constitution.md       # filled in: 5 principles from real incidents
```

## Phasing

1. **P1 — output assertions.** No browser, seconds to run, covers every historical defect that is
   gateable. Landed first so later phases build on a trustworthy build.
2. **P2 — visual regression.** Container, baselines, calibration, CI job.
3. **P3 — documentation and process.** Constitution, `CLAUDE.md`, `tests/README.md`.

## Verification approach

Every gate is proven in both directions before being considered done — a check that has never been
observed failing is not known to work:

| Injected defect | Expected |
| --- | --- |
| Master image planted in `public/` | output assertions fail |
| Internal link broken | output assertions fail |
| Each of the 3 historical resource declarations | `check-content` fails |
| Background colour shifted | visual regression fails with diffs |
| Caption `font-size` changed | visual regression fails on the artwork page only |
| Nothing changed, 3 consecutive runs | everything passes every time |
