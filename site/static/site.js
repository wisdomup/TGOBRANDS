/* TGO Brands — progressive enhancement. Every page is complete without this
   file; it adds the capsule nav, scroll reveal, the proof-figure flicker, the
   how-we-work sheet, the insights filter, region-ordered contact channels and
   the one-question-per-screen partner survey. */
(function () {
  'use strict';

  var doc = document.documentElement;
  var reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var $ = function (sel, root) { return (root || document).querySelector(sel); };
  var $$ = function (sel, root) { return Array.prototype.slice.call((root || document).querySelectorAll(sel)); };

  /* ── Nav: merged with the page at the top, a capsule once scrolled ──
     Scale tracks scroll continuously over 0–320px and is written straight to
     custom properties, so nothing re-renders per frame. */
  function initNav() {
    var nav = $('.nav');
    if (!nav) return;
    var overHero = nav.getAttribute('data-hero') === '1';
    var raf = 0;
    function update() {
      raf = 0;
      var y = window.scrollY;
      var p = Math.min(1, Math.max(0, y / 320));
      var eased = p * p * (3 - 2 * p);
      doc.style.setProperty('--nav-scale', (1 - 0.14 * eased).toFixed(4));
      doc.style.setProperty('--nav-top', (22 - 10 * eased).toFixed(2) + 'px');
      nav.setAttribute('data-scrolled', y > 24 ? '1' : '0');
      if (overHero) nav.setAttribute('data-dark', y < window.innerHeight * 0.88 ? '1' : '0');
    }
    window.addEventListener('scroll', function () { if (!raf) raf = requestAnimationFrame(update); }, { passive: true });
    window.addEventListener('resize', function () { if (!raf) raf = requestAnimationFrame(update); });
    update();

    // a drawer left open while the window widens would float in the top layer
    var menu = $('#site-menu');
    var wide = window.matchMedia('(min-width: 861px)');
    if (menu && menu.hidePopover) {
      wide.addEventListener('change', function (e) {
        if (e.matches && menu.matches(':popover-open')) menu.hidePopover();
      });
    }
  }

  /* ── Hero video: streamed after first paint so the page is interactive first ── */
  function initHeroVideo() {
    var v = $('.hero video[data-src]');
    if (!v || reduced) return;
    var conn = navigator.connection;
    if (conn && conn.saveData) return;
    function start() {
      setTimeout(function () {
        v.muted = true;
        v.src = v.getAttribute('data-src');
        var p = v.play();
        if (p && p.catch) p.catch(function () {});
      }, 300);
    }
    if (document.readyState === 'complete') start();
    else window.addEventListener('load', start, { once: true });
  }

  /* ── Proof figures flicker through random values, then settle left to right ── */
  function flicker(figs) {
    if (reduced || !figs.length) return;
    var finals = figs.map(function (el) { return el.getAttribute('data-fig'); });
    var t0 = Date.now();
    var DUR = 1100;
    figs.forEach(function (el) { el.classList.add('is-settling'); });
    var timer = setInterval(function () {
      var p = Math.min(1, (Date.now() - t0) / DUR);
      figs.forEach(function (el, i) {
        if (p >= 0.55 + i * 0.11) { el.textContent = finals[i]; return; }
        el.textContent = finals[i].replace(/\d+/, function (d) {
          var max = Math.pow(10, d.length) - 1;
          return String(Math.max(1, Math.floor(Math.random() * max))).padStart(d.length, '0');
        });
      });
      if (p >= 1) {
        clearInterval(timer);
        figs.forEach(function (el, i) { el.textContent = finals[i]; el.classList.remove('is-settling'); });
      }
    }, 70);
  }

  /* ── Scroll reveal: must match the selector the stylesheet hides ── */
  var REVEAL = ':is(.page > section:not(.hero), .page .survey) :is(h1, h2, h3, p, article, figure, .figs):not(.marq *)';
  function initReveal() {
    var els = $$(REVEAL);
    if (!('IntersectionObserver' in window)) {
      els.forEach(function (el) { el.classList.add('is-in'); });
      return;
    }
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (!e.isIntersecting) return;
        e.target.classList.add('is-in');
        io.unobserve(e.target);
        if (e.target.hasAttribute('data-figs')) flicker($$('[data-fig]', e.target));
      });
    }, { rootMargin: '0px 0px -12% 0px', threshold: 0.08 });
    els.forEach(function (el) {
      var i = el.parentElement ? Array.prototype.indexOf.call(el.parentElement.children, el) : 0;
      el.style.transitionDelay = Math.min(i, 5) * 70 + 'ms';
      io.observe(el);
    });
  }

  /* ── How-we-work sheet; its triggers fall back to /what-we-do/#start ── */
  function initHow() {
    var dlg = $('#how');
    if (!dlg || !dlg.showModal) return;
    $$('[data-open-how]').forEach(function (a) {
      a.addEventListener('click', function (e) {
        e.preventDefault();
        dlg.showModal();
      });
    });
    dlg.addEventListener('click', function (e) {
      // a click on the scrim (the dialog box itself, outside the sheet) closes it
      if (e.target === dlg || e.target.closest('[data-close]')) dlg.close();
    });
  }

  /* ── Contact: the fastest channel for the chosen region goes first ── */
  var ORDER = { cn: ['wechat', 'email', 'whatsapp'], pk: ['whatsapp', 'email', 'wechat'], other: ['email', 'whatsapp', 'wechat'] };
  function initRegion() {
    var list = $('[data-channels]');
    var chips = $$('[data-region]');
    if (!list || !chips.length) return;
    chips.forEach(function (chip) {
      chip.addEventListener('click', function () {
        chips.forEach(function (c) { c.setAttribute('aria-pressed', String(c === chip)); });
        ORDER[chip.getAttribute('data-region')].forEach(function (k) {
          list.appendChild($('[data-channel="' + k + '"]', list));
        });
      });
    });
  }

  /* ── Where a visitor came from: first touch per session, for the lead ── */
  function initSource() {
    try {
      if (sessionStorage.getItem('tgo_src')) return;
      var q = new URLSearchParams(location.search);
      var tag = ['utm_source', 'utm_medium', 'utm_campaign'].map(function (k) { return q.get(k); }).filter(Boolean).join(' / ');
      var ref = document.referrer && new URL(document.referrer).host !== location.host ? new URL(document.referrer).host : '';
      if (tag || ref) sessionStorage.setItem('tgo_src', tag || ref);
    } catch (e) { /* storage unavailable: no source tag */ }
  }
  function source() {
    try { return sessionStorage.getItem('tgo_src') || ''; } catch (e) { return ''; }
  }

  /* ── Partner application ────────────────────────────────────────────── */
  var WHATSAPP = { Umer: '639772547666', Umair: '8615623305030', Aryan: '917645912074', Shamas: '971542971969' };
  var SCORES = {
    party_type: { manufacturer: 25, brand_owner: 22, distributor: 15, creator: 12, investor: 8, other: 5 },
    monthly_volume_band: { '<1k': 5, '1k-10k': 15, '10k-50k': 25, '50k+': 35, 'n/a': 5 },
    dist_outlets: { '1': 5, '2-10': 12, '11-50': 22, '50+': 30, online: 15 },
    creator_following: { '<100k': 5, '100k-500k': 15, '500k-1m': 25, '1m+': 35 },
    investor_ticket: { '<50k': 5, '50k-250k': 15, '250k-1m': 25, '1m+': 35 },
    timeline: { now: 30, '3_months': 22, '6_months': 12, exploring: 4 }
  };

  // routing: PK → Umair, IN → Aryan, PH → Umer, UAE → Shamas, otherwise Umair
  function assignee(lead) {
    var m = lead.target_markets || [];
    var order = [['PK', 'Umair'], ['IN', 'Aryan'], ['PH', 'Umer'], ['AE', 'Shamas']];
    for (var i = 0; i < order.length; i++) if (m.indexOf(order[i][0]) > -1) return order[i][1];
    return 'Umair';
  }
  function score(lead) {
    return Object.keys(SCORES).reduce(function (sum, k) { return sum + (SCORES[k][lead[k]] || 0); }, 0);
  }

  function initSurvey() {
    var form = $('[data-survey]');
    if (!form) return;
    var steps = $$('.survey__step', form);
    var done = $('[data-done]');
    var text = JSON.parse($('[data-survey-text]', form).textContent);
    var of = form.getAttribute('data-of') || 'of';
    var seq = steps.slice();
    var pos = -1;

    // a service page links here with ?service=<slug>; carry it into the lead
    var svc = new URLSearchParams(location.search).get('service');
    if (svc && text.services[svc]) {
      form.elements.service.value = svc;
      var note = $('[data-service-note]', form);
      $('strong', note).textContent = text.services[svc];
      note.hidden = false;
    }

    var as = new URLSearchParams(location.search).get('as');
    $$('input[name="party_type"]', form).forEach(function (r) { if (r.value === as) r.checked = true; });

    function party() {
      var c = $('input[name="party_type"]:checked', form);
      return c ? c.value : '';
    }
    // the steps this applicant sees: shared ones plus those for their audience
    // until the first answer, count steps as the most common path (manufacturer)
    function rebuild() {
      var p = party() || 'manufacturer';
      seq = steps.filter(function (s) {
        var f = s.getAttribute('data-for');
        return !f || f.split(' ').indexOf(p) > -1;
      });
    }
    function answered(step) {
      if (!step.hasAttribute('data-key')) return true;
      return !!$('input:checked', step);
    }
    function refresh(step) {
      var next = $('[data-next]', step);
      if (next) next.disabled = !answered(step);
    }
    function relabel(step) {
      var alt = step.getAttribute('data-alt');
      if (!alt) return;
      var h = $('.display', step);
      if (!h.hasAttribute('data-default')) h.setAttribute('data-default', h.textContent);
      h.textContent = JSON.parse(alt)[party()] || h.getAttribute('data-default');
    }
    function show(i) {
      pos = i;
      form.setAttribute('data-state', i < 0 ? 'intro' : 'steps');
      steps.forEach(function (s) { s.classList.remove('is-active'); });
      var target = $('.survey__intro h1', form);
      if (i >= 0) {
        var step = seq[i];
        step.classList.add('is-active');
        relabel(step);
        refresh(step);
        $('.step-count', step).textContent = (i + 1) + ' ' + of + ' ' + seq.length;
        $('.progress > div', step).style.width = Math.round((i + 1) / seq.length * 100) + '%';
        target = $('.display', step);
      }
      target.setAttribute('tabindex', '-1');
      target.focus({ preventScroll: true });
      window.scrollTo({ top: 0 });
    }
    function forward() {
      if (seq[pos] && seq[pos].getAttribute('data-key') === 'party_type') rebuild();
      show(pos + 1);
    }

    form.addEventListener('click', function (e) {
      if (e.target.closest('[data-start]')) { e.preventDefault(); rebuild(); show(0); return; }
      if (e.target.closest('[data-back]')) { show(pos - 1); return; }
      if (e.target.closest('[data-next]')) { if (answered(seq[pos])) forward(); return; }
      // a single-choice answer tapped or clicked moves straight on. The click
      // lands on the label first (the input is visually hidden); keyboard
      // users select on the input itself and confirm with Next.
      var opt = e.target.closest('.opt');
      if (opt && e.target.tagName !== 'INPUT' && $('input', opt).type === 'radio') {
        setTimeout(forward, 120);
      }
    });
    form.addEventListener('change', function () { if (pos >= 0) refresh(seq[pos]); });

    // the application as a readable message for WhatsApp or email
    function summary(lead) {
      var lines = [text.labels.msg, ''];
      seq.forEach(function (step) {
        var picked = $$('input:checked', step).map(function (i) { return i.nextElementSibling.textContent; });
        if (picked.length) lines.push(step.getAttribute('data-short') + ': ' + picked.join(', '));
      });
      lines.push('');
      $$('.field', form).forEach(function (f) {
        var input = $('.input', f);
        if (input.value.trim()) lines.push($('label', f).textContent + ': ' + input.value.trim());
      });
      if (lead.service) lines.push(text.labels.service + ': ' + text.services[lead.service]);
      lines.push(text.labels.score + ': ' + lead.score + ' / 90');
      if (lead.source) lines.push(text.labels.source + ': ' + lead.source);
      return lines.join('\n');
    }

    var submit = $('button[type="submit"]', form);
    var contactError = $('[data-contact-error]', form);
    var sending = false;

    function finish(lead, mode) {
      var who = lead.assigned_to;
      var msg = summary(lead);
      $$('[data-mode]', done).forEach(function (el) { el.hidden = el.getAttribute('data-mode') !== mode; });
      $$('[data-assignee]', done).forEach(function (el) { el.textContent = who; });
      $$('[data-assignee-link]', done).forEach(function (a) { a.href = 'https://wa.me/' + WHATSAPP[who]; });
      $('[data-wa]', done).href = 'https://wa.me/' + WHATSAPP[who] + '?text=' + encodeURIComponent(msg);
      $('[data-mail]', done).href = 'mailto:help@tgobrands.com?subject=' + encodeURIComponent(text.labels.subject) +
        '&body=' + encodeURIComponent(msg);
      $('[data-score]', done).textContent = lead.score;
      form.hidden = true;
      done.hidden = false;
      window.scrollTo({ top: 0 });
      $('.done__title:not([hidden])', done).focus({ preventScroll: true });
    }

    form.addEventListener('submit', function (e) {
      e.preventDefault();
      if (sending) return;
      var data = new FormData(form);
      // a lead the team cannot answer is no lead: ask for one way to reply
      var reachable = ['contact_email', 'contact_phone', 'handle'].some(function (k) { return (data.get(k) || '').trim(); });
      contactError.hidden = reachable;
      if (!reachable) { $('#f-contact_email', form).focus(); return; }

      var lead = {
        created_at: new Date().toISOString(),
        locale: form.getAttribute('data-lang'),
        service: data.get('service') || '',
        source: source(),
        website: data.get('website') || ''
      };
      // answers from the steps this applicant actually saw
      seq.forEach(function (step) {
        var k = step.getAttribute('data-key');
        if (!k) return;
        var vals = $$('input:checked', step).map(function (i) { return i.value; });
        lead[k] = step.hasAttribute('data-multi') ? vals : (vals[0] || '');
      });
      ['contact_name', 'company_name', 'company_country', 'contact_email', 'contact_phone', 'handle', 'message']
        .forEach(function (k) { lead[k] = data.get(k) || ''; });
      lead.score = score(lead);
      lead.assigned_to = assignee(lead);

      // the server delivers the lead by email and WhatsApp; if it is not set up, cannot be
      // reached or says no, the applicant sends it themselves — nothing is lost either way
      var endpoint = form.getAttribute('data-endpoint');
      if (!endpoint || !window.fetch) return finish(lead, 'handoff');
      sending = true;
      var label = submit.textContent;
      submit.disabled = true;
      submit.textContent = text.labels.sending;
      var timer, timeout = new Promise(function (resolve, reject) { timer = setTimeout(reject, 15000); });
      var body = JSON.stringify(Object.assign({ summary: summary(lead) }, lead));
      Promise.race([
        fetch(endpoint, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: body })
          .then(function (r) { return r.ok ? r.json() : { ok: false }; }),
        timeout
      ]).then(function (res) {
        if (res && res.ok && res.assigned_to) lead.assigned_to = res.assigned_to;
        return res && res.ok ? 'sent' : 'handoff';
      }, function () { return 'handoff'; }).then(function (mode) {
        clearTimeout(timer);
        sending = false;
        submit.disabled = false;
        submit.textContent = label;
        finish(lead, mode);
      });
    });

    if (done) {
      $('[data-restart]', done).addEventListener('click', function () {
        form.reset();
        done.hidden = true;
        form.hidden = false;
        rebuild();
        show(-1);
      });
    }

    form.setAttribute('data-state', 'intro');
    // a deep link to a question (#q3) opens the stepper there
    var m = /^#q(\d+)$/.exec(location.hash);
    if (m && steps[m[1] - 1]) { rebuild(); show(Math.max(0, seq.indexOf(steps[m[1] - 1]))); }
  }

  /* ── Entry estimator: category × market → approvals, time, duty, landed cost ── */
  function el(tag, cls, text) {
    var n = document.createElement(tag);
    if (cls) n.className = cls;
    if (text != null) n.textContent = text;
    return n;
  }
  function initEstimator() {
    var form = $('[data-estimator]');
    if (!form) return;
    var d = JSON.parse($('[data-estimator-data]').textContent);
    var L = d.labels;
    var out = $('[data-est-result]');
    var q = new URLSearchParams(location.search);
    ['market', 'category'].forEach(function (k) {
      var v = q.get(k);
      $$('option', form.elements[k]).forEach(function (o) { if (o.value === v) form.elements[k].value = v; });
    });

    function tile(label, value) {
      var t = el('div', 'fact');
      t.appendChild(el('p', 'eyebrow', label));
      t.appendChild(el('p', 'fact__v', value));
      return t;
    }
    function render() {
      var market = form.elements.market.value;
      var r = d.rules[market][form.elements.category.value];
      var certMin = 0, certMax = 0;
      r.certs.forEach(function (c) { certMin = Math.max(certMin, c[1]); certMax = Math.max(certMax, c[2]); });
      // approvals, entity and customs run in parallel; shipping follows
      var wMin = Math.max(certMin, d.setup[0]) + d.ship[0];
      var wMax = Math.max(certMax, d.setup[1]) + d.ship[1];
      var fob = parseFloat(form.elements.fob.value);
      var landed = fob > 0
        ? '$' + (fob * r.landed[0]).toFixed(2) + ' – $' + (fob * r.landed[1]).toFixed(2)
        : '×' + r.landed[0] + ' – ×' + r.landed[1] + ' ' + L.landedFactor;

      out.textContent = '';
      var grid = el('div', 'est-grid');
      grid.appendChild(tile(L.time, wMin + '–' + wMax + ' ' + L.weeks));
      grid.appendChild(tile(L.duty, r.duty ? d.duty[r.duty] : d.dutyUnknown));
      grid.appendChild(tile(L.tax, d.tax[r.tax]));
      grid.appendChild(tile(L.landed, landed));
      out.appendChild(grid);

      var certs = el('div', 'panel est-block');
      certs.appendChild(el('p', 'eyebrow', L.approvals));
      if (r.certs.length) {
        var ul = el('ul', 'est-certs');
        r.certs.forEach(function (c) {
          var li = el('li');
          li.appendChild(el('span', '', d.certs[c[0]]));
          li.appendChild(el('span', '', c[1] + '–' + c[2] + ' ' + L.weeks));
          ul.appendChild(li);
        });
        certs.appendChild(ul);
      } else {
        certs.appendChild(el('p', '', L.none));
      }
      out.appendChild(certs);

      var svc = el('div', 'panel est-block');
      svc.appendChild(el('p', 'eyebrow', L.services));
      var chips = el('div', 'est-services');
      r.services.forEach(function (slug) {
        var a = el('a', 'chip', d.services[slug][0]);
        a.href = d.services[slug][1];
        chips.appendChild(a);
      });
      svc.appendChild(chips);
      out.appendChild(svc);

      var links = el('div', 'est-links');
      if (d.playbooks[market]) {
        var book = el('a', 'btn btn--outline', L.playbook);
        book.href = d.playbooks[market];
        links.appendChild(book);
      }
      var apply = el('a', 'btn btn--primary', L.apply);
      apply.href = d.apply + '?service=' + encodeURIComponent(r.services[0]);
      links.appendChild(apply);
      out.appendChild(links);
    }
    form.addEventListener('input', render);
    form.addEventListener('submit', function (e) { e.preventDefault(); });
    render();
  }

  /* ── Tabs (portal preview); without JS every pane is listed in order ── */
  function initTabs() {
    $$('[data-tabs]').forEach(function (root) {
      var tabs = $$('[role="tab"]', root);
      var panes = $$('[role="tabpanel"]', root);
      function select(tab, focus) {
        tabs.forEach(function (t) {
          var on = t === tab;
          t.setAttribute('aria-selected', String(on));
          t.tabIndex = on ? 0 : -1;
        });
        panes.forEach(function (p) { p.hidden = p.id !== tab.getAttribute('aria-controls'); });
        if (focus) tab.focus();
      }
      tabs.forEach(function (t) { t.addEventListener('click', function () { select(t); }); });
      $('[role="tablist"]', root).addEventListener('keydown', function (e) {
        var i = tabs.indexOf(document.activeElement);
        if (i < 0) return;
        var to = { ArrowRight: i + 1, ArrowLeft: i - 1, Home: 0, End: tabs.length - 1 }[e.key];
        if (to == null) return;
        e.preventDefault();
        select(tabs[(to + tabs.length) % tabs.length], true);
      });
      select(tabs[0]);
      // on phones the stage strip scrolls; bring the current stage into view without moving the page
      var strip = $('.pstages', root), now = strip && $('.is-now', strip);
      if (now && strip.scrollWidth > strip.clientWidth) {
        strip.scrollLeft += now.getBoundingClientRect().left - strip.getBoundingClientRect().left - 24;
      }
    });
  }

  initSource();
  initNav();
  initHeroVideo();
  initReveal();
  initHow();
  initRegion();
  initSurvey();
  initEstimator();
  initTabs();
})();
