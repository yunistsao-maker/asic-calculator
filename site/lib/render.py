"""Markdown -> enhanced HTML for the Inference ASIC Atlas site.

Everything here is deterministic and content-preserving: the text of the chapters is never rewritten, only
decorated (grade badges, status chips, table wrappers, cross-reference links, formula rendering).
"""
import hashlib
import json
import os
import re
import subprocess

from bs4 import BeautifulSoup, NavigableString, Tag
from markdown_it import MarkdownIt

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.dirname(HERE)
MD = MarkdownIt('commonmark', {'html': False}).enable('table')

GRADE_NAMES = {
    'A': '獨立第三方量測',
    'B': '廠商或夥伴公布，且揭露方法',
    'C': '廠商宣稱或規格，未揭露方法',
    'D': '本文推算，附算式',
}

# status vocabulary -> chip class. Applied only at the start of a table cell.
CHIP_WORDS = [
    ('查無公開資料', 'na'), ('不支援', 'no'), ('不可行', 'no'), ('有條件', 'part'), ('僅權重', 'part'),
    ('支援', 'yes'), ('正式', 'yes'), ('可行', 'yes'), ('有效', 'yes'),
    ('部分', 'part'), ('Beta', 'part'), ('實驗', 'exp'), ('失效', 'fail'), ('查無', 'na'), ('中性', 'na'),
    ('不能', 'no'), ('能', 'yes'),
]
CHIP_DELIM = '（(；;，,：:。 †['
RATE = {'高': 5, '中高': 4, '中': 3, '中低': 2, '低': 1}
MUTED = {'無', '查無', '查無公開資料', '未揭露', '未公布', '未載明', '未列', '不適用', '無牌價', '同上', '無資料列',
         '否', '–', '—', '未見於來源', '未上架', '無端點', '無公布值', '未提供', '不公開'}

_cjk = re.compile(r'[⺀-鿿豈-﫿＀-￯]')


def dw(s):
    """display width: CJK counts 2."""
    return sum(2 if _cjk.match(c) else 1 for c in s)


# ---------------------------------------------------------------- KaTeX
_katex_cache = None
_KCACHE = os.path.join(SITE, 'katex-cache.json')   # rendered formulas; node is only needed when a formula is new


def katex_many(tex_list):
    global _katex_cache
    if _katex_cache is None:
        _katex_cache = json.load(open(_KCACHE, encoding='utf-8')) if os.path.exists(_KCACHE) else {}
    todo = [t for t in dict.fromkeys(tex_list) if t not in _katex_cache]
    if todo:
        r = subprocess.run(['node', 'tools/katex_render.js'], input=json.dumps(todo), capture_output=True,
                           text=True, cwd=SITE, check=True)
        out = json.loads(r.stdout)
        for t, h in zip(todo, out):
            if h.startswith('ERROR'):
                raise SystemExit('KaTeX failed: %s -> %s' % (t, h))
            _katex_cache[t] = h
        os.makedirs(os.path.dirname(_KCACHE), exist_ok=True)
        json.dump(_katex_cache, open(_KCACHE, 'w', encoding='utf-8'), ensure_ascii=False)
    return [_katex_cache[t] for t in tex_list]


# ---------------------------------------------------------------- helpers
def new(soup, name, cls=None, text=None, **attrs):
    t = soup.new_tag(name)
    if cls:
        t['class'] = cls.split()
    for k, v in attrs.items():
        t[k.rstrip('_').replace('_', '-')] = v
    if text is not None:
        t.string = text
    return t


def badge(soup, letter):
    return new(soup, 'span', 'g g-' + letter.lower(), letter, title='等級 %s：%s' % (letter, GRADE_NAMES[letter]))


SKIP_PARENTS = {'a', 'code', 'pre', 'script', 'style', 'math', 'svg', 'button'}


def text_nodes(root):
    for n in list(root.descendants):
        if isinstance(n, NavigableString):
            p = n.parent
            skip = False
            while p is not None and p is not root.parent:
                if getattr(p, 'name', None) in SKIP_PARENTS or 'katex' in (p.get('class') or []) \
                        or 'g' in (p.get('class') or []) or 'chip' in (p.get('class') or []):
                    skip = True
                    break
                p = p.parent
            if not skip and str(n).strip():
                yield n


