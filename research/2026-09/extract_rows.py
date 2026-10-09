#!/usr/bin/env python3
"""Collect the v3 summary rows from vendors/*.json into results/ for merge.py.

Usage: python3 research/2026-09/extract_rows.py
Writes results/existing.json (slugs already in data.json) and results/new.json.
"""
import json, os, glob

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
have = {v['slug'] for v in json.load(open(os.path.join(ROOT, 'data.json')))['vendors']}
existing, new = [], []
for f in sorted(glob.glob(os.path.join(HERE, 'vendors', '*.json'))):
    row = json.load(open(f))['row']
    (existing if row['slug'] in have else new).append(row)
os.makedirs(os.path.join(HERE, 'results'), exist_ok=True)
json.dump(existing, open(os.path.join(HERE, 'results', 'existing.json'), 'w'), indent=1, ensure_ascii=False)
json.dump(new, open(os.path.join(HERE, 'results', 'new.json'), 'w'), indent=1, ensure_ascii=False)
print(f'existing: {len(existing)}  new: {len(new)}')
