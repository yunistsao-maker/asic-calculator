#!/usr/bin/env python3
"""shots.py <out_dir> <spec.json> — screenshots with Playwright. spec: [{url, name, w, h, theme, full, click:[selectors], wait}]"""
import json, os, sys, subprocess, time
from playwright.sync_api import sync_playwright
out, spec = sys.argv[1], json.load(open(sys.argv[2]))
os.makedirs(out, exist_ok=True)
BASE = 'http://127.0.0.1:8765/'
with sync_playwright() as p:
    b = p.chromium.launch()
    for s in spec:
        ctx = b.new_context(viewport={'width': s.get('w', 1440), 'height': s.get('h', 900)}, color_scheme=s.get('theme', 'light'), device_scale_factor=s.get('dpr', 1))
        page = ctx.new_page()
        errs = []
        page.on('console', lambda m: errs.append(m.text) if m.type == 'error' else None)
        page.on('pageerror', lambda e: errs.append('PAGEERROR ' + str(e)))
        page.goto(BASE + s['url'], wait_until='networkidle')
        for sel in s.get('click', []):
            page.click(sel)
            page.wait_for_timeout(150)
        for js in s.get('eval', []):
            page.evaluate(js)
            page.wait_for_timeout(150)
        page.wait_for_timeout(s.get('wait', 300))
        path = os.path.join(out, s['name'] + '.png')
        if s.get('clip'):
            page.screenshot(path=path, clip=s['clip'])
        else:
            page.screenshot(path=path, full_page=s.get('full', False))
        dims = page.evaluate('({sw: document.documentElement.scrollWidth, cw: document.documentElement.clientWidth, sh: document.documentElement.scrollHeight})')
        print(s['name'], dims, 'errors:', errs[:5])
        ctx.close()
    b.close()
