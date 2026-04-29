"""Generate the program QR code (PNG + SVG) with SSI in the center,
then decode-verify with two independent libraries.

Usage:  python make_qr.py <URL>
        python make_qr.py https://yourname.github.io/111sb-coc/
"""
import sys, pathlib
import qrcode
from qrcode.constants import ERROR_CORRECT_H
from qrcode.image.svg import SvgPathImage
from PIL import Image

if len(sys.argv) < 2:
    print("ERROR: provide the URL.\n  python make_qr.py https://example.github.io/111sb-coc/")
    sys.exit(2)

URL = sys.argv[1].strip()
ROOT = pathlib.Path(__file__).parent
ASSETS = ROOT / "assets"
OUT = ROOT / "qr"
OUT.mkdir(exist_ok=True)

# Print resolution math:
# - QR border (quiet zone) of 4 modules required by spec.
# - Box size 30 px/module @ 300dpi gives a comfy print at >=2".
BOX = 30
BORDER = 4

# ---------- PNG ----------
qr = qrcode.QRCode(error_correction=ERROR_CORRECT_H, box_size=BOX, border=BORDER)
qr.add_data(URL)
qr.make(fit=True)
img = qr.make_image(fill_color="black", back_color="white").convert("RGB")

# Overlay SSI in center. With ECC=H, ~30% of the code can be obscured;
# we cover ~18% (linear ~22%) to stay well under that bound.
ssi = Image.open(ASSETS / "ssi.png").convert("RGBA")
W, H = img.size
overlay_w = int(W * 0.22)            # 22% of width
ssi_ratio = ssi.size[1] / ssi.size[0]
overlay_h = int(overlay_w * ssi_ratio)
ssi_resized = ssi.resize((overlay_w, overlay_h), Image.LANCZOS)
# White backing rectangle so SSI doesn't blend with QR modules
pad = max(8, BOX // 2)
bg_w, bg_h = overlay_w + pad*2, overlay_h + pad*2
bg = Image.new("RGB", (bg_w, bg_h), "white")
img.paste(bg, ((W - bg_w)//2, (H - bg_h)//2))
img.paste(ssi_resized, ((W - overlay_w)//2, (H - overlay_h)//2), ssi_resized)

png_path = OUT / "qr.png"
img.save(png_path, dpi=(300,300), optimize=True)
print(f"PNG saved: {png_path}  {img.size}  ({(W/300):.2f}\" at 300dpi)")

# ---------- SVG ----------
qr_svg = qrcode.QRCode(error_correction=ERROR_CORRECT_H, box_size=BOX, border=BORDER)
qr_svg.add_data(URL)
qr_svg.make(fit=True)
svg_img = qr_svg.make_image(image_factory=SvgPathImage)
svg_path = OUT / "qr.svg"
svg_img.save(str(svg_path))
print(f"SVG saved: {svg_path}")

# ---------- Verify with TWO independent libraries ----------
print("\n--- Decode verification ---")
ok = True

# 1) pyzbar (libzbar)
try:
    from pyzbar.pyzbar import decode as zbar_decode
    res = zbar_decode(Image.open(png_path))
    decoded = [r.data.decode() for r in res]
    if URL in decoded:
        print(f"[PASS] pyzbar -> {decoded[0]}")
    else:
        print(f"[FAIL] pyzbar -> {decoded}")
        ok = False
except Exception as e:
    print(f"[ERR ] pyzbar: {e}")
    ok = False

# 2) OpenCV QRCodeDetector
try:
    import cv2, numpy as np
    arr = np.array(Image.open(png_path).convert("RGB"))[:, :, ::-1]
    det = cv2.QRCodeDetector()
    data, pts, _ = det.detectAndDecode(arr)
    if data == URL:
        print(f"[PASS] opencv -> {data}")
    else:
        print(f"[FAIL] opencv -> {data!r}")
        ok = False
except Exception as e:
    print(f"[ERR ] opencv: {e}")
    ok = False

print("\nResult:", "OK -- both decoders match URL." if ok else "FAILED -- review QR.")
sys.exit(0 if ok else 1)
