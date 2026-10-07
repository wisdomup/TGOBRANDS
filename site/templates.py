"""Page templates for the TGO Brands site.

Every function takes the locale's content dict (`c`, from content/<lang>.json)
and returns an HTML string. Markup is server-rendered in full: the JavaScript in
static/site.js only enhances it (nav state, reveal, the survey stepper, the
how-we-work dialog), so every page reads correctly with scripting off.
"""
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
}
NAV = ['what', 'brands', 'founders', 'markets', 'insights']

PHOTO = '/assets/photo.jpg'
WHATSAPP = {'Umer': '639772547666', 'Umair': '8615623305030', 'Aryan': '917645912074'}

WA_ICON = ('<svg class="wa" viewBox="0 0 24 24" aria-hidden="true"><path d="M12.04 2C6.58 2 2.13 6.45 2.13 11.91c0 1.75.46 3.45 1.32 4.95L2 22l5.25-1.38a9.9 9.9 0 0 0 4.79 1.22h.01c5.46 0 9.91-4.45 9.91-9.91 0-2.65-1.03-5.14-2.9-7.01A9.82 9.82 0 0 0 12.04 2m0 1.67a8.2 8.2 0 0 1 5.83 2.42 8.18 8.18 0 0 1 2.41 5.82c0 4.55-3.7 8.24-8.25 8.24a8.24 8.24 0 0 1-4.2-1.15l-.3-.18-3.12.82.83-3.04-.2-.31a8.22 8.22 0 0 1-1.26-4.4c0-4.55 3.7-8.22 8.26-8.22m-4.53 4.7c-.15 0-.4.06-.61.3-.21.24-.8.78-.8 1.9 0 1.12.82 2.2.93 2.35.12.15 1.6 2.5 3.9 3.44 1.9.78 2.3.63 2.71.6.42-.04 1.34-.55 1.53-1.08.19-.53.19-.98.13-1.08-.05-.1-.2-.16-.42-.27-.22-.11-1.34-.66-1.55-.74-.21-.08-.36-.11-.51.12-.15.22-.58.73-.71.88-.13.15-.26.16-.48.05-.22-.11-.94-.35-1.79-1.11-.66-.59-1.11-1.32-1.24-1.54-.13-.22-.01-.34.1-.45.1-.1.22-.26.33-.39.11-.13.15-.22.22-.37.07-.15.04-.28-.02-.39-.06-.11-.51-1.25-.71-1.71-.18-.44-.37-.38-.51-.39-.13-.01-.28-.01-.43-.01Z"/></svg>')


def e(s):
    return escape(str(s), quote=True)


def root(lang):
    return '/zh/' if lang == 'zh' else '/'


def href(lang, page, slug=None):
    path = f'brands/{slug}/' if page == 'brand' else PATHS[page]
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
SEQUENCE = ['home', 'what', 'brands', 'founders', 'markets', 'insights', 'partner']


def site_pager(c, lang, page):
    i = SEQUENCE.index(page)
    title = lambda k: c['ui']['home'] if k == 'home' else c['nav'][k]
    prev = (href(lang, SEQUENCE[i - 1]), title(SEQUENCE[i - 1])) if i > 0 else None
    nxt = (href(lang, SEQUENCE[i + 1]), title(SEQUENCE[i + 1])) if i + 1 < len(SEQUENCE) else None
    return pager(c['ui']['continue'], prev, nxt, c['ui']['prev'], c['ui']['next'])


