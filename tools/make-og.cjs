#!/usr/bin/env node
// Renders og.png (1200x630), the share-preview image for scimtax.org. The date comes from data.json.
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
const logo = fs.readFileSync(path.join(__dirname, 'iden-logo.svg'), 'utf8').replace(/width="\d+" height="\d+"/, 'height="32"');

const html = `<!doctype html><html><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500&display=swap" rel="stylesheet">
<style>
  * { box-sizing: border-box; margin: 0; }
  body { width: 1200px; height: 630px; background: #fff; color: #0f0f0f; font-family: 'Inter', sans-serif; padding: 0 72px; display: flex; flex-direction: column; }
  .main { flex: 1; display: flex; flex-direction: column; justify-content: center; gap: 20px; }
  h1 { font-size: 96px; line-height: 1; font-weight: 500; letter-spacing: -0.03em; }
  .date { font-size: 32px; color: #6b7280; }
  .foot { height: 112px; border-top: 1px solid #e5e7eb; display: flex; align-items: center; justify-content: space-between; font-size: 26px; color: #6b7280; }
  .foot .by { display: flex; align-items: center; gap: 14px; }
</style></head><body>
  <div class="main"><h1>SCIM Tax Index</h1><p class="date">${month}</p></div>
  <div class="foot"><span>scimtax.org</span><span class="by">Maintained by ${logo}</span></div>
</body></html>`;

(async () => {
  const browser = await chromium.launch({ headless: true, channel: process.env.PW_CHANNEL || 'chrome' });
  const page = await browser.newPage({ viewport: { width: 1200, height: 630 }, deviceScaleFactor: 1 });
  await page.setContent(html, { waitUntil: 'networkidle' });
  await page.evaluate(() => document.fonts.ready);
  await page.screenshot({ path: path.join(ROOT, 'og.png') });
  await browser.close();
  console.log(`Wrote og.png (${month}).`);
})();
