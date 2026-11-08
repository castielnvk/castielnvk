// «Sözümün Canı — Məlal» : dusk, rain, still water, silence and fullness
const DUR = 59.4;
const cv = document.getElementById('c'); cv.width = W; cv.height = H;
const X = cv.getContext('2d');
const mk = () => { const c = document.createElement('canvas'); c.width = W; c.height = H; return c; };
const layer = mk(), LC = layer.getContext('2d');
const above = mk(), AC = above.getContext('2d');
const LOGO = new Image(); window.LOGO_READY = new Promise(r => { LOGO.onload = r; LOGO.onerror = r; }); LOGO.src = LOGO_SRC;
const PF = 'PF', LO = 'LO', IN = 'Inter';

// ---------- atmosphere ----------
function sky(c, k = {}) {
  // dusk gradient; k.warm 0..1 shifts toward amber, k.cold toward clinical
  const w = k.warm || 0, cl = k.cold || 0, d = k.deep || 0;
  const mix = (a, b, t) => a.map((v, i) => Math.round(v + (b[i] - v) * t));
  let top = [10, 14, 22], mid = [18, 26, 38], bot = [26, 33, 46];
  top = mix(top, [22, 14, 12], w); mid = mix(mid, [40, 26, 22], w); bot = mix(bot, [52, 34, 26], w);
  top = mix(top, [8, 14, 18], cl); mid = mix(mid, [14, 24, 30], cl); bot = mix(bot, [18, 32, 38], cl);
  top = mix(top, [4, 14, 20], d); mid = mix(mid, [6, 22, 30], d); bot = mix(bot, [3, 10, 16], d);
  const g = c.createLinearGradient(0, 0, 0, H);
  g.addColorStop(0, `rgb(${top})`); g.addColorStop(0.55, `rgb(${mid})`); g.addColorStop(1, `rgb(${bot})`);
  c.fillStyle = g; c.fillRect(0, 0, W, H);
  const gx = k.gx ?? CX, gy = k.gy ?? 900, gr = k.gr ?? 900;
  const glowCol = w > 0.3 ? `rgba(231,169,100,${0.10 + 0.08 * w})` : cl > 0.3 ? 'rgba(127,211,220,0.08)' : 'rgba(185,197,209,0.09)';
  const r = c.createRadialGradient(gx, gy, 0, gx, gy, gr); r.addColorStop(0, glowCol); r.addColorStop(1, 'rgba(0,0,0,0)');
  c.fillStyle = r; c.fillRect(0, 0, W, H);
}
const RAIN = (() => { const r = rng(5), a = []; for (let i = 0; i < 150; i++) a.push({ x: r() * (W + 300) - 150, y: r() * H, z: 0.3 + r() * 0.7, s: 0.7 + r() * 0.6 }); return a; })();
function rain(c, t, amt = 1, waterY = null) {
  if (amt <= 0) return;
  c.save(); c.lineCap = 'round';
  for (const d of RAIN) {
    const sp = 1500 * d.z * d.s, len = 30 + 70 * d.z;
    const y = ((d.y + t * sp) % (H + 200)) - 100, x = d.x - (y * 0.12);
    if (waterY && y > waterY) continue;
    c.strokeStyle = `rgba(200,214,228,${amt * (0.05 + 0.16 * d.z)})`; c.lineWidth = 0.6 + d.z * 1.3;
    c.beginPath(); c.moveTo(x, y); c.lineTo(x - len * 0.12, y + len); c.stroke();
  }
  c.restore();
}
// rain rings on a water surface
function rainRings(c, t, waterY, amt = 1, depth = 260) {
  if (amt <= 0) return; const r = rng(17);
  c.save();
  for (let i = 0; i < 26; i++) {
    const per = 0.9 + r() * 1.4, ph = r() * per, x = 60 + r() * (W - 120), zy = r();
    const lt = ((t + ph) % per) / per; const y = waterY + 14 + zy * depth;
    const rx = 6 + lt * (30 + 60 * zy), ry = rx * (0.16 + 0.12 * zy);
    c.strokeStyle = `rgba(200,214,228,${amt * (1 - lt) * (0.12 + 0.2 * zy)})`; c.lineWidth = 1;
    c.beginPath(); c.ellipse(x, y, rx, ry, 0, 0, 7); c.stroke();
  }
  c.restore();
}
function ripple(c, x, y, t, t0, o = {}) {
  const d = t - t0; if (d < 0 || d > (o.life || 2.2)) return;
  const n = o.n || 3, life = o.life || 2.2;
  c.save();
  for (let j = 0; j < n; j++) {
    const dd = d - j * 0.22; if (dd < 0) continue;
    const rx = (o.r0 || 6) + dd * (o.sp || 150), a = (o.a ?? 0.6) * Math.max(0, 1 - dd / life);
    c.strokeStyle = o.col ? o.col(a) : `rgba(220,230,240,${a})`; c.lineWidth = o.lw || 1.4;
    c.beginPath(); c.ellipse(x, y, rx, rx * (o.flat ?? 0.18), 0, 0, 7); c.stroke();
  }
  c.restore();
}
// reflection of everything in `src` above waterY, rippled, into c below waterY
function reflect(c, src, waterY, t, o = {}) {
  const hh = Math.min(o.h || 700, H - waterY), strip = 3, amp = o.amp ?? 5, alpha = o.a ?? 0.38;
  c.save(); c.globalAlpha = alpha;
  for (let y = 0; y < hh; y += strip) {
    const sy = waterY - y - strip; if (sy < 0) break;
    const k = y / hh, off = Math.sin(y * 0.045 - t * 2.2) * amp * (0.4 + k * 1.6) + Math.sin(y * 0.11 + t * 1.3) * amp * 0.5;
    c.globalAlpha = alpha * (1 - k) * (1 - k * 0.3);
    c.drawImage(src, 0, sy, W, strip, off, waterY + y, W, strip);
  }
  c.restore();
}
function waterLine(c, y, w, a = 1, col = '233,238,243') {
  if (w <= 1) return;
  const g = c.createLinearGradient(CX - w / 2, 0, CX + w / 2, 0);
  g.addColorStop(0, `rgba(${col},0)`); g.addColorStop(0.5, `rgba(${col},${0.75 * a})`); g.addColorStop(1, `rgba(${col},0)`);
  c.fillStyle = g; c.fillRect(CX - w / 2, y - 0.75, w, 1.5);
}
const MOTES = (() => { const r = rng(91), a = []; for (let i = 0; i < 90; i++) a.push({ x: r() * W, y: r() * H, z: 0.3 + r() * 0.7, ph: r() * 6.3 }); return a; })();
function motes(c, t, amt = 0.5, col = '210,222,235', vy = -10) {
  c.save(); c.globalCompositeOperation = 'lighter';
  for (const m of MOTES) {
    const x = m.x + Math.sin(t * 0.3 + m.ph) * 25 * m.z, y = ((m.y + t * vy * m.z) % H + H) % H;
    const a = amt * (0.1 + 0.3 * (0.5 + 0.5 * Math.sin(t * 1.3 + m.ph))) * m.z;
    c.fillStyle = `rgba(${col},${a})`; c.beginPath(); c.arc(x, y, 0.8 + m.z * 2.2, 0, 7); c.fill();
  }
  c.restore();
}
function glow(c, x, y, r, col, a) { if (a <= 0) return; const g = c.createRadialGradient(x, y, 0, x, y, r); g.addColorStop(0, `rgba(${col},${a})`); g.addColorStop(0.4, `rgba(${col},${a * 0.35})`); g.addColorStop(1, `rgba(${col},0)`); c.fillStyle = g; c.fillRect(x - r, y - r, 2 * r, 2 * r); }
function silverGrad(c, y0, y1) { const g = c.createLinearGradient(0, y0, 0, y1); g.addColorStop(0, '#ffffff'); g.addColorStop(0.5, MOON); g.addColorStop(1, '#93a3b4'); return g; }
function amberGrad(c, y0, y1) { const g = c.createLinearGradient(0, y0, 0, y1); g.addColorStop(0, '#fff0d6'); g.addColorStop(0.5, AMBER_L); g.addColorStop(1, '#c98a4a'); return g; }
// sampled points of a word, for particle assembly
function wordPoints(str, o, cx, by, step) {
  const c2 = mk(), c = c2.getContext('2d'); font(c, o); c.textAlign = 'center'; c.fillStyle = '#fff'; c.fillText(str, cx + (o.ls || 0) / 2, by);
  const d = c.getImageData(0, 0, W, H).data, pts = [], r = rng(3);
  for (let y = 0; y < H; y += step) for (let x = 0; x < W; x += step) if (d[(y * W + x) * 4 + 3] > 140) pts.push({ x: x + (r() - 0.5) * step, y: y + (r() - 0.5) * step, sx: r() * W, sy: -50 - r() * 900, d: r(), z: r() });
  return pts;
}
// heart / circle shapes (param u 0..1)
function heartPt(u, s) { const t = Math.PI + u * Math.PI * 2; return [16 * Math.pow(Math.sin(t), 3) * s, -(13 * Math.cos(t) - 5 * Math.cos(2 * t) - 2 * Math.cos(3 * t) - Math.cos(4 * t)) * s]; }
function circlePt(u, r) { const a = Math.PI / 2 + u * Math.PI * 2; return [Math.cos(a) * r, -Math.sin(a) * r * -1]; }
function morphPath(c, cx, cy, k, r, s) { c.beginPath(); for (let i = 0; i <= 160; i++) { const u = i / 160; const a = circlePt(u, r), b = heartPt(u, s); const x = cx + lerp(a[0], b[0], k), y = cy + lerp(a[1] + r * 0.05, b[1], k); i ? c.lineTo(x, y) : c.moveTo(x, y); } c.closePath(); }
function flame(c, x, y, t, s = 1, a = 1) {
  if (a <= 0) return;
  glow(c, x, y - 40 * s, 420 * s, '231,169,100', 0.22 * a);
  glow(c, x, y - 30 * s, 140 * s, '255,214,160', 0.35 * a);
  const fl = Math.sin(t * 9.1) * 0.5 + Math.sin(t * 13.7 + 1) * 0.3 + Math.sin(t * 4.3) * 0.4;
  for (const [sc, col] of [[1, 'rgba(231,150,80,0.55)'], [0.72, 'rgba(250,200,130,0.85)'], [0.42, 'rgba(255,246,225,0.95)']]) {
    const h = 120 * s * sc * (1 + fl * 0.06), w = 34 * s * sc, sway = fl * 6 * s * sc;
    c.save(); c.globalAlpha = a; c.fillStyle = col; c.beginPath(); c.moveTo(x, y);
    c.bezierCurveTo(x - w * 1.2, y - h * 0.25, x - w * 0.5 + sway, y - h * 0.7, x + sway * 1.6, y - h);
    c.bezierCurveTo(x + w * 0.5 + sway, y - h * 0.7, x + w * 1.2, y - h * 0.25, x, y); c.fill(); c.restore();
  }
}
function capsule(c, x, y, ang, len, r) {
  c.save(); c.translate(x, y); c.rotate(ang);
  c.fillStyle = CLIN; c.beginPath(); c.arc(-len / 2 + r, 0, r, Math.PI / 2, Math.PI * 1.5); c.lineTo(0, -r); c.lineTo(0, r); c.closePath(); c.fill();
  c.fillStyle = CYAN; c.beginPath(); c.arc(len / 2 - r, 0, r, -Math.PI / 2, Math.PI / 2); c.lineTo(0, r); c.lineTo(0, -r); c.closePath(); c.fill();
  c.fillStyle = 'rgba(255,255,255,0.5)'; c.fillRect(-len / 2 + r, -r * 0.6, len - 2 * r, r * 0.25);
  c.restore();
}
function outlineText(c, s, x, y, o) { c.save(); font(c, o); c.textAlign = 'center'; c.globalAlpha *= (o.a ?? 1); c.strokeStyle = o.col || MOON; c.lineWidth = o.lw || 1.6; c.strokeText(s, x + (o.ls || 0) / 2, y); c.restore(); }