def img(ratio='', cls='photo', eager=False):
    """Every photograph is the placeholder plate for now, printed in greyscale."""
    load = '' if eager else ' loading="lazy" decoding="async"'
    r = f' photo--{ratio}' if ratio else ''
    return f'<figure class="{cls}{r}"><img src="{PHOTO}" alt=""{load}></figure>'


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
          {img('4x3')}
          <div class="bcard__body">
            {eyebrow(b["cat"])}
            <h3>{e(b["name"])}</h3>
            <p class="bcard__pos">{e(b["pos"])}</p>
            {eyebrow(b["mk"] + " · " + b["st"], "bcard__meta")}
            <span class="bcard__link">{e(c["brands"]["detailKicker"])} →</span>
          </div>
        </a>'''


# ── chrome ────────────────────────────────────────────────────────────────

def nav(c, lang, page, alt_href):
    home = page == 'home'
    cur = {'brand': 'brands', 'post': 'insights'}.get(page, page)
    current = ' aria-current="page"'
    links = ''.join(
        f'<a href="{href(lang, k)}"{current if cur == k else ""}>{e(c["nav"][k])}</a>'
        for k in NAV)
    cta = f'{e(c["nav"]["partner"])}<span class="nav__arrow" aria-hidden="true">→</span>'
    other = 'en' if lang == 'zh' else 'zh-CN'
    return f'''<header class="nav" data-scrolled="0" data-hero="{1 if home else 0}" data-dark="{1 if home else 0}">
  <a class="nav__logo" href="{href(lang, 'home')}" aria-label="TGO Brands">TGO<span class="nav__word">Brands</span></a>
  <nav class="nav__links" id="site-menu" popover aria-label="{e(c["ui"]["menu"])}">
    {links}
    <a class="btn nav__cta nav__cta--drawer" href="{href(lang, 'partner')}">{cta}</a>
  </nav>
  <a class="nav__lang" href="{alt_href}" hreflang="{other}" lang="{other}" aria-label="{e(c["ui"]["langSwitchLabel"])}">{e(c["ui"]["langSwitch"])}</a>
  <a class="btn nav__cta" href="{href(lang, 'partner')}">{cta}</a>
  <button class="nav__burger" type="button" popovertarget="site-menu" aria-label="{e(c["ui"]["menu"])}"><span></span><span></span><span></span></button>
</header>'''


def footer(c, lang):
    f = c['footer']
    legal = ''.join(action(x, '', cls='footer__pending') for x in f['legal'])
    return f'''<footer class="footer">
  <div class="footer__in">
    <p>{e(f["tag"])}</p>
    <p>{e(f["note"])}</p>
    <div class="footer__links"><a href="{href(lang, 'contact')}">{e(c["nav"]["contact"])}</a>{legal}</div>
  </div>
</footer>'''


def how_dialog(c, lang):
    """The how-we-work sheet. Its triggers are real links to /what-we-do/#start,
    so without JavaScript they still land on the same content."""
    w = c['what']
    steps = ''.join(f'''
      <li class="how__step"><p class="how__n">{e(s["n"])}</p><div><h3>{e(s["t"])}</h3><p>{e(s["d"])}</p></div></li>''' for s in w['steps'])
    return f'''<dialog class="how" id="how" aria-labelledby="how-title">
  <div class="how__sheet">
    <button class="how__close" type="button" data-close aria-label="{e(c["ui"]["close"])}">✕</button>
    <p class="how__kicker">{e(c["home"]["cta2"])}</p>
    <h2 id="how-title">{e(w["startKicker"])}</h2>
    <p class="how__note">{e(w["startNote"])}</p>
    <ol class="how__steps">{steps}
    </ol>
    <div class="how__acts">
      <a class="btn btn--primary" href="{href(lang, 'partner')}">{e(c["home"]["cta"])}</a>
      <a class="btn btn--link" href="{href(lang, 'what')}">{e(c["nav"]["what"])}</a>
    </div>
  </div>
