"""
Images, read from the assets folder.
Tabler icons, glyphs of tabler-icons.ttf found in tabler-icons.css: https://tabler.io/icons lists them all.
"""

import base64
import io
import re
import sys
from functools import cache
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFont, ImageTk

# From source, the root is the root of the repository.
# In a a build, PyInstaller unpacks it into the folder named by sys._MEIPASS.
ROOT = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parents[3]))
ASSETS = ROOT / "assets"
ELEMENTS = ROOT / "scripts" / "_elements"
CSS_FILE = ELEMENTS / "tabler-icons.css"
FONT_FILE = ELEMENTS / "fonts" / "tabler-icons" / "tabler-icons.ttf"

# A rule of the CSS
RULE = re.compile(r'\.ti-([\w-]+):before\s*\{\s*content:\s*"\\([0-9a-f]+)"')

# The tick badge of an icon: its radius, its distance from the icon's centre (right and down)
# and the size of the tick inside it, in pixels
TICK_RADIUS = 8
TICK_OFFSET = 12
TICK_SIZE = 13
SMOOTHING = 4


def from_base64(encoded, width, height):
    """ The picture held by a base64 string, reduced to fit in a box of width by height pixels.
    Returns None when the string is not a picture. """
    try:
        picture = Image.open(io.BytesIO(base64.b64decode(encoded, validate=True)))
        picture.thumbnail((width, height))
        return ImageTk.PhotoImage(picture.convert("RGBA"))
    except (OSError, ValueError, Image.DecompressionBombError):
        return None


def load(name, height=None):
    """ Return the image from the image name, scaled to height pixels when a height is given. """
    image = Image.open(ASSETS / name)
    if height:
        width = round(image.width * height / image.height)
        image = image.resize((width, height), Image.Resampling.LANCZOS)
    return ImageTk.PhotoImage(image)


@cache
def glyphs():
    """ Every icon name with its character in the font, read from the CSS once. """
    css = CSS_FILE.read_text(encoding="utf-8")
    return {name: chr(int(code, 16)) for name, code in RULE.findall(css)}


@cache
def font(size):
    """ The font at a size in pixels, opened once for each size. """
    return ImageFont.truetype(str(FONT_FILE), size)


@cache
def icon_image(name, size, color, margin=0, tick=None):
    """
    The icon, in a #RRGGBB colour, as a Pillow image on a transparent background.
    Args:
        name (str): Tabler icon name
        size (int): Icon size in pixels
        color (str): Hex color
        margin (int): Transparent pixels added around
        tick (None|str): Disc color, tick color
    """
    try:
        glyph = glyphs()[name]
    except KeyError:
        raise ValueError(f"There is no Tabler icon named {name!r}") from None
    side = size + 2 * margin
    image = Image.new("RGBA", (side, side), (0, 0, 0, 0))
    ImageDraw.Draw(image).text((side / 2, side / 2), glyph, font=font(size), fill=color,
                               anchor="mm")
    if tick is None:
        return image

    disc_color, tick_color = tick
    centre = side / 2 + TICK_OFFSET

    def circle(radius):
        """ A mask of a smooth disc of this radius at the badge's place. """
        big = side * SMOOTHING
        mask = Image.new("L", (big, big), 0)
        box = [(centre - radius) * SMOOTHING, (centre - radius) * SMOOTHING,
               (centre + radius) * SMOOTHING, (centre + radius) * SMOOTHING]
        ImageDraw.Draw(mask).ellipse(box, fill=255)
        return mask.resize((side, side), Image.Resampling.LANCZOS)

    ring = circle(TICK_RADIUS + 2)
    image.putalpha(ImageChops.multiply(image.getchannel("A"), ImageChops.invert(ring)))

    # The disc, then the tick centred on it
    disc = Image.new("RGBA", (side, side), disc_color)
    disc.putalpha(circle(TICK_RADIUS))
    image = Image.alpha_composite(image, disc)
    mark = icon_image("check", TICK_SIZE, tick_color)
    image.alpha_composite(mark, (round(centre - TICK_SIZE / 2), round(centre - TICK_SIZE / 2)))
    return image


def load_icon(name, size, color, margin=0, tick=None):
    """ icon_image() as an image Tk can show. """
    return ImageTk.PhotoImage(icon_image(name, size, color, margin, tick))


@cache
def radio_image(size, colors, gap):
    """ A radio button.
    Args:
        size (int): Diameter of the circle in pixels
        colors (tuple): Hex colours of the inside, of the border and of the dot (None: no dot)
        gap (int): Transparent pixels on the right of the circle
    """
    fill, border, dot = colors
    big = size * SMOOTHING
    circle = Image.new("RGBA", (big, big), (0, 0, 0, 0))
    draw = ImageDraw.Draw(circle)
    draw.ellipse([0, 0, big - 1, big - 1], fill=border)
    draw.ellipse([SMOOTHING, SMOOTHING, big - 1 - SMOOTHING, big - 1 - SMOOTHING], fill=fill)
    if dot is not None:
        margin = big // 4
        draw.ellipse([margin, margin, big - 1 - margin, big - 1 - margin], fill=dot)
    image = Image.new("RGBA", (size + gap, size), (0, 0, 0, 0))
    image.paste(circle.resize((size, size), Image.Resampling.LANCZOS), (0, 0))
    return image


@cache
def check_box_image(size, colors, gap, mark="check"):
    """ A square box with a 1 pixel border, with a tick in it when a tick colour is given, as a
    Pillow image followed by a transparent gap before the text.
    Args:
        size (int): Side of the box in pixels
        colors (tuple): Hex colours of the inside, of the border and of the tick (None: no tick)
        gap (int): Transparent pixels on the right of the box
        mark (str): The Tabler icon drawn as the tick: "minus" for a box partly ticked
    """
    fill, border, tick = colors
    image = Image.new("RGBA", (size + gap, size), (0, 0, 0, 0))
    ImageDraw.Draw(image).rectangle([0, 0, size - 1, size - 1], fill=fill, outline=border)
    if tick is not None:
        image.alpha_composite(icon_image(mark, size, tick))
    return image
