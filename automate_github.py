"""End-to-end GitHub setup using the persistent browser profile.

Steps:
  1. Open Chromium with the persisted GitHub session.
  2. Verify the user is signed in (else fail loudly).
  3. Create repo `111sb-coc` (public).
  4. Mint a classic PAT (`repo` scope, 30-day expiry).
  5. Print the PAT to stdout for the next step (git push).
  6. Save a screenshot at each stage for visual QA.
"""
import pathlib, sys, time
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout

USERNAME = "rogue-ioAI"
REPO     = "111sb-coc"
PROFILE  = pathlib.Path(r"c:/Users/rogue/.claude/playwright-profile/github")
SHOTS    = pathlib.Path(__file__).parent / "_automation_shots"
SHOTS.mkdir(exist_ok=True)

def shot(page, name):
    page.screenshot(path=str(SHOTS/f"{name}.png"), full_page=False)
    print(f"  screenshot: {name}.png")

with sync_playwright() as p:
    ctx = p.chromium.launch_persistent_context(
        user_data_dir=str(PROFILE),
        headless=False,
        viewport={"width":1280,"height":860},
        args=["--disable-blink-features=AutomationControlled"],
    )
    page = ctx.pages[0] if ctx.pages else ctx.new_page()

    print("[1/5] Verifying signed-in state ...")
    page.goto("https://github.com/", wait_until="domcontentloaded")
    page.wait_for_timeout(1500)
    shot(page, "01_home")
    # Signed in if the user-menu avatar is present, OR /login is not in url
    if "/login" in page.url or page.locator('input[name="login"]').count():
        print("NOT SIGNED IN. Open the browser, log in, then re-run.")
        sys.exit(2)
    print(f"  OK -> {page.url}")

    print(f"[2/5] Creating repo {USERNAME}/{REPO} ...")
    page.goto("https://github.com/new", wait_until="domcontentloaded")
    page.wait_for_timeout(1500)
    # Fill name (current GitHub UI: id=repository-name-input)
    name_field = page.locator("input#repository-name-input").first
    name_field.wait_for(state="visible", timeout=20000)
    name_field.fill(REPO)
    page.wait_for_timeout(1500)  # let server-side name validation complete
    shot(page, "02_new_repo_form")
    # Submit
    create_btn = page.get_by_role("button", name="Create repository")
    create_btn.wait_for(state="visible", timeout=15000)
    create_btn.click()
    # Wait for redirect
    page.wait_for_url(f"https://github.com/{USERNAME}/{REPO}**", timeout=30000)
    page.wait_for_timeout(1500)
    shot(page, "03_repo_created")
    print(f"  OK -> {page.url}")

    print("[3/5] Generating classic PAT ...")
    page.goto("https://github.com/settings/tokens/new", wait_until="domcontentloaded")
    page.wait_for_timeout(1500)
    shot(page, "04_pat_form")
    # Note field
    page.locator("input#oauth_access_description, input[name='oauth_access[description]']").first.fill("claude-coc-deploy")
    # Expiration: 30 days
    try:
        page.locator("select#oauth_access_default_expires_at, select[name='oauth_access[default_expires_at]']").first.select_option(value="30")
    except Exception:
        pass
    # Scope: repo (top-level)
    page.locator("input[type=checkbox][value='repo']").first.check()
    shot(page, "05_pat_filled")
    page.get_by_role("button", name="Generate token").click()
    page.wait_for_url("**/settings/tokens**", timeout=30000)
    page.wait_for_timeout(1500)
    shot(page, "06_pat_generated")
    # Token appears as a code element on the success page
    token_el = page.locator("#new-oauth-token, code.token, [data-clipboard-text^='ghp_'], input[value^='ghp_']").first
    try:
        token_el.wait_for(state="visible", timeout=10000)
        token = token_el.get_attribute("value") or token_el.inner_text()
    except PWTimeout:
        token = ""
    if not token or "ghp_" not in token and "github_pat_" not in token:
        # Fallback: any element whose text starts with ghp_ or github_pat_
        for sel in ["text=/^ghp_[A-Za-z0-9]+/","text=/^github_pat_[A-Za-z0-9_]+/"]:
            try:
                token = page.locator(sel).first.inner_text(timeout=2000)
                if token: break
            except Exception:
                continue
    token = (token or "").strip()
    if not token:
        print("ERROR: could not capture PAT from the page. Inspect _automation_shots/06_pat_generated.png")
        sys.exit(3)
    print("  PAT captured (length:", len(token), ")")

    # Write to a sibling file (gitignored) for the next bash step
    out = pathlib.Path(__file__).parent / ".pat.tmp"
    out.write_text(token, encoding="utf-8")
    print(f"  Wrote: {out}  (delete me after push)")

    print("[4/5] Done with browser steps for now (Pages config after push).")
    shot(page, "07_done")
    ctx.close()

print("\nNEXT: git push, then re-run this script with --pages flag (we'll add) to enable Pages.")
