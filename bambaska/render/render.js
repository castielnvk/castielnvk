// Melay — "Bambaşka biri" — cinematic kinetic-typography lyric video renderer (1920x1080, 30 fps).
// v2: forced-aligned word timing (words appear only when sung, letter by letter), illustrated
// backdrops per section, many more illustration elements, HUD details.
// Usage:
//   node render.js still OUTDIR t1 t2 ...        -> PNG stills
//   node render.js video F0 F1 OUT.mp4           -> frames [F0,F1) encoded to H.264 (no audio)
//   node render.js info
const { createCanvas, GlobalFonts } = require('@napi-rs/canvas');
const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');
const { lines: ALL_LINES, backing, DURATION } = require('./timeline');
const AUDIO = require('./audio.json');

const REEL = process.env.REEL === '1';
const W = REEL ? 1080 : 1920, H = REEL ? 1920 : 1080, FPS = 30;
const ARTIST = 'Melay', SONG = 'Bambaşka biri';
const F = (n) => path.join(__dirname, 'fonts', n);
GlobalFonts.registerFromPath(F('Anton_400Regular.ttf'), 'Anton');
GlobalFonts.registerFromPath(F('BigShouldersDisplay_900Black.ttf'), 'BSD');
GlobalFonts.registerFromPath(F('BigShouldersDisplay_300Light.ttf'), 'BSL');
GlobalFonts.registerFromPath(F('BebasNeue_400Regular.ttf'), 'Bebas');
GlobalFonts.registerFromPath(F('PlayfairDisplay_900Black_Italic.ttf'), 'PFB');
GlobalFonts.registerFromPath(F('PlayfairDisplay_600SemiBold_Italic.ttf'), 'PFS');
GlobalFonts.registerFromPath(F('PlayfairDisplay_400Regular_Italic.ttf'), 'PFR');
GlobalFonts.registerFromPath(F('Inter_500Medium.ttf'), 'Inter');

// ------------------------------------------------------------------ helpers
const clamp = (x, a = 0, b = 1) => Math.max(a, Math.min(b, x));
const lerp = (a, b, p) => a + (b - a) * p;
const TAU = Math.PI * 2;
const eOutCubic = (p) => 1 - Math.pow(1 - clamp(p), 3);
const eInCubic = (p) => Math.pow(clamp(p), 3);
const eInOut = (p) => { p = clamp(p); return p < 0.5 ? 16 * p ** 5 : 1 - Math.pow(-2 * p + 2, 5) / 2; };
const eInOut3 = (p) => { p = clamp(p); return p < 0.5 ? 4 * p ** 3 : 1 - Math.pow(-2 * p + 2, 3) / 2; };
const eOutBack = (p, s = 1.9) => { p = clamp(p) - 1; return 1 + (s + 1) * p ** 3 + s * p ** 2; };
function rng(seed) { let a = seed >>> 0; return () => { a |= 0; a = (a + 0x6D2B79F5) | 0; let t = Math.imul(a ^ (a >>> 15), 1 | a); t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; }; }
const hash = (n) => { const r = rng(n * 7919 + 13); r(); return r(); };
const up = (s) => s.toLocaleUpperCase('tr-TR');
function hexA(hex, a) { const n = parseInt(hex.slice(1), 16); return `rgba(${n >> 16},${(n >> 8) & 255},${n & 255},${a})`; }
function mixHex(h1, h2, p) {
  const a = parseInt(h1.slice(1), 16), b = parseInt(h2.slice(1), 16);
  const r = Math.round(lerp(a >> 16, b >> 16, p)), g = Math.round(lerp((a >> 8) & 255, (b >> 8) & 255, p)), bl = Math.round(lerp(a & 255, b & 255, p));
  return '#' + ((1 << 24) | (r << 16) | (g << 8) | bl).toString(16).slice(1);
}
const BEATS = AUDIO.beats;
function beatPulse(t, k = 7) {
  let lo = 0, hi = BEATS.length - 1, best = -1;
  while (lo <= hi) { const m = (lo + hi) >> 1; if (BEATS[m] <= t) { best = m; lo = m + 1; } else hi = m - 1; }
  if (best < 0) return 0;
  return Math.exp(-(t - BEATS[best]) * k);
}
const env = (arr, t) => arr[clamp(Math.floor(t * FPS), 0, arr.length - 1)] || 0;

// ------------------------------------------------------------------ palette
const C = {
  ink: '#15122C', night: '#0C0B1D', teal: '#2C6E6C', tealD: '#1C4C4D', berry: '#BD3550', berryD: '#6A1934',
  amber: '#F2B544', cream: '#F4E7D1', orange: '#E9773D', sky: '#86CFC4', black: '#07060E', red: '#FF5A5F', indigo: '#2f2968',
};
const SEC = {
  intro: { bg: C.ink, bg2: '#2a2350', fg: [C.cream], acc: C.amber, sh: '#0a0918' },
  v1: { bg: C.teal, bg2: '#3d8a85', fg: [C.cream, C.amber], acc: C.berry, sh: '#123c3c', style: 'rise', fonts: ['Anton', 'BSD', 'Bebas'], label: 'VERSE I' },
  pre: { bg: C.berryD, bg2: '#8f2747', fg: [C.amber, C.cream], acc: C.sky, sh: '#3a0c1d', style: 'pop', fonts: ['BSD', 'Anton', 'Bebas'], label: 'PRE-CHORUS' },
  ch: { bg: C.ink, bg2: '#2b2560', fg: [C.cream], acc: C.amber, sh: '#07060f', split: [C.cream, C.amber], disc: [C.indigo, C.teal, C.berryD], style: 'slam', fonts: ['Anton', 'BSD'], label: 'CHORUS' },
  v2: { bg: C.night, bg2: '#1f1c44', fg: [C.cream, '#d9cbb2'], acc: C.amber, sh: '#000000', style: 'rise', fonts: ['Bebas', 'Anton', 'BSD'], label: 'VERSE II' },
  q: { bg: '#3B0F23', bg2: '#64203c', fg: [C.cream, C.amber], acc: C.red, sh: '#1a0510', style: 'pop', fonts: ['Anton', 'BSD', 'Bebas'], label: 'VERSE II' },
  ch2: { bg: '#123c3c', bg2: '#1f5b59', fg: [C.cream], acc: C.amber, sh: '#061a1a', split: [C.amber, C.cream], disc: [C.berryD, C.ink, C.indigo], style: 'slam', fonts: ['BSD', 'Anton'], label: 'CHORUS' },
  br: { bg: C.black, bg2: '#1a1734', fg: [C.cream], acc: C.berry, sh: '#000000', style: 'flicker', fonts: ['Bebas', 'Anton', 'BSD'], label: 'BRIDGE' },
  fin: { bg: C.amber, bg2: '#ffd98a', fg: [C.ink, C.berryD], acc: C.berry, sh: '#b97d1c', split: [C.berry, C.ink], disc: [C.cream, C.orange, C.cream], style: 'slam', fonts: ['Anton', 'BSD'], label: 'FINAL CHORUS' },
  outro: { bg: C.ink, bg2: '#2a2350', fg: [C.cream], acc: C.amber, sh: '#0a0918' },
};

// ------------------------------------------------------------------ text metrics
const mctx = createCanvas(10, 10).getContext('2d');
const capCache = {};
function capH(font) {
  if (!capCache[font]) { mctx.font = `100px ${font}`; capCache[font] = mctx.measureText('H').actualBoundingBoxAscent / 100; }
  return capCache[font];
}
const wCache = {};
function w100(font, s) { const k = font + '|' + s; if (wCache[k] === undefined) { mctx.font = `100px ${font}`; wCache[k] = mctx.measureText(s).width; } return wCache[k]; }

// ------------------------------------------------------------------ build blocks
const STAMPS = ALL_LINES.filter((l) => l.fx === 'stamp');
const LINES = ALL_LINES.filter((l) => l.fx !== 'stamp');

function greedy(ws, maxc) {
  const rows = []; let cur = [], n = 0;
  for (const w of ws) {
    const c = w.text.length;
    if (cur.length && (n + c > maxc || cur.length >= 3)) { rows.push(cur); cur = []; n = 0; }
    cur.push(w); n += c + 1;
  }
  if (cur.length) rows.push(cur);
  return rows;
}
function rowsFor(line) {
  const ws = line.words;
  if (['tek', 'clash', 'head'].includes(line.fx)) return ws.map((w) => [w]);
  if (line.fx === 'split') { const r = [[ws[0]]]; if (ws.length > 1) r.push(...greedy(ws.slice(1), 11)); return r; }
  if (line.fx === 'echo') return [ws];
  return greedy(ws, line.words.length > 6 ? 13 : 11);
}

function layoutBlock(line, li) {
  const S = SEC[line.sec];
  const BW = line.fx === 'head' ? 560 : line.fx === 'clash' ? 900 : line.fx === 'bubble' ? 880 : 1000;
  const rows = rowsFor(line);
  const out = { line, rows: [], words: [] };
  let y = 0;
  rows.forEach((row, r) => {
    const font = S.fonts[(r + li) % S.fonts.length];
    const items = row.map((w) => {
      const acc = (line.accent || []).includes(w.text);
      return { w, f: acc ? 'PFB' : font, acc, txt: up(w.text) };
    });
    const sp = 22;
    const tot = items.reduce((a, it) => a + w100(it.f, it.txt), 0) + sp * (items.length - 1);
    const maxSize = line.fx === 'tek' ? 300 : line.fx === 'echo' ? 330 : 420;
    const size = Math.min((BW / tot) * 100, maxSize);
    const rowW = (tot * size) / 100;
    const ch = Math.max(...items.map((it) => capH(it.f))) * size;
    const top = y + (r ? 0.17 * size : 0);
    const base = top + ch;
    let x = -rowW / 2;
    items.forEach((it) => {
      const ww = (w100(it.f, it.txt) * size) / 100;
      const col = it.acc ? S.acc : S.fg[(r + li) % S.fg.length];
      // letter offsets
      const lx = []; let acc = '';
      for (const chr of it.txt) { lx.push((w100(it.f, acc) * size) / 100); acc += chr; }
      out.words.push({ ...it, x, base, size, ww, lx, ch: capH(it.f) * size, col, row: r, idx: out.words.length, t: it.w.t, e: it.w.e });
      x += ww + (sp * size) / 100;
    });
    out.rows.push({ top, base, size, rowW });
    y = base + 0.06 * size + 10;
  });
  const bh = y;
  out.words.forEach((w) => { w.base -= bh / 2; });
  out.rows.forEach((r) => { r.top -= bh / 2; r.base -= bh / 2; });
  out.tw = BW; out.th = bh; out.hw = BW / 2; out.hh = bh / 2;
  const pad = { l: 0, r: 0, t: 0, b: 0 };
  const fx = line.fx;
  if (fx === 'wing') pad.l = 640;
  if (fx === 'eye') pad.t = 600;
  if (fx === 'cage') { pad.l = pad.r = 110; pad.t = 300; pad.b = 90; }
  if (fx === 'arrows') { pad.l = pad.r = 380; }
  if (fx === 'moon') { pad.r = 420; pad.t = 420; }
  if (fx === 'split') { pad.t = 150; pad.b = 60; }
  if (fx === 'clash') { pad.t = pad.b = 120; pad.l = pad.r = 80; }
  if (fx === 'head') { out.headMirror = li % 2 === 1; pad.t = 190; pad.b = 330; pad.l = pad.r = 200; }
  if (fx === 'puppet') { pad.t = 420; pad.l = pad.r = 60; }
  if (fx === 'bubble') { pad.l = pad.r = 120; pad.t = 110; pad.b = 230; }
  if (fx === 'vines') { pad.l = pad.r = pad.t = pad.b = 110; }
  if (fx === 'clone') { pad.b = 180; }
  if (fx === 'dark') { pad.t = 470; }
  if (fx === 'brokenheart') { pad.r = 620; }
  if (fx === 'crumble') { pad.l = 520; }
  if (fx === 'hearts') { pad.l = pad.r = 160; pad.t = pad.b = 60; }
  if (fx === 'bigheart') { pad.t = pad.b = 80; }
  if (fx === 'tape') { pad.l = pad.r = 60; }
  out.pad = pad;
  out.bx0 = -out.hw - pad.l; out.bx1 = out.hw + pad.r; out.by0 = -out.hh - pad.t; out.by1 = out.hh + pad.b;
  return out;
}

const PATTERN = [
  { d: 'down', r: 0 }, { d: 'right', r: -90 }, { d: 'down', r: 0 }, { d: 'left', r: 90 }, { d: 'down', r: 0 },
  { d: 'right', r: 0 }, { d: 'down', r: 90 }, { d: 'right', r: -90 },
];
const SCALES = [1, 0.8, 1.15, 0.9, 1.3, 0.75, 1.05];

const BLOCKS = [];
(function place() {
  let prev = null;
  LINES.forEach((line, i) => {
    const b = layoutBlock(line, i);
    b.i = i;
    const newSec = !prev || prev.line.sec !== line.sec;
    b.scale = SCALES[i % SCALES.length];
    if (newSec) { b.x = 0; b.y = 0; b.rot = 0; b.k = 0; }
    else {
      const pat = PATTERN[(prev.k + 1 + i) % PATTERN.length];
      b.k = prev.k + 1;
      b.rot = prev.rot + (pat.r * Math.PI) / 180;
      const pr = prev.rot, ca = Math.cos(pr), sa = Math.sin(pr);
      const rel = pat.r !== 0;
      const nx = rel ? (b.by1 - b.by0) / 2 : (b.bx1 - b.bx0) / 2;
      const ny = rel ? (b.bx1 - b.bx0) / 2 : (b.by1 - b.by0) / 2;
      let ox = 0, oy = 0;
      const gap = 300;
      const pcx = (prev.bx0 + prev.bx1) / 2, pcy = (prev.by0 + prev.by1) / 2;
      if (pat.d === 'down') { oy = prev.by1 * prev.scale + gap + ny * b.scale; ox = pcx * prev.scale + (hash(i) - 0.5) * 300; }
      if (pat.d === 'right') { ox = prev.bx1 * prev.scale + gap + nx * b.scale; oy = pcy * prev.scale + (hash(i) - 0.5) * 200; }
      if (pat.d === 'left') { ox = prev.bx0 * prev.scale - gap - nx * b.scale; oy = pcy * prev.scale + (hash(i) - 0.5) * 200; }
      b.x = prev.x + ox * ca - oy * sa;
      b.y = prev.y + ox * sa + oy * ca;
    }
    const cxl = ((b.bx0 + b.bx1) / 2) * b.scale, cyl = ((b.by0 + b.by1) / 2) * b.scale;
    const c = Math.cos(b.rot), s = Math.sin(b.rot);
    const fitW = line.fx === 'split' ? 0.74 : 0.78, fitH = line.fx === 'split' ? 0.68 : 0.7;
    b.cam = {
      x: b.x + cxl * c - cyl * s, y: b.y + cxl * s + cyl * c, rot: b.rot,
      z: Math.min((W * fitW) / ((b.bx1 - b.bx0) * b.scale), (H * fitH) / ((b.by1 - b.by0) * b.scale)),
    };
    b.newSec = newSec;
    BLOCKS.push(b);
    prev = b;
  });
  BLOCKS.forEach((b, i) => {
    const p = BLOCKS[i - 1];
    const lastPrev = p ? p.line.words[p.line.words.length - 1].e : 0;
    if (b.newSec) {
      b.wipe0 = b.line.t - 0.42; b.wipe1 = b.line.t - 0.04; b.tIn = (b.wipe0 + b.wipe1) / 2; b.mv0 = b.mv1 = b.tIn;
    } else {
      // move only after the previous line has been sung; land just before the first word
      const D = clamp(b.line.t - lastPrev - 0.05, 0.26, 0.6);
      b.mv1 = b.line.t - 0.02; b.mv0 = b.mv1 - D; b.tIn = b.mv0;
    }
    b.lastT = b.line.words[b.line.words.length - 1].t;
  });
  BLOCKS.forEach((b, i) => { const n = BLOCKS[i + 1]; b.tOut = b.line.end || (n ? n.tIn : DURATION); });
})();

