#!/usr/bin/env python3
"""Build the Inference ASIC Atlas static site into site/dist (plain HTML/CSS/JS, no build step on the host).

    python3 site/build.py

Chapters are read from ../chapters/*.md and are never rewritten here; the only text transformation is the
punctuation normalisation of chapters 1, 4 and 10 (lib/normalize.py).
"""
import collections
import html as _html
import json
import os
import re
import shutil
import sys

from bs4 import BeautifulSoup

SITE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(SITE)
sys.path.insert(0, SITE)
sys.path.insert(0, os.path.join(SITE, 'lib'))

import meta as M  # noqa: E402
import render as R  # noqa: E402
import widgets as W  # noqa: E402
from normalize import normalize  # noqa: E402

DIST = os.path.join(SITE, 'dist')
CHDIR = os.path.join(ROOT, 'chapters')
FC = os.path.join(ROOT, 'factcheck')
esc = _html.escape

LABEL_OVERRIDE = {
    'tensor parallel 對 MLA 模型 KV 容量的影響': 'TP 與 MLA 的 KV',
    '一條 1M 序列的 KV 有多大、搬一次要多久': 'KV 搬移時間',
    'InferenceX 的模型化成本與每 MW token': 'InferenceX 模型化成本',
    '各供應商與硬體類別實際提供的 context': '實際提供的 context',
    'rate limit、配額與長 context 的流量占比': 'rate limit 與配額',
    '模型的原生 context、最大輸出與長 prompt 計價': '原生 context 與計價',
    '不能換算到 Trainium、TPU 與 Cerebras 的部分': '不能換算的部分',
    '四個家族在各晶片上有文件的最新版本': '四個家族的最新版本',
    'GPU：InferenceX agentic trace replay': 'GPU：InferenceX',
    'GPU：Qwen3.8-2.4T 與其他引擎團隊量測': 'GPU：引擎團隊量測',
    'NVIDIA：Hopper、Blackwell、Vera Rubin': 'NVIDIA',
    'AMD：MI300X 到 MI455X / Helios': 'AMD',
    'Groq 3 LPU / LPX 與 GPU–LPU 分工': 'Groq 3 LPU / LPX',
    '(c) coding agent 的成本、token 揭露、預算與上限': '(c) coding agent 的成本',
    '(a) 第三方量測：Artificial Analysis 與 OpenRouter': '(a) 第三方量測',
    '規劃時要讀出的六件事': '要讀出的六件事',
    'AWS Trainium 與 Inferentia2（Neuron）': 'Trainium 與 Inferentia2',
}


# ------------------------------------------------------------------ parsing
def parse_chapter(text):
    lines = text.split('\n')
    assert lines[0].startswith('# '), lines[0]
    pre, secs, cur, sub, fence = [], [], None, None, False
    for line in lines[1:]:
        if line.startswith('```'):
            fence = not fence
        if not fence and line.startswith('## '):
            cur = {'title': line[3:].strip(), 'intro': [], 'subs': []}
            secs.append(cur)
            sub = None
            continue
        if not fence and line.startswith('### ') and cur is not None:
            sub = {'title': line[4:].strip(), 'lines': []}
            cur['subs'].append(sub)
            continue
        (pre if cur is None else cur['intro'] if sub is None else sub['lines']).append(line)
    for s in secs:
        s['intro'] = '\n'.join(s['intro']).strip('\n')
        for b in s['subs']:
            b['md'] = '\n'.join(b.pop('lines')).strip('\n')
    return {'title': lines[0][2:].strip(), 'pre': '\n'.join(pre).strip(),
            'secs': [s for s in secs if '網站呈現建議' not in s['title']]}


def split_lead(md):
    parts = re.split(r'\n\s*\n', md.strip(), maxsplit=1)
    first = parts[0]
    if first and not re.match(r'^(\||- |\d+\. |```|\*\*表 )', first):
        return first, (parts[1].strip('\n') if len(parts) > 1 else '')
    return '', md


CAP = re.compile(r'^\*\*(表 \d+-\d+)\s*([^*\n]*)\*\*', re.M)


def split_by_caption(md):
    idx = [m.start() for m in CAP.finditer(md)]
    if len(idx) < 2 or len(md) < 6000:
        return None
    blocks = []
    for a, b in zip(idx, idx[1:] + [len(md)]):
        blk = md[a:b].strip()
        m = CAP.match(blk)
        blocks.append((m.group(1), m.group(2).strip(), blk))
    return md[:idx[0]].strip(), blocks