</dialog>'''


def stations(c, leads=True):
    items = ''
    for name, lead in zip(c['route']['stations'], c['route']['leads']):
        sub = f'<p class="eyebrow route__lead">{e(lead)}</p>' if leads else ''
        items += f'<li><span class="route__dot"></span><p class="route__name">{e(name)}</p>{sub}</li>'
    return f'<ol class="route__stations">{items}</ol>'


# ── home ──────────────────────────────────────────────────────────────────

def page_home(c, lang):
    h = c['home']
    hd = h['headings']
    route_line = ' → '.join([c['route']['origin']] + c['route']['stations'])
    how = href(lang, 'what') + '#start'

    names = ''.join(f'<span class="ticker__item">{e(n)}<span class="ticker__dot"></span></span>' for n in h['marquee'])
    names_dup = names.replace('<span class="ticker__item">', '<span class="ticker__item" aria-hidden="true">')

    premise = ''.join(f'<p>{e(p)}</p>' for p in h['premise'])
    figs = ''.join(f'''
        <div class="tile"><p class="tile__fig" data-fig="{e(f["n"])}">{e(f["n"])}</p><p class="tile__label">{e(f["l"])}</p></div>''' for f in h['proof'])

    pillars = ''.join(f'''
      <div class="panel pillar">
        <p class="pillar__n">{e(p["n"])}</p>
        <h3>{e(p["t"])}</h3>
        <div><p class="pillar__d">{e(p["d"])}</p><p class="pillar__who">{e(p["w"])}</p></div>
      </div>''' for p in c['what']['pillars'])

    bcards = ''.join(bcard(c, lang, b) for b in c['brands']['items'])

    fcards = ''.join(f'''
          <div class="fcard">
            {img('3x4')}
            <div class="fcard__body"><h3>{e(p["name"])}</h3>{eyebrow(p["city"])}<p>{e(p["role"])}</p></div>
          </div>''' for p in c['founders']['people'])

    posts = ''.join(f'''
        <a class="panel post" href="{href_post(lang, p['slug'])}">
          {eyebrow(p["d"] + " · " + p["c"])}
          <h3>{e(p["t"])}</h3>
          <p>{e(p["ex"])}</p>
        </a>''' for p in c['insights']['posts'][:3])

    step_cards = ''.join(f'''
            <article class="step-card"{dup}>
              {img('16x10')}
              <div>{eyebrow(s["n"])}<h3>{e(s["t"])}</h3><p>{e(s["d"])}</p></div>
            </article>''' for dup in ('', ' aria-hidden="true"', ' aria-hidden="true"', ' aria-hidden="true"') for s in c['what']['steps'])

    services = ''.join(f'''
          <div class="panel service"><h3>{e(s["n"])}</h3><p>{e(s["d"])}</p></div>''' for s in h['services'])

    explore = ''.join(f'''
          <a class="panel explore" href="{href(lang, x['page'])}">
            {eyebrow(x["k"])}
            <h3>{e(x["n"])}</h3>
            <p>{e(x["d"])}</p>
            <span class="explore__arrow" aria-hidden="true">→</span>
          </a>''' for x in h['explore'])

    gallery = ''.join(f'<figure class="gallery__item"><img src="{PHOTO}" alt="" loading="lazy" decoding="async"></figure>' for _ in range(24))

    return f'''<main id="main" class="page page--home">
  <section class="hero">
    <figure class="hero__media">
      <img src="{PHOTO}" alt="" fetchpriority="high">
      <video muted loop playsinline preload="none" disablepictureinpicture poster="{PHOTO}" data-src="/assets/hero.mp4" aria-hidden="true"></video>
    </figure>
    <div class="hero__shade"></div>
    <div class="hero__in">
      <p class="hero__eyebrow">{e(h["premiseKicker"])}</p>
      <h1 class="hero__title disp"><span>{e(h["h1a"])}</span> <span>{e(h["h1b"])}</span></h1>
      <p class="hero__sub">{e(h["sub"])}</p>
      <div class="hero__acts">
        <a class="btn btn--primary btn--lg" href="{href(lang, 'partner')}">{e(h["cta"])}</a>
        <a class="btn btn--glass btn--lg" href="{how}" data-open-how>{e(h["cta2"])}</a>
      </div>
      <p class="hero__route">{e(route_line)}</p>
    </div>
  </section>

  <section class="ticker" aria-label="{e(c["ui"]["brands"])}">
    <div class="marq">{names}{names_dup}{names_dup}{names_dup}</div>
  </section>

  <section class="wrap route" aria-label="{e(c["ui"]["route"])}">
    <div class="route__track">{stations(c)}</div>
  </section>

  <section class="wrap sec">
    <header class="shead">{eyebrow(h["premiseKicker"])}<h2 class="sech">{e(hd["premise"])}</h2></header>
    <div class="cols">{premise}</div>
  </section>

  <section class="band">
    <div class="wrap sec">
      <header class="shead">{eyebrow(h["proofKicker"])}<h2 class="sech">{e(hd["proof"])}</h2></header>
      <div class="figs" data-figs>{figs}
      </div>
      <p class="footnote">{e(h["proofNote"])}</p>
    </div>
  </section>

  <section class="wrap sec">
    <header class="shead">{eyebrow(h["doKicker"])}<h2 class="sech">{e(hd["pillars"])}</h2></header>
    {pillars}
    <div class="more"><a class="btn btn--link" href="{how}" data-open-how>{e(h["cta2"])}</a></div>
  </section>

  <section class="band">
    <div class="wrap sec">
      <header class="shead">{eyebrow(h["brandsKicker"])}<h2 class="sech">{e(hd["brands"])}</h2><p class="lead" style="--mw:52ch">{e(h["brandsNote"])}</p></header>
      <div class="bcards">{bcards}
      </div>
    </div>
  </section>

  <section class="band band--ruled">
    <div class="wrap sec">
      <header class="shead">{eyebrow(h["foundersKicker"])}<h2 class="sech">{e(hd["founders"])}</h2></header>
      <div class="trio">{fcards}
      </div>
      <div class="actions"><a class="btn btn--link" href="{href(lang, 'founders')}">{e(c["nav"]["founders"])}</a></div>
    </div>
  </section>

  <section class="wrap sec">
    <header class="shead">{eyebrow(h["routeKicker"])}<h2 class="sech">{e(hd["route"])}</h2><p class="lead">{e(h["routeNote"])}</p></header>
    <div class="grid grid--3">{posts}
    </div>
  </section>

  <section class="band hww" id="how-we-work" aria-label="{e(h["cta2"])}">
    <div class="wrap hww__head">
      <p class="eyebrow">{e(h["cta2"])}</p>
      <h2 class="title disp" style="--mw:24ch">{e(c["what"]["title"])}</h2>
      <p class="lead" style="--mw:52ch">{e(c["what"]["startNote"])}</p>
    </div>
    <div class="wrap hww__body">
      <div class="strip"><div class="marq">{step_cards}
      </div></div>
    </div>
  </section>

  <section class="band" aria-label="{e(c["ui"]["services"])}">
    <div class="wrap sec">
      <header class="shead shead--services">{eyebrow(h["servicesKicker"])}<h2 class="title" style="--mw:20ch">{e(h["servicesTitle"])}</h2><p class="lead" style="--mw:56ch">{e(h["servicesNote"])}</p></header>
      <div class="grid grid--2 services">{services}
      </div>
    </div>
  </section>

  <section aria-label="{e(c["ui"]["explore"])}">
    <div class="wrap sec">
      <header class="shead">{eyebrow(h["exploreKicker"])}<h2 class="title" style="--mw:18ch">{e(h["exploreTitle"])}</h2></header>
      <div class="grid grid--2">{explore}
      </div>
    </div>
  </section>

  <section class="gallery" aria-hidden="true">
    <div class="marq">{gallery}</div>
  </section>

  <section class="poster">
    <div class="wrap sec">
      <h2 class="title disp"><span>{e(h["closeA"])}</span> <span class="poster__dim">{e(h["closeB"])}</span></h2>
      <a class="btn btn--light" href="{href(lang, 'partner')}">{e(h["closeBtn"])}</a>
    </div>
  </section>
  {site_pager(c, lang, 'home')}
