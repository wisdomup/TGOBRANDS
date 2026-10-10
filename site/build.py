#!/usr/bin/env python3
"""Build the TGO Brands static site.

    python3 build.py              # writes ./dist
    python3 build.py --out DIR    # writes somewhere else

Standard library only. Every page is pre-rendered for both locales
(/ and /zh/), with clean directory URLs, a sitemap carrying hreflang pairs,
robots.txt and llms.txt. Deploy the output folder to any static host.
"""
import argparse
import csv
import hashlib
import json
import shutil
from pathlib import Path

import templates as T

ROOT = Path(__file__).resolve().parent
LANGS = ('en', 'zh')
# passport x destination base data (MIT, see data/passport-index/LICENSE); corrected by content/shared/visa_overrides.json
VISA_BASE = ROOT.parent / 'data' / 'passport-index' / 'passport-index-tidy-iso2.csv'
VISA_TYPES = {'visa free': 'free', 'visa on arrival': 'voa', 'e-visa': 'evisa', 'eta': 'eta',
              'visa required': 'visa', 'no admission': 'blocked'}
VISA_TOKEN = {'free': 'F', 'voa': 'A', 'evisa': 'E', 'eta': 'T', 'visa': 'V', 'blocked': 'B', 'home': 'H', 'check': 'C'}
GENERIC_NOTES = {'free', 'voa', 'evisa', 'eta', 'visa', 'blocked', 'check', 'home'}


def visa_world(content):
    """Every passport to every destination: the base dataset, then the government-checked
    overrides (later rules win), then TGO's core rules for its own corridors. Returns the sorted
    country codes and final[passport][destination] = {type, stay?, note?, core?}."""
    final = {}
    for row in csv.DictReader(VISA_BASE.open(encoding='utf-8')):
        p, d, v = row['Passport'], row['Destination'], row['Requirement'].strip().lower()
        if v == '-1':
            rule = {'type': 'home'}
        elif v.isdigit():
            rule = {'type': 'free', 'stay': int(v)}
        else:
            rule = {'type': VISA_TYPES.get(v, 'check')}
        final.setdefault(p, {})[d] = rule
    codes = sorted(final)
    for rule in content['visaOverrides']['rules']:
        d = rule['dest']
        for p in (codes if rule['passports'] == '*' else rule['passports']):
            if p == d or p not in final or p in rule.get('except', ()):
                continue
            cur = final[p].get(d, {'type': 'check'})
            if 'when' in rule and cur['type'] not in rule['when']:
                continue
            new = {'type': rule['type'], 'note': rule.get('note')}
            stay = cur.get('stay') if rule.get('keepStay') else rule.get('stay')
            if stay:
                new['stay'] = stay
            final[p][d] = new
    for d, per in content['visaRules']['rules'].items():
        for p, rule in per.items():
            if p in final:
                final[p][d] = dict(rule, core=True)
    return codes, final


def visa_asset(codes, final):
    """The world table as compact text for the browser: one row per passport, one token per
    destination (type letter + stay days), plus the few pair-specific note keys."""
    rows, notes = {}, {}
    for p in codes:
        toks = []
        for d in codes:
            r = final[p].get(d, {'type': 'check'})
            toks.append(VISA_TOKEN[r['type']] + (str(r['stay']) if r.get('stay') and r['type'] != 'home' else ''))
            if r.get('note') and r['note'] not in GENERIC_NOTES and not r.get('core'):
                notes[f'{p}>{d}'] = r['note']
        rows[p] = ','.join(toks)
    return json.dumps({'codes': codes, 'rows': rows, 'notes': notes}, separators=(',', ':'))


def load(lang):
    """content/<lang>.json plus every module in content/<lang>/ and the language-neutral
    data in content/shared/ (one top-level key per file)."""
    content = json.loads((ROOT / 'content' / f'{lang}.json').read_text(encoding='utf-8'))
    modules = sorted((ROOT / 'content' / lang).glob('*.json')) + sorted((ROOT / 'content' / 'shared').glob('*.json'))
    for f in modules:
        module = json.loads(f.read_text(encoding='utf-8'))
        clash = set(module) & set(content)
        if clash:
            raise SystemExit(f'{f}: keys {sorted(clash)} already defined elsewhere')
        content.update(module)
    return content


