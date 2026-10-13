const { chromium } = require('playwright');
const fs = require('fs'), path = require('path');
const dir = process.argv[2];
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ deviceScaleFactor: 2 });
  for (const f of fs.readdirSync(dir).filter(f => f.endsWith('.svg')).sort()) {
    const svg = fs.readFileSync(path.join(dir, f), 'utf8');
    await p.setContent(`<html><body style="margin:0;background:#fff">${svg}</body></html>`);
    await p.evaluate(() => document.fonts.ready);
    await p.locator('svg').first().screenshot({ path: path.join(dir, f.replace('.svg', '.png')), omitBackground: true });
  }
  await b.close();
})();
