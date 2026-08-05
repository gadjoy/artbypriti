# Backend & Build Optimization Plan

**Scope:** build pipeline, image pipeline, CI, repository hygiene, and configuration.
**Non-goal:** redesigning the front end. Every change below is intended to leave the rendered
pages visually identical, with two exceptions that are called out explicitly as product
decisions (full-resolution downloads, and the RSS feed).

Measured on 2026-08-04 against `main` @ `8d0cf6e`, Hugo 0.147.8 extended.

---

## 0. Implementation status

Everything below is **implemented** except where noted. Post-implementation measurements:

| | before | after |
| --- | --- | --- |
| Build (warm cache) | 197.6 s every deploy | **3.0 s** |
| Published site | 140 MB | **28 MB** |
| Repo working tree | ~1500 MB | **118 MB** |
| Pages with inline `<style>` | 47 | **0** |
| Front-matter validation | none | 47 bundles, 0 errors, 7 warnings |

**Not implemented, deliberately:**

- **§1.5 (downscale masters)** — skipped on the strength of the measurement in that section.
  The masters are untouched.
- **§2.4 (drop RSS)** — kept. Removing a feed is user-visible and wasn't requested.
- **§5 (history rewrite)** — not done; needs a force-push. `legacy/` was removed from the tree
  only, and is permanently retrievable via the `legacy-archive` tag (see
  [legacy-archive.md](legacy-archive.md)).

**Two claims in this plan were wrong and are corrected in place below** (§1.1, §2.1): the
masters turned out to be referenced by zero pages, and `params.author` turned out to be inert.
Both corrections came from diffing the built output rather than from re-reading the templates.

---

## 1. Baseline — where the time and bytes actually go

| Metric | Measured |
| --- | --- |
| Artworks (page bundles) | 47 |
| Source images | 48 files, **115.8 MB**, typically 2490–3900 px on the long edge |
| Images processed per full build | **187** |
| **Cold build** (empty `resources/_gen`) | **197.6 s** |
| **Warm build** (variants cached) | **5.6 s** — 35× faster |
| Published site | **140 MB** total (61 HTML files, 237 image files) |
| — of which source originals, copied verbatim | **115.8 MB (83%)** |
| — of which derived variants | 22.2 MB |
| Repo tip tree (what CI checks out every run) | **1497 MB**, of which `legacy/` is **1380 MB** |
| Packed git history | 561 MB |
| CI image-variant cache | none — every deploy reprocesses all 187 images |

Derived-variant breakdown, which shows exactly what each build is paying for:

| Variant | Count | Bytes | Consumer |
| --- | --- | --- | --- |
| 1600 px fit | 47 | 12.5 MB | PhotoSwipe lightbox |
| 1000 px fit | 47 | 4.6 MB | single artwork page |
| 900×600 fill | 46 | 3.3 MB | **RSS feed thumbnails only** |
| 600 px fit | 46 | 1.7 MB | home/category grid |
| originals | 48 | 115.8 MB | lightbox `href` fallback only |

Three things fall straight out of these numbers:

- **83% of the deployed payload is originals** that no page displays. They are reachable only
  by following the grid's `href` (or the lightbox download button) — an 8 MB file for `Olive.jpg`.
- **Every deploy pays the full 197.6 s cold-build cost**, because nothing persists
  `resources/_gen` between CI runs. With the cache warm the same build is 5.6 s. This is a
  pure configuration miss, not a workload problem.
- **The largest image the site ever renders is 1600 px**, yet every master is 2490–3900 px.
  That extra resolution costs clone and checkout size — but note it is *not* the main build-time
  lever once the cache exists (see §1.5, which measurement demoted).

---

## 2. Phase 1 — Ship weight and CI (the big wins)

### 1.1 Stop publishing full-resolution originals

`content/_index.md` already contains the switch, commented out. Enabling it makes Hugo skip
copying masters into `public/`:

```yaml
cascade:
  build:
    publishResources: false
```

