/* Capacity model — JavaScript port of calc/capacity_model.py (chapter 10).
   Pure functions, no DOM. Tested against calc/out/selftest.json and calc/out/model.json at build time. */
(function (rootObj, factory) {
  if (typeof module === 'object' && module.exports) module.exports = factory();
  else rootObj.IA_MODEL = factory();
})(typeof self !== 'undefined' ? self : this, function () {
  'use strict';

  // [a, r, u, c, o]: weekday-active share, calls per active day, uncached input, cache-read input, output tokens per call
  var ROLES = {
    OA: { name: 'OA', sub: '辦公助理', weekend: 0.45, ttft: 1.0,
      lv: { low: [0.12, 4, 900, 100, 125], base: [0.35, 10, 1750, 1750, 400], high: [0.50, 30, 3000, 9000, 800] } },
    SE: { name: 'Coding', sub: '軟體開發', weekend: 0.25, ttft: 2.0,
      lv: { low: [0.30, 20, 5000, 63000, 250], base: [0.45, 170, 6500, 85000, 600], high: [0.75, 400, 8500, 120000, 700] } },
    RD: { name: 'R&D', sub: '研究', weekend: 0.35, ttft: 2.5,
      lv: { low: [0.28, 26, 2615, 1615, 615], base: [0.40, 100, 2500, 3000, 720], high: [0.55, 540, 2640, 6805, 611] } }
  };
  var KEYS = ['OA', 'SE', 'RD'];
  var PEAK = { sSingle: 0.11, sGlobal: 0.065, d: 1.2, kFloor: 1.15, fu: 1.18, fc: 1.04, fo: 1.06, v: 80, z: 3.1,
    util: 0.8, warm: 16, res: 1.2, wpm: 52.14 / 12, price: 0.72 };
  var ROLE_MIXES = [
    { id: 'A', key: 'A_office', label: 'A 辦公室為主', se: 7, rd: 3 },
    { id: 'B', key: 'B_manufacturing', label: 'B 製造 / 硬體', se: 12, rd: 18 },
    { id: 'C', key: 'C_finance', label: 'C 金融', se: 15, rd: 5 },
    { id: 'D', key: 'D_software', label: 'D 軟體 / 網路', se: 50, rd: 10 },
    { id: 'E', key: 'E_rnd', label: 'E 研發為主', se: 25, rd: 40 }
  ];
  // out: output tokens/s per GPU at the operating point; user: tokens/s per user there; unit: GPUs of that deployment
  // price: US$ per 1M tokens [input, cached input, output] at first-party list price
  var MODELS = {
    opus: { label: 'Claude Opus 5.5', short: 'Opus 5.5', burn: 10, def: 30e6, bedrock: true },
    sonnet: { label: 'Claude Sonnet 5.5', short: 'Sonnet 5.5', burn: 5, def: 6e6, bedrock: true },
    k3: { label: 'Kimi K3', short: 'Kimi K3', burn: 1, def: 10e6, bedrock: true, out: 136, user: 38, unit: 8,
      hw: 'GB300 NVL72', kv: 13.8e3, state: 434e6, price: [3.00, 0.30, 15.00] },
    glm: { label: 'GLM-5.3', short: 'GLM-5.3', burn: 1, def: 100e6, bedrock: false, out: 149, user: 101, unit: 32,
      hw: 'GB300 NVL72', kv: 44.9e3, state: 0, price: [1.40, 0.26, 4.40] },
    dsv4: { label: 'DeepSeek V4-Pro', short: 'V4-Pro', burn: 1, def: 100e6, bedrock: false, out: 739, user: 37, unit: 8,
      hw: 'B300', kv: 5.0e3, state: 0, price: [1.32, 0.044, 3.96] },
    flash: { label: 'DeepSeek V4.1-Flash', short: 'V4.1-Flash', burn: 1, def: 100e6, bedrock: false, out: 3059, user: 60, unit: 2,
      hw: 'B300', kv: 0.89e3, state: 0, price: [0.30, 0.006, 1.20] }
  };
  var MODEL_ORDER = ['opus', 'sonnet', 'k3', 'glm', 'dsv4', 'flash'];
  var MIXES = [
    { id: 'MX1', label: 'MX1 只用 frontier API', OA: { opus: 0.10, sonnet: 0.90 }, SE: { opus: 0.54, sonnet: 0.46 }, RD: { opus: 0.50, sonnet: 0.50 } },
    { id: 'MX2', label: 'MX2 分層路由', OA: { flash: 0.80, glm: 0.20 }, SE: { k3: 0.40, dsv4: 0.30, opus: 0.30 }, RD: { dsv4: 0.50, opus: 0.30, flash: 0.20 } },
    { id: 'MX3', label: 'MX3 只用開源模型', OA: { flash: 1 }, SE: { glm: 0.50, k3: 0.50 }, RD: { dsv4: 1 } },
    { id: 'MX4', label: 'MX4 單一旗艦', OA: { k3: 1 }, SE: { k3: 1 }, RD: { k3: 1 } }
  ];

  function kFactor(m, P) { return m > 0 ? Math.max(P.kFloor, 1 + 3 / Math.sqrt(m)) : P.kFloor; }

  // streams routed to ONE endpoint: k is computed on the pooled busy-hour RPM
  function pool(streams, P, v) {
    var m = 0, i;
    for (i = 0; i < streams.length; i++) m += streams[i].m;
    var k = kFactor(m, P), U = 0, C = 0, O = 0, L = 0, Lt = 0, ctx = 0;
    for (i = 0; i < streams.length; i++) {
      var x = streams[i];
      U += x.m * k * x.u; C += x.m * k * x.c; O += x.m * k * x.o;
      L += x.m * k / 60 * (x.ttft + x.o / v);
      Lt += x.m * k / 60 * x.ttft;
      ctx += x.m * (x.u + x.c + x.o);
    }
    U *= P.fu; C *= P.fc; O *= P.fo;
    return { m: m, k: k, rpm: m * k, U: U, C: C, O: O, all: U + C + O, L: L, Lt: Lt,
      L999: L > 0 ? L + P.z * Math.sqrt(L) : 0, ctx: m ? ctx / m : 0 };
  }

  function platform(pk) {
    var U = pk.U, C = pk.C, O = pk.O;
    return { itpm: U, otpm: O, b5: U + 5 * O, b10: U + 10 * O, b15: U + 15 * O, bOpen: U + O,
      ptu: (U + 0.1 * C + 5 * O) / 3000, gsuOpus: (U + 0.05 * C + 5 * O) / 60 / 261,
      gsuFlash: (U + 0.1 * C + 5 * O) / 60 / 675, cbUncached: U + O, cbTotal: U + C + O };
  }

  /* st: { n, share: {OA,SE,RD} (fractions), level: {OA,SE,RD}, s, roles?, peak?, mix? (routing object), params? }
     returns everything the planner shows */
  function compute(st) {
    var P = {}, k;
    for (k in PEAK) P[k] = PEAK[k];
    if (st.peak) for (k in st.peak) P[k] = st.peak[k];
    var roles = st.roles || ROLES;
    function par(r) { return (st.custom && st.custom[r]) || roles[r].lv[st.level[r]]; }
    function stream(r, frac) {
      var p = par(r);
      var calls = st.n * st.share[r] * p[0] * p[1] * frac;
      return { role: r, calls: calls, m: calls * st.s / 60 * P.d, u: p[2], c: p[3], o: p[4], ttft: roles[r].ttft };
    }
    var active = KEYS.filter(function (r) { return st.share[r] > 0; });
    var pk = pool(active.map(function (r) { return stream(r, 1); }), P, P.v);
    var per = {}, dayCalls = 0, dayTok = 0, monTok = 0;
    KEYS.forEach(function (r) {
      var p = par(r);
      var seatCalls = p[0] * p[1], seatTok = seatCalls * (p[2] + p[3] + p[4]);
      var wk = 5 + 2 * roles[r].weekend, seats = st.n * st.share[r];
      per[r] = { p: p, seats: seats, calls: seats * seatCalls, tok: seats * seatTok, seatCalls: seatCalls,
        userDay: p[1] * (p[2] + p[3] + p[4]), seatTok: seatTok, seatWeek: seatTok * wk, seatMonth: seatTok * wk * P.wpm,
        seatMonthU: seatCalls * p[2] * wk * P.wpm, seatMonthC: seatCalls * p[3] * wk * P.wpm, seatMonthO: seatCalls * p[4] * wk * P.wpm };
      dayCalls += per[r].calls; dayTok += per[r].tok; monTok += per[r].tok * wk * P.wpm;
    });
    var out = { P: P, pk: pk, per: per, dayCalls: dayCalls, dayTok: dayTok, monTok: monTok,
      monPer: st.n ? monTok / st.n : 0, cost: monTok / 1e6 * P.price,
      seShare: dayTok ? per.SE.tok / dayTok : 0, plat: platform(pk), active: active };
    if (st.mix) {
      var pools = {}, order = [];
      active.forEach(function (r) {
        Object.keys(st.mix[r] || {}).forEach(function (mk) {
          var f = st.mix[r][mk];
          if (!(f > 0)) return;
          if (!pools[mk]) { pools[mk] = []; order.push(mk); }
          var s2 = stream(r, f);
          s2.frac = f;
          pools[mk].push(s2);
        });
      });
      var gpuSum = 0, gpuUnits = 0, hotSum = 0, warmSum = 0, rpmSum = 0, costSum = 0;
      out.pools = order.map(function (mk) {
        var M = MODELS[mk];
        var q = pool(pools[mk], P, M.user || P.v);
        var row = { key: mk, M: M, q: q, bed: q.U + M.burn * q.O };
        rpmSum += q.rpm;
        if (M.out) {
          row.outTps = q.O / 60;
          row.gpus = row.outTps / M.out / P.util;
          row.gpusUnit = Math.ceil(row.gpus / M.unit - 1e-9) * M.unit;
          row.hotTok = q.L999 * q.ctx;
          row.hotB = row.hotTok * M.kv + q.L999 * M.state;
          row.warmSessions = P.warm * q.L;
          row.warmTok = row.warmSessions * P.res * q.ctx;
          row.warmB = row.warmTok * M.kv + row.warmSessions * M.state;
          gpuSum += row.gpus; gpuUnits += row.gpusUnit; hotSum += row.hotB; warmSum += row.warmB;
        }
        if (M.price) {
          var mu = 0, mc = 0, mo = 0;
          pools[mk].forEach(function (s2) {
            var seats = st.n * st.share[s2.role];
            mu += seats * s2.frac * per[s2.role].seatMonthU;
            mc += seats * s2.frac * per[s2.role].seatMonthC;
            mo += seats * s2.frac * per[s2.role].seatMonthO;
          });
          row.cost = (mu * M.price[0] + mc * M.price[1] + mo * M.price[2]) / 1e6;
          costSum += row.cost;
        }
        return row;
      });
      out.gpuSum = gpuSum; out.gpuUnits = gpuUnits; out.hotSum = hotSum; out.warmSum = warmSum;
      out.rpmSum = rpmSum; out.costSum = costSum;
    }
    return out;
  }

  // 3 significant figures with K / M / B / T (same rounding as the Python reference)
  function trim(s) { return s.indexOf('.') >= 0 ? s.replace(/0+$/, '').replace(/\.$/, '') : s; }
  function h(x) {
    if (x == null || !isFinite(x)) return '–';
    var ax = Math.abs(x);
    if (ax > 0) {
      var p = 2 - Math.floor(Math.log10(ax));
      if (p >= 0) { var f = Math.pow(10, p); x = Math.round(x * f) / f; } else { var g = Math.pow(10, -p); x = Math.round(x / g) * g; }
      ax = Math.abs(x);
    }
    var units = [[1e12, 'T'], [1e9, 'B'], [1e6, 'M'], [1e3, 'K']];
    for (var i = 0; i < units.length; i++) {
      if (ax >= units[i][0]) {
        var v = x / units[i][0];
        var dec = Math.max(0, 3 - String(Math.floor(Math.abs(v))).length);
        return trim(v.toFixed(dec)) + units[i][1];
      }
    }
    if (ax >= 100) return x.toFixed(0);
    if (ax >= 10) return trim(x.toFixed(1));
    return trim(x.toFixed(2));
  }

  return { ROLES: ROLES, KEYS: KEYS, PEAK: PEAK, ROLE_MIXES: ROLE_MIXES, MODELS: MODELS, MODEL_ORDER: MODEL_ORDER,
    MIXES: MIXES, compute: compute, pool: pool, platform: platform, kFactor: kFactor, h: h };
});
