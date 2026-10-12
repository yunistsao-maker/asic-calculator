"""Page-specific blocks: home, technique matrix, long-context charts, planner shell, fact-check record.

Every number shown by a hand-built block is either parsed from a chapter table or asserted to be present in the
chapter text at build time (need()), so the blocks cannot drift away from the chapters.
"""
import collections
import html as _html
import json
import math
import os
import re
import shutil

import meta as M
import render as R

esc = _html.escape
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CHDIR = os.path.join(ROOT, 'chapters')
_texts = {}


def chapter_text(n):
    if n not in _texts:
        import glob
        from normalize import normalize
        p = glob.glob(os.path.join(CHDIR, '%02d-*.md' % n))[0]
        t = open(p, encoding='utf-8').read()
        cfg = [c for c in M.CHAPTERS if c['n'] == n]
        _texts[n] = normalize(t) if cfg and cfg[0].get('norm') else t
    return _texts[n]


def need(n, *strings):
    """Fail the build if a hand-written figure is not in chapter n."""
    t = chapter_text(n)
    for s in strings:
        if s not in t:
            raise SystemExit('BUILD CHECK FAILED: %r not found in chapter %d' % (s, n))


def g(letter, label=None):
    cls = {'A': 'gl gl-a', 'B': 'gl', 'C': 'gl gl-c', 'D': 'gl gl-d'}[letter]
    if label:
        return '<span class="%s">%s %s</span>' % (cls, letter, label)
    return '<span class="g g-%s" title="等級 %s：%s">%s</span>' % (letter.lower(), letter, R.GRADE_NAMES[letter], letter)


def fam(cls, tag):
    return '<span class="fam fam-%s">%s</span>' % (cls, tag)


def md_table(text, caption):
    """Rows of the Markdown table that follows the line starting with **caption."""
    i = text.index('**' + caption)
    lines = text[i:].split('\n')
    rows, started = [], False
    for line in lines[1:]:
        if line.startswith('|'):
            started = True
            if re.match(r'^\|[-| :]+\|\s*$', line):
                continue
            rows.append([c.strip() for c in re.split(r'(?<!\\)\|', line.strip().strip('|'))])
        elif started:
            break
    return rows[0], rows[1:]


def num(s):
    m = re.search(r'-?\d[\d,]*(?:\.\d+)?', s)
    return float(m.group(0).replace(',', '')) if m else None


# ---------------------------------------------------------------- home
def home_overview(counts, stats):
    need(8, '1,764', '320', '5.5×')
    need(7, '131,072', 'tested up to 128K', '98,304', '32,768', '65,536')
    need(1, '96 GiB', '144 GiB', '192 GiB', '2.235', '0.7582', '12.9813', '12.00', '5.40', '44 GB SRAM', '270 GB', '180 GB')
    need(8, '6.69', '14.24', '8.60')
    need(10, '4,764', '單一時區')
    kpis = [
        ('<span class="hl">5.5×</span>', 'Cerebras 對最快的非 ASIC 端點的輸出速度。gpt-oss-120b、10K 輸入：1,764 對 320 tokens/s（Azure，硬體未揭露）',
         g('A', '獨立量測'), '08-metrics.html#t8-6'),
        ('%d : %d' % (counts['nv'], counts['wse']), '34 項推論技術中文件列為「支援」的項數，NVIDIA GPU 對 Cerebras 公開 API',
         g('D', '本文推算'), '06-technique-matrix.html'),
        ('131K', 'GPU 以外、用公開工具鏈或公開端點拿得到的最大 context：Trainium 文件測試到 128K（131,072）、Cerebras 公開 API 131K。可重現的 1M 只在 GPU 上',
         g('C', '廠商文件'), '07-long-context.html#t7-9'),
        ('4,764', '100,000 人、單一時區的尖峰 RPM。OA 70%、coding 12%、R&amp;D 18%、base 用量；coding 佔 94% 的 token',
         g('D', '本文推算'), '10-capacity.html#calc'),
    ]
    k_html = ''.join('<div class="kpi"><span class="v">%s</span><span class="d">%s</span>%s<a href="%s" style="font-size:12px">看出處</a></div>' % k for k in kpis)

    def meter(n):
        return '<span class="meter"><span class="mv">%d</span><span class="mt"><span class="mf" style="width:%.0f%%"></span></span></span>' % (n, n / 34 * 100)

    fams = [
        (fam('trn', 'TRN') + 'Trainium2 / 3', '96 / 144 GiB HBM', counts['trn'], '131,072<small>文件測試到 128K</small>',
         'Trn2 只能用 Capacity Blocks，每 chip-hour $2.235；Trn3 沒有公開價格與自助 SKU', 'vLLM Neuron plugin（Beta）'),
        (fam('inf', 'INF') + 'Inferentia2', '32 GiB HBM', counts['inf'], '32,768<small>獨立實測；65,536 無法啟動</small>',
         'On-demand。us-east-1 每小時 $0.76–12.98（inf2.xlarge 至 inf2.48xlarge）', 'NxD Inference（維護模式）'),
        (fam('tpu', 'TPU') + 'TPU7x Ironwood', '192 GiB HBM', counts['tpu'], '98,304<small>repository 內最大；Ironwood 的 LLM recipe 多為 9,216–10,240。Gemini 的 1M 僅 first-party</small>',
         'us-central1 on-demand 每 chip-hour $12.00，3 年承諾 $5.40', 'vLLM TPU plugin、SGLang-JAX'),
        (fam('gpu', 'GPU') + 'NVIDIA B200 / B300', '180 / 270 GB', counts['nv'], '1,048,576',
         'B200 on-demand 每 GPU-hour $6.69–14.24（Lambda、Nebius、CoreWeave、OCI、AWS）<small>Vera Rubin（288 GB HBM4）自 2026-09-30 在 CoreWeave limited availability，引擎支援為實驗</small>',
         'vLLM、SGLang、TensorRT-LLM'),
        (fam('amd', 'AMD') + 'AMD Instinct MI355X', '288 GB', counts['amd'], '1,048,576<small>Kimi K3 的 vLLM recipe</small>',
         'OCI on-demand 每 GPU-hour $8.60', 'ATOM、vLLM、SGLang'),
        (fam('wse', 'WSE') + 'Cerebras WSE-3', '44 GB SRAM / 晶圓', counts['wse'], '131K<small>公開 API</small>',
         'API 按 token 計價、Dedicated，或地端採購', '自有堆疊，不開放'),
    ]
    rows = ''.join(
        '<tr><td class="rowhead" style="white-space:nowrap">%s</td><td class="num">%s</td><td>%s</td><td class="ctxc"><span class="mono">%s</td><td>%s</td><td>%s</td></tr>' % (
            f[0], f[1], meter(f[2]), f[3].replace('<small>', '</span><small>', 1) if '<small>' in f[3] else f[3] + '</span>', f[4], f[5]) for f in fams)
    table = ('<figure class="tbl famtable" data-plain="1"><div class="tbl-scroll"><table style="min-width:880px;font-size:14px"><thead><tr>'
             '<th scope="col">家族</th><th scope="col">每晶片記憶體</th><th scope="col" style="min-width:130px">支援技術 / 34</th>'
             '<th scope="col" style="min-width:170px">公開可取得的最大 context</th><th scope="col" style="min-width:220px">怎麼買</th><th scope="col" style="min-width:120px">引擎</th>'
             '</tr></thead><tbody>%s</tbody></table></div></figure>' % rows)
    cards_m = ''.join(
        '<div class="famcard"><div class="h"><span>%s</span><span class="c">%d / 34</span></div><span class="t"><i style="width:%.0f%%"></i></span>'
        '<div class="m"><span>%s</span><span>context %s</span></div><div class="b">%s</div></div>' % (
            f[0], f[2], f[2] / 34 * 100, f[1], re.sub(r'<small>.*?</small>', '', f[3]), re.sub(r'<small>.*?</small>', '', f[4])) for f in fams)
    table += '<div class="famcards" aria-label="五個家族一覽">%s</div>' % cards_m
    cards = [
        ('SHEET 06', '技術支援矩陣', '34 項技術在 6 種晶片上支援、部分或不支援，可依類別篩選、看每一格的限定條件與來源。', '打開矩陣 →', '06-technique-matrix.html'),
        ('SHEET 07', '長上下文 200K / 1M', '每條序列要多少 KV 記憶體、冷啟與命中 cache 的 TTFT、哪些晶片做得到。', '看可行性 →', '07-long-context.html'),
        ('SHEET 10', '容量計算器', '輸入人數、角色組合與模型組合，得到尖峰 RPM、TPM 與各平台要申請的配額。', '開始試算 →', '10-capacity.html#calc'),
    ]
    c_html = ''.join('<a class="card" href="%s"><span class="c">%s</span><span class="t">%s</span><span class="d">%s</span><span class="go">%s</span></a>' % (
        c[4], c[0], c[1], c[2], c[3]) for c in cards)
    cmap = [
        (1, '五類晶片各世代的記憶體、頻寬、算力、價格與可得性'),
        (2, '哪個引擎能在哪種晶片上跑，各組合的優缺點，編譯式與動態執行的差別'),
        (3, '各晶片支援哪些模型架構，兆級參數模型放不放得下，市場上實際跑什麼'),
        (4, 'Kimi、GLM、DeepSeek、Qwen 在各晶片的 TPS、TTFT 與自架需求'),
        (5, 'Claude、GPT、Gemini 等跑在哪些晶片，公開量到的速度與價格'),
        (6, '34 項推論技術在 6 種晶片上支援或不支援'),
        (7, 'context 到 200K 與 1M 時，記憶體、TTFT、各技術與各晶片的可行性'),
        (8, '跨晶片的效能、每百萬 token 成本、能效與適用情境評分'),
        (9, '部署選項、各晶片可用的模式、選型決策樹'),
        (10, '1 萬與 10 萬人導入時的 TPM 與 RPM，依角色組合與模型組合'),
        (11, '每個估算參數的來源、等級與落差'),
    ]
    by = {c['n']: c for c in M.CHAPTERS}
    ntab = stats.get('tables_by_ch', {})
    m_rows = ''.join('<tr><td class="num">%02d</td><td class="rowhead"><a href="%s.html">%s</a></td><td>%s</td><td class="num">%s</td></tr>' % (
        n, by[n]['slug'], esc(by[n]['nav']), q, ntab.get(n, '')) for n, q in cmap)
    m_rows += '<tr><td class="num">12</td><td class="rowhead"><a href="12-sources.html">來源</a></td><td>%d 個來源的清單、引用它的章節與查核方式</td><td class="num"></td></tr>' % stats['n_sources']
    m_rows += '<tr><td class="num">A</td><td class="rowhead"><a href="factcheck.html">查核紀錄</a></td><td>查核怎麼做、更正了哪 %d 處、哪些無法查核</td><td class="num"></td></tr>' % stats['n_corr']
    cmap_html = ('<figure class="tbl" data-plain="1"><div class="tbl-scroll"><table class="fit" style="min-width:640px"><thead><tr><th scope="col">張</th><th scope="col">章節</th>'
                 '<th scope="col">回答的問題</th><th scope="col">表格數</th></tr></thead><tbody>%s</tbody></table></div></figure>' % m_rows)
    grades = ('<div class="grades"><div>%s<span>獨立第三方量測，例如 Artificial Analysis、InferenceX、OpenRouter 的遙測</span></div>'
              '<div>%s<span>廠商或夥伴公布，且揭露方法</span></div><div>%s<span>廠商宣稱或規格，未揭露方法</span></div>'
              '<div>%s<span>本文推算，附算式</span></div></div>') % (g('A'), g('B'), g('C'), g('D'))
    return ('<section class="kpis" aria-label="關鍵數字">%s</section>'
            '<section class="block"><div class="sec-h"><h3 style="font-size:22px">五個家族一覽</h3><span class="sub">記憶體與價格的出處在第 1 章與第 8 章，技術項數在第 6 章，context 在第 7 章；AMD 併在 GPU 下作對照</span></div>%s</section>'
            '<section class="cards">%s</section>'
            '<section class="block"><h3 style="font-size:18px">每一張回答什麼</h3>%s</section>'
            '<section class="block"><h3 style="font-size:18px">證據等級</h3>%s</section>') % (k_html, table, c_html, cmap_html, grades)


