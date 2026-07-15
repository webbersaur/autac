# Autac SEO: Diagnosis + Sitewide Address Fix

**Date:** 2026-07-14
**Commits:** `6fb65d9` (address), plus phone alignment and PO Box restoration
**Started as:** "Can we block foreign countries without hurting SEO?"
**Ended as:** the business address was wrong in 158 files, and the traffic collapse had nothing to do with bots.

---

## 1. The original question: bot traffic

GA4 showed Singapore at 34% of users. It is bot traffic, and it is not an SEO problem.

| Country | GA4 users | Engagement rate | Avg engagement time |
|---|---|---|---|
| United States | 810 (38%) | 23.79% | 35s |
| **Singapore** | **732 (34%)** | **2.58%** | **2s** |
| China | 127 | 2.34% | 1s |
| Vietnam | 54 | 0% | 0s |
| Canada | 22 | **58.62%** | 46s |

Cross-checked against Google Search Console for the same window:

| | GA4 (users) | GSC (impressions) |
|---|---|---|
| United States | 810 (38%) | 16,134 (**84.2%**) |
| Singapore | 732 (**34%**) | 172 (**0.9%**) |

Singapore is 0.9% of actual search presence but 34% of GA4 "users" - a ~38x discrepancy from an independent source. These are headless scrapers hitting URLs directly, not people arriving from Google.

**Conclusions:**
- GA4 traffic is not a Google ranking input. The bots cost zero rankings. They pollute measurement only.
- Country-level *blocking* is the actual SEO risk (Googlebot and AI crawlers do not all crawl from US IPs). Never do this in robots.txt, `noindex`, or hreflang.
- GA4 has **no property-wide country filter**. Data Filters support internal/developer traffic only. Report-level filters are UI-only (no API).
- **Recommendation: do nothing about the bots.** Use GSC, which is inherently bot-proof, as the SEO dashboard.

---

## 2. What actually happened to the traffic

Sitewide GSC, all countries:

```
Feb   74,415 impr   244 clicks   pos  9.0
Mar   71,372 impr   239 clicks   pos 11.7
Apr   48,978 impr   183 clicks   pos 13.6
May    6,179 impr    26 clicks   pos 21.1   <-- 87% collapse
Jun   10,486 impr    89 clicks   pos 15.7
Jul   13,444 impr    69 clicks   pos 16.2   (13 days)
```

Daily data across the cliff shows a **steady decay** from ~2,000/day on Apr 19 to ~100/day by May 20 - not a step-change on a single day.

**A slow decay to near-zero is Google progressively deindexing pages. A penalty or algorithm update is a cliff.**

Cause: the WordPress-to-static migration deleted the high-traffic blog pages. Google took roughly a month to drop them. The 74k February impressions *were* those pages.

**The fix already worked.** 20 of 24 dropped pages were restored (2026-05-05, 2026-06-16). They are re-ranking (`straight-wiring-a-cooling-fan` at pos 4.9, `how-to-fix-retractable-cord-on-iron` at 8.9) and impressions are climbing 6k -> 10k -> 13k. **Leave it alone; it recovers on its own.**

The 4 un-restored pages are garden hose reel articles (2,739 impressions, 35 clicks) and `wp-posts.json` - the WP archive `restore_posts.py` reads from - is not in the repo. Not worth restoring.

---

## 3. The strategic problem (UNSOLVED)

Content performance, Jun 1 - Jul 13:

| Content type | Pages | Impressions | Clicks | CTR | Avg pos |
|---|---|---|---|---|---|
| NEW: state/geo pages | 14 | 346 | **1** | 0.29% | 17.3 |
| NEW: blog posts | 27 | 1,783 | **4** | 0.22% | 20.2 |
| RESTORED: old WP posts | 19 | 14,675 | 77 | 0.52% | 11.9 |
| COMMERCIAL: product hubs | 10 | 1,864 | 7 | 0.38% | **27.3** |
| **COMMERCIAL: homepage** | **1** | **591** | **43** | **7.28%** | **6.4** |

**The entire new content program - 41 pages - produced 5 clicks in six weeks.** The blog-publish cron was disabled on 2026-07-14 (`~/Library/LaunchAgents/com.autac.publish-blog-batch.plist.disabled`). The scorecard cron still runs.

Commercial-intent queries: **139 queries, 1,130 impressions, 1 click. Only 6% of total visibility.**

