"""Build-time punctuation normalisation for chapters written with half-width punctuation (1, 4, 10).

Converts ( ) ; : , to full-width forms in running text. Never touches fenced code, inline code, Markdown links
(text and URL), straight double-quoted spans, ASCII-only 「…」 quotations, or table separator rows.
"""
import re

PROT = re.compile(
    r'```.*?```'                                             # fenced blocks
    r'|`[^`\n]+`'                                            # inline code
    r'|\[[^\]\n]*\]\((?:[^()\s]|\([^()\s]*\))+\)'            # links
    r'|"[^"\n]{1,400}"'                                      # straight double quotes
    r'|「[\x20-\x7e–—’‘“”…×÷≥≤≈·]{1,400}」'                    # ASCII-only quotations
    r'|^\|[-| :]+\|[ \t]*$',                                 # table separator rows
    re.S | re.M)

NUM = re.compile(r'(?<![A-Za-z0-9.])\d{1,3}(?:,\d{3})+(?![0-9])')
TIME = re.compile(r'(?<![A-Za-z0-9.:])\d{1,2}:\d{2}(?![0-9:])')
RATIO = re.compile(r'(?<![A-Za-z0-9.])\d+:1(?![0-9.])')
KEEP = re.compile(r're:Invent|re:Inforce|\b(?:max|min|ceil|floor)\([^()\n]*\)')


def _plain(s):
    hold = []

    def keep(m):
        hold.append(m.group(0))
        return '%d' % (len(hold) - 1)

    for rx in (KEEP, NUM, TIME, RATIO):
        s = rx.sub(keep, s)
    s = s.replace('(', '（').replace(')', '）').replace(';', '；')
    s = re.sub(r':(?![ /])', '：', s)
    s = re.sub(r',(?! )', '，', s)
    s = re.sub(r'(\d+)', lambda m: hold[int(m.group(1))], s)
    return s


def normalize(text):
    out, last = [], 0
    for m in PROT.finditer(text):
        out.append(_plain(text[last:m.start()]))
        out.append(m.group(0))
        last = m.end()
    out.append(_plain(text[last:]))
    return ''.join(out)


if __name__ == '__main__':
    import sys, difflib, random
    for ch in sys.argv[1:]:
        t = open(ch, encoding='utf-8').read()
        n = normalize(t)
        a, b = t.split('\n'), n.split('\n')
        changed = [(x, y) for x, y in zip(a, b) if x != y]
        print(ch, 'lines changed', len(changed), 'of', len(a))
        left = {c: n.count(c) for c in '();:,'}
        print('  half-width left in whole file (incl. protected):', left)
