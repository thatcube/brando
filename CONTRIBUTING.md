# Maintaining this repo

`README.md` is the public brand page. This file is the maintenance manual.

## What's here

```
logos/                    App icons + the personal wordmark (light and dark)
logos/lockups/            Generated icon+name lockups, light and dark
apps.json                 Source of truth: names, taglines, links, logos
repos.json                Every repo that carries the shared footer
footer.md                 The generated footer block (committed so it can be diffed)
tools/build-lockups.py    Draws the lockups from apps.json + logos/
tools/sync-footer.mjs     Regenerates footer.md and rewrites every README
```

## Renaming an app, or changing the type

The footer shows one **lockup** per app — icon and name drawn into a single
SVG — rather than an image next to a markdown link. That is deliberate: GitHub
paints link text its own blue and gives you no way to change it, and an image
sitting on a text baseline never lines up with the words beside it. Drawing
both together settles the colour and makes the alignment exact.

The name is converted to outlines, so it does not depend on a font being
installed on whoever is reading the README. Type is SF Rounded, which echoes
the brando wordmark, falling back to Arial Bold off macOS.

So after changing a **name** or a **logo**, rebuild the lockups before syncing:

```bash
python3 tools/build-lockups.py
node tools/sync-footer.mjs
```

Changing only a tagline, link, or the heading needs just the sync — taglines
are link tooltips, not drawn art.

## Changing the footer

Edit **`apps.json`** — that is the only file to touch to rename an app, reword a
tagline, repoint a link, or add a fifth app. If you changed a name or a logo,
run `python3 tools/build-lockups.py` first (see below).

```bash
node tools/sync-footer.mjs           # rewrite the footer in every repo
node tools/sync-footer.mjs --check   # CI-friendly: fail if a README is stale
node tools/sync-footer.mjs --print   # print the block, write nothing
node tools/sync-footer.mjs ../Plozz  # limit to one repo
```

Each README delimits its footer with `<!-- app-family:start -->` and
`<!-- app-family:end -->`. The script replaces only what sits between them, so
nothing above the markers is ever touched. A README without the markers gets the
block appended once.

The script assumes the sibling repos are checked out next to this one:

```
Development/
  brand/        <- this repo (thatcube/brando)
  Plozz/  Mozz/  hozz/  Twizz/  plozz-website/  ...
```

If yours live elsewhere, edit the paths in `repos.json`.

The footer is deliberately **table-free**. GitHub styles `<table>` cells with
borders and zebra striping, which renders as an opaque box behind every icon —
it looks like the logos have a background they don't have.

## Changing a logo

Replace the file in `logos/` and commit. **No README needs to change** — every
README references the logo by its `raw.githubusercontent.com` URL on `main`, so
new art appears everywhere as soon as it lands here.

Logos are 32×32 SVG pixel art with transparent backgrounds, rendered at 48px (an integer 1.5x, so the pixel grid stays clean).
The personal wordmark ships in two colours and is served through `<picture>` so
it stays legible on GitHub's light and dark themes.

## Adding a new app

1. Drop `logos/<app>.svg` in — 32x32 pixel art, transparent background.
2. Add an entry to `apps.json`.
3. Add the repo to `repos.json`.
4. `python3 tools/build-lockups.py && node tools/sync-footer.mjs`
5. Commit here, then commit the touched READMEs in their own repos.
