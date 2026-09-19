# TGO Brands — Website Architecture, Sitemap & Build Spec

**Domain:** TGObrands.com
**Entity:** Hong Kong
**Languages:** English + 中文 (both at launch)
**Timeline:** 4 weeks to launch
**Build path:** Claude Design → handoff to in-house full-stack dev

> **All names, numbers and brand names below marked `⟨PLACEHOLDER⟩` are dummy data.**
> Replace with real values before launch. Structure is final; content is not.

---

# PART 1 — What actually makes a site still look current in 2030

Most "futuristic" websites age badly because they chase visual effects. The sites that still look right after five years get the *architecture* right and stay restrained on the surface. Six shifts matter for you specifically.

### 1. Your site now has two audiences: people, and AI agents

This is the single biggest change in how websites work, and most sites haven't caught up. A meaningful share of your discovery in 2026 already happens through ChatGPT, Claude, Perplexity, and 豆包 / Kimi on the Chinese side — someone asks "who can help me distribute my product in Pakistan?" and an LLM answers from what it can read.

That means being **citable** matters as much as ranking. Practically:

- Server-render everything. Content that only exists after JavaScript runs is invisible to a lot of crawlers and agents.
- Publish `/llms.txt` — a plain-text summary of who you are, what you do, and your key pages.
- Structured data (JSON-LD): `Organization`, `Person` for each founder, `Article` for posts, `FAQPage` on partner pages.
- Write in clear factual sentences. "TGO Brands is a Hong Kong holding company that brings Chinese consumer electronics brands into Pakistan, India and the Philippines" is a sentence an LLM can quote. "We unlock synergies across emerging markets" is not.

### 2. Static-first, edge-delivered

Pre-render your pages at build time and serve them from the edge. A 7-page company site has no business being a heavy client-side app. This is also what keeps you fast in Hong Kong, Karachi, Mumbai and Manila simultaneously — four places with very different network conditions.

### 3. CSS has absorbed what used to need JavaScript

Modern CSS handles container queries, `:has()`, scroll-driven animations, view transitions, nesting, and `light-dark()`. Sites built on native CSS in 2026 will still run in 2032. Sites built on a JS animation library will break, get abandoned, or need a rewrite.

Use the **View Transitions API** for page-to-page transitions. You get an app-like feel with no SPA framework overhead — this is the thing that will make the site feel modern in a way people can't quite name.

### 4. Fluid, not breakpointed

`clamp()` for type and spacing, container queries instead of device breakpoints. Layouts that respond to their container rather than the viewport survive redesigns, new device sizes, and embedding.

### 5. Bilingual has to be structural, not bolted on

This is where most Chinese-facing sites fail. Build the content model with locale as a first-class field from day one. Concretely for you:

- **Self-host all fonts, subsetted.** Google Fonts is blocked in mainland China. A CDN font request that hangs for 8 seconds means a blank page for half your target audience.
- **Chinese needs different type settings.** CJK glyphs are stroke-dense: larger minimum size (16px floor, 17px preferred), looser line-height (1.75–1.9 vs 1.5 for Latin), tighter letter-spacing. A single stylesheet for both languages will make one of them look wrong.
- **Never embed YouTube on the `/zh` side.** Blocked. Serve Bilibili or Tencent Video, or a self-hosted MP4.
- Subset your CJK font aggressively — a full Noto Sans SC is ~10MB. Subset to your actual characters and it's under 300KB.

### 6. Accessibility is now a compliance issue, not a nice-to-have

The EU Accessibility Act is in force. If you ever sell into or market toward Europe, WCAG 2.2 AA is a legal floor, not a bonus. It's also cheap if built in from the start and expensive to retrofit.

### What dates fastest — avoid all of these

Scroll-jacking. WebGL blob heroes. Cursor followers. Loading animations before content. Aggressive parallax. Glassmorphism. AI-gradient mesh backgrounds. Text that animates in letter-by-letter. Horizontal scroll sections. Any of these will make the site look unmistakably "2024" by 2028.

**What doesn't date:** confident typography, generous whitespace, real photography, fast load, and one strong structural idea.

---

# PART 2 — Sitemap

```
TGObrands.com
│
├── /                        Home
├── /what-we-do              The bridge — services & model
├── /brands                  Portfolio (house of brands)
│   ├── /brands/⟨kiro⟩        Brand detail — accessories
│   └── /brands/⟨voltara⟩     Brand detail — solar & storage
├── /founders                Our story + three founder profiles
├── /markets                 Pakistan · India · Philippines
├── /insights                Notes from the route (blog)
│   └── /insights/[slug]
├── /partner                 Survey CTA — the conversion page
│
├── /contact                 Regional contact — WeChat / WhatsApp / email
├── /privacy  /terms         Legal
├── /llms.txt                AI-agent summary
└── /zh/*                    Full Chinese mirror of all of the above
```

