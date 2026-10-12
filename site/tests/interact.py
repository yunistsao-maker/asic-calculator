#!/usr/bin/env python3
"""Browser checks of every interactive part of the site (Playwright, Chromium).
Serves site/dist itself on a free port; `python3 tests/interact.py` exits non-zero when a check fails."""
import functools, http.server, json, math, os, socket, sys, threading
from playwright.sync_api import sync_playwright

SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIST = os.path.join(SITE, 'dist')
REF = json.load(open(os.path.join(os.path.dirname(SITE), 'calc', 'out', 'model.json'), encoding='utf-8'))


class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass


class Server(http.server.ThreadingHTTPServer):
    def handle_error(self, request, client_address):   # the browser drops connections when a context closes
        pass


def serve():
    s = socket.socket(); s.bind(('127.0.0.1', 0)); port = s.getsockname()[1]; s.close()
    srv = Server(('127.0.0.1', port), functools.partial(Quiet, directory=DIST))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv, 'http://127.0.0.1:%d/' % port


results = []


def check(name, ok, detail=''):
    results.append((name, bool(ok), detail))
    print(('PASS ' if ok else 'FAIL ') + name + ((' — ' + str(detail)) if detail and not ok else ''))


def visible_panels(page, sel):
    return page.evaluate("""(sel) => Array.from(document.querySelectorAll(sel)).filter(e => e.offsetParent !== null).map(e => e.id)""", sel)


