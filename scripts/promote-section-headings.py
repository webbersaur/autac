#!/usr/bin/env python3
"""Promote visual section headings to real <h2> elements.

Section headers across the site were marked up as <div class="section-title">,
so pages that *look* well structured shipped almost no heading outline - the
homepage, /solutions/ and several hubs had zero <h2> at all, while the blog
posts competing with them for the same head terms carry 8-10. This rewrites

    <div class="section-title">Coiled Cord Questions</div>
 -> <h2 class="section-title">Coiled Cord Questions</h2>

All .section-title CSS is class-based (no div.section-title selector anywhere)
and the rule sets its own font-size, weight, colour and margin, so the rendered
result is identical.

    python3 scripts/promote-section-headings.py
    python3 scripts/promote-section-headings.py --check   # exit 1 if any remain
"""

import argparse
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SKIP = {".git", "seo-reports", "node_modules"}

OPEN_RE = re.compile(r'<div class="section-title">(.*?)</div>', re.DOTALL)
# a section-title sitting inside an already-open heading would nest h2 in h2
NESTED_RE = re.compile(r"<h[1-6][^>]*>(?:(?!</h[1-6]>).)*$", re.DOTALL)


def pages():
    for path in sorted(REPO.rglob("*.html")):
        if path.relative_to(REPO).parts[0] in SKIP:
            continue
        yield path


def convert(html):
    out, last, count = [], 0, 0
    for m in OPEN_RE.finditer(html):
        if NESTED_RE.search(html[max(0, m.start() - 400):m.start()]):
            continue  # leave anything already inside a heading alone
        out.append(html[last:m.start()])
        out.append(f'<h2 class="section-title">{m.group(1)}</h2>')
        last = m.end()
        count += 1
    out.append(html[last:])
    return "".join(out), count


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()

    files = total = 0
    for path in pages():
        html = path.read_text(encoding="utf-8")
        new, n = convert(html)
        if not n:
            continue
        files += 1
        total += n
        if not args.check:
            path.write_text(new, encoding="utf-8")

    verb = "still using a div" if args.check else "promoted"
    print(f"{total} section heading(s) {verb} across {files} page(s)")
    return 1 if (args.check and total) else 0


if __name__ == "__main__":
    sys.exit(main())
