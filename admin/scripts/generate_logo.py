"""Render a LEAPP tool's logo assets from its vector logo.

The same file sits in iLEAPP, ALEAPP, RLEAPP, VLEAPP, DLEAPP, GLEAPP and LAVA.
It finds the repository it runs in, reads that tool's vector master (``svg`` in
TOOLS below) and rewrites every raster the app, its reports and its README use:

    square   the tile at a fixed size (README, app window, report, web UI)
    banner   the tile extended into a rounded plate with the tool name beside
             it (GUI header and HTML report header), rendered once at 640 px
             tall and scaled to each height
    icns     the macOS app icon, every size rendered from the vector
    ico      the Windows icon, every size rendered from the vector

The plate color is the tile's own fill and its corner radius is the tile's, so
the banner reads as the icon with the name written on it. The name is set in
black to match the artwork's outlines.

To take a new logo from the designer, import it first:

    python <this script> --import path/to/NEW.svg

An Inkscape export stores the tile as ``rx="0" ry="45.43"``. Inkscape draws
that rounded, but the SVG specification (and so every browser and librsvg)
treats a zero rx as square corners, so the import copies ry into rx. It also
drops images hidden with ``display:none`` (tracing layers), which never render.

Requires rsvg-convert (librsvg), Pillow, Arial Bold or Helvetica for the name,
and iconutil for the .icns (macOS only). Then run with no arguments:

    python <this script>
"""
import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile

from PIL import Image, ImageDraw, ImageFont

TOOLS = {
    "iLEAPP": {
        "marker": "ileappGUI.py",
        "svg": "assets/iLEAPP_logo.svg",
        "square": {"assets/icon.png": 256, "scripts/_elements/logo.png": 512},
        "banner": {"assets/iLEAPP_logo.png": 51, "scripts/_elements/iLEAPP_banner.png": 80},
        "icns": ["assets/icon.icns"],
        "ico": [],
    },
    "ALEAPP": {
        "marker": "aleappGUI.py",
        "svg": "assets/ALEAPP_logo.svg",
        "square": {"assets/icon.png": 256, "scripts/_elements/logo.png": 512},
        "banner": {"assets/ALEAPP_logo.png": 51, "scripts/_elements/ALEAPP_banner.png": 80},
        "icns": ["assets/icon.icns"],
        "ico": [],
    },
    "RLEAPP": {
        "marker": "rleappGUI.py",
        "svg": "assets/RLEAPP_logo.svg",
        "square": {"assets/icon.png": 256, "scripts/_elements/logo.png": 512},
        "banner": {"assets/RLEAPP_logo.png": 51, "scripts/_elements/RLEAPP_banner.png": 70},
        "icns": ["assets/icon.icns"],
        "ico": [],
    },
    "VLEAPP": {
        "marker": "vleappGUI.py",
        "svg": "assets/VLEAPP_logo.svg",
        "square": {"assets/icon.png": 256, "scripts/_elements/logo.png": 512},
        "banner": {"assets/VLEAPP_logo.png": 51, "scripts/_elements/VLEAPP_banner.png": 80},
        "icns": ["assets/icon.icns"],
        "ico": [],
    },
    "DLEAPP": {
        "marker": "dleappGUI.py",
        "svg": "assets/DLEAPP_logo.svg",
        "square": {"assets/DLEAPP_logo.png": 1024, "assets/icon.png": 256,
                   "scripts/_elements/logo.png": 512},
        "banner": {"assets/DLEAPP_banner.png": 640, "scripts/_elements/DLEAPP_banner.png": 640},
        "icns": ["assets/icon.icns"],
        "ico": [],
    },
    "GLEAPP": {
        "marker": "gleapp/__init__.py",
        "svg": "docs/images/gleapp-logo.svg",
        "square": {"docs/images/gleapp-logo.png": 256, "gleapp/web/static/gleapp-logo.png": 256,
                   "gleapp/web/static/favicon.png": 64},
        "banner": {},
        "icns": ["packaging/gleapp.icns"],
        "ico": ["packaging/gleapp.ico"],
    },
    "LAVA": {
        "marker": "src/renderer/App.jsx",
        "svg": "assets/LAVA_logo.svg",
        "square": {"assets/LAVA_icon_1024.png": 1024, "public/LAVA_icon_1024.png": 1024,
                   "src/renderer/public/LAVA_icon_1024.png": 1024},
        "banner": {},
        "icns": ["assets/lava.icns"],
        "ico": ["assets/lava.ico"],
    },
}

