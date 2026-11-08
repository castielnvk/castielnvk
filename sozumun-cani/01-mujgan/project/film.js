// «Sözümün Canı — Müjgan» : procedural editorial film, 1080x1920
const W = 1080, H = 1920, CX = 540, DUR = 71.83;
const LOGO = new Image(); window.LOGO_READY = new Promise(r => { LOGO.onload = r; LOGO.onerror = r; }); LOGO.src = LOGO_SRC;
const cv = document.getElementById('c'); cv.width = W; cv.height = H;
const X = cv.getContext('2d');
const layer = document.createElement('canvas'); layer.width = W; layer.height = H;
const LC = layer.getContext('2d');

// ---------- palette ----------
const GOLD = '#d6b06c', GOLD_L = '#f2dcab', GOLD_D = '#9c7a43', CREAM = '#efe6d6',
  CRIMSON = '#b3313c', ROSE = '#e9a9b4', PEARL = '#fbf3ea';

// ---------- utils ----------
const clamp = (v, a = 0, b = 1) => Math.max(a, Math.min(b, v));
const lerp = (a, b, t) => a + (b - a) * t;
const p = (t, a, b) => clamp((t - a) / (b - a));
const eo = t => 1 - Math.pow(1 - t, 3);
const ei = t => t * t * t;
const eio = t => t < .5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;
const sm = t => t * t * (3 - 2 * t);
const eback = t => { const c1 = 1.4, c3 = c1 + 1; return 1 + c3 * Math.pow(t - 1, 3) + c1 * Math.pow(t - 1, 2); };
function rng(seed) { return () => { seed |= 0; seed = seed + 0x6D2B79F5 | 0; let t = Math.imul(seed ^ seed >>> 15, 1 | seed); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; }; }
const WT = (l, w) => LINES[l].w[w][1];
// a 0..1 "word has been spoken" ramp
const said = (t, time, d = 0.35) => sm(p(t, time - 0.06, time - 0.06 + d));

// ---------- text ----------
function font(c, o) { c.font = (o.it ? 'italic ' : '') + (o.wt || 400) + ' ' + (o.sz || 48) + 'px ' + (o.ff || 'CG'); c.letterSpacing = (o.ls || 0) + 'px'; }
function T(c, s, x, y, o = {}) {
  const a = o.a ?? 1; if (a <= 0.003) return;
  c.save(); font(c, o); c.textAlign = o.al || 'center'; c.textBaseline = 'alphabetic';
  c.globalAlpha *= a; c.fillStyle = o.col || CREAM;
  if (o.glow) { c.shadowColor = o.glowCol || 'rgba(240,200,130,0.55)'; c.shadowBlur = o.glow; }
  if (o.blur > 0.3) c.filter = `blur(${o.blur}px)`;
  const dx = (o.al || 'center') === 'center' ? (o.ls || 0) / 2 : 0;
  c.fillText(s, x + dx, y); c.restore();
}
function tw(c, s, o) { c.save(); font(c, o); const w = c.measureText(s).width - (o.ls || 0); c.restore(); return w; }
// per-letter drawing; fn(i,n,ch) -> {dx,dy,a,sc,rot,blur,col}
function letters(c, s, x, y, o, fn) {
  c.save(); font(c, o); c.textAlign = 'center'; c.textBaseline = 'alphabetic';
  const total = c.measureText(s).width - (o.ls || 0);
  let x0 = (o.al === 'left') ? x : x - total / 2;
  const chars = [...s], n = chars.length; let acc = '';
  for (let i = 0; i < n; i++) {
    const before = c.measureText(acc).width, cw = c.measureText(chars[i]).width - (o.ls || 0);
    acc += chars[i];
    const st = fn ? fn(i, n, chars[i]) : {};
    const a = (st.a ?? 1) * (o.a ?? 1); if (a <= 0.003 || chars[i] === ' ') continue;
    c.save(); c.translate(x0 + before + cw / 2 + (st.dx || 0), y + (st.dy || 0));
    if (st.rot) c.rotate(st.rot); if (st.sc != null) c.scale(st.sc, st.sc);
    c.globalAlpha *= a; c.fillStyle = st.col || o.col || CREAM;
    if (o.glow) { c.shadowColor = o.glowCol || 'rgba(240,200,130,0.5)'; c.shadowBlur = o.glow; }
    if ((st.blur || 0) > 0.3) c.filter = `blur(${st.blur}px)`;
    c.fillText(chars[i], 0, 0); c.restore();
  }
  c.restore(); return total;
}
// a centred line of words, each with own reveal time
function wordsLine(c, items, x, y, o) {
  c.save(); font(c, o); const sp = c.measureText(' ').width;
  const ws = items.map(it => { font(c, Object.assign({}, o, it.o || {})); return c.measureText(it.s).width - (o.ls || 0); });
  const total = ws.reduce((a, b) => a + b, 0) + sp * (items.length - 1);
  let cx = x - total / 2; c.restore();
  items.forEach((it, i) => {
    const k = it.t != null ? said(c.__t, it.t, it.d || 0.45) : 1;
    const oo = Object.assign({}, o, it.o || {}, { al: 'left', a: (o.a ?? 1) * k * (it.a ?? 1), blur: (1 - k) * (o.blurIn ?? 10) });
    T(c, it.s, cx, y + (1 - k) * (o.rise ?? 18), oo);
    cx += ws[i] + sp;
  });
}
function gradGold(c, y0, y1) { const g = c.createLinearGradient(0, y0, 0, y1); g.addColorStop(0, '#fff1cf'); g.addColorStop(0.45, GOLD_L); g.addColorStop(1, '#b8904f'); return g; }