// ---------- captions ----------
const CAP = { 1: 1, 2: 1, 3: 1, 4: 1, 5: 1, 6: 1, 7: 1, 8: 1, 9: 1, 10: 1 };
function captions(c, t) {
  for (const li in CAP) {
    const Ln = LINES[li], next = LINES[+li + 1];
    const endT = Math.min(Ln.e + 0.7, next ? next.s - 0.05 : 99);
    if (t < Ln.s - 0.15 || t > endT) continue;
    const fade = sm(p(t, Ln.s - 0.15, Ln.s + 0.1)) * (1 - sm(p(t, endT - 0.35, endT)));
    const o = { ff: IN, wt: 400, sz: 37 };
    c.save(); font(c, o); const sp = c.measureText(' ').width;
    const lines = [[]]; let lw = 0; const maxW = 820;
    for (const [w, wt] of Ln.w) { const ww = c.measureText(w).width; if (lw + ww > maxW && lines[lines.length - 1].length) { lines.push([]); lw = 0; } lines[lines.length - 1].push([w, wt, ww]); lw += ww + sp; }
    const lh = 54, bottom = 1555, top = bottom - (lines.length - 1) * lh;
    const g = c.createLinearGradient(0, top - 130, 0, H); g.addColorStop(0, 'rgba(4,7,12,0)'); g.addColorStop(0.3, `rgba(4,7,12,${0.45 * fade})`); g.addColorStop(1, `rgba(4,7,12,${0.5 * fade})`);
    c.fillStyle = g; c.fillRect(0, top - 130, W, H - top + 130);
    lines.forEach((L, j) => {
      const total = L.reduce((a, q) => a + q[2], 0) + sp * (L.length - 1); let x = CX - total / 2;
      for (const [w, wt, ww] of L) {
        const k = sm(p(t, wt - 0.08, wt + 0.2)); const cur = t >= wt - 0.05 && t < wt + 0.45;
        c.globalAlpha = fade * (0.12 + 0.86 * k); c.fillStyle = cur ? AMBER_L : CREAM; c.textAlign = 'left';
        c.shadowColor = 'rgba(0,0,0,0.6)'; c.shadowBlur = 10;
        c.fillText(w, x, top + j * lh + (1 - k) * 6); x += ww + sp;
      }
    });
    c.restore();
  }
}
// ---------- branding: exact logo asset + segment title ----------
function branding(c, t) {
  if (!LOGO.naturalWidth) return;
  const ar = LOGO.naturalHeight / LOGO.naturalWidth;
  // top: logo + title, appear quietly after the word reveal; end card: larger, centred
  const inA = sm(p(t, 2.2, 3.2)), endK = eio(p(t, 55.4, 56.6));
  const topA = inA * (1 - sm(p(t, 54.9, 55.5)));
  if (topA > 0) {
    const lw = 200, lh = lw * ar; c.save(); c.globalAlpha = 0.86 * topA; c.drawImage(LOGO, CX - lw / 2, 150, lw, lh); c.restore();
    T(c, 'SÖZÜMÜN CANI', CX, 150 + lh + 46, { ff: IN, wt: 500, sz: 22, ls: 8, col: MIST, a: 0.75 * topA });
  }
  if (endK > 0) {
    const lw = 400, lh = lw * ar, y0 = 330;
    c.save(); c.globalAlpha = endK; c.drawImage(LOGO, CX - lw / 2, y0 + (1 - endK) * 20, lw, lh); c.restore();
    letters(c, 'SÖZÜMÜN CANI', CX, y0 + lh + 92, { ff: PF, wt: 400, sz: 52, ls: 14, col: MOON }, (i) => { const ti = 56.15 + i * 0.07; const r = sm(p(t, ti, ti + 0.6)); return { a: r, dy: (1 - r) * 12, blur: (1 - r) * 6 }; });
  }
}

