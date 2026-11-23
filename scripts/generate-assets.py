#!/usr/bin/env python3
"""Generate GitHub-ready derivatives from the supplied branding originals.

Run from the repository root:

    python3 scripts/generate-assets.py

The files in assets/branding/originals/ are never modified. This script only
writes derived files. It requires Pillow and NumPy.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
ORIGINALS = ROOT / "assets" / "branding" / "originals"
OUT = ROOT / "assets" / "branding"


def rounded_mask(size: tuple[int, int], radius: float, scale: int = 4) -> Image.Image:
    """Antialiased rounded-rectangle mask."""
    w, h = size
    mask = Image.new("L", (w * scale, h * scale), 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle(
        (0, 0, w * scale - 1, h * scale - 1),
        radius=radius * scale,
        fill=255,
    )
    return mask.resize((w, h), Image.LANCZOS)


def save_rgba(image: Image.Image, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    image.convert("RGBA").save(path, optimize=True)


def extract_from_light_background(image: Image.Image) -> Image.Image:
    """Remove the near-white backdrop while preserving the original shading.

    The supplied card is not pure white (it has a gentle gradient), so a simple
    colour-to-alpha wipe leaves a visible rectangle. A narrow antialiasing band
    around a 238 cutoff removes the card cleanly without touching the mark.
    """
    rgb = np.asarray(image.convert("RGB"), dtype=np.uint8)
    alpha = np.clip((238 - rgb.min(axis=2).astype(np.float32)) / 8.0, 0.0, 1.0)
    out = np.zeros((*rgb.shape[:2], 4), dtype=np.uint8)
    out[..., :3] = rgb
    out[..., 3] = (alpha * 255).astype(np.uint8)
    return Image.fromarray(out, "RGBA")


def extract_from_dark_background(image: Image.Image, bg_luma: float = 15.0) -> Image.Image:
    """Turn the near-black backdrop of the simplified mark into transparency."""
    rgb = np.asarray(image.convert("RGB"), dtype=np.float32)
    luma = rgb.mean(axis=2)
    alpha = np.clip((luma - bg_luma) / (255.0 - bg_luma), 0.0, 1.0)
    out = np.zeros((*rgb.shape[:2], 4), dtype=np.uint8)
    out[..., :3] = 255
    out[..., 3] = (alpha * 255).astype(np.uint8)
    return Image.fromarray(out, "RGBA")


def recolor(image: Image.Image, rgb: tuple[int, int, int]) -> Image.Image:
    rgba = np.asarray(image.convert("RGBA")).copy()
    rgba[..., :3] = rgb
    return Image.fromarray(rgba, "RGBA")


def resize(image: Image.Image, width: int) -> Image.Image:
    height = round(image.height * width / image.width)
    return image.resize((width, height), Image.LANCZOS)


def square_with_padding(image: Image.Image) -> Image.Image:
    """Centre a nearly-square source on a square transparent canvas."""
    side = max(image.size)
    canvas = Image.new("RGBA", (side, side), (0, 0, 0, 0))
    canvas.alpha_composite(image, ((side - image.width) // 2, (side - image.height) // 2))
    return canvas


def main() -> None:
    banner = Image.open(ORIGINALS / "company-banner-original.png")
    icon = Image.open(ORIGINALS / "browser-icon-original.png")
    light = Image.open(ORIGINALS / "documentation-mark-light-original.png")
    watermark = Image.open(ORIGINALS / "watermark-original.png")

    # --- Company banner ---------------------------------------------------
    # Crop to the banner panel; its bottom edge is flush with the source frame.
    panel = banner.convert("RGB").crop((6, 20, 806, 458))  # 800 x 438

    # README hero: tighter crop around the logotype, soft rounded corners.
    hero = panel.crop((0, 39, 800, 399))  # 800 x 360, content stays centred
    hero = hero.resize((1600, 720), Image.LANCZOS).convert("RGBA")
    hero.putalpha(rounded_mask(hero.size, radius=40))
    save_rgba(hero, OUT / "company-banner" / "company-banner-1600x720.png")

    # Social preview: full panel, aspect-correct centre crop to 2:1, no stretch.
    social = panel.resize((1280, 701), Image.LANCZOS)
    social = social.crop((0, 30, 1280, 670))  # 1280 x 640
    social.convert("RGB").save(
        OUT / "company-banner" / "social-preview-1280x640.png", optimize=True
    )

    # --- Browser application icon ----------------------------------------
    # Trim the white presentation card and its drop shadow, keep the tile.
    tile = icon.convert("RGBA").crop((161, 118, 562, 521))  # 401 x 403
    tile.putalpha(rounded_mask(tile.size, radius=90))
    tile = square_with_padding(tile)
    for size in (512, 256, 128):
        save_rgba(
            resize(tile, size),
            OUT / "browser-icon" / f"browser-icon-{size}.png",
        )
    save_rgba(
        resize(tile, 180),
        OUT / "browser-icon" / "apple-touch-icon-180.png",
    )
    save_rgba(
        resize(tile, 32),
        OUT / "browser-icon" / "favicon-32.png",
    )

    # --- Documentation marks ---------------------------------------------
    light_mark = extract_from_light_background(light.crop((162, 151, 512, 468)))
    save_rgba(resize(light_mark, 512), OUT / "documentation" / "documentation-mark-light-512.png")

    dark_mark = extract_from_dark_background(watermark.crop((190, 181, 479, 459)))
    save_rgba(
        resize(dark_mark, 512),
        OUT / "documentation" / "documentation-mark-dark-512.png",
    )

    # --- Watermarks / small placements ------------------------------------
    white = extract_from_dark_background(watermark.crop((201, 193, 468, 447)))
    black = recolor(white, (17, 17, 17))
    for size in (512, 128):
        save_rgba(resize(white, size), OUT / "watermark" / f"watermark-light-{size}.png")
        save_rgba(resize(black, size), OUT / "watermark" / f"watermark-dark-{size}.png")

    # --- Organization avatar ----------------------------------------------
    # Circular-friendly mark on a dark field, echoing the supplied banner.
    canvas = Image.new("RGBA", (512, 512), (10, 10, 10, 255))
    glow = Image.new("L", (512, 512), 0)
    mark = resize(white, 300)
    mark_x = (512 - mark.width) // 2
    mark_y = (512 - mark.height) // 2
    glow.paste(mark.getchannel("A"), (mark_x, mark_y))
    glow = glow.filter(ImageFilter.GaussianBlur(26)).point(lambda p: round(p * 0.22))
    glow_layer = Image.new("RGBA", (512, 512), (150, 160, 190, 0))
    glow_layer.putalpha(glow)
    canvas = Image.alpha_composite(canvas, glow_layer)
    canvas.alpha_composite(mark, (mark_x, mark_y))
    save_rgba(canvas, OUT / "organization-avatar" / "organization-avatar-512.png")

    print("Branding derivatives written to", OUT)


if __name__ == "__main__":
    main()
