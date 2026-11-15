// Araz FM TV banner v7 — "Akustik Simlər" (client storyboard).
// Dark tar wood, macro gold strings, glassmorphism panels, 3D social tiles + QR, kamança bow, braided finale.
// window.renderV7(ctx, t, A, TL)  Canvas 1920x1080, transparent outside the band.
const GOLD = '#D9AE52', GOLD_L = '#FFE9B0', GOLD_D = '#6E4C14';
const FLAGC = ['#00B5E2', '#EF3340', '#509E2F'];
const clamp = (v, a = 0, b = 1) => Math.max(a, Math.min(b, v));
const eOut = p => 1 - Math.pow(1 - p, 3), eIn = p => p * p * p, eOut5 = p => 1 - Math.pow(1 - p, 5);
const eIO = p => p < .5 ? 4 * p * p * p : 1 - Math.pow(-2 * p + 2, 3) / 2;
const eBack = p => { const c = 1.5; return 1 + (c + 1) * Math.pow(p - 1, 3) + c * Math.pow(p - 1, 2); };
const seg = (t, a, b) => clamp((t - a) / (b - a));
const hash = (i, j = 0) => { const x = Math.sin(i * 127.1 + j * 311.7) * 43758.5453; return x - Math.floor(x); };
const rr = (c, x, y, w, h, r) => { c.beginPath(); c.roundRect(x, y, w, h, r); };

const BY = 844, BH = 236, CY = BY + BH / 2;
const STR = [-74, -46, -18, 18, 46, 74];          // string offsets from CY
const SW = [5.5, 3.2, 2.6, 2.6, 3.4, 6.0];         // thickness (outer ones = macro foreground)
const LOOP = 26.0;

let BUF = null, QR = null;
function star8Path(c, cx, cy, r, inner = .55) {
  c.beginPath();
  for (let i = 0; i < 16; i++) { const a = i * Math.PI / 8 - Math.PI / 2, rad = i % 2 ? r * inner : r;
    const x = cx + Math.cos(a) * rad, y = cy + Math.sin(a) * rad; i ? c.lineTo(x, y) : c.moveTo(x, y); }
  c.closePath();
}
function goldGrad(c, x0, y0, x1, y1) {
  const g = c.createLinearGradient(x0, y0, x1, y1);
  g.addColorStop(0, '#8A6420'); g.addColorStop(.35, '#F4D58A'); g.addColorStop(.5, '#FFF3CF'); g.addColorStop(.65, '#D9AE52'); g.addColorStop(1, '#7A5518');
  return g;
}

// ------------------------------------------------------------ timeline
// phases (in loop time u): F1 0–6.5 | F2 6.5–13 | F3 13–19 | F4 19–25.4 | back to F1 25.4–26
function phase(t, TL) {
  const intro = TL.noIntro ? 99 : t;
  const u = t < LOOP ? t : ((t - LOOP) % LOOP) + 0; // after the first pass the loop restarts at 0 (F1 already on)
  return { u, intro, first: t < LOOP && !TL.noIntro };
}

