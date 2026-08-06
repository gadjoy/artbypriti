# Implementation Plan: Spec-First, Gate-Last Enforcement

**Branch**: `002-spec-process` | **Date**: 2026-08-06 | **Spec**: [spec.md](./spec.md)

## Summary

Turn two written habits into enforced ones. A pull request that changes substantive paths must carry
either a spec or a written exemption, and specs must be real rather than unfilled templates. Where
enforcement is impossible — judging whether a new check genuinely covers a new defect class — say so
and ask a human, rather than shipping a check that measures compliance and looks like coverage.

## Technical Context

**Language/Version**: Python 3.8+, stdlib only (matches the existing validators)

**Primary Dependencies**: none — `git` and the standard library

**Storage**: N/A

**Testing**: the checks are proven against injected cases on scratch branches, in both directions

**Target Platform**: GitHub Actions `ubuntu-latest`, plus developer machines

**Project Type**: Hugo static site

**Performance Goals**: under 5 s (achieved: well under 1 s)

**Constraints**: an exemption must always exist and cost one line; no new dependency; the check must
not overstate what it verifies

**Scale/Scope**: 3 feature directories, ~11 substantive path prefixes

## Constitution Check

| Principle | Compliance |
| --- | --- |
| I — a green build is not evidence | The check asserts on the actual diff and the actual spec files, not on a build succeeding |
| II — the rendered page is the contract | Untouched; no rendering change (verified by visual regression) |
| III — structural fails, content warns | Mirrored: a missing spec is structural and fails; a missing `plan.md`/`tasks.md` warns |
| IV — performance is a budget | Sub-second; no new dependency |
| V — vendored deps declare themselves | Untouched |

This feature also amends the constitution itself (1.0.0 → 1.1.0), which the Governance section
permits by pull request stating what prompted it.

## Technical decisions

### An escape hatch is mandatory

`No-Spec: <reason>` recorded in a commit message or the PR body. Without a route out, a
one-line CSS fix would demand a specification, and people would start bypassing CI wholesale — the
constitution's own warning about content gaps blocking deploys applies equally here. Recording the
reason in history is the point: the exemption is visible, unlike a label that can be removed.

### Why substantive paths are enumerated rather than inferred

Content edits vastly outnumber code changes on this repository. An allowlist of code-ish paths keeps
the common case frictionless, and the list is short enough to read. `specs/` and `docs/` are excluded
so writing a spec never itself demands a spec.

### Strip code spans before scanning for template tokens

Found while testing: both existing specs failed hygiene for quoting the placeholder token in prose
while *describing* this very problem. A spec must be able to discuss the tokens it checks for, so
fenced blocks and inline code are stripped before scanning. Unfilled templates carry the tokens bare.

### Rejected alternatives

- **Require a `tests/` change on every fix** — trivially satisfied by a meaningless edit. It would
  measure compliance, not coverage, and produce exactly the false assurance this project has already
  documented. The PR template asks a human instead.
- **A GitHub label as the exemption** — labels can be removed after merge, leaving no record.
- **Branch protection to block merges** — that is the owner's setting to make; these checks are what
  it would enforce.
- **Checking spec quality** — not machine-checkable. Stated as a limit in the spec.

## Project Structure

```
scripts/check-specs.py              # NEW — hygiene + spec-required
.github/pull_request_template.md    # NEW — asks for spec link, evidence, and which gate covers it
.github/workflows/pr-check.yml      # + "Require recorded intent" step (needs fetch-depth: 0)
Makefile                            # check now includes spec hygiene; new spec-required target
specs/README.md                     # NEW — index, statuses, why 000 is out of band
.specify/memory/constitution.md     # amended to 1.1.0
CLAUDE.md                           # documents the workflow and its escape hatch
```

## Verification approach

Every scenario exercised on scratch branches, then cleaned up:

| Injected case | Expected | Observed |
| --- | --- | --- |
| Substantive change, no spec, no exemption | fail with guidance | ✅ exit 1, named `assets/css/custom.css`, printed both routes |
| Same change with `No-Spec:` recorded | pass | ✅ passed, reason echoed back |
| Content-only change | pass, no spec needed | ✅ passed |
| Unfilled spec template | fail hygiene | ✅ failed on `[FEATURE NAME]` |
| The three real feature dirs | pass hygiene | ✅ passed |
