#!/usr/bin/env python3
"""Re-fetch every cited page and check the quote is on it.

Usage: python3 research/2026-09/check_quotes.py [vendors/ or vendors/x.json] [--json out.json] [--browser]

--browser re-loads, in headless Chrome, pages the plain fetch could not read or where a quote was not found (tools/render.cjs, no visible window).

Per citation: found (quote text is on the fetched page), missing (page loaded, quote not on it),
unreachable (fetch failed or page is a JS shell), found_in_data (only in embedded JSON / script data,
e.g. a JS-rendered pricing table). Matching ignores case, whitespace, HTML tags,
quote and dash styles, and accepts a match on 80% of the quote's 8-word windows.
"""
import json, sys, os, re, glob, gzip, zlib, html, subprocess, tempfile, urllib.request, concurrent.futures as cf
RENDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tools', 'render.cjs')

UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0 Safari/537.36'
_cache = {}
_data = {}


def norm(s, keep_scripts=False):
    if keep_scripts:
        s = s.replace('\\u0026', '&').replace('\\u003c', '<').replace('\\u003e', '>').replace('\\"', '"').replace('\\n', ' ').replace('\\/', '/')
        s = re.sub(r'<style.*?</style>', ' ', s, flags=re.S | re.I)
    else:
        s = re.sub(r'<script.*?</script>|<style.*?</style>', ' ', s, flags=re.S | re.I)
    s = html.unescape(s)
    s = re.sub(r'<[^>]+>', ' ', s)
    s = s.replace('’', "'").replace('‘', "'").replace('“', '"').replace('”', '"')
    s = s.replace('–', '-').replace('—', '-').replace(' ', ' ')
    s = re.sub(r'[^\w\s$%/{}.:-]', ' ', s)          # drop markdown, pilcrows, quotes, brackets
    s = re.sub(r'(?<!\w)[.:-]|[.:-](?!\w)', ' ', s)  # punctuation not inside a word, URL or price
    return re.sub(r'\s+', ' ', s).strip().lower()


def fetch(url):
    if url in _cache:
        return _cache[url]
    try:
        req = urllib.request.Request(url, headers={'User-Agent': UA, 'Accept': 'text/html,application/json,*/*'})
        with urllib.request.urlopen(req, timeout=25) as r:
            raw = r.read(12_000_000)
        if raw[:2] == b'\x1f\x8b':
            raw = gzip.decompress(raw)
        elif raw[:1] == b'\x78':
            try: raw = zlib.decompress(raw)
            except zlib.error: pass
        if raw[:4] == b'%PDF':  # vendor PDF guides: extract text with pdftotext
            try:
                body = subprocess.run(['pdftotext', '-layout', '-', '-'], input=raw, capture_output=True, timeout=60).stdout.decode('utf-8', 'replace')
            except Exception:
                body = ''
        else:
            body = raw.decode('utf-8', 'replace')
        text = norm(body)
        if len(text) <= 400:
            raise ValueError('short or undecodable body (e.g. brotli)')  # fall through to curl
        _cache[url] = text
        _data[url] = norm(body, keep_scripts=True)
    except Exception:
        _cache[url] = None
        try:  # Python TLS can't verify some new chains (Let's Encrypt YR2); curl uses the macOS trust store
            jar = tempfile.mktemp(prefix='cq-cj-')  # cookie jar: some docs sites loop redirects without cookies
            raw = subprocess.run(['curl', '-sL', '--compressed', '--max-time', '30', '-c', jar, '-b', jar, '-A', UA, url],
                                 capture_output=True, timeout=40).stdout
            if raw[:4] == b'%PDF':
                raw = subprocess.run(['pdftotext', '-layout', '-', '-'], input=raw, capture_output=True, timeout=60).stdout
            body = raw.decode('utf-8', 'replace')
            text = norm(body)
            if len(text) > 400:
                _cache[url] = text
                _data[url] = norm(body, keep_scripts=True)
        except Exception:
            pass
    return _cache[url]