const INTRO_END = BLOCKS[0].tIn;
const OUTRO_START = BLOCKS[BLOCKS.length - 1].tOut;
function blockIndexAt(t) { let k = -1; for (let i = 0; i < BLOCKS.length; i++) if (BLOCKS[i].tIn <= t) k = i; return k; }

function heldCam(b, t) {
  const n = BLOCKS[b.i + 1];
  const tEnd = n && !n.newSec ? n.mv0 : b.tOut;
  const p = clamp((t - b.mv1) / Math.max(0.5, tEnd - b.mv1));
  let z = b.cam.z * (1 + 0.05 * eInOut3(p));
  if (b.newSec) z *= lerp(0.86, 1, eOutCubic((t - b.tIn) / 0.9));
  return { x: b.cam.x, y: b.cam.y, rot: b.cam.rot, z };
}
function angDiff(a, b) { let d = b - a; while (d > Math.PI) d -= TAU; while (d < -Math.PI) d += TAU; return d; }
function camAt(t, k) {
  const b = BLOCKS[k];
  if (!b.newSec && t < b.mv1) {
    const a = heldCam(BLOCKS[k - 1], b.mv0), c = heldCam(b, b.mv1);
    const e = eInOut((t - b.mv0) / (b.mv1 - b.mv0));
    const dist = Math.hypot(c.x - a.x, c.y - a.y);
    const pull = 1 - Math.min(0.35, dist / 9000) * Math.sin(Math.PI * e);
    return { x: lerp(a.x, c.x, e), y: lerp(a.y, c.y, e), rot: a.rot + angDiff(a.rot, c.rot) * e, z: Math.exp(lerp(Math.log(a.z), Math.log(c.z), e)) * pull, moving: true };
  }
  return { ...heldCam(b, t), moving: false };
}

const PUNCH = [];
LINES.forEach((l) => {
  if (l.fx === 'tek') l.words.forEach((w) => PUNCH.push([w.t, 0.07]));
  if (l.fx === 'split') PUNCH.push([l.t, 0.035]);
  if (l.fx === 'sun') PUNCH.push([l.words[1].t, 0.06]);
  if (l.fx === 'brokenheart') PUNCH.push([l.words[l.words.length - 1].t, 0.04]);
});
STAMPS.forEach((s) => PUNCH.push([s.t, 0.06]));
function punch(t) { let z = 0; for (const [te, a] of PUNCH) if (t >= te && t < te + 0.6) z += a * Math.exp(-(t - te) * 9); return z; }

// ------------------------------------------------------------------ textures
function makeGrain(seed) {
  const c = createCanvas(960, 540), x = c.getContext('2d');
  const id = x.createImageData(960, 540), r = rng(seed);
  for (let i = 0; i < id.data.length; i += 4) { const v = 128 + (r() + r() + r() - 1.5) * 120; id.data[i] = id.data[i + 1] = id.data[i + 2] = v; id.data[i + 3] = 255; }
  x.putImageData(id, 0, 0);
  return c;
}
const GRAIN = [1, 2, 3, 4, 5].map(makeGrain);
const VIG = (() => {
  const c = createCanvas(W, H), x = c.getContext('2d');
  const g = x.createRadialGradient(W / 2, H / 2, H * 0.35, W / 2, H / 2, H * 1.05);
  g.addColorStop(0, 'rgba(0,0,0,0)'); g.addColorStop(1, 'rgba(0,0,0,0.55)');
  x.fillStyle = g; x.fillRect(0, 0, W, H); return c;
})();
// halftone dot field (pre-rendered, drifted at draw time)
function makeHalftone(col, step, maxR) {
  const c = createCanvas(W + 2 * step, H + 2 * step), x = c.getContext('2d');
  x.fillStyle = col;
  for (let yy = 0; yy < c.height; yy += step) for (let xx = (yy / step) % 2 ? step / 2 : 0; xx < c.width; xx += step) {
    const d = Math.hypot(xx - c.width * 0.85, yy - c.height * 0.9) / (c.width * 1.0);
    const r = maxR * clamp(1 - d);
    if (r > 0.6) { x.beginPath(); x.arc(xx, yy, r, 0, TAU); x.fill(); }
  }
  return c;
}
const HT = { teal: makeHalftone('#3f8783', 34, 11), berry: makeHalftone('#7d2141', 34, 11), q: makeHalftone('#4f1530', 30, 10), ch2: makeHalftone('#1a4f4d', 34, 11) };

// ------------------------------------------------------------------ shape library
function headPath(ctx) {
  ctx.beginPath();
  ctx.moveTo(330, 1100);
  ctx.bezierCurveTo(330, 1000, 300, 930, 260, 880);
  ctx.bezierCurveTo(150, 800, 115, 640, 135, 500);
  ctx.bezierCurveTo(160, 250, 330, 70, 560, 60);
  ctx.bezierCurveTo(760, 50, 880, 170, 900, 330);
  ctx.bezierCurveTo(905, 380, 900, 410, 915, 440);
  ctx.bezierCurveTo(940, 480, 975, 540, 985, 580);
  ctx.bezierCurveTo(990, 600, 975, 615, 950, 618);
  ctx.bezierCurveTo(930, 620, 915, 625, 915, 640);
  ctx.bezierCurveTo(935, 655, 935, 675, 920, 688);
  ctx.bezierCurveTo(935, 700, 935, 720, 915, 735);
  ctx.bezierCurveTo(905, 745, 905, 760, 915, 775);
  ctx.bezierCurveTo(925, 820, 890, 860, 830, 870);
  ctx.bezierCurveTo(770, 880, 700, 880, 680, 900);
  ctx.bezierCurveTo(660, 950, 660, 1030, 670, 1100);
  ctx.closePath();
}
function drawHead(ctx, x, y, s, mirror, fill) {
  ctx.save(); ctx.translate(x, y); ctx.scale(mirror ? -s : s, s); ctx.translate(-560, -550);
  headPath(ctx); ctx.fillStyle = fill; ctx.fill(); ctx.restore();
}
function star4(ctx, x, y, r) {
  ctx.beginPath(); ctx.moveTo(x, y - r); ctx.quadraticCurveTo(x, y, x + r, y); ctx.quadraticCurveTo(x, y, x, y + r);
  ctx.quadraticCurveTo(x, y, x - r, y); ctx.quadraticCurveTo(x, y, x, y - r); ctx.fill();
}
function heartPath(ctx, s) {
  ctx.beginPath(); ctx.moveTo(0, s * 0.62);
  ctx.bezierCurveTo(-s * 1.15, -s * 0.12, -s * 0.58, -s * 0.98, 0, -s * 0.42);
  ctx.bezierCurveTo(s * 0.58, -s * 0.98, s * 1.15, -s * 0.12, 0, s * 0.62); ctx.closePath();
}
function heart(ctx, x, y, s, col) { ctx.save(); ctx.translate(x, y); heartPath(ctx, s); ctx.fillStyle = col; ctx.fill(); ctx.restore(); }
function brokenHeart(ctx, x, y, s, col, split, rotSplit = 0.25) {
  const zig = [[0, -0.42], [-0.12, -0.18], [0.1, 0.0], [-0.1, 0.2], [0.06, 0.4], [0, 0.62]];
  for (const side of [-1, 1]) {
    ctx.save(); ctx.translate(x + side * split * s * 0.5, y + split * s * 0.12);
    ctx.rotate(side * split * rotSplit);
    ctx.beginPath();
    ctx.moveTo(side * 2 * s, -s); ctx.lineTo(side * 2 * s, s);
    for (let k = zig.length - 1; k >= 0; k--) ctx.lineTo(zig[k][0] * s, zig[k][1] * s);
    ctx.closePath(); ctx.clip();
    heartPath(ctx, s); ctx.fillStyle = col; ctx.fill();
    ctx.restore();
  }
}
function feather(ctx, x, y, len, rot, col) {
  ctx.save(); ctx.translate(x, y); ctx.rotate(rot);
  ctx.fillStyle = col; ctx.beginPath(); ctx.ellipse(0, 0, len / 2, len * 0.14, 0, 0, TAU); ctx.fill();
  ctx.strokeStyle = 'rgba(0,0,0,0.25)'; ctx.lineWidth = Math.max(1, len * 0.025);
  ctx.beginPath(); ctx.moveTo(-len * 0.62, 0); ctx.lineTo(len * 0.45, 0); ctx.stroke();
  ctx.restore();
}
function flame(ctx, x, y, s, t, seed, colOut, colIn) {
  const f1 = Math.sin(t * 13 + seed) * 0.12, f2 = Math.sin(t * 9.3 + seed * 2) * 0.1;
  const draw = (k, col) => {
    ctx.fillStyle = col; ctx.beginPath(); ctx.moveTo(x - s * 0.5 * k, y);
    ctx.bezierCurveTo(x - s * 0.6 * k, y - s * 0.6 * k, x + (f1 - 0.1) * s, y - s * 0.7 * k, x + f2 * s, y - s * 1.4 * k);
    ctx.bezierCurveTo(x + s * (0.15 + f1) * k, y - s * 0.8 * k, x + s * 0.65 * k, y - s * 0.55 * k, x + s * 0.5 * k, y);
    ctx.closePath(); ctx.fill();
  };
  draw(1, colOut); draw(0.55, colIn);
}
function bird(ctx, x, y, s, phase, col) {
  const f = Math.sin(phase);
  ctx.strokeStyle = col; ctx.lineWidth = s * 0.14; ctx.lineCap = 'round'; ctx.lineJoin = 'round';
  ctx.beginPath(); ctx.moveTo(x - s, y - s * 0.5 * f); ctx.quadraticCurveTo(x - s * 0.45, y - s * 0.25 - s * 0.35 * f, x, y);
  ctx.quadraticCurveTo(x + s * 0.45, y - s * 0.25 - s * 0.35 * f, x + s, y - s * 0.5 * f); ctx.stroke();
}
function flower(ctx, x, y, s, rot, petal, center) {
  ctx.save(); ctx.translate(x, y); ctx.rotate(rot); ctx.fillStyle = petal;
  for (let k = 0; k < 5; k++) { ctx.rotate(TAU / 5); ctx.beginPath(); ctx.ellipse(0, -s * 0.55, s * 0.32, s * 0.55, 0, 0, TAU); ctx.fill(); }
  ctx.fillStyle = center; ctx.beginPath(); ctx.arc(0, 0, s * 0.28, 0, TAU); ctx.fill(); ctx.restore();
}
function sword(ctx, x, y, len, rot, blade, hilt) {
  ctx.save(); ctx.translate(x, y); ctx.rotate(rot);
  ctx.fillStyle = blade; ctx.beginPath(); ctx.moveTo(0, -len * 0.5); ctx.lineTo(len * 0.045, -len * 0.38); ctx.lineTo(len * 0.045, len * 0.22); ctx.lineTo(-len * 0.045, len * 0.22); ctx.lineTo(-len * 0.045, -len * 0.38); ctx.closePath(); ctx.fill();
  ctx.fillStyle = hilt; ctx.fillRect(-len * 0.17, len * 0.22, len * 0.34, len * 0.05);
  ctx.fillRect(-len * 0.03, len * 0.27, len * 0.06, len * 0.17);
  ctx.beginPath(); ctx.arc(0, len * 0.47, len * 0.045, 0, TAU); ctx.fill();
  ctx.restore();
}
function bulb(ctx, x, y, s, glow, lit) {
  ctx.save(); ctx.translate(x, y);
  if (glow > 0) {
    const g = ctx.createRadialGradient(0, 0, s * 0.3, 0, 0, s * 3.2);
    g.addColorStop(0, hexA(C.amber, 0.55 * glow)); g.addColorStop(1, hexA(C.amber, 0));
    ctx.fillStyle = g; ctx.fillRect(-s * 3.2, -s * 3.2, s * 6.4, s * 6.4);
  }
  ctx.fillStyle = mixHex('#3b3854', C.amber, lit);
  ctx.beginPath(); ctx.arc(0, 0, s, Math.PI * 0.8, Math.PI * 2.2); ctx.lineTo(s * 0.42, s * 1.15); ctx.lineTo(-s * 0.42, s * 1.15); ctx.closePath(); ctx.fill();
  ctx.strokeStyle = mixHex('#5d5873', '#fff6dc', lit); ctx.lineWidth = s * 0.06;
  ctx.beginPath(); ctx.moveTo(-s * 0.2, s * 1.1); ctx.lineTo(-s * 0.2, s * 0.2); ctx.lineTo(-s * 0.1, 0); ctx.lineTo(0, s * 0.2); ctx.lineTo(s * 0.1, 0); ctx.lineTo(s * 0.2, s * 0.2); ctx.lineTo(s * 0.2, s * 1.1); ctx.stroke();
  ctx.fillStyle = '#8c8aa0';
  for (let k = 0; k < 3; k++) ctx.fillRect(-s * 0.46, s * (1.17 + k * 0.17), s * 0.92, s * 0.12);
  ctx.fillStyle = '#5d5873'; ctx.beginPath(); ctx.arc(0, s * 1.72, s * 0.2, 0, Math.PI); ctx.fill();
  ctx.restore();
}
function rose(ctx, x, y, s, col, leaf) {
  ctx.save(); ctx.translate(x, y);
  ctx.strokeStyle = leaf; ctx.lineWidth = s * 0.08; ctx.beginPath(); ctx.moveTo(0, s * 0.4); ctx.quadraticCurveTo(s * 0.25, s * 1.5, -s * 0.05, s * 2.6); ctx.stroke();
  ctx.fillStyle = leaf; ctx.beginPath(); ctx.ellipse(s * 0.3, s * 1.4, s * 0.38, s * 0.15, -0.6, 0, TAU); ctx.fill();
  ctx.beginPath(); ctx.ellipse(-s * 0.15, s * 1.95, s * 0.34, s * 0.13, 0.7, 0, TAU); ctx.fill();
  ctx.fillStyle = col;
  ctx.beginPath(); ctx.moveTo(-s * 0.7, -s * 0.3); ctx.quadraticCurveTo(-s * 0.75, s * 0.6, 0, s * 0.6); ctx.quadraticCurveTo(s * 0.75, s * 0.6, s * 0.7, -s * 0.3);
  ctx.quadraticCurveTo(s * 0.35, 0, 0, -s * 0.45); ctx.quadraticCurveTo(-s * 0.35, 0, -s * 0.7, -s * 0.3); ctx.fill();
  ctx.strokeStyle = 'rgba(0,0,0,0.28)'; ctx.lineWidth = s * 0.05;
  ctx.beginPath(); ctx.arc(0, 0, s * 0.28, 0.2, Math.PI * 1.6); ctx.stroke();
  ctx.beginPath(); ctx.arc(0, 0.05 * s, s * 0.48, 0.6, Math.PI - 0.2); ctx.stroke();
  ctx.restore();
}
function polaroid(ctx, x, y, s, rot, k, t) {
  ctx.save(); ctx.translate(x, y); ctx.rotate(rot);
  ctx.fillStyle = 'rgba(0,0,0,0.35)'; ctx.fillRect(-s * 0.5 + 10, -s * 0.6 + 12, s, s * 1.2);
  ctx.fillStyle = C.cream; ctx.fillRect(-s * 0.5, -s * 0.6, s, s * 1.2);
  const ix = -s * 0.43, iy = -s * 0.53, iw = s * 0.86, ih = s * 0.86;
  const bgs = [C.indigo, C.berryD, C.tealD, '#3b2a1a'];
  ctx.fillStyle = bgs[k % 4]; ctx.fillRect(ix, iy, iw, ih);
  ctx.save(); ctx.beginPath(); ctx.rect(ix, iy, iw, ih); ctx.clip(); ctx.translate(ix + iw / 2, iy + ih / 2);
  const m = k % 4;
  if (m === 0) { ctx.fillStyle = C.amber; ctx.beginPath(); ctx.arc(0, ih * 0.1, iw * 0.25, Math.PI, 0); ctx.fill(); ctx.fillStyle = C.tealD; ctx.fillRect(-iw / 2, ih * 0.1, iw, ih); }
  if (m === 1) { heart(ctx, 0, 0, iw * 0.28, C.berry); }
  if (m === 2) { ctx.fillStyle = C.cream; ctx.beginPath(); ctx.arc(-iw * 0.15, -ih * 0.05, iw * 0.09, 0, TAU); ctx.arc(iw * 0.15, -ih * 0.05, iw * 0.09, 0, TAU); ctx.fill(); ctx.fillRect(-iw * 0.25, ih * 0.05, iw * 0.2, ih * 0.4); ctx.fillRect(iw * 0.05, ih * 0.05, iw * 0.2, ih * 0.4); }
  if (m === 3) { ctx.fillStyle = C.amber; ctx.beginPath(); ctx.arc(iw * 0.2, -ih * 0.2, iw * 0.15, 0, TAU); ctx.fill(); ctx.fillStyle = C.ink; ctx.beginPath(); ctx.arc(iw * 0.27, -ih * 0.25, iw * 0.13, 0, TAU); ctx.fill(); }
  ctx.restore();
  // fading: memories burn out
  ctx.fillStyle = `rgba(20,16,30,${0.25 + 0.2 * Math.sin(t * 2 + k)})`; ctx.fillRect(ix, iy, iw, ih);
  ctx.restore();
}
function cloud(ctx, x, y, s, col) {
  ctx.fillStyle = col; ctx.beginPath();
  ctx.arc(x, y, s * 0.5, Math.PI, 0); ctx.arc(x + s * 0.55, y + s * 0.1, s * 0.38, Math.PI, 0); ctx.arc(x - s * 0.55, y + s * 0.12, s * 0.33, Math.PI, 0);
  ctx.rect(x - s * 0.9, y + s * 0.1, s * 1.85, s * 0.2); ctx.fill();
}

