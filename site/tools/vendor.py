#!/usr/bin/env python3
"""Copy the third-party web assets the site ships (IBM Plex woff2, KaTeX CSS and fonts) from tools/node_modules
into site/vendor/. Run once after `npm ci` in site/tools; build.py only reads site/vendor/."""
import os, re, shutil
SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
nm = os.path.join(SITE, 'tools', 'node_modules')
v = os.path.join(SITE, 'vendor')
if os.path.exists(v):
    shutil.rmtree(v)
os.makedirs(os.path.join(v, 'fonts'))
for pkg, weights in (('ibm-plex-sans', (400, 500, 600)), ('ibm-plex-sans-condensed', (500, 600, 700)), ('ibm-plex-mono', (400, 500, 600))):
    for w in weights:
        fn = '%s-latin-%d-normal.woff2' % (pkg, w)
        shutil.copy(os.path.join(nm, '@fontsource', pkg, 'files', fn), os.path.join(v, 'fonts', fn))
shutil.copy(os.path.join(nm, '@fontsource', 'ibm-plex-sans', 'LICENSE'), os.path.join(v, 'fonts', 'LICENSE-IBM-Plex.txt'))
kd = os.path.join(v, 'katex')
os.makedirs(os.path.join(kd, 'fonts'))
css = open(os.path.join(nm, 'katex', 'dist', 'katex.min.css'), encoding='utf-8').read()
css = re.sub(r',url\(fonts/[^)]+\.woff\) format\("woff"\),url\(fonts/[^)]+\.ttf\) format\("truetype"\)', '', css)
assert '.ttf' not in css and '.woff)' not in css
open(os.path.join(kd, 'katex.min.css'), 'w', encoding='utf-8').write(css)
for f in sorted(os.listdir(os.path.join(nm, 'katex', 'dist', 'fonts'))):
    if f.endswith('.woff2'):
        shutil.copy(os.path.join(nm, 'katex', 'dist', 'fonts', f), os.path.join(kd, 'fonts', f))
shutil.copy(os.path.join(nm, 'katex', 'LICENSE'), os.path.join(kd, 'LICENSE-KaTeX.txt'))
import json
ver = {p: json.load(open(os.path.join(nm, p, 'package.json')))['version'] for p in ('katex', '@fontsource/ibm-plex-sans', '@fontsource/ibm-plex-sans-condensed', '@fontsource/ibm-plex-mono')}
json.dump(ver, open(os.path.join(v, 'VERSIONS.json'), 'w'), indent=1)
print('vendored', sum(len(fs) for _, _, fs in os.walk(v)), 'files', ver)
