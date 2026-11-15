// Araz FM TV banner v5 — broadcast lower-third, Araz teal + white only (flag in its own colours).
// Structure: left teal wing with Araz logo | white message panel | right teal wing "103.3 FM".
// window.renderV6(ctx, t, A, TL)  Canvas 1920x1080, transparent.
const T = '#095D6A', T2 = '#0B7482', T3 = '#3E97A1', T4 = '#8CC6CB', TW = '#E8F3F4';
const FLAGC = ['#00B5E2', '#EF3340', '#509E2F'];
const clamp = (v, a = 0, b = 1) => Math.max(a, Math.min(b, v));
const eOut = p => 1 - Math.pow(1 - p, 3), eIn = p => p * p * p, eOut5 = p => 1 - Math.pow(1 - p, 5);
const eIO = p => p < .5 ? 4 * p * p * p : 1 - Math.pow(-2 * p + 2, 3) / 2;
const eBack = p => { const c = 1.4; return 1 + (c + 1) * Math.pow(p - 1, 3) + c * Math.pow(p - 1, 2); };
const seg = (t, a, b) => clamp((t - a) / (b - a));
const hash = (i, j = 0) => { const x = Math.sin(i * 127.1 + j * 311.7) * 43758.5453; return x - Math.floor(x); };
const rr = (c, x, y, w, h, r) => { c.beginPath(); c.roundRect(x, y, w, h, r); };

const PY = 872, CY = 978, TOPW = 856, SL = 52;              // panel top, text centre, wing top, slant
const LW = 300, RW = 1668;                                   // left wing edge (top), right wing edge (top)
const AREA = [LW + 20, RW - SL - 20];

function star8Path(c, cx, cy, r, inner = .72) {
  c.beginPath();
  for (let i = 0; i < 16; i++) { const a = i * Math.PI / 8 - Math.PI / 2, rad = i % 2 ? r * inner : r;
    const x = cx + Math.cos(a) * rad, y = cy + Math.sin(a) * rad; i ? c.lineTo(x, y) : c.moveTo(x, y); }
  c.closePath();
}
function rhombus(c, cx, cy, rx, ry) { c.beginPath(); c.moveTo(cx, cy - ry); c.lineTo(cx + rx, cy); c.lineTo(cx, cy + ry); c.lineTo(cx - rx, cy); c.closePath(); }

// ---------- cached textures
let GIRIH = null, FLAG = null, PANELPAT = null;
function makeGirih(W, H, alpha) { // white interlace of 8-point stars for the wings
  const cv = document.createElement('canvas'); cv.width = W; cv.height = H; const c = cv.getContext('2d');
  c.strokeStyle = `rgba(255,255,255,${alpha})`; c.lineWidth = 1.6;
  const s = 56;
  for (let x = -s; x < W + s; x += s) for (let y = -s; y < H + s; y += s) {
    star8Path(c, x, y, s * .5, .74); c.stroke();
    rhombus(c, x + s / 2, y + s / 2, 8, 8); c.stroke();
  }
  return cv;
}
function makePanelPattern() { // very faint teal geometric texture for the white panel
  const W = 1920, H = 210, cv = document.createElement('canvas'); cv.width = W; cv.height = H; const c = cv.getContext('2d');
  c.strokeStyle = 'rgba(9,93,106,.045)'; c.lineWidth = 1.4;
  const s = 70;
  for (let x = 0; x < W + s; x += s) for (let y = 0; y < H + s; y += s) { star8Path(c, x + (y / s % 2 ? s / 2 : 0), y, s * .42, .7); c.stroke(); }
  return cv;
}
function makeFlag() {
  const W = 1200, H = 600, cv = document.createElement('canvas'); cv.width = W; cv.height = H; const c = cv.getContext('2d');
  FLAGC.forEach((col, k) => { c.fillStyle = col; c.fillRect(0, k * H / 3, W, H / 3 + 1); });
  const cx = W / 2, cy = H / 2;
  c.beginPath(); c.arc(cx - 24, cy, 90, 0, 7); c.fillStyle = '#fff'; c.fill();
  c.beginPath(); c.arc(cx - 2, cy, 75, 0, 7); c.fillStyle = FLAGC[1]; c.fill();
  star8Path(c, cx + 94, cy, 44, .55); c.fillStyle = '#fff'; c.fill();
  // fabric weave
  for (let y = 0; y < H; y += 3) { c.fillStyle = `rgba(0,0,0,${.025 + .02 * (y % 6 === 0)})`; c.fillRect(0, y, W, 1); }
  for (let x = 0; x < W; x += 3) { c.fillStyle = 'rgba(255,255,255,.025)'; c.fillRect(x, 0, 1, H); }
  return cv;
}

