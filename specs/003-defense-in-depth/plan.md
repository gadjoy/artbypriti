# Implementation Plan: Defense in Depth

**Branch**: `003-defense-in-depth` | **Date**: 2026-08-08 | **Spec**: [spec.md](./spec.md)

## Summary

Stop treating pull-request CI as the only place gates can live. Add the two layers that were missing —
local hooks before a commit exists, and validation inside the deploy workflow — by **vendoring the
gate bundle that already exists in `resumefit`** rather than writing a new one.

## Technical Context

**Language/Version**: bash + Python 3.8 stdlib | **Dependencies**: none new | **Testing**: each gate
proven by injecting the defect it claims to catch | **Performance**: `pre-commit` 0.13 s measured

## Constitution Check

| Principle | Compliance |
| --- | --- |
| I — a green build is not evidence | Deploy now asserts on built output *before* uploading, not just on build success |
| II — the rendered page is the contract | Unchanged; visual regression still authoritative |
| III — structural fails, content warns | Preserved through every layer |
| IV — performance is a budget | `pre-commit` 0.13 s, well inside the 2 s ceiling |
| V — vendored deps declare themselves | `.githooks/GATES_VERSION` records the bundle version and origin |

## Technical decisions

### Vendor, don't reinvent

`resumefit/scripts/install-hooks.sh` already solves this: `core.hooksPath` over copied hooks, gates
skipped where inapplicable, existing hooks extended rather than replaced, idempotent. Writing a
parallel implementation would have created a second dialect of the same idea across the portfolio.

**The installer aborted partway here** — it copies `scripts/check-spec.sh` whenever the target has
`specs/`, but that file no longer exists in `resumefit` (removed there once that repo checked specs its
own way). Installation was completed by hand, wiring this repository's existing `check-specs.py` into
`pre-commit` instead. The bug is reported in the hand-off notes; it will bite on any repo with
`specs/`, and it is not this repository's to fix.

### Hooks are feedback, not a boundary

Every hook is bypassable with `--no-verify`, and the documentation says so plainly. Pretending
otherwise would be the "theatre" failure this project has already documented twice. The layer that is
*not* bypassable is the deploy gate.

### Deploy-time gates are the real answer to "fail the build"

Validation now runs before Hugo builds, and output assertions run before the artifact uploads. A
broken site cannot be published even if it reaches `main` by a route nobody policed. This closes the
same hole branch protection would — for the case that actually matters — without depending on a
setting.

### Rejected

- **Writing new hooks from scratch** — a second dialect of an existing bundle.
- **Making hooks unbypassable** — impossible client-side, and pretending would mislead.
- **Running visual regression in `pre-commit`** — 10 s and needs Docker; it belongs in `pre-push`,
  where it is skipped loudly if Docker is absent.

## Verification approach

| Injected defect | Expected | Observed |
| --- | --- | --- |
| Staged credential | commit blocked | ✅ blocked, named the file |
| Commit message "wip" | rejected | ✅ rejected |
| Real message | accepted | ✅ committed |
| Unfilled spec template | commit blocked | ✅ (spec hygiene runs in `pre-commit`) |
| `pre-commit` duration | < 2 s | ✅ **0.13 s** |
