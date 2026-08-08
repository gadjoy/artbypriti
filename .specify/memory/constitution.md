# Art by Priti Constitution

The project is a Hugo static site whose product is a gallery of paintings. It has no application
code and no users other than visitors looking at artwork. These principles are written against
the failure modes this repository has actually experienced, not a generic web-app checklist.

<!-- BEGIN SHARED CONSTITUTION v1.0.0 — vendored from constitution/base.md.
     Do not edit here; amend upstream and re-vendor. `make check` enforces this. -->

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

<!-- END SHARED CONSTITUTION -->

---

# Art by Priti — project principles

The shared principles above apply. These are what is specific to this project.

## Core Principles

### I. A Green Build Is Not Evidence of Correctness

Hugo's dominant failure mode is silent fallback, not error. Front matter naming a resource that
does not exist will not fail the build — Hugo picks a different image and the deploy goes green.
Three such declarations shipped and survived roughly 15 months behind 16 consecutive successful
deploys.

Therefore: **every gate asserts on built output, never only on the exit code.** A check that
proves only "Hugo ran" adds confidence without adding safety, which is worse than no check at
all. Where a defect class is invisible in the exit code, write an assertion that inspects
`public/` and fails loudly.

### II. The Rendered Page Is the Contract

Visitors experience pixels, not templates. Reasoning about templates is not verification: on this
project, reading `gallery.html` produced two confident and *wrong* conclusions — that the grid
linked full-resolution masters, and that setting `params.author` would emit schema.org metadata.
Both were disproved by grepping the built HTML.

Therefore: **claims about site behaviour are substantiated against build output** — grep the
HTML, diff before against after, compare screenshots. "The template says so" is a hypothesis.

### III. Structural Errors Fail, Content Gaps Warn

Content gaps — a missing size caption, an unwritten description — can only be resolved by the
artist. A pipeline that blocks a deploy on them trains everyone to bypass the pipeline.
Structural errors — a declared file that is absent, a bundle with no image, a malformed caption —
are unambiguous defects.

Therefore: **structural defects fail CI; missing artist-authored content warns and never blocks.**
Automation must not invent artistic facts: no inventing a painting's dimensions, no writing the
artist's copy, no silently converting units she chose.

### IV. Performance Is a Budget, Not an Afterthought

An image-heavy gallery degrades quietly. Two hundred seconds of image processing per deploy, and
116 MB of unreferenced files in the payload, persisted for over a year because nothing watched
them.

Therefore: the deployed site stays **under 40 MB**, a cache-warm build stays **under 15 s**, and
no full-resolution master is ever published. A change that breaches a budget states the new
number and the reason.

### V. Vendored Dependencies Declare Themselves

`themes/gallery` is committed directly while `.gitmodules` claimed it was a submodule, and CI ran
a `submodules: recursive` step that did nothing. The theme also carried five undocumented local
modifications, one of them dead code shadowed by a root override.

Therefore: **vendored code records its upstream, its version, and every local modification**
(`themes/gallery/UPSTREAM.md`). Customisation belongs in root `layouts/` and
`assets/css/custom.css` overrides, not in the vendored copy.

### VI. The Live Site Is Someone's Portfolio

Merging deploys. There is no staging step between `main` and a working artist's public presence,
so `main` must always build and always look right.

### VII. The Images Are the Product

Never re-encode, rename, or move artwork unasked. A missing or degraded image is the most damaging
failure this site has — worse than a broken layout, because the layout is scaffolding and the
painting is the point. (This is why downscaling the masters was measured and then rejected.)

### VIII. URLs That Exist Must Keep Existing

Gallery links outlive redesigns: they are shared, bookmarked, and printed. Add an alias rather than
breaking a path.

### IX. Respect the Repository's Size Constraints

There is no Git LFS here, so GitHub's **100 MB per-file limit is a hard wall** — the WordPress
backup is stored as 99 MB chunks precisely because of it (see
`docs/linux-file-split-and-merge-guide.md`). Do not rewrite history to reclaim space; it would
invalidate every existing clone in exchange for disk that costs nothing.

## Additional Constraints

- **The front end does not change unintentionally.** Backend, build, and configuration work leaves
  rendered pages visually identical, and demonstrates it. Deliberate visual change is welcome — it
  just has to be deliberate, and stated.
- **Measure before claiming.** Performance and quality assertions carry the number and the method
  that produced them. No adjectives standing in for measurements.
- **Prefer deleting to accumulating.** Dead configuration, unused scaffolding, and stale
  documentation actively mislead the next reader — including automated agents, which follow
  instructions literally.

## Development Workflow

Written intent that nothing checks gets skipped. This project proved that twice: the speckit
scaffolding sat unused for 15 months, and the backend optimization work shipped with no spec while
that scaffolding was sitting right there. So each step below is enforced by something, and where it
cannot be, that is stated rather than implied.

1. **Specify — at the start.** Anything touching templates, styles, config, CI, or scripts gets a
   spec under `specs/` *before* implementation (`/speckit-specify`). A spec states user-visible
   outcomes and acceptance criteria, not an implementation.
   - *Enforced*: `scripts/check-specs.py` fails a pull request that changes substantive paths
     without either a `specs/**` change or a recorded exemption. It also fails an unfilled template
     — a spec full of placeholders is not a spec.
   - *Escape hatch, by design*: `No-Spec: <reason>` in a commit message or the PR body. Content
     edits, documentation, and typo fixes need nothing. A gate with no way out gets routed around,
     and a routed-around gate protects nothing.
2. **Gate — at the end.** Work finishes by leaving behind a check that fails if the defect returns.
   Fixing a defect includes adding its class to the suite.
   - *Enforced mechanically* for rendering (visual regression fails unless baselines are
     deliberately re-recorded) and for content and output (both assertion suites run on every PR).
   - *Not mechanically enforceable* for a genuinely new defect class: whether a new check covers it
     is a judgment, and requiring "some file under `tests/` changed" would measure compliance rather
     than coverage. The pull-request template asks for it explicitly instead.
3. **Verify.** A change is done when its effect is demonstrated: measured numbers, a diff of built
   output, or a screenshot comparison. Not when the code looks right. A check that has never been
   observed failing is not known to work — prove new gates in both directions.
4. **Never force-push `main`, never rewrite shared history.** Archive by reference (see the
   `legacy-archive` tag) rather than by deletion.

Retroactive specs are legitimate when they record history honestly — see
`specs/000-backend-optimization/`, numbered out of band because it precedes this process. Writing a
backfill that pretends the process was followed would be worse than having no backfill.

## Governance

This constitution supersedes convenience. Amendments are made by pull request, stating what
experience prompted the change — every principle above exists because something broke.

Compliance is expected of human contributors and AI agents alike. An agent that cannot satisfy a
principle says so plainly rather than routing around it.

**Version**: 1.1.0 | **Ratified**: 2026-08-05 | **Last Amended**: 2026-08-06

### Amendments

- **1.1.0** (2026-08-06) — Development Workflow rewritten so spec-first and gate-last are enforced
  rather than encouraged, each with its enforcement mechanism or an explicit admission that none is
  possible. Prompted by `000-backend-optimization` shipping without a spec: the previous wording
  described the habit but nothing checked it, which is exactly how the original scaffolding went
  unused for 15 months.
