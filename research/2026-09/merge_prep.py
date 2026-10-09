#!/usr/bin/env python3
"""Dry-run merge preparation for the 2026-09 refresh.

Reads vendors/*.json and writes run/MERGE_PLAN.json describing every change the merge would make.
Nothing in vendors/ or data.json is touched; applying the plan is a separate step once the open
decisions are settled.

Groups:
  mechanical   field-level clean-ups that follow from the schema (no judgement)
  rule_fixes   status corrections where a batch applied a rule that was clarified later
  remove       discontinued vendors, duplicates to merge, and out-of-scope candidates
  decisions    open methodology questions and the rows each one moves
  recheck      rows whose evidence needs another pass (blocked sites, challenge-page citations)
"""
import json, glob, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
V = {}
for f in sorted(glob.glob(os.path.join(HERE, 'vendors', '*.json'))):
    d = json.load(open(f))
    V[d['slug']] = d

plan = {'mechanical': [], 'rule_fixes': [], 'remove': {}, 'decisions': {}, 'recheck': []}
mech = plan['mechanical']


def change(slug, field, old, new, why):
    mech.append({'slug': slug, 'field': field, 'from': old, 'to': new, 'why': why})


CHALLENGE = re.compile(r'security checkpoint|just a moment|verifying your browser|attention required|access denied', re.I)

for slug, d in V.items():
    r = d['row']
    cits = {c['id']: c for c in d.get('citations', [])}
    # 1. docs_url / pricing_page_url pointing at a machine-readable export -> the human page
    for k in ('docs_url', 'pricing_page_url'):
        u = r.get(k)
        if not u:
            continue
        for c in cits.values():
            if c.get('url', '').rstrip('/') == u.rstrip('/') and c.get('page_url') and re.search(r'\.json($|\?)|/api/v2/help_center|\.md($|\?)|/api/v1/', u):
                change(slug, k, u, c['page_url'], 'machine-readable URL; use the human page')
                break
    # 2. free with SCIM on the team tier: SCIM price = team price, multiplier 1.0
    if r['status'] == 'free' and r.get('team_price_per_user_mo') is not None and r.get('scim_price_per_user_mo') is None:
        change(slug, 'scim_price_per_user_mo', None, r['team_price_per_user_mo'], 'No Tax: SCIM included at the team price')
        change(slug, 'price_multiplier', r.get('price_multiplier'), 1.0, 'No Tax: no upcharge')
    # 3. api_provisioning true backed only by third-party connectors -> null
    if r.get('api_provisioning') is True:
        apps = [a for a in (d.get('idp_apps') or {}).values() if isinstance(a, dict) and a.get('kind') == 'api_connector']
        if apps and all(a.get('built_by') == 'third_party' for a in apps):
            change(slug, 'api_provisioning', True, None, 'only third-party connectors provision via the API')
    # 4. slug format: dots -> hyphens
    if '.' in slug:
        plan.setdefault('slug_renames', []).append({'from': slug, 'to': slug.replace('.', '-')})
    # 5. citations that quote a bot-challenge page instead of content
    for c in cits.values():
        if not c.get('blocked') and CHALLENGE.search(c.get('quote', '')):
            plan['recheck'].append({'slug': slug, 'cid': c['id'], 'why': 'quote is bot-challenge text: ' + c['quote'][:60]})

# Hand-curated from run/REVIEW_NOTES.md --------------------------------------------------------
for slug, val, why in [
    ('capsule-crm', ('row.sso_plan', None), 'only Google/Microsoft domain sign-in (social), not SAML/OIDC'),
    ('livechat', ('row.api_tax', False), 'API metered per request on every plan, not locked above the team plan'),
    ('skilljar', ('row.user_api_available', False), 'API manages learners, not admin users'),
    ('veeam', ('row.team_price_per_user_mo', None), 'price is per protected M365 user, not per admin seat'),
]:
    if slug in V:
        change(slug, val[0], None, val[1], why)