// ================= SCENES =================
const WORD = 'MƏLAL';
const WO = { ff: PF, wt: 600, sz: 250, ls: 22 };
let PTS = null;
// 1 — the word condenses out of rain onto still water
function s1(c, t) {
  sky(c, { gy: 1000 });
  const wy = 960, water = 1000;
  if (!PTS) PTS = wordPoints(WORD, WO, CX, wy, 5);
  const mv = eio(p(t, 2.0, 3.0)); // lift for the origin passage
  AC.clearRect(0, 0, W, H);
  // assembled word (particles -> crisp)
  const crisp = sm(p(t, WT(0, 3) - 0.1, WT(0, 3) + 0.5));
  AC.save(); AC.translate(CX, lerp(wy, 560, mv)); AC.scale(lerp(1, 0.62, mv), lerp(1, 0.62, mv)); AC.translate(-CX, -wy);
  if (crisp < 1) {
    AC.save(); AC.globalCompositeOperation = 'lighter';
    for (const q of PTS) {
      const st = q.d * 0.9, k = eio(p(t, st, st + 0.65));
      if (k <= 0) { // still a raindrop streak
        const y = q.sy + (t + 0.2) * 1600 * (0.6 + q.z * 0.6); if (y > -10 && y < H) { AC.strokeStyle = 'rgba(210,222,235,0.25)'; AC.lineWidth = 1; AC.beginPath(); AC.moveTo(q.sx, y); AC.lineTo(q.sx - 4, y + 40); AC.stroke(); }
        continue;
      }
      const sy = Math.min(q.sy + st * 1600, q.y - 10);
      const x = lerp(q.sx, q.x, k), y = lerp(sy, q.y, k);
      AC.fillStyle = `rgba(225,233,242,${(0.35 + 0.5 * k) * (1 - crisp)})`; AC.fillRect(x - 1.3, y - 1.3, 2.6, 2.6);
    }
    AC.restore();
  }
  T(AC, WORD, CX, wy, Object.assign({}, WO, { col: silverGrad(AC, wy - 190, wy), a: crisp, glow: 18, glowCol: 'rgba(200,220,240,0.35)' }));
  AC.restore();
  // "Bu günün sözü"
  c.__t = t;
  c.drawImage(above, 0, 0);
  wordsLine(c, [{ s: 'Bu', t: WT(0, 0) }, { s: 'günün', t: WT(0, 1) }, { s: 'sözü', t: WT(0, 2) }], CX, 690, { ff: LO, it: true, sz: 54, col: MIST, a: 1 - sm(p(t, 1.9, 2.4)) });
  const wa = 1 - mv;
  waterLine(c, water, 860 * eo(p(t, 0, 1.2)), wa);
  if (wa > 0) { reflect(c, above, water, t, { a: 0.36 * wa, h: 420 }); rainRings(c, t, water, 0.8 * wa, 300); }
  rain(c, t, 1 - 0.6 * mv, wa > 0.5 ? water : null);
  ripple(c, CX, water + 6, t, WT(0, 3), { n: 3, sp: 260, a: 0.5 * wa, life: 1.8 });
}
// 2 — origin, two qualities, three meanings
function s2(c, t) {
  c.__t = t; const L = LINES[1].w;
  const wy = 560;
  if (t < 3.05) { s1(c, t); c.__t = t; } else { sky(c, { gy: 1000 }); rain(c, t, 0.4); }
  motes(c, t, 0.35 * p(t, 2.6, 3.4));
  if (t >= 3.05) T(c, WORD, CX, wy, Object.assign({}, WO, { sz: 155, ls: 14, col: silverGrad(c, wy - 120, wy), glow: 14, glowCol: 'rgba(200,220,240,0.3)' }));
  // origin: words travel down a thread like a drop of water
  const oa = 1 - sm(p(t, 5.2, 5.8));
  T(c, 'ərəb dilindən', CX, 680, { ff: LO, it: true, sz: 44, col: MIST, a: said(t, L[1][1]) * oa });
  const th = eio(p(t, L[2][1] - 0.15, L[3][1] + 0.4));
  if (th > 0 && oa > 0) {
    c.save(); c.globalAlpha = oa; c.strokeStyle = 'rgba(185,197,209,0.5)'; c.lineWidth = 1.2; c.beginPath(); c.moveTo(CX, 702); c.lineTo(CX, 702 + 66 * th); c.stroke(); c.restore();
    glow(c, CX, 702 + 66 * th, 14, '233,238,243', 0.9 * oa * (1 - p(t, L[3][1] + 0.3, L[3][1] + 0.7)));
  }
  T(c, 'dilimizə', CX, 812, { ff: LO, it: true, sz: 44, col: MOON, a: said(t, L[2][1]) * oa });
  // two qualities flanking
  T(c, 'şairanə', 300, 900, { ff: LO, it: true, sz: 50, col: LAV, a: said(t, L[5][1]) * oa });
  T(c, 'kübar', 780, 900, { ff: LO, it: true, sz: 50, col: LAV, a: said(t, L[7][1]) * oa });
  if (oa > 0) { c.save(); c.globalAlpha = said(t, L[6][1]) * oa * 0.7; c.fillStyle = MIST; c.beginPath(); c.arc(CX, 886, 3.5, 0, 7); c.fill(); c.restore(); }
  // meanings
  const mA = 1;
  const r1 = 790, r2 = 1010, r3 = 1230;
  // kədər: a single drop falls to its own little water line
  const k1 = said(t, L[10][1], 0.5);
  if (k1 > 0) {
    T(c, 'kədər', CX, r1, { ff: PF, it: true, sz: 104, col: MOON, a: k1 * mA, blur: (1 - k1) * 10 });
    const dropT = L[10][1] + 0.15, df = p(t, dropT, dropT + 0.45);
    if (df < 1) glow(c, CX + 150, lerp(r1 - 120, r1 + 36, ei(df)), 9, '233,238,243', 0.9 * p(t, dropT - 0.1, dropT));
    waterLine(c, r1 + 38, 380 * k1, 0.6);
    ripple(c, CX + 150, r1 + 38, t, dropT + 0.45, { n: 3, sp: 110, a: 0.6, life: 2.2 });
  }
  // sıxıntı: walls close in, the word is squeezed
  const k2 = said(t, L[11][1], 0.5);
  if (k2 > 0) {
    const sq = eio(p(t, L[11][1], L[11][1] + 1.2));
    c.save(); c.translate(CX, r2); c.scale(1 - 0.18 * sq, 1); T(c, 'sıxıntı', 0, 0, { ff: PF, it: true, sz: 104, col: MOON, a: k2, blur: (1 - k2) * 10 }); c.restore();
    const gap = lerp(330, 210, sq);
    c.save(); c.globalAlpha = k2 * 0.8; c.fillStyle = 'rgba(185,197,209,0.55)'; c.fillRect(CX - gap - 3, r2 - 95, 2.5, 125); c.fillRect(CX + gap, r2 - 95, 2.5, 125); c.restore();
  }
  // qəlb yorğunluğu: a pulse line that tires and flattens
  const k3 = said(t, L[12][1], 0.5);
  if (k3 > 0) {
    const pY = r3 - 40, tired = p(t, L[12][1], L[14][1] + 0.6);
    c.save(); c.strokeStyle = `rgba(231,169,100,${0.55 * k3})`; c.lineWidth = 2; c.shadowColor = 'rgba(231,169,100,0.6)'; c.shadowBlur = 8; c.beginPath();
    const drawn = 1000 * eo(p(t, L[12][1] - 0.1, L[12][1] + 1.4));
    for (let x = 40; x < 40 + drawn; x += 4) {
      const ph = ((x - 40) / 230) % 1, amp = 70 * Math.max(0, 1 - (x - 40) / 1000 * 0.9 - tired * 0.6);
      const y = pY + (ph > 0.45 && ph < 0.5 ? -amp : ph >= 0.5 && ph < 0.55 ? amp * 0.5 : 0);
      x === 40 ? c.moveTo(x, y) : c.lineTo(x, y);
    }
    c.stroke(); c.restore();
    T(c, 'qəlb yorğunluğu', CX, r3 + 40, { ff: PF, it: true, sz: 84, col: AMBER_L, a: k3, blur: (1 - k3) * 10 });
  }
}
// 3 — not physical tiredness: a matter of the heart (könül)
function s3(c, t) {
  const L = LINES[2].w; c.__t = t;
  const kk = said(t, L[8][1], 0.8);
  sky(c, { gy: 1000, warm: 0.35 * kk }); motes(c, t, 0.35);
  const dy = said(t, L[5][1], 0.6);
  const fy = 'fiziki yorğunluq';
  T(c, fy, CX, 700, { ff: LO, sz: 74, col: MOON, a: said(t, L[3][1]) * (1 - dy), blur: (1 - said(t, L[3][1])) * 8 });
  outlineText(c, fy, CX, 700 + dy * 14, { ff: LO, sz: 74, col: 'rgba(185,197,209,0.7)', lw: 1.2, a: dy * (1 - 0.5 * sm(p(t, 11.5, 12.4))) });
  T(c, 'deyil', CX, 780, { ff: IN, wt: 500, sz: 26, ls: 10, col: SLATE, a: dy * 0.9 });
  T(c, 'tamamilə', CX, 905, { ff: LO, it: true, sz: 46, col: MIST, a: said(t, L[6][1]) });
  // ember of the heart
  const br = 0.85 + 0.15 * Math.sin(t * 2.2);
  glow(c, CX, 1030, 420 * kk, '231,169,100', 0.28 * kk * br);
  glow(c, CX, 1030, 120 * kk, '255,220,170', 0.25 * kk * br);
  T(c, 'könül', CX, 1080, { ff: PF, it: true, sz: 190, col: amberGrad(c, 940, 1090), a: kk, blur: (1 - kk) * 14, glow: 26, glowCol: 'rgba(231,169,100,0.55)' });
  T(c, 'məsələsi', CX, 1180, { ff: LO, it: true, sz: 50, col: AMBER_L, a: said(t, L[9][1]) * 0.85 });
}
// 4 — today: labels, pills, fast-forward
const PILLS = (() => { const r = rng(61), a = []; for (let i = 0; i < 26; i++) a.push({ x: 150 + r() * 780, d: r() * 0.8, a0: r() * 6, va: (r() - 0.5) * 6, rest: 1300 + r() * 60, rot: (r() - 0.5) * 1.2 }); return a; })();
function s4(c, t) {
  const L = LINES[3].w; c.__t = t;
  sky(c, { cold: 1, gy: 900 });
  const ff = eio(p(t, L[13][1], 18.0)); // "tez keçib getsin": everything swipes away
  c.save(); c.translate(-ff * 1300, 0);
  // clinical grid
  c.strokeStyle = 'rgba(127,211,220,0.07)'; c.lineWidth = 1;
  for (let x = 0; x < W + 1400; x += 60) { c.beginPath(); c.moveTo(x, 0); c.lineTo(x, H); c.stroke(); }
  for (let y = 0; y < H; y += 60) { c.beginPath(); c.moveTo(0, y); c.lineTo(W + 1400, y); c.stroke(); }
  T(c, 'indi', CX, 470, { ff: IN, wt: 500, sz: 30, ls: 12, col: CYAN, a: said(t, L[0][1]) });
  const stamp = (txt, tt, y, rot) => {
    const k = p(t, tt - 0.05, tt + 0.25); if (k <= 0) return;
    const sc = lerp(1.5, 1, eback(k)); c.save(); c.translate(CX, y); c.rotate(rot); c.scale(sc, sc); c.globalAlpha = Math.min(1, k * 2);
    font(c, { ff: IN, wt: 600, sz: 86, ls: 4 }); const w = c.measureText(txt).width + 70;
    c.strokeStyle = CLIN; c.lineWidth = 3; c.strokeRect(-w / 2, -72, w, 104);
    c.fillStyle = CLIN; c.textAlign = 'center'; c.fillText(txt, 0, 0); c.restore();
  };
  stamp('stres', L[4][1], 700, -0.04);
  stamp('depressiya', L[7][1], 870, 0.03);
  // pills
  const pk = L[9][1];
  for (const q of PILLS) {
    const st = pk - 0.2 + q.d * 0.7, d = t - st; if (d < 0) continue;
    let y = -60 + 0.5 * 3800 * d * d; let ang = q.a0 + q.va * d;
    if (y > q.rest) { const tl = Math.sqrt(2 * (q.rest + 60) / 3800); const after = d - tl; y = q.rest - Math.abs(Math.sin(after * 9)) * 60 * Math.exp(-after * 5); ang = q.a0 + q.va * tl + q.rot * (1 - Math.exp(-after * 4)); }
    capsule(c, q.x, y, ang, 64, 15);
  }
  c.restore();
  // speed streaks during swipe
  if (ff > 0 && ff < 1) { const r = rng(8); for (let i = 0; i < 40; i++) { c.fillStyle = `rgba(228,246,248,${0.25 * Math.sin(ff * Math.PI)})`; c.fillRect(r() * W, r() * H, 200 + r() * 400, 1.5); } }
}
// 5 — the ancients: a lamp, slow light, respect
function s5(c, t) {
  const L = LINES[4].w; c.__t = t;
  sky(c, { warm: 0.8, gy: 900, gr: 1100 }); motes(c, t, 0.5, '250,215,170', -14);
  const la = eio(p(t, 17.9, 19.0));
  flame(c, CX, 960, t, 1.15, la);
  // lamp base
  c.save(); c.globalAlpha = la; c.strokeStyle = 'rgba(231,169,100,0.8)'; c.lineWidth = 2; c.beginPath(); c.ellipse(CX, 990, 120, 30, 0, 0, Math.PI); c.stroke(); c.beginPath(); c.moveTo(CX - 120, 990); c.quadraticCurveTo(CX - 60, 975, CX - 6, 966); c.moveTo(CX + 120, 990); c.quadraticCurveTo(CX + 170, 984, CX + 205, 962); c.stroke(); c.restore();
  wordsLine(c, [{ s: 'Halbuki', t: L[0][1] }], CX, 520, { ff: IN, wt: 500, sz: 28, ls: 10, col: AMBER, a: 0.85 });
  wordsLine(c, [{ s: 'qədim', t: L[1][1] }, { s: 'insanlar', t: L[2][1] }], CX, 610, { ff: LO, it: true, sz: 66, col: AMBER_L });
  const hk = said(t, L[7][1], 0.9);
  T(c, 'hörmətlə', CX, 1250, { ff: PF, it: true, sz: 140, col: amberGrad(c, 1140, 1260), a: hk, blur: (1 - hk) * 14, glow: 20, glowCol: 'rgba(231,169,100,0.45)' });
}
// 6 — noise of the world, withdrawal inward, alone with oneself
const NOISE = (() => { const r = rng(71), a = []; for (let i = 0; i < 70; i++) a.push({ x: 60 + r() * 960, y: 380 + r() * 1000, l: 30 + r() * 90, ph: r() * 6, f: 6 + r() * 14, d: r(), out: r() }); return a; })();
function s6(c, t) {
  const L = LINES[5].w; c.__t = t;
  sky(c, { gy: 900 });
  const lampOut = 1 - sm(p(t, 21.7, 22.6));
  if (lampOut > 0) glow(c, CX, 900, 60, '255,214,160', 0.8 * lampOut);
  // noise (səs-küy)
  const nIn = p(t, L[5][1] - 0.6, L[6][1] + 0.5), bez = eio(p(t, L[7][1], L[9][1] + 0.6));
  c.save(); c.lineWidth = 1.6; c.lineCap = 'round';
  for (const q of NOISE) {
    const a = clamp(nIn * 2 - q.d) * (1 - bez);
    if (a <= 0) continue;
    const push = bez * 400, dx = (q.x - CX), dy = (q.y - 900), dl = Math.hypot(dx, dy) || 1;
    const x = q.x + dx / dl * push, y = q.y + dy / dl * push;
    c.strokeStyle = `rgba(185,197,209,${0.5 * a})`; c.beginPath();
    for (let s = 0; s <= q.l; s += 4) { const yy = y + Math.sin(s * 0.35 + t * q.f + q.ph) * (6 + 8 * Math.sin(t * 7 + q.ph)) * (1 - s / q.l * 0.5); s ? c.lineTo(x + s, yy) : c.moveTo(x + s, yy); }
    c.stroke();
  }
  c.restore();
  // inward: a circle closes around one light
  const inK = eio(p(t, L[9][1] - 0.2, L[10][1] + 0.6));
  const ci = 1 - eio(p(t, L[11][1], L[12][1] + 0.4));
  if (inK > 0) {
    const R = lerp(700, 150, inK);
    c.save(); c.strokeStyle = `rgba(233,238,243,${0.5 * inK * ci})`; c.lineWidth = 1.5; c.beginPath(); c.arc(CX, 880, R, 0, 7); c.stroke(); c.restore();
  }
  // alone with oneself: the light and its reflection face each other
  const bb = eio(p(t, L[11][1] - 0.2, L[13][1] + 0.4));
  const lightY = lerp(880, 860, bb);
  glow(c, CX, lightY, 120, '233,238,243', 0.55 * Math.max(inK, 0.0));
  glow(c, CX, lightY, 18, '255,255,255', 0.9 * inK);
  if (bb > 0) {
    waterLine(c, 1000, 900 * bb, bb);
    glow(c, CX, 1140, 110, '185,197,209', 0.35 * bb);
    glow(c, CX, 1140, 16, '233,238,243', 0.6 * bb);
  }
  T(c, 'səs-küy', CX, 600, { ff: IN, wt: 500, sz: 30, ls: 12, col: SLATE, a: said(t, L[6][1]) * (1 - bez) });
  T(c, 'öz içinə', CX, 620, { ff: LO, it: true, sz: 70, col: MOON, a: said(t, L[9][1], 0.6) * (1 - sm(p(t, L[11][1], L[11][1] + 0.4))) });
  T(c, 'baş-başa', CX, 640, { ff: PF, it: true, sz: 92, col: MOON, a: said(t, L[13][1], 0.6) });
}
// 7 — not emptiness: fullness. 8 — the heart fills with words until speech runs out
const FILLW = ['söz', 'kədər', 'könül', 'duyğu', 'söz', 'sıxıntı', 'məlal', 'ürək', 'söz', 'sükut', 'hörmət', 'söz', 'qəlb', 'könül', 'kədər', 'duyğu', 'söz', 'məlal', 'söz', 'ruh', 'söz', 'könül', 'səs', 'söz'];
let SLOTS = null;
function s78(c, t) {
  const L6 = LINES[6].w, L7 = LINES[7].w; c.__t = t;
  sky(c, { gy: 900, warm: 0.25 * p(t, 30.3, 31.5) }); motes(c, t, 0.35);
  const cx = CX, cy = 900, R = 230, HS = 15;
  const appear = eio(p(t, 28.6, 29.3));
  const mk = eio(p(t, 31.0, 32.0)); // circle -> heart
  // liquid fill of the vessel (doluluq)
  const fillK = eio(p(t, L6[5][1] - 0.1, L6[5][1] + 1.1)) * (1 - sm(p(t, 31.2, 32.0)));
  c.save(); morphPath(c, cx, cy, mk, R, HS); c.clip();
  if (fillK > 0) {
    const lvl = cy + R - fillK * 2 * R;
    const g = c.createLinearGradient(0, lvl, 0, cy + R); g.addColorStop(0, 'rgba(246,211,161,0.55)'); g.addColorStop(1, 'rgba(231,169,100,0.25)');
    c.fillStyle = g; c.beginPath(); c.moveTo(cx - R - 10, cy + R + 10);
    for (let x = cx - R - 10; x <= cx + R + 10; x += 6) c.lineTo(x, lvl + Math.sin(x * 0.04 + t * 3) * 6);
    c.lineTo(cx + R + 10, cy + R + 10); c.fill();
  }
  // words pile into the heart
  if (t > 31.3) {
    if (!SLOTS) { SLOTS = []; const tmp = mk === 1 ? null : null; const r = rng(4); const c2 = document.createElement('canvas').getContext('2d'); morphPath(c2, cx, cy, 1, R, HS);
      for (let y = cy + 220; y > cy - 220; y -= 34) for (let x = cx - 260; x < cx + 260; x += 70 + r() * 30) { if (c2.isPointInPath(x, y) && c2.isPointInPath(x - 30, y) && c2.isPointInPath(x + 30, y)) SLOTS.push({ x: x + (r() - 0.5) * 16, y, rot: (r() - 0.5) * 0.3, w: FILLW[SLOTS.length % FILLW.length], c: r() }); } }
    const t0 = L7[1][1] - 0.2, t1 = L7[8][1] + 0.2; // "ürəyi" -> "qalmaz"
    SLOTS.forEach((q, i) => {
      const st = lerp(t0, t1 - 0.4, i / SLOTS.length), d = t - st; if (d < 0) return;
      const fall = Math.min(1, d / 0.45), y = lerp(cy - 420, q.y, ei(fall) * 0 + (1 - Math.pow(1 - fall, 2)));
      T(c, q.w, q.x, y, { ff: LO, it: true, sz: 30, col: q.c > 0.7 ? AMBER_L : MOON, a: Math.min(1, d * 4) * 0.85 });
    });
  }
  c.restore();
  morphPath(c, cx, cy, mk, R, HS);
  c.save(); c.globalAlpha = appear * (1 - sm(p(t, 35.0, 35.6))); c.strokeStyle = mk > 0.5 ? AMBER_L : MOON; c.lineWidth = 2.2; c.shadowColor = 'rgba(233,238,243,0.4)'; c.shadowBlur = 12; c.stroke(); c.restore();
  // boşluq (hollow) -> doluluq (full)
  const bA = said(t, L6[2][1], 0.5) * (1 - sm(p(t, L6[4][1], L6[4][1] + 0.4)));
  outlineText(c, 'boşluq', cx, cy + 40, { ff: PF, it: true, sz: 120, col: MOON, lw: 1.6, a: bA });
  T(c, 'deyil', cx, cy + 110, { ff: IN, wt: 500, sz: 24, ls: 10, col: SLATE, a: said(t, L6[3][1]) * bA });
  const dA = said(t, L6[5][1], 0.5) * (1 - sm(p(t, 31.1, 31.6)));
  T(c, 'doluluq', cx, cy + 40, { ff: PF, it: true, sz: 120, col: amberGrad(c, cy - 50, cy + 40), a: dA, glow: 22, glowCol: 'rgba(231,169,100,0.6)' });
  // "danışmağa taqəti qalmaz": stillness — a closed line under the heart
  const q = said(t, L7[8][1], 0.6) * (1 - sm(p(t, 35.0, 35.6)));
  waterLine(c, cy + 330, 300 * q, q, '231,169,100');
}
// 9 — silence (sükut), then depth (dərin)
function s9(c, t) {
  const L = LINES[8].w; c.__t = t;
  const dive = eio(p(t, L[8][1] - 0.3, L[8][1] + 1.2)); // "dərin"
  sky(c, { gy: 900, deep: dive });
  const water = lerp(1000, -40, dive);
  AC.clearRect(0, 0, W, H);
  const sk = said(t, L[4][1], 0.9), spread = eio(p(t, L[4][1], 39.5));
  AC.save(); AC.globalAlpha = 1 - sm(clamp(dive * 2.2)); AC.translate(0, water - 1000);
  T(AC, 'sükut', CX, 940, { ff: PF, it: true, sz: 170, ls: 10 + 34 * spread, col: silverGrad(AC, 820, 950), a: sk, blur: (1 - sk) * 12 });
  T(AC, 'Bax,', CX, 650, { ff: LO, it: true, sz: 54, col: MIST, a: said(t, L[0][1]) * (1 - said(t, L[4][1])) });
  T(AC, 'məlal', CX, 730, { ff: LO, it: true, sz: 64, col: MOON, a: said(t, L[1][1]) * 0.9 });
  AC.restore();
  c.drawImage(above, 0, 0);
  if (water > 0) { waterLine(c, water, 900, 1 - dive); reflect(c, above, water, t, { a: 0.32 * (1 - dive), amp: 2.5, h: 500 }); }
  // underwater depth
  if (dive > 0) {
    c.save(); c.globalAlpha = dive; motes(c, t, 0.7, '160,205,215', -26); c.restore();
    for (let i = 0; i < 6; i++) { const yy = 300 + i * 220; c.save(); c.globalAlpha = dive * 0.08; c.fillStyle = '#9fd0d8'; c.beginPath(); c.ellipse(CX + Math.sin(t * 0.5 + i) * 120, yy + Math.sin(t * 0.8 + i) * 20, 520, 26, 0, 0, 7); c.fill(); c.restore(); }
    const dk = said(t, L[8][1], 1.0);
    T(c, 'dərin', CX, 1050, { ff: PF, it: true, sz: 200, col: 'rgba(205,232,238,0.92)', a: dk * dive, blur: (1 - dk) * 16 + 1.2, glow: 30, glowCol: 'rgba(150,210,220,0.5)' });
  }
}
// 10 — if there is a məlal in your heart today, do not fear it
function s10(c, t) {
  const L = LINES[9].w; c.__t = t;
  const rise = eio(p(t, 39.4, 40.6));
  const warm = eio(p(t, L[12][1] - 0.3, L[12][1] + 1.2));
  sky(c, { deep: 1 - rise, warm: warm * 0.9, gy: 980 }); motes(c, t, 0.4, warm > 0.5 ? '250,215,170' : '180,215,225', -12);
  const hk = eio(p(t, L[7][1] - 0.2, L[7][1] + 0.8));
  c.save(); heartPath(c, CX, 980, 9.5, hk); c.strokeStyle = `rgba(233,238,243,${0.55 * (1 - warm) + 0.0})`; c.lineWidth = 1.6; c.stroke();
  heartPath(c, CX, 980, 9.5, hk); c.strokeStyle = `rgba(246,211,161,${0.8 * warm})`; c.stroke(); c.restore();
  const em = said(t, L[9][1], 0.8); const br = 0.85 + 0.15 * Math.sin(t * 2.6);
  glow(c, CX, 960, lerp(60, 380, warm) * em, '231,169,100', (0.35 + 0.2 * warm) * em * br);
  glow(c, CX, 960, 14 + 10 * warm, '255,236,205', 0.95 * em);
  T(c, 'bu gün', CX, 560, { ff: LO, it: true, sz: 50, col: MIST, a: said(t, L[5][1]) * (1 - warm * 0.3) });
  T(c, 'məlal', CX, 660, { ff: PF, it: true, sz: 96, col: MOON, a: said(t, L[9][1], 0.6) });
  const qk = said(t, L[12][1], 0.9);
  T(c, 'qorxmayın', CX, 1310, { ff: PF, it: true, sz: 124, col: amberGrad(c, 1210, 1320), a: qk, blur: (1 - qk) * 14, glow: 22, glowCol: 'rgba(231,169,100,0.5)' });
}
// 11 — the soul's most sincere, most silent conversation
function s11(c, t) {
  const L = LINES[10].w; c.__t = t;
  sky(c, { warm: 0.35, gy: 1000, gr: 1000 }); motes(c, t, 0.3, '240,215,185', -8);
  const wl = eo(p(t, 44.0, 45.0)), water = 1000;
  waterLine(c, water, 920 * wl, wl, '246,211,161');
  rainRings(c, t * 0.35, water, 0.35 * wl, 380);
  const you = said(t, L[4][1], 0.8), soul = said(t, L[3][1], 0.8);
  const b1 = 0.5 + 0.5 * Math.sin(t * 1.6), b2 = 0.5 + 0.5 * Math.sin(t * 1.6 + Math.PI);
  glow(c, CX, 860, 150, '246,211,161', 0.4 * you * (0.6 + 0.4 * b1)); glow(c, CX, 860, 16, '255,245,230', 0.95 * you);
  glow(c, CX, 1140, 150, '185,197,209', 0.35 * soul * (0.6 + 0.4 * b2)); glow(c, CX, 1140, 14, '233,238,243', 0.8 * soul);
  // silent dialogue: soft dotted arcs between the two lights
  const dl = Math.min(you, soul);
  if (dl > 0) for (let s of [-1, 1]) { c.save(); c.globalAlpha = dl * 0.55; c.setLineDash([2, 10]); c.lineDashOffset = -t * 20 * s; c.strokeStyle = s < 0 ? AMBER_L : MIST; c.lineWidth = 1.4; c.beginPath(); c.moveTo(CX, 880); c.bezierCurveTo(CX + s * 170, 940, CX + s * 170, 1060, CX, 1120); c.stroke(); c.restore(); }
  T(c, 'ruhunuzun', CX, 1290, { ff: LO, it: true, sz: 54, col: MIST, a: soul * (1 - sm(p(t, 46.8, 47.3))) });
  wordsLine(c, [{ s: 'ən', t: L[5][1] }, { s: 'səmimi', t: L[6][1] }], CX, 560, { ff: PF, it: true, sz: 92, col: AMBER_L });
  wordsLine(c, [{ s: 'ən', t: L[8][1] }, { s: 'səssiz', t: L[9][1] }], CX, 680, { ff: PF, it: true, sz: 92, col: MOON });
  T(c, 'söhbəti', CX, 1310, { ff: PF, it: true, sz: 100, col: CREAM, a: said(t, L[10][1], 0.6) * 0.95 });
}
// 12–13 — the word settles on the water; its reflection completes it; sign-off
function s12(c, t) {
  const L = LINES[11].w; c.__t = t;
  sky(c, { gy: 1000, warm: 0.15 }); motes(c, t, 0.3);
  const water = 1000, wy = 960;
  AC.clearRect(0, 0, W, H);
  const chars = [...WORD]; const lands = [];
  letters(AC, WORD, CX, wy, Object.assign({}, WO, { sz: 230, ls: 20, col: silverGrad(AC, wy - 180, wy), glow: 16, glowCol: 'rgba(200,220,240,0.35)' }), (i, n) => {
    const st = 50.9 + i * 0.3, f = p(t, st, st + 0.7); lands.push(st + 0.7);
    return { a: sm(clamp(f * 3)), dy: -700 * Math.pow(1 - eo(f), 1.5), blur: (1 - f) * 6 };
  });
  c.drawImage(above, 0, 0);
  const wl = eo(p(t, 50.4, 51.2));
  waterLine(c, water, 900 * wl, wl);
  reflect(c, above, water, t, { a: 0.4, h: 420 });
  const xs = [-340, -175, 0, 170, 330];
  lands.forEach((lt, i) => ripple(c, CX + xs[i], water + 4, t, lt, { n: 2, sp: 170, a: 0.55, life: 1.6 }));
  rainRings(c, t, water, 0.35 * p(t, 55.0, 56.5), 300);
  rain(c, t, 0.6 * p(t, 55.2, 57.0), water);
  const ta = 1 - sm(p(t, 55.0, 55.6));
  wordsLine(c, [{ s: 'Söz', t: L[0][1] }, { s: 'yerinə', t: L[1][1] }, { s: 'düşdü.', t: L[2][1] }], CX, 1300, { ff: LO, it: true, sz: 62, col: MOON, a: ta });
  wordsLine(c, [{ s: 'Gələn', t: L[3][1] }, { s: 'sözlərə', t: L[4][1] }, { s: 'qədər.', t: L[5][1] }], CX, 1385, { ff: LO, it: true, sz: 48, col: AMBER_L, a: ta * 0.9 });
}

