"""Page templates for the TGO Brands site.

Every function takes the locale's content dict (`c`, from content/<lang>.json)
and returns an HTML string. Markup is server-rendered in full: the JavaScript in
static/site.js only enhances it (nav state, reveal, the survey stepper, the
how-we-work dialog), so every page reads correctly with scripting off.
"""
import json
import re
from html import escape

SITE = 'https://tgobrands.com'

# page key -> path under the locale root
PATHS = {
    'home': '',
    'what': 'what-we-do/',
    'brands': 'brands/',
    'founders': 'founders/',
    'markets': 'markets/',
    'insights': 'insights/',
    'partner': 'partner/',
    'contact': 'contact/',
    'services': 'services/',
    'launch': 'launch/',
    'expeditions': 'expeditions/',
    'travel': 'travel/',
    'estimator': 'tools/entry-estimator/',
    'portal': 'portal/',
    'privacy': 'privacy/',
    'terms': 'terms/',
    'sitemap': 'sitemap/',
    'packages': 'travel/packages/',
    'visas': 'travel/visas/',
    'booking': 'travel/booking/',
}
# detail pages: key -> path pattern under the locale root
DETAIL = {
    'brand': 'brands/{}/',
    'service': 'services/{}/',
    'audience': 'for/{}/',
    'playbook': 'markets/{}/',
    'trip': 'expeditions/{}/',
    'guide': 'travel/{}/',
}
NAV = ['services', 'markets', 'travel', 'brands', 'founders', 'insights']

PHOTO = '/assets/photo.jpg'
WHATSAPP = {'Umer': '639772547666', 'Umair': '8615623305030', 'Aryan': '917645912074', 'Shamas': '971542971969'}

WA_ICON = ('<svg class="wa" viewBox="0 0 24 24" aria-hidden="true"><path d="M12.04 2C6.58 2 2.13 6.45 2.13 11.91c0 1.75.46 3.45 1.32 4.95L2 22l5.25-1.38a9.9 9.9 0 0 0 4.79 1.22h.01c5.46 0 9.91-4.45 9.91-9.91 0-2.65-1.03-5.14-2.9-7.01A9.82 9.82 0 0 0 12.04 2m0 1.67a8.2 8.2 0 0 1 5.83 2.42 8.18 8.18 0 0 1 2.41 5.82c0 4.55-3.7 8.24-8.25 8.24a8.24 8.24 0 0 1-4.2-1.15l-.3-.18-3.12.82.83-3.04-.2-.31a8.22 8.22 0 0 1-1.26-4.4c0-4.55 3.7-8.22 8.26-8.22m-4.53 4.7c-.15 0-.4.06-.61.3-.21.24-.8.78-.8 1.9 0 1.12.82 2.2.93 2.35.12.15 1.6 2.5 3.9 3.44 1.9.78 2.3.63 2.71.6.42-.04 1.34-.55 1.53-1.08.19-.53.19-.98.13-1.08-.05-.1-.2-.16-.42-.27-.22-.11-1.34-.66-1.55-.74-.21-.08-.36-.11-.51.12-.15.22-.58.73-.71.88-.13.15-.26.16-.48.05-.22-.11-.94-.35-1.79-1.11-.66-.59-1.11-1.32-1.24-1.54-.13-.22-.01-.34.1-.45.1-.1.22-.26.33-.39.11-.13.15-.22.22-.37.07-.15.04-.28-.02-.39-.06-.11-.51-1.25-.71-1.71-.18-.44-.37-.38-.51-.39-.13-.01-.28-.01-.43-.01Z"/></svg>')


def e(s):
    return escape(str(s), quote=True)


def root(lang):
    return '/zh/' if lang == 'zh' else '/'


def href(lang, page, slug=None):
    path = DETAIL[page].format(slug) if page in DETAIL else PATHS[page]
    return root(lang) + path


def list_path(cat_slug='', page_no=1):
    """Insights listing: /insights/, /insights/page/2/, /insights/category/<cat>/page/2/."""
    path = 'insights/' + (f'category/{cat_slug}/' if cat_slug else '')
    return path + (f'page/{page_no}/' if page_no > 1 else '')


def href_list(lang, cat_slug='', page_no=1):
    return root(lang) + list_path(cat_slug, page_no)


def href_post(lang, slug):
    return root(lang) + f'insights/{slug}/'


def post_cat(c, post):
    """Index of a post's category in the insights category list (0 is All)."""
    cats = c['insights']['cats']
    return cats.index(post['c']) if post['c'] in cats else 0


def pager(aria, prev=None, nxt=None, prev_label='', next_label=''):
    """Previous / next cards at the foot of a page. prev and nxt are (url, title)."""
    if not prev and not nxt:
        return ''

    def cell(item, label, rel):
        if not item:
            return ''
        url, title = item
        return (f'<a class="pager__link pager__link--{rel}" href="{url}" rel="{rel}">'
                f'<span class="pager__dir">{label}</span><span class="pager__title">{e(title)}</span></a>')
    return f'''
  <nav class="wrap pager" aria-label="{e(aria)}">
    {cell(prev, "← " + e(prev_label), "prev")}
    {cell(nxt, e(next_label) + " →", "next")}
  </nav>'''


# the order a first-time visitor walks the site; ends on the conversion page
SEQUENCE = ['home', 'what', 'services', 'launch', 'markets', 'travel', 'expeditions', 'brands', 'founders', 'insights', 'partner']


def site_pager(c, lang, page):
    i = SEQUENCE.index(page)
    title = lambda k: c['ui']['home'] if k == 'home' else c['nav'][k]
    prev = (href(lang, SEQUENCE[i - 1]), title(SEQUENCE[i - 1])) if i > 0 else None
    nxt = (href(lang, SEQUENCE[i + 1]), title(SEQUENCE[i + 1])) if i + 1 < len(SEQUENCE) else None
    return pager(c['ui']['continue'], prev, nxt, c['ui']['prev'], c['ui']['next'])


def initials(name):
    """Two letters for a plate: first and last word ("Lightspeed International" → LI), or the
    capitals of a single word ("SeeTrack" → ST)."""
    words = name.split()
    if len(words) > 1:
        return (words[0][0] + words[-1][0]).upper()
    caps = [ch for ch in name if ch.isupper()]
    return ''.join(caps[:2]) if len(caps) > 1 else name[:2].upper()


def plate(mark, ratio=''):
    """Where a real photograph will go: a typographic plate with initials, until the founders'
    own photos arrive. No stock photography anywhere on the site."""
    r = f' photo--{ratio}' if ratio else ''
    return f'<figure class="photo plate{r}" aria-hidden="true"><span class="plate__mark">{e(mark)}</span></figure>'


def portrait(c, name, ratio='3x4', alt=''):
    """A founder's photograph when one exists (keyed by first name in
    content/shared/portraits.json), else the placeholder plate. `focus` is the
    object-position that keeps the face in frame when a card crops the 3:4
    original to a square or a wide strip on phones."""
    p = c['portraits'].get(name.split()[0])
    if not p:
        return plate(name[0], ratio)  # a founder's first initial until the portrait arrives
    return (f'<figure class="photo photo--{ratio} photo--portrait">'
            f'<img src="{p["src"]}" srcset="{p["small"]} 400w, {p["src"]} {p["w"]}w" '
            f'sizes="(max-width: 680px) 50vw, 340px" width="{p["w"]}" height="{p["h"]}" '
            f'alt="{e(alt)}" style="object-position:{p["focus"]}" loading="lazy" decoding="async"></figure>')


def face(c, name):
    """The round host avatar, or nothing while there is no photograph."""
    p = c['portraits'].get(name.split()[0])
    return f'<img class="host__face" src="{p["face"]}" width="64" height="64" alt="" loading="lazy" decoding="async">' if p else ''


def target(c, lang, ref):
    """(url, name) for a cross-link given as {"service": slug}, {"brand": slug} or {"page": key}."""
    if 'service' in ref:
        x = service_by_slug(c, ref['service'])
        return href(lang, 'service', x['slug']), x['name']
    if 'brand' in ref:
        b = next(b for b in c['brands']['items'] if b['slug'] == ref['brand'])
        return href(lang, 'brand', b['slug']), b['name']
    key = ref['page']
    pages = {'packages': 'packagesPage', 'visas': 'visasPage', 'booking': 'bookingPage'}
    name = c['travel'][pages[key]]['name'] if key in pages else c['nav'][key]
    return href(lang, key), name


def eyebrow(text, cls=''):
    return f'<p class="eyebrow{" " + cls if cls else ""}">{e(text)}</p>'


def action(label, url, cls='btn btn--link'):
    """A link when its destination is known; until then a placeholder anchor
    (no href, so it is neither focusable nor a dead click)."""
    if url:
        ext = ' target="_blank" rel="noopener"' if url.startswith('http') else ''
        return f'<a class="{cls}" href="{e(url)}"{ext}>{e(label)}</a>'
    return f'<a class="{cls} is-pending" title="Link to come">{e(label)}</a>'


def bcard(c, lang, b):
    return f'''
        <a class="bcard" href="{href(lang, 'brand', b['slug'])}">
          {plate(initials(b['name']), '4x3')}
          <div class="bcard__body">
            {eyebrow(b["cat"])}
            <h3>{e(b["name"])}</h3>
            <p class="bcard__pos">{e(b["pos"])}</p>
            {eyebrow(b["mk"] + " · " + b["st"], "bcard__meta")}
            <span class="bcard__link">{e(c["brands"]["detailKicker"])} →</span>
          </div>
        </a>'''


# ── chrome ────────────────────────────────────────────────────────────────

# the Obsidian face, in both themes. Loaded by script, print-media first, so it
# never blocks the first paint; skipped on 中文 pages because Google Fonts is
# blocked in mainland China (those pages use the CJK system faces).
FONT_CSS = 'https://fonts.googleapis.com/css2?family=Work+Sans:wght@300..900&display=swap'

# line icons for the theme switches: 1.5px stroke on a 16px grid
SUN = ('<svg class="{}" viewBox="0 0 16 16" aria-hidden="true"><circle cx="8" cy="8" r="3"/>'
       '<path d="M8 1.5v1.6M8 12.9v1.6M1.5 8h1.6M12.9 8h1.6M3.4 3.4l1.1 1.1M11.5 11.5l1.1 1.1M3.4 12.6l1.1-1.1M11.5 4.5l1.1-1.1"/></svg>')
MOON = '<svg class="{}" viewBox="0 0 16 16" aria-hidden="true"><path d="M13.6 10.2A5.8 5.8 0 0 1 5.8 2.4a5.8 5.8 0 1 0 7.8 7.8z"/></svg>'


def nav(c, lang, page, alt_href):
    home = page == 'home'
    cur = {'brand': 'brands', 'post': 'insights', 'service': 'services', 'playbook': 'markets',
           'trip': 'travel', 'expeditions': 'travel', 'guide': 'travel', 'what': 'services',
           'packages': 'travel', 'visas': 'travel', 'booking': 'travel'}.get(page, page)
    current = ' aria-current="page"'
    links = ''.join(
        f'<a href="{href(lang, k)}"{current if cur == k else ""}>{e(c["nav"][k])}</a>'
        for k in NAV)
    cta = f'{e(c["ui"]["talk"])}<span class="nav__arrow" aria-hidden="true">→</span>'
    other = 'en' if lang == 'zh' else 'zh-CN'
    hero = 1 if home and c['home'].get('photo') else 0
    return f'''<header class="nav" data-scrolled="0" data-hero="{hero}" data-dark="{hero}">
  <a class="nav__logo" href="{href(lang, 'home')}" aria-label="TGO Brands">TGO<span class="nav__word">Brands</span></a>
  <nav class="nav__links" id="site-menu" popover aria-label="{e(c["ui"]["menu"])}">
    {links}
    <a class="btn nav__cta nav__cta--drawer" href="{href(lang, 'partner')}">{cta}</a>
  </nav>
  <a class="nav__lang" href="{alt_href}" hreflang="{other}" lang="{other}" aria-label="{e(c["ui"]["langSwitchLabel"])}">{e(c["ui"]["langSwitch"])}</a>
  <button class="nav__theme" type="button" role="switch" aria-checked="false" aria-label="{e(c["ui"]["themeDark"])}" title="{e(c["ui"]["themeDark"])}" data-theme-toggle>{MOON.format('nav__moon')}{SUN.format('nav__sun')}</button>
  <a class="btn nav__cta" href="{href(lang, 'partner')}">{cta}</a>
  <button class="nav__burger" type="button" popovertarget="site-menu" aria-label="{e(c["ui"]["menu"])}"><span></span><span></span><span></span></button>
</header>'''


