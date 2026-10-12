#!/usr/bin/env python3
"""
Capacity model: employees -> per-seat usage -> peak RPM / TPM -> platform quota units -> GPUs.

Reference implementation for chapter 10 of the ASIC survey (and for the website calculator,
which re-implements the same formulas in JavaScript and must reproduce out/selftest.json).

Every parameter carries a `src` key that points to the evidence table in chapter 11
(research notes: usage_evidence.md, capacity_planning_methods.md, open_model_families.md).

Formulas (symbols as in chapter 10):
  calls_day          = N_role * a * r
  m  (busy-hour RPM) = calls_day * s / 60 * d                  # mean minute of the busy hour, P95 weekday
  k  (peak minute)   = max(1.15, 1 + 3 / sqrt(m_pool))         # computed on the pooled RPM of one endpoint
  peak RPM           = m * k
  peak TPM (class)   = peak RPM * tokens_per_call(class) * f_class
  W  (call duration) = TTFT + o / v
  L  (in flight)     = peak RPM / 60 * W          (Little's law)
  L99.9              = L + 3.1 * sqrt(L)          (Poisson head-room)
"""
import csv
import json
import math
import os
from copy import deepcopy

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
os.makedirs(OUT, exist_ok=True)

# --------------------------------------------------------------------------------------
# 1. Parameters
# --------------------------------------------------------------------------------------

# Per-role usage, three fleet-level scenario levels.
#   a = share of licensed seats active on an average weekday
#   r = model calls per active user per active day (fleet mean, not median user)
#   u = uncached input tokens per call (fresh input + cache writes)
#   c = cache-read input tokens per call
#   o = output tokens per call (reasoning included)
#   ttft = seconds to first token assumed for the call-duration estimate
#   weekend = volume of a weekend day relative to a weekday
ROLES = {
    "OA": {
        "label": "OA / office assistant",
        "weekend": 0.45,   # src: traces chat 0.36-0.57
        "ttft": 1.0,
        "levels": {
            "low":  {"a": 0.12, "r": 4,   "u": 900,  "c": 100,   "o": 125,
                     "note": "early Copilot-style chat: ~40% weekly users, 3.7-4 msgs/day, Azure-2024 chat tokens"},
            "base": {"a": 0.35, "r": 10,  "u": 1750, "c": 1750,  "o": 400,
                     "note": "mature assistant: UK-gov/ChatGPT DAU share, 7.5 msgs/DAU x1.3, 3.5K in (50% cached), 400 out"},
            "high": {"a": 0.50, "r": 30,  "u": 3000, "c": 9000,  "o": 800,
                     "note": "office agents mainstream (4-15x chat tokens): JPMorgan-level daily use, 12K in (75% cached)"},
        },
    },
    "SE": {
        "label": "Coding / software engineering",
        "weekend": 0.25,   # src: traces coding 0.21-0.32
        "ttft": 2.0,
        "levels": {
            "low":  {"a": 0.30, "r": 20,  "u": 5000, "c": 63000,  "o": 250,
                     "note": "occasional agent / IDE-assistant users (Copilot non-enterprise median)"},
            "base": {"a": 0.45, "r": 170, "u": 6500, "c": 85000,  "o": 600,
                     "note": "standardised coding agent: Anthropic $13/active day ~ 13-23M tokens; Copilot/TraceLab call shape"},
            "high": {"a": 0.75, "r": 400, "u": 8500, "c": 120000, "o": 700,
                     "note": "parallel / long-running agents: P90 $30/day ~ 30-52M tokens; Meta fleet average 23.6M/employee/day"},
        },
    },
    "RD": {
        "label": "R&D / research",
        "weekend": 0.35,
        "ttft": 2.5,
        "levels": {
            # low : 10 document requests (6K in, 20% cached, 400 out) + 0.2 deep-research run (250K in 60% cached, 60K out, 80 calls)
            "low":  {"a": 0.28, "r": 26,  "u": 2615, "c": 1615, "o": 615,
                     "note": "10 document requests + 0.2 deep-research run per active day"},
            # base: 20 document requests (15K in, 50% cached, 600 out) + 1 run (250K in 60% cached, 60K out, 80 calls)
            "base": {"a": 0.40, "r": 100, "u": 2500, "c": 3000, "o": 720,
                     "note": "20 document requests + 1 deep-research run per active day"},
            # high: 60 document requests (40K in, 80% cached, 1.5K out) + 3 Max runs (900K in 65% cached, 80K out, 160 calls)
            "high": {"a": 0.55, "r": 540, "u": 2640, "c": 6805, "o": 611,
                     "note": "60 document requests + 3 deep-research-max runs per active day"},
        },
    },
}

