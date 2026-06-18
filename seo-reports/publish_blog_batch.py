#!/usr/bin/env python3
"""Publish the next batch of staged state blog posts.

Staggered-release mechanism for the 30 state blog posts (see project memory
"geo-SEO pages build pattern"). The post HTML files already live in the repo at
blog/<slug>/index.html but are intentionally NOT wired into discovery surfaces
(sitemap.xml, blog/index.html, the Request-Indexing worklist) so Google doesn't
see all 30 appear at once. Each run of this script "publishes" the next N posts
by stamping them with the real publish date and wiring them in.

Run from the repo root:
    python3 seo-reports/publish_blog_batch.py            # publish next batch, dated today
    python3 seo-reports/publish_blog_batch.py --dry-run  # show what would happen
    python3 seo-reports/publish_blog_batch.py --date 2026-06-22   # override date

It edits files only; committing + pushing is done by the caller (the scheduled
routine). When the queue is empty it exits 0 with "queue empty".
"""
import argparse, datetime, re, sys, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
QUEUE = os.path.join(ROOT, "seo-reports", "blog-publish-queue.txt")
SITEMAP = os.path.join(ROOT, "sitemap.xml")
INDEX = os.path.join(ROOT, "blog", "index.html")
WORKLIST = os.path.join(ROOT, "seo-reports", "request-indexing-priority.txt")
GRID_ANCHOR = '<div class="blog-grid">\n'
WORKLIST_HEADER = "# ---- Scheduled blog releases (staggered) ----"


def read_queue():
    batch = 3
    slugs = []
    with open(QUEUE) as f:
        for line in f:
            s = line.strip()
            if not s or s.startswith("#"):
                m = re.match(r"#?\s*BATCH_SIZE\s*=\s*(\d+)", s)
                if m:
                    batch = int(m.group(1))
                continue
            if s.startswith("BATCH_SIZE="):
                batch = int(s.split("=", 1)[1]); continue
            slugs.append(s)
    return batch, slugs


def write_queue(batch, remaining):
    lines = [
        "# Autac state blog posts — staggered publish queue.",
        "# Released by seo-reports/publish_blog_batch.py (run weekly by the scheduled routine).",
        "# One slug per line, in publish order. Remove nothing by hand — the script pops the top N.",
        "# When no slug lines remain, the routine is done.",
        f"BATCH_SIZE={batch}",
        "",
    ]
    lines += remaining
    with open(QUEUE, "w") as f:
        f.write("\n".join(lines) + ("\n" if remaining else ""))


def post_meta(slug):
    p = os.path.join(ROOT, "blog", slug, "index.html")
    if not os.path.exists(p):
        raise SystemExit(f"ERROR: staged post missing: blog/{slug}/index.html")
    h = open(p).read()
    headline = re.search(r'"headline":\s*"(.*?)"', h).group(1)
    desc = re.search(r'<meta name="description" content="(.*?)">', h, re.S).group(1)
    return p, h, headline, desc


def restamp(html, iso, human):
    html = re.sub(r'("datePublished":\s*")\d{4}-\d{2}-\d{2}(")', rf'\g<1>{iso}\g<2>', html, count=1)
    html = re.sub(r'(<span>Published )[^<]+(</span>)', rf'\g<1>{human}\g<2>', html, count=1)
    return html


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--date")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    d = datetime.date.fromisoformat(a.date) if a.date else datetime.date.today()
    iso = d.isoformat()
    human = f"{d.strftime('%B')} {d.day}, {d.year}"

    batch, slugs = read_queue()
    if not slugs:
        print("queue empty — all blog posts published. Nothing to do.")
        return 0
    todo = slugs[:batch]
    remaining = slugs[batch:]
    print(f"Publishing {len(todo)} post(s) dated {iso} ({human}); {len(remaining)} will remain.")

    idx = open(INDEX).read()
    sm = open(SITEMAP).read()
    cards, urls, work_lines = [], [], []
    for slug in todo:
        p, h, headline, desc = post_meta(slug)
        if f"/blog/{slug}/" in idx:
            print(f"  ! {slug} already wired into index — skipping wiring, still restamping")
        h2 = restamp(h, iso, human)
        cards.append(
            f'        <a href="/blog/{slug}/" class="blog-card">\n'
            f'          <div class="blog-card-meta">{human} &middot; Marie-Louise Burkle</div>\n'
            f'          <h3>{headline}</h3>\n'
            f'          <p>{desc}</p>\n'
            f'          <span class="read-more">Read more &rarr;</span>\n'
            f'        </a>\n')
        urls.append(
            f"  <url>\n    <loc>https://autacusa.com/blog/{slug}/</loc>\n"
            f"    <lastmod>{iso}</lastmod>\n    <priority>0.7</priority>\n  </url>\n")
        work_lines.append(f"https://autacusa.com/blog/{slug}/")
        print(f"  + {slug}  — {headline}")
        if not a.dry_run:
            open(p, "w").write(h2)

    if a.dry_run:
        print("\n--dry-run: no files changed.")
        return 0

    # blog index: newest-first, right after the grid opener
    assert idx.count(GRID_ANCHOR) == 1, "blog-grid anchor not found uniquely"
    idx = idx.replace(GRID_ANCHOR, GRID_ANCHOR + "".join(cards), 1)
    open(INDEX, "w").write(idx)

    # sitemap: before </urlset>
    assert sm.count("</urlset>") == 1
    sm = sm.replace("</urlset>", "".join(urls) + "</urlset>")
    open(SITEMAP, "w").write(sm)

    # worklist: append under a stable header
    w = open(WORKLIST).read().rstrip() + "\n"
    if WORKLIST_HEADER not in w:
        w += f"\n{WORKLIST_HEADER}\n"
    w += "".join(f"{u}    # released {iso}\n" for u in work_lines)
    open(WORKLIST, "w").write(w)

    write_queue(batch, remaining)
    print(f"\nDone. {len(remaining)} post(s) remain in the queue.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