The theme is already written for this. `layouts/partials/gallery.html` reads
`$publishResources` and falls back to the 1600 px variant for the grid `href`, and
`layouts/partials/head.html` passes `enableDownload` from the same key. Our single-artwork
path already links to the 1600 px variant unconditionally, so single pages don't change at all.

- **Effect:** published site 140 MB → **28 MB** (measured). Faster Pages artifact upload and
  deploy on every push.
- **Trade-off, corrected after verification.** I originally wrote that the grid links to
  masters and that a download affordance would be lost. Grepping the built HTML disproved the
  first half: **zero rendered pages referenced the masters** — 0 non-derived image references
  across all 61 pages. The `gallery-item` grid branch of `gallery.html` never executes on this
  site (the home page renders via `home.html` → `album-card.html`, and there are no
  image-bearing section lists), so the masters were reachable only by guessing a URL. The one
  real change is that PhotoSwipe's download button is hidden — and it offered the **1600 px
  display variant**, never the master. Verified as a single bit flip in the built JS
  (`enableDownload` true → false).

### 1.2 Take `legacy/` out of the working tree

`legacy/` is 1380 MB of the 1497 MB tip tree: five near-identical migration snapshots
(`migration_1`…`migration_5`, ~1 GB of duplicated WordPress-era images) plus a 336 MB
WordPress backup split into four `.wpress_part_*` blobs. None of it feeds the build.

Every CI run — and every clone — downloads and writes all of it.

1. Archive it first: push it to a separate `artbypriti-legacy` repo, attach the `.wpress`
   parts to a GitHub Release, or keep an offline copy. Do not skip this step.
2. `git rm -r legacy/` on a branch, merge normally. No force-push, no history rewrite.

- **Effect:** CI checkout drops from ~1.5 GB to ~117 MB. Shallow clones (what
  `actions/checkout` does by default) stop fetching those blobs entirely.
- **Note:** packed history stays at 561 MB, so *full* clones stay slow. Fixing that needs a
  history rewrite — see §5.

### 1.3 Cache the image pipeline in CI

This is the single biggest CI win and the most commonly-missed detail. Hugo's image variants
are cached in **`resourceDir/_gen/images`** (i.e. `./resources/_gen`), *not* in
`HUGO_CACHEDIR`. The current workflow sets `HUGO_CACHEDIR` but caches nothing, so every deploy
redoes all 187 conversions from scratch.

Point the image cache at `HUGO_CACHEDIR` in `hugo.toml`:

```toml
[caches]
  [caches.images]
    dir = ":cacheDir/images"
    maxAge = "720h"
```

…then actually persist it in `.github/workflows/hugo.yml`, before the build step:

```yaml
      - name: Cache Hugo image variants
        uses: actions/cache@v4
        with:
          path: |
            ${{ runner.temp }}/hugo_cache
            resources/_gen
          key: hugo-img-${{ env.HUGO_VERSION }}-${{ hashFiles('content/**/*.jpg', 'content/**/*.jpeg', 'content/**/*.png', 'hugo.toml') }}
          restore-keys: |
            hugo-img-${{ env.HUGO_VERSION }}-
```

The `restore-keys` fallback matters: adding one painting then reuses the other 47 artworks'
variants and only processes the new one.

- **Effect, measured:** **197.6 s → 5.6 s** for the build step. Image processing effectively
  disappears from typical deploys. This is the highest-value change on the list, it is
  config-only, it touches no content, and it carries no risk — do it first.

### 1.4 Delete two CI steps that do nothing

- **`sudo snap install dart-sass`** — not needed. The theme compiles `main.scss` via
  `toCSS`, which Hugo Extended handles with its bundled LibSass. Verified: this machine has no
  `dart-sass` installed and the SCSS (including `custom.css`, which `main.scss` `@import`s)
  compiled correctly into the fingerprinted stylesheet. Snap installs cost ~20–40 s per run.
- **`npm ci` step** — a no-op guard; there is no root `package-lock.json`. Harmless, but it is
  one more thing to read past.

### 1.5 Downscale the masters to 2000 px — *optional, and demoted after measurement*

