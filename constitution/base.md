<!-- SHARED-CONSTITUTION v1.0.0 — canonical copy; do not edit in a consuming repo.
     Amend upstream and re-vendor, or the drift check will flag it. -->

# Shared Engineering Principles

Portfolio-wide rules, **derived from what these repositories independently converged on** —
not invented for this document. Each principle names the repos that arrived at it separately;
convergence is the evidence that it generalises.

A project constitution vendors this block and then adds its own principles below it. Where they
conflict, the project's own principle wins and says why.

## S-I. Verify the artifact, not the appearance of success

A command that exits 0, a build that goes green, a log line that says "passed" — none is evidence
that the thing you wanted actually happened. Read back the artifact and compare it to intent.

*Converged independently in:* `landseer` III/IV ("record observations, never inferences"; "verify
by exit code **and** by outcome"), `resumefit` III ("verify the artifact, not the log"),
`artbypriti` I/II ("a green build is not evidence"; "the rendered page is the contract"), and the
machine-wide notes ("many CLIs exit 0 having done nothing").

## S-II. Never fabricate domain content

Automation may format, move, and check. It may not invent the things a human is the source of — a
measurement, a person's words, a record, a citation. When the value is unknown, say so and stop.

*Converged in:* `resumefit` I (never fabricate resume content), `gadjoy` III (no fabricated data),
`artbypriti` III (no inventing a painting's dimensions or the artist's copy).

## S-III. Specs precede implementation; gates precede merge

Non-trivial work states its intent and acceptance criteria before it is built, and finishes by
leaving behind a check that fails if the defect returns. Both need an escape hatch with a written
reason — a gate that cannot be bypassed gets bypassed wholesale.

*Converged in:* `gadjoy` I (test-first), `resumefit` IV (tests gate merges, specs precede tests),
`landseer` I (every change ships through a reviewed PR), `artbypriti` workflow.

## S-IV. History is additive; archive by reference

Prefer adding over rewriting. Do not force-push shared branches or rewrite published history: it
buys disk and costs every existing clone. When something must leave the working tree, leave a
reference that still resolves.

*Converged in:* `resumefit` V (destructive changes backed up first, history additive),
`artbypriti` (removed 1.38 GB from the tree, kept it at a tag, no rewrite).

## S-V. A green suite is not a current suite

Tests rot silently. A suite that passes proves the checks that exist still hold — not that they
still cover what the system now does. Every defect found in production is first a question about
which gate should have caught it.

*Converged in:* `landseer` VII (keeping a suite green is not keeping it current), and every
incident in `artbypriti`'s ledger.