</main>
{how_dialog(c, lang)}'''


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
    pillars = ''.join(f'''
    <div class="pillar-row">
      <p class="pillar__n">{e(p["n"])}</p>
      <div><h2>{e(p["t"])}</h2><p class="pillar-row__who">{e(p["w"])}</p></div>
      <p class="pillar-row__d">{e(p["d"])}</p>
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
    return f'''<main id="main" class="page page--brand">
  <section class="wrap brand-back"><a class="back-link" href="{href(lang, 'brands')}">← {e(L["back"])}</a></section>
  <section class="wrap brand-hero">
    <div>
      {eyebrow(it["cat"])}
      <h1 class="disp">{e(it["name"])}</h1>
      <p class="lead" style="--mw:48ch">{e(it["pos"])}</p>
    </div>
    {img('4x3')}
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


def person(p, team=False):
    tags = ''.join(f'<span class="tag tag--outline">{e(v)}</span>' for v in p['v'])
    photo = '' if team else img('3x4')
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
    people = ''.join(person(p) for p in f['people'])
    team = ''.join(person(p, team=True) for p in f['team'])
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
    items = ''
    for it in m['items']:
        items += f'''
    <div class="market">
      <div class="market__head"><h2>{e(it["c"])}</h2>{eyebrow(L["lead"] + " — " + it["who"])}</div>
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
      {eyebrow(p["d"] + " · " + p["c"])}
      <h2>{e(p["t"])}</h2>
      <p class="post-row__ex">{e(p["ex"])}</p>
      {eyebrow(p["lang"])}
    </a>''' for p in shown)
    chips_html = f'\n    <nav class="chips" aria-label="{e(c["ui"]["filter"])}">{chips}</nav>'
    # YouTube on the English site; the 中文 site links out rather than embedding
    return f'''<main id="main" class="page page--insights">
  {phead(s["kicker"], s["title"], s["sub"], extra=chips_html)}

  <section class="wrap posts">{posts}{page_numbers(c, lang, slugs[cat], page_no, insights_pages(c, cat))}
  </section>

  <section class="band band--ruled">
    <div class="wrap sec channel">
      <div>
        {eyebrow(s["videoKicker"])}
        <h2 class="disp">{e(s["videoTitle"])}</h2>
        <p>{e(s["videoNote"])}</p>
        {action(s["videoBtn"], s.get("videoHref", ""))}
      </div>
      {img('16x9')}
    </div>
  </section>
  {site_pager(c, lang, 'insights')}