ICNS_SIZES = [16, 32, 128, 256, 512]          # each also rendered @2x
ICO_SIZES = [16, 24, 32, 48, 64, 128, 256]
BANNER_DESIGN_H = 640
INK = (0, 0, 0)
FONTS = ("/System/Library/Fonts/Supplemental/Arial Bold.ttf",
         "/Library/Fonts/Arial Bold.ttf",
         "/System/Library/Fonts/HelveticaNeue.ttc")

RECT_RE = re.compile(r"<rect\b[^>]*>")
IMAGE_RE = re.compile(r"<image\b[^>]*?/>", re.S)


def repo_root():
    """The first directory above this script that holds a .git entry."""
    here = os.path.dirname(os.path.abspath(__file__))
    while not os.path.exists(os.path.join(here, ".git")):
        parent = os.path.dirname(here)
        if parent == here:
            raise SystemExit("not inside a git checkout")
        here = parent
    return here


def this_tool(root):
    """The TOOLS entry whose marker file exists in root."""
    found = [name for name, spec in TOOLS.items()
             if os.path.exists(os.path.join(root, spec["marker"]))]
    if len(found) != 1:
        raise SystemExit(f"cannot tell which tool this repository is: {found or 'none'}")
    return found[0]


def _attr(tag, name):
    m = re.search(rf'\b{name}="([^"]*)"', tag)
    return m.group(1) if m else None


def view_width(svg):
    """The width of the SVG viewBox, in user units."""
    m = re.search(r'viewBox="\s*[-\d.]+\s+[-\d.]+\s+([\d.]+)\s+[\d.]+"', svg)
    if not m:
        raise SystemExit("the SVG has no viewBox")
    return float(m.group(1))


def tile_rect(svg):
    """The background tile: the one rect as wide as the viewBox."""
    width = view_width(svg)
    tiles = [t for t in RECT_RE.findall(svg)
             if _attr(t, "width") and abs(float(_attr(t, "width")) - width) < 0.01]
    if len(tiles) != 1:
        raise SystemExit(f"expected one full-width tile rect, found {len(tiles)}")
    return tiles[0], width


def tile_style(svg):
    """(fill color, corner radius as a fraction of the side) of the tile."""
    tile, width = tile_rect(svg)
    fill = re.search(r"fill:(#[0-9a-fA-F]{6})", tile)
    rx, ry = float(_attr(tile, "rx") or 0), float(_attr(tile, "ry") or 0)
    if not fill:
        raise SystemExit("the tile rect has no fill color")
    if rx == 0 or ry == 0:
        raise SystemExit("the tile has a zero corner radius and renders square outside "
                         "Inkscape; bring the file in with --import")
    color = tuple(int(fill.group(1)[i:i + 2], 16) for i in (1, 3, 5))
    return color, ry / width


def import_svg(src, dest):
    """Copy a designer SVG to the master path, rounding the tile and dropping
    images hidden with display:none."""
    with open(src, "r", encoding="utf-8") as fh:
        svg = fh.read()
    tile, _ = tile_rect(svg)
    ry = _attr(tile, "ry")
    if (_attr(tile, "rx") or "0") in ("0", "0.0") and ry:
        fixed = re.sub(r'\brx="[^"]*"', f'rx="{ry}"', tile) if _attr(tile, "rx") \
            else tile.replace("<rect", f'<rect rx="{ry}"', 1)
        svg = svg.replace(tile, fixed, 1)
    hidden = [i for i in IMAGE_RE.findall(svg) if "display:none" in i]
    for img in hidden:
        svg = svg.replace(img, "", 1)
    if "<image" in svg:
        raise SystemExit("the SVG still holds a visible or unparsed <image>; check it by hand")
    with open(dest, "w", encoding="utf-8", newline="") as fh:
        fh.write(svg)
    print(f"imported {src} -> {dest} ({len(hidden)} hidden image(s) dropped)")


