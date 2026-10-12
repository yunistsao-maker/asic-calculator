// Verifies the JavaScript capacity model against the Python reference outputs.
const fs = require('fs');
const path = require('path');
const M = require('../static/planner-model.js');
const OUT = path.join(__dirname, '..', '..', 'calc', 'out');   // outputs of calc/capacity_model.py
const ref = JSON.parse(fs.readFileSync(path.join(OUT, 'model.json'), 'utf8'));
const self = JSON.parse(fs.readFileSync(path.join(OUT, 'selftest.json'), 'utf8'));
let checks = 0, fails = 0;
function close(a, b, what) {
  checks++;
  const ok = (a === b) || Math.abs(a - b) <= 1e-9 * Math.max(1, Math.abs(a), Math.abs(b));
  if (!ok) { fails++; if (fails < 25) console.log('MISMATCH', what, a, b); }
}
const mixes = ref.role_mixes;
function state(N, mixKey, level, s) {
  const mx = mixes[mixKey];
  return { n: N, share: { OA: mx.OA, SE: mx.SE, RD: mx.RD }, level: { OA: level, SE: level, RD: level }, s: s };
}
// 1. self-test vector
{
  const e = self.expect;
  const r = M.compute(state(100000, 'B_manufacturing', 'base', 0.11));
  close(r.pk.m, e.m, 'self m'); close(r.pk.k, e.k, 'self k'); close(r.pk.rpm, e.rpm, 'self rpm');
  close(r.pk.U, e.U, 'self U'); close(r.pk.C, e.C, 'self C'); close(r.pk.O, e.O, 'self O');
  close(r.pk.L, e.L, 'self L'); close(r.pk.L999, e.L999, 'self L999');
  close(r.dayTok, e.weekday_tokens, 'self weekday tokens'); close(r.monTok, e.month_tokens, 'self month tokens');
  close(r.plat.ptu, e.azure_ptu_gpt61sol, 'self PTU'); close(r.plat.gsuOpus, e.google_gsu_opus55, 'self GSU');
  close(r.plat.gsuFlash, e.google_gsu_gemini38flash, 'self GSU flash');
  close(r.seShare, e.se_share_of_tokens, 'self se share'); close(r.cost, e.month_cost_effective_usd, 'self cost');
  console.log('selftest: RPM', r.pk.rpm.toFixed(2), 'U', r.pk.U.toFixed(2), 'L999', r.pk.L999.toFixed(4));
}
// 2. the whole 96-row matrix
for (const e of ref.matrix) {
  const r = M.compute(state(e.N, e.mix, e.level, e.s));
  const tag = `${e.N}/${e.mix}/${e.level}`;
  close(r.pk.m, e.m, tag + ' m'); close(r.pk.k, e.k, tag + ' k'); close(r.pk.rpm, e.rpm, tag + ' rpm');
  close(r.pk.U, e.U, tag + ' U'); close(r.pk.C, e.C, tag + ' C'); close(r.pk.O, e.O, tag + ' O'); close(r.pk.all, e.all, tag + ' all');
  close(r.pk.L, e.L, tag + ' L'); close(r.pk.L999, e.L999, tag + ' L999'); close(r.pk.ctx, e.avg_ctx, tag + ' ctx');
  close(r.dayCalls, e.weekday_calls, tag + ' calls'); close(r.dayTok, e.weekday_tokens, tag + ' daytok');
  close(r.monTok, e.month_tokens, tag + ' montok'); close(r.monPer, e.month_tokens_per_employee, tag + ' monper');
  close(r.seShare, e.se_share_of_tokens, tag + ' se'); close(r.cost, e.month_cost_effective_usd, tag + ' cost');
  close(r.plat.itpm, e.anthropic_itpm, tag); close(r.plat.otpm, e.anthropic_otpm, tag);
  close(r.plat.b5, e.bedrock_tpm_b5, tag); close(r.plat.b10, e.bedrock_tpm_b10, tag); close(r.plat.b15, e.bedrock_tpm_b15, tag);
  close(r.plat.bOpen, e.bedrock_tpm_open, tag); close(r.plat.ptu, e.azure_ptu_gpt61sol, tag);
  close(r.plat.gsuOpus, e.google_gsu_opus55, tag); close(r.plat.gsuFlash, e.google_gsu_gemini38flash, tag);
  close(r.plat.cbUncached, e.cerebras_uncached_tpm, tag); close(r.plat.cbTotal, e.cerebras_total_tpm, tag);
}
// 3. model-mix blocks
const mmKey = { MX1_frontier: 'MX1', MX2_tiered: 'MX2', MX3_open: 'MX3', MX4_single: 'MX4' };
const summary = [];
for (const b of ref.model_mix) {
  const st = state(b.N, b.mix, b.level, 0.11);
  st.mix = M.MIXES.find((x) => x.id === mmKey[b.model_mix]);
  const r = M.compute(st);
  const tag = `${b.N}/${b.mix}/${b.level}/${b.model_mix}`;
  close(r.pools.length, b.pools.length, tag + ' pool count');
  for (const e of b.pools) {
    const p = r.pools.find((x) => x.key === e.model);
    if (!p) { fails++; console.log('missing pool', tag, e.model); continue; }
    close(p.q.rpm, e.rpm, tag + e.model + ' rpm'); close(p.q.U, e.U, tag + e.model + ' U'); close(p.q.C, e.C, tag + e.model + ' C');
    close(p.q.O, e.O, tag + e.model + ' O'); close(p.q.L, e.L, tag + e.model + ' L'); close(p.q.L999, e.L999, tag + e.model + ' L999');
    close(p.bed, e.bedrock_tpm, tag + e.model + ' bed');
    if (e.gpus_decode !== undefined) {
      close(p.gpus, e.gpus_decode, tag + e.model + ' gpus'); close(p.hotTok, e.hot_tokens, tag + e.model + ' hot tokens');
      close(p.hotB / 1e9, e.kv_hot_gb, tag + e.model + ' hot GB'); close(p.warmB / 1e12, e.kv_warm_tb, tag + e.model + ' warm TB');
      close(p.warmTok, e.warm_tokens, tag + e.model + ' warm tokens');
    }
    if (e.month_cost_list_usd !== undefined) close(p.cost, e.month_cost_list_usd, tag + e.model + ' cost');
  }
  summary.push(`${tag}: GPUs ${M.h(r.gpuSum)} linear, ${r.gpuUnits} rounded; hot ${M.h(r.hotSum / 1e9)} GB; warm ${M.h(r.warmSum / 1e12)} TB; cost $${M.h(r.costSum)}; rpm ratio ${(r.rpmSum / r.pk.rpm).toFixed(3)}`);
}
console.log(summary.join('\n'));
// 4. the N = 1,000 vector named in chapter 10
{
  const r = M.compute(state(1000, 'B_manufacturing', 'base', 0.11));
  console.log('N=1000 B base: k', r.pk.k.toFixed(4), 'RPM', r.pk.rpm.toFixed(2));
}
console.log(`${checks} checks, ${fails} failures`);
process.exit(fails ? 1 : 0);