// ------------------------------------------------------------------ word rendering (letter by letter, only when sung)
function letterTimes(wd) {
  const n = wd.lx.length;
  const dur = clamp((wd.e || wd.t + 0.3) - wd.t, 0.12, 0.5);
  return (j) => wd.t + (dur * j) / n;
}
function drawWord(ctx, wd, t, style, col, S, opts = {}) {
  if (t < wd.t - 0.02) return;
  ctx.font = `${wd.size}px ${wd.f}`;
  const lt = letterTimes(wd);
  const ext = opts.noExtrude ? 0 : Math.max(3, Math.round(wd.size * 0.035));
  const chars = [...wd.txt];
  const shCol = opts.shadow || S.sh;
  // highlight marker behind accent words (grows as the word is sung)
  if (wd.acc && !opts.noMarker) {
    const p = eOutCubic((t - wd.t) / 0.45);
    ctx.save(); ctx.fillStyle = hexA(opts.marker || S.fg[0], 0.16);
    ctx.beginPath(); const y0 = wd.base - wd.ch * 0.55, hh = wd.ch * 0.62;
    ctx.moveTo(wd.x - 14, y0 + 6); ctx.lineTo(wd.x - 14 + (wd.ww + 28) * p, y0); ctx.lineTo(wd.x - 14 + (wd.ww + 28) * p, y0 + hh); ctx.lineTo(wd.x - 14, y0 + hh + 6); ctx.fill(); ctx.restore();
  }
  chars.forEach((chr, j) => {
    const ta = lt(j);
    const p = (t - ta) / 0.22;
    if (p <= 0) return;
    const cw = (w100(wd.f, chr) * wd.size) / 100;
    const lx = wd.x + wd.lx[j];
    const cx = lx + cw / 2, cy = wd.base - wd.ch / 2;
    ctx.save();
    if (style === 'rise') {
      ctx.beginPath(); ctx.rect(lx - 6, wd.base - wd.ch - 0.32 * wd.size, cw + 12 + ext, wd.ch + 0.62 * wd.size + ext); ctx.clip();
      ctx.translate(0, (1 - eOutCubic(p)) * (wd.ch + 0.4 * wd.size));
    } else if (style === 'pop') {
      const s = lerp(0.2, 1, eOutBack(p, 2.4));
      ctx.translate(cx, cy); ctx.scale(s, s); ctx.rotate((1 - eOutCubic(p)) * (j % 2 ? 0.35 : -0.35)); ctx.translate(-cx, -cy);
      ctx.globalAlpha *= clamp(p * 4);
    } else if (style === 'slam') {
      const s = lerp(1.9, 1, eOutCubic(p * 1.3));
      ctx.translate(cx, cy); ctx.scale(s, s); ctx.translate(-cx, -cy);
      ctx.globalAlpha *= clamp(p * 4);
    } else if (style === 'flicker') {
      const fr = Math.floor((t - ta) * 30);
      if (fr < 6 && [1, 0, 1, 0, 1, 1][Math.max(0, fr)] === 0) { ctx.restore(); return; }
      ctx.translate(0, (1 - eOutCubic(p)) * 26);
    } else if (style === 'drop') {
      ctx.translate(0, (1 - eOutBack(p, 1.6)) * -wd.size * 0.6); ctx.globalAlpha *= clamp(p * 3);
    }
    if (opts.stroke) { ctx.lineWidth = opts.stroke; ctx.strokeStyle = col; ctx.strokeText(chr, lx, wd.base); ctx.restore(); return; }
    if (ext) { ctx.fillStyle = shCol; for (let k = ext; k >= 1; k -= Math.max(1, Math.floor(ext / 6))) ctx.fillText(chr, lx + k, wd.base + k); }
    ctx.fillStyle = col; ctx.fillText(chr, lx, wd.base);
    ctx.restore();
  });
}
function drawWordWhole(ctx, wd, col, opt = {}) {
  ctx.font = `${wd.size}px ${wd.f}`;
  if (opt.stroke) { ctx.lineWidth = opt.stroke; ctx.strokeStyle = col; ctx.lineJoin = 'round'; ctx.strokeText(wd.txt, wd.x, wd.base); return; }
  ctx.fillStyle = col; ctx.fillText(wd.txt, wd.x, wd.base);
}
function drawSplitWord(ctx, wd, t, S) {
  // identity split, revealed left->right as it is sung (karaoke wipe), halves slide on the beat
  if (t < wd.t - 0.02) return;
  const age = t - wd.t;
  const dur = clamp(wd.e - wd.t, 0.25, 0.8);
  const rev = eOutCubic(age / dur);
  const s = lerp(1.25, 1, eOutCubic(age / 0.25));
  const cx = wd.x + wd.ww / 2, cy = wd.base - wd.ch / 2;
  ctx.translate(cx, cy); ctx.scale(s, s); ctx.translate(-cx, -cy);
  const dx = 70 * Math.exp(-age * 5) + 10 * beatPulse(t) + 4;
  const midY = wd.base - wd.ch * 0.5;
  const topY = wd.base - wd.ch - wd.size * 0.4;
  ctx.font = `${wd.size}px ${wd.f}`;
  ctx.save(); ctx.beginPath(); ctx.rect(wd.x - 200, topY, 200 + (wd.ww + 200) * rev, wd.size * 1.6); ctx.clip();
  const ext = Math.round(wd.size * 0.03);
  ctx.save(); ctx.beginPath(); ctx.rect(wd.x - 300, topY, wd.ww + 600, midY - topY); ctx.clip();
  ctx.fillStyle = S.sh; for (let k = ext; k >= 1; k -= 2) ctx.fillText(wd.txt, wd.x - dx + k, wd.base + k);
  ctx.fillStyle = S.split[0]; ctx.fillText(wd.txt, wd.x - dx, wd.base); ctx.restore();
  ctx.save(); ctx.beginPath(); ctx.rect(wd.x - 300, midY, wd.ww + 600, wd.size); ctx.clip();
  ctx.fillStyle = S.sh; for (let k = ext; k >= 1; k -= 2) ctx.fillText(wd.txt, wd.x + dx + k, wd.base + k);
  ctx.fillStyle = S.split[1]; ctx.fillText(wd.txt, wd.x + dx, wd.base); ctx.restore();
  ctx.fillStyle = S.fg[0]; ctx.globalAlpha *= 0.85; ctx.fillRect(wd.x - 40 - dx, midY - 2, (wd.ww + 80 + 2 * dx) * rev, 4);
  ctx.restore();
}
function drawCrumbleWord(ctx, wd, t, col, S) {
  if (t < wd.t - 0.02) return;
  const lt = letterTimes(wd);
  ctx.font = `${wd.size}px ${wd.f}`;
  const start = wd.t + 0.85;
  [...wd.txt].forEach((chr, j) => {
    const ta = lt(j); if (t < ta) return;
    const pApp = clamp((t - ta) / 0.15);
    const x = wd.x + wd.lx[j];
    const cw = (w100(wd.f, chr) * wd.size) / 100;
    const ts = start + j * 0.035 + hash(wd.idx * 31 + j) * 0.12;
    const tau = Math.max(0, t - ts);
    ctx.save();
    ctx.globalAlpha *= pApp * (1 - clamp(tau / 0.9));
    const dy = 0.5 * 3200 * tau * tau, rot = tau * (hash(j + wd.idx * 3) - 0.5) * 6;
    ctx.translate(x + cw / 2, wd.base - wd.ch / 2 + dy); ctx.rotate(rot);
    ctx.fillStyle = S.sh; ctx.fillText(chr, -cw / 2 + 4, wd.ch / 2 + 4);
    ctx.fillStyle = col; ctx.fillText(chr, -cw / 2, wd.ch / 2);
    ctx.restore();
  });
}

// ------------------------------------------------------------------ per-block decor
function firstT(L) { return L.words[0].t; }
function lastW(L) { return L.words[L.words.length - 1]; }