I originally had this as a headline win. Measuring it argued otherwise, so it is now optional
and explicitly a repo-size play rather than a performance one.

**What it buys:** sources **115.8 MB → 24.9 MB (−78%)**, cold build 197.6 s → 105.6 s.

**Why that's less compelling than it looks:** §1.3 already takes the build to 5.6 s, so the
90 s of saved cold-build time is time you stop paying anyway. And with §1.1 in place the
masters are no longer deployed, so they cost clone size only.

**What it costs — measured, not assumed.** Comparing the 1600 px image a visitor actually
receives, generated from a downscaled master vs. from the current master:

| Master rewritten at | PSNR vs today's delivered image | mean abs diff/channel | master size |
| --- | --- | --- | --- |
| 2000 px, quality 85 | 32.2 dB | 4.80 | 1.17 MB |
| 2000 px, quality 92 | 34.2 dB | 3.67 | 1.61 MB |
| 2000 px, quality 95 | 35.1 dB | 3.23 | 2.00 MB |

For reference, >40 dB is generally imperceptible; 30–35 dB is visible on close inspection of
fine detail — which is exactly what this art is. An end-to-end check through the real Hugo
pipeline measured lower still (26.3 dB), though a good part of that gap is Hugo's `Box`
resample filter behaving differently on a 2516 px source than on a 2000 px one, rather than
true information loss.

**Therefore:** if you do this, use **quality 92–95, not 85**, and treat the delivered-image
comparison as a merge gate. If the goal is purely a smaller repository, moving the masters to
external storage is lossless and strictly better. My recommendation is to skip this step unless
clone size is actively bothering you.

---

## 3. Phase 2 — Configuration correctness

`hugo.toml` is currently 7 lines and leans entirely on defaults. Several of those defaults are
wrong for an image-heavy art site, and a few declarations elsewhere are silently dead.

### 2.1 Harden `hugo.toml`

```toml
baseURL = 'https://artbypriti.com/'
languageCode = 'en-us'
title = 'Art by Priti'
theme = 'gallery'
enableRobotsTXT = true
timeout = "180s"          # cold image-heavy builds can exceed the 60s default

[taxonomies]
  category = "categories"

[params]
  description = "Online gallery of paintings by Priti Ghatlia"
  [params.author]
    name = "Priti Ghatlia"

[imaging]
  quality = 82             # default is 75
  resampleFilter = "CatmullRom"   # default is Box — faster but softer
  [imaging.exif]
    disableLatLong = true  # don't leak location data from source photos

[module]
  [module.hugoVersion]
    min = "0.128.0"
```

Why each line earns its place:

- **`timeout`** — Hugo's default render timeout is 60 s (confirmed via `hugo config`). The
  theme's own example site raises it to 120 s precisely because image processing runs during
  rendering, and a cold build here already takes longer than 60 s of wall clock. A cold build
  on a slow runner is a real failure mode today.
- **`resampleFilter`/`quality`** — Hugo defaults to `Box` at quality 75 (confirmed via
  `hugo config`), and this turns out to be **the biggest actual image-fidelity deficit on the
  site**. Measured: the delivered 1600 px image at q75 sits **30.1 dB from the same image at
  q92** — i.e. the current default quality setting costs *more* visible fidelity than
  downscaling the masters ever would (§1.5). `Box` is likewise the fast-and-soft option;
  `CatmullRom` is what the theme's own example site uses.

  The price is modest and precisely known (sampled across 12 masters, extrapolated to the
  47-image 1600 px set):

  | quality | per image | site-wide 1600 px set |
  | --- | --- | --- |
  | 75 (today) | 215 KB | 9.9 MB |
  | 82 | 269 KB | 12.4 MB (**+2.5 MB**) |
  | 90 | 383 KB | 17.6 MB (**+7.7 MB**) |

  (The extrapolated q75 baseline here is 9.9 MB against 12.5 MB measured in the real build; the
  sample used a different resampler than Hugo's `Box`. Treat the **deltas** as indicative
  — order-of-magnitude-correct, not exact — and confirm on the first real build.)

  Since §1.1 removes 116 MB from the payload, spending 2.5–7.7 MB of that on images which are
  the entire point of the site is an easy trade. I'd go with 82, or 90 if you want the
  brushwork to hold up on a retina display. Extra encode time is absorbed by §1.3's cache.