// ------------------------------------------------------------ strings
function stringY(i, x, u, t, braid) {
  const base = CY + STR[i];
  const beat = Math.pow(Math.max(0, Math.sin(t * Math.PI * 2 * 1.05)), 10);
  let vib = Math.sin(x / 140 - t * 9 + i) * (0.6 + 1.4 * beat) * Math.sin(Math.PI * clamp(x / 1920));
  // pluck on scene changes
  for (const ev of [6.5, 13.0, 19.0, 25.4]) { const d = u - ev; if (d > 0 && d < 1.6) vib += Math.sin(x / 60 - t * 40 + i * 2) * 6 * Math.pow(1 - d / 1.6, 2) * Math.sin(Math.PI * clamp(x / 1920)); }
  if (braid > 0) {
    const ph = i * Math.PI / 3, w = 34 * Math.sin(Math.PI * clamp((x - 0) / 1920) * 1.0);
    const target = CY + Math.sin(x / 95 - t * 3.2 + ph) * w;
    return base + (target - base) * braid + vib * (1 - braid);
  }
  return base + vib;
}
function drawStrings(c, u, t, braid, alpha, spinK) {
  c.save(); c.globalAlpha = alpha;
  if (spinK > 0) { c.translate(960, CY); c.rotate(spinK * Math.PI * 1.2); c.scale(1 - spinK * .93, 1 - spinK * .6); c.translate(-960, -CY); }
  for (let i = 0; i < 6; i++) {
    const w = SW[i] * (1 + braid * .4), pts = [];
    for (let x = -20; x <= 1940; x += 8) pts.push([x, stringY(i, x, u, t, braid)]);
    const path = () => { c.beginPath(); pts.forEach(([x, y], k) => k ? c.lineTo(x, y) : c.moveTo(x, y)); };
    // macro depth of field: outer strings soft
    const soft = (i === 0 || i === 5) ? 1.6 : 0;
    c.filter = soft ? `blur(${soft}px)` : 'none';
    path(); c.strokeStyle = GOLD_D; c.lineWidth = w; c.stroke();
    path(); c.strokeStyle = GOLD; c.lineWidth = w * .72; c.stroke();
    c.save(); c.translate(0, -w * .18); path(); c.strokeStyle = GOLD_L; c.lineWidth = Math.max(.8, w * .22); c.stroke(); c.restore();
    // wound strings: diagonal winding glints travelling slowly
    if (i >= 3) { path(); c.setLineDash([1.6, 2.6]); c.lineDashOffset = -t * 18; c.strokeStyle = 'rgba(255,240,200,.55)'; c.lineWidth = w * .6; c.stroke(); c.setLineDash([]); }
    c.filter = 'none';
  }
  // glint travelling along a string
  const gs = (t % 3.4) / 1.6;
  if (gs < 1 && braid < .5) {
    const si = Math.floor(hash(Math.floor(t / 3.4)) * 6), gx = -100 + 2120 * eIO(gs), gy = stringY(si, gx, u, t, braid);
    const g = c.createRadialGradient(gx, gy, 0, gx, gy, 40); g.addColorStop(0, 'rgba(255,248,220,.95)'); g.addColorStop(1, 'rgba(255,248,220,0)');
    c.globalCompositeOperation = 'lighter'; c.fillStyle = g; c.fillRect(gx - 40, gy - 40, 80, 80); c.globalCompositeOperation = 'source-over';
  }
  c.restore();
}
function drawShadows(c, u, t, braid, alpha) {
  c.save(); c.globalAlpha = alpha * .55; c.filter = 'blur(5px)';
  for (let i = 0; i < 6; i++) {
    c.beginPath(); for (let x = -20; x <= 1940; x += 16) { const y = stringY(i, x, u, t, braid) + 13; x < 0 ? c.moveTo(x, y) : c.lineTo(x, y); }
    c.strokeStyle = '#000'; c.lineWidth = SW[i] * 1.6; c.stroke();
  }
  c.filter = 'none'; c.restore();
}

// ------------------------------------------------------------ glass panel (glassmorphism)
function glass(c, x, y, w, h, r, opts = {}) {
  if (w < 4) return;
  const cv = c.canvas;
  if (!BUF) { BUF = document.createElement('canvas'); BUF.width = 1920; BUF.height = 1080; }
  const b = BUF.getContext('2d'); b.clearRect(0, 0, 1920, 1080); b.drawImage(cv, 0, 0);
  c.save(); rr(c, x, y, w, h, r); c.clip();
  c.filter = 'blur(16px) saturate(1.2)'; c.drawImage(BUF, 0, 0); c.filter = 'none';
  c.fillStyle = 'rgba(255,248,236,.13)'; c.fillRect(x, y, w, h);
  if (opts.tint) opts.tint(c, x, y, w, h);
  const hg = c.createLinearGradient(0, y, 0, y + h); hg.addColorStop(0, 'rgba(255,255,255,.22)'); hg.addColorStop(.45, 'rgba(255,255,255,.04)'); hg.addColorStop(1, 'rgba(255,255,255,0)');
  c.fillStyle = hg; c.fillRect(x, y, w, h);
  c.restore();
  c.save(); rr(c, x + .75, y + .75, w - 1.5, h - 1.5, r);
  const bg = c.createLinearGradient(x, y, x + w, y + h); bg.addColorStop(0, 'rgba(255,255,255,.65)'); bg.addColorStop(.5, 'rgba(255,230,170,.25)'); bg.addColorStop(1, 'rgba(255,255,255,.35)');
  c.strokeStyle = bg; c.lineWidth = 1.5; c.stroke(); c.restore();
}