function decorUnder(ctx, b, t, S) {
  const L = b.line, fx = L.fx;
  // small icons scattered around every block (pop in with the first sung word, then bob)
  scatterIcons(ctx, b, t, S);
  if (fx === 'split') {
    const col = S.disc[b.i % S.disc.length];
    const p = eOutBack((t - firstT(L) + 0.1) / 0.45, 1.4);
    const r = Math.max(b.tw, b.th) * 0.62 * p * (1 + 0.025 * beatPulse(t));
    if (L.sec === 'fin') drawWings(ctx, t, r, p);
    // rotating rays of the "mirror"
    ctx.save(); ctx.rotate(t * 0.15 + b.i); ctx.fillStyle = hexA(S.fg[0], 0.06);
    for (let k = 0; k < 12; k++) { ctx.beginPath(); ctx.moveTo(0, 0); ctx.arc(0, 0, Math.max(1, r * 2.6), (k * TAU) / 12, ((k + 0.45) * TAU) / 12); ctx.closePath(); ctx.fill(); }
    ctx.restore();
    ctx.fillStyle = col; ctx.beginPath(); ctx.arc(0, 0, Math.max(0, r), 0, TAU); ctx.fill();
    // mirror cracks radiating from the disc
    ctx.save(); ctx.strokeStyle = hexA(S.fg[0], 0.35); ctx.lineWidth = 3;
    const R = rng(b.i * 11 + 5);
    for (let k = 0; k < 9; k++) {
      const a = R() * TAU, l = r * (0.5 + R() * 0.6) * clamp((t - firstT(L)) / 0.3);
      ctx.beginPath(); ctx.moveTo(Math.cos(a) * r * 0.25, Math.sin(a) * r * 0.25);
      ctx.lineTo(Math.cos(a + 0.08) * l * 0.6, Math.sin(a + 0.08) * l * 0.6); ctx.lineTo(Math.cos(a - 0.04) * l, Math.sin(a - 0.04) * l); ctx.stroke();
    }
    ctx.restore();
    ctx.strokeStyle = hexA(S.fg[0], 0.35); ctx.lineWidth = 4; ctx.beginPath(); ctx.arc(0, 0, Math.max(0, r * 1.12), 0, TAU); ctx.stroke();
    ctx.setLineDash([6, 18]); ctx.beginPath(); ctx.arc(0, 0, Math.max(0, r * 1.25), t * 0.3, t * 0.3 + TAU); ctx.stroke(); ctx.setLineDash([]);
  }
  if (fx === 'hearts') {
    L.words.forEach((w, k) => {
      const p = eOutBack((t - w.t) / 0.35, 2.5); if (p <= 0) return;
      const side = k % 2 ? 1 : -1;
      const x = side * (b.hw + 70 + 40 * hash(k + b.i)), y = (hash(k * 3 + b.i) - 0.5) * b.th * 0.9;
      const s = (38 + 30 * hash(k * 7)) * p * (1 + 0.08 * beatPulse(t));
      heart(ctx, x, y - (t - w.t) * 18, s, k % 2 ? C.berry : C.amber);
    });
  }
  if (fx === 'bigheart') {
    const w = L.words[1];
    const p = eOutBack((t - w.t) / 0.4, 1.8); if (p > 0) {
      const s = Math.max(b.tw, b.th) * 0.42 * p * (1 + 0.06 * beatPulse(t, 9));
      ctx.save(); ctx.translate(0, b.th * 0.05); heartPath(ctx, s); ctx.fillStyle = C.berry; ctx.fill();
      ctx.lineWidth = 8; ctx.strokeStyle = hexA(C.cream, 0.5); ctx.setLineDash([14, 16]); heartPath(ctx, s * 1.12); ctx.stroke(); ctx.setLineDash([]); ctx.restore();
    }
  }
  if (fx === 'wing') {
    const tk = L.words[1].t;
    const crack = eOutBack((t - tk) / 0.5, 1.2);
    const ox = -b.hw - 340, oy = 20;
    for (let f = 0; f < 9; f++) {
      const outer = f >= 5;
      ctx.save(); ctx.translate(ox, oy);
      if (outer) { ctx.translate(-60, 40); ctx.rotate(crack * 0.42); ctx.translate(crack * -20, crack * 120); ctx.translate(60, -40); }
      ctx.rotate(-0.95 + f * 0.2 + Math.PI);
      const appear = eOutBack((t - firstT(L) + 0.1 - f * 0.04) / 0.4, 1.5);
      ctx.scale(appear, appear);
      const len = 260 + f * 22;
      ctx.fillStyle = S.sh; ctx.beginPath(); ctx.ellipse(len / 2 + 6, 8, len / 2, 34, 0, 0, TAU); ctx.fill();
      ctx.fillStyle = f % 2 ? C.cream : C.amber; ctx.beginPath(); ctx.ellipse(len / 2, 0, len / 2, 34, 0, 0, TAU); ctx.fill();
      ctx.restore();
    }
    ctx.fillStyle = C.berry; ctx.beginPath(); ctx.arc(ox + 40, oy - 10, 80 * eOutBack((t - firstT(L) + 0.1) / 0.4), 0, TAU); ctx.fill();
    if (t > tk) {
      ctx.strokeStyle = C.ink; ctx.lineWidth = 12; ctx.beginPath();
      const pts = [[-120, -260], [-150, -170], [-100, -110], [-170, -20], [-120, 40], [-180, 140]];
      const n = Math.min(pts.length, 1 + Math.floor((t - tk) / 0.03));
      pts.slice(0, n).forEach(([x, y], k) => (k ? ctx.lineTo(ox + x, oy + y) : ctx.moveTo(ox + x, oy + y)));
      ctx.stroke();
      // loose feathers falling
      for (let k = 0; k < 4; k++) { const tau = t - tk - k * 0.15; if (tau > 0) feather(ctx, ox - 150 + k * 40, oy + 100 + tau * 160, 90, 1.2 + Math.sin(tau * 3 + k) * 0.6, C.cream); }
    }
  }
  if (fx === 'eye') {
    const ey = -b.hh - 220, ew = 780, eh = 300;
    const app = eOutCubic((t - firstT(L) + 0.1) / 0.5);
    const tk = L.words[2].t;
    const squint = eInOut3((t - tk) / 0.35);
    const open = app * lerp(1, 0.42, squint);
    ctx.save(); ctx.translate(0, ey);
    // lashes
    ctx.strokeStyle = S.fg[0]; ctx.lineWidth = 10; ctx.lineCap = 'round';
    for (let k = -3; k <= 3; k++) { const a = k * 0.22; ctx.beginPath(); ctx.moveTo(Math.sin(a) * ew * 0.42, -eh * open * 0.5 - 10); ctx.lineTo(Math.sin(a) * ew * 0.5, -eh * open * 0.5 - 60 * open); ctx.stroke(); }
    ctx.beginPath(); ctx.moveTo(-ew / 2, 0); ctx.quadraticCurveTo(0, -eh * open, ew / 2, 0); ctx.quadraticCurveTo(0, eh * open * 0.8, -ew / 2, 0); ctx.closePath();
    ctx.fillStyle = C.cream; ctx.fill();
    ctx.save(); ctx.clip();
    const look = Math.sin((t - firstT(L)) * 2.2) * 120 + squint * 150;
    ctx.fillStyle = C.amber; ctx.beginPath(); ctx.arc(look, 0, 115, 0, TAU); ctx.fill();
    ctx.strokeStyle = hexA(C.orange, 0.8); ctx.lineWidth = 6; for (let k = 0; k < 12; k++) { const a = (k * TAU) / 12; ctx.beginPath(); ctx.moveTo(look + Math.cos(a) * 60, Math.sin(a) * 60); ctx.lineTo(look + Math.cos(a) * 105, Math.sin(a) * 105); ctx.stroke(); }
    ctx.fillStyle = C.ink; ctx.beginPath(); ctx.arc(look, 0, 52, 0, TAU); ctx.fill();
    ctx.fillStyle = C.cream; ctx.beginPath(); ctx.arc(look + 30, -30, 16, 0, TAU); ctx.fill();
    ctx.restore();
    ctx.strokeStyle = C.ink; ctx.lineWidth = 16;
    ctx.beginPath(); ctx.moveTo(-ew / 2 - 20, 0); ctx.quadraticCurveTo(0, -eh * open - 10, ew / 2 + 20, 0); ctx.stroke();
    ctx.lineWidth = 26; ctx.strokeStyle = S.fg[0];
    ctx.beginPath(); ctx.moveTo(-ew * 0.45, -eh * 0.62 + squint * 40); ctx.quadraticCurveTo(0, -eh * 0.95 + squint * 30, ew * 0.45, -eh * 0.6 + squint * 110); ctx.stroke();
    ctx.restore();
  }
  if (fx === 'moon') {
    const app = eOutCubic((t - firstT(L) + 0.2) / 1.0);
    const mx = b.hw + 170, my = -b.hh - 140, mr = 240;
    ctx.save(); ctx.globalAlpha *= app;
    const g = ctx.createRadialGradient(mx, my, mr * 0.6, mx, my, mr * 2.2);
    g.addColorStop(0, hexA(C.amber, 0.22)); g.addColorStop(1, hexA(C.amber, 0)); ctx.fillStyle = g;
    ctx.fillRect(mx - mr * 2.2, my - mr * 2.2, mr * 4.4, mr * 4.4);
    ctx.save(); ctx.beginPath(); ctx.arc(mx, my, mr, 0, TAU); ctx.clip();
    ctx.beginPath(); ctx.arc(mx, my, mr, 0, TAU); ctx.arc(mx + mr * 0.45, my - mr * 0.25, mr * 0.88, 0, TAU);
    ctx.fillStyle = C.amber; ctx.fill('evenodd'); ctx.restore();
    cloud(ctx, mx - 60 + Math.sin(t * 0.4) * 30, my + mr * 0.55, 260, hexA('#2c2856', 0.95));
    ctx.restore();
  }
  if (fx === 'vines') {
    // thorny vines wrapping the block as the fear "wraps" (sardı)
    const p = clamp((t - firstT(L)) / (lastW(L).e - firstT(L) + 0.3));
    const x0 = -b.hw - 70, x1 = b.hw + 70, y0 = -b.hh - 70, y1 = b.hh + 70;
    for (const side of [0, 1]) {
      ctx.save(); ctx.strokeStyle = side ? '#3f7a3a' : '#2c5a2a'; ctx.lineWidth = 14; ctx.lineCap = 'round';
      ctx.beginPath();
      const N = 120;
      for (let k = 0; k <= N * p; k++) {
        const u = k / N; // around the rectangle perimeter, wavy
        const per = 2 * (x1 - x0) + 2 * (y1 - y0); let d = ((u + side * 0.5) % 1) * per;
        let x, y;
        if (d < x1 - x0) { x = x0 + d; y = y0; } else if ((d -= x1 - x0) < y1 - y0) { x = x1; y = y0 + d; } else if ((d -= y1 - y0) < x1 - x0) { x = x1 - d; y = y1; } else { d -= x1 - x0; x = x0; y = y1 - d; }
        const wob = Math.sin(u * 60 + side * 2) * 26;
        x += (x === x0 || x === x1 ? wob : 0); y += (y === y0 || y === y1 ? wob : 0);
        k ? ctx.lineTo(x, y) : ctx.moveTo(x, y);
        if (k % 8 === 4) { ctx.save(); ctx.fillStyle = C.berry; ctx.translate(x, y); ctx.rotate(u * 40); ctx.beginPath(); ctx.moveTo(-8, 0); ctx.lineTo(0, -26); ctx.lineTo(8, 0); ctx.fill(); ctx.restore(); }
      }
      ctx.stroke(); ctx.restore();
    }
  }
  if (fx === 'clone') {
    const tk = L.words[2].t;
    const src = b.words[1];
    const R = rng(4242);
    for (let k = 0; k < 22; k++) {
      const ta = tk + k * 0.045;
      const px = (R() - 0.5) * b.tw * 2.2, py = (R() - 0.5) * b.th * 2.4, rr = (R() - 0.5) * 0.5, sc = 0.25 + R() * 0.4;
      if (t < ta) continue;
      const e = eOutBack((t - ta) / 0.25, 2);
      ctx.save(); ctx.translate(px, py); ctx.rotate(rr); ctx.scale(sc * e, sc * e);
      ctx.font = `${src.size}px ${src.f}`; ctx.textAlign = 'center';
      if (k % 3 === 0) { ctx.lineWidth = 6; ctx.strokeStyle = C.berry; ctx.strokeText(src.txt, 0, src.ch / 2); }
      else { ctx.fillStyle = k % 2 ? C.berry : hexA(C.amber, 0.85); ctx.fillText(src.txt, 0, src.ch / 2); }
      ctx.restore();
    }
    // anger flames under the block, from "öfke"
    const pf = eOutCubic((t - src.t) / 0.4);
    if (pf > 0) for (let k = 0; k < 9; k++) {
      const x = lerp(-b.hw, b.hw, k / 8), s = (90 + 60 * hash(k + 3)) * pf * (1 + 0.15 * env(AUDIO.low, t));
      flame(ctx, x, b.hh + 170, s, t, k, C.berry, C.amber);
    }
  }
  if (fx === 'dark') {
    // the light bulb dies as the light "sinks into darkness"
    const t0 = firstT(L), t1 = L.words[2].t + 0.35;
    const p = clamp((t - t0) / (t1 - t0));
    const flick = p > 0.45 && p < 0.95 ? (hash(Math.floor(t * 20)) > 0.45 ? 1 : 0.2) : 1;
    const lit = (1 - eInCubic(p)) * flick;
    bulb(ctx, 0, -b.hh - 260, 130, lit, lit);
    const r = lerp(Math.max(b.tw, b.th) * 0.75, 0, eInCubic(p)) * (1 + 0.03 * beatPulse(t));
    ctx.fillStyle = hexA(C.amber, 0.9); ctx.beginPath(); ctx.arc(0, 0, Math.max(0, r), 0, TAU); ctx.fill();
  }
  if (fx === 'qmarks') {
    const R = rng(b.i * 17 + 3);
    for (let k = 0; k < 9; k++) {
      const ta = firstT(L) + k * 0.12; if (t < ta) continue;
      const px = (R() - 0.5) * b.tw * 1.8, py = (R() - 0.5) * b.th * 2.4, sz = 200 + R() * 320, rr = (R() - 0.5) * 0.7;
      const e = eOutBack((t - ta) / 0.35, 2);
      ctx.save(); ctx.translate(px, py); ctx.rotate(rr + Math.sin(t * 0.8 + k) * 0.08); ctx.scale(e, e);
      ctx.font = `${sz}px PFB`; ctx.textAlign = 'center';
      if (k % 2) { ctx.fillStyle = hexA(C.red, 0.55); ctx.fillText('?', 0, sz * 0.35); }
      else { ctx.lineWidth = 5; ctx.strokeStyle = hexA(C.cream, 0.5); ctx.strokeText('?', 0, sz * 0.35); }
      ctx.restore();
    }
  }
  if (fx === 'bubble') {
    const p = eOutBack((t - firstT(L) + 0.05) / 0.4, 1.6);
    if (p > 0) {
      ctx.save(); ctx.scale(p, p);
      const x0 = -b.hw - 90, x1 = b.hw + 90, y0 = -b.hh - 80, y1 = b.hh + 70, r = 60;
      const path = () => {
        ctx.beginPath(); ctx.moveTo(x0 + r, y0); ctx.lineTo(x1 - r, y0); ctx.quadraticCurveTo(x1, y0, x1, y0 + r); ctx.lineTo(x1, y1 - r); ctx.quadraticCurveTo(x1, y1, x1 - r, y1);
        ctx.lineTo(-b.hw * 0.2, y1); ctx.lineTo(-b.hw * 0.55, y1 + 150); ctx.lineTo(-b.hw * 0.45, y1); ctx.lineTo(x0 + r, y1); ctx.quadraticCurveTo(x0, y1, x0, y1 - r); ctx.lineTo(x0, y0 + r); ctx.quadraticCurveTo(x0, y0, x0 + r, y0); ctx.closePath();
      };
      ctx.translate(14, 14); path(); ctx.fillStyle = S.sh; ctx.fill(); ctx.translate(-14, -14);
      path(); ctx.fillStyle = '#8f2747'; ctx.fill(); ctx.lineWidth = 8; ctx.strokeStyle = C.amber; ctx.stroke();
      ctx.restore();
    }
  }
  if (fx === 'brokenheart') {
    const hx = b.hw + 330, hy = 0, s = 230;
    const p = eOutBack((t - firstT(L)) / 0.4, 1.8);
    if (p > 0) {
      const crackT = lastW(L).t;
      const sp = eOutBack((t - crackT) / 0.5, 1.4);
      ctx.save(); ctx.translate(hx, hy); ctx.scale(p, p);
      if (t < crackT) heart(ctx, 0, 0, s * (1 + 0.06 * beatPulse(t, 9)), C.red);
      else brokenHeart(ctx, 0, 0, s, C.red, sp * 0.35);
      ctx.restore();
    }
  }
  if (fx === 'crumble') {
    // a rose losing its petals
    const rx = -b.hw - 260, ry = -b.hh * 0.6;
    const p = eOutCubic((t - firstT(L)) / 0.5);
    if (p > 0) {
      ctx.save(); ctx.globalAlpha *= p; rose(ctx, rx, ry, 150, C.red, '#3f7a3a'); ctx.restore();
      for (let k = 0; k < 10; k++) {
        const tau = t - firstT(L) - 0.3 - k * 0.25; if (tau < 0) continue;
        const x = rx + Math.sin(tau * 2 + k) * 80 + (hash(k) - 0.5) * 120, y = ry + 40 + tau * 260;
        ctx.save(); ctx.translate(x, y); ctx.rotate(tau * 3 + k); ctx.fillStyle = hexA(C.red, 1 - clamp(tau / 2.5));
        ctx.beginPath(); ctx.ellipse(0, 0, 26, 14, 0, 0, TAU); ctx.fill(); ctx.restore();
      }
    }
  }
  if (fx === 'head') {
    const cols = [C.berryD, '#22385a', C.berryD, '#2a2a52'];
    const app = eOutCubic((t - b.tIn) / 0.6);
    ctx.save(); ctx.globalAlpha *= app;
    ctx.save(); ctx.translate(b.headMirror ? 40 : -40, 0); drawHeadOutline(ctx, b, t); ctx.restore();
    drawHead(ctx, 0, 170, 1.12, b.headMirror, cols[b.i % cols.length]);
    ctx.restore();
  }
  if (fx === 'clash') {
    const R = rng(b.i * 5 + 1);
    ctx.save(); ctx.globalAlpha *= 0.5;
    const fr = Math.floor(t * 8);
    for (let k = 0; k < 5; k++) {
      const s = 0.25 + 0.75 * R();
      ctx.strokeStyle = k % 2 ? C.berry : C.sky; ctx.lineWidth = 3;
      ctx.save(); ctx.translate((hash(fr * 3 + k) - 0.5) * 30, (hash(fr * 5 + k) - 0.5) * 30);
      ctx.beginPath(); ctx.arc((R() - 0.5) * 900, (R() - 0.5) * 600, 200 * s + 60, 0, TAU); ctx.stroke(); ctx.restore();
    }
    ctx.restore();
    // memories flying around the words
    L.words.forEach((w, k) => {
      const p = eOutBack((t - w.t) / 0.4, 1.6); if (p <= 0) return;
      for (let j = 0; j < 2; j++) {
        const side = (k + j) % 2 ? 1 : -1;
        polaroid(ctx, side * (b.hw + 40 + j * 120), (k - 1) * b.th * 0.33 + j * 60, 170 * p, side * (0.2 + 0.1 * j) + Math.sin(t + k) * 0.05, k * 2 + j, t);
      }
    });
  }
  if (fx === 'sun') {
    const ts = L.words[1].t;
    const p = clamp((t - ts + 0.05) / 0.9);
    if (p > 0) {
      const R0 = 5000 * eOutCubic(p);
      ctx.fillStyle = mixHex(C.berryD, C.amber, eOutCubic(p)); ctx.beginPath(); ctx.arc(0, 0, R0, 0, TAU); ctx.fill();
      ctx.save(); ctx.rotate((t - ts) * 0.12); ctx.fillStyle = hexA('#ffd98a', 0.85 * eOutCubic(p));
      for (let k = 0; k < 18; k++) { ctx.beginPath(); ctx.moveTo(0, 0); ctx.arc(0, 0, R0, (k * TAU) / 18, ((k + 0.5) * TAU) / 18); ctx.closePath(); ctx.fill(); }
      ctx.restore();
      ctx.fillStyle = C.cream; ctx.beginPath(); ctx.arc(0, 0, 330 * eOutBack(p * 1.5, 1.3), 0, TAU); ctx.fill();
      for (let k = 0; k < 7; k++) { const tau = t - ts - 0.2 - k * 0.12; if (tau > 0) bird(ctx, -700 + tau * 420 + k * 90, -300 - k * 40 - tau * 60, 34, t * 10 + k, C.ink); }
    }
  }
  if (fx === 'echo') {
    for (let k = 0; k < 6; k++) {
      const te = firstT(L) + 0.6 + k * 0.87;
      const age = t - te; if (age < 0 || age > 2.4) continue;
      const s = 1 + age * 0.35, a = (1 - age / 2.4) * 0.6;
      ctx.save(); ctx.scale(s, s); ctx.globalAlpha *= a;
      b.words.forEach((w) => drawWordWhole(ctx, w, S.acc, { stroke: 5 / s }));
      ctx.restore();
    }
    drawWings(ctx, t, 560, eOutCubic((t - firstT(L)) / 0.8));
  }
}
function drawWings(ctx, t, r, p) {
  // the broken wing from verse 1, healed: two full wings beating slowly behind the disc
  if (p <= 0) return;
  const flap = Math.sin(t * 2.4) * 0.12;
  for (const side of [-1, 1]) {
    ctx.save(); ctx.scale(side, 1); ctx.translate(r * 0.55, -r * 0.05); ctx.rotate(-flap);
    for (let f = 0; f < 9; f++) {
      ctx.save(); ctx.rotate(-0.95 + f * 0.2); const len = (r * 0.75 + f * r * 0.06) * p;
      ctx.fillStyle = 'rgba(120,70,10,0.35)'; ctx.beginPath(); ctx.ellipse(len / 2 + 8, 8, len / 2, r * 0.075, 0, 0, TAU); ctx.fill();
      ctx.fillStyle = f % 2 ? C.cream : '#fff3dc'; ctx.beginPath(); ctx.ellipse(len / 2, 0, len / 2, r * 0.075, 0, 0, TAU); ctx.fill();
      ctx.restore();
    }
    ctx.restore();
  }
}
function drawHeadOutline(ctx, b, t) {
  const s = 1.12;
  ctx.save(); ctx.translate(0, 170); ctx.scale(b.headMirror ? -s : s, s); ctx.translate(-560, -550);
  const fr = Math.floor(t * 8);
  ctx.translate((hash(fr) - 0.5) * 18, (hash(fr + 99) - 0.5) * 18);
  headPath(ctx); ctx.lineWidth = 6; ctx.strokeStyle = hexA(C.sky, 0.6); ctx.stroke(); ctx.restore();
}