</main>'''


def page_post(c, lang, i):
    s = c['insights']
    posts = s['posts']
    p = posts[i]
    ui = c['ui']
    body = ''.join(f'<p>{e(x)}</p>' for x in p.get('body', [])) or f'<p class="post-body__soon">{e(ui["articleSoon"])}</p>'
    prev = (href_post(lang, posts[i - 1]['slug']), posts[i - 1]['t']) if i > 0 else None
    nxt = (href_post(lang, posts[i + 1]['slug']), posts[i + 1]['t']) if i + 1 < len(posts) else None
    return f'''<main id="main" class="page page--post">
  <section class="wrap post-head">
    <a class="back-link" href="{href_list(lang)}">← {e(ui["allInsights"])}</a>
    {eyebrow(p["d"] + " · " + p["c"])}
    <h1 class="disp">{e(p["t"])}</h1>
    <p class="lead" style="--mw:52ch">{e(p["ex"])}</p>
    {eyebrow(p["lang"], "post-head__lang")}
  </section>

  <section class="wrap post-body">
    {img('16x9')}
    {body}
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
        return f'''
        <div class="survey__nav">
          <button class="btn btn--link" type="button" data-back>{e(p["back"])}</button>
          {nxt}
        </div>'''

    steps = ''
    for i, q in enumerate(qs):
        kind = 'checkbox' if q.get('multi') else 'radio'
        opts = ''.join(
            f'<label class="opt"><input type="{kind}" name="{q["k"]}" value="{e(v)}"><span>{e(label)}</span></label>'
            for v, label in q['opts'])
        steps += f'''
      <div class="survey__step" id="q{i + 1}" role="group" aria-labelledby="q{i + 1}-t" data-step="{i}" data-key="{q["k"]}"{' data-multi' if q.get('multi') else ''}>{progress(i + 1)}
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
    return f'''<main id="main" class="page page--partner">
  <form class="survey" method="post" data-survey data-state="intro" data-endpoint="" data-lang="{lang}" novalidate>
    <section class="survey__intro" data-step="intro">
      {eyebrow(p["kicker"])}
      <h1 class="disp">{e(p["title"])}</h1>
      <p class="lead" style="--mw:52ch">{e(p["sub"])}</p>
      <a class="btn btn--primary" href="#q1" data-start>{e(p["start"])}</a>
    </section>
    <div class="survey__steps">{steps}
      <div class="survey__step" id="q{total}" role="group" aria-labelledby="q{total}-t" data-step="{len(qs)}">{progress(total)}
        <h2 class="display disp" id="q{total}-t">{e(ct["q"])}</h2>
        <p class="lead">{e(ct["h"])}</p>
        <div class="fields">{inputs}
        </div>
        <div class="field field--wide"><label for="f-message">{e(ct["message"])}</label><textarea class="input" id="f-message" name="message" rows="4"></textarea></div>{nav_row(last=True)}
      </div>
    </div>
  </form>

  <section class="done" data-done hidden>
    <div class="done__in">
      <span class="done__tick" aria-hidden="true"><svg viewBox="0 0 44 44" width="34" height="34" fill="none" stroke="currentColor" stroke-width="3.2" stroke-linecap="round" stroke-linejoin="round"><path d="M11 23.5 L19 31 L33 14"/></svg></span>
      {eyebrow(p["kicker"])}
      <h1 class="done__title" tabindex="-1">{e(d["t"])}</h1>
      <p class="done__sub">{e(d["d"])} <a class="wa-link" data-assignee-link href="#" target="_blank" rel="noopener"><span data-assignee></span>{WA_ICON}</a> — {e(d["d2"])}</p>
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


