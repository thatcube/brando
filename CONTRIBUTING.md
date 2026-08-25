# Maintaining this repo

`README.md` is the public brand page. This file is the maintenance manual.

## What's here

```
logos/                  App icons + the personal wordmark (light and dark)
apps.json               Source of truth: names, taglines, links, logos
repos.json              Every repo that carries the shared footer
footer.md               The generated footer block (committed so it can be diffed)
tools/sync-footer.mjs   Regenerates footer.md and rewrites every README
```

## Changing the footer

Edit **`apps.json`** — that is the only file to touch to rename an app, reword a
tagline, repoint a link, or add a fifth app.

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

1. Drop `logos/<app>.svg` in.
2. Add an entry to `apps.json`.
3. Add the repo to `repos.json`.
4. `node tools/sync-footer.mjs`
5. Commit here, then commit the touched READMEs in their own repos.
