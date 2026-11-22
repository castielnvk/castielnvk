// usage: node render.js outdir scale fps "t1,t2,..."  OR  node render.js outdir scale fps all workerIdx nWorkers
const { chromium } = require('playwright');
const fs = require('fs');
(async () => {
  const [out, scale, fps, which, wi, nw] = process.argv.slice(2);
  fs.mkdirSync(out, { recursive: true });
  const b = await chromium.launch({ args: ['--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  const p = await b.newPage({ viewport: { width: 1080, height: 1920 } });
  p.on('console', m => { if (m.type() === 'error') console.error('PAGE', m.text()); });
  p.on('pageerror', e => console.error('PAGEERR', e.message));
  await p.goto(`http://127.0.0.1:8765/scene.html?s=${scale}`);
  await p.waitForFunction(() => window.ready === true, null, { timeout: 120000 });
  let times;
  const F = parseFloat(fps);
  if (which === 'all') { times = []; for (let i = 0; i < Math.round(12 * F); i++) if (i % parseInt(nw) === parseInt(wi)) times.push([i, i / F]); }
  else times = which.split(',').map((t, i) => [t, parseFloat(t)]);
  for (const [name, t] of times) {
    const fn = which === 'all' ? `${out}/f${String(name).padStart(4, '0')}.png` : `${out}/t${name}.png`;
    if (which === 'all' && fs.existsSync(fn)) continue;
    const t0 = Date.now();
    // render twice so reflectors pick up the current frame
    const data = await p.evaluate(tt => { window.renderAt(tt); window.renderAt(tt); return document.querySelector('canvas').toDataURL('image/png'); }, t);
    fs.writeFileSync(fn + '.tmp', Buffer.from(data.split(',')[1], 'base64'));
    fs.renameSync(fn + '.tmp', fn);
    console.log(fn, Date.now() - t0, 'ms');
  }
  await b.close();
})();