def main():
    srv, BASE = serve()
    errors = []
    with sync_playwright() as p:
        b = p.chromium.launch()

        def ctx_page(w=1440, h=900, theme='light', **kw):
            c = b.new_context(viewport={'width': w, 'height': h}, color_scheme=theme, **kw)
            pg = c.new_page()
            pg.on('console', lambda m: errors.append((pg.url, m.text)) if m.type == 'error' else None)
            pg.on('pageerror', lambda e: errors.append((pg.url, 'PAGEERROR ' + str(e))))
            pg.on('requestfailed', lambda r: errors.append((pg.url, 'REQUESTFAILED ' + r.url)) if '127.0.0.1' in r.url else None)
            return c, pg

        pages = sorted(f for f in os.listdir(DIST) if f.endswith('.html'))

        # ---------------------------------------------------------- 1. every page, every tab
        c, pg = ctx_page()
        total_tabs = 0
        for f in pages:
            pg.goto(BASE + f, wait_until='load')
            pg.wait_for_timeout(120)
            n = pg.evaluate("document.querySelectorAll('.tablist > [role=tab]').length")
            bad = []
            for i in range(n):
                pg.evaluate("(i) => document.querySelectorAll('.tablist > [role=tab]')[i].click()", i)
                vis = visible_panels(pg, '.tabs > .panel')
                want = pg.evaluate("(i) => document.querySelectorAll('.tablist > [role=tab]')[i].getAttribute('aria-controls')", i)
                if vis != [want] or pg.evaluate('location.hash') != '#' + want:
                    bad.append((i, vis, want))
                # sub-tabs of this panel
                m = pg.evaluate("(id) => document.querySelectorAll('#' + id + ' .subtablist > [role=tab]').length", want)
                for j in range(m):
                    pg.evaluate("([id, j]) => document.querySelectorAll('#' + id + ' .subtablist > [role=tab]')[j].click()", [want, j])
                    sv = visible_panels(pg, '#' + want + ' .subtabs > .subpanel')
                    sw = pg.evaluate("([id, j]) => document.querySelectorAll('#' + id + ' .subtablist > [role=tab]')[j].getAttribute('aria-controls')", [want, j])
                    if sv != [sw]:
                        bad.append((i, j, sv, sw))
                    total_tabs += 1
                total_tabs += 1
            over = pg.evaluate('document.documentElement.scrollWidth - document.documentElement.clientWidth')
            check('tabs switch on %s (%d tabs)' % (f, n), not bad, bad[:3])
            check('no horizontal page overflow on %s' % f, over <= 0, over)
        print('   tabs and sub-tabs clicked:', total_tabs)

        # ---------------------------------------------------------- 2. deep links and keyboard
        pg.goto(BASE + '07-long-context.html#t7-9', wait_until='load'); pg.wait_for_timeout(300)
        r = pg.evaluate("(() => { const e = document.getElementById('t7-9'); const r = e.getBoundingClientRect(); return {vis: e.offsetParent !== null, top: r.top}; })()")
        check('deep link #t7-9 opens the panel and scrolls to the table', r['vis'] and 0 <= r['top'] < 400, r)
        pg.goto(BASE + '07-long-context.html#s2-3', wait_until='load'); pg.wait_for_timeout(300)
        check('deep link #s2-3 selects tab 2 and sub-tab 3', visible_panels(pg, '.tabs > .panel') == ['s2'] and visible_panels(pg, '#s2 .subtabs > .subpanel') == ['s2-3'])
        pg.goto(BASE + '01-silicon.html', wait_until='load')
        pg.focus('.tablist > [role=tab][aria-selected=true]')
        pg.keyboard.press('ArrowRight'); pg.keyboard.press('ArrowRight')
        check('arrow keys move between tabs', visible_panels(pg, '.tabs > .panel') == ['s3'], visible_panels(pg, '.tabs > .panel'))
        pg.keyboard.press('Home')
        check('Home key returns to the first tab', visible_panels(pg, '.tabs > .panel') == ['s1'])
        # cross-reference link to a table on another page
        pg.goto(BASE + '08-metrics.html', wait_until='load')
        href = pg.evaluate("(() => { const a = Array.from(document.querySelectorAll('a.xref')).find(a => /#t\\d+-\\d+$/.test(a.getAttribute('href')) && !a.getAttribute('href').startsWith('#')); return a ? a.getAttribute('href') : null; })()")
        if href:
            pg.goto(BASE + href, wait_until='load'); pg.wait_for_timeout(300)
            tid = href.split('#')[1]
            ok = pg.evaluate("(id) => { const e = document.getElementById(id); return !!e && e.offsetParent !== null; }", tid)
            check('cross-page table link %s lands on a visible table' % href, ok)
        # in-page xref inside a hidden panel
        pg.goto(BASE + '07-long-context.html', wait_until='load')
        tgt = pg.evaluate("""(() => { const a = Array.from(document.querySelectorAll('.panel.on a.xref[href^="#t"]')).find(a => { const e = document.getElementById(a.getAttribute('href').slice(1)); return e && e.offsetParent === null; }); if (!a) return null; a.click(); return a.getAttribute('href').slice(1); })()""")
        if tgt:
            pg.wait_for_timeout(300)
            check('in-page link to a table in a hidden panel reveals it (#%s)' % tgt, pg.evaluate("(id) => document.getElementById(id).offsetParent !== null", tgt))

        # ---------------------------------------------------------- 3. table tools
        pg.goto(BASE + '01-silicon.html', wait_until='load'); pg.wait_for_timeout(200)
        info = pg.evaluate("""(() => {
          const figs = Array.from(document.querySelectorAll('.panel.on figure.tbl')).filter(f => f.offsetParent !== null && f.querySelector('.tbl-tools input'));
          const f = figs[0]; if (!f) return null;
          f.setAttribute('data-test', '1');
          return {rows: f.querySelectorAll('tbody tr').length, cols: f.querySelectorAll('thead th').length};
        })()""")
        check('a table with a filter box exists on chapter 1', bool(info), info)
        if info:
            F = 'figure[data-test="1"]'
            first = pg.evaluate("(F) => document.querySelector(F + ' tbody tr td').textContent.trim().slice(0, 12)", F)
            pg.fill(F + ' .tbl-tools input', first[:6])
            shown = pg.evaluate("(F) => Array.from(document.querySelectorAll(F + ' tbody tr')).filter(r => !r.hidden).length", F)
            cnt = pg.inner_text(F + ' .tbl-tools .cnt')
            check('filter narrows the rows and updates the count', 0 < shown < info['rows'] and cnt.startswith('%d / %d' % (shown, info['rows'])), (shown, cnt))
            pg.fill(F + ' .tbl-tools input', '')
            shown = pg.evaluate("(F) => Array.from(document.querySelectorAll(F + ' tbody tr')).filter(r => !r.hidden).length", F)
            check('clearing the filter restores every row', shown == info['rows'])
            before = pg.evaluate("(F) => Array.from(document.querySelectorAll(F + ' tbody tr')).map(r => r.getAttribute('data-i'))", F)
            pg.click(F + ' thead th >> nth=0')
            st1 = pg.get_attribute(F + ' thead th >> nth=0', 'aria-sort')
            after = pg.evaluate("(F) => Array.from(document.querySelectorAll(F + ' tbody tr')).map(r => r.getAttribute('data-i'))", F)
            pg.click(F + ' thead th >> nth=0'); st2 = pg.get_attribute(F + ' thead th >> nth=0', 'aria-sort')
            pg.click(F + ' thead th >> nth=0'); st3 = pg.get_attribute(F + ' thead th >> nth=0', 'aria-sort')
            back = pg.evaluate("(F) => Array.from(document.querySelectorAll(F + ' tbody tr')).map(r => r.getAttribute('data-i'))", F)
            check('header click cycles descending, ascending, original order', (st1, st2, st3) == ('descending', 'ascending', None) and sorted(after) == sorted(before) and back == before, (st1, st2, st3))
        # numeric sort on the capacity chapter
        pg.goto(BASE + '10-capacity.html', wait_until='load'); pg.wait_for_timeout(300)
        res = pg.evaluate("""(() => {
          const out = [];
          const num = s => { const m = s.replace(/,/g, '').match(/^([\\d.]+)\\s?([KMBT])?/); return m ? parseFloat(m[1]) * ({K: 1e3, M: 1e6, B: 1e9, T: 1e12}[m[2]] || 1) : NaN; };
          for (const f of document.querySelectorAll('.tabs figure.tbl')) {
            const ths = Array.from(f.querySelectorAll('thead th'));
            const ci = ths.findIndex(t => /尖峰 RPM/.test(t.textContent));
            if (ci < 0 || f.querySelectorAll('tbody tr').length < 4 || !f.querySelector('.tbl-tools')) continue;
            IA.reveal(f, false);
            ths[ci].click();
            const vals = Array.from(f.querySelectorAll('tbody tr')).map(r => num(r.children[ci].textContent.trim())).filter(x => !isNaN(x));
            out.push({n: vals.length, vals: vals, sorted: vals.every((v, i) => i === 0 || vals[i - 1] >= v), bars: f.querySelectorAll('td.bar').length, state: ths[ci].getAttribute('aria-sort')});
            ths[ci].click(); ths[ci].click();
            break;
          }
          return out;
        })()""")
        check('numeric column sorts by value and draws proportional bars', bool(res) and res[0]['sorted'] and res[0]['bars'] > 0, res)
        # copy
        c2, pg2 = ctx_page(permissions=['clipboard-read', 'clipboard-write'])
        pg2.goto(BASE + '08-metrics.html#t8-19', wait_until='load'); pg2.wait_for_timeout(300)
        pg2.click('#t8-19 .tbl-tools button:has-text("複製")'); pg2.wait_for_timeout(200)
        clip = pg2.evaluate('navigator.clipboard.readText()')
        lines = clip.split('\n')
        nrows = pg2.evaluate("document.querySelectorAll('#t8-19 tbody tr').length")
        check('copy puts header plus every row on the clipboard as TSV', len(lines) == nrows + 1 and lines[0].count('\t') == 6, (len(lines), nrows, lines[0][:80]))
        # enlarge
        pg2.click('#t8-19 .tbl-tools button:has-text("放大")'); pg2.wait_for_timeout(200)
        o = pg2.evaluate("(() => { const d = document.querySelector('dialog.tbl-dialog'); return {open: d.open, has: !!d.querySelector('#t8-19')}; })()")
        check('enlarge opens the table in a full-screen dialog', o['open'] and o['has'], o)
        pg2.keyboard.press('Escape'); pg2.wait_for_timeout(200)
        o = pg2.evaluate("(() => { const d = document.querySelector('dialog.tbl-dialog'); const f = document.getElementById('t8-19'); return {open: d.open, back: !!f.closest('.panel'), label: Array.from(f.querySelectorAll('.tbl-tools button')).map(b => b.textContent)}; })()")
        check('Esc closes the dialog and puts the table back', (not o['open']) and o['back'] and '放大' in o['label'], o)
        wide = pg2.evaluate("(() => { const f = document.getElementById('t8-19'); return {wide: f.classList.contains('is-wide'), hint: !f.querySelector('.wide-hint').hidden, pos: getComputedStyle(f.querySelector('tbody tr > :first-child')).position}; })()")
        check('a wide table shows the scroll hint and keeps its first column in place', wide['wide'] and wide['hint'] and wide['pos'] == 'sticky', wide)
        c2.close()

        # ---------------------------------------------------------- 4. long table clipping (fact-check record)
        pg.goto(BASE + 'factcheck.html#s6', wait_until='load'); pg.wait_for_timeout(300)
        vis = pg.evaluate("Array.from(document.querySelectorAll('#s6 tbody tr')).filter(r => r.offsetParent !== null).length")
        tot = pg.evaluate("document.querySelectorAll('#s6 tbody tr').length")
        check('corrections table opens with 30 of %d rows' % tot, vis == 30 and tot > 150, (vis, tot))
        pg.fill('#s6 .tbl-tools input', 'WRONG')
        vis = pg.evaluate("Array.from(document.querySelectorAll('#s6 tbody tr')).filter(r => r.offsetParent !== null).length")
        nw = pg.evaluate("Array.from(document.querySelectorAll('#s6 tbody tr')).filter(r => /wrong/i.test(r.textContent)).length")
        check('filtering the corrections table searches all rows', vis == nw and nw > 30, (vis, nw))
        pg.fill('#s6 .tbl-tools input', '')
        pg.click('#s6 button.more')
        vis = pg.evaluate("Array.from(document.querySelectorAll('#s6 tbody tr')).filter(r => r.offsetParent !== null).length")
        check('"show all" reveals every correction', vis == tot, (vis, tot))
        pg.goto(BASE + '05-proprietary-models.html', wait_until='load'); pg.wait_for_timeout(200)
        rid = pg.evaluate("(() => { const rows = document.querySelectorAll('#t5-2 tbody tr'); const r = rows[rows.length - 3]; return r.id || null; })()")
        if rid:
            pg.goto(BASE + '05-proprietary-models.html#' + rid, wait_until='load'); pg.wait_for_timeout(400)
            check('deep link to a clipped row (#%s) expands the table' % rid, pg.evaluate("(id) => document.getElementById(id).offsetParent !== null", rid))

        # ---------------------------------------------------------- 5. technique matrix
        pg.goto(BASE + '06-technique-matrix.html', wait_until='load'); pg.wait_for_timeout(300)
        D = pg.evaluate('({rows: IA_MATRIX.rows.length, fams: IA_MATRIX.fams.map(f => f.id), groups: IA_MATRIX.groups.length})')
        counts = pg.evaluate("Array.from(document.querySelectorAll('#mx-fams .famb')).map(b => [b.dataset.f, parseInt(b.querySelector('.fc').textContent, 10)])")
        check('matrix shows 34 rows and the six support counts', D['rows'] == 34 and dict(counts) == {'nv': 33, 'amd': 24, 'trn': 12, 'inf': 8, 'tpu': 11, 'wse': 6}, counts)
        pg.click('#mx-fams .famb[data-f="wse"]')
        check('choosing a chip moves the highlight', pg.evaluate("document.querySelector('#mx-fams .famb[aria-pressed=\"true\"]').dataset.f") == 'wse')
        pg.check('#mx-gaps')
        shown = pg.evaluate("document.querySelectorAll('#mx-grid .mx-n').length")
        check('"only gaps" hides the rows Cerebras supports', shown == 34 - 6, shown)
        pg.uncheck('#mx-gaps')
        pg.click('#mx-groups button[data-g="0"]')
        g0 = pg.evaluate("IA_MATRIX.rows.filter(r => r.g === 0).length")
        check('group filter narrows the matrix', pg.evaluate("document.querySelectorAll('#mx-grid .mx-n').length") == g0, g0)
        pg.click('#mx-groups button[data-g="-1"]')
        pg.click('#mx-grid .mx-n >> nth=0'); pg.wait_for_timeout(100)
        d = pg.evaluate("(() => { const d = document.querySelector('#mx-grid .mx-d'); return d ? {items: d.querySelectorAll('.mx-di').length, src: d.querySelectorAll('.mx-src a').length} : null; })()")
        check('opening a row shows six cells of conditions and its sources', bool(d) and d['items'] == 6 and d['src'] >= 1, d)
        pg.click('.gaps .gap >> nth=0'); pg.wait_for_timeout(300)
        j = pg.evaluate("(() => { const b = document.querySelector('#mx-grid .mx-n[aria-expanded=\"true\"]'); if (!b) return null; const r = b.getBoundingClientRect(); return {name: b.textContent.trim(), top: r.top}; })()")
        check('a gap card opens its matrix row and scrolls to it', bool(j) and 0 <= j['top'] < 700, j)
        pg.goto(BASE + '06-technique-matrix.html#s1-2', wait_until='load'); pg.wait_for_timeout(200)
        check('the source tables of the matrix stay reachable as sub-tabs', visible_panels(pg, '#s1 .subtabs > .subpanel') == ['s1-2'])

        # ---------------------------------------------------------- 6. long-context widgets
        pg.goto(BASE + '07-long-context.html#s2', wait_until='load'); pg.wait_for_timeout(300)
        kv = pg.evaluate('IA_KV')
        k3 = [r for r in kv if r['model'] == 'Kimi K3' and r['prec'] == 'FP8'][0]
        one = pg.inner_text('#kc-one')
        want = 200000 * k3['b'] / 2 ** 30 + k3['state'] / 2 ** 30
        check('KV calculator default: Kimi K3 FP8 at 200,000 tokens', one == '%.2f GiB' % want, (one, want))
        fit = pg.inner_text('#kc-fit')
        check('KV calculator: sequences that fit the 42.23 GiB budget', fit == '%d 條' % math.floor(42.23 / want) if 42.23 / want >= 10 else fit == '%.1f 條' % (math.floor(42.23 / want * 10) / 10), fit)
        pg.click('#kc-pre button[data-n="1048576"]')
        one = pg.inner_text('#kc-one'); want = 1048576 * k3['b'] / 2 ** 30 + k3['state'] / 2 ** 30
        check('KV calculator at 1M', one == '%.2f GiB' % want, (one, want))
        idx = [i for i, r in enumerate(kv) if r['state'] == 0][0]
        pg.select_option('#kc-m', str(idx))
        one = pg.inner_text('#kc-one'); want = 1048576 * kv[idx]['b'] / 2 ** 30
        check('KV calculator after changing the model (%s)' % kv[idx]['model'], one == '%.2f GiB' % want and pg.inner_text('#kc-st') == '無', (one, want))
        pg.fill('#kc-s', '64'); pg.dispatch_event('#kc-s', 'change')
        tot = pg.inner_text('#kc-tot')
        w = want * 64
        check('KV calculator total for 64 sequences', tot == ('%.2f TiB' % (w / 1024) if w >= 1024 else '%.1f GiB' % w), (tot, w))
        b1 = pg.evaluate("Array.from(document.querySelectorAll('#kv-bars .brow .bar span')).map(s => s.textContent)")
        pg.click('#kv-toggle button[data-m="k"]')
        b2 = pg.evaluate("Array.from(document.querySelectorAll('#kv-bars .brow .bar span')).map(s => s.textContent)")
        check('KV bars switch between 1M and 200K', len(b1) == 11 and b1 != b2 and b2[0] == '%.2f GiB' % max(r['k200'] for r in kv), (b1[:2], b2[:2]))
        pg.goto(BASE + '07-long-context.html#s3', wait_until='load'); pg.wait_for_timeout(200)
        dots = pg.evaluate("document.querySelectorAll('#s3 .pt.dotp').length")
        check('TTFT chart draws 9 warm and 15 cold points', dots == 24, dots)

        # ---------------------------------------------------------- 6b. charts built from chapter tables
        pg.goto(BASE + '08-metrics.html', wait_until='load'); pg.wait_for_timeout(200)
        v = pg.evaluate("Array.from(document.querySelectorAll('#xhw [data-pane]')).filter(p => !p.hidden).map(p => p.getAttribute('data-pane'))")
        first = pg.evaluate("document.querySelector('#xhw [data-pane=k10] .brow').textContent")
        check('cross-hardware chart opens on the 10K view with Cerebras first', v == ['k10'] and 'Cerebras' in first and '1,764 t/s' in first, (v, first[:60]))
        pg.click('[data-switch=xhw] button[data-view=k100]')
        v = pg.evaluate("Array.from(document.querySelectorAll('#xhw [data-pane]')).filter(p => !p.hidden).map(p => p.getAttribute('data-pane'))")
        first = pg.evaluate("document.querySelector('#xhw [data-pane=k100] .brow').textContent")
        check('switching to the 100K view shows 1,225 t/s', v == ['k100'] and '1,225 t/s' in first and pg.get_attribute('[data-switch=xhw] button[data-view=k100]', 'aria-pressed') == 'true', (v, first[:60]))
        pg.goto(BASE + '04-open-models.html#s2', wait_until='load'); pg.wait_for_timeout(200)
        check('flagship chart: 8 models x 3 bars', pg.evaluate("document.querySelectorAll('#s2 .grow').length") == 8 and pg.evaluate("document.querySelectorAll('#s2 .grow .b1').length") == 24)
        pg.goto(BASE + '04-open-models.html#s3', wait_until='load'); pg.wait_for_timeout(200)
        cells = pg.evaluate("document.querySelectorAll('#shg [data-pane=hi] .hc').length")
        top = pg.evaluate("Array.from(document.querySelectorAll('#shg [data-pane=hi] .hc.top')).map(c => c.firstChild.textContent)")
        check('self-hosting grid: 6 models x 8 hardware columns, one best cell per model', cells == 48 and top == ['136', '230', '1,092', '3,108', '709', '1,266'], (cells, top))
        pg.click('[data-switch=shg] button[data-view=lo]')
        top = pg.evaluate("Array.from(document.querySelectorAll('#shg [data-pane=lo] .hc.top')).map(c => c.firstChild.textContent)")
        check('self-hosting grid: low-concurrency view', pg.evaluate("document.querySelector('#shg [data-pane=hi]').hidden") and top == ['259', '485', '312', '621', '292', '575'], top)
        pg.goto(BASE + '01-silicon.html', wait_until='load')
        check('chapter 1 chart lists 15 chips', pg.evaluate("document.querySelectorAll('.duo-r').length") == 15)
        pg.goto(BASE + '09-deployment.html#s3', wait_until='load')
        leaves = pg.evaluate("Array.from(document.querySelectorAll('ol.tree .leaf-id')).map(e => e.textContent)")
        check('decision tree marks its 12 leaves', leaves == ['L%d' % i for i in range(1, 13)], leaves)

        # ---------------------------------------------------------- 7. capacity planner against the reference model
        pg.goto(BASE + '10-capacity.html#calc', wait_until='load'); pg.wait_for_timeout(300)
        rpm = pg.inner_text('#pl-out .peak-top .hl')
        check('planner default shows 4,764 RPM', rpm == '4,764', rpm)
        js_all = pg.evaluate("""(() => {
          const M = IA_MODEL, out = {};
          for (const N of [1000, 10000, 100000]) for (const mix of M.ROLE_MIXES) for (const lv of ['low', 'base', 'high']) for (const tz of ['single', 'global']) {
            const R = M.compute({n: N, share: {OA: (100 - mix.se - mix.rd) / 100, SE: mix.se / 100, RD: mix.rd / 100}, level: {OA: lv, SE: lv, RD: lv}, custom: {}, s: tz === 'single' ? 0.11 : 0.065,
              peak: {d: 1.2, kFloor: 1.15, fu: 1.18, fc: 1.04, fo: 1.06, v: 80, util: 0.8, price: 0.72}, mix: M.MIXES[1]});
            out[[N, mix.id, lv, tz].join('|')] = R.pk.rpm;
          }
          return out;
        })()""")
        check('planner model is loaded in the page and computes 90 scenarios', len(js_all) == 90 and all(v > 0 for v in js_all.values()), len(js_all))
        # UI path: 10,000 people, preset D, high, global
        pg.click('#pl-np button[data-n="10000"]')
        pg.click('#pl-presets button[data-p="D"]')
        for r in ('OA', 'SE', 'RD'):
            pg.click('#pl-roles button[data-r="%s"][data-l="high"]' % r)
        pg.click('#pl-tz button[data-tz="global"]')
        ui = pg.evaluate('IA_PLANNER.result().pk.rpm')
        key = '10000|D|high|global'
        shown = pg.inner_text('#pl-out .peak-top .hl')
        check('planner UI path (10,000 people, preset D, high, global) matches the model', abs(ui - js_all[key]) < 1e-6 and shown == format(round(ui), ','), (ui, js_all[key], shown))
        # custom level
        pg.click('#pl-roles button[data-r="SE"][data-l="custom"]')
        pg.fill('#pl-roles input[data-cr="SE"][data-ci="1"]', '50'); pg.dispatch_event('#pl-roles input[data-cr="SE"][data-ci="1"]', 'change')
        st = pg.evaluate('IA_PLANNER.state()')
        check('custom level accepts a telemetry value', st['lv']['SE'] == 'custom' and st['custom']['SE'][1] == 50, st['custom'])
        # custom routing
        pg.click('#pl-mx button[data-mx="custom"]'); pg.wait_for_timeout(100)
        n_inputs = pg.evaluate("document.querySelectorAll('#pl-mix input[data-mr]').length")
        check('custom routing editor lists 3 roles x 6 models', n_inputs == 18, n_inputs)
        pg.fill('#pl-mix input[data-mr="OA"][data-mk="flash"]', '50'); pg.dispatch_event('#pl-mix input[data-mr="OA"][data-mk="flash"]', 'change')
        note = pg.evaluate("document.querySelector('#pl-mix tbody tr td:last-child').textContent")
        check('a routing row that does not sum to 100 is flagged and rescaled', '按比例調整' in note, note)
        # link round trip
        link = pg.evaluate("location.href.split('#')[0] + '#calc?' + (function(){ document.getElementById('pl-copy').click(); return location.hash.slice(6); })()")
        st_a = pg.evaluate('JSON.stringify([IA_PLANNER.state().n, IA_PLANNER.state().se, IA_PLANNER.state().rd, IA_PLANNER.state().lv, IA_PLANNER.state().tz, IA_PLANNER.state().mx, IA_PLANNER.state().custom, IA_PLANNER.result().pk.rpm, IA_PLANNER.result().gpuSum])')
        c3, pg3 = ctx_page()
        pg3.goto(link, wait_until='load'); pg3.wait_for_timeout(300)
        st_b = pg3.evaluate('JSON.stringify([IA_PLANNER.state().n, IA_PLANNER.state().se, IA_PLANNER.state().rd, IA_PLANNER.state().lv, IA_PLANNER.state().tz, IA_PLANNER.state().mx, IA_PLANNER.state().custom, IA_PLANNER.result().pk.rpm, IA_PLANNER.result().gpuSum])')
        check('a copied scenario link restores the same inputs and results', st_a == st_b and visible_panels(pg3, '.tabs > .panel') == ['calc'], (st_a[:160], st_b[:160]))
        c3.close()
        # reset, employee field, slider
        pg.evaluate("document.getElementById('pl-adv').open = true"); pg.click('#pl-reset')
        check('reset returns to the default scenario', pg.inner_text('#pl-out .peak-top .hl') == '4,764')
        pg.fill('#pl-n-num', '25,000'); pg.dispatch_event('#pl-n-num', 'change')
        check('typing an employee count with a thousands separator works', pg.evaluate('IA_PLANNER.state().n') == 25000)
        rpm0 = pg.evaluate('IA_PLANNER.result().pk.L')
        pg.click('#pl-advin input[data-adv="v"]'); pg.keyboard.press('Control+A'); pg.keyboard.type('120'); pg.keyboard.press('Tab')
        foc = pg.evaluate("document.activeElement && document.activeElement.dataset ? document.activeElement.dataset.adv : null")
        check('an advanced parameter commits on Tab, changes the result and focus moves to the next field',
              pg.evaluate('IA_PLANNER.state().adv.v') == 120 and pg.evaluate("document.getElementById('pl-adv').open") and foc == 'util' and pg.evaluate('IA_PLANNER.result().pk.L') < rpm0, (foc,))
        pg.click('#pl-mx button[data-mx="custom"]')
        pg.click('#pl-editor input[data-mr="OA"][data-mk="glm"]'); pg.keyboard.press('Control+A'); pg.keyboard.type('60'); pg.keyboard.press('Tab')
        foc = pg.evaluate("document.activeElement && document.activeElement.dataset ? [document.activeElement.dataset.mr, document.activeElement.dataset.mk] : null")
        check('routing editor keeps focus order while recalculating', foc == ['OA', 'dsv4'] and pg.evaluate('IA_PLANNER.state().cmixRaw.OA.glm') == 60, foc)
        pg.fill('#pl-editor input[data-mr="OA"][data-mk="flash"]', '999'); pg.keyboard.press('Enter')
        check('out-of-range routing input is clamped and written back', pg.input_value('#pl-editor input[data-mr="OA"][data-mk="flash"]') == '100')
        with pg.expect_download() as dl:
            pg.click('#pl-csv')
        path = dl.value.path()
        csv = open(path, encoding='utf-8-sig').read()
        check('CSV download holds the scenario', csv.startswith('item,value,unit') and 'peak RPM' in csv and 'employees,25000' in csv, csv[:120])
        # reference numbers of the chapter appear in the planner for the 100,000 base case
        pg.click('#pl-reset'); pg.wait_for_timeout(100)
        txt = pg.inner_text('#planner')
        for needle in ('4,764', '24.5M', '212M', '3.13M', '865', '20,444 PTU', '3,239 GSU', '1,514 GSU', '134', '172'):
            check('planner default text contains %s' % needle, needle in txt)

        # ---------------------------------------------------------- 8. search
        pg.goto(BASE + 'search.html?q=' + 'Capacity%20Blocks', wait_until='load'); pg.wait_for_timeout(500)
        n = pg.evaluate("document.querySelectorAll('#res a.hit').length")
        check('search for "Capacity Blocks" returns hits', n >= 10, n)
        href = pg.get_attribute('#res a.hit >> nth=3', 'href')
        pg.click('#res a.hit >> nth=3'); pg.wait_for_load_state('load'); pg.wait_for_timeout(500)
        anchor = href.split('#')[1]
        o = pg.evaluate("(id) => { const e = document.getElementById(id); if (!e) return null; const r = e.getBoundingClientRect(); return {vis: e.offsetParent !== null, top: r.top, text: e.textContent.slice(0, 60)}; }", anchor)
        check('a search hit lands on a visible block (%s)' % href, bool(o) and o['vis'] and -50 <= o['top'] < 900, o)
        pg.goto(BASE + 'search.html', wait_until='load')
        pg.fill('#q', '131,072 Trainium'); pg.wait_for_timeout(400)
        n2 = pg.evaluate("document.querySelectorAll('#res a.hit').length")
        check('search needs every term and accepts numbers with separators', n2 >= 3 and pg.evaluate("Array.from(document.querySelectorAll('#res a.hit')).every(a => /131,072/.test(a.textContent) && /trainium/i.test(a.textContent))"), n2)
        pg.select_option('#pg', index=7); pg.wait_for_timeout(200)
        chs = pg.evaluate("Array.from(new Set(Array.from(document.querySelectorAll('#res a.hit')).map(a => a.getAttribute('href').split('#')[0])))")
        check('search can be limited to one chapter', len(chs) <= 1, chs)
        pg.goto(BASE + 'index.html', wait_until='load')
        pg.fill('#hsearch input', 'MLA'); pg.press('#hsearch input', 'Enter'); pg.wait_for_load_state('load'); pg.wait_for_timeout(400)
        check('header search box goes to the search page with results', 'search.html?q=MLA' in pg.url and pg.evaluate("document.querySelectorAll('#res a.hit').length") > 5, pg.url)

        # ---------------------------------------------------------- 9. sources
        pg.goto(BASE + '12-sources.html', wait_until='load'); pg.wait_for_timeout(300)
        n_all = pg.evaluate('IA_SOURCES.length')
        check('sources page lists the first 150 of %d' % n_all, pg.evaluate("document.querySelectorAll('#src-list li').length") == 150 and n_all == 777)
        pg.select_option('#src-vs', 'unreadable')
        check('filter by verification method: 4 unreadable', pg.evaluate("document.querySelectorAll('#src-list li').length") == 4)
        pg.select_option('#src-vs', ''); pg.select_option('#src-ch', '06'); pg.fill('#src-q', 'vllm')
        k = pg.evaluate("document.querySelectorAll('#src-list li').length")
        want = pg.evaluate("IA_SOURCES.filter(s => s.c.indexOf('06') >= 0 && (s.n.join(' ') + ' ' + s.u).toLowerCase().indexOf('vllm') >= 0).length")
        check('filter sources by chapter and text', k == min(want, 150) and want > 0, (k, want))
        pg.fill('#src-q', ''); pg.select_option('#src-ch', ''); pg.click('#src-more')
        check('"show more" extends the list', pg.evaluate("document.querySelectorAll('#src-list li').length") == 450)

        # ---------------------------------------------------------- 10. theme
        pg.goto(BASE + 'index.html', wait_until='load')
        bg0 = pg.evaluate("getComputedStyle(document.body).backgroundColor")
        pg.click('#theme-btn')
        bg1 = pg.evaluate("getComputedStyle(document.body).backgroundColor")
        pg.goto(BASE + '03-architectures.html', wait_until='load')
        bg2 = pg.evaluate("getComputedStyle(document.body).backgroundColor")
        check('theme toggle switches to dark and persists across pages', bg0 == 'rgb(242, 244, 241)' and bg1 == 'rgb(16, 23, 20)' and bg2 == bg1, (bg0, bg1, bg2))
        pg.click('#theme-btn')
        check('theme toggle switches back', pg.evaluate("getComputedStyle(document.body).backgroundColor") == bg0)
        c.close()
        c4, pg4 = ctx_page(theme='dark')
        pg4.goto(BASE + 'index.html', wait_until='load')
        check('system dark preference is followed without a stored choice', pg4.evaluate("getComputedStyle(document.body).backgroundColor") == 'rgb(16, 23, 20)')
        c4.close()

        # ---------------------------------------------------------- 11. phone
        c5, pg5 = ctx_page(390, 800)
        for f in pages:
            pg5.goto(BASE + f, wait_until='load'); pg5.wait_for_timeout(120)
            over = pg5.evaluate('document.documentElement.scrollWidth - document.documentElement.clientWidth')
            check('phone: no horizontal page overflow on %s' % f, over <= 0, over)
        pg5.goto(BASE + '07-long-context.html', wait_until='load')
        nav0 = pg5.evaluate("document.getElementById('idx').offsetParent !== null")
        pg5.click('#menu-btn')
        nav1 = pg5.evaluate("document.getElementById('idx').offsetParent !== null")
        check('phone: chapter menu opens from the header button', (not nav0) and nav1 and pg5.get_attribute('#menu-btn', 'aria-expanded') == 'true')
        small = pg5.evaluate("""(() => Array.from(document.querySelectorAll('button, .idx a, input[type=search], select')).filter(e => e.offsetParent !== null).map(e => { const r = e.getBoundingClientRect(); return [e.className || e.tagName, Math.round(r.width), Math.round(r.height)]; }).filter(x => x[2] < 36))()""")
        check('phone: visible controls are at least 36 px tall', not small, small[:6])
        c5.close()

        # ---------------------------------------------------------- 12. print and no-script
        c6, pg6 = ctx_page()
        pg6.goto(BASE + '07-long-context.html', wait_until='load')
        pg6.emulate_media(media='print')
        hidden = pg6.evaluate("Array.from(document.querySelectorAll('.tabs > .panel, .subtabs > .subpanel')).filter(e => getComputedStyle(e).display === 'none').length")
        check('print layout shows every panel', hidden == 0, hidden)
        c6.close()
        c7 = b.new_context(java_script_enabled=False, viewport={'width': 1280, 'height': 900})
        pg7 = c7.new_page()
        pg7.goto(BASE + '04-open-models.html', wait_until='load')
        hidden = pg7.evaluate("Array.from(document.querySelectorAll('.tabs > .panel, .subtabs > .subpanel')).filter(e => getComputedStyle(e).display === 'none').length") if False else None
        shown = pg7.locator('.tabs > .panel').count()
        vis = sum(1 for i in range(shown) if pg7.locator('.tabs > .panel').nth(i).is_visible())
        check('without JavaScript every section of a chapter is readable', shown > 1 and vis == shown, (vis, shown))
        c7.close()
        b.close()

    srv.shutdown()
    errs = [e for e in errors if 'fonts.googleapis' not in e[1] and 'fonts.gstatic' not in e[1] and 'ERR_' not in e[1]]
    check('no console errors, page errors or failed local requests', not errs, errs[:5])
    bad = [r for r in results if not r[1]]
    print('\n%d checks, %d failed' % (len(results), len(bad)))
    for name, ok, detail in bad:
        print('  FAIL', name, '—', detail)
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()
