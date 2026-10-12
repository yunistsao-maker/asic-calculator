/* Long context (chapter 7): KV bars with a 200K / 1M switch, and the per-sequence KV calculator.
   Data (window.IA_KV) is parsed from table 7-1 of the chapter at build time. */
(function () {
  'use strict';
  var D = window.IA_KV;
  if (!D) return;
  var GIB = 1073741824;
  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }
  function fmt(x, d) { return x.toLocaleString('en-US', { minimumFractionDigits: d, maximumFractionDigits: d }); }

  /* ---- bars */
  var bars = document.getElementById('kv-bars');
  if (bars) {
    var mode = 'm';
    var draw = function () {
      var key = mode === 'k' ? 'k200' : 'm1';
      var rows = D.slice().sort(function (a, b) { return b.m1 - a.m1; });
      var max = rows[0][key];
      bars.innerHTML = rows.map(function (r) {
        return '<div class="brow"><span class="lab"><b>' + esc(r.model) + '</b><small>' + esc(r.prec) + ' · ' + fmt(r.b, 0) + ' B/token</small></span>' +
          '<span class="bar"><i style="width:' + (r[key] / max * 82).toFixed(2) + '%"></i><span>' + r[key].toFixed(2) + ' GiB</span></span></div>';
      }).join('');
      document.querySelectorAll('#kv-toggle button').forEach(function (b) { b.setAttribute('aria-pressed', String(b.getAttribute('data-m') === mode)); });
    };
    var tg = document.getElementById('kv-toggle');
    if (tg) tg.addEventListener('click', function (e) { var b = e.target.closest('button'); if (b) { mode = b.getAttribute('data-m'); draw(); } });
    draw();
  }

  /* ---- calculator */
  var calc = document.getElementById('kv-calc');
  if (!calc) return;
  var st = { i: 0, n: 200000, seq: 16, pool: 42.23 };
  for (var j = 0; j < D.length; j++) if (D[j].model === 'Kimi K3' && D[j].prec === 'FP8') st.i = j;
  var PRE = [[32768, '32K'], [131072, '128K'], [200000, '200K'], [262144, '256K'], [524288, '512K'], [1048576, '1M']];
  var lo = Math.log(8192), hi = Math.log(1048576);
  calc.innerHTML =
    '<div class="pl"><section class="pl-in" aria-label="輸入" style="flex:1 1 280px"><div class="bar-t">輸入 INPUTS</div>' +
    '<div class="fld"><div class="fld-h"><label for="kc-m">模型與 KV 精度</label></div><select id="kc-m" class="sel" style="min-height:44px">' +
      D.map(function (r, i) { return '<option value="' + i + '">' + esc(r.model + ' · ' + r.prec) + '</option>'; }).join('') + '</select>' +
      '<small id="kc-mp"></small></div>' +
    '<div class="fld"><div class="fld-h"><label for="kc-n">context 長度 n</label><span class="big" id="kc-nv"></span></div>' +
      '<input id="kc-n" type="range" min="0" max="1000" step="1"><div class="seg mono" id="kc-pre" role="group" aria-label="context 預設值">' +
      PRE.map(function (p) { return '<button type="button" data-n="' + p[0] + '">' + p[1] + '</button>'; }).join('') + '</div><small>對數刻度，8,192 至 1,048,576 tokens；本章的 200K 是 200,000、1M 是 1,048,576</small></div>' +
    '<div class="fld"><div class="numin"><label>同時常駐的序列數<input id="kc-s" type="number" min="1" max="100000" step="1"></label>' +
      '<label>KV 預算（GiB）<input id="kc-p" type="number" min="0" step="0.5"></label></div>' +
      '<small>KV 預算填引擎扣掉權重後回報的 KV 容量。預設的 42.23 GiB 是 Kimi K3 在 8× B300、TP8、FP8 KV 的實測值。</small></div></section>' +
    '<div class="pl-out" style="flex:2 1 380px"><section class="peak" aria-live="polite"><div class="peak-top"><div style="display:flex;flex-direction:column;gap:6px"><span class="k">一條序列的 KV</span><span class="v" style="font-size:44px"><span class="hl" id="kc-one"></span></span></div>' +
      '<div class="s"><span id="kc-form" class="mono" style="font-size:12px"></span><span><span class="g g-d" title="等級 D：本文推算，附算式">D</span> n × b + b_s</span></div></div>' +
      '<div class="peak-g"><div class="peak-c"><span class="k">不含固定 state</span><span class="v" id="kc-kv"></span><span class="s">n × b</span></div>' +
      '<div class="peak-c"><span class="k">每序列固定 state</span><span class="v" id="kc-st"></span><span class="s" id="kc-stn"></span></div>' +
      '<div class="peak-c"><span class="k" id="kc-tl"></span><span class="v" id="kc-tot"></span><span class="s">序列數 × 每條 KV</span></div>' +
      '<div class="peak-c"><span class="k">這個預算放得下</span><span class="v" id="kc-fit"></span><span class="s" id="kc-fitn"></span></div></div>' +
      '<p class="peak-n">序列數是上限：沒有扣掉碎片，也沒有扣掉為了維持命中率而保留的閒置 session。tensor parallel 下 MLA 的 latent KV 每個 rank 各存一份，預算要填單一份 KV 的容量；DCP 或 DEP 才會讓容量隨 rank 數增加。</p></section></div></div>';
  var $ = function (id) { return document.getElementById(id); };
  function upd() {
    var r = D[st.i], kv = st.n * r.b / GIB, sb = r.state / GIB, one = kv + sb;
    $('kc-m').value = st.i;
    $('kc-mp').textContent = 'b = ' + fmt(r.b, 0) + ' bytes/token' + (r.state ? '；b_s = ' + r.stateText : '；沒有每序列固定 state');
    $('kc-nv').textContent = fmt(st.n, 0);
    $('kc-n').value = Math.round((Math.log(st.n) - lo) / (hi - lo) * 1000);
    document.querySelectorAll('#kc-pre button').forEach(function (b) { b.setAttribute('aria-pressed', String(Number(b.getAttribute('data-n')) === st.n)); });
    $('kc-s').value = st.seq; $('kc-p').value = st.pool;
    $('kc-one').textContent = one.toFixed(2) + ' GiB';
    $('kc-form').textContent = fmt(st.n, 0) + ' × ' + fmt(r.b, 0) + ' B' + (r.state ? ' + ' + fmt(r.state / 1048576, 0) + ' MiB' : '');
    $('kc-kv').textContent = kv.toFixed(2) + ' GiB';
    $('kc-st').textContent = r.state ? fmt(r.state / 1048576, 0) + ' MiB' : '無';
    $('kc-stn').textContent = r.state ? '不隨 n 成長' : '';
    $('kc-tl').textContent = fmt(st.seq, 0) + ' 條同時常駐';
    var tot = one * st.seq;
    $('kc-tot').textContent = tot >= 1024 ? (tot / 1024).toFixed(2) + ' TiB' : tot.toFixed(1) + ' GiB';
    var fit = one > 0 ? st.pool / one : 0;
    $('kc-fit').textContent = (fit >= 10 ? Math.floor(fit) : Math.floor(fit * 10) / 10) + ' 條';
    $('kc-fitn').textContent = fmt(st.pool, 2) + ' GiB ÷ ' + one.toFixed(2) + ' GiB' + (fit < 1 ? '；放不下一條' : '');
  }
  calc.addEventListener('input', function (e) {
    var t = e.target;
    if (t.id === 'kc-n') { st.n = Math.round(Math.exp(lo + Number(t.value) / 1000 * (hi - lo)) / 1024) * 1024; upd(); }
  });
  calc.addEventListener('change', function (e) {
    var t = e.target;
    if (t.id === 'kc-m') st.i = Number(t.value);
    else if (t.id === 'kc-s') st.seq = Math.max(1, Math.round(Number(t.value)) || 1);
    else if (t.id === 'kc-p') st.pool = Math.max(0, Number(t.value) || 0);
    upd();
  });
  calc.addEventListener('click', function (e) { var b = e.target.closest('button[data-n]'); if (b) { st.n = Number(b.getAttribute('data-n')); upd(); } });
  upd();
})();