- **`params.author`** — `layouts/partials/gallery.html` has a
  `{{ with site.Params.Author }}` block emitting schema.org `creator` metadata, and no author is
  configured, so the artist is absent from the structured data.

  **Corrected after verification:** setting it is *not* the free SEO win I claimed. That block
  sits in the list branch of `gallery.html`, which never renders on this site — the built HTML
  contains zero `itemprop=creator` occurrences both before *and* after the change. The setting
  is kept as correct site metadata but is currently inert; actually surfacing author metadata
  needs a small template change (adding it to `single.html` or `opengraph.html`), which is a
  markup change and therefore out of scope here.
- **`imaging.exif.disableLatLong`** — the masters are camera/phone photos of paintings; don't
  publish GPS coordinates.

### 2.2 Fix two dead resource declarations

Both are silent — Hugo does not warn, it just falls back:

- `content/_index.md` declares a cover of `staircase.jpg`, but that file lives in the
  `content/staircase/` bundle and is not a resource of the home page. The OpenGraph image
  therefore falls back to `content/Priti_Ghatlia.jpg` — the artist's portrait is currently the
  social-share card for the whole site. Either move/copy the intended cover into the home
  bundle or point the declaration at a file that is actually there.
- `content/about/index.md` declares `Priti_Ghatlia.jpg`, but the folder contains
  `Priti-Ghatlia.jpeg` (hyphen, different extension). The declaration matches nothing.

### 2.3 Align the Hugo version

CI pins `HUGO_VERSION: 0.128.0`; local development here is 0.147.8. That is 19 minor releases
of drift in image handling and template semantics — the exact area we are changing. Pick one
version, set it in CI, and enforce the floor via `[module.hugoVersion]` as above.

### 2.4 Optional: drop the RSS feed

The 900×600 fill variants are **46 of the 187 conversions (25%)** and exist solely for
`index.xml`. If nobody subscribes to a painting feed, `[outputs] home = ["HTML"]` removes a
quarter of the image work outright. Keep it if the feed is wanted — this is a product call, not
a defect.

---

## 4. Phase 3 — Maintainability

These don't move the clock much; they stop the site from drifting as paintings are added.

### 3.1 Make `hugo new` scaffold a real artwork

`archetypes/default.md` is still the stock stub, so all 47 artworks were hand-authored — which
is why the front matter has drifted (§3.2). Replace it with the real shape:

```markdown
+++
title = '{{ replace .File.ContentBaseName "-" " " | title }}'
date = '{{ .Date }}'
draft = true
weight = 0
categories = ['Acrylic on Canvas']
description = ''
dimensions = '(00 cm X 00 cm)'
[[resources]]
  src = ''
+++
```

Adding a painting becomes: `hugo new content/<slug>/index.md`, drop the image in, fill four
fields.

### 3.2 Normalize and then *enforce* front matter

Current state across the 47 artworks:

- **3 missing `dimensions`** entirely (`mosaic-coasters`, `peace-stool`, `staircase`), so those
  pages render without the caption every other page has.
- **Format drift** in the rest: `(91 cm x 61 cm)` vs `(91 cm X 61 cm)`, `46 cm Diameter` with
  no parentheses, `12" Diameter` in inches among 40+ metric entries.

Canonical caption format: parentheses with an uppercase `X` separator — `(92 cm X 61 cm)`,
`(46 cm Diameter)`. Five files were normalized to it.

`scripts/check-content.py` now enforces this, split deliberately between hard failures and
nudges so that content gaps can never block a deploy:

- **Errors** (fail CI): missing `title`/`date`/`categories`; a `resources` entry naming a file
  that isn't in the bundle; a bundle with no image; malformed `dimensions`.
