"""Generate the 8.5x11 entrance sign as a print-ready PDF.

Layout (portrait):
   - Brigade SSI at top
   - Title block
   - Large QR (~5.5") centered
   - Scan instruction line
   - Plain readable URL below QR
   - Footer

Usage:  python make_scan_card.py <URL>
"""
import sys, pathlib
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from PIL import Image

if len(sys.argv) < 2:
    print("ERROR: provide the URL.\n  python make_scan_card.py https://example.github.io/111sb-coc/")
    sys.exit(2)

URL = sys.argv[1].strip()
ROOT = pathlib.Path(__file__).parent
ASSETS = ROOT / "assets"
QR_PNG = ROOT / "qr" / "qr.png"
OUT = ROOT / "print" / "scan_card_letter.pdf"
OUT.parent.mkdir(exist_ok=True)

# Fonts: try to register a Garamond/serif if present on Windows; fall back to Times.
SERIF = "Times-Roman"
SERIF_BOLD = "Times-Bold"
for name, path in [
    ("EBGaramond",      r"C:\Windows\Fonts\GARA.TTF"),
    ("EBGaramond-Bold", r"C:\Windows\Fonts\GARABD.TTF"),
]:
    try:
        if pathlib.Path(path).exists():
            pdfmetrics.registerFont(TTFont(name, path))
    except Exception:
        pass
if "EBGaramond" in pdfmetrics.getRegisteredFontNames():
    SERIF = "EBGaramond"
if "EBGaramond-Bold" in pdfmetrics.getRegisteredFontNames():
    SERIF_BOLD = "EBGaramond-Bold"

W, H = LETTER  # 612 x 792 points

c = canvas.Canvas(str(OUT), pagesize=LETTER)
c.setTitle("111SB Change of Command — Scan for Program")
c.setAuthor("111th Sustainment Brigade")

# Accent bar at top (brigade red / gold)
bar_h = 12
c.setFillColor(HexColor("#a01e1e")); c.rect(0, H-bar_h, W/2, bar_h, fill=1, stroke=0)
c.setFillColor(HexColor("#e6b324")); c.rect(W/2, H-bar_h, W/2, bar_h, fill=1, stroke=0)

# SSI top center
ssi_w = 1.1*inch
ssi = Image.open(ASSETS/"ssi.png")
ssi_h = ssi_w * (ssi.size[1]/ssi.size[0])
c.drawImage(str(ASSETS/"ssi.png"),
            (W-ssi_w)/2, H - bar_h - 0.45*inch - ssi_h,
            width=ssi_w, height=ssi_h, mask="auto")

# Title block
c.setFillColor(HexColor("#1b1b1b"))
y = H - bar_h - 0.45*inch - ssi_h - 0.45*inch
c.setFont(SERIF_BOLD, 28); c.drawCentredString(W/2, y, "Change of Command Ceremony")
y -= 0.42*inch
c.setFont(SERIF, 18); c.drawCentredString(W/2, y, "111th Sustainment Brigade")
y -= 0.28*inch
c.setFont(SERIF, 14); c.drawCentredString(W/2, y, "2 May 2026")

# Scan instruction
y -= 0.55*inch
c.setFont(SERIF_BOLD, 22); c.drawCentredString(W/2, y, "Scan for the full program")

# QR
qr_size = 4.6*inch
qr_x = (W - qr_size)/2
qr_y = y - 0.35*inch - qr_size
c.drawImage(str(QR_PNG), qr_x, qr_y, width=qr_size, height=qr_size,
            preserveAspectRatio=True, mask="auto")

# Light frame around QR (helps the eye lock onto the code)
c.setStrokeColor(HexColor("#bfb9a8")); c.setLineWidth(0.6)
pad = 6
c.rect(qr_x-pad, qr_y-pad, qr_size+2*pad, qr_size+2*pad, fill=0, stroke=1)

# Readable URL
c.setFillColor(HexColor("#3a3a3a"))
c.setFont(SERIF, 11)
c.drawCentredString(W/2, qr_y - 0.45*inch, "Or visit:")
c.setFont(SERIF_BOLD, 14)
c.setFillColor(HexColor("#1b1b1b"))
c.drawCentredString(W/2, qr_y - 0.70*inch, URL)

# Footer
c.setFont(SERIF, 9); c.setFillColor(HexColor("#3a3a3a"))
c.drawCentredString(W/2, 0.45*inch,
    "111th Sustainment Brigade  -  New Mexico Army National Guard  -  Rio Rancho, NM")

c.showPage()
c.save()
print(f"Saved: {OUT}")
