"""Extract images from source.pdf into ./assets/."""
import fitz, os, pathlib

src = pathlib.Path(__file__).parent / "source.pdf"
out = pathlib.Path(__file__).parent / "assets"
out.mkdir(exist_ok=True)

doc = fitz.open(src)
for page_index, page in enumerate(doc, start=1):
    images = page.get_images(full=True)
    for img_index, info in enumerate(images, start=1):
        xref = info[0]
        pix = fitz.Pixmap(doc, xref)
        if pix.n - pix.alpha > 3:  # CMYK -> RGB
            pix = fitz.Pixmap(fitz.csRGB, pix)
        name = f"page{page_index}_img{img_index}.png"
        pix.save(out / name)
        print(f"saved {name}  {pix.width}x{pix.height}")
        pix = None
print("done")