def site_groups(c, lang, full=False):
    """The site, grouped as it is built: (title, section link or None, parts, wide), where parts is
    [(subheading or None, [(href, label)])]. The footer shows each section's pages; the site-map
    page (full=True) adds the home page, full trip names and every article."""
    n, cols, t, s, m = c['nav'], c['footer']['cols'], c['travel'], c['insights'], c['sitemap']
    services = [(href(lang, 'service', x['slug']), x['name']) for x in c['services']['items']]
    travel = ([(href(lang, k), t[p]['name']) for k, p in (('packages', 'packagesPage'), ('visas', 'visasPage'), ('booking', 'bookingPage'))]
              + [(href(lang, 'guide', g['slug']), g['name']) for g in t['guides']])
    trips = [(href(lang, 'trip', x['slug']), x['title'] if full else x['short']) for x in c['expeditions']['editions']]
    markets = ([(href(lang, 'playbook', b['slug']), c['markets']['items'][b['market']]['c']) for b in c['playbooks']['items']]
               + [(href(lang, 'estimator'), n['estimator'])])
    who = ([(href(lang, 'audience', a['slug']), a['name']) for a in c['audiences']['items']]
           + [(href(lang, 'launch'), n['launch']), (href(lang, 'portal'), n['portal'])])
    brands = [(href(lang, 'brand', b['slug']), b['name']) for b in c['brands']['items']]
    topics = [(href_list(lang, slug), name) for name, slug in zip(s['cats'][1:], s['catSlugs'][1:])]
    insights = ([(m['topics'], topics), (m['articles'], [(href_post(lang, p['slug']), p['t']) for p in s['posts']])]
                if full else [(None, topics)])
    company = (([(href(lang, 'home'), m['home'])] if full else [])
               + [(href(lang, k), n[k]) for k in ('what', 'founders', 'contact', 'partner')]
               + [(href(lang, 'privacy'), c['privacy']['name']), (href(lang, 'terms'), c['terms']['name'])]
               + ([] if full else [(href(lang, 'sitemap'), m['name'])]))
    return [
        (cols['services'], href(lang, 'services'), [(None, services)], True),
        (cols['travel'], href(lang, 'travel'), [(None, travel)], False),
        (n['expeditions'], href(lang, 'expeditions'), [(None, trips)], False),
        (cols['markets'], href(lang, 'markets'), [(None, markets)], False),
        (cols['who'], None, [(None, who)], False),
        (cols['brands'], href(lang, 'brands'), [(None, brands)], False),
        (n['insights'], href(lang, 'insights'), insights, False),
        (cols['company'], None, [(None, company)], False),
    ]


def footer(c, lang):
    """The footer is a compact site map: every section and its pages, in small type. The
    full list, with every article, is the site-map page it links to."""
    f = c['footer']
    cols = f['cols']

    def col(title, head, parts, wide):
        h = f'<a class="footer__h" href="{head}">{e(title)}</a>' if head else f'<p class="footer__h">{e(title)}</p>'
        links = ''.join(f'<a href="{u}">{e(label)}</a>' for _, items in parts for u, label in items)
        cls = 'footer__col footer__col--wide' if wide else 'footer__col'
        return f'\n      <nav class="{cls}" aria-label="{e(title)}">{h}<div class="footer__list">{links}</div></nav>'

    sitemap = ''.join(col(*g) for g in site_groups(c, lang))
    return f'''<footer class="footer">
  <div class="footer__top">
    <div class="footer__brand">
      <a class="footer__logo" href="{href(lang, 'home')}">TGO<span>Brands</span></a>
      <p>{e(f["about"])}</p>
    </div>
    <div class="footer__map" role="group" aria-label="{e(cols["sitemap"])}">{sitemap}
    </div>
  </div>
  <div class="footer__in">
    <p>{e(f["tag"])}</p>
    <p>{e(f["note"])}</p>
    <button class="theme-switch" type="button" role="switch" aria-checked="false" data-theme-toggle>
      <span class="theme-switch__label">{e(c["ui"]["themeDark"])}</span>
      <span class="theme-switch__track" aria-hidden="true">
        {SUN.format('theme-switch__sun')}
        {MOON.format('theme-switch__moon')}
        <span class="theme-switch__thumb"></span>
      </span>
    </button>
  </div>
</footer>'''


def stations(c, leads=True):
    items = ''
    for name, lead in zip(c['route']['stations'], c['route']['leads']):
        sub = f'<p class="eyebrow route__lead">{e(lead)}</p>' if leads else ''
        items += f'<li><span class="route__dot"></span><p class="route__name">{e(name)}</p>{sub}</li>'
    return f'<ol class="route__stations">{items}</ol>'


# ── home ──────────────────────────────────────────────────────────────────

# the signature line: anchors of a smooth curve, start and end included (viewBox 1200 × 120)
ROUTE_POINTS = ((8, 92), (260, 52), (500, 82), (740, 38), (980, 70), (1192, 28))
ROUTE_PATH = 'M8 92 C120 92 170 50 260 52 S420 90 500 82 S650 28 740 38 S900 86 980 70 S1120 24 1192 28'


def route_line(c):
    """Guangzhou in 2006, through the places the founders have built in, to the world. The line
    draws itself once as the page opens and stays still for readers who prefer reduced motion.
    The dots are HTML, so they stay round while the line stretches to the width of the page."""
    h = c['home']
    last = len(ROUTE_POINTS) - 1
    dots = ''.join(
        f'<span class="route-line__dot{" route-line__dot--end" if i in (0, last) else ""}" '
        f'style="--x:{x / 12:.2f}%;--y:{y / 1.2:.2f}%;--i:{i}"></span>'
        for i, (x, y) in enumerate(ROUTE_POINTS))
    return f'''<div class="route-line" aria-hidden="true">
        <svg viewBox="0 0 1200 120" preserveAspectRatio="none" focusable="false"><path d="{ROUTE_PATH}" pathLength="1" vector-effect="non-scaling-stroke"/></svg>{dots}
      </div>
      <p class="route-line__ends"><span>{e(h["routeFrom"])}</span><span>{e(h["routeTo"])}</span></p>'''


def first_sentence(text):
    for stop in ('。', '. '):
        if stop in text:
            return text.split(stop, 1)[0] + stop.strip()
    return text


def page_home(c, lang):
    """Five sections, in the founders' voice: who we are for, what you can come to us for, how we
    look after you, who we are, and how to start. Everything else lives on its own page."""
    h = c['home']
    first = lambda p: p['name'].split()[0]

    needs = ''
    for n, x in enumerate(h['needs']):
        link = x['link']
        url = href(lang, 'services') + '#' + link['group'] if 'group' in link else href(lang, link['page'])
        needs += f'''
      <li><a class="need" href="{url}">
        <span class="need__n">{n + 1:02d}</span>
        <span class="need__body"><span class="need__t">{e(x["t"])}</span><span class="need__d">{e(x["d"])}</span></span>
        <span class="need__go" aria-hidden="true">→</span>
      </a></li>'''
    who = ' <span aria-hidden="true">·</span> '.join(
        f'<a href="{href(lang, "audience", a["slug"])}">{e(a["name"])}</a>' for a in c['audiences']['items'])

    care = ''.join(f'''
      <li class="care__item"><p class="care__n">{n + 1:02d}</p><h3>{e(x["t"])}</h3><p>{e(x["d"])}</p></li>'''
                   for n, x in enumerate(h['care']))

    people = c['founders']['people']
    founders = ''.join(f'''
      <article class="founder">
        {portrait(c, p['name'], '4x5', alt=p['name'])}
        <h3>{e(p["name"])}</h3>
        {eyebrow(p["city"])}
        <p>{e(h["lines"][first(p)])}</p>
      </article>''' for p in people)
    figures = ''.join(f'<div><dt>{e(f["n"])}</dt><dd>{e(f["l"])}</dd></div>' for f in h['proof'])

    brands = ''.join(f'''
      <li><a class="brandrow" href="{href(lang, 'brand', b['slug'])}">
        <span class="brandrow__name">{e(b["name"])}</span>
        <span class="brandrow__cat">{e(b["cat"])}</span>
        <span class="brandrow__pos">{e(first_sentence(b["pos"]))}</span>
        <span class="brandrow__go" aria-hidden="true">→</span>
      </a></li>''' for b in c['brands']['items'])

    # client stories appear here once the founders have written them up
    stories = ''
    if h.get('stories'):
        cards = ''.join(f'''
        <article class="panel story">{eyebrow(x["who"])}<h3>{e(x["t"])}</h3><p>{e(x["d"])}</p></article>''' for x in h['stories'])
        stories = f'''
  <section class="wrap sec">
    <header class="shead shead--left"><h2 class="sech">{e(h["storiesTitle"])}</h2></header>
    <div class="grid grid--3">{cards}
    </div>
  </section>'''

    chips = ''.join(
        f'<a class="chip chip--wa" href="https://wa.me/{WHATSAPP[first(p)]}" target="_blank" rel="noopener">'
        f'{WA_ICON}{e(h["wa"].format(name=first(p)))}</a>' for p in people)
    photo = (f'\n      <figure class="lobby__photo"><img src="{e(h["photo"])}" alt="" fetchpriority="high"></figure>'
             if h.get('photo') else '')

    return f'''<main id="main" class="page page--home">
  <section class="lobby">
    <div class="wrap lobby__in">
      <p class="lobby__kicker">{e(h["kicker"])}</p>
      <h1 class="lobby__title disp">{e(h["h1"])}</h1>
      <p class="lobby__sub">{e(h["sub"])}</p>
      <div class="lobby__acts">
        <a class="btn btn--primary btn--lg" href="{href(lang, 'partner')}">{e(h["cta"])}</a>
        <a class="btn btn--outline btn--lg" href="{href(lang, 'founders')}">{e(h["cta2"])}</a>
      </div>
      {route_line(c)}{photo}
    </div>
  </section>

  <section class="wrap sec home-needs">
    <header class="shead shead--left"><h2 class="sech">{e(h["needsTitle"])}</h2></header>
    <ol class="needs">{needs}
    </ol>
    <p class="needs__who"><span class="needs__label">{e(h["whoLabel"])}</span> {who}</p>
  </section>

  <section class="band">
    <div class="wrap sec">
      <header class="shead shead--left"><h2 class="sech">{e(h["careTitle"])}</h2></header>
      <ol class="care">{care}
      </ol>
    </div>
  </section>

  <section class="wrap sec home-founders">
    <header class="shead shead--left"><h2 class="sech">{e(h["foundersTitle"])}</h2><p class="lead">{e(h["foundersSub"])}</p></header>
    <div class="founders">{founders}
    </div>
    <dl class="figures">{figures}</dl>
    <p class="note figures__note">{e(h["proofNote"])}</p>
    <p class="home-founders__more"><a class="btn btn--link" href="{href(lang, 'founders')}">{e(h["storyLink"])} →</a></p>
  </section>

  <section class="band">
    <div class="wrap sec">
      <header class="shead shead--left"><h2 class="sech">{e(h["brandsTitle"])}</h2><p class="lead">{e(h["brandsNote"])}</p></header>
      <ul class="brandrows">{brands}
      </ul>
    </div>
  </section>{stories}

  <section class="wrap sec home-close">
    <header class="shead shead--left"><h2 class="sech">{e(h["closeTitle"])}</h2><p class="lead">{e(h["closeNote"])}</p></header>
    <div class="home-close__acts">
      <a class="btn btn--primary btn--lg" href="{href(lang, 'partner')}">{e(h["closeCta"])}</a>
      <div class="home-close__chips">{chips}</div>
    </div>
  </section>
  {site_pager(c, lang, 'home')}
</main>'''


# ── interior pages ────────────────────────────────────────────────────────

def phead(kicker, title, sub, mw='56ch', extra=''):
    return f'''<section class="wrap phead">
    {eyebrow(kicker)}
    <h1 class="disp">{e(title)}</h1>
    <p class="lead" style="--mw:{mw}">{e(sub)}</p>{extra}
  </section>'''


def poster(c, lang):
    h = c['home']
    return f'''<section class="poster">
    <div class="wrap sec">
      <h2 class="title disp">{e(h["closeA"])}</h2>
      <a class="btn btn--light" href="{href(lang, 'partner')}">{e(h["closeBtn"])}</a>
    </div>
  </section>'''


def page_what(c, lang):
    w = c['what']

    def pillar_link(p):
        if not p.get('link'):
            return ''
        url, name = target(c, lang, p['link'])
        return f'\n      <a class="btn btn--link" href="{url}">{e(name)} →</a>'

    pillars = ''.join(f'''
    <div class="pillar-row">
      <p class="pillar__n">{e(p["n"])}</p>
      <div><h2>{e(p["t"])}</h2><p class="pillar-row__who">{e(p["w"])}</p></div>
      <p class="pillar-row__d">{e(p["d"])}</p>{pillar_link(p)}
    </div>''' for p in w['pillars'])
    steps = ''.join(f'''
          <div class="step"><p class="step__n">{e(s["n"])}</p><h3>{e(s["t"])}</h3><p>{e(s["d"])}</p></div>''' for s in w['steps'])
    proof = ''.join(f'<p class="case">{e(p)}</p>' for p in w['proof'])
    return f'''<main id="main" class="page page--what">
  {phead(w["kicker"], w["title"], w["sub"])}

  <section class="wrap pillars">{pillars}
  </section>

  <section class="band band--ruled" id="start">
    <div class="wrap sec">
      <p class="eyebrow start__kicker">{e(w["startKicker"])}</p>
      <p class="start__note">{e(w["startNote"])}</p>
      <div class="grid grid--2">{steps}
      </div>
    </div>
  </section>

  <section class="wrap sec">
    <p class="eyebrow cases__kicker">{e(w["proofKicker"])}</p>
    <div class="grid grid--280 cases">{proof}</div>
    <p class="footnote">{e(w["proofNote"])}</p>
  </section>

  {poster(c, lang)}
  {site_pager(c, lang, 'what')}
</main>'''


def page_brands(c, lang):
    b = c['brands']
    cols = ''.join(f'<th scope="col">{e(x)}</th>' for x in b['cols'])
    rows = ''.join(f'''
          <tr>
            <td><a href="{href(lang, 'brand', it['slug'])}">{e(it["name"])}</a></td>
            <td>{e(it["cat"])}</td>
            <td class="nowrap">{e(it["mk"])}</td>
            <td><span class="tag">{e(it["st"])}</span></td>
          </tr>''' for it in b['items'])
    cards = ''.join(bcard(c, lang, it) for it in b['items'])
    return f'''<main id="main" class="page page--brands">
  {phead(b["kicker"], b["title"], b["sub"])}

  <section class="wrap brands-table">
    <table class="table">
      <thead><tr>{cols}</tr></thead>
      <tbody>{rows}
      </tbody>
    </table>
  </section>

  <section class="wrap brands-cards">
    <div class="bcards">{cards}
    </div>
  </section>
  {site_pager(c, lang, 'brands')}
</main>'''


