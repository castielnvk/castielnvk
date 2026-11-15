// node render_film.js <outdir> <seconds> <preview|alpha> [startSeconds]
// preview: JPG frames composited over studio_bg.jpg ; alpha: transparent PNG frames (1920x1080 RGBA)
const { chromium } = require('playwright');
const fs = require('fs'), path = require('path');
const [out, secs, mode = 'preview', start = '0'] = process.argv.slice(2);
const FPS = 25, N = Math.round(parseFloat(secs) * FPS), T0 = parseFloat(start);
const root = path.resolve(__dirname, '..', '..');
const data = (f, m) => `data:${m};base64,` + fs.readFileSync(f).toString('base64');
const font = w => data(path.join(__dirname, 'fonts', `Montserrat_${w}.ttf`), 'font/ttf');
const html = `<style>
 @font-face{font-family:Montserrat;font-weight:500;src:url(${font('500Medium')})}
 @font-face{font-family:Montserrat;font-weight:600;src:url(${font('600SemiBold')})}
 @font-face{font-family:Montserrat;font-weight:700;src:url(${font('700Bold')})}
 @font-face{font-family:Montserrat;font-weight:800;src:url(${font('800ExtraBold')})}
 body{margin:0}</style><canvas id=c width=1920 height=1080></canvas>
 <script>${fs.readFileSync(path.join(__dirname, 'film.js'), 'utf8')}</script>`;
const IMG = { metal: 'metal.jpg', waterBase: 'water_base.jpg', c0: 'caustic_0.jpg', c1: 'caustic_1.jpg', land: 'land.jpg', wood: 'wood.jpg', bg: 'studio_bg.jpg' };
const W = 4;
(async () => {
  fs.mkdirSync(out, { recursive: true });
  const br = await chromium.launch();
  const srcs = Object.fromEntries(Object.entries(IMG).map(([k, f]) => [k, data(path.join(__dirname, f), 'image/jpeg')]));
  srcs.logoWhite = data(path.join(root, 'logos/individual/araz-radio_white.png'), 'image/png');
  await Promise.all([...Array(W).keys()].map(async w => {
    const pg = await br.newPage({ viewport: { width: 1920, height: 1080 } });
    pg.on('pageerror', e => { console.error('PAGE ERROR', e.message); process.exit(1); });
    await pg.setContent(html);
    await pg.evaluate(async (srcs) => {
      for (const wt of [500, 600, 700, 800]) await document.fonts.load(`${wt} 40px Montserrat`);
      const ld = s => new Promise(r => { const i = new Image(); i.onload = () => r(i); i.src = s; });
      window.A = {}; for (const k in srcs) window.A[k] = await ld(srcs[k]);
    }, srcs);
    for (let f = w; f < N; f += W) {
      const d = await pg.evaluate(([t, mode]) => {
        const c = document.getElementById('c'), x = c.getContext('2d');
        x.setTransform(1, 0, 0, 1, 0, 0); x.globalAlpha = 1; x.globalCompositeOperation = 'source-over'; x.filter = 'none'; x.clearRect(0, 0, 1920, 1080);
        if (mode === 'preview') x.drawImage(A.bg, 0, 0);
        renderFilm(x, t, A);
        return mode === 'preview' ? c.toDataURL('image/jpeg', .92) : c.toDataURL('image/png');
      }, [T0 + f / FPS, mode]);
      fs.writeFileSync(path.join(out, `f${String(f).padStart(4, '0')}.${mode === 'preview' ? 'jpg' : 'png'}`), Buffer.from(d.split(',')[1], 'base64'));
    }
  }));
  await br.close();
})();
