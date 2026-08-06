<!--
Delete any section that does not apply. A content-only change (a new painting, a typo) needs
only the first line and the checklist's first box.
-->

## What and why

<!-- One or two sentences. What changes for a visitor, or for whoever maintains this next? -->

**Spec:** <!-- specs/NNN-name/spec.md — or `No-Spec: <reason>` if this is small enough not to need one -->

## Verification

<!--
Constitution Principle II: the rendered page is the contract. State what you actually observed,
not what should be true. Numbers, a diff of built output, a screenshot comparison.

"Reading the template says so" is a hypothesis — on this repository that reasoning has produced
confident, wrong conclusions more than once.
-->

- [ ] `make check` passes
- [ ] `make visual` passes, or baselines were intentionally re-recorded and reviewed
- [ ] Measurements included for any performance or size claim

## Which gate covers this?

<!--
Only for a defect fix. Fixing a defect includes making the same defect unable to return
silently — CI cannot verify that a new check is meaningful, so it is asked here instead.

Name the check that now fails if this regresses, or say plainly that none can and why.
-->

## Anything deliberately not done

<!-- Rejected alternatives with their reason, deferred work, decisions left to the artist. -->
