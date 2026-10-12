/* Sources page: 777 cited sources with the chapters that cite them and how each was verified. */
(function () {
  'use strict';
  var D = window.IA_SOURCES, host = document.getElementById('sources');
  if (!D || !host) return;
  var CH = window.IA_CHAPTERS || {};
  var VS = { local: '已比對本地副本', web: '線上逐句核對', unreadable: '無法重讀' };
  var st = { q: '', ch: '', vs: '', limit: 150 };
  try { var p = new URLSearchParams(location.search); if (p.get('q')) st.q = p.get('q'); if (p.get('ch')) st.ch = p.get('ch'); if (p.get('vs')) st.vs = p.get('vs'); } catch (e) { /* no query */ }
  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }
  function host_(u) { var m = u.match(/^https?:\/\/([^\/]+)/); return m ? m[1].replace(/^www\./, '') : ''; }
  host.innerHTML =
    '<div class="sbox"><input type="search" id="src-q" placeholder="搜尋來源名稱或網址，例如 vllm、inferencex、bedrock" aria-label="搜尋來源">' +
    '<select id="src-ch" aria-label="章節"><option value="">全部章節</option>' + Object.keys(CH).map(function (k) { return '<option value="' + k + '">第 ' + Number(k) + ' 章 ' + esc(CH[k].nav) + '</option>'; }).join('') + '</select>' +
    '<select id="src-vs" aria-label="查核方式"><option value="">全部查核方式</option><option value="local">已比對本地副本</option><option value="web">線上逐句核對</option><option value="unreadable">無法重讀</option></select></div>' +
    '<div class="keyrow" id="src-cnt" role="status"></div><ul class="srclist" id="src-list"></ul><button type="button" class="more" id="src-more" hidden>顯示更多</button>';
  var $ = function (id) { return document.getElementById(id); };
  $('src-q').value = st.q; $('src-ch').value = st.ch; $('src-vs').value = st.vs;
  function render() {
    var terms = st.q.toLowerCase().split(/\s+/).filter(Boolean);
    var rows = D.filter(function (s) {
      if (st.ch && s.c.indexOf(st.ch) < 0) return false;
      if (st.vs && s.s !== st.vs) return false;
      if (!terms.length) return true;
      var hay = (s.n.join(' ') + ' ' + s.u).toLowerCase();
      return terms.every(function (t) { return hay.indexOf(t) >= 0; });
    });
    var c = { local: 0, web: 0, unreadable: 0 };
    rows.forEach(function (s) { c[s.s]++; });
    $('src-cnt').innerHTML = '<span class="mono">' + rows.length + ' / ' + D.length + ' 個來源</span><span><span class="vs vs-local">' + VS.local + '</span> ' + c.local + '</span><span><span class="vs vs-web">' + VS.web + '</span> ' + c.web + '</span><span><span class="vs vs-unreadable">' + VS.unreadable + '</span> ' + c.unreadable + '</span>';
    $('src-list').innerHTML = rows.slice(0, st.limit).map(function (s) {
      return '<li><span><a href="' + esc(s.u) + '" target="_blank" rel="noopener">' + esc(s.n[0]) + '</a>' + (s.n.length > 1 ? ' <span style="color:var(--mute);font-size:12px">（另稱 ' + esc(s.n.slice(1, 4).join('、')) + '）</span>' : '') + '</span>' +
        '<span class="m"><span class="vs vs-' + s.s + '">' + VS[s.s] + '</span><span class="chs">' + s.c.map(function (k) { return CH[k] ? '<a href="' + CH[k].slug + '.html" title="第 ' + Number(k) + ' 章 ' + esc(CH[k].nav) + '">' + k + '</a>' : ''; }).join('') + '</span></span>' +
        '<span class="u">' + esc(host_(s.u)) + ' · ' + esc(s.u.length > 150 ? s.u.slice(0, 150) + '…' : s.u) + '</span></li>';
    }).join('') || '<li><span>沒有符合的來源。</span></li>';
    $('src-more').hidden = rows.length <= st.limit;
    $('src-more').textContent = '顯示更多（還有 ' + (rows.length - st.limit) + ' 個）';
  }
  $('src-q').addEventListener('input', function (e) { st.q = e.target.value; st.limit = 150; render(); });
  $('src-ch').addEventListener('change', function (e) { st.ch = e.target.value; st.limit = 150; render(); });
  $('src-vs').addEventListener('change', function (e) { st.vs = e.target.value; st.limit = 150; render(); });
  $('src-more').addEventListener('click', function () { st.limit += 300; render(); });
  render();
})();
