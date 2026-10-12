/* Technique matrix (chapter 6): 34 techniques x 6 accelerators. Data comes from the chapter tables at build time. */
(function () {
  'use strict';
  var D = window.IA_MATRIX, host = document.getElementById('matrix');
  if (!D || !host) return;
  var ST = {
    s: { label: '● 支援', word: '支援', cls: 'st-s' },
    p: { label: '△ 部分', word: '部分', cls: 'st-p' },
    e: { label: '◇ 實驗', word: '實驗', cls: 'st-e' },
    n: { label: '× 不支援', word: '不支援', cls: 'st-n' },
    u: { label: '– 查無', word: '查無', cls: 'st-u' }
  };
  var st = { focus: 'trn', group: -1, gaps: false, open: null };
  (function fromHash() {
    var m = (location.hash || '').match(/row=([\w-]+)/);
    if (m) st.open = m[1];
    var f = (location.hash || '').match(/chip=(\w+)/);
    if (f && D.fams.some(function (x) { return x.id === f[1]; })) st.focus = f[1];
  })();
  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }
  function fi() { for (var i = 0; i < D.fams.length; i++) if (D.fams[i].id === st.focus) return i; return 0; }
  function tag(f) { return '<span class="fam fam-' + f.cls + '">' + f.tag + '</span>'; }

  host.innerHTML =
    '<section class="block"><div class="sec-h"><h3 style="font-size:18px">選一種晶片</h3><span class="sub">選中的欄會在矩陣裡以琥珀色標出；數字隨下方的群組篩選更新</span></div>' +
    '<div class="fams" id="mx-fams" role="group" aria-label="晶片"></div>' +
    '<div class="keyrow"><span><i class="sw teal" style="width:14px;height:8px"></i>支援</span><span><i class="sw tl" style="width:14px;height:8px"></i>部分或實驗</span><span><i class="sw tr" style="width:14px;height:8px"></i>不支援或查無</span></div></section>' +
    '<section class="block"><div class="mx-ctl"><div class="seg" id="mx-groups" role="group" aria-label="技術群組"></div>' +
    '<label><input type="checkbox" id="mx-gaps"><span id="mx-gapl"></span></label><span class="cnt" id="mx-cnt"></span></div>' +
    '<div class="mx-scroll" tabindex="0" role="region" aria-label="技術支援矩陣"><div class="mx" id="mx-grid" role="table" aria-label="技術支援矩陣"></div></div></section>';

  var el = function (id) { return document.getElementById(id); };

  function render() {
    var f = fi(), focus = D.fams[f];
    var inGroup = D.rows.filter(function (r) { return st.group < 0 || r.g === st.group; });
    var visible = inGroup.filter(function (r) { return !st.gaps || r.st[f] !== 's'; });
    el('mx-fams').innerHTML = D.fams.map(function (fm, i) {
      var c = { s: 0, p: 0, e: 0, n: 0, u: 0 };
      inGroup.forEach(function (r) { c[r.st[i]]++; });
      var tot = inGroup.length || 1;
      return '<button type="button" class="famb" data-f="' + fm.id + '" aria-pressed="' + (fm.id === st.focus) + '"><span class="fh">' + tag(fm) + esc(fm.name) + '</span>' +
        '<span class="fc">' + c.s + '<span class="ft"> / ' + inGroup.length + '</span></span>' +
        '<span class="fbar"><i class="s" style="width:' + (c.s / tot * 100).toFixed(1) + '%"></i><i class="p" style="width:' + ((c.p + c.e) / tot * 100).toFixed(1) + '%"></i></span>' +
        '<span class="fe">' + esc(fm.engine) + '</span></button>';
    }).join('');
    el('mx-groups').innerHTML = [['全部', D.rows.length, -1]].concat(D.groups.map(function (g, i) { return [g, D.rows.filter(function (r) { return r.g === i; }).length, i]; })).map(function (g) {
      return '<button type="button" data-g="' + g[2] + '" aria-pressed="' + (st.group === g[2]) + '">' + esc(g[0]) + ' <span class="mono" style="font-size:12px">' + g[1] + '</span></button>';
    }).join('');
    el('mx-gaps').checked = st.gaps;
    el('mx-gapl').textContent = '只看 ' + focus.name + ' 不是「支援」的列';
    el('mx-cnt').textContent = '顯示 ' + visible.length + ' / ' + D.rows.length + ' 列';
    var html = '<div class="mx-r" role="row"><span class="mx-h0" role="columnheader">技術（點一列看限定條件與來源）</span>' +
      D.fams.map(function (fm, i) { return '<span class="mx-h' + (i === f ? ' on' : '') + '" role="columnheader"><span>' + tag(fm) + '</span><span>' + esc(fm.name) + '</span><small>' + esc(fm.engine) + '</small></span>'; }).join('') + '</div>';
    var lastG = -2;
    visible.forEach(function (r) {
      if (r.g !== lastG) { html += '<div role="row"><span class="mx-g" role="columnheader" style="display:block">' + esc(D.groups[r.g]) + '</span></div>'; lastG = r.g; }
      var open = st.open === r.id;
      html += '<div id="row-' + r.id + '" style="display:flex;flex-direction:column;gap:2px"><div class="mx-r" role="row"><span role="rowheader" style="display:flex"><button type="button" class="mx-n" data-row="' + r.id + '" aria-expanded="' + open + '"><span>' + r.name + '</span><span class="pm" aria-hidden="true">' + (open ? '−' : '+') + '</span></button></span>' +
        D.fams.map(function (fm, i) { var s = ST[r.st[i]]; return '<span class="mx-c ' + s.cls + (i === f ? ' focus' : '') + '" role="cell">' + s.label + '</span>'; }).join('') + '</div>';
      if (open) {
        html += '<div class="mx-d"><div class="mx-dg">' + D.fams.map(function (fm, i) {
          var s = ST[r.st[i]];
          return '<div class="mx-di"><span class="h">' + tag(fm) + '<b>' + esc(fm.name) + '</b><span class="st ' + s.cls + '">' + s.word + '</span></span><span class="nt">' + (r.notes[i] || '') + '</span></div>';
        }).join('') + '</div><div class="mx-src"><span class="k">來源</span>' + r.src.map(function (s) { return '<a href="' + esc(s[1]) + '" target="_blank" rel="noopener">' + esc(s[0]) + '</a>'; }).join('') + '</div></div>';
      }
      html += '</div>';
    });
    if (!visible.length) html += '<div style="padding:24px 18px;background:var(--surface);font-size:14px">這個群組裡，' + esc(focus.name) + ' 的每一項都列為「支援」。</div>';
    el('mx-grid').innerHTML = html;
  }

  host.addEventListener('click', function (e) {
    var b = e.target.closest('button'); if (!b) return;
    if (b.dataset.f) { st.focus = b.dataset.f; render(); }
    else if (b.dataset.g !== undefined) { st.group = Number(b.dataset.g); render(); }
    else if (b.dataset.row) { st.open = st.open === b.dataset.row ? null : b.dataset.row; render(); var nb = host.querySelector('[data-row="' + b.dataset.row + '"]'); if (nb) nb.focus(); }
  });
  host.addEventListener('change', function (e) { if (e.target.id === 'mx-gaps') { st.gaps = e.target.checked; render(); } });
  document.addEventListener('click', function (e) {
    var j = e.target.closest ? e.target.closest('[data-jump]') : null; if (!j) return;
    st.open = j.getAttribute('data-jump'); st.group = -1; st.gaps = false;
    if (j.getAttribute('data-focus')) st.focus = j.getAttribute('data-focus');
    render();
    var row = document.getElementById('row-' + st.open);
    if (row && window.IA) window.IA.reveal(row, true);
  });
  render();
  if (st.open) { var r0 = document.getElementById('row-' + st.open); if (r0 && window.IA) setTimeout(function () { window.IA.reveal(r0, true); }, 50); }
})();
