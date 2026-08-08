# Theme provenance

This theme is **vendored** — its files are committed directly into this repository. It is
deliberately *not* a git submodule and not a Hugo module.

| | |
| --- | --- |
| Upstream | https://github.com/nicokaiser/hugo-theme-gallery |
| Version | **v4.9.0** (per `package.json`) |
| Imported in | `7c96a28` — "Add gallery theme files directly to repository" |
| License | See `LICENSE` in this directory |

A `.gitmodules` entry used to declare this directory as a submodule of upstream. That was
misleading: the files have always been committed directly and `git submodule status` returned
nothing, which also made `submodules: recursive` in the deploy workflow a no-op. Both have been
removed.

## Local modifications

This copy **diverges from upstream v4.9.0**. Full list, from
`git diff 7c96a28 HEAD -- themes/gallery`:

| File | Change |
| --- | --- |
| `layouts/_default/home.html` | Categories section moved *after* featured galleries |
| `layouts/_default/terms.html` | **Added** — empty template, suppresses the taxonomy terms page |
| `layouts/partials/album-card.html` | Flex centring, `max-width: 600px`; removed the album/photo count line |
| `layouts/partials/header.html` | Always links to home; dropped the `.Parent` back-button branch |
| `layouts/partials/gallery.html` | Single-image centred layout — **but see the warning below** |
| `exampleSite/**` | Upstream demo images deleted (~9 MB of unsplash JPEGs) |

Regenerate that list any time with:

```bash
git diff --stat 7c96a28 HEAD -- themes/gallery
```

### Warning: the theme's `gallery.html` is dead code

`themes/gallery/layouts/partials/gallery.html` was modified locally, but the repository root
also has `layouts/partials/gallery.html`, which **takes precedence at build time**. The two
files differ. Edit the root copy; changes to the theme's copy have no effect and will mislead
the next person.

## Site-level overrides (the right place for changes)

Prefer these over editing the vendored theme. They live in the repository root and win over the
theme's own copies:

- `layouts/_default/single.html` — artwork page: title, gallery, category link, related, prose.
- `layouts/partials/gallery.html` — single-image centred layout plus the dimensions caption.
- `layouts/partials/head.html` — page title and favicon handling.
- `assets/css/custom.css` — the site's visual identity. It reaches the page because the theme's
  `assets/css/main.scss` does `@import "custom"`, *not* via any `<link>` tag.

## Updating the theme

```bash
git clone --depth=1 --branch v<new-version> https://github.com/nicokaiser/hugo-theme-gallery /tmp/gallery
rm -rf themes/gallery && cp -r /tmp/gallery themes/gallery && rm -rf themes/gallery/.git
```

Then re-apply the modifications in the table above, restore this file, update the version, and
run `make check`. Review the diff before committing — that reviewable diff is the whole point
of vendoring.