// small decorative icons around each block — they appear with the line's first sung word
function scatterIcons(ctx, b, t, S) {
  const L = b.line, sec = L.sec;
  if (['head', 'sun', 'dark'].includes(L.fx)) return;
  const R = rng(b.i * 97 + 11);
  const n = 8;
  const t0 = firstT(L);
  for (let k = 0; k < n; k++) {
    const ang = (k / n) * TAU + R() * 0.5;
    const rx = (b.bx1 - b.bx0) * 0.5 + 120 + R() * 160, ry = (b.by1 - b.by0) * 0.5 + 90 + R() * 120;
    const cxb = (b.bx0 + b.bx1) / 2, cyb = (b.by0 + b.by1) / 2;
    const x = cxb + Math.cos(ang) * rx, y = cyb + Math.sin(ang) * ry + Math.sin(t * 1.3 + k) * 10;
    const p = eOutBack((t - t0 - k * 0.06) / 0.35, 2); if (p <= 0) continue;
    const s = (22 + R() * 26) * p; const rot = R() * TAU + t * 0.3 * (k % 2 ? 1 : -1);
    ctx.save(); ctx.globalAlpha *= 0.9;
    const kind = { v1: ['heart', 'feather', 'spark'], pre: ['spark', 'ring', 'tri'], ch: ['shard', 'spark', 'ring'], v2: ['spark', 'spark', 'dot'], q: ['q', 'spark', 'tri'], ch2: ['shard', 'spark', 'ring'], br: ['ring', 'dot', 'spark'], fin: ['flower', 'spark', 'heart'] }[sec] || ['spark'];
    const kd = kind[k % kind.length];
    const col = [S.fg[0], S.acc, S.fg[S.fg.length - 1]][k % 3];
    ctx.fillStyle = col; ctx.strokeStyle = col; ctx.lineWidth = 5;
    if (kd === 'heart') heart(ctx, x, y, s, col);
    else if (kd === 'feather') feather(ctx, x, y, s * 3, rot, col);
    else if (kd === 'spark') star4(ctx, x, y, s * 1.1);
    else if (kd === 'ring') { ctx.beginPath(); ctx.arc(x, y, s * 0.8, 0, TAU); ctx.stroke(); }
    else if (kd === 'dot') { ctx.beginPath(); ctx.arc(x, y, s * 0.35, 0, TAU); ctx.fill(); }
    else if (kd === 'tri') { ctx.save(); ctx.translate(x, y); ctx.rotate(rot); ctx.beginPath(); ctx.moveTo(0, -s); ctx.lineTo(s * 0.9, s * 0.6); ctx.lineTo(-s * 0.9, s * 0.6); ctx.closePath(); ctx.stroke(); ctx.restore(); }
    else if (kd === 'shard') { ctx.save(); ctx.translate(x, y); ctx.rotate(rot); ctx.globalAlpha *= 0.7; ctx.beginPath(); ctx.moveTo(0, -s * 1.6); ctx.lineTo(s * 0.7, s * 0.4); ctx.lineTo(-s * 0.5, s); ctx.closePath(); ctx.fill(); ctx.restore(); }
    else if (kd === 'flower') flower(ctx, x, y, s * 1.4, rot, C.cream, C.berry);
    else if (kd === 'q') { ctx.font = `${s * 3}px PFB`; ctx.textAlign = 'center'; ctx.fillText('?', x, y + s); }
    ctx.restore();
  }
}

function decorOver(ctx, b, t, S) {
  const L = b.line, fx = L.fx;
  if (fx === 'echo') {
    [[175.0, -420, 330], [176.4, 380, -300], [176.6, 60, 420]].forEach(([te, x, y], k) => {
      const age = t - te; if (age < 0 || age > 1.6) return;
      const a = clamp(age / 0.15) * (1 - clamp((age - 0.8) / 0.8));
      ctx.save(); ctx.globalAlpha *= a; ctx.font = `${130 - k * 20}px PFB`; ctx.textAlign = 'center'; ctx.fillStyle = k === 1 ? C.berry : C.ink;
      ctx.fillText(up('biri'), x, y - age * 30); ctx.restore();
    });
  }
  if (fx === 'cage') {
    const x0 = -b.hw - 80, x1 = b.hw + 80, yb = b.hh + 60, yt = -b.hh - 40;
    const n = 9;
    ctx.strokeStyle = C.amber; ctx.lineCap = 'round';
    for (let k = 0; k < n; k++) {
      const ta = firstT(L) + 0.05 * k;
      const p = eOutCubic((t - ta) / 0.35); if (p <= 0) continue;
      const x = lerp(x0, x1, k / (n - 1));
      const dome = Math.sqrt(Math.max(0, 1 - Math.pow((x / (x1 - x0)) * 2, 2)));
      const top = yt - 220 * dome;
      ctx.lineWidth = 16; ctx.beginPath(); ctx.moveTo(x, top); ctx.lineTo(x, lerp(top, yb, p)); ctx.stroke();
    }
    const pa = eOutCubic((t - firstT(L) - 0.35) / 0.35);
    if (pa > 0) {
      ctx.save(); ctx.globalAlpha *= pa; ctx.lineWidth = 22;
      ctx.beginPath(); ctx.moveTo(x0 - 30, yb); ctx.lineTo(x1 + 30, yb); ctx.stroke();
      ctx.lineWidth = 16; ctx.beginPath(); ctx.ellipse(0, yt, (x1 - x0) / 2, 220, 0, Math.PI, TAU); ctx.stroke();
      ctx.beginPath(); ctx.arc(0, yt - 270, 46, 0, TAU); ctx.stroke();
      // little caged bird on a swing
      const sw = Math.sin(t * 2.2) * 0.25;
      ctx.save(); ctx.translate(0, yt - 160); ctx.rotate(sw);
      ctx.lineWidth = 5; ctx.beginPath(); ctx.moveTo(-50, 0); ctx.lineTo(-50, 120); ctx.moveTo(50, 0); ctx.lineTo(50, 120); ctx.stroke();
      ctx.lineWidth = 10; ctx.beginPath(); ctx.moveTo(-70, 120); ctx.lineTo(70, 120); ctx.stroke();
      ctx.fillStyle = C.berry; ctx.beginPath(); ctx.ellipse(0, 92, 40, 28, 0, 0, TAU); ctx.fill();
      ctx.beginPath(); ctx.arc(30, 62, 20, 0, TAU); ctx.fill();
      ctx.fillStyle = C.amber; ctx.beginPath(); ctx.moveTo(48, 58); ctx.lineTo(66, 64); ctx.lineTo(48, 70); ctx.fill();
      ctx.fillStyle = C.ink; ctx.beginPath(); ctx.arc(34, 58, 4, 0, TAU); ctx.fill();
      ctx.restore();
      ctx.restore();
    }
  }
  if (fx === 'arrows') {
    L.words.forEach((w, wi) => {
      if (!/suçlandım/.test(w.text)) return;
      for (let k = 0; k < 3; k++) {
        const ta = w.t + k * 0.07; const p = eOutBack((t - ta) / 0.3, 1.6); if (p <= 0) continue;
        const side = wi < 2 ? -1 : 1;
        const yy = (k - 1) * b.th * 0.36 + (wi < 2 ? -40 : 40);
        ctx.save(); ctx.translate(side * (b.hw + 40) + side * (1 - p) * 500, yy); ctx.scale(side, 1);
        ctx.fillStyle = S.sh; ctx.translate(8, 8);
        const arrow = () => { ctx.beginPath(); ctx.moveTo(0, 0); ctx.lineTo(90, -55); ctx.lineTo(90, -20); ctx.lineTo(330, -20); ctx.lineTo(330, 20); ctx.lineTo(90, 20); ctx.lineTo(90, 55); ctx.closePath(); ctx.fill(); };
        arrow(); ctx.translate(-8, -8); ctx.fillStyle = k === 1 ? C.amber : C.cream; arrow();
        ctx.restore();
      }
    });
  }
  if (fx === 'puppet') {
    // marionette control bar with strings to the words (used like a puppet)
    const p = eOutCubic((t - firstT(L) + 0.05) / 0.4);
    const sw = Math.sin(t * 2.6) * 0.07;
    const by = -b.hh - 300;
    ctx.save(); ctx.globalAlpha *= p; ctx.translate(0, by - (1 - p) * 200); ctx.rotate(sw);
    ctx.fillStyle = S.sh; ctx.fillRect(-b.hw * 0.75 + 8, -16 + 8, b.hw * 1.5, 32); ctx.fillRect(-16 + 8, -120 + 8, 32, 240);
    ctx.fillStyle = '#c98a3a'; ctx.fillRect(-b.hw * 0.75, -16, b.hw * 1.5, 32); ctx.fillRect(-16, -120, 32, 240);
    ctx.restore();
    ctx.save(); ctx.strokeStyle = hexA(C.cream, 0.8); ctx.lineWidth = 3;
    b.words.forEach((wd, k) => {
      if (t < wd.t) return;
      const ax = lerp(-b.hw * 0.7, b.hw * 0.7, b.words.length > 1 ? k / (b.words.length - 1) : 0.5);
      const axr = ax * Math.cos(sw), ayr = by + ax * Math.sin(sw);
      ctx.beginPath(); ctx.moveTo(axr, ayr); ctx.lineTo(wd.x + wd.ww / 2, wd.base - wd.ch); ctx.stroke();
    });
    ctx.restore();
  }
  if (fx === 'tape') {
    // patched-up "repair" tape strips that don't hold (Tamiri yok gibi)
    const tk = L.words[1].t;
    [[-0.35, 0], [0.32, 1]].forEach(([rot, k]) => {
      const p = eOutCubic((t - tk - k * 0.12) / 0.25); if (p <= 0) return;
      const peel = clamp((t - lastW(L).t - 0.3) / 0.6);
      ctx.save(); ctx.rotate(rot + peel * 0.3 * (k ? 1 : -1)); ctx.translate(peel * 40, peel * 80);
      const L2 = (b.tw + 160) * p;
      ctx.fillStyle = hexA('#e9dcc0', 0.82); ctx.beginPath();
      ctx.moveTo(-L2 / 2, -42); for (let j = 0; j <= 6; j++) ctx.lineTo(-L2 / 2 + (j % 2 ? 10 : 0), -42 + j * 14);
      ctx.lineTo(L2 / 2, 42); for (let j = 6; j >= 0; j--) ctx.lineTo(L2 / 2 - (j % 2 ? 10 : 0), -42 + j * 14);
      ctx.closePath(); ctx.fill();
      ctx.restore();
    });
  }
  if (fx === 'strike') {
    const wd = b.words[1];
    const p = eOutCubic((t - wd.t - 0.35) / 0.4); if (p > 0) {
      ctx.fillStyle = C.sky; ctx.save(); ctx.translate(wd.x - 20, wd.base - wd.ch * 0.45); ctx.rotate(-0.04);
      ctx.fillRect(0, -8, (wd.ww + 40) * p, 16); ctx.restore();
    }
  }
}

