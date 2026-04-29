"""Open the live URL in a phone viewport, screenshot, and verify."""
import pathlib
from playwright.sync_api import sync_playwright

URL  = "https://rogue-ioai.github.io/111sb-coc/"
ROOT = pathlib.Path(__file__).parent

with sync_playwright() as p:
    browser = p.chromium.launch()
    ctx = browser.new_context(viewport={"width":390,"height":844},
                              device_scale_factor=1,
                              user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X)")
    page = ctx.new_page()
    page.goto(URL, wait_until="networkidle", timeout=30000)
    page.screenshot(path=str(ROOT/"_live_top.png"))
    title = page.title()
    print("title:", title)
    # Verify the four section headings render
    for t in ["Schedule","History of the Change of Command","Outgoing Commander","Incoming Commander"]:
        ok = page.locator(f"text={t}").count() > 0
        print(f"  {'OK' if ok else 'FAIL'}: '{t}'")
    browser.close()
