// usage: node render.js <outdir> [frame list "a,b,c" | "all"]
const { chromium } = require('playwright');
const fs = require('fs'), path = require('path');
const S = path.resolve(__dirname, '..');
const out = process.argv[2]; const sel = process.argv[3] || 'all';
const TOTAL = 657;
const map = (u) => {
  const p = new URL(u).pathname;
  if (p === '/') return path.join(__dirname, 'render.html');
  if (p === '/logo.png') return '/workspace/castielnvk/logos/overlays/kesfet_overlay_1080x1920.png';
  if (p.startsWith('/frames/')) return path.join(S, p);
  if (p.startsWith('/fonts/')) {
    const f = path.basename(p);
    return path.join(S, 'fonts/node_modules', f.startsWith('archivo') ? '@fontsource-variable/archivo/files' : '@fontsource/playfair-display/files', f);
  }
};
(async () => {
  fs.mkdirSync(out, { recursive: true });
  const frames = sel === 'all' ? [...Array(TOTAL).keys()] : sel.split(',').map(Number);
  const browser = await chromium.launch();
  const N = sel === 'all' ? 4 : 1;
  await Promise.all([...Array(N).keys()].map(async (k) => {
    const page = await browser.newPage();
    page.on('console', (m) => console.log('[page]', m.text()));
    page.on('pageerror', (e) => console.log('[err]', e.message));
    await page.route('**/*', async (route) => {
      const f = map(route.request().url());
      if (f && fs.existsSync(f)) route.fulfill({ path: f }); else route.fulfill({ status: 404, body: '' });
    });
    await page.goto('http://app.local/');
    const m = await page.evaluate(() => init());
    if (k === 0) console.log('font widths expanded/normal', m);
    // contiguous slices keep the image cache effective
    const mine = frames.filter((_, i) => Math.floor(i * N / frames.length) === k);
    for (const n of mine) {
      const d = await page.evaluate((n) => render(n), n);
      fs.writeFileSync(path.join(out, String(n).padStart(5, '0') + '.jpg'), Buffer.from(d.split(',')[1], 'base64'));
    }
    await page.close();
  }));
  await browser.close();
})();
