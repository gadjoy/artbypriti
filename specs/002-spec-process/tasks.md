# Tasks: Spec-First, Gate-Last Enforcement

**Branch**: `002-spec-process` | **Spec**: [spec.md](./spec.md) | **Plan**: [plan.md](./plan.md)

## Phase 0 — Backfill the gap this feature exists to close

- [x] **T001** Write `specs/000-backend-optimization/spec.md` from the session record: measured
      baselines, rejected alternatives with their evidence, and both claims that turned out wrong.
- [x] **T002** Write its `plan.md` — the sequencing actually followed, and the verification methods,
      including the admission that all of it was one-off and manual.
- [x] **T003** Write its `tasks.md`, mapping each task to the commit that shipped it, so the record is
      checkable rather than merely plausible.
- [x] **T004** Fix the error the backfill surfaced: "47 artworks" → 46 plus the `about` page, in four
      places in `docs/backend-optimization-plan.md`. *Spotted a day earlier while building output
      assertions and left unfixed — precisely the kind of loose end a spec review catches.*

## Phase 1 — Spec-first enforcement (US1, P1)

- [x] **T005** `scripts/check-specs.py` hygiene: fail on leftover template tokens and on a spec with
      no Success Criteria section; warn on a missing `plan.md`/`tasks.md`.
- [x] **T006** Strip fenced blocks and inline code before scanning for tokens. *Both existing specs
      initially failed for quoting the placeholder token while describing this problem.*
- [x] **T007** Spec-required: classify the branch diff against a base ref, and demand either a
      `specs/**` change or a `No-Spec: <reason>` trailer in a commit message or `PR_BODY`.
- [x] **T008** Enumerate substantive paths; exclude content, `docs/`, `README.md`, and `specs/` so a
      typo fix never demands a specification.
- [x] **T009** Acceptance-test all four cases on scratch branches (fail without intent, pass with
      exemption, pass for content-only, fail on an unfilled template), then delete the branches.
      *First attempt was invalid — the script does not exist on the base branch after checkout, so it
      never ran; re-run from a copy held outside the repo.*
- [x] **T010** Wire into `make check` and add a `spec-required` target for local use.
- [x] **T011** Add the CI step with `fetch-depth: 0` and `PR_BODY` so exemptions in a PR body count.

## Phase 2 — Gate-last (US2, P2)

- [x] **T012** `.github/pull_request_template.md`: asks for the spec link, verification evidence, and
      **which gate now covers this** — the judgment CI cannot make.
- [x] **T013** Record in the spec and the constitution exactly what is mechanically enforced (visual
      regression on rendering; content and output assertions) and what is not (whether a new check
      genuinely covers a new defect class). *A check that appears to enforce more than it does is the
      theatre this project has already documented.*

## Phase 3 — Discoverability (US3, P3)

- [x] **T014** Amend the constitution to 1.1.0: workflow steps now carry their enforcement mechanism,
      with an amendment note stating what prompted the change.
- [x] **T015** `specs/README.md`: index with statuses and an explanation of why 000 is out of band.
- [x] **T016** `CLAUDE.md`: document the workflow, the substantive paths, and the escape hatch.

## Deferred / not done

- [ ] **T017** GitHub branch protection requiring these checks before merge — the owner's setting to
      make; the checks are what it would enforce.
- [ ] **T018** Spec-quality checking — not machine-checkable; review's job.
- [ ] **T019** Backfilling anything older than `000-backend-optimization`.