def short_label(title, limit=30):
    if title in LABEL_OVERRIDE:
        return LABEL_OVERRIDE[title]
    m = re.match(r'^(\([a-h]\)\s*)(.*)$', title)
    head, t = (m.group(1), m.group(2)) if m else ('', title)
    if R.dw(head + t) <= limit:
        return head + t
    for i, c in enumerate(t):
        if c in '（(：:' and i >= 3:
            t = t[:i].strip()
            break
    if R.dw(head + t) > limit + 4:
        out, w = '', 0
        for c in t:
            w += R.dw(c)
            if w > limit:
                break
            out += c
        t = out.rstrip() + '…'
    return head + t


# ------------------------------------------------------------------ tabs
def build_tab(sec, label, ctx, chn, only_subs=None, with_intro=True, subtabs=True):
    tab = {'label': label, 'title': sec['title'], 'lead': None, 'top': [], 'subs': [], 'body': None, 'links': []}
    ctx['links'] = []
    lead_md, rest = split_lead(sec['intro']) if with_intro else ('', '')
    if lead_md:
        tab['lead'] = R.render_md(lead_md, ctx)
    subs = sec['subs'] if only_subs is None else [sec['subs'][i] for i in only_subs]
    if subs:
        if rest.strip():
            has_table = bool(re.search(r'^\|', rest, flags=re.M))
            if (has_table or len(rest) > 900) and subtabs:
                lab = M.FIRST_SUB.get((chn, sec['title'])) or ('總表' if has_table else '概要')
                tab['subs'].append({'label': lab, 'title': None, 'soup': R.render_md(rest, ctx)})
            else:
                tab['top'].append(R.render_md(rest, ctx))
        for b in subs:
            tab['subs'].append({'label': short_label(b['title']), 'title': b['title'], 'soup': R.render_md(b['md'], ctx)})
        if not subtabs or len(tab['subs']) == 1:
            tab['flat'] = True
    else:
        sp = split_by_caption(rest)
        if sp:
            head, blocks = sp
            if head:
                tab['top'].append(R.render_md(head, ctx))
            for num, ttl, blk in blocks:
                tab['subs'].append({'label': short_label(num + ' ' + ttl, 24), 'title': None, 'soup': R.render_md(blk, ctx)})
        else:
            tab['body'] = R.render_md(rest, ctx) if rest.strip() else None
    tab['links'] = ctx['links']
    return tab


def unique_links(links):
    seen, out = set(), []
    for url, name in links:
        if url in seen:
            continue
        seen.add(url)
        out.append((name, url))
    return out


# ------------------------------------------------------------------ page chrome
LOGO = ('<svg width="32" height="32" viewBox="0 0 32 32" aria-hidden="true"><rect class="k" x="7" y="7" width="18" height="18"></rect>'
        '<circle cx="11" cy="11" r="1.6" fill="#F2B544"></circle><path class="p" d="M11 2v5M16 2v5M21 2v5M11 25v5M16 25v5M21 25v5M2 11h5M2 16h5M2 21h5M25 11h5M25 16h5M25 21h5" stroke-width="2" fill="none"></path></svg>')
GRADE_LEGEND = ('<div class="legend" aria-label="證據等級"><span><span class="g g-a">A</span>獨立第三方量測</span>'
                '<span><span class="g g-b">B</span>廠商或夥伴公布，揭露方法</span><span><span class="g g-c">C</span>廠商宣稱或規格</span>'
                '<span><span class="g g-d">D</span>本文推算，附算式</span></div>')


def nav_html(pages, current):
    def link(p):
        cur = ' aria-current="page"' if p['file'] == current else ''
        return '<a href="%s"%s><span class="n">%s</span><span>%s</span></a>' % (p['file'], cur, p['num'], esc(p['nav']))
    by_num = {p['num']: p for p in pages}
    out = [link(by_num['00'])]
    for title, nums in M.GROUPS:
        out.append('<div class="grp"><span class="grp-t">%s</span>%s</div>' % (title, ''.join(link(by_num['%02d' % n]) for n in nums)))
    out.append('<div class="grp"><span class="grp-t">附錄 APPENDIX</span>%s</div>' % link(by_num['A']))
    return ''.join(out)


