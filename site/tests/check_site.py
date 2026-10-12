#!/usr/bin/env python3
"""Static checks on site/dist:
1. content preservation: every number of every chapter appears on its page the same number of times;
2. every source link of every chapter is on its page;
3. every internal link and anchor resolves; ids are unique;
4. no leftover Markdown syntax in the rendered text."""
import collections, glob, os, re, sys
from bs4 import BeautifulSoup
from markdown_it import MarkdownIt
SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, SITE); sys.path.insert(0, SITE + '/lib')
import meta as M
from normalize import normalize
DIST = SITE + '/dist'
MD = MarkdownIt('commonmark', {'html': False}).enable('table')
NUM = re.compile(r'\d[\d,]*(?:\.\d+)?')
fail = 0

def nums(text):
    return collections.Counter(NUM.findall(text))

def source_view(path, norm):
    t = open(path, encoding='utf-8').read()
    if norm:
        t = normalize(t)
    t = re.split(r'^## 網站呈現建議', t, flags=re.M)[0]
    t = '\n'.join(t.split('\n')[1:])          # drop the H1
    html = MD.render(t)
    s = BeautifulSoup(html, 'html.parser')
    for pre in s.find_all('pre'):
        pre.decompose()
    links = collections.Counter(a['href'] for a in s.find_all('a'))
    return s.get_text(' '), links

pages = {}
for f in sorted(glob.glob(DIST + '/*.html')):
    pages[os.path.basename(f)] = BeautifulSoup(open(f, encoding='utf-8').read(), 'html.parser')

# ---- 1 + 2
for c in M.CHAPTERS:
    src_text, src_links = source_view(os.path.join(os.path.dirname(SITE), 'chapters', c['src']), c.get('norm'))
    page = pages[c['slug'] + '.html']
    main = page.find('main')
    parts, links = [], collections.Counter()
    for h2 in main.select('.panel-head h2'):
        parts.append(h2.get_text(' '))
    seen = set()
    for pr in main.select('.prose'):
        if any(id(p) in seen for p in pr.parents):
            continue
        seen.add(id(pr))
        clone = BeautifulSoup(str(pr), 'html.parser')
        for x in clone.select('.formula, .ph'):
            x.decompose()
        parts.append(clone.get_text(' '))
        for a in clone.find_all('a'):
            if a.get('href', '').startswith('http'):
                links[a['href']] += 1
    page_text = ' '.join(parts)
    a, b = nums(src_text), nums(page_text)
    # the custom chapter-7 plan renders one section title twice (two tabs) and renames it
    diff = {k: (a[k], b[k]) for k in set(a) | set(b) if a[k] != b[k]}
    miss_links = {k: (src_links[k], links[k]) for k in src_links if src_links[k] != links[k]}
    extra_links = [k for k in links if k not in src_links]
    status = 'OK ' if not diff and not miss_links and not extra_links else 'DIFF'
    print('%s ch%02d numbers %d (distinct %d) links %d | number diffs %d, link diffs %d, extra links %d' % (
        status, c['n'], sum(a.values()), len(a), sum(src_links.values()), len(diff), len(miss_links), len(extra_links)))
    for k, v in sorted(diff.items())[:12]:
        print('     number %r: source %d, page %d' % (k, v[0], v[1]))
    for k, v in list(miss_links.items())[:5]:
        print('     link %s: source %d, page %d' % (k[:90], v[0], v[1]))
    if diff or miss_links or extra_links:
        fail += 1

# ---- 3
ids = {name: collections.Counter(el['id'] for el in soup.find_all(id=True)) for name, soup in pages.items()}
for name, cnt in ids.items():
    dup = [k for k, v in cnt.items() if v > 1]
    if dup:
        fail += 1
        print('DUPLICATE IDS', name, dup[:10])
bad = 0
for name, soup in pages.items():
    for a in soup.find_all('a', href=True):
        h = a['href']
        if h.startswith(('http://', 'https://', 'mailto:')):
            continue
        f, _, frag = h.partition('#')
        f = f.split('?')[0] or name
        if f not in pages:
            bad += 1; print('BROKEN LINK', name, h)
        elif frag and frag.split('?')[0] not in ids[f]:
            bad += 1; print('BROKEN ANCHOR', name, h)
    for el in soup.find_all(attrs={'aria-controls': True}):
        if el['aria-controls'] not in ids[name]:
            bad += 1; print('BROKEN aria-controls', name, el['aria-controls'])
    for el in soup.find_all(['script', 'link']):
        ref = el.get('src') or (el.get('href') if el.name == 'link' else None)
        if ref and not ref.startswith('http') and not os.path.exists(os.path.join(DIST, ref)):
            bad += 1; print('MISSING ASSET', name, ref)
print('internal links/anchors/assets broken:', bad)
fail += bad

# ---- 4
for name, soup in pages.items():
    # the correction log quotes chapter source text (before / after), which legitimately holds Markdown
    main = BeautifulSoup(str(soup.find('main')), 'html.parser')
    for x in main.select('.diff'):
        x.decompose()
    txt = main.get_text(' ')
    left = re.findall(r'.{0,30}(?:\*\*|\]\(http|```|^\s*#{1,4} |\{\{).{0,30}', txt, flags=re.M)
    if left:
        fail += 1
        print('LEFTOVER MARKDOWN', name, left[:4])
print('RESULT:', 'PASS' if not fail else 'FAIL (%d)' % fail)
sys.exit(1 if fail else 0)