// ------------------------------------------------------------------ block drawing
function drawBlock(ctx, b, t, S) {
  ctx.save();
  ctx.translate(b.x, b.y); ctx.rotate(b.rot); ctx.scale(b.scale, b.scale);
  const L = b.line;
  decorUnder(ctx, b, t, S);
  if (L.fx === 'head') {
    ctx.save(); ctx.translate(0, 170); ctx.scale(b.headMirror ? -1.12 : 1.12, 1.12); ctx.translate(-560, -550); headPath(ctx); ctx.restore();
    ctx.save(); ctx.clip();
  }
  const style = S.style || 'rise';
  for (const wd of b.words) {
    if (t < wd.t - 0.02) continue; // never show a word before it is sung
    ctx.save();
    let col = wd.col;
    if (L.fx === 'sun' && t > L.words[1].t) col = wd.acc ? C.berry : C.ink;
    if (L.fx === 'dark') { const p = clamp((t - L.words[2].t) / 0.6); col = mixHex(C.ink, '#2a2745', p); }
    if (L.fx === 'crumble') { drawCrumbleWord(ctx, wd, t, col, S); ctx.restore(); continue; }
    if (L.fx === 'split' && wd.row === 0) { drawSplitWord(ctx, wd, t, S); ctx.restore(); continue; }
    if (L.fx === 'clash') {
      const fr = Math.floor(t * 8);
      ctx.translate((hash(fr * 13 + wd.idx) - 0.5) * 16, (hash(fr * 7 + wd.idx) - 0.5) * 16);
      const cx = wd.x + wd.ww / 2, cy = wd.base - wd.ch / 2;
      ctx.translate(cx, cy); ctx.rotate((hash(wd.idx + 50) - 0.5) * 0.12 + (hash(fr + wd.idx) - 0.5) * 0.03); ctx.translate(-cx, -cy);
      ctx.save(); ctx.globalAlpha *= 0.8; ctx.translate(-9, 0); drawWord(ctx, wd, t, 'flicker', C.berry, S, { noExtrude: true }); ctx.translate(18, 0); drawWord(ctx, wd, t, 'flicker', C.sky, S, { noExtrude: true }); ctx.restore();
    }
    if (L.fx === 'head') col = C.cream;
    if (L.fx === 'echo') col = S.fg[0];
    const st = L.fx === 'tek' ? 'slam' : L.fx === 'puppet' ? 'drop' : L.fx === 'bubble' ? 'pop' : style;
    if (L.fx === 'puppet' && t > wd.t) { // words dangle on their strings
      const cx = wd.x + wd.ww / 2, cy = wd.base - wd.ch;
      ctx.translate(cx, cy); ctx.rotate(Math.sin(t * 2.6 + wd.idx) * 0.05); ctx.translate(-cx, -cy);
    }
    drawWord(ctx, wd, t, st, col, S, { marker: L.sec === 'fin' ? C.cream : undefined });
    ctx.restore();
  }
  if (L.fx === 'head') ctx.restore();
  decorOver(ctx, b, t, S);
  ctx.restore();
}

// ------------------------------------------------------------------ screen-space backdrops (each section gets its own world)
function drawBG(ctx, t, S) {
  ctx.fillStyle = S.bg; ctx.fillRect(0, 0, W, H);
  const gx = W * (0.5 + 0.28 * Math.sin(t * 0.13)), gy = H * (0.45 + 0.2 * Math.cos(t * 0.17));
  const g = ctx.createRadialGradient(gx, gy, 0, gx, gy, H * 1.1);
  g.addColorStop(0, hexA(S.bg2, 0.9)); g.addColorStop(1, hexA(S.bg2, 0));
  ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
}
function drawHalftone(ctx, img, t, alpha) {
  ctx.save(); ctx.globalAlpha = alpha; ctx.drawImage(img, -34 + Math.sin(t * 0.2) * 30, -34 + Math.cos(t * 0.17) * 30); ctx.restore();
}
const SKY = (() => { const R = rng(99); return Array.from({ length: 140 }, () => [R() * W, R() * H * 0.75, 1 + R() * 2.6, R() * TAU]); })();
const CITY = (() => {
  const R = rng(7); const b = []; let x = -40;
  while (x < W + 40) { const w = 60 + R() * 110, h = 120 + R() * 330; b.push({ x, w, h, win: Array.from({ length: 40 }, () => R()) , ant: R() > 0.7 }); x += w + 4; }
  return b;
})();
function drawCity(ctx, t, redness, off) {
  CITY.forEach((bd, i) => {
    const y = H - bd.h;
    ctx.fillStyle = '#121029'; ctx.fillRect(bd.x, y, bd.w, bd.h);
    if (bd.ant) { ctx.fillRect(bd.x + bd.w / 2 - 2, y - 60, 4, 60); ctx.fillStyle = hash(Math.floor(t * 2) + i) > 0.5 ? C.red : '#5a1020'; ctx.beginPath(); ctx.arc(bd.x + bd.w / 2, y - 62, 5, 0, TAU); ctx.fill(); }
    let k = 0;
    for (let yy = y + 18; yy < H - 20; yy += 34) for (let xx = bd.x + 12; xx < bd.x + bd.w - 18; xx += 26) {
      const v = bd.win[k++ % 40];
      const on = v > 0.55 && hash(i * 131 + k + Math.floor(t * 0.5 + v * 5)) > 0.25 && v > off;
      if (!on) continue;
      ctx.fillStyle = mixHex('#f2c867', C.red, redness); ctx.globalAlpha = 0.75; ctx.fillRect(xx, yy, 12, 16); ctx.globalAlpha = 1;
    }
  });
}
function drawStrings(ctx, t, col) {
  ctx.save(); ctx.strokeStyle = col; ctx.lineWidth = 2;
  for (let k = 0; k < 14; k++) {
    const x = (k + 0.5) * (W / 14) + Math.sin(t * 0.7 + k) * 20; const len = 250 + 500 * hash(k + 4);
    const sw = Math.sin(t * 1.1 + k * 1.7) * 30;
    ctx.beginPath(); ctx.moveTo(x, 0); ctx.quadraticCurveTo(x + sw * 0.3, len * 0.5, x + sw, len); ctx.stroke();
    ctx.beginPath(); ctx.arc(x + sw, len + 8, 8, 0, TAU); ctx.stroke();
  }
  ctx.restore();
}
function drawRain(ctx, t, col, n = 90) {
  ctx.save(); ctx.strokeStyle = col; ctx.lineWidth = 2;
  for (let k = 0; k < n; k++) {
    const sp = 900 + 500 * hash(k);
    const x = ((hash(k * 3) * (W + 400) + t * 140) % (W + 400)) - 200;
    const y = ((hash(k * 7) * (H + 300) + t * sp) % (H + 300)) - 150;
    ctx.beginPath(); ctx.moveTo(x, y); ctx.lineTo(x - 12, y + 46); ctx.stroke();
  }
  ctx.restore();
}
function drawFallingFeathers(ctx, t, col) {
  for (let k = 0; k < 7; k++) {
    const sp = 40 + 30 * hash(k);
    const y = ((hash(k * 5) * (H + 300) + t * sp) % (H + 300)) - 150;
    const x = hash(k * 9) * W + Math.sin(t * 0.9 + k) * 60;
    ctx.save(); ctx.globalAlpha = 0.35; feather(ctx, x, y, 90 + 50 * hash(k + 2), Math.sin(t * 0.9 + k) * 0.8 + 0.5, col); ctx.restore();
  }
}
function drawFloatingShards(ctx, t, col) {
  for (let k = 0; k < 12; k++) {
    const x = ((hash(k) * (W + 300) + t * (20 + 30 * hash(k + 1)) * (k % 2 ? 1 : -1)) % (W + 300) + W + 300) % (W + 300) - 150;
    const y = hash(k * 3) * H + Math.sin(t * 0.5 + k) * 30;
    const s = 30 + 70 * hash(k * 5);
    ctx.save(); ctx.translate(x, y); ctx.rotate(t * 0.2 * (k % 2 ? 1 : -1) + k);
    ctx.globalAlpha = 0.18; ctx.fillStyle = col; ctx.beginPath(); ctx.moveTo(0, -s); ctx.lineTo(s * 0.6, s * 0.4); ctx.lineTo(-s * 0.5, s * 0.7); ctx.closePath(); ctx.fill();
    ctx.globalAlpha = 0.4; ctx.strokeStyle = col; ctx.lineWidth = 2; ctx.stroke();
    ctx.restore();
  }
}
function drawPolaroidDrift(ctx, t) {
  for (let k = 0; k < 7; k++) {
    const depth = 0.4 + 0.6 * hash(k + 20);
    const x = ((hash(k) * (W + 600) + t * 25 * depth) % (W + 600)) - 300;
    const y = hash(k * 3) * H * 0.9 + 60 + Math.sin(t * 0.4 + k) * 20;
    ctx.save(); ctx.globalAlpha = 0.25 + 0.25 * depth; polaroid(ctx, x, y, 140 * depth + 60, Math.sin(t * 0.3 + k) * 0.3, k, t); ctx.restore();
  }
}
function drawFinBackdrop(ctx, t) {
  ctx.save(); ctx.translate(W / 2, H * 0.55); ctx.rotate(t * 0.05); ctx.fillStyle = 'rgba(255,240,200,0.22)';
  for (let k = 0; k < 20; k++) { ctx.beginPath(); ctx.moveTo(0, 0); ctx.arc(0, 0, 2400, (k * TAU) / 20, ((k + 0.5) * TAU) / 20); ctx.closePath(); ctx.fill(); }
  ctx.restore();
  // birds crossing (the wing has healed)
  for (let k = 0; k < 9; k++) {
    const x = ((hash(k) * (W + 400) + t * (110 + 60 * hash(k + 3))) % (W + 400)) - 200;
    const y = 120 + hash(k * 3) * 320 + Math.sin(t * 1.5 + k) * 18;
    bird(ctx, x, y, 22 + 16 * hash(k * 5), t * 9 + k * 2, hexA(C.ink, 0.6));
  }
  // flowers at the bottom corners
  for (let k = 0; k < 9; k++) {
    const side = k % 2 ? 1 : -1;
    const x = side > 0 ? W - 40 - (k >> 1) * 70 : 40 + (k >> 1) * 70;
    const y = H - 30 - hash(k) * 90;
    flower(ctx, x, y, 34 + 20 * hash(k + 7), t * 0.4 * side + k, k % 3 ? C.cream : C.berry, k % 3 ? C.orange : C.cream);
  }
}

