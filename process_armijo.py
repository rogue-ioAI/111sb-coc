"""Process COL Armijo OCP photo to match james.jpg style (165x177)."""
from PIL import Image, ImageOps

SRC = r"c:/Users/rogue/Downloads/Armijo - OCP.JPG"
DST = r"c:/Users/rogue/OneDrive/Desktop/Claude Code/111sb-coc/assets/armijo.jpg"

im = Image.open(SRC)
im = ImageOps.exif_transpose(im)
w, h = im.size
print("after exif:", im.size)

# Source is 4000x6000 portrait after exif transpose.
# Face is in the upper portion. Crop a head-and-shoulders square-ish region.
# Empirically tuned for this specific photo.
# Face center roughly at x=2000 (centered horizontally), y=1900 (upper third).
# Match james.jpg framing: top of head -> just below rank insignia.
# In 4000x6000: head top ~y=550, US ARMY tape ~y=2900, rank eagle ~y=3150.
top = 350
bottom = 3450
crop_h = bottom - top
crop_w = int(crop_h * 165 / 177)
cx = 2000
left = cx - crop_w // 2
right = left + crop_w
right = left + crop_w
bottom = top + crop_h
im2 = im.crop((left, top, right, bottom))
im2 = im2.resize((165, 177), Image.LANCZOS)
im2.save(DST, "JPEG", quality=85, optimize=True)
print("saved:", DST, im2.size)
