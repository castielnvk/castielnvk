// node render.js -> cover_1080x1920.jpg (Reels cover) via headless Chromium
const { chromium } = require('playwright'); const path = require('path');
(async () => {
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 });
  await p.goto('file://' + path.resolve(__dirname, 'cover.html')); await p.waitForLoadState('load'); await p.evaluate(() => document.fonts.ready);
  await p.locator('#cover').screenshot({ path: path.resolve(__dirname, process.argv[2] || 'cover_1080x1920.jpg'), type: 'jpeg', quality: 95 });
  await b.close();
})();