```
"coiled cords"              pos 35.1
"retractile cord"           pos 34.1
"retractile cords"          pos 56.3   <-- the core product
"retractable cords"         pos 47.2
"custom retractile cables"  pos 43.9
```

Product hubs have good titles, one clean H1, ~1,500 words, and 522 inbound internal links each. **Good on-page + rank 27-56 = an authority problem, not an on-page problem.** No amount of content fixes this. It needs links.

The homepage converts at **7.28% CTR**. Demand is brand-driven, not search-driven.

**Open strategic question: is organic search the right channel at all?** Custom retractile cords are bought via RFQ, ThomasNet, trade shows, and referrals - not by googling "coiled cords" (66 impressions in six weeks).

### The brand term is FINE - do not optimize it
`autac` ranks **#1 with sitelinks and a Knowledge Panel.** The GSC "position 8.5" was an averaging artifact across 15 pages. Brand CTR is only 6-10% because **AUTAC is also a biochemistry term** (autophagy-targeting chimera) - much of that query's demand is researchers, and never will be Autac's.

---

## 4. The address bug (FIXED)

**Autac's real HQ and plant: 25 Thompson Rd, Branford, CT 06405.** Confirmed by the Google Business Profile and Google's own AI Overview.

The site had it wrong in **158 files**:

```
5 Branford Industrial Court  ->  25 Thompson Rd            (1x, homepage schema, bogus)
P.O. Box 306                 ->  25 Thompson Rd          (334x, topbar + footer)
North Branford               ->  Branford                (742x)
06471                        ->  06405                   (336x)
geo 41.3854,-72.7673         ->  41.3025,-72.7773        (was ~6 miles off)
North%20Branford             ->  Branford                (Google Maps embed URL)
```

It had propagated into hero copy, the topbar, the contact page, `LocalBusiness` schema on every page, all blog posts, and every generated geo page - **and had leaked off-site into third-party citations** (MapQuest still says "North Branford"). That is a NAP consistency failure, which erodes the local-entity trust signals linking the site to the business.

All 182 JSON-LD blocks validate post-change.

### The PO Box is real
`P.O. Box 306, North Branford, CT 06471` **is** Autac's genuine mailing/remittance address. The problem was that it was being displayed, unlabelled, as the *company address* in the topbar and footer of all 158 pages. Google will not accept a PO Box for a physical-location entity.

It now lives on the **contact page only**, labelled:

```
Facility & Shipping     25 Thompson Rd, Branford, CT 06405
Mailing & Remittance    P.O. Box 306, North Branford, CT 06471
```

**Rule: two addresses, two jobs.** Street address for schema/GBP/entity. PO Box for mail. Keep the PO Box out of all schema and out of the topbar/footer. Do not delete it either.

### Phone
GBP primary is the local line `(203) 481-3444`. The schema declared the toll-free `+1-800-243-3161` as primary on the homepage and 17 state pages, breaking the phone half of NAP matching.

Schema `telephone` is now `+1-203-481-3444` everywhere. The 800 number is preserved as a schema.org `contactPoint` with `contactType: "sales"` - it remains a first-class number without competing with GBP for entity matching. Visible site copy shows both, unchanged.

---

## 5. Other homepage changes shipped

- Added Organization `alternateName` (`Autac`, `AUTAC`, `Autac Inc`, `Autac Incorporated`, `Autac Cords`) - disambiguates the brand from the biochemistry term.
- Added visible `rel="me"` footer links to LinkedIn and YouTube (both were declared in `sameAs` but never actually linked from the site).
- Retitled: `Autac USA - Retractile & Coil Cord Manufacturer Since 1947` (was `The Source for Coil Cords`, which contained none of the target terms, plus an em dash).

---

## 6. Open actions

