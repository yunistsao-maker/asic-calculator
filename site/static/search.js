/* Full-text search over every chapter. The index (assets/search-index.js) is loaded only on this page. */
(function () {
  'use strict';
  var I = window.IA_INDEX, host = document.getElementById('search');
  if (!I || !host) return;
  var st = { q: '', page: '', limit: 60 };
  try { var p = new URLSearchParams(location.search); if (p.get('q')) st.q = p.get('q'); } catch (e) { /* no query */ }
  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }
  host.innerHTML =
    '<div class="sbox"><input type="search" id="q" placeholder="例如 MLA、Capacity Blocks、TTFT p50、131,072" aria-label="搜尋全站" autocomplete="off">' +
    '<select id="pg" aria-label="限定章節"><option value="">全部章節</option>' + I.pages.map(function (pg, i) { return '<option value="' + i + '">' + esc(pg.n + ' ' + pg.t) + '</option>'; }).join('') + '</select></div>' +
    '<div class="keyrow" id="s-cnt" role="status"></div><div class="res" id="res"></div><button type="button" class="more" id="s-more" hidden>顯示更多</button>';
  var $ = function (id) { return document.getElementById(id); };
  var KIND = { p: '段落', r: '表格列', c: '表格標題', h: '標題' };
  var low = null;
  function run() {
    var q = st.q.trim();
    if (q.length < 2 && !/[一-鿿]/.test(q)) { $('res').innerHTML = '<div class="none">輸入至少兩個字元。多個詞以空白分隔，結果必須同時包含每個詞；數字可以含千分位，例如 4,764。</div>'; $('s-cnt').textContent = ''; $('s-more').hidden = true; return; }
    if (!low) low = I.e.map(function (e) { return e[5].toLowerCase(); });
    var terms = q.toLowerCase().split(/\s+/).filter(Boolean);
    var hits = [];
    for (var i = 0; i < low.length; i++) {
      var e = I.e[i];
      if (st.page !== '' && e[0] !== Number(st.page)) continue;
      var t = low[i], ok = true, first = -1;
      for (var k = 0; k < terms.length; k++) { var at = t.indexOf(terms[k]); if (at < 0) { ok = false; break; } if (first < 0 || at < first) first = at; }
      if (!ok) continue;
      var score = (e[4] === 'h' ? 0 : e[4] === 'c' ? 1 : 2) * 1e6 + i;
      if (t.indexOf(q.toLowerCase()) >= 0) score -= 5e5;
      hits.push([score, i, first]);
    }
    hits.sort(function (a, b) { return a[0] - b[0]; });
    $('s-cnt').innerHTML = '<span class="mono">' + hits.length + ' 筆</span>';
    var rx = new RegExp('(' + terms.map(function (t) { return t.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'); }).join('|') + ')', 'gi');
    $('res').innerHTML = hits.slice(0, st.limit).map(function (h) {
      var e = I.e[h[1]], pg = I.pages[e[0]], tab = pg.tabs[e[1]] || { t: '' };
      var sub = e[2] >= 0 && tab.subs ? tab.subs[e[2]] : '';
      var txt = e[5], a = Math.max(0, h[2] - 70), b = Math.min(txt.length, h[2] + 190);
      var snip = (a > 0 ? '…' : '') + txt.slice(a, b) + (b < txt.length ? '…' : '');
      return '<a class="hit" href="' + pg.f + '#' + e[3] + '"><span class="path">' + esc(pg.n + ' ' + pg.t) + (tab.t ? ' › ' + esc(tab.t) : '') + (sub ? ' › ' + esc(sub) : '') + ' · ' + KIND[e[4]] + '</span><span class="snip">' + esc(snip).replace(rx, '<mark>$1</mark>') + '</span></a>';
    }).join('') || '<div class="none">找不到「' + esc(q) + '」。試試英文術語（例如 prefix caching）或較短的詞。</div>';
    $('s-more').hidden = hits.length <= st.limit;
    $('s-more').textContent = '顯示更多（還有 ' + (hits.length - st.limit) + ' 筆）';
  }
  var timer = null;
  $('q').value = st.q;
  $('q').addEventListener('input', function (e) { st.q = e.target.value; st.limit = 60; clearTimeout(timer); timer = setTimeout(function () { run(); try { history.replaceState(null, '', '?q=' + encodeURIComponent(st.q)); } catch (err) { /* ignore */ } }, 140); });
  $('pg').addEventListener('change', function (e) { st.page = e.target.value; st.limit = 60; run(); });
  $('s-more').addEventListener('click', function () { st.limit += 120; run(); });
  run();
  $('q').focus();
})();
