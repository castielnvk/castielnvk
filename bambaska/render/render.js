// "Bambaşka biri" — cinematic kinetic-typography lyric video renderer (1920x1080, 30 fps).
// Usage:
//   node render.js still OUTDIR t1 t2 ...        -> PNG stills
//   node render.js video F0 F1 OUT.mp4           -> frames [F0,F1) encoded to H.264 (no audio)
const { createCanvas, GlobalFonts } = require('@napi-rs/canvas');
const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');
const { lines: ALL_LINES, backing, DURATION } = require('./timeline');
const AUDIO = require('./audio.json');

const W = 1920, H = 1080, FPS = 30;
const F = (n) => path.join(__dirname, 'fonts', n);
GlobalFonts.registerFromPath(F('Anton_400Regular.ttf'), 'Anton');
GlobalFonts.registerFromPath(F('BigShouldersDisplay_900Black.ttf'), 'BSD');
GlobalFonts.registerFromPath(F('BebasNeue_400Regular.ttf'), 'Bebas');
GlobalFonts.registerFromPath(F('PlayfairDisplay_900Black_Italic.ttf'), 'PFB');
GlobalFonts.registerFromPath(F('PlayfairDisplay_600SemiBold_Italic.ttf'), 'PFS');
GlobalFonts.registerFromPath(F('PlayfairDisplay_400Regular_Italic.ttf'), 'PFR');

// ------------------------------------------------------------------ helpers
const clamp = (x, a = 0, b = 1) => Math.max(a, Math.min(b, x));
const lerp = (a, b, p) => a + (b - a) * p;
const eOutCubic = (p) => 1 - Math.pow(1 - clamp(p), 3);
const eInCubic = (p) => Math.pow(clamp(p), 3);
const eInOut = (p) => { p = clamp(p); return p < 0.5 ? 16 * p ** 5 : 1 - Math.pow(-2 * p + 2, 5) / 2; };
const eInOut3 = (p) => { p = clamp(p); return p < 0.5 ? 4 * p ** 3 : 1 - Math.pow(-2 * p + 2, 3) / 2; };
const eOutBack = (p, s = 1.9) => { p = clamp(p) - 1; return 1 + (s + 1) * p ** 3 + s * p ** 2; };
const eOutElastic = (p) => { p = clamp(p); if (p === 0 || p === 1) return p; return Math.pow(2, -10 * p) * Math.sin((p * 10 - 0.75) * (2 * Math.PI / 3)) + 1; };
function rng(seed) { let a = seed >>> 0; return () => { a |= 0; a = (a + 0x6D2B79F5) | 0; let t = Math.imul(a ^ (a >>> 15), 1 | a); t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; }; }
const hash = (n) => { const r = rng(n * 7919 + 13); r(); return r(); };
const up = (s) => s.toLocaleUpperCase('tr-TR');
function hexA(hex, a) { const n = parseInt(hex.slice(1), 16); return `rgba(${n >> 16},${(n >> 8) & 255},${n & 255},${a})`; }
function mixHex(h1, h2, p) {
  const a = parseInt(h1.slice(1), 16), b = parseInt(h2.slice(1), 16);
  const r = Math.round(lerp(a >> 16, b >> 16, p)), g = Math.round(lerp((a >> 8) & 255, (b >> 8) & 255, p)), bl = Math.round(lerp(a & 255, b & 255, p));
  return '#' + ((1 << 24) | (r << 16) | (g << 8) | bl).toString(16).slice(1);
}