// ---------- text layout → per-character items
const LINES = [
  { text: 'Azərbaycanın səsi bu dalğada!', kw: 'səsi' },
  { text: 'Bizə rəqəmsalda da qoşul!', social: true, kw: 'rəqəmsalda' },
  { text: 'Milli musiqinin dəyişməz ünvanı!', kw: 'Milli' },
  { text: 'QOVUŞDURAN RADİO!', big: true },
];
const LCACHE = {};
function layout(c, li) {
  if (LCACHE[li]) return LCACHE[li];
  const L = LINES[li], items = [], FS = L.big ? 64 : 58, font = `${L.big ? 800 : 600} ${FS}px Montserrat`;
  c.font = font; const tw = c.measureText(L.text).width;
  let extra = 0; const fUrl = `600 ${FS * .62}px Montserrat`;
  if (L.social) { c.font = fUrl; extra = 64 + 3 * 54 + 16 + c.measureText('arazfm.az').width; }
  const mid = (AREA[0] + AREA[1]) / 2; let x = mid - (tw + extra) / 2;
  const chars = (txt, f, kwr) => { c.font = f; let i = 0; for (const ch of txt) { const w = c.measureText(ch).width; items.push({ ch, x: x + w / 2, w, font: f, kw: kwr && i >= kwr[0] && i < kwr[1] }); x += w; i++; } };
  const ks = L.kw ? [...L.text].findIndex((_, i) => [...L.text].slice(i, i + [...L.kw].length).join('') === L.kw) : -1;
  chars(L.text, font, ks >= 0 ? [ks, ks + [...L.kw].length] : null);
  if (ks >= 0) { const kc = items.filter(q => q.kw); items.kwBox = [kc[0].x - kc[0].w / 2, kc[kc.length - 1].x + kc[kc.length - 1].w / 2]; }
  if (L.social) {
    x += 64; for (let k = 0; k < 3; k++) { items.push({ icon: k, x: x + 17 }); x += 54; }
    x += 16 - 54 + 54; chars('arazfm.az', fUrl);
  }
  return (LCACHE[li] = items);
}
function icon(c, k) {
  const s = 34; c.strokeStyle = T; c.fillStyle = T; c.lineWidth = 3.2;
  if (k === 0) { c.font = `800 ${s * 1.05}px Montserrat`; c.textAlign = 'center'; c.textBaseline = 'middle'; c.fillText('f', 0, 2); }
  if (k === 1) { rr(c, -s / 2, -s / 2, s, s, 9); c.stroke(); c.beginPath(); c.arc(0, 0, 7.5, 0, 7); c.stroke(); c.beginPath(); c.arc(9, -9, 2, 0, 7); c.fill(); }
  if (k === 2) { rr(c, -23, -15.5, 46, 31, 9); c.stroke(); c.beginPath(); c.moveTo(-5, -7); c.lineTo(8, 0); c.lineTo(-5, 7); c.closePath(); c.fill(); }
}
// draw one glyph with horizontal motion smear m (0 = crisp, 1 = fully smeared)
function glyph(c, it, x, y, m, a, dir, fill) {
  if (a <= .003) return;
  const n = m > .02 ? 16 : 1, spread = 90 * m;
  c.save(); c.translate(x, y); c.scale(1 + 1.6 * m, 1 - .1 * m);
  for (let i = 0; i < n; i++) {
    const f = n === 1 ? 0 : i / (n - 1) - .5;
    c.globalAlpha = a * (n === 1 ? 1 : 2.2 / n * (1 - Math.abs(f)));
    c.save(); c.translate(f * spread * dir, 0);
    if (it.icon !== undefined) icon(c, it.icon);
    else { c.font = it.font; c.fillStyle = fill || T; c.textAlign = 'center'; c.textBaseline = 'middle'; c.fillText(it.ch, 0, 3); }
    c.restore();
  }
  c.restore(); c.globalAlpha = 1;
}

