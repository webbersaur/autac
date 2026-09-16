# Autac satellite / landing-site audit - 2026-09-09

Question: are the separate landing-page sites hurting autacusa.com?
Short answer: not measurably, but they add nothing, three carry the wrong NAP
and a duplicate "Autac Inc" Organization schema, and one brand-named Weebly
takes a slot on the "autac inc" SERP. Recommendation at the bottom.

## The network (15 properties found)

### Built by Chris on SiteGround (Divi 4.27.8, Yoast, one page each)
| Domain | Title | Pages | Notes |
|---|---|---|---|
| retractilecords.com | Retractile Cords - in stock now | 1 | 99% identical copy to the other two |
| custompowercord.com | Custom Power Cords | 2 | "Sample Page" indexed |
| coilcorddirect.com | Coil Cord Direct | 1 | empty H1 |
| retracti-cords.com | Custom Lanyards by Retracti Cords | 6 (Woo) | different product; 86% shared boilerplate |

All four: wrong NAP in footer ("P.O. Box 306, North Branford, CT 06471"),
Organization schema named "Autac Inc" (first three), links to dead legacy
URLs on autacusa.com (2021 catalog PDFs 403, /straight-wire/ 404,
/retracti-cords/ 404, /news-press/ 308). Copy is NOT lifted from
autacusa.com (0 shared lines) so there is no duplicate-content contest with
the main site. Indexed by Google. Do not appear in top 10 for retractile
cords / coiled cords / custom power cords / curly cords (checked live).

### Older free-platform satellites (previous SEO vendor pattern)
| Property | Title | Links to autacusa.com |
|---|---|---|
| autacusa.weebly.com | Autac, Inc. - Home | yes (2) |
| curlycords.weebly.com | Autac, Inc. - Curly Cords | yes (4) + g.page |
| retractilecordsbranford.weebly.com | Autac, Inc. - Retractile Cords | yes (5) |
| customcoiledcords.weebly.com | Custom Coiled Cords | yes (4) + g.page |
| customelectricalcables.weebly.com | Retractile Power Cords | yes (5) + g.page |
| retractilepowercords.weebly.com | Retractile Power Cords | yes (2) |
| retractablecoilcable.weebly.com | Retractile Power Cords - Home | yes (1) + g.page |
| coiledcords.weebly.com | Curly Cords - Coiled Cords | yes (3) |
| autacusa1.wordpress.com | Autac, Inc. | yes (2) |
| retractilecords.blogspot.com | Retractile Cords | no (posts Nov 2022) |
| autacusact.blogspot.com | Autac, Inc. | no (posts 2022) |
| sites.google.com/view/retractable-coil-cable-usa | Retractable Coil Cable | via google redirect only |

Weebly set is 83-96% identical to each other (template spun). NAP on them
is the correct 25 Thompson Rd. Three are named "Autac, Inc." and read like
alternate homepages for the entity.

## Evidence on harm
- Brand SERP "autac": autacusa.com #1, no satellite in top 5.
- Brand SERP "autac inc": autacusa.com #1, Facebook, LinkedIn, MapQuest, BBB,
  then autacusa.weebly.com at #6. Slot taken, no clicks lost.
- GSC last 28d: "autac" homepage pos 3.5 (211 impr, 27 clicks); "autac inc"
  pos 1.0. Head terms 15-36 as before; nothing new attributable to satellites.
- "retractile cords manufacturer" (search API): autacusa.com 6-7 with
  retractilecordsbranford.weebly.com and customcoiledcords.weebly.com at 8-9.
  That is the one place the satellites compete with the main site.
- No shared copy with autacusa.com, so Google is not choosing a clone over it.
- Ahrefs backlink/keyword endpoints are plan-gated; DR not retrievable.

## Recommendation
1. retractilecords.com -> 301 to https://autacusa.com/retractile-cords/
   coilcorddirect.com -> 301 to https://autacusa.com/coiled-cords/
   custompowercord.com -> 301 to https://autacusa.com/cord-sets/ (or
   /build-your-cord/). Domain-level redirect in SiteGround Site Tools; keep
   the domains registered. Topically equivalent, so not a soft 404.
   If Chris wants to keep them live instead: unique copy, fix NAP to
   25 Thompson Rd, drop or align the Organization schema (sameAs ->
   autacusa.com), fix the dead legacy links, noindex sample-page.
2. retracti-cords.com: keep (separate product/brand). Fix NAP to 25 Thompson
   Rd, add Organization sameAs to autacusa.com.
3. Free-platform satellites: delete or set to noindex, brand-named ones
   first (autacusa.weebly.com, autacusa1.wordpress.com, autacusact.blogspot.com).
   Needs the old logins. If unreachable, leave them; they are not causing
   measurable harm.
4. No disavow needed.

## Executed 2026-09-09 (same day, all verified live with curl)
- retractilecords.com/  -> 301 https://autacusa.com/retractile-cords/  (SiteGround Site Tools > Domain > Redirects; also catches www, http, and deep paths)
- coilcorddirect.com/   -> 301 https://autacusa.com/coiled-cords/
- custompowercord.com/  -> 301 https://autacusa.com/cord-sets/  (sample-page now lands on the hub too)
- retracti-cords.com: NAP on pages 8 (home) and 13029 (lanyards) changed from
  "P.O. Box 306 / North Branford, CT 06471" to "25 Thompson Rd / Branford, CT 06405"
  via REST; Yoast Site representation > Other profiles = https://autacusa.com/
  so the Organization schema now emits sameAs. SG cache purged.
- Domains stay registered on SiteGround; the WordPress installs behind the three
  clones are untouched (redirect happens in .htaccess ahead of WP).

## Blocked: free-platform satellites (needs client)
Ownership found from public feeds/APIs:
- autacusa1.wordpress.com: WordPress.com user "autacusact"
- autacusact.blogspot.com: author "Autac, Inc." (same vendor Google account)
- retractilecords.blogspot.com: author "Abdus Salam" (offshore SEO freelancer)
- Weebly x8 and the Google Site: not in Chris's Weebly, Blogger, or Google Sites
  accounts (checked while signed in)
Chris's accounts own none of them. Ask Marie-Louise / Autac whether they have the
"autacusact" Gmail or the 2022 vendor's logins. If yes: delete the sites, or set
Weebly SEO > "Hide site from search engines", Blogger Settings > "Visible to
search engines" off, WordPress.com Privacy > "Discourage search engines".
If no: leave them; they cause no measurable harm. Do not file platform abuse
reports without the client's say-so.

## Watch (2-4 weeks)
- GSC: /retractile-cords/, /coiled-cords/, /cord-sets/ impressions; the three
  EMDs had negligible traffic so expect no visible bump, only cleaner SERPs.
- "autac inc" SERP: autacusa.weebly.com at #6 stays until the client retires it.