def page_html(page, pages, body, stats, scripts=(), katex=False, data_scripts=()):
    title = page['nav'] if page['num'] != '00' else '總覽'
    order = [p for p in pages if p['num'] not in ('S',)]
    i = [p['file'] for p in order].index(page['file']) if page['file'] in [p['file'] for p in order] else -1
    pager = ''
    if i >= 0:
        prev = order[i - 1] if i > 0 else None
        nxt = order[i + 1] if i + 1 < len(order) else None
        pager = '<nav class="pager" aria-label="上一張與下一張">%s%s</nav>' % (
            '<a href="%s"><span>← %s</span>%s</a>' % (prev['file'], prev['num'], esc(prev['nav'])) if prev else '',
            '<a class="nx" href="%s"><span>%s →</span>%s</a>' % (nxt['file'], nxt['num'], esc(nxt['nav'])) if nxt else '')
    code = 'IA-%s' % page['num']
    head = [
        '<!doctype html>', '<html lang="zh-Hant">', '<head>', '<meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1">',
        '<title>%s · %s</title>' % (esc(title), M.SITE_NAME),
        '<meta name="description" content="%s">' % esc(page.get('desc') or page.get('lead_text') or ''),
        '<meta name="color-scheme" content="light dark">',
        '<link rel="icon" href="assets/favicon.svg" type="image/svg+xml">',
        '<link rel="preconnect" href="https://fonts.googleapis.com">',
        '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>',
        '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@400;500;700;900&amp;display=swap">',
        '<link rel="stylesheet" href="assets/site.css">',
    ]
    if katex:
        head.append('<link rel="stylesheet" href="assets/katex/katex.min.css">')
    head.append("<script>(function(){var d=document.documentElement;d.classList.add('js');try{var t=localStorage.getItem('ia-theme');"
                "if(t==='light'||t==='dark')d.setAttribute('data-theme',t)}catch(e){}})();</script>")
    head.append('</head>')
    hdr = (
        '<body><a class="skip" href="#sheet">跳到內容</a>'
        '<header class="hdr"><div class="hdr-in">'
        '<a class="brand" href="index.html">%s<span class="brand-t"><span class="brand-en">INFERENCE ASIC ATLAS</span><span class="brand-zh">推論晶片圖鑑</span></span></a>'
        '<button type="button" class="hbtn menu-btn" id="menu-btn" aria-expanded="false" aria-controls="idx">'
        '<svg width="18" height="18" viewBox="0 0 18 18" aria-hidden="true"><path d="M2 4.5h14M2 9h14M2 13.5h14" stroke="currentColor" stroke-width="1.8" fill="none"></path></svg><span>章節</span></button>'
        '<div class="hdr-tools"><span class="rev">REV %s · 12 SHEETS · %d SOURCES</span>'
        '<form id="hsearch" class="hsearch" action="search.html" method="get" role="search"><input name="q" type="search" placeholder="搜尋全站" aria-label="搜尋全站">'
        '<button type="submit" aria-label="搜尋"><svg width="18" height="18" viewBox="0 0 18 18" aria-hidden="true"><circle cx="7.5" cy="7.5" r="5" fill="none" stroke="currentColor" stroke-width="1.8"></circle><path d="M11.5 11.5L16 16" stroke="currentColor" stroke-width="1.8"></path></svg></button></form>'
        '<button type="button" class="hbtn" id="theme-btn" aria-label="切換深色模式"><svg width="18" height="18" viewBox="0 0 18 18" aria-hidden="true"><circle cx="9" cy="9" r="7" fill="none" stroke="currentColor" stroke-width="1.6"></circle><path d="M9 2a7 7 0 0 1 0 14z" fill="currentColor"></path></svg></button>'
        '</div></div></header>'
    ) % (LOGO, M.REV, stats['n_sources'])
    foot = ('<footer class="foot"><span>%s</span><span class="code">%s · REV %s</span></footer>' % (
        page.get('foot') or '資料截至 %s；逐項查核於 %s 完成。模型與價格每週在變，引用前請對照來源。' % (M.DATA_DATE, M.REV), code, M.REV))
    tail = ['<script src="assets/site.js" defer></script>']
    for s in data_scripts:
        tail.append('<script src="%s" defer></script>' % s)
    for s in scripts:
        tail.append('<script src="%s" defer></script>' % s)
    return '\n'.join(head) + '\n' + hdr + '\n<div class="wrap">\n<nav class="idx" id="idx" aria-label="章節">' + nav_html(pages, page['file']) + \
        '</nav>\n<main id="sheet">\n' + body + '\n' + pager + '\n' + foot + '\n</main>\n</div>\n' + '\n'.join(tail) + '\n</body>\n</html>\n'


