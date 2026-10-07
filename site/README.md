# TGO Brands — website

v4: TGO as a senior brand operator and R&D partner taking Chinese brands into Pakistan, India, the
Philippines and the UAE — a service catalogue, the Launch programme, audience pages, market playbooks,
an entry estimator, Expeditions and a Partner Portal preview, built on the tightened v3 Glass design.
Static, pre-rendered, bilingual (`/` English, `/zh/` 中文). No framework and no dependencies:
Python 3 standard library to build, plain HTML/CSS/JS out.

```bash
python3 build.py                                   # writes ./dist (every page + sitemap, robots, llms.txt)
python3 -m http.server 8000 --directory dist       # preview at http://localhost:8000
```

Deploy `dist/` to any static host (Vercel, Netlify, Cloudflare Pages, S3). Clean URLs are
folders with an `index.html`, so no rewrites are needed.

## Layout

| Path | What it is |
| --- | --- |
| `content/en.json`, `content/zh.json` | Site-wide copy: nav, footer, home, the original pages, the application, insights. |
| `content/<lang>/*.json` | One file per v4 module, same shape in both languages: `services`, `launch`, `audiences`, `playbooks`, `estimator`, `expeditions`, `portal`. |
| `content/shared/*.json` | Language-neutral data — the estimator rules (category × market → approvals, weeks, duty band, tax, landed-cost factor, services). |
| `templates.py` | Page templates (one function per page) and the shared head/nav/footer. |
| `build.py` | Merges the content files (a key defined twice stops the build), renders every page for both locales, versions the CSS/JS, writes sitemap (with hreflang pairs), `robots.txt`, `llms.txt`. |
| `static/site.css` | The one stylesheet: tokens at the top, then base, components, pages, the 中文 layer, responsive, motion. |
| `static/site.js` | Progressive enhancement only — every page is complete without it. |
| `static/photo.jpg`, `static/hero.mp4` | Placeholder photography and the hero loop. |

## Pages

| URL | Page |
| --- | --- |
| `/` | Home: hero, the four audience doors, three service groups, Launch stages, estimator and next expedition, brands, founders, insights |
| `/services/`, `/services/<slug>/` | The catalogue in three groups (Enter the market, Sell and grow, Run it) and one page per service (15): problem, deliverables, timeline, engagement model, lead, markets, related services |
| `/launch/` | TGO Launch: seven stages with scope, duration, deliverable and pricing model; who it is for; how pricing works; FAQ |
| `/for/<audience>/` | Manufacturers, distributors & retailers, creators, investors — each links into its own application branch (`/partner/?as=…`) |
| `/markets/`, `/markets/<country>/` | The four markets and a playbook per country: approvals with typical weeks, customs and tax, channels, cities, visiting |
| `/tools/entry-estimator/` | Product × market → approvals, weeks to the first shelf, duty band, import tax, landed-cost range, matching services. Accepts `?market=` and `?category=` |
| `/expeditions/`, `/expeditions/<trip>/` | Trip types, travel support, and dated editions with a day-by-day itinerary |
| `/portal/` | Partner Portal preview: one sample partner's stages, approvals, shipments, sell-through, documents and messages — labelled as sample data |
| `/partner/` | The application (below) |

Adding a service, trip, market playbook or audience: add the item (with a `slug`) to the module file in
**both** languages and rebuild — cards, detail pages, links, sitemap and `llms.txt` follow. Estimator
rules live once, in `content/shared/estimator_rules.json`; certificate and tax names are translated in
each language's `estimator.json`.

Adding an insight: add a post (with a `slug`, its category name and optional `body` paragraphs) to
`insights.posts` in both content files, newest first. Its article page, the category listings, page
numbers, Previous / Next links, sitemap and `llms.txt` all follow. Until `body` has paragraphs the
article shows a "full article coming soon" note. Both languages must produce the same pages — the
build stops if they differ.

Adding a brand: add an item (with a `slug`) to `brands.items` in both content files and rebuild —
the table, the cards and the `/brands/<slug>/` pages all follow.

## Behaviour

- **Application** (`/partner/`) is one form. With JavaScript it runs one question per screen and
  branches on the first answer (manufacturer, distributor/retailer, creator, investor), with
  questions and wording per audience. `?as=<audience>` preselects the branch and `?service=<slug>`
  notes the service the visitor came from. It scores the lead and routes it by market (PK → Umair,
  IN → Aryan, PH → Umer, AE → Shamas, otherwise Umair). While the site is static the done screen hands
  off: a WhatsApp message to that person, pre-filled with the answers, and an email fallback to
  hello@tgobrands.com. The first-touch source (utm tag or referrer) rides along in the message. To send
  leads to a backend instead, set `data-endpoint` on the form in `templates.py`; `site.js` then POSTs
  the lead as JSON. Without JavaScript every question is listed in order.
