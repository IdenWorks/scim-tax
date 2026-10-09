#!/usr/bin/env node
// Headless page render for vendor research. Never opens a visible window.
// Usage: node render.cjs <url> <out_prefix> [--wait ms]
// Writes <out_prefix>.txt (visible text), <out_prefix>.html (rendered DOM), prints final URL, status and text length.
const PW = process.env.PW_PATH || 'playwright';
const { chromium } = require(PW);
const fs = require('fs');
(async () => {
  const [url, out] = process.argv.slice(2);
  const wi = process.argv.indexOf('--wait');
  const wait = wi > 0 ? +process.argv[wi + 1] : 2500;
  if (!url || !out) { console.error('usage: render.cjs <url> <out_prefix> [--wait ms]'); process.exit(2); }
  const browser = await chromium.launch({ headless: true, channel: process.env.PW_CHANNEL || 'chrome', args: ['--disable-blink-features=AutomationControlled'] });
  try {
    const ctx = await browser.newContext({
      userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0 Safari/537.36',
      locale: 'en-US', viewport: { width: 1366, height: 900 }, ignoreHTTPSErrors: true,
    });
    const page = await ctx.newPage();
    const resp = await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 45000 });
    try { await page.waitForLoadState('networkidle', { timeout: 12000 }); } catch {}
    await page.waitForTimeout(wait);
    const text = await page.evaluate(() => document.body ? document.body.innerText : '');
    fs.writeFileSync(out + '.txt', text);
    fs.writeFileSync(out + '.html', await page.content());
    console.log(JSON.stringify({ url: page.url(), status: resp ? resp.status() : null, title: await page.title(), text_len: text.length }));
  } catch (e) {
    console.log(JSON.stringify({ url, error: String(e).slice(0, 300) })); process.exitCode = 1;
  } finally { await browser.close(); }
})();
