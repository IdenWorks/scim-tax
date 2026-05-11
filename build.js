#!/usr/bin/env node
// Generate data.csv and data.json from the V array in index.html.
// Run after editing the vendor list in index.html.

const fs = require('fs');
const path = require('path');

const ROOT = __dirname;
const html = fs.readFileSync(path.join(ROOT, 'index.html'), 'utf8');

const arrayMatch = html.match(/const V = \[([\s\S]*?)\n\];/);
if (!arrayMatch) {
  console.error('Could not find `const V = [...]` block in index.html.');
  process.exit(1);
}

const block = arrayMatch[1];
const rowRegex = /\['((?:[^'\\]|\\.)*)','((?:[^'\\]|\\.)*)','((?:[^'\\]|\\.)*)','((?:[^'\\]|\\.)*)','((?:[^'\\]|\\.)*)','((?:[^'\\]|\\.)*)'\]/g;

const slug = (s) => s.toLowerCase()
  .replace(/&/g, 'and')
  .replace(/[^a-z0-9]+/g, '-')
  .replace(/^-+|-+$/g, '');

const rows = [];
let m;
while ((m = rowRegex.exec(block)) !== null) {
  rows.push({
    vendor: m[1],
    slug: slug(m[1]),
    status: m[2],
    plan_required: m[3],
    scim_price: m[4],
    base_plan_price: m[5],
    pricing_page_url: m[6],
  });
}

if (rows.length === 0) {
  console.error('Parsed zero rows. Check the V array formatting in index.html.');
  process.exit(1);
}

// data.json
const json = {
  name: 'The SCIM Tax Index',
  source: 'https://scimtax.org/',
  license: 'CC-BY 4.0',
  last_updated: '2026-04',
  count: rows.length,
  vendors: rows,
};
fs.writeFileSync(path.join(ROOT, 'data.json'), JSON.stringify(json, null, 2) + '\n');

// data.csv
const header = ['vendor', 'slug', 'status', 'plan_required', 'scim_price', 'base_plan_price', 'pricing_page_url'];
const csvLines = [header.join(',')];
for (const r of rows) {
  csvLines.push(header.map((h) => {
    const v = String(r[h] ?? '');
    return /[",\n]/.test(v) ? '"' + v.replace(/"/g, '""') + '"' : v;
  }).join(','));
}
fs.writeFileSync(path.join(ROOT, 'data.csv'), csvLines.join('\n') + '\n');

console.log(`Wrote data.json and data.csv (${rows.length} vendors).`);