def sheet_head(page, extra=''):
    total = 12
    code = 'SHEET %s / %d · %s' % (page['num'], total, page['en']) if page['num'].isdigit() and len(page['num']) == 2 else page['en']
    lead = '<p class="lead">%s</p>' % page['lead_html'] if page.get('lead_html') else ''
    return '<section class="sheet-head"><span class="sheet-code">%s</span><h1>%s</h1>%s%s</section>' % (code, esc(page['h1']), lead, extra)


# ------------------------------------------------------------------ serialise tabs
def soup_html(s):
    return str(s) if s is not None else ''


def tabs_html(page, tabs, aria='本章的小節'):
    n = int(page['num']) if page['num'].isdigit() else None
    btns, panels = [], []
    for ti, tab in enumerate(tabs):
        pid = tab.get('id') or 's%d' % (ti + 1)
        on = ti == 0
        num = '<span class="n">%d.%d</span>' % (n, ti + 1) if n else ''
        btns.append('<button type="button" class="tab" role="tab" id="tab-%s" aria-controls="%s" aria-selected="%s">%s<span>%s</span></button>' % (
            pid, pid, 'true' if on else 'false', num, esc(tab['label'])))
        inner = ['<div class="panel-head"><h2>%s</h2>%s</div>' % (esc(tab['title']), '<div class="sec-lead prose">%s</div>' % soup_html(tab['lead']) if tab.get('lead') else '')]
        for t in tab.get('top', []):
            inner.append(t if isinstance(t, str) else '<div class="prose">%s</div>' % soup_html(t))
        if tab.get('subs') and not tab.get('flat'):
            sb, sp = [], []
            for si, sub in enumerate(tab['subs']):
                sid = '%s-%d' % (pid, si + 1)
                son = si == 0
                sb.append('<button type="button" class="subtab" role="tab" id="tab-%s" aria-controls="%s" aria-selected="%s">%s</button>' % (
                    sid, sid, 'true' if son else 'false', esc(sub['label'])))
                h3 = '<h3>%s</h3>' % esc(sub['title']) if sub.get('title') else '<h3 class="ph">%s</h3>' % esc(sub['label'])
                if 'html' in sub:
                    content = sub['html'] + ('<div class="prose" style="margin-top:22px">%s</div>' % soup_html(sub['soup']) if 'soup' in sub else '')
                else:
                    content = '<div class="prose">%s%s</div>' % (h3, soup_html(sub['soup']))
                sp.append('<div class="subpanel%s" role="tabpanel" id="%s" aria-labelledby="tab-%s">%s</div>' % (
                    ' on' if son else '', sid, sid, content))
            inner.append('<div class="subtabs"><div class="subtablist" role="tablist" aria-label="%s">%s</div>%s</div>' % (
                esc(tab['title']), ''.join(sb), ''.join(sp)))
        elif tab.get('subs'):
            for sub in tab['subs']:
                h3 = '<h3>%s</h3>' % esc(sub['title']) if sub.get('title') else ''
                inner.append(sub['html'] if 'html' in sub else '<div class="prose">%s%s</div>' % (h3, soup_html(sub['soup'])))
        if tab.get('body') is not None:
            inner.append(tab['body'] if isinstance(tab['body'], str) else '<div class="prose">%s</div>' % soup_html(tab['body']))
        links = unique_links(tab.get('links', []))
        if links:
            inner.append('<details class="srcs"><summary>本節來源（%d）</summary><ul>%s</ul></details>' % (
                len(links), ''.join('<li><a href="%s" target="_blank" rel="noopener">%s</a></li>' % (esc(u, quote=True), esc(nm)) for nm, u in links)))
        panels.append('<section class="panel%s" role="tabpanel" id="%s" aria-labelledby="tab-%s">%s</section>' % (
            ' on' if on else '', pid, pid, '\n'.join(inner)))
    return '<div class="tabs"><div class="tablist" role="tablist" aria-label="%s">%s</div>\n%s</div>' % (aria, ''.join(btns), '\n'.join(panels))