GRADE_RX = re.compile(
    r'\[(?P<a>[ABCD])\]'
    r'|\[(?P<b1>[ABCD]) / (?P<b2>[ABCD])\]'
    r'|\[(?P<c>[ABCD])(?=[，,；;：:、/ ][^\[\]]{0,90}\])'
    r'|[（(](?P<d>[ABCD])[）)]'
    r'|(?P<eo>[（(])(?P<e>[ABCD])(?=[：:；;，,、])'
    r'|等級(?P<fs> ?)(?P<f>[ABCD])(?![A-Za-z0-9])'
    r'|(?P<h0>[，,；;、]\s?)(?P<h>[ABCD])(?=[）)])'
)
LEGEND_RX = re.compile(r'(?:(?<=[：:；;])|^)\s?(?P<l>[ABCD])(?=\s?(?:=|[一-鿿]))')
XREF_RX = re.compile(r'第 (?P<ch>\d{1,2}) 章|表 (?P<tc>\d{1,2})-(?P<tn>\d{1,2})')


def _replace_text(soup, node, rx, make):
    s = str(node)
    out, last, hit = [], 0, False
    for m in rx.finditer(s):
        rep = make(m)
        if rep is None:
            continue
        hit = True
        if m.start() > last:
            out.append(NavigableString(s[last:m.start()]))
        out.extend(rep)
        last = m.end()
    if not hit:
        return
    if last < len(s):
        out.append(NavigableString(s[last:]))
    for x in out:
        node.insert_before(x)
    node.extract()


def add_grade_badges(soup, root, legend=False):
    def make(m):
        g = m.groupdict()
        if g['a']:
            return [badge(soup, g['a'])]
        if g['b1']:
            return [badge(soup, g['b1']), NavigableString(' '), badge(soup, g['b2'])]
        if g['c']:
            return [NavigableString('['), badge(soup, g['c'])]
        if g['d']:
            return [badge(soup, g['d'])]
        if g['e']:
            return [NavigableString(g['eo']), badge(soup, g['e'])]
        if g['f']:
            return [NavigableString('等級 '), badge(soup, g['f'])]
        if g['h']:
            return [NavigableString(g['h0']), badge(soup, g['h'])]
        return None

    for n in list(text_nodes(root)):
        _replace_text(soup, n, GRADE_RX, make)
    # bold single grade letters (legends)
    for st in root.find_all('strong'):
        if st.get_text() in GRADE_NAMES and not st.find_parent('a'):
            st.replace_with(badge(soup, st.get_text()))
    if legend:
        for n in list(text_nodes(root)):
            _replace_text(soup, n, LEGEND_RX, lambda m: [badge(soup, m.group('l')), NavigableString(' ')])


def grade_cells(soup, td):
    """In a 等級 column: badge every standalone A/B/C/D before the first link."""
    rx = re.compile(r'(?<![A-Za-z0-9./])([ABCD])(?![A-Za-z0-9.])')
    for n in list(text_nodes(td)):
        _replace_text(soup, n, rx, lambda m: [badge(soup, m.group(1))])


# ---------------------------------------------------------------- tables
def _cell_text(c):
    return re.sub(r'\s+', ' ', c.get_text(' ', strip=True))


def _numeric(t):
    """A cell that is a number (or a few numbers) with at most a short unit: set in the mono face."""
    if not t or len(t) > 30:
        return False
    if not re.match(r'^(?:[≈約~<>≤≥+−–\-$]|n = )?\s?\$?\d', t):
        return False
    rest = re.sub(r'[\d\s.,/；;×%$≈約~<>≤≥+−–\-:：()（）†*=]', '', t)
    return len(re.findall(r'[一-鿿]', rest)) <= 3 and len(re.findall(r'[A-Za-zµ]', rest)) <= 12


def chipify(soup, td):
    first = None
    for ch in td.children:
        if isinstance(ch, NavigableString) and not str(ch).strip():
            continue
        first = ch
        break
    if first is None:
        return False
    word, cls, rest_node, rest = None, None, None, ''
    if isinstance(first, Tag) and first.name == 'strong':
        w = first.get_text().strip()
        for cw, cc in CHIP_WORDS:
            if w == cw:
                word, cls = cw, cc
                break
        if word is None:
            return False
        nxt = first.next_sibling
        if isinstance(nxt, NavigableString):
            rest_node, rest = nxt, str(nxt)
        elif nxt is not None:
            rest_node, rest = None, ''
        if rest and rest[0] not in CHIP_DELIM:
            return False
        chip = new(soup, 'span', 'chip chip-' + cls, word)
        first.replace_with(chip)
    elif isinstance(first, NavigableString):
        s = str(first).lstrip()
        for cw, cc in CHIP_WORDS:
            if s.startswith(cw) and (len(s) == len(cw) or s[len(cw)] in CHIP_DELIM):
                word, cls = cw, cc
                break
        if word is None:
            return False
        chip = new(soup, 'span', 'chip chip-' + cls, word)
        rest = s[len(word):]
        rest_node = NavigableString(rest)
        first.replace_with(chip)
        chip.insert_after(rest_node)
    else:
        return False
    # tidy what follows the chip
    if rest_node is not None:
        r = str(rest_node)
        if r.startswith(('：', ':')):
            r = r[1:].lstrip()
            rest_node.replace_with(NavigableString(' ' + r))
        elif r.startswith('†'):
            pass
        else:
            m = re.fullmatch(r'\s*[（(]([^（）()]*)[）)]\s*', r)
            if m and rest_node.next_sibling is None:
                note = new(soup, 'span', 'chip-note', m.group(1))
                rest_node.replace_with(note)
            else:
                rest_node.replace_with(NavigableString(' ' + r.lstrip() if r[:1] not in '（(†' else r))
    return True


