# TGO Brands — website

v4: TGO as a senior brand operator and R&D partner taking Chinese brands into Pakistan, India, the
Philippines and the UAE — a service catalogue, the Launch programme, audience pages, market playbooks,
an entry estimator, a Travel desk with destination guides, Expeditions and a Partner Portal preview, built on
the tightened v3 Glass design (light) and the Obsidian design system (dark).
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
| `content/<lang>/*.json` | One file per v4 module, same shape in both languages: `services`, `launch`, `audiences`, `playbooks`, `estimator`, `expeditions`, `travel`, `portal`. |
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
| `/travel/` | Opens with the **visa and passport check** (below), then the travel desk: five destinations, who travels with us, six ways to travel, ground services, how a trip comes together, upcoming expeditions and the travel enquiry form |
| `/travel/<country>/` | Destination guides (`travel.guides`), written as the local desk briefing a client. Each guide is a list of typed `sections` — `cards`, `ticks`, `plans`, `phases`, `packages`, `split`, `faq`, `trip` (an expedition's day-by-day) and `desk` (services + host) — so each country carries what matters there. **Philippines:** entry rules by passport, flights, business districts, guests from China, islands, sample itineraries. **China:** the Canton Fair by phase, four packages up to the 12-day Five-City Sourcing Tour, the five cities, what's included, visas by passport, fair advice and FAQ. **India, Pakistan, Bangladesh:** business-first packages, the trade-fair calendar, visas by passport (including blocked neighbour combinations), each country's traps (WeChat in India, the security protocol for Chinese guests in Pakistan, hartals and the Friday weekend in Bangladesh), business geography, leisure extensions, itineraries, included / not included and FAQ; the Philippines guide carries the same packages, fairs, included list and FAQ. Market playbooks and trip pages link to their guide; Bangladesh is a travel destination without a playbook |
| `/expeditions/`, `/expeditions/<trip>/` | Dated group editions with a day-by-day itinerary |
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
  IN → Aryan, PH → Umer, AE → Shamas, otherwise Umair). The last screen needs at least one way to
  reply (email, phone or WeChat / WhatsApp). On submit the page POSTs the lead to `/api/lead`
  (below); when the server confirms delivery the applicant sees "Got it". If delivery is not set up,
  fails, or takes more than 15 seconds, the page hands off instead: a WhatsApp message to the market
  lead, pre-filled with the answers, and an email fallback to help@tgobrands.com — no lead is lost
  either way. The first-touch source (utm tag or referrer) rides along. A hidden honeypot field
  catches form-filling bots. Without JavaScript every question is listed in order.
- **Travel enquiry** (on `/travel/` and every destination guide, `#plan`) posts to `/api/lead` the same
  way. It needs a destination and a way to reply, `?to=PH` preselects a destination, and if delivery is
  not set up it hands off to the destination host's WhatsApp or to help@tgobrands.com.
- **Visa and passport check** (top of `/travel/`, `#check`; `?pp=CN&to=IN` preselects) — **any passport to any
  country or territory** (199 × 199). Passport, destination and purpose, plus optional arrival, departure and
  passport-expiry dates, give the visa type (visa-free, on arrival, e-Visa, electronic travel authorisation,
  visa before travel, not possible now, own country, or "we'll check"), the stay, the fee where known, an
  apply-by date (flagged when it has passed), a passport-validity verdict (six months from arrival by
  default; three months beyond departure for Schengen; six beyond the stay for the Philippines) and a
  checklist. Country names come from the browser (`Intl.DisplayNames`) in the page's language.
  Data, in order of precedence (no sources are shown on the site):
  1. `content/shared/visa_rules.json` — TGO's core corridors (our six destinations × the main passports),
     with fees, lead times and business notes.
  2. `content/shared/visa_overrides.json` — corrections checked against government announcements, each with
     its source URL (China's visa-free scheme and mutual exemptions, UK ETA, US ESTA and 2026 travel
     restrictions, Thailand's September 2026 scheme, Brazil, Malaysia, Vietnam, South Korea, Kenya, Sri Lanka,
     Russia). Rules can target `"*"`, filter by the current type (`when`) and exclude passports.
  3. `data/passport-index/passport-index-tidy-iso2.csv` — the base table for every pair (MIT, see the
     `LICENSE` beside it; its data is from January 2025, which is why the overrides exist).
  `build.py` merges them into `/assets/visa-<hash>.json` (~108 KB), which the tool loads after the page; the
  core corridors work even if that file fails to load. The table under the tool covers the main routes
  without JavaScript.
  **Refreshing:** replace the CSV with a newer copy if one is published, review `visa_overrides.json` against
  official portals (expiring schemes are noted with their end dates), rebuild, and run the fixture test
  described in the research file.
