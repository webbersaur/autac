# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Static HTML/CSS/JS website for **Autac USA** (autacusa.com), a 100% woman-owned retractile cord manufacturer in Branford, CT since 1947. No build system, no bundler, no CMS - all pages are self-contained HTML with inline `<style>` blocks.

**NAP (do not get this wrong - it was wrong in 158 files until 2026-07-14):**
- Facility / schema / GBP address: **25 Thompson Rd, Branford, CT 06405**
- Mailing & remittance only: P.O. Box 306, North Branford, CT 06471 - belongs on `contact/index.html` **only**, labeled. Never in schema, topbar, or footer.
- Schema `telephone`: **+1-203-481-3444** (matches the Google Business Profile). The toll-free 800-243-3161 stays as a `contactPoint` with `contactType: "sales"`.

**Repo:** github.com/webbersaur/autac.git (branch: `main`)
**GitHub Pages:** https://webbersaur.github.io/autac/

## Local Development

```bash
python3 -m http.server 8080
```

## Site Structure

### Public Pages (indexed in sitemap.xml)
- `index.html` — Homepage
- `about.html` — Company history, leadership, woman-owned messaging
- `products.html` — Product catalog with filtering (loads from JSON, pricing behind Supabase OTP auth)
- `products/retractile-cords.html` — Retractile cord category
- `products/curly-cords.html` — Curly cord category
- `products/coiled-cords.html` — Coiled cord category
- `products/cord-sets.html` — Cord sets (straight, retractile, shielded assemblies)
- `products/color-charts.html` — Conductor color reference
- `solutions.html` — Industry-specific solutions
- `contact.html` — Contact form (wired to Supabase)
- `quote.html` — 5-step guided quote wizard (wired to Supabase)
- `build-your-cord.html` — 8-step custom cord configurator (wired to Supabase)
- `faq.html` — 16-question FAQ with accordion UI and FAQPage structured data
- `shop-online.html` — Links to eBay store
- `media.html` — 8 YouTube videos from WordPress site
- `news.html` — News & press index
- `news/*.html` — 9 individual news/press articles
- `blog/index.html` — Blog index
- `blog/*.html` — 34 blog posts (11 from WordPress + 23 SEO posts)
- `privacy-policy.html` — Privacy policy
- `terms-of-service.html` — Website terms of service
- `terms-of-sale.html` — B2B terms and conditions of sale (18 sections)
- `75th-anniversary.html` — 75th anniversary celebration (1947–2022)
- `2026-price-adjustments.html` — Price adjustment notice
- `holiday-schedule.html` — 2026 holiday closure schedule

### Non-indexed Files (blocked in robots.txt)
- `proposal-v1.html` — Webbersaurus website redesign proposal (different brand colors)
- `invoice-deposit.html` — Webbersaurus deposit invoice
- `admin.html` — Supabase-powered dashboard (password auth, email allowlist)

## Architecture & Patterns

### Generated Content: the Product Catalog
`products/index.html` contains a **pre-rendered** copy of the whole catalog so the
page ships complete in the HTML response (it used to render client-side only,
which meant Googlebot's first-wave crawl saw "Loading product catalog..." and
nothing else). Edit `catalog/data/products.json`, then regenerate:

```bash
python3 scripts/build-catalog.py
```

Never hand-edit between the markers in `products/index.html`:
- `<!-- CATFILTER:START/END -->` - category `<select>` options
- `<!-- CATALOG:START/END -->` - category sections and product cards
- `<!-- CATCOUNT:START/END -->` - the "Showing N products" count

The page's `buildCard()`/`renderProducts()` JS still owns filtering and re-renders
from the same JSON on every filter change, so **the generator's markup and
`buildCard()` must stay byte-identical**. If you change one, change the other and
re-verify by round-tripping a filter (apply a category filter, return to "All",
and confirm the DOM is unchanged).

### Generated Content: Hub Catalog Tables
The four hubs (`retractile-cords`, `coiled-cords`, `curly-cords`, `cord-sets`)
used to build their catalog tables client-side from the same
`catalog/data/products.json`, so the HTML response shipped "Loading product
data..." and not one catalog number - the same first-wave-crawl problem
`/products/` had before it was pre-rendered. All four are now generated:

```bash
python3 scripts/build-hub-tables.py           # rewrite
python3 scripts/build-hub-tables.py --check   # exit 1 if stale
```

Markers: `<!-- HUBROWS:<category>:START/END -->` inside each retractile tbody
(its section prose is hand-written and stays), `<!-- HUBTABLES:START/END -->`
for the coiled/curly sections and the cord-sets platform table.

The hubs have **no filter UI**, so unlike `/products/` there is no second
renderer to keep byte-identical - the fetch/render scripts were deleted from all
four pages. Do not add them back. Their templates also referenced fields that do
not exist in `products.json` (`category.extensionRatio`, `product.cableOD` both
printed "undefined") and wrote `${p.ampRating}A`, which doubled the unit into
"7AA", since `ampRating` already carries it.

### Generated Content: Hub Disambiguation and Schema
Two more idempotent generators keep repeated blocks identical across the hubs.
Both replace whatever sits between their markers, so re-run them rather than
editing the output:

