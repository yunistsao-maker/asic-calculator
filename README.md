# Inference ASIC Atlas（推論晶片圖鑑）

A static website on AI inference across AWS Trainium and Inferentia, Google TPU, NVIDIA and AMD GPUs,
and Cerebras: measured speed and TTFT for Kimi, GLM, DeepSeek, Qwen and proprietary models, engine and
technique support, 200K and 1M context, cost, deployment options, and a TPM / RPM capacity calculator
for 1,000 to 100,000 employees. The content is in Traditional Chinese. Data as of 2026-10-04,
fact-checked on 2026-10-05: 777 sources re-read, 179 corrections, all listed on the site.

The built site is committed in `site/dist/` (16 pages). Hosting it needs no build step.

## Deploy on AWS Amplify Hosting

Connect this repository in the Amplify console. `amplify.yml` serves `site/dist` as it is, and every push
to `main` redeploys. Step-by-step instructions, the zip and CLI alternatives, and the 404 rule are in
[DEPLOY-AMPLIFY.md](DEPLOY-AMPLIFY.md).

## Look at it locally

```sh
python3 -m http.server 8000 --directory site/dist     # then open http://localhost:8000
```

Opening `site/dist/index.html` straight from disk also works.

## Layout

```
chapters/        00-overview.md, 01 … 11 (the survey), 12-sources.md, 13-factcheck.md   Traditional Chinese
calc/            capacity_model.py (chapter 10 reference model) and its outputs in calc/out/
factcheck/       corrections.jsonl   179 logged corrections (chapter, kind, before, after, reason)
                 sources_site.json   777 cited sources with how each was verified
                 grounding.jsonl     per text unit: which numbers, versions and quotes were found in the cited source
site/
  dist/          the built site (committed; this is what Amplify serves)
  build.py       chapters/*.md -> site/dist/*.html
  meta.py        page titles, tab labels, lead sentences
  lib/           render.py (Markdown -> page parts), widgets.py (charts, matrix, calculator shell), normalize.py
  static/        site.css, site.js, planner-model.js, planner.js, matrix.js, longctx.js, search.js, sources.js
  vendor/        IBM Plex woff2, KaTeX CSS and fonts, with their licences
  tests/         check_site.py, test_model.js, interact.py, shots.py
  make.sh        build + offline checks (+ zip)
amplify.yml      Amplify build settings: serve site/dist
DEPLOY-AMPLIFY.md, amplify-redirects.json
```

## Rebuild after editing a chapter

```sh
pip install -r site/requirements.txt      # markdown-it-py, beautifulsoup4
site/make.sh                              # rewrites site/dist, runs check_site.py and test_model.js
site/make.sh zip                          # also writes release/inference-asic-atlas-site.zip (not committed)
```

Commit `site/dist` together with the chapter change; the build is deterministic, so the diff shows only
what changed. Tested with Python 3.13 and Node.js 22. Node.js is needed for `tests/test_model.js`, and for
the build only when a chapter contains a formula that is not yet in `site/katex-cache.json`; in that case
run `npm ci` in `site/tools` first. `python3 site/tools/vendor.py` refreshes `site/vendor/` from
`site/tools/node_modules`.

Browser checks (optional): `pip install playwright && playwright install chromium`, then
`python3 site/tests/interact.py`.

## How a chapter becomes a page

- `## ` headings become the page's tabs, `### ` headings become sub-tabs. A section named
  「網站呈現建議」 is left out. Tab labels come from `site/meta.py`; the number of labels must match the
  number of `## ` sections or the build stops.
- A paragraph that starts with `**表 N-M 標題**` becomes the caption of the table that follows and gives
  it the anchor `#tN-M`; 「表 N-M」 and 「第 N 章」 anywhere in the text become links.
- Evidence grades written as `[A]`, `（等級 B）`, `[C，…]` and similar become badges.
- Cells that start with 支援 / 部分 / 實驗 / 不支援 / 查無 (and the other status words in
  `render.CHIP_WORDS`) become status chips.
- Fenced blocks tagged `latex` are rendered with KaTeX at build time.
- Chapters 1, 4 and 10 are written with half-width punctuation; `lib/normalize.py` converts it for display.

## Charts and interactive parts

All of them read the chapter text at build time, so they cannot drift away from the tables:

| Page | Part | Source |
|---|---|---|
| 01 | memory and bandwidth per chip | the 「每顆晶片」 table |
| 04 | flagship endpoints; model × hardware grid | tables 4-6 and 4-13 to 4-16 |
| 06 | technique matrix (34 × 6) | the four tables of the chapter's first section |
| 07 | context limits, KV bars and calculator, TTFT chart | tables 7-1, 7-6, 7-7 and figures asserted with `need()` |
| 08 | gpt-oss-120b across ten endpoints | table 8-6 |
| 09 | decision tree | the nested list of the chapter |
| 10 | capacity calculator | `static/planner-model.js`, a port of `calc/capacity_model.py` |

Sentences written by hand in `lib/widgets.py` quote figures that must exist in the chapter; `need(n, …)`
stops the build when one of them is no longer there.

## Checks

- `tests/check_site.py`: every number and every source link of chapters 1–11 appears on its page as often
  as in the chapter; internal links, anchors and assets resolve; ids are unique; no leftover Markdown.
- `tests/test_model.js`: the JavaScript capacity model against `calc/out/model.json` and `selftest.json`
  (3,175 values).
- `tests/interact.py`: browser checks in Chromium (tabs, deep links, table tools, matrix, calculators,
  search, sources, themes, phone width, print, no JavaScript).

## Changing the capacity model

Edit `calc/capacity_model.py`, run it to refresh `calc/out/`, mirror the change in
`site/static/planner-model.js`, and run `node site/tests/test_model.js`. Chapter 10's tables are the
Python output; the calculator page is the JavaScript port.

## Third-party files

`site/vendor/` (copied into `site/dist/assets/`) contains IBM Plex fonts under the SIL Open Font License
1.1 and KaTeX under the MIT License; the licence texts are next to the files.
