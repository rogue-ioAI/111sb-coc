"""Launch a headed, persistent Chromium so the user can log in to GitHub.
The profile is saved on disk so subsequent runs stay signed in.

Run:   python launch_browser.py
Then log in.  Close the window when finished, or just leave it open and
tell Claude you're signed in — Claude will reattach via the same profile.
"""
import pathlib, time
from playwright.sync_api import sync_playwright

PROFILE = pathlib.Path(r"c:/Users/rogue/.claude/playwright-profile/github")
PROFILE.mkdir(parents=True, exist_ok=True)

with sync_playwright() as p:
    ctx = p.chromium.launch_persistent_context(
        user_data_dir=str(PROFILE),
        headless=False,
        viewport={"width": 1280, "height": 860},
        args=["--disable-blink-features=AutomationControlled"],
    )
    page = ctx.pages[0] if ctx.pages else ctx.new_page()
    page.goto("https://github.com/login")
    print("Browser open. Log in to GitHub, then come back to Claude.")
    print("Profile dir:", PROFILE)
    # Keep alive until the user closes the window.
    try:
        while True:
            if not ctx.pages:
                break
            time.sleep(2)
    except KeyboardInterrupt:
        pass
    finally:
        ctx.close()