PEAK = {
    "s_single_tz": 0.11,    # busy-hour share of weekday volume, one site / one time-zone band (traces: 0.09-0.125)
    "s_global": 0.065,      # same, globally distributed population (traces: 0.052-0.070)
    "d": 1.2,               # P95 weekday / mean weekday (BurstGPT 1.20-1.80; set 1.0 to size on an average weekday)
    "k_floor": 1.15,        # peak minute / mean minute of the busy hour at large volume (traces: 1.09-1.30)
    "f_u": 1.18,            # token lumpiness on top of the request peak: uncached input (1.29 / 1.09)
    "f_c": 1.04,            # cache-read input (1.13 / 1.09)
    "f_o": 1.06,            # output (1.15 / 1.09)
    "v": 80.0,              # output tokens/s per stream assumed for call duration (typical GPU-hosted flagship)
    "z999": 3.1,            # Poisson quantile multiplier for 99.9%
    "util": 0.80,           # utilisation ceiling for self-hosted fleets (published 0.75-0.85)
    "warm_sessions_per_inflight": 16.0,  # sessions active in the busy hour / mean in-flight calls (Copilot trace: 1/0.063)
    "resident_ctx_factor": 1.2,   # resident KV tokens per warm session = 1.2 x mean context per call
                                  # (coding base: 92K x 1.2 = 110K, matching InferenceX / llm-d's ~110-112K per session)
    "weeks_per_month": 52.14 / 12,
}

POPULATIONS = [1_000, 10_000, 50_000, 100_000]

ROLE_MIXES = {
    "A_office":        {"label": "A. Office-heavy (services, retail HQ)",          "OA": 0.90, "SE": 0.07, "RD": 0.03},
    "B_manufacturing": {"label": "B. Manufacturing / hardware (ODM, EMS, semis)",  "OA": 0.70, "SE": 0.12, "RD": 0.18},
    "C_finance":       {"label": "C. Financial services",                          "OA": 0.80, "SE": 0.15, "RD": 0.05},
    "D_software":      {"label": "D. Software / internet company",                 "OA": 0.40, "SE": 0.50, "RD": 0.10},
    "E_rnd":           {"label": "E. R&D-centric (IC design, research institute)", "OA": 0.35, "SE": 0.25, "RD": 0.40},
    "P_OA":            {"label": "Pure OA (100%)",                                 "OA": 1.00, "SE": 0.00, "RD": 0.00},
    "P_SE":            {"label": "Pure coding (100%)",                             "OA": 0.00, "SE": 1.00, "RD": 0.00},
    "P_RD":            {"label": "Pure R&D (100%)",                                "OA": 0.00, "SE": 0.00, "RD": 1.00},
}