for slug, new, why in [
    ('genesys-cloud', 'unknown', 'rule 1a: no page names a plan for SCIM'),
    ('nice-cxone', 'unknown', 'rule 1a'),
    ('customer-io', 'unknown', 'rule 1a'), ('customer.io', 'unknown', 'rule 1a'),
    ('twilio', 'unknown', 'rule 1a'),
    ('navan', 'unknown', 'rule 1a: free was inferred'),
    ('veeva-systems', 'gated', 'rule 6a: quote-only + SCIM documented'),
    ('five9', 'gated', 'rule 6a: quote-only + SCIM documented'),
    ('cornerstone', 'unknown', 'rule 6a: SCIM only in an IdP catalogue'),
    ('hireez', 'unknown', 'rule 6a: SCIM only in an IdP catalogue'),
    ('island-technology', 'unknown', 'rule 6a: SCIM only in an IdP catalogue'),
]:
    if slug in V and V[slug]['row']['status'] != new:
        plan['rule_fixes'].append({'slug': slug, 'from': V[slug]['row']['status'], 'to': new, 'why': why})

plan['remove'] = {
    'discontinued': ['multi', 'pivotal-tracker', 'rows', 'almanac', 'around', 'bluejeans', 'delighted', 'facebook-workplace',
                     'hired', 'invision', 'lightstep', 'height', 'returnly', 'samepage', 'mention', 'redash', 'workshare'],
    'merge': [['bill-com', 'bill.com'], ['devin', 'codeium', 'windsurf'], ['infor', 'infor-hcm'], ['lucidchart', 'lucid'],
              ['notarize', 'proof'], ['bmc-helix', 'remedy'], ['drift-salesloft', 'salesloft'], ['toggl-track', 'toggl-plan'], ['lightspeed', 'vend'],
              ['workday-recruiting?', 'hiredscore']],
    'merge_maybe': [['mailchimp', 'mandrill'], ['jack-henry', 'symitar'], ['fivetran', 'census'], ['clearwater-analytics', 'enfusion'],
                    ['proofpoint', 'tessian'], ['gainsight', 'staircase'], ['adroll', 'rollworks'], ['onetrust', 'tugboat-logic'], ['madkudu', 'trustradius'], ['trinet', 'zenefits']],
    'scope_self_hosted_or_oss': ['argo-cd', 'arcsight', 'backstage', 'fortinet', 'jenkins', 'kubernetes', 'openshift', 'pdq-deploy',
                                 'puppet', 'qradar', 'rancher', 'saltstack', 'spinnaker', 'spotfire', 'spree', 'redshift', 'vmware-tanzu'],
    'scope_consumer_or_benefit': ['legalzoom', 'origami-studio', 'pixelmator', 'principle', 'procreate', 'one-medical',
                                  'modern-health', 'spring-health'],
}
plan['decisions'] = {
    '7 JIT-only = none or partial': 'rows with status none and fallbacks.jit true',
    '8 IdP vendors scored as provisioning targets': ['google-workspace', 'microsoft-365', 'okta', 'rippling', 'jumpcloud', 'auth0', 'duo-security'],
    '9 per-unit multiplier (store/org/host) to keep plan-jump stats like Shopify 79x': ['shopify', 'sentry', 'datadog'],
    '10 platform-native apps inherit host status?': ['certinia', 'champify', 'pardot', 'judge.me'],
    '11 free needs positive evidence (applied as rule 1a)': 'see rule_fixes',
    '12 single quote-only plan with SCIM: free or gated': ['peakon', 'productplan', 'rollworks', 'sourcegraph', 'strong-dm', 'totango'],
    'single-IdP SCIM on a free tier: free or partial': ['commonroom', 'qlik'],
    'scope: self-hosted / consumer / benefit rows': 'see remove.scope_*',
}
plan['recheck'] += [{'slug': s, 'why': 'site blocked or login-walled during research'} for s in
                    ['8x8', 'checkr', 'constant-contact', 'contentful', 'coursera-for-business', 'crowdin', 'goto-meeting', 'hibob',
                     'jobber', 'lastpass', 'netsuite', 'observable', 'quickbooks-online', 'xero', 'yardi']]

out = os.path.join(HERE, 'run', 'MERGE_PLAN.json')
json.dump(plan, open(out, 'w'), indent=1, ensure_ascii=False)
print(f"vendors: {len(V)}  mechanical: {len(mech)}  rule_fixes: {len(plan['rule_fixes'])}  "
      f"slug_renames: {len(plan.get('slug_renames', []))}  recheck: {len(plan['recheck'])}")
print('written', out)