- **Warnings** (report only): missing `dimensions`, empty `description`, inch-based dimensions.
  These need the artist's input — a script must not invent them, and must not block on them.

**It justified itself immediately:** on first run it found a *third* broken resource declaration
I had missed by reading — `content/ganeshas-blessings/index.md` declared
`Ganeshas-Blessings.jpg` while the file on disk is `Ganeshas-Blessings.jpeg`. It also found two
artworks whose `description` key is present but empty, which a `grep` for the key cannot see.

Current state: **47 bundles, 0 errors, 7 warnings.** The 7 are listed in §8 for you to resolve.

### 3.3 A Makefile that works

The current one has a single `sync` target hardcoding
`/Users/Vivekanand.balakrishnan/per/projects/...` — it cannot work for anyone else, and won't
work on this Linux checkout either. Replace with the commands actually used:

Implemented targets (`make` with no argument lists them):

| Target | Does |
| --- | --- |
| `make serve` | `hugo server -D` — dev server with drafts |
| `make build` | `hugo --minify --gc` into `./public` |
| `make check` | validator + a build with `--printPathWarnings`; what CI runs |
| `make new SLUG=my-painting` | scaffolds the bundle from the §3.1 archetype |
| `make clean` | drops build output and the local variant cache |

There is no `images` target: §1.5 was not implemented, so there is nothing for it to do.

### 3.4 Add a PR check

There is **no `pull_request` workflow at all** — the only automation is deploy-on-merge to
`main`. Every PR so far has gone in unverified; a typo in front matter or a broken
resource reference reaches production before anyone notices. Add a lightweight job:
`make check` (build + content validation), no deploy. Reuse the §1.3 cache so it stays quick.

### 3.5 Move the inline `<style>` block into `custom.css`

`layouts/partials/gallery.html` ends with a ~30-line `<style>` block that is emitted into the
body of every page. `assets/css/custom.css` already holds the site's visual identity and is
compiled (and minified, and fingerprinted) via `main.scss`'s `@import "custom"`. Moving those
rules there gives one place to look for styling and lets them be cached with the stylesheet
instead of re-sent per page. Pure refactor; rendering is unchanged.

### 3.6 Resolve the theme provenance contradiction

`.gitmodules` declares `themes/gallery` as a submodule of `nicokaiser/hugo-theme-gallery`, but
85 theme files are committed directly and `git submodule status` returns nothing. Meanwhile CI
runs `submodules: recursive`, which is a no-op that looks meaningful. The vendored copy is
theme **v4.9.0** and has at least one local modification (`1a15017`, reordering home sections).

Vendoring a locally-patched theme is a defensible choice — but say so. Either:

- **Keep vendored (recommended):** delete `.gitmodules`, drop `submodules: recursive` from CI,
  and add `themes/gallery/UPSTREAM.md` recording v4.9.0, the upstream URL, and the local
  patches, so a future update is a reviewable diff rather than an archaeology project; or
- **Make it a real submodule** pinned to a tag, and move the local patches into `layouts/`
  overrides (where `single.html`, `head.html`, and `gallery.html` already live).

---

## 5. Considered and rejected

- **WebP / AVIF conversion.** Tested directly: `Olive.jpg` at a 1600 px fit came out
  **665 KB as WebP vs 568 KB as JPEG** at the same quality setting — WebP is *larger* for this
  material (dense, high-detail brushwork is close to the JPEG sweet spot). The theme also
  warns explicitly against WebP, citing level shifts on resize
  (`nicokaiser/hugo-theme-gallery#102`). No win, real risk: skip.
- **Rewriting git history** to shed the 561 MB pack (down to roughly 50 MB). Effective, but it
  requires a force-push and every existing clone must be re-cloned. §1.2 already fixes the CI
  and shallow-clone cost without it. Your call — I won't force-push.

---

## 6. Impact summary

Ordered by measured value, not by section number:

