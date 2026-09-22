#!/usr/bin/env python3
"""Render the website product catalog (catalog/data/products.json) as a
printable, letter-size PDF.

    python3 scripts/build-catalog-pdf.py            # writes catalog/autac-product-catalog-web.pdf
    python3 scripts/build-catalog-pdf.py --html-only  # just write the intermediate HTML

The PDF is built from the same JSON that drives /products/ and the hub tables,
so it always matches the site. It is NOT the Illustrator catalog at
catalog/autac-catalog.pdf, which is a separate, hand-designed document with its
own part numbering; this script never touches that file.

Rendering uses the installed Google Chrome in headless mode (no extra
dependencies). The intermediate HTML is written to the system temp dir (path
is printed) so it can be opened in a browser for layout tweaks without
shipping to Vercel.
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "catalog" / "data" / "products.json"
OUT_PDF = ROOT / "catalog" / "autac-product-catalog-web.pdf"
OUT_HTML = Path(tempfile.gettempdir()) / "autac-product-catalog-web.html"
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

# Facility / schema / GBP address. The P.O. Box is mailing and remittance only.
FACILITY = "25 Thompson Rd, Branford, CT 06405"
MAILING = "P.O. Box 306, North Branford, CT 06471"
PHONE_LOCAL = "(203) 481-3444"
PHONE_TOLL = "(800) 243-3161"
EMAIL = "sales@autacusa.com"
SITE = "autacusa.com"

# Category groupings for the PDF sections, in print order.
GROUPS: list[tuple[str, str, list[str]]] = [
    (
        "Retractile Power Cords",
        "UL-listed retractile power cords in TPE, TPR, and PVC. Bare copper conductors. "
        "Specify by conductor count, gauge, UL type, and retracted length.",
        ["tpe-power", "tpr-power", "pvc-power", "tpe-power-bare"],
    ),
    (
        "Communications, Control, and Test Lead Cords",
        "Tinned-copper curly cords for telephone handsets, dispatch radios, headsets, "
        "control panels, and meter and probe test leads.",
        ["comm-control", "test-leads"],
    ),
    (
        "Shielded Coiled Cables",
        "Shielded coiled cables for signal and data runs in electrically noisy "
        "environments, where EMI would otherwise couple into the conductors.",
        ["shielded-comm", "pvc-shielded"],
    ),
    (
        "Miniature Coiled Cords",
        "Small-diameter coiled cords for handheld devices, panel wiring, and tight "
        "enclosures where a standard power cord will not fit.",
        ["pvc-miniature", "pvc-miniature-foil"],
    ),
]

CATEGORY_DESC: dict[str, str] = {
    "tpe-power": "Our most popular retractile power cords. TPE insulation stays flexible in cold service and resists oil and abrasion.",
    "tpr-power": "Heavier-gauge power cords for tools and industrial equipment, 16 to 12 AWG, at 300V and 600V.",
    "pvc-power": "Economical PVC retractile power cords for indoor, climate-controlled equipment.",
    "tpe-power-bare": "TPE insulation and TPE jacket throughout, for full chemical resistance and flexibility.",
    "comm-control": "Handset, headset, radio, and control-panel curly cords. Tinned copper for flex life at the terminations.",
    "test-leads": "Single-conductor test leads for meters and probes.",
    "shielded-comm": "Each conductor individually shielded, for signal runs where crosstalk matters.",
    "pvc-shielded": "Overall shielded coiled cable for instrumentation and control circuits.",
    "pvc-miniature": "Small-diameter cords for handheld devices and tight enclosures.",
    "pvc-miniature-foil": "Miniature cords with an overall foil shield, for low-level signal runs.",
}


def esc(s: str) -> str:
    return (
        str(s)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def lengths(product: dict) -> str:
    return ", ".join(str(n) for n in product["retractedLengths"])


def weights(product: dict) -> str:
    w = product.get("weightLbs")
    if not w:
        return ""
    return " / ".join(f"{x:.2f}" for x in w)


def category_block(cat: dict, products: list[dict]) -> str:
    rows = "\n".join(
        f"""          <tr>
            <td class="cat">{esc(p['catNo'])}</td>
            <td>{p['conductors']}</td>
            <td>{esc(p['awg'])}</td>
            <td>{esc(p.get('strand', ''))}</td>
            <td>{esc(p['type']).replace('/', '/<wbr>')}</td>
            <td>{esc(p['voltage'])}</td>
            <td>{esc(p['ampRating'])}</td>
            <td>{p.get('tempC', '')}&deg;C</td>
            <td>{esc(p.get('conductorOD', ''))}</td>
            <td>{esc(p.get('coilOD', ''))}</td>
            <td class="len">{lengths(p)}</td>
            <td class="wt">{weights(p)}</td>
          </tr>"""
        for p in products
    )
    meta = [
        f"<span><b>Conductor</b> {esc(cat['conductor'])}</span>",
        f"<span><b>Insulation</b> {esc(cat['insulation'])}</span>",
        f"<span><b>Jacket</b> {esc(cat['jacket'])}</span>",
    ]
    if cat.get("shield"):
        meta.append("<span><b>Shield</b> Yes</span>")
    meta.append(f"<span><b>Listing</b> {esc(cat['listing'])}</span>")
    if cat.get("extension"):
        meta.append(f"<span><b>Extension</b> {esc(cat['extension'])}</span>")
    if cat.get("catalogPage"):
        meta.append(f"<span><b>Print catalog</b> p. {cat['catalogPage']}</span>")
    n = len(products)
    meta.append(f"<span><b>Stock</b> {n} catalog number{'s' if n != 1 else ''}</span>")
    desc = CATEGORY_DESC.get(cat["id"], "")
    if cat.get("notes"):
        desc = (desc + " " if desc else "") + cat["notes"]
    desc_html = f'<p class="cat-desc">{esc(desc)}</p>' if desc else ""
    return f"""
    <section class="category">
      <div class="cat-head">
        <h3>{esc(cat['name'])}</h3>
        <span class="listing {'rec' if 'Recognized' in cat['listing'] else 'listed'}">{esc(cat['listing'])}</span>
      </div>
      {desc_html}
      <div class="cat-meta">{' '.join(meta)}</div>
      <table>
        <thead>
          <tr>
            <th>Cat. No.</th><th>Cond.</th><th>AWG</th><th>Strand</th><th>Type</th><th>Volts</th><th>Amps</th><th>Temp</th><th>Cord OD</th><th>Coil OD</th><th>Retracted in.</th><th>Wt. lbs at each length</th>
          </tr>
        </thead>
        <tbody>
{rows}
        </tbody>
      </table>
    </section>"""


def build_html(data: dict) -> str:
    cats = {c["id"]: c for c in data["categories"]}
    by_cat: dict[str, list[dict]] = {}
    for p in data["products"]:
        by_cat.setdefault(p["category"], []).append(p)
    total = len(data["products"])
    today = date.today()
    edition = today.strftime("%B %Y")

    # Table of contents + sections
    toc_items = []
    sections = []
    for gi, (title, blurb, cat_ids) in enumerate(GROUPS, start=1):
        toc_items.append(
            f'<li><span class="toc-n">{gi}</span><span class="toc-t">{esc(title)}</span>'
            f'<span class="toc-c">{", ".join(esc(cats[c]["name"]) for c in cat_ids if c in cats)}</span></li>'
        )
        blocks = "\n".join(category_block(cats[c], by_cat.get(c, [])) for c in cat_ids if c in cats)
        sections.append(
            f"""
  <section class="group{" first" if gi == 1 else ""}">
    <div class="group-head">
      <div class="group-n">{gi}</div>
      <div>
        <h2>{esc(title)}</h2>
        <p>{esc(blurb)}</p>
      </div>
    </div>
{blocks}
  </section>"""
        )
    foot = (f'<div class="page-foot"><span><b>Autac USA</b> &nbsp;|&nbsp; {esc(FACILITY)} &nbsp;|&nbsp; '
            f'{esc(PHONE_LOCAL)} &nbsp;|&nbsp; {esc(PHONE_TOLL)}</span>'
            f'<span>{esc(EMAIL)} &nbsp;|&nbsp; {esc(SITE)} &nbsp;|&nbsp; Edition {esc(edition)}</span></div>')
    toc_items.append('<li><span class="toc-n">5</span><span class="toc-t">Reference</span><span class="toc-c">Length chart, cord types, conductor color codes</span></li>')
    toc_items.append('<li><span class="toc-n">6</span><span class="toc-t">Specifying a Custom Cord</span><span class="toc-c">Spec worksheet, extension ratio, terminations</span></li>')

    logo = (ROOT / "logo.png").resolve().as_uri()
    cover_img = (ROOT / "images" / "coiled-cords-red-white-blue-on-mandrels-branford-ct.webp").resolve().as_uri()
    plant_img = (ROOT / "images" / "red-retractile-cords-manufacturing-branford-ct.webp").resolve().as_uri()

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Autac USA Retractile Cord Catalog</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap" rel="stylesheet">
<style>
  :root {{
    --red: #cc0a2b; --red-dark: #a30822; --accent: #f5c518; --black: #1a1a1a;
    --gray: #f3f3f3; --gray-2: #e2e2e2; --muted: #5c5c5c;
  }}
  @page {{ size: letter; margin: 0.5in 0.45in 0.6in 0.45in; }}
  @page :first {{ margin: 0; }}
  * {{ box-sizing: border-box; }}
  html, body {{ margin: 0; padding: 0; }}
  body {{
    font-family: 'Inter', 'Helvetica Neue', Helvetica, Arial, sans-serif;
    color: var(--black); font-size: 9.6pt; line-height: 1.4;
    -webkit-print-color-adjust: exact; print-color-adjust: exact;
  }}
  h1, h2, h3 {{ margin: 0; line-height: 1.15; }}
  p {{ margin: 0 0 6pt; }}

  /* ---------- Cover ---------- */
  .cover {{
    height: 11in; width: 8.5in; position: relative; overflow: hidden;
    background: var(--black); color: #fff; page-break-after: always;
  }}
  .cover-photo {{
    position: absolute; inset: 0; background: url("{cover_img}") center/cover no-repeat;
    opacity: 0.55;
  }}
  .cover-shade {{
    position: absolute; inset: 0;
    background: linear-gradient(180deg, rgba(26,26,26,0.15) 0%, rgba(26,26,26,0.35) 45%, rgba(26,26,26,0.97) 78%);
  }}
  .cover-band {{
    position: absolute; top: 0; left: 0; right: 0; height: 0.32in; background: var(--red);
  }}
  .cover-logo {{
    position: absolute; top: 0.6in; left: 0.7in; background: #fff; padding: 12pt 16pt; border-radius: 4pt;
  }}
  .cover-logo img {{ height: 0.85in; display: block; }}
  .cover-text {{ position: absolute; left: 0.7in; right: 0.7in; bottom: 1.35in; }}
  .cover-kicker {{
    display: inline-block; background: var(--accent); color: var(--black); font-weight: 800;
    font-size: 9pt; letter-spacing: 0.12em; text-transform: uppercase; padding: 4pt 9pt; margin-bottom: 14pt;
  }}
  .cover h1 {{ font-size: 38pt; font-weight: 800; letter-spacing: -0.01em; margin-bottom: 8pt; }}
  .cover h1 span {{ color: var(--accent); }}
  .cover-sub {{ font-size: 12.5pt; color: #ddd; max-width: 5.6in; margin-bottom: 18pt; }}
  .cover-facts {{ display: flex; gap: 22pt; font-size: 9pt; color: #eee; }}
  .cover-facts b {{ display: block; font-size: 15pt; color: #fff; font-weight: 800; }}
  .cover-foot {{
    position: absolute; left: 0; right: 0; bottom: 0; background: var(--red); color: #fff;
    padding: 12pt 0.7in; display: flex; justify-content: space-between; font-size: 9pt; font-weight: 600;
  }}
  .cover-foot span + span {{ margin-left: 14pt; }}


  /* ---------- Intro page ---------- */
  .intro {{ page-break-after: always; }}
  .intro-grid {{ display: grid; grid-template-columns: 1.15fr 0.85fr; gap: 22pt; margin-top: 10pt; }}
  .intro h2, .group h2, .custom h2 {{
    font-size: 17pt; font-weight: 800; color: var(--black);
  }}
  .eyebrow {{
    color: var(--red); font-weight: 700; font-size: 8pt; letter-spacing: 0.14em; text-transform: uppercase; margin-bottom: 4pt;
  }}
  .intro p {{ font-size: 9.6pt; }}
  .plant {{ width: 100%; height: 2.35in; object-fit: cover; border-radius: 4pt; display: block; margin-bottom: 8pt; }}
  .card {{ background: var(--gray); border-left: 4px solid var(--red); padding: 10pt 12pt; margin-bottom: 10pt; }}
  .card h3 {{ font-size: 10pt; font-weight: 800; margin-bottom: 4pt; }}
  .card p, .card li {{ font-size: 8.8pt; margin: 0 0 3pt; }}
  .card ul {{ margin: 0; padding-left: 14pt; }}
  .toc {{ list-style: none; padding: 0; margin: 6pt 0 0; }}
  .toc li {{ display: grid; grid-template-columns: 22pt 1fr; gap: 0 8pt; padding: 6pt 0; border-bottom: 1px solid var(--gray-2); }}
  .toc-n {{ grid-row: span 2; width: 18pt; height: 18pt; border-radius: 50%; background: var(--red); color: #fff; font-weight: 800; font-size: 9pt; display: flex; align-items: center; justify-content: center; }}
  .toc-t {{ font-weight: 700; font-size: 10pt; }}
  .toc-c {{ font-size: 8.4pt; color: var(--muted); }}
  .contact-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 6pt 14pt; font-size: 8.8pt; margin-top: 6pt; }}
  .contact-grid b {{ display: block; font-size: 7.4pt; letter-spacing: 0.1em; text-transform: uppercase; color: var(--muted); }}
  .howto {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 10pt; margin-top: 8pt; }}
  .howto div {{ border: 1px solid var(--gray-2); border-top: 3px solid var(--accent); padding: 8pt 9pt; font-size: 8.6pt; }}
  .howto b {{ display: block; font-size: 9.2pt; margin-bottom: 3pt; }}

  /* ---------- Product groups ---------- */
  .group {{ margin-top: 16pt; }}
  .group.first {{ page-break-before: always; margin-top: 0; }}
  .group-head {{ break-after: avoid; page-break-after: avoid; }}
  .page-foot {{ margin-top: 14pt; padding-top: 6pt; border-top: 1px solid var(--gray-2); font-size: 7.6pt; color: var(--muted); display: flex; justify-content: space-between; }}
  .page-foot b {{ color: var(--red); }}
  .group-head {{ display: flex; gap: 12pt; align-items: flex-start; border-bottom: 3px solid var(--red); padding-bottom: 8pt; margin-bottom: 10pt; }}
  .group-n {{ flex: 0 0 auto; width: 30pt; height: 30pt; border-radius: 4pt; background: var(--red); color: #fff; font-weight: 800; font-size: 15pt; display: flex; align-items: center; justify-content: center; }}
  .group-head p {{ color: var(--muted); font-size: 9.2pt; margin: 3pt 0 0; max-width: 6in; }}
  .category {{ margin-bottom: 11pt; }}
  .cat-head, .cat-desc, .cat-meta {{ break-after: avoid; page-break-after: avoid; }}
  .cat-head {{ display: flex; align-items: center; justify-content: space-between; background: var(--black); color: #fff; padding: 6pt 10pt; border-radius: 3pt 3pt 0 0; }}
  .cat-head h3 {{ font-size: 11pt; font-weight: 700; }}
  .listing {{ font-size: 7.4pt; font-weight: 800; letter-spacing: 0.08em; text-transform: uppercase; padding: 2pt 7pt; border-radius: 10pt; }}
  .listing.listed {{ background: var(--accent); color: var(--black); }}
  .listing.rec {{ background: #fff; color: var(--black); }}
  .cat-desc {{ font-size: 8.6pt; color: var(--muted); margin: 6pt 0 4pt; }}
  .cat-meta {{ font-size: 8pt; display: flex; flex-wrap: wrap; gap: 4pt 14pt; margin-bottom: 5pt; }}
  .cat-meta b {{ color: var(--muted); font-weight: 600; margin-right: 3pt; }}
  table {{ width: 100%; border-collapse: collapse; font-size: 7.6pt; }}
  .intro, .group, .custom {{ overflow: hidden; }}
  th {{ text-align: left; background: var(--gray); color: var(--black); font-weight: 700; font-size: 6.6pt; letter-spacing: 0.02em; text-transform: uppercase; padding: 4pt 3.5pt; border-bottom: 2px solid var(--gray-2); }}
  td {{ padding: 3pt 3.5pt; border-bottom: 1px solid var(--gray-2); vertical-align: top; }}
  td.cat {{ font-weight: 800; color: var(--red); font-size: 8.6pt; }}
  td.wt {{ color: var(--muted); }}
  td, th {{ white-space: nowrap; }}
  thead {{ display: table-header-group; }}
  tr {{ page-break-inside: avoid; break-inside: avoid; }}
  td.len {{ }}
  tr:nth-child(even) td {{ background: #fafafa; }}

  /* ---------- Custom cord page ---------- */
  .custom {{ page-break-before: always; }}
  .ref-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 0 22pt; margin-top: 10pt; }}
  table.ref {{ font-size: 8.6pt; }}
  table.ref td {{ padding: 4pt 7pt; }}
  .ref-note {{ font-size: 8.4pt; color: var(--muted); margin-top: 10pt; }}
  .spec-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 0 22pt; margin-top: 10pt; }}
  .spec-row {{ display: flex; justify-content: space-between; align-items: flex-end; border-bottom: 1px dotted #999; padding: 9pt 0 3pt; font-size: 9pt; }}
  .spec-row span:last-child {{ color: #bbb; font-size: 7.6pt; }}
  .note {{ background: #fff8dc; border: 1px solid var(--accent); padding: 8pt 10pt; font-size: 8.6pt; margin-top: 12pt; }}
  .cta-box {{ margin-top: 14pt; background: var(--black); color: #fff; padding: 12pt 14pt; border-radius: 4pt; display: flex; justify-content: space-between; align-items: center; }}
  .cta-box b {{ font-size: 12pt; }}
  .cta-box span {{ font-size: 9pt; }}
  .cta-box .y {{ color: var(--accent); font-weight: 700; }}
</style>
</head>
<body>

<!-- ================= COVER ================= -->
<section class="cover">
  <div class="cover-photo"></div>
  <div class="cover-shade"></div>
  <div class="cover-band"></div>
  <div class="cover-logo"><img src="{logo}" alt="Autac USA - Re-Trak-Tul Kords"></div>
  <div class="cover-text">
    <div class="cover-kicker">Stock Product Catalog &middot; {esc(edition)}</div>
    <h1>Retractile Cords,<br>Coiled Cords &amp; <span>Curly Cords</span></h1>
    <p class="cover-sub">UL-listed retractile power cords, communications and control cords, test leads, shielded coiled cables, and miniature cords. Manufactured in Branford, Connecticut since 1947.</p>
    <div class="cover-facts">
      <div><b>{total}</b>stock catalog numbers</div>
      <div><b>1947</b>manufacturing since</div>
      <div><b>100%</b>woman-owned</div>
      <div><b>USA</b>made in Branford, CT</div>
    </div>
  </div>
  <div class="cover-foot">
    <div><span>{esc(PHONE_TOLL)}</span><span>{esc(PHONE_LOCAL)}</span></div>
    <div><span>{esc(EMAIL)}</span><span>{esc(SITE)}</span></div>
  </div>
</section>

<!-- ================= INTRO ================= -->
<section class="intro">
  <div class="eyebrow">About This Catalog</div>
  <h2>Stock retractile cords, ready to quote</h2>
  <div class="intro-grid">
    <div>
      <p>Autac has manufactured retractile cords, also called coiled cords, coil cords, and curly cords, in Branford, Connecticut since 1947. Every cord in this catalog is wound and heat-set in our own plant, which is what gives it the spring memory to extend to its working length and pull itself back thousands of times without going slack.</p>
      <p>The tables that follow list our {total} stock catalog numbers by construction, with the same specifications as our printed catalog: conductor count, gauge and stranding, cord type, electrical and temperature ratings, cord and coil diameter, and weight. Every stock number is available in 12, 24, 36, and 48 inch retracted lengths unless noted. Extended working length is five times the retracted length; the length chart on the reference page gives the full figures.</p>
      <p>Anything not listed here is built to order. Custom conductor counts, gauges, lengths, jacket colors, shielding, and terminations are all available, and there is no minimum order quantity on most constructions. The worksheet on the last page lists what we need to quote a custom cord.</p>
      <div class="card">
        <h3>How to read the tables</h3>
        <ul>
          <li><b>Cat. No.</b> is the stock catalog number. Quote it with the retracted length you need, for example <b>93161, 24 inch</b>. A number ending in <b>W</b> is the white-jacket version; <b>5P</b> is a PVC jacket and <b>7P</b> an Auta-Prene TPE jacket on the same cord.</li>
          <li><b>Cond.</b>, <b>AWG</b>, and <b>Strand</b> are conductor count, wire gauge, and stranding (number of strands / strand gauge).</li>
          <li><b>Type</b> is the UL cord designation. <b>AWM</b> is UL Recognized appliance wiring material. Volts, amps, and temperature are the rated maximums for that construction.</li>
          <li><b>Cond. OD</b> and <b>Coil OD</b> are the outside diameter of the finished cord and of the coil, in inches.</li>
          <li><b>Retracted</b> lengths are the coil lengths stocked, in inches, at rest. <b>Wt. lbs</b> gives the weight at each of those lengths in order.</li>
          <li><b>UL/cUL Listed</b> cords are finished, standalone products. <b>UL Recognized</b> cords are components for use inside equipment that carries its own approval.</li>
        </ul>
      </div>
      <div class="card">
        <h3>Pricing</h3>
        <p>Pricing is not printed in this catalog. Call or email sales for a quote, or, if you are an existing customer, verify your email at {esc(SITE)}/products/ to view current pricing online.</p>
      </div>
    </div>
    <div>
      <img class="plant" src="{plant_img}" alt="Red retractile cords in production at the Autac plant in Branford, Connecticut">
      <div class="eyebrow">Contents</div>
      <ul class="toc">
        {''.join(toc_items)}
      </ul>
      <div class="eyebrow" style="margin-top:12pt">Contact</div>
      <div class="contact-grid">
        <div><b>Sales</b>{esc(PHONE_TOLL)}<br>{esc(PHONE_LOCAL)}</div>
        <div><b>Email</b>{esc(EMAIL)}</div>
        <div><b>Facility</b>{esc(FACILITY)}</div>
        <div><b>Mailing and remittance</b>{esc(MAILING)}</div>
        <div><b>Web</b>{esc(SITE)}</div>
        <div><b>Hours</b>Mon to Fri, 8am to 5pm ET</div>
      </div>
    </div>
  </div>
</section>

{''.join(sections)}
{foot}

<!-- ================= REFERENCE ================= -->
<section class="custom">
  <div class="group-head">
    <div class="group-n">5</div>
    <div>
      <h2>Reference</h2>
      <p>Length chart, UL cord types, and the conductor color codes used on every stock cord.</p>
    </div>
  </div>
  <div class="ref-grid">
    <div>
      <div class="eyebrow">Length chart, 1:5 extension</div>
      <table class="ref">
        <thead><tr><th>Retracted</th><th>Extended</th><th>Tangent leads, both ends</th></tr></thead>
        <tbody>
          <tr><td>12 inches</td><td>5 feet</td><td>12 inches</td></tr>
          <tr><td>24 inches</td><td>10 feet</td><td>6 inches</td></tr>
          <tr><td>36 inches</td><td>15 feet</td><td>6 inches</td></tr>
          <tr><td>48 inches</td><td>20 feet</td><td>6 inches</td></tr>
          <tr><td>60 inches</td><td>25 feet</td><td>Special</td></tr>
          <tr><td>Up to 12 feet</td><td>Up to 60 feet</td><td>Special</td></tr>
        </tbody>
      </table>
      <div class="eyebrow" style="margin-top:12pt">UL Listed and cUL certified cord types</div>
      <table class="ref">
        <thead><tr><th>Type</th><th>Temp. rating</th><th>Voltage</th></tr></thead>
        <tbody>
          <tr><td>SVT, SVEO</td><td>60 to 105&deg;C</td><td>300V</td></tr>
          <tr><td>SJT, SJEOOW</td><td>60 to 105&deg;C</td><td>300V</td></tr>
          <tr><td>ST, SEOW</td><td>60 to 105&deg;C</td><td>600V</td></tr>
        </tbody>
      </table>
      <p class="ref-note">All Autac cords are RoHS compliant. Conductors are soft bare copper on power cords and soft tinned copper on communications, control, test lead, shielded, and miniature cords. CAGE code 3AWW0.</p>
    </div>
    <div>
      <div class="eyebrow">Conductor colors, power cords</div>
      <table class="ref two">
        <thead><tr><th>Cond.</th><th>Base color</th><th>Cond.</th><th>Base color</th></tr></thead>
        <tbody>
          <tr><td>1</td><td>Black</td><td>6</td><td>Blue</td></tr>
          <tr><td>2</td><td>White</td><td>7</td><td>Yellow</td></tr>
          <tr><td>3</td><td>Green</td><td>8</td><td>Brown</td></tr>
          <tr><td>4</td><td>Red</td><td>9</td><td>Gray</td></tr>
          <tr><td>5</td><td>Orange</td><td>10</td><td>Violet</td></tr>
        </tbody>
      </table>
      <div class="eyebrow" style="margin-top:12pt">Conductor colors, AWM style cords</div>
      <table class="ref two">
        <thead><tr><th>Cond.</th><th>Base color</th><th>Cond.</th><th>Base color</th></tr></thead>
        <tbody>
          <tr><td>1</td><td>Black</td><td>9</td><td>Gray</td></tr>
          <tr><td>2</td><td>White</td><td>10</td><td>Pink</td></tr>
          <tr><td>3</td><td>Red</td><td>11</td><td>Violet</td></tr>
          <tr><td>4</td><td>Green</td><td>12</td><td>Tan</td></tr>
          <tr><td>5</td><td>Orange</td><td>13</td><td>White / black</td></tr>
          <tr><td>6</td><td>Blue</td><td>14</td><td>Red / black</td></tr>
          <tr><td>7</td><td>Yellow</td><td>15</td><td>Green / black</td></tr>
          <tr><td>8</td><td>Brown</td><td></td><td></td></tr>
        </tbody>
      </table>
    </div>
  </div>
</section>

<!-- ================= CUSTOM CORD ================= -->
<section class="custom">
  <div class="group-head">
    <div class="group-n">6</div>
    <div>
      <h2>Specifying a Custom Cord</h2>
      <p>Send us the items below and we will quote the build. Anything you leave blank we will recommend.</p>
    </div>
  </div>
  <div class="howto">
    <div><b>1. Reach, not coil</b>Measure the working distance the cord has to cover. Divide by five for the retracted length. Size it so the cord reaches with tension to spare, or it will take a set.</div>
    <div><b>2. Electrical load</b>Voltage, current, and the number of circuits set the conductor count and gauge. Signal and handset cords run 22 to 26 AWG; power cords 18 down to 10 AWG.</div>
    <div><b>3. Environment</b>PVC for indoor, climate-controlled service. TPE or TPR for cold, oil, or abrasion. Ask about Auta-Prene where coil recovery over a long life is the point of the cord.</div>
  </div>
  <div class="spec-grid">
    <div>
      <div class="spec-row"><span>Company / contact</span><span>__________________________</span></div>
      <div class="spec-row"><span>Application</span><span>__________________________</span></div>
      <div class="spec-row"><span>Number of conductors</span><span>__________________________</span></div>
      <div class="spec-row"><span>Wire gauge (AWG)</span><span>__________________________</span></div>
      <div class="spec-row"><span>Voltage / amps</span><span>__________________________</span></div>
      <div class="spec-row"><span>Insulation material</span><span>__________________________</span></div>
      <div class="spec-row"><span>Jacket material and color</span><span>__________________________</span></div>
      <div class="spec-row"><span>Shielding (none / braid / foil)</span><span>__________________________</span></div>
    </div>
    <div>
      <div class="spec-row"><span>Retracted length</span><span>__________________________</span></div>
      <div class="spec-row"><span>Extended working length</span><span>__________________________</span></div>
      <div class="spec-row"><span>Tangent (lead) length, each end</span><span>__________________________</span></div>
      <div class="spec-row"><span>Termination, end A</span><span>__________________________</span></div>
      <div class="spec-row"><span>Termination, end B</span><span>__________________________</span></div>
      <div class="spec-row"><span>UL Listed or UL Recognized</span><span>__________________________</span></div>
      <div class="spec-row"><span>Annual quantity</span><span>__________________________</span></div>
      <div class="spec-row"><span>Target date</span><span>__________________________</span></div>
    </div>
  </div>
  <div class="note"><b>Sample cords.</b> If you have a cord you are replacing, send it with the worksheet. We will match the construction and quote from the sample.</div>
  <div class="cta-box">
    <div><b>Request a quote</b><br><span>Online at <span class="y">{esc(SITE)}/quote/</span> or configure a cord step by step at <span class="y">{esc(SITE)}/build-your-cord/</span></span></div>
    <div style="text-align:right"><span class="y">{esc(PHONE_TOLL)}</span><br><span>{esc(EMAIL)}</span></div>
  </div>
  {foot}
</section>

</body>
</html>
"""