def page_brand(c, lang, i):
    b = c['brands']
    it = b['items'][i]
    L = b['labels']
    rng = ''.join(f'<p class="spec__item">{e(r)}</p>' for r in it['range'])
    # a brand with its own website gets a way out to it
    site = ''
    if it.get('url'):
        domain = it['url'].split('//', 1)[-1].rstrip('/')
        site = (f'\n      <p class="brand-hero__site"><a class="btn btn--outline" href="{e(it["url"])}" target="_blank" rel="noopener">'
                f'{e(L["site"].format(domain=domain))} ↗</a></p>')
    return f'''<main id="main" class="page page--brand">
  <section class="wrap brand-back"><a class="back-link" href="{href(lang, 'brands')}">← {e(L["back"])}</a></section>
  <section class="wrap brand-hero">
    <div>
      {eyebrow(it["cat"])}
      <h1 class="disp">{e(it["name"])}</h1>
      <p class="lead" style="--mw:48ch">{e(it["pos"])}</p>{site}
    </div>
    {plate(initials(it['name']), '4x3')}
  </section>
  <section class="wrap brand-specs">
    <div class="grid grid--2">
      <div class="spec">{eyebrow(L["range"])}{rng}</div>
      <div class="spec">{eyebrow(L["channel"])}<p>{e(it["channel"])}</p></div>
      <div class="spec">{eyebrow(L["mk"])}<p>{e(it["mk"])}</p></div>
      <div class="spec">{eyebrow(L["st"])}<p class="spec__tag"><span class="tag">{e(it["st"])}</span></p><p>{e(it["note"])}</p></div>
    </div>
  </section>
  {brand_pager(c, lang, i)}
</main>'''


def brand_pager(c, lang, i):
    items = c['brands']['items']
    prev = ((href(lang, 'brand', items[i - 1]['slug']), items[i - 1]['name']) if i > 0
            else (href(lang, 'brands'), c['nav']['brands']))
    nxt = ((href(lang, 'brand', items[i + 1]['slug']), items[i + 1]['name']) if i + 1 < len(items)
           else (href(lang, 'founders'), c['nav']['founders']))
    return pager(c['ui']['continue'], prev, nxt, c['ui']['prev'], c['ui']['next'])


def person(c, lang, p, team=False):
    brands = {b['name']: b['slug'] for b in c['brands']['items']}
    tags = ''.join(f'<a class="tag tag--outline tag--link" href="{href(lang, "brand", brands[v])}">{e(v)}</a>' if v in brands
                   else f'<span class="tag tag--outline">{e(v)}</span>' for v in p['v'])
    photo = '' if team else portrait(c, p['name'], alt=p['name'])
    contact = f'<a class="person__contact" href="{e(p["waHref"])}" target="_blank" rel="noopener">{e(p["contact"])}</a>' if team else ''
    return f'''
        <article class="person">
          {photo}
          <div>
            {eyebrow(p["city"])}
            <h2>{e(p["name"])}</h2>
            {eyebrow(p["role"], "person__role")}
            <p class="person__bio">{e(p["bio"])}</p>
            {contact}
            <div class="tags">{tags}</div>
          </div>
        </article>'''


def page_founders(c, lang):
    f = c['founders']
    acts = ''.join(f'''
          <div class="act">{eyebrow(a["n"])}<h2>{e(a["t"])}</h2><p>{e(a["d"])}</p></div>''' for a in f['acts'])
    people = ''.join(person(c, lang, p) for p in f['people'])
    team = ''.join(person(c, lang, p, team=True) for p in f['team'])
    return f'''<main id="main" class="page page--founders">
  <section class="band band--ruled">
    <div class="wrap story">
      {eyebrow(f["kicker"])}
      <h1 class="disp">{e(f["title"])}</h1>
      <p class="lead" style="--mw:54ch">{e(f["sub"])}</p>
      <div class="grid grid--3">{acts}
      </div>
    </div>
  </section>

  <section class="wrap profiles-head">
    {eyebrow(f["profKicker"])}
    <p>{e(f["photoNote"])}</p>
  </section>

  <section class="wrap people">
    <div class="trio trio--people">{people}
    </div>
  </section>

  <section class="wrap people people--team">
    {eyebrow(f["teamKicker"], "people__kicker")}
    <div class="trio trio--people">{team}
    </div>
  </section>
  {site_pager(c, lang, 'founders')}
</main>'''


def page_markets(c, lang):
    m = c['markets']
    L = m['labels']
    books = {b['market']: b['slug'] for b in c['playbooks']['items']}
    read = c['playbooks']['labels']['read']
    items = ''
    for n, it in enumerate(m['items']):
        book = f'<a class="btn btn--link" href="{href(lang, "playbook", books[n])}">{e(read)} →</a>' if n in books else ''
        items += f'''
    <div class="market">
      <div class="market__head"><h2>{e(it["c"])}</h2>{eyebrow(L["lead"] + " — " + it["who"])}{book}</div>
      <div class="grid grid--2 facts">
        <div>{eyebrow(L["size"])}<p>{e(it["size"])}</p></div>
        <div>{eyebrow(L["retail"])}<p>{e(it["retail"])}</p></div>
        <div>{eyebrow(L["hard"])}<p>{e(it["hard"])}</p></div>
        <div>{eyebrow(L["have"])}<p>{e(it["have"])}</p></div>
      </div>
    </div>'''
    return f'''<main id="main" class="page page--markets">
  {phead(m["kicker"], m["title"], m["sub"])}

  <section class="wrap route" aria-label="{e(c["ui"]["route"])}">
    <div class="route__track">{stations(c)}</div>
  </section>

  <section class="wrap markets">{items}
  </section>
  {site_pager(c, lang, 'markets')}
</main>'''


def insights_posts(c, cat=0):
    posts = c['insights']['posts']
    return [p for p in posts if cat == 0 or post_cat(c, p) == cat]