| # | Change | Effect | Risk | Effort |
| --- | --- | --- | --- | --- |
| **1.3** | Cache `resources/_gen` in CI | **build 197.6 s → 5.6 s** | none | S |
| **1.1** | Stop publishing originals | **site 140 MB → ~24 MB** | behaviour change (downloads) | 1 line |
| **1.2** | Remove `legacy/` from tree | **checkout 1497 MB → ~117 MB** | needs archive first | S |
| 2.1 | Harden `hugo.toml` | fixes timeout risk; +fidelity for 2.5 MB; author metadata | none | S |
| 1.4 | Drop dart-sass + npm steps | −20–40 s per deploy | none (verified) | XS |
| 2.2 | Fix dead resource declarations | correct OG image | none | XS |
| 2.3 | Align Hugo versions | removes 19-release drift | low | XS |
| 3.4 | Add a PR check | stops broken front matter reaching prod | none | S |
| 2.4 | Drop RSS *(optional)* | −25% of image conversions | removes feed | XS |
| 3.1–3.6 | Archetype, validation, Makefile, CSS consolidation, theme provenance | stops drift | none | M |
| 1.5 | Masters → 2000 px *(optional)* | sources 115.8 MB → 24.9 MB | measurable fidelity cost | M |

The top three are independent of each other, carry no design implications, and between them
take the deployed site from 140 MB to roughly 24 MB, the build from 197.6 s to 5.6 s, and CI's
per-run download to about 8% of what it is today.

---

## 7. Suggested sequencing

Small, reviewable PRs, in dependency order:

1. **`chore/ci-cache-and-slim-steps`** — §1.3 + §1.4. Pure win, no content touched, and it
   makes every later PR's CI run fast. Do this first.
2. **`chore/config-hardening`** — §2.1 + §2.2 + §2.3. Verify the OG image and one artwork page
   look right after the resampling change.
3. **`chore/archive-legacy`** — §1.2, *after* the archive exists and is verified.
4. **`perf/publish-no-originals`** — §1.1. Needs your decision on downloads first.
5. **`chore/maintainability`** — §3.1–§3.6, splittable; the PR check (§3.4) is worth pulling
   forward to right after step 1, since everything later benefits from it.
6. **`perf/downscale-masters`** — §1.5, only if you decide clone size warrants it, and only
   after the masters are archived. Include the delivered-image comparison in the PR description.

## 8. Open items

### Resolved

1. **`legacy/` location** — archived by git reference: tag `legacy-archive` at
   `8d0cf6e376da7eb0e482d328cda45b472408ef6b`, removed from the working tree, retrieval
   documented in [legacy-archive.md](legacy-archive.md).
2. **Full-resolution downloads** — masters are no longer published. This turned out to be
   near-costless: no page ever linked them (see the correction in §1.1).
3. **Masters left untouched** (§1.5) and **RSS kept** (§2.4).
4. **History rewrite** — not done. Available later if wanted; needs a force-push.

### Still needs the artist's input

The validator's 7 warnings. None block a build; all are content, not code:

| Artwork | Warning |
| --- | --- |
| `mosaic-coasters` | no `dimensions` — page renders without a size caption |
| `peace-stool` | no `dimensions` |
| `staircase` | no `dimensions`, and empty `description` |
| `pear-with-pink-background` | empty `description` — no subtext under the title |
| `ganeshas-blessings` | `(36 inch X 36 inch)` — inches, where the rest of the site uses cm |
| `mosaic-modern-ganesha` | `(12" Diameter)` — inches |

I deliberately did not convert the inch measurements or write the two missing descriptions:
both change what visitors read, and only the artist can decide them.

### Optional follow-up

- **Author metadata** — `params.author` is set but inert (§2.1). Emitting it needs ~2 lines in
  `single.html` or `opengraph.html`. Invisible to visitors, mildly useful for SEO.
- **Home page OpenGraph image** — the social-share card is the artist's portrait
  (`Priti_Ghatlia.jpg`), which is what the site already served; the declaration is now merely
  truthful rather than silently falling back. Switching it to a painting is a one-line change.