// ------------------------------------------------------------ text helpers
function textWithMotion(c, txt, x, y, font, fill, p, dir = 1) { // p: 0 → 1 arriving with horizontal smear
  if (p <= 0) return;
  c.font = font; c.textBaseline = 'middle';
  const n = p < .98 ? 10 : 1, spread = 70 * (1 - p);
  for (let k = 0; k < n; k++) {
    const f = n === 1 ? 0 : k / (n - 1);
    c.globalAlpha = (n === 1 ? 1 : 1.8 / n * (1 - f * .7)) * clamp(p * 1.6);
    c.fillStyle = fill; c.fillText(txt, x + dir * (spread * f + 140 * (1 - eOut(p))), y);
  }
  c.globalAlpha = 1;
}

// ------------------------------------------------------------ social tiles + QR
function glyph(c, k, s) {
  c.save(); c.strokeStyle = '#fff'; c.fillStyle = '#fff'; c.lineWidth = s * .085; c.lineJoin = 'round';
  if (k === 0) { c.font = `800 ${s * 1.05}px Montserrat`; c.textAlign = 'center'; c.textBaseline = 'middle'; c.fillText('f', 0, s * .05); }
  if (k === 1) { rr(c, -s / 2, -s / 2, s, s, s * .28); c.stroke(); c.beginPath(); c.arc(0, 0, s * .22, 0, 7); c.stroke(); c.beginPath(); c.arc(s * .26, -s * .26, s * .06, 0, 7); c.fill(); }
  if (k === 2) { rr(c, -s * .66, -s * .44, s * 1.32, s * .88, s * .26); c.stroke(); c.beginPath(); c.moveTo(-s * .14, -s * .2); c.lineTo(s * .22, 0); c.lineTo(-s * .14, s * .2); c.closePath(); c.fill(); }
  if (k === 3) { // TikTok-style note
    c.lineWidth = s * .13; c.lineCap = 'round';
    c.beginPath(); c.moveTo(s * .02, -s * .46); c.lineTo(s * .02, s * .2); c.stroke();
    c.beginPath(); c.arc(-s * .16, s * .2, s * .18, 0, 7); c.stroke();
    c.beginPath(); c.moveTo(s * .02, -s * .46); c.quadraticCurveTo(s * .1, -s * .2, s * .36, -s * .2); c.stroke();
  }
  c.restore();
}
function tile(c, cx, cy, size, k, p, t) { // 3D glass tile with gold edges; p = rise progress
  if (p <= 0) return;
  const ang = (1 - eOut(p)) * 1.2, sx = Math.max(.04, Math.cos(ang)), h = size * (0.04 + .96 * eBack(p));
  c.save(); c.translate(cx, cy);
  c.shadowColor = 'rgba(0,0,0,.55)'; c.shadowBlur = 18; c.shadowOffsetY = 8;
  c.scale(sx, 1); rr(c, -size / 2, -h / 2, size, h, 20); c.fillStyle = 'rgba(30,18,10,.35)'; c.fill(); c.shadowColor = 'transparent';
  c.restore();
  glass(c, cx - size * sx / 2, cy - h / 2, size * sx, h, 20);
  c.save(); c.translate(cx, cy); c.scale(sx, 1);
  rr(c, -size / 2 + 1, -h / 2 + 1, size - 2, h - 2, 19); c.strokeStyle = goldGrad(c, -size / 2, -h / 2, size / 2, h / 2); c.lineWidth = 2.6; c.stroke();
  if (p > .5) { c.globalAlpha = seg(p, .5, .9); c.scale(1, h / size); glyph(c, k, size * .42); }
  c.restore();
  // specular sweep
  const sp = ((t * .6 + k * .17) % 1);
  if (p >= 1) { c.save(); rr(c, cx - size / 2, cy - size / 2, size, size, 20); c.clip();
    const gx = cx - size + sp * size * 3, g = c.createLinearGradient(gx - 20, 0, gx + 20, 0); g.addColorStop(0, 'rgba(255,255,255,0)'); g.addColorStop(.5, 'rgba(255,255,255,.22)'); g.addColorStop(1, 'rgba(255,255,255,0)');
    c.transform(1, 0, -.6, 1, 0, 0); c.fillStyle = g; c.fillRect(gx - 20 + cy * .6, cy - size / 2, 40, size); c.restore(); }
}
function qrCard(c, cx, cy, size, p, t) {
  if (p <= 0) return;
  const ang = (1 - eOut5(p)) * Math.PI * .9, sx = Math.cos(ang), back = sx < 0;
  const w = size * Math.abs(sx);
  c.save(); c.translate(cx, cy);
  c.shadowColor = 'rgba(0,0,0,.55)'; c.shadowBlur = 24; c.shadowOffsetY = 10;
  rr(c, -w / 2 - 8, -size / 2 - 8, w + 16, size + 16, 16); c.fillStyle = back ? '#2A170C' : '#FFFDF7'; c.fill(); c.shadowColor = 'transparent';
  c.strokeStyle = goldGrad(c, -size / 2, -size / 2, size / 2, size / 2); c.lineWidth = 3; c.stroke();
  if (!back && p > .35) {
    const n = QR.length, m = size / n;
    c.scale(Math.abs(sx), 1);
    for (let r = 0; r < n; r++) for (let q = 0; q < n; q++) {
      if (!QR[r][q]) continue;
      const appear = seg(p, .35 + hash(r, q) * .4, .5 + hash(r, q) * .4); if (appear <= 0) continue;
      c.fillStyle = '#16100A'; const s = m * (.6 + .4 * appear) + .4;
      c.fillRect(-size / 2 + q * m + (m - s) / 2, -size / 2 + r * m + (m - s) / 2, s, s);
    }
  }
  c.restore();
  // glint
  if (p >= 1) { const gp = (t % 4) / 1.2; if (gp < 1) { c.save(); rr(c, cx - size / 2 - 8, cy - size / 2 - 8, size + 16, size + 16, 16); c.clip();
    const gx = cx - size + gp * size * 2.4, g = c.createLinearGradient(gx - 30, 0, gx + 30, 0); g.addColorStop(0, 'rgba(255,255,255,0)'); g.addColorStop(.5, 'rgba(255,255,255,.35)'); g.addColorStop(1, 'rgba(255,255,255,0)');
    c.fillStyle = g; c.fillRect(gx - 30, cy - size, 60, size * 2); c.restore(); } }
}