// ---------- drawing primitives ----------
function lash(c, x, y, ang, len, curl, w, col) {
  if (len < 0.5) return;
  const N = 14, L = [], R = []; let px = x, py = y, a = ang; const st = len / N;
  for (let i = 0; i <= N; i++) {
    const s = i / N, ww = w * Math.pow(1 - s, 0.9) + 0.25;
    const nx = -Math.sin(a), ny = Math.cos(a);
    L.push([px + nx * ww / 2, py + ny * ww / 2]); R.push([px - nx * ww / 2, py - ny * ww / 2]);
    px += Math.cos(a) * st; py += Math.sin(a) * st; a += curl * 2 * s / N * 1.0;
  }
  c.beginPath(); c.moveTo(L[0][0], L[0][1]); for (const q of L) c.lineTo(q[0], q[1]);
  for (let i = R.length - 1; i >= 0; i--) c.lineTo(R[i][0], R[i][1]); c.closePath();
  c.fillStyle = col; c.fill();
}
function qpt(p0, p1, p2, u) { const v = 1 - u; return [v * v * p0[0] + 2 * u * v * p1[0] + u * u * p2[0], v * v * p0[1] + 2 * u * v * p1[1] + u * u * p2[1]]; }
function qtan(p0, p1, p2, u) { return [2 * (1 - u) * (p1[0] - p0[0]) + 2 * u * (p2[0] - p1[0]), 2 * (1 - u) * (p1[1] - p0[1]) + 2 * u * (p2[1] - p1[1])]; }
const LASH_R = (() => { const r = rng(7), a = []; for (let i = 0; i < 80; i++) a.push([r(), r(), r()]); return a; })();
// Eye: returns lash anchor info for reuse
function eye(c, cx, cy, o) {
  const w = o.w, h = o.h, op = o.open ?? 1, col = o.col || GOLD, lw = o.lw || 3;
  const P0 = [cx - w / 2, cy], P2 = [cx + w / 2, cy], U1 = [cx, cy - 2 * h * Math.max(op, 0.02)], D1 = [cx, cy + 2 * h * 0.62 * Math.max(op, 0.0)];
  c.save();
  if ((o.iris ?? 0) > 0 && op > 0.05) {
    c.save(); c.beginPath(); c.moveTo(...P0); c.quadraticCurveTo(...U1, ...P2); c.quadraticCurveTo(...D1, ...P0); c.clip();
    const ir = h * 0.95, iy = cy - h * 0.18 * op, ix = cx + (o.look || 0) * w * 0.12;
    const g = c.createRadialGradient(ix, iy, ir * 0.15, ix, iy, ir);
    g.addColorStop(0, '#120c08'); g.addColorStop(0.32, '#3a2412'); g.addColorStop(0.75, o.irisCol || '#8a5e2c'); g.addColorStop(1, '#2a1a0c');
    c.globalAlpha = o.iris; c.fillStyle = g; c.beginPath(); c.arc(ix, iy, ir, 0, 7); c.fill();
    c.fillStyle = '#060404'; c.beginPath(); c.arc(ix, iy, ir * 0.36, 0, 7); c.fill();
    c.fillStyle = 'rgba(255,244,220,0.9)'; c.beginPath(); c.arc(ix + ir * 0.3, iy - ir * 0.32, ir * 0.11, 0, 7); c.fill();
    if (o.glint) { c.globalAlpha = o.iris * o.glint; c.fillStyle = '#fff'; c.beginPath(); c.arc(ix - ir * 0.25, iy + ir * 0.2, ir * 0.05, 0, 7); c.fill(); }
    c.restore();
  }
  c.strokeStyle = col; c.lineCap = 'round'; c.globalAlpha *= (o.lidA ?? 1);
  if (o.glow) { c.shadowColor = 'rgba(240,200,130,0.5)'; c.shadowBlur = o.glow; }
  const draw = o.draw ?? 1;
  // upper lid (tapered: draw twice)
  c.lineWidth = lw; c.beginPath();
  for (let i = 0; i <= 60 * draw; i++) { const u = 0.5 + (i / 60 - 0.5) * 1, q = qpt(P0, U1, P2, 0.5 - draw / 2 + draw * i / (60 * draw || 1)); i ? c.lineTo(...q) : c.moveTo(...q); }
  c.stroke();
  if (op > 0.02 && (o.lower ?? 1) > 0) { c.globalAlpha *= (o.lower ?? 1); c.lineWidth = lw * 0.6; c.beginPath(); c.moveTo(...P0); c.quadraticCurveTo(...D1, ...P2); c.stroke(); c.globalAlpha /= (o.lower ?? 1); }
  c.restore();
  // lashes
  const n = o.lashes || 0, anchors = [];
  for (let k = 0; k < n; k++) {
    const u = 0.1 + 0.82 * (n === 1 ? 0.5 : k / (n - 1));
    const q = qpt(P0, U1, P2, u), tg = qtan(P0, U1, P2, u);
    let a = Math.atan2(tg[1], tg[0]) - Math.PI / 2; // normal pointing up(out)
    a += (u - 0.5) * 0.55;
    const down = -a; // mirror for closed
    const ang = lerp(down, a, sm(clamp(op * 1.6)));
    const rr = LASH_R[k % 80];
    const L = (o.lashLen || 40) * (0.55 + 0.45 * Math.sin(Math.PI * u)) * (0.85 + 0.3 * rr[0]);
    const g = clamp((o.lashP ?? 1) * 1.7 - (rr[1] * 0.7));
    const curlS = (op > 0.35 ? 1 : -1) * (u < 0.5 ? -1 : 1) * 0.35;
    anchors.push({ x: q[0], y: q[1], ang, len: L, u });
    if (o.skip && o.skip(k)) continue;
    c.save(); if (o.glow) { c.shadowColor = 'rgba(240,200,130,0.45)'; c.shadowBlur = o.glow * 0.6; }
    c.globalAlpha *= (o.lashA ?? 1);
    lash(c, q[0], q[1], ang, L * eo(g), curlS * (o.curl ?? 1), o.lashW || 3.2, o.lashCol || col);
    c.restore();
  }
  return anchors;
}
function arrow(c, x, y, ang, len, o = {}) { // (x,y) = tip
  const col = o.col || GOLD_L, w = o.w || 3, hs = o.hs || 16;
  const dx = Math.cos(ang), dy = Math.sin(ang), tx = x - dx * len, ty = y - dy * len;
  c.save(); c.globalAlpha *= (o.a ?? 1);
  if (o.glow) { c.shadowColor = o.glowCol || 'rgba(245,205,140,0.6)'; c.shadowBlur = o.glow; }
  c.strokeStyle = col; c.fillStyle = col; c.lineCap = 'round'; c.lineWidth = w;
  c.beginPath(); c.moveTo(tx, ty); c.lineTo(x - dx * hs * 0.6, y - dy * hs * 0.6); c.stroke();
  const nx = -dy, ny = dx;
  c.beginPath(); c.moveTo(x, y); c.lineTo(x - dx * hs + nx * hs * 0.42, y - dy * hs + ny * hs * 0.42);
  c.lineTo(x - dx * hs * 0.72, y - dy * hs * 0.72); c.lineTo(x - dx * hs - nx * hs * 0.42, y - dy * hs - ny * hs * 0.42); c.closePath(); c.fill();
  if (o.fletch !== false) {
    c.lineWidth = w * 0.7;
    for (let j = 0; j < 3; j++) {
      const bx = tx + dx * j * hs * 0.45, by = ty + dy * j * hs * 0.45;
      c.beginPath(); c.moveTo(bx, by); c.lineTo(bx - dx * hs * 0.7 + nx * hs * 0.5, by - dy * hs * 0.7 + ny * hs * 0.5); c.stroke();
      c.beginPath(); c.moveTo(bx, by); c.lineTo(bx - dx * hs * 0.7 - nx * hs * 0.5, by - dy * hs * 0.7 - ny * hs * 0.5); c.stroke();
    }
  }
  c.restore();
}
function heartPath(c, cx, cy, s, draw = 1) {
  c.beginPath(); const N = 140;
  for (let i = 0; i <= N * draw; i++) {
    const t = Math.PI + (i / N) * Math.PI * 2;
    const x = 16 * Math.pow(Math.sin(t), 3), y = -(13 * Math.cos(t) - 5 * Math.cos(2 * t) - 2 * Math.cos(3 * t) - Math.cos(4 * t));
    i ? c.lineTo(cx + x * s, cy + y * s) : c.moveTo(cx + x * s, cy + y * s);
  }
}
function heart(c, cx, cy, s, o = {}) {
  c.save();
  if ((o.fill || 0) > 0) {
    heartPath(c, cx, cy, s, 1);
    const g = c.createRadialGradient(cx, cy - s * 2, s * 1, cx, cy, s * 18);
    g.addColorStop(0, `rgba(235,120,110,${0.85 * o.fill})`); g.addColorStop(0.6, `rgba(160,40,52,${0.75 * o.fill})`); g.addColorStop(1, `rgba(70,12,24,${0.6 * o.fill})`);
    c.fillStyle = g; c.shadowColor = `rgba(220,70,70,${0.6 * o.fill})`; c.shadowBlur = 60 * o.fill; c.fill(); c.shadowBlur = 0;
  }
  heartPath(c, cx, cy, s, o.draw ?? 1);
  c.strokeStyle = o.col || GOLD; c.lineWidth = o.lw || 3; c.lineJoin = 'round'; c.lineCap = 'round';
  c.shadowColor = 'rgba(240,200,130,0.5)'; c.shadowBlur = 14; c.globalAlpha *= (o.a ?? 1); c.stroke();
  c.restore();
}
// ---------- atmosphere ----------
const DUST = (() => { const r = rng(11), a = []; for (let i = 0; i < 170; i++) a.push({ x: r() * W, y: r() * H, z: 0.25 + r() * 0.75, ph: r() * 6.28, f: 0.5 + r() }); return a; })();
function dust(c, t, o = {}) {
  const col = o.col || '246,214,160', amt = o.a ?? 0.6, sp = o.sp ?? 1;
  c.save(); c.globalCompositeOperation = 'lighter';
  for (const d of DUST) {
    const x = (d.x + Math.sin(t * 0.25 * d.f + d.ph) * 40 * d.z + (o.dx || 0) * d.z) % W;
    const y = ((d.y - t * 14 * d.z * sp) % H + H) % H;
    const fl = 0.5 + 0.5 * Math.sin(t * 1.7 * d.f + d.ph);
    const r = 0.8 + d.z * d.z * 3.2;
    const a = amt * (0.12 + 0.35 * fl) * d.z;
    if (d.z > 0.85) { const g = c.createRadialGradient(x, y, 0, x, y, r * 4); g.addColorStop(0, `rgba(${col},${a * 0.6})`); g.addColorStop(1, `rgba(${col},0)`); c.fillStyle = g; c.beginPath(); c.arc(x, y, r * 4, 0, 7); c.fill(); }
    else { c.fillStyle = `rgba(${col},${a})`; c.beginPath(); c.arc(x, y, r, 0, 7); c.fill(); }
  }
  c.restore();
}
function bg(c, kind, t, o = {}) {
  const P = {
    night: ['#0a0912', '#151026', '#1d1630', 'rgba(214,170,100,0.10)'],
    deep: ['#07060d', '#0f0b1b', '#141022', 'rgba(214,170,100,0.07)'],
    parch: ['#160f0a', '#24180f', '#2e2015', 'rgba(232,180,110,0.16)'],
    salon: ['#100c13', '#1d1420', '#2a1b2a', 'rgba(240,175,190,0.12)'],
    road: ['#070912', '#0d1224', '#1a1830', 'rgba(230,160,110,0.10)'],
    crimson: ['#0b080f', '#170c16', '#220f19', 'rgba(200,70,80,0.12)'],
  }[kind];
  const g = c.createLinearGradient(0, 0, 0, H); g.addColorStop(0, P[0]); g.addColorStop(0.55, P[1]); g.addColorStop(1, P[2]);
  c.fillStyle = g; c.fillRect(0, 0, W, H);
  const gx = o.gx ?? CX, gy = o.gy ?? 900, gr = o.gr ?? 900;
  const r = c.createRadialGradient(gx, gy, 0, gx, gy, gr); r.addColorStop(0, P[3]); r.addColorStop(1, 'rgba(0,0,0,0)');
  c.fillStyle = r; c.fillRect(0, 0, W, H);
}
// parchment fibres texture (static, generated once)
const PARCH = (() => {
  const cc = document.createElement('canvas'); cc.width = W; cc.height = H; const c = cc.getContext('2d'); const r = rng(3);
  for (let i = 0; i < 2600; i++) { c.strokeStyle = `rgba(240,200,150,${0.015 + r() * 0.03})`; c.lineWidth = 0.6 + r(); const x = r() * W, y = r() * H, a = r() * 0.6 - 0.3, l = 10 + r() * 60; c.beginPath(); c.moveTo(x, y); c.lineTo(x + Math.cos(a) * l, y + Math.sin(a) * l); c.stroke(); }
  for (let i = 0; i < 40; i++) { const x = r() * W, y = r() * H, rr = 80 + r() * 260; const g = c.createRadialGradient(x, y, 0, x, y, rr); g.addColorStop(0, `rgba(0,0,0,${0.05 + r() * 0.08})`); g.addColorStop(1, 'rgba(0,0,0,0)'); c.fillStyle = g; c.fillRect(x - rr, y - rr, rr * 2, rr * 2); }
  return cc;
})();
// illuminated manuscript frame with draw-on
function frame(c, t0, t, a = 1) {
  const k = eio(p(t, t0, t0 + 1.8)); if (k <= 0 || a <= 0) return;
  c.save(); c.globalAlpha *= a; c.strokeStyle = GOLD; c.shadowColor = 'rgba(240,200,130,0.35)'; c.shadowBlur = 8;
  const ins = [[66, 1.6], [84, 0.8]];
  for (const [m, lw] of ins) {
    const x0 = m, y0 = m + 60, w = W - 2 * m, h = H - 2 * m - 60, per = 2 * (w + h);
    c.lineWidth = lw; c.setLineDash([per * k, per]); c.beginPath();
    c.moveTo(CX, y0); c.lineTo(x0 + w, y0); c.lineTo(x0 + w, y0 + h); c.lineTo(x0, y0 + h); c.lineTo(x0, y0); c.closePath(); c.stroke();
  }
  c.setLineDash([]);
  // corner 8-point stars
  const corners = [[75, 135], [W - 75, 135], [75, H - 75], [W - 75, H - 75]];
  const ks = sm(p(t, t0 + 0.9, t0 + 2.0));
  for (const [x, y] of corners) {
    c.save(); c.translate(x, y); c.globalAlpha *= ks; c.lineWidth = 1.2;
    for (let j = 0; j < 2; j++) { c.save(); c.rotate(j * Math.PI / 4 + t * 0.05); c.strokeRect(-17, -17, 34, 34); c.restore(); }
    c.beginPath(); c.arc(0, 0, 5, 0, 7); c.fillStyle = GOLD; c.fill(); c.restore();
  }
  // top/bottom centre ornament: small diamonds
  c.globalAlpha *= ks;
  for (const y of [135, H - 75]) { for (let i = -3; i <= 3; i++) { c.save(); c.translate(CX + i * 26, y); c.rotate(Math.PI / 4); const s = i === 0 ? 7 : 3.5; c.fillStyle = GOLD; c.fillRect(-s / 2, -s / 2, s, s); c.restore(); } }
  c.restore();
}

