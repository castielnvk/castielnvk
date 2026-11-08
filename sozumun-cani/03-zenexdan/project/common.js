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
function font(c, o) { c.font = (o.it ? 'italic ' : '') + (o.wt || 400) + ' ' + (o.sz || 48) + 'px ' + (o.ff || 'FR'); c.letterSpacing = (o.ls || 0) + 'px'; }
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

