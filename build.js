#!/usr/bin/env node
// Generate data.csv and data.json from the V array in index.html.
// Run after editing the vendor list in index.html.
//
// V tuple shape (12 elements):
//   [0] vendor name
//   [1] status              (free | gated | partial | none | unknown)
//   [2] scim_plan_label     (the plan name required for SCIM)
//   [3] scim_price_text     (free-text price for that plan, may say "Contact Sales")
//   [4] team_price_text     (free-text price for the lowest paid team plan)
//   [5] pricing_page_url
//   [6] team_plan           (the plan name for the lowest paid tier; may be null)
//   [7] team_price_per_user_mo   (numeric or null)
//   [8] scim_price_per_user_mo   (numeric or null)
//   [9] price_multiplier         (numeric or null, scim/team ratio)
//   [10] notes
//   [11] last_verified           (YYYY-MM-DD)

const fs = require('fs');
const path = require('path');

const ROOT = __dirname;
const html = fs.readFileSync(path.join(ROOT, 'index.html'), 'utf8');

const arrayMatch = html.match(/const V = (\[[\s\S]*?\n\]);/);
if (!arrayMatch) {
  console.error('Could not find `const V = [...]` block in index.html.');
  process.exit(1);
}

// Safely parse the V array literal as JS.
let V;
try {
  V = new Function('return ' + arrayMatch[1])();
} catch (e) {
  console.error('Failed to parse V array as JS:', e.message);
  process.exit(1);
}

const slug = (s) => s.toLowerCase()
  .replace(/&/g, 'and')
  .replace(/[^a-z0-9]+/g, '-')
  .replace(/^-+|-+$/g, '');

const rows = V.map((r) => ({
  vendor: r[0],
  slug: slug(r[0]),
  status: r[1],
  scim_plan: r[2],
  scim_price_text: r[3],
  team_price_text: r[4],
  pricing_page_url: r[5],
  team_plan: r[6] ?? null,
  team_price_per_user_mo: r[7] ?? null,
  scim_price_per_user_mo: r[8] ?? null,
  price_multiplier: r[9] ?? null,
  notes: r[10] ?? '',
  last_verified: r[11] ?? '',
}));

if (rows.length === 0) {
  console.error('Parsed zero rows. Check the V array formatting in index.html.');
  process.exit(1);
}

// data.json
const json = {
  name: 'The SCIM Tax Index',
  source: 'https://scimtax.org/',
  license: 'CC-BY 4.0',
  last_updated: '2026-06',
  count: rows.length,
  vendors: rows,
};
fs.writeFileSync(path.join(ROOT, 'data.json'), JSON.stringify(json, null, 2) + '\n');

// data.csv
const header = [
  'vendor',
  'slug',
  'status',
  'scim_plan',
  'scim_price_text',
  'team_price_text',
  'pricing_page_url',
  'team_plan',
  'team_price_per_user_mo',
  'scim_price_per_user_mo',
  'price_multiplier',
  'notes',
  'last_verified',
];
const csvLines = [header.join(',')];
for (const r of rows) {
  csvLines.push(header.map((h) => {
    const v = r[h];
    if (v === null || v === undefined) return '';
    const s = String(v);
    return /[",\n]/.test(s) ? '"' + s.replace(/"/g, '""') + '"' : s;
  }).join(','));
}
fs.writeFileSync(path.join(ROOT, 'data.csv'), csvLines.join('\n') + '\n');

console.log(`Wrote data.json and data.csv (${rows.length} vendors).`);
