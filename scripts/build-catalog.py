#!/usr/bin/env python3
"""Pre-render the product catalog into products/index.html.

The catalog used to be built entirely in the browser from
catalog/data/products.json, which meant Googlebot's first-wave crawl saw
"Loading product catalog..." and nothing else - no category names, no part
numbers, no specs. This script emits the same markup buildCard()/renderProducts()
produce in products/index.html and injects it between the CATALOG markers, so
the page ships complete in the HTML response. The JS still owns filtering and
re-renders from the same JSON on any filter change.

Never hand-edit between the markers - edit catalog/data/products.json, then:

    python3 scripts/build-catalog.py

Markers:
  <!-- CATFILTER:START --> / <!-- CATFILTER:END -->  category <select> options
  <!-- CATALOG:START -->   / <!-- CATALOG:END -->    category sections + cards
  <!-- CATCOUNT:START -->  / <!-- CATCOUNT:END -->   "Showing N products"
  <!-- CATSCHEMA:START --> / <!-- CATSCHEMA:END -->  ItemList of ProductGroups

Pricing is gated behind customer verification, so the schema deliberately omits
`offers`. Search Console will flag the missing field as a non-critical warning;
that is correct and expected for a catalog without public pricing. Publishing a
fabricated price to silence the warning would be worse than the warning.
"""

import json
import re
import sys
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "catalog" / "data" / "products.json"
PAGE = ROOT / "products" / "index.html"

# Mirrors the categoryMeta object in products/index.html. Keep in sync.
CATEGORY_META = {
    "tpe-power": ("badge-power", "Power Cord"),
    "tpr-power": ("badge-power", "Power Cord"),
    "pvc-power": ("badge-power", "Power Cord"),
    "tpe-power-bare": ("badge-power", "Power Cord"),
    "comm-control": ("badge-comm", "Communications"),
    "test-leads": ("badge-comm", "Test Lead"),
    "shielded-comm": ("badge-shielded", "Shielded"),
    "pvc-shielded": ("badge-shielded", "Shielded"),
    "pvc-miniature": ("badge-mini", "Miniature"),
    "pvc-miniature-foil": ("badge-mini", "Miniature"),
}

LOCKED_PRICE = (
    '<span class="price-locked" onclick="openPricingModal()">'
    "&#128274; Unlock pricing</span>"
)


def attr(value: str) -> str:
    return escape(str(value), quote=True)


def text(value: str) -> str:
    return escape(str(value), quote=False)


def build_description(category: dict) -> str:
    parts = []
    if category.get("conductor"):
        parts.append(f"{category['conductor']} conductor")
    if category.get("insulation"):
        parts.append(f"{category['insulation']} insulation")
    if category.get("jacket"):
        parts.append(f"{category['jacket']} jacket")
    if category.get("shield"):
        parts.append("Shielded")
    return ". ".join(parts) + "."


def search_blob(product: dict, category: dict) -> str:
    return " ".join(
        str(x)
        for x in (
            product["catNo"],
            f"{product['awg']} AWG",
            f"{product['conductors']} conductor",
            product["type"],
            product["voltage"],
            category.get("name", ""),
            category.get("jacket", "") or "",
            category.get("insulation", "") or "",
            product["ampRating"],
        )
    ).lower()


def spec(label: str, value: str) -> str:
    return (
        '<div class="product-spec">'
        f'<span class="product-spec-label">{text(label)}</span>'
        f'<span class="product-spec-value">{text(value)}</span>'
        "</div>"
    )


def build_card(product: dict, category: dict) -> str:
    badge, kind = CATEGORY_META.get(product["category"], ("badge-power", "Cord"))
    lengths = ", ".join(f'{n}"' for n in product.get("retractedLengths", []))
    listing = category.get("listing") or "N/A"

    specs = "".join(
        [
            spec("Gauge", f"{product['awg']} AWG"),
            spec("Conductors", product["conductors"]),
            spec("Voltage", product["voltage"]),
            spec("Amp Rating", product["ampRating"]),
            spec("Lengths", lengths),
            spec("Listing", listing),
        ]
    )

    return (
        f'<div class="product-card" data-category="{attr(product["category"])}"'
        f' data-material="{attr((category.get("insulation") or "").upper())}"'
        f' data-search="{attr(search_blob(product, category))}">'
        '<div class="product-card-header">'
        f'<span class="product-card-badge {badge}">{text(kind)}</span>'
        f"<h3>Cat. {text(product['catNo'])} - {text(product['conductors'])}/"
        f"{text(product['awg'])} AWG {text(product['type'])}</h3>"
        "</div>"
        '<div class="product-card-body">'
        f'<p class="product-card-desc">{text(build_description(category))}</p>'
        f'<div class="product-specs">{specs}</div>'
        '<div class="product-card-footer">'
        f'<div class="product-price" data-catno="{attr(product["catNo"])}">'
        f"{LOCKED_PRICE}</div>"
        '<a href="/quote/" class="product-card-link">Request Quote &rarr;</a>'
        "</div></div></div>"
    )


