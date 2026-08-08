# Art by Priti — working notes

A Hugo static site: an online gallery of Priti Ghatlia's paintings, deployed to GitHub Pages at
artbypriti.com. There is no application code — 46 artwork page bundles, four template overrides,
one stylesheet, and two Python validators.

## Read these first

- **[`.specify/memory/constitution.md`](.specify/memory/constitution.md)** — the project's
  principles. Every one exists because something broke; they are not generic advice.
- **[`tests/README.md`](tests/README.md)** — the three gates, what each guards, and how to run
  them.
- **[`specs/`](specs/)** — specifications for in-flight work. If a spec exists for what you are
  changing, read it before the code.

## Before you claim anything works

Hugo's dominant failure mode is **silent fallback, not error**. Front matter naming a file that
does not exist will not fail the build — Hugo picks a different image and the deploy goes green.
Three such declarations shipped and survived ~15 months behind 16 consecutive green deploys.

So: **verify against build output, never against the templates.** Grep `public/`, diff before
against after, compare screenshots. Reading a template tells you what it *probably* does — on this
repository that reasoning has produced confident, wrong conclusions more than once.

## Commands

```bash
make            # list every target
make serve      # dev server with drafts, localhost:1313
make check      # front matter + strict build + output assertions (seconds; what CI runs)
make check-all  # the above plus visual regression (needs Docker)
make new SLUG=my-painting   # scaffold an artwork bundle
```

`make check` must pass before you open a pull request.

## Layout

| Path | What |
| --- | --- |
| `content/<slug>/` | One artwork per directory: `index.md` + its image |
| `layouts/` | Overrides that win over the theme — edit here, not in the theme |
| `assets/css/custom.css` | The site's visual identity. Reaches the page via `@import "custom"` in the theme's `main.scss`, **not** a `<link>` tag |
| `themes/gallery/` | **Vendored** (not a submodule) — see `themes/gallery/UPSTREAM.md` before touching it |
| `scripts/` | `check-content.py` validates inputs, `check-output.py` validates the built site |
| `tests/visual/` | Playwright specs and committed screenshot baselines |
| `docs/` | Deployment notes, the backend optimization plan, the legacy archive pointer |

## Gotchas that have cost time

- **Image cache lives in the path set by `[caches.images]`**, not `HUGO_CACHEDIR` by default. A
  cold build is ~200 s; warm is ~3 s. CI persists it — do not remove that cache step.
- **Hugo leaves stale files in `public/`** unless `--cleanDestinationDir` is passed. A renamed
  stylesheet keeps its predecessor, which makes output assertions report phantom problems.
- **The grid branch of `layouts/partials/gallery.html` never renders.** The home page uses the
  theme's `home.html` → `album-card.html`, and there are no image-bearing section lists. Its
  `site.Params.Author` schema.org block is therefore dead code.
- **Full-resolution masters are not published** (`publishResources: false` cascades from
  `content/_index.md`). Keep it that way: they were 116 MB of a 140 MB deploy and no page linked
  them.
- **`legacy/` was removed from the tree**, not from history — see
  [`docs/legacy-archive.md`](docs/legacy-archive.md).

## Working agreements

- Non-trivial work gets a spec under `specs/` first (`/speckit-specify`).
- Never force-push `main`; never rewrite shared history.
- Do not invent artistic facts. A painting's dimensions, a description, the artist's choice of
  units — these come from her, and automation warns rather than guesses.
- Fixing a defect includes adding it to a gate, so the same class cannot return silently.
