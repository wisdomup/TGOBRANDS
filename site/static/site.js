/* TGO Brands — progressive enhancement. Every page is complete without this
   file; it adds the nav's menus and sheet, the home slides, the footer form,
   the insights filter, region-ordered contact channels, the visa check, the
   estimator and the one-question-per-screen partner survey. */
(function () {
  'use strict';

  var doc = document.documentElement;
  var reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var $ = function (sel, root) { return (root || document).querySelector(sel); };
  var $$ = function (sel, root) { return Array.prototype.slice.call((root || document).querySelectorAll(sel)); };
  // a button's label sits in its own span so its colour can sweep on hover
  function button(cls, text) { var a = document.createElement('a'); a.className = cls; var s = document.createElement('span'); s.className = 'btn__t'; s.textContent = text; a.appendChild(s); return a; }

  /* ── Nav: merged with the page at the top, a capsule once scrolled ──
     Scale tracks scroll continuously over 0–320px. The values are written on
     the nav itself (not the root, which would restyle the whole page every
     frame) and only when they change, so scrolling stays smooth on phones. */
  function initNav() {
    var nav = $('.nav');
    if (!nav) return;
    var items = $$('.nav__item', nav);
    var hover = window.matchMedia('(hover: hover) and (pointer: fine)');
    var wide = window.matchMedia('(min-width: 768px)');
    function setOpen(item, open) {
      item.classList.toggle('is-open', open);
      var link = $('.nav__link', item);
      if (link) link.setAttribute('aria-expanded', open ? 'true' : 'false');
    }
    function closeAll(except) { items.forEach(function (it) { if (it !== except) setOpen(it, false); }); }
    items.forEach(function (item) {
      var timer = 0;
      item.addEventListener('pointerenter', function (e) {
        if (!wide.matches || !hover.matches || e.pointerType === 'touch') return;
        clearTimeout(timer);
        timer = setTimeout(function () { closeAll(item); setOpen(item, true); }, 70);
      });
      item.addEventListener('pointerleave', function () {
        clearTimeout(timer);
        timer = setTimeout(function () { setOpen(item, false); }, 140);
      });
      item.addEventListener('focusin', function () { closeAll(item); setOpen(item, true); });
      item.addEventListener('focusout', function (e) { if (!item.contains(e.relatedTarget)) setOpen(item, false); });
      // a touch on the link opens the menu first; a second touch follows the link
      $('.nav__link', item).addEventListener('click', function (e) {
        if (hover.matches || item.classList.contains('is-open')) return;
        e.preventDefault();
        closeAll(item);
        setOpen(item, true);
      });
      // the category rail switches the card grid
      $$('.mega__tab', item).forEach(function (tab, k) {
        tab.addEventListener('click', function () {
          $$('.mega__tab', item).forEach(function (x, n) { x.setAttribute('aria-selected', n === k ? 'true' : 'false'); });
          $$('.mega__grid', item).forEach(function (g, n) { g.classList.toggle('is-active', n === k); });
        });
      });
    });
    document.addEventListener('keydown', function (e) { if (e.key === 'Escape') { closeAll(); closeSheet(); } });
    document.addEventListener('pointerdown', function (e) { if (!nav.contains(e.target)) closeAll(); });

    var burger = $('.burger', nav), sheet = $('.msheet', nav);
    function closeSheet() {
      if (!sheet || !sheet.classList.contains('is-open')) return;
      sheet.classList.remove('is-open');
      burger.setAttribute('aria-expanded', 'false');
      document.documentElement.style.overflow = '';
    }
    if (burger && sheet) {
      burger.addEventListener('click', function () {
        var open = !sheet.classList.contains('is-open');
        if (!open) return closeSheet();
        sheet.classList.add('is-open');
        burger.setAttribute('aria-expanded', 'true');
        document.documentElement.style.overflow = 'hidden';
      });
      wide.addEventListener('change', function (e) { if (e.matches) closeSheet(); });
    }
  }

  /* ── Footer contact form: posts to /api/lead like the application; if the server cannot take
     it, the message goes by email instead ── */
  function initFooterForm() {
    var form = $('[data-footer-form]');
    if (!form) return;
    var text = JSON.parse($('[data-footer-text]', form).textContent);
    var btn = $('button[type="submit"]', form), need = $('[data-need]', form), ok = $('[data-footer-ok]'), fail = $('[data-footer-fail]');
    var again = $('[data-footer-again]');
    if (again) again.addEventListener('click', function () {
      form.reset();
      ok.hidden = true;
      form.hidden = false;
      btn.disabled = false;
      var label = $('.btn__t', btn); if (label) label.textContent = text.send;
      var firstField = $('.input', form); if (firstField) firstField.focus();
    });
    form.addEventListener('submit', function (ev) {
      ev.preventDefault();
      var data = new FormData(form);
      var reachable = ['contact_email', 'contact_phone'].some(function (k) { return (data.get(k) || '').trim(); });
      need.hidden = reachable;
      if (!reachable) { $('[name="contact_email"]', form).focus(); return; }
      var lead = { created_at: new Date().toISOString(), locale: form.getAttribute('data-lang'), party_type: 'other',
        target_markets: [], source: source(), website: data.get('website') || '', summary: text.msg };
      ['contact_name', 'company_name', 'contact_email', 'contact_phone', 'message'].forEach(function (k) { lead[k] = data.get(k) || ''; });
      lead.score = 0; lead.assigned_to = 'Umair';
      btn.disabled = true;
      var label = $('.btn__t', btn); if (label) label.textContent = text.sending;
      function done(sent) {
        form.hidden = true;
        if (sent) { ok.hidden = false; ok.focus && ok.focus(); }
        else {
          fail.hidden = false;
          var body = ['contact_name', 'company_name', 'contact_email', 'contact_phone', 'message'].map(function (k) { return k + ': ' + (lead[k] || '-'); }).join('\n');
          $('a', fail).href = 'mailto:help@tgobrands.com?subject=' + encodeURIComponent(text.subject) + '&body=' + encodeURIComponent(body);
        }
      }
      if (!window.fetch) return done(false);
      fetch(form.getAttribute('data-endpoint'), { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(lead) })
        .then(function (r) { return r.ok ? r.json() : Promise.reject(r); })
        .then(function (b) { done(!!(b && b.ok)); })
        .catch(function () { done(false); });
    });
  }

  /* ── Home slides: a clip-path wipe between full-screen slides, copy cross-fading, a progress
     line that fills over each slide's time, arrows, step labels and a scroll cue. Autoplay
     rests while the tab is hidden and never runs for readers who prefer reduced motion. ── */
  function initSlides() {
    var root = $('[data-slides]');
    if (!root) return;
    var slides = $$('.slide', root), copies = $$('.slide__copy', root), labels = $$('.slide-steps__labels button', root);
    var line = $('.slide-steps__line span', root);
    var n = slides.length, cur = 0, timer = 0, every = parseInt(root.getAttribute('data-every'), 10) || 5000;
    var auto = !reduced && n > 1;
    function fill(from, to, ms) {
      if (!line) return;
      line.style.transition = 'none';
      line.style.width = (from * 100 / n) + '%';
      void line.offsetWidth;
      line.style.transition = ms ? 'width ' + ms + 'ms linear' : 'width 0.4s ease';
      line.style.width = (to * 100 / n) + '%';
    }
    function go(i) {
      i = (i + n) % n;
      var prev = (i - 1 + n) % n, next = (i + 1) % n;
      slides.forEach(function (s, k) {
        s.style.zIndex = k === i ? 2 : 1;
        s.classList.toggle('close-right', k === next && n > 2 || n === 2 && k !== i);
        s.classList.toggle('close-left', k === prev && n > 2);
      });
      copies.forEach(function (c, k) { c.classList.toggle('is-active', k === i); c.setAttribute('aria-hidden', k === i ? 'false' : 'true'); });
      labels.forEach(function (b, k) { b.classList.toggle('is-active', k <= i); b.setAttribute('aria-current', k === i ? 'true' : 'false'); });
      fill(i, i + 1, auto ? every : 0);
      cur = i;
    }
    function play() {
      clearInterval(timer);
      if (!auto || document.hidden) return;
      timer = setInterval(function () { go(cur + 1); }, every);
    }
    var prevBtn = $('.slide-arrow--prev', root), nextBtn = $('.slide-arrow--next', root);
    if (prevBtn) prevBtn.addEventListener('click', function () { go(cur - 1); play(); });
    if (nextBtn) nextBtn.addEventListener('click', function () { go(cur + 1); play(); });
    labels.forEach(function (b, k) { b.addEventListener('click', function () { go(k); play(); }); });
    root.addEventListener('keydown', function (e) {
      if (e.key === 'ArrowLeft') { go(cur - 1); play(); }
      if (e.key === 'ArrowRight') { go(cur + 1); play(); }
    });
    document.addEventListener('visibilitychange', function () { if (document.hidden) clearInterval(timer); else { go(cur); play(); } });
    go(0);
    play();
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
    party_type: { entrepreneur: 22, manufacturer: 25, brand_owner: 22, distributor: 15, creator: 12, investor: 8, other: 5 },
    monthly_volume_band: { '<1k': 5, '1k-10k': 15, '10k-50k': 25, '50k+': 35, 'n/a': 5 },
    dist_outlets: { '1': 5, '2-10': 12, '11-50': 22, '50+': 30, online: 15 },
    creator_following: { '<100k': 5, '100k-500k': 15, '500k-1m': 25, '1m+': 35 },
    investor_ticket: { '<50k': 5, '50k-250k': 15, '250k-1m': 25, '1m+': 35 },
    timeline: { now: 30, '3_months': 22, '6_months': 12, exploring: 4 }
  };

  // routing: a service one founder leads goes to that founder (IT and ERP & CRM → Umair, also when
  // IT is the only need); otherwise by market: PK → Umair, IN → Aryan, PH → Umer, UAE → Shamas, else Umair.
  // Mirrors route() in api/lead.py, which decides.
  var SERVICE_LEADS = { 'it-solutions': 'Umair', 'erp-crm-integration': 'Umair' };
  function assignee(lead) {
    if (SERVICE_LEADS[lead.service]) return SERVICE_LEADS[lead.service];
    if (lead.need && lead.need.length === 1 && lead.need[0] === 'systems') return SERVICE_LEADS['it-solutions'];
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
      window.scrollTo({ top: 0, behavior: 'instant' });
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
      window.scrollTo({ top: 0, behavior: 'instant' });
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
        var book = button('btn btn--outline', L.playbook);
        book.href = d.playbooks[market];
        links.appendChild(book);
      }
      var apply = button('btn btn--primary', L.apply);
      apply.href = d.apply + '?service=' + encodeURIComponent(r.services[0]);
      links.appendChild(apply);
      out.appendChild(links);
    }
    form.addEventListener('input', render);
    form.addEventListener('submit', function (e) { e.preventDefault(); });
    render();
  }

  /* ── Travel enquiry: delivered like the application — the server sends it to the
     destination's host, or the traveller does on WhatsApp or by email ── */
  function initTravel() {
    var form = $('[data-travel]');
    if (!form) return;
    var text = JSON.parse($('[data-travel-text]', form).textContent);
    var L = text.labels;
    var done = $('[data-travel-done]', form.parentNode);
    var submit = $('button[type="submit"]', form);
    var error = $('[data-travel-error]', form);
    var sending = false;

    // ?to=PH preselects a destination
    var to = new URLSearchParams(location.search).get('to');
    $$('input[name="destinations"]', form).forEach(function (i) { if (i.value === to) i.checked = true; });

    function host(dests) {
      var order = ['PK', 'IN', 'PH', 'AE', 'CN', 'BD', 'NP'];
      for (var i = 0; i < order.length; i++) if (dests.indexOf(order[i]) > -1) return text.hosts[order[i]];
      return 'Umair';
    }
    function line(label, value) { return label.replace(/[?？]$/, '') + ': ' + value; }
    function summary(lead) {
      var lines = [L.msg, '', line(L.dest, lead.destinations.map(function (d) { return text.dests[d]; }).join(', '))];
      if (lead.purpose) lines.push(line(L.purpose, text.purposes[lead.purpose]));
      if (lead.travellers) lines.push(line(L.travellers, lead.travellers + ' ' + L.people));
      [['travel_when', L.when], ['travel_from', L.from], ['contact_name', L.name], ['contact_email', L.email],
        ['handle', L.handle], ['contact_phone', L.phone], ['message', L.message]].forEach(function (f) {
        if (lead[f[0]].trim()) lines.push(line(f[1], lead[f[0]].trim()));
      });
      if (lead.source) lines.push('Source: ' + lead.source);
      return lines.join('\n');
    }
    function finish(lead, mode) {
      var who = lead.assigned_to;
      var msg = summary(lead);
      $$('[data-mode]', done).forEach(function (n) { n.hidden = n.getAttribute('data-mode') !== mode; });
      $$('[data-who]', done).forEach(function (n) { n.textContent = who; });
      $$('h3, p', done).forEach(function (n) { n.classList.add('is-in'); });
      $('[data-wa]', done).href = 'https://wa.me/' + WHATSAPP[who] + '?text=' + encodeURIComponent(msg);
      $('[data-mail]', done).href = 'mailto:help@tgobrands.com?subject=' + encodeURIComponent(L.subject) +
        '&body=' + encodeURIComponent(msg);
      form.hidden = true;
      done.hidden = false;
      done.scrollIntoView({ block: 'center' });
      $('.tdone__title:not([hidden])', done).focus({ preventScroll: true });
    }

    form.addEventListener('submit', function (e) {
      e.preventDefault();
      if (sending) return;
      var data = new FormData(form);
      var dests = data.getAll('destinations');
      var reachable = ['contact_email', 'contact_phone', 'handle'].some(function (k) { return (data.get(k) || '').trim(); });
      error.hidden = dests.length > 0 && reachable;
      if (!dests.length) {
        error.textContent = L.needDest;
        return $('input[name="destinations"]', form).focus();
      }
      if (!reachable) {
        error.textContent = L.needContact;
        return $('#t-contact_email', form).focus();
      }
      var lead = {
        kind: 'travel',
        created_at: new Date().toISOString(),
        locale: form.getAttribute('data-lang'),
        source: source(),
        website: data.get('website') || '',
        destinations: dests,
        purpose: data.get('purpose') || '',
        travellers: data.get('travellers') || ''
      };
      ['travel_when', 'travel_from', 'contact_name', 'contact_email', 'contact_phone', 'handle', 'message']
        .forEach(function (k) { lead[k] = data.get(k) || ''; });
      lead.assigned_to = host(dests);

      var endpoint = form.getAttribute('data-endpoint');
      if (!endpoint || !window.fetch) return finish(lead, 'handoff');
      sending = true;
      var label = submit.textContent;
      submit.disabled = true;
      submit.textContent = L.sending;
      var timer, timeout = new Promise(function (resolve, reject) { timer = setTimeout(reject, 15000); });
      Promise.race([
        fetch(endpoint, {
          method: 'POST', headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(Object.assign({ summary: summary(lead) }, lead))
        }).then(function (r) { return r.ok ? r.json() : { ok: false }; }),
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
  }

  /* ── Visa and passport check: any passport to any country. TGO's core corridors carry their
     own rules (fees, lead times, business notes); everything else comes from the world table,
     which loads as a cached file. Names come from the browser in the page's language. ── */
  function initChecker() {
    var form = $('[data-checker]');
    if (!form) return;
    var d = JSON.parse($('[data-checker-data]').textContent);
    var L = d.labels;
    var out = $('[data-checker-result]');
    var locale = d.lang === 'zh' ? 'zh-CN' : 'en';
    var TYPES = { F: 'free', A: 'voa', E: 'evisa', T: 'eta', V: 'visa', B: 'blocked', H: 'home', C: 'check' };
    var LEAD = { free: 0, voa: 0, eta: 3, evisa: 7, visa: 21 };
    var world = null;
    var regions = null;
    try { regions = new Intl.DisplayNames([locale], { type: 'region' }); } catch (e) { /* older browsers: codes */ }
    function name(code) {
      if (d.destNames[code]) return d.destNames[code];
      try { return (regions && regions.of(code)) || code; } catch (e) { return code; }
    }
    var q = new URLSearchParams(location.search);
    var wanted = { passport: q.get('pp'), dest: q.get('to') };
    function pick(sel, v) { if (v && $$('option', sel).some(function (o) { return o.value === v; })) sel.value = v; }
    pick(form.elements.passport, wanted.passport);
    pick(form.elements.dest, wanted.dest);

    function fill(sel, current) {
      var coll = new Intl.Collator(locale);
      var top = document.createElement('optgroup');
      top.label = L.groupTop;
      d.featured.forEach(function (c) { top.appendChild(new Option(name(c), c)); });
      var all = document.createElement('optgroup');
      all.label = L.groupAll;
      world.codes.slice().sort(function (a, b) { return coll.compare(name(a), name(b)); })
        .forEach(function (c) { all.appendChild(new Option(name(c), c)); });
      sel.textContent = '';
      sel.appendChild(top);
      sel.appendChild(all);
      sel.value = current;
    }

    function rule(pp, dest) {
      if (d.core[dest] && d.core[dest][pp]) return d.core[dest][pp];
      if (pp === dest) return { type: 'home', note: 'home' };
      if (!world || !world.rows[pp]) return { type: 'check', note: 'g_check' };
      if (typeof world.rows[pp] === 'string') world.rows[pp] = world.rows[pp].split(',');
      var tok = world.rows[pp][world.index[dest]] || 'C';
      var type = TYPES[tok.charAt(0)] || 'check';
      var stay = parseInt(tok.slice(1), 10) || null;
      var note = world.notes[pp + '>' + dest] || ('g_' + type + (stay && d.notes['g_' + type + '_n'] ? '_n' : ''));
      return { type: type, stay: stay, note: note, fee: type === 'free' ? 0 : null, lead: LEAD[type] || 0 };
    }

    function fmt(str, map) { return str.replace(/\{(\w+)\}/g, function (m, k) { return map[k] != null ? map[k] : m; }); }
    function day(v) { var x = v ? new Date(v + 'T00:00:00') : null; return x && !isNaN(x) ? x : null; }
    function addDays(x, n) { var y = new Date(x); y.setDate(y.getDate() + n); return y; }
    function addMonths(x, n) { var y = new Date(x); y.setMonth(y.getMonth() + n); return y; }
    function show(x) { return x.toLocaleDateString(d.lang === 'zh' ? 'zh-CN' : 'en-GB', { day: 'numeric', month: 'long', year: 'numeric' }); }
    function tile(label, value, cls) {
      var t = el('div', 'fact' + (cls ? ' ' + cls : ''));
      t.appendChild(el('p', 'eyebrow', label));
      t.appendChild(el('p', 'fact__v', value));
      return t;
    }
    function checklist(r, pp, dest, biz) {
      if (r.type === 'home') return ['id'];
      var k = ['passport'];
      if (r.type === 'evisa' || r.type === 'eta') k.push('photo', 'online');
      if (r.type === 'visa') k.push('photo', 'form', 'funds');
      if (r.type === 'voa') k.push('cash');
      k.push('ticket', 'hotel');
      if (biz) k.push(dest === 'CN' ? 'fair' : 'invite', 'company');
      if (biz && dest === 'BD' && r.type === 'voa') k.push('notice');
      if (dest === 'PK' && pp === 'CN') k.push('security');
      if (dest === 'PH') k.push('etravel');
      return k;
    }

    function render() {
      var pp = form.elements.passport.value, dest = form.elements.dest.value;
      var biz = form.elements.purpose.value === 'business';
      var r = rule(pp, dest);
      var arrive = day(form.elements.arrive.value), leave = day(form.elements.leave.value), expiry = day(form.elements.expiry.value);
      out.textContent = '';

      var card = el('div', 'panel vresult');
      var head = el('div', 'vresult__head');
      head.appendChild(el('span', 'vbadge vbadge--' + r.type, L.types[r.type]));
      head.appendChild(el('h3', 'vresult__title', name(dest)));
      card.appendChild(head);
      var key = biz && r.noteBiz ? r.noteBiz : r.note;
      card.appendChild(el('p', 'vresult__note', fmt(d.notes[key] || d.notes['g_' + r.type] || '', { n: r.stay })));

      if (['free', 'voa', 'evisa', 'eta', 'visa'].indexOf(r.type) > -1) {
        var grid = el('div', 'est-grid');
        grid.appendChild(tile(L.stay, r.stay ? fmt(L.days, { n: r.stay }) : r.open ? L.stayOpen : L.stayVaries));
        // a business-specific rule (e.g. India's e-B-4) has its own fee, so don't show the tourist one
        var fee = biz && r.noteBiz ? L.feeVaries
          : r.fee === 0 ? L.noFee
          : r.fee && r.fee.kind === 'onArrival' ? fmt(L.feeOnArrival, { n: r.fee.n })
          : r.fee && r.fee.kind === 'from' ? fmt(L.feeFrom, { n: r.fee.n }) : L.feeVaries;
        grid.appendChild(tile(L.fee, fee));
        var lead = biz && r.leadBiz != null ? r.leadBiz : r.lead;
        var by = lead && arrive ? addDays(arrive, -lead) : null;
        var late = by && by < new Date(new Date().toDateString());
        grid.appendChild(tile(L.applyBy, !lead ? L.noApply : by ? show(by) + (late ? ' — ' + L.late : '') : fmt(L.beforeFly, { n: lead }),
          late ? 'is-bad' : ''));
        // passport validity: Schengen asks three months beyond departure; the Philippines six beyond the
        // stay; most other countries six months from arrival
        var schengen = d.schengen.indexOf(dest) > -1, beyond = schengen || d.beyondStay.indexOf(dest) > -1;
        var months = schengen ? 3 : d.validity;
        var verdict = L.addDates, cls = '';
        if (expiry && arrive) {
          var ok = expiry >= addMonths(beyond ? (leave || arrive) : arrive, months);
          verdict = ok ? L.valid : L.renew;
          cls = ok ? 'is-ok' : 'is-bad';
        }
        grid.appendChild(tile(L.passportCheck, verdict, cls));
        card.appendChild(grid);
        card.appendChild(el('p', 'vresult__rule', (schengen ? L.validRuleStay3 : beyond ? L.validRuleStay : L.validRule) + ' ' + L.pages));
      }
      if (d.destNotes[dest] && r.type !== 'blocked') card.appendChild(el('p', 'vresult__note', d.destNotes[dest]));

      if (r.type !== 'blocked' && r.type !== 'check') {
        var block = el('div', 'vresult__list');
        block.appendChild(el('p', 'eyebrow', L.checklist));
        var ul = el('ul', 'ticks');
        checklist(r, pp, dest, biz).forEach(function (k) { ul.appendChild(el('li', '', d.docs[k])); });
        block.appendChild(ul);
        card.appendChild(block);
      }

      var acts = el('div', 'vresult__acts');
      var plan = button('btn btn--primary', L.plan);
      plan.href = '#plan';
      plan.addEventListener('click', function () {
        var box = $('[data-travel] input[name="destinations"][value="' + dest + '"]');
        if (box) box.checked = true;
        else {
          var msg = $('[data-travel] textarea[name="message"]');
          if (msg && !msg.value.trim()) msg.value = L.tripTo + ' ' + name(dest);
        }
      });
      acts.appendChild(plan);
      if (d.guides[dest]) {
        var guide = button('btn btn--outline', fmt(L.guide, { country: name(dest) }));
        guide.href = d.guides[dest];
        acts.appendChild(guide);
      }
      var host = d.hosts[dest];
      if (host && WHATSAPP[host]) {
        var wa = el('a', 'btn btn--link', fmt(L.whatsapp, { name: host }));
        wa.href = 'https://wa.me/' + WHATSAPP[host];
        wa.target = '_blank';
        wa.rel = 'noopener';
        acts.appendChild(wa);
      }
      card.appendChild(acts);
      out.appendChild(card);
    }

    form.addEventListener('input', render);
    form.addEventListener('change', render);
    form.addEventListener('submit', function (e) { e.preventDefault(); });
    render();

    // the world table: every passport and destination, cached by its hashed file name
    if (window.fetch && d.world) {
      fetch(d.world).then(function (res) { return res.json(); }).then(function (w) {
        world = w;
        world.index = {};
        w.codes.forEach(function (c, i) { world.index[c] = i; });
        fill(form.elements.passport, wanted.passport && world.index[wanted.passport] != null ? wanted.passport : form.elements.passport.value);
        fill(form.elements.dest, wanted.dest && world.index[wanted.dest] != null ? wanted.dest : form.elements.dest.value);
        render();
      }).catch(function () { /* the core corridors still work */ });
    }
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

  /* ── Theme: follows the device until the visitor picks one (nav or footer) ──
     The head script sets data-theme before first paint; this keeps both
     switches, the stored choice and live device changes in step. */
  initSource();
  initNav();
  initFooterForm();
  initSlides();
  initRegion();
  initSurvey();
  initTravel();
  initChecker();
  initEstimator();
  initTabs();
})();