PAGES = {
    'home': page_home,
    'what': page_what,
    'brands': page_brands,
    'founders': page_founders,
    'markets': page_markets,
    'insights': page_insights,
    'partner': page_partner,
    'contact': page_contact,
}


# ── document ──────────────────────────────────────────────────────────────

def document(c, lang, page, body, path, alt_path, title, description, version, ld=None):
    m = c['meta']
    zh = lang == 'zh'
    en_path, zh_path = (alt_path, path) if zh else (path, alt_path)
    preload = f'\n<link rel="preload" as="image" href="{PHOTO}" fetchpriority="high">' if page == 'home' else ''
    extra_ld = ''.join(f'\n<script type="application/ld+json">{x}</script>' for x in (ld or []))
    org = ('{"@context":"https://schema.org","@type":"Organization","name":"TGO Brands",'
           '"alternateName":"TGO优选","url":"' + SITE + '/",'
           '"description":"Market entry, distribution and local company setup for Chinese brands in Pakistan, the Philippines, India and the UAE.",'
           '"areaServed":["PK","PH","IN","AE","CN"]}')
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
<meta name="theme-color" content="#1d1d1f">
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
<link rel="icon" href="/favicon.svg" type="image/svg+xml">{preload}
<link rel="stylesheet" href="/assets/site.css?v={version}">
<script>document.documentElement.classList.add('js')</script>
<script src="/assets/site.js?v={version}" defer onerror="document.documentElement.classList.remove('js')"></script>
<script type="application/ld+json">{org}</script>{extra_ld}
</head>
<body data-page="{page}">
<a class="skip" href="#main">{e(c["ui"]["skip"])}</a>
{nav(c, lang, page, alt_path)}
{body}
{footer(c, lang)}
</body>
</html>
'''