# Models used in the model-mix scenarios.
#   price = US$ per million tokens (input, cached input, output); None = filled in chapter 5 / 8
#   bedrock_burndown = output-token weight in the Bedrock runtime TPM quota
#   selfhost = AgentX (InferenceX agentic trace replay) operating point on Blackwell-class GPUs:
#              out_tps_gpu = output tokens/s per GPU, user_tps = median tokens/s per user at that point
#   kv_bytes = KV-cache bytes per token of context in the deployed precision
MODELS = {
    "opus":   {"label": "Claude Opus 5.5 (API / Bedrock)", "kind": "proprietary",
               "price": None, "bedrock_burndown": 10, "bedrock_default_tpm": 30e6,
               "selfhost": None, "kv_bytes": None},
    "sonnet": {"label": "Claude Sonnet 5.5 (API / Bedrock)", "kind": "proprietary",
               "price": None, "bedrock_burndown": 5, "bedrock_default_tpm": 6e6,   # burndown for Sonnet 5.5 not named in AWS text; 5x = Sonnet 4.6
               "selfhost": None, "kv_bytes": None},
    "k3":     {"label": "Kimi K3 (2.78T / 104B active)", "kind": "open",
               "price": (3.00, 0.30, 15.00), "bedrock_burndown": 1, "bedrock_default_tpm": 10e6,
               "selfhost": {"hw": "GB300 NVL72, vLLM, MXFP4, c48 on 8 GPUs", "out_tps_gpu": 136, "user_tps": 38, "ttft": 1.15},
               "kv_bytes": 13.8e3, "state_bytes": 434e6,   # + 434 MB recurrent state per sequence (FP32)
               "kv_tokens_gpu": 3.25e6 / 8},              # HBM KV room after weights: 3.25M tokens on 8x B300 (InferenceX)
    "glm":    {"label": "GLM-5.3 (744B / 40B active)", "kind": "open",
               "price": (1.40, 0.26, 4.40), "bedrock_burndown": 1, "bedrock_default_tpm": 100e6,
               "selfhost": {"hw": "GB300 NVL72, SGLang P/D, FP4, c128 on 32 GPUs (GLM-5.2 run)", "out_tps_gpu": 149, "user_tps": 101, "ttft": 2.33},
               "kv_bytes": 44.9e3},
    "dsv4":   {"label": "DeepSeek V4-Pro (1.6T / 49B active)", "kind": "open",
               "price": (1.32, 0.044, 3.96), "bedrock_burndown": 1, "bedrock_default_tpm": 100e6,
               "selfhost": {"hw": "B300, SGLang, FP4, c384 on 8 GPUs", "out_tps_gpu": 739, "user_tps": 37, "ttft": 2.94},
               "kv_bytes": 5.0e3,
               "kv_tokens_gpu": 43e6 / 8},                # HBM KV working set 43M tokens on 8x B300 at c384 (InferenceX)
    "flash":  {"label": "DeepSeek V4.1-Flash (552B backbone)", "kind": "open",
               "price": (0.30, 0.006, 1.20), "bedrock_burndown": 1, "bedrock_default_tpm": 100e6,
               "selfhost": {"hw": "B300, vLLM, FP4, c192 on 2 GPUs", "out_tps_gpu": 3059, "user_tps": 60, "ttft": 0.25},
               "kv_bytes": 0.89e3},
}

# Share of each role's calls routed to each model.
MODEL_MIXES = {
    "MX1_frontier": {
        "label": "MX1. Frontier API only (Opus share follows Anthropic's own split: 10% of chat, 54% of coding sessions)",
        "OA": {"opus": 0.10, "sonnet": 0.90},
        "SE": {"opus": 0.54, "sonnet": 0.46},
        "RD": {"opus": 0.50, "sonnet": 0.50},
    },
    "MX2_tiered": {
        "label": "MX2. Tiered routing (small open model for OA, open flagships + frontier for coding and R&D)",
        "OA": {"flash": 0.80, "glm": 0.20},
        "SE": {"k3": 0.40, "dsv4": 0.30, "opus": 0.30},
        "RD": {"dsv4": 0.50, "opus": 0.30, "flash": 0.20},
    },
    "MX3_open": {
        "label": "MX3. Open-weight only (self-hosted or managed open-weight endpoints)",
        "OA": {"flash": 1.00},
        "SE": {"glm": 0.50, "k3": 0.50},
        "RD": {"dsv4": 1.00},
    },
    "MX4_single": {
        "label": "MX4. One open flagship for everything (Kimi K3)",
        "OA": {"k3": 1.00},
        "SE": {"k3": 1.00},
        "RD": {"k3": 1.00},
    },
}

EFFECTIVE_PRICE_PER_M = 0.72   # US$ per million tokens, observed blended effective price (Ramp, April 2026)


# --------------------------------------------------------------------------------------
# 2. Core functions
# --------------------------------------------------------------------------------------

def per_seat_usage(role, level):
    """Usage per active user-day and per licensed seat (weekday / week / month)."""
    R = ROLES[role]
    p = R["levels"][level]
    per_call = p["u"] + p["c"] + p["o"]
    day_calls = p["r"]
    day = {"calls": day_calls, "u": day_calls * p["u"], "c": day_calls * p["c"], "o": day_calls * p["o"],
           "all": day_calls * per_call}
    seat_weekday = {k: v * p["a"] for k, v in day.items()}
    week_factor = 5 + 2 * R["weekend"]
    seat_week = {k: v * week_factor for k, v in seat_weekday.items()}
    seat_month = {k: v * PEAK["weeks_per_month"] for k, v in seat_week.items()}
    return {"role": role, "level": level, "a": p["a"], "per_call": per_call,
            "cache_share_of_input": p["c"] / (p["u"] + p["c"]),
            "active_user_day": day, "seat_weekday": seat_weekday, "seat_week": seat_week, "seat_month": seat_month}


def k_factor(m, peak=PEAK):
    if m <= 0:
        return peak["k_floor"]
    return max(peak["k_floor"], 1 + 3 / math.sqrt(m))