// audio-reactive helpers
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
  amber: '#F2B544', cream: '#F4E7D1', orange: '#E9773D', sky: '#86CFC4', black: '#07060E', red: '#FF5A5F',
};
const SEC = {
  intro: { bg: C.ink, bg2: '#2a2350', fg: [C.cream], acc: C.amber },
  v1: { bg: C.teal, bg2: '#3d8a85', fg: [C.cream, C.amber], acc: C.berry, style: 'rise', fonts: ['Anton', 'BSD', 'Bebas'] },
  pre: { bg: C.berryD, bg2: '#8f2747', fg: [C.amber, C.cream], acc: C.sky, style: 'pop', fonts: ['BSD', 'Anton', 'Bebas'] },
  ch: { bg: C.ink, bg2: '#2b2560', fg: [C.cream], acc: C.amber, split: [C.cream, C.amber], disc: ['#2f2968', C.teal, C.berryD], style: 'slam', fonts: ['Anton', 'BSD'] },
  v2: { bg: C.night, bg2: '#1f1c44', fg: [C.cream, '#cdbfa8'], acc: C.amber, style: 'rise', fonts: ['Bebas', 'Anton', 'BSD'] },
  q: { bg: '#3B0F23', bg2: '#64203c', fg: [C.cream, C.amber], acc: C.red, style: 'pop', fonts: ['Anton', 'BSD', 'Bebas'] },
  ch2: { bg: '#123c3c', bg2: '#1f5b59', fg: [C.cream], acc: C.amber, split: [C.amber, C.cream], disc: [C.berryD, C.ink, '#2f2968'], style: 'slam', fonts: ['BSD', 'Anton'] },
  br: { bg: C.black, bg2: '#1a1734', fg: [C.cream], acc: C.berry, style: 'flicker', fonts: ['Bebas', 'Anton', 'BSD'] },
  fin: { bg: C.amber, bg2: '#ffd98a', fg: [C.ink, C.berryD], acc: C.berry, split: [C.berry, C.ink], disc: [C.cream, C.orange, C.cream], style: 'slam', fonts: ['Anton', 'BSD'] },
  outro: { bg: C.ink, bg2: '#2a2350', fg: [C.cream], acc: C.amber },
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
const LINE_TIMES = LINES.map((l) => l.t);

function rowsFor(line) {
  const ws = line.words;
  if (line.fx === 'tek') return ws.map((w) => [w]);
  if (line.fx === 'split') { const r = [[ws[0]]]; if (ws.length > 1) r.push(...greedy(ws.slice(1), 11)); return r; }
  if (line.fx === 'clash') return ws.map((w) => [w]);
  if (line.fx === 'head') return ws.map((w) => [w]);
  if (line.fx === 'echo') return [ws];
  return greedy(ws, line.words.length > 6 ? 13 : 11);
}
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

function layoutBlock(line, li) {
  const S = SEC[line.sec];
  const BW = line.fx === 'head' ? 560 : line.fx === 'clash' ? 900 : 1000;
  const rows = rowsFor(line);
  const out = { line, rows: [], words: [], hw: 0, hh: 0 };
  let y = 0;
  const fonts = S.fonts;
  rows.forEach((row, r) => {
    const font = fonts[(r + li) % fonts.length];
    const items = row.map((w) => {
      const acc = (line.accent || []).includes(w.text);
      const f = acc ? 'PFB' : font;
      return { w, f, acc, txt: up(w.text) };
    });
    const sp = 22;
    const tot = items.reduce((a, it) => a + w100(it.f, it.txt), 0) + sp * (items.length - 1);
    let size = (BW / tot) * 100;
    const maxSize = line.fx === 'tek' ? 300 : line.fx === 'echo' ? 330 : 420;
    size = Math.min(size, maxSize);
    const rowW = (tot * size) / 100;
    const ch = Math.max(...items.map((it) => capH(it.f))) * size;
    const top = y + (r ? 0.17 * size : 0);
    const base = top + ch;
    let x = -rowW / 2;
    items.forEach((it, k) => {
      const ww = (w100(it.f, it.txt) * size) / 100;
      const col = it.acc ? S.acc : S.fg[(r + li) % S.fg.length];
      out.words.push({ ...it, x, base, size, ww, ch: capH(it.f) * size, col, row: r, idx: out.words.length, t: it.w.t });
      x += ww + (sp * size) / 100;
    });
    out.rows.push({ top, base, size, rowW });
    y = base + 0.06 * size + 10;
  });
  const bh = y;
  out.words.forEach((w) => { w.base -= bh / 2; });
  out.rows.forEach((r) => { r.top -= bh / 2; r.base -= bh / 2; });
  out.tw = BW; out.th = bh;
  out.hw = BW / 2; out.hh = bh / 2;
  // decor padding (bounding box used for camera framing)
  const pad = { l: 0, r: 0, t: 0, b: 0 };
  if (line.fx === 'wing') pad.l = 640;
  if (line.fx === 'eye') pad.t = 600;
  if (line.fx === 'cage') { pad.l = pad.r = 110; pad.t = 300; pad.b = 90; }
  if (line.fx === 'arrows') { pad.l = pad.r = 380; }
  if (line.fx === 'moon') { pad.r = 420; pad.t = 420; }
  if (line.fx === 'split') { pad.t = 150; pad.b = 60; }
  if (line.fx === 'clash') { pad.t = pad.b = 120; pad.l = pad.r = 80; }
  if (line.fx === 'head') { out.headMirror = li % 2 === 1; pad.t = 190; pad.b = 330; pad.l = pad.r = 200; }
  out.pad = pad;
  out.bx0 = -out.hw - pad.l; out.bx1 = out.hw + pad.r; out.by0 = -out.hh - pad.t; out.by1 = out.hh + pad.b;
  return out;
}

// placement pattern per section (direction in previous block frame, relative rotation)
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
    b.scale = SCALES[i % SCALES.length] * (line.fx === 'head' ? 1.0 : 1);
    if (newSec) { b.x = 0; b.y = 0; b.rot = 0; b.k = 0; }
    else {
      const pat = PATTERN[(prev.k + 1 + i) % PATTERN.length];
      b.k = prev.k + 1;
      b.rot = prev.rot + (pat.r * Math.PI) / 180;
      const pr = prev.rot, ca = Math.cos(pr), sa = Math.sin(pr);
      const rel = pat.r !== 0;
      // extents of new block along prev-frame axes
      const nx = rel ? (b.by1 - b.by0) / 2 : (b.bx1 - b.bx0) / 2;
      const ny = rel ? (b.bx1 - b.bx0) / 2 : (b.by1 - b.by0) / 2;
      let ox = 0, oy = 0;
      const gap = 260;
      const pcx = (prev.bx0 + prev.bx1) / 2, pcy = (prev.by0 + prev.by1) / 2;
      if (pat.d === 'down') { oy = prev.by1 * prev.scale + gap + ny * b.scale; ox = pcx * prev.scale + (hash(i) - 0.5) * 300; }
      if (pat.d === 'right') { ox = prev.bx1 * prev.scale + gap + nx * b.scale; oy = pcy * prev.scale + (hash(i) - 0.5) * 200; }
      if (pat.d === 'left') { ox = prev.bx0 * prev.scale - gap - nx * b.scale; oy = pcy * prev.scale + (hash(i) - 0.5) * 200; }
      b.x = prev.x + ox * ca - oy * sa;
      b.y = prev.y + ox * sa + oy * ca;
    }
    // camera target: frame the block's bbox (centre of bbox in world)
    const cxl = ((b.bx0 + b.bx1) / 2) * b.scale, cyl = ((b.by0 + b.by1) / 2) * b.scale;
    const c = Math.cos(b.rot), s = Math.sin(b.rot);
    const fitW = line.fx === 'split' ? 0.74 : 0.8, fitH = line.fx === 'split' ? 0.7 : 0.74;
    b.cam = {
      x: b.x + cxl * c - cyl * s, y: b.y + cxl * s + cyl * c, rot: b.rot,
      z: Math.min((W * fitW) / ((b.bx1 - b.bx0) * b.scale), (H * fitH) / ((b.by1 - b.by0) * b.scale)),
    };
    b.newSec = newSec;
    BLOCKS.push(b);
    prev = b;
  });
  // timing of camera moves / section wipes
  BLOCKS.forEach((b, i) => {
    const p = BLOCKS[i - 1];
    const lastPrev = p ? p.line.words[p.line.words.length - 1].t : 0;
    if (b.newSec) {
      b.wipe0 = b.line.t - 0.42; b.wipe1 = b.line.t - 0.02; b.tIn = (b.wipe0 + b.wipe1) / 2; b.mv0 = b.mv1 = b.tIn;
    } else {
      const D = clamp(b.line.t - lastPrev - 0.22, 0.28, 0.6);
      b.mv1 = b.line.t - 0.03; b.mv0 = b.mv1 - D; b.tIn = b.mv0;
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
  let z = b.cam.z * (1 + 0.045 * eInOut3(p));
  if (b.newSec) z *= lerp(0.86, 1, eOutCubic((t - b.tIn) / 0.9));
  return { x: b.cam.x, y: b.cam.y, rot: b.cam.rot, z };
}
function angDiff(a, b) { let d = b - a; while (d > Math.PI) d -= 2 * Math.PI; while (d < -Math.PI) d += 2 * Math.PI; return d; }
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

// punches (screen zoom kicks)
const PUNCH = [];
LINES.forEach((l) => {
  if (l.fx === 'tek') l.words.forEach((w) => PUNCH.push([w.t, 0.07]));
  if (l.fx === 'split') PUNCH.push([l.t, 0.035]);
  if (l.fx === 'sun') PUNCH.push([l.words[1].t, 0.06]);
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

// ------------------------------------------------------------------ illustration paths
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

// ------------------------------------------------------------------ word rendering
function wordAppear(ctx, wd, t, style, b) {
  const p = (t - wd.t + 0.05) / 0.3;
  if (p <= 0) return false;
  const cx = wd.x + wd.ww / 2, cy = wd.base - wd.ch / 2;
  if (style === 'rise') {
    const e = eOutCubic(p);
    ctx.beginPath(); ctx.rect(wd.x - 20, wd.base - wd.ch - 0.32 * wd.size, wd.ww + 40, wd.ch + 0.62 * wd.size); ctx.clip();
    ctx.translate(0, (1 - e) * (wd.ch + 0.4 * wd.size));
  } else if (style === 'pop') {
    const s = lerp(0.3, 1, eOutBack(p, 2.2));
    ctx.translate(cx, cy); ctx.scale(s, s); ctx.rotate((1 - eOutCubic(p)) * (wd.idx % 2 ? 0.25 : -0.25)); ctx.translate(-cx, -cy);
    ctx.globalAlpha *= clamp(p * 4);
  } else if (style === 'slam') {
    const s = lerp(2.1, 1, eOutCubic(p * 1.6));
    ctx.translate(cx, cy); ctx.scale(s, s); ctx.translate(-cx, -cy);
    ctx.globalAlpha *= clamp(p * 5);
  } else if (style === 'flicker') {
    const fr = Math.floor((t - wd.t) * 30);
    if (fr < 8 && [0, 1, 0, 1, 1, 0, 1, 1][Math.max(0, fr)] === 0) return false;
    ctx.translate(0, (1 - eOutCubic(p)) * 30);
  }
  return true;
}

function drawWordText(ctx, wd, col, opt = {}) {
  ctx.font = `${wd.size}px ${wd.f}`;
  if (opt.stroke) { ctx.lineWidth = opt.stroke; ctx.strokeStyle = col; ctx.lineJoin = 'round'; ctx.strokeText(wd.txt, wd.x, wd.base); return; }
  ctx.fillStyle = col; ctx.fillText(wd.txt, wd.x, wd.base);
}

function drawSplitWord(ctx, wd, t, S, b) {
  // identity split: top half / bottom half in two colours, sliding apart on the beat
  const age = t - wd.t;
  const dx = 70 * Math.exp(-age * 5) + 10 * beatPulse(t) + 4;
  const midY = wd.base - wd.ch * 0.5;
  ctx.font = `${wd.size}px ${wd.f}`;
  ctx.save(); ctx.beginPath(); ctx.rect(wd.x - 200, wd.base - wd.ch - wd.size * 0.4, wd.ww + 400, midY - (wd.base - wd.ch - wd.size * 0.4)); ctx.clip();
  ctx.fillStyle = S.split[0]; ctx.fillText(wd.txt, wd.x - dx, wd.base); ctx.restore();
  ctx.save(); ctx.beginPath(); ctx.rect(wd.x - 200, midY, wd.ww + 400, wd.size); ctx.clip();
  ctx.fillStyle = S.split[1]; ctx.fillText(wd.txt, wd.x + dx, wd.base); ctx.restore();
  // thin cut line
  ctx.fillStyle = S.fg[0]; ctx.globalAlpha *= 0.85; ctx.fillRect(wd.x - 40 - dx, midY - 2, wd.ww + 80 + 2 * dx, 4);
}

// ------------------------------------------------------------------ decor (block-local, under/over text)
function decorUnder(ctx, b, t, S, active) {
  const L = b.line, fx = L.fx;
  if (fx === 'split') {
    const col = S.disc[b.i % S.disc.length];
    const p = eOutBack((t - b.line.t + 0.1) / 0.45, 1.4);
    const r = Math.max(b.tw, b.th) * 0.62 * p * (1 + 0.025 * beatPulse(t));
    ctx.fillStyle = col; ctx.beginPath(); ctx.arc(0, 0, Math.max(0, r), 0, Math.PI * 2); ctx.fill();
    ctx.strokeStyle = hexA(S.fg[0], 0.35); ctx.lineWidth = 4; ctx.beginPath(); ctx.arc(0, 0, Math.max(0, r * 1.12), 0, Math.PI * 2); ctx.stroke();
  }
  if (fx === 'wing') {
    const tk = L.words[1].t;
    const crack = eOutBack((t - tk) / 0.5, 1.2);
    const ox = -b.hw - 340, oy = 20;
    const R = rng(77);
    for (let f = 0; f < 9; f++) {
      const outer = f >= 5;
      ctx.save(); ctx.translate(ox, oy);
      if (outer) { ctx.translate(-60, 40); ctx.rotate(crack * 0.42); ctx.translate(crack * -20, crack * 120); ctx.translate(60, -40); }
      const ang = -0.95 + f * 0.2;
      const len = 260 + f * 22;
      ctx.rotate(ang + Math.PI);
      ctx.fillStyle = f % 2 ? C.cream : C.amber;
      const appear = eOutBack((t - L.t + 0.2 - f * 0.04) / 0.4, 1.5);
      ctx.scale(appear, appear);
      ctx.beginPath(); ctx.ellipse(len / 2, 0, len / 2, 34 + (R() * 8), 0, 0, Math.PI * 2); ctx.fill();
      ctx.restore();
    }
    // shoulder
    ctx.fillStyle = C.berry; ctx.beginPath(); ctx.arc(ox + 40, oy - 10, 80 * eOutBack((t - L.t + 0.2) / 0.4), 0, Math.PI * 2); ctx.fill();
    if (t > tk) {
      ctx.strokeStyle = C.ink; ctx.lineWidth = 12; ctx.lineJoin = 'miter'; ctx.beginPath();
      const pts = [[-120, -260], [-150, -170], [-100, -110], [-170, -20], [-120, 40], [-180, 140]];
      const n = Math.min(pts.length, 1 + Math.floor((t - tk) / 0.03));
      pts.slice(0, n).forEach(([x, y], k) => (k ? ctx.lineTo(ox + x, oy + y) : ctx.moveTo(ox + x, oy + y)));
      ctx.stroke();
    }
  }
  if (fx === 'eye') {
    const ey = -b.hh - 220, ew = 780, eh = 300;
    const app = eOutCubic((t - L.t + 0.3) / 0.5);
    const tk = L.words[2].t;
    const squint = eInOut3((t - tk + 0.1) / 0.35);
    const open = app * lerp(1, 0.42, squint);
    ctx.save(); ctx.translate(0, ey);
    ctx.beginPath(); ctx.moveTo(-ew / 2, 0); ctx.quadraticCurveTo(0, -eh * open, ew / 2, 0); ctx.quadraticCurveTo(0, eh * open * 0.8, -ew / 2, 0); ctx.closePath();
    ctx.fillStyle = C.cream; ctx.fill();
    ctx.save(); ctx.clip();
    const look = Math.sin((t - L.t) * 2.2) * 120 + squint * 150;
    ctx.fillStyle = C.amber; ctx.beginPath(); ctx.arc(look, 0, 115, 0, Math.PI * 2); ctx.fill();
    ctx.fillStyle = C.ink; ctx.beginPath(); ctx.arc(look, 0, 52, 0, Math.PI * 2); ctx.fill();
    ctx.fillStyle = C.cream; ctx.beginPath(); ctx.arc(look + 30, -30, 16, 0, Math.PI * 2); ctx.fill();
    ctx.restore();
    // lid line + brow
    ctx.strokeStyle = C.ink; ctx.lineWidth = 16; ctx.lineCap = 'round';
    ctx.beginPath(); ctx.moveTo(-ew / 2 - 20, 0); ctx.quadraticCurveTo(0, -eh * open - 10, ew / 2 + 20, 0); ctx.stroke();
    ctx.lineWidth = 26; ctx.strokeStyle = S.fg[0];
    ctx.beginPath(); ctx.moveTo(-ew * 0.45, -eh * 0.62 + squint * 40); ctx.quadraticCurveTo(0, -eh * 0.95 + squint * 30, ew * 0.45, -eh * 0.6 + squint * 110); ctx.stroke();
    ctx.restore();
  }
  if (fx === 'moon') {
    const app = eOutCubic((t - L.t + 0.4) / 1.0);
    const mx = b.hw + 170, my = -b.hh - 140, mr = 240;
    ctx.save(); ctx.globalAlpha *= app;
    const g = ctx.createRadialGradient(mx, my, mr * 0.6, mx, my, mr * 2.2);
    g.addColorStop(0, hexA(C.amber, 0.22)); g.addColorStop(1, hexA(C.amber, 0)); ctx.fillStyle = g;
    ctx.fillRect(mx - mr * 2.2, my - mr * 2.2, mr * 4.4, mr * 4.4);
    ctx.save(); ctx.beginPath(); ctx.arc(mx, my, mr, 0, Math.PI * 2); ctx.clip();
    ctx.beginPath(); ctx.arc(mx, my, mr, 0, Math.PI * 2); ctx.arc(mx + mr * 0.45, my - mr * 0.25, mr * 0.88, 0, Math.PI * 2);
    ctx.fillStyle = C.amber; ctx.fill('evenodd'); ctx.restore();
    ctx.fillStyle = C.cream; const R = rng(b.i * 31);
    for (let s = 0; s < 14; s++) {
      const sx = (R() - 0.5) * b.tw * 1.5, sy = (R() - 0.5) * b.th * 1.6 - 60, tw = 0.5 + 0.5 * Math.sin(t * 3 + s * 1.7);
      star4(ctx, sx, sy, 8 + 14 * R() * tw);
    }
    ctx.restore();
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
  }
  if (fx === 'dark') {
    const t0 = L.t - 0.3, t1 = L.words[2].t + 0.35;
    const p = clamp((t - t0) / (t1 - t0));
    const r = lerp(Math.max(b.tw, b.th) * 0.75, 0, eInCubic(p)) * (1 + 0.03 * beatPulse(t));
    ctx.fillStyle = C.amber; ctx.beginPath(); ctx.arc(0, 0, Math.max(0, r), 0, Math.PI * 2); ctx.fill();
  }
  if (fx === 'qmarks') {
    const R = rng(b.i * 17 + 3);
    for (let k = 0; k < 7; k++) {
      const ta = L.t + k * 0.12; if (t < ta - 0.05) continue;
      const px = (R() - 0.5) * b.tw * 1.7, py = (R() - 0.5) * b.th * 2.2, sz = 200 + R() * 320, rr = (R() - 0.5) * 0.7;
      const e = eOutBack((t - ta) / 0.35, 2);
      ctx.save(); ctx.translate(px, py); ctx.rotate(rr + Math.sin(t * 0.8 + k) * 0.08); ctx.scale(e, e);
      ctx.font = `${sz}px PFB`; ctx.textAlign = 'center';
      if (k % 2) { ctx.fillStyle = hexA(C.red, 0.55); ctx.fillText('?', 0, sz * 0.35); }
      else { ctx.lineWidth = 5; ctx.strokeStyle = hexA(C.cream, 0.5); ctx.strokeText('?', 0, sz * 0.35); }
      ctx.restore();
    }
  }
  if (fx === 'head') {
    const cols = [C.berryD, '#22385a', C.berryD, '#2a2a52'];
    const app = eOutCubic((t - b.tIn) / 0.6);
    ctx.save(); ctx.globalAlpha *= app;
    // echo outline of the head (conflicting second self)
    ctx.save(); ctx.translate(b.headMirror ? 40 : -40, 0); ctx.scale(1.0, 1);
    drawHeadOutline(ctx, b, t);
    ctx.restore();
    drawHead(ctx, 0, 170, 1.12, b.headMirror, cols[b.i % cols.length]);
    ctx.restore();
  }
  if (fx === 'clash') {
    const R = rng(b.i * 5 + 1);
    ctx.save(); ctx.globalAlpha *= 0.5;
    for (let k = 0; k < 5; k++) {
      const s = 0.25 + 0.75 * R();
      ctx.strokeStyle = k % 2 ? C.berry : C.sky; ctx.lineWidth = 3;
      const fr = Math.floor(t * 8);
      ctx.save(); ctx.translate((hash(fr * 3 + k) - 0.5) * 30, (hash(fr * 5 + k) - 0.5) * 30);
      ctx.beginPath(); ctx.arc((R() - 0.5) * 900, (R() - 0.5) * 600, 200 * s + 60, 0, Math.PI * 2); ctx.stroke(); ctx.restore();
    }
    ctx.restore();
  }
  if (fx === 'sun') {
    const ts = L.words[1].t;
    const p = clamp((t - ts + 0.05) / 0.9);
    if (p > 0) {
      const R0 = 5000 * eOutCubic(p);
      ctx.fillStyle = mixHex(C.berryD, C.amber, eOutCubic(p)); ctx.beginPath(); ctx.arc(0, 0, R0, 0, Math.PI * 2); ctx.fill();
      ctx.save(); ctx.rotate((t - ts) * 0.12); ctx.fillStyle = hexA('#ffd98a', 0.85 * eOutCubic(p));
      for (let k = 0; k < 18; k++) { ctx.beginPath(); ctx.moveTo(0, 0); ctx.arc(0, 0, R0, (k * 2 * Math.PI) / 18, ((k + 0.5) * 2 * Math.PI) / 18); ctx.closePath(); ctx.fill(); }
      ctx.restore();
      ctx.fillStyle = C.cream; ctx.beginPath(); ctx.arc(0, 0, 330 * eOutBack(p * 1.5, 1.3), 0, Math.PI * 2); ctx.fill();
    }
  }
  if (fx === 'echo') {
    const wd = b.words[0];
    for (let k = 0; k < 6; k++) {
      const te = L.t + 0.6 + k * 0.58 * 1.5;
      const age = t - te; if (age < 0 || age > 2.4) continue;
      const s = 1 + age * 0.35, a = (1 - age / 2.4) * 0.6;
      ctx.save(); ctx.scale(s, s); ctx.globalAlpha *= a;
      b.words.forEach((w) => drawWordText(ctx, w, S.acc, { stroke: 5 / s }));
      ctx.restore();
    }
  }
}
function drawHeadOutline(ctx, b, t) {
  const s = 1.12;
  ctx.save(); ctx.translate(0, 170); ctx.scale(b.headMirror ? -s : s, s); ctx.translate(-560, -550);
  const fr = Math.floor(t * 8);
  ctx.translate((hash(fr) - 0.5) * 18, (hash(fr + 99) - 0.5) * 18);
  headPath(ctx); ctx.lineWidth = 6; ctx.strokeStyle = hexA(C.sky, 0.6); ctx.stroke(); ctx.restore();
}

function decorOver(ctx, b, t, S) {
  const L = b.line, fx = L.fx;
  if (fx === 'echo') {
    [[175.0, -420, 330], [176.4, 380, -300], [176.6, 60, 420]].forEach(([te, x, y], k) => {
      const age = t - te; if (age < -0.05 || age > 1.6) return;
      const a = clamp((age + 0.05) / 0.15) * (1 - clamp((age - 0.8) / 0.8));
      ctx.save(); ctx.globalAlpha *= a; ctx.font = `${130 - k * 20}px PFB`; ctx.textAlign = 'center'; ctx.fillStyle = k === 1 ? C.berry : C.ink;
      ctx.fillText(up('biri'), x, y - age * 30); ctx.restore();
    });
  }
  if (fx === 'cage') {
    const x0 = -b.hw - 80, x1 = b.hw + 80, yb = b.hh + 60, yt = -b.hh - 40;
    const n = 9;
    ctx.strokeStyle = C.amber; ctx.lineCap = 'round';
    for (let k = 0; k < n; k++) {
      const ta = L.t + 0.05 * k;
      const p = eOutCubic((t - ta) / 0.35); if (p <= 0) continue;
      const x = lerp(x0, x1, k / (n - 1));
      const dome = Math.sqrt(Math.max(0, 1 - Math.pow((x / (x1 - x0)) * 2, 2)));
      const top = yt - 220 * dome;
      ctx.lineWidth = 16; ctx.beginPath(); ctx.moveTo(x, top); ctx.lineTo(x, lerp(top, yb, p)); ctx.stroke();
    }
    const pa = eOutCubic((t - L.t - 0.35) / 0.35);
    if (pa > 0) {
      ctx.globalAlpha *= pa; ctx.lineWidth = 22;
      ctx.beginPath(); ctx.moveTo(x0 - 30, yb); ctx.lineTo(x1 + 30, yb); ctx.stroke();
      ctx.lineWidth = 16; ctx.beginPath(); ctx.ellipse(0, yt, (x1 - x0) / 2, 220, 0, Math.PI, 2 * Math.PI); ctx.stroke();
      ctx.beginPath(); ctx.arc(0, yt - 270, 46, 0, Math.PI * 2); ctx.stroke();
    }
  }
  if (fx === 'arrows') {
    L.words.forEach((w, wi) => {
      if (!/suçlandım/.test(w.text)) return;
      for (let k = 0; k < 3; k++) {
        const ta = w.t + k * 0.07; const p = eOutBack((t - ta) / 0.3, 1.6); if (p <= 0) continue;
        const side = wi < 2 ? -1 : 1;
        const yy = (k - 1) * b.th * 0.36 + (wi < 2 ? -40 : 40);
        const tipX = side * (b.hw + 40);
        ctx.save(); ctx.translate(tipX + side * (1 - p) * 500, yy); ctx.scale(side, 1);
        ctx.fillStyle = k === 1 ? C.amber : C.cream;
        ctx.beginPath(); ctx.moveTo(0, 0); ctx.lineTo(90, -55); ctx.lineTo(90, -20); ctx.lineTo(330, -20); ctx.lineTo(330, 20); ctx.lineTo(90, 20); ctx.lineTo(90, 55); ctx.closePath(); ctx.fill();
        ctx.restore();
      }
    });
  }
}

// ------------------------------------------------------------------ block drawing
function drawBlock(ctx, b, t, S, isCur) {
  ctx.save();
  ctx.translate(b.x, b.y); ctx.rotate(b.rot); ctx.scale(b.scale, b.scale);
  const L = b.line;
  decorUnder(ctx, b, t, S, isCur);
  if (L.fx === 'head') { // text clipped inside the head
    ctx.save(); ctx.translate(0, 170); ctx.scale(b.headMirror ? -1.12 : 1.12, 1.12); ctx.translate(-560, -550); headPath(ctx); ctx.restore();
    ctx.save(); ctx.clip();
  }
  const style = S.style || 'rise';
  for (const wd of b.words) {
    ctx.save();
    let col = wd.col;
    if (L.fx === 'sun' && t > L.words[1].t) col = wd.acc ? C.berry : C.ink;
    if (L.fx === 'dark') { const p = clamp((t - L.words[2].t) / 0.6); col = mixHex(C.ink, '#2a2745', p); }
    if (L.fx === 'split' && t < wd.t - 0.05) { // ghost preview of upcoming words
      ctx.globalAlpha *= 0.16; drawWordText(ctx, wd, S.fg[0], { stroke: 3 }); ctx.restore(); continue;
    }
    if (L.fx === 'crumble') {
      if (t < wd.t - 0.05) { ctx.restore(); continue; }
      drawCrumbleWord(ctx, wd, t, col, b); ctx.restore(); continue;
    }
    if (!wordAppear(ctx, wd, t, L.fx === 'tek' ? 'slam' : style, b)) { ctx.restore(); continue; }
    if (L.fx === 'split' && wd.row === 0) { drawSplitWord(ctx, wd, t, S, b); ctx.restore(); continue; }
    if (L.fx === 'clash') {
      const fr = Math.floor(t * 8);
      const jx = (hash(fr * 13 + wd.idx) - 0.5) * 16, jy = (hash(fr * 7 + wd.idx) - 0.5) * 16;
      ctx.translate(jx, jy);
      const cx = wd.x + wd.ww / 2, cy = wd.base - wd.ch / 2;
      ctx.translate(cx, cy); ctx.rotate((hash(wd.idx + 50) - 0.5) * 0.12 + (hash(fr + wd.idx) - 0.5) * 0.03); ctx.translate(-cx, -cy);
      ctx.save(); ctx.globalAlpha *= 0.8; ctx.translate(-9, 0); drawWordText(ctx, wd, C.berry); ctx.translate(18, 0); drawWordText(ctx, wd, C.sky); ctx.restore();
    }
    if (L.fx === 'head' || L.fx === 'echo') col = L.fx === 'echo' ? S.fg[0] : C.cream;
    drawWordText(ctx, wd, col);
    ctx.restore();
  }
  if (L.fx === 'head') ctx.restore();
  decorOver(ctx, b, t, S);
  ctx.restore();
}

function drawCrumbleWord(ctx, wd, t, col, b) {
  const pApp = clamp((t - wd.t + 0.05) / 0.2);
  ctx.font = `${wd.size}px ${wd.f}`; ctx.fillStyle = col;
  const start = wd.t + 0.75;
  const chars = [...wd.txt];
  let acc = '';
  chars.forEach((chr, j) => {
    const x = wd.x + (w100(wd.f, acc) * wd.size) / 100; acc += chr;
    const cw = (w100(wd.f, chr) * wd.size) / 100;
    const ts = start + j * 0.035 + hash(wd.idx * 31 + j) * 0.12;
    const tau = Math.max(0, t - ts);
    ctx.save();
    ctx.globalAlpha *= pApp * (1 - clamp(tau / 0.9));
    const dy = 0.5 * 3200 * tau * tau, rot = tau * (hash(j + wd.idx * 3) - 0.5) * 6;
    ctx.translate(x + cw / 2, wd.base - wd.ch / 2 + dy); ctx.rotate(rot);
    ctx.fillText(chr, -cw / 2, wd.ch / 2);
    ctx.restore();
  });
}

// ------------------------------------------------------------------ screen-space layers
function drawBG(ctx, t, S, secKey) {
  ctx.fillStyle = S.bg; ctx.fillRect(0, 0, W, H);
  const gx = W * (0.5 + 0.28 * Math.sin(t * 0.13)), gy = H * (0.45 + 0.2 * Math.cos(t * 0.17));
  const g = ctx.createRadialGradient(gx, gy, 0, gx, gy, H * 1.1);
  g.addColorStop(0, hexA(S.bg2, 0.9)); g.addColorStop(1, hexA(S.bg2, 0));
  ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
}

function drawMarquee(ctx, t, b) {
  // "ÇOĞALDI" multiplying in the background
  const L = b.line;
  const n = clamp(Math.floor((t - L.t + 0.3) / 0.22) + 1, 0, 10);
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
  const t0 = L.t - 0.3, t1 = L.words[2].t + 0.35;
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
    if (t < bk.t0 - 0.05 || t > bk.t1 + 0.4) continue;
    const txt = bk.text;
    const size = 68;
    ctx.save();
    ctx.font = `${size}px PFS`;
    const tw = ctx.measureText(txt).width;
    const x0 = W / 2 - tw / 2, y = H - 70;
    const out = clamp((t - bk.t1) / 0.4);
    const light = S.bg === C.amber;
    ctx.shadowColor = light ? 'rgba(255,240,210,0.6)' : 'rgba(0,0,0,0.65)'; ctx.shadowBlur = 18;
    // thin rule
    const pr = eOutCubic((t - bk.t0) / 0.5);
    ctx.fillStyle = hexA(light ? C.ink : C.amber, 0.9 * (1 - out));
    ctx.fillRect(W / 2 - (tw / 2 + 40) * pr, y + 24, (tw + 80) * pr, 3);
    let acc = '';
    const dur = Math.max(0.3, Math.min(0.9, (bk.t1 - bk.t0) * 0.7));
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
    const age = t - s.t + 0.04;
    if (age < 0 || age > 1.0) continue;
    const sc = lerp(2.8, 1, eOutCubic(age / 0.14));
    const a = clamp(age / 0.06) * (1 - clamp((age - 0.7) / 0.3));
    ctx.save(); ctx.globalAlpha = a;
    ctx.translate(W * 0.5, H * 0.5); ctx.rotate(-0.12); ctx.scale(sc, sc);
    ctx.font = '300px PFB'; ctx.textAlign = 'center';
    const txt = up(s.words[0].text);
    ctx.lineWidth = 22; ctx.lineJoin = 'round'; ctx.strokeStyle = C.cream; ctx.strokeText(txt, 0, 105);
    ctx.fillStyle = C.red; ctx.fillText(txt, 0, 105);
    ctx.restore();
  }
}

function drawWipe(ctx, t, b, Sold, Snew) {
  // skewed two-layer wipe: accent slab leads, new background follows; full cover at midpoint
  const p = clamp((t - b.wipe0) / (b.wipe1 - b.wipe0));
  if (p <= 0 || p >= 1) return;
  const e = eInOut3(p);
  const sk = 300;
  const slab = (x, col) => { ctx.fillStyle = col; ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x + W + sk, 0); ctx.lineTo(x + W, H); ctx.lineTo(x - sk, H); ctx.closePath(); ctx.fill(); };
  const x = lerp(-W - 2 * sk, W + 2 * sk, e);
  slab(x + 180, Snew.acc || C.amber);
  slab(x, Snew.bg);
}

function letterbox(ctx, h) { if (h <= 0) return; ctx.fillStyle = '#000'; ctx.fillRect(0, 0, W, h); ctx.fillRect(0, H - h, W, h); }

// ------------------------------------------------------------------ intro / outro
function drawTitleScene(ctx, t, mode) {
  // mode 'intro' (0..INTRO_END) or 'outro'
  const S = SEC[mode];
  drawBG(ctx, t, S);
  const local = mode === 'intro' ? t : t - OUTRO_START;
  // two silhouettes facing each other: the old self and the new self
  const inP = mode === 'intro' ? eOutCubic((local - 0.6) / 3.2) : 1;
  const breathe = 1 + 0.008 * Math.sin(t * 1.3);
  const sz = 0.72 * breathe;
  let leftCol = C.cream, rightCol = C.berry;
  if (mode === 'outro') leftCol = t >= 179.42 ? C.berry : C.cream;
  ctx.save(); ctx.globalAlpha = inP;
  drawHead(ctx, lerp(-200, 250, inP), 600, sz, false, leftCol);
  drawHead(ctx, lerp(W + 200, W - 250, inP), 600, sz, true, rightCol);
  ctx.restore();
  // title
  const word = up('bambaşka');
  ctx.save(); ctx.font = '210px Anton'; ctx.textAlign = 'left';
  const tw = ctx.measureText(word).width; let x = W / 2 - tw / 2; let acc = '';
  const t0 = mode === 'intro' ? 5.76 : OUTRO_START + 0.15;
  const gap = mode === 'intro' ? 0.29 : 0.17;
  [...word].forEach((ch, j) => {
    const cx = W / 2 - tw / 2 + ctx.measureText(acc).width; acc += ch;
    const ta = t0 + j * gap;
    const p = clamp((t - ta) / 0.35); if (p <= 0) return;
    const dy = (1 - eOutBack(p, 2.2)) * -260;
    ctx.globalAlpha = clamp(p * 3);
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
  if (b.line.fx === 'clone2') drawMarquee(ctx, t, b);
  const cam = camAt(t, k);
  const drift = { x: Math.sin(t * 0.31) * 10, y: Math.cos(t * 0.23) * 8, r: Math.sin(t * 0.19) * 0.006 };
  const z = cam.z * (1 + punch(t));
  ctx.save();
  ctx.translate(W / 2, H / 2); ctx.scale(z, z); ctx.rotate(-(cam.rot + drift.r)); ctx.translate(-cam.x - drift.x / z, -cam.y - drift.y / z);
  for (let j = Math.max(0, k - 2); j <= Math.min(BLOCKS.length - 1, k + 1); j++) {
    const bj = BLOCKS[j];
    if (bj.line.sec !== b.line.sec) continue;
    if (j > k) continue;
    let a = 1;
    if (j < k) { a = 0.42 * (1 - clamp((t - b.mv1) / 0.9)); if (j < k - 1) a *= 0.5; }
    if (a <= 0.01) continue;
    ctx.save(); ctx.globalAlpha = a; drawBlock(ctx, bj, t, S, j === k); ctx.restore();
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
    const lb = 130 * (1 - eInOut3((t - (INTRO_END - 0.5)) / 0.5));
    letterbox(mc, lb);
  } else if (t >= OUTRO_START) {
    drawTitleScene(mc, t, 'outro');
    const lo = t - OUTRO_START;
    letterbox(mc, 130 * eInOut3((t - 180.2) / 2.6));
  } else {
    const b = BLOCKS[k];
    const cam0 = camAt(t, k);
    if (cam0.moving) {
      // motion blur: average subframes across a 180° shutter
      const N = 5;
      for (let s = 0; s < N; s++) {
        const ts = t - (0.5 / FPS) * (s / (N - 1));
        sc.globalAlpha = 1; renderWorld(sc, ts, k);
        mc.globalAlpha = 1 / (s + 1); mc.drawImage(sub, 0, 0);
      }
      mc.globalAlpha = 1;
    } else renderWorld(mc, t, k);
    if (b.line.fx === 'dark') drawDarkOverlay(mc, t, b);
    // section wipe into the next section is drawn by the next block (before its tIn)
    const n = BLOCKS[k + 1];
    if (n && n.newSec && t >= n.wipe0) drawWipe(mc, t, n, SEC[b.line.sec], SEC[n.line.sec]);
    if (b.newSec && t < b.wipe1) drawWipe(mc, t, b, null, SEC[b.line.sec]);
    // into outro
    if (t > OUTRO_START - 0.45) drawWipe(mc, t, { wipe0: OUTRO_START - 0.45, wipe1: OUTRO_START + 0.0 }, null, SEC.outro);
    drawBacking(mc, t, SEC[b.line.sec]);
    drawStamps(mc, t);
    if (b.line.sec === 'br') letterbox(mc, 90 * eOutCubic((t - BLOCKS.find((x) => x.line.sec === 'br').tIn) / 1.0) * (b.line.fx === 'sun' ? 1 - clamp((t - b.line.words[1].t) / 0.6) : 1));
  }
  // intro -> first block wipe
  if (k < 0 && t > BLOCKS[0].wipe0) drawWipe(mc, t, BLOCKS[0], SEC.intro, SEC[BLOCKS[0].line.sec]);
  // finishing: grain + vignette + global fades
  mc.save();
  mc.globalCompositeOperation = 'overlay'; mc.globalAlpha = 0.2;
  mc.drawImage(GRAIN[Math.floor(t * FPS) % GRAIN.length], 0, 0, W, H);
  mc.restore();
  mc.save(); mc.globalAlpha = 1; mc.drawImage(VIG, 0, 0); mc.restore();
  const fin = Math.min(clamp(t / 1.2), 1 - clamp((t - (DURATION - 2.2)) / 1.9));
  if (fin < 1) { mc.fillStyle = `rgba(0,0,0,${1 - fin})`; mc.fillRect(0, 0, W, H); }
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
} else if (mode === 'info') {
  BLOCKS.forEach((b) => console.log(b.i, b.line.sec, b.line.fx || '', b.tIn.toFixed(2), b.tOut.toFixed(2), b.words.map((w) => w.txt).join(' '), 'z=' + b.cam.z.toFixed(2)));
}
