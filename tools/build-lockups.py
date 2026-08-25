#!/usr/bin/env python3
"""Build the icon+name lockups used in the shared README footer.

The footer used to be an <img> next to a markdown link, which loses on two
counts: GitHub paints link text its own blue, and an image sitting on a text
baseline never lines up with the words beside it. Drawing both into one SVG
takes back control of the colour and makes the alignment exact.

Text is converted to outlines rather than left as <text>, so the lockup does
not depend on a font being installed on whoever is reading the README.

    python3 tools/build-lockups.py

Writes logos/lockups/<app>-light.svg and -dark.svg, one pair per app in
apps.json. Re-run after changing a name, a logo, or the type treatment.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer

ROOT = Path(__file__).resolve().parent.parent
LOGOS = ROOT / "logos"
OUT = LOGOS / "lockups"

# SF Rounded echoes the brando wordmark. Arial Bold is the fallback so this
# still runs somewhere without Apple's system fonts.
FONT_CANDIDATES = [
    (Path("/System/Library/Fonts/SFNSRounded.ttf"), 600),
    (Path("/System/Library/Fonts/SFCompactRounded.ttf"), 600),
    (Path("/Library/Fonts/Arial Bold.ttf"), None),
    (Path("/System/Library/Fonts/Supplemental/Arial Bold.ttf"), None),
]

ICON = 32          # icon box, and the lockup's full height
FONT_SIZE = 17.5   # cap height is centred on the icon's centre, not the baseline
GAP = 9            # space between icon and first glyph
PAD_RIGHT = 1

INK = {"light": "#1f2328", "dark": "#f0f6fc"}


def load_font() -> TTFont:
    for path, weight in FONT_CANDIDATES:
        if not path.exists():
            continue
        font = TTFont(str(path), fontNumber=0)
        if weight and "fvar" in font:
            axes = {a.axisTag for a in font["fvar"].axes}
            if "wght" in axes:
                font = instancer.instantiateVariableFont(font, {"wght": weight})
        return font
    sys.exit("No usable font found; install Arial Bold or run on macOS.")


def text_to_paths(font: TTFont, text: str, size: float) -> tuple[str, float, float, float]:
    """Return (svg path data, advance width, cap top, baseline drop) in px."""
    upem = font["head"].unitsPerEm
    scale = size / upem
    cmap = font.getBestCmap()
    glyphs = font.getGlyphSet()
    hmtx = font["hmtx"]

    parts: list[str] = []
    x = 0.0
    ymin = ymax = None

    for ch in text:
        name = cmap.get(ord(ch))
        if name is None:
            continue
        pen = SVGPathPen(glyphs)
        glyphs[name].draw(pen)
        d = pen.getCommands()
        if d:
            # Font units are y-up; SVG is y-down. Flip, then place at the pen x.
            parts.append(f'<path transform="translate({x * scale:.3f} 0) scale({scale:.6f} {-scale:.6f})" d="{d}" />')
            bounds = glyphs[name]._glyph.__dict__ if hasattr(glyphs[name], "_glyph") else None
        try:
            gb = font["glyf"][name] if "glyf" in font else None
            if gb is not None and gb.numberOfContours != 0:
                ymin = gb.yMin if ymin is None else min(ymin, gb.yMin)
                ymax = gb.yMax if ymax is None else max(ymax, gb.yMax)
        except Exception:
            pass
        x += hmtx[name][0]

    if ymax is None:  # CFF font: fall back to the declared cap height
        ymax = getattr(font["OS/2"], "sCapHeight", None) or int(upem * 0.7)
        ymin = 0

    return "".join(parts), x * scale, ymax * scale, (ymin or 0) * scale


def inner_svg(path: Path) -> tuple[str, str]:
    """Strip a logo's <svg> wrapper, keeping its contents and shape-rendering."""
    raw = path.read_text()
    m = re.search(r"<svg\b([^>]*)>(.*)</svg>", raw, re.S)
    if not m:
        sys.exit(f"{path} does not look like an SVG")
    attrs, body = m.group(1), m.group(2)
    rendering = ' shape-rendering="crispEdges"' if "crispEdges" in attrs else ""
    return body.strip(), rendering


def main() -> None:
    config = json.loads((ROOT / "apps.json").read_text())
    font = load_font()
    OUT.mkdir(parents=True, exist_ok=True)

    for app in config["apps"]:
        name = app["name"]
        body, rendering = inner_svg(LOGOS / Path(app["logo"]).name)
        d, advance, cap_top, _ = text_to_paths(font, name, FONT_SIZE)

        # Centre the cap height on the icon's centre line so the word sits
        # optically level with the icon rather than on a text baseline.
        baseline = ICON / 2 + cap_top / 2
        width = round(ICON + GAP + advance + PAD_RIGHT, 2)

        for mode, ink in INK.items():
            svg = (
                f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{ICON}" '
                f'viewBox="0 0 {width} {ICON}" fill="none" role="img" aria-label="{name}">\n'
                f"  <g{rendering}>{body}</g>\n"
                f'  <g transform="translate({ICON + GAP} {baseline:.3f})" fill="{ink}">{d}</g>\n'
                f"</svg>\n"
            )
            (OUT / f"{Path(app['logo']).stem}-{mode}.svg").write_text(svg)

        print(f"{name:8} {width:6.1f} x {ICON}")


if __name__ == "__main__":
    main()
