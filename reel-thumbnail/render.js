// İstifadə: node render.js [kadr.jpg]   →  thumbnail.png (1080x1920)
const { chromium } = require('playwright');
const path = require('path');
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1080, height: 1920 } });
  const frame = process.argv[2] ? '?frame=' + encodeURIComponent(path.resolve(process.argv[2])) : '';
  await p.goto('file://' + path.join(__dirname, 'thumbnail.html') + frame);
  await p.evaluate(() => document.fonts.ready);
  await p.waitForTimeout(500);
  await p.screenshot({ path: path.join(__dirname, 'thumbnail.png') });
  await b.close();
})();