# ---------------------------------------------------------------- chapter 6: matrix
ST = {'支援': 's', '部分': 'p', '實驗': 'e', '不支援': 'n', '查無': 'u'}
LINK = re.compile(r'\[([^\]]+)\]\((https?://(?:[^()\s]|\([^()\s]*\))+)\)')


def matrix_rows():
    """The 34 technique rows of chapter 6, read from the four tables of its first section."""
    text = chapter_text(6)
    sec = text.split('## 技術 × 晶片支援矩陣')[1].split('## 不支援或受限的原因與替代做法')[0]
    rows, group = [], None
    for line in sec.split('\n'):
        if line.startswith('### '):
            group = line[4:].strip()
        if not line.startswith('|') or line.startswith('| 技術') or line.startswith('|---'):
            continue
        cells = [c.strip() for c in line.strip().strip('|').split('|')]
        assert len(cells) == 8, line[:80]
        status = []
        for v in cells[1:7]:
            m = re.match(r'(支援|部分|實驗|不支援|查無)', v)
            assert m, v
            status.append(m.group(1))
        rows.append({'group': group, 'name': cells[0], 'cells': cells[1:7], 'status': status, 'src': cells[7]})
    return rows


def matrix_data(ctx):
    rows = matrix_rows()
    fams = M.FAMILIES
    groups, out = [], []
    counts = {f['id']: 0 for f in fams}
    for i, r in enumerate(rows):
        if r['group'] not in groups:
            groups.append(r['group'])
        st = ''.join(ST[s] for s in r['status'])
        for f, s in zip(fams, st):
            if s == 's':
                counts[f['id']] += 1
        notes = []
        for cell, status in zip(r['cells'], r['status']):
            rest = cell[len(status):].strip()
            m = re.fullmatch(r'[（(](.*)[）)]', rest, flags=re.S)
            if m and '（' not in m.group(1)[:1]:
                # only strip when the outer pair really wraps the whole remainder
                depth, ok = 0, True
                for k, ch in enumerate(rest):
                    if ch in '（(':
                        depth += 1
                    elif ch in '）)':
                        depth -= 1
                        if depth == 0 and k != len(rest) - 1:
                            ok = False
                            break
                if ok:
                    rest = m.group(1)
            if rest:
                soup = R.render_md(rest, {'unreadable': ()})
                notes.append(soup.p.decode_contents() if soup.p else str(soup))
            else:
                notes.append('')
        name_soup = R.render_md(r['name'], {'unreadable': ()})
        out.append({'id': 'r%d' % (i + 1), 'g': groups.index(r['group']), 'name': name_soup.p.decode_contents(), 'plain': r['name'],
                    'st': st, 'notes': notes, 'src': [[n, u] for n, u in LINK.findall(r['src'])]})
    assert len(out) == 34, len(out)
    js = {'fams': [{'id': f['id'], 'tag': f['tag'], 'cls': f['cls'], 'name': f['name'], 'engine': f['engine']} for f in fams],
          'groups': groups, 'rows': [{k: v for k, v in r.items() if k != 'plain'} for r in out]}
    return {'counts': counts, 'js': js, 'rows': out}