| # | Action | Owner | Status | Why |
|---|---|---|---|---|
| 1 | **Fix the ThomasNet listing** to 25 Thompson Rd, Branford, CT 06405 + (203) 481-3444 | Chris | **DONE 2026-07-14** | ThomasNet is the top-authority B2B citation and the one place a real buyer sends an RFQ |
| 2 | Fix MapQuest | Chris | **Address DONE.** Description body copy unverified - may still say "North Branford" | Same NAP contradiction |
| 3 | Create `admin@autacusa.com` -> forward to Gmail (M365 shared mailbox + Full Access + Send As) | Chris | In progress - getting tenant admin access | Needed to claim/fix remaining listings |
| 4 | Prune `include:websitewelcome.com` from the SPF record (stale HostGator entry) | Chris | Open | An old host is still authorised to send mail as autacusa.com. DNS is at GoDaddy. |
| 5 | URL-Inspect / Request-Indexing the schema-changed pages (~10/day, GSC UI only) | Chris | **Ready - worklist reprioritized 2026-07-15, not yet started** | Gets the corrected NAP/schema in front of Google in days not weeks. See plan below. |
| 6 | Clean up em dashes: 26 pages still have them in `<title>` | open | Open | Workspace convention violation |
| 7 | **Decide on the SEO budget** | Chris + client | Open | Product pages rank 27-56 on authority, not on-page. More content will not fix it. |

### Request-Indexing plan (action #5) - REPRIORITIZED 2026-07-15, ready to execute

The old worklist was ordered around the June recovery (restored blog pages first). It has been rewritten to target the **address fix** instead - because Request-Indexing only makes Google re-crawl sooner, it does not raise rankings, so it is only worth doing on pages whose content actually changed. The corrected NAP/schema is live but Google still serves the old wrong address; this run fixes that.

Verified 2026-07-15: all Day 1/2 URLs return 200, and live homepage + retractile-cords hub serve only `25 Thompson` / `06405` (no `North Branford` / `06471`). Safe to re-crawl.

**Execution (GSC UI, `https://autacusa.com/` property, ~10-12/day cap):**
- **First, once:** Sitemaps section -> resubmit `sitemap.xml` (background-crawls the tail so the hand-requests can focus on the pages that matter).
- **Day 1 (10):** homepage, `/contact/`, the 5 product hubs, `/color-charts/`, `/about/`, `/solutions/` - where the schema changed.
- **Day 2 (10):** `/service-areas/` hub + 9 state pages (they carried the corrected schema `telephone`).
- **Day 3 (8):** the remaining 8 state pages.
- Stop there. Everything below Day 3 in the worklist is already indexed; the sitemap resubmit covers it.

Full ordered list: `seo-reports/request-indexing-priority.txt`. Old version backed up alongside it as `.bak-20260715`. **Status: not yet started - Chris to click through in GSC.**

### Remaining citation cleanup (low priority - hygiene, not growth)

The wrong address leaked off-site before it was fixed. Still carrying stale data as of 2026-07-14:

- **Yahoo Local** (`local.yahoo.com/info-27075686-autac-inc-branford`) - unverified whether live-wrong or just cached
- **latinbusinesses.com** - lists Autac under **"cleaning and restoration"**. Wrong *category*, which is worse than a wrong address.
- General web search still surfaces "P.O. Box 306, North Branford, CT 06471" + the 800 number as Autac's NAP.

**Free and worth more than MapQuest:** Bing Places and Apple Business Connect (both free, direct, ~15 min each). Foursquare Places syndicates widely and is a free claim.

**On paying for citation cleanup:** BrightLocal Citation Builder is the right tool if it comes to that - a **one-time** purchase (~$100-200 for 20-30 citations), because BrightLocal's submissions are permanent. **Do NOT buy Yext, Semrush Listing Management, or Moz Local** - they all *lease* the correction and the data reverts to the old wrong address the moment you stop paying. Run BrightLocal's Citation Tracker audit first; the number of bad citations may be small enough to fix by hand for free.

**Set expectations: citations are a local signal.** They feed the map pack and "near me" queries. Autac is a national B2B manufacturer - nobody sources a custom retractile cord by searching nearby. This is hygiene that protects the entity and stops the wrong address propagating. It will not move the commercial rankings, which are an authority problem (see section 3).

## 7. Infrastructure notes

- **GSC API works.** `~/.env` has working OAuth creds. Scope is `webmasters` ONLY.
- **GA4 API is NOT reachable** (no analytics scope), and adding it would not help - GA4 report filters have no API.
- **Ahrefs MCP `gsc-*`, `serp-overview`, `site-explorer-*` all return `Insufficient plan`.** No backlink or SERP data available through it.
- **Chrome DevTools MCP cannot sign into Google** (CDP-controlled browser is blocked) and Google captchas SERP scraping.
- `autacusa.com` mail = **Microsoft 365**; DNS = **GoDaddy**. `webbersaurus.com` = Google Cloud DNS, no mail configured.
