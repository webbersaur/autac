#!/usr/bin/env python3
"""Add ProductGroup + BreadcrumbList schema to the four product hubs.

The hubs carried CollectionPage and FAQPage markup but nothing identifying them
as product ranges, which left Google with no structured signal that these pages
are commercial rather than editorial. Each hub now declares a ProductGroup with
its real published spec ranges as additionalProperty values.

Pricing is gated behind customer verification, so `offers` is deliberately
omitted rather than fabricated. See the same note in build-catalog.py.

Idempotent - re-running replaces the block between the markers. Run:

    python3 scripts/add-hub-product-schema.py
"""

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

BRAND = {"@type": "Brand", "name": "Autac USA"}
MANUFACTURER = {
    "@type": "Organization",
    "name": "Autac USA Inc.",
    "url": "https://autacusa.com/",
    "address": {
        "@type": "PostalAddress",
        "streetAddress": "25 Thompson Rd",
        "addressLocality": "Branford",
        "addressRegion": "CT",
        "postalCode": "06405",
        "addressCountry": "US",
    },
}


def prop(name: str, value: str) -> dict:
    return {"@type": "PropertyValue", "name": name, "value": value}


HUBS = {
    "coiled-cords": {
        "crumb": "Coiled Cords",
        "name": "Autac Coiled Cords",
        "alt": ["Coil Cords", "Coiled Cable", "Coiled Power Cords"],
        "description": (
            "UL-listed coiled cords and coil cords with heat-set helical geometry, "
            "including shielded EMI-protected cable, miniature cords for "
            "instrumentation, and heavy-gauge coiled power cable."
        ),
        "props": [
            ("Wire Gauge", "26 AWG to 10 AWG"),
            ("Conductors", "2 to 25"),
            ("Jacket Materials", "TPE, TPR, PVC, Auta-Prene, Neoprene"),
            ("Shielding", "Spiral serve, braided, foil with drain wire"),
            ("Extension Ratio", "Approximately 5:1"),
            ("Safety Listing", "UL Listed, UL Recognized, CUL"),
            ("Country of Origin", "Made in USA"),
        ],
        "varies": ["Wire Gauge", "Conductors", "Shielding"],
    },
    "curly-cords": {
        "crumb": "Curly Cords",
        "name": "Autac Curly Cords",
        "alt": ["Curly Cable", "Handset Cords", "Coiled Phone Cords"],
        "description": (
            "UL-listed curly cords for telephone handsets, headsets, dispatch "
            "radios, control panels, and Auta-Prene test leads, built on the same "
            "heat-set helical construction as our industrial retractile range."
        ),
        "props": [
            ("Wire Gauge", "28 AWG to 16 AWG"),
            ("Conductors", "2 to 12"),
            ("Jacket Materials", "PVC, Auta-Prene TPE"),
            ("Typical Applications", "Handsets, headsets, control panels, test leads"),
            ("Extension Ratio", "Approximately 5:1"),
            ("Safety Listing", "UL Listed, UL Recognized"),
            ("Country of Origin", "Made in USA"),
        ],
        "varies": ["Wire Gauge", "Conductors", "Jacket Materials"],
    },
    "retractile-cords": {
        "crumb": "Retractile Cords",
        "name": "Autac Retractile Cords",
        "alt": ["Retractile Power Cords", "Retractable Coiled Cords"],
        "description": (
            "UL and CUL listed retractile power cords in TPE, TPR, and PVC jackets, "
            "in 2 to 10 conductor configurations with 12 to 48 inch retracted "
            "lengths, plus custom retractile builds to specification."
        ),
        "props": [
            ("Wire Gauge", "26 AWG to 10 AWG"),
            ("Conductors", "2 to 10"),
            ("Retracted Lengths", "12 in to 48 in"),
            ("Jacket Materials", "TPE, TPR, PVC"),
            ("Voltage Rating", "Up to 600V"),
            ("Extension Ratio", "Approximately 5:1"),
            ("Safety Listing", "UL Listed, UL Recognized, CUL"),
            ("Country of Origin", "Made in USA"),
        ],
        "varies": ["Wire Gauge", "Conductors", "Retracted Lengths"],
    },
    "cord-sets": {
        "crumb": "Cord Sets",
        "name": "Autac Cord Sets",
        "alt": ["Cordsets", "Power Cord Assemblies", "Flexible Cord Sets"],
        "description": (
            "Flexible cord sets and cordsets assembled and tested as finished "
            "units, in straight, retractile, and shielded configurations with "
            "molded NEMA plugs and IEC connectors."
        ),
        "props": [
            ("Wire Gauge", "26 AWG to 10 AWG"),
            ("Conductors", "2 to 25"),
            ("Jacket Materials", "PVC, TPE, TPR, Neoprene"),
            ("Voltage Rating", "Up to 600V"),
            ("Amp Rating", "Up to 20A"),
            ("Plug Types", "NEMA 1-15P, 5-15P, 5-20P, 6-15P, 6-20P, Hospital Grade"),
            ("Connector Types", "IEC C13, C15, C19, stripped and tinned, ring terminals"),
            ("Safety Listing", "UL Listed, CUL, RoHS compliant options"),
            ("Country of Origin", "Made in USA"),
        ],
        "varies": ["Wire Gauge", "Conductors", "Plug Types"],
    },
}


def build(slug: str, spec: dict) -> str:
    url = f"https://autacusa.com/{slug}/"
    product_group = {
        "@context": "https://schema.org",
        "@type": "ProductGroup",
        "name": spec["name"],
        "alternateName": spec["alt"],
        "description": spec["description"],
        "url": url,
        "productGroupID": slug,
        "brand": BRAND,
        "manufacturer": MANUFACTURER,
        "variesBy": spec["varies"],
        "additionalProperty": [prop(n, v) for n, v in spec["props"]],
        "isSimilarTo": [
            {"@type": "ProductGroup", "name": HUBS[other]["name"],
             "url": f"https://autacusa.com/{other}/"}
            for other in HUBS
            if other != slug
        ],
    }
    breadcrumb = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home",
             "item": "https://autacusa.com/"},
            {"@type": "ListItem", "position": 2, "name": "Products",
             "item": "https://autacusa.com/products/"},
            {"@type": "ListItem", "position": 3, "name": spec["crumb"], "item": url},
        ],
    }
    out = []
    for payload in (product_group, breadcrumb):
        body = json.dumps(payload, indent=2, ensure_ascii=False)
        body = "\n".join("  " + line for line in body.splitlines())
        out.append(f'  <script type="application/ld+json">\n{body}\n  </script>')
    return "\n".join(out)


def main() -> None:
    for slug, spec in HUBS.items():
        path = ROOT / slug / "index.html"
        html = path.read_text(encoding="utf-8")
        block = (
            "  <!-- HUBSCHEMA:START -->\n"
            + build(slug, spec)
            + "\n  <!-- HUBSCHEMA:END -->\n"
        )

        pattern = re.compile(
            r"  <!-- HUBSCHEMA:START -->.*?  <!-- HUBSCHEMA:END -->\n", re.DOTALL
        )
        if pattern.search(html):
            html = pattern.sub(lambda _: block, html, count=1)
        else:
            if "</head>" not in html:
                sys.exit(f"no </head> in {slug}")
            html = html.replace("</head>", block + "</head>", 1)

        path.write_text(html, encoding="utf-8")
        print(f"  {slug}: ProductGroup + BreadcrumbList")


if __name__ == "__main__":
    main()