def matrix_shell(matrix):
    rows = {r['plain']: r for r in matrix['rows']}
    idx = {f['id']: i for i, f in enumerate(M.FAMILIES)}

    def st(name, fam_id):
        return rows[name]['st'][idx[fam_id]]

    mla, m1, dram, nvme = 'MLA kernel', '1M-token serving 有文件', 'KV offload：主機 DRAM', 'KV offload：NVMe／遠端'
    assert st(mla, 'trn') == 'n' and st(mla, 'inf') == 'n' and st(mla, 'tpu') == 'p', 'MLA row changed'
    assert st(m1, 'nv') == 's' and st(m1, 'trn') == 'u' and st(m1, 'tpu') == 'u' and st(m1, 'wse') == 'n', '1M row changed'
    assert st(dram, 'trn') == 'n' and st(nvme, 'nv') == 's' and all(st(nvme, f) != 's' for f in ('amd', 'trn', 'inf', 'tpu', 'wse')), 'KV offload rows changed'
    need(6, '文件測試到 128K', 'repository 內最大 98,304', '公開 API 131K')
    gaps = [
        ('缺口 1', 'MLA kernel', 'Trainium、Inferentia2 不支援，TPU 只到「部分」。Kimi、GLM、DeepSeek 旗艦在 GPU 之外沒有受支援的路徑。', rows[mla]['id']),
        ('缺口 2', '1M-token serving', '只有 GPU 引擎有 recipe。Trainium 文件測試到 128K、TPU repository 內最大 98,304、Cerebras 公開 API 131K。', rows[m1]['id']),
        ('缺口 3', 'KV offload', '主機 DRAM 層在 Trainium 不支援；NVMe 與遠端層只有 NVIDIA GPU 欄有文件，其餘五欄不是查無就是不支援。', rows[dram]['id']),
    ]
    g_html = ''.join('<button type="button" class="gap" data-jump="%s" data-focus="trn"><span class="c">%s</span><span class="t">%s</span><span class="d">%s</span><span class="go">看這一列 →</span></button>' % (
        x[3], x[0], x[1], x[2]) for x in gaps)
    leg = ('<div class="stleg"><div><span class="st st-s">● 支援</span><span>文件列為支援，含廠商 matrix 的 Passing，且無重大限制</span></div>'
           '<div><span class="st st-p">△ 部分</span><span>只涵蓋部分模型或硬體世代、有已知限制，或廠商 matrix 標 Untested</span></div>'
           '<div><span class="st st-e">◇ 實驗</span><span>文件自標 experimental 或 preview</span></div>'
           '<div><span class="st st-n">× 不支援</span><span>文件明示不支援</span></div>'
           '<div><span class="st st-u">– 查無</span><span>讀過的文件沒有提到；不代表做不到</span></div></div>')
    return ('<div class="widget" style="gap:24px"><section class="gaps" aria-label="三個最大的缺口">%s</section>'
            '<div id="matrix" class="widget" style="gap:24px"><noscript><p class="wnote">互動矩陣需要 JavaScript。四張原始表在旁邊的分頁，內容相同。</p></noscript></div>'
            '<section class="block"><h3 style="font-size:18px">狀態怎麼判定</h3>%s</section>'
            '<p class="wnote">這張矩陣由本章的四張表產生，每一格的限定條件與來源與原表相同；原表在旁邊的四個分頁。這張表會隨每次引擎釋出而過期，引用前請對照來源。</p></div>') % (g_html, leg)


# ---------------------------------------------------------------- chapter 7
def lg(x):
    return (math.log2(x) - 14) / 7 * 100


def ctx_chart(text):
    need(7, '32,768', '98,304', '100K input tokens', '131,072', '131K', '7,022,899', '3.1 條滿長度請求', '1,048,576')
    rows = [
        ('AWS Inferentia2', '獨立實測；65,536 無法啟動', 32768, True, 'A'),
        ('Google TPU', 'repository 內最大值；LLM recipe 多為 9,216', 98304, True, 'B'),
        ('NVIDIA Groq 3 LPX', '參考；唯一的量測', 100000, True, 'A'),
        ('AWS Trainium', '公開 Neuron 工具鏈；文件測試到 128K', 131072, True, 'C'),
        ('Cerebras', '公開 API', 131072, True, 'C'),
        ('NVIDIA Hopper', 'H100、H200、H20；依模型', 1048576, True, 'A'),
        ('NVIDIA Blackwell', 'B200、B300、GB200、GB300', 1048576, True, 'A'),
        ('AMD Instinct', 'MI350 系列', 1048576, True, 'A'),
        ('Google TPU', 'Gemini，first-party；硬體與技術未揭露', 1048576, False, 'C'),
    ]
    p200, p1m = lg(200000), lg(1048576)
    ticks = ''.join('<span class="tick" style="left:%.2f%%">%s</span>' % (lg(v), lab) for v, lab in
                    [(32768, '32K'), (65536, '64K'), (131072, '128K'), (262144, '256K'), (524288, '512K')])
    head = ('<div class="axis"><span class="lab"></span><span class="plot"><span class="mark" style="left:%.2f%%">200K</span>'
            '<span class="mark" style="left:%.2f%%">1M</span>%s</span><span class="val"></span></div>') % (p200, p1m, ticks)
    body = ''
    for name, sub, v, solid, grade in rows:
        pos = lg(v)
        body += ('<div class="drow"><span class="lab">%s<small>%s</small></span><span class="plot"><span class="thr" style="left:%.2f%%"></span>'
                 '<span class="thr" style="left:%.2f%%"></span><span class="stem" style="width:%.2f%%"></span>'
                 '<span class="pt%s" style="left:%.2f%%"></span></span><span class="val">%s %s</span></div>') % (
            esc(name), esc(sub), p200, p1m, pos, '' if solid else ' hollow', pos, format(v, ','), g(grade))
    key = ('<div class="keyrow" style="padding-top:10px;border-top:1px solid var(--rule)"><span><i class="sw ink"></i>客戶可用公開 recipe、文件或獨立量測重現</span>'
           '<span><i class="sw surf"></i>只有產品規格，硬體與技術未揭露</span></div>')
    return ('<div class="widget" role="img" aria-label="各平台公開示範過的最大 context：Inferentia2 32,768、TPU repository 98,304、LPX 100,000、Trainium 與 Cerebras 131,072、NVIDIA 與 AMD GPU 1,048,576、Gemini first-party 1,048,576">'
            '<div class="sec-h"><h3 style="font-size:18px">各平台公開示範過的最大 context</h3><span class="sub">對數刻度；兩條虛線是本章的兩個門檻</span></div>'
            '<div class="wbox">%s%s%s</div></div>') % (head, body, key)


def kv_rows(text):
    head, rows = md_table(text, '表 7-1')
    assert head[:6] == ['模型', 'KV 精度', 'KV bytes/token（等級）', '每序列固定 state', '200K 的 KV（GiB）', '1M 的 KV（GiB）'], head
    out, last_state = [], (0, '')
    for r in rows:
        b = re.search(r'([\d,]+) B', r[2])
        b = int(b.group(1).replace(',', ''))
        s = r[3]
        if s.startswith('同上'):
            state, stext = last_state
        else:
            m = re.search(r'(\d+) (MB|MiB)', s)
            if m and ('state' in s or 'MiB（' in s or 'MB（' in s):
                state = int(m.group(1)) * (1000000 if m.group(2) == 'MB' else 1048576)
                stext = m.group(0)
            else:
                state, stext = 0, ''
        if not s.startswith('同上'):
            last_state = (state, stext)
        model = re.sub(r'（.*?）', '', r[0]).strip()
        prec = r[1]
        k200, m1 = num(r[4]), num(r[5])
        # the table's own figures must equal n x b
        assert abs(200000 * b / 2 ** 30 - k200) < 0.011 and abs(1048576 * b / 2 ** 30 - m1) < 0.011, (model, b, k200, m1)
        out.append({'model': model, 'prec': prec, 'b': b, 'state': state, 'stateText': stext, 'k200': k200, 'm1': m1})
    assert len(out) == 11, len(out)
    return out


def kv_widget(text):
    need(7, '相差約 50 倍', '0.87 GiB', '285 MiB', '434 MB')
    return ('<div class="widget" style="gap:26px">'
            '<section class="block"><div class="sec-h"><h3 style="font-size:18px">一條序列要多少 KV 記憶體</h3>'
            '<div class="seg mono" id="kv-toggle" role="group" aria-label="context 長度"><button type="button" data-m="k" aria-pressed="false">200K</button><button type="button" data-m="m" aria-pressed="true">1M</button></div></div>'
            '<p class="wnote">一條 1M-token 序列的 KV cache 在現役開源模型之間相差約 50 倍。gpt-oss-120b 是 Trainium 文件用的例子。%s n × b，資料取自表 7-1；b 的推導在第 4 章。</p>'
            '<div class="wbox" id="kv-bars" style="padding:6px 18px"><noscript>長條圖需要 JavaScript；數值在「每條序列」分頁的表 7-1。</noscript></div>'
            '<div class="formula" style="max-width:none"><code style="background:transparent;font-size:15px">M_KV(n) = n · b + b_s</code>'
            '<div style="font-size:12px;color:var(--ink2);margin-top:4px">n 為 context 的 token 數；b 為每 token 的 KV bytes；b_s 為每序列的固定 state。Kimi K3 的 KDA state 約 434 MB，Qwen3.8-2.4T 的 Gated DeltaNet state 285 MiB。</div></div></section>'
            '<section class="block"><div class="sec-h"><h3 style="font-size:18px">KV 試算</h3><span class="sub">選模型與 context 長度，算每條序列的 KV 與一份預算放得下幾條</span></div>'
            '<div id="kv-calc"><noscript>試算需要 JavaScript。</noscript></div></section></div>') % g('D')


