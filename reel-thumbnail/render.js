// İstifadə: node render.js [fayl.html]  →  eyni adlı .png (1080x1920)
const { chromium } = require('playwright');
const path = require('path');
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1080, height: 1920 } });
  await p.goto('file://' + path.join(__dirname, process.argv[2] || 'thumbnail.html'));
  await p.evaluate(() => document.fonts.ready);
  await p.waitForTimeout(600);
  await p.screenshot({ path: path.join(__dirname, (process.argv[2] || 'thumbnail.html').replace('.html', '.png')) });
  await b.close();
})();
