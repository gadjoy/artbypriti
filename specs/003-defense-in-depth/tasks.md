# Tasks: Defense in Depth

**Branch**: `003-defense-in-depth` | **Spec**: [spec.md](./spec.md) | **Plan**: [plan.md](./plan.md)

## Phase 0 — Learn from the portfolio first

- [x] **T001** Survey the 12 sibling projects instead of inventing. *Found `resumefit`'s versioned gate
      bundle and `keepsake`'s `.githooks`; found filled constitutions in `landseer`, `resumefit`,
      `gadjoy`. The answers already existed here.*
- [x] **T002** Read the bundle end to end before installing — hook extension logic, skip rules,
      escape hatches.

## Phase 1 — Local gates (US1, P1)

- [x] **T003** Vendor `check-hygiene.sh`, `check-message.sh`, `post-merge-notes.sh` from the bundle.
- [x] **T004** Complete the install by hand after the installer aborted on a missing
      `check-spec.sh`; wire this repo's `check-specs.py` into `pre-commit` instead.
- [x] **T005** Write `.githooks/{pre-commit,commit-msg,pre-push,post-merge}` and record the bundle
      version in `.githooks/GATES_VERSION`.
- [x] **T006** Write `scripts/preflight.sh` — the local equivalent of CI, skipping visual regression
      loudly when Docker is absent.
- [x] **T007** `make setup` (install hooks, print the layers) and `make preflight`.
- [x] **T008** Prove each gate: credential blocked, "wip" rejected, real message accepted,
      `pre-commit` 0.13 s.

## Phase 2 — Deploy gates (US2, P1)

- [x] **T009** `hugo.yml`: validate specs and content **before** building.
- [x] **T010** `hugo.yml`: assert on the built site **before** uploading the artifact.

## Phase 3 — Documentation (US3, P2)

- [x] **T011** Spec, plan, tasks recording where each layer sits and what it cannot do.

## Deferred / not ours

- [ ] **T012** Fix the installer bug in `resumefit` — another repository; reported instead.
- [ ] **T013** Extract a shared constitution across the portfolio — a decision spanning several
      repos, proposed separately.
- [ ] **T014** Continuous-learning loop (scheduled live-site health check, incident→gate ledger) —
      proposed, not built.
- [ ] **T015** Branch protection / rulesets — the owner's setting; now one layer among six rather
      than the only one.