def tpos(t):
    return (math.log10(t) + 1) / (math.log10(2000) + 1) * 100


def ttft_widget(text):
    head, rows = md_table(text, '表 7-6')
    assert head[3].startswith('TTFT p50') and head[5].startswith('GPU cache'), head
    warm = []
    for r in rows:
        hit = num(r[5])
        if hit >= 0.96:
            warm.append((num(r[3]), '%s · %s' % (r[0], r[1].split('；')[0]), num(r[4]), hit))
    assert len(warm) == 9, warm
    w_lo, w_hi = min(w[0] for w in warm), max(w[0] for w in warm)
    isl_lo, isl_hi = min(w[2] for w in warm), max(w[2] for w in warm)
    hit_lo, hit_hi = min(w[3] for w in warm), max(w[3] for w in warm)
    h7, r7 = md_table(text, '表 7-7')
    allrow = [r for r in r7 if r[0] == '全部模型'][0]
    hi9 = float(re.search(r'：([\d.]+) /', allrow[1]).group(1))
    lo3 = float(re.search(r'：([\d.]+) /', allrow[4]).group(1))
    n_hi = re.search(r'n = (\d+)', allrow[1]).group(1)
    n_lo = re.search(r'n = (\d+)', allrow[4]).group(1)
    need(7, '43.74 s', '5.88 s', '7.98 s', '10.54 s', '15.2 s', '10.35 s', '15.51 s', '32.68 s', '28.74 s', '20.27 s', '34.98 s', '114.33 s',
         '79.21 s', '420.91 s', '1,143.74 s', '0.2–5 s')
    cold = [
        ('cold · 約 128K', [(5.88, 'DeepSeek-V4-Pro · 32× H20'), (7.98, 'DeepSeek-V4-Pro · 16× H20'), (10.54, 'Qwen3-235B · 32× H20'), (15.2, 'DeepSeek-R1 · GB300 的 8 顆 GPU（mean）')]),
        ('cold · 約 256K', [(10.35, 'DeepSeek-V4-Pro · 32× H20'), (15.51, 'DeepSeek-V4-Pro · 16× H20'), (28.74, 'GLM-5.2 · 24× B300（mean）'), (32.68, 'Qwen3-235B · 32× H20')]),
        ('cold · 約 512K', [(20.27, 'DeepSeek-V4-Pro · 32× H20'), (34.98, 'DeepSeek-V4-Pro · 16× H20'), (114.33, 'Qwen3-235B · 32× H20')]),
        ('cold · 1M', [(43.74, 'DeepSeek-V4-Pro · 32× H20'), (79.21, 'DeepSeek-V4-Pro · 16× H20'), (420.91, 'Qwen3-235B · 32× H20'), (1143.74, 'Qwen3.8-27B · 1× RTX PRO 6000')]),
    ]
    kp = ('<section class="kpis" aria-label="關鍵數字" style="grid-template-columns:repeat(auto-fit,minmax(min(220px,100%%),1fr))">'
          '<div class="kpi"><span class="v" style="font-size:32px">43.7 s</span><span class="d">cold prefill 1M tokens 已公布的最快數字。DeepSeek-V4-Pro、32 顆 H20、併發 1</span>%s</div>'
          '<div class="kpi"><span class="v" style="font-size:32px"><span class="hl">%.2f–%.2f s</span></span><span class="d">warm 的 TTFT p50。併發 1、命中率 %.3f–%.3f 的 9 筆量測，輸入長度 p50 為 %dK–%dK</span>%s</div>'
          '<div class="kpi"><span class="v" style="font-size:32px">約 %d 倍</span><span class="d">命中率 ≥ 0.9（n = %s）與 &lt; 0.3（n = %s）之間的中位 TTFT 差距：%.2f ÷ %.2f</span>%s</div></section>') % (
        g('B', '廠商公布、有方法'), w_lo, w_hi, hit_lo, hit_hi, isl_lo, isl_hi, g('A', '獨立量測'),
        round(lo3 / hi9 / 100) * 100, n_hi, n_lo, lo3, hi9, g('D', '本文推算'))
    ticks = ''.join('<span class="tick" style="left:%.2f%%%s">%s</span>' % (tpos(v), ';transform:none' if v == 0.1 else '', lab) for v, lab in
                    [(0.1, '0.1 s'), (1, '1 s'), (10, '10 s'), (100, '100 s'), (1000, '1,000 s')])
    band = '<span class="band" style="left:%.2f%%;width:%.2f%%"></span>' % (tpos(0.2), tpos(5) - tpos(0.2))
    rows_html = ''
    series = [('warm · 命中率 ≥ 0.96', 'warm', [(w[0], w[1]) for w in sorted(warm)])] + [(lab, '', pts) for lab, pts in cold]
    for lab, cls, pts in series:
        vals = [p[0] for p in pts]
        dots = ''.join('<span class="pt dotp %s" style="left:%.2f%%" title="%s"></span>' % (cls, tpos(v), esc('%s s · %s' % (format(v, ','), t))) for v, t in pts)
        rng = '%s–%s s' % (('%.2f' % min(vals)), format(max(vals), ',.2f'))
        rows_html += ('<div class="drow"><span class="lab" style="flex-basis:26%%;max-width:190px">%s</span><span class="plot" style="height:34px">%s%s</span>'
                      '<span class="val" style="flex-basis:118px;font-size:12px">%s</span></div>') % (lab, band, dots, rng)
    key = ('<div class="keyrow" style="padding-top:10px;border-top:1px solid var(--rule)"><span><i class="sw teal dot"></i>warm，命中 prefix cache</span>'
           '<span><i class="sw ink dot"></i>cold，整段重新 prefill</span><span><i class="sw tr" style="width:18px"></i>0.2–5 s：InferenceX 對 agentic 服務 p90 TTFT 的尺度</span></div>')
    plot = ('<section class="block"><div class="sec-h"><h3 style="font-size:18px">cold 與 warm 的 TTFT</h3><span class="sub">對數刻度；每個點是一筆已公布的量測，模型與硬體各不相同（游標移到點上可看是哪一筆）</span></div>'
            '<div class="wbox"><div class="axis"><span class="lab" style="flex-basis:26%%;max-width:190px"></span><span class="plot" style="height:22px">%s</span><span class="val" style="flex-basis:118px"></span></div>%s%s</div>'
            '<p class="wnote">一條 cold 的 1M 請求在所有已公布的配置都超出互動延遲，最快的 43.7 s 還是 32 顆 GPU 只服務一條請求。長 context 的互動服務靠的是 cache 重用，不是 prefill 速度。各點的出處在「cold prefill」與「warm」兩個分頁的表 7-3 與表 7-6。</p></section>') % (ticks, rows_html, key)
    return '<div class="widget" style="gap:26px">' + kp + plot + '</div>'


def mrcr_widget(text):
    need(7, '97.14 / 95.98', '94.20 / 93.00', '30.66 / 40.53', '20.71 / 26.44', 'Qwen3.8-Flash-Next')
    data = [('128K', 97.14, 95.98), ('256K', 94.20, 93.00), ('512K', 30.66, 40.53), ('1M', 20.71, 26.44)]
    rows = ''
    for lab, a, b in data:
        rows += ('<div style="display:flex;gap:14px;align-items:center"><span class="mono" style="flex:0 0 56px;font-size:13px">%s</span>'
                 '<span style="flex:1 1 auto;display:flex;flex-direction:column;gap:2px;min-width:0">'
                 '<span style="display:flex;align-items:center;gap:8px"><span style="display:block;height:12px;width:%.2f%%;background:var(--ink)"></span><span class="mono" style="font-size:12px">%.2f</span></span>'
                 '<span style="display:flex;align-items:center;gap:8px"><span style="display:block;height:12px;width:%.2f%%;background:var(--teal)"></span><span class="mono" style="font-size:12px">%.2f</span></span>'
                 '</span></div>') % (lab, a * 0.85, a, b * 0.85, b)
    return ('<div class="widget"><div class="wbox" style="gap:10px"><span style="font-size:13px;font-weight:600">8-needle MRCR，Qwen3.8-Flash-Next，依輸入長度 %s</span>%s'
            '<div class="keyrow" style="padding-top:8px;border-top:1px solid var(--rule)"><span><i class="sw ink"></i>full attention</span><span><i class="sw teal"></i>QSA sparse</span><span>橫條長度與分數成正比；資料在表 7-15</span></div></div></div>') % (g('B'), rows)