// ---------- waving flag
function drawFlag(c, t, sc, cx, cy, fold) {
  if (sc <= 0) return;
  const W = 330 * sc * (1 - fold), H = 165 * sc, x0 = cx - W / 2, sw = 2;
  c.save(); c.shadowColor = 'rgba(0,0,0,.28)'; c.shadowBlur = 18; c.shadowOffsetY = 6;
  c.fillStyle = 'rgba(0,0,0,.001)'; c.fillRect(x0, cy - H / 2, W, H); c.restore();
  for (let x = 0; x < W; x += sw) {
    const u = x / Math.max(1, W);
    const ph1 = u * 9 - t * 6.5, ph2 = u * 15 - t * 9.1 + 1.3;
    const amp = H * (.03 + .06 * u);
    const off = Math.sin(ph1) * amp + Math.sin(ph2) * amp * .35;
    const sl = Math.cos(ph1) * .8 + Math.cos(ph2) * .3;
    const h = H * (1 - .03 * Math.abs(Math.sin(ph1)));
    c.drawImage(FLAG, u * 1200, 0, Math.max(1, sw / W * 1200), 600, x0 + x, cy - h / 2 + off, sw + .6, h);
    // cloth light: highlights on crests, shadows in troughs
    if (sl > 0) { c.fillStyle = `rgba(255,255,255,${sl * .22})`; } else { c.fillStyle = `rgba(0,10,20,${-sl * .26})`; }
    c.fillRect(x0 + x, cy - h / 2 + off, sw + .6, h);
  }
  // specular gloss travelling across
  const gx = x0 + ((t * 260) % (W + 300)) - 150;
  const gg = c.createLinearGradient(gx - 60, 0, gx + 60, 0); gg.addColorStop(0, 'rgba(255,255,255,0)'); gg.addColorStop(.5, 'rgba(255,255,255,.14)'); gg.addColorStop(1, 'rgba(255,255,255,0)');
  c.save(); c.beginPath(); c.rect(x0, cy - H / 2 - 20, W, H + 40); c.clip(); c.fillStyle = gg; c.fillRect(gx - 60, cy - H / 2 - 20, 120, H + 40); c.restore();
}

// ---------- wings
function wingPath(c, side, dx, inset = 0) {
  c.beginPath();
  if (side < 0) { c.moveTo(-10 + dx, TOPW + inset); c.lineTo(LW + dx - inset, TOPW + inset); c.lineTo(LW - SL + dx - inset, 1080); c.lineTo(-10 + dx, 1080); }
  else { c.moveTo(RW + dx + inset, TOPW + inset); c.lineTo(1930 + dx, TOPW + inset); c.lineTo(1930 + dx, 1080); c.lineTo(RW - SL + dx + inset, 1080); }
  c.closePath();
}
function drawWing(c, t, side, p, A, extra) {
  const layers = [[T4, 26, 0], [T3, 13, .07], [T2, 0, .14]];
  layers.forEach(([col, o, d]) => {
    const q = eOut5(seg(p, d, d + .75)); if (q <= 0) return;
    const dx = side * (1 - q) * 420 + side * o * 0;
    c.save(); c.translate(side * -o * 0, 0);
    wingPath(c, side, dx + side * -o, 0);
    c.fillStyle = col; c.fill(); c.restore();
  });
  const q = eOut5(seg(p, .2, .95)); if (q <= 0) return;
  const dx = side * (1 - q) * 420;
  c.save(); wingPath(c, side, dx, 0);
  const g = c.createLinearGradient(0, TOPW, 0, 1080); g.addColorStop(0, '#0C6F7C'); g.addColorStop(1, '#063F48');
  c.fillStyle = g; c.shadowColor = 'rgba(0,0,0,.3)'; c.shadowBlur = 16; c.fill(); c.shadowColor = 'transparent';
  c.clip();
  // girih interlace drifting slowly + shimmering light band
  const off = (t * 6) % 56;
  c.globalAlpha = .9; c.drawImage(GIRIH, (side < 0 ? 0 : RW - 80) - off + dx, TOPW - off); c.globalAlpha = 1;
  const sx = (side < 0 ? -200 : RW - 200) + ((t * 120 + (side > 0 ? 300 : 0)) % 900);
  const sg = c.createLinearGradient(sx, 0, sx + 160, 0); sg.addColorStop(0, 'rgba(255,255,255,0)'); sg.addColorStop(.5, 'rgba(255,255,255,.10)'); sg.addColorStop(1, 'rgba(255,255,255,0)');
  c.fillStyle = sg; c.fillRect(sx + dx, TOPW, 160, 230);
  // top highlight edge
  c.fillStyle = 'rgba(255,255,255,.35)'; c.fillRect(-20 + dx, TOPW, 1960, 2);
  extra(c, dx, q);
  c.restore();
}

