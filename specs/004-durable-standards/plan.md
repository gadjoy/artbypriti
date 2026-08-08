# Implementation Plan: Durable Standards

**Branch**: `004-durable-standards` | **Date**: 2026-08-08 | **Spec**: [spec.md](./spec.md)

## Summary

Two mechanisms so standards outlive the session that wrote them: a shared constitution vendored with
drift detection, and a scheduled check that watches the live system when no one is committing.

## Technical Context

**Language**: bash + Python 3.8 stdlib | **Dependencies**: none new | **Testing**: each check proven
by injecting the failure it claims to catch | **Scale**: 5 shared principles, 9 project principles,
7 live endpoints, 9 ledger entries

## Constitution Check

| Principle | Compliance |
| --- | --- |
| S-I / I–II verify the artifact | `check-live.py` reads the deployed site, not the deploy's exit code |
| S-II never fabricate | The shared base cites which repos converged on each rule; nothing invented |
| S-III specs precede, gates follow | This spec preceded the code — and `pre-commit` blocked a commit mid-implementation for a spec directory with no `spec.md` |
| S-IV additive history | Nothing rewritten; the parallel branch's principles are absorbed, not discarded |
| S-V green ≠ current | The whole point of the ledger and the scheduled run |
| IX size constraints | Text only |

## Technical decisions

### Derive the base, do not invent it

Every shared principle names the repositories that arrived at it independently. Convergence across
`landseer`, `resumefit`, `gadjoy` and `artbypriti` is the evidence it generalises. A base of invented
best practice would be someone's opinion with extra ceremony.

### Vendor with drift detection, rather than reference

A reference (a URL, `~/.claude/CLAUDE.md`) does not travel to CI or a fresh clone, and cannot be
reviewed in a diff. A vendored copy that anyone may quietly edit is a fork with a misleading name.
Vendoring plus a byte-comparison check gets both: local, reviewable, and provably identical. Same
pattern the hooks bundle already uses.

### Projects must be able to disagree

A shared rule that cannot be overridden gets the entire base rejected the first time it is wrong for
someone. Overriding is legitimate — below the block, in writing, with the reason.

### Scheduled checks are the only decay detector

Everything else here triggers on a commit. Certificates expire, DNS moves, external references rot,
deploys silently stop — none of which any PR would notice. The scheduled run deliberately skips the
image cache, because a cold build proving the site still builds from nothing is the point.

### Rejected

- **Alerting/paging** — GitHub's own failure notifications are proportionate for a personal site.
- **Auto-opening an issue on failure** — noise before there is evidence anyone triages it.
- **Running the installer against sibling repos** — those repositories' maintainer decides.

## Verification approach

| Injected | Expected | Observed |
| --- | --- | --- |
| Edited shared block | drift check fails | ✅ failed, pointed at re-vendor or override |
| Restored block | passes | ✅ in sync, v1.0.0 |
| Live site today | healthy | ✅ 7 pages 200, masters 404, archive resolves |
| Bad base URL | fails loudly | ✅ 7 errors |
| Spec dir with no `spec.md` | commit blocked | ✅ blocked by `pre-commit` during this work |