const SCENES = [
  [0, 2.3, 0, 0.0, s1],
  [2.2, 8.55, 0.0, 0.45, s2],
  [8.5, 12.85, 0.4, 0.3, s3],
  [12.85, 17.95, 0.15, 0.3, s4],
  [17.85, 21.7, 0.35, 0.35, s5],
  [21.6, 28.65, 0.3, 0.35, s6],
  [28.55, 35.0, 0.35, 0.4, s78],
  [34.9, 39.45, 0.4, 0.3, s9],
  [39.3, 45.0, 0.3, 0.5, s10],
  [45.0, 50.5, 0.5, 0.45, s11],
  [50.3, 60, 0.45, 0, s12],
];
function render(t, fr = 0) {
  X.save(); X.fillStyle = '#000'; X.fillRect(0, 0, W, H);
  for (const [a, b, fi, fo, fn] of SCENES) {
    if (t < a - fi || t > b + fo) continue;
    const al = Math.min(fi ? sm(p(t, a - fi, a + fi * 0.2)) : 1, fo ? 1 - sm(p(t, b - fo * 0.2, b + fo)) : 1);
    if (al <= 0) continue;
    LC.setTransform(1, 0, 0, 1, 0, 0); LC.globalAlpha = 1; LC.globalCompositeOperation = 'source-over'; LC.filter = 'none'; LC.clearRect(0, 0, W, H);
    LC.save(); fn(LC, t); LC.restore();
    X.globalAlpha = al; X.drawImage(layer, 0, 0); X.globalAlpha = 1;
  }
  branding(X, t);
  captions(X, t);
  finish(X, t, fr);
  const fa = sm(p(t, DUR - 0.9, DUR));
  if (fa > 0) { X.fillStyle = `rgba(0,0,0,${fa})`; X.fillRect(0, 0, W, H); }
  X.restore();
}
window.render = render; window.DUR = DUR;
window.frameJPEG = (t, fr) => { render(t, fr); return cv.toDataURL('image/png'); };