def routes(c):
    """Every page for one locale as (key, path under the locale root, title,
    description, render, structured data). Both locales produce the same paths."""
    suffix = c['meta']['suffix']
    out = [('home', '', c['meta']['title'], c['meta']['description'], T.page_home, None)]
    for key in ('what', 'services', 'launch', 'brands', 'founders', 'markets', 'partner', 'contact',
                'expeditions', 'travel', 'estimator', 'portal'):
        out.append((key, T.PATHS[key], f'{c["nav"][key]} — {suffix}', c[key]['sub'], T.PAGES[key], None))
    for key in ('privacy', 'terms', 'sitemap'):
        out.append((key, T.PATHS[key], f'{c[key]["name"]} — {suffix}', c[key]['sub'], T.PAGES[key], None))
    for key, page in (('packages', 'packagesPage'), ('visas', 'visasPage'), ('booking', 'bookingPage')):
        p = c['travel'][page]
        out.append((key, T.PATHS[key], f'{p["name"]} — {c["nav"]["travel"]} — {suffix}', p['sub'], T.PAGES[key], None))
    for i, x in enumerate(c['services']['items']):
        render = lambda c, lang, i=i: T.page_service(c, lang, i)
        out.append(('service', T.DETAIL['service'].format(x['slug']), f'{x["name"]} — {suffix}', x['one'], render, None))

    s = c['insights']
    for cat, (cat_name, cat_slug) in enumerate(zip(s['cats'], s['catSlugs'])):
        for n in range(1, T.insights_pages(c, cat) + 1):
            parts = [c['nav']['insights']] + ([cat_name] if cat else []) + ([c['ui']['pageN'].format(n=n)] if n > 1 else [])
            render = lambda c, lang, cat=cat, n=n: T.page_insights(c, lang, cat, n)
            out.append(('insights', T.list_path(cat_slug, n), ' — '.join(parts + [suffix]), s['sub'], render, None))
    for i, post in enumerate(s['posts']):
        render = lambda c, lang, i=i: T.page_post(c, lang, i)
        out.append(('post', f'insights/{post["slug"]}/', f'{post["t"]} — {suffix}', post['ex'], render, i))

    for i, x in enumerate(c['audiences']['items']):
        render = lambda c, lang, i=i: T.page_audience(c, lang, i)
        out.append(('audience', T.DETAIL['audience'].format(x['slug']), f'{x["name"]} — {suffix}', x['sub'], render, None))
    for i, x in enumerate(c['playbooks']['items']):
        name = c['markets']['items'][x['market']]['c']
        render = lambda c, lang, i=i: T.page_playbook(c, lang, i)
        out.append(('playbook', T.DETAIL['playbook'].format(x['slug']), f'{name} — {c["playbooks"]["kicker"]} — {suffix}',
                    c['markets']['items'][x['market']]['size'], render, None))
    for i, x in enumerate(c['expeditions']['editions']):
        render = lambda c, lang, i=i: T.page_trip(c, lang, i)
        out.append(('trip', T.DETAIL['trip'].format(x['slug']), f'{x["title"]} — {suffix}', x['one'], render, None))

    for i, g in enumerate(c['travel']['guides']):
        render = lambda c, lang, i=i: T.page_guide(c, lang, i)
        out.append(('guide', T.DETAIL['guide'].format(g['slug']), f'{g["name"]} — {c["travel"]["labels"]["guide"]} — {suffix}',
                    g['sub'], render, None))

    for i, brand in enumerate(c['brands']['items']):
        render = lambda c, lang, i=i: T.page_brand(c, lang, i)
        out.append(('brand', f'brands/{brand["slug"]}/', f'{brand["name"]} — {suffix}', brand['pos'], render, None))
    return out


def article_ld(c, lang, i, url):
    post = c['insights']['posts'][i]
    return json.dumps({
        '@context': 'https://schema.org', '@type': 'Article',
        'headline': post['t'], 'description': post['ex'], 'datePublished': post['d'],
        'inLanguage': 'zh-CN' if lang == 'zh' else 'en', 'url': url,
        'image': T.SITE + T.PHOTO,
        'publisher': {'@type': 'Organization', 'name': 'TGO Brands', 'url': T.SITE + '/'},
    }, ensure_ascii=False)


def write(out, url_path, html):
    target = out / url_path.lstrip('/') / 'index.html'
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(html, encoding='utf-8')


MARKER = '.tgo-build'


