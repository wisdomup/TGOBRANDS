"""POST /api/lead — a partner application from /partner/ or a travel enquiry from /travel/.

Delivers the lead twice: by email to the team (Resend) and on WhatsApp to the founder who
covers the applicant's market or destination (WhatsApp Cloud API). Each channel is on only when its
environment variables are set. With neither configured the function answers 503 and the
page falls back to the applicant sending the application themselves, so no lead is lost
while this is being set up. Standard library only, like the site build.

Environment (set in the Vercel project, never in the repo):
  RESEND_API_KEY        Resend API key (turns email on)
  LEAD_EMAIL_FROM       optional sender on a domain verified in Resend (default "TGO Brands <leads@tgobrands.com>")
  LEAD_EMAIL_TO         optional comma-separated inboxes for every lead (default help@tgobrands.com)
  WHATSAPP_TOKEN        WhatsApp Cloud API token (a permanent system-user token)
  WHATSAPP_PHONE_ID     phone-number ID of the sending WhatsApp Business number
  WHATSAPP_TEMPLATE     approved template name (default "new_lead"; see site/README.md)
  WHATSAPP_LANG         template language code (default "en")
  WHATSAPP_API_VERSION  Graph API version (default "v23.0")
"""
import json
import os
import re
import urllib.error
import urllib.request
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse

# Who covers which market, first match wins. Mirrors assignee() in site/static/site.js; the
# numbers are the founders' public WhatsApp numbers (WHATSAPP in site/templates.py). The
# recipient is always derived here, never taken from the request.
COVERS = [('PK', 'Umair'), ('IN', 'Aryan'), ('PH', 'Umer'), ('AE', 'Shamas'), ('CN', 'Umair')]
DEFAULT_LEAD = 'Umair'
WHATSAPP = {'Umer': '639772547666', 'Umair': '8615623305030', 'Aryan': '917645912074', 'Shamas': '971542971969'}

PARTY = {'manufacturer': 'Manufacturer', 'brand_owner': 'Brand owner', 'distributor': 'Distributor / retailer',
         'creator': 'Creator', 'investor': 'Investor', 'other': 'Other'}
MARKETS = {'PK': 'Pakistan', 'IN': 'India', 'PH': 'Philippines', 'AE': 'UAE', 'other': 'Other'}
DESTINATIONS = {'PK': 'Pakistan', 'IN': 'India', 'PH': 'Philippines', 'AE': 'UAE', 'CN': 'China'}
PURPOSE = {'business': 'Business meetings', 'fair': 'Trade fair or factory visits', 'group': 'Company or incentive group',
           'leisure': 'Holiday', 'mix': 'Business and holiday'}

LEAD_INBOX = 'help@tgobrands.com'
LEAD_SENDER = 'TGO Brands <leads@tgobrands.com>'

MAX_BODY = 32 * 1024
TEXT_FIELDS = {'contact_name': 120, 'company_name': 160, 'company_country': 80, 'contact_email': 200,
               'contact_phone': 40, 'handle': 120, 'message': 2000, 'service': 80, 'source': 200,
               'locale': 5, 'party_type': 40, 'travel_when': 80, 'travel_from': 120, 'purpose': 20, 'travellers': 10}
EMAIL = re.compile(r'^[^@\s]+@[^@\s]+\.[^@\s]+$')
KEY = re.compile(r'^[a-z_]{1,40}$')
NOT_ANSWERS = set(TEXT_FIELDS) | {'kind', 'target_markets', 'destinations', 'score', 'summary', 'website',
                                   'assigned_to', 'created_at'}
CONTROL = re.compile(r'[\x00-\x08\x0b-\x1f\x7f]')


def clean(value, limit, multiline=False):
    """A string from untrusted input: control characters dropped, length capped."""
    s = CONTROL.sub('', str(value if value is not None else ''))
    if not multiline:
        s = ' '.join(s.split())
    return s.strip()[:limit]


def one_line(s, limit=200):
    # WhatsApp template parameters may not contain newlines, tabs or runs of spaces
    return ' '.join(str(s).split())[:limit] or '-'


def assignee(markets):
    for code, who in COVERS:
        if code in markets:
            return who
    return DEFAULT_LEAD