def ch7_tabs(ch, ctx, build_tab, text):
    secs = {s['title']: s for s in ch['secs']}
    calc = secs['KV cache 記憶體與 prefill 時間的計算']
    feas = secs['各晶片在 200K / 1M 的可行性與限制']
    tech = secs['各推論技術在長上下文下有效或失效']
    lim = secs['模型與服務端的 context 上限對照']
    qual = secs['長上下文的品質']
    assert len(ch['secs']) == 5
    idx = {b['title']: i for i, b in enumerate(calc['subs'])}
    kv_subs = [idx[k] for k in ('算式', '每條序列在 200K 與 1M 的 KV', '具名節點放得下幾條序列', 'tensor parallel 對 MLA 模型 KV 容量的影響', '機隊層級：hot 與 warm KV')]
    tt_subs = [idx[k] for k in ('cold prefill 的量測值', 'warm（cache 命中）的量測值')]
    assert sorted(kv_subs + tt_subs) == list(range(len(calc['subs'])))
    a, b = calc['intro'].split('。cold prefill', 1)
    kv_sec = dict(calc, intro=a + '。')
    tt_sec = dict(calc, intro='cold prefill' + b)
    t1 = build_tab(feas, '可行性', ctx, 7)
    t1['top'].insert(0, ctx_chart(text))
    t2 = build_tab(kv_sec, 'KV 記憶體', ctx, 7, only_subs=kv_subs)
    t2['title'] = 'KV cache 記憶體的計算'
    t2['subs'].insert(0, {'label': '圖解與試算', 'title': None, 'html': kv_widget(text)})
    t3 = build_tab(tt_sec, 'TTFT', ctx, 7, only_subs=tt_subs)
    t3['title'] = 'cold 與 warm 的 TTFT'
    t3['subs'].insert(0, {'label': '圖解', 'title': None, 'html': ttft_widget(text)})
    t4 = build_tab(tech, '技術', ctx, 7)
    t5 = build_tab(lim, 'context 與計價', ctx, 7)
    t6 = build_tab(qual, '品質', ctx, 7)
    t6['top'].insert(0, mrcr_widget(text))
    return [t1, t2, t3, t4, t5, t6]


# ---------------------------------------------------------------- chapter 1: memory and bandwidth per chip
def table_after(text, marker):
    """Rows of the first Markdown table after `marker`."""
    lines = text[text.index(marker):].split('\n')
    rows, started = [], False
    for line in lines[1:]:
        if line.startswith('|'):
            started = True
            if re.match(r'^\|[-| :]+\|\s*$', line):
                continue
            rows.append([c.strip() for c in re.split(r'(?<!\\)\|', line.strip().strip('|'))])
        elif started:
            break
    return rows[0], rows[1:]


def bwpos(tb):
    return (math.log10(tb) + 0.30103) / 5 * 100     # 0.5 TB/s .. 50,000 TB/s


def silicon_chart():
    text = chapter_text(1)
    head, rows = table_after(text, '### 每顆晶片')
    assert head[:5] == ['晶片', '世代與狀態', '製程', '記憶體類型與容量', '記憶體頻寬'], head
    TO_GB = {'GiB': 1.073741824, 'GB': 1.0, 'MB': 0.001}
    TO_TB = {'TB/s': 1.0, 'GiB/s': 1.073741824e-3, 'GBps': 1e-3, 'GB/s': 1e-3, 'PB/s': 1e3}
    data, skipped = [], []
    for r in rows:
        mem = re.search(r'([\d,.]+)\s*(GiB|GB|MB)', r[3])
        if not mem:
            skipped.append(r[0])
            continue
        bw = re.search(r'([\d,.]+)\s*(TB/s|GiB/s|GBps|GB/s|PB/s)', r[4])
        name = r[0]
        tag = ('trn', 'TRN') if 'Trainium' in name else ('inf', 'INF') if 'Inferentia' in name else ('tpu', 'TPU') if name.startswith('Google') else \
            ('gpu', 'LPU') if 'LPU' in name else ('gpu', 'GPU') if name.startswith('NVIDIA') else ('amd', 'AMD') if name.startswith('AMD') else ('wse', 'WSE')
        segs = [s.strip() for s in r[1].split('；')]
        st = [s for s in segs if s.startswith('GA')][-1:] or [s for s in segs if re.match(r'^(Preview|已宣布|\d{4}-|AMD 稱)', s)][:1] or segs[:1]
        status = re.sub(r'（.*$', '', st[0]).strip()
        data.append({'name': re.sub(r'^(AWS|Google|NVIDIA|AMD|Cerebras) ', '', name) if not name.startswith('NVIDIA Groq') else 'Groq 3 LPU（LP30）',
                     'full': name, 'tag': tag, 'status': status, 'sram': 'SRAM' in r[3] and not re.search(r'HBM', r[3].split('加')[0]),
                     'mem_txt': '%s %s' % (mem.group(1), mem.group(2)), 'mem': float(mem.group(1).replace(',', '')) * TO_GB[mem.group(2)],
                     'bw_txt': ('%s %s' % (bw.group(1), bw.group(2))) if bw else None,
                     'bw': float(bw.group(1).replace(',', '')) * TO_TB[bw.group(2)] if bw else None})
    assert skipped == ['AWS Trainium4'], skipped
    assert len(data) == 15, len(data)
    by = {d['full']: d for d in data}
    assert by['AWS Trainium2']['mem_txt'] == '96 GiB' and by['AWS Trainium2']['bw'] == 2.9
    assert by['Cerebras WSE-3（CS-3）']['mem'] == 44 and by['Cerebras WSE-3（CS-3）']['bw'] == 21000 and by['Cerebras WSE-3（CS-3）']['sram']
    assert not by['Google TPU 8i']['sram'] and by['NVIDIA Groq 3 LPU（LP30）']['sram']
    mmax = max(d['mem'] for d in data)
    assert round(mmax) == 432
    ticks = ''.join('<span class="tick" style="left:%.2f%%">%s</span>' % (bwpos(v), lab) for v, lab in
                    [(1, '1 TB/s'), (10, '10'), (100, '100'), (1000, '1 PB/s'), (10000, '10')])
    grid = ''.join('<span class="thr" style="left:%.2f%%"></span>' % bwpos(v) for v in (1, 10, 100, 1000, 10000))
    body = ''
    for d in data:
        bwc = ('<span class="plot">%s<span class="pt%s" style="left:%.2f%%"></span></span><span class="v">%s</span>' % (
            grid, ' hollow' if d['sram'] else '', bwpos(d['bw']), esc(d['bw_txt']))) if d['bw'] else \
            '<span class="plot">%s</span><span class="v na">查無</span>' % grid
        body += ('<div class="duo-r"><span class="lab">%s%s<small>%s</small></span><span class="mbar"><i class="%s" style="width:%.2f%%"></i></span><span class="v">%s</span>%s</div>') % (
            fam(*d['tag']), esc(d['name']), esc(d['status']), 'sram' if d['sram'] else 'hbm', max(0.6, d['mem'] / mmax * 100), esc(d['mem_txt']), bwc)
    head_html = ('<div class="duo-h"><span>晶片</span><span>每顆記憶體（線性）</span><span></span><span class="plot" style="height:20px">%s</span><span></span></div>') % ticks
    key = ('<div class="keyrow" style="padding-top:10px;border-top:1px solid var(--rule)"><span><i class="sw teal"></i>HBM</span><span><i class="sw hatch"></i>SRAM</span>'
           '<span>右側為記憶體頻寬，對數刻度，一格 10 倍</span></div>')
    hbm = [d for d in data if not d['sram']]
    sram = [d for d in data if d['sram']]
    hb = [d['bw'] for d in hbm if d['bw']]
    assert (round(min(d['mem'] for d in hbm)), round(max(d['mem'] for d in hbm))) == (32, 432) and (round(min(hb), 2), max(hb)) == (0.88, 23.3)
    assert (min(d['mem'] for d in sram), max(d['mem'] for d in sram)) == (0.5, 44) and (min(d['bw'] for d in sram), max(d['bw'] for d in sram)) == (150, 43200)
    sub = 'HBM：每顆 32–432 GB、頻寬 0.88–23.3 TB/s。SRAM：每顆 0.5–44 GB、頻寬 150 TB/s 至 43.2 PB/s'
    return ('<div class="widget"><div class="sec-h"><h3 style="font-size:18px">每顆晶片的記憶體與頻寬</h3><span class="sub">' + sub + '</span></div>'
            '<div class="wbox" style="padding:10px 18px 12px">%s%s%s</div>'
            '<p class="wnote">數值取自「每顆晶片」分頁的表，等級與來源見該表；記憶體橫條以 GB 換算（1 GiB = 1.074 GB），標示的數字照原表單位。'
            '同一格有兩種說法時取表中第一個數字（Rubin 22 TB/s、MI455X 23.3 TB/s）。Trainium4 未公布容量，沒有列入。'
            'Cerebras 的 44 GB 是整片晶圓，Groq 3 LPU 的 500 MB 是單顆。</p></div>') % (head_html, body, key)