def render(svg_path, size):
    """Render the SVG to a size x size RGBA image with rsvg-convert."""
    with tempfile.TemporaryDirectory() as tmp:
        out = os.path.join(tmp, "r.png")
        subprocess.run(["rsvg-convert", "-w", str(size), "-h", str(size), svg_path, "-o", out],
                       check=True)
        return Image.open(out).convert("RGBA").copy()


def save_png(img, root, rel):
    """Write img to root/rel as an optimized PNG."""
    path = os.path.join(root, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    img.save(path, optimize=True)
    print(f"wrote {rel} {img.size[0]}x{img.size[1]}")


def _font(size):
    """The first installed font in FONTS at the given size."""
    for path in FONTS:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    raise SystemExit(f"none of these fonts is installed: {', '.join(FONTS)}")


def make_banner(mark, name, color, radius_frac, height=BANNER_DESIGN_H):
    """The tile at the left of a plate of the tile's color, the name beside it."""
    font = _font(int(height * 0.59))
    box = ImageDraw.Draw(Image.new("RGBA", (4, 4))).textbbox((0, 0), name, font=font)
    text_x = height + int(height * 0.10)
    width = text_x + (box[2] - box[0]) + int(height * 0.14)

    plate = Image.new("RGBA", (width, height), color + (255,))
    mask = Image.new("L", (width, height), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, width - 1, height - 1],
                                           radius=round(height * radius_frac), fill=255)
    plate.putalpha(mask)
    banner = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    banner.alpha_composite(plate)
    banner.alpha_composite(mark.resize((height, height), Image.Resampling.LANCZOS), (0, 0))
    ImageDraw.Draw(banner).text((text_x, (height - (box[3] - box[1])) // 2 - box[1]), name,
                                font=font, fill=INK)
    return banner


def build_icns(svg_path, root, rel):
    """Pack every icon size, rendered from the vector, into a macOS .icns."""
    if not shutil.which("iconutil"):
        print(f"skip {rel} (iconutil is macOS only)")
        return
    with tempfile.TemporaryDirectory(suffix=".iconset") as work:
        for s in ICNS_SIZES:
            render(svg_path, s).save(os.path.join(work, f"icon_{s}x{s}.png"))
            render(svg_path, s * 2).save(os.path.join(work, f"icon_{s}x{s}@2x.png"))
        subprocess.run(["iconutil", "-c", "icns", work, "-o", os.path.join(root, rel)],
                       check=True)
    print(f"wrote {rel}")


def build_ico(svg_path, root, rel):
    """Write a Windows .ico holding every ICO_SIZES frame, rendered from the vector."""
    frames = [render(svg_path, s) for s in ICO_SIZES]
    frames[-1].save(os.path.join(root, rel), format="ICO",
                    sizes=[(s, s) for s in ICO_SIZES], append_images=frames[:-1])
    print(f"wrote {rel} {ICO_SIZES}")


def main():
    """Import a new master when asked, then render every output for this tool."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--import", dest="source", metavar="SVG",
                        help="copy a new designer SVG to the vector master first")
    args = parser.parse_args()

    if not shutil.which("rsvg-convert"):
        raise SystemExit("rsvg-convert (librsvg) is required")
    root = repo_root()
    name = this_tool(root)
    spec = TOOLS[name]
    svg_path = os.path.join(root, spec["svg"])
    if args.source:
        import_svg(args.source, svg_path)
    with open(svg_path, "r", encoding="utf-8") as fh:
        color, radius_frac = tile_style(fh.read())

    for rel, size in spec["square"].items():
        save_png(render(svg_path, size), root, rel)
    if spec["banner"]:
        banner = make_banner(render(svg_path, BANNER_DESIGN_H), name, color, radius_frac)
        for rel, height in spec["banner"].items():
            size = (round(banner.width * height / banner.height), height)
            save_png(banner.resize(size, Image.Resampling.LANCZOS), root, rel)
    for rel in spec["icns"]:
        build_icns(svg_path, root, rel)
    for rel in spec["ico"]:
        build_ico(svg_path, root, rel)
    print(f"{name}: done")


if __name__ == "__main__":
    sys.exit(main())
