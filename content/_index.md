---
description: Online Gallery
#lastmod: 2023-07-05
title: Art by Priti
resources:
  # Must name a file in this directory (content/), not one inside a child bundle.
  # This previously said staircase.jpg, which lives in content/staircase/ and so
  # matched nothing; Hugo silently fell back to the image below anyway.
  - src: Priti_Ghatlia.jpg
    params:
      cover: true # cover of the home page is used for OpenGraph cards, etc.
menus:
  main:
    name: Home
    weight: -1
  footer:
    name: Home
    weight: 1
# sub-galleries on list pages are sorted by date and weight (descending)
# Don't copy the full-resolution masters into the published site. They were 116MB of a
# 140MB deploy and *zero* rendered pages referenced them — verified by grepping the
# built HTML — so they were reachable only by guessing a URL.
# Side effect: this also hides the lightbox download button, which offered the 1600px
# display variant (never the master).
cascade:
  build:
    publishResources: false
---