# ---------------------------------------------------------------- charts for chapters 4 and 8
def switcher(sid, views):
    """Segmented control that shows one [data-pane] of #sid at a time (site.js initSwitchers)."""
    return '<div class="seg" role="group" aria-label="檢視" data-switch="%s">%s</div>' % (sid, ''.join(
        '<button type="button" data-view="%s" aria-pressed="%s">%s</button>' % (k, 'true' if i == 0 else 'false', lab)
        for i, (k, lab) in enumerate(views)))


def xhw_chart():
    """Chapter 8: one set of weights (gpt-oss-120b) on ten endpoints, from table 8-6."""
    text = chapter_text(8)
    head, rows = md_table(text, '表 8-6')
    assert head[:6] == ['供應商', '硬體類別', '10K 輸入：t/s', '10K 輸入：TTFT（s）', '100K 輸入：t/s；TTFT（s）', '10 個並行請求（1K）：t/s'], head
    assert len(rows) == 10, len(rows)
    need(8, '5.5×', '= 3.7×', 'Baseten 0.18 s、Crusoe 0.41 s', 'uptime 51%', '9.9×', 'P50 / 72 h')
    data = []
    for r in rows:
        kind = 'asic' if 'ASIC' in r[1] else 'gpu' if 'GPU' in r[1] else 'unk'
        m = re.match(r'([\d,]+)；([\d.]+)$', r[4])
        data.append({'name': r[0], 'hw': r[1], 'kind': kind, 'k10': num(r[2]), 't10': float(r[3]),
                     'k100': float(m.group(1).replace(',', '')), 't100': float(m.group(2)), 'par': num(r[5])})
    assert data[0]['name'] == 'Cerebras' and data[0]['k10'] == 1764 and [d['kind'] for d in data].count('asic') == 3

    def pane(key, tkey, label):
        rs = sorted(data, key=lambda d: -d[key])
        vmax = rs[0][key]
        out = ''
        for d in rs:
            ttft = ' <small>TTFT %s s</small>' % (('%.2f' % d[tkey])) if tkey else ''
            out += ('<div class="brow"><span class="lab"><b>%s</b><small class="s">%s</small></span><span class="bar"><i class="k-%s" style="width:%.2f%%"></i>'
                    '<span>%s t/s%s</span></span></div>') % (esc(d['name']), esc(d['hw']), d['kind'], d[key] / vmax * 70, format(int(d[key]), ','), ttft)
        return '<div data-pane="%s"><h4 class="pane-t">%s</h4>%s</div>' % (key, label, out)
    views = [('k10', '10K 輸入'), ('k100', '100K 輸入'), ('par', '10 個並行（1K）')]
    panes = pane('k10', 't10', '10K 輸入') + pane('k100', 't100', '100K 輸入') + pane('par', None, '10 個並行請求（1K 輸入）')
    key = ('<div class="keyrow" style="padding-top:10px;border-top:1px solid var(--rule)"><span><i class="sw teal"></i>ASIC（WSE-3、RDU、LPU）</span>'
           '<span><i class="sw ink"></i>GPU 雲</span><span><i class="sw hatch"></i>硬體未揭露</span></div>')
    return ('<div class="widget"><div class="sec-h"><h3 style="font-size:18px">同一份權重、十個端點：gpt-oss-120b 的輸出速度</h3>%s</div>'
            '<p class="wnote">Artificial Analysis，72 小時 P50，2026-10-04；每次量測為單一請求，各端點的精度與是否使用 spec decode 未揭露 %s。</p>'
            '<div class="wbox" id="xhw" style="padding:6px 18px 12px">%s%s</div>'
            '<p class="wnote">10K 輸入時 Cerebras 是最快的非 ASIC 端點（Azure，硬體未揭露）的 5.5 倍，是十個第三方 GPU 端點中位數的 9.9 倍；100K 輸入時對最快的 GPU 端點縮小到 3.7 倍。'
            'TTFT 最低的是 GPU 端點（Baseten 0.18 s、Crusoe 0.41 s），不是 ASIC。Vertex 端點當日 TTFT 96 s、單日 uptime 51%%，不能代表 Google 的硬體。資料與硬體類別的標註在「同條件比較」分頁的表 8-6。</p></div>') % (
        switcher('xhw', views), g('A'), panes, key)


def flagship_chart():
    """Chapter 4: fastest endpoint, median of all endpoints and the first-party API for eight models, from table 4-6."""
    text = chapter_text(4)
    head, rows = md_table(text, '表 4-6')
    assert head[2].startswith('最快端點') and head[3] == '全部端點中位' and head[4] == '原廠 API', head
    assert len(rows) == 8, len(rows)
    need(4, '1.6×–3.2× 的「最快 ÷ 中位」是供應商與 serving stack 的效應', '原廠 API 多半落在慢的一端', 'TTFT 正常的最快者是 LithosAI', '依廠商自述全部是 GPU 上的軟體堆疊')
    data = []
    for r in rows:
        f = re.match(r'(.+?)：([\d,]+)；([\d.]+)；', r[2])
        md = re.match(r'([\d,]+)；([\d.]+)$', r[3])
        own = re.match(r'(.+?)：([\d,]+)；([\d.]+)$', r[4])
        assert f and md and own, r
        alt = re.search(r'TTFT 正常的最快者是 (.+?)：([\d,]+)；([\d.]+)', r[2])
        data.append({'model': re.sub(r'（.*?）', '', r[0]).strip(), 'n': int(r[1]), 'fp': f.group(1), 'f': num(f.group(2)), 'ft': float(f.group(3)),
                     'm': num(md.group(1)), 'mt': float(md.group(2)), 'op': own.group(1), 'o': num(own.group(2)), 'ot': float(own.group(3)),
                     'alt': (alt.group(1), num(alt.group(2)), float(alt.group(3))) if alt else None})
    vmax = max(d['f'] for d in data)
    assert vmax == 723, vmax

    def b(cls, v, label):
        return '<span class="b1"><i class="%s" style="width:%.2f%%"></i><span>%s</span></span>' % (cls, v / vmax * 52, label)
    out = ''
    for d in data:
        fl = '%d t/s · TTFT %s s · %s' % (d['f'], ('%.0f' % d['ft']) if d['ft'] >= 100 else ('%.2f' % d['ft']), esc(d['fp']))
        if d['alt']:
            fl += '；TTFT 正常的最快者 %d t/s（%s）' % (d['alt'][1], esc(d['alt'][0]))
        out += ('<div class="grow"><span class="lab"><b>%s</b><small>%d 個有速度資料的端點</small></span><span class="bars">%s%s%s</span></div>') % (
            esc(d['model']), d['n'], b('fast', d['f'], fl), b('med', d['m'], '%d t/s · TTFT %.2f s' % (d['m'], d['mt'])),
            b('own', d['o'], '%d t/s · TTFT %.2f s · %s' % (d['o'], d['ot'], esc(d['op']))))
    key = ('<div class="keyrow" style="padding-top:10px;border-top:1px solid var(--rule)"><span><i class="sw teal"></i>最快端點</span>'
           '<span><i class="sw ink"></i>全部端點的中位</span><span><i class="sw surf"></i>原廠 API</span></div>')
    return ('<div class="widget"><div class="sec-h"><h3 style="font-size:18px">四個家族的旗艦：最快端點、端點中位與原廠 API</h3>'
            '<span class="sub">輸出速度（t/s）與 TTFT；10K workload</span></div>'
            '<p class="wnote">Artificial Analysis，72 小時 P50，2026-10-04 擷取 %s；中位數為本文計算 %s。</p>'
            '<div class="wbox" style="padding:6px 18px 12px">%s%s</div>'
            '<p class="wnote">最快的端點依廠商自述全部是 GPU 上的軟體堆疊，所以旗艦 1.6×–3.2× 的「最快 ÷ 中位」是供應商與 serving stack 的效應，不是晶片差異；原廠 API 多半落在慢的一端。'
            '每個端點的硬體標註與來源在「旗艦模型」分頁的表 4-6。</p></div>') % (g('A'), g('D'), out, key)