def enhance_tables(soup, root, ctx):
    for table in root.find_all('table'):
        fig = new(soup, 'figure', 'tbl')
        table.insert_before(fig)
        # caption: previous <p> that starts with <strong>表 N-M
        prev = fig.previous_sibling
        while isinstance(prev, NavigableString) and not str(prev).strip():
            prev = prev.previous_sibling
        tid = None
        if isinstance(prev, Tag) and prev.name == 'p':
            st = prev.find('strong')
            m = st and prev.contents and prev.contents[0] is st and re.match(r'表 (\d{1,2})-(\d{1,2})', st.get_text())
            if m:
                tid = 't%d-%d' % (int(m.group(1)), int(m.group(2)))
                cap = new(soup, 'figcaption')
                for c in list(prev.contents):
                    cap.append(c.extract())
                prev.decompose()
                fig.append(cap)
        ctx['ntables'] = ctx.get('ntables', 0) + 1
        if tid:
            fig['id'] = tid
            ctx.setdefault('tables', {})[tid] = True
        scroll = new(soup, 'div', 'tbl-scroll', tabindex='0', role='region',
                     aria_label=(fig.figcaption.strong.get_text() if fig.figcaption and fig.figcaption.strong else '資料表'))
        fig.append(scroll)
        scroll.append(table.extract())

        head = table.find('thead')
        hcells = head.find_all('th') if head else []
        for th in hcells:
            th['scope'] = 'col'
        rows = table.find('tbody').find_all('tr') if table.find('tbody') else []
        ncol = len(hcells)
        fig['data-rows'] = str(len(rows))
        fig['data-cols'] = str(ncol)
        cols = [[] for _ in range(ncol)]
        for tr in rows:
            for i, td in enumerate(tr.find_all('td')):
                if i < ncol:
                    cols[i].append(td)
        htext = [_cell_text(h) for h in hcells]
        # status chips: only in matrix-like tables (>= 2 cells start with a vocabulary word)
        cand = 0
        for tr in rows:
            for td in tr.find_all('td'):
                t = td.get_text().strip()
                if any(t.startswith(w) and (len(t) == len(w) or t[len(w)] in CHIP_DELIM) for w, _ in CHIP_WORDS):
                    cand += 1
        rate_cells = sum(1 for tr in rows for td in tr.find_all('td')
                         if td.contents and isinstance(td.contents[0], Tag) and td.contents[0].name == 'strong'
                         and td.contents[0].get_text() in RATE)
        for i, col in enumerate(cols):
            h = htext[i] if i < len(htext) else ''
            texts = [_cell_text(td) for td in col]
            widths = [dw(t) for t in texts] or [0]
            avg = sum(widths) / len(widths)
            mx = max(widths)
            wcls = 'w4' if avg > 150 else 'w3' if avg > 70 else 'w2' if avg > 26 or mx > 60 else 'w1' if avg > 12 else ''
            is_src = '來源' in h and '等級' not in h and '（等級' not in h
            if is_src and all(td.find('a') or not _cell_text(td) or _cell_text(td) in MUTED for td in col):
                wcls = 'src'
            if wcls and i < len(hcells):
                hcells[i]['class'] = hcells[i].get('class', []) + [wcls]
            is_grade = '等級' in h
            for td, t in zip(col, texts):
                cls = td.get('class', [])
                if wcls == 'src':
                    cls.append('src')
                if t in MUTED:
                    cls.append('muted')
                elif t in ('優', '缺'):
                    td.string = ''
                    td.append(new(soup, 'span', 'pc pc-' + ('pro' if t == '優' else 'con'), t))
                elif _numeric(t):
                    cls.append('num')
                if is_grade:
                    grade_cells(soup, td)
                if cand >= 2 and i > 0:
                    chipify(soup, td)
                if rate_cells >= 6 and td.contents and isinstance(td.contents[0], Tag) \
                        and td.contents[0].name == 'strong' and td.contents[0].get_text() in RATE:
                    w = td.contents[0].get_text()
                    rs = new(soup, 'span', 'rate rate-%d' % RATE[w], w)
                    td.contents[0].replace_with(rs)
                    nx = rs.next_sibling
                    if isinstance(nx, NavigableString):
                        s2 = str(nx)
                        m2 = re.match(r'^(\s*†)?\s*[：:]\s*', s2)
                        if m2:
                            nx.replace_with(NavigableString((' †' if m2.group(1) else '') + ' ' + s2[m2.end():]))
                if i == 0 and not td.find(['a', 'code', 'strong', 'span']):
                    m = re.fullmatch(r'([^（()）]{2,40})（([^（）]{2,120})）', t)
                    if m and len(td.contents) == 1:
                        td.clear()
                        td.append(new(soup, 'span', 'rh', m.group(1).strip()))
                        sub_ = new(soup, 'span', 'rh-sub')
                        sub_.append(new(soup, 'span', 'vh', '（'))
                        sub_.append(NavigableString(m.group(2).strip()))
                        sub_.append(new(soup, 'span', 'vh', '）'))
                        td.append(sub_)
                    elif dw(t) <= 44:
                        cls.append('rowhead')
                elif i == 0 and dw(t) <= 44 and not td.find('a'):
                    cls.append('rowhead')
                if cls:
                    td['class'] = cls