def insights_pages(c, cat=0):
    per = c['insights']['perPage']
    return max(1, -(-len(insights_posts(c, cat)) // per))


def page_numbers(c, lang, cat_slug, page_no, total):
    """1 · 2 · 3 with Previous / Next; nothing at all while everything fits on one page."""
    if total < 2:
        return ''
    ui = c['ui']
    nums = ''.join(
        '<li><a class="pages__n" href="{0}" aria-label="{1}"{2}>{3}</a></li>'.format(
            href_list(lang, cat_slug, n), e(ui['pageN'].format(n=n)),
            ' aria-current="page"' if n == page_no else '', n)
        for n in range(1, total + 1))
    prev = (f'<a class="pages__step" href="{href_list(lang, cat_slug, page_no - 1)}" rel="prev">← {e(ui["prev"])}</a>'
            if page_no > 1 else f'<span class="pages__step is-off" aria-hidden="true">← {e(ui["prev"])}</span>')
    nxt = (f'<a class="pages__step" href="{href_list(lang, cat_slug, page_no + 1)}" rel="next">{e(ui["next"])} →</a>'
           if page_no < total else f'<span class="pages__step is-off" aria-hidden="true">{e(ui["next"])} →</span>')
    return f'''
    <nav class="pages" aria-label="{e(ui["pages"])}">{prev}<ol>{nums}</ol>{nxt}</nav>'''


def written(p):
    return bool(p.get('body'))


def post_meta(c, p):
    """The line above a post's title: its date, or "Coming soon" while it is still being written."""
    return (p['d'] if written(p) else c['ui']['soon']) + ' · ' + p['c']


def page_insights(c, lang, cat=0, page_no=1):
    s = c['insights']
    cats, slugs = s['cats'], s['catSlugs']
    per = s['perPage']
    chips = ''.join(
        '<a class="chip" href="{0}"{1}>{2}</a>'.format(
            href_list(lang, slugs[i]), ' aria-current="page"' if i == cat else '', e(x))
        for i, x in enumerate(cats))
    shown = insights_posts(c, cat)[(page_no - 1) * per: page_no * per]
    posts = ''.join(f'''
    <a class="post-row" href="{href_post(lang, p['slug'])}">
      {eyebrow(post_meta(c, p))}
      <h2>{e(p["t"])}</h2>
      <p class="post-row__ex">{e(p["ex"])}</p>
      {eyebrow(p["lang"])}
    </a>''' for p in shown)
    chips_html = f'\n    <nav class="chips" aria-label="{e(c["ui"]["filter"])}">{chips}</nav>'
    # the channel is shown once it has an address to send people to
    channel = f'''
  <section class="band band--ruled">
    <div class="wrap sec channel">
      <div>
        {eyebrow(s["videoKicker"])}
        <h2 class="disp">{e(s["videoTitle"])}</h2>
        <p>{e(s["videoNote"])}</p>
        {action(s["videoBtn"], s["videoHref"])}
      </div>
      {plate('▶', '16x9')}
    </div>
  </section>''' if s.get('videoHref') else ''
    return f'''<main id="main" class="page page--insights">
  {phead(s["kicker"], s["title"], s["sub"], extra=chips_html)}

  <section class="wrap posts">{posts}{page_numbers(c, lang, slugs[cat], page_no, insights_pages(c, cat))}
  </section>
{channel}
  {site_pager(c, lang, 'insights')}
</main>'''


def page_post(c, lang, i):
    s = c['insights']
    posts = s['posts']
    p = posts[i]
    ui = c['ui']
    body = ''.join(f'<p>{e(x)}</p>' for x in p.get('body', [])) or f'<p class="post-body__soon">{e(ui["articleSoon"])}</p>'
    related = ''
    if p.get('rel'):
        url, name = target(c, lang, p['rel'])
        related = f'\n    <p class="post-rel">{eyebrow(ui["related"])}<a class="btn btn--outline" href="{url}">{e(name)} →</a></p>'
    prev = (href_post(lang, posts[i - 1]['slug']), posts[i - 1]['t']) if i > 0 else None
    nxt = (href_post(lang, posts[i + 1]['slug']), posts[i + 1]['t']) if i + 1 < len(posts) else None
    return f'''<main id="main" class="page page--post">
  <section class="wrap post-head">
    <a class="back-link" href="{href_list(lang)}">← {e(ui["allInsights"])}</a>
    {eyebrow(post_meta(c, p))}
    <h1 class="disp">{e(p["t"])}</h1>
    <p class="lead" style="--mw:52ch">{e(p["ex"])}</p>
    {eyebrow(p["lang"], "post-head__lang")}
  </section>

  <section class="wrap post-body">
    {body}{related}
  </section>
  {pager(ui["allInsights"], prev, nxt, ui["prevArticle"], ui["nextArticle"])}
</main>'''


def page_contact(c, lang):
    k = c['contact']
    regions = ''.join(
        f'<button class="chip" type="button" data-region="{v}" aria-pressed="{"true" if v == "cn" else "false"}">{e(label)}</button>'
        for v, label in k['regions'])
    channels = ''.join(f'''
        <div class="channel-card" data-channel="{key}">
          <h2>{e(k["channels"][key]["t"])}</h2>
          <p>{e(k["channels"][key]["d"])}</p>
          {action(k["channels"][key]["a"], k["channels"][key].get("href", ""))}
        </div>''' for key in ('wechat', 'email', 'whatsapp'))
    offices = ''.join(f'''
          <div class="office"><p class="office__city">{e(city)}</p><p>{e(note)}</p></div>''' for city, note in k['offices'])
    region_html = f'''
    <div class="region" role="group" aria-labelledby="region-label"><p class="eyebrow" id="region-label">{e(k["region"])}</p>{regions}</div>'''
    return f'''<main id="main" class="page page--contact">
  {phead(k["kicker"], k["title"], k["sub"], extra=region_html)}

  <section class="wrap channels">
    <div class="grid grid--3" data-channels>{channels}
    </div>
  </section>

  <section class="offices">
    <div class="wrap sec">
      <p class="eyebrow offices__kicker">{e(k["officesKicker"])}</p>
      <div class="office-list">{offices}
      </div>
    </div>
  </section>
</main>'''


def page_partner(c, lang):
    p = c['partner']
    qs = p['qs']
    total = len(qs) + 1

    def progress(n):
        pct = round(n / total * 100)
        return f'''
        <div class="progress" aria-hidden="true"><div style="width:{pct}%"></div></div>
        <p class="eyebrow step-count">{n} {e(p["of"])} {total}</p>'''

    def nav_row(last=False):
        nxt = (f'<button class="btn btn--primary" type="submit">{e(p["submit"])}</button>' if last
               else f'<button class="btn btn--primary" type="button" data-next>{e(p["next"])}</button>')
        note = privacy_note(c, lang) if last else ''
        return f'''
        <div class="survey__nav">
          <button class="btn btn--link" type="button" data-back>{e(p["back"])}</button>
          {nxt}
        </div>{note}'''

    steps = ''
    for i, q in enumerate(qs):
        kind = 'checkbox' if q.get('multi') else 'radio'
        opts = ''.join(
            f'<label class="opt"><input type="{kind}" name="{q["k"]}" value="{e(v)}"><span>{e(label)}</span></label>'
            for v, label in q['opts'])
        # steps only some audiences see, and wording that changes per audience
        attrs = f' data-short="{e(q["short"])}"'
        if q.get('multi'):
            attrs += ' data-multi'
        if q.get('for'):
            attrs += f' data-for="{" ".join(q["for"])}"'
        if q.get('qFor'):
            attrs += f' data-alt="{e(json.dumps(q["qFor"], ensure_ascii=False))}"'
        steps += f'''
      <div class="survey__step" id="q{i + 1}" role="group" aria-labelledby="q{i + 1}-t" data-step="{i}" data-key="{q["k"]}"{attrs}>{progress(i + 1)}
        <h2 class="display disp" id="q{i + 1}-t">{e(q["q"])}</h2>
        <p class="lead">{e(q["h"])}</p>
        <div class="opts">{opts}</div>{nav_row()}
      </div>'''

    ct = p['contact']
    fields = [('contact_name', 'name', 'text', 'name'), ('company_name', 'company', 'text', 'organization'),
              ('company_country', 'country', 'text', 'country-name'), ('contact_email', 'email', 'email', 'email'),
              ('handle', 'handle', 'text', 'off'), ('contact_phone', 'phone', 'tel', 'tel')]
    inputs = ''.join(f'''
          <div class="field"><label for="f-{k}">{e(ct[label])}</label><input class="input" id="f-{k}" name="{k}" type="{t}" autocomplete="{ac}"></div>'''
                     for k, label, t, ac in fields)

    d = p['done']
    h = d['handoff']
    services = {x['slug']: x['name'] for x in c['services']['items']}
    labels = {'service': h['service'], 'source': h['source'], 'score': h['scoreLine'], 'msg': h['msg'], 'subject': h['subject'],
              'sending': p['sending']}
    return f'''<main id="main" class="page page--partner">
  <form class="survey" method="post" data-survey data-state="intro" data-endpoint="/api/lead" data-lang="{lang}" data-of="{e(p["of"])}" novalidate>
    <script type="application/json" data-survey-text>{json.dumps({"services": services, "labels": labels}, ensure_ascii=False)}</script>
    <input type="hidden" name="service" value="">
    <div class="hp" aria-hidden="true"><label for="f-website">Website</label><input id="f-website" name="website" type="text" tabindex="-1" autocomplete="off"></div>
    <section class="survey__intro" data-step="intro">
      {eyebrow(p["kicker"])}
      <h1 class="disp">{e(p["title"])}</h1>
      <p class="lead" style="--mw:52ch">{e(p["sub"])}</p>
      <p class="survey__service" data-service-note hidden>{e(h["service"])}: <strong></strong></p>
      <a class="btn btn--primary" href="#q1" data-start>{e(p["start"])}</a>
    </section>
    <div class="survey__steps">{steps}
      <div class="survey__step" id="q{total}" role="group" aria-labelledby="q{total}-t" data-step="{len(qs)}">{progress(total)}
        <h2 class="display disp" id="q{total}-t">{e(ct["q"])}</h2>
        <p class="lead">{e(ct["h"])}</p>
        <div class="fields">{inputs}
        </div>
        <div class="field field--wide"><label for="f-message">{e(ct["message"])}</label><textarea class="input" id="f-message" name="message" rows="4"></textarea></div>
        <p class="survey__error is-in" role="alert" data-contact-error hidden>{e(ct["need"])}</p>{nav_row(last=True)}
      </div>
    </div>
  </form>

  <section class="done" data-done hidden>
    <div class="done__in">
      <span class="done__tick" aria-hidden="true"><svg viewBox="0 0 44 44" width="34" height="34" fill="none" stroke="currentColor" stroke-width="3.2" stroke-linecap="round" stroke-linejoin="round"><path d="M11 23.5 L19 31 L33 14"/></svg></span>
      {eyebrow(p["kicker"])}
      <h1 class="done__title" tabindex="-1" data-mode="handoff">{e(h["t"])}</h1>
      <h1 class="done__title" tabindex="-1" data-mode="sent" hidden>{e(d["t"])}</h1>
      <p class="done__sub" data-mode="handoff">{e(h["d"])} <strong data-assignee></strong> {e(h["d2"])}</p>
      <p class="done__sub" data-mode="sent" hidden>{e(d["d"])} <a class="wa-link" data-assignee-link href="#" target="_blank" rel="noopener"><span data-assignee></span>{WA_ICON}</a> — {e(d["d2"])}</p>
      <div class="done__acts done__send" data-mode="handoff">
        <a class="btn btn--primary btn--lg" data-wa href="#" target="_blank" rel="noopener">{WA_ICON}{e(h["wa"])}</a>
        <a class="btn btn--outline btn--lg" data-mail href="#">{e(h["email"])}</a>
      </div>
      <div class="done__cards">
        <div class="done__card">{eyebrow(d["route"])}<a class="done__fig wa-link" data-assignee-link href="#" target="_blank" rel="noopener"><span data-assignee></span>{WA_ICON}</a></div>
        <div class="done__card">{eyebrow(d["score"])}<p class="done__fig"><span class="done__score" data-score></span><span class="done__of">/ 90</span></p></div>
      </div>
      <div class="done__acts">
        <a class="btn btn--primary" href="{href(lang, 'brands')}">{e(c["nav"]["brands"])}</a>
        <button class="btn btn--outline" type="button" data-restart>{e(d["again"])}</button>
      </div>
    </div>
  </section>
</main>'''


# ── services ──────────────────────────────────────────────────────────────

def service_by_slug(c, slug):
    return next(x for x in c['services']['items'] if x['slug'] == slug)


def model_badges(c, models):
    names = c['services']['models']
    return ''.join(f'<span class="badge badge--{k}">{e(names[k])}</span>' for k in models)


def service_card(c, lang, x):
    return f'''
        <a class="panel svc-card" href="{href(lang, 'service', x['slug'])}">
          <p class="svc-card__models">{model_badges(c, x['model'])}</p>
          <h3>{e(x["name"])}</h3>
          <p>{e(x["one"])}</p>
          <p class="svc-card__meta">{e(x["timeline"])}<span aria-hidden="true">→</span></p>
        </a>'''


def page_services(c, lang):
    s = c['services']
    jumps = ''.join(f'<a class="chip" href="#{g["key"]}">{e(g["name"])}</a>' for g in s['groups'])
    groups = ''
    for i, g in enumerate(s['groups']):
        cards = ''.join(service_card(c, lang, x) for x in s['items'] if x['group'] == g['key'])
        groups += f'''
  <section class="svc-group{' band' if i % 2 else ''}" id="{g['key']}">
    <div class="wrap sec">
      <header class="shead">{eyebrow(f"{i + 1:02d}")}<h2 class="sech">{e(g["name"])}</h2><p class="lead">{e(g["intro"])}</p></header>
      <div class="grid grid--2 svc-cards">{cards}
      </div>
    </div>
  </section>'''
    l = c['launch']
    pricing = ''.join(f'<div class="panel"><h3>{e(p["t"])}</h3><p>{e(p["d"])}</p></div>' for p in l['pricing'])
    extra = f'\n    <nav class="chips" aria-label="{e(s["kicker"])}">{jumps}</nav>'
    return f'''<main id="main" class="page page--services">
  {phead(s["kicker"], s["title"], s["sub"], extra=extra)}
{groups}

  <section class="wrap sec">
    <header class="shead">{eyebrow(l["pricingKicker"])}<h2 class="sech">{e(l["pricingTitle"])}</h2></header>
    <div class="grid grid--2">{pricing}</div>
    <div class="actions"><a class="btn btn--primary" href="{href(lang, 'launch')}">{e(c["nav"]["launch"])}</a></div>
  </section>
  {site_pager(c, lang, 'services')}
</main>'''


def service_catalog(c, lang, cat):
    """A service's practice list (the IT catalogue): numbered cards, each a one-line
    purpose and its named services; a practice may point to a sibling service."""
    def more(g):
        if not g.get('link'):
            return ''
        return (f'\n          <a class="btn btn--link cap__more" href="{href(lang, "service", g["link"])}">'
                f'{e(service_by_slug(c, g["link"])["name"])} →</a>')
    cards = ''.join(f'''
      <article class="panel cap">
        <p class="cap__n">{n + 1:02d}</p>
        <h3>{e(g["t"])}</h3>
        <p class="cap__d">{e(g["d"])}</p>
        <ul class="cap__list">{''.join(f'<li>{e(it)}</li>' for it in g["items"])}</ul>{more(g)}
      </article>''' for n, g in enumerate(cat['groups']))
    return f'''

  <section class="wrap caps-wrap" id="practices">
    <header class="shead">{eyebrow(cat["kicker"])}<h2 class="sech">{e(cat["title"])}</h2><p class="lead">{e(cat["sub"])}</p></header>
    <div class="caps">{cards}
    </div>
  </section>'''


def page_service(c, lang, i):
    s = c['services']
    L = s['labels']
    items = s['items']
    x = items[i]
    group = next(g for g in s['groups'] if g['key'] == x['group'])
    facts = [(L['timeline'], e(x['timeline'])), (L['model'], model_badges(c, x['model'])),
             (L['lead'], e(x['lead'])), (L['markets'], e(x['markets']))]
    facts_html = ''.join(f'<div class="fact">{eyebrow(k)}<p class="fact__v">{v}</p></div>' for k, v in facts)
    deliver = ''.join(f'<li>{e(d)}</li>' for d in x['deliverables'])
    related = ''.join(service_card(c, lang, service_by_slug(c, r)) for r in x['related'])
    catalog = service_catalog(c, lang, x['catalog']) if x.get('catalog') else ''
    also = ''
    if x.get('links'):
        also_links = ''.join(f'<a class="btn btn--link" href="{u}">{e(nm)} →</a>' for u, nm in (target(c, lang, {'page': k}) for k in x['links']))
        also = f'\n    <div class="svc-also">{eyebrow(L["also"])}{also_links}</div>'
    prev = ((href(lang, 'service', items[i - 1]['slug']), items[i - 1]['name']) if i > 0
            else (href(lang, 'services'), L['all']))
    nxt = ((href(lang, 'service', items[i + 1]['slug']), items[i + 1]['name']) if i + 1 < len(items)
           else (href(lang, 'launch'), c['nav']['launch']))
    return f'''<main id="main" class="page page--service">
  <section class="wrap brand-back"><a class="back-link" href="{href(lang, 'services')}#{x['group']}">← {e(L["all"])}</a></section>
  <section class="wrap svc-hero">
    {eyebrow(group["name"])}
    <h1 class="disp">{e(x["name"])}</h1>
    <p class="lead" style="--mw:46ch">{e(x["one"])}</p>
    <div class="svc-facts">{facts_html}</div>
  </section>

  <section class="wrap svc-body">
    <div class="grid grid--2">
      <div class="panel svc-problem">{eyebrow(L["problem"])}<p>{e(x["problem"])}</p></div>
      <div class="panel svc-deliver">{eyebrow(L["deliverables"])}<ul class="ticks">{deliver}</ul></div>
    </div>
    <p class="note">{e(L["indicative"])}</p>{also}
  </section>{catalog}

  <section class="band">
    <div class="wrap sec">
      <header class="shead">{eyebrow(L["related"])}</header>
      <div class="grid grid--3 svc-cards">{related}
      </div>
    </div>
  </section>

  <section class="poster">
    <div class="wrap sec">
      <h2 class="title disp">{e(x["name"])}</h2>
      <a class="btn btn--light" href="{href(lang, 'partner')}?service={x['slug']}">{e(L["cta"])}</a>
    </div>
  </section>
  {pager(c['ui']['continue'], prev, nxt, c['ui']['prev'], c['ui']['next'])}
</main>'''


# ── launch programme ──────────────────────────────────────────────────────

def page_launch(c, lang):
    l = c['launch']
    L = l['labels']
    models = c['services']['models']
    stages = ''.join(f'''
      <li class="stage">
        <p class="stage__n">{e(st["n"])}</p>
        <div class="stage__body">
          <h3>{e(st["name"])}</h3>
          <p>{e(st["scope"])}</p>
          <dl class="stage__facts">
            <div><dt>{e(L["duration"])}</dt><dd>{e(st["duration"])}</dd></div>
            <div><dt>{e(L["deliverable"])}</dt><dd>{e(st["deliverable"])}</dd></div>
            <div><dt>{e(L["model"])}</dt><dd><span class="badge badge--{st["model"]}">{e(models[st["model"]])}</span></dd></div>
          </dl>
          <a class="btn btn--link" href="{href(lang, 'service', st['service'])}">{e(service_by_slug(c, st["service"])["name"])} →</a>
        </div>
      </li>''' for st in l['stages'])

    def fit(block, kind):
        items = ''.join(f'<li>{e(x)}</li>' for x in block['items'])
        return f'<div class="panel fit"><h3>{e(block["t"])}</h3><ul class="ticks ticks--{kind}">{items}</ul></div>'

    pricing = ''.join(f'<div class="panel"><h3>{e(p["t"])}</h3><p>{e(p["d"])}</p></div>' for p in l['pricing'])
    faq = ''.join(f'<details class="faq__item"><summary>{e(q["q"])}</summary><p>{e(q["a"])}</p></details>' for q in l['faq'])
    return f'''<main id="main" class="page page--launch">
  {phead(l["kicker"], l["title"], l["sub"])}

  <section class="wrap sec">
    <header class="shead">{eyebrow(l["stagesKicker"])}<h2 class="sech">{e(l["stagesTitle"])}</h2></header>
    <ol class="stages">{stages}
    </ol>
  </section>

  <section class="band">
    <div class="wrap sec">
      <header class="shead">{eyebrow(l["forKicker"])}<h2 class="sech">{e(l["forTitle"])}</h2></header>
      <div class="grid grid--2">{fit(l["forYes"], "yes")}{fit(l["forNo"], "no")}</div>
    </div>
  </section>

  <section class="wrap sec">
    <header class="shead">{eyebrow(l["pricingKicker"])}<h2 class="sech">{e(l["pricingTitle"])}</h2></header>
    <div class="grid grid--2">{pricing}</div>
  </section>

  <section class="band">
    <div class="wrap sec">
      <header class="shead">{eyebrow(l["faqKicker"])}<h2 class="sech">{e(l["faqTitle"])}</h2></header>
      <div class="faq">{faq}</div>
    </div>
  </section>

  <section class="poster">
    <div class="wrap sec">
      <h2 class="title disp">{e(c["home"]["closeA"])}</h2>
      <p class="poster__note">{e(l["applyNote"])}</p>
      <a class="btn btn--light" href="{href(lang, 'partner')}">{e(c["home"]["closeBtn"])}</a>
    </div>
  </section>
  {site_pager(c, lang, 'launch')}
</main>'''


# ── audiences ─────────────────────────────────────────────────────────────

def page_audience(c, lang, i):
    a = c['audiences']
    L = a['labels']
    items = a['items']
    x = items[i]
    apply = href(lang, 'partner') + '?as=' + x['as']
    pains = ''.join(f'<div class="panel"><h3>{e(p["t"])}</h3><p>{e(p["d"])}</p></div>' for p in x['pains'])
    offer = ''.join(
        f'<div class="panel offer"><p class="offer__n">{n + 1:02d}</p><h3>{e(o["t"])}</h3><p>{e(o["d"])}</p></div>'
        for n, o in enumerate(x['offer']))
    services = ''.join(service_card(c, lang, service_by_slug(c, s)) for s in x['services'])
    prev = ((href(lang, 'audience', items[i - 1]['slug']), items[i - 1]['name']) if i > 0
            else (href(lang, 'services'), c['nav']['services']))
    nxt = ((href(lang, 'audience', items[i + 1]['slug']), items[i + 1]['name']) if i + 1 < len(items)
           else (href(lang, 'launch'), c['nav']['launch']))
    cta = f'\n    <div class="actions"><a class="btn btn--primary btn--lg" href="{apply}">{e(x["cta"])}</a></div>'
    return f'''<main id="main" class="page page--audience">
  {phead(x["name"], x["title"], x["sub"], mw="52ch", extra=cta)}

  <section class="wrap sec">
    <header class="shead">{eyebrow(L["pains"])}</header>
    <div class="grid grid--3">{pains}</div>
  </section>

  <section class="band">
    <div class="wrap sec">
      <header class="shead">{eyebrow(L["offer"])}</header>
      <div class="grid grid--2">{offer}</div>
    </div>
  </section>

  <section class="wrap sec">
    <header class="shead">{eyebrow(L["services"])}</header>
    <div class="grid grid--3 svc-cards">{services}
    </div>
  </section>

  <section class="poster">
    <div class="wrap sec">
      <h2 class="title disp">{e(x["title"])}</h2>
      <a class="btn btn--light" href="{apply}">{e(x["cta"])}</a>
    </div>
  </section>
  {pager(c['ui']['continue'], prev, nxt, c['ui']['prev'], c['ui']['next'])}
</main>'''


# ── market playbooks ──────────────────────────────────────────────────────

def ticks(items, kind=''):
    return f'<ul class="ticks{" ticks--" + kind if kind else ""}">' + ''.join(f'<li>{e(x)}</li>' for x in items) + '</ul>'


def page_playbook(c, lang, i):
    pb = c['playbooks']
    L = pb['labels']
    books = pb['items']
    x = books[i]
    m = c['markets']['items'][x['market']]
    ML = c['markets']['labels']
    certs = ''.join(f'<tr><th scope="row">{e(name)}</th><td>{e(scope)}</td><td class="nowrap">{e(weeks)}</td></tr>'
                    for name, scope, weeks in x['certs'])
    guide = next((g for g in c['travel']['guides'] if g['slug'] == x['slug']), None)
    guide_link = (f'\n      <a class="btn btn--outline" href="{href(lang, "guide", x["slug"])}">{e(c["travel"]["labels"]["guide"])}</a>'
                  if guide else '')
    estimate = href(lang, 'estimator') + '?market=' + x['code']
    prev = ((href(lang, 'playbook', books[i - 1]['slug']), c['markets']['items'][books[i - 1]['market']]['c']) if i > 0
            else (href(lang, 'markets'), L['all']))
    nxt = ((href(lang, 'playbook', books[i + 1]['slug']), c['markets']['items'][books[i + 1]['market']]['c']) if i + 1 < len(books)
           else (href(lang, 'estimator'), c['nav']['estimator']))
    return f'''<main id="main" class="page page--playbook">
  <section class="wrap brand-back"><a class="back-link" href="{href(lang, 'markets')}">← {e(L["all"])}</a></section>
  <section class="wrap svc-hero">
    {eyebrow(pb["kicker"])}
    <h1 class="disp">{e(m["c"])}</h1>
    <p class="lead" style="--mw:46ch">{e(m["size"])}</p>
    {eyebrow(ML["lead"] + " — " + m["who"], "playbook__lead")}
    <div class="actions actions--row">
      <a class="btn btn--primary" href="{estimate}">{e(L["estimate"])}</a>
      <a class="btn btn--outline" href="{href(lang, 'trip', x['trip'])}">{e(L["trip"])}</a>{guide_link}
    </div>
  </section>

  <section class="wrap sec">
    <div class="grid grid--3">
      <div class="panel">{eyebrow(L["retail"])}<p>{e(m["retail"])}</p></div>
      <div class="panel">{eyebrow(L["hard"])}<p>{e(m["hard"])}</p></div>
      <div class="panel">{eyebrow(L["have"])}<p>{e(m["have"])}</p></div>
    </div>
  </section>

  <section class="band">
    <div class="wrap sec">
      <header class="shead">{eyebrow(L["certs"])}</header>
      <table class="table table--spec">
        <thead><tr><th scope="col">{e(L["approval"])}</th><th scope="col">{e(L["covers"])}</th><th scope="col">{e(L["weeks"])}</th></tr></thead>
        <tbody>{certs}</tbody>
      </table>
    </div>
  </section>

  <section class="wrap sec">
    <div class="grid grid--2">
      <div class="panel">{eyebrow(L["customs"])}{ticks(x["customs"])}</div>
      <div class="panel">{eyebrow(L["channels"])}{ticks(x["channels"])}</div>
      <div class="panel">{eyebrow(L["cities"])}<p class="cities">{" · ".join(e(y) for y in x["cities"])}</p></div>
      <div class="panel">{eyebrow(L["visiting"])}{ticks(x["visiting"])}</div>
    </div>
    <p class="note">{e(L["note"])}</p>
  </section>
  {pager(c['ui']['continue'], prev, nxt, c['ui']['prev'], c['ui']['next'])}
</main>'''


# ── entry estimator ───────────────────────────────────────────────────────

def page_estimator(c, lang):
    est = c['estimator']
    L = est['labels']
    books = {b['code']: (href(lang, 'playbook', b['slug']), c['markets']['items'][b['market']]['c']) for b in c['playbooks']['items']}
    data = {
        'rules': c['estimatorRules'], 'certs': est['certs'], 'tax': est['tax'], 'duty': est['duty'],
        'dutyUnknown': est['dutyUnknown'], 'labels': L, 'setup': est['setupWeeks'], 'ship': est['shipWeeks'],
        'services': {x['slug']: [x['name'], href(lang, 'service', x['slug'])] for x in c['services']['items']},
        'playbooks': {k: v[0] for k, v in books.items()},
        'apply': href(lang, 'partner'),
    }
    payload = json.dumps(data, ensure_ascii=False).replace('</', '<\\/')
    cats = ''.join(f'<option value="{k}">{e(v)}</option>' for k, v in est['categories'])
    markets = ''.join(f'<option value="{k}">{e(v)}</option>' for k, v in est['markets'])
    cards = ''.join(f'''
        <a class="panel svc-card" href="{url}">
          <h3>{e(name)}</h3>
          <p>{e(c["markets"]["items"][b["market"]]["size"])}</p>
          <p class="svc-card__meta">{e(c["playbooks"]["labels"]["read"])}<span aria-hidden="true">→</span></p>
        </a>''' for b in c['playbooks']['items'] for url, name in [books[b['code']]])
    return f'''<main id="main" class="page page--estimator">
  {phead(est["kicker"], est["title"], est["sub"])}

  <section class="wrap estimator-wrap">
    <script type="application/json" data-estimator-data>{payload}</script>
    <form class="panel estimator" data-estimator>
      <div class="estimator__fields">
        <div class="field"><label for="est-category">{e(L["category"])}</label><select class="input" id="est-category" name="category">{cats}</select></div>
        <div class="field"><label for="est-market">{e(L["market"])}</label><select class="input" id="est-market" name="market">{markets}</select></div>
        <div class="field"><label for="est-fob">{e(L["fob"])}</label><input class="input" id="est-fob" name="fob" type="number" min="0" step="0.01" inputmode="decimal" placeholder="12.50"></div>
      </div>
      <p class="estimator__hint">{e(L["fobHint"])}</p>
    </form>
    <noscript><p class="note">{e(L["noscript"])}</p></noscript>
    <div class="est-result" data-est-result aria-live="polite"></div>
    <p class="note">{e(L["disclaimer"])}</p>
  </section>

  <section class="band">
    <div class="wrap sec">
      <header class="shead">{eyebrow(c["playbooks"]["kicker"])}</header>
      <div class="grid grid--2 svc-cards">{cards}
      </div>
    </div>
  </section>
  {pager(c['ui']['continue'], (href(lang, 'markets'), c['nav']['markets']), (href(lang, 'expeditions'), c['nav']['expeditions']), c['ui']['prev'], c['ui']['next'])}
</main>'''


# ── expeditions ──────────────────────────────────────────────────────────

def trip_card(c, lang, x, kicker=None):
    ex = c['expeditions']
    return f'''
        <a class="panel svc-card trip-card" href="{href(lang, 'trip', x['slug'])}">
          {eyebrow(kicker or ex["types"][x["type"]]["t"])}
          <h3>{e(x["title"])}</h3>
          <p>{e(x["one"])}</p>
          <p class="svc-card__meta">{e(x["when"])} · {e(x["length"])}<span aria-hidden="true">→</span></p>
        </a>'''


def page_expeditions(c, lang):
    ex = c['expeditions']
    editions = ''.join(trip_card(c, lang, x) for x in ex['editions'])
    interest = 'mailto:help@tgobrands.com?subject=' + ex['kicker'].replace(' ', '%20')
    return f'''<main id="main" class="page page--expeditions">
  {phead(ex["kicker"], ex["title"], ex["sub"])}

  <section class="wrap sec">
    <header class="shead">{eyebrow(ex["editionsKicker"])}<h2 class="sech">{e(ex["editionsTitle"])}</h2></header>
    <div class="grid grid--2 svc-cards">{editions}
    </div>
    <p class="note">{e(ex["labels"]["note"])}</p>
  </section>

  <section class="band">
    <div class="wrap sec">
      <header class="shead">{eyebrow(c["travel"]["kicker"])}<h2 class="sech">{e(ex["labels"]["private"])}</h2><p class="lead" style="--mw:52ch">{e(c["travel"]["sub"])}</p></header>
      <div class="actions"><a class="btn btn--primary" href="{href(lang, 'travel')}#plan">{e(c["travel"]["labels"]["plan"])}</a></div>
    </div>
  </section>

  <section class="poster">
    <div class="wrap sec">
      <h2 class="title disp">{e(ex["title"])}</h2>
      <a class="btn btn--light" href="{interest}">{e(ex["labels"]["interest"])}</a>
    </div>
  </section>
  {site_pager(c, lang, 'expeditions')}
</main>'''


def page_trip(c, lang, i):
    ex = c['expeditions']
    L = ex['labels']
    items = ex['editions']
    x = items[i]
    facts = [(L['when'], x['when']), (L['length'], x['length']), (L['group'], x['group']), (L['lead'], x['lead'])]
    facts_html = ''.join(f'<div class="fact">{eyebrow(k)}<p class="fact__v">{e(v)}</p></div>' for k, v in facts)
    days = ''.join(
        f'<li class="day"><p class="day__n">{e(L["day"].format(n=n + 1))}</p><div><h3>{e(city)}</h3><p>{e(what)}</p></div></li>'
        for n, (city, what) in enumerate(x['days']))
    apply = href(lang, 'partner') + '?service=market-survey-trips'
    book = (f'<a class="btn btn--outline" href="{href(lang, "playbook", x["playbook"])}">{e(L["playbook"])}</a>'
            if x['playbook'] else '')
    guide = next((g for g in c['travel']['guides'] if g['code'] == x['market']), None)
    if guide:
        book += f'\n      <a class="btn btn--outline" href="{href(lang, "guide", guide["slug"])}">{e(c["travel"]["labels"]["guide"])}</a>'
    prev = ((href(lang, 'trip', items[i - 1]['slug']), items[i - 1]['title']) if i > 0
            else (href(lang, 'expeditions'), L['all']))
    nxt = ((href(lang, 'trip', items[i + 1]['slug']), items[i + 1]['title']) if i + 1 < len(items)
           else (href(lang, 'expeditions'), L['all']))
    return f'''<main id="main" class="page page--trip">
  <section class="wrap brand-back"><a class="back-link" href="{href(lang, 'expeditions')}">← {e(L["all"])}</a></section>
  <section class="wrap svc-hero">
    {eyebrow(ex["types"][x["type"]]["t"])}
    <h1 class="disp">{e(x["title"])}</h1>
    <p class="lead" style="--mw:46ch">{e(x["one"])}</p>
    <div class="svc-facts">{facts_html}</div>
    <div class="actions actions--row">
      <a class="btn btn--primary" href="{apply}">{e(L["apply"])}</a>
      {book}
    </div>
  </section>

  <section class="wrap sec">
    <header class="shead">{eyebrow(L["itinerary"])}</header>
    <ol class="itinerary">{days}</ol>
  </section>

  <section class="band">
    <div class="wrap sec">
      <div class="grid grid--2">
        <div class="panel">{eyebrow(L["included"])}{ticks(ex["included"])}</div>
        <div class="panel">{eyebrow(L["excluded"])}{ticks(ex["excluded"], "no")}</div>
        <div class="panel">{eyebrow(L["for"])}<p>{e(x["for"])}</p></div>
        <div class="panel">{eyebrow(L["price"])}<p class="price">{e(x["price"])}</p></div>
      </div>
      <p class="note">{e(L["note"])}</p>
    </div>
  </section>
  {pager(c['ui']['continue'], prev, nxt, c['ui']['prev'], c['ui']['next'])}
</main>'''


# ── travel ────────────────────────────────────────────────────────────────

TRAVEL_HOSTS = {'PK': 'Umair', 'IN': 'Aryan', 'PH': 'Umer', 'AE': 'Shamas', 'CN': 'Umair', 'BD': 'Aryan', 'NP': 'Aryan'}


def attr(name, value):
    return f' {name}="{e(value)}"' if value else ''


def travel_form(c, lang, preset=''):
    """The travel enquiry. Posts to /api/lead like the partner application and, when the
    server cannot deliver it, hands off to WhatsApp or email."""
    t = c['travel']
    f = t['form']
    opt = lambda kind, name, value, label, on=False: (
        f'<label class="opt"><input type="{kind}" name="{name}" value="{e(value)}"{" checked" if on else ""}>'
        f'<span>{e(label)}</span></label>')
    dests = ''.join(opt('checkbox', 'destinations', d['code'], d['name'], d['code'] == preset) for d in t['destinations'])
    purposes = ''.join(opt('radio', 'purpose', v, n) for v, n in f['purposes'])
    bands = ''.join(opt('radio', 'travellers', v, n) for v, n in f['bands'])
    fields = [('contact_name', 'name', 'text', 'name', ''), ('travel_from', 'from', 'text', 'off', f['fromHint']),
              ('travel_when', 'when', 'text', 'off', f['whenHint']), ('contact_email', 'email', 'email', 'email', ''),
              ('handle', 'handle', 'text', 'off', ''), ('contact_phone', 'phone', 'tel', 'tel', '')]
    inputs = ''.join(
        f'<div class="field"><label for="t-{k}">{e(f[label])}</label>'
        f'<input class="input" id="t-{k}" name="{k}" type="{kind}" autocomplete="{ac}"{attr("placeholder", hint)}></div>'
        for k, label, kind, ac, hint in fields)
    payload = {
        'labels': {k: f[k] for k in ('sending', 'needDest', 'needContact', 'subject', 'msg', 'people', 'dest', 'purpose',
                                     'travellers', 'when', 'from', 'name', 'email', 'handle', 'phone', 'message')},
        'dests': {d['code']: d['name'] for d in t['destinations']},
        'purposes': dict(f['purposes']),
        'hosts': TRAVEL_HOSTS,
    }
    data = json.dumps(payload, ensure_ascii=False).replace('</', '<\\/')
    sep = ''  # the second half of each sentence carries its own punctuation
    return f"""<section class="wrap sec" id="plan">
    <header class="shead">{eyebrow(f["kicker"])}<h2 class="sech">{e(f["title"])}</h2><p class="lead">{e(f["sub"])}</p></header>
    <form class="panel tform" data-travel data-endpoint="/api/lead" data-lang="{lang}" novalidate>
      <script type="application/json" data-travel-text>{data}</script>
      <div class="hp" aria-hidden="true"><label for="t-website">Website</label><input id="t-website" name="website" type="text" tabindex="-1" autocomplete="off"></div>
      <fieldset class="tform__group"><legend>{e(f["dest"])}</legend><div class="opts">{dests}</div></fieldset>
      <fieldset class="tform__group"><legend>{e(f["purpose"])}</legend><div class="opts">{purposes}</div></fieldset>
      <fieldset class="tform__group"><legend>{e(f["travellers"])}</legend><div class="opts">{bands}</div></fieldset>
      <div class="fields">{inputs}</div>
      <div class="field field--wide"><label for="t-message">{e(f["message"])}</label><textarea class="input" id="t-message" name="message" rows="3"></textarea></div>
      <p class="survey__error is-in" role="alert" data-travel-error hidden></p>
      <div class="tform__nav"><button class="btn btn--primary btn--lg" type="submit">{e(f["submit"])}</button></div>
      {privacy_note(c, lang)}
      <noscript><p class="note">{e(f["noscript"])}</p></noscript>
    </form>
    <div class="panel tdone" data-travel-done hidden>
      <h3 class="tdone__title" tabindex="-1" data-mode="sent">{e(f["sentT"])}</h3>
      <p data-mode="sent">{e(f["sentD"])} <strong data-who></strong>{sep}{e(f["sentD2"])}</p>
      <h3 class="tdone__title" tabindex="-1" data-mode="handoff">{e(f["handoffT"])}</h3>
      <p data-mode="handoff">{e(f["handoffD"])} <strong data-who></strong>{sep}{e(f["handoffD2"])}</p>
      <div class="done__acts" data-mode="handoff">
        <a class="btn btn--primary" data-wa href="#" target="_blank" rel="noopener">{WA_ICON}{e(f["wa"])}</a>
        <a class="btn btn--outline" data-mail href="#">{e(f["email"])}</a>
      </div>
    </div>
  </section>"""


def visa_rule(c, passport, dest):
    """The merged rule (world data, corrections, core corridors) for one passport and destination."""
    if passport == dest:
        return {'type': 'home', 'note': 'home'}
    return c['visaFinal'].get(passport, {}).get(dest) or {'type': 'check', 'note': 'check'}


def visa_checker(c, lang):
    """Passport and visa check for every passport and destination. The page carries TGO's core
    corridor rules (with fees, lead times and business notes); the full world table loads as a
    cached asset. The table below the tool covers the main routes without JavaScript."""
    k = c['checker']
    t = c['travel']
    vr = c['visaRules']
    pnames = dict(k['passports'])
    dnames = {d['code']: d['name'] for d in t['destinations']}
    dests = [d for d in vr['destinations'] if d in dnames]
    core = {d: {p: r for p, r in per.items() if len(p) == 2} for d, per in vr['rules'].items()}
    payload = {
        'core': core, 'world': c['visaWorld'],
        'validity': vr['validityMonths'], 'beyondStay': vr['validityBeyondStay'], 'schengen': vr['schengen'],
        'labels': {x: k[x] for x in ('types', 'stay', 'fee', 'applyBy', 'passportCheck', 'days', 'stayVaries', 'noFee',
                                     'feeOnArrival', 'feeFrom', 'feeVaries', 'stayOpen', 'noApply', 'beforeFly', 'addDates', 'valid',
                                     'renew', 'validRule', 'validRuleStay', 'validRuleStay3', 'pages', 'checklist', 'plan',
                                     'guide', 'whatsapp', 'late', 'groupTop', 'groupAll', 'tripTo')},
        'notes': k['notes'], 'destNotes': k['destNotes'], 'docs': k['docs'],
        'destNames': dnames, 'featured': ['CN', 'PK', 'IN', 'BD', 'NP', 'PH', 'AE'],
        'guides': {g['code']: href(lang, 'guide', g['slug']) for g in t['guides']},
        'hosts': TRAVEL_HOSTS, 'lang': lang,
    }
    data = json.dumps(payload, ensure_ascii=False).replace('</', '<\\/')
    opt = lambda pairs: ''.join(f'<option value="{e(v)}">{e(n)}</option>' for v, n in pairs)
    passports = opt(k['passports'])  # replaced by every passport once the world table loads
    destopts = opt([(d, dnames[d]) for d in dests])
    purposes = opt(k['purposes'])
    # the same answers as a table, for scanning and for readers without JavaScript
    head = ''.join(f'<th scope="col">{e(dnames[d])}</th>' for d in dests)
    rows = ''
    for p in vr['passports']:
        cells = ''
        for d in dests:
            rule = visa_rule(c, p, d)
            stay = (' · ' + k['dayShort'].format(n=rule['stay'])) if rule.get('stay') and rule['type'] in ('free', 'voa') else ''
            cells += f'<td class="vt vt--{rule["type"]}">{e(k["short"][rule["type"]])}{e(stay)}</td>'
        rows += f'<tr><th scope="row">{e(pnames[p])}</th>{cells}</tr>'
    return f"""<section class="band" id="check">
    <div class="wrap sec">
      <header class="shead">{eyebrow(k["kicker"])}<h2 class="sech">{e(k["title"])}</h2><p class="lead" style="--mw:56ch">{e(k["sub"])}</p></header>
      <script type="application/json" data-checker-data>{data}</script>
      <form class="panel checker" data-checker>
        <div class="checker__fields">
          <div class="field"><label for="vc-passport">{e(k["passport"])}</label><select class="input" id="vc-passport" name="passport">{passports}</select></div>
          <div class="field"><label for="vc-dest">{e(k["dest"])}</label><select class="input" id="vc-dest" name="dest">{destopts}</select></div>
          <div class="field"><label for="vc-purpose">{e(k["purpose"])}</label><select class="input" id="vc-purpose" name="purpose">{purposes}</select></div>
          <div class="field"><label for="vc-arrive">{e(k["arrive"])}</label><input class="input" id="vc-arrive" name="arrive" type="date"></div>
          <div class="field"><label for="vc-leave">{e(k["leave"])}</label><input class="input" id="vc-leave" name="leave" type="date"></div>
          <div class="field"><label for="vc-expiry">{e(k["expiry"])}</label><input class="input" id="vc-expiry" name="expiry" type="date"></div>
        </div>
        <p class="estimator__hint">{e(k["optional"])}</p>
      </form>
      <noscript><p class="note">{e(k["noscript"])}</p></noscript>
      <div class="checker__result" data-checker-result aria-live="polite"></div>
      <div class="vtable-wrap">
        <p class="eyebrow vtable__kicker">{e(k["tableKicker"])}</p>
        <h3 class="vtable__title" id="vtable-title">{e(k["tableTitle"])}</h3>
        <div class="vtable-scroll" tabindex="0" role="region" aria-labelledby="vtable-title">
          <table class="vtable">
            <thead><tr><th scope="col">{e(k["tablePassport"])}</th>{head}</tr></thead>
            <tbody>{rows}</tbody>
          </table>
        </div>
      </div>
      <p class="note">{e(k["tableNote"])}</p>
    </div>
  </section>"""


def dest_card(c, lang, d):
    L = c['travel']['labels']
    facts = ''.join(f'<div><dt class="eyebrow">{e(k)}</dt><dd>{e(v)}</dd></div>'
                    for k, v in ((L['cities'], d['cities']), (L['best'], d['best']), (L['host'], d['host'])))
    links = []
    if d['guide']:
        links.append(f'<a class="btn btn--primary" href="{href(lang, "guide", d["guide"])}">{e(L["guide"])}</a>')
    if d['playbook']:
        links.append(f'<a class="btn btn--link" href="{href(lang, "playbook", d["playbook"])}">{e(L["playbook"])}</a>')
    if d['trip']:
        links.append(f'<a class="btn btn--link" href="{href(lang, "trip", d["trip"])}">{e(L["trip"])}</a>')
    return f"""
        <article class="panel dest{' dest--guide' if d['guide'] else ''}">
          <h3>{e(d["name"])}</h3>
          <dl class="dest__facts">{facts}</dl>
          <div class="dest__links">{''.join(links)}</div>
        </article>"""


def page_travel(c, lang):
    t = c['travel']
    who = ''.join(f'<div class="panel"><h3>{e(x["t"])}</h3><p>{e(x["d"])}</p></div>' for x in t['who'])
    formats = ''.join(
        f'<div class="panel offer"><p class="offer__n">{n + 1:02d}</p><h3>{e(x["t"])}</h3><p>{e(x["d"])}</p>'
        + (f'<a class="btn btn--link" href="{href(lang, x["link"])}">{e(t["tripsMore"])}</a>' if x.get('link') else '')
        + '</div>' for n, x in enumerate(t['formats']))
    services = ''.join(f'<div class="panel"><h3>{e(x["t"])}</h3><p>{e(x["d"])}</p></div>' for x in t['services'])
    dests = ''.join(dest_card(c, lang, d) for d in t['destinations'])
    how = ''.join(f'<li class="hstep"><span class="hstep__n">{n + 1:02d}</span><h3>{e(x["t"])}</h3><p>{e(x["d"])}</p></li>'
                  for n, x in enumerate(t['how']))
    trips = ''.join(trip_card(c, lang, x) for x in c['expeditions']['editions'][:4])
    help_cards = ''.join(f'''
      <a class="panel explore" href="{href(lang, x['link'])}{'#' + x['hash'] if x.get('hash') else ''}">
        <p class="cap__n">{n + 1:02d}</p>
        <h3>{e(x["t"])}</h3>
        <p>{e(x["d"])}</p>
        <span class="explore__arrow" aria-hidden="true">→</span>
      </a>''' for n, x in enumerate(t['help']))
    return f"""<main id="main" class="page page--travel">
  {phead(t["kicker"], t["title"], t["sub"], extra=f'<div class="actions actions--row"><a class="btn btn--primary" href="{href(lang, "packages")}">{e(t["packagesCta"])}</a><a class="btn btn--outline" href="#check">{e(c["checker"]["cta"])}</a><a class="btn btn--outline" href="#plan">{e(t["labels"]["plan"])}</a></div>')}

  <section class="wrap sec travel-help">
    <header class="shead">{eyebrow(t["helpKicker"])}<h2 class="sech">{e(t["helpTitle"])}</h2></header>
    <div class="grid grid--3">{help_cards}
    </div>
  </section>

  {visa_checker(c, lang)}

  <section class="wrap sec" id="destinations">
    <header class="shead">{eyebrow(t["destKicker"])}<h2 class="sech">{e(t["destTitle"])}</h2></header>
    <div class="grid grid--2 dests">{dests}
    </div>
  </section>

  <section class="band">
    <div class="wrap sec">
      <header class="shead">{eyebrow(t["whoKicker"])}<h2 class="sech">{e(t["whoTitle"])}</h2></header>
      <div class="grid grid--3">{who}</div>
    </div>
  </section>

  <section class="wrap sec">
    <header class="shead">{eyebrow(t["formatsKicker"])}<h2 class="sech">{e(t["formatsTitle"])}</h2></header>
    <div class="grid grid--3">{formats}</div>
  </section>

  <section class="band">
    <div class="wrap sec">
      <header class="shead">{eyebrow(t["servicesKicker"])}<h2 class="sech">{e(t["servicesTitle"])}</h2></header>
      <div class="grid grid--3">{services}</div>
    </div>
  </section>

  <section class="wrap sec">
    <header class="shead">{eyebrow(t["howKicker"])}<h2 class="sech">{e(t["howTitle"])}</h2></header>
    <ol class="hsteps">{how}</ol>
    <div class="actions"><a class="btn btn--link" href="{href(lang, 'booking')}">{e(t["bookingLink"])} →</a></div>
  </section>

  <section class="band">
    <div class="wrap sec">
      <header class="shead">{eyebrow(t["tripsKicker"])}<h2 class="sech">{e(t["tripsTitle"])}</h2></header>
      <div class="grid grid--2 svc-cards">{trips}
      </div>
      <div class="actions"><a class="btn btn--link" href="{href(lang, 'expeditions')}">{e(t["tripsMore"])}</a></div>
    </div>
  </section>

  {travel_form(c, lang)}
  {site_pager(c, lang, 'travel')}
</main>"""


def catalogue_card(c, lang, g, x):
    """A package in the catalogue: where, how long, the price, who it suits, what it
    includes, and two ways on — the destination guide and the guide's trip form."""
    P = c['travel']['packagesPage']
    return f'''
      <article class="panel pkg{" pkg--featured" if x.get("featured") else ""}">
        {eyebrow(g["name"] + " · " + x["len"])}
        <h3>{e(x["t"])}</h3>
        <p class="pkg__cities">{e(x["cities"])}</p>
        <p class="pkg__price">{e(x["price"])}<span>{e(x["priceNote"])}</span></p>
        <p class="pkg__best">{e(x["best"])}</p>{ticks(x["incl"])}
        <div class="pkg__acts">
          <a class="btn {"btn--primary" if x.get("featured") else "btn--outline"}" href="{href(lang, "guide", g["slug"])}#plan">{e(P["plan"])}</a>
          <a class="btn btn--link" href="{href(lang, "guide", g["slug"])}#packages">{e(P["guide"])}</a>
        </div>
      </article>'''


def travel_back(c, lang):
    return f'<section class="wrap brand-back"><a class="back-link" href="{href(lang, "travel")}">← {e(c["nav"]["travel"])}</a></section>'


def travel_pager(c, lang, key):
    """Packages → visas → booking, each ending on the next; the last goes back to travel."""
    t = c['travel']
    order = [('packages', t['packagesPage']['name']), ('visas', t['visasPage']['name']), ('booking', t['bookingPage']['name'])]
    i = [k for k, _ in order].index(key)
    prev = (href(lang, order[i - 1][0]), order[i - 1][1]) if i else (href(lang, 'travel'), c['nav']['travel'])
    nxt = (href(lang, order[i + 1][0]), order[i + 1][1]) if i + 1 < len(order) else (href(lang, 'expeditions'), c['nav']['expeditions'])
    return pager(c['ui']['continue'], prev, nxt, c['ui']['prev'], c['ui']['next'])


def page_packages(c, lang):
    t = c['travel']
    P = t['packagesPage']
    def group(kind):
        return ''.join(catalogue_card(c, lang, g, x)
                       for g in t['guides']
                       for x in next(s for s in g['sections'] if s['type'] == 'packages')['items'] if x['kind'] == kind)
    def block(key, sid, kind, band):
        b = P[key]
        inner = f'''<header class="shead">{eyebrow(b["kicker"])}<h2 class="sech">{e(b["title"])}</h2><p class="lead">{e(b["sub"])}</p></header>
      <div class="grid grid--2 pkgs">{group(kind)}
      </div>'''
        return (f'<section class="band" id="{sid}"><div class="wrap sec">{inner}</div></section>' if band
                else f'<section class="wrap sec" id="{sid}">{inner}</section>')
    v = P['visas']
    return f'''<main id="main" class="page page--packages">
  {travel_back(c, lang)}
  {phead(P["kicker"], P["title"], P["sub"])}
  {block("business", "business", "business", False)}
  {block("holiday", "holidays", "holiday", True)}
  <section class="wrap sec">
    <a class="panel explore travel-visas" href="{href(lang, "visas")}">
      {eyebrow(v["kicker"])}
      <h3>{e(v["title"])}</h3>
      <p>{e(v["d"])}</p>
      <span class="explore__arrow" aria-hidden="true">→</span>
    </a>
    <p class="note">{e(P["dated"])} <a href="{href(lang, "expeditions")}">{e(P["datedCta"])}</a></p>
  </section>
  {travel_pager(c, lang, "packages")}
</main>'''


def page_visas(c, lang):
    t = c['travel']
    V = t['visasPage']
    services = ''.join(f'<div class="panel"><h3>{e(x["t"])}</h3><p>{e(x["d"])}</p></div>' for x in V['services'])
    steps = ''.join(f'<li class="hstep"><span class="hstep__n">{n + 1:02d}</span><h3>{e(x["t"])}</h3><p>{e(x["d"])}</p></li>'
                    for n, x in enumerate(V['steps']))
    faq = ''.join(f'<details class="faq__item"><summary>{e(x["q"])}</summary><p>{e(x["a"])}</p></details>' for x in V['faq'])
    half = lambda title, items, k: (f'<div class="panel fit"><h3>{e(title)}</h3><ul class="ticks ticks--{k}">'
                                    + ''.join(f'<li>{e(x)}</li>' for x in items) + '</ul></div>')
    return f'''<main id="main" class="page page--visas">
  {travel_back(c, lang)}
  {phead(V["kicker"], V["title"], V["sub"], extra=f'<div class="actions actions--row"><a class="btn btn--primary" href="{href(lang, "travel")}#check">{e(c["checker"]["cta"])}</a><a class="btn btn--outline" href="{href(lang, "travel")}#plan">{e(t["labels"]["plan"])}</a></div>')}
  <section class="band"><div class="wrap sec">
    <header class="shead">{eyebrow(V["servicesKicker"])}<h2 class="sech">{e(V["servicesTitle"])}</h2></header>
    <div class="grid grid--3">{services}</div>
  </div></section>
  <section class="wrap sec">
    <header class="shead">{eyebrow(V["stepsKicker"])}<h2 class="sech">{e(V["stepsTitle"])}</h2></header>
    <ol class="hsteps hsteps--6">{steps}</ol>
  </section>
  <section class="band"><div class="wrap sec">
    <header class="shead">{eyebrow(V["feesKicker"])}<h2 class="sech">{e(V["feesTitle"])}</h2></header>
    <div class="grid grid--2">{half(V["feesTitle"], V["fees"], "yes")}{half(V["limitsTitle"], V["limits"], "no")}</div>
  </div></section>
  <section class="wrap sec">
    <header class="shead">{eyebrow(V["faqKicker"])}<h2 class="sech">{e(V["faqTitle"])}</h2></header>
    <div class="faq">{faq}</div>
  </section>
  {travel_pager(c, lang, "visas")}
</main>'''


def page_booking(c, lang):
    t = c['travel']
    B = t['bookingPage']
    steps = ''.join(f'<li class="hstep"><span class="hstep__n">{n + 1:02d}</span><h3>{e(x["t"])}</h3><p>{e(x["d"])}</p></li>'
                    for n, x in enumerate(B['steps']))
    def block(b):
        if isinstance(b, list):
            return '<ul class="legal__list">' + ''.join(f'<li>{linked(x)}</li>' for x in b) + '</ul>'
        return f'<p>{linked(b)}</p>'
    terms = ''.join(f'''
    <section class="legal__sec" id="{s["id"]}">
      <h2>{e(s["h"])}</h2>
      {''.join(block(b) for b in s["body"])}
    </section>''' for s in B['terms'])
    return f'''<main id="main" class="page page--booking">
  {travel_back(c, lang)}
  {phead(B["kicker"], B["title"], B["sub"])}
  <section class="band"><div class="wrap sec">
    <header class="shead">{eyebrow(B["stepsKicker"])}<h2 class="sech">{e(B["stepsTitle"])}</h2></header>
    <ol class="hsteps hsteps--7">{steps}</ol>
  </div></section>
  <div class="wrap legal">
    <header class="shead">{eyebrow(B["termsKicker"])}<h2 class="sech">{e(B["termsTitle"])}</h2></header>{terms}
    <p class="legal__other">{e(B["note"])} <a href="{href(lang, "terms")}">{e(B["termsLink"])}</a>{"" if lang == "zh" else "."}{"共同适用。" if lang == "zh" else ""}</p>
  </div>
  {travel_pager(c, lang, "booking")}
</main>'''


def guide_section(c, lang, g, sec):
    """One section of a destination guide. Each guide is a list of typed sections, so a
    country can carry what matters there: entry rules, islands, a fair calendar, packages."""
    t = c['travel']
    L = t['labels']
    kind = sec['type']
    if kind == 'cards':
        cls = 'grid grid--2 svc-cards' if sec.get('cols', 3) == 2 else 'grid grid--3'
        body = f'<div class="{cls}">' + ''.join(
            (f'<div class="panel isle">{eyebrow(x["e"])}<h3>{e(x["t"])}</h3><p>{e(x["d"])}</p></div>' if x.get('e')
             else f'<div class="panel"><h3>{e(x["t"])}</h3><p>{e(x["d"])}</p></div>')
            for x in sec['items']) + '</div>'
    elif kind == 'ticks':
        body = f'<div class="panel guide-tips">{ticks(sec["items"])}</div>'
    elif kind == 'plans':
        body = '<div class="grid grid--3 plans">' + ''.join(
            f'<div class="panel plan">{eyebrow(x["len"])}<h3>{e(x["t"])}</h3><ol class="plan__days">'
            + ''.join(f'<li><span>{e(L["day"].format(n=n + 1))}</span>{e(day)}</li>' for n, day in enumerate(x['days']))
            + '</ol></div>' for x in sec['items']) + '</div>'
    elif kind == 'phases':
        body = '<div class="grid grid--3 phases">' + ''.join(
            f'<div class="panel phase">{eyebrow(x["n"])}<h3>{e(x["t"])}</h3><p>{e(x["d"])}</p><dl class="phase__dates">'
            + ''.join(f'<div><dt>{e(k)}</dt><dd>{e(v)}</dd></div>' for k, v in x['dates'])
            + '</dl></div>' for x in sec['items']) + '</div>'
    elif kind == 'packages':
        body = '<div class="grid grid--2 pkgs">' + ''.join(
            f'<article class="panel pkg{" pkg--featured" if x.get("featured") else ""}">{eyebrow(x["len"])}'
            f'<h3>{e(x["t"])}</h3><p class="pkg__cities">{e(x["cities"])}</p>'
            f'<p class="pkg__price">{e(x["price"])}<span>{e(x["priceNote"])}</span></p>'
            f'<p class="pkg__best">{e(x["best"])}</p>{ticks(x["incl"])}'
            f'<a class="btn {"btn--primary" if x.get("featured") else "btn--outline"}" href="#plan">{e(L["plan"])}</a></article>'
            for x in sec['items']) + '</div>'
    elif kind == 'split':
        half = lambda b, k: (f'<div class="panel fit"><h3>{e(b["t"])}</h3><ul class="ticks ticks--{k}">'
                             + ''.join(f'<li>{e(x)}</li>' for x in b['items']) + '</ul></div>')
        body = f'<div class="grid grid--2">{half(sec["a"], "yes")}{half(sec["b"], "no")}</div>'
    elif kind == 'faq':
        body = '<div class="faq">' + ''.join(
            f'<details class="faq__item"><summary>{e(x["q"])}</summary><p>{e(x["a"])}</p></details>' for x in sec['items']) + '</div>'
    elif kind == 'trip':
        eds = c['expeditions']['editions']
        x = next(ed for ed in eds if ed['slug'] == sec['slug'])
        day = c['expeditions']['labels']['day']
        days = ''.join(
            f'<li class="day"><p class="day__n">{e(day.format(n=n + 1))}</p><div><h3>{e(city)}</h3><p>{e(what)}</p></div></li>'
            for n, (city, what) in enumerate(x['days']))
        body = (f'<ol class="itinerary">{days}</ol>'
                f'<div class="actions"><a class="btn btn--outline" href="{href(lang, "trip", x["slug"])}">{e(c["expeditions"]["labels"]["apply"])}</a></div>')
    elif kind == 'desk':
        d = next(x for x in t['destinations'] if x['code'] == g['code'])
        person = next((p for p in c['founders']['people'] if p['name'].split()[0] == d['host']), None)
        host = f"""<div class="panel host">
          {face(c, d['host'])}
          {eyebrow(L["host"])}
          <h3>{e(person['name'] if person else d['host'])}</h3>
          <p>{e(g["hostNote"])}</p>
          <a class="wa-link" href="https://wa.me/{WHATSAPP[d['host']]}" target="_blank" rel="noopener">WhatsApp {e(d["host"])}{WA_ICON}</a>
        </div>"""
        body = f'<div class="grid grid--2 desk"><div class="panel">{ticks(sec["items"])}</div>{host}</div>'
    else:
        raise ValueError(f'unknown guide section type: {kind}')
    note = sec.get('note', '')
    if sec.get('checked'):
        note = f'{note} {L["checked"]}.'
    note_html = f'\n    <p class="note">{e(note)}</p>' if note else ''
    return f"""<header class="shead">{eyebrow(sec["kicker"])}<h2 class="sech">{e(sec["title"])}</h2></header>
    {body}{note_html}"""


def page_guide(c, lang, i):
    t = c['travel']
    L = t['labels']
    g = t['guides'][i]
    d = next(x for x in t['destinations'] if x['code'] == g['code'])
    facts = ''.join(f'<div class="fact">{eyebrow(k)}<p class="fact__v">{e(v)}</p></div>' for k, v in g['facts'])
    sections = ''
    for n, sec in enumerate(g['sections']):
        inner = guide_section(c, lang, g, sec)
        # sections alternate between a white band and the grey ground, starting with a band
        sid = f' id="{sec["id"]}"' if sec.get('id') else ''
        sections += (f'\n  <section class="band"{sid}>\n    <div class="wrap sec">\n    {inner}\n    </div>\n  </section>\n' if n % 2 == 0
                     else f'\n  <section class="wrap sec"{sid}>\n    {inner}\n  </section>\n')
    form = travel_form(c, lang, g['code'])
    form = f'<div class="band">{form}</div>' if len(g['sections']) % 2 == 0 else form
    book = (f'<a class="btn btn--outline" href="{href(lang, "playbook", d["playbook"])}">{e(L["playbook"])}</a>'
            if d['playbook'] else '')
    eds = c['expeditions']['editions']
    trip = next((x for x in eds if x['slug'] == d['trip']), None)
    prev = (href(lang, 'travel') + '#destinations', L['all'])
    # the next card is the destination's dated trip, else its playbook, else the expeditions list
    nxt = ((href(lang, 'trip', trip['slug']), trip['title']) if trip
           else (href(lang, 'playbook', d['playbook']), L['playbook']) if d['playbook']
           else (href(lang, 'expeditions'), c['nav']['expeditions']))
    return f"""<main id="main" class="page page--guide">
  <section class="wrap brand-back"><a class="back-link" href="{href(lang, 'travel')}#destinations">← {e(L["all"])}</a></section>
  <section class="wrap svc-hero">
    {eyebrow(g["kicker"])}
    <h1 class="disp">{e(g["title"])}</h1>
    <p class="lead" style="--mw:52ch">{e(g["sub"])}</p>
    <div class="svc-facts guide-facts">{facts}</div>
    <div class="actions actions--row">
      <a class="btn btn--primary" href="#plan">{e(g["cta"])}</a>
      <a class="btn btn--outline" href="{href(lang, 'travel')}?to={g['code']}#check">{e(c["checker"]["cta"])}</a>
      {book}
    </div>
  </section>
{sections}
  {form}
  <section class="wrap"><p class="note">{e(g["note"])}</p></section>
  {pager(c['ui']['continue'], prev, nxt, c['ui']['prev'], c['ui']['next'])}
</main>"""


# ── partner portal preview ────────────────────────────────────────────────

def privacy_note(c, lang):
    """The collection notice under a form's send button, linked to the privacy notice."""
    u = c['ui']
    return f'<p class="form-note">{e(u["privacyNote"])} <a href="{href(lang, "privacy")}">{e(u["privacyLink"])}</a></p>'


EMAIL_RE = re.compile(r'[\w.+-]+@[\w-]+(?:\.[\w-]+)+')


def linked(text):
    """Escaped text with any email address turned into a mailto link."""
    return EMAIL_RE.sub(lambda m: f'<a href="mailto:{m.group(0)}">{m.group(0)}</a>', e(text))


def page_legal(c, lang, key):
    d = c[key]
    other = 'terms' if key == 'privacy' else 'privacy'
    toc = ''.join(f'<li><a href="#{s["id"]}">{e(s["h"])}</a></li>' for s in d['sections'])

    def block(b):
        if isinstance(b, list):
            return '<ul class="legal__list">' + ''.join(f'<li>{linked(x)}</li>' for x in b) + '</ul>'
        return f'<p>{linked(b)}</p>'
    sections = ''.join(f'''
    <section class="legal__sec" id="{s["id"]}">
      <h2>{e(s["h"])}</h2>
      {''.join(block(b) for b in s["body"])}
    </section>''' for s in d['sections'])
    return f'''<main id="main" class="page page--legal">
  {phead(d["kicker"], d["title"], d["sub"])}
  <div class="wrap legal">
    <p class="legal__updated">{e(d["updated"])}</p>
    <nav class="panel legal__toc" aria-label="{e(d["tocLabel"])}">
      <p class="eyebrow">{e(d["tocLabel"])}</p>
      <ol>{toc}</ol>
    </nav>{sections}
    <p class="legal__other"><a class="btn btn--link" href="{href(lang, other)}">{e(c[other]["name"])} →</a></p>
  </div>
</main>'''


def page_sitemap(c, lang):
    """Every page on the site, grouped as the footer groups them, with every article listed."""
    m = c['sitemap']

    def group(title, head, parts, wide):
        h = f'<a href="{head}">{e(title)}</a>' if head else e(title)
        lists = ''.join(
            (f'<h3 class="smap__sub">{e(sub)}</h3>' if sub else '')
            + '<ul class="smap__list">' + ''.join(f'<li><a href="{u}">{e(label)}</a></li>' for u, label in items) + '</ul>'
            for sub, items in parts)
        return f"""
    <section class="panel smap__group{' smap__group--wide' if wide else ''}">
      <h2 class="smap__h">{h}</h2>{lists}
    </section>"""
    return f'''<main id="main" class="page page--sitemap">
  {phead(m["kicker"], m["title"], m["sub"])}
  <div class="wrap smap">{''.join(group(*g) for g in site_groups(c, lang, full=True))}
  </div>
</main>'''


def page_portal(c, lang):
    p = c['portal']
    tabs = p['tabs']
    def stage_attrs(n):
        if n == p['stageNow']:
            return 'class="pstage is-now" aria-current="step"'
        return 'class="pstage is-done"' if n < p['stageNow'] else 'class="pstage"'
    stages = ''.join(
        f'<li {stage_attrs(n)}>'
        f'<span class="pstage__n">{e(st["n"])}</span><span class="pstage__t">{e(st["name"])}</span></li>'
        for n, st in enumerate(c['launch']['stages']))
    stats = ''.join(f'<div class="fact">{eyebrow(k)}<p class="fact__v">{e(v)}</p></div>' for k, v in p['stats'])
    feedback = ''.join(f'<blockquote class="quote"><p>“{e(q)}”</p><footer>{e(who)}</footer></blockquote>' for who, q in p['feedback'])
    approvals = ''.join(f'''
          <div class="clock">
            <div class="clock__head"><h3>{e(name)}</h3><span class="badge badge--{'share' if cur >= tot else 'retainer'}">{e(status)}</span></div>
            <p class="clock__meta">{e(market)} · {e(p["week"])} {cur} {e(p["of"])} {tot}</p>
            <div class="bar"><div style="width:{round(cur / tot * 100)}%"></div></div>
          </div>''' for name, market, status, cur, tot in p['approvals'])
    shipments = ''.join(f'<tr><th scope="row">{e(ref)}</th><td>{e(what)}</td><td><span class="badge badge--{"share" if st == "done" else "fixed"}">{e(status)}</span></td></tr>'
                        for ref, what, status, st in p['shipments'])
    sales = ''.join(f'<div class="sale"><p class="sale__city">{e(city)}</p><div class="bar"><div style="width:{pct}%"></div></div><p class="sale__pct">{pct}%</p></div>'
                    for city, pct in p['sales'])
    docs = ''.join(f'<li class="doc"><span class="doc__icon" aria-hidden="true">PDF</span><span class="doc__t">{e(t)}</span><span class="badge badge--fixed">{e(s)}</span></li>'
                   for t, s in p['documents'])
    msgs = ''.join(f'<li class="msg{" msg--me" if n % 2 else ""}"><p class="msg__who">{e(who)}</p><p>{e(text)}</p></li>'
                   for n, (who, text) in enumerate(p['messages']))
    panels = [
        ('overview', f'''<div class="svc-facts">{stats}</div>
          <div class="next">{eyebrow(p["nextLabel"])}<p>{e(p["next"])}</p></div>
          <h3 class="portal__h">{e(p["feedbackTitle"])}</h3><div class="quotes">{feedback}</div>'''),
        ('approvals', f'<h3 class="portal__h">{e(p["approvalsTitle"])}</h3>{approvals}'),
        ('shipments', f'''<h3 class="portal__h">{e(p["shipmentsTitle"])}</h3>
          <table class="table table--spec"><tbody>{shipments}</tbody></table>'''),
        ('sales', f'<h3 class="portal__h">{e(p["salesTitle"])}</h3><div class="sales">{sales}</div><p class="note">{e(p["salesNote"])}</p>'),
        ('documents', f'<h3 class="portal__h">{e(p["documentsTitle"])}</h3><ul class="docs">{docs}</ul>'),
        ('messages', f'<h3 class="portal__h">{e(p["messagesTitle"])}</h3><ul class="msgs">{msgs}</ul>'),
    ]
    tablist = ''.join(f'<button class="tab" type="button" role="tab" id="tab-{k}" aria-controls="pane-{k}" aria-selected="{"true" if n == 0 else "false"}">{e(tabs[k])}</button>'
                      for n, (k, _) in enumerate(panels))
    panes = ''.join(f'\n        <section class="pane" id="pane-{k}" role="tabpanel" aria-labelledby="tab-{k}"><h2 class="pane__title">{e(tabs[k])}</h2>{body}</section>'
                    for k, body in panels)
    return f'''<main id="main" class="page page--portal">
  {phead(p["kicker"], p["title"], p["sub"])}

  <section class="wrap portal-wrap">
    <div class="portal" data-tabs>
      <div class="portal__top">
        <div><p class="demo-badge">{e(p["demo"])}</p><h2 class="portal__company">{e(p["company"])}</h2><p class="portal__note">{e(p["companyNote"])}</p></div>
        <div>{eyebrow(p["stageLabel"])}<p class="portal__stage">{e(c["launch"]["stages"][p["stageNow"]]["n"])} · {e(c["launch"]["stages"][p["stageNow"]]["name"])}</p></div>
      </div>
      <ol class="pstages">{stages}</ol>
      <div class="tabs" role="tablist" aria-label="{e(p["kicker"])}">{tablist}</div>
      <div class="panes">{panes}
      </div>
    </div>
  </section>

  <section class="poster">
    <div class="wrap sec">
      <h2 class="title disp">{e(p["title"])}</h2>
      <a class="btn btn--light" href="{href(lang, 'partner')}">{e(p["cta"])}</a>
    </div>
  </section>
  {pager(c['ui']['continue'], (href(lang, 'launch'), c['nav']['launch']), (href(lang, 'partner'), c['nav']['partner']), c['ui']['prev'], c['ui']['next'])}
</main>'''


PAGES = {
    'packages': page_packages,
    'visas': page_visas,
    'booking': page_booking,
    'privacy': lambda c, lang: page_legal(c, lang, 'privacy'),
    'terms': lambda c, lang: page_legal(c, lang, 'terms'),
    'sitemap': page_sitemap,
    'home': page_home,
    'what': page_what,
    'brands': page_brands,
    'founders': page_founders,
    'markets': page_markets,
    'insights': page_insights,
    'partner': page_partner,
    'contact': page_contact,
    'services': page_services,
    'launch': page_launch,
    'expeditions': page_expeditions,
    'travel': page_travel,
    'estimator': page_estimator,
    'portal': page_portal,
}


# ── document ──────────────────────────────────────────────────────────────

def keep_dots(html):
    """A no-break space before every ' · ' so a separator never starts a line."""
    return html.replace(' · ', '\u00a0· ')


def document(c, lang, page, body, path, alt_path, title, description, version, ld=None, noindex=False):
    m = c['meta']
    zh = lang == 'zh'
    en_path, zh_path = (alt_path, path) if zh else (path, alt_path)
    # an article still being written stays out of search until it has a body
    robots = '\n<meta name="robots" content="noindex">' if noindex else ''
    extra_ld = ''.join(f'\n<script type="application/ld+json">{x}</script>' for x in (ld or []))
    org = ('{"@context":"https://schema.org","@type":"Organization","name":"TGO Brands",'
           '"alternateName":"TGO优选","url":"' + SITE + '/",'
           '"description":"A lobby for entrepreneurs and businesses going into new markets, run by its three founders.",'
           '"areaServed":"Worldwide"}')
    return f'''<!doctype html>
<html lang="{'zh-CN' if zh else 'en'}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{e(title)}</title>
<meta name="description" content="{e(description)}">
<link rel="canonical" href="{SITE}{path}">
<link rel="alternate" hreflang="en" href="{SITE}{en_path}">
<link rel="alternate" hreflang="zh-CN" href="{SITE}{zh_path}">
<link rel="alternate" hreflang="x-default" href="{SITE}{en_path}">
<meta name="theme-color" content="#ffffff" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#000000" media="(prefers-color-scheme: dark)">
<meta name="format-detection" content="telephone=no">
<meta property="og:type" content="{'article' if page == 'post' else 'website'}">
<meta property="og:site_name" content="TGO Brands">
<meta property="og:url" content="{SITE}{path}">
<meta property="og:title" content="{e(m['ogTitle'] if page == 'home' else title)}">
<meta property="og:description" content="{e(m['ogDescription'] if page == 'home' else description)}">
<meta property="og:image" content="{SITE}{PHOTO}">
<meta property="og:locale" content="{'zh_CN' if zh else 'en_US'}">
<meta property="og:locale:alternate" content="{'en_US' if zh else 'zh_CN'}">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">{robots}
<script>(function(){{var d=document.documentElement,s=null;try{{s=localStorage.getItem('tgo-theme')}}catch(e){{}}if(s!=='dark'&&s!=='light')s=window.matchMedia&&matchMedia('(prefers-color-scheme: dark)').matches?'dark':'light';d.setAttribute('data-theme',s);window.tgoFont=function(){{if(d.lang!=='en'||document.getElementById('tgo-font'))return;var l=document.createElement('link');l.id='tgo-font';l.rel='stylesheet';l.media='print';l.onload=function(){{l.media='all'}};l.href='{FONT_CSS}';document.head.appendChild(l)}};window.tgoFont()}})()</script>
<link rel="stylesheet" href="/assets/site.css?v={version}">
<script>document.documentElement.classList.add('js')</script>
<script src="/assets/site.js?v={version}" defer onerror="document.documentElement.classList.remove('js')"></script>
<script type="application/ld+json">{org}</script>{extra_ld}
</head>
<body data-page="{page}">
<a class="skip" href="#main">{e(c["ui"]["skip"])}</a>
{nav(c, lang, page, alt_path)}
{keep_dots(body)}
{keep_dots(footer(c, lang))}
</body>
</html>
'''