def pool_peak(streams, peak=PEAK, v=None):
    """streams: list of dicts {m, u, c, o, ttft} routed to ONE endpoint/pool. Returns the pooled peak."""
    v = v or peak["v"]
    m_pool = sum(s["m"] for s in streams)
    k = k_factor(m_pool, peak)
    rpm = m_pool * k
    U = sum(s["m"] * k * s["u"] for s in streams) * peak["f_u"]
    C = sum(s["m"] * k * s["c"] for s in streams) * peak["f_c"]
    O = sum(s["m"] * k * s["o"] for s in streams) * peak["f_o"]
    L = sum(s["m"] * k / 60 * (s["ttft"] + s["o"] / v) for s in streams)
    L999 = L + peak["z999"] * math.sqrt(L) if L > 0 else 0.0
    ctx = (sum(s["m"] * (s["u"] + s["c"] + s["o"]) for s in streams) / m_pool) if m_pool else 0.0
    return {"m": m_pool, "k": k, "rpm": rpm, "U": U, "C": C, "O": O, "all": U + C + O,
            "L": L, "L999": L999, "avg_ctx": ctx}


def role_stream(n_seats, role, level, s, d, share=1.0):
    p = ROLES[role]["levels"][level]
    calls_day = n_seats * p["a"] * p["r"] * share
    return {"role": role, "calls_day": calls_day, "m": calls_day * s / 60 * d,
            "u": p["u"], "c": p["c"], "o": p["o"], "ttft": ROLES[role]["ttft"]}


def scenario(N, mix_key, level, s=None, peak=PEAK, levels_by_role=None):
    """One row of the big matrix: all roles pooled on one endpoint."""
    s = s if s is not None else peak["s_single_tz"]
    mix = ROLE_MIXES[mix_key]
    streams, daily, monthly = [], {"calls": 0.0, "all": 0.0}, {"all": 0.0}
    by_role = {}
    for role in ROLES:
        n = N * mix[role]
        if n <= 0:
            continue
        lvl = (levels_by_role or {}).get(role, level)
        st = role_stream(n, role, lvl, s, peak["d"])
        streams.append(st)
        us = per_seat_usage(role, lvl)
        daily["calls"] += n * us["seat_weekday"]["calls"]
        daily["all"] += n * us["seat_weekday"]["all"]
        monthly["all"] += n * us["seat_month"]["all"]
        by_role[role] = {"seats": n, "weekday_tokens": n * us["seat_weekday"]["all"]}
    pk = pool_peak(streams, peak)
    out = {"N": N, "mix": mix_key, "level": level, "s": s, **pk,
           "weekday_calls": daily["calls"], "weekday_tokens": daily["all"], "month_tokens": monthly["all"],
           "month_tokens_per_employee": monthly["all"] / N,
           "se_share_of_tokens": (by_role.get("SE", {}).get("weekday_tokens", 0.0) / daily["all"]) if daily["all"] else 0.0,
           "month_cost_effective_usd": monthly["all"] / 1e6 * EFFECTIVE_PRICE_PER_M}
    out.update(platform_units(pk))
    return out


def platform_units(pk):
    """Translate one pool's peak (U, C, O tokens/min) into each platform's own quota definition."""
    U, C, O = pk["U"], pk["C"], pk["O"]
    return {
        "anthropic_itpm": U, "anthropic_otpm": O,                    # cache reads excluded
        "bedrock_tpm_b5": U + 5 * O, "bedrock_tpm_b10": U + 10 * O, "bedrock_tpm_b15": U + 15 * O,
        "bedrock_tpm_open": U + O,                                   # open-weight models: 1x output, cache reads excluded
        "azure_ptu_gpt61sol": (U + 0.1 * C + 5 * O) / 3000,          # normalised TPM / 3,000 per PTU
        "google_gsu_opus55": (U + 0.05 * C + 5 * O) / 60 / 261,      # tokens/s per GSU = 261
        "google_gsu_gemini38flash": (U + 0.1 * C + 5 * O) / 60 / 675,
        "cerebras_uncached_tpm": U + O, "cerebras_total_tpm": U + C + O,
    }


