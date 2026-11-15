// node render_stills.js <outdir>  -> <outdir>/<V>_<line>.png (1920x1080 RGBA)
const { chromium } = require('playwright');
const fs = require('fs'), path = require('path');
const out = process.argv[2]; fs.mkdirSync(out, { recursive: true });
const root = path.resolve(__dirname, '..', '..');
const b64 = f => 'data:image/png;base64,' + fs.readFileSync(path.join(root, f)).toString('base64');
const font = w => 'data:font/ttf;base64,' + fs.readFileSync(path.join(__dirname, 'fonts', `Montserrat_${w}.ttf`)).toString('base64');
(async () => {
  const br = await chromium.launch(); const pg = await br.newPage({ viewport: { width: 1920, height: 1080 } });
  await pg.setContent(`<style>
   @font-face{font-family:Montserrat;font-weight:500;src:url(${font('500Medium')})}
   @font-face{font-family:Montserrat;font-weight:700;src:url(${font('700Bold')})}
   @font-face{font-family:Montserrat;font-weight:800;src:url(${font('800ExtraBold')})}
   body{margin:0;background:transparent}</style><canvas id=c width=1920 height=1080></canvas>
   <div style="font:700 10px Montserrat;position:absolute;opacity:0">əİ</div><div style="font:800 10px Montserrat;position:absolute;opacity:0">əİ</div>
   <script>${fs.readFileSync(path.join(__dirname, 'banner.js'), 'utf8')}</script>`);
  await pg.evaluate(async ([w, t]) => {
    await document.fonts.load('700 40px Montserrat'); await document.fonts.load('800 40px Montserrat');
    const ld = s => new Promise(r => { const i = new Image(); i.onload = () => r(i); i.src = s; });
    window.A = { white: await ld(w), teal: await ld(t) };
  }, [b64('logos/individual/araz-radio_white.png'), b64('logos/individual/araz-radio_teal.png')]);
  for (const v of ['A', 'B', 'C', 'D']) for (let li = 0; li < 4; li++) {
    const d = await pg.evaluate(([v, li]) => { const c = document.getElementById('c'); drawBanner(c.getContext('2d'), v, li, A); return c.toDataURL('image/png'); }, [v, li]);
    fs.writeFileSync(path.join(out, `${v}_${li}.png`), Buffer.from(d.split(',')[1], 'base64'));
  }
  await br.close();
})();