def parse_lead(raw):
    """Validate the posted application. Returns (lead, error)."""
    if not isinstance(raw, dict):
        return None, 'expected a JSON object'
    lead = {k: clean(raw.get(k), n, multiline=(k == 'message')) for k, n in TEXT_FIELDS.items()}
    lead['kind'] = 'travel' if raw.get('kind') == 'travel' else 'partner'
    markets = raw.get('target_markets') or []
    lead['target_markets'] = [m for m in MARKETS if isinstance(markets, list) and m in markets]
    dests = raw.get('destinations') or []
    lead['destinations'] = [d for d in DESTINATIONS if isinstance(dests, list) and d in dests]
    if lead['kind'] == 'travel' and not lead['destinations']:
        return None, 'a destination is required'
    try:
        lead['score'] = max(0, min(90, int(raw.get('score') or 0)))
    except (TypeError, ValueError):
        lead['score'] = 0
    # the readable summary the page built from the questions this applicant saw
    lead['summary'] = clean(raw.get('summary'), 6000, multiline=True)
    if lead['contact_email'] and not EMAIL.match(lead['contact_email']):
        lead['contact_email'] = ''
    if not (lead['contact_email'] or lead['contact_phone'] or lead['handle']):
        return None, 'a way to reply is required'
    # the audience-specific answers (category, capacity, outlets, ticket size…), kept as given
    lead['answers'] = {}
    for k, v in raw.items():
        if k in NOT_ANSWERS or not KEY.match(k):
            continue
        if isinstance(v, list):
            lead['answers'][k] = [clean(x, 80) for x in v[:12] if isinstance(x, str)]
        elif isinstance(v, (str, int, float)) and not isinstance(v, bool):
            lead['answers'][k] = clean(v, 80)
    lead['assigned_to'] = assignee(lead['destinations'] if lead['kind'] == 'travel' else lead['target_markets'])
    lead['received_at'] = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')
    return lead, None


def post_json(url, payload, headers):
    """POST JSON and return (status, body). Never raises for HTTP errors."""
    req = urllib.request.Request(url, data=json.dumps(payload).encode(), method='POST', headers={
        'Content-Type': 'application/json', 'User-Agent': 'tgobrands-leads/1.0', **headers})
    try:
        with urllib.request.urlopen(req, timeout=8) as r:
            return r.status, r.read().decode('utf-8', 'replace')
    except urllib.error.HTTPError as err:
        return err.code, err.read().decode('utf-8', 'replace')
    except (urllib.error.URLError, OSError) as err:
        return 0, str(err)


def who_line(lead):
    name = lead['contact_name'] or 'Someone'
    return name + (f' ({lead["company_name"]})' if lead['company_name'] else '')


def contact_line(lead):
    return ' · '.join(x for x in (lead['contact_email'], lead['contact_phone'], lead['handle']) if x)


def kind_line(lead):
    if lead['kind'] == 'travel':
        return 'Travel enquiry'
    return PARTY.get(lead['party_type'], lead['party_type'] or '-')


def detail_line(lead):
    if lead['kind'] == 'travel':
        parts = [', '.join(DESTINATIONS[d] for d in lead['destinations']),
                 f'{lead["travellers"]} people' if lead['travellers'] else '',
                 lead['travel_when'], PURPOSE.get(lead['purpose'], '')]
        return ' · '.join(p for p in parts if p)
    markets = ', '.join(MARKETS[m] for m in lead['target_markets']) or '-'
    return f'Markets: {markets} · lead score {lead["score"]}/90'


def email_configured():
    return bool(os.environ.get('RESEND_API_KEY'))


def whatsapp_configured():
    return all(os.environ.get(k) for k in ('WHATSAPP_TOKEN', 'WHATSAPP_PHONE_ID'))