def model_mix_scenario(N, mix_key, level, mm_key, s=None, peak=PEAK):
    s = s if s is not None else peak["s_single_tz"]
    mix, mm = ROLE_MIXES[mix_key], MODEL_MIXES[mm_key]
    pools = {}
    for role in ROLES:
        n = N * mix[role]
        if n <= 0:
            continue
        for model, share in mm[role].items():
            pools.setdefault(model, []).append(role_stream(n, role, level, s, peak["d"], share))
    rows = []
    for model, streams in pools.items():
        M = MODELS[model]
        # call duration uses the self-host operating point's per-user speed when there is one
        v = M["selfhost"]["user_tps"] if M["selfhost"] else peak["v"]
        pk = pool_peak(streams, peak, v=v)
        row = {"model": model, "label": M["label"], **pk}
        b = M["bedrock_burndown"]
        row["bedrock_tpm"] = pk["U"] + b * pk["O"]
        row["bedrock_default_tpm"] = M["bedrock_default_tpm"]
        row["bedrock_quota_multiple"] = row["bedrock_tpm"] / M["bedrock_default_tpm"]
        row["anthropic_itpm"], row["anthropic_otpm"] = pk["U"], pk["O"]
        if M["selfhost"]:
            sh = M["selfhost"]
            out_tps = pk["O"] / 60
            row["out_tps"] = out_tps
            row["gpus_decode"] = out_tps / sh["out_tps_gpu"] / peak["util"]
            row["selfhost_hw"] = sh["hw"]
            hot_tokens = pk["L999"] * pk["avg_ctx"]
            warm_sessions = peak["warm_sessions_per_inflight"] * pk["L"]
            warm_tokens = warm_sessions * peak["resident_ctx_factor"] * pk["avg_ctx"]
            state = M.get("state_bytes", 0.0)
            row["hot_tokens"] = hot_tokens
            row["kv_hot_gb"] = (hot_tokens * M["kv_bytes"] + pk["L999"] * state) / 1e9
            row["warm_sessions"] = warm_sessions
            row["warm_tokens"] = warm_tokens
            row["kv_warm_tb"] = (warm_tokens * M["kv_bytes"] + warm_sessions * state) / 1e12
            if M.get("kv_tokens_gpu"):
                row["gpus_kv_hot"] = hot_tokens / M["kv_tokens_gpu"]
            row["selfhost_user_tps"] = sh["user_tps"]
            row["selfhost_ttft"] = sh["ttft"]
        if M["price"]:
            pi, pc, po = M["price"]
            # monthly tokens routed to this model, split by class
            mu = mc = mo = 0.0
            for role in ROLES:
                n = N * mix[role]
                if n <= 0 or model not in mm[role]:
                    continue
                us = per_seat_usage(role, level)
                share = mm[role][model]
                mu += n * share * us["seat_month"]["u"]
                mc += n * share * us["seat_month"]["c"]
                mo += n * share * us["seat_month"]["o"]
            row["month_cost_list_usd"] = (mu * pi + mc * pc + mo * po) / 1e6
            row["month_tokens"] = mu + mc + mo
        rows.append(row)
    return rows


# --------------------------------------------------------------------------------------
# 3. Formatting helpers
# --------------------------------------------------------------------------------------

def h(x, digits=3):
    """Human-readable number with K / M / B / T suffix."""
    if x is None:
        return "–"
    ax = abs(x)
    # round to `digits` significant figures first so 999,600 prints as 1M, not 1000K
    if ax > 0:
        x = round(x, digits - 1 - int(math.floor(math.log10(ax))))
        ax = abs(x)
    for lim, suf in ((1e12, "T"), (1e9, "B"), (1e6, "M"), (1e3, "K")):
        if ax >= lim:
            val = x / lim
            return _trim(f"{val:.{max(0, digits - len(str(int(abs(val)))))}f}") + suf
    if ax >= 100:
        return f"{x:.0f}"
    if ax >= 10:
        return _trim(f"{x:.1f}")
    return _trim(f"{x:.2f}")


def _trim(s):
    """Drop trailing zeros only after a decimal point (never from an integer)."""
    return s.rstrip("0").rstrip(".") if "." in s else s


def md_table(headers, rows):
    lines = ["| " + " | ".join(headers) + " |", "|" + "|".join(["---"] * len(headers)) + "|"]
    for r in rows:
        lines.append("| " + " | ".join(str(x) for x in r) + " |")
    return "\n".join(lines)


# --------------------------------------------------------------------------------------
# 4. Outputs
# --------------------------------------------------------------------------------------