- **Live result areas** (`[aria-live]`: the checker and the entry estimator) are excluded from the scroll
  reveal, which only watches elements present at load.
- **Entry estimator** reads its data from a JSON block in the page; with JavaScript off it says so and
  points to the market playbooks, which carry the same facts.
- **Portal tabs** are ARIA tabs (arrow keys, Home, End); without JavaScript every pane is listed.
- **Pagination.** Insights lists `insights.perPage` posts per page (6) at `/insights/`, `/insights/page/2/`,
  and per category at `/insights/category/<name>/` (`insights.catSlugs`). Each post has an article at
  `/insights/<slug>/` with Previous / Next links. Section pages end with Previous / Next cards in
  this order: Home → What We Do → Services → Launch → Markets → Travel → Expeditions → Brands → Founders →
  Insights → Partner With Us. Service, audience, brand, playbook and trip pages step between their siblings.
- **Nav** merges with the page at the top and becomes a frosted capsule once scrolled; over the
  dark hero it switches to smoked glass with white links. On phones the links live in a
  `popover` drawer, which works without JavaScript.
- **How we work** opens as a dialog; its links fall back to `/what-we-do/#start`.
- **Reveal, marquees, hero video** respect `prefers-reduced-motion`; the video also skips Save-Data.
- **Scrolling.** In-page links glide (`scroll-behavior: smooth`, off under reduced motion) and land
  below the fixed nav (`scroll-padding-top`). The nav writes its shrink values on itself, only when
  they change, never on the root (which would restyle the whole page each frame). On touch screens
  the reveal is a rise and fade without the blur filter, which phones pay for while scrolling.
- **Separators.** `keep_dots()` puts a no-break space before every ` · ` in the page body, so a
  middle dot never starts a line.
- **Light / dark.** The site follows the device setting until the visitor picks a theme with the
  switch in the nav (sun / moon) or in the footer; the choice is kept in `localStorage` (`tgo-theme`).
  A one-line head script sets `data-theme` before first paint, so there is no flash. Light is the v3
  Glass design. Dark is the **Obsidian** design system: black ground, white Work Sans headings at 500,
  `#cbcbcb` body, one blue accent (`#6289ff`), GlowCards (gradient hairline edge, two neutral corner
  shades, no shadows), white primary buttons with a blue gradient arrow chip, line eyebrows between
  diamond-ended rules, broken-outline fields, a squarer frosted nav and a hairline footer grid lit by a
  grey and a blue glow. Every dark rule lives under `[data-theme="dark"]` at the end of `site.css`, so
  the light theme is untouched by it. Without JavaScript both switches hide and the page stays light.
- **Fonts.** Light is system fonts only (SF / PingFang / YaHei). Dark loads Work Sans from Google
  Fonts on English pages only, by script and as a print stylesheet first, so it never blocks the
  first paint. 中文 pages never request it (Google Fonts is blocked in mainland China) and use the
  CJK system faces, then Helvetica Neue / Arial. To remove the Google dependency entirely, self-host
  Work Sans (OFL) under `static/` and point `FONT_CSS` in `templates.py` at it.

## Lead delivery (`/api/lead`)