def send_email(lead):
    record = {k: v for k, v in lead.items() if k != 'summary'}
    body = '\n'.join([
        f'Routed to {lead["assigned_to"]} · received {lead["received_at"]}',
        f'{kind_line(lead)} · {detail_line(lead)}',
        f'Reply to: {contact_line(lead)}',
        '',
        lead['summary'] or '(no summary)',
        '',
        '-- record --',
        json.dumps(record, ensure_ascii=False, indent=2),
    ])
    payload = {
        'from': os.environ.get('LEAD_EMAIL_FROM') or LEAD_SENDER,
        'to': [a.strip() for a in (os.environ.get('LEAD_EMAIL_TO') or LEAD_INBOX).split(',') if a.strip()],
        'subject': one_line(f'New {"travel enquiry" if lead["kind"] == "travel" else "lead"} for '
                            f'{lead["assigned_to"]}: {who_line(lead)}', 180),
        'text': body,
    }
    if lead['contact_email']:
        payload['reply_to'] = lead['contact_email']
    status, text = post_json('https://api.resend.com/emails', payload,
                             {'Authorization': 'Bearer ' + os.environ['RESEND_API_KEY']})
    if not 200 <= status < 300:
        print(f'lead email failed: {status} {text[:300]}')
    return 200 <= status < 300


def send_whatsapp(lead):
    """Business-initiated messages must use an approved template; its five parameters are
    the founder, the applicant, what kind of lead it is, the details and how to reply."""
    params = [lead['assigned_to'], who_line(lead), kind_line(lead), detail_line(lead), contact_line(lead)]
    payload = {
        'messaging_product': 'whatsapp',
        'to': WHATSAPP[lead['assigned_to']],
        'type': 'template',
        'template': {
            'name': os.environ.get('WHATSAPP_TEMPLATE', 'new_lead'),
            'language': {'code': os.environ.get('WHATSAPP_LANG', 'en')},
            'components': [{'type': 'body', 'parameters': [{'type': 'text', 'text': one_line(p)} for p in params]}],
        },
    }
    url = 'https://graph.facebook.com/{}/{}/messages'.format(
        os.environ.get('WHATSAPP_API_VERSION', 'v23.0'), os.environ['WHATSAPP_PHONE_ID'])
    status, text = post_json(url, payload, {'Authorization': 'Bearer ' + os.environ['WHATSAPP_TOKEN']})
    if not 200 <= status < 300:
        print(f'lead whatsapp failed: {status} {text[:300]}')
    return 200 <= status < 300


def deliver(raw):
    """Handle one posted application. Returns (status, response body)."""
    if isinstance(raw, dict) and raw.get('website'):
        # the hidden honeypot field was filled in: a bot. Answer as if sent, send nothing.
        return 200, {'ok': True}
    lead, error = parse_lead(raw)
    if error:
        return 400, {'ok': False, 'error': error}
    channels = []
    if email_configured():
        channels.append(('email', send_email))
    if whatsapp_configured():
        channels.append(('whatsapp', send_whatsapp))
    if not channels:
        return 503, {'ok': False, 'error': 'lead delivery is not configured'}
    sent = {name: fn(lead) for name, fn in channels}
    if not any(sent.values()):
        return 502, {'ok': False, 'error': 'delivery failed', **sent}
    return 200, {'ok': True, 'assigned_to': lead['assigned_to'], **sent}


class handler(BaseHTTPRequestHandler):
    def _reply(self, status, body, extra=None):
        data = json.dumps(body).encode()
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Cache-Control', 'no-store')
        for k, v in (extra or {}).items():
            self.send_header(k, v)
        self.send_header('Content-Length', str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_POST(self):
        # same-origin only: the form posts from the site itself
        origin = self.headers.get('Origin')
        host = self.headers.get('X-Forwarded-Host') or self.headers.get('Host') or ''
        if origin and urlparse(origin).netloc != host:
            return self._reply(403, {'ok': False, 'error': 'cross-origin request'})
        try:
            length = int(self.headers.get('Content-Length') or 0)
        except ValueError:
            length = 0
        if length <= 0 or length > MAX_BODY:
            return self._reply(413 if length > MAX_BODY else 400, {'ok': False, 'error': 'bad request size'})
        try:
            raw = json.loads(self.rfile.read(length).decode('utf-8'))
        except (UnicodeDecodeError, json.JSONDecodeError):
            return self._reply(400, {'ok': False, 'error': 'invalid JSON'})
        status, body = deliver(raw)
        self._reply(status, body)

    def do_GET(self):
        self._reply(405, {'ok': False, 'error': 'POST only'}, {'Allow': 'POST'})

    def log_message(self, *args):
        pass  # no request logging: the requests carry personal data