def out_role_usage():
    rows, js = [], []
    for role in ROLES:
        for lvl in ("low", "base", "high"):
            us = per_seat_usage(role, lvl)
            p = ROLES[role]["levels"][lvl]
            d, w, mth = us["active_user_day"], us["seat_week"], us["seat_month"]
            sd = us["seat_weekday"]
            rows.append([ROLES[role]["label"], lvl, f"{p['a']:.0%}", p["r"], h(p["u"]), h(p["c"]), h(p["o"]),
                         f"{us['cache_share_of_input']:.0%}", h(d["all"]), h(sd["calls"]), h(sd["all"]),
                         h(w["calls"]), h(w["all"]), h(mth["calls"]), h(mth["all"]), h(mth["u"]), h(mth["c"]), h(mth["o"])])
            js.append(us)
    md = md_table(["Role", "Level", "Active/weekday (a)", "Calls/active day (r)", "Uncached in/call (u)",
                   "Cache-read in/call (c)", "Out/call (o)", "Cache share of input", "Tokens/active user-day",
                   "Calls/seat/weekday", "Tokens/seat/weekday", "Calls/seat/week", "Tokens/seat/week",
                   "Calls/seat/month", "Tokens/seat/month", "…uncached in/month", "…cache-read/month", "…output/month"], rows)
    return md, js


def out_matrix():
    rows, js = [], []
    for N in POPULATIONS:
        for mix in ROLE_MIXES:
            for lvl in ("low", "base", "high"):
                r = scenario(N, mix, lvl)
                js.append(r)
                rows.append([f"{N:,}", ROLE_MIXES[mix]["label"], lvl, h(r["rpm"]), h(r["U"]), h(r["C"]), h(r["O"]), h(r["all"]),
                             h(r["bedrock_tpm_b10"]), h(r["L"]), h(r["L999"]), f"{r['k']:.2f}",
                             h(r["weekday_calls"]), h(r["weekday_tokens"]), h(r["month_tokens"]),
                             h(r["month_tokens_per_employee"]), f"{r['se_share_of_tokens']:.0%}",
                             "$" + h(r["month_cost_effective_usd"])])
    headers = ["Employees", "Role mix", "Level", "Peak RPM", "Peak uncached-input TPM (= Anthropic ITPM)",
               "Peak cache-read TPM", "Peak output TPM (= OTPM)", "Peak all-token TPM",
               "Bedrock-style TPM (U + 10×O)", "In-flight calls (mean)", "In-flight (99.9%)", "k",
               "Calls/weekday", "Tokens/weekday", "Tokens/month", "Tokens/employee/month", "Coding share of tokens",
               "Month cost @ $0.72/M effective"]
    return md_table(headers, rows), js, headers


def out_model_mix():
    blocks, js = [], []
    cases = [(10_000, "B_manufacturing", "base"), (100_000, "B_manufacturing", "base"),
             (100_000, "B_manufacturing", "high"), (100_000, "D_software", "base")]
    for N, mix, lvl in cases:
        for mm in MODEL_MIXES:
            rows = model_mix_scenario(N, mix, lvl, mm)
            js.append({"N": N, "mix": mix, "level": lvl, "model_mix": mm, "pools": rows})
            t = []
            for r in rows:
                t.append([r["label"], h(r["rpm"]), h(r["U"]), h(r["C"]), h(r["O"]), h(r["all"]),
                          h(r["bedrock_tpm"]), f"{r['bedrock_quota_multiple']:.2f}×",
                          h(r["L"]), h(r["L999"]),
                          (h(r["gpus_decode"]) + f" ({r['selfhost_hw']}; {r['selfhost_user_tps']} tok/s per user, TTFT {r['selfhost_ttft']} s)") if "gpus_decode" in r else "n/a (API only)",
                          h(r["gpus_kv_hot"]) if "gpus_kv_hot" in r else "–",
                          h(r.get("kv_hot_gb")) + " GB" if "kv_hot_gb" in r else "–",
                          h(r.get("kv_warm_tb")) + " TB" if "kv_warm_tb" in r else "–",
                          ("$" + h(r["month_cost_list_usd"])) if "month_cost_list_usd" in r else "see ch.5 prices"])
            blocks.append(f"### {N:,} employees · {ROLE_MIXES[mix]['label']} · level={lvl} · {MODEL_MIXES[mm]['label']}\n\n" +
                          md_table(["Model pool", "Peak RPM", "Uncached-in TPM", "Cache-read TPM", "Output TPM",
                                    "All-token TPM", "Bedrock-counted TPM", "× default Bedrock quota",
                                    "In-flight (mean)", "In-flight (99.9%)", "GPUs, decode-bound (÷0.8 util; operating point)",
                                    "GPUs, HBM-KV-bound (in-flight contexts)",
                                    "Hot KV (in-flight)", "Warm KV (sessions kept for cache hits)",
                                    "Month cost at first-party list price"], t))
    return "\n\n".join(blocks), js