# ---------------------------------------------------------------- main entry
def render_md(text, ctx, legend=False):
    """text: Markdown. Returns a BeautifulSoup fragment (not yet cross-linked)."""
    html = MD.render(text)
    soup = BeautifulSoup(html, 'html.parser')
    # formulas
    pres = [p for p in soup.find_all('pre') if p.code and 'language-latex' in (p.code.get('class') or [])]
    if pres:
        rendered = katex_many([p.code.get_text().strip() for p in pres])
        for p, h in zip(pres, rendered):
            div = new(soup, 'div', 'formula')
            div.append(BeautifulSoup(h, 'html.parser'))
            p.replace_with(div)
    enhance_tables(soup, soup, ctx)
    add_grade_badges(soup, soup, legend=legend)
    # links
    for a in soup.find_all('a'):
        href = a.get('href', '')
        if href.startswith('http'):
            a['target'] = '_blank'
            a['rel'] = 'noopener'
            ctx.setdefault('links', []).append((href, a.get_text()))
            if href in ctx.get('unreadable', ()):
                a['class'] = a.get('class', []) + ['unread']
                a['title'] = '查核時無法重讀此頁；所引內容另有其他來源佐證'
    return soup


def crosslink(soup, root, ctx, page_slug):
    """第 N 章 and 表 N-M become links. ctx['chapters'][n] = slug, ctx['table_page'][tid] = slug."""
    def make(m):
        g = m.groupdict()
        if g['ch']:
            n = int(g['ch'])
            slug = ctx['chapters'].get(n)
            if not slug or slug == page_slug:
                return None
            return [new(soup, 'a', 'xref', m.group(0), href=slug + '.html')]
        tid = 't%d-%d' % (int(g['tc']), int(g['tn']))
        slug = ctx['table_page'].get(tid)
        if not slug:
            return None
        href = ('#' + tid) if slug == page_slug else slug + '.html#' + tid
        return [new(soup, 'a', 'xref', m.group(0), href=href)]

    for n in list(text_nodes(root)):
        # never link a caption's own number
        p = n.parent
        if p is not None and p.name == 'strong' and p.find_parent('figcaption') is not None:
            continue
        _replace_text(soup, n, XREF_RX, make)


def plain_blocks(root):
    """Yield (element, kind, text) for search indexing."""
    for el in root.find_all(['p', 'li', 'tr', 'figcaption', 'h3', 'h4']):
        if el.name == 'tr' and el.find_parent('thead') is not None:
            continue
        if el.name == 'p' and el.find_parent(['li', 'td', 'figcaption']) is not None:
            continue
        if el.name == 'li' and el.find('li') is not None:
            # index only own text of a parent list item
            txt = ' '.join(str(c) for c in el.find_all(string=True, recursive=False)).strip()
            if not txt:
                continue
        if el.name == 'tr':
            txt = ' | '.join(_cell_text(c) for c in el.find_all(['td', 'th']))
        else:
            txt = _cell_text(el)
        if len(txt) < 2:
            continue
        yield el, {'tr': 'r', 'figcaption': 'c', 'h3': 'h', 'h4': 'h'}.get(el.name, 'p'), txt