function drawBackdrop(ctx, t, b) {
  const sec = b.line.sec;
  if (sec === 'v1') { drawHalftone(ctx, HT.teal, t, 0.8); drawFallingFeathers(ctx, t, C.cream); }
  if (sec === 'pre') { drawHalftone(ctx, HT.berry, t, 0.8); drawStrings(ctx, t, hexA(C.amber, 0.22)); }
  if (sec === 'ch' || sec === 'ch2') { if (sec === 'ch2') drawHalftone(ctx, HT.ch2, t, 0.8); drawFloatingShards(ctx, t, sec === 'ch' ? C.amber : C.cream); }
  if (sec === 'v2') {
    ctx.fillStyle = C.cream;
    SKY.forEach(([x, y, r, ph]) => { ctx.globalAlpha = 0.25 + 0.5 * (0.5 + 0.5 * Math.sin(t * 2 + ph)); ctx.beginPath(); ctx.arc(x, y, r, 0, TAU); ctx.fill(); });
    ctx.globalAlpha = 1;
    for (let k = 0; k < 4; k++) cloud(ctx, ((hash(k) * (W + 600) + t * 18) % (W + 600)) - 300, 120 + k * 120, 200 + 80 * hash(k + 1), hexA('#24204a', 0.8));
    const red = b.line.fx === 'clone' || b.line.fx === 'clone2' ? eOutCubic((t - firstT(b.line)) / 1.0) : 0;
    const off = b.line.fx === 'dark' ? clamp((t - firstT(b.line)) / 1.6) : 0;
    drawCity(ctx, t, red, off);
  }
  if (sec === 'q') { drawHalftone(ctx, HT.q, t, 0.8); drawRain(ctx, t, 'rgba(244,231,209,0.16)'); }
  if (sec === 'br') { drawPolaroidDrift(ctx, t); }
  if (sec === 'fin') drawFinBackdrop(ctx, t);
}

function drawMarquee(ctx, t, b) {
  const L = b.line;
  const n = clamp(Math.floor((t - firstT(L)) / 0.2) + 1, 0, 10);
  if (t < firstT(L)) return;
  ctx.save();
  ctx.font = '120px Anton';
  const word = up('çoğaldı') + '  ';
  const ww = ctx.measureText(word).width;
  for (let r = 0; r < n; r++) {
    const y = 120 + r * 108;
    const dir = r % 2 ? 1 : -1;
    const off = ((t * 260 * dir) % ww + ww) % ww;
    ctx.globalAlpha = 0.16 + 0.06 * (r % 3);
    if (r % 2) { ctx.fillStyle = C.berry; for (let x = -ww + off; x < W; x += ww) ctx.fillText(word, x, y); }
    else { ctx.lineWidth = 3; ctx.strokeStyle = C.amber; for (let x = -ww + off; x < W; x += ww) ctx.strokeText(word, x, y); }
  }
  ctx.restore();
}
function drawDarkOverlay(ctx, t, b) {
  const L = b.line;
  const t0 = firstT(L), t1 = L.words[2].t + 0.35;
  const p = clamp((t - t0) / (t1 - t0));
  const r = lerp(1300, 40, eInCubic(p));
  const g = ctx.createRadialGradient(W / 2, H / 2, r * 0.35, W / 2, H / 2, r);
  g.addColorStop(0, 'rgba(0,0,0,0)'); g.addColorStop(1, `rgba(0,0,0,${0.35 + 0.6 * p})`);
  ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
  const fade = clamp((t - t1) / 0.4);
  if (fade > 0) { ctx.fillStyle = `rgba(0,0,0,${fade * 0.9})`; ctx.fillRect(0, 0, W, H); }
}

function drawBacking(ctx, t, S) {
  for (const bk of backing) {
    if (t < bk.t0 || t > bk.t1 + 0.4) continue;
    const txt = bk.text;
    const size = REEL ? 54 : 68;
    ctx.save();
    ctx.font = `${size}px PFS`;
    const tw = ctx.measureText(txt).width;
    const x0 = W / 2 - tw / 2, y = REEL ? H * 0.685 : H - 74;
    const out = clamp((t - bk.t1) / 0.4);
    const light = S.bg === C.amber;
    ctx.shadowColor = light ? 'rgba(255,240,210,0.6)' : 'rgba(0,0,0,0.7)'; ctx.shadowBlur = 18;
    const pr = eOutCubic((t - bk.t0) / 0.5);
    ctx.fillStyle = hexA(light ? C.ink : C.amber, 0.9 * (1 - out));
    ctx.fillRect(W / 2 - (tw / 2 + 40) * pr, y + 24, (tw + 80) * pr, 3);
    // icon to the left of the line
    if (bk.icon) {
      const ip = eOutBack((t - bk.t0) / 0.4, 2) * (1 - out);
      ctx.save(); ctx.translate(x0 - 70, y - 24); ctx.scale(ip, ip); ctx.shadowBlur = 0;
      if (bk.icon === 'swords') { sword(ctx, 0, 0, 96, 0.7, light ? C.ink : C.cream, C.berry); sword(ctx, 0, 0, 96, -0.7, light ? C.ink : C.cream, C.amber); }
      else brokenHeart(ctx, 0, 0, 30, C.red, 0.3);
      ctx.restore();
    }
    let acc = '';
    const dur = Math.max(0.35, Math.min(1.0, (bk.t1 - bk.t0) * 0.7));
    [...txt].forEach((ch, j) => {
      const x = x0 + ctx.measureText(acc).width; acc += ch;
      const a = clamp((t - bk.t0 - (j / txt.length) * dur) / 0.18) * (1 - out);
      if (a <= 0) return;
      ctx.globalAlpha = a;
      ctx.fillStyle = light ? C.ink : C.cream;
      ctx.fillText(ch, x, y + (1 - a) * 14);
    });
    ctx.restore();
  }
}
function drawStamps(ctx, t) {
  for (const s of STAMPS) {
    const age = t - s.t;
    if (age < 0 || age > 1.0) continue;
    const sc = lerp(2.8, 1, eOutCubic(age / 0.14));
    const a = clamp(age / 0.06) * (1 - clamp((age - 0.7) / 0.3));
    ctx.save(); ctx.globalAlpha = a;
    ctx.translate(W * 0.5, H * 0.5); ctx.rotate(-0.12); ctx.scale(sc, sc);
    // ink splat behind the stamp
    ctx.fillStyle = hexA(C.ink, 0.55); ctx.beginPath();
    for (let k = 0; k <= 24; k++) { const an = (k / 24) * TAU, r = 260 + 70 * hash(k + 3) * (k % 2 ? 1 : 0.4); k ? ctx.lineTo(Math.cos(an) * r * 1.5, Math.sin(an) * r * 0.6) : ctx.moveTo(Math.cos(an) * r * 1.5, Math.sin(an) * r * 0.6); }
    ctx.fill();
    ctx.font = '300px PFB'; ctx.textAlign = 'center';
    const txt = up(s.words[0].text);
    ctx.lineWidth = 22; ctx.lineJoin = 'round'; ctx.strokeStyle = C.cream; ctx.strokeText(txt, 0, 105);
    ctx.fillStyle = C.red; ctx.fillText(txt, 0, 105);
    ctx.restore();
  }
}
function drawWipe(ctx, t, b, Snew) {
  const p = clamp((t - b.wipe0) / (b.wipe1 - b.wipe0));
  if (p <= 0 || p >= 1) return;
  const e = eInOut3(p);
  const sk = 300;
  const slab = (x, col) => { ctx.fillStyle = col; ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x + W + sk, 0); ctx.lineTo(x + W, H); ctx.lineTo(x - sk, H); ctx.closePath(); ctx.fill(); };
  const x = lerp(-W - 2 * sk, W + 2 * sk, e);
  slab(x + 260, Snew.fg[0]);
  slab(x + 160, Snew.acc || C.amber);
  slab(x, Snew.bg);
}
function letterbox(ctx, h) { if (h <= 0) return; ctx.fillStyle = '#000'; ctx.fillRect(0, 0, W, h); ctx.fillRect(0, H - h, W, h); }

// cinematic HUD: artist / title, section label, corner marks, running timecode
function drawHUD(ctx, t, S, label, alpha) {
  if (alpha <= 0) return;
  const light = S.bg === C.amber;
  const col = light ? C.ink : C.cream;
  ctx.save(); ctx.globalAlpha = alpha * 0.85; ctx.fillStyle = col; ctx.strokeStyle = col;
  ctx.font = '34px Anton'; ctx.textBaseline = 'alphabetic';
  if (REEL) {
    ctx.textAlign = 'center'; ctx.font = '40px Anton'; ctx.fillText(up(ARTIST).split('').join(' '), W / 2, 250);
    ctx.font = '34px PFS'; ctx.fillText(SONG, W / 2, 300); ctx.fillRect(W / 2 - 40, 268, 80, 2);
    ctx.restore(); return;
  }
  ctx.fillText(up(ARTIST), 72, 84);
  const aw = ctx.measureText(up(ARTIST)).width;
  ctx.fillRect(72 + aw + 18, 70, 46, 2);
  ctx.font = '28px PFS'; ctx.fillText(SONG, 72 + aw + 80, 84);
  ctx.font = '22px Inter'; ctx.textAlign = 'right';
  ctx.fillText(label, W - 72, 82);
  ctx.beginPath(); ctx.arc(W - 72 - ctx.measureText(label).width - 22, 74, 6, 0, TAU); ctx.globalAlpha = alpha * (0.5 + 0.5 * beatPulse(t, 5)); ctx.fillStyle = S.acc; ctx.fill();
  ctx.globalAlpha = alpha * 0.85; ctx.fillStyle = col;
  // timecode + progress line
  const mm = (x) => String(Math.floor(x / 60)).padStart(2, '0') + ':' + String(Math.floor(x % 60)).padStart(2, '0');
  ctx.font = '20px Inter'; ctx.textAlign = 'right'; ctx.fillText(`${mm(t)} / ${mm(DURATION)}`, W - 72, H - 50);
  ctx.globalAlpha = alpha * 0.3; ctx.fillRect(72, H - 58, W - 72 * 2 - 160, 2);
  ctx.globalAlpha = alpha * 0.9; ctx.fillRect(72, H - 59, (W - 72 * 2 - 160) * (t / DURATION), 4);
  // corner marks
  ctx.globalAlpha = alpha * 0.5; ctx.lineWidth = 2;
  const m = 36, l = 34;
  [[m, m, 1, 1], [W - m, m, -1, 1], [m, H - m, 1, -1], [W - m, H - m, -1, -1]].forEach(([x, y, sx, sy]) => { ctx.beginPath(); ctx.moveTo(x, y + sy * l); ctx.lineTo(x, y); ctx.lineTo(x + sx * l, y); ctx.stroke(); });
  ctx.restore();
}

// ------------------------------------------------------------------ intro / outro
function drawTitleScene(ctx, t, mode) {
  const S = SEC[mode];
  drawBG(ctx, t, S);
  // starry backdrop + slow light beam
  ctx.fillStyle = C.cream;
  SKY.forEach(([x, y, r, ph]) => { ctx.globalAlpha = 0.15 + 0.35 * (0.5 + 0.5 * Math.sin(t * 2 + ph)); ctx.beginPath(); ctx.arc(x, y, r * 0.8, 0, TAU); ctx.fill(); });
  ctx.globalAlpha = 1;
  const local = mode === 'intro' ? t : t - OUTRO_START;
  ctx.save(); ctx.translate(W / 2, H / 2); ctx.rotate(t * 0.05);
  ctx.strokeStyle = hexA(C.amber, 0.18); ctx.lineWidth = 2;
  for (let k = 1; k <= 5; k++) { ctx.setLineDash([4, 14 + k * 4]); ctx.beginPath(); ctx.arc(0, 0, 180 + k * 70 + Math.sin(t + k) * 6, 0, TAU); ctx.stroke(); }
  ctx.setLineDash([]); ctx.restore();
  const inP = mode === 'intro' ? eOutCubic((local - 0.6) / 3.2) : 1;
  const sz = 0.72 * (1 + 0.008 * Math.sin(t * 1.3));
  const leftCol = mode === 'outro' && t >= 179.42 ? C.berry : C.cream;
  ctx.save(); ctx.globalAlpha = inP;
  drawHead(ctx, lerp(-200, 250, inP), 600, sz, false, leftCol);
  drawHead(ctx, lerp(W + 200, W - 250, inP), 600, sz, true, C.berry);
  ctx.restore();
  // artist name
  const ta0 = mode === 'intro' ? 3.6 : OUTRO_START + 0.05;
  const pa = eOutCubic((t - ta0) / 0.8);
  if (pa > 0) {
    ctx.save(); ctx.globalAlpha = pa; ctx.font = '46px Anton'; ctx.fillStyle = C.amber; ctx.textAlign = 'center';
    const name = up(ARTIST).split('').join(' ');
    ctx.fillText(name, W / 2, 360 - (1 - pa) * 20);
    ctx.fillRect(W / 2 - 160 * pa, 382, 320 * pa, 2);
    ctx.restore();
  }
  const word = up('bambaşka');
  ctx.save(); ctx.font = '210px Anton'; ctx.textAlign = 'left';
  const tw = ctx.measureText(word).width; let acc = '';
  const t0 = mode === 'intro' ? 5.76 : OUTRO_START + 0.15;
  const gap = mode === 'intro' ? 0.29 : 0.17;
  [...word].forEach((ch, j) => {
    const cx = W / 2 - tw / 2 + ctx.measureText(acc).width; acc += ch;
    const ta = t0 + j * gap;
    const p = clamp((t - ta) / 0.35); if (p <= 0) return;
    const dy = (1 - eOutBack(p, 2.2)) * -260;
    ctx.globalAlpha = clamp(p * 3);
    ctx.fillStyle = '#07060f'; for (let k = 8; k >= 1; k -= 2) ctx.fillText(ch, cx + k, 600 + dy + k);
    ctx.fillStyle = j % 2 ? C.amber : C.cream;
    ctx.fillText(ch, cx, 600 + dy);
  });
  const tb = t0 + 8 * gap + 0.1;
  const pb = eOutCubic((t - tb) / 0.6);
  if (pb > 0) {
    ctx.font = '150px PFB'; ctx.textAlign = 'center'; ctx.globalAlpha = pb; ctx.fillStyle = C.berry;
    ctx.save(); ctx.translate(W / 2 + 230, 735 + (1 - pb) * 40); ctx.rotate(-0.06);
    ctx.lineWidth = 14; ctx.strokeStyle = C.ink; ctx.strokeText(up('biri'), 0, 0); ctx.fillText(up('biri'), 0, 0); ctx.restore();
  }
  ctx.restore();
}

