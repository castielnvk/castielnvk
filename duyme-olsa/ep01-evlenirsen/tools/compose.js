// Composites the 3D plates with the HTML interface layer and encodes the final MP4 (no audio).
// Usage: node tools/compose.js [--preview SEC,SEC,...]   (preview writes PNGs to build/preview/)
const {chromium} = require('playwright');
const fs = require('fs'), path = require('path'), {execFileSync} = require('child_process');

const ROOT = path.join(__dirname, '..');
const E = JSON.parse(fs.readFileSync(path.join(ROOT, 'episode.json'), 'utf8'));
const FPS = E.fps, N = Math.round(E.duration * FPS), END = E.ui.end_card;
const BG = path.join(ROOT, 'build', 'bg');
const ENDCARD = path.join(ROOT, '..', 'logo', 'anim', 'endcard.html');
const OUT = path.join(ROOT, 'Duyme_olsa_Ep01_evlenirsen_9x16.mp4');

// Rendered 3D frames; held stretches reuse the nearest earlier rendered frame.
const rendered = fs.existsSync(BG) ? fs.readdirSync(BG).filter(f => /^bg_\d+\.png$/.test(f))
  .map(f => +f.match(/\d+/)[0]).sort((a, b) => a - b) : [];
const bgFor = frame => {  // frame is 1-based
  let best = rendered[0];
  for (const r of rendered) if (r <= frame) best = r; else break;
  return path.join(BG, `bg_${String(best).padStart(4, '0')}.png`);
};

(async () => {
  const args = process.argv.slice(2);
  const preview = args.includes('--preview') ? args[args.indexOf('--preview') + 1].split(',').map(Number) : null;
  const b = await chromium.launch();
  const ui = await b.newPage({viewport: {width: E.width, height: E.height}});
  await ui.addInitScript(ep => { window.EPISODE = ep; }, E);
  await ui.goto('file://' + path.join(ROOT, 'ui', 'overlay.html'));
  await ui.waitForFunction(() => window.UI_READY);
  await ui.evaluate(() => document.fonts.ready);
  const end = await b.newPage({viewport: {width: E.width, height: E.height}});
  await end.goto('file://' + ENDCARD);

  const outDir = path.join(ROOT, 'build', preview ? 'preview' : 'frames');
  fs.rmSync(outDir, {recursive: true, force: true}); fs.mkdirSync(outDir, {recursive: true});
  const times = preview || [...Array(N).keys()].map(i => i / FPS);
  let lastBg = null;
  for (let i = 0; i < times.length; i++) {
    const t = times[i];
    const file = path.join(outDir, preview ? `t_${t.toFixed(2)}.png` : `f${String(i).padStart(4, '0')}.png`);
    if (t < END) {
      const bg = bgFor(Math.round(t * FPS) + 1);
      if (bg !== lastBg) { await ui.evaluate(src => window.setBg(src), 'file://' + bg); lastBg = bg; }
      await ui.evaluate(tt => window.setT(tt), t);
      await ui.screenshot({path: file});
    } else {
      // brand end card: hard cut, the press + name land inside one second
      await end.evaluate(tt => window.setT(tt), 0.55 + (t - END) * 1.5);
      await end.screenshot({path: file});
    }
  }
  await b.close();
  if (preview) return console.log('preview written to', outDir);
  execFileSync('ffmpeg', ['-y', '-loglevel', 'error', '-framerate', String(FPS), '-i', path.join(outDir, 'f%04d.png'),
    '-an', '-c:v', 'libx264', '-profile:v', 'high', '-pix_fmt', 'yuv420p', '-crf', '17', '-preset', 'slow',
    '-movflags', '+faststart', '-vf', 'scale=1080:1920:flags=lanczos', OUT]);
  console.log('wrote', OUT);
})();