def render_pdf(html_path: Path, pdf_path: Path) -> None:
    if not Path(CHROME).exists():
        sys.exit(f"Google Chrome not found at {CHROME}; open {html_path} and print to PDF manually.")
    with tempfile.TemporaryDirectory() as profile:
        cmd = [
            CHROME,
            "--headless=new",
            "--disable-gpu",
            "--no-first-run",
            "--no-default-browser-check",
            f"--user-data-dir={profile}",
            "--no-pdf-header-footer",
            "--virtual-time-budget=8000",
            f"--print-to-pdf={pdf_path}",
            html_path.resolve().as_uri(),
        ]
        # Chrome sometimes keeps running after the PDF is written; the file is
        # complete once it stops growing, so a timeout is treated as success if
        # the PDF exists.
        try:
            subprocess.run(cmd, check=True, capture_output=True, timeout=60)
        except subprocess.TimeoutExpired:
            if not pdf_path.exists():
                raise


def main() -> None:
    data = json.loads(DATA.read_text())
    html = build_html(data)
    OUT_HTML.write_text(html)
    print(f"Wrote {OUT_HTML}")
    if "--html-only" in sys.argv:
        return
    render_pdf(OUT_HTML, OUT_PDF)
    size_kb = OUT_PDF.stat().st_size // 1024
    print(f"Wrote {OUT_PDF.relative_to(ROOT)} ({size_kb} KB)")
    if shutil.which("pdfinfo"):
        out = subprocess.run(["pdfinfo", str(OUT_PDF)], capture_output=True, text=True).stdout
        for line in out.splitlines():
            if line.startswith(("Pages", "Page size")):
                print("  " + line)


if __name__ == "__main__":
    main()