**7 primary pages.** Brand detail pages grow as the portfolio grows without adding nav weight.

### Navigation

Primary nav: **What We Do · Brands · Founders · Markets · Insights**
Right side: **中文 / EN** toggle, then **Partner With Us** (the only button in the nav)

Footer carries Contact, legal, WeChat QR, and social.

---

# PART 3 — Page-by-page specification

## `/` Home

The job of this page: a Chinese manufacturer decides within 15 seconds whether you're serious, and a YouTube viewer decides whether to keep reading.

| Section | Content |
|---|---|
| **Hero — The Route** | The signature element. A drawn line originating in Guangzhou branching to Karachi, Mumbai, Manila. Headline: **"We take Chinese brands to the world."** Sub: "Starting where we live — Pakistan, India, the Philippines. Three founders, three markets, one route from Guangzhou." |
| **The premise** | 3 short paragraphs. Why a Chinese manufacturer needs someone on the ground, not an agent in an office. Warm, first-person plural. |
| **Proof strip** | 4 figures maximum. ⟨45+ combined years in China⟩ · ⟨3 live markets⟩ · ⟨6 ventures built⟩ · ⟨40+ manufacturing partners⟩ — with footnote: "Figures as of ⟨Q3 2026⟩, across TGO founder operations." |
| **What we do** | 3 cards: Distribution · Brand building · Market entry. Each links deeper. |
| **Our brands** | 2 brand cards with real product photography. |
| **The founders** | Three portraits, three cities, one line each. Links to /founders. |
| **From the route** | Latest 3 insights + YouTube (EN) / Bilibili (中文). |
| **CTA** | "Tell us about your business" → /partner |

## `/what-we-do`

Three pillars, each with a plain description, who it's for, and how it works in practice.

1. **Distribution** — we put Chinese products into shops in three countries
2. **Brand building** — we build and own brands under TGO
3. **Market entry** — certification, pricing, channel strategy, warranty

Include an honest section on **how a partnership actually starts** — a 4-step sequence (conversation → sample → trial shipment → territory agreement). Manufacturers care about process; almost nobody publishes it.

Anonymized client proof lives here: *"⟨A Shenzhen lithium-battery manufacturer with 400 staff, exporting to 14 countries, needed a route into Pakistan⟩."* Specific, not identifying.

## `/brands`

House-of-brands view. This page is what makes the holding structure legible.

| Brand | Category | Markets | Status |
|---|---|---|---|
| ⟨KIRO⟩ | Mobile & household accessories | PK · IN · PH | In development |
| ⟨VOLTARA⟩ | Solar & energy storage | PK · IN · PH | Certification in progress |

Each brand gets a detail page: positioning, product range, target channel, market availability.

## `/founders`

The strongest page on the site. Structure it as a narrative, not a team grid.

**Act 1 — We met in China.** Guangzhou, ⟨2006⟩ onward. Two brothers and a friend.
**Act 2 — We went our separate ways.** Umair to Pakistan. Umer to Manila, ⟨10+ years⟩. Aryan to India, ⟨Oppo, Bihar⟩.
**Act 3 — We came back.** 2026, with three markets between us.

Then three founder profiles, equal weight:

- **Umair ⟨Surname⟩** — ⟨Group / Pakistan⟩ — brand building, electronics, solar, lithium
- **Umer Ahmad Shad** — ⟨Philippines⟩ — ⟨10+ years in Manila⟩, distribution, travel agency
- **Aryan Roshan** — ⟨India⟩ — ⟨ex-Oppo Bihar⟩, founder of ⟨tech company⟩

> **Note:** give Umer full equal weight in layout and word count. Umair fronts the YouTube channel; the site should not read as one founder with two assistants — that reads badly in both Pakistani and Chinese business contexts.

## `/markets`

One section per country. Each carries: market size, retail structure, what's hard about it, and what you have there. This is your entity-SEO engine and your most linkable content.

## `/insights`

Weekly, tied to the YouTube channel. Categories: Market notes · Manufacturing · Building TGO. Every post bilingual or clearly marked EN-only.

## `/partner` — the conversion page

Progressive survey, one question per screen, no wall of fields.

**Survey schema for your backend:**

```
lead {
  id
  created_at
  locale                 en | zh
  party_type             manufacturer | brand_owner | distributor | investor | other
  company_name
  company_country
  category               accessories | solar_energy | appliances | audio | other
  monthly_volume_band    <1k | 1k-10k | 10k-50k | 50k+ | n/a
  target_markets[]       PK | IN | PH | other
  need                   distribution | brand_building | sourcing | market_entry
  timeline               now | 3_months | 6_months | exploring
  contact_name
  contact_email
  contact_phone
  preferred_channel      wechat | whatsapp | email
  wechat_id / whatsapp
  message
  source                 utm / referrer / youtube
  score                  computed
  assigned_to            umair | umer | aryan
}
```