def tab_soups(tab):
    """(sub index or -1, soup) for every rendered piece of a tab."""
    if tab.get('lead') is not None:
        yield -1, tab['lead']
    for t in tab.get('top', []):
        if not isinstance(t, str):
            yield -1, t
    for si, sub in enumerate(tab.get('subs', [])):
        if 'soup' in sub:
            yield (-1 if tab.get('flat') else si), sub['soup']
    if tab.get('body') is not None and not isinstance(tab['body'], str):
        yield -1, tab['body']


def tree_soup_tag(node, text):
    soup = node
    while soup.parent is not None:
        soup = soup.parent
    tag = soup.new_tag('span', attrs={'class': 'leaf-id'})
    tag.string = text
    return tag


# ------------------------------------------------------------------ main
def main():
    stats = {}
    src_site = json.load(open(os.path.join(FC, 'sources_site.json'), encoding='utf-8'))
    corr = [json.loads(l) for l in open(os.path.join(FC, 'corrections.jsonl'), encoding='utf-8')]
    stats['n_sources'] = len(src_site)
    stats['src_status'] = collections.Counter(s['status'] for s in src_site)
    stats['n_corr'] = len(corr)
    unreadable = {s['url'] for s in src_site if s['status'] == 'unreadable'}

    ctx = {'unreadable': unreadable, 'chapters': {c['n']: c['slug'] for c in M.CHAPTERS}, 'table_page': {}, 'tables': {}}
    ctx['chapters'][12] = '12-sources'

    # ---- pages registry
    pages = [{'num': '00', 'file': 'index.html', 'nav': '總覽', 'en': 'OVERVIEW'}]
    for c in M.CHAPTERS:
        pages.append({'num': '%02d' % c['n'], 'file': c['slug'] + '.html', 'nav': c['nav'], 'en': c['en'], 'h1': c['h1'], 'cfg': c})
    pages.append({'num': '12', 'file': '12-sources.html', 'nav': '來源', 'en': 'SOURCES', 'h1': '來源'})
    pages.append({'num': 'A', 'file': 'factcheck.html', 'nav': '查核紀錄', 'en': 'APPENDIX A · FACT-CHECK RECORD', 'h1': '查核紀錄'})
    pages.sort(key=lambda p: (p['num'] == 'A', p['num']))
    by_num = {p['num']: p for p in pages}

    # ---- chapters: parse and render
    chapters = {}
    for c in M.CHAPTERS:
        text = open(os.path.join(CHDIR, c['src']), encoding='utf-8').read()
        if c.get('norm'):
            text = normalize(text)
        ch = parse_chapter(text)
        chapters[c['n']] = ch
        page = by_num['%02d' % c['n']]
        before = set(ctx['tables'])
        nt0 = ctx.get('ntables', 0)
        if c['n'] == 7:
            tabs = W.ch7_tabs(ch, ctx, build_tab, text)
        else:
            labels = c['tabs']
            assert len(labels) == len(ch['secs']), (c['n'], labels, [s['title'] for s in ch['secs']])
            tabs = [build_tab(sec, lab, ctx, c['n']) for sec, lab in zip(ch['secs'], labels)]
        ctx['links'] = []
        page['pre'] = R.render_md(ch['pre'], ctx, legend=True) if ch['pre'] else None
        page['tabs'] = tabs
        for tid in set(ctx['tables']) - before:
            ctx['table_page'][tid] = c['slug']
        page['text'] = text
        stats.setdefault('tables_by_ch', {})[c['n']] = ctx.get('ntables', 0) - nt0

    # ---- chapter-specific widgets
    matrix = W.matrix_data(ctx)
    counts = matrix['counts']
    stats['matrix_counts'] = counts
    p6 = by_num['06']
    p6['cfg']['lead'] = ('文件列為「支援」的項數：NVIDIA GPU %d、AMD GPU %d、Trainium %d、TPU %d、Inferentia2 %d、Cerebras 公開 API %d；'
                         '「部分」與「實驗」不計入。狀態取自各專案在 2026-10-04 的文件與 repository 預設分支。') % (
        counts['nv'], counts['amd'], counts['trn'], counts['tpu'], counts['inf'], counts['wse'])
    t0 = p6['tabs'][0]
    first = {'label': '互動矩陣', 'title': None, 'html': W.matrix_shell(matrix)}
    if t0['top']:
        first['soup'] = t0['top'].pop(0)
        assert not t0['top']
    t0['subs'].insert(0, first)
    t0.pop('flat', None)
    p10 = by_num['10']
    p10['tabs'].insert(0, {'id': 'calc', 'label': '計算器', 'title': '容量計算器', 'lead': None, 'top': [], 'subs': [],
                           'body': W.planner_shell(), 'links': []})
    for ti, tab in enumerate(p10['tabs'][1:], start=1):
        tab['id'] = 's%d' % ti

    # chapter 9: draw the nested list of the decision tree as a tree, leaf codes as chips
    tree = by_num['09']['tabs'][2]['subs'][0]['soup'].find('ol')
    tree['class'] = ['tree']
    leaves = 0
    for st in tree.find_all('strong'):
        m = re.match(r'^(L\d+)｜', st.get_text())
        if not m:
            continue
        first = st.contents[0]
        assert isinstance(first, str) and first.startswith(m.group(0)), first
        chip = tree_soup_tag(tree, m.group(1))
        first.replace_with(first[len(m.group(0)):])
        st.insert(0, chip)
        st['class'] = ['leaf']
        leaves += 1
    assert leaves == 12, leaves

    # charts built from the chapters' own tables
    by_num['01']['tabs'][0]['top'].append(W.silicon_chart())
    by_num['08']['tabs'][0]['top'].insert(0, W.xhw_chart())
    by_num['04']['tabs'][1]['top'].insert(0, W.flagship_chart())
    by_num['04']['tabs'][2]['top'].insert(0, W.selfhost_grid())

    # ---- overview and fact-check record
    ov_text = open(os.path.join(CHDIR, '00-overview.md'), encoding='utf-8').read()
    stats['n_tables_ch'] = sum(stats['tables_by_ch'].values())
    for k, v in (('N_TABLES', stats['n_tables_ch']), ('N_SRC', stats['n_sources']), ('N_LOCAL', stats['src_status']['local']),
                 ('N_WEB', stats['src_status']['web']), ('N_UNREAD', stats['src_status']['unreadable']), ('N_CORR', stats['n_corr'])):
        ov_text = ov_text.replace('{{%s}}' % k, str(v))
    assert '{{' not in ov_text
    ov = parse_chapter(ov_text)
    home = by_num['00']
    home['h1'] = '五類推論晶片的實測、限制與容量規劃'
    home_tabs = [{'id': 'home', 'label': '總覽', 'title': '關鍵數字與五個家族', 'lead': None, 'top': [], 'subs': [],
                  'body': W.home_overview(counts, stats), 'links': []}]
    for sec, lab in zip(ov['secs'], ['14 項關鍵發現', '研究範圍', '方法與限制']):
        home_tabs.append(build_tab(sec, lab, ctx, 0, subtabs=False))
    home['tabs'] = home_tabs
    ctx['links'] = []
    home['pre'] = None

    fc_text = open(os.path.join(CHDIR, '13-factcheck.md'), encoding='utf-8').read()
    fc_text = W.fill_factcheck(fc_text, stats, corr, os.path.join(FC, 'grounding.jsonl'))
    fcp = parse_chapter(fc_text)
    fpage = by_num['A']
    ftabs = []
    for sec, lab in zip(fcp['secs'], ['摘要', '方法', '重算的項目', '即時資料的漂移', '未能查核', '更正紀錄']):
        if lab == '更正紀錄':
            tab = build_tab({'title': sec['title'], 'intro': '', 'subs': []}, lab, ctx, 13)
            tab['body'] = W.corrections_table(corr, ctx)
        elif lab == '摘要':
            tab = build_tab(sec, lab, ctx, 13, subtabs=False)
            # the two count tables sit side by side and need no table tools
            for piece in [tab.get('body')] + list(tab.get('top', [])):
                figs = piece.find_all('figure', class_='tbl') if piece is not None and not isinstance(piece, str) else []
                if len(figs) >= 2:
                    pair = piece.new_tag('div', attrs={'class': 'pair'})
                    figs[0].insert_before(pair)
                    for f in figs[:2]:
                        f['data-plain'] = '1'
                        f.find('table')['class'] = (f.find('table').get('class') or []) + ['fit']
                        pair.append(f.extract())
            tab['top'].insert(0, W.factcheck_kpis(stats))
        else:
            tab = build_tab(sec, lab, ctx, 13, subtabs=False)
        tab['links'] = []
        ftabs.append(tab)
    fpage['tabs'] = ftabs
    fpage['pre'] = R.render_md(fcp['pre'], ctx) if fcp['pre'] else None

    # ---- cross-links, block ids, search index
    index_entries, index_pages = [], []
    content_pages = [p for p in pages if p.get('tabs')]
    for pi, page in enumerate(content_pages):
        slug = page['file'][:-5]
        bid = 0
        pmeta = {'f': page['file'], 'n': page['num'], 't': page['nav'], 'tabs': []}
        if page.get('pre') is not None:
            R.crosslink(page['pre'], page['pre'], ctx, slug)
        for ti, tab in enumerate(page['tabs']):
            pid = tab.get('id') or 's%d' % (ti + 1)
            real_subs = [s for s in tab.get('subs', [])] if not tab.get('flat') else []
            pmeta['tabs'].append({'t': tab['label'], 'subs': [s['label'] for s in real_subs]})
            index_entries.append([pi, ti, -1, pid, 'h', tab['title']])
            for si, sub in enumerate(real_subs):
                index_entries.append([pi, ti, si, '%s-%d' % (pid, si + 1), 'h', sub.get('title') or sub['label']])
            for si, soup in tab_soups(tab):
                R.crosslink(soup, soup, ctx, slug)
                for el, kind, txt in R.plain_blocks(soup):
                    if kind == 'c':
                        fig = el.find_parent('figure')
                        anchor = fig.get('id') if fig is not None else None
                        if not anchor:
                            bid += 1
                            anchor = 'b%d' % bid
                            fig['id'] = anchor
                    else:
                        anchor = el.get('id')
                        if not anchor:
                            bid += 1
                            anchor = 'b%d' % bid
                            el['id'] = anchor
                    index_entries.append([pi, ti, si, anchor, kind, txt])
        index_pages.append(pmeta)

    # ---- write
    if os.path.exists(DIST):
        shutil.rmtree(DIST)
    os.makedirs(os.path.join(DIST, 'assets'))
    W.copy_assets(SITE, DIST)

    for page in content_pages:
        cfg = page.get('cfg', {})
        if page['num'] == '00':
            page['lead_html'] = ('Trainium、Inferentia、TPU、GPU、Cerebras 跑大型語言模型時的速度、技術支援與長上下文可行性，'
                                 '以及 1 萬到 10 萬人導入時要準備多少 TPM 與 RPM。每個數字都附來源與證據等級。')
        elif page['num'] == 'A':
            page['lead_html'] = ('%d 個來源全部重新讀取，更正 %d 處。這一頁記錄查核怎麼做、改了什麼、哪些無法查核。' % (stats['n_sources'], stats['n_corr']))
        else:
            lead_soup = R.render_md(cfg['lead'], {'unreadable': unreadable})
            R.crosslink(lead_soup, lead_soup, ctx, page['file'][:-5])
            page['lead_html'] = lead_soup.p.decode_contents()
        page['lead_text'] = BeautifulSoup(page['lead_html'], 'html.parser').get_text()
        extra = ''
        if page.get('pre') is not None:
            extra += '<div class="conv prose">%s</div>' % soup_html(page['pre'])
        if page.get('pre') is None or '等級' not in page['pre'].get_text():
            extra += GRADE_LEGEND
        body = sheet_head(page, extra) + '\n' + tabs_html(page, page['tabs'])
        scripts, data_scripts = [], []
        if page['num'] == '06':
            data_scripts.append('assets/data-matrix.js')
            scripts.append('assets/matrix.js')
        if page['num'] == '07':
            data_scripts.append('assets/data-kv.js')
            scripts.append('assets/longctx.js')
        if page['num'] == '10':
            scripts += ['assets/planner-model.js', 'assets/planner.js']
        html = page_html(page, pages, body, stats, scripts=scripts, katex='class="formula"' in body, data_scripts=data_scripts)
        open(os.path.join(DIST, page['file']), 'w', encoding='utf-8').write(html)

    # sources page
    sp = by_num['12']
    sp['lead_html'] = ('%d 個不重複來源，依引用它的章節列出；%d 個以本地副本比對、%d 個線上逐句核對、%d 個無法重讀。'
                       '查核的做法與更正紀錄見<a href="factcheck.html">查核紀錄</a>。') % (
        stats['n_sources'], stats['src_status']['local'], stats['src_status']['web'], stats['src_status']['unreadable'])
    sp['lead_text'] = BeautifulSoup(sp['lead_html'], 'html.parser').get_text()
    body = sheet_head(sp) + '\n' + W.sources_shell(stats)
    open(os.path.join(DIST, sp['file']), 'w', encoding='utf-8').write(
        page_html(sp, pages, body, stats, scripts=['assets/sources.js'], data_scripts=['assets/data-sources.js']))

    # search page and 404
    srch = {'num': 'S', 'file': 'search.html', 'nav': '搜尋', 'en': 'SEARCH', 'h1': '搜尋全站',
            'lead_html': '搜尋 11 章的每一段文字、每一列表格與表格標題；點結果會直接跳到那一列。', 'lead_text': '搜尋全站'}
    body = sheet_head(srch) + '\n<div id="search" class="widget"><noscript>搜尋需要 JavaScript。</noscript></div>'
    open(os.path.join(DIST, 'search.html'), 'w', encoding='utf-8').write(
        page_html(srch, pages, body, stats, scripts=['assets/search.js'], data_scripts=['assets/search-index.js']))
    nf = {'num': '404', 'file': '404.html', 'nav': '找不到這一頁', 'en': 'NOT FOUND', 'h1': '找不到這一頁',
          'lead_html': '這個網址沒有對應的頁面。從左邊的章節索引選一張，或<a href="search.html">搜尋全站</a>。', 'lead_text': '找不到這一頁'}
    # Amplify serves 404.html for any missing path, so its links must resolve from the site root
    open(os.path.join(DIST, '404.html'), 'w', encoding='utf-8').write(
        page_html(nf, pages, sheet_head(nf), stats).replace('<meta charset="utf-8">', '<meta charset="utf-8">\n<base href="/">', 1))

    # data files
    A = os.path.join(DIST, 'assets')
    open(os.path.join(A, 'data-matrix.js'), 'w', encoding='utf-8').write(
        'window.IA_MATRIX=' + json.dumps(matrix['js'], ensure_ascii=False, separators=(',', ':')) + ';\n')
    open(os.path.join(A, 'data-kv.js'), 'w', encoding='utf-8').write(
        'window.IA_KV=' + json.dumps(W.kv_rows(by_num['07']['text']), ensure_ascii=False, separators=(',', ':')) + ';\n')
    chmap = {'%02d' % c['n']: {'slug': c['slug'], 'nav': c['nav']} for c in M.CHAPTERS}
    open(os.path.join(A, 'data-sources.js'), 'w', encoding='utf-8').write(
        'window.IA_CHAPTERS=' + json.dumps(chmap, ensure_ascii=False, separators=(',', ':')) + ';\nwindow.IA_SOURCES=' +
        json.dumps([{'u': s['url'], 'n': s['names'], 'c': s['chs'], 's': s['status']} for s in src_site], ensure_ascii=False, separators=(',', ':')) + ';\n')
    open(os.path.join(A, 'search-index.js'), 'w', encoding='utf-8').write(
        'window.IA_INDEX=' + json.dumps({'pages': index_pages, 'e': index_entries}, ensure_ascii=False, separators=(',', ':')) + ';\n')

    stats_out = {'pages': len(os.listdir(DIST)) - 1, 'tables': ctx.get('ntables'), 'numbered_tables': len(ctx['tables']),
                 'search_entries': len(index_entries), 'sources': stats['n_sources'], 'corrections': stats['n_corr'],
                 'matrix_counts': counts}
    os.makedirs(os.path.join(SITE, '.cache'), exist_ok=True)
    json.dump(stats_out, open(os.path.join(SITE, '.cache', 'build-stats.json'), 'w'), ensure_ascii=False, indent=1)
    print(json.dumps(stats_out, ensure_ascii=False))
    return stats_out


if __name__ == '__main__':
    main()