// ---------- grain & vignette ----------
const GRAIN = [0, 1, 2].map(s => {
  const cc = document.createElement('canvas'); cc.width = 540; cc.height = 960; const c = cc.getContext('2d');
  const id = c.createImageData(540, 960), r = rng(100 + s);
  for (let i = 0; i < id.data.length; i += 4) { const v = 128 + (r() + r() + r() - 1.5) * 90; id.data[i] = id.data[i + 1] = id.data[i + 2] = v; id.data[i + 3] = 255; }
  c.putImageData(id, 0, 0); return cc;
});
function finish(c, t, fr) {
  c.save(); c.globalCompositeOperation = 'soft-light'; c.globalAlpha = 0.22;
  const g = GRAIN[fr % 3]; const ox = (fr * 37) % 60, oy = (fr * 53) % 60;
  c.drawImage(g, -ox, -oy, W + 120, H + 120); c.restore();
  const v = c.createRadialGradient(CX, 900, 380, CX, 960, 1250); v.addColorStop(0, 'rgba(0,0,0,0)'); v.addColorStop(1, 'rgba(0,0,0,0.62)');
  c.fillStyle = v; c.fillRect(0, 0, W, H);
}

// ---------- captions (word-synced) ----------
const CAP = { 4: 1, 5: 1, 6: 1, 8: 1, 9: 1, 10: 1, 11: 1, 12: 1, 14: 1 };
function captions(c, t) {
  for (const li in CAP) {
    const Ln = LINES[li], next = LINES[+li + 1];
    const endT = Math.min(Ln.e + 0.7, next ? next.s - 0.05 : 99);
    if (t < Ln.s - 0.15 || t > endT) continue;
    const fade = sm(p(t, Ln.s - 0.15, Ln.s + 0.1)) * (1 - sm(p(t, endT - 0.35, endT)));
    const o = { ff: 'Inter', wt: 400, sz: 37 };
    c.save(); font(c, o); const sp = c.measureText(' ').width;
    const lines = [[]]; let lw = 0; const maxW = 820;
    for (const [w, wt] of Ln.w) { const ww = c.measureText(w).width; if (lw + ww > maxW && lines[lines.length - 1].length) { lines.push([]); lw = 0; } lines[lines.length - 1].push([w, wt, ww]); lw += ww + sp; }
    const lh = 54, bottom = 1555, top = bottom - (lines.length - 1) * lh;
    // readability scrim
    const g = c.createLinearGradient(0, top - 120, 0, bottom + 80); g.addColorStop(0, 'rgba(5,4,10,0)'); g.addColorStop(0.45, `rgba(5,4,10,${0.42 * fade})`); g.addColorStop(1, `rgba(5,4,10,${0.5 * fade})`);
    c.fillStyle = g; c.fillRect(0, top - 120, W, H - top + 120);
    lines.forEach((L, j) => {
      const total = L.reduce((a, q) => a + q[2], 0) + sp * (L.length - 1); let x = CX - total / 2;
      for (const [w, wt, ww] of L) {
        const k = sm(p(t, wt - 0.08, wt + 0.2)); const cur = t >= wt - 0.05 && t < wt + 0.45;
        c.globalAlpha = fade * (0.12 + 0.86 * k);
        c.fillStyle = cur ? GOLD_L : CREAM; c.textAlign = 'left';
        c.shadowColor = 'rgba(0,0,0,0.6)'; c.shadowBlur = 10;
        c.fillText(w, x, top + j * lh + (1 - k) * 6); x += ww + sp;
      }
    });
    c.restore();
  }
}

// ---------- brand (segment title) ----------
function brand(c, t) {
  const C = { y: 838, sz: 66, a: 1 }, Tp = { y: 268, sz: 28, a: 0.7 };
  // exact supplied logo (ARAZ Radio 103.3 FM), proportions preserved
  if (LOGO.naturalWidth) {
    const ar = LOGO.naturalHeight / LOGO.naturalWidth;
    const topA = sm(p(t, 3.6, 4.6)) * (1 - sm(p(t, 67.5, 67.9)));
    if (topA > 0) { const lw = 180, lh = lw * ar; c.save(); c.globalAlpha = 0.88 * topA; c.drawImage(LOGO, CX - lw / 2, 150, lw, lh); c.restore(); }
    const endA = sm(p(t, 68.3, 69.0));
    if (endA > 0) { const lw = 360, lh = lw * ar; c.save(); c.globalAlpha = endA; c.drawImage(LOGO, CX - lw / 2, 600 + (1 - endA) * 16, lw, lh); c.restore(); }
  }
  let k = eio(p(t, 3.3, 4.5)); if (t > 68.3) k = 0;
  const y = lerp(C.y, Tp.y, k), sz = lerp(C.sz, Tp.sz, k), a = lerp(C.a, Tp.a, k) * (t > 67.5 && t < 68.3 ? 1 - sm(p(t, 67.5, 67.9)) : 1);
  const s = 'SÖZÜMÜN CANI';
  letters(c, s, CX, y, { ff: 'CSC', wt: 500, sz, ls: sz * 0.32, col: GOLD_L, a, glow: 10 }, (i, n) => {
    let r = 1;
    if (t < 5) { const ti = 0.95 + i * 0.09; r = sm(p(t, ti, ti + 0.7)); }
    if (t > 68.3) { const ti = 68.5 + i * 0.08; r = sm(p(t, ti, ti + 0.7)); }
    return { a: r, dy: (1 - r) * 14, blur: (1 - r) * 8 };
  });
}