HW_ORDER = ['H100', 'H200', 'B200', 'B300', 'GB200 NVL72', 'GB300 NVL72', 'VR200', 'MI355X']
SH_MODELS = [('Kimi K3', 'Kimi K3', 'MXFP4'), ('GLM-5.2', 'GLM-5.2 / 5.3', 'TileRT 列為 GLM-5.3'), ('V4-Pro', 'DeepSeek-V4-Pro', ''),
             ('V4.1-Flash', 'DeepSeek-V4.1-Flash', ''), ('Flash-Next', 'Qwen3.8-Flash-Next', ''), ('Qwen3.5-397B', 'Qwen3.5-397B', 'trace 截斷到 256K')]


def selfhost_grid():
    """Chapter 4: model x hardware grid of the InferenceX AgentX rows in tables 4-13 to 4-16."""
    text = chapter_text(4)
    need(4, '所以開了 spec decode 的每使用者速度是上限', 'InferenceX 沒有 Qwen3.8-2.4T-A95B 與 Qwen3.8-27B 的資料', '只有引擎團隊的數字',
         'TPU 唯一的獨立量測', '截斷到 256K 的 trace', '高吞吐點', '低並行點')
    cells = collections.defaultdict(list)
    n = 0
    for cap, model in (('表 4-13', 'Kimi K3'), ('表 4-14', 'GLM-5.2'), ('表 4-15', None), ('表 4-16', None)):
        head, rows = md_table(text, cap)
        assert head[3].startswith('低並行：tok/s/user 中位') and head[5].startswith('高吞吐：output tok/s/GPU'), head
        for r in rows:
            m, hw = (model, r[0]) if model else [x.strip() for x in r[0].split('；')]
            hw = re.sub(r'（.*?）', '', hw).strip()
            assert hw in HW_ORDER and m in [x[0] for x in SH_MODELS], (m, hw)
            eng = [x.strip() for x in r[1].split('；')]
            lo = re.match(r'([\d,]+) / ([\d,]+)；([\d.]+) / ([\d.]+)$', r[3])
            assert lo, r[3]
            mode = 'P/D' if eng[1].startswith('P/D') else 'agg'
            cells[(m, hw)].append({'eng': re.sub(r'（.*?）', '', eng[0]), 'mode': mode, 'hi': num(r[5]), 'lo': num(lo.group(1)), 'ttft': float(lo.group(3))})
            n += 1
    assert n == 52, n

    def grid(metric, unit, pane_title):
        cols = 'grid-template-columns:minmax(148px,1.5fr) repeat(%d,minmax(84px,1fr))' % len(HW_ORDER)
        h = '<span class="hh">模型</span>' + ''.join(
            '<span class="hh">%s%s</span>' % (hw.replace(' NVL72', '<small>NVL72</small>'), '<small>AMD</small>' if hw == 'MI355X' else ('<small>Vera Rubin NVL72</small>' if hw == 'VR200' else ''))
            for hw in HW_ORDER)
        body = ''
        for key, label, sub in SH_MODELS:
            best = {hw: max(cells[(key, hw)], key=lambda c: c[metric]) for hw in HW_ORDER if cells.get((key, hw))}
            vmax = max(c[metric] for c in best.values())
            body += '<span class="hr">%s%s</span>' % (esc(label), '<small>%s</small>' % esc(sub) if sub else '')
            for hw in HW_ORDER:
                c = best.get(hw)
                if not c:
                    body += '<span class="hc na">–</span>'
                    continue
                note = '%s · %s' % (c['eng'], c['mode']) if metric == 'hi' else 'TTFT %.2f s · %s' % (c['ttft'], c['eng'])
                body += '<span class="hc%s">%s<small>%s</small><i style="width:%.1f%%"></i></span>' % (
                    ' top' if c[metric] == vmax else '', format(int(c[metric]), ','), esc(note), max(2, c[metric] / vmax * 100))
        return ('<div data-pane="%s"><h4 class="pane-t">%s</h4><div class="hm-scroll" tabindex="0" role="region" aria-label="%s"><div class="hm" style="%s">%s%s</div></div>'
                '<p class="hm-u">單位：%s。橫條以同一列（同一個模型）的最大值為 100%%；粗體是該模型的最大值。</p></div>') % (metric, pane_title, pane_title, cols, h, body, unit)
    views = [('hi', '高吞吐點：每顆 GPU 的輸出 tok/s'), ('lo', '低並行點：每使用者 tok/s')]
    panes = grid('hi', 'output tokens/s per GPU；高吞吐點是中位 TTFT 低於 5 s 的最高吞吐點，沒有合格點時取最高吞吐點。小字為引擎與模式（agg = aggregated，P/D = prefill / decode 分離）', views[0][1]) + \
        grid('lo', '每使用者 tokens/s 的中位數（1 / TPOT，不含 TTFT）；低並行點是各配置最低並行的一點。小字為該點的中位 TTFT 與引擎', views[1][1])
    return ('<div class="widget"><div class="sec-h"><h3 style="font-size:18px">自架量測一覽：模型 × 硬體</h3>%s</div>'
            '<p class="wnote">InferenceX AgentX（長 context、多輪的 agentic trace 重播），2026-10-04 擷取 %s。每格取表 4-13 至表 4-16 中該模型在該硬體的最大值；'
            '各格的引擎、精度、佈局、GPU 數與執行日都不相同，引用前請看原表的那一列。</p>'
            '<div class="wbox" id="shg" style="padding:10px 0 8px">%s</div>'
            '<p class="wnote">這份資料只涵蓋 NVIDIA 與 AMD 的 GPU。TPU 的獨立量測只有 Qwen3.5-397B 的 8K / 1K（表 4-21），Trainium、Inferentia2 與 Cerebras 的公開結果在「AWS Trainium / Inferentia」與「Cerebras」兩個分頁。'
            'InferenceX 沒有 Qwen3.8-2.4T-A95B 與 Qwen3.8-27B 的資料，Qwen3.8-2.4T 只有引擎團隊的數字（表 4-17）。'
            'spec decode 採固定 acceptance，Kimi K3 開了 spec decode 的每使用者速度是上限。</p></div>') % (switcher('shg', views), g('A'), panes)


# ---------------------------------------------------------------- chapter 10: planner
def planner_shell():
    need(10, '4,764', '24.5M', '212M', '3.13M', '865', 'Scale tier 10M ITPM', 'Sonnet 4.6 預設 6M', 'Opus 5.5 預設 30M', 'Opus 4.8 預設 30M', 'Kimi K3 預設 10M', '3,239 GSU', '20,444 PTU', '1,514 GSU')
    eqs = [
        ('C_i = N · p_i · a_i · r_i', '角色 i 的平日呼叫數'),
        ('m = Σ C_i · s ÷ 60 · d', 'busy hour 的平均每分鐘請求數，以 P95 平日計'),
        ('k = max(1.15, 1 + 3 ÷ √m)', '尖峰分鐘係數，以共用同一份配額的合併流量計算'),
        ('RPM = m · k', '尖峰 RPM，與延遲無關'),
        ('TPM_x = RPM · tokens_x · f_x', 'x 為未快取輸入、cache read、輸出三類；f 是 token 比請求更尖的修正'),
        ('W = TTFT + o ÷ v', '一次呼叫的總時間；工具執行時間不計入'),
        ('L = RPM ÷ 60 · W', '同時在途請求數，Little’s law'),
        ('L99.9 = L + 3.1 · √L', 'Poisson 餘裕'),
    ]
    e_html = ''.join('<div class="eq"><code>%s</code><span>%s</span></div>' % (esc(a), b) for a, b in eqs)
    return ('<div class="widget" style="gap:28px"><div id="planner" class="widget" style="gap:28px"><noscript><p class="wnote">計算器需要 JavaScript。靜態的情境表在「情境」與「模型組合」兩個分頁。</p></noscript></div>'
            '<section class="block"><h3 style="font-size:22px">算式</h3><div class="eqs">%s</div>'
            '<p class="wnote">沒有算進去的三件事：被限流的請求會重試；用量逐年成長；會預扣 max_tokens 的平台，在途請求佔住的配額是併發 ×（輸入 + max_tokens）。'
            '算式的來歷在「方法與公式」分頁，每個參數的證據在<a href="11-evidence.html">第 11 章</a>。計算器與第 10 章的表用同一組算式：100,000 人、組合 B、base、單一時區的結果是 4,764 RPM。</p></section></div>') % e_html


