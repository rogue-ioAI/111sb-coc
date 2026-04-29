import pathlib
from playwright.sync_api import sync_playwright

PROFILE = pathlib.Path(r"c:/Users/rogue/.claude/playwright-profile/github")
SHOTS   = pathlib.Path(__file__).parent / "_automation_shots"

with sync_playwright() as p:
    ctx = p.chromium.launch_persistent_context(
        user_data_dir=str(PROFILE), headless=False,
        viewport={"width":1280,"height":860})
    page = ctx.pages[0] if ctx.pages else ctx.new_page()
    page.goto("https://github.com/new", wait_until="domcontentloaded")
    page.wait_for_timeout(3500)
    page.screenshot(path=str(SHOTS/"02b_new_full.png"), full_page=True)
    # Dump every input/select/button visible on the page
    info = page.evaluate("""
      () => {
        const out = [];
        for (const el of document.querySelectorAll('input,select,button,textarea')) {
          const r = el.getBoundingClientRect();
          if (r.width===0 && r.height===0) continue;
          out.push({
            tag: el.tagName.toLowerCase(),
            type: el.type || null,
            id: el.id || null,
            name: el.getAttribute('name'),
            placeholder: el.getAttribute('placeholder'),
            ariaLabel: el.getAttribute('aria-label'),
            text: (el.innerText || '').trim().slice(0,80) || null,
            visible: r.top < 1500
          });
        }
        return out;
      }""")
    for x in info:
        print(x)
    ctx.close()