def browser_fetch(url):
    tmp = tempfile.mkdtemp(prefix='cq-')
    out = os.path.join(tmp, 'p')
    try:
        subprocess.run(['node', RENDER, url, out], capture_output=True, timeout=120)
        text = open(out + '.txt', encoding='utf-8', errors='replace').read()
        body = open(out + '.html', encoding='utf-8', errors='replace').read()
    except Exception:
        return
    if len(text) > 200:
        _cache[url] = norm(text)
        _data[url] = norm(body, keep_scripts=True)


def matches(quote, page):
    q = norm(quote)
    if q in page or q.replace(' ', '') in page.replace(' ', ''):
        return True
    words = q.split()
    if len(words) < 8:
        return False
    wins = [' '.join(words[i:i + 8]) for i in range(0, len(words) - 7)]
    return sum(w in page for w in wins) / len(wins) >= 0.8


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    out = sys.argv[sys.argv.index('--json') + 1] if '--json' in sys.argv else None
    if out in args: args.remove(out)
    target = args[0] if args else os.path.join(os.path.dirname(os.path.abspath(__file__)), 'vendors')
    files = sorted(glob.glob(os.path.join(target, '*.json'))) if os.path.isdir(target) else [target]
    jobs = []
    for f in files:
        d = json.load(open(f))
        for c in d.get('citations', []):
            jobs.append((d['slug'], c))
    with cf.ThreadPoolExecutor(12) as ex:
        list(ex.map(fetch, {c['url'] for _, c in jobs}))
    if '--browser' in sys.argv:
        def _plain(url):  # some sites serve text only to a plain (non-browser) client; still an honest UA, never a crawler
            try:
                raw = subprocess.run(['curl', '-sL', '--compressed', '--max-time', '30', '-A', 'Mozilla/5.0', url],
                                     capture_output=True, timeout=40).stdout
                body = raw.decode('utf-8', 'replace')
                if len(norm(body)) > 400:
                    _cache[url] = norm(body); _data[url] = norm(body, keep_scripts=True)
            except Exception:
                pass
        def _ok(c):
            pg, dt = _cache.get(c['url']), _data.get(c['url'])
            return (pg is not None and matches(c.get('quote', ''), pg)) or (dt and matches(c.get('quote', ''), dt))
        retry = sorted({c['url'] for _, c in jobs if not _ok(c)})   # unreachable, or JS fills the text in
        with cf.ThreadPoolExecutor(4) as ex:
            list(ex.map(browser_fetch, retry))
        retry2 = sorted({c['url'] for _, c in jobs if not _ok(c)})
        with cf.ThreadPoolExecutor(6) as ex:
            list(ex.map(_plain, retry2))
    report = {}
    for slug, c in jobs:
        page, data = _cache.get(c['url']), _data.get(c['url'])
        q = c.get('quote', '')
        if c.get('blocked'): res = 'blocked'
        elif page is not None and matches(q, page): res = 'found'
        elif data and matches(q, data): res = 'found_in_data'
        elif page is None and not data: res = 'unreachable'
        elif c.get('interaction'): res = 'needs_interaction'   # quote only shows after a click (tab, toggle)
        elif page is None: res = 'unreachable'
        else: res = 'missing'
        report.setdefault(slug, []).append({'id': c['id'], 'url': c['url'], 'result': res})
    tot = {'found': 0, 'found_in_data': 0, 'needs_interaction': 0, 'blocked': 0, 'missing': 0, 'unreachable': 0}
    for slug, rows in report.items():
        t = {k: sum(r['result'] == k for r in rows) for k in tot}
        for k in tot: tot[k] += t[k]
        print(f"{slug:28} found {t['found']:3}  in_data {t['found_in_data']:3}  click {t['needs_interaction']:3}  missing {t['missing']:3}  unreachable {t['unreachable']:3}")
        for r in rows:
            if r['result'] == 'missing':
                print(f"    MISSING {r['id']} {r['url']}")
    print('total', tot)
    if out:
        json.dump(report, open(out, 'w'), indent=1)


if __name__ == '__main__':
    main()
