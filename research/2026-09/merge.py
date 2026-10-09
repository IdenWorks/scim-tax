#!/usr/bin/env python3
"""Merge research batch outputs into data.json (schema v3).

Usage: python3 research/2026-09/merge.py <results_dir> [--dry-run]

- existing-*.json rows replace the matching slug in data.json (status_prev is set from the old row if the researcher left it null)
- new-*.json rows are appended; a new row whose slug (or normalised vendor name) already exists is reported and skipped
- every row is normalised to the full v3 field list; missing keys become null
- rows are validated (same rules as validate.py); the merge aborts on any error unless --force
"""
import json,sys,glob,os,re,datetime
HERE=os.path.dirname(os.path.abspath(__file__)); ROOT=os.path.abspath(os.path.join(HERE,'..','..'))
sys.path.insert(0,HERE)
FIELDS=['vendor','slug','category','status','scim_plan','scim_price_text','scim_price_per_user_mo','team_plan','team_price_text','team_price_per_user_mo','price_multiplier','sso_plan','sso_price_per_user_mo','sso_required_for_scim','scim_addon_price_text','min_seats','scim_ops','idp','pricing_page_url','docs_url','evidence','notes','confidence','last_verified','first_added','status_prev']
def norm(s):
    s=s.lower().replace('&','and'); s=re.sub(r'\(.*?\)','',s); return re.sub(r'[^a-z0-9]+','-',s).strip('-')
def normalise(r):
    out={k:r.get(k) for k in FIELDS}
    if not out['slug']: out['slug']=norm(out['vendor'])
    if out['scim_ops'] is not None:
        out['scim_ops']={k:out['scim_ops'].get(k) for k in ['create','update','deactivate','delete','groups']}
    if out['idp'] is None: out['idp']={}
    out['idp']={k:out['idp'].get(k) for k in ['okta','entra','google','onelogin','jumpcloud','generic']}
    if out['notes'] is None: out['notes']=''
    return out
def main():
    args=[a for a in sys.argv[1:] if not a.startswith('--')]; dry='--dry-run' in sys.argv; force='--force' in sys.argv
    rdir=args[0]
    data=json.load(open(os.path.join(ROOT,'data.json')))
    old={v['slug']:v for v in data['vendors']}
    by_slug=dict(old)
    name_index={norm(v['vendor']):s for s,v in old.items()}
    report={'replaced':0,'added':0,'skipped_dupe':[],'status_changes':[],'errors':[]}
    try:
        from validate import validate
    except Exception as e:
        validate=lambda rows:[]; print("warning: validator not importable:",e)
    for f in sorted(glob.glob(os.path.join(rdir,'*.json'))):
        rows=json.load(open(f)); rows=rows.get('vendors',rows) if isinstance(rows,dict) else rows
        kind='existing' if os.path.basename(f).startswith('existing') else 'new'
        errs=validate(rows)
        if errs:
            report['errors'].append((os.path.basename(f),len(errs)))
            for e in errs[:5]: print("  ",os.path.basename(f),e)
            if not force: continue
        for r in rows:
            r=normalise(r)
            if kind=='existing':
                prev=old.get(r['slug'])
                if prev is None:
                    report['skipped_dupe'].append((r['slug'],'existing row not found')); continue
                if r['status_prev'] is None: r['status_prev']=prev['status']
                if r['first_added'] is None: r['first_added']='2026-04'
                if prev['status']!=r['status']: report['status_changes'].append((r['vendor'],prev['status'],r['status']))
                by_slug[r['slug']]=r; report['replaced']+=1
            else:
                if r['slug'] in by_slug or norm(r['vendor']) in name_index:
                    report['skipped_dupe'].append((r['slug'],'already in dataset')); continue
                if r['first_added'] is None: r['first_added']='2026-09'
                by_slug[r['slug']]=r; name_index[norm(r['vendor'])]=r['slug']; report['added']+=1
    vendors=sorted(by_slug.values(),key=lambda v:v['vendor'].lower())
    data['vendors']=vendors; data['count']=len(vendors); data['last_updated']='2026-09'; data['schema']='v3'
    data['schema_url']='https://github.com/IdenWorks/scim-tax/blob/main/research/2026-09/SCHEMA.md'
    print(json.dumps({k:(v if not isinstance(v,list) else len(v)) for k,v in report.items()},indent=1))
    for s in report['status_changes'][:40]: print("  status change:",s)
    for s in report['skipped_dupe'][:40]: print("  skipped:",s)
    if report['errors']: print("  files with validation errors:",report['errors'])
    if dry: print("dry run, data.json untouched"); return
    json.dump(data,open(os.path.join(ROOT,'data.json'),'w'),indent=2,ensure_ascii=False); open(os.path.join(ROOT,'data.json'),'a').write('\n')
    print("data.json written:",len(vendors),"vendors")
if __name__=='__main__': main()