`api/lead.py` at the repo root is a Vercel Python function (standard library only). It takes both
partner applications and travel enquiries (`kind: "travel"`, routed by destination; China goes to
Umair). For each one it sends an **email** to the team (via [Resend](https://resend.com)) with the readable
application and the full record, reply-to set to the applicant, to help@tgobrands.com, and a **WhatsApp** message (via the
WhatsApp Cloud API) to the founder who covers the applicant's market. The recipient is worked out on
the server from the markets chosen; the founders' numbers are in `api/lead.py` and must match
`WHATSAPP` in `templates.py` and `site.js`. Each channel switches on when its environment variables are
set; with neither, the function answers 503 and the page hands off as above.

Set these in Vercel → Project → Settings → Environment Variables (Production), then redeploy:

| Variable | Value |
| --- | --- |
| `RESEND_API_KEY` | API key from Resend — the only one email needs |
| `LEAD_EMAIL_FROM` | Optional; sender on the verified domain, default `TGO Brands <leads@tgobrands.com>` |
| `LEAD_EMAIL_TO` | Optional; inboxes for every lead, comma-separated, default `help@tgobrands.com` |
| `WHATSAPP_TOKEN` | A permanent system-user token with `whatsapp_business_messaging` |
| `WHATSAPP_PHONE_ID` | The phone-number ID of the WhatsApp Business sending number |
| `WHATSAPP_TEMPLATE` | Optional; template name, default `new_lead` |
| `WHATSAPP_LANG` | Optional; template language code, default `en` |
| `WHATSAPP_API_VERSION` | Optional; Graph API version, default `v23.0` |

**Email setup (Resend).** Create an account, add the domain `tgobrands.com` and publish the DNS
records Resend shows (SPF and DKIM) where the domain's DNS is managed, then create an API key.

**WhatsApp setup (Meta).** In a Meta Business account, create an app with the WhatsApp product and
add a sending number — a number not already registered in the WhatsApp or WhatsApp Business app.
Create a system user with a permanent token. WhatsApp only lets a business start a conversation with
an approved template, so submit this one (category Utility, language English, name `new_lead`). It
serves both partner applications and travel enquiries:

> New TGO enquiry for {{1}}: {{2}}, {{3}}. {{4}}. Reply to {{5}}. The full details are in the help inbox.

Sample values for the review: `Umer`, `Li Wei (Shenzhen Power Co.)`, `Travel enquiry`,
`Philippines · 6-15 people · March 2027 · Business and holiday`, `liwei@example.com`. A partner
application fills {{3}} with the applicant type and {{4}} with `Markets: Pakistan, UAE · lead score 72/90`. Meta charges a small fee per template message. While the
app is in test mode, only numbers added to its recipient list receive messages.

Testing: the function's outbound calls go through `post_json()`, so tests can replace it and inspect
exactly what would be sent to Resend and Meta.

## Still to supply

Rendered as non-clickable placeholders, or marked as drafts, until filled in:

- Prices: service and stage fees, trip prices ("Price on application" for now)
- Expedition dates (each edition says "dates to be announced")
- Estimator and playbook figures — approvals, weeks, duty bands, landed-cost factors — for each
  market lead to verify; they move with every budget
- Home figures (`home.proof`) and the Portal's sample partner, which is illustrative
- Native review of all 中文 copy, the v4 modules especially
- China / Canton Fair: confirm the package prices (Fair Week from ¥8,800, Fair and Factories from ¥16,800,
  Five-City Sourcing Tour from ¥29,800), the inclusions (flights from the listed hubs, travel insurance,
  interpreter languages) and the spring 2027 dates once the fair announces them. The market study behind
  the page is in [`research/canton-fair-tours-2026.md`](../research/canton-fair-tours-2026.md)
- India, Pakistan, Bangladesh and Philippines travel packages: confirm prices (all "from" US$ figures),
  inclusions and who hosts Bangladesh (enquiries currently route to Aryan). Study:
  [`research/india-pakistan-bangladesh-philippines-travel-2026.md`](../research/india-pakistan-bangladesh-philippines-travel-2026.md)
- Visa rules: re-check `content/shared/visa_rules.json` regularly — China's 30-day visa-free pilot runs to
  31 December 2026, and the India–Pakistan and India–Bangladesh rules have changed several times
- Travel: confirm the services promised (meet and assist, Cantonese and Hokkien interpreters, a planner
  on call day and night) and re-check the Philippines entry rules and flights before each season
- WeChat QR and the public WhatsApp number — `contact.channels.*.href` in the content files
- Channel link (YouTube for EN, Bilibili for 中文 — never YouTube on `/zh/`) — `insights.videoHref`
- Privacy and Terms pages (footer)
- Real photography and founder portraits (every image is currently `photo.jpg`)
- Resend and WhatsApp credentials for lead delivery (above)
- The rest of Phase 2: a database for leads, the live Portal with sign-in, investor deck uploads

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