```bash
python3 scripts/add-hub-disambiguation.py   # <!-- CORD FAMILY:START/END -->
python3 scripts/add-hub-product-schema.py   # <!-- HUBSCHEMA:START/END -->
```

- **Disambiguation block** (`coiled-cords`, `curly-cords`, `retractile-cords`) -
  coiled/curly/retractile are near-synonyms, and Google was splitting the same
  queries across all three. The block states identically on every hub which page
  owns which term, rendering the current page as a non-linked "you are here"
  card. **Do not let a hub claim the other hubs' terms in its own copy** - route
  to them instead, or the cannibalization comes back.
- **ProductGroup + BreadcrumbList schema** (those three plus `cord-sets`).

**Product schema and the `offers` problem.** Google's product-snippet validator
requires `offers`, `review`, or `aggregateRating` on every Product-typed entity.
Autac's pricing is gated behind customer verification and there are no reviews,
so none of the three can be supplied honestly - which makes product rich results
permanently unreachable here. Search Console reports the shortfall as an
**error** ("invalid items"), not a warning. It does not affect indexing or
rankings; it only means "ineligible for this feature".

The deliberate split:
- The four hubs each carry exactly **one** `ProductGroup` (4 invalid items
  sitewide). Worth the noise for the commercial-entity signal on the pages that
  matter.
- `/products/` uses a plain nested `ItemList` with **no Product types**. Marking
  its 10 categories and 25 part numbers as Products generated 35 permanently
  invalid items for no possible rich result. The ItemList carries the same
  catalog data and validates clean.
- Never add `isSimilarTo` with `{name, url}` stubs to a ProductGroup. Google
  counts each stub as its own Product entity, which turned 1 invalid item per
  hub into 4. Cross-hub relationships live in the visible disambiguation links.
- Never fabricate a price, review, or rating to turn the report green.

### Legacy URL Redirects
`vercel.json` carries 160+ 301s, most of them WordPress URLs that survived the
migration. Add new ones via `scripts/add-legacy-redirects.py` (idempotent).
A redirect must land on a **topically equivalent** page - Google treats an
irrelevant 301 as a soft 404, so off-topic legacy content (hose reels,
magnetic-field explainers) is deliberately left to 404. That list, with reasons,
is in the script's `LEAVE_404`.

### No Shared CSS/JS
Every page has its own complete inline `<style>` block and `<script>` block. When creating new pages, copy the full header/nav/footer structure and CSS from an existing page. This means **sitewide changes (nav, footer, theme) must be applied to all pages individually**.

### CSS Theme (consistent across all pages)
- `--red: #cc0a2b` / `--red-light: #e01235` — Primary CTA color
- `--accent: #f5c518` / `--accent-dark: #d4a80e` — Secondary CTA (yellow)
- `--black: #1a1a1a` — Headers, dark backgrounds
- `--font: 'Inter'` — Google Fonts (weights 400–800)
- `.container` — max-width: 1200px centered wrapper

### Page Template Structure
Every page follows: Topbar → Sticky Header (logo + nav + CTA) → Page Hero → Content → Footer

### Navigation
- Products has a hover dropdown with invisible bridge (`::before` spacer) to prevent flickering
- Dropdown items: Full Catalog, Retractile Cords, Curly Cords, Coiled Cords, Color Charts
- Mobile: hamburger toggle with `nav.open` class
- "Get a Quote" yellow CTA button links to `quote.html`
- Blog link points to `blog/`
- Product subpages use `../` prefix for root-level links
- Footer has three legal links: Privacy Policy | Terms of Service | Terms of Sale

### Forms (Supabase Backend)
All three forms (`contact.html`, `quote.html`, `build-your-cord.html`) submit to Supabase tables via the JS client. A Supabase Edge Function (`supabase/functions/notify-submission/`) sends email notifications on new submissions via Resend SMTP. All forms block disposable/temporary email domains.

- **contact.html**: Simple contact form → `contacts` table
- **quote.html**: `nextStep()`/`prevStep()`/`goToStep()` navigation, `validateContact()` on step 4, NDA checkbox on step 2, generates reference number `QR-YYYYMMDD-XXXX` → `quotes` table
- **build-your-cord.html**: `cordConfig` state object, `updateSummary()` updates sticky sidebar, auto-calculates extended length (5x retracted) → `cord_configs` table
- **products.html**: Pricing behind OTP auth (`verifyOtp` type: `magiclink` — required because the customized Magic Link template is what delivers the code; using type `email` returns "Token has expired or is invalid"), access logged to `pricing_access_log` and `page_views` tables

## SEO Status
- Canonical tags on all pages (autacusa.com)
- Unique title tags and meta descriptions per page
- JSON-LD structured data on all pages
- Open Graph tags on homepage
- robots.txt and sitemap.xml in place

## When Adding New Pages
1. Copy header/nav/footer HTML and full `<style>` block from an existing page
2. Add `<link rel="canonical">` tag in `<head>`
3. Add the page to `sitemap.xml`
4. For pages in subdirectories, use `../` prefix for root-level asset/page links
5. Ensure nav dropdown includes all 5 product links (Catalog, Retractile, Curly, Coiled, Color Charts)
6. Ensure footer has all 3 legal links (Privacy Policy, Terms of Service, Terms of Sale)
7. Add JSON-LD structured data appropriate to the page type