// ================= SCENES =================
// A — opening: closed eyelid of gold, lashes grow
function sA(c, t) {
  bg(c, 'deep', t, { gy: 960, gr: 800 }); dust(c, t, { a: 0.45 });
  c.save(); const s = 1 + 0.035 * t / 4; c.translate(CX, 990); c.scale(s, s); c.translate(-CX, -990);
  const k = eo(p(t, 0.05, 1.5));
  eye(c, CX, 990, { w: 720 * k + 2, h: 30, open: 0.0, lw: 2.6, col: GOLD_L, glow: 16, lashes: 23, lashLen: 70, lashP: p(t, 1.3, 3.6), lashW: 2.6, lower: 0 });
  // spark travelling the lid while it draws
  if (t < 1.6) { const x = CX + 360 * k; const g = c.createRadialGradient(x, 990, 0, x, 990, 40); g.addColorStop(0, `rgba(255,240,205,${0.9 * (1 - p(t, 1.2, 1.6))})`); g.addColorStop(1, 'rgba(255,240,205,0)'); c.fillStyle = g; c.fillRect(x - 40, 950, 80, 80); const x2 = CX - 360 * k; c.save(); c.translate(x2 - x, 0); c.fillRect(x - 40, 950, 80, 80); c.restore(); }
  c.restore();
}
// B — proverb, rings of sound
function sB(c, t) {
  bg(c, 'deep', t, { gy: 960 }); dust(c, t, { a: 0.4 });
  const L = LINES[1].w; c.__t = t;
  c.save(); c.lineWidth = 1.4;
  L.forEach(([w, wt], i) => {
    for (let j = 0; j < 2; j++) { const dt = t - wt - j * 0.18; if (dt < 0 || dt > 3) continue; const r = 40 + dt * 360, a = (1 - dt / 3) * 0.32 * (t < WT(1, 5) + 0.2 ? 1 : 1 - p(t, WT(1, 5), WT(1, 5) + 0.8)); c.strokeStyle = `rgba(214,176,108,${a})`; c.beginPath(); c.arc(CX, 960, r, 0, 7); c.stroke(); }
  });
  c.restore();
  const o = { it: true, wt: 300, sz: 96, col: CREAM, blurIn: 14 };
  wordsLine(c, [{ s: 'Qulaq', t: L[0][1] }, { s: 'gündə', t: L[1][1] }], CX, 860, o);
  wordsLine(c, [{ s: 'bir', t: L[2][1] }, { s: 'söz', t: L[3][1], o: { it: false, wt: 500, col: GOLD_L, glow: 14 } }, { s: 'eşitməsə', t: L[4][1] }], CX, 985, o);
  // "kar olar." — goes quiet: letters tighten & dim
  const kk = p(t, L[6][1] + 0.4, L[6][1] + 1.6);
  wordsLine(c, [{ s: 'kar', t: L[5][1] }, { s: 'olar.', t: L[6][1] }], CX, 1110, Object.assign({}, o, { a: 1 - 0.35 * kk }));
}
// C — "qulağınız bizdə olsun": rings converge into a spiral (ear / shell)
function sC(c, t) {
  bg(c, 'night', t, { gy: 880 }); dust(c, t, { a: 0.5 });
  const L = LINES[2].w; c.__t = t;
  const col = 1 - eio(p(t, 11.7, 12.75)); // collapse
  // inward rings
  c.save(); c.lineWidth = 1.3;
  for (let j = 0; j < 6; j++) { const ph = ((t * 0.55 + j / 6) % 1); const r = lerp(520, 30, ph) * col; const a = Math.sin(ph * Math.PI) * 0.28 * p(t, 7.3, 8.3); c.strokeStyle = `rgba(214,176,108,${a})`; c.beginPath(); c.arc(CX, 900, Math.max(r, 1), 0, 7); c.stroke(); }
  c.restore();
  // golden spiral (ear)
  const dk = eio(p(t, WT(2, 4) - 0.1, WT(2, 4) + 1.6));
  c.save(); c.translate(CX, 900); c.rotate(-t * 0.12 * 0); c.scale(col, col);
  c.strokeStyle = GOLD_L; c.lineWidth = 2.4; c.shadowColor = 'rgba(240,200,130,0.5)'; c.shadowBlur = 12; c.lineCap = 'round';
  c.beginPath(); const turns = 3.2, N = 300;
  for (let i = 0; i <= N * dk; i++) { const s = i / N, a = s * turns * Math.PI * 2 + 1.2, r = 175 * Math.pow(1 - s, 1.25) + 6; const x = Math.cos(a) * r * 0.78, y = Math.sin(a) * r; i ? c.lineTo(x, y) : c.moveTo(x, y); }
  c.stroke(); c.restore();
  if (t > 11.6) { const k = sm(p(t, 11.9, 12.6)) * (1 - p(t, 12.9, 13.3)); const g = c.createRadialGradient(CX, 900, 0, CX, 900, 90); g.addColorStop(0, `rgba(255,240,210,${k})`); g.addColorStop(1, 'rgba(255,240,210,0)'); c.fillStyle = g; c.fillRect(CX - 90, 810, 180, 180); }
  const ta = col;
  wordsLine(c, [{ s: 'Sözümün', t: L[0][1] }, { s: 'canı', t: L[1][1] }, { s: 'odur', t: L[2][1] }, { s: 'ki,', t: L[3][1] }], CX, 560, { it: true, wt: 300, sz: 56, col: GOLD_L, a: ta });
  wordsLine(c, [{ s: 'qulağınız', t: L[4][1], d: 0.9 }], CX, 1240, { it: true, wt: 300, sz: 132, col: CREAM, a: ta, blurIn: 18 });
  wordsLine(c, [{ s: 'bizdə', t: L[5][1] }, { s: 'olsun.', t: L[6][1] }], CX, 1360, { it: false, wt: 300, sz: 84, col: CREAM, a: ta * 0.9, ls: 6 });
}
// WORD — reveal, origin, meaning, manuscript, lashes become arrows
const ARR = (() => { const r = rng(21), a = []; for (let i = 0; i < 40; i++) a.push({ dx: (r() - 0.5) * 260, dy: (r() - 0.35) * 120, d: r() * 0.35, rot: (r() - 0.5) * 0.5 }); return a; })();
function sWord(c, t) {
  // background: night -> parchment
  bg(c, 'night', t, { gy: 960 });
  const pk = eio(p(t, 18.9, 20.3));
  if (pk > 0) { c.save(); c.globalAlpha = pk; bg(c, 'parch', t, { gy: 900, gr: 1000 }); c.globalAlpha = pk * 0.9; c.drawImage(PARCH, 0, 0); c.restore(); }
  dust(c, t, { a: 0.5 + pk * 0.3 });
  frame(c, 19.4, t, pk);
  c.__t = t;
  const L3 = LINES[3].w;
  // "Bu günün sözü"
  const bA = 1 - sm(p(t, 15.0, 15.6));
  wordsLine(c, [{ s: 'Bu', t: L3[0][1] }, { s: 'günün', t: L3[1][1] }, { s: 'sözü', t: L3[2][1] }], CX, 720, { it: true, wt: 300, sz: 60, col: GOLD_L, a: bA });
  // aperture (eye-shaped) through which the word emerges
  const rev = WT(3, 3); // 14.30
  const ap = eio(p(t, rev - 0.15, rev + 0.85));
  const mv = eio(p(t, 15.0, 16.0)); // move word up
  const wy = lerp(1035, 610, mv), wsc = lerp(1, 0.6, mv);
  const word = 'MÜJGAN';
  if (t > rev - 0.6) {
    // slit of light before opening
    const sl = sm(p(t, rev - 0.6, rev - 0.1)) * (1 - p(t, rev + 0.4, rev + 1.2));
    if (sl > 0) { const g = c.createLinearGradient(CX - 520, 0, CX + 520, 0); g.addColorStop(0, 'rgba(255,236,200,0)'); g.addColorStop(0.5, `rgba(255,236,200,${0.9 * sl})`); g.addColorStop(1, 'rgba(255,236,200,0)'); c.fillStyle = g; c.fillRect(CX - 520 * sl, 958, 1040 * sl, 4); }
    c.save();
    if (ap < 1) { c.beginPath(); const hh = 230 * ap; c.moveTo(CX - 520, 960); c.quadraticCurveTo(CX, 960 - 2 * hh, CX + 520, 960); c.quadraticCurveTo(CX, 960 + 2 * hh * 0.7, CX - 520, 960); c.clip(); }
    c.translate(CX, wy); c.scale(wsc, wsc); c.translate(-CX, -wy);
    const g = gradGold(c, wy - 160, wy + 10);
    letters(c, word, CX, wy, { wt: 500, sz: 228, ls: 16, col: g, glow: 22 }, (i, n) => { const ti = rev + i * 0.06; const k = eo(p(t, ti - 0.1, ti + 0.7)); return { dy: (1 - k) * 90, blur: (1 - k) * 10, a: k }; });
    c.restore();
    // the aperture's lids + lashes as it opens (fade after)
    const la = sm(p(t, rev - 0.1, rev + 0.3)) * (1 - sm(p(t, rev + 0.9, rev + 1.5)));
    if (la > 0) { c.save(); c.globalAlpha = la; eye(c, CX, 960, { w: 1040, h: 230 * ap, open: 1, lw: 2, col: GOLD, lashes: 30, lashLen: 70, lashP: p(t, rev, rev + 0.9), lashW: 2.4, glow: 10 }); c.restore(); }
  }
  // origin journey: "fars dilindən" -> "dilimizə"
  const L4 = LINES[4].w;
  const oA = 1 - sm(p(t, 18.6, 19.3));
  T(c, 'fars dilindən', 250, 780, { it: true, wt: 300, sz: 46, col: CREAM, a: said(t, L4[1][1]) * oA * 0.9 });
  T(c, 'dilimizə', 840, 780, { it: true, wt: 300, sz: 46, col: CREAM, a: said(t, L4[2][1]) * oA * 0.9 });
  const jk = eio(p(t, L4[2][1] - 0.15, L4[3][1] + 0.5));
  if (jk > 0 && oA > 0) {
    const P0 = [250, 735], P1 = [CX, 655], P2 = [840, 735];
    c.save(); c.globalAlpha = oA; c.setLineDash([2, 9]); c.strokeStyle = GOLD; c.lineWidth = 2; c.lineCap = 'round';
    c.beginPath(); for (let i = 0; i <= 50 * jk; i++) { const q = qpt(P0, P1, P2, i / 50); i ? c.lineTo(...q) : c.moveTo(...q); } c.stroke(); c.setLineDash([]);
    const q = qpt(P0, P1, P2, jk), tg = qtan(P0, P1, P2, jk); arrow(c, q[0], q[1], Math.atan2(tg[1], tg[0]), 34, { hs: 12, w: 2, fletch: false, glow: 8, a: 1 });
    c.restore();
  }
  // "kirpik" + eye illustration
  const kT = L4[8][1]; // 17.96
  const L5 = LINES[5].w;
  const strike = eio(p(t, L5[8][1] - 0.02, L5[8][1] + 0.35)); // "deyil"
  const kA = said(t, kT, 0.6) * (1 - 0.6 * sm(p(t, L5[8][1] + 0.3, L5[8][1] + 0.9))) * (1 - sm(p(t, 22.75, 23.2)));
  const ky = 905;
  T(c, 'kirpik', CX, ky, { it: true, wt: 300, sz: 112, col: CREAM, a: kA, blur: (1 - said(t, kT, 0.6)) * 12 });
  T(c, 'mənası', CX, ky - 112, { ff: 'CSC', wt: 500, sz: 30, ls: 9, col: GOLD, a: said(t, L4[6][1]) * kA * 0.85 });
  if (strike > 0 && kA > 0) { const w = tw(c, 'kirpik', { it: true, wt: 300, sz: 112 }) + 50; c.save(); c.globalAlpha = Math.min(1, kA * 1.6); c.strokeStyle = GOLD_L; c.lineWidth = 3; c.shadowColor = 'rgba(240,200,130,0.6)'; c.shadowBlur = 10; c.beginPath(); c.moveTo(CX - w / 2, ky - 30); c.lineTo(CX - w / 2 + w * strike, ky - 30 - 8 * strike); c.stroke(); c.restore(); }
  // the eye: drawn at "sadəcə/kirpik", moves up for the arrow passage
  const eD = eio(p(t, L4[7][1], kT + 0.8));
  if (eD > 0) {
    const up = eio(p(t, 22.4, 23.3));
    const ey = lerp(1170, 880, up);
    const op = 0.78;
    // lashes -> arrows
    const fly0 = WT(6, 2) - 0.05; // "sancılan" 23.84
    const hx = CX, hy = 1235, hs = 7.6;
    const anchors = eye(c, CX, ey, { w: 600, h: 70, open: op * eD, lw: 3, col: GOLD_L, glow: 12, iris: eD * 0.9 * (1 - 0.3 * pk), lashes: 17, lashLen: 78, lashP: p(t, kT, kT + 1.3), lashW: 3, draw: eD,
      skip: (k) => t > fly0 + ARR[k].d * 0.6 - 0.02, curl: 1 - sm(p(t, 22.9, 23.7)) });
    // arrows in flight / embedded
    const ha = sm(p(t, 22.9, 23.5));
    if (ha > 0) {
      const pulse = 1 + 0.05 * Math.exp(-6 * Math.max(0, t - (fly0 + 0.55))) * (t > fly0 + 0.55 ? 1 : 0);
      heart(c, hx, hy, hs * pulse, { draw: eio(ha), a: 1, fill: 0.8 * sm(p(t, fly0 + 0.45, fly0 + 1.2)) });
    }
    anchors.forEach((A, k) => {
      const st = fly0 + ARR[k].d * 0.6;
      if (t < st - 0.02) return;
      const f = eio(p(t, st, st + 0.55));
      const tx = hx + ARR[k].dx * 0.7, ty = hy + ARR[k].dy - 10;
      const x = lerp(A.x + Math.cos(A.ang) * A.len, tx, f), y = lerp(A.y + Math.sin(A.ang) * A.len, ty, f);
      const dirFly = Math.atan2(ty - A.y, tx - A.x) + ARR[k].rot * f;
      const ang = lerp(A.ang, dirFly, sm(clamp(f * 3)));
      const ln = lerp(A.len, 120, sm(clamp(f * 2)));
      arrow(c, x, y, ang, ln, { hs: 13, w: 2.2, glow: 10, a: 1 });
    });
  }
}
// G — eye becomes bow, gaze the archer, lash the arrow, target
function sG(c, t) {
  bg(c, 'night', t, { gy: 900 }); dust(c, t, { a: 0.45 });
  c.__t = t; const L = LINES[8].w;
  const zoom = eio(p(t, 31.6, 32.5)); // push into target
  c.save(); const zs = 1 + zoom * 1.25; c.translate(CX, 560); c.scale(zs, zs); c.translate(-CX, -560 + zoom * -300 / zs * 0);
  wordsLine(c, [{ s: 'Təsəvvür', t: WT(7, 0) }, { s: 'edin.', t: WT(7, 1) }], CX, 340 + 0, { it: true, wt: 300, sz: 66, col: CREAM, a: (1 - 0.45 * p(t, 26.6, 27.2)) * (1 - zoom) });
  // target
  const tA = eio(p(t, L[8][1] - 0.1, L[8][1] + 0.9));
  const hit = L[13][1] - 0.12; // ~31.28
  const shake = t > hit ? Math.exp(-8 * (t - hit)) * Math.sin((t - hit) * 70) * 6 : 0;
  if (tA > 0) {
    c.save(); c.translate(CX + shake, 560);
    for (let r = 5; r >= 1; r--) {
      const rr = r * 30 * tA;
      c.beginPath(); c.arc(0, 0, rr, 0, 7);
      c.fillStyle = r % 2 ? 'rgba(40,30,50,0.85)' : 'rgba(22,17,32,0.9)'; c.fill();
      c.strokeStyle = GOLD; c.lineWidth = 1.6; c.stroke();
    }
    const tenK = said(t, L[10][1], 0.5); // "onluğundan"
    c.beginPath(); c.arc(0, 0, 30 * tA, 0, 7); c.fillStyle = `rgba(214,176,108,${0.25 + 0.55 * tenK})`; c.shadowColor = 'rgba(240,200,130,0.7)'; c.shadowBlur = 25 * tenK; c.fill(); c.shadowBlur = 0;
    T(c, '10', 0, 12, { wt: 500, sz: 36, col: '#1a1222', a: tenK });
    c.restore();
    if (t > hit) { const d = t - hit; for (let j = 0; j < 3; j++) { const dd = d - j * 0.12; if (dd < 0) continue; c.strokeStyle = `rgba(242,220,171,${Math.max(0, 0.6 - dd * 0.5)})`; c.lineWidth = 2; c.beginPath(); c.arc(CX, 560, 150 + dd * 380, 0, 7); c.stroke(); } }
  }
  // equation rows
  const rows = [['Göz', L[0][1], 'yay', L[2][1]], ['Baxış', L[3][1], 'atıcı', L[5][1]], ['Müjgan', L[6][1], 'ox', L[13][1]]];
  rows.forEach(([a, ta, b, tb], i) => {
    const y = 870 + i * 82, ra = said(t, ta, 0.5), rb = said(t, tb, 0.5);
    T(c, a, CX - 34, y + (1 - ra) * 12, { al: 'right', wt: 500, sz: 60, col: GOLD_L, a: ra * (1 - zoom), blur: (1 - ra) * 8 });
    T(c, b, CX + 34, y + (1 - rb) * 12, { al: 'left', it: true, wt: 300, sz: 62, col: CREAM, a: rb * (1 - zoom), blur: (1 - rb) * 8 });
    c.save(); c.globalAlpha = ra * (1 - zoom) * 0.9; c.fillStyle = GOLD; c.translate(CX, y - 18); c.rotate(Math.PI / 4); c.fillRect(-4, -4, 8, 8); c.restore();
  });
  // eye -> bow
  const by = 1265;
  const m = eio(p(t, L[0][1] - 0.1, L[2][1] + 0.4)); // morph
  const draw = sm(p(t, L[3][1] + 0.2, L[5][1] + 0.5)); // archer draws string
  const rel = L[11][1]; // "vuran" 30.86
  const released = t > rel;
  const snap = released ? Math.exp(-14 * (t - rel)) * Math.cos((t - rel) * 60) : 1;
  const pull = released ? 0.0 + 0.0 * snap : draw;
  const bw = 640, limb = lerp(70, 105, m);
  const P0 = [CX - bw / 2, by + lerp(0, 25, m)], P2 = [CX + bw / 2, by + lerp(0, 25, m)], U1 = [CX, by - 2 * limb];
  // iris (gaze) fades out as it becomes a bow
  const irisA = (1 - m) * 0.9;
  if (irisA > 0.01) eye(c, CX, by, { w: bw, h: 70, open: 0.8, lw: 3, col: GOLD_L, iris: irisA, lashes: 0, lidA: 0 });
  c.save(); c.strokeStyle = GOLD_L; c.lineCap = 'round'; c.shadowColor = 'rgba(240,200,130,0.5)'; c.shadowBlur = 14;
  // limb, thicker in middle
  for (let i = 0; i < 40; i++) { const u0 = i / 40, u1 = (i + 1) / 40; const a = qpt(P0, U1, P2, u0), b = qpt(P0, U1, P2, u1); c.lineWidth = 3 + m * 7 * Math.sin(Math.PI * (u0 + u1) / 2); c.beginPath(); c.moveTo(...a); c.lineTo(...b); c.stroke(); }
  // string (was lower lid)
  const strY = by + lerp(0, 25, m) + pull * 120 + (released ? snap * 18 : 0);
  const lowCtrlY = lerp(by + 2 * 70 * 0.62 * 0.8, strY, m);
  c.lineWidth = 1.6; c.beginPath(); c.moveTo(...P0);
  if (m < 1) c.quadraticCurveTo(CX, lowCtrlY, ...P2); else { c.lineTo(CX, strY); c.lineTo(...P2); }
  c.stroke(); c.restore();
  // lashes on the lid fade out as eye becomes bow
  if (m < 1) { c.save(); c.globalAlpha = 1 - m; eye(c, CX, by, { w: bw, h: 70, open: 0.8, lw: 0.01, lidA: 0, col: GOLD_L, lashes: 15, lashLen: 70, lashW: 3, lower: 0 }); c.restore(); }
  // gaze beam (archer)
  const gz = said(t, L[3][1], 0.6) * (released ? 1 - p(t, rel, rel + 0.3) : 1);
  if (gz > 0) { const g = c.createLinearGradient(0, strY, 0, 560); g.addColorStop(0, `rgba(245,215,160,${0.0})`); g.addColorStop(0.3, `rgba(245,215,160,${0.12 * gz})`); g.addColorStop(1, `rgba(245,215,160,${0.02 * gz})`); c.fillStyle = g; c.beginPath(); c.moveTo(CX - 8, strY); c.lineTo(CX - 60, 560); c.lineTo(CX + 60, 560); c.lineTo(CX + 8, strY); c.fill();
    c.save(); c.globalAlpha = gz * 0.8; c.setLineDash([3, 12]); c.strokeStyle = GOLD; c.lineWidth = 1.5; c.beginPath(); c.moveTo(CX, strY - 260); c.lineTo(CX, 600); c.stroke(); c.restore(); }
  // arrows (müjgan = arrows): one hero + two companions
  const nk = said(t, L[6][1], 0.6);
  if (nk > 0) {
    const hitT = hit, fl = released ? eio(p(t, rel, hitT)) : 0;
    const tipRest = strY - 330;
    [[0, 1], [-1, 0.45], [1, 0.45]].forEach(([s, aa]) => {
      const ang = -Math.PI / 2 + s * 0.16;
      const tipY = lerp(tipRest, 560 + 18, fl), tipX = CX + s * lerp(48, 120, fl) * (1 - fl * 0.2) + s * fl * 30;
      const ax = s === 0 ? CX : tipX, ay = s === 0 ? tipY : lerp(tipRest + 20, 470 + 40, fl);
      const alpha = nk * aa * (s !== 0 && released ? 1 - p(t, rel, rel + 0.5) : 1);
      arrow(c, ax, ay, ang, 330, { hs: 20, w: 3, glow: 14, a: alpha });
    });
  }
  c.restore();
}
// H — salon: ring light, lash extensions, hours
function sH(c, t) {
  bg(c, 'salon', t, { gy: 860, gr: 950 }); dust(c, t, { a: 0.35, col: '250,225,230' });
  c.__t = t; const L = LINES[9].w;
  const cx = CX, cy = 860, R = 330;
  const inK = eio(p(t, 31.9, 32.8));
  // bokeh
  c.save(); c.globalCompositeOperation = 'lighter';
  const br = rng(5); for (let i = 0; i < 16; i++) { const x = br() * W, y = 300 + br() * 1300, r = 30 + br() * 70, a = 0.04 + br() * 0.05; const g = c.createRadialGradient(x, y, 0, x, y, r); g.addColorStop(0, `rgba(255,205,215,${a})`); g.addColorStop(0.8, `rgba(255,205,215,${a * 0.6})`); g.addColorStop(1, 'rgba(255,205,215,0)'); c.fillStyle = g; c.beginPath(); c.arc(x + Math.sin(t * 0.3 + i) * 10, y, r, 0, 7); c.fill(); }
  c.restore();
  // ring light
  const rewind = p(t, WT(10, 0) - 0.1, WT(10, 1) + 0.4); // spin back at "Halbuki keçmişdə"
  c.save(); c.globalAlpha = inK;
  c.strokeStyle = PEARL; c.lineWidth = 16; c.shadowColor = 'rgba(255,235,240,0.85)'; c.shadowBlur = 50;
  c.beginPath(); c.arc(cx, cy, R * lerp(0.6, 1, inK), 0, 7); c.stroke();
  c.shadowBlur = 0; c.lineWidth = 2; c.strokeStyle = 'rgba(255,240,240,0.4)'; c.beginPath(); c.arc(cx, cy, R - 30, 0, 7); c.stroke();
  c.restore();
  // clock ticks + hand ("saatlarla")
  const sT = L[6][1]; const ck = sm(p(t, sT - 0.1, sT + 0.5));
  if (ck > 0) {
    const handA = -Math.PI / 2 + eio(p(t, sT, 37.6)) * Math.PI * 2 * 3 - eio(rewind) * Math.PI * 2 * 4;
    for (let i = 0; i < 60; i++) {
      const a = -Math.PI / 2 + i / 60 * Math.PI * 2; const big = i % 5 === 0;
      const r0 = R + 26, r1 = R + (big ? 56 : 40);
      c.strokeStyle = `rgba(250,230,220,${ck * (big ? 0.85 : 0.45)})`; c.lineWidth = big ? 3 : 1.5;
      c.beginPath(); c.moveTo(cx + Math.cos(a) * r0, cy + Math.sin(a) * r0); c.lineTo(cx + Math.cos(a) * r1, cy + Math.sin(a) * r1); c.stroke();
    }
    c.save(); c.globalAlpha = ck; c.strokeStyle = GOLD_L; c.lineWidth = 3; c.shadowColor = 'rgba(255,220,180,0.8)'; c.shadowBlur = 16;
    c.beginPath(); c.moveTo(cx + Math.cos(handA) * (R + 8), cy + Math.sin(handA) * (R + 8)); c.lineTo(cx + Math.cos(handA) * (R + 66), cy + Math.sin(handA) * (R + 66)); c.stroke();
    c.beginPath(); c.arc(cx + Math.cos(handA) * (R + 66), cy + Math.sin(handA) * (R + 66), 6, 0, 7); c.fillStyle = GOLD_L; c.fill(); c.restore();
  }
  // eye in the mirror — lash extensions added one by one
  const ext = p(t, L[4][1] - 0.2, L[6][1] + 0.6); // "kirpik qaynağına"
  const opn = 0.62 + 0.25 * eio(p(t, L[11][1], L[12][1] + 0.4)); // "baxışları təsirli"
  const eA = inK;
  c.save(); c.globalAlpha = eA;
  eye(c, cx, cy + 30, { w: 470, h: 64, open: opn, lw: 3, col: ROSE, iris: 0.95, irisCol: '#7b5a3a', lashes: 13, lashLen: 46, lashW: 2.2, lashCol: '#e9c2c4', glint: p(t, L[12][1], L[12][1] + 0.3) });
  // extensions: longer, gold-tipped
  const nE = Math.floor(ext * 26);
  eye(c, cx, cy + 30, { w: 470, h: 64, open: opn, lw: 0.01, lidA: 0, lower: 0, col: GOLD_L, lashes: 26, lashLen: 92, lashW: 2.4, lashCol: GOLD_L, skip: k => ((k * 7) % 26) >= nE, glow: 6 });
  // sparkle on the newest lash
  if (ext > 0 && ext < 1) { const k = [...Array(26).keys()].find(k => ((k * 7) % 26) === nE - 1); if (k != null) { const u = 0.1 + 0.82 * k / 25; const q = qpt([cx - 235, cy + 30], [cx, cy + 30 - 2 * 64 * opn], [cx + 235, cy + 30], u); const g = c.createRadialGradient(q[0], q[1] - 40, 0, q[0], q[1] - 40, 30); g.addColorStop(0, 'rgba(255,250,240,0.9)'); g.addColorStop(1, 'rgba(255,250,240,0)'); c.fillStyle = g; c.fillRect(q[0] - 30, q[1] - 70, 60, 60); } }
  c.restore();
  // labels
  T(c, '— indi —', CX, 380, { it: true, wt: 300, sz: 48, col: ROSE, a: said(t, L[0][1]) * (1 - rewind) });
  // "saatlarla" stretching like time
  const sk = said(t, sT, 0.5), stretch = eio(p(t, sT, 37.8));
  T(c, 'saatlarla', CX, 1330, { it: true, wt: 300, sz: 104, ls: stretch * 30, col: CREAM, a: sk * (1 - sm(p(t, 37.9, 38.4))), blur: (1 - sk) * 10 });
}
// I — manuscript: walls fall to one languid glance
const BRICKS = (() => { const r = rng(9), a = []; const rows = 6, bw = 112, bh = 46, x0 = CX - 3.5 * bw, y0 = 1250; for (let j = 0; j < rows; j++) { const off = j % 2 ? bw / 2 : 0; for (let i = -1; i < 8; i++) { const x = x0 + i * bw + off; if (x < x0 - 1 || x + bw > x0 + 7 * bw + 1) continue; a.push({ x, y: y0 - (j + 1) * bh, w: bw - 6, h: bh - 6, j, vx: (r() - 0.5) * 380, vy: -r() * 260, vr: (r() - 0.5) * 5, d: r() * 0.5 }); } } for (let i = 0; i < 7; i += 2) a.push({ x: x0 + i * bw + 10, y: y0 - 7 * bh, w: bw - 26, h: bh - 6, j: 6, vx: (r() - 0.5) * 380, vy: -r() * 260, vr: (r() - 0.5) * 5, d: r() * 0.5 }); return a; })();
function sI(c, t) {
  bg(c, 'parch', t, { gy: 760, gr: 1000 }); c.save(); c.globalAlpha = 0.9; c.drawImage(PARCH, 0, 0); c.restore();
  dust(c, t, { a: 0.6 }); frame(c, 37.0, t, 1);
  c.__t = t; const L = LINES[10].w;
  T(c, '— keçmişdə —', CX, 380, { it: true, wt: 300, sz: 48, col: GOLD_L, a: said(t, L[1][1]) });
  // wall
  const wk = p(t, L[2][1] - 0.1, L[3][1] + 0.7);
  const crack = eio(p(t, L[4][1], L[4][1] + 0.5));
  const fallT = L[8][1] + 0.12; // "baxış"
  c.save();
  for (const b of BRICKS) {
    const appear = eo(clamp(wk * 1.8 - b.j * 0.13));
    if (appear <= 0) continue;
    let x = b.x, y = b.y + (1 - appear) * 40, rot = 0, a = appear;
    const ft = t - fallT - b.d * 0.6 - (6 - b.j) * 0.04;
    if (ft > 0) { x += b.vx * ft; y += b.vy * ft + 900 * ft * ft; rot = b.vr * ft; a *= 1 - clamp(ft / 1.1); }
    if (a <= 0) continue;
    c.save(); c.globalAlpha = a; c.translate(x + b.w / 2, y + b.h / 2); c.rotate(rot);
    c.fillStyle = 'rgba(60,40,24,0.85)'; c.fillRect(-b.w / 2, -b.h / 2, b.w, b.h);
    c.strokeStyle = GOLD_D; c.lineWidth = 1.6; c.strokeRect(-b.w / 2, -b.h / 2, b.w, b.h);
    c.restore();
  }
  c.restore();
  if (crack > 0 && t < fallT + 0.2) { const r = rng(4); c.save(); c.globalAlpha = 1 - p(t, fallT, fallT + 0.2); c.strokeStyle = GOLD_L; c.lineWidth = 2; c.shadowColor = 'rgba(255,220,160,0.9)'; c.shadowBlur = 12; for (let k = 0; k < 4; k++) { let x = CX - 260 + k * 170 + r() * 60, y = 1250 - 330; c.beginPath(); c.moveTo(x, y); for (let s = 0; s < 8 * crack; s++) { x += (r() - 0.5) * 60; y += 40; c.lineTo(x, y); } c.stroke(); } c.restore(); }
  // languid (süzgün) eye
  const eK = eio(p(t, L[6][1] - 0.2, L[7][1] + 0.5));
  const lashGlow = said(t, L[10][1], 0.6);
  if (eK > 0) {
    c.save(); c.globalAlpha = eK;
    eye(c, CX, 660, { w: 520, h: 62, open: 0.42 * eK + 0.02, lw: 3, col: GOLD_L, glow: 10 + 20 * lashGlow, iris: 0.9, lashes: 19, lashLen: 82 + 10 * lashGlow, lashW: 3.2, lashP: eK, lashCol: lashGlow > 0 ? '#ffe9bf' : GOLD_L });
    c.restore();
    const bz = said(t, L[8][1], 0.4) * (1 - p(t, 43.4, 44.4));
    if (bz > 0) { const g = c.createLinearGradient(0, 690, 0, 1250); g.addColorStop(0, `rgba(255,228,170,${0.28 * bz})`); g.addColorStop(1, 'rgba(255,228,170,0)'); c.fillStyle = g; c.beginPath(); c.moveTo(CX - 120, 690); c.lineTo(CX - 420, 1250); c.lineTo(CX + 420, 1250); c.lineTo(CX + 120, 690); c.fill(); }
  }
  // a few rubble sparks
  if (t > fallT) { const r = rng(12); c.save(); c.globalCompositeOperation = 'lighter'; for (let i = 0; i < 50; i++) { const ft = t - fallT - r() * 0.3; if (ft < 0) { r(); r(); continue; } const x = CX + (r() - 0.5) * 760 + (r() - 0.5) * 200 * ft, y = 1050 + r() * 200 - 120 * ft + 200 * ft * ft; c.fillStyle = `rgba(255,220,160,${Math.max(0, 0.5 - ft * 0.35)})`; c.beginPath(); c.arc(x, y, 1.6, 0, 7); c.fill(); } c.restore(); }
}
// J — the name among us; night road, steering wheel, radio
const NAMES = (() => { const r = rng(33), a = []; const spots = [[230, 520, 0.5], [800, 450, 0.35], [370, 760, 0.8], [760, 820, 0.6], [190, 1050, 0.4], [880, 1120, 0.45], [520, 1240, 0.3], [640, 600, 0.25], [300, 1330, 0.55]]; spots.forEach(([x, y, z], i) => a.push({ x, y, z, d: r() * 0.7, ph: r() * 6 })); return a; })();
function sJ(c, t) {
  bg(c, 'road', t, { gy: 820, gr: 900 });
  c.__t = t; const L = LINES[11].w;
  const road = eio(p(t, L[8][1] - 0.2, L[9][1] + 0.6)); // "indi sükan"
  // night road in perspective
  if (road > 0) {
    c.save(); c.globalAlpha = road;
    const vx = CX, vy = 830;
    const hz = c.createLinearGradient(0, vy - 200, 0, vy + 60); hz.addColorStop(0, 'rgba(230,150,100,0)'); hz.addColorStop(0.8, 'rgba(230,150,100,0.18)'); hz.addColorStop(1, 'rgba(230,150,100,0)'); c.fillStyle = hz; c.fillRect(0, vy - 200, W, 260);
    c.fillStyle = 'rgba(8,8,16,0.9)'; c.beginPath(); c.moveTo(vx - 6, vy); c.lineTo(vx + 6, vy); c.lineTo(W + 500, H); c.lineTo(-500, H); c.fill();
    c.strokeStyle = 'rgba(214,176,108,0.35)'; c.lineWidth = 2; c.beginPath(); c.moveTo(vx - 4, vy); c.lineTo(-300, H); c.moveTo(vx + 4, vy); c.lineTo(W + 300, H); c.stroke();
    for (let i = 0; i < 12; i++) { const ph = ((t * 0.9 + i / 12) % 1), z0 = Math.pow(ph, 2.2), z1 = Math.pow(Math.min(1, ph + 0.035), 2.2); const y0 = vy + (H - vy) * z0, y1 = vy + (H - vy) * z1; c.strokeStyle = `rgba(242,220,171,${0.75 * ph})`; c.lineWidth = 2 + 16 * z0; c.beginPath(); c.moveTo(vx, y0); c.lineTo(vx, y1); c.stroke(); }
    // horizon lights
    c.globalCompositeOperation = 'lighter'; const r = rng(44);
    for (let i = 0; i < 26; i++) { const x = r() * W, y = vy - 10 - r() * 40, rr = 4 + r() * 16; const g = c.createRadialGradient(x, y, 0, x, y, rr); const warm = r() > 0.4; g.addColorStop(0, warm ? 'rgba(255,200,140,0.5)' : 'rgba(200,210,255,0.4)'); g.addColorStop(1, 'rgba(0,0,0,0)'); c.fillStyle = g; c.beginPath(); c.arc(x, y, rr, 0, 7); c.fill(); }
    c.restore();
    // steering wheel
    c.save(); c.globalAlpha = road; c.translate(CX, 1860 + (1 - road) * 200);
    c.strokeStyle = '#0a0a12'; c.lineWidth = 64; c.beginPath(); c.arc(0, 0, 560, Math.PI * 1.08, Math.PI * 1.92); c.stroke();
    c.strokeStyle = 'rgba(214,176,108,0.55)'; c.lineWidth = 2.5; c.beginPath(); c.arc(0, 0, 590, Math.PI * 1.1, Math.PI * 1.9); c.stroke();
    c.restore();
    // radio waves ("bizi dinləyən")
    const rk = said(t, L[11][1], 0.5);
    if (rk > 0) { c.save(); c.lineWidth = 2; for (let j = 0; j < 4; j++) { const ph = (t * 0.7 + j / 4) % 1; c.strokeStyle = `rgba(242,220,171,${rk * 0.35 * (1 - ph)})`; c.beginPath(); c.arc(CX, 1430, 40 + ph * 240, Math.PI * 1.15, Math.PI * 1.85); c.stroke(); } c.restore(); }
  }
  // many women with this name: names at depth
  const nA = 1;
  NAMES.forEach((N, i) => {
    const ap = said(t, L[4][1] + N.d, 0.7); // "adda"
    const go = eio(p(t, L[8][1] - 0.1 + N.d * 0.3, L[9][1] + 0.5 + N.d * 0.3)); // fly past toward viewer
    if (ap <= 0) return;
    const sc = (0.5 + N.z) * (1 + go * 3);
    const x = CX + (N.x - CX) * (1 + go * 2.2) + Math.sin(t * 0.4 + N.ph) * 12, y = 830 + (N.y - 830) * (1 + go * 2.2);
    T(c, 'Müjgan', x, y, { it: true, wt: 300, sz: 70 * sc, col: GOLD_L, a: ap * (0.35 + 0.5 * N.z) * (1 - go), blur: (1 - N.z) * 4 + go * 6 });
  });
  // the one listening now
  const one = said(t, L[14][1], 0.7);
  T(c, 'Müjgan', CX, 640, { it: true, wt: 300, sz: 150, col: gradGold(c, 520, 650), a: one, blur: (1 - one) * 12, glow: 24 });
}
// K — not just a gentle name
function sK(c, t) {
  bg(c, 'night', t, { gy: 860 }); dust(c, t, { a: 0.4 });
  c.__t = t; const L = LINES[12].w;
  const mv = eio(p(t, 50.2, 51.4));
  const y = lerp(640, 820, mv), sz = lerp(150, 176, mv);
  const out = 1 - sm(p(t, 53.55, 53.95));
  T(c, 'Müjgan', CX, y, { it: true, wt: 300, sz, col: gradGold(c, y - 120, y + 10), a: out, glow: 24 });
  // "sadəcə" … "zərif bir qadın adı" dissolves at "deyil"
  const dz = p(t, L[10][1] - 0.02, L[10][1] + 0.9);
  T(c, 'sadəcə', CX, 935, { ff: 'CSC', wt: 500, sz: 30, ls: 10, col: GOLD, a: said(t, L[5][1]) * (1 - dz) });
  const r = rng(77);
  const items = [['zərif', L[6][1]], ['bir', L[7][1]], ['qadın', L[8][1]], ['adı', L[9][1]]];
  const s = items.map(q => q[0]).join(' ');
  letters(c, s, CX, 1040, { it: true, wt: 300, sz: 72, col: CREAM }, (i, n, ch) => {
    const wi = s.slice(0, i).split(' ').length - 1; const k = said(t, items[wi][1], 0.4);
    const rx = r() - 0.5, ry = r(), rd = r() * 0.4;
    const d = eio(clamp((dz - rd) / 0.6));
    return { a: k * (1 - d), dx: rx * 120 * d, dy: -ry * 200 * d + (1 - k) * 10, blur: d * 6 + (1 - k) * 6, rot: rx * d };
  });
  // the struck "deyil"
  const dk = said(t, L[10][1], 0.4);
  T(c, 'deyil', CX, 1150, { wt: 500, sz: 64, ls: 14, col: GOLD_L, a: dk * out * 0.95, blur: (1 - dk) * 8 });
}
// L — said without speaking, pierces without touching
function sL(c, t) {
  bg(c, 'deep', t, { gy: 900 }); dust(c, t, { a: 0.55 });
  c.__t = t; const L = LINES[13].w;
  const o = { it: true, wt: 300, sz: 112, col: CREAM, blurIn: 16 };
  wordsLine(c, [{ s: 'O,', t: L[0][1] }], CX, 560, { it: true, wt: 300, sz: 64, col: GOLD_L });
  wordsLine(c, [{ s: 'danışmadan', t: L[1][1], d: 0.6 }], CX, 720, o);
  wordsLine(c, [{ s: 'deyilən', t: L[2][1] }, { s: 'söz', t: L[3][1], o: { it: false, wt: 500, col: GOLD_L, glow: 16 } }], CX, 845, o);
  const dv = eio(p(t, L[4][1] - 0.05, L[4][1] + 0.6));
  c.save(); c.strokeStyle = GOLD; c.lineWidth = 1.4; c.globalAlpha = 0.8; c.beginPath(); c.moveTo(CX - 200 * dv, 925); c.lineTo(CX + 200 * dv, 925); c.stroke(); c.restore();
  if (dv > 0) { c.save(); c.globalAlpha = dv; c.fillStyle = GOLD; c.translate(CX, 925); c.rotate(Math.PI / 4); c.fillRect(-5, -5, 10, 10); c.restore(); }
  wordsLine(c, [{ s: 'toxunmadan', t: L[5][1], d: 0.6 }], CX, 1050, o);
  wordsLine(c, [{ s: 'sancılan', t: L[6][1] }, { s: 'oxdur.', t: L[7][1], o: { it: false, wt: 500, col: GOLD_L, glow: 16 } }], CX, 1175, o);
  // an arrow glides in and halts a breath short of the words — "without touching"
  const at = eo(p(t, L[6][1] - 0.1, L[7][1] + 0.3));
  if (at > 0) { const x = lerp(-120, 905, at); const hover = Math.sin(t * 3) * 2; arrow(c, x, 1238 + hover, 0, 300, { hs: 18, w: 2.6, glow: 14, a: 1 - p(t, 57.2, 57.6) });
    if (at > 0.98) { const g = c.createRadialGradient(925, 1238, 0, 925, 1238, 30); g.addColorStop(0, 'rgba(255,240,210,0.35)'); g.addColorStop(1, 'rgba(255,240,210,0)'); c.fillStyle = g; c.fillRect(895, 1208, 60, 60); } }
}
// M — mind whose heart you aim at
function sM(c, t) {
  bg(c, 'crimson', t, { gy: 860, gr: 800 }); dust(c, t, { a: 0.45, col: '250,200,190' });
  c.__t = t; const L = LINES[14].w;
  const hx = CX, hy = 840, hs = 13;
  const rel = L[5][1], hitT = rel + 0.75;
  const hd = eio(p(t, L[0][1] - 0.1, L[0][1] + 1.0));
  const beat = t > hitT ? 1 + 0.06 * Math.pow(Math.max(0, Math.sin((t - hitT) * 5.2)), 6) + 0.08 * Math.exp(-5 * (t - hitT)) : 1;
  heart(c, hx, hy, hs * beat, { draw: hd, lw: 3, fill: sm(p(t, hitT - 0.05, hitT + 0.9)) * 0.95 });
  // arrow, aiming (kimin = whose?) then released
  const ak = said(t, L[2][1], 0.5);
  if (ak > 0) {
    const tail = [180, 1330];
    const aim = Math.atan2(hy - tail[1], hx - tail[0]);
    const searching = t < L[4][1] + 0.3 ? Math.sin((t - L[3][1]) * 3) * 0.12 * p(t, L[3][1], L[3][1] + 0.3) : 0;
    const ang = aim + searching * (1 - p(t, L[4][1], L[4][1] + 0.4));
    const f = t > rel ? eio(p(t, rel, hitT)) : 0;
    const startTip = [tail[0] + Math.cos(ang) * 300, tail[1] + Math.sin(ang) * 300];
    const endTip = [hx - Math.cos(aim) * 20, hy + 40 - Math.sin(aim) * 10];
    const tx = lerp(startTip[0], endTip[0], f), ty = lerp(startTip[1], endTip[1], f);
    // dotted trajectory
    const tr = said(t, L[4][1], 0.6) * (1 - p(t, rel, rel + 0.5));
    if (tr > 0) { c.save(); c.globalAlpha = tr * 0.8; c.setLineDash([3, 12]); c.strokeStyle = GOLD; c.lineWidth = 1.6; c.beginPath(); c.moveTo(...startTip); c.lineTo(...endTip); c.stroke(); c.restore(); }
    arrow(c, tx, ty, ang, 300, { hs: 20, w: 3, glow: 16, a: ak });
  }
  // "diqqət edin"
  const dq = said(t, L[7][1], 0.5);
  T(c, 'diqqət edin', CX, 1250, { it: true, wt: 300, sz: 80, col: GOLD_L, a: dq * (1 - p(t, 62.4, 62.9)), blur: (1 - dq) * 10 });
}
// N — the word falls into place, resting on a closed eyelid; O — closing
function sN(c, t) {
  bg(c, 'deep', t, { gy: 980 }); dust(c, t, { a: 0.45 });
  c.__t = t; const L = LINES[15].w;
  const lineK = eio(p(t, 62.7, 63.5));
  const sink = eio(p(t, 68.0, 69.3)); // word sinks behind the lid at the end
  // lid with lashes (closed eye) — the word rests on it
  eye(c, CX, 1052, { w: 720 * lineK + 2, h: 30, open: 0, lw: 2.6, col: GOLD_L, glow: 16, lashes: 23, lashLen: 70, lashP: p(t, 65.9, 68.0), lashW: 2.6, lower: 0 });
  // letters fall
  c.save(); c.beginPath(); c.rect(0, 0, W, 1046); c.clip();
  const word = 'MÜJGAN';
  letters(c, word, CX, 990 + sink * 220, { wt: 500, sz: 200, ls: 14, col: gradGold(c, 840 + sink * 220, 990 + sink * 220), glow: 18 }, (i, n) => {
    const st = 63.42 + i * 0.21, f = p(t, st, st + 0.52);
    const fall = f < 1 ? (1 - f * f) : 0; // gravity
    const bounce = t > st + 0.52 ? Math.exp(-9 * (t - st - 0.52)) * Math.abs(Math.sin((t - st - 0.52) * 18)) * 14 : 0;
    return { a: f > 0 ? 1 : 0, dy: -1100 * fall - bounce, rot: (1 - f) * (i % 2 ? 0.25 : -0.2) };
  });
  c.restore();
  // little landing flashes
  for (let i = 0; i < 6; i++) { const lt = 63.42 + i * 0.21 + 0.52, d = t - lt; if (d < 0 || d > 0.6) continue; const x = CX - 340 + i * 136; const g = c.createRadialGradient(x, 996, 0, x, 996, 70); g.addColorStop(0, `rgba(255,236,200,${0.5 * (1 - d / 0.6)})`); g.addColorStop(1, 'rgba(255,236,200,0)'); c.fillStyle = g; c.fillRect(x - 70, 922, 140, 140); }
  const ta = 1 - sm(p(t, 67.4, 68.0));
  wordsLine(c, [{ s: 'Söz', t: L[0][1] }, { s: 'yerinə', t: L[1][1] }, { s: 'düşdü.', t: L[2][1] }], CX, 1250, { it: true, wt: 300, sz: 66, col: CREAM, a: ta });
  wordsLine(c, [{ s: 'Gələn', t: L[3][1] }, { s: 'sözlərə', t: L[4][1] }, { s: 'qədər.', t: L[5][1] }], CX, 1335, { it: true, wt: 300, sz: 50, col: GOLD_L, a: ta * 0.85 });
}

