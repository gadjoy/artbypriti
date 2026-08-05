#!/usr/bin/env python3
"""Assert on the BUILT SITE, not on the build's exit code.

Constitution Principle I: a green build is not evidence of correctness. Hugo answers a
missing resource with a silent fallback, so every defect this repository has actually
shipped was invisible to `hugo`'s exit code. These assertions read `public/` and fail
loudly on output that is wrong despite a successful build.

Companion to check-content.py, which validates inputs. This validates results.

Usage:  python3 scripts/check-output.py [built_dir] [--content content_dir]
Exit:   0 = clean (warnings allowed), 1 = errors found
"""

import os
import re
import sys
from urllib.parse import urlparse, unquote

# Principle IV: the deployed site stays under 40MB. It is ~28MB today.
MAX_PAYLOAD_MB = 40
IMAGE_EXTS = (".jpg", ".jpeg", ".png")
# Hugo names every processed variant with an "_hu_<hash>" infix. Anything without it is
# an original copied verbatim.
DERIVED_MARKER = "_hu_"
NON_ARTWORK = {"about"}

errors = []
warnings = []
notes = []


def artworks_from_content(content_dir):
    """Map slug -> whether front matter promises a dimensions caption."""
    out = {}
    if not os.path.isdir(content_dir):
        return out
    for name in sorted(os.listdir(content_dir)):
        index = os.path.join(content_dir, name, "index.md")
        if not os.path.isfile(index) or name in NON_ARTWORK:
            continue
        fm = open(index, encoding="utf-8").read().split("\n---", 1)[0]
        m = re.search(r"^dimensions:[ \t]*(.*)$", fm, re.MULTILINE)
        out[name] = bool(m and m.group(1).strip())
    return out


def check_no_masters(built):
    """No full-resolution original may be published (Principle IV).

    Scoped to page-bundle output directories — those containing an index.html — because
    that is where Hugo copies bundle resources. Files under static/ (favicons, the touch
    icon) are legitimately copied verbatim and must not be flagged.
    """
    masters = [
        os.path.relpath(os.path.join(dp, fn), built)
        for dp, _, fns in os.walk(built)
        for fn in fns
        if fn.lower().endswith(IMAGE_EXTS)
        and DERIVED_MARKER not in fn
        and "index.html" in fns
    ]
    if masters:
        total = sum(os.path.getsize(os.path.join(built, m)) for m in masters) / 1048576
        errors.append(
            f"{len(masters)} full-resolution master(s) published ({total:.1f} MB) — "
            f"publishResources should prevent this. First: {masters[0]}"
        )
    else:
        notes.append("no full-resolution masters published")


def check_payload(built):
    total = sum(
        os.path.getsize(os.path.join(dp, fn))
        for dp, _, fns in os.walk(built)
        for fn in fns
    ) / 1048576
    if total > MAX_PAYLOAD_MB:
        errors.append(f"payload {total:.1f} MB exceeds the {MAX_PAYLOAD_MB} MB budget")
    else:
        notes.append(f"payload {total:.1f} MB (budget {MAX_PAYLOAD_MB} MB)")


def check_artwork_pages(built, artworks):
    """Every artwork must render a page, with an image, and with its caption."""
    missing_caption = []
    for slug, promises_dimensions in artworks.items():
        page = os.path.join(built, slug, "index.html")
        if not os.path.isfile(page):
            errors.append(f"artwork '{slug}' has no built page at {slug}/index.html")
            continue
        html = open(page, encoding="utf-8", errors="replace").read()

        if not re.search(r'<img[^>]+(?:data-src|src)=', html):
            errors.append(f"artwork page '{slug}' renders no image")

        has_caption = 'class=dimensions' in html or 'class="dimensions"' in html
        if promises_dimensions and not has_caption:
            errors.append(
                f"artwork page '{slug}' has dimensions in front matter but renders no caption"
            )
        elif not promises_dimensions:
            missing_caption.append(slug)

    if missing_caption:
        # Principle III: artist-authored content warns, never blocks.
        warnings.append(
            f"{len(missing_caption)} artwork(s) render no size caption because front matter "
            f"has no dimensions: {', '.join(sorted(missing_caption))}"
        )
    notes.append(f"{len(artworks)} artwork pages checked")


def check_expected_files(built):
    for rel in ("index.html", "about/index.html", "request/index.html", "sitemap.xml", "robots.txt"):
        if not os.path.exists(os.path.join(built, rel)):
            errors.append(f"expected output missing: {rel}")


def check_internal_links(built):
    """Every internal href/src must resolve to something in the built site."""
    checked = 0
    broken = {}
    for dp, _, fns in os.walk(built):
        for fn in fns:
            if not fn.endswith(".html"):
                continue
            page = os.path.join(dp, fn)
            html = open(page, encoding="utf-8", errors="replace").read()
            for m in re.finditer(r'(?:href|src|data-src)=["\']?([^"\'> ]+)', html):
                url = m.group(1)
                if url.startswith(("http://", "https://", "mailto:", "#", "data:", "//")):
                    continue
                checked += 1
                target = os.path.join(built, unquote(urlparse(url).path).lstrip("/"))
                if not (os.path.exists(target) or os.path.exists(os.path.join(target, "index.html"))):
                    broken.setdefault(url, os.path.relpath(page, built))
    for url, src in list(broken.items())[:10]:
        errors.append(f"broken internal link: {src} -> {url}")
    if len(broken) > 10:
        errors.append(f"...and {len(broken) - 10} more broken link(s)")
    notes.append(f"{checked} internal references resolved")


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    built = args[0] if args else "public"
    content = "content"
    if "--content" in sys.argv:
        content = sys.argv[sys.argv.index("--content") + 1]

    if not os.path.isdir(built):
        print(f"error: no built site at {built!r} — run a build first", file=sys.stderr)
        return 1

    artworks = artworks_from_content(content)
    if not artworks:
        print(f"error: no artwork bundles found under {content!r}", file=sys.stderr)
        return 1

    check_no_masters(built)
    check_payload(built)
    check_artwork_pages(built, artworks)
    check_expected_files(built)
    check_internal_links(built)

    for n in notes:
        print(f"ok:      {n}")
    for w in warnings:
        print(f"warning: {w}")
    for e in errors:
        print(f"ERROR:   {e}")

    print(f"\nchecked built site {built!r}: {len(errors)} error(s), {len(warnings)} warning(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