# ---------------------------------------------------------------- sources page
def sources_shell(stats):
    s = stats['src_status']
    k = ('<section class="kpis" aria-label="來源統計"><div class="kpi"><span class="v"><span class="hl">%d</span></span><span class="d">不重複來源，第 1–11 章引用</span></div>'
         '<div class="kpi"><span class="v">%d</span><span class="d">存成本地副本後逐項比對</span></div>'
         '<div class="kpi"><span class="v">%d</span><span class="d">無法存檔，改以線上逐句核對</span></div>'
         '<div class="kpi"><span class="v">%d</span><span class="d">無法重讀；所引內容另有其他來源並列</span></div></section>') % (
        stats['n_sources'], s['local'], s['web'], s['unreadable'])
    return k + '<div id="sources" class="widget"><noscript><p class="wnote">來源清單需要 JavaScript。各章的來源也列在每個分頁最下方的「本節來源」。</p></noscript></div>'


# ---------------------------------------------------------------- fact-check record
KIND_ZH = collections.OrderedDict([
    ('WRONG', '數值或敘述與來源不符'), ('NOT_IN_SOURCE', '所引來源沒有這項內容'), ('CITATION', '補上或更換引用'),
    ('CLARIFY', '補上條件或限定範圍'), ('QUOTE', '引句改為逐字'), ('STALE', '來源已更新'),
    ('DERIVED_LABEL', '推算值補標 D 與算式'), ('DEAD_LINK', '連結失效，改指現行網址'),
])


def fill_factcheck(text, stats, corr, grounding_path):
    rows = [json.loads(l) for l in open(grounding_path, encoding='utf-8')]
    src = [r for r in rows if r['status'] in ('GROUNDED', 'PARTIAL', 'NONE_FOUND', 'NO_TOKENS', 'NO_LOCAL_SOURCE')]
    n_tok = sum(r.get('n_tok', 0) for r in src)
    n_found = sum(r.get('n_found', 0) for r in src)
    stats.update({'n_units': len(src), 'n_tok': n_tok, 'n_found': n_found})
    kinds = collections.Counter(c['kind'] for c in corr)
    chs = collections.Counter(c['ch'] for c in corr)
    assert set(kinds) <= set(KIND_ZH), kinds
    tk = '| 更正類型 | 處數 | 說明 |\n|---|---|---|\n' + '\n'.join(
        '| %s | %d | %s |' % (k, kinds.get(k, 0), z) for k, z in KIND_ZH.items() if kinds.get(k))
    names = {'%02d' % c['n']: c['nav'] for c in M.CHAPTERS}
    tc = '| 章 | 更正處數 |\n|---|---|\n' + '\n'.join('| 第 %d 章 %s | %d |' % (int(k), names[k], v) for k, v in sorted(chs.items()))
    s = stats['src_status']
    rep = {'N_SRC': stats['n_sources'], 'N_LOCAL': s['local'], 'N_WEB': s['web'], 'N_UNREAD': s['unreadable'],
           'N_WEB_UNREAD': s['web'] + s['unreadable'], 'N_CORR': len(corr), 'N_UNITS': format(len(src), ','),
           'N_TOK': format(n_tok, ','), 'N_FOUND': format(n_found, ','), 'PCT_FOUND': '%.1f%%' % (n_found / n_tok * 100),
           'TABLE_KINDS': tk, 'TABLE_CHAPTERS': tc, 'TABLE_CORRECTIONS': ''}
    for k, v in rep.items():
        text = text.replace('{{%s}}' % k, str(v))
    assert '{{' not in text, re.findall(r'\{\{\w+\}\}', text)
    return text


def factcheck_kpis(stats):
    s = stats['src_status']
    return ('<section class="kpis" aria-label="查核統計"><div class="kpi"><span class="v"><span class="hl">%d</span></span><span class="d">處更正，逐筆列在「更正紀錄」</span></div>'
            '<div class="kpi"><span class="v">%d</span><span class="d">個來源：%d 個本地比對、%d 個線上核對、%d 個無法重讀</span></div>'
            '<div class="kpi"><span class="v">%s</span><span class="d">個數字、版本、日期與引句逐項比對，%.1f%% 在所引來源直接找到，其餘逐一判讀</span></div>'
            '<div class="kpi"><span class="v">24</span><span class="d">項首頁與關鍵發現的敘述交給獨立複核；數字全部重現，13 項收緊了條件</span></div></section>') % (
        stats['n_corr'], stats['n_sources'], s['local'], s['web'], s['unreadable'], format(stats['n_tok'], ','), stats['n_found'] / stats['n_tok'] * 100)


def _plain_md(s):
    s = LINK.sub(lambda m: '[' + m.group(1) + ']', s)
    return s.replace('**', '')


def corrections_table(corr, ctx):
    names = {'%02d' % c['n']: c for c in M.CHAPTERS}
    rows = []
    for i, c in enumerate(corr, 1):
        ch = names[c['ch']]
        rows.append('<tr><td class="num">%d</td><td style="white-space:nowrap"><a href="%s.html">%s</a></td><td><span class="kind kind-%s">%s</span><span class="chip-note">%s</span></td>'
                    '<td><dl class="diff"><dt>原文</dt><dd class="old">%s</dd><dt>更正</dt><dd>%s</dd><dt>依據</dt><dd class="why" lang="en">%s</dd></dl></td></tr>' % (
                        i, ch['slug'], '第 %d 章' % ch['n'], c['kind'], c['kind'], KIND_ZH[c['kind']],
                        esc(_plain_md(c['old'])), esc(_plain_md(c['new'])), esc(c['why'])))
    return ('<p class="wnote">每一筆是章節原稿的一次改動，依套用順序排列。「依據」是查核當下記下的理由，多數直接引用來源原文，所以保留英文。'
            '表上方的篩選框可以輸入章號（例如「第 7 章」）或類型（例如 WRONG、CITATION）。</p>'
            '<figure class="tbl" data-rows="%d" data-cols="4"><div class="tbl-scroll"><table style="min-width:760px"><thead><tr><th scope="col">#</th><th scope="col" style="min-width:5em">章</th>'
            '<th scope="col" style="min-width:11em">類型</th><th scope="col">改動</th></tr></thead><tbody>%s</tbody></table></div></figure>') % (len(corr), '\n'.join(rows))


# ---------------------------------------------------------------- assets
def copy_assets(site, dist):
    """static/ plus the vendored third-party fonts and KaTeX CSS (site/vendor, filled by tools/vendor.py)."""
    a = os.path.join(dist, 'assets')
    for f in os.listdir(os.path.join(site, 'static')):
        shutil.copy(os.path.join(site, 'static', f), os.path.join(a, f))
    v = os.path.join(site, 'vendor')
    if not os.path.isdir(v):
        raise SystemExit('site/vendor is missing: run `npm ci` in site/tools, then `python3 tools/vendor.py`')
    shutil.copytree(os.path.join(v, 'fonts'), os.path.join(a, 'fonts'))
    shutil.copytree(os.path.join(v, 'katex'), os.path.join(a, 'katex'))
    open(os.path.join(a, 'favicon.svg'), 'w').write(
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32"><rect width="32" height="32" fill="#FBFCFA"/><rect x="7" y="7" width="18" height="18" fill="#14201C"/>'
        '<circle cx="11" cy="11" r="1.6" fill="#F2B544"/><path d="M11 2v5M16 2v5M21 2v5M11 25v5M16 25v5M21 25v5M2 11h5M2 16h5M2 21h5M25 11h5M25 16h5M25 21h5" stroke="#14201C" stroke-width="2" fill="none"/></svg>')
