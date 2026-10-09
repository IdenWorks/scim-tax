#!/usr/bin/env python3
"""Apply the 2026-09 refresh to data.json, keeping the published v3 schema unchanged.

Usage: python3 research/2026-09/apply_merge.py [--dry-run]

Reads vendors/*.json (one research file per vendor) and run/MERGE_PLAN.json, then:
  1. applies the mechanical clean-ups and the rule fixes from the plan
  2. renames dotted slugs, drops discontinued vendors, folds duplicates into one row
  3. trims every row to the v3 field list in SCHEMA.md (the deep SCIM and API detail stays
     in vendors/*.json, documented in DEEP_SCHEMA.md)
  4. maps IdP values outside the v3 enum to null
  5. sets status_prev and first_added from the June 2026 release (commit e6436da), and writes data.json

Open methodology decisions in the plan (quote-only single plans, single-IdP SCIM, scope
exclusions, possible merges) are NOT applied: those rows keep their researched status.
"""
import json, glob, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, HERE)

FIELDS = ['vendor', 'slug', 'category', 'status', 'scim_plan', 'scim_price_text', 'scim_price_per_user_mo', 'team_plan',
          'team_price_text', 'team_price_per_user_mo', 'price_multiplier', 'sso_plan', 'sso_price_per_user_mo',
          'sso_required_for_scim', 'scim_addon_price_text', 'min_seats', 'scim_ops', 'idp', 'pricing_page_url', 'docs_url',
          'evidence', 'notes', 'confidence', 'last_verified', 'first_added', 'status_prev']
IDP_KEYS = ['okta', 'entra', 'google', 'onelogin', 'jumpcloud', 'generic']
IDP_ENUM = {'native', 'via_generic', 'sso_only', 'none', None}
RELEASE = '2026-09'
LAST_UPDATED = '2026-10'

dry = '--dry-run' in sys.argv
plan = json.load(open(os.path.join(HERE, 'run', 'MERGE_PLAN.json')))
# The June 2026 release, read from git so a re-run never treats its own output as the baseline.
JUNE_COMMIT = 'e6436da'
june_doc = json.loads(subprocess.check_output(['git', '-C', ROOT, 'show', f'{JUNE_COMMIT}:data.json']))
assert june_doc['last_updated'] == '2026-06', 'baseline is not the June 2026 release'
june = {v['slug']: v for v in june_doc['vendors']}

rows = {}
for f in sorted(glob.glob(os.path.join(HERE, 'vendors', '*.json'))):
    d = json.load(open(f))
    rows[d['slug']] = dict(d['row'])

log = {'mechanical': 0, 'rule_fixes': [], 'renamed': [], 'dropped': [], 'idp_mapped_to_null': 0}

rename = {x['from']: x['to'] for x in plan.get('slug_renames', [])}
def find(slug):  # plan entries may use the pre-rename (dotted) slug
    return rows.get(slug) or rows.get(rename.get(slug, slug))

# 1. mechanical clean-ups and rule fixes
for m in plan['mechanical']:
    r = find(m['slug'])
    field = m['field'].replace('row.', '')
    if r is None or field not in FIELDS:
        continue  # fields outside v3 (the API flags) live only in the research files
    r[field] = m['to']
    log['mechanical'] += 1
# Fixes in the plan that a re-read showed to be wrong, with the reason.
SKIP_FIXES = {
    'five9': 'publishes Digital and Core prices, so it is not quote-only; SCIM is in controlled availability '
             'with no plan named, which is unknown under rule 1a (the researched status)',
}
for fx in plan['rule_fixes']:
    r = find(fx['slug'])
    if r is None or fx['slug'] in SKIP_FIXES:
        continue
    r['status'] = fx['to']
    if fx['to'] == 'unknown':
        r['scim_price_per_user_mo'] = None
        r['price_multiplier'] = None
        r['confidence'] = 'low'
    if fx['to'] == 'gated' and 'rule 6a' in fx['why']:
        r['confidence'] = 'low'
        if not r['notes'].startswith('Quote-only'):
            r['notes'] = 'Quote-only: ' + r['notes']
    log['rule_fixes'].append((fx['slug'], fx['from'], fx['to']))

# 2. slugs, removals, duplicates
drop = set(plan['remove']['discontinued'])
# Duplicates found after the plan was written: (kept slug, dropped slug, reason)
EXTRA_MERGES = [
    ('athenahealth', 'athenaone', 'same product: athenaOne is athenahealth\'s suite; Okta evidence folded into athenahealth'),
]
for keep, gone, _why in EXTRA_MERGES:
    if keep in rows:
        drop.add(gone)
for group in plan['remove']['merge']:
    present = [s for s in group if s in rows or rename.get(s, s) in rows]
    keep = group[0] if group[0] in rows else None  # a group whose first slug is absent folds into a product outside the index
    drop.update(s for s in present if s != keep)
for s in sorted(drop):
    if rows.pop(s, None) is not None:
        log['dropped'].append(s)
for old, new in rename.items():
    if old in rows:
        if new in rows:
            rows.pop(old); log['dropped'].append(old); continue
        rows[new] = rows.pop(old); rows[new]['slug'] = new; log['renamed'].append((old, new))

# 3-5. trim to v3, map IdP values, history fields
out = []
for slug, r in rows.items():
    row = {k: r.get(k) for k in FIELDS}
    row['slug'] = slug
    if row['notes'] is None:
        row['notes'] = ''
    if row['scim_ops'] is not None:
        row['scim_ops'] = {k: row['scim_ops'].get(k) for k in ['create', 'update', 'deactivate', 'delete', 'groups']}
    idp = row['idp'] or {}
    row['idp'] = {}
    for k in IDP_KEYS:
        v = idp.get(k)
        if k != 'generic' and v not in IDP_ENUM:
            v = None; log['idp_mapped_to_null'] += 1
        row['idp'][k] = v
    prev = june.get(slug)
    row['status_prev'] = prev['status'] if prev else None
    row['first_added'] = '2026-04' if prev else RELEASE
    out.append(row)

out.sort(key=lambda v: v['vendor'].lower())
missing_june = sorted(set(june) - {r['slug'] for r in out} - drop)

try:
    from validate import validate
    errs = validate(out)
except Exception as e:  # validator shape drift should not silently pass
    print('validator failed to run:', e); sys.exit(1)

counts = {s: sum(1 for r in out if r['status'] == s) for s in ['free', 'gated', 'partial', 'none', 'unknown']}
print(json.dumps({'vendors': len(out), 'status': counts, 'mechanical_applied': log['mechanical'],
                  'rule_fixes': len(log['rule_fixes']), 'renamed': len(log['renamed']), 'dropped': len(log['dropped']),
                  'idp_mapped_to_null': log['idp_mapped_to_null'], 'june_rows_not_carried': missing_june,
                  'validation_errors': len(errs)}, indent=1))
for e in errs[:20]:
    print('  ', e)
if errs or dry:
    print('data.json untouched' + (' (dry run)' if dry else ' (fix validation errors first)'))
    sys.exit(1 if errs else 0)

doc = {k: v for k, v in june_doc.items() if k != 'vendors'}
doc.update({'last_updated': LAST_UPDATED, 'count': len(out), 'vendors': out})
with open(os.path.join(ROOT, 'data.json'), 'w') as fh:
    json.dump(doc, fh, indent=2, ensure_ascii=False); fh.write('\n')
json.dump(log, open(os.path.join(HERE, 'run', 'APPLY_LOG.json'), 'w'), indent=1, ensure_ascii=False)
print('data.json written:', len(out), 'vendors')
