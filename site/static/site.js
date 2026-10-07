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

  /* ── Insights: filter posts by category ── */
  function initFilter() {
    var group = $('[data-filter]');
    if (!group) return;
    group.addEventListener('click', function (e) {
      var chip = e.target.closest('[data-cat]');
      if (!chip) return;
      var cat = chip.getAttribute('data-cat');
      $$('[data-cat]', group).forEach(function (c) { c.setAttribute('aria-pressed', String(c === chip)); });
      $$('.post-row').forEach(function (row) {
        row.hidden = cat !== '0' && row.getAttribute('data-cat') !== cat;
      });
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

  /* ── Partner survey ─────────────────────────────────────────────────── */
  var WHATSAPP = { Umer: '639772547666', Umair: '8615623305030', Aryan: '917645912074' };
  var SCORES = {
    monthly_volume_band: { '<1k': 5, '1k-10k': 15, '10k-50k': 25, '50k+': 35, 'n/a': 5 },
    timeline: { now: 30, '3_months': 22, '6_months': 12, exploring: 4 },
    party_type: { manufacturer: 25, brand_owner: 22, distributor: 15, investor: 8, other: 5 }
  };

  // auto-routing: PK → Umair, IN → Aryan, PH → Umer, a manufacturer → Umair
  function assignee(lead) {
    var m = lead.target_markets;
    if (m.indexOf('PK') > -1) return 'Umair';
    if (m.indexOf('IN') > -1) return 'Aryan';
    if (m.indexOf('PH') > -1) return 'Umer';
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
    var current = -1;

    function answered(step) {
      if (!step.hasAttribute('data-key')) return true;
      return !!$('input:checked', step);
    }
    function refresh(step) {
      var next = $('[data-next]', step);
      if (next) next.disabled = !answered(step);
    }
    function show(i) {
      current = i;
      form.setAttribute('data-state', i < 0 ? 'intro' : 'steps');
      steps.forEach(function (s, n) { s.classList.toggle('is-active', n === i); });
      var target = i < 0 ? $('.survey__intro h1', form) : $('.display', steps[i]);
      if (i >= 0) refresh(steps[i]);
      if (target) {
        target.setAttribute('tabindex', '-1');
        target.focus({ preventScroll: true });
      }
      window.scrollTo({ top: 0 });
    }

    form.addEventListener('click', function (e) {
      if (e.target.closest('[data-start]')) { e.preventDefault(); show(0); return; }
      if (e.target.closest('[data-back]')) { show(current - 1); return; }
      if (e.target.closest('[data-next]')) { if (answered(steps[current])) show(current + 1); return; }
      // a single-choice answer tapped or clicked moves straight on. The click
      // lands on the label first (the input is visually hidden); keyboard
      // users select on the input itself and confirm with Next.
      var opt = e.target.closest('.opt');
      if (opt && e.target.tagName !== 'INPUT' && $('input', opt).type === 'radio') {
        setTimeout(function () { show(current + 1); }, 120);
      }
    });
    form.addEventListener('change', function () { if (current >= 0) refresh(steps[current]); });

    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var data = new FormData(form);
      var lead = {
        created_at: new Date().toISOString(),
        locale: form.getAttribute('data-lang'),
        party_type: data.get('party_type') || '',
        category: data.get('category') || '',
        monthly_volume_band: data.get('monthly_volume_band') || '',
        target_markets: data.getAll('target_markets'),
        need: data.get('need') || '',
        timeline: data.get('timeline') || '',
        contact_name: data.get('contact_name') || '',
        company_name: data.get('company_name') || '',
        company_country: data.get('company_country') || '',
        contact_email: data.get('contact_email') || '',
        contact_phone: data.get('contact_phone') || '',
        handle: data.get('handle') || '',
        message: data.get('message') || '',
        source: document.referrer || ''
      };
      lead.score = score(lead);
      lead.assigned_to = assignee(lead);

      // wire the backend by setting data-endpoint on the form
      var endpoint = form.getAttribute('data-endpoint');
      if (endpoint && window.fetch) {
        fetch(endpoint, {
          method: 'POST', headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(lead), keepalive: true
        }).catch(function () {});
      }

      var who = lead.assigned_to;
      $$('[data-assignee]', done).forEach(function (el) { el.textContent = who; });
      $$('[data-assignee-link]', done).forEach(function (a) { a.href = 'https://wa.me/' + WHATSAPP[who]; });
      $('[data-score]', done).textContent = lead.score;
      form.hidden = true;
      done.hidden = false;
      window.scrollTo({ top: 0 });
      $('.done__title', done).focus({ preventScroll: true });
    });

    if (done) {
      $('[data-restart]', done).addEventListener('click', function () {
        form.reset();
        done.hidden = true;
        form.hidden = false;
        show(-1);
      });
    }

    form.setAttribute('data-state', 'intro');
    // a deep link to a question (#q3) opens the stepper there
    var m = /^#q(\d+)$/.exec(location.hash);
    if (m && steps[m[1] - 1]) show(m[1] - 1);
  }

  initNav();
  initHeroVideo();
  initReveal();
  initHow();
  initFilter();
  initRegion();
  initSurvey();
})();