def out_sensitivity():
    base_kwargs = dict(N=100_000, mix_key="B_manufacturing", level="base")
    base = scenario(**base_kwargs)
    rows = [["Base case (100,000 employees, mix B, base level, single time zone)", h(base["rpm"]), h(base["U"]), h(base["C"]),
             h(base["O"]), h(base["all"]), h(base["L999"]), "1.00×", "1.00×"]]
    js = [{"name": "base", **base}]

    def add(name, r):
        rows.append([name, h(r["rpm"]), h(r["U"]), h(r["C"]), h(r["O"]), h(r["all"]), h(r["L999"]),
                     f"{r['rpm'] / base['rpm']:.2f}×", f"{r['U'] / base['U']:.2f}×"])
        js.append({"name": name, **r})

    add("Global population (busy-hour share 6.5% instead of 11%)", scenario(**base_kwargs, s=PEAK["s_global"]))
    pk = deepcopy(PEAK); pk["s_single_tz"] = 0.125
    add("Sharper day (busy-hour share 12.5%)", scenario(**base_kwargs, peak=pk))
    pk = deepcopy(PEAK); pk["d"] = 1.0
    add("Average weekday instead of P95 weekday (d = 1.0)", scenario(**base_kwargs, peak=pk))
    pk = deepcopy(PEAK); pk["d"] = 1.5
    add("Month-end / release peak (d = 1.5)", scenario(**base_kwargs, peak=pk))
    add("Coding at high level, others base", scenario(**base_kwargs, levels_by_role={"SE": "high"}))
    add("Coding at low level, others base", scenario(**base_kwargs, levels_by_role={"SE": "low"}))
    add("OA at high level (office agents), others base", scenario(**base_kwargs, levels_by_role={"OA": "high"}))
    add("R&D at high level, others base", scenario(**base_kwargs, levels_by_role={"RD": "high"}))
    # prefix caching unavailable: every cache-read token becomes uncached input
    saved = deepcopy(ROLES)
    for role in ROLES:
        for lvl in ROLES[role]["levels"].values():
            lvl["u"], lvl["c"] = lvl["u"] + lvl["c"], 0
    add("No prefix / prompt caching (all input uncached)", scenario(**base_kwargs))
    ROLES.clear(); ROLES.update(deepcopy(saved))
    # output doubled (heavier reasoning)
    for role in ROLES:
        for lvl in ROLES[role]["levels"].values():
            lvl["o"] *= 2
    add("Output tokens ×2 (more reasoning)", scenario(**base_kwargs))
    ROLES.clear(); ROLES.update(deepcopy(saved))
    for v, name in ((40, "Slower streams (40 tok/s per user)"), (300, "Fast streams (300 tok/s per user)"),
                    (1000, "Wafer-scale class streams (1,000 tok/s per user)")):
        pk = deepcopy(PEAK); pk["v"] = v
        add(name, scenario(**base_kwargs, peak=pk))
    md = md_table(["Change from base", "Peak RPM", "Uncached-in TPM", "Cache-read TPM", "Output TPM", "All-token TPM",
                   "In-flight (99.9%)", "RPM vs base", "Uncached-in TPM vs base"], rows)
    return md, js


