#!/usr/bin/env python3
"""Announcement bar.

Inserts (or updates, or removes) a single banner immediately above the topbar.
The block is self-contained - markup plus its own <style> - between
<!-- SITENOTICE:START/END --> markers, so it can be re-run to change the wording
and pulled back out cleanly when the notice is over:

    python3 scripts/site-notice.py            # homepage only (default)
    python3 scripts/site-notice.py --all      # every page with a topbar
    python3 scripts/site-notice.py --remove   # take it down
    python3 scripts/site-notice.py --check    # exit 1 if anything is out of date

Every run sweeps ALL pages and strips the block from any page outside the
current scope, so narrowing the scope cleans up a wider previous run by itself.
Non-indexed pages (admin, invoices, proposals, reports) have no topbar and are
skipped automatically.
"""

import argparse
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

TARGETS = ["index.html"]  # scope when --all is not given

START = "<!-- SITENOTICE:START -->"
END = "<!-- SITENOTICE:END -->"

NOTICE = """  <!-- SITENOTICE:START -->
  <div class="sitenotice" role="status">
    <div class="container">
      <span class="sitenotice-tag">Service Notice</span>
      <p>Comcast is working on our phone and internet lines today (Thursday, September 3) and we may experience intermittent outages. If you can&rsquo;t reach us by phone, email <a href="mailto:sales@autacusa.com">sales@autacusa.com</a> or <a href="/quote/">send us a quote request</a> and we&rsquo;ll get right back to you.</p>
    </div>
  </div>
  <style>
    .sitenotice { background: #f5c518; color: #1a1a1a; padding: 0.6rem 0; font-size: 0.875rem; line-height: 1.45; }
    .sitenotice .container { display: flex; align-items: baseline; gap: 0.75rem; }
    .sitenotice p { margin: 0; }
    .sitenotice a { color: #1a1a1a; font-weight: 700; text-decoration: underline; }
    .sitenotice-tag { flex: none; font-weight: 800; text-transform: uppercase; letter-spacing: 0.04em; font-size: 0.7rem; background: #1a1a1a; color: #f5c518; padding: 0.2rem 0.5rem; border-radius: 3px; }
    @media (max-width: 640px) {
      .sitenotice .container { flex-direction: column; gap: 0.35rem; }
    }
  </style>
  <!-- SITENOTICE:END -->
"""

BLOCK_RE = re.compile(
    r"^[ \t]*" + re.escape(START) + r".*?" + re.escape(END) + r"\n?",
    re.DOTALL | re.MULTILINE,
)
# Insert above the "<!-- TOP BAR -->" comment when it is there, else above the bar itself.
ANCHOR_RE = re.compile(r"^([ \t]*)(<!-- TOP BAR -->\n[ \t]*)?<div class=\"topbar\">", re.MULTILINE)


def pages():
    for path in sorted(REPO.rglob("*.html")):
        rel = path.relative_to(REPO)
        if rel.parts[0] in {".git", "seo-reports", "node_modules"}:
            continue
        if '<div class="topbar">' not in path.read_text(encoding="utf-8"):
            continue
        yield path


def apply(html, remove):
    stripped = BLOCK_RE.sub("", html)
    if remove:
        return stripped
    match = ANCHOR_RE.search(stripped)
    if not match:
        return None
    return stripped[: match.start()] + NOTICE + stripped[match.start():]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--all", action="store_true", help="show the notice on every page, not just the homepage")
    ap.add_argument("--remove", action="store_true", help="strip the notice from every page")
    ap.add_argument("--check", action="store_true", help="report stale pages, write nothing")
    args = ap.parse_args()

    targets = {REPO / t for t in TARGETS}
    changed, skipped = [], []
    for path in pages():
        html = path.read_text(encoding="utf-8")
        # Anything outside the scope gets stripped, so a narrower scope cleans up
        # after a wider run.
        drop = args.remove or not (args.all or path in targets)
        out = apply(html, drop)
        if out is None:
            skipped.append(path)
            continue
        if out == html:
            continue
        changed.append(path)
        if not args.check:
            path.write_text(out, encoding="utf-8")

    for path in skipped:
        print(f"SKIP (no anchor): {path.relative_to(REPO)}", file=sys.stderr)

    verb = "stale" if args.check else ("cleaned" if args.remove else "updated")
    print(f"{len(changed)} page(s) {verb}")
    if args.check and changed:
        for path in changed[:20]:
            print(f"  {path.relative_to(REPO)}")
        return 1
    return 1 if skipped else 0


if __name__ == "__main__":
    sys.exit(main())
