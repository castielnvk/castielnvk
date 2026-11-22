// Renders PNG exports and the animated end-card MP4 for the final Düymə olsa logo.
const {chromium} = require('playwright');
const fs = require('fs'), path = require('path'), {execFileSync} = require('child_process');
const D = __dirname, FPS = 30, DUR = 3.6;

(async () => {
  const b = await chromium.launch();
  // PNG exports (transparent where the SVG has no background)
  const png = [
    ['svg/avatar.svg', 'png/avatar-1080.png', 1080], ['svg/avatar.svg', 'png/avatar-320.png', 320],
    ['svg/logo-horizontal.svg', 'png/logo-horizontal.png'], ['svg/logo-horizontal-light.svg', 'png/logo-horizontal-light.png'],
    ['svg/logo-horizontal-transparent.svg', 'png/logo-horizontal-transparent.png'],
    ['svg/logo-stacked.svg', 'png/logo-stacked.png'], ['svg/logo-stacked-light.svg', 'png/logo-stacked-light.png'],
    ['svg/icon.svg', 'png/icon.png'], ['svg/icon-on-light.svg', 'png/icon-on-light.png'],
    ['svg/icon-mono-white.svg', 'png/icon-mono-white.png'], ['svg/icon-mono-navy.svg', 'png/icon-mono-navy.png'],
    ['svg/endcard.svg', 'png/endcard.png'],
  ];
  fs.mkdirSync(path.join(D, 'png'), {recursive: true});
  for (const [src, out, size] of png) {
    const s = fs.readFileSync(path.join(D, src), 'utf8');
    const [, w, h] = s.match(/width="(\d+)" height="(\d+)"/).map(Number);
    const scale = size ? size / w : (w >= 1080 ? 1 : 2);
    const p = await b.newPage({viewport: {width: Math.round(w * scale), height: Math.round(h * scale)}});
    await p.setContent(`<style>html,body{margin:0;background:transparent}svg{display:block;width:100%;height:100%}</style>${s}`);
    await p.screenshot({path: path.join(D, out), omitBackground: true});
    await p.close();
  }
  // Animated end-card frames
  const fr = path.join(D, 'anim', 'frames');
  fs.rmSync(fr, {recursive: true, force: true}); fs.mkdirSync(fr, {recursive: true});
  const p = await b.newPage({viewport: {width: 1080, height: 1920}});
  await p.goto('file://' + path.join(D, 'anim', 'endcard.html'));
  const N = Math.round(FPS * DUR);
  for (let i = 0; i < N; i++) {
    await p.evaluate(t => window.setT(t), i / FPS);
    await p.screenshot({path: path.join(fr, `f${String(i).padStart(4, '0')}.png`)});
  }
  await b.close();
  execFileSync('ffmpeg', ['-y', '-loglevel', 'error', '-framerate', String(FPS), '-i', path.join(fr, 'f%04d.png'),
    '-i', path.join(D, 'anim', 'click.wav'), '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '16', '-preset', 'slow',
    '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', '-ac', '2', '-shortest', '-movflags', '+faststart',
    path.join(D, 'Duyme_olsa_endcard_9x16.mp4')]);
  execFileSync('ffmpeg', ['-y', '-loglevel', 'error', '-framerate', String(FPS), '-i', path.join(fr, 'f%04d.png'),
    '-vf', 'fps=15,scale=360:-1:flags=lanczos,split[a][b];[a]palettegen[p];[b][p]paletteuse', path.join(D, 'anim', 'endcard-preview.gif')]);
  fs.rmSync(fr, {recursive: true, force: true});
  console.log('done');
})();
