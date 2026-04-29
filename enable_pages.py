"""Enable GitHub Pages on rogue-ioAI/111sb-coc and wait for deploy.

Uses the GitHub REST API with the captured PAT.
"""
import pathlib, time, sys, json, urllib.request, urllib.error

ROOT = pathlib.Path(__file__).parent
PAT  = (ROOT / ".pat.tmp").read_text().strip()
USER = "rogue-ioAI"
REPO = "111sb-coc"
URL  = f"https://api.github.com/repos/{USER}/{REPO}/pages"

def req(method, url, body=None):
    data = None if body is None else json.dumps(body).encode()
    r = urllib.request.Request(url, data=data, method=method, headers={
        "Authorization": f"token {PAT}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "claude-coc-deploy",
        "Content-Type": "application/json",
    })
    try:
        with urllib.request.urlopen(r) as resp:
            return resp.status, json.loads(resp.read() or b"{}")
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read() or b"{}")

print("Creating Pages site (branch=main, path=/) ...")
status, body = req("POST", URL, {"source": {"branch": "main", "path": "/"}})
print(f"  -> {status}")
if status not in (201, 204, 409):  # 409 = already exists
    print("  body:", body); sys.exit(1)
if status == 409:
    print("  Pages already configured.")

print("\nWaiting for first deployment to go live ...")
public_url = None
for i in range(40):  # ~ up to 4 minutes
    time.sleep(6)
    s, b = req("GET", URL)
    print(f"  poll {i+1:02d}: status={s} build_status={b.get('status')!r} url={b.get('html_url')}")
    if b.get("status") == "built":
        public_url = b.get("html_url")
        break
    if s >= 400 and s != 404:
        print("  api error:", b); break

if not public_url:
    print("\nFirst build not yet 'built'. Page may still be building; check"
          f" https://github.com/{USER}/{REPO}/actions in a minute.")
else:
    print(f"\nLIVE: {public_url}")
