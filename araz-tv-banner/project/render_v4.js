// node render_tar.js <outdir> <seconds> <mode: preview|alpha> [timelineJSON]
// preview: JPG frames over studio_bg.jpg ; alpha: transparent PNG frames
const { chromium } = require('playwright');
const fs = require('fs'), path = require('path');
const [out, secs, mode = 'preview', CONCEPT = 'SILK', tlj] = process.argv.slice(2);
const FPS = 25, N = Math.round(parseFloat(secs) * FPS);
const TL = tlj ? JSON.parse(tlj) : { at: [0.6, 6.0, 12.0, 17.5, 24.0], lines: [0, 1, 2, 3, 0], flagDur: 3.0 };
const root = path.resolve(__dirname, '..', '..');
const data = (f, m) => `data:${m};base64,` + fs.readFileSync(f).toString('base64');
const font = w => data(path.join(__dirname, 'fonts', `Montserrat_${w}.ttf`), 'font/ttf');
const html = `<style>
 @font-face{font-family:Montserrat;font-weight:600;src:url(${font('600SemiBold')})}
 @font-face{font-family:Montserrat;font-weight:700;src:url(${font('700Bold')})}
 @font-face{font-family:Montserrat;font-weight:800;src:url(${font('800ExtraBold')})}
 body{margin:0}</style><canvas id=c width=1920 height=1080></canvas>
 <script>${fs.readFileSync(path.join(__dirname, 'v4.js'), 'utf8')}</script>`;
const W = 4;
(async () => {
  fs.mkdirSync(out, { recursive: true });
  const br = await chromium.launch();
  await Promise.all([...Array(W).keys()].map(async w => {
    const pg = await br.newPage({ viewport: { width: 1920, height: 1080 } });
    await pg.setContent(html);
    await pg.evaluate(async ([wl, bg, tl]) => {
      await document.fonts.load('700 40px Montserrat'); await document.fonts.load('600 40px Montserrat'); await document.fonts.load('800 40px Montserrat');
      const ld = s => new Promise(r => { const i = new Image(); i.onload = () => r(i); i.src = s; });
      window.A = { white: await ld(wl), teal: await ld(tl) }; window.BG = await ld(bg);
    }, [data(path.join(root, 'logos/individual/araz-radio_white.png'), 'image/png'), data(path.join(__dirname, 'studio_bg.jpg'), 'image/jpeg'), data(path.join(root, 'logos/individual/araz-radio_teal.png'), 'image/png')]);
    for (let f = w; f < N; f += W) {
      const d = await pg.evaluate(([t, TL, mode, CONCEPT]) => {
        const c = document.getElementById('c'), x = c.getContext('2d');
        x.setTransform(1, 0, 0, 1, 0, 0); x.globalAlpha = 1; x.clearRect(0, 0, 1920, 1080);
        if (mode === 'preview') x.drawImage(BG, 0, 0);
        renderV4(x, t, A, TL);
        return mode === 'preview' ? c.toDataURL('image/jpeg', .9) : c.toDataURL('image/png');
      }, [f / FPS, TL, mode, CONCEPT]);
      fs.writeFileSync(path.join(out, `f${String(f).padStart(4, '0')}.${mode === 'preview' ? 'jpg' : 'png'}`), Buffer.from(d.split(',')[1], 'base64'));
    }
  }));
  await br.close();
})();
