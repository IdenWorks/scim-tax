#!/usr/bin/env python3
"""Validate v3 summary rows and per-vendor deep research files.

Usage:
  python3 research/2026-09/validate.py vendors/            # every vendors/*.json deep file
  python3 research/2026-09/validate.py vendors/1password.json

merge.py imports validate(rows) for the v3 summary rows.
Rules: SCHEMA.md (rows) and DEEP_SCHEMA.md (deep files).
"""
import json, sys, os, re, glob
from urllib.parse import urlparse

STATUS = {'free', 'gated', 'partial', 'none', 'unknown'}
CONF = {'high', 'medium', 'low'}
IDP_KEYS = ['okta', 'entra', 'google', 'onelogin', 'jumpcloud']
IDP_VALS = {'native', 'via_generic', 'api_connector', 'directory_sync', 'third_party', 'sso_only', 'none', None}
KINDS = {'scim', 'api_connector', 'directory_sync', 'swa', 'sso_only', None}
BUILT = {'vendor', 'idp', 'third_party', None}
OPS = ['create', 'update', 'deactivate', 'delete', 'groups']
DATE = re.compile(r'^\d{4}-\d{2}-\d{2}$')
BANNED = ('stitchflow.com', 'sso.tax', 'notsosso.com', 'g2.com', 'capterra.com', 'vendr.com',
          'reddit.com', 'trustradius.com', 'getapp.com', 'softwareadvice.com', 'scimtax.org')
TRI = (True, False, None)


def _url(u):
    return isinstance(u, str) and re.match(r'^https?://', u)


def _num(x):
    return x is None or (isinstance(x, (int, float)) and not isinstance(x, bool) and x >= 0)


def validate_row(r):
    e = []
    who = r.get('slug') or r.get('vendor') or '?'
    err = lambda m: e.append(f'{who}: row: {m}')
    for k in ('vendor', 'slug', 'status', 'pricing_page_url'):
        if not r.get(k): err(f'missing {k}')
    if r.get('status') not in STATUS: err(f'bad status {r.get("status")!r}')
    if r.get('pricing_page_url') and not _url(r['pricing_page_url']): err('pricing_page_url not a URL')
    if r.get('docs_url') is not None and not _url(r['docs_url']): err('docs_url not a URL')
    if r.get('confidence') not in CONF: err(f'bad confidence {r.get("confidence")!r}')
    if not r.get('category'): err('missing category')
    if not r.get('evidence'): err('missing evidence')
    if r.get('status') in ('free', 'gated', 'partial') and r.get('scim_plan') in (None, '', '—'):
        err(f'status {r["status"]} needs scim_plan')
    for k in ('scim_price_per_user_mo', 'team_price_per_user_mo', 'sso_price_per_user_mo', 'price_multiplier', 'min_seats'):
        if not _num(r.get(k)): err(f'{k} must be a non-negative number or null')
    s, t, m = r.get('scim_price_per_user_mo'), r.get('team_price_per_user_mo'), r.get('price_multiplier')
    if s is not None and t not in (None, 0):
        if m is None or abs(m - round(s / t, 1)) > 0.11: err(f'price_multiplier {m} != {round(s / t, 1)}')
    elif m is not None:
        err('price_multiplier set but a price side is null')
    if r.get('last_verified') and not DATE.match(r['last_verified']): err('last_verified not ISO date')
    if r.get('status_prev') not in STATUS | {None}: err('bad status_prev')
    idp = r.get('idp') or {}
    for k in IDP_KEYS:
        if idp.get(k) not in IDP_VALS: err(f'idp.{k} bad value {idp.get(k)!r}')
    if idp.get('generic') not in TRI: err('idp.generic must be bool or null')
    if r.get('api_provisioning') not in TRI: err('api_provisioning must be bool or null')
    if r.get('user_api_available') not in (True, False, None, 'partner_only'): err('bad user_api_available')
    if r.get('api_tax') not in TRI: err('api_tax must be bool or null')
    ops = r.get('scim_ops')
    if ops is not None:
        for k in OPS:
            if ops.get(k) not in TRI: err(f'scim_ops.{k} must be bool or null')
    return e


def validate(rows):
    out = []
    for r in rows:
        out += validate_row(r)
    return out


def _cites_in(node, path, found):
    """Collect (path, cite list) pairs and flag facts that have values but no cite."""
    if isinstance(node, dict):
        if 'cite' in node:
            found.append((path, node['cite'], node))
        for k, v in node.items():
            if k != 'cite':
                _cites_in(v, f'{path}.{k}', found)
    elif isinstance(node, list):
        for i, v in enumerate(node):
            _cites_in(v, f'{path}[{i}]', found)