// ------------------------------------------------------------ kamança bow
function bow(c, x, y, ang, len) {
  c.save(); c.translate(x, y); c.rotate(ang);
  // hair (cream band with glow)
  c.shadowColor = 'rgba(255,240,210,.9)'; c.shadowBlur = 22;
  c.fillStyle = '#F4EAD2'; c.fillRect(-len / 2, -3, len, 6); c.shadowBlur = 0;
  c.fillStyle = 'rgba(255,255,255,.9)'; c.fillRect(-len / 2, -1, len, 1.4);
  // stick (slight arc) in dark wood with a gold line
  c.beginPath(); c.moveTo(-len / 2, -4); c.quadraticCurveTo(0, -38, len / 2, -6);
  c.lineWidth = 9; c.strokeStyle = '#3A1F10'; c.stroke(); c.lineWidth = 2; c.strokeStyle = 'rgba(217,174,82,.8)'; c.stroke();
  // frog with gold ferrule
  rr(c, -len / 2 - 30, -22, 44, 26, 6); c.fillStyle = '#2A150A'; c.fill(); c.fillStyle = GOLD; c.fillRect(-len / 2 + 6, -20, 8, 22);
  c.restore();
}

// ------------------------------------------------------------ scene
window.renderV7 = function (c, t, A, TL) {
  if (!QR) QR = TL.qr;
  const intro = TL.noIntro ? 99 : t;
  const u = t < LOOP ? t : (t - LOOP) % LOOP + 0.0001;
  const looped = t >= LOOP || TL.noIntro;
  const reveal = looped ? 1 : eOut(seg(intro, 0, .9));

  // ----- camera pan (F1 → F2)
  const pan = eIO(seg(u, 6.5, 7.6)) * 1100 - (u >= 25.4 ? eIO(seg(u, 25.4, 26)) * 1100 : 0) + (u >= 25.4 ? 0 : 0);
  const camX = (u < 25.4 ? pan : 1100 - eIO(seg(u, 25.4, 26)) * 1100) + t * 6;

  // ----- band: wood, vignette, gold rim
  c.save();
  c.beginPath(); c.rect(0, BY + (1 - reveal) * BH, 1920, BH); c.clip();
  c.shadowColor = 'rgba(0,0,0,.5)'; c.shadowBlur = 30; c.fillStyle = '#140A05'; c.fillRect(0, BY, 1920, BH); c.shadowColor = 'transparent';
  const wx = -((camX) % 5200);
  // motion blur on the wood while panning
  const panV = Math.abs(seg(u, 6.5, 7.6) > 0 && seg(u, 6.5, 7.6) < 1 ? 1 : 0) + (u > 25.4 && u < 26 ? 1 : 0);
  c.filter = panV ? 'blur(3px)' : 'none';
  for (const k of [0, 1, 2]) { const x0 = wx + k * 2600; if (x0 > 1920 || x0 + 2600 < 0) continue;
    if (k % 2) { c.save(); c.translate(x0 + 2600, 0); c.scale(-1, 1); c.drawImage(A.wood, 0, BY - 2, 2600, BH + 4); c.restore(); }
    else c.drawImage(A.wood, x0, BY - 2, 2600, BH + 4); }
  c.filter = 'none';
  const vg = c.createLinearGradient(0, BY, 0, BY + BH); vg.addColorStop(0, 'rgba(0,0,0,.55)'); vg.addColorStop(.25, 'rgba(0,0,0,.05)'); vg.addColorStop(.75, 'rgba(0,0,0,.1)'); vg.addColorStop(1, 'rgba(0,0,0,.6)');
  c.fillStyle = vg; c.fillRect(0, BY, 1920, BH);
  const hv = c.createLinearGradient(0, 0, 1920, 0); hv.addColorStop(0, 'rgba(0,0,0,.45)'); hv.addColorStop(.18, 'rgba(0,0,0,0)'); hv.addColorStop(.82, 'rgba(0,0,0,0)'); hv.addColorStop(1, 'rgba(0,0,0,.45)');
  c.fillStyle = hv; c.fillRect(0, BY, 1920, BH);

  // ----- F3 colour spill on the wood
  const f3 = seg(u, 13.2, 14.2) * (1 - seg(u, 19.0, 19.8));
  if (f3 > 0) {
    c.globalCompositeOperation = 'lighter';
    [[FLAGC[0], BY + 30], [FLAGC[1], CY], [FLAGC[2], BY + BH - 30]].forEach(([col, yy], k) => {
      const g = c.createRadialGradient(960, yy, 10, 960, yy, 760); g.addColorStop(0, col); g.addColorStop(1, 'rgba(0,0,0,0)');
      c.globalAlpha = .32 * f3 * (.85 + .15 * Math.sin(t * 2 + k)); c.fillStyle = g; c.fillRect(0, BY, 1920, BH);
    });
    c.globalAlpha = 1; c.globalCompositeOperation = 'source-over';
  }

  // ----- strings (+ their shadows), braid in F4
  const braid = eIO(seg(u, 19.0, 20.2)) * (1 - eIO(seg(u, 21.0, 21.8)));
  const spin = eIn(seg(u, 20.0, 20.9)) * (1 - seg(u, 20.9, 21.0));
  const strA = u > 20.6 && u < 21.0 ? 1 - seg(u, 20.6, 20.9) : (u >= 21.0 ? seg(u, 21.0, 21.8) : 1);
  const drawIn = looped ? 1 : eOut(seg(intro, .3, 1.2));
  c.save(); c.beginPath(); c.rect(0, 0, 1920 * drawIn, 1080); c.clip();
  drawShadows(c, u, t, braid, strA * (1 - spin));
  drawStrings(c, u, t, braid, strA, spin);
  // coloured light ribbons braided with the strings (F4)
  if (braid > 0 && strA > 0) {
    c.save(); c.globalCompositeOperation = 'lighter'; c.globalAlpha = braid * strA;
    if (spin > 0) { c.translate(960, CY); c.rotate(spin * Math.PI * 1.2); c.scale(1 - spin * .93, 1 - spin * .6); c.translate(-960, -CY); }
    FLAGC.forEach((col, k) => {
      c.beginPath(); for (let x = -20; x <= 1940; x += 8) { const w = 40 * Math.sin(Math.PI * clamp(x / 1920)); const y = CY + Math.sin(x / 95 - t * 3.2 + k * 2.1 + .5) * w; x < 0 ? c.moveTo(x, y) : c.lineTo(x, y); }
      c.shadowColor = col; c.shadowBlur = 18; c.strokeStyle = col; c.lineWidth = 4; c.stroke();
    });
    c.restore();
  }
  c.restore();
  c.restore(); // band clip

  // gold rim on the top edge
  c.save(); c.globalAlpha = reveal;
  const rim = goldGrad(c, 0, 0, 1920, 0); c.fillStyle = rim; c.fillRect(0, BY + (1 - reveal) * BH, 1920, 2.5);
  c.restore();

  // =========================== F1 — glass panel with the first line
  const f1In = looped ? (u < 6.5 ? (u > 25 ? 0 : 1) : 0) : seg(intro, 1.0, 1.7);
  const f1Back = seg(u, 25.5, 26.0);
  const f1Vis = u < 7.6 || u >= 25.5;
  if (f1Vis && (f1In > 0 || f1Back > 0 || (looped && u < 7.6))) {
    const pIn = u >= 25.5 ? eOut5(f1Back) : (looped ? 1 : eOut5(f1In));
    const px = 300 + (1 - pIn) * 900 - (u < 25 ? pan : 0), pw = 1320, ph = 112, py = CY - ph / 2;
    c.save(); c.globalAlpha = clamp(pIn * 1.5);
    glass(c, px, py, pw, ph, 22);
    c.restore();
    const tp = u >= 25.5 ? seg(u, 25.6, 26.0) : (looped ? 1 : seg(intro, 1.25, 1.9));
    c.save(); c.shadowColor = 'rgba(0,0,0,.6)'; c.shadowBlur = 12; c.shadowOffsetY = 2;
    const tx = px + 48;
    textWithMotion(c, 'Bizimlə eyni dalğada qala bilmirsinizsə', tx, CY + 2, '600 44px Montserrat', '#FFFFFF', tp);
    c.font = '600 44px Montserrat'; const w1 = c.measureText('Bizimlə eyni dalğada qala bilmirsinizsə').width;
    c.font = '300 44px Montserrat';
    textWithMotion(c, '—', tx + w1 + 20, CY + 2, '600 44px Montserrat', 'rgba(255,233,176,.8)', tp);
    c.shadowColor = 'rgba(0,0,0,.35)';
    textWithMotion(c, '103.3 FM', tx + w1 + 74, CY + 2, '800 46px Montserrat', goldGrad(c, 0, CY - 24, 0, CY + 24), seg(tp, .25, 1));
    c.restore();
  }

  // =========================== F2 — shadows rise into 3D tiles, QR opens, text
  const inF2 = u >= 6.5 && u < 14.2;
  if (inF2) {
    const off = 1100 - pan; // elements arrive with the camera pan
    const wipeX = u >= 13 ? -200 + 2400 * eIO(seg(u, 13.0, 14.0)) : -9999; // bow wipe (F3) removes F2 behind it
    c.save(); if (wipeX > -9999) { c.beginPath(); c.rect(wipeX, 0, 2400, 1080); c.clip(); }
    // text panel
    const tpIn = seg(u, 7.5, 8.2);
    if (tpIn > 0) {
      c.save(); c.globalAlpha = clamp(tpIn * 2); glass(c, 150 + off, CY - 78, 560, 156, 22); c.restore();
      c.save(); c.shadowColor = 'rgba(0,0,0,.6)'; c.shadowBlur = 10;
      textWithMotion(c, 'Eyni səhifədə qalın!', 186 + off, CY - 22, '700 44px Montserrat', '#fff', seg(u, 7.8, 8.5));
      textWithMotion(c, 'arazfm.az', 188 + off, CY + 36, '700 34px Montserrat', goldGrad(c, 0, CY + 18, 0, CY + 54), seg(u, 8.1, 8.8));
      c.restore();
    }
    // QR card (centre)
    qrCard(c, 960 + off, CY, 172, seg(u, 7.8, 8.9), t);
    c.save(); c.font = '700 15px Montserrat'; c.letterSpacing = '3px'; c.fillStyle = `rgba(255,233,176,${seg(u, 8.8, 9.2)})`; c.textAlign = 'center'; c.textBaseline = 'middle';
    c.restore();
    // tiles rise out of the string shadows
    [0, 1, 2, 3].forEach(k => {
      const cx = 1210 + k * 140 + off, rp = seg(u, 7.7 + k * .12, 8.5 + k * .12);
      if (rp > 0 && rp < .25) { // the shadow line lifting
        c.save(); c.globalAlpha = .6; c.filter = 'blur(3px)'; c.fillStyle = '#000'; c.fillRect(cx - 46, CY + STR[3 + (k % 3)] + 13 - rp * 120, 92, 4); c.restore();
      }
      tile(c, cx, CY, 100, k, seg(rp, .15, 1), t);
    });
    c.restore();
  }

  // =========================== F3 — kamança bow cuts through; flag-lit glass; text writes on
  const inF3 = u >= 13.0 && u < 20.0;
  if (inF3) {
    const bx = -200 + 2400 * eIO(seg(u, 13.0, 14.0));
    const out = seg(u, 19.0, 19.6);
    c.save(); c.beginPath(); c.rect(0, 0, Math.max(0, bx), 1080); c.clip(); c.globalAlpha = 1 - out;
    const px = 330, pw = 1260, ph = 120, py = CY - ph / 2;
    glass(c, px, py, pw, ph, 24, { tint: (c, x, y, w, h) => {
      c.globalCompositeOperation = 'lighter';
      FLAGC.forEach((col, k) => { const g = c.createLinearGradient(0, y + k * h / 3, 0, y + (k + 1) * h / 3); g.addColorStop(0, 'rgba(0,0,0,0)'); g.addColorStop(.5, col); g.addColorStop(1, 'rgba(0,0,0,0)');
        c.globalAlpha = .62 * (1 - out) * (.85 + .15 * Math.sin(t * 2.2 + k)); c.fillStyle = g; c.fillRect(x, y + k * h / 3 - 22, w, h / 3 + 44); });
      c.globalAlpha = 1; c.globalCompositeOperation = 'source-over'; } });
    // text: written on behind a soft light edge
    const wp = eIO(seg(u, 13.6, 15.0));
    c.font = '600 52px Montserrat'; const T3 = 'Milli musiqinin tək ünvanı', tw = c.measureText(T3).width, tx = 960 - tw / 2;
    c.save(); c.beginPath(); c.rect(tx - 10, 0, (tw + 20) * wp, 1080); c.clip();
    c.shadowColor = 'rgba(0,0,0,.55)'; c.shadowBlur = 12; c.fillStyle = '#fff'; c.textBaseline = 'middle'; c.fillText(T3, tx, CY + 2); c.restore();
    if (wp > 0 && wp < 1) { const ex = tx + (tw + 20) * wp, g = c.createRadialGradient(ex, CY, 0, ex, CY, 46); g.addColorStop(0, 'rgba(255,248,220,.9)'); g.addColorStop(1, 'rgba(255,248,220,0)');
      c.globalCompositeOperation = 'lighter'; c.fillStyle = g; c.fillRect(ex - 46, CY - 46, 92, 92); c.globalCompositeOperation = 'source-over'; }
    // small crescent-and-star accents at both ends of the panel
    c.restore();
    // the bow itself + sparkle trail
    if (u < 14.2) {
      for (let k = 0; k < 18; k++) { const h1 = hash(k, Math.floor(u * 10)); c.globalAlpha = .7 * (1 - k / 18); c.fillStyle = k % 3 === 0 ? '#fff' : GOLD_L;
        c.beginPath(); c.arc(bx - k * 16 - h1 * 10, BY + 20 + h1 * (BH - 40), 1.6 + h1 * 1.6, 0, 7); c.fill(); }
      c.globalAlpha = 1;
      bow(c, bx, CY, -1.25, 360);
    }
  }

  // =========================== F4 — braid spins into the logo; pulsing like a sound wave
  const inF4 = u >= 20.4 && u < 26.0;
  if (inF4) {
    const lp = eBack(seg(u, 20.7, 21.4)), la = seg(u, 20.6, 21.0) * (1 - seg(u, 25.4, 25.8));
    const beat = Math.pow(Math.max(0, Math.sin(t * Math.PI * 2 * 1.05)), 8);
    // flash at the moment the braid becomes the logo
    const fl = Math.exp(-Math.pow((u - 20.85) / .12, 2));
    if (fl > .01) { const g = c.createRadialGradient(960, CY, 0, 960, CY, 260); g.addColorStop(0, `rgba(255,244,214,${.85 * fl})`); g.addColorStop(1, 'rgba(255,244,214,0)'); c.globalCompositeOperation = 'lighter'; c.fillStyle = g; c.fillRect(700, BY, 520, BH); c.globalCompositeOperation = 'source-over'; }
    // soft dark pool behind logo + tagline so the strings never cut through them
    { const g = c.createRadialGradient(960, (CY + 10) / .55, 20, 960, (CY + 10) / .55, 330); g.addColorStop(0, `rgba(12,6,3,${.85 * la})`); g.addColorStop(.55, `rgba(12,6,3,${.6 * la})`); g.addColorStop(1, 'rgba(12,6,3,0)');
      c.save(); c.scale(1, .55); c.fillStyle = g; c.fillRect(560, (CY + 10) / .55 - 330, 800, 660); c.restore(); }
    // sound-wave arcs pulsing either side of the logo
    for (let k = 0; k < 3; k++) {
      const ph = ((t * 1.05 + k / 3) % 1), r = 120 + ph * 160;
      c.save(); c.globalAlpha = la * (1 - ph) * .8; c.strokeStyle = goldGrad(c, 960 - r, 0, 960 + r, 0); c.lineWidth = 2.5;
      c.beginPath(); c.arc(960, CY - 18, r, -.45, .45); c.stroke(); c.beginPath(); c.arc(960, CY - 18, r, Math.PI - .45, Math.PI + .45); c.stroke(); c.restore();
    }
    const img = A.white, lh = 96, lw = img.width * lh / img.height, s = (.6 + .4 * lp) * (1 + .035 * beat);
    c.save(); c.globalAlpha = la; c.translate(960, CY - 22); c.scale(s, s);
    c.shadowColor = 'rgba(255,220,150,.55)'; c.shadowBlur = 18 + 14 * beat; c.drawImage(img, -lw / 2, -lh / 2, lw, lh); c.restore();
    c.save(); c.globalAlpha = la * seg(u, 21.1, 21.7); c.font = '700 36px Montserrat'; c.letterSpacing = '4px'; c.textAlign = 'center'; c.textBaseline = 'middle';
    c.shadowColor = 'rgba(0,0,0,.6)'; c.shadowBlur = 10; c.fillStyle = goldGrad(c, 0, CY + 40, 0, CY + 76); c.fillText('Qovuşduran radio!', 960, CY + 62 + (1 - seg(u, 21.1, 21.7)) * 14); c.restore();
  }
};