def out_crosschecks():
    """Compare the model with published sizing anchors."""
    lines = []
    # 1. Anthropic Claude Code table at 500+ users: 10-15K TPM and 0.25-0.35 RPM per user.
    for lvl, a_override in (("base", None), ("base", 0.70)):
        saved = ROLES["SE"]["levels"][lvl]["a"]
        if a_override:
            ROLES["SE"]["levels"][lvl]["a"] = a_override
        r = scenario(10_000, "P_SE", lvl)
        lines.append(f"- Coding only, 10,000 developers, level={lvl}, a={ROLES['SE']['levels'][lvl]['a']:.2f}: "
                     f"peak {r['rpm'] / 10_000:.3f} RPM per licensed developer; all-token {r['all'] / 10_000 / 1e3:.1f}K TPM; "
                     f"uncached+output {(r['U'] + r['O']) / 10_000 / 1e3:.2f}K TPM per developer. "
                     f"Anthropic's table for 500+ users: 0.25-0.35 RPM and 10-15K TPM per user.")
        ROLES["SE"]["levels"][lvl]["a"] = saved
    # 2. AWS guidance default: 225M tokens per user per month.
    us = per_seat_usage("SE", "base")
    lines.append(f"- Coding base level: {us['active_user_day']['all'] / 1e6:.1f}M tokens per active developer-day "
                 f"(Anthropic $13/day at $0.57-1.00 per M = 13-23M); {us['seat_month']['all'] / 1e6:.0f}M tokens per licensed seat per month "
                 f"and {us['active_user_day']['all'] * 19 / 1e6:.0f}M per month for a developer active 19 days "
                 f"(AWS default quota: 225M per user per month).")
    # 3. Researcher's illustrative blend: 10,000-person firm, 70/20/10 at the medians -> ~16.5B tokens per working day.
    ROLE_MIXES["_tmp"] = {"label": "tmp", "OA": 0.70, "SE": 0.20, "RD": 0.10}
    r = scenario(10_000, "_tmp", "base")
    lines.append(f"- 10,000 employees at 70/20/10, base level: {r['weekday_tokens'] / 1e9:.1f}B tokens per weekday "
                 f"({r['se_share_of_tokens']:.0%} from coding); usage notes derive ~16.5B with 18M tokens per developer-day.")
    del ROLE_MIXES["_tmp"]
    # 4. Meta: 23.6M tokens per employee per calendar day.
    r = scenario(85_000, "D_software", "high")
    lines.append(f"- 85,000 employees, software mix, high level: {r['month_tokens'] / 85_000 / 30.4 / 1e6:.1f}M tokens per employee per calendar day "
                 f"(Meta, April 2026: 23.6M across all employees).")
    return "\n".join(lines)


def main():
    usage_md, usage_js = out_role_usage()
    matrix_md, matrix_js, matrix_headers = out_matrix()
    mm_md, mm_js = out_model_mix()
    sens_md, sens_js = out_sensitivity()
    cross = out_crosschecks()

    with open(os.path.join(OUT, "role_usage.md"), "w") as f:
        f.write(usage_md + "\n")
    with open(os.path.join(OUT, "matrix.md"), "w") as f:
        f.write(matrix_md + "\n")
    with open(os.path.join(OUT, "model_mix.md"), "w") as f:
        f.write(mm_md + "\n")
    with open(os.path.join(OUT, "sensitivity.md"), "w") as f:
        f.write(sens_md + "\n")
    with open(os.path.join(OUT, "crosschecks.md"), "w") as f:
        f.write(cross + "\n")
    with open(os.path.join(OUT, "matrix.csv"), "w", newline="") as f:
        w = csv.writer(f)
        keys = ["N", "mix", "level", "s", "m", "k", "rpm", "U", "C", "O", "all", "L", "L999", "avg_ctx", "weekday_calls",
                "weekday_tokens", "month_tokens", "month_tokens_per_employee", "se_share_of_tokens",
                "month_cost_effective_usd", "anthropic_itpm", "anthropic_otpm", "bedrock_tpm_b5", "bedrock_tpm_b10",
                "bedrock_tpm_b15", "bedrock_tpm_open", "azure_ptu_gpt61sol", "google_gsu_opus55",
                "google_gsu_gemini38flash", "cerebras_uncached_tpm", "cerebras_total_tpm"]
        w.writerow(keys)
        for r in matrix_js:
            w.writerow([r[k] for k in keys])
    with open(os.path.join(OUT, "model.json"), "w") as f:
        json.dump({"roles": ROLES, "peak": PEAK, "populations": POPULATIONS, "role_mixes": ROLE_MIXES,
                   "models": MODELS, "model_mixes": MODEL_MIXES, "effective_price_per_m": EFFECTIVE_PRICE_PER_M,
                   "role_usage": usage_js, "matrix": matrix_js, "model_mix": mm_js, "sensitivity": sens_js}, f, indent=1)
    # self-test vector for the JavaScript port
    st = scenario(100_000, "B_manufacturing", "base")
    with open(os.path.join(OUT, "selftest.json"), "w") as f:
        json.dump({"case": "N=100000, mix=B_manufacturing, level=base, s=0.11", "expect": st}, f, indent=1)
    print("== role usage ==\n" + usage_md)
    print("\n== cross-checks ==\n" + cross)
    print("\n== sensitivity ==\n" + sens_md)
    print(f"\nmatrix rows: {len(matrix_js)}; model-mix blocks: {len(mm_js)}")


if __name__ == "__main__":
    main()