// ---------- scene
window.renderV6 = function (c, t, A, TL) {
  if (!GIRIH) { GIRIH = makeGirih(420, 300, .13); FLAG = makeFlag(); PANELPAT = makePanelPattern(); }
  const it = TL.noIntro ? 99 : t;
  const at = TL.at; let k = -1; for (let i = 0; i < at.length; i++) if (t >= at[i]) k = i;
  const li = k >= 0 ? TL.lines[k] : null, prev = k > 0 ? TL.lines[k - 1] : null, tc = k >= 0 ? t - at[k] : -1;
  const flagSwap = li === 3 && prev === 2, D = TL.flagDur || 3.2;
  const logoPulse = flagSwap ? Math.exp(-Math.pow((tc - (D - .2)) / .35, 2)) : 0;

  // 1. light line shoots from centre (intro)
  const lp = seg(it, 0, .45);
  if (lp > 0 && lp < 1) {
    const half = 980 * eOut(lp);
    const g = c.createLinearGradient(960 - half, 0, 960 + half, 0); g.addColorStop(0, 'rgba(140,198,203,0)'); g.addColorStop(.5, 'rgba(230,248,250,1)'); g.addColorStop(1, 'rgba(140,198,203,0)');
    c.fillStyle = g; c.fillRect(960 - half, PY - 2, half * 2, 4);
  }
  // 2. white panel opens vertically from that line
  const pp = eOut5(seg(it, .25, .9));
  if (pp > 0) {
    const top = PY, h = (1080 - PY) * pp;
    c.save(); c.shadowColor = 'rgba(0,0,0,.22)'; c.shadowBlur = 26; c.shadowOffsetY = -3;
    const g = c.createLinearGradient(0, top, 0, 1080); g.addColorStop(0, '#FFFFFF'); g.addColorStop(.55, '#FBFDFD'); g.addColorStop(1, '#E6F1F2');
    c.fillStyle = g; c.fillRect(0, top, 1920, h); c.shadowColor = 'transparent';
    c.beginPath(); c.rect(0, top, 1920, h); c.clip();
    c.drawImage(PANELPAT, -((t * 5) % 70), top);
    // kilim border: teal rule + rhombus chain
    c.fillStyle = T; c.fillRect(0, top, 1920, 3.5);
    for (let x = LW + 10, i = 0; x < RW - 10; x += 22, i++) { rhombus(c, x, top + 14, 6, 4.5); c.fillStyle = i % 2 ? 'rgba(9,93,106,.55)' : 'rgba(9,93,106,.22)'; c.fill(); }
    c.fillStyle = 'rgba(9,93,106,.25)'; c.fillRect(0, top + 24, 1920, 1);
    // glare sweep across the panel (every 6 s and on each change)
    const gs = tc >= 0 && tc < 1.1 && !flagSwap ? seg(tc, .1, 1.1) : seg((t % 6.5), 0, 1.3);
    if (gs > 0 && gs < 1 && it > 1.5) {
      const gx = -400 + 2700 * eIO(gs), gg = c.createLinearGradient(gx - 180, 0, gx + 180, 0);
      gg.addColorStop(0, 'rgba(140,198,203,0)'); gg.addColorStop(.5, 'rgba(140,198,203,.18)'); gg.addColorStop(1, 'rgba(140,198,203,0)');
      c.save(); c.transform(1, 0, -.35, 1, 0, 0); c.fillStyle = gg; c.fillRect(gx - 180 + 340, top, 360, 220); c.restore();
    }
    c.restore();
  }
  // 3. wings
  drawWing(c, t, -1, seg(it, .35, 1.4), A, (c, dx, q) => {
    const img = A.white, lh = 66, lw = img.width * lh / img.height, cx = 128 + dx, cy = CY - 2;
    const s = (.85 + .15 * eBack(seg(it, .9, 1.5))) * (1 + .06 * logoPulse);
    c.globalAlpha = seg(it, .9, 1.2); c.save(); c.translate(cx, cy); c.scale(s, s); c.drawImage(img, -lw / 2, -lh / 2, lw, lh); c.restore(); c.globalAlpha = 1;
    // lens flare sweep over logo on entry and on the flag reveal
    const fl = Math.max(seg(it, 1.05, 1.6) * (it < 1.6 ? 1 : 0), logoPulse);
    if (fl > 0) { const fx = cx - 110 + 220 * (it < 1.6 ? seg(it, 1.05, 1.6) : .5); const fg = c.createRadialGradient(fx, cy, 0, fx, cy, 70); fg.addColorStop(0, `rgba(255,255,255,${.55 * (it < 1.6 ? Math.sin(Math.PI * seg(it, 1.05, 1.6)) : logoPulse)})`); fg.addColorStop(1, 'rgba(255,255,255,0)'); c.fillStyle = fg; c.fillRect(fx - 70, cy - 70, 140, 140); }
  });
  drawWing(c, t, 1, seg(it, .45, 1.5), A, (c, dx, q) => {
    // frequency with odometer roll 88.0 → 103.3
    const r = seg(it, 1.0, 2.0), f = it < 2 ? 88 + (103.3 - 88) * eOut(r) : 103.3;
    const txt = f.toFixed(1), cx = 1800 + dx, cy = CY - 14;
    c.globalAlpha = seg(it, .95, 1.15);
    c.font = '800 50px Montserrat'; c.fillStyle = '#fff'; c.textAlign = 'center'; c.textBaseline = 'middle'; c.fillText(txt, cx, cy);
    c.font = '700 22px Montserrat'; c.fillStyle = TW; c.fillText('FM', cx - 46, cy + 40);
    // mini equalizer
    for (let b = 0; b < 5; b++) {
      const h = 6 + 16 * Math.abs(Math.sin(t * (3.2 + b * .9) + b * 1.7)) * (it > 1.5 ? 1 : seg(it, 1, 1.5));
      c.fillStyle = 'rgba(232,243,244,.9)'; rr(c, cx - 10 + b * 10, cy + 52 - h, 6, h, 2); c.fill();
    }
    c.globalAlpha = 1;
  });

  // 3b. "Hazırda efirdə" tab (rises from behind the panel top)
  // (now-playing tab removed at the user's request)

  if (k < 0) return;
  // 4. message text
  c.save(); c.beginPath(); c.rect(LW - 10, PY + 26, RW - LW - SL + 20, 1080 - PY - 26); c.clip();
  if (flagSwap) {
    const old = layout(c, 2);
    old.forEach((g, i) => { const p = seg(tc, .05 + Math.abs(g.x - 960) / 900 * .25, .45 + Math.abs(g.x - 960) / 900 * .25); glyph(c, g, g.x + Math.sign(g.x - 960) * 80 * eIn(p), CY, eIn(p), 1 - p, Math.sign(g.x - 960) || 1); });
    const items = layout(c, 3), r0 = D - .25;
    items.forEach((g, i) => { const d = Math.abs(g.x - 960) / 700; const p = seg(tc, r0 + d * .3, r0 + .5 + d * .3); glyph(c, g, 960 + (g.x - 960) * eOut(p), CY, 1 - eOut(p), eOut(p), Math.sign(g.x - 960) || 1); });
    c.restore();
    starFlag(c, t, tc, D, old);
    return;
  }
  const items = layout(c, li);
  if (prev !== null && tc < .8) {
    const o = layout(c, prev);
    const ka = 1 - seg(tc, 0, .25);
    if (o.kwBox && ka > 0) kwPill(c, o.kwBox, 1, ka);
    o.forEach((g, i) => { const p = seg(tc, i * .012, .32 + i * .012); glyph(c, g, g.x - 140 * eIn(p), CY, eIn(p), 1 - eIn(p) * .9 - p * .1, -1, g.kw && ka > .5 ? '#fff' : null); });
  }
  // keyword highlight: teal bar slides in under the word after the line settles
  const kp = items.kwBox ? eOut5(seg(tc, 1.25, 1.75)) : 0;
  if (kp > 0) kwPill(c, items.kwBox, kp, 1);
  items.forEach((g, i) => { const p = seg(tc, .28 + i * .016, .78 + i * .016);
    let fill = null; if (g.kw && kp > 0) { const edge = items.kwBox[0] - 9 + (items.kwBox[1] - items.kwBox[0] + 18) * kp; if (g.x < edge) fill = '#fff'; }
    glyph(c, g, g.x + 160 * (1 - eOut5(p)), CY, 1 - eOut5(p), eOut(p), 1, fill); });
  c.restore();
};

