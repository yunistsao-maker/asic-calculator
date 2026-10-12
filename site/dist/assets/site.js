/* Inference ASIC Atlas — shared behaviour: theme, phone menu, two-level tabs with deep links, table tools. */
(function () {
  'use strict';
  var doc = document, root = doc.documentElement;
  function $(sel, el) { return (el || doc).querySelector(sel); }
  function $$(sel, el) { return Array.prototype.slice.call((el || doc).querySelectorAll(sel)); }
  function store(k, v) { try { if (v === undefined) return localStorage.getItem(k); localStorage.setItem(k, v); } catch (e) { return null; } }

  /* ---------- theme */
  function currentTheme() {
    var t = root.getAttribute('data-theme');
    if (t === 'light' || t === 'dark') return t;
    return window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  }
  function initTheme() {
    var btn = $('#theme-btn');
    if (!btn) return;
    function label() { btn.setAttribute('aria-label', currentTheme() === 'dark' ? '切換為淺色模式' : '切換為深色模式'); btn.setAttribute('aria-pressed', currentTheme() === 'dark' ? 'true' : 'false'); }
    label();
    btn.addEventListener('click', function () {
      var next = currentTheme() === 'dark' ? 'light' : 'dark';
      root.setAttribute('data-theme', next);
      store('ia-theme', next);
      label();
    });
  }

  /* ---------- phone menu */
  function initMenu() {
    var btn = $('#menu-btn'), nav = $('#idx');
    if (!btn || !nav) return;
    btn.addEventListener('click', function () {
      var open = !nav.classList.contains('open');
      nav.classList.toggle('open', open);
      btn.setAttribute('aria-expanded', open ? 'true' : 'false');
      $('span', btn).textContent = open ? '關閉' : '章節';
    });
  }

  /* ---------- tabs */
  function tabsOf(list) { return $$('[role="tab"]', list).filter(function (t) { return t.parentNode === list; }); }
  function selectTab(tab, setHash) {
    var list = tab.parentNode;
    tabsOf(list).forEach(function (t) {
      var on = t === tab;
      t.setAttribute('aria-selected', on ? 'true' : 'false');
      t.tabIndex = on ? 0 : -1;
      var p = doc.getElementById(t.getAttribute('aria-controls'));
      if (p) p.classList.toggle('on', on);
    });
    if (setHash && window.history && history.replaceState) {
      var id = tab.getAttribute('aria-controls');
      var panel = doc.getElementById(id);
      // a section tab with sub-tabs: keep the hash on the section
      history.replaceState(null, '', '#' + id);
      if (panel) doc.dispatchEvent(new CustomEvent('ia:panel', { detail: { id: id } }));
    }
  }
  function tabFor(panel) { return doc.getElementById(panel.getAttribute('aria-labelledby')); }
  function reveal(el, scroll) {
    var chain = [], p = el;
    while (p && p !== doc.body) {
      if (p.getAttribute && p.getAttribute('role') === 'tabpanel') chain.unshift(p);
      if (p.tagName === 'DETAILS') p.open = true;
      if (p.tagName === 'TBODY' && p._iaExpand) p._iaExpand();
      p = p.parentNode;
    }
    chain.forEach(function (panel) { var t = tabFor(panel); if (t) selectTab(t, false); });
    if (!scroll) return;
    var isPanel = el.getAttribute('role') === 'tabpanel';
    var target = isPanel ? (tabFor(el) ? tabFor(el).parentNode : el) : el;
    window.requestAnimationFrame(function () {
      var r = target.getBoundingClientRect();
      window.scrollTo({ top: Math.max(0, window.pageYOffset + r.top - (isPanel ? 12 : 80)), behavior: 'auto' });
      if (!isPanel) {
        el.classList.remove('flash');
        void el.offsetWidth;
        el.classList.add('flash');
      }
    });
  }
  function fromHash(scroll) {
    var h = decodeURIComponent((location.hash || '').slice(1));
    if (!h) return;
    var q = h.indexOf('?');
    if (q >= 0) h = h.slice(0, q);
    var el = h ? doc.getElementById(h) : null;
    if (el) reveal(el, scroll);
  }
  function initTabs() {
    $$('[role="tablist"]').forEach(function (list) {
      var tabs = tabsOf(list);
      tabs.forEach(function (t) { t.tabIndex = t.getAttribute('aria-selected') === 'true' ? 0 : -1; });
      list.addEventListener('click', function (e) {
        var t = e.target.closest ? e.target.closest('[role="tab"]') : null;
        if (t && t.parentNode === list) selectTab(t, true);
      });
      list.addEventListener('keydown', function (e) {
        var i = tabs.indexOf(doc.activeElement);
        if (i < 0) return;
        var n = -1;
        if (e.key === 'ArrowRight' || e.key === 'ArrowDown') n = (i + 1) % tabs.length;
        else if (e.key === 'ArrowLeft' || e.key === 'ArrowUp') n = (i - 1 + tabs.length) % tabs.length;
        else if (e.key === 'Home') n = 0;
        else if (e.key === 'End') n = tabs.length - 1;
        if (n >= 0) { e.preventDefault(); tabs[n].focus(); selectTab(tabs[n], true); }
      });
    });
    fromHash(true);
    window.addEventListener('hashchange', function () { fromHash(true); });
    // in-page links to an element inside a hidden panel
    doc.addEventListener('click', function (e) {
      var a = e.target.closest ? e.target.closest('a[href^="#"]') : null;
      if (!a) return;
      var id = decodeURIComponent(a.getAttribute('href').slice(1));
      var el = id ? doc.getElementById(id) : null;
      if (el) { e.preventDefault(); history.pushState(null, '', '#' + id); reveal(el, true); }
    });
  }

  /* ---------- tables: sort, filter, copy, enlarge */
  function parseCell(td) {
    var t = (td.getAttribute('data-v') || td.textContent || '').replace(/\s+/g, ' ').trim();
    var d = t.match(/^(\d{4})-(\d{2})(?:-(\d{2}))?/);
    if (d) return { n: Number(d[1]) * 10000 + Number(d[2]) * 100 + Number(d[3] || 0), t: t, u: 'date', pure: false };
    var m = t.match(/^[^\d\-−+]{0,10}?([\-−+]?\d[\d,]*(?:\.\d+)?)\s?([KMBT](?![A-Za-z]))?\s?([^\d\s（(；;，,／\/]{0,12})/);
    if (!m) return { n: null, t: t };
    var v = Number(m[1].replace(/,/g, '').replace('−', '-'));
    var mult = { K: 1e3, M: 1e6, B: 1e9, T: 1e12 }[m[2]] || 1;
    var rest = t.slice(m[0].length).trim();
    return { n: v * mult, t: t, u: m[3] || '', pure: rest.length === 0 || /^[（(]/.test(rest) };
  }
  function initTable(fig) {
    var table = $('table', fig), body = $('tbody', fig);
    if (!table || !body || fig.hasAttribute('data-plain')) return;
    var rows = $$('tr', body);
    var nrows = rows.length, ncols = Number(fig.getAttribute('data-cols') || 0);
    rows.forEach(function (r, i) { r.setAttribute('data-i', i); });
    var heads = $$('thead th', fig);
    var tools = doc.createElement('div');
    tools.className = 'tbl-tools';
    var left = doc.createElement('span');
    left.className = 'tl';
    var cnt = doc.createElement('span');
    cnt.className = 'cnt';
    left.appendChild(cnt);
    var hint = doc.createElement('span');
    hint.className = 'wide-hint';
    hint.textContent = '可左右捲動';
    hint.hidden = true;
    left.appendChild(hint);
    tools.appendChild(left);
    // long tables open with the first 30 rows; filtering, a deep link or the button shows the rest
    var CLIP = 30, clipped = nrows > 40, more = null;
    function count(shown, q) {
      cnt.textContent = q ? shown + ' / ' + nrows + ' 列' : (body.classList.contains('clip') ? '前 ' + CLIP + ' / ' + nrows + ' 列' : nrows + ' 列');
    }
    function setClip(on) { body.classList.toggle('clip', on); if (more) more.hidden = !on; }
    if (clipped) {
      more = doc.createElement('button');
      more.type = 'button';
      more.className = 'more';
      more.textContent = '顯示全部 ' + nrows + ' 列';
      more.addEventListener('click', function () { clipped = false; setClip(false); count(nrows, ''); });
      body._iaExpand = function () { if (clipped) { clipped = false; setClip(false); count(nrows, ''); } };
      body.classList.add('clip');
    }
    count(nrows, '');
    var filter = null;
    if (nrows >= 8) {
      filter = doc.createElement('input');
      filter.type = 'search';
      filter.placeholder = '篩選列…';
      filter.setAttribute('aria-label', '篩選這張表的列');
      filter.addEventListener('input', function () {
        var q = filter.value.trim().toLowerCase(), shown = 0;
        rows.forEach(function (r) {
          var ok = !q || r.textContent.toLowerCase().indexOf(q) >= 0;
          r.hidden = !ok;
          if (ok) shown++;
        });
        setClip(clipped && !q);
        count(shown, q);
      });
      tools.appendChild(filter);
    }
    var copy = doc.createElement('button');
    copy.type = 'button';
    copy.textContent = '複製';
    copy.title = '把目前顯示的列複製為 TSV，可直接貼進試算表';
    copy.addEventListener('click', function () {
      var lines = [heads.map(function (h) { return h.textContent.trim(); }).join('\t')];
      $$('tr', body).forEach(function (r) {
        if (r.hidden) return;
        lines.push($$('td,th', r).map(function (c) { return c.textContent.replace(/\s+/g, ' ').trim(); }).join('\t'));
      });
      var text = lines.join('\n');
      function done(ok) { copy.textContent = ok ? '已複製' : '無法複製'; setTimeout(function () { copy.textContent = '複製'; }, 1600); }
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(text).then(function () { done(true); }, function () { fallback(); });
      } else fallback();
      function fallback() {
        try {
          var ta = doc.createElement('textarea');
          ta.value = text; ta.style.position = 'fixed'; ta.style.left = '-9999px';
          doc.body.appendChild(ta); ta.select();
          var ok = doc.execCommand('copy');
          doc.body.removeChild(ta); done(ok);
        } catch (e) { done(false); }
      }
    });
    tools.appendChild(copy);
    if (ncols >= 5 || nrows >= 12) {
      var big = doc.createElement('button');
      big.type = 'button';
      big.textContent = '放大';
      big.title = '以全螢幕檢視這張表';
      big.addEventListener('click', function () { enlarge(fig, big); });
      tools.appendChild(big);
    }
    var scroll = $('.tbl-scroll', fig);
    fig.insertBefore(tools, scroll);
    if (more) fig.appendChild(more);
    function measure() {
      if (!scroll.clientWidth) return;
      var wide = scroll.scrollWidth > scroll.clientWidth + 4;
      fig.classList.toggle('is-wide', wide);
      hint.hidden = !wide;
    }
    if (window.ResizeObserver) new ResizeObserver(measure).observe(scroll); else { measure(); window.addEventListener('resize', measure); }
    if (nrows < 3) return;
    heads.forEach(function (th, ci) {
      th.classList.add('sortable');
      th.tabIndex = 0;
      th.setAttribute('role', 'columnheader');
      th.setAttribute('title', '點一下排序');
      function sort() {
        var state = th.getAttribute('aria-sort');
        var next = state === 'descending' ? 'ascending' : state === 'ascending' ? 'none' : 'descending';
        heads.forEach(function (h) { h.removeAttribute('aria-sort'); });
        var cur = $$('tr', body);
        cur.forEach(function (r) { $$('td.bar', r).forEach(function (c) { c.classList.remove('bar'); c.style.removeProperty('--bar'); }); });
        if (next === 'none') {
          cur.sort(function (a, b) { return a.getAttribute('data-i') - b.getAttribute('data-i'); });
        } else {
          th.setAttribute('aria-sort', next);
          var vals = cur.map(function (r) { var c = r.children[ci]; return c ? parseCell(c) : { n: null, t: '' }; });
          var numeric = vals.filter(function (v) { return v.n !== null; }).length >= Math.max(2, 0.6 * vals.filter(function (v) { return v.t; }).length);
          var dir = next === 'ascending' ? 1 : -1;
          var idx = cur.map(function (r, i) { return i; });
          idx.sort(function (a, b) {
            var x = vals[a], y = vals[b];
            if (numeric) {
              if (x.n === null && y.n === null) return a - b;
              if (x.n === null) return 1;
              if (y.n === null) return -1;
              return (x.n - y.n) * dir || a - b;
            }
            return x.t.localeCompare(y.t, 'zh-Hant') * dir || a - b;
          });
          var sorted = idx.map(function (i) { return cur[i]; });
          // proportional bars when the column is one clean, same-unit, non-negative quantity
          if (numeric) {
            var pure = vals.filter(function (v) { return v.n !== null && v.pure && v.u !== 'date'; });
            var units = {};
            pure.forEach(function (v) { units[v.u] = 1; });
            var max = Math.max.apply(null, pure.map(function (v) { return v.n; }));
            var min = Math.min.apply(null, pure.map(function (v) { return v.n; }));
            if (pure.length >= 3 && pure.length >= 0.8 * vals.filter(function (v) { return v.t; }).length && Object.keys(units).length === 1 && min >= 0 && max > 0) {
              cur.forEach(function (r, i) {
                var v = vals[i], c = r.children[ci];
                if (c && v.n !== null && v.pure) { c.classList.add('bar'); c.style.setProperty('--bar', (v.n / max * 100).toFixed(1) + '%'); }
              });
            }
          }
          cur = sorted;
        }
        cur.forEach(function (r) { body.appendChild(r); });
      }
      th.addEventListener('click', sort);
      th.addEventListener('keydown', function (e) { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); sort(); } });
    });
  }
  var dlg = null, dlgBack = null;
  function enlarge(fig, btn) {
    if (!dlg) {
      dlg = doc.createElement('dialog');
      dlg.className = 'tbl-dialog';
      dlg.innerHTML = '<div class="dlg-in"><div class="dlg-bar"><span class="sheet-code">全螢幕檢視 · 按 Esc 關閉</span><button type="button" class="hbtn" id="dlg-x">關閉</button></div><div id="dlg-slot" style="display:flex;flex-direction:column;flex:1 1 auto;min-height:0"></div></div>';
      doc.body.appendChild(dlg);
      $('#dlg-x', dlg).addEventListener('click', function () { dlg.close(); });
      dlg.addEventListener('close', function () {
        var f = $('#dlg-slot .tbl', dlg);
        if (f && dlgBack) { dlgBack.parentNode.insertBefore(f, dlgBack); dlgBack.parentNode.removeChild(dlgBack); }
        dlgBack = null;
        $$('.tbl-tools button', f || doc).forEach(function (b) { if (b.textContent === '還原') b.textContent = '放大'; });
      });
    }
    if (dlg.open) { dlg.close(); return; }
    if (typeof dlg.showModal !== 'function') return;
    dlgBack = doc.createComment('table');
    fig.parentNode.insertBefore(dlgBack, fig);
    $('#dlg-slot', dlg).appendChild(fig);
    btn.textContent = '還原';
    dlg.showModal();
  }
  function initTables() { $$('figure.tbl').forEach(initTable); }

  /* ---------- header search */
  function initSearchForm() {
    var f = $('#hsearch');
    if (!f) return;
    f.addEventListener('submit', function (e) {
      var q = $('input', f).value.trim();
      if (!q) { e.preventDefault(); }
    });
  }

  /* ---------- view switchers: one [data-pane] of the target at a time */
  function initSwitchers() {
    $$('[data-switch]').forEach(function (grp) {
      var host = doc.getElementById(grp.getAttribute('data-switch'));
      if (!host) return;
      function show(view) {
        $$('button[data-view]', grp).forEach(function (b) { b.setAttribute('aria-pressed', String(b.getAttribute('data-view') === view)); });
        $$('[data-pane]', host).forEach(function (p) { p.hidden = p.getAttribute('data-pane') !== view; });
      }
      grp.addEventListener('click', function (e) {
        var b = e.target.closest ? e.target.closest('button[data-view]') : null;
        if (b) show(b.getAttribute('data-view'));
      });
      var first = $('button[data-view]', grp);
      if (first) show(first.getAttribute('data-view'));
    });
  }

  function init() { initTheme(); initMenu(); initTables(); initSwitchers(); initTabs(); initSearchForm(); }
  if (doc.readyState === 'loading') doc.addEventListener('DOMContentLoaded', init); else init();
  window.IA = { reveal: reveal, selectTab: selectTab, $: $, $$: $$, store: store };
})();
