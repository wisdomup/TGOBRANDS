# TGO Brands — website

The production build of the **TGO Brands v3 Glass** design, tightened into the base for v4.
Static, pre-rendered, bilingual (`/` English, `/zh/` 中文). No framework and no dependencies:
Python 3 standard library to build, plain HTML/CSS/JS out.

```bash
python3 build.py                                   # writes ./dist (20 pages + sitemap, robots, llms.txt)
python3 -m http.server 8000 --directory dist       # preview at http://localhost:8000
```

Deploy `dist/` to any static host (Vercel, Netlify, Cloudflare Pages, S3). Clean URLs are
folders with an `index.html`, so no rewrites are needed.

## Layout

| Path | What it is |
| --- | --- |
| `content/en.json`, `content/zh.json` | All copy, one file per locale, identical shape. Edit copy here. |
| `templates.py` | Page templates (one function per page) and the shared head/nav/footer. |
| `build.py` | Renders every page for both locales, versions the CSS/JS, writes sitemap (with hreflang pairs), `robots.txt`, `llms.txt`. |
| `static/site.css` | The one stylesheet: tokens at the top, then base, components, pages, the 中文 layer, responsive, motion. |
| `static/site.js` | Progressive enhancement only — every page is complete without it. |
| `static/photo.jpg`, `static/hero.mp4` | Placeholder photography and the hero loop. |

Adding a brand: add an item (with a `slug`) to `brands.items` in both content files and rebuild —
the table, the cards and the `/brands/<slug>/` pages all follow.

## Behaviour

- **Nav** merges with the page at the top and becomes a frosted capsule once scrolled; over the
  dark hero it switches to smoked glass with white links. On phones the links live in a
  `popover` drawer, which works without JavaScript.
- **Survey** (`/partner/`) is one form. With JavaScript it runs one question per screen, scores the
  lead and routes it (PK → Umair, IN → Aryan, PH → Umer, otherwise Umair). To send leads to a backend,
  set `data-endpoint` on the form in `templates.py`; `site.js` POSTs the lead as JSON (field names
  follow the spec's lead schema). Without JavaScript every question is listed in order.
- **How we work** opens as a dialog; its links fall back to `/what-we-do/#start`.
- **Reveal, marquees, hero video** respect `prefers-reduced-motion`; the video also skips Save-Data.
- **Fonts** are system fonts only (SF / PingFang / YaHei) — nothing loads from Google Fonts, so the
  中文 site is not blocked in the mainland.

## Still to supply

Rendered as non-clickable placeholders until filled in:

- WeChat QR and the public WhatsApp number — `contact.channels.*.href` in the content files
- Channel link (YouTube for EN, Bilibili for 中文 — never YouTube on `/zh/`) — `insights.videoHref`
- Privacy and Terms pages (footer)
- Real photography and founder portraits (every image is currently `photo.jpg`)
- Placeholder copy marked in the spec (figures, dates, names)

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