// ------------------------------------------------------------------ frame
function renderWorld(ctx, t, k) {
  const b = BLOCKS[k];
  const S = SEC[b.line.sec];
  drawBG(ctx, t, S);
  drawBackdrop(ctx, t, b);
  if (b.line.fx === 'clone2') drawMarquee(ctx, t, b);
  const cam = camAt(t, k);
  const drift = { x: Math.sin(t * 0.31) * 10, y: Math.cos(t * 0.23) * 8, r: Math.sin(t * 0.19) * 0.006 };
  const z = cam.z * (1 + punch(t));
  ctx.save();
  ctx.translate(W / 2, H / 2); ctx.scale(z, z); ctx.rotate(-(cam.rot + drift.r)); ctx.translate(-cam.x - drift.x / z, -cam.y - drift.y / z);
  for (let j = Math.max(0, k - 2); j <= k; j++) {
    const bj = BLOCKS[j];
    if (bj.line.sec !== b.line.sec) continue;
    let a = 1;
    if (j < k) { a = 0.42 * (1 - clamp((t - b.mv1) / 0.9)); if (j < k - 1) a *= 0.5; }
    if (a <= 0.01) continue;
    ctx.save(); ctx.globalAlpha = a; drawBlock(ctx, bj, t, S); ctx.restore();
  }
  ctx.restore();
  return cam;
}

const main = createCanvas(W, H), mc = main.getContext('2d');
const sub = createCanvas(W, H), sc = sub.getContext('2d');

function renderFrame(t) {
  const k = blockIndexAt(t);
  mc.globalAlpha = 1; mc.globalCompositeOperation = 'source-over';
  if (k < 0) {
    drawTitleScene(mc, t, 'intro');
    letterbox(mc, 130 * (1 - eInOut3((t - (INTRO_END - 0.5)) / 0.5)));
    if (t > BLOCKS[0].wipe0) drawWipe(mc, t, BLOCKS[0], SEC[BLOCKS[0].line.sec]);
  } else if (t >= OUTRO_START) {
    drawTitleScene(mc, t, 'outro');
    letterbox(mc, 130 * eInOut3((t - 180.2) / 2.6));
  } else {
    const b = BLOCKS[k];
    const S = SEC[b.line.sec];
    const cam0 = camAt(t, k);
    if (cam0.moving) {
      const N = 5;
      for (let s = 0; s < N; s++) {
        const ts = t - (0.5 / FPS) * (s / (N - 1));
        sc.globalAlpha = 1; renderWorld(sc, ts, k);
        mc.globalAlpha = 1 / (s + 1); mc.drawImage(sub, 0, 0);
      }
      mc.globalAlpha = 1;
    } else renderWorld(mc, t, k);
    if (b.line.fx === 'dark') drawDarkOverlay(mc, t, b);
    const brStart = BLOCKS.find((x) => x.line.sec === 'br').tIn;
    let lb = 0;
    if (b.line.sec === 'br') lb = 90 * eOutCubic((t - brStart) / 1.0) * (b.line.fx === 'sun' ? 1 - clamp((t - b.line.words[1].t) / 0.6) : 1);
    letterbox(mc, lb);
    drawHUD(mc, t, S, S.label || '', clamp((t - INTRO_END) / 0.8) * (1 - clamp((t - (OUTRO_START - 0.6)) / 0.4)) * (b.line.fx === 'dark' ? 1 - clamp((t - b.line.words[1].t) / 0.6) : 1));
    const n = BLOCKS[k + 1];
    if (n && n.newSec && t >= n.wipe0) drawWipe(mc, t, n, SEC[n.line.sec]);
    if (b.newSec && t < b.wipe1) drawWipe(mc, t, b, S);
    if (t > OUTRO_START - 0.45) drawWipe(mc, t, { wipe0: OUTRO_START - 0.45, wipe1: OUTRO_START }, SEC.outro);
    drawBacking(mc, t, S);
    drawStamps(mc, t);
  }
  mc.save(); mc.globalCompositeOperation = 'overlay'; mc.globalAlpha = 0.2;
  mc.drawImage(GRAIN[Math.floor(t * FPS) % GRAIN.length], 0, 0, W, H); mc.restore();
  mc.drawImage(VIG, 0, 0);
  const fin = Math.min(clamp(t / 1.2), 1 - clamp((t - (DURATION - 2.2)) / 1.9));
  if (fin < 1) { mc.fillStyle = `rgba(0,0,0,${1 - fin})`; mc.fillRect(0, 0, W, H); }
}

// ------------------------------------------------------------------ Instagram reel (9:16 teaser -> YouTube)
const R_T0 = 46.70, R_CUT = 64.90, R_END = 69.47; // source seconds
const R_DUR = R_END - R_T0;
function playIcon(ctx, x, y, r, col, fg) {
  ctx.fillStyle = col; ctx.beginPath(); ctx.arc(x, y, r, 0, TAU); ctx.fill();
  ctx.fillStyle = fg; ctx.beginPath(); ctx.moveTo(x - r * 0.3, y - r * 0.42); ctx.lineTo(x + r * 0.48, y); ctx.lineTo(x - r * 0.3, y + r * 0.42); ctx.closePath(); ctx.fill();
}
function drawCTAPill(ctx, t, tr) {
  const p = eOutBack((tr - 1.6) / 0.5, 1.8); if (p <= 0) return;
  const y = H - 470, txt = 'Tam versiya YouTube-da';
  ctx.save(); ctx.font = '44px Anton';
  const tw = ctx.measureText(up(txt)).width, w = tw + 140, h = 92;
  ctx.translate(W / 2, y); ctx.scale(p * (1 + 0.03 * beatPulse(t)), p);
  ctx.fillStyle = 'rgba(0,0,0,0.35)'; ctx.beginPath(); ctx.roundRect(-w / 2 + 8, -h / 2 + 8, w, h, h / 2); ctx.fill();
  ctx.fillStyle = C.cream; ctx.beginPath(); ctx.roundRect(-w / 2, -h / 2, w, h, h / 2); ctx.fill();
  playIcon(ctx, -w / 2 + 52, 0, 30, C.red, C.cream);
  ctx.fillStyle = C.ink; ctx.textAlign = 'left'; ctx.fillText(up(txt), -w / 2 + 100, 16);
  ctx.restore();
}
function drawReelEnd(ctx, t, lt) {
  const S = SEC.outro;
  drawBG(ctx, t, S);
  ctx.save(); ctx.translate(W / 2, H * 0.45); ctx.rotate(t * 0.06); ctx.fillStyle = 'rgba(242,181,68,0.07)';
  for (let k = 0; k < 16; k++) { ctx.beginPath(); ctx.moveTo(0, 0); ctx.arc(0, 0, 1800, (k * TAU) / 16, ((k + 0.5) * TAU) / 16); ctx.closePath(); ctx.fill(); }
  ctx.restore();
  ctx.fillStyle = C.cream;
  SKY.forEach(([x, y, r, ph]) => { if (x > W) return; ctx.globalAlpha = 0.15 + 0.35 * (0.5 + 0.5 * Math.sin(t * 2 + ph)); ctx.beginPath(); ctx.arc(x, y * 1.8, r * 0.8, 0, TAU); ctx.fill(); });
  ctx.globalAlpha = 1;
  const inP = eOutCubic(lt / 0.7);
  drawHead(ctx, lerp(-200, 105, inP), 800, 0.34, false, C.cream);
  drawHead(ctx, lerp(W + 200, W - 105, inP), 800, 0.34, true, C.berry);
  const pa = eOutCubic((lt - 0.1) / 0.5);
  ctx.save(); ctx.globalAlpha = pa; ctx.font = '50px Anton'; ctx.fillStyle = C.amber; ctx.textAlign = 'center';
  ctx.fillText(up(ARTIST).split('').join(' '), W / 2, 520); ctx.fillRect(W / 2 - 130 * pa, 545, 260 * pa, 2); ctx.restore();
  const word = up('bambaşka');
  ctx.save(); ctx.font = '128px Anton';
  const tw = ctx.measureText(word).width; let acc = '';
  [...word].forEach((ch, j) => {
    const cx = W / 2 - tw / 2 + ctx.measureText(acc).width; acc += ch;
    const p = clamp((lt - 0.25 - j * 0.07) / 0.3); if (p <= 0) return;
    const dy = (1 - eOutBack(p, 2.2)) * -200;
    ctx.globalAlpha = clamp(p * 3);
    ctx.fillStyle = '#07060f'; for (let k = 7; k >= 1; k -= 2) ctx.fillText(ch, cx + k, 800 + dy + k);
    ctx.fillStyle = j % 2 ? C.amber : C.cream; ctx.fillText(ch, cx, 800 + dy);
  });
  const pb = eOutCubic((lt - 0.9) / 0.5);
  if (pb > 0) { ctx.font = '110px PFB'; ctx.textAlign = 'center'; ctx.globalAlpha = pb; ctx.save(); ctx.translate(W / 2 + 160, 905); ctx.rotate(-0.06);
    ctx.lineWidth = 12; ctx.strokeStyle = C.ink; ctx.strokeText(up('biri'), 0, 0); ctx.fillStyle = C.berry; ctx.fillText(up('biri'), 0, 0); ctx.restore(); }
  ctx.restore();
  // call to action
  const pc = eOutBack((lt - 1.2) / 0.5, 1.7);
  if (pc > 0) {
    ctx.save(); ctx.translate(W / 2, 1150); ctx.scale(pc, pc);
    ctx.font = '46px PFS'; ctx.fillStyle = hexA(C.cream, 0.85); ctx.textAlign = 'center'; ctx.fillText('yeni lyric video', 0, -95);
    ctx.font = '104px Anton'; const tx = up('İndi YouTube-da'); const w2 = ctx.measureText(tx).width;
    const pr = 62 * (1 + 0.08 * beatPulse(t));
    playIcon(ctx, -w2 / 2 - 30, 40 - 36, pr, C.red, C.cream);
    ctx.textAlign = 'left'; ctx.fillStyle = '#07060f'; ctx.fillText(tx, -w2 / 2 + 60 + 6, 40 + 6); ctx.fillStyle = C.cream; ctx.fillText(tx, -w2 / 2 + 60, 40);
    ctx.restore();
  }
  const pl = eOutCubic((lt - 1.7) / 0.5);
  if (pl > 0) {
    ctx.save(); ctx.globalAlpha = pl; ctx.font = '56px PFS'; ctx.fillStyle = C.amber; ctx.textAlign = 'center';
    const bob = Math.sin(t * 5) * 6;
    ctx.fillText('Link bio-da', W / 2, 1320);
    ctx.strokeStyle = C.amber; ctx.lineWidth = 6; ctx.lineCap = 'round'; ctx.lineJoin = 'round';
    ctx.beginPath(); ctx.moveTo(W / 2, 1400 + bob); ctx.lineTo(W / 2, 1350 + bob); ctx.moveTo(W / 2 - 18, 1368 + bob); ctx.lineTo(W / 2, 1350 + bob); ctx.lineTo(W / 2 + 18, 1368 + bob); ctx.stroke();
    ctx.restore();
  }
}
function renderReel(tr) {
  const t = R_T0 + tr;
  if (t < R_CUT) {
    renderFrame(t);
    drawCTAPill(mc, t, tr);
    if (t > R_CUT - 0.35) drawWipe(mc, t, { wipe0: R_CUT - 0.35, wipe1: R_CUT + 0.05 }, SEC.outro);
  } else {
    mc.globalAlpha = 1;
    drawReelEnd(mc, t, t - R_CUT);
    drawWipe(mc, t, { wipe0: R_CUT - 0.35, wipe1: R_CUT + 0.05 }, SEC.outro);
    mc.save(); mc.globalCompositeOperation = 'overlay'; mc.globalAlpha = 0.2; mc.drawImage(GRAIN[Math.floor(t * FPS) % GRAIN.length], 0, 0, W, H); mc.restore();
    mc.drawImage(VIG, 0, 0);
  }
  const fo = clamp((tr - (R_DUR - 0.5)) / 0.5);
  if (fo > 0) { mc.fillStyle = `rgba(0,0,0,${fo})`; mc.fillRect(0, 0, W, H); }
}

// ------------------------------------------------------------------ main
const [, , mode, ...args] = process.argv;
if (mode === 'still') {
  const out = args[0]; fs.mkdirSync(out, { recursive: true });
  for (const ts of args.slice(1)) {
    const t = parseFloat(ts); renderFrame(t);
    fs.writeFileSync(path.join(out, `f_${t.toFixed(2).padStart(7, '0')}.png`), main.toBuffer('image/png'));
  }
} else if (mode === 'video') {
  const f0 = parseInt(args[0]), f1 = parseInt(args[1]), outp = args[2];
  const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgba', '-s', `${W}x${H}`, '-r', String(FPS), '-i', '-',
    '-c:v', 'libx264', '-preset', 'medium', '-crf', '17', '-pix_fmt', 'yuv420p', '-tune', 'grain', outp], { stdio: ['pipe', 'inherit', 'inherit'] });
  let f = f0;
  const t0 = Date.now();
  function next() {
    while (f < f1) {
      renderFrame(f / FPS);
      const buf = Buffer.from(mc.getImageData(0, 0, W, H).data.buffer);
      f++;
      if (f % 150 === 0) process.stderr.write(`[${f0}-${f1}] ${f} ${((Date.now() - t0) / 1000).toFixed(0)}s\n`);
      if (!ff.stdin.write(buf)) { ff.stdin.once('drain', next); return; }
    }
    ff.stdin.end();
  }
  next();
} else if (mode === 'reelstill') {
  const out = args[0]; fs.mkdirSync(out, { recursive: true });
  for (const ts of args.slice(1)) { const t = parseFloat(ts); renderReel(t); fs.writeFileSync(path.join(out, `r_${t.toFixed(2).padStart(6, '0')}.png`), main.toBuffer('image/png')); }
} else if (mode === 'reelvideo') {
  const outp = args[0], N = Math.round(R_DUR * FPS);
  const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgba', '-s', `${W}x${H}`, '-r', String(FPS), '-i', '-',
    '-c:v', 'libx264', '-preset', 'medium', '-crf', '17', '-pix_fmt', 'yuv420p', outp], { stdio: ['pipe', 'inherit', 'inherit'] });
  let f = 0;
  (function next() {
    while (f < N) { renderReel(f / FPS); const buf = Buffer.from(mc.getImageData(0, 0, W, H).data.buffer); f++; if (!ff.stdin.write(buf)) { ff.stdin.once('drain', next); return; } }
    ff.stdin.end();
  })();
} else if (mode === 'info') {
  BLOCKS.forEach((b) => console.log(b.i, b.line.sec, b.line.fx || '', 'mv', b.mv0.toFixed(2), b.mv1.toFixed(2), 'first', b.line.t.toFixed(2), b.words.map((w) => w.txt + '@' + w.t.toFixed(2)).join(' ')));
}