function kwPill(c, box, p, a) {
  const x0 = box[0] - 9, w = (box[1] - box[0] + 18) * p, y = CY - 37, h = 76;
  c.save(); c.globalAlpha = a;
  c.beginPath(); c.moveTo(x0 + 6, y); c.lineTo(x0 + w + 6, y); c.lineTo(x0 + w - 4, y + h); c.lineTo(x0 - 4, y + h); c.closePath();
  const g = c.createLinearGradient(0, y, 0, y + h); g.addColorStop(0, '#0C6F7C'); g.addColorStop(1, T); c.fillStyle = g; c.fill();
  // small rhombus accents at the ends
  if (p > .95) {  }
  c.restore();
}

function nowPlaying(c, t, p, song) {
  const y0 = PY - 56, h = 56, xl = 318, xr = 1110, sl = 13, oy = (1 - p) * h;
  c.save(); c.beginPath(); c.rect(0, 0, 1920, PY); c.clip(); c.translate(0, oy);
  c.beginPath(); c.moveTo(xl + sl, y0); c.lineTo(xr + sl, y0); c.lineTo(xr, y0 + h); c.lineTo(xl, y0 + h); c.closePath();
  const g = c.createLinearGradient(xl, 0, xr, 0); g.addColorStop(0, '#0B6B78'); g.addColorStop(1, '#074C56');
  c.shadowColor = 'rgba(0,0,0,.25)'; c.shadowBlur = 12; c.fillStyle = g; c.fill(); c.shadowColor = 'transparent';
  c.save(); c.clip(); c.globalAlpha = .7; c.drawImage(GIRIH, xl - ((t * 6) % 56), y0 - 40); c.restore(); c.globalAlpha = 1;
  c.fillStyle = 'rgba(255,255,255,.35)'; c.fillRect(xl + sl, y0, xr - xl, 1.5);
  const cy = y0 + h / 2 + 1;
  // live dot + mini equalizer
  const pulse = .6 + .4 * Math.sin(t * 5);
  c.beginPath(); c.arc(xl + 34, cy, 6, 0, 7); c.fillStyle = `rgba(255,255,255,${pulse})`; c.fill();
  c.beginPath(); c.arc(xl + 34, cy, 6 + 6 * (1 - pulse), 0, 7); c.strokeStyle = `rgba(255,255,255,${.4 * pulse})`; c.lineWidth = 1.5; c.stroke();
  c.font = '800 17px Montserrat'; c.textBaseline = 'middle'; c.textAlign = 'left'; c.fillStyle = '#fff';
  c.letterSpacing = '2px'; c.fillText('HAZIRDA EFİRDƏ', xl + 52, cy + 1); c.letterSpacing = '0px';
  const lx = xl + 52 + 186;
  for (let b = 0; b < 4; b++) { const hh = 5 + 14 * Math.abs(Math.sin(t * (4 + b) + b * 2)); rr(c, lx + b * 7, cy + 9 - hh, 4, hh, 1.5); c.fillStyle = '#BFE1E4'; c.fill(); }
  c.fillStyle = 'rgba(255,255,255,.5)'; c.fillRect(lx + 40, cy - 16, 2, 32);
  // song title (marquee if too long)
  c.save(); c.beginPath(); c.rect(lx + 54, y0, xr - lx - 66, h); c.clip();
  c.font = '600 25px Montserrat'; c.fillStyle = '#fff';
  const tw = c.measureText(song).width, room = xr - lx - 72;
  let sx = lx + 58; if (tw > room) sx -= ((t * 50) % (tw + 80));
  c.fillText(song, sx, cy + 1); if (tw > room) c.fillText(song, sx + tw + 80, cy + 1);
  c.restore();
  c.restore();
}