**Auto-routing:** target market PK → Umair · IN → Aryan · PH → Umer · manufacturer in China → Umair.
**Scoring:** volume band + timeline + party type. Surface hot leads first in your dashboard.

## `/contact`

Region-aware. China → WeChat QR first. Pakistan/India → WhatsApp first. Elsewhere → email first. All three always visible.

---

# PART 4 — Design system

Hand these tokens directly to your dev as CSS custom properties.

### Colour

| Token | Hex | Use |
|---|---|---|
| `--paper` | `#F7F6F3` | Primary background |
| `--ink` | `#12151A` | Dark cinematic sections, primary text |
| `--seal` | `#A83A2B` | Accent — the cinnabar of a Chinese company chop |
| `--jade` | `#2F5D50` | Secondary accent, market sections |
| `--sand` | `#E6E0D4` | Section fills, dividers |
| `--grey` | `#6B6862` | Secondary text |

The accent is deliberate: 朱砂 cinnabar is the colour of a company seal — an authentication mark in Chinese business culture. For a company whose product is trust, the palette should say that before the copy does. It also reads as warm rather than corporate to the Western audience.

### Type

| Role | Latin | 中文 |
|---|---|---|
| Display | **Fraunces** (variable, optical size + soft axes) | **Noto Serif SC** |
| Body | **Geist Sans** | **Noto Sans SC** |
| Data / labels | **Geist Mono** | Geist Mono + Noto Sans SC |

All self-hosted, WOFF2, CJK subsetted to used characters. Fluid scale via `clamp()`.

**CJK overrides:** minimum 17px body, line-height 1.8, letter-spacing 0, heavier weight for headings (Chinese at light weights disappears).

### Signature element — The Route

A single hairline rule with four station markers: **Guangzhou** (origin) → **Karachi · Mumbai · Manila**. It draws once on page load, then reappears throughout the site as the section divider, with the active station marked. It's the nav progress indicator on long pages.

This is the one place to spend boldness. Everything else stays quiet. The route is true — it's literally the business — so it encodes information rather than decorating.

### Motion

One orchestrated page-load sequence (the route drawing). Scroll reveals at 200ms, subtle. View Transitions between pages. Nothing else. `prefers-reduced-motion` fully respected.

---

# PART 5 — SEO & technical

**Technical:** SSG/SSR, Core Web Vitals green (LCP <2.0s, INP <200ms, CLS <0.1), XML sitemap with `hreflang` for en/zh, canonical tags, per-page OG images, `robots.txt`, `llms.txt`.

**Structured data:** `Organization` (with HK address, founders, sameAs), `Person` × 3, `Article`, `FAQPage`, `BreadcrumbList`.

**Entity strategy:** nobody searches "TGO Brands" yet. Your traffic comes from long-tail intent — "Chinese electronics distributor Pakistan", "solar brand distribution India", "export to Philippines from Guangzhou". The `/markets` pages target these. Each founder gets an indexable profile so Google links the people to the company as entities.

**Chinese SEO is a separate discipline.** Baidu ignores most of what Google rewards. If the 中文 side matters commercially, you need Baidu Webmaster Tools submission, simplified characters throughout, and realistically a WeChat Official Account — for Chinese B2B, WeChat matters more than the website.

**Don't bother with:** keyword stuffing, bought backlinks, weekly AI-written filler. One real post a month using your actual operating knowledge beats twenty generic ones.

---

# PART 6 — Four-week roadmap

### Week 0 — before design starts
- [ ] File **BIS registration** for the solar line (India is the long pole — this clock runs independently)
- [ ] File **TGO** trademark in Hong Kong; `TGO优选` as a compound mark in China
- [ ] Collect real numbers, venture list, founder bios
- [ ] Audit existing photo/video — tag what's usable

### Week 1 — content & design
- Finalise copy deck EN, translate to 中文 (human translation, not machine)
- Claude Design: homepage + one interior page, both languages
- Design tokens locked
- Photography selected and edited

### Week 2 — build
- Dev builds page templates from Claude Design output
- CMS schema with locale fields
- Self-hosted fonts, CJK subsetting
- Survey UI + backend schema

### Week 3 — content load & integration
- All pages populated both languages
- Survey → backend → dashboard wired, routing and scoring live
- Structured data, sitemap, llms.txt
- WeChat QR, WhatsApp links, email routing

### Week 4 — test & launch
- Test load times from Karachi, Mumbai, Manila, Guangzhou (real devices, not just Lighthouse)
- Verify no blocked resources on the 中文 side
- WCAG 2.2 AA pass, keyboard nav, reduced motion
- Baidu + Google Search Console submission
- Launch, then first YouTube episode within 7 days

