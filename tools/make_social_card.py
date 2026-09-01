#!/usr/bin/env python3
"""Build the 1200x630 social-sharing card (assets/img/social-card.jpg).

Left: course title and dates in the site palette. Right: the circular photo of
Kent Kiehl, Vince Calhoun, and Tor Wager, on a soft amber/steel glow.
Run from the repository root:  python3 tools/make_social_card.py
"""
import os
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H = 1200, 630
BG, BG2 = (250, 248, 244), (233, 237, 240)
INK, INK2, MUTED = (28, 32, 38), (58, 64, 73), (100, 107, 117)
AMBER, AMBER_DEEP, STEEL = (233, 185, 73), (199, 147, 26), (111, 143, 176)

SERIF = "/System/Library/Fonts/Supplemental/Georgia.ttf"
SANS = "/System/Library/Fonts/HelveticaNeue.ttc"


# HelveticaNeue.ttc face indices: 0 Regular, 1 Bold, 10 Medium
REGULAR, BOLD, MEDIUM = 0, 1, 10


def sans(size, weight=REGULAR):
    return ImageFont.truetype(SANS, size, index=weight)


def tracked(d, xy, text, font, fill, track=0):
    """Draw text with extra letter-spacing (PIL has no tracking)."""
    x, y = xy
    for ch in text:
        d.text((x, y), ch, font=font, fill=fill)
        x += d.textlength(ch, font=font) + track
    return x


def main():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(root)

    # --- background: warm cream washing into cool steel toward the photo side
    card = Image.new("RGB", (W, H), BG)
    grad = Image.new("RGB", (W, H))
    gd = ImageDraw.Draw(grad)
    for x in range(W):
        t = (x / W) ** 1.25
        gd.line([(x, 0), (x, H)], fill=tuple(round(a + (b - a) * t) for a, b in zip(BG, BG2)))
    card.paste(grad, (0, 0))

    # soft amber glow behind the portrait
    glow = Image.new("RGB", (W, H), (0, 0, 0))
    ImageDraw.Draw(glow).ellipse([700, 40, 1220, 600], fill=(90, 68, 20))
    glow = glow.filter(ImageFilter.GaussianBlur(90))
    card = Image.blend(card, Image.blend(card, Image.new("RGB", (W, H), AMBER), 0.30), 0)
    card = Image.composite(Image.blend(card, Image.new("RGB", (W, H), (252, 240, 208)), 0.55), card,
                           glow.convert("L").point(lambda v: min(255, int(v * 2.2))))

    # --- portrait: circular crop of the group photo
    photo = Image.open("assets/img/instructors-group.jpg").convert("RGB")
    # the source is already a circle on white; crop to the disc, then re-mask cleanly
    pw, ph = photo.size
    side = min(pw, ph)
    photo = photo.crop(((pw - side) // 2, 0, (pw - side) // 2 + side, side))
    D = 430
    photo = photo.resize((D, D), Image.LANCZOS)
    mask = Image.new("L", (D * 4, D * 4), 0)
    ImageDraw.Draw(mask).ellipse([0, 0, D * 4 - 1, D * 4 - 1], fill=255)
    mask = mask.resize((D, D), Image.LANCZOS)
    px, py = 725, (H - D) // 2

    ring = Image.new("L", (W, H), 0)
    ImageDraw.Draw(ring).ellipse([px - 13, py - 13, px + D + 13, py + D + 13], fill=255)
    card = Image.composite(Image.new("RGB", (W, H), (255, 255, 255)), card, ring.filter(ImageFilter.GaussianBlur(2)))
    ring2 = Image.new("L", (W, H), 0)
    ImageDraw.Draw(ring2).ellipse([px - 5, py - 5, px + D + 5, py + D + 5], outline=255, width=3)
    card = Image.composite(Image.new("RGB", (W, H), AMBER), card, ring2)
    card.paste(photo, (px, py), mask)

    d = ImageDraw.Draw(card)

    # --- left column type
    x = 74
    d.line([(x, 118), (x + 34, 118)], fill=AMBER_DEEP, width=3)
    tracked(d, (x + 48, 105), "SEPT 9–11, 2026  ·  LIVE ONLINE", sans(20, MEDIUM), AMBER_DEEP, track=1.8)

    title = ImageFont.truetype(SERIF, 74)
    d.text((x, 158), "fMRI Acquisition", font=title, fill=INK)
    d.text((x, 244), "and Analysis", font=title, fill=INK)

    body = sans(25, 0)
    d.text((x, 358), "A three-day, hands-on course on the design,", font=body, fill=INK2)
    d.text((x, 394), "acquisition, and analysis of neuroimaging data.", font=body, fill=INK2)

    d.line([(x, 460), (x + 560, 460)], fill=(211, 207, 198), width=1)
    d.text((x, 484), "Vince Calhoun  ·  Kent Kiehl  ·  Tor Wager", font=sans(24, MEDIUM), fill=INK)
    d.text((x, 524), "torwager.github.io/mindfmricourse", font=sans(21, REGULAR), fill=MUTED)

    # dot accents echoing the home-page neuron network
    for i, (cx, cy, r, col) in enumerate([(646, 120, 5, AMBER), (676, 152, 3, STEEL), (628, 168, 3, STEEL)]):
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=col)

    out = "assets/img/social-card.jpg"
    card.save(out, quality=92, optimize=True, progressive=True)
    print("wrote", out, card.size, os.path.getsize(out) // 1024, "KB")


if __name__ == "__main__":
    main()