def build_sections(data: dict) -> tuple[str, int]:
    by_id = {c["id"]: c for c in data["categories"]}
    grouped: dict[str, list] = {c["id"]: [] for c in data["categories"]}
    for product in data["products"]:
        if product["category"] in grouped:
            grouped[product["category"]].append(product)

    out, count = [], 0
    for cat in data["categories"]:
        products = grouped[cat["id"]]
        if not products:
            continue
        meta = " &bull; ".join(
            filter(
                None,
                [
                    text(cat.get("conductor", "")),
                    f"{text(cat.get('insulation', ''))} insulation",
                    f"{text(cat.get('jacket', ''))} jacket",
                    text(cat.get("listing", "")),
                ],
            )
        )
        cards = "".join(build_card(p, by_id[p["category"]]) for p in products)
        count += len(products)
        out.append(
            '      <div class="category-section">\n'
            '        <div class="category-header">\n'
            f"          <h2>{text(cat['name'])}</h2>\n"
            f"          <p>{meta}</p>\n"
            "        </div>\n"
            f'        <div class="product-grid">{cards}</div>\n'
            "      </div>"
        )
    return "\n".join(out), count


def build_schema(data: dict) -> str:
    """An ItemList of one ProductGroup per category, each carrying its real
    catalog numbers as variants with their published specs."""
    by_id = {c["id"]: c for c in data["categories"]}
    grouped: dict[str, list] = {c["id"]: [] for c in data["categories"]}
    for product in data["products"]:
        if product["category"] in grouped:
            grouped[product["category"]].append(product)

    brand = {"@type": "Brand", "name": "Autac USA"}
    items = []
    position = 0
    for cat in data["categories"]:
        products = grouped[cat["id"]]
        if not products:
            continue
        position += 1
        variants = []
        for p in products:
            props = [
                {"@type": "PropertyValue", "name": "Wire Gauge",
                 "value": f"{p['awg']} AWG"},
                {"@type": "PropertyValue", "name": "Conductors",
                 "value": str(p["conductors"])},
                {"@type": "PropertyValue", "name": "Cable Type", "value": p["type"]},
                {"@type": "PropertyValue", "name": "Voltage Rating",
                 "value": p["voltage"]},
                {"@type": "PropertyValue", "name": "Amp Rating",
                 "value": p["ampRating"]},
                {"@type": "PropertyValue", "name": "Retracted Lengths",
                 "value": ", ".join(f'{n}"' for n in p.get("retractedLengths", []))},
                {"@type": "PropertyValue", "name": "Safety Listing",
                 "value": cat.get("listing", "")},
            ]
            variants.append({
                "@type": "Product",
                "name": f"Autac Cat. {p['catNo']} - {p['conductors']}/{p['awg']} AWG "
                        f"{p['type']} Retractile Cord",
                "sku": p["catNo"],
                "mpn": p["catNo"],
                "brand": brand,
                "category": cat["name"],
                "material": cat.get("jacket") or cat.get("insulation") or "",
                "additionalProperty": props,
            })
        items.append({
            "@type": "ListItem",
            "position": position,
            "item": {
                "@type": "ProductGroup",
                "name": f"Autac {cat['name']}",
                "description": build_description(cat),
                "brand": brand,
                "manufacturer": {
                    "@type": "Organization",
                    "name": "Autac USA Inc.",
                    "url": "https://autacusa.com/",
                },
                "productGroupID": cat["id"],
                "variesBy": ["Wire Gauge", "Conductors", "Retracted Lengths"],
                "hasVariant": variants,
            },
        })

    payload = {
        "@context": "https://schema.org",
        "@type": "ItemList",
        "name": "Autac Retractile Cord Catalog",
        "url": "https://autacusa.com/products/",
        "numberOfItems": len(items),
        "itemListElement": items,
    }
    body = json.dumps(payload, indent=2, ensure_ascii=False)
    body = "\n".join("  " + line for line in body.splitlines())
    return f'  <script type="application/ld+json">\n{body}\n  </script>'


def build_options(data: dict) -> str:
    return "\n".join(
        f'        <option value="{attr(c["id"])}">{text(c["name"])}</option>'
        for c in data["categories"]
    )


def replace_block(html: str, marker: str, body: str) -> str:
    pattern = re.compile(
        rf"(<!-- {marker}:START -->).*?(<!-- {marker}:END -->)", re.DOTALL
    )
    if not pattern.search(html):
        sys.exit(f"marker {marker}:START/{marker}:END not found in {PAGE}")
    return pattern.sub(lambda m: f"{m.group(1)}\n{body}\n{m.group(2)}", html, count=1)


def main() -> None:
    data = json.loads(DATA.read_text(encoding="utf-8"))
    sections, count = build_sections(data)
    html = PAGE.read_text(encoding="utf-8")

    html = replace_block(html, "CATFILTER", build_options(data))
    html = replace_block(html, "CATALOG", sections)
    html = replace_block(
        html, "CATCOUNT", f"      Showing <strong>{count}</strong> products"
    )
    html = replace_block(html, "CATSCHEMA", build_schema(data))

    PAGE.write_text(html, encoding="utf-8")
    print(
        f"Pre-rendered {count} products across "
        f"{len(data['categories'])} categories into {PAGE.relative_to(ROOT)}"
    )


if __name__ == "__main__":
    main()
