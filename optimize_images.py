"""Resize and recompress images for fast mobile loading."""
from PIL import Image
import pathlib

a = pathlib.Path(__file__).parent / "assets"

# Prussian: oversize -> JPEG 1200w, q82
im = Image.open(a / "prussian.png").convert("RGB")
im.thumbnail((1200, 1200), Image.LANCZOS)
im.save(a / "prussian.jpg", "JPEG", quality=82, optimize=True, progressive=True)
print("prussian.jpg", (a / "prussian.jpg").stat().st_size, "bytes")

# SSI: keep as PNG (transparency), but downscale
im = Image.open(a / "ssi.png")
im.thumbnail((400, 400), Image.LANCZOS)
im.save(a / "ssi.png", "PNG", optimize=True)
print("ssi.png", (a / "ssi.png").stat().st_size, "bytes")

# James photo: small already, recompress
im = Image.open(a / "james.png").convert("RGB")
im.save(a / "james.jpg", "JPEG", quality=88, optimize=True, progressive=True)
print("james.jpg", (a / "james.jpg").stat().st_size, "bytes")

# Remove originals we replaced
(a / "prussian.png").unlink()
(a / "james.png").unlink()
print("done")