**Deliberately deferred to v1.1:** the AI intake agent. Launch the survey as a form first, watch what people actually write in the free-text field for a month, then build the agent against real inputs instead of guesses.

---

# PART 7 — Prompt for Claude Design

Copy everything below into Claude Design.

---

**Build the website for TGO Brands — a Hong Kong holding company that brings Chinese consumer-electronics brands into Pakistan, India and the Philippines.**

**The company.** Three founders — two brothers and a lifelong friend — met in Guangzhou around 2006, spent 15 years apart building businesses in three different countries, and returned to China in 2026 to combine what they learned. Umair covers Pakistan, Umer covers the Philippines from Manila, Aryan covers India. TGO owns and builds brands under its umbrella, in the model of BBK Electronics: an invisible parent, visible brands. TGO means "The Good One". Chinese name: TGO优选.

**Two audiences, equal weight.** (1) Chinese manufacturers and brand owners looking for export markets and partners they can trust. (2) An English-speaking online audience arriving from a founder-led YouTube channel, deciding whether these people are serious operators.

**Tone.** Warm and human, relationship-first. Not aggressive operator-speak, not corporate boilerplate. These are people who trade on relationships — the writing should sound like someone who has actually sat in a factory canteen in Dongguan and a phone shop in Karachi. Plain verbs, specific detail, no superlatives.

**Pages.** Home · What We Do · Brands · Founders · Markets · Insights · Partner With Us. Plus Contact and legal. Full bilingual EN / 中文 — design both, don't design English and hope Chinese fits.

**Visual direction — light base with dark cinematic blocks.** Predominantly light, structured, clearly organised for the business content: what we do, brands, markets, contact. Full-bleed dark sections for the founder story, portraits, and video. Not a dark site. The reason is partly technical — Chinese characters are stroke-dense and go muddy in light-on-dark at body sizes, and half the audience reads Chinese.

**Palette:**
- `--paper #F7F6F3` background
- `--ink #12151A` dark sections and text
- `--seal #A83A2B` accent — the cinnabar red of a Chinese company chop
- `--jade #2F5D50` secondary accent
- `--sand #E6E0D4` fills and dividers
- `--grey #6B6862` secondary text

**Type:** Fraunces (variable) for display, Geist Sans for body, Geist Mono for data and labels. Noto Serif SC and Noto Sans SC for Chinese. All self-hosted. Chinese body text at minimum 17px with 1.8 line-height and heavier heading weights than the Latin equivalent.

**Signature element — The Route.** A hairline rule with four station markers: Guangzhou as origin, branching to Karachi, Mumbai and Manila. It draws once on page load as the hero, then recurs as the structural divider between sections throughout the site, with the current station marked. This is the one bold move — everything around it stays quiet and disciplined. It's not decoration: the route is literally the business.

**Hero.** Headline: "We take Chinese brands to the world." Sub: "Starting where we live — Pakistan, India, the Philippines. Three founders, three markets, one route from Guangzhou." The route drawing is the hero image — no stock photography, no gradient, no big number.

**Proof.** No published financials. Credibility comes from the story, named own-brands, real factory and retail photography, and founder profiles. Four figures maximum anywhere on the homepage, each with a footnote on scope. Anonymised client references must be specific about scale without naming anyone.

**Primary CTA:** "Tell us about your business" — a progressive survey, one question per screen, that captures business type, category, volume band, target markets, timeline and contact details. Not a contact form with twelve fields.

**Contact is region-aware:** WeChat QR for China, WhatsApp for Pakistan and India, email everywhere. All three visible, ordered by visitor region.

**Technical constraints — these are hard requirements:**
- Self-host all fonts. Google Fonts is blocked in mainland China.
- No YouTube embeds on the 中文 pages. Use Bilibili or self-hosted video there.
- Server-render all content. It must be readable without JavaScript.
- Fluid type and spacing with `clamp()`, container queries rather than device breakpoints.
- View Transitions API for page transitions.
- WCAG 2.2 AA: visible keyboard focus, `prefers-reduced-motion` respected, 4.5:1 contrast minimum.
- Design tokens as CSS custom properties — this gets handed to a full-stack developer.

**Avoid entirely:** scroll-jacking, WebGL or particle backgrounds, cursor followers, loading animations, parallax, glassmorphism, gradient mesh backgrounds, letter-by-letter text animation, horizontal scroll sections. Every one of these will date the site within three years.

**Motion budget:** one orchestrated page-load sequence (the route drawing), subtle scroll reveals, view transitions between pages. Nothing else.

Use placeholder content where I haven't given you specifics, and mark it clearly so I can find and replace it.

---