def _has_fact(node):
    for k, v in node.items():
        if k in ('cite', 'notes'):
            continue
        if isinstance(v, dict):
            if _has_fact(v): return True
        elif isinstance(v, list):
            if any(_has_fact(x) if isinstance(x, dict) else x not in (None, '') for x in v): return True
        elif v not in (None, ''):
            return True
    return False


def validate_deep(d, fname=''):
    e = []
    who = d.get('slug') or fname
    err = lambda m: e.append(f'{who}: {m}')
    for k in ('slug', 'vendor', 'researched_at', 'row', 'citations'):
        if k not in d: err(f'missing {k}')
    if fname and d.get('slug') and os.path.basename(fname) != d['slug'] + '.json':
        err('file name does not match slug')
    row = d.get('row') or {}
    e += validate_row(row)
    if row.get('slug') != d.get('slug'): err('row.slug != slug')

    cits = d.get('citations') or []
    ids = set()
    blocked_ids = set()
    urls = set()
    for c in cits:
        cid = c.get('id')
        if not cid or cid in ids: err(f'citation id missing or duplicate: {cid!r}')
        ids.add(cid)
        if not _url(c.get('url')): err(f'{cid}: bad url'); continue
        urls.add(c['url'].rstrip('/'))
        if _url(c.get('page_url')): urls.add(c['page_url'].rstrip('/'))  # human page behind a JSON/.md citation
        host = urlparse(c['url']).netloc.lower()
        own = urlparse(d.get('vendor_url') or '').netloc.lower().removeprefix('www.')  # e.g. G2 or Vendr researched as vendors
        if any((host == b or host.endswith('.' + b)) and not (own == b or own.endswith('.' + b)) for b in BANNED):
            err(f'{cid}: third-party source {host}')
        q = c.get('quote') or ''
        if c.get('blocked'):  # page refused every fetch; cited only so the row can name its pricing/docs URL
            blocked_ids.add(cid)
        elif not q.strip(): err(f'{cid}: empty quote')
        if len(q) > 320: err(f'{cid}: quote longer than 300 chars')
        if not DATE.match(c.get('accessed') or ''): err(f'{cid}: accessed not ISO date')
        if c.get('page_url') is not None and not _url(c['page_url']): err(f'{cid}: page_url not a URL')
    if not cits: err('no citations')

    for k in ('pricing_page_url', 'docs_url'):
        u = row.get(k)
        if u and u.rstrip('/') not in urls: err(f'row.{k} not in citations')

    found = []
    for sec in ('plans', 'scim', 'user_api', 'idp_apps', 'fallbacks', 'conflicts'):
        if sec in d:
            _cites_in(d[sec], sec, found)
    for path, cite, node in found:
        if not isinstance(cite, list): err(f'{path}.cite must be a list'); continue
        for c in cite:
            if c not in ids: err(f'{path}: unknown citation {c}')
            elif c in blocked_ids: err(f'{path}: cites {c}, which is a blocked page and backs no facts')
        if _has_fact(node) and not cite: err(f'{path}: has values but no cite')
    for i, ep in enumerate((d.get('user_api') or {}).get('endpoints') or []):
        if not ep.get('method') or not ep.get('path'): err(f'user_api.endpoints[{i}] needs method and path')
    for sec in ('scim', 'user_api', 'idp_apps', 'fallbacks'):
        if sec not in d: err(f'missing section {sec}')
    fb = d.get('fallbacks') or {}
    if 'saml_jit' in fb: err('fallbacks.saml_jit was renamed to jit + jit_protocol')
    if fb.get('jit_protocol') not in ('saml', 'oidc', 'both', None): err('bad fallbacks.jit_protocol')
    for k, x in (d.get('idp_apps') or {}).items():
        if not isinstance(x, dict): continue
        if x.get('kind') not in KINDS: err(f'idp_apps.{k}.kind bad value {x.get("kind")!r}')
        if x.get('built_by') not in BUILT: err(f'idp_apps.{k}.built_by bad value {x.get("built_by")!r}')
    if row.get('status') in ('none', 'unknown') and not d.get('searched'):
        err(f'status {row.get("status")} needs a non-empty searched list')
    if row.get('status') == 'none' and (d.get('scim') or {}).get('available') is True:
        err('status none but scim.available is true')
    return e


def main():
    target = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), 'vendors')
    files = sorted(glob.glob(os.path.join(target, '*.json'))) if os.path.isdir(target) else [target]
    total = 0
    for f in files:
        try:
            d = json.load(open(f))
        except Exception as ex:
            print(f'{f}: invalid JSON: {ex}'); total += 1; continue
        errs = validate_deep(d, f)
        total += len(errs)
        for x in errs:
            print(x)
    print(f'{len(files)} files, {total} errors')
    sys.exit(1 if total else 0)


if __name__ == '__main__':
    main()