// ---------- flag built from flying eight-point stars, then dissolving back into stars
let FLAGPX = null;
function flagColor(u, v) {
  if (!FLAGPX) { const cv = document.createElement('canvas'); cv.width = 1200; cv.height = 600; const x = cv.getContext('2d'); x.drawImage(FLAG, 0, 0); FLAGPX = x.getImageData(0, 0, 1200, 600).data; }
  const px = Math.min(1199, Math.floor(u * 1200)), py = Math.min(599, Math.floor(v * 600)), o = (py * 1200 + px) * 4;
  return `rgb(${FLAGPX[o]},${FLAGPX[o + 1]},${FLAGPX[o + 2]})`;
}
function flagWave(u, t, H) { const amp = H * (.03 + .06 * u); return Math.sin(u * 9 - t * 6.5) * amp + Math.sin(u * 15 - t * 9.1 + 1.3) * amp * .35; }
function starFlag(c, t, tc, D, old) {
  const W = 330, H = 165, cx = 960, cy = CY - 2, COLS = 30, ROWS = 15, cw = W / COLS;
  const flagIn = seg(tc, 1.05, 1.4), flagOut = seg(tc, D - 1.05, D - .9);
  const flagA = flagIn * (1 - flagOut);
  if (flagA > 0) { c.save(); c.globalAlpha = flagA; drawFlag(c, t, 1, cx, cy, 0); c.restore(); }
  for (let r = 0; r < ROWS; r++) for (let q = 0; q < COLS; q++) {
    const n = r * COLS + q, h1 = hash(n, 1), h2 = hash(n, 2), h3 = hash(n, 3);
    const u = (q + .5) / COLS, v = (r + .5) / ROWS;
    const tx = cx - W / 2 + u * W, ty = cy - H / 2 + v * H + flagWave(u, t, H);
    const col = flagColor(u, v);
    // phase 1: fly from the old letters into place
    const st = .08 + h1 * .45, p = seg(tc, st, st + .6);
    let x, y, a, sz, rot;
    if (tc < D - 1.05) {
      if (p <= 0) continue;
      const src = old[n % old.length], sx = src.x + (h2 - .5) * 30, sy = cy + (h3 - .5) * 40;
      const e = eIO(p), arc = Math.sin(Math.PI * e) * (h2 - .5) * 160;
      x = sx + (tx - sx) * e; y = sy + (ty - sy) * e + arc;
      a = Math.min(1, p * 4) * (1 - flagIn); sz = cw * (.35 + .5 * e); rot = (1 - e) * 4 * (h3 - .5);
      const fill = e < .6 ? (h1 > .5 ? '#fff' : T) : col;
      if (a <= .01) continue;
      c.globalAlpha = a; star8Path(c, x, y, sz * .62, .55); c.fillStyle = fill; c.fill();
      if (e < .9) { c.globalAlpha = a * .35; star8Path(c, x, y, sz * 1.1, .55); c.fillStyle = '#fff'; c.fill(); }
    } else {
      // phase 2: dissolve outward and upward as sparkles
      const d = seg(tc, D - 1.05 + h1 * .25, D - .25 + h1 * .25); if (d >= 1) continue;
      const ang = Math.atan2(ty - cy, tx - cx) + (h2 - .5) * .8, dist = (120 + 380 * h3) * eOut(d);
      x = tx + Math.cos(ang) * dist; y = ty + Math.sin(ang) * dist * .35 - 60 * eOut(d);
      a = (1 - d) * (flagOut > .3 ? 1 : flagOut / .3); sz = cw * (.85 - .5 * d); rot = d * 3 * (h3 - .5);
      c.globalAlpha = a; star8Path(c, x, y, sz * .62, .55); c.fillStyle = d < .4 ? col : (h1 > .5 ? '#fff' : '#8CC6CB'); c.fill();
    }
  }
  c.globalAlpha = 1;
}
