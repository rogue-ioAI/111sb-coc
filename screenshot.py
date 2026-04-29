"""Screenshot the program at multiple scroll positions for visual QA."""
from playwright.sync_api import sync_playwright
import pathlib

root = pathlib.Path(__file__).parent
url = (root / "index.html").as_uri()

with sync_playwright() as p:
    browser = p.chromium.launch()
    ctx = browser.new_context(viewport={"width":390,"height":844},
                              device_scale_factor=1,
                              user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X)")
    page = ctx.new_page()
    page.goto(url, wait_until="networkidle")
    sections = ["schedule-title","history-title","outgoing-title","incoming-title"]
    page.screenshot(path=str(root/"_preview_top.png"))
    for s in sections:
        page.evaluate(f"document.getElementById('{s}').scrollIntoView()")
        page.wait_for_timeout(200)
        page.screenshot(path=str(root/f"_preview_{s}.png"))
    print("section previews saved")
    browser.close()
