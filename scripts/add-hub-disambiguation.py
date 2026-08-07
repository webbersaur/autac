#!/usr/bin/env python3
"""Inject the cord-family disambiguation block into the three cord hubs.

Coiled, curly, and retractile are near-synonyms in this industry, and Google was
splitting the same queries across all three hubs: "coil cord" surfaced
/coiled-cords/ at position 28 AND /curly-cords/ at position 53, "coil cords"
surfaced both at 27 and 67, and neither ever broke through.

This block states, identically on all three pages, which page owns which term.
The current page is rendered as a non-linked "you are here" card so each page
declares its own scope, and the other two are linked with exact-match anchor
text so the intent flows to the right hub.

Idempotent - re-running replaces the block between the markers. Run:

    python3 scripts/add-hub-disambiguation.py
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# hub slug -> (insert-before marker, term it owns)
HUBS = {
    "coiled-cords": "<!-- EDUCATIONAL: WHAT IS A COILED CORD -->",
    "curly-cords": "<!-- WHY ARE PHONE CORDS CURLY -->",
    "retractile-cords": "<!-- TERMINOLOGY: RETRACTILE VS RETRACTABLE -->",
}

CARDS = [
    (
        "coiled-cords",
        "Coiled Cords",
        "Also called coil cords",
        "Industrial and signal coil cords: shielded multi-conductor cable, "
        "miniature cords for instrumentation, and heavy-gauge coiled power cable. "
        "Start here for any coil cord specified by gauge, conductor count, or shielding.",
    ),
    (
        "curly-cords",
        "Curly Cords",
        "Phone, headset, and test leads",
        "Curly cords for telephone handsets, dispatch radios, headsets, control "
        "panels, and Auta-Prene test leads. Start here when the cord attaches to a "
        "handset, a headset, or a meter.",
    ),
    (
        "retractile-cords",
        "Retractile Cords",
        "The UL term for the whole family",
        "UL-listed retractile power cords in TPE, TPR, and PVC, 2 to 10 conductors, "
        "with 12 to 48 inch retracted lengths. Start here for the full stock range "
        "and custom retractile builds.",
    ),
]

CSS = """
    /* === CORD FAMILY DISAMBIGUATION === */
    .cord-family {
      padding: 4rem 0;
      background: var(--gray-50);
      border-top: 1px solid var(--gray-100);
      border-bottom: 1px solid var(--gray-100);
    }

    .cord-family .section-desc { max-width: 720px; }

    .cord-family-grid {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 1.25rem;
      margin-top: 2rem;
    }

    .cord-family-card {
      display: block;
      background: var(--white);
      border: 1px solid var(--gray-200);
      border-radius: 10px;
      padding: 1.5rem;
      text-decoration: none;
      color: inherit;
      transition: border-color 0.2s, transform 0.2s, box-shadow 0.2s;
    }

    a.cord-family-card:hover {
      border-color: var(--red);
      transform: translateY(-2px);
      box-shadow: 0 6px 20px rgba(0,0,0,0.07);
    }

    .cord-family-card.current {
      background: var(--gray-100);
      border-color: var(--gray-300);
    }

    .cord-family-card h3 {
      font-size: 1.1rem;
      font-weight: 700;
      color: var(--black);
      margin-bottom: 0.2rem;
    }

    .cord-family-tag {
      display: block;
      font-size: 0.75rem;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 1px;
      color: var(--red);
      margin-bottom: 0.75rem;
    }

    .cord-family-card.current .cord-family-tag { color: var(--text-light); }

    .cord-family-card p {
      font-size: 0.92rem;
      line-height: 1.65;
      color: var(--text-light);
      margin: 0;
    }

    .cord-family-here {
      display: inline-block;
      margin-top: 0.9rem;
      font-size: 0.78rem;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 1px;
      color: var(--text-light);
    }

    .cord-family-go {
      display: inline-block;
      margin-top: 0.9rem;
      font-size: 0.85rem;
      font-weight: 600;
      color: var(--red);
    }

    @media (max-width: 860px) {
      .cord-family-grid { grid-template-columns: 1fr; }
    }
"""


def build_block(current: str) -> str:
    cards = []
    for slug, name, tag, desc in CARDS:
        if slug == current:
            cards.append(
                '        <div class="cord-family-card current">\n'
                f'          <span class="cord-family-tag">{tag}</span>\n'
                f"          <h3>{name}</h3>\n"
                f"          <p>{desc}</p>\n"
                '          <span class="cord-family-here">You are here</span>\n'
                "        </div>"
            )
        else:
            cards.append(
                f'        <a class="cord-family-card" href="/{slug}/">\n'
                f'          <span class="cord-family-tag">{tag}</span>\n'
                f"          <h3>{name}</h3>\n"
                f"          <p>{desc}</p>\n"
                f'          <span class="cord-family-go">See {name.lower()} &rarr;</span>\n'
                "        </a>"
            )
    return (
        '  <section class="cord-family">\n'
        '    <div class="container">\n'
        '      <div class="section-label">Which cord do you need?</div>\n'
        '      <h2 class="section-title">Coiled, Curly, or Retractile?</h2>\n'
        '      <p class="section-desc">These three names describe the same helical '
        "geometry, and the industry uses them interchangeably. Autac splits them by "
        "application so you land on the right stock range. Retractile is the term UL "
        "uses for the category as a whole.</p>\n"
        '      <div class="cord-family-grid">\n'
        + "\n".join(cards)
        + "\n      </div>\n"
        "    </div>\n"
        "  </section>\n"
    )


def inject(slug: str, before_marker: str) -> None:
    path = ROOT / slug / "index.html"
    html = path.read_text(encoding="utf-8")

    block = (
        "  <!-- CORD FAMILY:START -->\n"
        + build_block(slug)
        + "  <!-- CORD FAMILY:END -->\n\n"
    )

    # Replace an existing block, or insert before the marker on first run.
    existing = re.compile(
        r"  <!-- CORD FAMILY:START -->.*?  <!-- CORD FAMILY:END -->\n\n", re.DOTALL
    )
    if existing.search(html):
        html = existing.sub(lambda _: block, html, count=1)
    else:
        if before_marker not in html:
            sys.exit(f"marker not found in {slug}: {before_marker}")
        html = html.replace(before_marker, block + "  " + before_marker.strip(), 1)

    # CSS goes in once, right before the page's closing </style>.
    if "/* === CORD FAMILY DISAMBIGUATION === */" not in html:
        idx = html.index("</style>")
        html = html[:idx] + CSS + "  " + html[idx:]

    path.write_text(html, encoding="utf-8")
    print(f"  {slug}: block injected")


def main() -> None:
    for slug, marker in HUBS.items():
        inject(slug, marker)


if __name__ == "__main__":
    main()
