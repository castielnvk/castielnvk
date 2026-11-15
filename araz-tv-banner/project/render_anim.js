// node render_anim.js <outdir> <seconds> [variants...]  -> <outdir>/<V>/f%04d.jpg (preview over studio bg)
const { chromium } = require('playwright');
const fs = require('fs'), path = require('path');
const [out, secs, ...vs] = process.argv.slice(2);
const FPS = 25, N = Math.round(parseFloat(secs) * FPS);
const TL = { intro: 1.6, dur: .9, changes: [1.3, 4.8, 8.4, 12.0], lines: [0, 1, 2, 3] };
const root = path.resolve(__dirname, '..', '..');
const data = (f, m) => `data:${m};base64,` + fs.readFileSync(f).toString('base64');
const font = w => data(path.join(__dirname, 'fonts', `Montserrat_${w}.ttf`), 'font/ttf');
const html = `<style>
 @font-face{font-family:Montserrat;font-weight:700;src:url(${font('700Bold')})}
 @font-face{font-family:Montserrat;font-weight:800;src:url(${font('800ExtraBold')})}
 body{margin:0}</style><canvas id=c width=1920 height=1080></canvas>
 <script>${fs.readFileSync(path.join(__dirname, 'banner2.js'), 'utf8')}</script>`;
(async () => {
  const br = await chromium.launch();
  await Promise.all(vs.map(async v => {
    const dir = path.join(out, v); fs.mkdirSync(dir, { recursive: true });
    const pg = await br.newPage({ viewport: { width: 1920, height: 1080 } });
    await pg.setContent(html);
    await pg.evaluate(async ([w, t, bg]) => {
      await document.fonts.load('700 40px Montserrat'); await document.fonts.load('800 40px Montserrat');
      const ld = s => new Promise(r => { const i = new Image(); i.onload = () => r(i); i.src = s; });
      window.A = { white: await ld(w), teal: await ld(t) }; window.BG = await ld(bg);
    }, [data(path.join(root, 'logos/individual/araz-radio_white.png'), 'image/png'), data(path.join(root, 'logos/individual/araz-radio_teal.png'), 'image/png'), data(path.join(__dirname, 'studio_bg.jpg'), 'image/jpeg')]);
    for (let f = 0; f < N; f++) {
      const d = await pg.evaluate(([v, t, TL]) => {
        const c = document.getElementById('c'), x = c.getContext('2d');
        x.globalAlpha = 1; x.filter = 'none'; x.drawImage(BG, 0, 0);
        renderFrame(x, v, t, A, TL); return c.toDataURL('image/jpeg', .9);
      }, [v, f / FPS, TL]);
      fs.writeFileSync(path.join(dir, `f${String(f).padStart(4, '0')}.jpg`), Buffer.from(d.split(',')[1], 'base64'));
    }
  }));
  await br.close();
})();
