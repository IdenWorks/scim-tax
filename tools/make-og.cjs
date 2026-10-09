#!/usr/bin/env node
// Renders og.png (1200x630), the share-preview image for scimtax.org, from data.json.
// Run after a data refresh, alongside build.js. Needs Playwright and a local Chrome:
//   PW_PATH=/path/to/node_modules/playwright node tools/make-og.cjs
// (PW_PATH is optional when `playwright` resolves from this directory.)

const fs = require('fs');
const path = require('path');
const { chromium } = require(process.env.PW_PATH || 'playwright');

const ROOT = path.join(__dirname, '..');
const data = JSON.parse(fs.readFileSync(path.join(ROOT, 'data.json'), 'utf8'));
const rows = data.vendors;
const counts = { free: 0, gated: 0, partial: 0, none: 0, unknown: 0 };
rows.forEach((r) => counts[r.status]++);
const withScim = counts.free + counts.gated + counts.partial;
const gatedShare = Math.round((counts.gated / withScim) * 100);
const [y, m] = data.last_updated.split('-');
const month = new Date(Date.UTC(+y, +m - 1, 1)).toLocaleString('en-US', { month: 'long', timeZone: 'UTC' }) + ' ' + y;
const logo = fs.readFileSync(path.join(__dirname, 'iden-logo.svg'), 'utf8').replace(/width="\d+" height="\d+"/, 'height="28"');

// Same colours as the status dots on the site.
const SEG = [
  ['No Tax', counts.free, '#16a34a'],
  ['Gated', counts.gated, '#f59e0b'],
  ['Partial', counts.partial, '#94a3b8'],
  ['No SCIM', counts.none, '#d1d5db'],
  ['Unknown', counts.unknown, '#e5e7eb'],
];

const html = `<!doctype html><html><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500&display=swap" rel="stylesheet">
<style>
  * { box-sizing: border-box; margin: 0; }
  body { width: 1200px; height: 630px; background: #fff; color: #0f0f0f; font-family: 'Inter', sans-serif; padding: 56px 72px 0; display: flex; flex-direction: column; }
  .top { display: flex; justify-content: space-between; font-size: 22px; color: #6b7280; }
  .top b { color: #0f0f0f; font-weight: 500; }
  h1 { margin-top: 64px; font-size: 68px; line-height: 1.08; font-weight: 500; letter-spacing: -0.02em; max-width: 1000px; }
  .sub { margin-top: 22px; font-size: 26px; color: #374151; }
  .bar { margin-top: 44px; display: flex; height: 18px; border-radius: 4px; overflow: hidden; }
  .legend { margin-top: 16px; display: flex; gap: 28px; font-size: 19px; color: #6b7280; }
  .legend span { display: inline-flex; align-items: center; gap: 8px; }
  .legend i { width: 10px; height: 10px; border-radius: 50%; display: inline-block; }
  .legend b { color: #0f0f0f; font-weight: 500; }
  .foot { margin-top: auto; height: 92px; border-top: 1px solid #e5e7eb; display: flex; align-items: center; justify-content: space-between; font-size: 22px; color: #6b7280; }
  .foot .by { display: flex; align-items: center; gap: 14px; }
</style></head><body>
  <div class="top"><b>The SCIM Tax Index</b><span>Open dataset · ${month}</span></div>
  <h1>${gatedShare}% of SaaS vendors with SCIM charge extra for it.</h1>
  <p class="sub">${rows.length} vendors surveyed. Every price cited to the vendor's own pages.</p>
  <div class="bar">${SEG.map(([, n, c]) => `<div style="flex:${n};background:${c}"></div>`).join('')}</div>
  <div class="legend">${SEG.map(([l, n, c]) => `<span><i style="background:${c}"></i>${l} <b>${n}</b></span>`).join('')}</div>
  <div class="foot"><span>scimtax.org</span><span class="by">Maintained by ${logo}</span></div>
</body></html>`;

(async () => {
  const browser = await chromium.launch({ headless: true, channel: process.env.PW_CHANNEL || 'chrome' });
  const page = await browser.newPage({ viewport: { width: 1200, height: 630 }, deviceScaleFactor: 1 });
  await page.setContent(html, { waitUntil: 'networkidle' });
  await page.evaluate(() => document.fonts.ready);
  await page.screenshot({ path: path.join(ROOT, 'og.png') });
  await browser.close();
  console.log(`Wrote og.png: ${gatedShare}% gated of ${withScim}, ${rows.length} vendors, ${month}.`);
})();
