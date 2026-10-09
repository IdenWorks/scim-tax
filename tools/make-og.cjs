#!/usr/bin/env node
// Renders the share-preview images for scimtax.org from data.json (the date):
//   og.png         1200x630, the og:image for link previews
//   og-square.png  1200x1200, for profiles and posts that want a square
// Run after a data refresh, alongside build.js. Needs Playwright and a local Chrome:
//   PW_PATH=/path/to/node_modules/playwright node tools/make-og.cjs
// (PW_PATH is optional when `playwright` resolves from this directory.)

const fs = require('fs');
const path = require('path');
const { chromium } = require(process.env.PW_PATH || 'playwright');

const ROOT = path.join(__dirname, '..');
const data = JSON.parse(fs.readFileSync(path.join(ROOT, 'data.json'), 'utf8'));
const [y, m] = data.last_updated.split('-');
const month = new Date(Date.UTC(+y, +m - 1, 1)).toLocaleString('en-US', { month: 'short', timeZone: 'UTC' }) + ' ' + y;
const logo = fs.readFileSync(path.join(__dirname, 'iden-logo.svg'), 'utf8').replace(/width="\d+" height="\d+"/, 'height="32"')
  .replace(/fill="#404040"/g, 'fill="currentColor"'); // logo takes the text colour

const page = (w, h, title, date, foot, by) => `<!doctype html><html><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500&display=swap" rel="stylesheet">
<style>
  * { box-sizing: border-box; margin: 0; }
  body { width: ${w}px; height: ${h}px; background: #fff; color: #0f0f0f; font-family: 'Inter', sans-serif; padding: 0 72px; display: flex; flex-direction: column; }
  .top { height: ${foot}px; display: flex; align-items: center; justify-content: space-between; font-size: ${date}px; color: #6b7280; }
  .main { flex: 1; display: flex; flex-direction: column; justify-content: center; }
  h1 { font-size: ${title}px; line-height: 1; font-weight: 500; letter-spacing: -0.03em; }
  .foot { height: ${foot}px; border-top: 1px solid #e5e7eb; display: flex; align-items: center; justify-content: space-between; font-size: ${by}px; color: #6b7280; }
  .foot .by { display: flex; align-items: center; gap: ${Math.round(by * 0.45)}px; }
  .foot .by svg { height: ${Math.round(by * 0.95)}px; width: auto; }
</style></head><body>
  <div class="top"><span>Updated ${month}</span><span>scimtax.org</span></div>
  <div class="main"><h1>SCIM Tax Index</h1></div>
  <div class="foot"><span class="by">Maintained by ${logo}</span></div>
</body></html>`;

const SIZES = [
  ['og.png', page(1200, 630, 104, 26, 120, 38)],
  ['og-square.png', page(1200, 1200, 140, 30, 170, 46)],
];

(async () => {
  const browser = await chromium.launch({ headless: true, channel: process.env.PW_CHANNEL || 'chrome' });
  for (const [file, html] of SIZES) {
    const [w, h] = html.match(/width: (\d+)px; height: (\d+)px/).slice(1).map(Number);
    const p = await browser.newPage({ viewport: { width: w, height: h }, deviceScaleFactor: 1 });
    await p.setContent(html, { waitUntil: 'networkidle' });
    await p.evaluate(() => document.fonts.ready);
    await p.screenshot({ path: path.join(ROOT, file) });
    await p.close();
  }
  await browser.close();
  console.log(`Wrote og.png and og-square.png (${month}).`);
})();
