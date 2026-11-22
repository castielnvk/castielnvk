// Renders SVG files to PNG with Chromium (transparent background), and the board HTML.
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

(async () => {
  const browser = await chromium.launch();
  if (process.argv[2] === '--board') {
    const page = await browser.newPage({ viewport: { width: 1200, height: 800 }, deviceScaleFactor: 2 });
    await page.goto('file://' + path.resolve(process.argv[3]));
    await page.waitForLoadState('networkidle');
    await page.screenshot({ path: process.argv[4], fullPage: true });
  } else {
    const jobs = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
    for (const [svg, png, w, h, scale] of jobs) {
      const page = await browser.newPage({ viewport: { width: w, height: h }, deviceScaleFactor: scale });
      const src = fs.readFileSync(svg, 'utf8');
      await page.setContent(`<html><body style="margin:0;background:transparent;overflow:hidden">${src}</body></html>`);
      await page.screenshot({ path: png, omitBackground: true, clip: { x: 0, y: 0, width: w, height: h } });
      await page.close();
    }
  }
  await browser.close();
})();