- **Entry estimator** reads its data from a JSON block in the page; with JavaScript off it says so and
  points to the market playbooks, which carry the same facts.
- **Portal tabs** are ARIA tabs (arrow keys, Home, End); without JavaScript every pane is listed.
- **Pagination.** Insights lists `insights.perPage` posts per page (6) at `/insights/`, `/insights/page/2/`,
  and per category at `/insights/category/<name>/` (`insights.catSlugs`). Each post has an article at
  `/insights/<slug>/` with Previous / Next links. Section pages end with Previous / Next cards in
  this order: Home → What We Do → Services → Launch → Markets → Expeditions → Brands → Founders →
  Insights → Partner With Us. Service, audience, brand, playbook and trip pages step between their siblings.
- **Nav** merges with the page at the top and becomes a frosted capsule once scrolled; over the
  dark hero it switches to smoked glass with white links. On phones the links live in a
  `popover` drawer, which works without JavaScript.
- **How we work** opens as a dialog; its links fall back to `/what-we-do/#start`.
- **Reveal, marquees, hero video** respect `prefers-reduced-motion`; the video also skips Save-Data.
- **Fonts** are system fonts only (SF / PingFang / YaHei) — nothing loads from Google Fonts, so the
  中文 site is not blocked in the mainland.

## Still to supply

Rendered as non-clickable placeholders, or marked as drafts, until filled in:

- Prices: service and stage fees, trip prices ("Price on application" for now)
- Expedition dates (each edition says "dates to be announced")
- Estimator and playbook figures — approvals, weeks, duty bands, landed-cost factors — for each
  market lead to verify; they move with every budget
- Home figures (`home.proof`) and the Portal's sample partner, which is illustrative
- Native review of all 中文 copy, the v4 modules especially
- WeChat QR and the public WhatsApp number — `contact.channels.*.href` in the content files
- Channel link (YouTube for EN, Bilibili for 中文 — never YouTube on `/zh/`) — `insights.videoHref`
- Privacy and Terms pages (footer)
- Real photography and founder portraits (every image is currently `photo.jpg`)
- A backend (Phase 2) for stored leads, the live Portal and investor deck uploads

## What changed from the v3 prototype

The v3 file stacked about ten CSS override passes; this resolves them into one system and fixes what
those passes broke:

- One spacing rhythm on every page (the tighter home scale), one card surface: white with a soft shadow
  on the grey ground, ground-grey on white bands — cards no longer vanish white-on-white.
- 中文 headings with a max-width were pushed ~100px off-centre by a CJK margin reset; now centred.
- No more 3 + 1 orphan grids: steps, market facts, brand specs and explore cards are 2 × 2, an odd
  last service spans the row, offices sit in a centred row.
- Headings sized to their column (founder names, story acts, contact channels were 52px in 270px columns);
  mixed-alignment rows on What We Do and Insights now read as one centred column.
- Small grey text darkened to meet WCAG AA; links use the AA-safe blue; status tags were leftover red
  from the old design system and are now in the site's blue.
- Photos run flush inside cards (no rounded notch), the marquee loops without a seam, the dialog close
  button and survey options match the rest of the controls, the nav capsule is opaque enough to read.
- Copy fixes: "the UAEs", "Four things" over five pillars, "our three markets" in a four-market pitch.

## Audit pass (mobile first)

Checked at 360, 390, 820, 1280 and 1680px in both languages for contrast, touch-target size,
tiny text, overflow and grid orphans:

- Every interactive control has a 44px touch target on phones (logo, language switch, burger,
  chips, text-style links, footer links, table links); the language switch went from 11px to 12px.
- Contrast: the ticker grey and the dialog's small blue labels now meet AA; placeholder actions
  (QR code, WhatsApp, channel link, Privacy, Terms) read as grey text rather than dead blue links.
- Home on a phone is ~1,800px shorter: the hero fits one screen with equal-width stacked actions and the
  route line clear of the fade; founders are compact rows instead of three full-screen portraits; card
  insets, gaps and the lead/subhead sizes step down one notch.
- Phones: chip rows fill the width (no lone chip), offices read as a city/role list, the brand table
  becomes compact rows, the footer stacks with its links on one row, long copy on What We Do and
  Insights sits flush left, and headings balance their lines instead of stranding a word.
- Tablet: three-item rows (posts, story acts, contact channels) stay three-up; the premise stacks to
  one column at a readable measure — no 2 + 1 orphans at any width.
