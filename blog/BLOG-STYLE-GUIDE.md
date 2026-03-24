# Autac USA Blog Style Guide

## Reference Post
Use `blog/coiled-extension-cords.html` as the canonical template for all future posts. Copy its exact HTML structure, CSS, header, nav, footer, and article layout.

## Page Structure
1. Full inline CSS (copy from reference post — all theme vars, topbar, header, nav, article styles, footer, responsive)
2. Topbar → Sticky header with nav dropdown → Page hero → Article body → CTA → Related links → Footer
3. All links use `../` prefix (blog posts live in /blog/)
4. Blog nav link gets `class="active"`
5. No empty `<span></span>` in footer

## Metadata Checklist
- `<title>` — Post title + " | Autac USA"
- `<meta name="description">` — 150-160 chars, includes primary keyword
- OG tags (og:title, og:description, og:type="article", og:url, og:site_name, og:image)
- `<link rel="canonical">` — full https://www.autacusa.com/blog/filename.html
- `<link rel="icon" type="image/png" href="../logo.png">`

## Article Layout
- Hero: badge label, H1 title, subtitle paragraph, meta line (date + read time)
- Body: max-width 760px, centered
- H2 for main sections, H3 for subsections
- Include at least one comparison table where relevant
- CTA section at bottom with two buttons (quote + build-your-cord or product page)
- Related links section before footer (3 links to relevant product/tool pages)

## Writing Rules
- **Audience:** Engineers, purchasing managers, facility managers. B2B tone.
- **Voice:** Professional, specific, technically accurate. Not academic, not salesy.
- **Word count:** 1,200–2,200 words depending on topic depth.
- **Keywords:** Incorporate primary keyword in H1, first paragraph, 2-3 H2s, and naturally throughout. Don't force it.
- **Specifics over generics:** Use real numbers ("a 2-foot retracted cord extends to 10 feet" not "they come in various lengths").
- **Autac mentions:** 2–3 natural mentions in the body. Don't mention Autac in every section.
- **No filler:** No "In today's fast-paced world", "When it comes to", "In conclusion". Every paragraph must contain useful information.
- **Internal links:** Link to 1–2 product pages, quote.html or build-your-cord.html, and mention related blog posts once they exist.

## File Naming
Lowercase, hyphenated, keyword-rich:
- `coiled-extension-cords.html`
- `retractable-coil-cords.html`
- `recoil-extension-cord.html`

## After Creating a Post
1. Add it to `sitemap.xml` with the current date and priority 0.8
2. Update `blog/index.html` if needed to link to published posts