def build(out):
    if out.exists() and any(out.iterdir()):
        if not (out / MARKER).exists():
            raise SystemExit(f'{out} is not empty and is not a previous build; refusing to overwrite it')
        shutil.rmtree(out)
    assets = out / 'assets'
    assets.mkdir(parents=True)
    (out / MARKER).write_text('generated by build.py — safe to delete\n', encoding='utf-8')

    static = ROOT / 'static'
    for f in static.iterdir():
        if f.is_dir():
            shutil.copytree(f, assets / f.name)
        else:
            shutil.copy2(f, assets / f.name)
    version = hashlib.sha1(b''.join((static / n).read_bytes() for n in ('site.css', 'site.js'))).hexdigest()[:10]

    content = {lang: load(lang) for lang in LANGS}
    codes, final = visa_world(content['en'])
    world = visa_asset(codes, final)
    world_name = f'visa-{hashlib.sha1(world.encode()).hexdigest()[:10]}.json'
    (assets / world_name).write_text(world, encoding='utf-8')
    for lang in LANGS:
        content[lang]['visaFinal'] = final
        content[lang]['visaWorld'] = '/assets/' + world_name
    plans = {lang: routes(content[lang]) for lang in LANGS}
    paths = {lang: [r[1] for r in plans[lang]] for lang in LANGS}
    if paths['en'] != paths['zh']:
        raise SystemExit('en and zh content produce different pages; keep posts, categories and brands aligned')

    count = 0
    for lang in LANGS:
        c = content[lang]
        other = 'zh' if lang == 'en' else 'en'
        for key, rel, title, desc, render, post in plans[lang]:
            path, alt = T.root(lang) + rel, T.root(other) + rel
            # an article still being written is labelled on the page and kept out of search
            draft = key == 'post' and not T.written(c['insights']['posts'][post])
            ld = [article_ld(c, lang, post, T.SITE + path)] if key == 'post' and not draft else None
            write(out, path, T.document(c, lang, key, render(c, lang), path, alt, title, desc, version, ld, noindex=draft))
            count += 1
    drafts = {r[1] for r in plans['en'] if r[0] == 'post' and not T.written(content['en']['insights']['posts'][r[5]])}
    sitemap = [(T.root('en') + rel, T.root('zh') + rel) for rel in paths['en'] if rel not in drafts]

    urls = ''.join(
        f'''  <url><loc>{T.SITE}{p}</loc>
    <xhtml:link rel="alternate" hreflang="en" href="{T.SITE}{p}"/>
    <xhtml:link rel="alternate" hreflang="zh-CN" href="{T.SITE}{z}"/>
  </url>
  <url><loc>{T.SITE}{z}</loc>
    <xhtml:link rel="alternate" hreflang="en" href="{T.SITE}{p}"/>
    <xhtml:link rel="alternate" hreflang="zh-CN" href="{T.SITE}{z}"/>
  </url>
''' for p, z in sitemap)
    (out / 'sitemap.xml').write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
        f'{urls}</urlset>\n', encoding='utf-8')
    (out / 'robots.txt').write_text(f'User-agent: *\nAllow: /\n\nSitemap: {T.SITE}/sitemap.xml\n', encoding='utf-8')
    (out / 'llms.txt').write_text(llms(content['en']), encoding='utf-8')
    (out / 'favicon.svg').write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="14" fill="#1d1d1f"/>'
        '<text x="32" y="40" text-anchor="middle" font-family="-apple-system,Helvetica,Arial,sans-serif" font-weight="700" '
        'font-size="22" fill="#f5f5f7">TGO</text></svg>\n', encoding='utf-8')
    return count


def llms(c):
    """A plain-text summary for AI agents, built from the same English copy."""
    lines = [
        '# TGO Brands',
        '',
        '> TGO Brands Limited is a Hong Kong company run by its three founders: a lobby for entrepreneurs and '
        'business owners going into new markets. Market entry and certification, distribution, brand building, '
        'sourcing, market survey trips, and IT and systems (software, cloud, data, AI, security, ERP and CRM), '
        'with a travel agency for business trips, trade fairs, holidays, visas and documents.',
        '',
        c['home']['sub'],
        '',
        '## Pages',
        '',
    ]
    for key in ('what', 'services', 'launch', 'markets', 'travel', 'expeditions', 'estimator', 'brands', 'founders',
                'insights', 'partner', 'contact'):
        section = c[key]
        lines.append(f'- [{c["nav"][key]}]({T.SITE}{T.href("en", key)}): {section["sub"]}')
    for key, page in (('packages', 'packagesPage'), ('visas', 'visasPage'), ('booking', 'bookingPage')):
        p = c['travel'][page]
        lines.append(f'- [{p["name"]}]({T.SITE}{T.href("en", key)}): {p["sub"]}')
    for key in ('privacy', 'terms', 'sitemap'):
        lines.append(f'- [{c[key]["name"]}]({T.SITE}{T.href("en", key)}): {c[key]["sub"]}')
    lines += ['', '## Services', '']
    for x in c['services']['items']:
        lines.append(f'- [{x["name"]}]({T.SITE}{T.href("en", "service", x["slug"])}): {x["one"]}')
    lines += ['', '## Travel guides', '']
    for g in c['travel']['guides']:
        lines.append(f'- [{g["name"]}]({T.SITE}{T.href("en", "guide", g["slug"])}): {g["sub"]}')
    lines += ['', '## Brands', '']
    for b in c['brands']['items']:
        lines.append(f'- [{b["name"]}]({T.SITE}{T.href("en", "brand", b["slug"])}): {b["cat"]}. {b["pos"]}')
    lines += ['', '## Insights', '']
    for post in c['insights']['posts']:
        when = post['d'] if T.written(post) else 'coming soon'
        lines.append(f'- [{post["t"]}]({T.SITE}{T.href_post("en", post["slug"])}) ({when}): {post["ex"]}')
    lines += ['', '## Founders', '']
    for p in c['founders']['people']:
        lines.append(f'- {p["name"]} ({p["city"]}): {p["role"]}')
    lines += ['', '## Contact', '', '- hello@tgobrands.com', f'- Chinese site: {T.SITE}/zh/', '']
    return '\n'.join(lines)


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--out', default=str(ROOT / 'dist'), help='output directory (default: ./dist)')
    args = ap.parse_args()
    n = build(Path(args.out).resolve())
    print(f'built {n} pages into {args.out}')
