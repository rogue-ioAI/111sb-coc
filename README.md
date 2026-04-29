# 111th Sustainment Brigade — Change of Command Program (2 May 2026)

Single-page mobile program for attendees to scan with a QR code at the entrance.

## What's in here

| Path | Purpose |
|------|---------|
| `index.html` | The program itself — schedule, history, outgoing/incoming bios |
| `assets/` | SSI, Prussian illustration, COL James photo |
| `sw.js`, `manifest.webmanifest` | Service worker (offline cache) + PWA manifest |
| `qr/qr.png`, `qr/qr.svg` | QR code (300dpi PNG, SVG) — **regenerate with real URL** |
| `print/scan_card_letter.pdf` | 8.5x11 entrance sign with QR + readable URL |
| `make_qr.py` | Regenerates the QR + decode-verifies with two libraries |
| `make_scan_card.py` | Regenerates the entrance sign |
| `extract_images.py`, `optimize_images.py` | One-shot scripts used to build the assets folder |
| `screenshot.py` | Phone-viewport visual QA (Playwright) |
| `source.pdf` | The corrected source program (gitignored — kept locally) |

## Regenerating the QR for the real URL

```
python make_qr.py https://YOURNAME.github.io/111sb-coc/
python make_scan_card.py https://YOURNAME.github.io/111sb-coc/
```

`make_qr.py` decodes the result with **pyzbar** and **OpenCV** before exiting.
If either fails, it exits non-zero — don't ship a QR that didn't pass.

## Hosting on GitHub Pages

1. Create a personal GitHub account (https://github.com/join).
2. Create a public repo named `111sb-coc`.
3. Push this folder.
4. Repo Settings -> Pages -> Source: `Deploy from a branch` -> Branch: `main` / `(root)` -> Save.
5. Wait ~60 sec; URL is `https://<username>.github.io/111sb-coc/`.
6. Open it on a phone in airplane mode after first load to confirm the service worker cached it.
7. Re-run `make_qr.py` and `make_scan_card.py` with the real URL.

## Taking it down after the ceremony

Repo Settings -> Pages -> Source -> `None` -> Save.
Or delete the repo entirely (Settings -> bottom of page -> Delete this repository).

## Notes on content

- The post-9/11 NCR claim has been removed from the history section per source-document review.
- COL Armijo did not provide a portrait photo; his section is text-only by design.
- 111th SB lineage detail beyond the source document was intentionally not added.
