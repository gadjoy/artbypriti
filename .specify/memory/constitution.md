# Art by Priti Constitution

The project is a Hugo static site whose product is a gallery of paintings. It has no application
code and no users other than visitors looking at artwork. These principles are written against
the failure modes this repository has actually experienced, not a generic web-app checklist.

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

1. **Specify** — anything beyond a typo or a single content edit gets a spec under `specs/` before
   implementation (`/speckit-specify`). A spec states user-visible outcomes and acceptance
   criteria, not an implementation.
2. **Gate** — `make check` passes locally and in CI on every pull request: content validation,
   output assertions, visual regression. Adding a defect class to the gate is part of fixing a
   defect of that class, so it cannot return silently.
3. **Verify** — a change is done when its effect is demonstrated: measured numbers, a diff of
   built output, or a screenshot comparison. Not when the code looks right.
4. **Never force-push `main`, never rewrite shared history.** Archive by reference (see the
   `legacy-archive` tag) rather than by deletion.

## Governance

This constitution supersedes convenience. Amendments are made by pull request, stating what
experience prompted the change — every principle above exists because something broke.

Compliance is expected of human contributors and AI agents alike. An agent that cannot satisfy a
principle says so plainly rather than routing around it.

**Version**: 1.0.0 | **Ratified**: 2026-08-05 | **Last Amended**: 2026-08-05