// ---------- schedule ----------
const SCENES = [
  [0, 4.0, 0, 0.6, sA],
  [3.7, 7.35, 0.5, 0.5, sB],
  [7.1, 12.85, 0.5, 0.3, sC],
  [12.7, 25.5, 0.3, 0.45, sWord],
  [25.3, 32.3, 0.45, 0.45, sG],
  [32.1, 38.7, 0.35, 0.5, sH],
  [38.4, 44.7, 0.5, 0.5, sI],
  [44.5, 50.15, 0.45, 0.25, sJ],
  [50.05, 53.75, 0.2, 0.3, sK],
  [53.6, 57.45, 0.3, 0.45, sL],
  [57.3, 62.6, 0.45, 0.45, sM],
  [62.4, 72, 0.4, 0, sN],
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
  brand(X, t);
  captions(X, t);
  finish(X, t, fr);
  // global fades
  const fa = Math.max(1 - sm(p(t, 0, 0.35)), sm(p(t, 70.9, 71.8)));
  if (fa > 0) { X.fillStyle = `rgba(0,0,0,${fa})`; X.fillRect(0, 0, W, H); }
  X.restore();
}
window.render = render; window.DUR = DUR;
window.frameJPEG = (t, fr) => { render(t, fr); return cv.toDataURL('image/png'); };
