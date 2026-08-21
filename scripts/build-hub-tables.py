#!/usr/bin/env python3
"""Pre-render the catalog tables on the four product hubs.

Why this exists
---------------
All four hubs used to build their catalog tables client-side from
catalog/data/products.json, so the HTML response carried "Loading product
data..." and not one catalog number. That is the same first-wave-crawl problem
that scripts/build-catalog.py fixed on /products/ (commit 0772520): Googlebot
indexes the response body, and the response body had no products in it.

The client-side templates were also rendering fields that do not exist in
products.json - category.extensionRatio and product.cableOD both came out as
"undefined", and `${p.ampRating}A` printed "7AA" because ampRating already
carries its unit. Pre-rendering fixes the crawl problem and the display bugs in
the same pass.

None of the hubs has filter UI (unlike /products/, which re-renders on every
filter change), so the tables are now static HTML with no JS behind them. The
fetch/render script blocks were deleted from the hub pages; do not add them back
- there is nothing for them to do, and a second renderer is how the markup
drifts out of sync.

Idempotent. Rewrites whatever sits between the markers:
    <!-- HUBTABLES:START -->  ... <!-- HUBTABLES:END -->    (coiled, curly, cord-sets)
    <!-- HUBROWS:<cat>:START --> ... <!-- HUBROWS:<cat>:END -->  (retractile tbodies)

Usage:
    python3 scripts/build-hub-tables.py            # rewrite the hubs
    python3 scripts/build-hub-tables.py --check     # exit 1 if anything is stale
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "catalog" / "data" / "products.json"

# Which hub owns which catalog categories. Together these cover all 10
# categories and all 25 part numbers exactly once.
HUBS: dict[str, dict] = {
    "retractile-cords/index.html": {
        "style": "rows",   # hand-written sections already on the page; fill the tbodies
        "categories": ["tpe-power", "tpr-power", "pvc-power", "tpe-power-bare"],
    },
    "coiled-cords/index.html": {
        "style": "sections",
        "categories": ["shielded-comm", "pvc-shielded", "pvc-miniature", "pvc-miniature-foil"],
    },
    "curly-cords/index.html": {
        "style": "sections",
        "categories": ["comm-control", "test-leads"],
    },
    "cord-sets/index.html": {
        "style": "platforms",   # summary of every cable platform a cord set can be built on
        "categories": None,
    },
}

# Short factual lead-ins for the generated sections. Specs come from
# products.json; this is framing only, so nothing here states a number.
CATEGORY_DESC: dict[str, str] = {
    "shielded-comm": (
        "Tinned-copper coiled cables with a shield for signal and data runs where EMI "
        "would otherwise couple into the conductors. TPE insulation and jacket."
    ),
    "pvc-shielded": (
        "Shielded PVC coiled cables for instrumentation and control circuits in "
        "electrically noisy environments."
    ),
    "pvc-miniature": (
        "Small-diameter coiled cords for handheld devices, panel wiring, and any "
        "assembly where a standard power cord will not fit."
    ),
    "pvc-miniature-foil": (
        "Miniature coiled cords with foil shielding, for low-level signal runs inside "
        "tight enclosures."
    ),
    "comm-control": (
        "Tinned-copper curly cords for telephone handsets, dispatch radios, headsets, "
        "and control-panel wiring."
    ),
    "test-leads": (
        "Curly test lead cords for meters, probes, and bench and field test equipment, "
        "where the cord has to stretch to the work and pull itself back out of the way."
    ),
}

# Which hub each category is documented on, for the cord-sets platform table.
CATEGORY_HUB: dict[str, str] = {
    "tpe-power": "/retractile-cords/",
    "tpr-power": "/retractile-cords/",
    "pvc-power": "/retractile-cords/",
    "tpe-power-bare": "/retractile-cords/",
    "shielded-comm": "/coiled-cords/",
    "pvc-shielded": "/coiled-cords/",
    "pvc-miniature": "/coiled-cords/",
    "pvc-miniature-foil": "/coiled-cords/",
    "comm-control": "/curly-cords/",
    "test-leads": "/curly-cords/",
}


def load() -> tuple[dict[str, dict], list[dict]]:
    data = json.loads(DATA.read_text())
    cats = {c["id"]: c for c in data["categories"]}
    return cats, data["products"]


def sort_products(products: list[dict]) -> list[dict]:
    """Thinner gauge first, then fewer conductors - the order the catalog uses."""
    return sorted(products, key=lambda p: (-int(p["awg"]), p["conductors"]))


def lengths(p: dict) -> str:
    return ", ".join(f'{l}"' for l in p["retractedLengths"])


def row(p: dict, listing: str, indent: str) -> str:
    return (
        f"{indent}<tr>\n"
        f'{indent}  <td><strong>{p["catNo"]}</strong></td>\n'
        f'{indent}  <td>{p["conductors"]}</td>\n'
        f'{indent}  <td>{p["awg"]}</td>\n'
        f'{indent}  <td>{p["type"]}</td>\n'
        f'{indent}  <td>{p["voltage"]}</td>\n'
        f'{indent}  <td>{p["ampRating"]}</td>\n'
        f"{indent}  <td>{lengths(p)}</td>\n"
        f"{indent}  <td>{listing}</td>\n"
        f"{indent}</tr>"
    )


def render_rows(cat: dict, products: list[dict], indent: str) -> str:
    return "\n".join(row(p, cat["listing"], indent) for p in sort_products(products))


def render_section(cat: dict, products: list[dict]) -> str:
    label = f'{cat["insulation"]} Insulation &bull; {cat["jacket"]} Jacket'
    shield = (
        '\n        <span class="product-meta-item"><strong>Shielding:</strong> Shielded</span>'
        if cat.get("shield")
        else ""
    )
    desc = CATEGORY_DESC.get(cat["id"], "")
    desc_html = f'\n        <p class="section-desc">{desc}</p>' if desc else ""
    count = len(products)
    noun = "part number" if count == 1 else "part numbers"
    return f"""  <section class="product-section" id="{cat['id']}">
    <div class="container">
      <div class="product-section-header">
        <div class="section-label">{label}</div>
        <div class="section-title" style="font-size:1.75rem;">{cat['name']}</div>{desc_html}
      </div>
      <div class="product-meta">
        <span class="product-meta-item"><strong>Conductor:</strong> {cat['conductor']}</span>
        <span class="product-meta-item"><strong>Insulation:</strong> {cat['insulation']}</span>
        <span class="product-meta-item"><strong>Jacket:</strong> {cat['jacket']}</span>
        <span class="product-meta-item"><strong>Listing:</strong> {cat['listing']}</span>{shield}
        <span class="product-meta-item"><strong>Stock:</strong> {count} {noun}</span>
      </div>
      <div class="product-table-wrap">
        <table class="product-table">
          <thead>
            <tr>
              <th>Cat. No.</th>
              <th>Cond.</th>
              <th>AWG</th>
              <th>UL Type</th>
              <th>Voltage</th>
              <th>Amps</th>
              <th>Retracted Lengths</th>
              <th>Listing</th>
            </tr>
          </thead>
          <tbody>
{render_rows(cat, products, '            ')}
          </tbody>
        </table>
      </div>
    </div>
  </section>"""


def render_platforms(cats: dict[str, dict], products: list[dict]) -> str:
    """Cord-sets: every cable platform an assembly can be built on."""
    rows = []
    for cid, cat in cats.items():
        items = [p for p in products if p["category"] == cid]
        if not items:
            continue
        nums = ", ".join(p["catNo"] for p in sort_products(items))
        hub = CATEGORY_HUB.get(cid, "/products/")
        rows.append(
            f"""            <tr>
              <td><strong><a href="{hub}">{cat['name']}</a></strong></td>
              <td>{cat['conductor']}</td>
              <td>{cat['insulation']}</td>
              <td>{cat['jacket']}</td>
              <td>{'Shielded' if cat.get('shield') else 'Unshielded'}</td>
              <td>{cat['listing']}</td>
              <td>{nums}</td>
            </tr>"""
        )
    total = len(products)
    return f"""  <section class="section" id="cord-set-platforms">
    <div class="container">
      <div class="section-label">Base Cable Platforms</div>
      <h2 class="section-title">What Your Cord Set Is Built On</h2>
      <p class="section-desc">Every Autac cord set starts from one of the cable platforms below. Pick the platform that matches your electrical and environmental requirements, tell us the terminations you need on each end, and we build the assembly to that spec. All {total} stock catalog numbers are listed here; custom constructions are built to print with no minimum order quantity.</p>
      <div class="product-table-wrap">
        <table class="product-table">
          <thead>
            <tr>
              <th>Platform</th>
              <th>Conductor</th>
              <th>Insulation</th>
              <th>Jacket</th>
              <th>Shielding</th>
              <th>Listing</th>
              <th>Stock Cat. Nos.</th>
            </tr>
          </thead>
          <tbody>
{chr(10).join(rows)}
          </tbody>
        </table>
      </div>
      <p class="section-desc">Retracted lengths, conductor counts, and amp ratings for each catalog number are listed on the <a href="/retractile-cords/">retractile cords</a>, <a href="/coiled-cords/">coiled cords</a>, and <a href="/curly-cords/">curly cords</a> pages.</p>
    </div>
  </section>"""


def replace_block(html: str, start: str, end: str, body: str, where: str) -> str:
    pattern = re.compile(re.escape(start) + r".*?" + re.escape(end), re.S)
    if not pattern.search(html):
        raise SystemExit(f"markers {start} / {end} not found in {where}")
    return pattern.sub(lambda _: f"{start}\n{body}\n{end}", html, count=1)


def build(check: bool) -> int:
    cats, products = load()
    stale = []

    for rel, conf in HUBS.items():
        path = ROOT / rel
        html = original = path.read_text()

        if conf["style"] == "rows":
            for cid in conf["categories"]:
                items = [p for p in products if p["category"] == cid]
                body = render_rows(cats[cid], items, "              ")
                html = replace_block(
                    html,
                    f"<!-- HUBROWS:{cid}:START -->",
                    f"<!-- HUBROWS:{cid}:END -->",
                    body,
                    rel,
                )
        elif conf["style"] == "sections":
            blocks = []
            for cid in conf["categories"]:
                items = [p for p in products if p["category"] == cid]
                if not items:
                    continue
                blocks.append(render_section(cats[cid], items))
            html = replace_block(
                html, "<!-- HUBTABLES:START -->", "<!-- HUBTABLES:END -->",
                "\n\n".join(blocks), rel,
            )
        else:
            html = replace_block(
                html, "<!-- HUBTABLES:START -->", "<!-- HUBTABLES:END -->",
                render_platforms(cats, products), rel,
            )

        if html != original:
            stale.append(rel)
            if not check:
                path.write_text(html)

    if check:
        if stale:
            print("stale: " + ", ".join(stale))
            return 1
        print("all hub tables up to date")
        return 0

    covered = sum(
        len([p for p in products if p["category"] == c])
        for conf in HUBS.values()
        for c in (conf["categories"] or [])
    )
    print(f"rewrote {len(stale) or 0} of {len(HUBS)} hubs; "
          f"{covered} of {len(products)} part numbers rendered into hub tables")
    for rel in stale:
        print(f"  updated {rel}")
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="report staleness, write nothing")
    sys.exit(build(ap.parse_args().check))
