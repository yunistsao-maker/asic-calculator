/* Capacity planner UI (chapter 10). The maths lives in planner-model.js.
   Form controls are created once and updated in place, so focus survives every recalculation. */
(function () {
  'use strict';
  var M = window.IA_MODEL, host = document.getElementById('planner');
  if (!M || !host) return;
  var h = M.h, KEYS = M.KEYS, ROLES = M.ROLES;
  var DEF = { n: 100000, se: 12, rd: 18, lv: { OA: 'base', SE: 'base', RD: 'base' }, tz: 'single', mx: 'MX2',
    adv: { d: 1.2, kFloor: 1.15, fu: 1.18, fc: 1.04, fo: 1.06, v: 80, util: 0.8, price: 0.72, sSingle: 0.11, sGlobal: 0.065 },
    custom: {}, cmixRaw: null };
  function clone(o) { return JSON.parse(JSON.stringify(o)); }
  var st = clone(DEF), last = null;

  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }
  function int(x) { return Math.round(x).toLocaleString('en-US'); }
  function pct(x) { return (x === 0 ? '0' : x * 100 >= 10 ? (x * 100).toFixed(0) : (x * 100).toFixed(1)) + '%'; }
  function times(x) { return (x < 0.01 ? '<0.01' : x.toFixed(2)) + '×'; }
  function bytes(b) { return b >= 1e12 ? h(b / 1e12) + ' TB' : h(b / 1e9) + ' GB'; }
  function nice(x) { var mag = Math.pow(10, Math.floor(Math.log10(x)) - 1); return Math.round(x / mag) * mag; }
  function clamp(x, a, b) { return Math.min(b, Math.max(a, x)); }
  function each(list, fn) { Array.prototype.forEach.call(list, fn); }
  var $ = function (id) { return document.getElementById(id); };

  /* ----- routing */
  function seedCmix(base) {
    st.cmixRaw = {};
    KEYS.forEach(function (r) { st.cmixRaw[r] = {}; M.MODEL_ORDER.forEach(function (k) { st.cmixRaw[r][k] = Math.round(((base[r] || {})[k] || 0) * 100); }); });
  }
  function rowSum(r) { var s = 0; M.MODEL_ORDER.forEach(function (k) { s += st.cmixRaw[r][k] || 0; }); return s; }
  function mixDef() {
    if (st.mx !== 'custom') return M.MIXES.filter(function (x) { return x.id === st.mx; })[0];
    var out = { id: 'custom', label: '自訂路由' };
    KEYS.forEach(function (r) {
      var sum = rowSum(r);
      out[r] = {};
      if (sum <= 0) { out[r].k3 = 1; return; }
      M.MODEL_ORDER.forEach(function (k) { if (st.cmixRaw[r][k] > 0) out[r][k] = st.cmixRaw[r][k] / sum; });
    });
    return out;
  }

  /* ----- state <-> link */
  function encode() {
    var q = ['n=' + st.n, 'se=' + st.se, 'rd=' + st.rd, 'lv=' + KEYS.map(function (r) { return st.lv[r]; }).join(','), 'tz=' + st.tz, 'mx=' + st.mx];
    Object.keys(DEF.adv).forEach(function (k) { if (st.adv[k] !== DEF.adv[k]) q.push(k + '=' + st.adv[k]); });
    KEYS.forEach(function (r) { if (st.lv[r] === 'custom' && st.custom[r]) q.push('c' + r + '=' + st.custom[r].join(',')); });
    if (st.mx === 'custom' && st.cmixRaw) {
      q.push('cm=' + KEYS.map(function (r) { return M.MODEL_ORDER.map(function (m) { return st.cmixRaw[r][m] || 0; }).join('.'); }).join('_'));
    }
    return q.join('&');
  }
  function decode(qs) {
    qs.split('&').forEach(function (kv) {
      var i = kv.indexOf('='); if (i < 0) return;
      var k = kv.slice(0, i), v = kv.slice(i + 1);
      try { v = decodeURIComponent(v); } catch (e) { return; }
      if (k === 'n') st.n = clamp(Math.round(Number(v)) || DEF.n, 100, 2000000);
      else if (k === 'se') st.se = clamp(Math.round(Number(v)) || 0, 0, 100);
      else if (k === 'rd') st.rd = clamp(Math.round(Number(v)) || 0, 0, 100);
      else if (k === 'lv') v.split(',').forEach(function (x, j) { if (KEYS[j] && /^(low|base|high|custom)$/.test(x)) st.lv[KEYS[j]] = x; });
      else if (k === 'tz' && /^(single|global)$/.test(v)) st.tz = v;
      else if (k === 'mx' && /^(MX[1-4]|custom)$/.test(v)) st.mx = v;
      else if (Object.prototype.hasOwnProperty.call(DEF.adv, k) && v !== '' && isFinite(Number(v))) st.adv[k] = Number(v);
      else if (/^c(OA|SE|RD)$/.test(k)) {
        var a = v.split(',').map(Number);
        if (a.length === 5 && a.every(function (x) { return isFinite(x) && x >= 0; })) { a[0] = clamp(a[0], 0, 1); st.custom[k.slice(1)] = a; }
      }
      else if (k === 'cm') {
        var rows = v.split('_'); st.cmixRaw = {};
        KEYS.forEach(function (r, j) {
          var parts = (rows[j] || '').split('.'); st.cmixRaw[r] = {};
          M.MODEL_ORDER.forEach(function (mk, m) { st.cmixRaw[r][mk] = clamp(Math.round(Number(parts[m])) || 0, 0, 100); });
        });
      }
    });
    if (st.se + st.rd > 100) st.rd = 100 - st.se;
    KEYS.forEach(function (r) { if (st.lv[r] === 'custom' && !st.custom[r]) st.lv[r] = 'base'; });
    if (st.mx === 'custom' && !st.cmixRaw) st.mx = 'MX2';
  }
  function fromUrl() {
    var hsh = location.hash || '', i = hsh.indexOf('?');
    if (i >= 0) { decode(hsh.slice(i + 1)); return true; }
    if (location.search.length > 1 && /(^|[?&])n=/.test(location.search)) { decode(location.search.slice(1)); return true; }
    return false;
  }
  fromUrl();

  /* ----- model call */
  function params(r) { return st.lv[r] === 'custom' ? st.custom[r] : ROLES[r].lv[st.lv[r]]; }
  function run() {
    var custom = {};
    KEYS.forEach(function (r) { if (st.lv[r] === 'custom') custom[r] = st.custom[r]; });
    return M.compute({
      n: st.n, share: { OA: (100 - st.se - st.rd) / 100, SE: st.se / 100, RD: st.rd / 100 },
      level: st.lv, custom: custom, s: st.tz === 'single' ? st.adv.sSingle : st.adv.sGlobal,
      peak: { d: st.adv.d, kFloor: st.adv.kFloor, fu: st.adv.fu, fc: st.adv.fc, fo: st.adv.fo, v: st.adv.v, util: st.adv.util, price: st.adv.price },
      mix: mixDef()
    });
  }

  /* ----- skeleton (built once) */
  var roleSw = { OA: 'oa', SE: 'se', RD: 'rd' };
  var NP = [1000, 10000, 50000, 100000];
  var LV = ['low', 'base', 'high', 'custom'];
  var CUST = [['a（%）', 1], ['r', 1], ['u', 50], ['c', 50], ['o', 10]];
  var ADV = [['d', 'P95 平日係數 d', 0.05, 1, 2], ['kFloor', 'k 的下限', 0.01, 1, 2], ['fu', 'f_u', 0.01, 1, 2], ['fc', 'f_c', 0.01, 1, 2], ['fo', 'f_o', 0.01, 1, 2],
    ['v', 'v（tokens/s）', 10, 10, 2000], ['util', '使用率上限', 0.05, 0.3, 1], ['price', '實付均價（$ / 1M）', 0.01, 0, 100], ['sSingle', 's：單一時區', 0.005, 0.03, 0.3], ['sGlobal', 's：全球分散', 0.005, 0.03, 0.3]];
  function btn(attrs, label) { return '<button type="button" ' + attrs + ' aria-pressed="false">' + label + '</button>'; }
  function roleBox(r) {
    return '<div class="role" data-role="' + r + '"><div class="role-h"><span class="role-n"><span class="sw ' + roleSw[r] + '"></span><b>' + esc(ROLES[r].name) + '</b><small></small></span>' +
      '<div class="seg mono" role="group" aria-label="' + esc(ROLES[r].name) + ' 用量級">' + LV.map(function (l) { return btn('data-r="' + r + '" data-l="' + l + '"', l === 'custom' ? '自訂' : l); }).join('') + '</div></div>' +
      '<span class="role-p"></span>' +
      '<div class="numin" hidden>' + CUST.map(function (f, i) { return '<label>' + f[0] + '<input type="number" min="0" step="' + f[1] + '" data-cr="' + r + '" data-ci="' + i + '"></label>'; }).join('') + '</div></div>';
  }
  host.innerHTML =
    '<p class="vh" role="status" id="pl-live"></p>' +
    '<div class="pl">' +
    '<section class="pl-in" aria-label="輸入">' +
      '<div class="bar-t">輸入 INPUTS</div>' +
      '<div class="fld"><div class="fld-h"><label for="pl-n-num">員工數</label><input id="pl-n-num" class="big" type="text" inputmode="numeric" autocomplete="off" style="width:9.5ch;border:0;border-bottom:1px solid var(--ink);background:transparent;text-align:right"></div>' +
        '<input id="pl-n" type="range" min="0" max="250" step="1" aria-label="員工數（對數刻度）">' +
        '<div class="seg mono" id="pl-np" role="group" aria-label="員工數預設值">' + NP.map(function (v) { return btn('data-n="' + v + '"', int(v)); }).join('') + '</div>' +
        '<small>滑桿為對數刻度，1,000 至 320,000 人；右上的數字可以直接輸入</small></div>' +
      '<div class="fld"><div class="fld-h"><span class="l">角色組合</span><span id="pl-mixname" style="font-size:13px;color:var(--ink2)"></span></div>' +
        '<div class="btns" id="pl-presets" role="group" aria-label="角色組合預設值">' + M.ROLE_MIXES.map(function (p) { return btn('data-p="' + p.id + '"', esc(p.label)); }).join('') + '</div>' +
        '<div><div class="fld-h"><label for="pl-se" style="font-size:13px;font-weight:400">Coding 占比</label><span class="v" id="pl-sev"></span></div><input id="pl-se" type="range" min="0" max="100" step="1"></div>' +
        '<div><div class="fld-h"><label for="pl-rd" style="font-size:13px;font-weight:400">R&amp;D 占比</label><span class="v" id="pl-rdv"></span></div><input id="pl-rd" type="range" min="0" max="100" step="1"></div>' +
        '<div class="fld-h"><span style="font-size:13px">OA 占比（其餘）</span><span class="v" id="pl-oav"></span></div></div>' +
      '<div class="fld"><span class="l" style="font-size:14px;font-weight:600">每個角色的用量級</span><div id="pl-roles" style="display:flex;flex-direction:column;gap:12px">' + KEYS.map(roleBox).join('') + '</div>' +
        '<small>a 平日活躍占比；r 每活躍日的呼叫數；u 未快取輸入、c cache read、o 輸出，單位是每次呼叫的 tokens。三個級別都是全體平均，不是使用者的百分位。選「自訂」可以填入自己的遙測值。</small></div>' +
      '<div class="fld"><span class="l" style="font-size:14px;font-weight:600">時區分布</span><div class="btns" id="pl-tz" role="group" aria-label="時區分布">' + btn('data-tz="single"', '') + btn('data-tz="global"', '') + '</div><small>s 是一日中最忙的一小時占全日用量的比例</small></div>' +
      '<div class="fld"><details class="adv" id="pl-adv"><summary>進階參數</summary><div class="numin" id="pl-advin" style="margin-top:8px">' +
        ADV.map(function (f) { return '<label>' + f[1] + '<input type="number" data-adv="' + f[0] + '" step="' + f[2] + '" min="' + f[3] + '" max="' + f[4] + '"></label>'; }).join('') + '</div>' +
        '<div style="margin-top:10px"><button type="button" class="more" id="pl-reset" style="min-height:40px">全部重設為預設值</button></div></details>' +
        '<span class="role-p" id="pl-fixed"></span></div>' +
    '</section>' +
    '<div class="pl-out" id="pl-out"></div>' +
    '</div>' +
    '<section class="block" id="pl-mix">' +
      '<div class="sec-h"><h3 style="font-size:22px">模型組合</h3><span class="sub">每個角色的呼叫依比例分到各模型池；每個池各自計算 k、TPM 與在途數</span></div>' +
      '<div class="seg" role="group" aria-label="路由情境" id="pl-mx">' + M.MIXES.map(function (x) { return btn('data-mx="' + x.id + '"', esc(x.label)); }).join('') + btn('data-mx="custom"', '自訂路由') + '</div>' +
      '<figure class="tbl" id="pl-editor" hidden><figcaption>每個角色的呼叫分到各模型的百分比。每列合計不是 100 時，按比例調整成 100。</figcaption><div class="tbl-scroll"><table style="min-width:640px"><thead><tr><th scope="col">角色</th>' +
        M.MODEL_ORDER.map(function (k) { return '<th scope="col">' + esc(M.MODELS[k].short) + '</th>'; }).join('') + '<th scope="col">合計</th></tr></thead><tbody>' +
        KEYS.map(function (r) {
          return '<tr><td class="rowhead">' + esc(ROLES[r].name) + '</td>' + M.MODEL_ORDER.map(function (k) {
            return '<td><input class="cellin" type="number" min="0" max="100" step="5" data-mr="' + r + '" data-mk="' + k + '" aria-label="' + esc(ROLES[r].name + ' → ' + M.MODELS[k].short + '（%）') + '"></td>';
          }).join('') + '<td class="num" data-sum="' + r + '" style="white-space:normal"></td></tr>';
        }).join('') + '</tbody></table></div></figure>' +
      '<div id="pl-mixout" class="block"></div>' +
    '</section>' +
    '<section class="block" id="pl-seat"></section>';

  /* ----- inputs: update in place */
  function setVal(el, v) { if (el && el !== document.activeElement) el.value = v; }
  function press(list, fn) { each(list, function (b) { b.setAttribute('aria-pressed', String(!!fn(b))); }); }
  function shown(v) { return +(Number(v).toFixed(4)); }

  function renderInputs(keepSlider) {
    setVal($('pl-n-num'), int(st.n));
    if (!keepSlider) $('pl-n').value = clamp(Math.round(100 * (Math.log10(st.n) - 3)), 0, 250);
    press($('pl-np').children, function (b) { return Number(b.dataset.n) === st.n; });
    var on = M.ROLE_MIXES.filter(function (p) { return p.se === st.se && p.rd === st.rd; })[0];
    press($('pl-presets').children, function (b) { return on && on.id === b.dataset.p; });
    $('pl-mixname').textContent = on ? on.label : '自訂';
    $('pl-se').value = st.se; $('pl-rd').value = st.rd;
    $('pl-sev').textContent = st.se + '%'; $('pl-rdv').textContent = st.rd + '%'; $('pl-oav').textContent = (100 - st.se - st.rd) + '%';
    KEYS.forEach(function (r) {
      var box = host.querySelector('.role[data-role="' + r + '"]'), p = params(r);
      var share = r === 'OA' ? 100 - st.se - st.rd : r === 'SE' ? st.se : st.rd;
      box.querySelector('.role-n small').textContent = ROLES[r].sub + ' · ' + share + '%';
      press(box.querySelectorAll('button[data-l]'), function (b) { return b.dataset.l === st.lv[r]; });
      box.querySelector('.role-p').textContent = 'a ' + (+(p[0] * 100).toFixed(1)) + '% · r ' + p[1] + ' · u ' + h(p[2]) + ' · c ' + h(p[3]) + ' · o ' + h(p[4]);
      var ci = box.querySelector('.numin');
      ci.hidden = st.lv[r] !== 'custom';
      if (st.lv[r] === 'custom') each(ci.querySelectorAll('input'), function (inp, i) { setVal(inp, shown(i === 0 ? p[0] * 100 : p[i])); });
    });
    each($('pl-tz').children, function (b) {
      b.textContent = b.dataset.tz === 'single' ? '單一時區 s = ' + st.adv.sSingle : '全球分散 s = ' + st.adv.sGlobal;
      b.setAttribute('aria-pressed', String(st.tz === b.dataset.tz));
    });
    each($('pl-advin').querySelectorAll('input'), function (inp) { setVal(inp, st.adv[inp.dataset.adv]); });
    $('pl-fixed').innerHTML = 'd = ' + st.adv.d + ' · k = max(' + st.adv.kFloor + ', 1 + 3 / √m)<br>f_u ' + st.adv.fu + ' · f_c ' + st.adv.fc + ' · f_o ' + st.adv.fo + '<br>v = ' + st.adv.v + ' tokens/s · 使用率上限 ' + st.adv.util;
    press($('pl-mx').children, function (b) { return b.dataset.mx === st.mx; });
    var ed = $('pl-editor');
    ed.hidden = st.mx !== 'custom';
    if (st.mx === 'custom') {
      KEYS.forEach(function (r) {
        M.MODEL_ORDER.forEach(function (k) { setVal(ed.querySelector('input[data-mr="' + r + '"][data-mk="' + k + '"]'), st.cmixRaw[r][k] || 0); });
        var sum = rowSum(r);
        ed.querySelector('[data-sum="' + r + '"]').innerHTML = sum + '%' + (sum === 100 ? '' : ' <span class="chip chip-part" style="margin-left:6px">' + (sum > 0 ? '按比例調整' : '合計為 0，以 Kimi K3 計') + '</span>');
      });
    }
  }

  function seg(r, f) { return '<i class="' + roleSw[r] + '" title="' + esc(ROLES[r].name) + ' ' + pct(f) + '" style="flex:' + (f * 100).toFixed(2) + ' 0 0px' + (f > 0 ? '' : ';display:none') + '"></i>'; }

  /* ----- outputs */
  function renderOut() {
    var R = run(), pk = R.pk, U = pk.U, C = pk.C, O = pk.O, pl = R.plat, per = R.per, N = st.n;
    var cbX = pl.cbUncached > 0 ? pl.cbTotal / pl.cbUncached : 0;
    function flow(label, note, key, tot) {
      var segs = KEYS.map(function (r) { return seg(r, tot ? per[r][key] / tot : 0); }).join('');
      var txt = KEYS.map(function (r) { return ROLES[r].name + ' ' + pct(tot ? per[r][key] / tot : 0); }).join(' · ');
      return '<div class="flow"><div class="flow-r"><span class="l">' + label + '</span><span class="b">' + segs + '</span><span class="n">' + note + '</span></div><span class="flow-t">' + esc(txt) + '</span></div>';
    }
    var platRows = [
      ['全部 token（不分類別）', 'U + C + O', h(pk.all) + ' TPM', '只有 Cerebras 的 total bucket 這樣計'],
      ['Anthropic API', 'ITPM = U；OTPM = O', h(U) + ' ITPM<br>' + h(O) + ' OTPM', 'Scale tier 10M ITPM 的 ' + times(U / 10e6) + '；2M OTPM 的 ' + times(O / 2e6)],
      ['Bedrock runtime · burndown 5×', 'U + 5 × O', h(pl.b5) + ' TPM', 'Sonnet 4.6 預設 6M 的 ' + times(pl.b5 / 6e6)],
      ['Bedrock runtime · burndown 10×', 'U + 10 × O', h(pl.b10) + ' TPM', 'Opus 5.5 預設 30M 的 ' + times(pl.b10 / 30e6)],
      ['Bedrock runtime · burndown 15×', 'U + 15 × O', h(pl.b15) + ' TPM', 'Opus 4.8 預設 30M 的 ' + times(pl.b15 / 30e6)],
      ['Bedrock runtime · open-weight（1×）', 'U + O', h(pl.bOpen) + ' TPM', 'Kimi K3 預設 10M 的 ' + times(pl.bOpen / 10e6) + '；100M 類別的 ' + times(pl.bOpen / 100e6)],
      ['Azure PTU · gpt-6.1-sol', '(U + 0.1 × C + 5 × O) ÷ 3,000', int(pl.ptu) + ' PTU', 'normalised TPM = ' + h(pl.ptu * 3000)],
      ['Google GSU · Claude Opus 5.5', '(U + 0.05 × C + 5 × O) ÷ 60 ÷ 261', int(pl.gsuOpus) + ' GSU', 'burndown 後 ' + h(pl.gsuOpus * 261) + ' tokens/s'],
      ['Google GSU · Gemini 3.8 Flash', '(U + 0.1 × C + 5 × O) ÷ 60 ÷ 675', int(pl.gsuFlash) + ' GSU', 'burndown 後 ' + h(pl.gsuFlash * 675) + ' tokens/s'],
      ['Cerebras', '未快取 U + O；total U + C + O', h(pl.cbUncached) + ' TPM<br>' + h(pl.cbTotal) + ' TPM', 'total 是未快取的 ' + cbX.toFixed(1) + ' 倍；' + (cbX > 3 ? '超過 3 倍的上限，total bucket 先滿' : '在 3 倍以內，未快取 bucket 先滿')]
    ];
    $('pl-out').innerHTML =
      '<section class="peak" aria-label="尖峰需求">' +
        '<div class="peak-top"><div style="display:flex;flex-direction:column;gap:6px"><span class="k">尖峰 RPM</span><span class="v"><span class="hl">' + int(pk.rpm) + '</span></span></div>' +
        '<div class="s"><span>P95 平日、busy hour 內的尖峰分鐘</span><span class="mono" style="font-size:12px">m = ' + int(pk.m) + ' · k = ' + pk.k.toFixed(2) + ' · 每千人 ' + (pk.rpm / N * 1000).toFixed(1) + ' RPM</span></div></div>' +
        '<div class="peak-g">' +
          '<div class="peak-c"><span class="k">未快取輸入 TPM</span><span class="v">' + h(U) + '</span><span class="s">= Anthropic ITPM</span></div>' +
          '<div class="peak-c"><span class="k">輸出 TPM</span><span class="v">' + h(O) + '</span><span class="s">= OTPM</span></div>' +
          '<div class="peak-c"><span class="k">cache read TPM</span><span class="v">' + h(C) + '</span><span class="s">多數平台不計入配額</span></div>' +
          '<div class="peak-c"><span class="k">同時在途請求</span><span class="v">' + int(pk.L) + '</span><span class="s">99.9% 為 ' + int(pk.L999) + '</span></div>' +
        '</div>' +
        '<p class="peak-n">在途數用的是一次呼叫的總時間 W = TTFT + o / v。只用 TTFT 會算成 ' + int(pk.Lt) + '，低估 ' + (pk.Lt > 0 ? pk.L / pk.Lt : 0).toFixed(1) + ' 倍。</p>' +
      '</section>' +
      '<section class="block"><div class="sec-h"><h3 style="font-size:18px">尖峰分鐘的 token 組成</h3><span class="mono" style="font-size:12px;color:var(--mute)">全部 ' + h(pk.all) + ' TPM</span></div>' +
        '<div class="stack" role="img" aria-label="未快取輸入 ' + pct(U / pk.all) + '，cache read ' + pct(C / pk.all) + '，輸出 ' + pct(O / pk.all) + '"><i class="u" style="flex:' + (U / pk.all * 100).toFixed(2) + ' 0 0px"></i><i class="c" style="flex:' + (C / pk.all * 100).toFixed(2) + ' 0 0px"></i><i class="o" style="flex:' + (O / pk.all * 100).toFixed(2) + ' 0 0px"></i></div>' +
        '<div class="keyrow"><span><i class="sw ink"></i>未快取輸入 ' + pct(U / pk.all) + '</span><span><i class="sw surf"></i>cache read ' + pct(C / pk.all) + '</span><span><i class="sw teal"></i>輸出 ' + pct(O / pk.all) + '</span></div></section>' +
      '<section class="block"><h3 style="font-size:18px">用量從哪個角色來</h3>' +
        flow('席次', int(N) + ' 人', 'seats', N) + flow('平日呼叫數', h(R.dayCalls), 'calls', R.dayCalls) + flow('平日 token', h(R.dayTok), 'tok', R.dayTok) +
        '<div class="keyrow"><span><i class="sw oa"></i>OA</span><span><i class="sw se"></i>Coding</span><span><i class="sw rd"></i>R&amp;D</span></div>' +
        '<p class="wnote">每月 ' + h(R.monTok) + ' tokens，每位員工 ' + h(R.monPer) + '。以實付均價每 1M tokens $' + st.adv.price + ' 計，約 $' + h(R.cost) + ' / 月。' +
        (per.OA.seatMonth > 0 ? '一個 coding 席次的月用量等於 ' + int(per.SE.seatMonth / per.OA.seatMonth) + ' 個 OA 席次。' : '') + '</p></section>' +
      '<section class="block"><h3 style="font-size:18px">各平台要申請的數字</h3>' +
        '<p class="wnote">「TPM」不是單一數量。平台在 cache read 是否計入、輸出的權重、max_tokens 是否預扣上各不相同。U、C、O 是上面的未快取輸入、cache read 與輸出。</p>' +
        '<figure class="tbl"><div class="tbl-scroll"><table style="min-width:560px"><thead><tr><th scope="col">平台與計法</th><th scope="col">這個情境</th><th scope="col">對照</th></tr></thead><tbody>' +
        platRows.map(function (r) { return '<tr><td class="rowhead">' + r[0] + '<span class="mono" style="display:block;font-size:12px;font-weight:400;color:var(--ink2)">' + r[1] + '</span></td><td class="num" style="white-space:normal">' + r[2] + '</td><td>' + r[3] + '</td></tr>'; }).join('') +
        '</tbody></table></div></figure>' +
        '<div class="share"><button type="button" id="pl-copy">複製這個情境的連結</button><button type="button" id="pl-csv">下載 CSV</button><span class="ok" id="pl-ok" role="status"></span></div></section>';
    $('pl-live').textContent = '尖峰 ' + int(pk.rpm) + ' RPM，未快取輸入 ' + h(U) + ' TPM，輸出 ' + h(O) + ' TPM，同時在途 ' + int(pk.L) + '。';

    /* model mix */
    var mx = mixDef();
    var routeText = R.active.map(function (r) { return ROLES[r].name + ' → ' + Object.keys(mx[r]).filter(function (k) { return mx[r][k] > 0; }).map(function (k) { return M.MODELS[k].short + ' ' + Math.round(mx[r][k] * 100) + '%'; }).join('、'); }).join('；');
    var poolRows = R.pools.map(function (p) {
      var Md = p.M, q = p.q;
      return '<tr><td class="rowhead">' + esc(Md.label) + '</td><td class="num">' + int(q.rpm) + '</td><td class="num">' + h(q.U) + '</td><td class="num">' + h(q.O) + '</td><td class="num">' + int(q.L999) + '</td>' +
        '<td>' + (Md.bedrock ? '<span class="mono">' + h(p.bed) + ' TPM</span><span class="chip-note">預設 ' + h(Md.def) + ' 的 ' + times(p.bed / Md.def) + '</span>' : '<span style="color:var(--mute)">未上架</span>') + '</td>' +
        '<td>' + (Md.out ? '<span class="mono" style="font-weight:600">' + h(p.gpus) + ' 顆</span><span class="chip-note">取整 ' + p.gpusUnit + ' 顆（每單位 ' + Md.unit + '）· ' + Md.hw + ' · 每顆 ' + Md.out.toLocaleString('en-US') + ' tok/s</span>' : '僅 API') + '</td>' +
        '<td class="num">' + (Md.out ? bytes(p.hotB) : '–') + '</td><td class="num">' + (Md.out ? bytes(p.warmB) : '–') + '</td>' +
        '<td class="num">' + (p.cost !== undefined ? '$' + h(p.cost) : '<span style="font-family:var(--sans);color:var(--mute)">見第 5 章</span>') + '</td></tr>';
    }).join('');
    $('pl-mixout').innerHTML =
      '<p class="wnote">' + esc(routeText) + '。自架 GPU 線性需求 <span class="hl mono" style="font-weight:600">' + (R.gpuSum > 0 ? h(R.gpuSum) + ' 顆' : '0（全走 API）') + '</span>' +
        (R.gpuSum > 0 ? '，取整到各模型的部署單位後 <span class="mono" style="font-weight:600">' + R.gpuUnits + ' 顆</span>；hot KV 合計 ' + bytes(R.hotSum) + '、warm KV 合計 ' + bytes(R.warmSum) + '；open-weight 池的月成本（list price）$' + h(R.costSum) : '') +
        '。各池尖峰 RPM 合計是單一池的 ' + (R.rpmSum / pk.rpm).toFixed(3) + ' 倍。</p>' +
      '<figure class="tbl"><div class="tbl-scroll"><table style="min-width:980px"><thead><tr><th scope="col">模型池</th><th scope="col">尖峰 RPM</th><th scope="col">未快取輸入 TPM</th><th scope="col">輸出 TPM</th><th scope="col">在途 99.9%</th><th scope="col">Bedrock 計量</th><th scope="col">自架 GPU（decode）</th><th scope="col">hot KV</th><th scope="col">warm KV</th><th scope="col">月成本（list price）</th></tr></thead><tbody>' + poolRows + '</tbody></table></div></figure>' +
      '<ul class="prose" style="padding-left:20px;display:flex;flex-direction:column;gap:6px;font-size:13px;color:var(--ink2);max-width:64em">' +
      '<li>GPU 數只看 decode：該池的尖峰輸出 tokens/s ÷ 操作點的每顆輸出 tokens/s ÷ 使用率上限。操作點取自 InferenceX AgentX 在 2026-10-04 的快照 <span class="g g-a">A</span>，GLM-5.3 以 GLM-5.2 的量測代表。線性需求沒有取整也沒有備援；「取整」是把每個池進位到操作點的部署單位（Kimi K3 與 V4-Pro 8 顆、GLM-5.3 32 顆、V4.1-Flash 2 顆）。</li>' +
      '<li>hot KV 是 99.9% 在途請求的 context，必須在 HBM；warm KV 是為了讓下一次呼叫命中 prefix cache 而保留的 session，取在途數的 16 倍、每個 session 常駐 1.2 倍的平均 context，放在 DRAM 或 flash 層。</li>' +
      '<li>Bedrock：Sonnet 5.5 的 burndown 以 5× 假設，AWS 的文字沒有點名這個機型。GLM-5.3、DeepSeek V4-Pro 與 V4.1-Flash 未在 Bedrock 上架。</li>' +
      '<li>GPU 數無法換成 Trainium、TPU 或 Cerebras 的晶片數：這四個模型在這些硬體上的每晶片吞吐量查無公開資料。可以直接帶過去的是尖峰輸出 tokens/s、99.9% 在途數與 hot、warm KV 的 token 數。</li></ul>';

    /* per seat */
    $('pl-seat').innerHTML =
      '<h3 style="font-size:22px">每個席次的用量</h3>' +
      '<figure class="tbl"><div class="tbl-scroll"><table style="min-width:720px"><thead><tr><th scope="col">角色</th><th scope="col">平日活躍占比</th><th scope="col">每活躍使用者日 tokens</th><th scope="col">每席次平日呼叫</th><th scope="col">平日 tokens</th><th scope="col">每週 tokens</th><th scope="col">每月 tokens</th></tr></thead><tbody>' +
      KEYS.map(function (r) {
        var p = per[r];
        return '<tr><td class="rowhead">' + esc(ROLES[r].name) + ' <span style="font-weight:400;color:var(--mute);font-size:12px">' + ROLES[r].sub + '</span></td><td class="num">' + (+(p.p[0] * 100).toFixed(1)) + '%</td><td class="num">' + h(p.userDay) + '</td><td class="num">' + h(p.seatCalls) + '</td><td class="num">' + h(p.seatTok) + '</td><td class="num">' + h(p.seatWeek) + '</td><td class="num" style="font-weight:600">' + h(p.seatMonth) + '</td></tr>';
      }).join('') + '</tbody></table></div></figure>' +
      '<p class="wnote">席次是授權人數，不是活躍人數；除「每活躍使用者日」一欄外，數字已乘上平日活躍占比。每週以 5 個平日加 2 個週末日計，週末日的量是平日的 OA 0.45、coding 0.25、R&amp;D 0.35 倍；每月為 52.14 ÷ 12 週。</p>';
    last = R;
  }

  function render(keepSlider) { renderInputs(keepSlider); renderOut(); }

  /* ----- events */
  host.addEventListener('click', function (e) {
    var b = e.target.closest('button'); if (!b) return;
    if (b.dataset.n) { st.n = Number(b.dataset.n); render(); }
    else if (b.dataset.p) { var p = M.ROLE_MIXES.filter(function (x) { return x.id === b.dataset.p; })[0]; st.se = p.se; st.rd = p.rd; render(); }
    else if (b.dataset.l) {
      var r = b.dataset.r;
      if (b.dataset.l === 'custom' && !st.custom[r]) st.custom[r] = ROLES[r].lv[st.lv[r] === 'custom' ? 'base' : st.lv[r]].slice();
      st.lv[r] = b.dataset.l; render();
    }
    else if (b.dataset.tz) { st.tz = b.dataset.tz; render(); }
    else if (b.dataset.mx) {
      if (b.dataset.mx === 'custom' && !st.cmixRaw) seedCmix(mixDef());   // start from the routing that was showing
      st.mx = b.dataset.mx; render();
    }
    else if (b.id === 'pl-reset') { st = clone(DEF); render(); }
    else if (b.id === 'pl-copy') {
      var url = location.href.split('#')[0].split('?')[0] + '#calc?' + encode();
      var ok = $('pl-ok');
      var done = function (t) { ok.textContent = t; setTimeout(function () { ok.textContent = ''; }, 3000); };
      // the address bar always carries the scenario, so the link can be copied from there when the clipboard is unavailable
      try { history.replaceState(null, '', '#calc?' + encode()); } catch (err) { /* file:// or sandboxed frame */ }
      if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(url).then(function () { done('已複製連結'); }, function () { done('連結已寫入網址列，請從網址列複製'); });
      else done('連結已寫入網址列，請從網址列複製');
    }
    else if (b.id === 'pl-csv') { downloadCsv(); }
  });
  host.addEventListener('input', function (e) {
    var t = e.target;
    if (t.id === 'pl-n') { st.n = nice(Math.pow(10, 3 + Number(t.value) / 100)); render(true); }
    else if (t.id === 'pl-se') { st.se = Math.min(Number(t.value), 100 - st.rd); render(); }
    else if (t.id === 'pl-rd') { st.rd = Math.min(Number(t.value), 100 - st.se); render(); }
  });
  // text and number fields commit on change (Enter or leaving the field); the committed value is written back
  host.addEventListener('change', function (e) {
    var t = e.target, v;
    if (t.id === 'pl-n-num') {
      st.n = clamp(Math.round(Number(String(t.value).replace(/[^0-9.]/g, ''))) || DEF.n, 100, 2000000);
      t.value = int(st.n); render();
    } else if (t.dataset.adv) {
      v = Number(t.value);
      if (t.value !== '' && isFinite(v)) st.adv[t.dataset.adv] = clamp(v, Number(t.min), Number(t.max));
      t.value = st.adv[t.dataset.adv]; render();
    } else if (t.dataset.cr) {
      var r = t.dataset.cr, i = Number(t.dataset.ci);
      v = Math.max(0, Number(t.value) || 0);
      st.custom[r][i] = i === 0 ? clamp(v / 100, 0, 1) : v;
      t.value = shown(i === 0 ? st.custom[r][0] * 100 : st.custom[r][i]); render();
    } else if (t.dataset.mr) {
      v = clamp(Math.round(Number(t.value)) || 0, 0, 100);
      st.cmixRaw[t.dataset.mr][t.dataset.mk] = v;
      t.value = v; render();
    }
  });

  function downloadCsv() {
    var R = last, pk = R.pk, pl = R.plat, rows = [['item', 'value', 'unit']];
    function add(a, b, c) { rows.push([a, b, c || '']); }
    add('employees', st.n, 'people'); add('share OA / coding / R&D', (100 - st.se - st.rd) + ' / ' + st.se + ' / ' + st.rd, '%');
    KEYS.forEach(function (r) { add('level ' + r, st.lv[r] + ' [' + params(r).join(', ') + ']', 'a, r, u, c, o'); });
    add('busy-hour share s', st.tz === 'single' ? st.adv.sSingle : st.adv.sGlobal, ''); add('d', st.adv.d); add('v', st.adv.v, 'tokens/s');
    add('busy-hour mean RPM m', pk.m.toFixed(2), 'requests/min'); add('k', pk.k.toFixed(4)); add('peak RPM', pk.rpm.toFixed(2), 'requests/min');
    add('peak uncached-input TPM (U)', pk.U.toFixed(0), 'tokens/min'); add('peak cache-read TPM (C)', pk.C.toFixed(0), 'tokens/min'); add('peak output TPM (O)', pk.O.toFixed(0), 'tokens/min');
    add('in-flight mean', pk.L.toFixed(2), 'requests'); add('in-flight 99.9%', pk.L999.toFixed(2), 'requests');
    add('Bedrock TPM burndown 5x', pl.b5.toFixed(0)); add('Bedrock TPM burndown 10x', pl.b10.toFixed(0)); add('Bedrock TPM burndown 15x', pl.b15.toFixed(0)); add('Bedrock TPM open-weight', pl.bOpen.toFixed(0));
    add('Azure PTU gpt-6.1-sol', pl.ptu.toFixed(1)); add('Google GSU Claude Opus 5.5', pl.gsuOpus.toFixed(1)); add('Google GSU Gemini 3.8 Flash', pl.gsuFlash.toFixed(1));
    add('tokens per weekday', R.dayTok.toFixed(0)); add('tokens per month', R.monTok.toFixed(0)); add('tokens per employee per month', R.monPer.toFixed(0)); add('month cost at effective price', R.cost.toFixed(0), 'USD');
    add('routing', st.mx);
    (R.pools || []).forEach(function (p) {
      add('pool ' + p.M.label + ' peak RPM', p.q.rpm.toFixed(2)); add('pool ' + p.M.label + ' uncached-input TPM', p.q.U.toFixed(0)); add('pool ' + p.M.label + ' output TPM', p.q.O.toFixed(0));
      add('pool ' + p.M.label + ' in-flight 99.9%', p.q.L999.toFixed(2));
      if (p.M.out) { add('pool ' + p.M.label + ' GPUs linear', p.gpus.toFixed(2)); add('pool ' + p.M.label + ' GPUs rounded to unit', p.gpusUnit); add('pool ' + p.M.label + ' hot KV', (p.hotB / 1e9).toFixed(1), 'GB'); add('pool ' + p.M.label + ' warm KV', (p.warmB / 1e12).toFixed(2), 'TB'); }
    });
    var csv = rows.map(function (r) { return r.map(function (c) { c = String(c); return /[",\n]/.test(c) ? '"' + c.replace(/"/g, '""') + '"' : c; }).join(','); }).join('\n');
    try {
      var blob = new Blob(['﻿' + csv], { type: 'text/csv;charset=utf-8' });
      var a = document.createElement('a');
      a.href = URL.createObjectURL(blob); a.download = 'capacity-scenario.csv';
      document.body.appendChild(a); a.click(); document.body.removeChild(a);
      setTimeout(function () { URL.revokeObjectURL(a.href); }, 2000);
    } catch (err) { $('pl-ok').textContent = '這個環境無法下載檔案'; }
  }

  render();
  // a scenario link pasted into the same tab
  window.addEventListener('hashchange', function () {
    var hsh = location.hash || '';
    if (hsh.indexOf('#calc') === 0 && hsh.indexOf('?') >= 0) { st = clone(DEF); fromUrl(); render(); }
  });
  window.IA_PLANNER = { state: function () { return st; }, result: function () { return last; } };
})();
