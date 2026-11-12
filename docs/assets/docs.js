/* Ironclad docs — sidebar, copy buttons, search, scroll-spy. No dependencies. */
(function () {
  'use strict';

  /* ---------------- sidebar (mobile) ---------------- */
  var side = document.getElementById('side');
  var burger = document.getElementById('burger');
  var scrim = document.getElementById('scrim');

  function setSide(open) {
    if (!side) return;
    side.classList.toggle('open', open);
    if (scrim) scrim.hidden = !open;
    if (burger) burger.setAttribute('aria-expanded', String(open));
    document.body.style.overflow = open ? 'hidden' : '';
  }
  if (burger) burger.addEventListener('click', function () {
    setSide(!side.classList.contains('open'));
  });
  if (scrim) scrim.addEventListener('click', function () { setSide(false); });

  /* ---------------- copy buttons ---------------- */
  document.querySelectorAll('.codewrap .copy').forEach(function (btn) {
    btn.addEventListener('click', function () {
      var pre = btn.parentElement.querySelector('pre');
      if (!pre) return;
      var text = pre.innerText.replace(/\s+$/, '');
      var ok = function () {
        btn.textContent = 'TERSALIN';
        btn.classList.add('done');
        setTimeout(function () { btn.textContent = 'SALIN'; btn.classList.remove('done'); }, 1500);
      };
      var fail = function () {
        btn.textContent = 'GAGAL';
        btn.classList.add('fail');
        setTimeout(function () { btn.textContent = 'SALIN'; btn.classList.remove('fail'); }, 1500);
      };
      if (navigator.clipboard && window.isSecureContext) {
        navigator.clipboard.writeText(text).then(ok).catch(function () { legacy(text) ? ok() : fail(); });
      } else {
        legacy(text) ? ok() : fail();
      }
      function legacy(t) {
        var ta = document.createElement('textarea');
        ta.value = t;
        ta.style.cssText = 'position:fixed;top:-1000px;opacity:0';
        document.body.appendChild(ta);
        ta.select();
        var done = false;
        try { done = document.execCommand('copy'); } catch (e) { done = false; }
        document.body.removeChild(ta);
        return done;
      }
    });
  });

  /* ---------------- scroll-spy TOC ---------------- */
  var tocLinks = Array.prototype.slice.call(document.querySelectorAll('.toc a'));
  if (tocLinks.length && 'IntersectionObserver' in window) {
    var byId = {};
    tocLinks.forEach(function (a) { byId[a.getAttribute('href').slice(1)] = a; });
    var targets = Object.keys(byId).map(function (id) { return document.getElementById(id); })
      .filter(Boolean);
    var visible = new Set();
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) visible.add(e.target.id); else visible.delete(e.target.id);
      });
      var first = targets.filter(function (t) { return visible.has(t.id); })[0];
      tocLinks.forEach(function (a) { a.classList.remove('on'); });
      if (first) {
        var link = byId[first.id];
        if (link) link.classList.add('on');
      }
    }, { rootMargin: '-72px 0px -70% 0px', threshold: 0 });
    targets.forEach(function (t) { io.observe(t); });
  }

  /* ---------------- search ---------------- */
  var modal = document.getElementById('search');
  var input = document.getElementById('q');
  var results = document.getElementById('results');
  // Read lazily: search-index.js is a separate deferred script and may not have
  // run yet when this file executes. Capturing it here gave an empty index.
  function index() { return window.IRONCLAD_INDEX || []; }
  var sel = -1;

  function open() {
    if (!modal) return;
    modal.hidden = false;
    document.body.style.overflow = 'hidden';
    setTimeout(function () { input.focus(); }, 30);
    render(input.value);
  }
  function close() {
    if (!modal) return;
    modal.hidden = true;
    document.body.style.overflow = '';
    sel = -1;
  }
  function score(item, q) {
    var t = item.t.toLowerCase(), s = (item.s || '').toLowerCase(), x = (item.x || '').toLowerCase();
    var n = 0;
    if (t.indexOf(q) === 0) n += 90;
    else if (t.indexOf(q) > -1) n += 60;
    if (s.indexOf(q) > -1) n += 25;
    var idx = x.indexOf(q);
    if (idx > -1) n += 20;
    q.split(/\s+/).forEach(function (w) {
      if (w.length > 2 && x.indexOf(w) > -1) n += 6;
    });
    return n;
  }
  function snippet(text, q) {
    var i = text.toLowerCase().indexOf(q);
    if (i < 0) return '';
    var start = Math.max(0, i - 45);
    var out = (start ? '…' : '') + text.slice(start, i + q.length + 95).trim() + '…';
    return out.replace(new RegExp('(' + q.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + ')', 'ig'), '<mark>$1</mark>');
  }
  function render(q) {
    q = (q || '').trim().toLowerCase();
    if (!results) return;
    var data = index();
    if (!q) {
      results.innerHTML = data.slice(0, 7).map(function (d) {
        return '<li><a href="' + d.u + '"><small>' + d.g + '</small><b>' + d.t + '</b></a></li>';
      }).join('');
      return;
    }
    var hits = data.map(function (d) { return { d: d, n: score(d, q) }; })
      .filter(function (h) { return h.n > 0; })
      .sort(function (a, b) { return b.n - a.n; })
      .slice(0, 12);
    results.innerHTML = hits.length
      ? hits.map(function (h) {
          return '<li><a href="' + h.d.u + '"><small>' + h.d.g + '</small><b>' + h.d.t +
                 '</b><em>' + (snippet(h.d.x, q) || h.d.s || '') + '</em></a></li>';
        }).join('')
      : '<li><a><b>Tidak ada hasil</b><em>Coba kata lain: preset, enum, CI, install.</em></a></li>';
    sel = -1;
  }
  function move(delta) {
    var items = Array.prototype.slice.call(results.querySelectorAll('li'));
    if (!items.length) return;
    items.forEach(function (li) { li.classList.remove('sel'); });
    sel = (sel + delta + items.length) % items.length;
    items[sel].classList.add('sel');
    items[sel].scrollIntoView({ block: 'nearest' });
  }

  var btn = document.getElementById('searchbtn');
  var mini = document.getElementById('searchmini');
  if (btn) btn.addEventListener('click', open);
  if (mini) mini.addEventListener('click', open);
  var closer = document.getElementById('closeSearch');
  if (closer) closer.addEventListener('click', close);
  if (modal) modal.addEventListener('click', function (e) { if (e.target === modal) close(); });
  if (input) input.addEventListener('input', function () { render(input.value); });

  document.addEventListener('keydown', function (e) {
    var typing = /^(INPUT|TEXTAREA|SELECT)$/.test((e.target.tagName || ''));
    if ((e.key === '/' && !typing) || ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 'k')) {
      e.preventDefault(); open(); return;
    }
    if (!modal || modal.hidden) return;
    if (e.key === 'Escape') { e.preventDefault(); close(); }
    else if (e.key === 'ArrowDown') { e.preventDefault(); move(1); }
    else if (e.key === 'ArrowUp') { e.preventDefault(); move(-1); }
    else if (e.key === 'Enter') {
      var pick = results && results.querySelector('li.sel a') || results.querySelector('li a');
      if (pick && pick.getAttribute('href')) { e.preventDefault(); window.location.href = pick.getAttribute('href'); }
    }
  });

  /* close the mobile drawer when a link is tapped */
  if (side) side.addEventListener('click', function (e) {
    if (e.target.closest('a')) setSide(false);
  });
})();
